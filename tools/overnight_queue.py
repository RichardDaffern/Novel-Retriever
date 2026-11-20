"""One-shot overnight source verification and paced GitHub Actions queue.

Only approved, previously missing Yup/Idk entries are eligible. Public book
pages are fetched read-only, using strict same-title validation. No chapter
text, login, Cloudflare/DRM bypass, network retries or forced downloads.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from unicodedata import normalize as unicode_normalize
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


ROOT = Path(__file__).resolve().parent.parent
OVERNIGHT = ROOT / "campaigns" / "overnight"
YUP = ROOT / "campaigns" / "yup-pilot" / "backlog-163.json"
IDK = OVERNIGHT / "idk-82.json"
DENY = OVERNIGHT / "excluded-90.json"
VERIFIED = ROOT / "campaigns" / "yup-pilot" / "verified-urls.json"
REGISTRY = ROOT / "downloaded_novels.json"
CAMPAIGN = "yup-idk-overnight-20261119"
WORKFLOW = "library-bulk-download.yml"
MAX_ACTIVE_RUNS = 4
MAX_SOURCE_REQUESTS = 500
REQUEST_DELAY = 2
RUN_DELAY = 150
POLL_DELAY = 75
# Explicit aliases already queued in a prior wave. Do not download twice.
ALIASES = {"A Thought Through Eternity": "A Will Eternal"}
HOSTS = ("novelfull.com", "freewebnovel.com")
MAX_PAGE_BYTES = 3_000_000


class QueueError(ValueError):
    """Invalid manifest, conflicting title or unsupported source."""


def norm(title: str) -> str:
    if not isinstance(title, str):
        return ""
    ascii_title = unicode_normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", ascii_title.lower())


def slug(title: str) -> str:
    ascii_title = unicode_normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")[:140]


def read_json(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > 2_000_000:
        raise QueueError(f"Missing/oversized source file: {path.name}")
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise QueueError("Expected JSON object")
    return result


def _unique_titles(titles: list[str]) -> None:
    seen = set()
    for title in titles:
        if (not isinstance(title, str) or not 3 <= len(title) <= 240
                or not norm(title) or norm(title) in seen):
            raise QueueError(f"Invalid or duplicate title: {title!r}")
        seen.add(norm(title))


def manifests() -> tuple[list[str], list[str], set[str], set[str]]:
    yup = read_json(YUP)
    idk = read_json(IDK)
    exclusions = read_json(DENY)
    prior = read_json(VERIFIED)
    registry = read_json(REGISTRY)
    if (yup.get("version") != 1 or len(yup.get("entries", [])) != 163
            or idk.get("version") != 1 or idk.get("campaign") != CAMPAIGN
            or len(idk.get("entries", [])) != 82
            or exclusions.get("version") != 1
            or len(exclusions.get("excluded", [])) != 90
            or prior.get("version") != 1
            or not isinstance(prior.get("entries"), list)
            or not isinstance(registry.get("novels"), list)):
        raise QueueError("Original audit counts or campaign version changed")
    forbidden = exclusions["excluded"]
    _unique_titles(forbidden)
    denied = {norm(title) for title in forbidden}
    yup_entries = yup["entries"]
    if any(set(row) != {"title", "state"} for row in yup_entries):
        raise QueueError("Unexpected Yup entry schema")
    if any(row["state"] not in {"wave3_requested", "wave4_requested", "needs_source_verification"}
           for row in yup_entries):
        raise QueueError("Unrecognised Yup status; review it manually")
    yup_all = [row["title"] for row in yup_entries]
    idk_all = [row["title"] for row in idk["entries"]]
    if any(set(row) != {"title"} for row in idk["entries"]):
        raise QueueError("Unexpected Idk entry schema")
    _unique_titles(yup_all)
    _unique_titles(idk_all)
    if any(norm(title) in denied for title in yup_all + idk_all):
        raise QueueError("A red/Dropped title leaked into the queue")
    known_title = {norm(row["title"]) for row in prior["entries"]}
    known_title.update(norm(row["title"]) for row in registry["novels"]
                       if isinstance(row, dict) and isinstance(row.get("title"), str))
    yup_pending = [
        row["title"] for row in yup_entries
        if row["state"] == "needs_source_verification" and norm(row["title"]) not in known_title
    ]
    idk_pending = [
        name for name in idk_all
        if norm(name) not in known_title
        and norm(name) not in {norm(x) for x in yup_all}
        and norm(ALIASES.get(name, "")) not in known_title
    ]
    return yup_pending, idk_pending, denied, known_title


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def candidate_urls(title: str) -> list[str]:
    key = slug(title)
    if len(key) < 3:
        return []
    return [
        f"https://novelfull.com/{key}.html",
        f"https://freewebnovel.com/novel/{key}",
    ]


def page_titles(html: str) -> list[str]:
    # Only the public-listing discovery job needs BeautifulSoup.
    # Dispatch jobs intentionally use stdlib only and do not install
    # the source-fetch dependencies.
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.title.get_text(" ", strip=True) if soup.title else ""
    if any(text in title_tag.casefold() for text in (
        "just a moment", "attention required", "access denied", "captcha",
    )):
        return []
    titles = []
    for item in soup.select("h1, h2, h3.title, .book-info h3, meta[property='og:title']"):
        value = item.get("content") if item.name == "meta" else item.get_text(" ", strip=True)
        if value and len(value) < 245:
            titles.append(value.strip())
    if title_tag:
        titles.append(re.split(r"\s+[-|]\s+(?:NovelFull|Read|FreeWebNovel)", title_tag,
                               maxsplit=1, flags=re.I)[0])
    return titles


def matches_public_book_page(title: str, html: str) -> bool:
    return norm(title) in {norm(value) for value in page_titles(html)}


def fetch_public_book_page(url: str) -> tuple[str | None, str]:
    """Read one public listing only; never automatically retry or redirect."""
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in HOSTS:
        raise QueueError("Unapproved source host")
    opener = build_opener(NoRedirect())
    request = Request(url, headers={"User-Agent": "NovelRetriever-Book-Index/1.0"})
    try:
        with opener.open(request, timeout=12) as response:
            if response.headers.get("cf-mitigated", "").lower() == "challenge":
                return None, "site_challenge"
            if response.status != 200:
                return None, f"HTTP_{response.status}"
            if response.headers.get_content_type() not in (
                "text/html", "application/xhtml+xml"
            ):
                return None, "not_html"
            raw = response.read(MAX_PAGE_BYTES + 1)
            if len(raw) > MAX_PAGE_BYTES:
                return None, "page_oversize"
            return raw.decode("utf-8-sig", errors="replace"), "ok"
    except HTTPError as exc:
        return None, f"HTTP_{exc.code}"
    except (URLError, TimeoutError, OSError) as exc:
        return None, f"network_{type(exc).__name__}"


def discover(*, fetcher=fetch_public_book_page, sleeper=time.sleep,
             request_budget=MAX_SOURCE_REQUESTS) -> dict:
    yup, idk, forbidden, prior = manifests()
    selected, unresolved, blocked_hosts = [], [], set()
    seen_urls = set()
    request_count = 0
    for tier, names in (("Yup", yup), ("Idk", idk)):
        for title in names:
            found = None
            reasons = []
            for url in candidate_urls(title):
                host = urlsplit(url).hostname
                if host in blocked_hosts:
                    reasons.append(f"{host}_blocked")
                    continue
                if request_count >= request_budget:
                    reasons.append("request_budget_exhausted")
                    break
                if request_count:
                    sleeper(REQUEST_DELAY)
                request_count += 1
                html, status = fetcher(url)
                if status in {"HTTP_403", "HTTP_429", "site_challenge"}:
                    # Respect source access/rate limits; no fallback around a block.
                    blocked_hosts.add(host)
                    reasons.append(status)
                    continue
                if html is None:
                    reasons.append(status)
                    continue
                if matches_public_book_page(title, html):
                    if url in seen_urls:
                        reasons.append("duplicate_source_url")
                    else:
                        found = {"title": title, "url": url, "tier": tier,
                                 "evidence": "public_listing_exact_title"}
                        seen_urls.add(url)
                    break
                reasons.append("title_mismatch")
            if found is not None:
                selected.append(found)
                print(f"VERIFIED LISTING [{tier}] {title}", flush=True)
            else:
                reason = ",".join(reasons) or "unavailable"
                unresolved.append({"title": title, "tier": tier, "reason": reason})
                print(f"SKIPPED [{tier}] {title}: {reason}", flush=True)
    return {
        "version": 1, "campaign": CAMPAIGN,
        "verified": selected, "unresolved": unresolved,
        "summary": {
            "eligible_yup": len(yup), "eligible_idk": len(idk),
            "verified": len(selected), "unresolved": len(unresolved),
            "public_book_requests": request_count,
            "source_hosts_blocked": sorted(blocked_hosts),
            "global_exclusions_checked": len(forbidden),
        },
    }


def active_workflows(*, runner=subprocess.run) -> int:
    response = runner(
        ["gh", "api", "repos/" + os.environ["GITHUB_REPOSITORY"]
         + "/actions/workflows/" + WORKFLOW + "/runs?per_page=80"],
        check=True, capture_output=True, text=True, timeout=30,
    )
    data = json.loads(response.stdout)
    runs = data.get("workflow_runs", [])
    if not isinstance(runs, list):
        raise QueueError("GitHub workflow-run response was invalid")
    return sum(item.get("status") != "completed" for item in runs)


def dispatch(verified: dict, tier: str, *, runner=subprocess.run,
             sleeper=time.sleep, clock=time.monotonic, minutes=260) -> dict:
    yup, idk, forbidden, prior = manifests()
    allowed = {norm(x) for x in (yup if tier == "Yup" else idk)}
    pending = []
    seen = set()
    records = verified.get("verified", [])
    if (verified.get("version") != 1 or verified.get("campaign") != CAMPAIGN
            or not isinstance(records, list)):
        raise QueueError("Invalid discovered-book report")
    for item in records:
        if not isinstance(item, dict) or item.get("tier") != tier:
            continue
        title, url = item.get("title"), item.get("url")
        if (norm(title) not in allowed or norm(title) in forbidden
                or norm(title) in prior or norm(title) in seen
                or item.get("evidence") != "public_listing_exact_title"
                or url not in candidate_urls(title)):
            raise QueueError(f"Untrusted or duplicate discovery entry: {title!r}")
        seen.add(norm(title))
        pending.append(item)
    report = {"version": 1, "tier": tier, "campaign": CAMPAIGN,
              "submitted": [], "held": [], "approved_source_count": len(pending)}
    if os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("GITHUB_RUN_ATTEMPT", "1") != "1":
        report["held"] = pending
        report["reason"] = "GitHub Actions rerun blocked to avoid duplicate dispatch"
        return report
    deadline = clock() + minutes * 60
    while pending:
        if clock() >= deadline:
            report["reason"] = "overnight_dispatch_budget_exhausted"
            break
        if active_workflows(runner=runner) >= MAX_ACTIVE_RUNS:
            sleeper(POLL_DELAY)
            continue
        group = pending[:2]
        urls = [item["url"] for item in group]
        try:
            runner(
                ["gh", "workflow", "run", WORKFLOW, "--ref", "main",
                 "--field", "novel_urls=" + ",".join(urls),
                 "--field", "chapter_range=", "--field", "force=false"],
                check=True, timeout=45,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            report["reason"] = "GitHub dispatch refused: " + type(exc).__name__
            break
        report["submitted"].append({
            "titles": [item["title"] for item in group],
            "urls": urls,
        })
        del pending[:len(group)]
        print(f"Queued [{tier}] {len(group)} checked books; "
              f"{len(pending)} awaiting dispatcher slot", flush=True)
        if pending:
            sleeper(RUN_DELAY)
    report["held"] = pending
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("discover", "dispatch", "preflight"))
    p.add_argument("--tier", choices=("Yup", "Idk"))
    p.add_argument("--sources", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--minutes", type=int, default=260)
    p.add_argument("--request-budget", type=int, default=MAX_SOURCE_REQUESTS)
    args = p.parse_args(argv)
    try:
        if args.action == "preflight":
            yup, idk, denied, prior = manifests()
            output = {"eligible_yup": len(yup), "eligible_idk": len(idk),
                      "excluded_global": len(denied), "previously_known": len(prior),
                      "mode": "READ ONLY"}
        elif args.action == "discover":
            if not 1 <= args.request_budget <= MAX_SOURCE_REQUESTS:
                raise QueueError("Invalid public page request budget")
            output = discover(request_budget=args.request_budget)
        else:
            if not args.tier or not args.sources or not 1 <= args.minutes <= 290:
                raise QueueError("Expected --tier, --sources and 1-290 minutes")
            output = dispatch(read_json(args.sources), args.tier, minutes=args.minutes)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2)
                            + "\n", encoding="utf-8")
        print(json.dumps(output.get("summary", output if args.action == "preflight"
                                    else {k: (len(v) if isinstance(v, list) else v)
                                          for k, v in output.items() if k in (
                                              "tier", "submitted", "held", "reason")})),
              flush=True)
        return 0
    except (QueueError, ValueError, OSError, subprocess.SubprocessError) as exc:
        print("Overnight queue stopped:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

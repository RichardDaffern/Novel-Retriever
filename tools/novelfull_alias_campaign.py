#!/usr/bin/env python3
"""Search NovelFull using real /search listings, suffix titles and verified aliases.

A title match is metadata only. The downstream bulk workflow owns chapter
download, integrity checks and EPUB assembly. No chapter prose is fetched here.
"""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from tools import overnight_queue as q

TARGETS = Path("campaigns/novelfull-alias-20261124/targets.json")
CAMPAIGN = "novelfull-actual-search-20261124"
SEARCH_BASE = "https://novelfull.com/search"
MATCH_MIN = 0.91
PAUSE = 0.65
MAX_ACTIVE_BULKS = 2
BATCH_SIZE = 10

# Only independently established same-book titles, not speculative cross-book substitutions.
ALTERNATES = {
    "A Thought Through Eternity": ("A Will Eternal", "https://novelfull.com/a-will-eternal.html"),
    "The Military Female Soldier With Unwavering Stubbornness": (
        "Reborn at Boot Camp: General, Don’t Mess Around!",
        "https://novelfull.com/reborn-at-boot-camp-general-dont-mess-around.html"),
    "Golden Time (JungYong)": ("Golden Time", "https://novelfull.com/golden-time.html"),
    "Yong Heng Zhi Zun": ("Eternal Reverence", None),
}
# These have existing campaigns or a completed archive. They may be counted
# as existing NovelFull listings but must not be re-dispatched in parallel.
ALREADY_SUBMITTED = {
    "A Record Of Mortal’s Journey To Immortality",
    "Attack Of The Adorable Kid: President Daddy's Infinite Pampering",
    "Beautiful Time With You",
    "Beauty And The Bodyguard",
    "Bringing The Nation's Husband Home",
    "Seoul Station's Necromancer",
}
STOPWORDS = {"a", "an", "and", "of", "for", "with", "the", "in", "is", "to", "on"}


def normalise(s: str) -> str:
    v = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").casefold()
    v = v.replace("levelling", "leveling").replace("favourite", "favorite")
    return " ".join(re.findall(r"[a-z0-9]+", v))


def canon(s: str) -> str:
    return normalise(s).replace(" ", "")


def similarity(query: str, actual: str) -> float:
    qn, an = normalise(query), normalise(actual)
    if qn == an:
        return 1.0
    qt, at = [t for t in qn.split() if t not in STOPWORDS], [t for t in an.split() if t not in STOPWORDS]
    if qt == at and qt:
        return 1.0
    if len(qn) < 12:
        return 0.0
    overlap = len(set(qt) & set(at)) / max(1, len(set(qt)))
    ratio = SequenceMatcher(None, qn, an).ratio()
    return ratio if overlap >= .75 and ratio >= MATCH_MIN else 0.0


def queries(title: str) -> list[str]:
    candidates = [title]
    if ":" in title:
        suffix = title.rsplit(":", 1)[-1].strip()
        if len(suffix) >= 7:
            candidates.append(suffix)
    changed = title.replace("Levelling", "Leveling").replace("levelling", "leveling").replace("Favourite", "Favorite")
    if changed != title:
        candidates.append(changed)
    if title in ALTERNATES:
        candidates.append(ALTERNATES[title][0])
    return list(dict.fromkeys(candidates))


def source_get(url: str) -> str:
    if not url.startswith("https://novelfull.com/"):
        raise ValueError("Only canonical NovelFull HTTPS URLs allowed")
    req = Request(url, headers={"User-Agent": "NovelRetriever-Book-Index/1.0"})
    with urlopen(req, timeout=18) as response:
        if response.status != 200 or response.geturl().split("?")[0].split("#")[0] != url.split("?")[0]:
            raise ValueError("Unexpected site status or cross-path redirect")
        if response.headers.get_content_type() not in ("text/html", "application/xhtml+xml"):
            raise ValueError("Not an HTML listing")
        data = response.read(700001)
        if len(data) > 700000:
            raise ValueError("Book listing exceeded 700 kB")
        return data.decode("utf-8-sig", errors="replace")


def search_links(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    found, seen = [], set()
    for a in soup.select("a[href]"):
        href = urljoin("https://novelfull.com/", a.get("href", ""))
        parsed = urlsplit(href)
        if parsed.scheme != "https" or parsed.netloc != "novelfull.com":
            continue
        if not re.fullmatch(r"/[a-z0-9]+(?:-[a-z0-9]+)*\.html", parsed.path):
            continue  # Book page, never chapters, site navigation or external URLs.
        name = a.get_text(" ", strip=True)
        if not name or len(name) > 200 or href in seen:
            continue
        seen.add(href)
        found.append((name, f"https://novelfull.com{parsed.path}"))
    return found


def verify_title_page(url: str, expected: str, *, getter=source_get) -> tuple[bool, str]:
    """Check actual book page title; no chapter text is requested."""
    soup = BeautifulSoup(getter(url), "html.parser")
    heads = [h.get_text(" ", strip=True) for h in soup.select("h1, h2, h3.title")]
    real = next((t for t in heads if similarity(expected, t) >= MATCH_MIN), "")
    return bool(real), real


def inventory(*, getter=source_get, sleeper=time.sleep, out=Path("novelfull-match-report.json")) -> dict:
    data = json.loads(TARGETS.read_text(encoding="utf-8"))
    targets = data["titles"]
    if len(targets) != 100 or len({canon(t) for t in targets}) != 100:
        raise ValueError("Expected exactly 100 unique reconciliation title targets")
    denied = {canon(t) for t in q.read_json(q.DENY)["excluded"]}
    reg = q.read_json(q.REGISTRY)
    complete = [row for row in reg["novels"] if any(
        d.get("status") == "complete" and d.get("range") == "all"
        for d in row.get("downloads", []) if isinstance(d, dict))]
    completed_urls = {row["url"] for row in complete}
    completed_names = {canon(row["title"]) for row in complete}
    verified_source_aliases = {canon(row["title"]) for row in q.read_json(q.VERIFIED)["entries"]
                               if row.get("url") in completed_urls}
    submitted = {canon(x) for x in ALREADY_SUBMITTED}
    matches, held, requests, blocked = [], [], 0, False

    for title in targets:
        if canon(title) in denied:
            held.append({"requested": title, "reason": "global red/Dropped exclusion"})
            continue
        found = []
        reasons = []
        for phrase in queries(title):
            if blocked:
                reasons.append("source_access_blocked")
                break
            if requests:
                sleeper(PAUSE)
            requests += 1
            url = SEARCH_BASE + "?" + urlencode({"keyword": phrase})
            try:
                for name, source_url in search_links(getter(url)):
                    score = max(similarity(title, name), similarity(phrase, name))
                    if score >= MATCH_MIN:
                        found.append((score, name, source_url, phrase))
            except HTTPError as exc:
                reasons.append(f"HTTP_{exc.code}")
                if exc.code in (403, 429):
                    blocked = True
                    break
            except (URLError, TimeoutError, ValueError, OSError) as exc:
                reasons.append(type(exc).__name__)
        # Search itself does not index all source-side alternative names.
        if title in ALTERNATES and ALTERNATES[title][1] and not found:
            alias, url = ALTERNATES[title]
            found.append((1.0, alias, url, "independently_verified_alias"))
        found.sort(key=lambda row: (-row[0], row[2]))
        unique = []
        for item in found:
            if item[2] not in {x[2] for x in unique}:
                unique.append(item)
        if len(unique) > 1 and unique[1][0] >= unique[0][0] - 0.035:
            held.append({"requested": title, "reason": "ambiguous_multiple_books",
                         "candidate_titles": [x[1] for x in unique[:3]]})
            continue
        if not unique:
            held.append({"requested": title, "reason": ",".join(reasons) or "no_matched_book_listing"})
            continue
        score, found_title, url, phrase = unique[0]
        try:
            # For direct alias pages, verify the catalogue is actually reachable
            # and contains its independently established identity.
            valid, real = verify_title_page(url, found_title, getter=getter)
            if not valid:
                raise ValueError("Search title and actual book-page title differ")
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            held.append({"requested": title, "reason": "book_page_validation:" + str(exc)[:160]})
            continue
        already = (url in completed_urls or canon(title) in completed_names
                   or canon(title) in verified_source_aliases)
        in_progress = canon(title) in submitted
        entry = {"requested": title, "novelfull_title": real or found_title,
                 "url": url, "score": round(score, 4),
                 "matched_by": phrase, "already_complete": already,
                 "already_dispatched": in_progress}
        matches.append(entry)
        print("CONFIRMED_NOVELFULL", title, "=>", entry["novelfull_title"],
              url, "already_complete", already, "in_progress", in_progress, flush=True)

    # Alias collisions are never two separately downloadable novels.
    by_url = {}
    for row in matches:
        by_url.setdefault(row["url"], []).append(row["requested"])
    for row in matches:
        row["duplicate_source_url"] = len(by_url[row["url"]]) > 1
    eligible = [x for x in matches if not x["already_complete"] and
                not x["already_dispatched"] and not x["duplicate_source_url"]]
    report = {"version": 1, "campaign": CAMPAIGN, "targets": len(targets),
              "confirmed_novelfull_book_pages": len(matches),
              "distinct_novelfull_pages": len(by_url),
              "eligible_for_bulk": len(eligible),
              "already_complete": sum(x["already_complete"] for x in matches),
              "already_in_progress": sum(x["already_dispatched"] for x in matches),
              "listing_requests": requests, "source_access_blocked": blocked,
              "matches": matches, "unresolved": held}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("NOVELFULL_TOTAL", json.dumps({k:report[k] for k in (
        "targets", "confirmed_novelfull_book_pages", "distinct_novelfull_pages",
        "eligible_for_bulk", "already_complete", "already_in_progress",
        "listing_requests", "source_access_blocked")}), flush=True)
    return report


def dispatch(source: dict, *, out: Path, minutes=315, runner=subprocess.run,
             sleeper=time.sleep, clock=time.monotonic) -> dict:
    if source.get("version") != 1 or source.get("campaign") != CAMPAIGN:
        raise ValueError("Unexpected discovery source")
    import os
    if (os.getenv("GITHUB_REPOSITORY") != "RichardDaffern/Novel-Retriever"
            or os.getenv("GITHUB_ACTIONS") != "true"
            or os.getenv("GITHUB_RUN_ATTEMPT", "1") != "1"):
        raise ValueError("Only first authorised GitHub Actions attempt may dispatch")
    valid_targets = {canon(t) for t in json.loads(TARGETS.read_text())["titles"]}
    denied = {canon(t) for t in q.read_json(q.DENY)["excluded"]}
    completed_urls = {row["url"] for row in q.read_json(q.REGISTRY)["novels"] if any(
        d.get("status") == "complete" and d.get("range") == "all"
        for d in row.get("downloads", []) if isinstance(d, dict))}
    selected, seen = [], set()
    for x in source.get("matches", []):
        title, url = x["requested"], x["url"]
        if x.get("already_complete") or x.get("already_dispatched") or x.get("duplicate_source_url"):
            continue
        if (canon(title) not in valid_targets or canon(title) in denied
                or url in seen or url in completed_urls
                or x.get("score", 0) < MATCH_MIN
                or not re.fullmatch(r"https://novelfull\.com/[a-z0-9]+(?:-[a-z0-9]+)*\.html",url)):
            raise ValueError("Untrusted title or source URL in bulk plan")
        seen.add(url)
        selected.append(x)
    report = {"version": 1, "campaign": CAMPAIGN, "verified": len(selected),
              "submitted": [], "held": selected[:], "remaining": len(selected),
              "max_simultaneous_bulk_runs": MAX_ACTIVE_BULKS}
    def persist():
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp=out.with_suffix(".tmp")
        tmp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        tmp.replace(out)
    persist()
    end=clock()+minutes*60
    while selected:
        if clock() >= end:
            report["stop_reason"]="dispatch_window_expired"
            break
        try:
            active=q.active_workflows(runner=runner)
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            report["stop_reason"]="cannot_check_active_runs:"+type(exc).__name__
            break
        if active>=MAX_ACTIVE_BULKS:
            sleeper(75)
            continue
        group=selected[:BATCH_SIZE]
        cmd=["gh","workflow","run","library-bulk-download.yml","--ref","main",
             "--raw-field","novel_urls="+",".join(x["url"] for x in group),
             "--raw-field","chapter_range=","--raw-field","force=false",
             "--raw-field","confirm_rights=true"]
        try:
            runner(cmd,check=True,timeout=45)
        except (OSError,subprocess.SubprocessError) as exc:
            report["stop_reason"]="dispatch_refused:"+type(exc).__name__
            break
        report["submitted"].append({"titles":[x["requested"] for x in group],
                                    "urls":[x["url"] for x in group]})
        del selected[:len(group)]
        report["held"]=selected[:]
        report["remaining"]=len(selected)
        persist()
        print("DISPATCHED_NOVELFULL_BULK",len(group),"new titles",
              [x["requested"] for x in group],flush=True)
        if selected:
            sleeper(90)
    persist()
    return report


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("action",choices=["discover","dispatch"])
    p.add_argument("--source",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    try:
        if args.action=="discover":
            inventory(out=args.out)
        else:
            if not args.source:p.error("--source required for dispatch")
            report=dispatch(json.loads(args.source.read_text(encoding="utf-8")),out=args.out)
            print("BULK_DISPATCH_TOTAL",sum(len(x["titles"]) for x in report["submitted"]),
                  "submitted;",report["remaining"],"pending",report.get("stop_reason",""),flush=True)
            if report.get("stop_reason"):return 1
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print("NovelFull search campaign stopped",type(exc).__name__,str(exc)[:300],file=sys.stderr)
        return 1


if __name__=="__main__":
    raise SystemExit(main())

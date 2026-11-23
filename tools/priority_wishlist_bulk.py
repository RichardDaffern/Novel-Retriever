"""One-shot source-first bulk wishlist campaign: NovelFull then ReadNovelFull.

This is a separate campaign from old incomplete-chapter recovery. It uses the
historical Yup/Idk wishlist manifests, not a claim to have current private HF
Available.csv. Discovery only fetches public book listings / ReadNovelFull
chapter indexes; chapter prose is downloaded only by the existing guarded
Library - Bulk Download workflow after individual URL verification.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlsplit

from tools import overnight_queue as q
from tools.mixed_source_bulk import _validated_url

HOST_ORDER = ("novelfull.com", "readnovelfull.com")
MAX_ACTIVE = 2
BATCH_SIZE = 10
DELAY_SECONDS = 2.0
DISPATCH_GAP_SECONDS = 90
POLL_SECONDS = 75
MAX_REQUESTS = 500

# Correct the historical misconception that a previously attempted book is
# complete. These aliases, however, already identify separate known
# completed/excluded editions and must not trigger a second download.
COMPLETED_ALIASES = {
    "a thought through eternity", "arifureta shokugyou de sekai saikyou",
    "crazy levelling system", "dungeon defence",
    "evil dragon against the heaven", "invincible dragon emperor",
    "levelling up and becoming undefeated", "records of the human emperor",
    "soul land", "the school prince is a girl", "xian ni",
}
# Repair these old chapter-index problems separately, after the easy-source
# campaign. Current FreeWebNovel runs reconfirmed the four additional holds.
RECENT_REPAIR_HOLDS = {
    "this mc is kickass", "past life returner", "tomb raider king",
    "world domination system",
}
# Previously audited full original editions versus shorter mirror indexes.
MINIMUM_FULL_EDITION = {
    "doom lord": 856,
    "girl ill teach you cultivation": 812,
    "beast piercing the heavens": 1445,
}
MAIN_CAMPAIGN = "priority-novelfull-readnovelfull-20261124"


def _norm(s: str) -> str:
    return q.norm(s)


def _aliases() -> set[str]:
    return {_norm(x) for x in COMPLETED_ALIASES}


def pending_titles() -> tuple[list[dict], dict]:
    yup = q.read_json(q.YUP)
    idk = q.read_json(q.IDK)
    registry = q.read_json(q.REGISTRY)
    denied = q.read_json(q.DENY)
    blocked = q.read_json(q.OVERNIGHT / "blocked-full-retries-20261120.json")
    if (len(yup.get("entries", [])) != 163
            or len(idk.get("entries", [])) != 82
            or len(denied.get("excluded", [])) != 90
            or len(blocked.get("titles", [])) != 14
            or not isinstance(registry.get("novels"), list)):
        raise ValueError("Source-of-truth manifest structure changed: abort campaign")
    complete = {
        _norm(row.get("title", ""))
        for row in registry["novels"]
        if isinstance(row, dict) and any(
            isinstance(d, dict) and d.get("status") == "complete"
            and d.get("range") == "all" for d in row.get("downloads", [])
        )
    }
    completed_urls = {
        row.get("url") for row in registry["novels"]
        if isinstance(row, dict) and any(
            isinstance(d, dict) and d.get("status") == "complete"
            and d.get("range") == "all" for d in row.get("downloads", [])
        )
    }
    excluded = {_norm(x) for x in denied["excluded"]}
    repairs = {_norm(x) for x in blocked["titles"]} | {
        _norm(x) for x in RECENT_REPAIR_HOLDS
    }
    aliases = _aliases()
    selected, seen = [], set()
    skip = {"complete": 0, "red_dropped": 0, "repair_hold": 0,
            "completed_alias": 0, "duplicate": 0}
    for tier, rows in (("Yup", yup["entries"]), ("Idk", idk["entries"])):
        for row in rows:
            title = row.get("title", "")
            name = _norm(title)
            if not name:
                raise ValueError("Empty wishlist title")
            reason = None
            if name in seen:
                reason = "duplicate"
            elif name in excluded:
                reason = "red_dropped"
            elif name in complete:
                reason = "complete"
            elif name in aliases:
                reason = "completed_alias"
            elif name in repairs:
                reason = "repair_hold"
            if reason:
                skip[reason] += 1
                continue
            seen.add(name)
            selected.append({"title": title, "tier": tier})
    return selected, {"wishlist_yup": 163, "wishlist_idk": 82,
                      "completed_registry_records": len(registry["novels"]),
                      "selected_for_source_search": len(selected),
                      "skipped": skip,
                      "completed_urls": sorted(u for u in completed_urls if isinstance(u, str))}


def source_candidates(title: str, curated: dict) -> list[str]:
    expected = _norm(title)
    direct = q.candidate_urls(title)[:3]
    for item in curated.get("books", []):
        if _norm(item.get("title", "")) == expected and urlsplit(item["url"]).hostname in HOST_ORDER:
            direct.append(item["url"])
    return list(dict.fromkeys(sorted(direct, key=lambda u: HOST_ORDER.index(urlsplit(u).hostname))))


def discover(out: Path, *, fetcher=q.fetch_public_book_page,
             reader_discover=None, sleeper=time.sleep, request_budget=MAX_REQUESTS) -> dict:
    if reader_discover is None:
        from tools.readnovelfull_source import discover as reader_discover
    pending, audit = pending_titles()
    curated = q.read_json(q.OVERNIGHT / "curated-book-links-20261120-night.json")
    completed_urls = set(audit.pop("completed_urls"))
    matched, held, blocked_hosts, seen_urls = [], [], set(), set()
    requests = 0
    for item in pending:
        title, tier = item["title"], item["tier"]
        errors = []
        candidate = None
        reviewed_aliases = {
            _norm(x.get("source_title", "")) for x in curated.get("books", [])
            if _norm(x.get("title", "")) == _norm(title)
        }
        for url in source_candidates(title, curated):
            host = urlsplit(url).hostname
            if host in blocked_hosts:
                errors.append(f"{host}:blocked_after_denial")
                continue
            if url in completed_urls:
                errors.append("completed_canonical_URL")
                continue
            if requests >= request_budget:
                errors.append("request_budget_exhausted")
                break
            if requests:
                sleeper(DELAY_SECONDS)
            requests += 1
            html, status = fetcher(url)
            if status in ("HTTP_403", "HTTP_429", "site_challenge"):
                blocked_hosts.add(host)
                errors.append(f"{host}:{status}")
                continue
            if html is None:
                errors.append(f"{host}:{status}")
                continue
            discovered_names = {_norm(x) for x in q.page_titles(html)}
            if _norm(title) not in discovered_names and not (reviewed_aliases & discovered_names):
                errors.append(f"{host}:book_title_mismatch")
                continue
            site, canonical = _validated_url(url)
            if canonical in seen_urls:
                errors.append("duplicate_source_URL")
                continue
            if host == "readnovelfull.com":
                try:
                    details = reader_discover(canonical)
                    count = details["numChapters"]
                    if _norm(details["title"]) not in discovered_names:
                        raise ValueError("Book/AJAX title disagreement")
                    floor = MINIMUM_FULL_EDITION.get(_norm(title), 0)
                    if count < floor:
                        raise ValueError(f"Shorter translation: {count} chapters, expected at least {floor}")
                except (ValueError, OSError, KeyError, TypeError) as exc:
                    errors.append("ReadNovelFull:index_invalid:" + str(exc)[:180])
                    continue
            else:
                count = None  # NovelFull validates the catalogue in its prepare job.
            candidate = {"title": title, "tier": tier, "url": canonical,
                         "site": site, "source_verified": True,
                         "evidence": "public_book_page_exact_title",
                         "readnovelfull_index_chapters": count}
            seen_urls.add(canonical)
            print(f"VERIFIED [{tier}] [{site}] {title}", flush=True)
            break
        if candidate:
            matched.append(candidate)
        else:
            reason = ",".join(errors) or "no_supported_source"
            held.append({**item, "reason": reason})
            print(f"UNRESOLVED [{tier}] {title}: {reason}", flush=True)
    result = {"version": 1, "campaign": MAIN_CAMPAIGN, "audit": audit,
              "verified": matched, "unresolved": held,
              "requests": requests, "blocked_hosts": sorted(blocked_hosts),
              "priority": ["NovelFull", "ReadNovelFull"], "force": False,
              "contains_novel_chapter_text": False}
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Discovery done: {len(matched)} verified, {len(held)} unresolved, {requests} listing requests", flush=True)
    return result


def dispatch(source: dict, out: Path, *, runner=subprocess.run,
             sleeper=time.sleep, clock=time.monotonic, minutes=270) -> dict:
    if (source.get("campaign") != MAIN_CAMPAIGN or source.get("version") != 1
            or not isinstance(source.get("verified"), list)):
        raise ValueError("Invalid source verification report")
    if os.getenv("GITHUB_REPOSITORY") != "RichardDaffern/Novel-Retriever":
        raise ValueError("Unexpected repository")
    if os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("GITHUB_RUN_ATTEMPT") != "1":
        raise ValueError("Rerunning a dispatch would create duplicate downloads")
    pending, _ = pending_titles()
    allowed = {(_norm(x["title"]), x["tier"]) for x in pending}
    selected, seen = [], set()
    for item in source["verified"]:
        if not isinstance(item, dict):
            raise ValueError("Invalid verified item")
        title, tier, url = item["title"], item["tier"], item["url"]
        if (_norm(title), tier) not in allowed or _norm(title) in seen or not item.get("source_verified"):
            raise ValueError("Unapproved or duplicated title in scan")
        site, canonical = _validated_url(url)
        if site not in ("NovelFull", "ReadNovelFull") or canonical != url:
            raise ValueError("Unsupported source URL")
        seen.add(_norm(title))
        selected.append(item)
    # Prefer Yup first; within each priority, prefer NovelFull.
    selected.sort(key=lambda x: (0 if x["tier"] == "Yup" else 1,
                                0 if x["site"] == "NovelFull" else 1,
                                _norm(x["title"])))
    report = {"version": 1, "campaign": MAIN_CAMPAIGN,
              "verified": len(selected), "submitted": [], "held": selected[:],
              "force": False, "max_active": MAX_ACTIVE, "rights_attestation": "user_confirmed_in_chat",
              "remaining": len(selected)}
    def persist():
        temp = out.with_suffix(out.suffix + ".tmp")
        temp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temp.replace(out)
    persist()
    deadline = clock() + minutes * 60
    while selected:
        if clock() >= deadline:
            report["reason"] = "time_limit_reached"
            break
        try:
            active = q.active_workflows(runner=runner)
        except (ValueError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            report["reason"] = "unable_to_check_active_runs:" + type(exc).__name__
            break
        if active >= MAX_ACTIVE:
            sleeper(POLL_SECONDS)
            continue
        group = selected[:BATCH_SIZE]
        urls = ",".join(item["url"] for item in group)
        cmd = ["gh", "workflow", "run", q.WORKFLOW, "--ref", "main",
               "--raw-field", "novel_urls=" + urls,
               "--raw-field", "chapter_range=",
               "--raw-field", "force=false",
               "--raw-field", "confirm_rights=true"]
        try:
            runner(cmd, check=True, timeout=45)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            report["reason"] = "dispatch_rejected:" + type(exc).__name__
            break
        report["submitted"].append({"titles": [x["title"] for x in group],
                                    "urls": [x["url"] for x in group]})
        del selected[:len(group)]
        report["held"] = selected[:]
        report["remaining"] = len(selected)
        persist()
        print(f"DISPATCHED {len(group)} books; {len(selected)} awaiting a slot", flush=True)
        if selected:
            sleeper(DISPATCH_GAP_SECONDS)
    persist()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("discover", "dispatch"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--minutes", type=int, default=270)
    args = parser.parse_args(argv)
    try:
        if args.action == "discover":
            discover(args.out)
        else:
            if not args.source:
                parser.error("--source required for dispatch")
            if not 1 <= args.minutes <= 280:
                parser.error("--minutes must be 1-280")
            result = dispatch(json.loads(args.source.read_text(encoding="utf-8")),
                              args.out, minutes=args.minutes)
            print("Dispatch summary:", {
                "verified": result["verified"],
                "submitted_books": sum(len(group["titles"]) for group in result["submitted"]),
                "held": result["remaining"], "reason": result.get("reason"),
            }, flush=True)
            if result.get("reason"):
                return 1
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print("Bulk wishlist campaign stopped:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

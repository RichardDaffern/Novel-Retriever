#!/usr/bin/env python3
"""Plan validated multi-website novel downloads by saved names or exact URLs.

GitHub's manual workflow accepts mixed-site novel URLs separated by commas,
semicolons, spaces or newlines, plus optional saved names. The source of each
link is detected from its validated host and path: no website selection is
needed. Names resolve only from verified registry or curated records; unknown
or ambiguous titles fail instead of guessing URLs.
"""
from __future__ import annotations

import argparse
from difflib import get_close_matches
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from tools.sequential_bulk_download import parse_novel_urls
from tools.download_registry import (
    already_available, canonical_url, normalise_range, read_registry,
    website_name,
)
from tools.freewebnovel_source import validate_book_url
from tools.readnovelfull_source import validate_book_url as validate_readnovelfull_url
from tools.wuxiaclick_source import validate_book_url as validate_wuxiaclick_url
from tools.scribblehub_crosspost_downloader import _verified_record

# User-approved maximum number of new titles in one resumable bulk run.
# Cached/skipped titles do not count. Keep GitHub's larger platform ceiling
# separate so campaign policy cannot silently expand to the platform maximum.
MAX_BATCH_TITLES = 10
MAX_MATRIX_JOBS = 256
SITES = ("NovelFull", "FreeWebNovel", "ReadNovelFull", "WuxiaClick", "Scribble Hub")
WEBSITE_CHOICES = ("All",) + SITES
DEFAULT_CATALOGUE = Path("curated_novels.json")


def _normal_name(text: str) -> str:
    return " ".join(text.split()).casefold()


def _validated_url(value: str) -> tuple[str, str]:
    url = canonical_url(value)
    site = website_name(url)
    if site == "FreeWebNovel":
        return site, validate_book_url(url)
    if site == "ReadNovelFull":
        return site, validate_readnovelfull_url(url)
    if site == "WuxiaClick":
        return site, validate_wuxiaclick_url(url)
    if site == "Scribble Hub":
        # Uses only verified same-author cross-posts; never try direct
        # Scribble Hub chapter scraping for arbitrary series URLs.
        canonical, _, _ = _verified_record(url)
        return site, canonical
    if site == "NovelFull":
        # Prevent accidental use of unsupported websites/novel pages.
        if not re.fullmatch(r"/[a-z0-9_-]+\.html", urlsplit(url).path):
            raise ValueError("NovelFull URLs must point to /novel-name.html")
        if urlsplit(url).query:
            raise ValueError("NovelFull URL must not include query parameters")
        return site, url
    raise ValueError(f"Unsupported website: {site}. Supported: {', '.join(SITES)}")


def catalogue_entries(registry: dict, curated: dict) -> list[dict]:
    entries = []
    for record in list(registry.get("novels", [])) + list(curated.get("novels", [])):
        title, url = record.get("title"), record.get("url")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Catalogue novel has no title")
        site, url = _validated_url(url)
        entries.append({"title": title.strip(), "url": url, "site": site})
    return entries


def read_curated(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "novels": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("novels"), list):
        raise ValueError("Invalid curated_novels.json format")
    return data


def parse_names(raw: str, names: list[str]) -> list[str]:
    """Allow comma lists, plus semicolon/newline for titles containing commas."""
    known = {_normal_name(name) for name in names}
    parts = []
    for segment in re.split(r"[;\r\n]+", raw or ""):
        segment = segment.strip()
        if not segment:
            continue
        if _normal_name(segment) in known:
            parts.append(segment)
        else:
            parts.extend(part.strip() for part in segment.split(",") if part.strip())
    return parts


def selection_plan(
    registry: dict, curated: dict, names: str, urls: str, website: str = "All",
    chapter_range: str = "", force: bool = False,
    confirm_rights: bool = False,
) -> dict:
    if website not in WEBSITE_CHOICES:
        raise ValueError(f"Website must be one of: {', '.join(WEBSITE_CHOICES)}")
    entries = catalogue_entries(registry, curated)
    requested_names = parse_names(names, [e["title"] for e in entries])
    requested_urls = parse_novel_urls(urls) if urls.strip() else []
    if not requested_names and not requested_urls:
        raise ValueError("Choose at least one novel name or paste at least one novel URL")
    chosen: dict[str, dict] = {}
    for name in requested_names:
        candidates = [
            item for item in entries
            if _normal_name(item["title"]) == _normal_name(name)
            and (website == "All" or item["site"] == website)
        ]
        unique = {item["url"]: item for item in candidates}
        if not unique:
            available = sorted({
                item["title"] for item in entries
                if website == "All" or item["site"] == website
            })
            near = get_close_matches(name, available, n=3, cutoff=0.5)
            suffix = f" Possible matches: {', '.join(near)}." if near else ""
            raise ValueError(
                f"Unknown novel name {name!r} for {website}. "
                f"Add it to curated_novels.json or paste its exact URL.{suffix}"
            )
        if len(unique) > 1:
            # A verified NovelFull listing wins over alternate-source
            # catalogue records. Never invent a URL or guess between two
            # different NovelFull records for the same title.
            novelfull = [item for item in unique.values()
                         if item["site"] == "NovelFull"]
            if len(novelfull) == 1:
                item = novelfull[0]
            else:
                raise ValueError(
                    f"Ambiguous novel name {name!r} matches multiple URLs. "
                    "Paste the novel's exact URL instead."
                )
        else:
            item = next(iter(unique.values()))
        chosen[item["url"]] = item
    for raw in requested_urls:
        site, url = _validated_url(raw)
        if website != "All" and website != site:
            raise ValueError(
                f"URL {url} is from {site}, but website filter is {website}"
            )
        item = next((entry for entry in entries if entry["url"] == url), None)
        chosen[url] = item or {"url": url, "title": url.rsplit("/", 1)[-1], "site": site}
    if not confirm_rights:
        raise ValueError(
            "All downloads in this public repository require explicit permission "
            "to archive and publicly share every selected artefact; a public "
            "listing or free-to-read page is not permission"
        )
    rng = normalise_range(chapter_range)
    wuxia_selected = sum(item["site"] == "WuxiaClick" for item in chosen.values())
    if wuxia_selected:
        if not confirm_rights:
            raise ValueError(
                "WuxiaClick requires explicit permission to archive the work")
        if rng == "all":
            raise ValueError(
                "WuxiaClick has a 20-chapter/day signed-out offline allowance. "
                "Select an explicit inclusive range of at most 20 chapters")
        lower, upper = map(int, rng.split("-"))
        if (upper - lower + 1) * wuxia_selected > 20:
            raise ValueError(
                "WuxiaClick bulk selection exceeds the 20-chapter daily "
                "signed-out download allowance; reduce range or WuxiaClick books")
    if any(item["site"] == "Scribble Hub" for item in chosen.values()):
        if not confirm_rights:
            raise ValueError(
                "Scribble Hub cross-post downloads require the explicit "
                "I confirm I have permission to archive checkbox"
            )
        if rng != "all":
            raise ValueError(
                "Scribble Hub's verified cross-post downloader supports full "
                "novels only; leave the chapter range blank"
            )
    groups = {site: [] for site in SITES}
    skipped = []
    for item in sorted(chosen.values(), key=lambda i: (i["site"], i["title"].casefold(), i["url"])):
        payload = {
            "novel_url": item["url"],
            "chapter_range": "" if rng == "all" else rng,
            "force": bool(force),
            "title": item["title"],
        }
        if not force and already_available(registry, item["url"], rng):
            skipped.append({"site": item["site"], **payload})
        else:
            groups[item["site"]].append(payload)
    scheduled = sum(len(group) for group in groups.values())
    if scheduled > MAX_BATCH_TITLES:
        raise ValueError(
            f"Each bulk workflow run is limited to {MAX_BATCH_TITLES} new novel "
            f"titles, but {scheduled} were selected. Split the submission into "
            "separate resumable runs; already-available novels do not count."
        )
    if scheduled > MAX_MATRIX_JOBS:
        raise ValueError(
            f"GitHub Actions permits at most {MAX_MATRIX_JOBS} matrix jobs per "
            f"workflow run, but {scheduled} new downloads were selected."
        )
    return {
        "version": 1, "website": website, "range": rng,
        "groups": groups, "skipped": skipped,
        "selected_count": len(chosen),
    }


def retry_selection_plan(
    registry: dict, curated: dict, manifest: dict, *,
    confirm_rights: bool = False, expected_run_id: str = "",
) -> dict:
    """Reschedule ONLY missing/failed books, preserving the requested range.

    A recovery manifest is produced after the previous bulk run has verified
    every recovered book. Never accept a legacy manifest without range data:
    guessing would accidentally fetch full books instead of requested ranges.
    """
    if not isinstance(manifest, dict) or manifest.get("version") != 1:
        raise ValueError("Expected a version-1 bulk recovery manifest")
    previous = manifest.get("run_id")
    if expected_run_id and (
        not expected_run_id.isdecimal() or str(previous) != expected_run_id
    ):
        raise ValueError("The retry manifest does not match the requested GitHub run ID")
    missing = manifest.get("missing_or_failed")
    if not isinstance(missing, list):
        raise ValueError("Retry manifest is missing a failed/missing novels list")
    if not missing:
        raise ValueError("No failed or missing novels remain to retry")
    if len(missing) > MAX_BATCH_TITLES:
        raise ValueError(
            f"A retry run is limited to {MAX_BATCH_TITLES} missing novels; "
            "split the recovery into separate runs"
        )
    if len(missing) > MAX_MATRIX_JOBS:
        raise ValueError("A retry run cannot exceed the GitHub matrix job limit")
    urls: list[str] = []
    seen: set[str] = set()
    ranges: set[str] = set()
    for item in missing:
        if not isinstance(item, dict) or "chapter_range" not in item:
            raise ValueError(
                "The recovery manifest predates range-aware retry; cannot "
                "safely infer the original chapter ranges"
            )
        raw = item.get("url")
        if not isinstance(raw, str) or not raw:
            raise ValueError("The recovery manifest has an invalid novel URL")
        site, url = _validated_url(raw)
        if item.get("site") != site:
            raise ValueError("Retry manifest source-site identity mismatch")
        if url in seen:
            raise ValueError("Duplicate failed novel in recovery manifest")
        seen.add(url)
        urls.append(url)
        rng = normalise_range(item["chapter_range"])
        ranges.add(rng)
        if type(item.get("force", False)) is not bool:
            raise ValueError("Retry manifest contains an invalid original Force flag")
    if len(ranges) != 1:
        raise ValueError(
            "The previous bulk run used different chapter ranges; "
            "retry the groups separately to preserve exact ranges"
        )
    rng = next(iter(ranges))
    # Retry is intentionally NOT forceful. Cached valid successful artefacts
    # from another run must be skipped, regardless of the previous Force flag.
    plan = selection_plan(
        registry, curated, "", " ".join(urls), "All",
        "" if rng == "all" else rng,
        force=False, confirm_rights=confirm_rights,
    )
    plan["retry_from_run_id"] = str(previous or "")
    return plan


def _output(key: str, value: str) -> None:
    file = os.environ.get("GITHUB_OUTPUT")
    if file:
        with open(file, "a", encoding="utf-8") as handle:
            handle.write(f"{key}={value}\n")


def write_actions(plan: dict) -> None:
    for site, prefix in (
        ("NovelFull", "novelfull"),
        ("FreeWebNovel", "freewebnovel"),
        ("ReadNovelFull", "readnovelfull"),
        ("WuxiaClick", "wuxiaclick"),
        ("Scribble Hub", "scribblehub"),
    ):
        group = plan["groups"][site]
        _output(f"has_{prefix}", "true" if group else "false")
        _output(f"{prefix}_matrix", json.dumps({
            "include": [
                {k: row[k] for k in ("novel_url", "chapter_range", "force")}
                for row in group
            ]
        }, separators=(",", ":")))
    messages = [
        "## Library bulk download",
        "",
        f"Selected: {plan['selected_count']}; skipped (artifact available): {len(plan['skipped'])}.",
    ]
    for site in SITES:
        lines = plan["groups"][site]
        messages.extend(["", f"### {site} ({len(lines)} to download)"])
        messages.extend(f"- {item['title']} ({item['chapter_range'] or 'all'})" for item in lines)
    if plan["skipped"]:
        messages.extend(["", "### Already available"])
        messages.extend(f"- {item['site']}: {item['title']}" for item in plan["skipped"])
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("\n".join(messages) + "\n")
    print("\n".join(messages))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "list"))
    parser.add_argument("--names", default="", help="Comma, semicolon or newline separated saved novel names")
    parser.add_argument(
        "--urls", default="",
        help="Novel URLs from any supported source, separated by commas or whitespace",
    )
    # Retain this optional legacy CLI filter for existing scripts; the
    # GitHub Actions bulk form does not display or pass a website selector.
    parser.add_argument("--website", default="All", choices=WEBSITE_CHOICES,
                        help="Optional legacy CLI-only source filter")
    parser.add_argument("--chapter-range", default="")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--confirm-rights", action="store_true",
        help=("Required for every source: permission to archive and publicly "
              "share each resulting artefact from this public repository"),
    )
    parser.add_argument("--registry", type=Path, default=Path("downloaded_novels.json"))
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    parser.add_argument("--plan-file", type=Path, default=Path("library_bulk_plan.json"))
    parser.add_argument(
        "--retry-manifest", type=Path,
        help="Recovery manifest from an earlier bulk run; retry only failed/missing novels",
    )
    parser.add_argument("--retry-run-id", default="", help="Verify the source run ID")
    args = parser.parse_args(argv)
    try:
        registry = read_registry(args.registry)
        curated = read_curated(args.catalogue)
        if args.action == "list":
            for site in SITES:
                print(f"\n{site}")
                unique = sorted({e["title"] for e in catalogue_entries(registry, curated)
                                 if e["site"] == site}, key=str.casefold)
                print("\n".join(f"- {title}" for title in unique) or "(no saved novels)")
            return 0
        if args.retry_manifest is not None:
            if (args.names.strip() or args.urls.strip() or
                    args.chapter_range.strip() or args.website != "All" or args.force):
                raise ValueError(
                    "Retry from previous run cannot be mixed with titles, URLs, "
                    "chapter ranges, website filters or Force"
                )
            prior = json.loads(args.retry_manifest.read_text(encoding="utf-8"))
            plan = retry_selection_plan(
                registry, curated, prior,
                confirm_rights=args.confirm_rights,
                expected_run_id=args.retry_run_id,
            )
        else:
            if args.retry_run_id:
                raise ValueError("--retry-run-id requires --retry-manifest")
            plan = selection_plan(
                registry, curated, args.names, args.urls,
                args.website, args.chapter_range, args.force, args.confirm_rights,
            )
        args.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
        write_actions(plan)
        return 0
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Dispatch small, independently tracked pilot downloads from reviewed Yup titles.

The public campaign file is an *explicit verified-URL allowlist*, not an
automatic site search or a substitute for source and archiving permissions.
Only request files newly added by this push may be dispatched.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

CAMPAIGN = "yup-pilot-20261118"
ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "campaigns" / "yup-pilot" / "verified-urls.json"
REQUEST_DIR = ROOT / "campaigns" / "yup-pilot" / "requests"
REGISTRY = ROOT / "downloaded_novels.json"
WORKFLOW = "library-bulk-download.yml"
MAX_BATCH_BOOKS = 2
MAX_PUSH_BATCHES = 3
ALLOWED_HOSTS = {"novelfull.com", "freewebnovel.com"}


class CampaignError(ValueError):
    """Invalid, stale or unsafe download request."""


def _book_url(value: object) -> str:
    if not isinstance(value, str) or len(value) > 280:
        raise CampaignError("Source URL missing or oversized")
    try:
        p = urlsplit(value)
        port = p.port
    except ValueError as exc:
        raise CampaignError("Malformed source URL") from exc
    if (p.scheme != "https" or p.hostname not in ALLOWED_HOSTS
            or port is not None or p.username or p.password or p.query or p.fragment
            or not p.path.startswith("/") or p.path == "/"
            or any(token in p.path.lower() for token in ("chapter-", "/chapter/"))):
        raise CampaignError("Only direct HTTPS book links on approved public sources are permitted")
    return value


def _read_json(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > 30_000:
        raise CampaignError("Missing or oversized campaign file")
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise CampaignError("Campaign JSON must be an object")
    return doc


def manifest_entries(doc: dict) -> dict[str, str]:
    if (set(doc) != {"version", "campaign", "entries"} or doc["version"] != 1
            or doc["campaign"] != CAMPAIGN or not isinstance(doc["entries"], list)
            or not 1 <= len(doc["entries"]) <= 24):
        raise CampaignError("Unexpected campaign URL allowlist format")
    result = {}
    used = set()
    for item in doc["entries"]:
        if not isinstance(item, dict) or set(item) != {"title", "url"}:
            raise CampaignError("Invalid verified book entry")
        title = item["title"]
        if not isinstance(title, str) or not (3 <= len(title) <= 220) or title in result:
            raise CampaignError("Duplicate or invalid verified book title")
        url = _book_url(item["url"])
        if url in used:
            raise CampaignError("A source URL cannot identify multiple campaign books")
        used.add(url)
        result[title] = url
    return result


def prepare_batches(changed_paths: list[str], manifest: dict, registry: dict) -> list[tuple[str, list[str]]]:
    """Preflight every request before dispatching even one Actions run."""
    allowed = manifest_entries(manifest)
    if not isinstance(registry.get("novels"), list):
        raise CampaignError("Invalid downloader completion registry")
    if not 1 <= len(changed_paths) <= MAX_PUSH_BATCHES or len(set(changed_paths)) != len(changed_paths):
        raise CampaignError("Expected one to three distinct newly added request files")
    completed = {
        item.get("url") for item in registry["novels"]
        if isinstance(item, dict) and any(
            isinstance(download, dict)
            and download.get("range") == "all"
            and download.get("status") == "complete"
            for download in item.get("downloads", [])
        )
    }
    selected, groups = set(), []
    for raw in sorted(changed_paths):
        path = Path(raw)
        if (path.is_absolute() or len(path.parts) != 4
                or tuple(path.parts[:3]) != ("campaigns", "yup-pilot", "requests")
                or path.suffix != ".json"
                or not path.name.startswith("batch-")):
            raise CampaignError("Requests must be NEW campaign batch JSON files")
        document = _read_json(ROOT / path)
        if (set(document) != {"campaign", "titles"} or document["campaign"] != CAMPAIGN
                or not isinstance(document["titles"], list)
                or not 1 <= len(document["titles"]) <= MAX_BATCH_BOOKS):
            raise CampaignError("Each pilot batch must contain one or two approved books")
        urls = []
        for title in document["titles"]:
            if not isinstance(title, str) or title not in allowed:
                raise CampaignError("Book title is absent from the approved Yup source URL allowlist")
            if title in selected:
                raise CampaignError("One book is selected in multiple batches")
            selected.add(title)
            url = allowed[title]
            if url not in completed:
                urls.append(url)
        groups.append((path.name, urls))
    return groups


def dispatch(groups: list[tuple[str, list[str]]], *, runner=subprocess.run, sleeper=None) -> int:
    """Each nonempty group runs its own independent GitHub Actions workflow."""
    if sleeper is None:
        import time
        sleeper = time.sleep
    count = 0
    for label, urls in groups:
        if not urls:
            print("Skipped already complete:", label, flush=True)
            continue
        if count:
            # Avoid a burst of workflow dispatches; child workers have their
            # own source pacing and concurrency controls.
            sleeper(75)
        runner(
            ["gh", "workflow", "run", WORKFLOW, "--ref", "main",
             "--field", "novel_urls=" + ",".join(urls),
             "--field", "chapter_range=", "--field", "force=false"],
            cwd=ROOT, check=True,
        )
        count += 1
        print("Dispatched independent small bulk workflow:", label,
              "novels:", len(urls), flush=True)
    return count


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths-file", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    # Even an inadvertent 'Re-run jobs' must not create duplicate new batches.
    if os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_RUN_ATTEMPT", "1") != "1":
        print("Re-run detected. Refusing duplicate campaign dispatch.")
        return 0
    path = args.paths_file
    if not path.is_file() or path.stat().st_size > 10_000:
        raise CampaignError("Missing or oversized changed-request list")
    paths = [p.strip() for p in path.read_text(encoding="utf-8").splitlines() if p.strip()]
    if not paths:
        print("No new campaign requests in this push")
        return 0
    groups = prepare_batches(paths, _read_json(MANIFEST), _read_json(REGISTRY))
    if args.dry_run:
        print(json.dumps({
            "mode": "DRY RUN", "batch_count": len(groups),
            "new_novels": sum(len(urls) for _, urls in groups),
            "already_complete_batches": sum(not urls for _, urls in groups),
        }, sort_keys=True))
        return 0
    count = dispatch(groups)
    print("Independent GitHub Actions pipelines dispatched:", count)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CampaignError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        print("Yup campaign dispatch stopped:", exc, file=sys.stderr)
        raise SystemExit(1)

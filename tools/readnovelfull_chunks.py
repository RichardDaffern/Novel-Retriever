#!/usr/bin/env python3
"""ReadNovelFull adapter for existing resumable, validated chapter batch jobs."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from tools import chunked_download as batches
from tools.readnovelfull_source import HOLLYWOOD_BOOK, discover, validate_book_url


def _output(key: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


def plan_download(url: str, chapter_range: str, chunk_size: int,
                  plan_file: Path, *, discoverer=discover) -> dict:
    url = validate_book_url(url)
    if not 1 <= chunk_size <= 100:
        raise ValueError("ReadNovelFull batch size must be 1-100")
    details = (discoverer(url, allow_verified_prefix=True)
               if url == HOLLYWOOD_BOOK and chapter_range.strip() else discoverer(url))
    plan = batches.chapter_plan(url, details["numChapters"], chapter_range, chunk_size)
    # Do not increase source load with many concurrent chapter batches.
    plan["parallelism"] = min(2, plan["parallelism"])
    plan_file.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    _output("matrix", json.dumps({"include": plan["pieces"]}, separators=(",", ":")))
    for key in ("key", "first", "last", "parallelism"):
        _output(key, str(plan[key]))
    print(f"ReadNovelFull: {details['title']}, {details['numChapters']} chapters; "
          f"{len(plan['pieces'])} batches, {plan['parallelism']} parallel")
    return plan


def fetch_batch(url: str, key: str, first: int, last: int,
                folder: Path, scratch: Path, *, timeout_minutes=65,
                force=False, runner=subprocess.run) -> None:
    url = validate_book_url(url)
    if (key != batches.identity(url) or first < 1 or last < first
            or last - first + 1 > 100):
        raise ValueError("Invalid ReadNovelFull batch identity or range")
    if not force and batches.reuse_complete_piece(folder, url, key, first, last):
        return
    command = [
        sys.executable, "-u", "-m", "tools.readnovelfull_downloader", url,
        "--chapter-range", f"{first}-{last}",
        "--output-dir", str(scratch), "--confirm-rights",
    ]
    runner(command, check=True, timeout=timeout_minutes * 60)
    files = list(scratch.rglob("metadata.json"))
    if len(files) != 1:
        raise ValueError(f"Expected one validated book, found {len(files)}")
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copytree(files[0].parent, folder / "book", dirs_exist_ok=True)
    (folder / "part.json").write_text(json.dumps({
        "version": 1, "url": url, "key": key,
        "start": first, "end": last,
    }, indent=2) + "\n", encoding="utf-8")
    batches.validate_piece(folder, url, key, first, last)
    print(f"VERIFIED ReadNovelFull batch {first}-{last}", flush=True)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("plan", "fetch", "assemble"))
    p.add_argument("--url", required=True)
    p.add_argument("--chapter-range", default="")
    p.add_argument("--chunk-size", type=int, default=50)
    p.add_argument("--key", default="")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--end", type=int, default=0)
    p.add_argument("--force", action="store_true")
    p.add_argument("--timeout-minutes", type=int, default=65)
    p.add_argument("--plan-file", type=Path, default=Path("chapter_plan.json"))
    p.add_argument("--output-dir", type=Path, default=Path("part"))
    p.add_argument("--scratch-dir", type=Path, default=Path("scratch"))
    p.add_argument("--chunks-dir", type=Path, default=Path("completed_batches"))
    args = p.parse_args(argv)
    try:
        url = validate_book_url(args.url)
        if args.action == "plan":
            plan_download(url, args.chapter_range, args.chunk_size, args.plan_file)
        elif args.action == "fetch":
            fetch_batch(url, args.key, args.start, args.end,
                        args.output_dir, args.scratch_dir,
                        force=args.force, timeout_minutes=args.timeout_minutes)
        else:
            plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
            if plan.get("url") != url:
                raise ValueError("Cannot assemble chapters belonging to another book")
            batches.assemble(plan, args.chunks_dir, args.output_dir)
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"ReadNovelFull workflow stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

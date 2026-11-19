"""Resume only the 58 held Yup listings from the verified overnight queue.

The inputs are trusted GitHub Actions artifacts from fixed, completed runs.
Validate every held book against the original discovery record before passing
it to the existing paced dispatcher. No new URLs are guessed or requested.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools import overnight_queue as queue

SOURCE_RUN_ID = 44374654975
DISPATCH_RUN_ID = 44379714549
VERIFIED_YUP_COUNT = 108
PREVIOUSLY_SUBMITTED = 50
EXPECTED_HELD = 58


def prepare_remaining(source: dict, previous: dict, known_titles: set[str]) -> dict:
    """Check provenance and exclude registered or already-requested titles."""
    if (source.get("version") != 1
            or source.get("campaign") != queue.CAMPAIGN
            or source.get("summary", {}).get("verified") != 158
            or source.get("summary", {}).get("global_exclusions_checked") != 90
            or not isinstance(source.get("verified"), list)
            or previous.get("version") != 1
            or previous.get("campaign") != queue.CAMPAIGN
            or previous.get("tier") != "Yup"
            or previous.get("approved_source_count") != VERIFIED_YUP_COUNT
            or previous.get("reason") != "overnight_dispatch_budget_exhausted"
            or not isinstance(previous.get("submitted"), list)
            or len(previous["submitted"]) != PREVIOUSLY_SUBMITTED // 2
            or not isinstance(previous.get("held"), list)
            or len(previous["held"]) != EXPECTED_HELD):
        raise queue.QueueError("Original verified sources or held-run provenance changed")

    yup = {}
    for item in source["verified"]:
        if not isinstance(item, dict):
            raise queue.QueueError("Invalid discovered-book record")
        if item.get("tier") != "Yup":
            continue
        title, url = item.get("title"), item.get("url")
        if (not isinstance(title, str) or not isinstance(url, str)
                or item.get("evidence") != "public_listing_exact_title"
                or url not in queue.candidate_urls(title)
                or queue.norm(title) in yup):
            raise queue.QueueError("Untrusted or duplicate Yup discovery entry")
        yup[queue.norm(title)] = item
    if len(yup) != VERIFIED_YUP_COUNT:
        raise queue.QueueError("Verified Yup source count changed")

    submitted = set()
    for batch in previous["submitted"]:
        if (not isinstance(batch, dict)
                or not isinstance(batch.get("titles"), list)
                or not isinstance(batch.get("urls"), list)
                or len(batch["titles"]) != 2 or len(batch["urls"]) != 2):
            raise queue.QueueError("Invalid previously submitted download group")
        for title, url in zip(batch["titles"], batch["urls"]):
            key = queue.norm(title)
            if key in submitted or key not in yup or yup[key]["url"] != url:
                raise queue.QueueError("Prior dispatched title disagrees with discovery")
            submitted.add(key)
    if len(submitted) != PREVIOUSLY_SUBMITTED:
        raise queue.QueueError("Previously submitted title count changed")

    held_seen = set()
    pending = []
    for item in previous["held"]:
        if not isinstance(item, dict):
            raise queue.QueueError("Invalid held novel entry")
        title, url = item.get("title"), item.get("url")
        key = queue.norm(title)
        if (key in submitted or key in held_seen or key not in yup
                or url != yup[key]["url"] or item != yup[key]):
            raise queue.QueueError("Held novel differs from verified original listing")
        held_seen.add(key)
        if key not in known_titles:
            pending.append(item)

    if (len(held_seen) != EXPECTED_HELD
            or held_seen | submitted != set(yup)):
        raise queue.QueueError("Verified source partition is incomplete or duplicated")

    return {
        "version": 1,
        "campaign": queue.CAMPAIGN,
        "source_run_id": SOURCE_RUN_ID,
        "held_from_run_id": DISPATCH_RUN_ID,
        "verified": pending,
        "already_known_skipped": EXPECTED_HELD - len(pending),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        _, _, _, known_titles = queue.manifests()
        result = prepare_remaining(
            queue.read_json(args.source),
            queue.read_json(args.previous),
            known_titles,
        )
        args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        print(json.dumps({"verified_held": EXPECTED_HELD,
                          "to_dispatch": len(result["verified"]),
                          "already_known_skipped": result["already_known_skipped"]}))
        return 0
    except (queue.QueueError, ValueError, OSError) as exc:
        parser.exit(1, f"Remaining Yup recovery stopped: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())

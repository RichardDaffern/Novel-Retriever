#!/usr/bin/env python3
"""Fail-closed permission gate for public GitHub Actions archive artefacts.

This validates that the workflow has an explicit rights confirmation and a
separate HTTPS evidence URL. It does not fetch or interpret the evidence page:
the caller must independently verify that it grants the rights needed for
public archiving and sharing. A public book listing is not evidence.
"""
from __future__ import annotations

import argparse
import re
from urllib.parse import urlsplit


def _canonical(value: str) -> str:
    parts = urlsplit(value.strip())
    if (
        parts.scheme.lower() != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.port is not None
        or parts.fragment
    ):
        raise ValueError("Rights evidence must be a clean HTTPS URL without credentials, port or fragment")
    return parts._replace(
        scheme="https", netloc=parts.netloc.lower()
    ).geturl()


def validate_rights_evidence(
    confirm_rights: str | bool,
    evidence_url: str,
    source_urls: str = "",
) -> str:
    confirmed = str(confirm_rights).strip().lower() in {"true", "1", "yes"}
    if not confirmed:
        raise ValueError(
            "Public archive blocked: explicitly confirm rights to archive and publicly share every selected work"
        )
    if not isinstance(evidence_url, str) or not evidence_url.strip():
        raise ValueError(
            "Public archive blocked: provide a separate author/rights-holder permission or licence URL"
        )
    evidence = _canonical(evidence_url)
    sources = [
        item.strip()
        for item in re.split(r"[,;\\s]+", source_urls or "")
        if item.strip()
    ]
    for source in sources:
        try:
            if _canonical(source) == evidence:
                raise ValueError(
                    "A public book listing cannot be used as rights evidence; provide a separate permission or licence page"
                )
        except ValueError as exc:
            if "public book listing" in str(exc):
                raise
            # Ignore malformed source tokens here; the source-specific URL
            # validator reports those with its more precise error.
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-rights", required=True)
    parser.add_argument("--evidence-url", required=True)
    parser.add_argument("--source-urls", default="")
    args = parser.parse_args(argv)
    try:
        evidence = validate_rights_evidence(
            args.confirm_rights, args.evidence_url, args.source_urls
        )
    except ValueError as exc:
        parser.error(str(exc))
    print("Explicit rights confirmation accepted for workflow gating.")
    print(f"Evidence URL recorded for manual review: {evidence}")
    print("The evidence URL is not automatically verified by this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

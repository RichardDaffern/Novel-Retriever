"""Compatibility entry point for workflow runs pinned to older source revisions.

Historical bulk workflows invoke this filename; the maintained implementation
lives in the bulk download recovery module.
"""
from tools.bulk_download_recovery import main


if __name__ == "__main__":
    raise SystemExit(main())

"""Compatibility entry point for workflow runs pinned to older source revisions.

Historic bulk runs call `python -m tools.bulk_recovery`, while the
implementation is `tools.bulk_download_recovery`.
"""
from tools.bulk_download_recovery import main


if __name__ == "__main__":
    raise SystemExit(main())

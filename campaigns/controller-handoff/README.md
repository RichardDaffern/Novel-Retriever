# Completed novels hand-off to Taiyou Storage Controller

## Scope and safe format

- **Snapshot:** 19 November 2026, around 10:30 IST.
- **104** completed full-book download records from the recent campaign and pilot batches, starting 18 November 2026 16:00 UTC.
- **Source:** `downloaded_novels.json`, restricted to records marked `status: complete`, `range: all`, with actual GitHub artifact and run IDs.
- **Manifest:** [completed-20261119.json](completed-20261119.json) is in the same **registry schema** understood by `tools/download_all_artifacts.ps1`. It is **not** an EPUB and **not** itself uploadable to Hugging Face.
- Previously completed books outside this period are omitted. More novels are downloading; use the live registry for later completions.

## Windows: produce Controller-ready ZIPs

Install and authenticate GitHub CLI (`gh auth login`) and keep up-to-date local checkouts of both repositories.

From inside `Novel-Retriever` (adjust the sibling Controller path if different):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\tools\download_all_artifacts.ps1" -RegistryFile ".\campaigns\controller-handoff\completed-20261119.json" -Destination "..\Taiyou-Novels-Storage-Controller\novels"
```

The downloader reads the **104 records in this snapshot**, fetches each specific completed artifact, validates and repacks it as an **individual novel ZIP** directly into the Controller's `novels/` input directory. Existing valid ZIPs are reused. It never fetches incomplete-book chapter-batch artifacts. This command does not upload to Hugging Face.

Optional pilot: append `-Limit 5` to process just five alphabetically first; then run without that argument to fetch the remainder. GitHub artifacts expire, so any unavailable archives are reported separately and never treated as complete local ZIPs.

## Preview before uploading

From inside `Taiyou-Novels-Storage-Controller`:

```powershell
.\01_bulk_upload.cmd
```

This invokes `py -m taiyou_storage.upload novels --dedupe-local --interactive`. Preview changes, check that the target dataset is PRIVATE, and approve only after examining conflicts. Identical existing titles/EPUBs are skipped or preserved without overwriting personal ratings, progress or comments. Conflicting editions block uploads; do not use a forced overwrite. The uploader does not delete local ZIPs.

**Do not put the registry JSON, the outer consolidated GitHub export ZIP, or unfinished chapter-range artifacts in `novels/`.** Only the per-book ZIPs produced by the Retriever downloader belong there.

## After this snapshot

The remaining 58 source-verified Yup novels are being dispatched through [the separate continuation](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44463492638). Check later runs and repeat a new manifest/export after their individual downloads and registry entries are complete. Do not assume that the current 104-book snapshot includes books from that ongoing batch.

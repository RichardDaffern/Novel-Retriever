# Cover resolution and duplicate handling

This is the source-acquisition repository, not the private Hugging Face uploader.

## Cover contract

Every dedicated site workflow (NovelFull, FreeWebNovel, ReadNovelFull,
WuxiaClick and the authorised Scribble Hub cross-post) finalises the complete
book with the common cover_pipeline command before upload.
Bulk recovery uses --resolve-covers; completed GitHub archive exports also
finalise every selected ZIP. The existing cover-only workflow stays available.

Resolution order: embedded EPUB image; validated existing cover.jpg or
cover.png; optional cache keyed by canonical source URL; the exact novel
source page; an explicitly verified cross-source URL matching **both** title
and author. No search-by-title or generic placeholder covers are permitted.
JPEG/PNG are kept in their original format; WebP/GIF are converted to JPEG.
The 8 MiB, 20-million-pixel and minimum-dimension checks are enforced.

The result is recorded in metadata.json as:

- cover_status: available or missing.
- cover_provenance: method, optional image_url, sha256, embedded.
- cover_pipeline_version: 2.
- cover_warnings: optional reasons for unsuccessful attempts.

Missing covers do **not** make a complete novel a failed download. A valid
standalone cover remains usable even when EPUB embedding fails. Chapter text
and chapters.json are not rewritten.

To repair older packages locally, run:

~~~powershell
python -m pip install -r requirements.lock
python -m tools.cover_pipeline --zip ".\novels\One Novel.zip"
python -m tools.cover_pipeline --directory ".\downloads"
~~~

Use --offline to avoid websites; --cache-dir .\cover-cache to reuse across
runs. Set --verified-sources to an explicitly reviewed JSON map, for example:

~~~json
{
  "https://freewebnovel.com/novel/example": {
    "url": "https://novelfull.com/example.html",
    "title": "Exact Novel Title",
    "author": "Exact Author"
  }
}
~~~

No fallback mapping is shipped without verified evidence. Do not infer a
cross-post from title similarity.

## Deduplicating old and new ZIPs

**Keep older ZIPs**. Extract the consolidated GitHub Actions ZIP first, then
copy its individual novels/*.zip into the same local input directory as the
older archives. Existing input archives are never deleted by this tool.

~~~powershell
python -m tools.novel_dedupe --input ".\novels" --output ".\unique-novels"
~~~

Inspect unique-novels/manifest.json. Preferred one-per-book packages are
in unique-novels/novels/; materially different versions are in
unique-novels/review-conflicts/ and must be examined manually. Invalid
archives are reported, not silently imported. Exit code 2 signifies
conflicts or invalid inputs; the output remains available for inspection.

Identity is based first on canonical source URL, then normalised title and
author when URL is absent. EPUB SHA-256, chapter positions and chapter
SHA-256 identify equivalent content despite changed ZIP filenames or EPUB
cover metadata. Verified contained chapter ranges are recognised as
redundant. Different chapters/editions are retained for review. A verified
longer copy is favoured; equivalent complete versions favour a valid cover
then later source creation time.

The GitHub consolidated exporter uses the same deduplication engine, records
the original GitHub artifact name in its manifest, and caches downloaded
GitHub artifact ZIPs locally. Failed/expired artifacts are reported without
discarding other successful downloads. Chapter-range checkpoints already
support resuming without reacquiring complete verified batches.

**Important:** The Storage Controller's default strict mode still rejects
multiple ZIPs targeting the same book. It now also offers an explicit
`--dedupe-local` mode for mixed older and newer ZIPs (Windows menu option
12). Preview first. Conflicting editions still block every remote write.
See the [implemented Storage Controller integration](storage-controller-integration-handover.md).
The Retriever's local consolidation never modifies any input archive.

## Compatibility

Existing GitHub workflow filenames, EPUB layout, chapter manifests,
metadata fields, standalone cover downloader, storage repository and
private HF dataset remain unchanged. New metadata fields are additive.
Existing GitHub Actions artifacts and running jobs are untouched; these
changes apply only to future runs after merge.

All automated tests use local EPUB/ZIP fixtures and mocked HTTP responses;
no website traffic is required in CI. A live smoke test is optional and
must not bypass authorisation, download quotas or site access restrictions.

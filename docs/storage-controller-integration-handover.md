# Storage Controller implementation handover

**Target repository:** https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller

**Scope:** Proposed changes only. This Novel Retriever PR does NOT alter,
merge into, or weaken the Storage Controller's safety rules.

## Observed current behaviour

- taiyou_storage/upload.py::main scans ZIP files from the chosen folder.
- read_novel validates ZIP CRC, embedded EPUB and metadata.
- matching_entry currently prioritises an EPUB-byte-derived ID, then an
  exact normalised title and author. It does not prefer canonical source URL.
- plan raises a CONFLICT when multiple local ZIPs target the same existing
  novel. The entire batch stops before remote writes.
- apply_item revalidates dataset revision and local ZIP digest; its
  parent-commit compare-and-swap must remain in place.
- merged_metadata updates the prior metadata with every new field. Explicit
  field ownership should be introduced to prevent source-import metadata
  from accidentally replacing app-managed fields.

## Required changes in the target repository

1. Add a **local-only, opt-in deduplication preflight** before plan().
   Group ZIPs by canonical HTTPS source URL, then exact normalised
   title/author, with EPUB SHA-256 and chapter position/hash verification.
   Do not group distinct source URLs solely because of a similar title.
   Use the Retriever manifest as advisory provenance, not a trusted override.
2. For byte-identical EPUB or equivalent chapter content, choose one
   preferred ZIP with deterministic tie-breaks: complete validated
   coverage, available genuine cover, then latest verified copy. Report
   skipped duplicates with both original filenames.
3. If multiple versions differ in chapter text, coverage cannot be
   established, author identity is ambiguous, or existing remote data
   contradicts the local version, mark CONFLICT and block **all** writes
   until explicitly resolved. Preserve both local ZIPs.
4. Resolve against the remote catalogue **before assigning a new novel ID**.
   When a confirmed existing record matches, retain its exact ID, paths
   and user-owned metadata. Never derive a replacement ID merely because
   cover embedding or EPUB bytes have changed.
5. Split metadata into source-managed fields (title, author, sourceUrl,
   chapterCount, imported source genres, description, cover provenance)
   and user-managed fields (reading progress, personal tags, rating,
   comments, collections, notes, importedAt, app-specific settings).
   Updates must preserve user-managed values regardless of fields present
   in the new ZIP. Existing remote records remain authoritative.
6. Preserve the current hard stop on ambiguous identities, invalid ZIPs,
   unexpected remote paths, orphaned data, missing catalogue, changed
   dataset revision, concurrent edits and changed local ZIP checksums.
7. Keep the current default safety mode. Introduce --dedupe-local only
   after tests; default to preview. Allow apply only after showing unique,
   duplicates, updates, unchanged and conflicts.
8. For conflict resolution, require a separate explicit operator choice
   and re-preview against the current remote revision. Do not implement
   implicit overwrite or a general force switch.

## Tests needed

- Two older/newer ZIP names with the same source and identical chapters
  produce one candidate and a duplicate report.
- Cover-only EPUB rewrite retains the existing HF ID and all user metadata.
- Different chapter contents/edition of same novel stop the entire upload
  and keep both files.
- Multiple existing IDs with the same title or author are not guessed.
- A source URL match with a different EPUB hash remains the same remote
  identity only after chapter equivalence; otherwise conflict.
- No writes when another client changes the catalogue after preview.
- Invalid ZIP or malicious archive entry blocks all remote writes.
- Current Smart Bulk Upload without the opt-in flag behaves exactly as now.
- Preview and apply with a mocked private HF dataset preserve reader progress,
  ratings, comments, personal tags and collections.

## Coordination and release order

1. Review the Novel Retriever PR and its cover/dedupe manifest contract.
2. Implement Storage Controller preflight in a separate feature branch/PR.
3. Run its existing safety/CI suite and new offline fixtures.
4. First use preview mode against the actual private dataset.
5. Only then consider mixed old/new ZIP imports. Do not manually delete
   old ZIPs or modify HF IDs to work around conflicts.

The new Novel Retriever ZIPs are already suitable for existing Smart Bulk
Upload **when provided as one selected unique archive per novel**.

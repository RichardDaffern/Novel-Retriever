# Historical chapter-artifact recovery inventory, 23 November 2026

This is a **read-only, metadata-only recovery plan** for novels previously identified as absent from the owner's `Available.csv`. It does **not** claim that any book has been reconstructed, that an artefact is safe to redistribute, or that chapter text is valid.

**Machine-readable inventory:** [historical-chapter-artifact-inventory-20261123.json](historical-chapter-artifact-inventory-20261123.json). It records GitHub artifact IDs, source identities, original chapter-plan IDs, complete-batch names, partial-checkpoint names, expected positions and gaps.

## Evidence and exclusions

- Queried the live GitHub Actions artifact list for **13 distinct historic bulk runs** on 23 November 2026. Each was 100 or fewer items and fully represented on the first page. The 15 selected titles map to original source URLs and chapter-plan archives that were opened directly.
- The run lists contain **133 surviving partial-checkpoint artefacts**, alongside saved complete-batch artefacts representing **12,539 chapter positions**. These counts are based on artefact names, not chapter checksum validation, and are **not** a count of new finished books.
- Applied `campaigns/overnight/excluded-90.json` as an explicit hard exclusion and checked exact source URLs against the **343 complete** rows in `downloaded_novels.json`; the inventory lists no exact excluded title or completed source URL. The owner's newer `Available.csv` and original coloured workbook are not attached in this session, so their original earlier classification was not independently re-read.
- All artefacts in the checked pages were marked `expired=false`. This is a time-limited availability observation, not a storage guarantee.
- The repository is public and the sampled old workflows predate the universal rights gate. **Do not download/republish novel content without the relevant rights.** A public source listing or this inventory does not establish permission.

## Prioritised local verification

| Title | Chapter-plan size | Positions covered by complete-batch names | Missing complete-batch positions |
| --- | ---: | ---: | --- |
| Omega Summoner | 3,083 | 3,033 | 2,051–2,100 |
| Legend of Swordsman | 6,493 | 6,293 | 5,601–5,800 |
| Heavenly Star | 335 | 285 | 251–300 |
| Past Life Returner | 575 | 375 | 351–550 |
| Flower Master in the City | 1,553 | 1,253 | 1,101–1,150; 1,201–1,300; 1,401–1,550 |

For the other ten titles, consult the full inventory rather than assuming that a partial checkpoint is a complete chapter batch.

**Actual ZIP inspection, not just artefact names:**

- Omega Summoner: checkpoint artefact `14494694927` (batch 2,051–2,100) has valid ZIP CRC and chapter files **2,051–2,068**. Positions **2,069–2,100** are absent in that checkpoint. This is *not* yet a verified source-content judgement.
- Parasite in Love: checkpoint `14494440316` (batch 1–11) has valid ZIP CRC and **chapter 1** only. Positions **2–11** are absent there.
- A separate sample complete-batch ZIP had `book/chapters.json`, `book/metadata.json`, `book/source.epub` and `part.json`. Its true range was read from `part.json` rather than guessed from a local sample filename.

## Local recovery acceptance procedure

1. **Confirm legal authorisation and isolate output locally.** Do not trigger the public `Library - Bulk Download` workflow or publish a recovered EPUB/ZIP through this repository merely because a checkpoint exists.
2. Download existing artefacts **by ID**, keeping the original ZIP and its artifact ID, run ID, filename and hash together. Use `gh api repos/RichardDaffern/Novel-Retriever/actions/artifacts/<artifact-id>/zip` only where authorised. Never commit chapter text or EPUBs.
3. For each complete batch, open its ZIP without trusting filenames: require matching `part.json` URL/key/range; validate ordered chapter positions, `chapters.json` SHA-256 hashes, non-empty chapter TXT and valid EPUB structure. Reject any identity mismatch, duplicate conflicting chapter or missing manifest.
4. For partial checkpoints, inspect exact chapter filenames and UTF-8 bytes under the checkpoint folder. Check ZIP CRC, chapter range, content quality and conflicting duplicates. Checkpoint files have no verified chapter manifest: mark them **candidates** until individually validated, not accepted complete chapters.
5. Generate a position-by-position coverage report against the original chapter plan. Preserve both successful batches and partial checkpoints. Record exact holes and deterministic source failures. An absent file is missing; do not label it zero-content or fabricate a replacement chapter.
6. If every position is authenticated and coherent, assemble offline using the existing vetted `tools.chunked_download` validation/assembly contracts and validate the final EPUB, chapter hashes, author/edition, count and cover. Only then consider a separate rights-reviewed private import through the Storage Controller.
7. For any remaining holes, use targeted source troubleshooting only after correcting the deterministic TOC/numbering or empty-body failures already tracked in [issue #371](https://github.com/RichardDaffern/Novel-Retriever/issues/371). Do not suppress chapter-identity validation or blindly rerun.

**Do not confuse saved batch labels with a finished novel.** In particular, `Omega Summoner` has 61 complete-batch names and a partial checkpoint for the remaining range; it has **no** verified final archive. Issue #371's previous phrase “successful chapter-batch jobs for the full range” should not be interpreted as every batch having an intact, complete saved archive.

## This campaign's scope

This inventory is intentionally a **snapshot**, not an automatic download campaign. No new source requests, GitHub Actions dispatches, chapter-body publication, Storage Controller changes or private HF writes were performed. New downloads remain subject to exact edition/TOC verification, rights evidence, the 90 global exclusions and the source-specific failure fixes.

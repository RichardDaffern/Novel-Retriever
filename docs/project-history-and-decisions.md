# Project history, architectural decisions and roadmap

**Maintained:** 21 November 2026. This is a durable design/history note, not a live operational dashboard. See [Current Status](current-status.md) for a dated snapshot and [AGENTS.md](../AGENTS.md) for mandatory live-state inspection.

## 1. Original intent and user requirements

The early project brief was to improve the **Novel_Library acquisition and packaging utility only**. The reader, private Hugging Face dataset and Storage Controller were separate systems and were not to be changed as part of Retriever remediation.

The intended outcome is a dependable, local-first Python toolkit and GitHub Actions pipeline that can acquire works the operator is authorised to archive, preserve every expected chapter, and produce portable **EPUB + UTF-8 TXT chapters + JSON manifests/metadata + one-book ZIP** outputs. It also needs to retrieve completed GitHub Actions artefacts on Windows and convert authorised local EPUBs or selectable-text PDFs.

User-approved engineering constraints included:
- Preserve working NovelFull, FreeWebNovel, chapter-batch, Windows retrieval and PDF conversion functionality while improving it.
- Prefer explicit source identity, exact chapter order/count, safe recovery and non-destructive updates over optimistic success.
- Add regression tests for fixes and validate Linux and Windows CI.
- Do not modify the Personal Library, Storage Controller or private Hugging Face data as an incidental side effect.
- Do not bypass logins, paywalls, DRM, CAPTCHA, access challenges, rate limits or source restrictions. Public visibility does not grant permission to archive or redistribute a work.

## 2. Evolution

| Period | Evolution and evidence |
|---|---|
| Early integrity-remediation phase (by 11 Nov 2026) | A review identified URL-slug identity collisions, same-title overwrite risks, interrupted/mixed exports and unsafe cleanup, PDF memory pressure, and incomplete URL validation. The approved remediation focused on preserving old complete outputs, staging/rollback, stronger source identity and Linux/Windows regression tests. |
| Chunked acquisition | Long novels moved from one long-running download into bounded chapter ranges with checkpoints, batch validation and final assembly. A six-novel campaign completed 5,501 chapters; *Golden Time* exposed a single-batch extraction-path defect. The path was fixed and the book reassembled without re-downloading the successful chapter content. |
| Multi-source and local import | Separate source adapters were added for FreeWebNovel and ReadNovelFull, with strict chapter-index checks. WuxiaClick was limited to its published offline allowance. Direct Scribble Hub access was blocked, so only one independently verified same-author FanFiction.net cross-post was enabled. WebNovel remained a constrained metadata/browser experiment and offline saved-page importer, not a general website downloader. |
| Packaging and downstream boundary | EPUB metadata, covers, chapter manifests and SHA-256 checks became part of the output contract. A metadata-only registry records run/artefact references; temporary GitHub Actions artefacts are collected separately by the Windows utility. The Storage Controller alone owns private Hugging Face writes; the Personal Library owns reader UI and reading state. |
| Campaign operations (18-20 Nov) | The Yup and IDK lists, 90 global red/Dropped exclusions and separate 43-title Naruto/Harry Potter fanfiction catalogue were recorded as campaign inputs. Larger campaigns moved towards reviewed exact URLs, bounded batches, duplicate checks and explicit recovery rather than repeated guessed-slug searches. |
| Source audit and integrity preflight (21 Nov) | Read-only discovery was expanded to NovelFull, ReadNovelFull and FreeWebNovel. The audit found 26 book listings among 91 eligible Yup/IDK candidates; a separate five-book TOC preflight passed two indexes and failed three. Neither operation downloaded chapter prose or established archiving rights. See the [source-audit report](https://github.com/RichardDaffern/Novel-Retriever/blob/6674b26c9959d7b2f506cc32dc115975ab30c275/campaigns/overnight/source-audit-report-20261121.md). |

## 3. Architectural decisions and why they exist

| Decision | Reason / invariant |
|---|---|
| Source URL and stable source identity, not display title or slug alone | Different works can share titles or similar slugs; a title match must not overwrite another edition. |
| Independent site adapters and one mixed-site bulk entry point | Site-specific access, chapter numbering, pacing and failure semantics differ; one shared bulk form avoids competing dispatch interfaces. |
| Bounded chapter jobs, checkpoints and validated assembly | Large works can time out. Successful ranges should be reusable without treating partial output as complete. |
| Strict chapter manifests and content hashes | Detect gaps, duplicates, reordered chapters, empty pages, wrong source content and corrupted archives. |
| Staged output and rollback | A failed forced refresh or interrupted export must not destroy the previous known-good book. |
| Metadata-only registry | Git history must not become a novel-content store; registry rows are evidence of a past run, not permanent artefact availability. |
| Explicit source/rights gates and fail-closed parsing | A public page or HTTP 200 does not prove complete access or permission to archive. Do not evade restrictions to make a source work. |
| Separate offline EPUB/PDF import paths | A user-supplied authorised file is a different trust and access model from a live website downloader. |
| Separate Retriever, Storage Controller and Reader responsibilities | Download completion must not silently mutate private cloud storage or personal reading state. |

## 4. Failure lessons retained

- **Identity collisions:** URL path slugs and titles are not globally unique. Preserve canonical source identity and reject ambiguous reuse.
- **Unsafe replacement/cleanup:** Never overwrite a good ZIP/EPUB until the replacement passes validation; stage changes and roll back on failure.
- **Mixed or interrupted exports:** Validate each book independently, preserve successful books and use explicit manifests/checksums. Do not treat a failed multi-book workflow as proof that every child failed.
- **Chapter-index defects:** Duplicate links, non-consecutive numbering, missing chapters, invalid chapter URLs and empty content are integrity failures, not routine transient retries. Repair the source/index parser with a fixture before targeted retry.
- **Real prologues and editorial omissions:** ReadNovelFull prologues need explicit, tested handling. The *I Shall Seal the Heavens* Chapter 690 case required preserving a verified editorial note rather than inventing chapter prose; see [PR #453](https://github.com/RichardDaffern/Novel-Retriever/pull/453) and [PR #454](https://github.com/RichardDaffern/Novel-Retriever/pull/454).
- **Single-batch path assumptions:** *Golden Time* demonstrated that successful multi-batch assembly does not guarantee the single-batch path is correct. Test both paths.
- **PDF resource limits:** Process large PDFs with explicit byte/page budgets and avoid unnecessary whole-file copies. Do not promise OCR; the current converter is for selectable text.
- **Site access is not permission:** WebNovel browser checks encountered access challenges; no general automated chapter downloader was enabled. Scribble Hub direct access returned 403; the single allowlisted author cross-post is not general site support.
- **GitHub Actions are temporary delivery:** An artefact can expire even while its metadata registry row remains. Verify artefact availability independently and keep downstream import status separate.
- **Campaign activation is not completion:** A successful one-shot dispatcher can still select zero, hold candidates or launch failed children. Inspect child runs, final EPUB/ZIP, registry and expiry separately.

## 5. Current priority and roadmap

The following order reflects the user's latest explicit priority. Refresh live counts and issue/run state before execution.

1. **Harry Potter and Naruto fanfiction first.** Reconcile the 43 exact title/author records (24 Naruto, 19 Harry Potter), investigate the 32 requiring source verification, and repair the three previously source-matched but incomplete works. Respect screenshot-truncated names and edition/author identity. Do not use general WebNovel chapter scraping.
2. **Then the 65 unresolved Yup/IDK titles.** Research alternate titles, author and supported source pages from the 21 November audit. The 65 are unresolved by that audit's tested URL patterns, not proven unavailable everywhere.
3. **Review the 26 matched Yup/IDK listings individually.** They are not a ready-to-download batch. Most overlap prior failures; only two of five fresh candidates passed the TOC preflight. Rights, edition and full chapter completeness remain separate gates.
4. **Repair known failures selectively.** Reconcile issues [#452](https://github.com/RichardDaffern/Novel-Retriever/issues/452) and [#448](https://github.com/RichardDaffern/Novel-Retriever/issues/448), and the historical blocked-title manifest, against later PRs and successful runs before retrying. Do not repeat deterministic failures unchanged.
5. **Keep the artefact-to-library handover explicit.** Validate final ZIPs, hashes, cover files and metadata; import through the separate Storage Controller only when requested and authorised. Never infer a private Hugging Face import from a Retriever registry row.
6. **Continue engineering hardening:** deeper archive/EPUB integrity inspection, clear failure summaries, source-adapter fixture coverage, dependency/security maintenance and Windows compatibility. Any proposed source expansion needs permission evidence, stable public chapter indexes, fail-closed parsing and regression tests first.

## 6. Authoritative references

- [AGENTS.md](../AGENTS.md): live-state protocol, detailed architecture, code map, data contracts and coding rules.
- [README.md](../README.md): user-facing purpose and entry points.
- [Operations Runbook](operations-runbook.md): operational checks, workflow use, recovery and downstream handover.
- [Current Status](current-status.md): dated, evidence-linked snapshot only.
- [Website Support](website-support.md): source capability and restrictions.
- [Source feasibility research](research/source-feasibility-2026-11-15.md): historical source assessments.
- [Yup/IDK campaign inputs](https://github.com/RichardDaffern/Novel-Retriever/blob/6674b26c9959d7b2f506cc32dc115975ab30c275/campaigns/yup-pilot/README.md) and [fanfiction catalogue](https://github.com/RichardDaffern/Novel-Retriever/blob/6674b26c9959d7b2f506cc32dc115975ab30c275/campaigns/fanfiction/README.md).
- [Git history](https://github.com/RichardDaffern/Novel-Retriever/commits/main) and open issues/PRs: authoritative for later code changes; always inspect current state.

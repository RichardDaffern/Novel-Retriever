# Novel-Retriever: Deep Technical Handbook for AI Agents and Contributors

> **Purpose:** A detailed, repository-specific orientation for an AI coding agent, developer, maintainer or auditor who needs to work safely and effectively on Novel-Retriever.
>
> **Scope:** Only the `RichardDaffern/Novel-Retriever` repository. This is a **download, acquisition, conversion, validation, packaging, metadata and local retrieval** project, **not** the web reader or the Hugging Face dataset controller.
>
> **Documentation validation point:** Checked against `main` at `17a57dcbd21068ec6be8b85aeb2e2438cacc6577` on 23 November 2026, 00:45 IST. PR #490 merged; post-merge main CI #45061541599 passed 4/4. The 26 exact source matches are triaged (18 Yup, 8 IDK); the five new ReadNovelFull candidates have structural preflight results but zero rights clearances. The 43-title fanfiction research pass is complete through round 18 (8 complete, 3 blocked, 32 researched but rights-unresolved). The 65 unmatched rows have completed their first alternative-source pass; a new alias reconciliation maps `Very Pure And Ambiguous` to the already-registered `So Pure, So Flirtatious`, leaving 51 distinct rows (23 Yup, 28 IDK) after 13 registry aliases and one excluded alias. This is a dated snapshot, not a live-state guarantee.
>
> **Precedence:** For actual behaviour, trust the checked-out implementation and tests first, then active workflow definitions and observed run outputs, then current registry/campaign data, then focused documentation and Git history. Previous conversations, assistant summaries and old status snapshots are leads only. If documentation conflicts with current evidence, investigate and update it in the same change. Never silently treat experimental or historical code as production-ready.

## Mandatory dynamic project-state inspection

**This is required before every substantial task, not an optional orientation step.** Historical documentation, issue comments, saved handovers and prior assistant summaries can become stale within hours when downloads, PRs or campaigns run.

### If a local clone/worktree is available

Run and inspect these commands before editing or dispatching anything:

```bash
git status --short --branch
git branch --show-current
git rev-parse HEAD
git remote -v
git fetch origin
git status --short --branch
git log -15 --date=iso-strict --pretty=format:'%h %ad %d %s'
git diff --stat
git diff --cached --stat
```

- Read the actual dirty/untracked diff before touching files. Do not reset, clean, stash, overwrite or switch away from another agent's work.
- Confirm whether the task branch is based on current `origin/main`; inspect changed files and the complete diff, not only commit messages.
- Inspect relevant source, tests, configuration, workflows and data manifests at the checked-out SHA. Do not infer implementation from a filename or a historical PR title.

### If working through GitHub/API tools without a local clone

Record that local working-tree status is **not observable**. Inspect, at minimum:

1. Repository default branch and exact current `main` SHA; recursive file tree and relevant source/docs at that SHA.
2. Recent commits and changed paths; open PRs, their base/head SHAs, reviews and required checks.
3. Queued and in-progress Actions runs; then recent completed runs, job/step conclusions, logs, artefacts and expiry.
4. Open issues and recent comments for the affected subsystem.
5. The canonical registry and campaign manifests, with exact identity/alias matching and current exclusions.
6. Relevant source, tests, workflow inputs/triggers/permissions and downstream file contracts.

Never describe a remote repository inspection as a clean local `git status`.

### Classify project state explicitly

For every feature, workflow, source integration or campaign that materially affects the task, classify it as one of:

- **Implemented and active:** present in current code/configuration, covered by current tests, and available through a live entry point.
- **Implemented, live verification incomplete:** code and offline tests exist, but current source/site or end-to-end behaviour is not confirmed.
- **Partial / experimental:** limited proof, constrained path, fixture-only support or a specific allowlist; do not generalise it.
- **Planned:** discussed or documented but no current implementation.
- **Deprecated / retired / one-shot consumed:** code or workflow may remain in the tree, but must not be invoked without a new explicit review.
- **Historical:** evidence of an earlier run or design, not a statement of current availability.

State the evidence and checked-at date. A README statement, open issue, workflow filename or past green run alone does not prove a feature is active.

### Operational evidence must not be conflated

For novel acquisition, keep these states separate: requested; public listing found; title/author/edition verified; chapter index verified; rights to archive confirmed; selected; dispatched; chapter batches validated; final EPUB/ZIP assembled; registry complete; artefact still available; exported locally; imported into private Hugging Face; visible in the reader. A source audit or TOC preflight does **not** fetch chapter prose and does not establish copying rights. A green dispatcher does not prove its child downloads completed.

Before any external download or publication, re-check user authorisation, source restrictions, the 90 global red/Dropped exclusions, known failure cases, canonical completed registry, active/queued runs, one-shot activation markers and public artefact visibility. Use `force=false` unless a separately reviewed recovery requires otherwise. Do not re-run consumed campaign markers.

### User-approved backlog priority (22 November 2026)

The order below is binding for acquisition work. A previous first-pass search of a later tier does not authorise skipping unfinished work in an earlier tier.

1. **Triage the 26 exact public listings from source audit #44924359606 first.** This triage and the read-only five-book TOC preflight #44926984233 are complete. Keep the 12 older #371 failures and nine #452 source/index failures blocked until their exact root causes are fixed and covered by regression tests. Of the five fresh candidates, only *Doom Lord* (155 entries) and *Girl, I'll Teach You Cultivation* (283 entries) passed the structural TOC check, but both are partial against their 856- and 812-chapter original editions. The other three failed their indexes. The author/edition review in [the source-audit report](campaigns/overnight/source-audit-report-20261121.md) found 0 archiving permissions and 0 eligible downloads. The audit and preflight fetched no chapter prose.
2. **The original 43-title fanfiction source-research stage is complete for the current search scope.** The immutable catalogue remains 24 Naruto + 19 Harry Potter: 8 registry-complete, 3 blocked and 32 unresolved. Round 18 completed exact title/credited-author and supported-host checks for all 32 remaining entries; it found 0 new exact supported-host listings, 0 explicit archive permissions and 0 rights-cleared titles. The three blocked works remain held: Wind Calamity needs author permission and a complete one-to-one TOC map; Konoha Medical's credited editor is not the original writer and artifact #14462633408 remains rights-unverified; Arcane Thief needs full paginated TOC validation and archive permission. Do not request screenshots again, retry unchanged failures or publish another archive. See `campaigns/fanfiction/source-verification-round-18-20261122.md`.
3. **The 65 unmatched Yup/IDK alternative-source review is complete for the current search scope.** The 36-row Yup sweep is recorded in `campaigns/overnight/alternative-source-research-20261122.md`; the 29-row IDK sweep is recorded in `campaigns/overnight/idk-alternative-source-research-20261122.md`. All 29 IDK rows reconcile to the 82-entry manifest; Xian Ni is the completed Renegade Immortal alias, and A Thought Through Eternity is the A Will Eternal alias elsewhere in the manifest. One exact NovelFull/FreeWebNovel listing was found for *Attack Of The Adorable Kid* (Sweets Flood, 2,612 page-reported chapters), but its full TOC and archive permission are unverified. Eight WuxiaClick metadata listings have incomplete or mismatched indexes. Across the 65 rows, public metadata is not archive permission; no rights-cleared title or new download run resulted. The four URL-pattern 404s are not worldwide-unavailability evidence. Preserve all aliases, the 343 completed records, 70 separate HF imports and 90 exclusions.
4. **Dispatch only when every gate passes:** exact author/work/edition, English text, complete ordered chapter index, documented permission to archive **and publicly share** the resulting artefact from this public repository, and a safe output route. Public listings, free-to-read pages, translator credits, Patreon pages and TOCs are not permission. NovelFull and ReadNovelFull terms say their material is collected from public sources/free to read while users remain responsible for researching original copyright; FreeWebNovel's user-content licence is limited to use through its services and uploaders must hold the necessary rights. None grants this project blanket off-platform archive/publication rights. The `confirm_rights` flag is an operator attestation, not proof; set it only after independent evidence is recorded for every selected title. If permission is private-only, do not use public GitHub Actions artefacts. Use reviewed code/campaign changes with green CI, at most 10 titles per batch, at most two bulk workflows active, force=false, and no complete-title duplicates.

Keep requested, source-listed, identity-verified, TOC-verified, rights-cleared, dispatched, chapter-complete, assembled, registered, artifact-available and private-HF-imported counts separate.

### Keep the state model current

- Refresh `docs/current-status.md` only from live, timestamped evidence; label it as a snapshot, never a dashboard.
- Update `docs/operations-runbook.md` when procedures or recovery rules change, `docs/website-support.md` when source capability evidence changes, and `CHANGELOG.md` for operator-visible changes.
- Record important rationale and failure lessons in [Project History and Decisions](docs/project-history-and-decisions.md), linking to the implementation/tests/issues rather than duplicating the handbook.
- If a fact cannot be verified, write **unknown / not checked**. Do not fill gaps with model inference.

## Start here: agent navigation (updated 21 November 2026)

**Do not re-read old conversations to reconstruct live download status.** Use the following *living, source-linked* documents in order:

1. [README.md](README.md): end-user purpose, supported sources and entry points.
2. [docs/operations-runbook.md](docs/operations-runbook.md): operational checks, GitHub Actions monitoring, safe retries, export and downstream import.
3. [docs/current-status.md](docs/current-status.md): **timestamped** Yup/Idk, fanfiction, backlog, child-run, registry-PR and cover-repair state. It is a snapshot, **not** an auto-updating monitor; re-check the live repository and workflows.
4. [docs/agent-handover-template.md](docs/agent-handover-template.md): mandatory evidence and next-step checklist for handing work to another agent.
5. [Project History and Decisions](docs/project-history-and-decisions.md): original requirements, design evolution, failure lessons and roadmap.
6. [CHANGELOG.md](CHANGELOG.md): dated operator-visible changes; not a substitute for Git history.

**Absolute operational distinctions:** A successful dispatcher is not a complete child download; a complete registry row is not a durable or imported book; a cover embedded in an EPUB is not necessarily a standalone private-library thumbnail. Do not collapse these stages or promise automatic work outside a running GitHub workflow.

## Repository naming conventions

- Python modules and test files use `snake_case.py`; tests start with `test_` and identify the component under test.
- Internal modules distinguish **sequential novel bulk execution** (`tools/sequential_bulk_download.py`) from **mixed-site bulk orchestration** (`tools/mixed_source_bulk.py`). Site adapters and their tests use recognisable website names.
- Human-readable guides use lowercase `kebab-case.md`. Source investigations and experimental notes belong in `docs/research/`, not inside executable `tools/`.
- Keep **public entry points stable**: `novel_downloader.py`, `Download-All-Novels.cmd`, `PDF-to-Novel/Convert-PDFs.cmd`, all existing `.github/workflows/*.yml` names, `DOWNLOADED_NOVELS.md` and `downloaded_novels.json`. Their paths are consumed by users, GitHub Actions and storage workflows.
- When renaming an internal file, update imports, test names, workflow invocations, documentation links, JSON file paths and Windows commands together. `tests/test_repository_naming.py` checks the public entry points and local Markdown links; update its expected paths when intentionally renaming a stable entry point.

## 1. Mission, boundaries and design philosophy

Novel-Retriever is a Python-centric, local-first toolkit for converting content a user is authorised to archive into consistent, inspectable novel artefacts. Its core output is an EPUB, UTF-8 text chapters and JSON metadata. It also supplies GitHub Actions workflows for fetching or assembling permitted chapter ranges, a metadata-only index of completed downloads, a Windows tool for retrieving completed GitHub Actions artefacts, and local PDF/EPUB import utilities.

The project exists because long novels are frequently delivered as thousands of independently numbered chapters. A one-job scraper or one giant EPUB conversion can time out, lose progress, collide with another novel's files, or silently omit chapters. This repository favours bounded work, verifiable identities, recoverable checkpoints, strict manifests and explicit failures over optimistic “best effort” archives.

### What is in scope

- Acquire authorised books from **NovelFull** using the established **FanFicFare** integration and its site adapter.
- Acquire authorised, publicly readable **FreeWebNovel** chapter ranges through a separate, deliberately conservative downloader.
- Acquire authorised ReadNovelFull books through its separate AJAX chapter-index parser and bounded chapter batches; live full-book success is verified for one book, while per-title index failures remain possible.
- Split large books into independent, bounded batches; reuse only validated complete batches; assemble one verified EPUB and its chapter TXT collection.
- Export directly imported EPUBs, package authorised local EPUBs, convert locally supplied selectable-text PDFs, extract optional covers and preserve sourced metadata.
- Track completed GitHub Actions artefacts in a readable metadata-only registry.
- Download **already generated** GitHub Actions artefacts to Windows and package each complete novel as its own verified ZIP.
- Perform isolated source-feasibility experiments without enabling unapproved websites or bypassing access controls.
- Run offline unit and synthetic end-to-end regression checks on Linux and Windows.

### Explicit non-goals

- This repository is **not a hosted reader**, not the user's personal library web application, and not the private dataset administrator.
- It does **not** own the external application's user accounts, cloud synchronisation, ratings, reading progress or hosted collection metadata.
- It does **not** persist full novel text in Git history or in `downloaded_novels.json`. A GitHub Actions artefact is temporary delivery storage, not permanent backup storage.
- It does not grant permission to scrape, copy, redistribute, unlock, or circumvent restrictions on any third-party site. A `--confirm-rights` flag is a user declaration, not a legal or technical bypass.
- It must never implement CAPTCHA-solving, account-cookie harvesting, paywall bypass, hidden API scraping, challenge evasion or premium-content unlocking.
- A live website returning HTTP 200 does not prove completeness, licence, or compatibility.

### Architectural principles

1. **Source identity is stronger than a title.** Titles and final URL path components can collide.
2. **Correctness before publication.** Do not label a novel complete until expected chapter positions and files are validated.
3. **Non-destructive by default.** Existing ZIPs or complete books must not be overwritten through ordinary retries.
4. **Checkpoints are not completions.** Keep recoverable partial work separate from published completed artefacts.
5. **Reproducible, offline-first CI.** Synthetic fixtures and deterministic installs must remain the required checks; any live metadata smoke is supplementary.
6. **Site adapters remain isolated.** Changes to site adapters must not regress NovelFull, FreeWebNovel, ReadNovelFull, existing manifests, or Windows packaging.
7. **Respect operator boundaries.** Destructive data operations, external downloads, API credentials and publication are separate actions requiring the correct permissions and safeguards.
8. **Never invent book metadata.** Missing synopsis, cover, genre or publication status should be absent or explicitly reported, not guessed.

## 2. One-minute architectural map

Conceptual data flow:

~~~text
Authorised source book / user-supplied EPUB / user-supplied PDF
               |
               +--> NovelFull via FanFicFare + tools/fanficfare_progress_runner.py
               |       |
               |       +--> individual verified chapter-range jobs
               |       +--> cached complete range reuse (when available)
               |
               +--> FreeWebNovel conservative public-page downloader
               |       |
               |       +--> numbered, verified 50-chapter workflow jobs
               |
               +--> ReadNovelFull AJAX chapter index + bounded batches
               |       |
               |       +--> exact per-chapter URLs; 100-chapter workflow jobs
               |
               +--> offline import_local_epub.py / pdf_to_novel.py
                       |
                       v
        source.epub + chapter_*.txt + metadata.json
                       + chapters.json + optional cover
                       |
          source identity + count + order + SHA-256 checks
                       |
           +-----------+--------------------+
           |                                |
   GitHub Actions completion        Local ZIP conversion
           |                                |
   Temporary final artefact          One-book verified ZIP
           |                                |
   Metadata-only registry PR        Private downstream import,
           |                        if explicitly performed outside
   downloaded_novels.json           this repository
           + DOWNLOADED_NOVELS.md
           |
   Download-All-Novels.cmd
   (fetch existing complete artefacts; validate; save local ZIPs)
~~~

The acquisition tools and the downstream reading/storage repositories communicate through **files and contracts**, not through a shared runtime library. A successful ZIP generation here is **not** evidence that a separately maintained hosted importer has accepted the package.

## 3. Repository tree and ownership

This section is a navigation map, not an exhaustive list of every test.

| Path | Responsibility | Change caution |
| --- | --- | --- |
| `README.md` | Main user guide and up-to-date operational instructions | Update when behaviour or commands change |
| `AGENTS.md` | This detailed agent/contributor reference | Keep aligned with executable source |
| `novel_downloader.py` | Main FanFicFare-backed direct downloader; EPUB spine parsing, chapters, staging and identity safety | High: common library functions used by several tools |
| `tools/fanficfare_progress_runner.py` | FanFicFare callback wrapper for chapter progress and temporary chapter checkpoints | High: partial-download resilience |
| `tools/chunked_download.py` | NovelFull range planning, caching, batch validation, EPUB assembly | High: completeness, ordering, metadata and artifact reuse |
| `tools/freewebnovel_downloader.py` | Separate public-page sequential FreeWebNovel range downloader | High: site restrictions and fail-closed parser |
| `tools/freewebnovel_chunks.py` | FreeWebNovel workflow orchestration using shared batch APIs | High: keep independent from NovelFull |
| `tools/readnovelfull_source.py` | ReadNovelFull book URL and AJAX chapter-index validation | Reject invalid, duplicate or non-consecutive chapter links |
| `tools/readnovelfull_downloader.py`, `tools/readnovelfull_chunks.py` | ReadNovelFull single/range downloader and bounded batch assembly | Preserve source identity, prologues and chapter-index checks |
| `tools/wuxiaclick_source.py`, `tools/wuxiaclick_downloader.py`, `tools/wuxiaclick_chunks.py` | WuxiaClick's bounded 20-chapter-per-run source and batch path | Do not bypass daily allowance or enable full-book export |
| `tools/scribblehub_crosspost_downloader.py`, `tools/scribblehub_crosspost_artifact.py` | One allowlisted same-author Scribble Hub/FanFiction.net cross-post | No general Scribble Hub scraping or guessed cross-posts |
| `tools/download_registry.py` | Canonical URLs, ranges, availability, registry records and Markdown rendering | High: previously downloaded book selection |
| `tools/publish_registry.py` | Retryable optimistic registry PR publishing on the latest `main` | High: concurrent download completion |
| `tools/export_completed_github_novels.py` | Metadata-driven export of completed novel artefacts into a controller-ready bundle | Artefacts expire; validate each ZIP and manifest before downstream handover |
| `tools/mixed_source_bulk.py` | Single consolidated bulk workflow planning by names or URLs, grouped by site | High: avoid incorrect title-to-URL guessing |
| `tools/overnight_queue.py` | Read-only public book-page discovery and legacy paced Yup/IDK dispatcher | Keep discovery and dispatch separate; source matches do not prove rights |
| `tools/dispatch_curated_bulk.py` | Validates and submits operator-reviewed literal source URLs | No web search or guessed slugs; enforce exclusions and active-run cap |
| `tools/large_batch_dispatch.py`, `tools/dispatch_verified_yup_wave.py` | Legacy reviewed campaign grouping and bounded dispatcher helpers | One-shot campaign code; inspect marker and current run state before any invocation |
| `tools/fanfiction_campaign.py` | **Legacy one-shot queue; do not rerun** for the 43 reviewed Naruto/Harry Potter works | Its 2-title batches / 4-active limit conflicts with the current 10-title / 2-active policy; use only the reviewed resumable bulk workflow after rights clearance |
| `tools/five_book_toc_preflight.py` | Read-only chapter-index check for a reviewed five-book manifest | Does not fetch chapter prose or verify archiving rights |
| `tools/sequential_bulk_download.py` | General local/multiple-URL planning and execution utilities | Maintain tests even if a newer workflow path is preferred |
| `tools/epub_source_metadata.py` | Recover source EPUB description, genres and publication status from OPF | Preserve data instead of deriving it from novel prose |
| `tools/novel_covers.py` | Image detection, public URL restrictions, image limits, EPUB cover extraction | Covers are optional and untrusted image input |
| `tools/download_covers.py` | Cover-only collection from existing registry Markdown | Never download/rewrite chapter text |
| `tools/repair_synopsis.py` | Dry-run-first, validated repair of existing novel ZIP descriptions | Protect original ZIP on failure |
| `tools/pdf_to_novel.py` | Offline selectable-text PDF inspection, extraction, EPUB/ZIP creation and verification | High: chapter boundaries and source-text preservation |
| `tools/pdf_batch.py` | Convert every local PDF, skip good existing ZIPs, produce review plans when needed | High: never destroy input PDFs |
| `tools/import_local_epub.py` | Offline, source-identified ZIP packaging of already-authorised EPUB files | High: validation budgets and overwrite rules |
| `tools/download_all_artifacts.ps1` | Fetch existing GitHub Actions artefacts to Windows, handle authentication/logging/repacking | High: PowerShell 5.1 and local safety |
| `tools/zip_novel_artifacts.ps1` | Validate each book folder and produce reader-compatible, one-book ZIPs | High: ZIP format and duplicate detection |
| `Download-All-Novels.cmd` | Windows entry point for existing artefact retrieval | Preserve argument forwarding and visible errors |
| `PDF-to-Novel/Convert-PDFs.cmd` | Windows entry point for batch PDF conversion | Preserve relative paths, confirmation and pause |
| `PDF-to-Novel/PDFs/` | Local PDF inputs; gitignored | Do not commit books |
| `PDF-to-Novel/Novels/` | Local converted ZIPs and reports; gitignored | Do not commit books |
| `docs/pdf-to-novel.md` | PDF structure, manual review, limitations | Read before changing PDF heuristics |
| `docs/project-history-and-decisions.md` | Original requirements, architectural decisions, failure lessons and roadmap | Historical rationale; verify current implementation separately |
| `campaigns/overnight/source-audit-report-20261121.md` | Durable 26-match/65-unresolved Yup/IDK source audit and five-title TOC preflight | Discovery/index evidence only; not rights or download completion |
| `docs/research/source-feasibility-2026-11-15.md` | Candidate-source permissions and blockers | Read before introducing new sites |
| `docs/research/webnovel-bulk-import.md` | Offline saved-page import instructions | No live general WebNovel scraping |
| `docs/research/source-test-evidence-archive.md` | Historical site-probe evidence | Never confuse a past HTTP 200 with present authorisation |
| `downloaded_novels.json` | Metadata-only history of completed downloads and artefact links | Do not hand-edit concurrent updates without care |
| `DOWNLOADED_NOVELS.md` | Generated human-readable registry index | Maintain synchronisation with JSON |
| `curated_novels.json` | Small curated URL/title list for bulk name resolution | Not the downloaded content corpus |
| `requirements.txt`, `requirements-pdf.txt` | Broad developer compatibility constraints | Update deliberately, not incidentally |
| `requirements.lock`, `requirements-pdf.lock` | Resolved Python 3.12 package versions used in CI | Install from these in routine CI/workflows |
| `tests/` | Main offline unit tests, Windows packaging smoke, regressions | Extend alongside production changes |
| `tests_pdf/` | Isolated offline PDF and Windows CMD regression tests | Keep both Windows and Ubuntu passing |
| `.github/workflows/` | Active download, recovery, export and CI workflows | Check permissions, source restrictions and artefact retention |

Do not infer that a `tools/` file is automatically part of the regular production flow. Several modules are intentionally isolated feasibility stages.

## 4. Environment and first-day setup

### Supported practical environment

- The active workflows use **Python 3.12**. Do not assume that changing the tested Python version is harmless.
- The code is Python-first. EPUB extraction uses ZIP/XML and Beautiful Soup; FanFicFare performs supported-site acquisition. Pillow handles cover images. PDF conversion uses PyMuPDF (`fitz`) and Pillow.
- The normal downloader and PDF converter use separate lockfiles. The PDF package set is deliberately optional for normal novel downloads.
- Linux Ubuntu runners run primary tests and downloads; Windows runners test PowerShell, CMD launchers, novel ZIPs and offline PDFs.
- `gh` is used for querying/downloading GitHub Actions artefacts and registry PR publication. The user's local laptop only needs it for relevant workflows.
- Windows PowerShell **5.1** is a supported target for the one-click archive downloader; do not assume PowerShell 7-only syntax.

From the project root, a conservative normal setup is:

~~~powershell
python -m pip install -r requirements.lock
python -m pip check
python -m unittest discover -s tests -v
~~~

For PDF work:

~~~powershell
python -m pip install -r requirements-pdf.lock
python -m unittest discover -s tests_pdf -p "test_pdf_*.py" -v
~~~

Test the FanFicFare downloader without a live network request:

~~~powershell
python -u novel_downloader.py --self-test --chapter-range 3-4 --output-dir smoke
~~~

Do not run the two-chapter self-test as evidence that a real NovelFull page or a user's full novel still downloads. Distinguish **synthetic correctness** from **site availability**.

### Developer dependency policy

- `requirements.txt` contains compatible ranges for FanFicFare, Beautiful Soup and Pillow.
- `requirements-pdf.txt` defines the separate PDF requirements.
- `requirements.lock` and `requirements-pdf.lock` pin resolved versions, including transitive dependencies, for Python 3.12.
- The current lockfiles are **version locks, not hash-pinned wheel locks**.
- If upgrading, regenerate the affected lockfile with a reviewed resolver, check the actual installed version graph, and run both relevant operating systems in CI.
- Never casually replace locked installation in CI with an unconstrained `pip install -U`.

## 5. Data contracts: book directory, EPUB, chapters and ZIP

This section is especially important. There are **multiple producers** and at least two packaging pathways, so do not impose one producer's incidental filename style on all the others.

### Standard book directory

A completed book commonly looks like:

~~~text
some-book-folder/
    metadata.json
    chapters.json
    source.epub
    chapter_00001.txt
    chapter_00002.txt
    ...
    cover.jpg                # optional; cover.png also allowed
~~~

Some direct imports use `chapter_0001.txt` instead of five digits, a prologue name, or a `_part02` suffix if printed chapter numbers repeat. The PDF converter uses `chapter_0001.txt`, `chapter_0002.txt` etc. The final batch assembler uses five-digit **position-based** filenames.

**Therefore:** the true set and order of chapters comes from `chapters.json`, not a guessed glob, lexical sorting, or one hard-coded chapter-name width.

### Common metadata shape

`metadata.json` is source- and producer-dependent; common fields include:

~~~json
{
  "title": "Example Novel",
  "author": "Example Author",
  "language": "en",
  "source_url": "https://example.org/example-novel",
  "chapter_count": 2,
  "created_at_utc": "2026-11-13T00:00:00+00:00",
  "format": "epub",
  "chapter_files": "UTF-8 TXT",
  "description": "Source-provided summary when available.",
  "synopsis": "Source-provided summary when available.",
  "genres": ["Example genre"],
  "status": "Completed",
  "cover_image": "cover.jpg"
}
~~~

The sample is **illustrative, not a required universal schema**. `description`, `synopsis`, `genres`, `status` and `cover_image` are optional and must not be fabricated. Other producer-specific fields include `synopsis_pipeline_version`, `cover_pipeline_version`, `assembled_from_batches`, `original_format`, `source_pdf_sha256` and `source_pdf_pages`.

The identity field is `source_url`, not an arbitrary display title. For local PDF conversion the identity is `pdf://sha256/<full-pdf-sha256>` instead of a public website URL.

### Chapter manifest

A representative `chapters.json` row:

~~~json
{
  "position": 1,
  "chapter_number": 1,
  "title": "Chapter 1",
  "file": "chapter_00001.txt",
  "word_count": 1234,
  "sha256": "64-lowercase-hex-characters-calculated-from-the-TXT-bytes"
}
~~~

The digest shown is explanatory text, **not a valid hash fixture**. In real output the digest is computed from the UTF-8 chapter content. The chapter TXT typically contains the chapter title, a blank line and the body. Test exact bytes, encoding and line-endings where hashes are involved.

- **`position`:** the one-based position in the downloaded/assembled selection; it is not necessarily the chapter number printed in the title.
- **`chapter_number`:** parsed or assigned chapter number, which may differ from position, especially with prologues or unusual titles.
- **`file`:** the actual basename of that chapter's TXT; use it as the locator.
- **`word_count`:** the word-count contract of the relevant producer. Do not change tokenisation without changing validation and tests.
- **`sha256`:** digest of the generated TXT representation, not just the body. Windows CRLF conversion must be considered before claiming a checksum mismatch.

A valid batch covers **every expected position exactly once, in order**. Reject missing, duplicated, reordered, wrong-source, missing-file, corrupt or unexpected chapter ranges.

### EPUB details

The `source.epub` file is not merely a placeholder. It contains ordered XHTML chapters and OPF metadata. In assembled books, the merger rebuilds EPUB spine/toc and checks that the EPUB can be parsed back into the expected number of chapters. Where available, source OPF descriptions, genre subjects, status and cover information are carried forward.

`novel_downloader.epub_chapters()` reads EPUB spine order. It recognises FanFicFare's chapter markers and has a carefully limited fallback for generic EPUB pages. Cover/TOC pages must not become fake story chapters. It rejects basic unsafe EPUB traversal paths. Do not replace this reader with alphabetical member sorting.

### ZIP formats and ownership

The local Windows ZIP packager and the PDF/local EPUB tools publish **one book per ZIP**, rooted in a single novel directory:

~~~text
novel-some-id.zip
    some-book-folder/
        metadata.json
        chapters.json
        source.epub
        chapter_0001.txt
        chapter_0002.txt
        cover.jpg           # optional
~~~

Not every GitHub Actions artefact is already this final ZIP; workflow artefact storage and portable reader ZIPs are distinct concepts. The Windows downloader fetches the completed Actions artefact, finds the correct book, validates it, and then packages a one-book ZIP.

For local ZIP packaging, **do not identify a novel by ZIP filename alone**. Check its internal metadata `source_url`, expected manifest rows, EPUB presence, and optional cover. The Windows helpers protect existing ZIPs from overwrite, including invalid ones.

An archive that exists on disk is not proof that its chapters are complete or that it belongs to the requested source.

## 6. NovelFull: established acquisition and complete-book assembly

### Direct CLI

`novel_downloader.py` is the public entry point for FanFicFare-supported source URLs.

Examples:

~~~powershell
python -u novel_downloader.py "https://example.org/my-book" --confirm-rights
python -u novel_downloader.py "https://example.org/my-book" --confirm-rights --chapter-range 1-30
python -u novel_downloader.py "https://example.org/my-book" --confirm-rights --expected-chapters 500
python -u novel_downloader.py --import-epub "Authorised Book.epub" --output-dir downloads
~~~

The placeholder URL is only a syntax example. A real network download requires a site actually supported by FanFicFare and permission to archive that content.

Important flags: `--list-only` (FanFicFare metadata discovery), `--chapter-range` / `--range`, `--begin-chapter` / `--end-chapter`, `--output-dir`, `--slug`, `--overwrite`, `--expected-chapters`, `--timeout-minutes` and `--self-test`.

- URL input requires HTTPS and rejects URL credentials, IP literals and certain local/private hostname suffixes. **This is input hardening, not complete DNS-rebinding or redirect-time SSRF protection.** The FanFicFare adapter's own destination handling still matters.
- Download folders use a readable URL-path slug **plus a digest of the source URL**. Two sites with the same path stem must not overwrite each other.
- If a caller supplies the same custom `--slug` for two different URLs, the recorded metadata identity must block cross-book reuse, even when `--overwrite` is supplied.
- An existing EPUB with no verifiable associated source metadata must not be silently claimed as a cache hit.
- A requested exact range or explicit expected chapter count must be checked **before publication**.
- Without an authoritative expected count, a direct unrestricted download warns that completeness cannot be proven. For a verified whole book, favour the GitHub Actions batch workflow.
- Forced redownloads use a temporary sibling directory rather than destroying an already published complete EPUB before success.
- Exported chapter/manifest generations are staged, with a recoverable prior-directory backup and rollback on rename errors. This is **recoverable**, not a magical atomic multi-file transaction under sudden process death.
- Temporary `chapters_in_progress/` checkpoints are removed after successful complete export.

### Progress reporting

`tools/fanficfare_progress_runner.py` observes FanFicFare's chapter completion callback, rather than interpreting every console progress dot as one chapter. It produces chapter counts/progress percentages and writes temporary chapter text checkpoints as individual chapters finish.

Do not delete checkpoints or advertise a partial output as complete after exceptions. Tests in `tests/test_novel_downloader.py` exercise progress and checkpoint behaviour.

### GitHub workflow, step by step

The workflow is `.github/workflows/download-novel.yml`, named **NovelFull - Download**. It can run manually or as a reusable workflow called by the unified bulk job. High-level sequence:

1. **prepare**: read current `main`; validate input; check the JSON registry to skip an already available completed artefact unless `force` is set.
2. **discover**: use FanFicFare metadata-only discovery to establish a positive chapter count; interpret formatted counts carefully (including thousands separators).
3. **plan**: split the requested inclusive range into bounded pieces, by default **200 chapters per piece**, with a cap of **128 pieces**. The planner stores a source-derived identity key, exact bounds and selected work matrix.
4. **chapter-batches**: execute independent jobs for each piece, with bounded concurrency, separate timeouts and recoverable failure artefacts. The planner permits **up to six workers**, according to selected chapter count and available batches.
5. **reuse**: try prior non-expired GitHub Actions artefacts for each exact source/range; validate the cached manifest and SHA-256 values before accepting them.
6. **assemble**: gather the precise completed pieces; reject any missing/duplicated/out-of-order positions; copy verified TXT chapters into the assembled book, rebuild the EPUB, preserve source metadata and verify the new EPUB.
7. **publish artefact**: upload the final completed novel as an Actions artefact, normally retained for **seven days**.
8. **register**: update only the metadata registry through a PR built from the latest `main` (see Section 9).
9. **report**: on failure, explain failed ranges; do not register a partially assembled novel as complete.

The default parallelism is adaptive, not “always six”. Large jobs may run concurrently with **other novels**; duplicate requests for the same URL use workflow concurrency to queue rather than cancel in-progress runs.

### Batch identity and validation

`tools/chunked_download.py` has three CLI actions: `plan`, `fetch` and `assemble`. Key concepts:

- `identity(url)`: a stable digest-based key used in chapter batch artefact names.
- `chapter_plan(url, total, chapter_range, chunk_size)`: exact range, piece boundaries and concurrency matrix.
- `validate_piece(folder, url, key, first, last)`: verifies `part.json` identity, book metadata identity, every selected row position, chapter files/checksums, EPUB presence and cover data when supplied.
- `reuse_complete_piece(...)`: attempts prior Actions artefacts via `gh`; an absent, expired, corrupt, identity-mismatched or old-incompatible cached piece must be fetched again.
- `assemble(...)`: checks complete contiguous coverage and writes one EPUB plus its final chapter TXT/JSON collection.
- `cache_has_synopsis_support(...)`: ensures old NovelFull caches lacking the newer synopsis/cover metadata capabilities are not trusted to preserve those fields.

Some source EPUBs legitimately have no description or cover. The code must retain a warning/absence, **not** invent a synopsis or reject the book solely because its source supplied no cover.

### Selective FreeWebNovel request retries (18 November 2026)

`freewebnovel_source.fetch_public_html` distinguishes a
`TransientFetchError` subclass from the ordinary fail-closed
`ProbeError`. Retryable: HTTP 408, 500, 502, 503, 504 and positively
identified connection resets, abrupt remote disconnects, incomplete reads
or timeouts. Not retryable: 403, 404, 429, unrecognised redirects, site
challenges, DNS failures, bad URLs, denied content, missing/short bodies,
mismatched chapter numbers or any integrity check. The feasibility probe
remains non-retrying.

`freewebnovel_downloader._fetch_with_retry` retries only those explicitly
classified transient fetch exceptions, at most twice more for the **same**
URL, using 4-second and 12-second pauses. Existing 1-second interchapter
pacing and at-most-two concurrent batches per novel remain unchanged.
Downloaded chapters are checkpointed only after body/identity/hash checks;
exhaustion stops with a recoverable partial artefact. Never retry
`DownloadError` after a body or chapter-number mismatch, and never broaden
the catch-all to every `ProbeError`/`OSError`. Synthetic regression tests
exercise both retryable transport and nonretryable access/integrity failures.
See `docs/download-guide.md`.

## 7. FreeWebNovel: separate production path with restricted requests

**FreeWebNovel is not a FanFicFare adapter in this project.** Do not send it through `novel_downloader.py` as a substitute for the dedicated implementation.

Components:

- `tools/freewebnovel_source.py`: constrained catalogue/chapter compatibility probing, at most two chapter requests.
- `tools/freewebnovel_downloader.py`: site-specific book details, sequential numbered chapter extraction, text-quality checks, checkpoint files, optional cover, EPUB creation.
- `tools/freewebnovel_chunks.py`: batch plan/fetch/assemble wrapper.
- `.github/workflows/freewebnovel-download.yml`: dedicated single-book Actions workflow with the same high-level prepare/batches/assemble/register structure.

Operational rules:

- Only validated `https://freewebnovel.com/novel/<slug>`-style public book URLs are accepted.
- The standalone downloader accepts at most **100 consecutive chapters** in one call. The workflow normally divides into **50-chapter** pieces.
- The workflow uses at most **two concurrent chapter-batch jobs per book**. Requests **inside** a batch are sequential, with a one-second delay.
- The public catalogue's highest numbered chapter link is used as an upper bound; it is not a blanket guarantee that each intervening chapter exists or is readable.
- Each requested chapter must be present, correctly numbered, legible, non-locked, substantial enough for extraction, and independently validated.
- The parser rejects challenges, recognised locked content, missing reader selectors, suspiciously short chapter bodies, repeated chapters and numbering inconsistencies instead of silently skipping them.
- Recoverable per-range checkpoints may contain validated rows. Checkpoints themselves never become completed registry entries.
- Covers remain optional; a failed cover lookup must not lead to fabricated or substituted artwork.
- No login, concurrency within one batch, automated challenge retries, paywall workarounds or anti-bot evasion.
- The main README records a locally verified initial two-chapter test from 10 November 2026; **that is not proof that every currently available title supports complete downloading**.

Local example (requires rights and a real, permitted source):

~~~powershell
python -m tools.freewebnovel_downloader "https://freewebnovel.com/novel/the-first-order" --chapter-range 1-2 --output-dir freewebnovel-test --confirm-rights
~~~

This example makes live source requests. **Do not use it in deterministic CI or run it merely to explore a production bug without explicit purpose and permission.**

## 8. One unified bulk workflow, not multiple competing bulk menus

`.github/workflows/library-bulk-download.yml` is named **Library - Bulk Download** and is the single user-facing bulk workflow.

The user pastes **one or more supported novel URLs**, including a mixed list of NovelFull, FreeWebNovel and ReadNovelFull links, into the first **Novel links** field. The source is automatically detected per URL. There is **no website dropdown** in GitHub Actions; users can optionally add saved novel names and a chapter range. `force` bypasses an available-artifact skip. Scribble Hub author-verified cross-posts require a separate rights confirmation and a whole-book range.

Implementation is in `tools/mixed_source_bulk.py`:

- Resolve names from the downloaded registry and `curated_novels.json`.
- Reject unknown or ambiguous names rather than guessing which book is meant.
- Validate each URL's source site and recognised book path; auto-route by validated domain. No website selection is supplied by the manual GitHub Actions form. The deprecated optional `--website` CLI filter is retained for existing automation only.
- No arbitrary ten-novel limit. Respect the GitHub Actions **256-job matrix limit** for scheduled (non-skipped) downloads; fail with an informative message rather than letting GitHub silently reject an oversized matrix.
- Check available completed artefacts and skip them by default.
- Group mixed-source links automatically by site; call existing **NovelFull - Download**, **FreeWebNovel - Download**, **ReadNovelFull - Download** and the **verified Scribble Hub - Download** reusable workflows. Scribble Hub's `workflow_call` requires explicit `confirm_rights` and only allowlisted same-author cross-posts; only full-book exports are supported.
- Limit simultaneous novels to at most **three NovelFull**, **two FreeWebNovel**, **one ReadNovelFull** and **one Scribble Hub** jobs.
- Preserve each child's own chapter batch limits and per-book validation.
- After **all** children finish, the summary job runs under `if: always()`. If all child groups succeeded or were skipped, it bypasses the duplicate recovery artefact downloads, ZIP validation and repackaging: each completed book already has its independent downloadable artefact. When any child group failed or was cancelled, the `recovery_gate` enables retrieval of every successful `novel-<run-id>-*` artefact. `tools/bulk_download_recovery.py` then validates source identity, EPUB ZIP CRC, manifest ordering and each TXT SHA-256 before packaging one portable ZIP per complete novel into a seven-day `bulk-successful-novels-<run-id>` recovery artefact, plus a JSON manifest of missing/rejected downloads. Do not remove failure recovery or rewrite the already-finished child artefacts.
- Never delete independently uploaded successful child artefacts when any other book, registry update or recovery job fails. The overall bulk workflow must still signal failures, without losing verified successes. Recovery has an intentional 1.75 GiB aggregate size safety limit; original child artefacts persist if exceeded.
- On partial failure the summary also publishes a small **`bulk-recovery-manifest-<run-id>`** artefact with `run_id` and each failed/missing book's original `chapter_range`. No retry manifest is needed or generated for fully successful runs. The single bulk workflow's optional **`retry_run_id`** field downloads that manifest from the named earlier run via GitHub's artefact API. `tools.mixed_source_bulk.retry_selection_plan` then validates source sites, registered Scribble Hub identity, run ID and range, and schedules only missing books (skipping newly cached successes, never reusing an old Force flag). Do not mix retry with other selections. Retry manifests exist for seven days; legacy manifests without ranges are rejected instead of guessing.
- `python -m tools.bulk_download_stress` runs offline 20/50/100-batch planner and matrix tests, with a 256/257 boundary check. These consume no website requests.
- `tools/workflow_performance.py` reads GitHub's jobs API under `actions:read` during the bulk summary job and publishes small `bulk-performance-<run-id>` JSON and Markdown timing metrics. The API-only timing collector must never make source-site requests or log tokens; an API error must not fail downloads. Report cumulative **per-phase step seconds** and the **completed-jobs elapsed window** separately: parallel work overlaps and metrics are recorded before the summary job itself finishes.
- `tools/bulk_download_recovery.py` stores EPUB/JPEG/PNG members without recompression (ZIP_STORED), but keeps text and JSON compressed, preserving all integrity checks. The outer `bulk-successful-novels-<run-id>` Actions archive uses `compression-level: 0` because it mostly contains already-compressed book ZIPs. Do not change other artefacts' compression to 0 without measurement; TXT chapters can compress very well.
- NovelFull, FreeWebNovel and ReadNovelFull final assembly workflows already download only `chapter-batch-<key>-*` artefacts for their own novel. Do not label this existing protection as a new optimisation. Avoid increasing site concurrency or reducing polite request pacing until comparable real bulk timing data justifies it.

Do not create another bulk UI just because a source adds a new adapter. Extend the single planner and dispatch model only after that site's legal, technical and testing requirements are met.

Useful read-only command:

~~~powershell
python -m tools.mixed_source_bulk list
~~~

`tools/sequential_bulk_download.py` is an additional generic planner/running utility. Read it before modifying shared URL/range conventions, but **the endorsed combined Actions menu is Library - Bulk Download**.

## 9. Download registry, caching, artefact expiration and concurrent publication

### Registry sources of truth

- `downloaded_novels.json` has top-level `{"version": 1, "novels": [...]}`.
- Each novel has a canonical source URL, display title, author and a `downloads` history array.
- Each download record stores `range`, `status`, `chapter_count`, `run_id`, `run_url`, `artifact_id`, `artifact_url`, `completed_at_utc` and `expires_at_utc`.
- `DOWNLOADED_NOVELS.md` is the generated human-facing view of that history, grouped by website.
- `curated_novels.json` is a small curated list for resolving saved titles that are not yet in the completed registry. It does **not** contain the novel content.

The registry holds **metadata and links only**. The actual chapter text and EPUB live in GitHub Actions artefacts while available, or in user-controlled local storage after download.

### “Already downloaded” is a time-bound status

`tools/download_registry.py` provides `canonical_url()`, `normalise_range()`, `available_ranges()` and `already_available()`:

- A completed entry with an expired or unparsable expiry timestamp is **not an available cache hit**.
- `range: "all"` covers any requested subrange while the artefact is still available.
- Multiple valid completed ranges can collectively cover another requested range if there are no gaps.
- An incomplete or failed item cannot satisfy a skip check.
- History entries should remain visible even after artefact expiry.
- Registry availability does not verify a copy stored elsewhere on the user's PC; the Windows downloader separately checks local ZIPs.

Do **not** delete expired history in an attempt to “fix” redownloads. Do **not** equate a past run ID with durable storage.

### Safe publication under concurrency

`tools/publish_registry.py` is deliberately not a naive read-then-push of stale JSON:

1. Fetch the newest `origin/main`.
2. Create a registry update branch from that state.
3. Validate/record the exact newly completed book and artefact.
4. Commit only `downloaded_novels.json` and `DOWNLOADED_NOVELS.md`.
5. Open a metadata-only PR and try to squash-merge it.
6. If another novel's registry PR merged meanwhile, refresh from the latest `main`, rebuild the registry and retry with bounded attempts.
7. If automatic merging is prevented by repository rules, preserve the complete book artefact and provide a link to the pending PR instead of pretending registration succeeded.

Do not replace that algorithm with force-pushing registry files to `main`. A successful download job and a successful registry merge are **distinct outcomes**.

### Artifact lifetimes and privacy

The completed novel and intermediate range artefacts generally have **seven-day retention**. The cover-only artefact has **30-day retention**. These are workflow values that can change; inspect YAML when reporting an exact expiry. In a public GitHub repository, users with appropriate access may be able to retrieve Actions artefacts. Only archive/share works when permitted, and never put private novel contents into commits, test fixtures, generated PR descriptions or comments.

## 10. Windows: retrieve completed artefacts, do not download source chapters

Entry point: `Download-All-Novels.cmd` (repository root).

The CMD delegates to `tools/download_all_artifacts.ps1` under Windows PowerShell 5.1. The PowerShell helper `tools/zip_novel_artifacts.ps1` validates and packages **exactly one expected book** from the downloaded artefact.

Main behaviour:

1. Read the current registry or an explicitly supplied local registry file.
2. Select completed full-book records (`range == "all"`), preferring appropriate available artefacts.
3. Build a local index of existing, internally validated ZIP files, keyed by the novel's source URL rather than ZIP filename.
4. Skip books already present as a valid local ZIP; optionally scan **one specified extra ZIP directory** without changing it.
5. Repack recognised legacy extracted folders without accessing the network when possible.
6. If a real artefact download is required, check `gh` availability and user authentication, then fetch by stored artifact identity.
7. Stage, identify the correct book folder, validate required files/manifests/EPUB and optional cover, and publish one ZIP without overwriting an existing file.
8. Report expired/missing/invalid artefacts and keep a diagnostic transcript.

Key command examples:

~~~cmd
Download-All-Novels.cmd
Download-All-Novels.cmd -ExistingZipDirectory "D:\My Novel ZIPs"
Download-All-Novels.cmd -RepackOnly
Download-All-Novels.cmd -Limit 1
Download-All-Novels.cmd -BrowserLogin
~~~

Non-network launcher self-check:

~~~powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\download_all_artifacts.ps1 -CheckSetup
~~~

PowerShell parameters include `Repository`, `Destination`, `MaxAttempts`, `Limit`, `BrowserLogin`, `CheckSetup`, `RepackOnly`, `KeepOriginalFolders`, `RegistryFile` and `ExistingZipDirectory`.

Important local paths and safety contracts:

- Default output: ignored `Downloaded_Novels/`.
- Diagnostic log: ignored `download-last-run.log`.
- Failed items: `Downloaded_Novels/failed-downloads.txt`.
- Original legacy folders are kept/moved to recoverable backup space unless the user explicitly requests otherwise; do not discard them on repack failure.
- An existing corrupt ZIP is an error or conflict, **not a reason to overwrite or delete it**.
- A book folder discovered in a combined historic artefact must match the selected source URL. Never package the first arbitrary `metadata.json` you find.
- A local complete ZIP may have a different filename or artifact ID from the currently recorded one; validate identity from within the package.
- The CMD displays errors and pauses; preserve that behaviour for double-click users.
- Paths with spaces, Windows reserved names, PowerShell 5.1 parameter binding and native-command nonzero exit codes are tested operational requirements.
- `-RepackOnly` should work without network login and should leave invalid originals untouched.

The Windows ZIP helper's validation rules are its own concrete contract. Do not casually broaden accepted filenames or remove checks without tests, even if another producer has a slightly different standalone layout. If supporting new producer output, update compatibility tests deliberately.

## 11. Offline PDF to one-book ZIP

The PDF converter is separate from all website downloaders and is documented in `docs/pdf-to-novel.md` and `PDF-to-Novel/README.md`.

### Components

- `tools/pdf_to_novel.py`: inspect, detect headings, validate boundaries, collect chapter text, optionally extract a cover, build EPUB, construct a staged ZIP, validate its integrity and write a separate report.
- `tools/pdf_batch.py`: read each PDF in the specified folder; hash to a stable filename; skip existing valid ZIPs; preserve bad existing ZIPs; offer an editable review plan for ambiguous sources.
- `PDF-to-Novel/Convert-PDFs.cmd`: one-click Windows wrapper with relative-folder resolution, rights confirmation, dependency setup and visible pause.

Local folder layout:

~~~text
PDF-to-Novel/
    Convert-PDFs.cmd
    PDFs/               # user-supplied inputs, not committed
    Novels/             # novel-<hash>.zip + separate validation reports
    README.md
~~~

Advanced commands:

~~~powershell
python -m tools.pdf_to_novel "D:\Books\Story.pdf" --inspect --output-dir "D:\Books\Review"
python -m tools.pdf_to_novel "D:\Books\Story.pdf" --boundaries "D:\Books\Review\pdf-chapter-plan.json" --expected-chapters 120 --output-dir "D:\Books\Review" --confirm-rights
python -m tools.pdf_batch --confirm-rights
~~~

The converter works only on **selectable-text PDFs**. Image-only/scanned input fails closed; there is no OCR or network fallback. The source file must not be modified or deleted.

### Chapter detection and fidelity

- Preserve one-based source page and non-empty line positions.
- Support source-derived chapter headings including numbered chapters, prologue and epilogue.
- Respect manually reviewed heading overrides in a boundaries JSON file.
- Distinguish display headings from story text; avoid skipping body lines.
- Honour the source's actual line coverage, chapter order, start/end positions, paragraph grouping and warnings.
- Report missing/duplicate chapter numbering, ambiguous headings, suspicious short chapters, OCR-unreadable pages and unverified synopsis.
- Preserve original Chinese Unicode; only expand known presentation ligatures. Do not introduce broad aggressive text normalisation.
- Do not invent missing chapters, correct fictional prose, fabricate authors or create unsourced synopsis text.
- The validation report is deliberately **outside** the ZIP.

### PDF identity, limits, and publication

- Use streamed SHA-256 of the original PDF for stable file identity. `source_url` is `pdf://sha256/<digest>`.
- Standard output name: `novel-<first-12-hex-of-PDF-SHA256>.zip`.
- The converter guards against inputs larger than **1 GiB** or **50,000 pages**, and caps parsed chapter count at **20,000**.
- EPUB generation and PDF-page analysis still consume memory proportional to the novel. The code avoids some unnecessary whole-file copying, but is **not fully streaming**.
- Before publishing, write to a temporary ZIP in the destination folder; verify ZIP CRC, files, chapter hashes, ordering, word counts and EPUB spine.
- `--replace` must be explicit for intentional same-identity ZIP replacement.
- The batch wrapper skips an existing *valid* ZIP; it does not overwrite an existing *corrupt* ZIP.
- The user should inspect the validation report and selected first/middle/last chapters before downstream upload.
- The PDF ZIP's internal validation does **not** automatically prove acceptance by a separate Hugging Face dataset uploader.

## 12. Local EPUB conversion for other authorised sources

`tools/import_local_epub.py` is a **network-free** converter for EPUBs already supplied by the user with the necessary rights. It recognises strict permitted source-URL shapes for **Royal Road**, **WTR-Lab** and **Scribble Hub**. This offline importer is separate from the author-verified cross-post internet retriever described below. A source URL labels the output's identity; the program does not fetch the EPUB from that URL.

Example:

~~~powershell
python -m tools.import_local_epub --epub "My Author Export.epub" --source-url "https://royalroad.com/fiction/21220/mother-of-learning" --output-dir Imported_Novels --confirm-rights
~~~

That URL is a formatting example, **not** permission to archive that particular book.

Safety checks include:

- Source EPUB exists, is a real ZIP/EPUB, has usable title/chapters and passes CRC checks.
- Input EPUB compressed size no greater than **300 MiB**.
- Aggregate declared expanded size no greater than **750 MiB**.
- Any individual EPUB member no greater than **30 MiB**.
- At most **20,000 chapters**, with a limited additional budget for non-chapter EPUB members.
- Publish one ZIP with identity-derived `novel-<URL-SHA256-prefix>.zip` filename.
- Verify the copied EPUB, chapter counts, source URL, SHA-256 chapter TXT members, expected files and optional image format before replacing output.
- Use temporary/staged output; do not overwrite an existing ZIP without explicit `--replace`.

The generic `novel_downloader.py --import-epub` mode is distinct from this ZIP packager: it exports a book directory, checks title collisions and supports deliberate `--overwrite`. **Do not conflate the two interfaces or their overwrite flags.**

## 13. Covers and synopsis preservation

### Covers inside new novels

New NovelFull outputs may take a source EPUB's embedded cover; FreeWebNovel may use a publicly accessible book-page image. `tools/novel_covers.py` validates type, dimensions, public source restrictions and size before returning optional cover data. JPEG and PNG are the normal output extensions; supported conversions can produce JPEG from WebP/GIF.

Important controls visible in the code: maximum original image bytes **8 MiB**, maximum pixel count **20 million**, and rejection of obviously non-public image URLs. Cover embedding is optional and must not affect verified chapters or their hashes.

### Existing novels: image-only collection

`tools/download_covers.py` reads the completed-download Markdown index and fetches **only covers**, without fetching chapters or modifying old archives. The cover-only workflow (`.github/workflows/download-covers.yml`) produces an artefact such as:

~~~text
NovelFull/example-book-<8-char-url-hash>.jpg
FreeWebNovel/another-book-<8-char-url-hash>.png
covers_manifest.json
~~~

The stable URL digest avoids title collisions. The tool supports dry-run, website selection, limit, force and a controlled request delay. Successful output goes to ignored `Downloaded_Covers/`. Covers are **not retrofitted into existing novel ZIPs** by the image-only downloader.

### Synopses, genres and publication status

- `novel_downloader.epub_chapters()` reads sourced EPUB `dc:description` and exposes readable description/synopsis when present.
- `tools/epub_source_metadata.py` reads OPF-only source genres and recognised publication status.
- `tools/chunked_download.py` preserves description/genres/status through final EPUB rebuild and verifies the result.
- Legacy NovelFull range artefacts lacking newer metadata pipeline flags are deliberately rejected for reuse when they could drop metadata.
- A genuinely absent synopsis, cover, genre or status is **missing input**, not a reason to write AI-generated replacement metadata into the source record.

### Existing novels: validated synopsis repair

`tools/repair_synopsis.py` supports read-only preview by default and `--apply` for a deliberate repair. It can use an explicitly provided description or fetch a public **NovelFull book information page only**, not novel chapters.

For `--apply`, stage a modified ZIP, check the new EPUB and JSON, and verify the original chapter payloads and manifest are preserved. If it fails, keep the original untouched. This is an **in-place validated replacement, not a permanent separate backup**; users needing undo must keep their own copy.

Examples:

~~~powershell
python -m tools.repair_synopsis --zip "Downloaded_Novels\novel-example.zip"
python -m tools.repair_synopsis --zip "Downloaded_Novels\novel-example.zip" --apply
python -m tools.repair_synopsis --directory "Downloaded_Novels"
~~~

It does not automatically update the hosted reading application or private dataset after a local repair. That is a separate downstream import/update operation.

## 14. Experimental or restricted source support: do not silently expand scope

Different sites have different technical and permission restrictions. A parser existing in `tools/` does **not** mean automated whole-book download support is approved.

| Site or input | Current role in this repository | Safe boundary |
| --- | --- | --- |
| NovelFull | Production FanFicFare-backed bounded downloader | Authorised HTTPS source, verified range assembly |
| FreeWebNovel | Separate production public-page range downloader | Sequential requests, restrictions respected, missing chapters fail closed |
| ReadNovelFull | Production AJAX-index downloader with bounded chapter batches | One complete live book verified; each title still needs exact, consecutive TOC validation |
| WuxiaClick | **Bounded** public page source (20 chapters per run max) | Exact paginated TOC, rights gate, daily allowance awareness, no full-book harvest or quota evasion |
| Royal Road | Offline feasibility and authorised local EPUB import | No enabled live GitHub bulk downloader here |
| WTR-Lab | Offline feasibility and authorised local EPUB import | No automated website downloader enabled |
| Scribble Hub | Authorised offline EPUB import; **one** verified same-author FFN cross-post via FicHub | Direct Scribble Hub HTTP 403; no general site downloader or bulk menu |
| Novel Fire | Offline saved-HTML feasibility only | No automated novel crawling; respect published restrictions |
| Light Novel Pub | **Shut-down source**; historical saved-HTML parser only | No new live download support; successor NovelCodex does not host chapters |
| WebNovel | Read-only public metadata, HTTP/browser feasibility, constrained two-public-chapter tests, authorised saved-page/JSON/TXT imports | No unrestricted WebNovel all-chapter downloader, no locked content or challenge bypass |
| Local selectable-text PDF | Production offline conversion | Source review, no OCR |
| Authorised local EPUB | Production offline conversion | Source identity and archive validation |

### WuxiaClick bounded chapter downloader

Use `tools/wuxiaclick_source.py` for strict `https://wuxia.click/novel/<slug>` book IDs, numbered `/chapter/<slug>-N` links and linked `?page=N` TOC pagination. Live real index tests [#43729861621 (archived)](docs/research/source-test-evidence-archive.md) verified 2,276 *Martial World* and 1,709 *True Martial World* chapter entries. **Do not guess numeric URL suffixes**: a heading can say Chapter 0 when its URL ends `-1`; the site counts entries independently of maximal URL suffix. TOC entries belong to `section#chapters ol li a`, not the nearby latest or first-chapter navigation. Site labels include source numbers and dates, which must be removed before comparing text headings.

`tools/wuxiaclick_downloader.py` produces the standard verified EPUB/TXT chapter/metadata/cover output using `#chapter-content`, with strict heading identity checks, source hash and checkpoint integrity. `tools/wuxiaclick_chunks.py` reuses shared batch validation and assembly. It is **not** a full-book bulk scraper: site policy describes a daily signed-out offline download allowance of **20 chapters**. The code requires `--confirm-rights`, caps any range at 20 chapters, never schedules multiple parallel pieces for a full book and checks robots access before ordinary public-page requests. Multiple WuxiaClick books in a single bulk run must collectively fit 20 chapter selections. Do not run repeated jobs to exceed the daily allowance; cross-run allowance accounting is not implemented. The user's rights to store the works are not inferred from their public readability. When output artefacts are public, do not expose content without distribution rights.

The dedicated [WuxiaClick workflow](.github/workflows/wuxiaclick-download.yml) can be run for an authorised bounded range. The **same** existing [mixed-link bulk form](.github/workflows/library-bulk-download.yml) auto-routes WuxiaClick URLs. User must confirm rights for this site and Scribble Hub. Normal bulk retries, independent successful artefacts and failure recovery still apply. Never add a second bulk website selector.

### Author-verified Scribble Hub cross-post through FicHub

`tools/scribblehub_crosspost_downloader.py` is a **narrow, internet-enabled** route, distinct from both the direct NovelFull/FreeWebNovel downloaders and the network-free `tools/import_local_epub.py`:

- The user provides the original Scribble Hub **series** URL and `--confirm-rights`; no local EPUB is required. The command is `python -m tools.scribblehub_crosspost_downloader "<scribble-hub-series-url>" --confirm-rights`.
- `tools/scribblehub_verified_crossposts.json` is an explicit author cross-post allowlist. Currently it contains only Scribble Hub series `445037`, by MonkWithAPen, cross-posted by the same author as FanFiction.net story `14031894`. **Never** infer the mirror for an unrelated series simply from a similar title.
- The dedicated manual [`.github/workflows/scribblehub-download.yml`](.github/workflows/scribblehub-download.yml) uses the validated cross-post CLI and `tools/scribblehub_crosspost_artifact.py` to convert the validated ZIP to the **standard** book folder before `upload-artifact`. It runs the existing registry check and `tools.publish_registry`, and avoids publishing a nested ZIP. It has a mandatory authorisation checkbox and rejects unregistered novel IDs. Artefacts on public repositories may be publicly accessible.
- The downloader calls FicHub's documented `/api/v0/epub` and its same-host EPUB cache, **not** Scribble Hub's pages or the protected chapter AJAX endpoint. Source URL validation, story author/title/FFN numeric ID, reported count, first-chapter title and a numbered checkpoint are fail-closed.
- The 14 November 2026 remote test found **432** author-posted story chapters and a FicHub EPUB containing **two non-story introductory sections plus 432 actual chapters**. The code excludes only the two registered front sections when the verified first story chapter follows. If this structure or count changes unexpectedly, stop rather than silently shift chapters.
- Preserve cover and EPUB description if present, reconstruct a clean EPUB with exactly the story chapters, and call the **existing** `import_epub_to_zip` to stage and verify chapter SHA-256, EPUB integrity, ZIP CRC, metadata and stable Scribble numeric-ID identity. The command publishes to `Downloaded_Novels/` and requires `--replace` for updating an existing ZIP.
- FicHub's API is unstable and may be temporarily rate-limited or stale. Use a custom project User-Agent with contact; perform at most one export request plus one ebook request per operation; **no concurrent calls or automatic retries**. Do not expose or commit story text or upload the ebook into a public CI artefact.
- Tests in `tests/test_scribblehub_crosspost_downloader.py` and `tests/test_scribblehub_crosspost_artifact.py` use wholly synthetic EPUB fixtures and injected fake HTTP clients; they cover provenance, chapter completeness, front-matter exclusion, bad URL handling, rights, failed requests and rollback. Keep NovelFull and FreeWebNovel regressions green.

This route is also reused by the unified bulk workflow for authorised, registered cross-posts. It does **not** mean Scribble Hub's direct HTTPS chapter requests can be automated reliably. Unknown series IDs must fail with a clear explanation until another same-author cross-post is independently verified and registered.

### WebNovel modules

- `tools/webnovel_probe.py`: one public book metadata page, no chapter harvesting.
- `tools/webnovel_http_diagnostics.py`: one request and safe status/header diagnostics, no response body persistence.
- `tools/webnovel_browser_probe.py`: ordinary temporary Chromium browser feasibility; public book plus at most two chapter pages; no stealth/session import or challenge bypass.
- `tools/webnovel_public_two_chapter.py`: at most one public book page and two public chapter pages, only when access and rights allow.
- `tools/webnovel_export.py`: offline export of at most two user-supplied authorised chapter records.
- `tools/webnovel_saved_pages.py`: offline import of one or two locally saved authorised HTML/TXT chapter files.
- `tools/webnovel_bulk_import.py`: offline bulk import of up to **10,000 consecutively numbered** locally saved authorised chapters, with `--dry-run`, optional ranges and verified `--resume` state.
- `tools/WEBNOVEL_*.md`: instructions and precise limitations for each stage.

Do not infer from the bulk **local file import** that the project can fetch 10,000 WebNovel chapters. Importing user-held files and scraping a remote service are fundamentally different actions.

### Adding a genuinely new website

Before writing any live downloader:

1. Establish that the specific site's terms and permissions support the intended archiving.
2. Identify public canonical book paths, chapter numbering, metadata sources and access boundaries.
3. Build a **separate** offline HTML parser/fixture test with at most a small, authorised sample.
4. Reject access challenges, locked pages, unexpected redirects, empty chapter bodies, duplicates and missing numbers.
5. Add a dedicated adapter/module and bounded acquisition mechanism **only when justified**.
6. Prove stable source identity, chapter count, range checks, reproducible EPUB/ZIP export and full rollback behaviour.
7. Extend the existing **unified** bulk workflow rather than adding redundant bulk menus.
8. Run all NovelFull and FreeWebNovel regressions to prove the old pipelines remain unchanged.
9. Never use login automation, proxy rotation or content unlocking to make a prohibited source “work”.

## 15. GitHub Actions workflow catalogue and security

| Workflow | Trigger | Primary jobs | Output / side effects |
| --- | --- | --- | --- |
| `.github/workflows/ci.yml` | Push and PR | Ubuntu unit/synthetic pipeline; Windows smoke; Windows ZIP packaging | Test outputs only; short-lived synthetic artefact |
| `.github/workflows/pdf-conversion-ci.yml` | Relevant PR/push paths and manual dispatch | Ubuntu + Windows Python 3.12 PDF tests | Offline synthetic outputs |
| `.github/workflows/download-novel.yml` | Manual and reusable call | Prepare, bounded chapter batches, assemble, report | Temporary book artefacts and metadata registry PR |
| `.github/workflows/freewebnovel-download.yml` | Manual and reusable call | Prepare, bounded chapter batches, assemble, report | Temporary book artefacts and metadata registry PR |
| `.github/workflows/readnovelfull-download.yml` | Manual and reusable call | Discover AJAX chapter list, paced 100-chapter batches, verified EPUB assembly, publish registry | Temporary verified novel artefact; no website workaround |
| `.github/workflows/wuxiaclick-download.yml` | Manual and reusable call | Exact 100-entry paginated book TOC, single <=20-chapter confirmed-rights batch, verified EPUB and recovery | Bounded temporary source artefact only; no whole-book quota evasion |
| `.github/workflows/scribblehub-download.yml` | Manual and reusable call | Explicit rights gate, verified same-author FicHub cross-post, archive verification | Seven-day complete novel artefact and metadata-only registry PR; only allowlisted same-author cross-posts |
| `.github/workflows/library-bulk-download.yml` | Manual, one recommended download form | Accept mixed novel URLs and names, auto-detect sites, call five reusable workflows, always-run summary with failure-gated recovery | No website dropdown; avoids duplicate recovery transfers on success; preserves partial-failure artefacts and retry manifest |
| `.github/workflows/download-covers.yml` | Manual | Cover-only job | 30-day cover-image artefact; no chapter or registry edits |

The repository also retains one-shot or campaign-specific workflows (Yup/Idk discovery and dispatch, fanfiction queueing, curated waves, source audit, five-book TOC preflight, targeted retries and historical exports). Their presence in `.github/workflows/` does **not** mean they are currently active or safe to rerun. Inspect each workflow's trigger/path filter, marker-file guard, current run history and artifact before use. In particular, the 21 November source audit and five-book TOC preflight were read-only and have completed; neither downloaded chapter text.

Security/operational expectations:

- Workflow actions are pinned to reviewed **full commit SHAs**, not only mutable major tags.
- Workflows use Python 3.12 resolved dependency locks.
- CI's default permissions are read-only. Write/pull-request permissions appear only where publishing a metadata PR needs them.
- Never interpolate untrusted user text into a shell command without safe quoting/argument handling.
- Keep source URLs in environment variables or correctly quoted argument vectors. Do not use `shell=True` for downloader processes.
- Keep chapter content out of commit diffs, summaries and debug logs. Book artefacts can be accessible to other users of a public GitHub repo.
- No secrets or PATs should be embedded in tracked files; GitHub workflows use their available temporary token where authorised.
- When changing a reusable workflow, test both invocation paths: manual dispatch **and** Library - Bulk Download. Scribble Hub is now available through the single bulk menu only for explicitly verified same-author cross-posts with rights confirmation; no general Scribble Hub site scraping or unrestricted bulk coverage is implied.
- Do not remove mandatory CI jobs just because an intermittent live-site request is unavailable.
- External metadata-only NovelFull checks are **non-blocking** by design. Offline fixtures are the release gate.

## 16. Test map and minimum verification gates

### Core test collections

| Test file or collection | Focus |
| --- | --- |
| `tests/test_novel_downloader.py` | EPUB extraction, metadata, URL checks, direct chapter ranges, cache identity, imports, staged export and rollback, progress/checkpoints |
| `tests/test_chunked_download.py` | Batch planning, counts, piece identity, complete/reused artefacts, assembly, synopsis/cover/genre metadata |
| `tests/test_download_registry.py` | Canonical URL and range handling, expiry and completed record logic |
| `tests/test_publish_registry.py` | Latest-main metadata publishing, merge races and retry behaviour |
| `tests/test_mixed_source_bulk.py`, `tests/test_sequential_bulk_download.py` | Mixed-source URLs, automatic grouping with no UI site selection, deduplication and error handling |
| `tests/test_freewebnovel_source.py`, `tests/test_freewebnovel_downloader.py` | Public-site parser, boundaries, lock/challenge detection and complete ranges |
| `tests/test_epub_source_metadata.py` | OPF description/genre/status extraction |
| `tests/test_novel_covers.py` | Cover limits, safe book/image URL policy, EPUB cover handling |
| `tests/test_import_local_epub.py` | Offline, verified EPUB-to-ZIP import |
| `tests/test_repair_synopsis.py` | Synopsis repair integrity and dry run/apply |
| `tests/test_source_feasibility.py` | Offline parsing for investigated sources |
| `tests/test_readnovelfull.py`, `tests/test_wuxiaclick.py` | ReadNovelFull and WuxiaClick source/index/download contracts |
| `tests/test_overnight_queue.py`, `tests/test_five_book_toc_preflight.py`, `tests/test_fanfiction_campaign.py` | Source discovery, read-only TOC preflight and fanfiction campaign identity/queue safeguards |
| `tests/test_webnovel_*.py` | Separate WebNovel restricted/authorised import and feasibility behaviour |
| `tests/test_zip_packaging_windows.py`, `tests/cover_zip_smoke.ps1` | Portable ZIP compatibility, Windows processing, covers |
| `tests_pdf/test_pdf_to_novel.py` | PDF heading extraction, source fidelity, hashes, ZIP/EPUB integrity, source budgets |
| `tests_pdf/test_pdf_batch.py` | Multiple PDFs, non-destructive skips/failures and Windows one-click CMD |

### Standard test commands

~~~powershell
python -m pip install -r requirements.lock
python -m pip check
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p test_novel_downloader.py -v
python -m unittest discover -s tests -p test_chunked_download.py -v

python -m pip install -r requirements-pdf.lock
python -m unittest discover -s tests_pdf -p "test_pdf_*.py" -v
~~~

Run the relevant narrow suite while developing, **then all affected suites**, then check the workflow matrix. The Windows tests are indispensable when modifying PowerShell, CMD, filenames, path handling, line-endings or ZIP packaging.

### Non-negotiable regression scenarios

Changes to the relevant subsystem should prove all applicable cases:

- Two books whose URLs have the same terminal path do not overwrite each other.
- Same-title EPUB imports do not clobber different books by default.
- Explicit custom slugs cannot subvert source identity checks.
- A forced re-download failure or chapter count mismatch leaves a previously published book intact.
- A staging/rename failure rolls back to the complete previous generation.
- A process-interrupted export backup can be recovered on retry.
- Untracked `chapter_9999.txt` files survive an unrelated export; only previously tracked tool-owned chapter files are cleaned.
- Exact inclusive chapter ranges have no holes or repeated positions.
- Each range's file names, byte hashes, source identity and optional cover remain consistent.
- Cached artefacts are reused only after validation, not merely because a name exists.
- Source EPUB description/genres/status and optional covers survive final batch assembly.
- Missing descriptions/covers remain absent rather than being invented.
- A PDF with inaccessible text, bad boundaries, duplicate chapter identities or size/page-budget violations fails without publishing a bad ZIP.
- A good existing ZIP is skipped; an invalid existing ZIP is preserved for investigation.
- The Windows launcher handles whitespace paths, PowerShell 5.1 syntax, startup checks and visible nonzero error codes.
- Registry updates do not lose another novel's download record when multiple workflows finish concurrently.

### Evidence standard

A green unit suite means **the exercised behaviours passed**, not that real websites are stable. Describe findings accurately:

- **Confirmed by deterministic test**: e.g. synthetic four-chapter EPUB assembly.
- **Confirmed by checked source**: e.g. URL validation or known workflow limits.
- **Requires live verification**: e.g. current chapter selectors, access controls or complete remote catalogue.
- **Not verified here**: e.g. private dataset acceptance or long-term remote archive durability.

Avoid the overstatement “nothing can break”. Use targeted regressions, meaningful failures and explicit residual risk.

## 17. How an AI agent should approach changes

### Before editing

1. Read this file, then `README.md` and the focused guide for the component.
2. Check current `main`, open PRs, active workflow runs and latest related changes. Do not assume the baseline commit shown above is still current.
3. Identify the exact entry point, source module, orchestration workflow, output format, downstream consumer and affected tests.
4. Determine whether the requested operation is **read-only**, **local data-writing**, **network-fetching**, **GitHub publishing**, or **destructive**. Do not blur those categories.
5. Confirm whether the affected feature is established production, locally enabled only, or restricted feasibility.
6. Write down the invariants most likely to regress, especially identity, chapter count, filename formats and original-data preservation.
7. Check for current artefacts/records that must remain backward-compatible.

### During implementation

- Prefer a focused topic branch and a narrow PR; do not mix refactors of unrelated adapters.
- Change the smallest coherent part of the system, but follow data-contract changes through every producer, validator, registry writer and Windows consumer that handles them.
- Add regression tests for both normal success and failure/rollback behaviour.
- Use fixtures made from original synthetic prose, tiny legal/public-domain samples or mocked HTTP responses. Avoid placing real copyrighted novel text into Git.
- Keep existing functioning download logic and original source-site integrations unchanged unless directly necessary.
- Prefer offline, dependency-injected tests over automatic live requests.
- Avoid temporary workflow generators or diagnostic files remaining on `main` after completion.
- Verify output names, source identity, chapter manifests, EPUB spine, image metadata and SHA-256 contracts end to end.
- Keep lockfiles, README and this handbook in sync with actual changes.

### Before merging or closing a task

- Inspect the diff to ensure **only intended files changed** and no novel text, token or personally sensitive data was committed.
- Run narrow tests, full applicable offline test suite, and both platform matrices where applicable.
- Confirm GitHub Actions has concluded **success**, not merely started or queued.
- Treat a non-blocking failed live metadata smoke differently from a failed deterministic unit test; investigate but do not falsify the status.
- Review PR base/head freshness, successful checks and merge status.
- After merging, verify `main` points to the expected commit and its post-merge workflows pass.
- Do not claim that downstream cloud storage, authentication or real full-book downloads were exercised unless they truly were.
- Summarise changes, test evidence, remaining caveats and any operator action clearly.
- Do not alter or delete unrelated branches, artifacts, datasets or files unless explicitly part of the requested work.

### Review priorities

When time is constrained, prioritise:

1. Preventing loss or misattribution of an existing novel.
2. Preserving complete and correctly ordered chapter/manifest/EPUB outputs.
3. Keeping site access within explicit user permissions and the source's constraints.
4. Preserving Windows retrieval and historical archive compatibility.
5. Preserving recoverable partial work and valid completed artefacts.
6. Eliminating reproducibility drift and CI failures.
7. Improving documentation and operational ergonomics.

## 18. Typical user tasks and the files to inspect

| User request | Start here | Validation |
| --- | --- | --- |
| “A downloaded book has wrong chapters or a missing range” | `novel_downloader.py`, `tools/chunked_download.py`, `tools/download_registry.py` | Exact source/range identity, every position, EPUB spine, source metadata |
| “My previous EPUB was overwritten or the wrong book reused” | `novel_downloader.py` | Collision tests, failed forced refresh, rollback |
| “A large NovelFull download times out” | `.github/workflows/download-novel.yml`, `tools/chunked_download.py`, `tools/fanficfare_progress_runner.py` | Resume/reuse valid ranges; incomplete batches never register |
| “FreeWebNovel gives the wrong chapter” | `tools/freewebnovel_downloader.py`, `tools/freewebnovel_source.py` | Number/title/body checks; no auto bypass |
| “Add another bulk option” | `tools/mixed_source_bulk.py`, `.github/workflows/library-bulk-download.yml` | Reuse single grouped bulk menu; no duplicate workflow |
| “Why is a book not in DOWNLOADED_NOVELS.md?” | `tools/publish_registry.py`, `tools/download_registry.py` | Check artefact success versus registry PR state |
| “Why does downloaded novel ZIP not appear locally?” | `tools/download_all_artifacts.ps1`, `tools/zip_novel_artifacts.ps1` | Existing ZIP scan, expired artifact, correct nested book, local log |
| “Abe the Wizard / historic bulk artefact contains extra directories” | `tools/zip_novel_artifacts.ps1` | Exact source metadata, only one correct book ZIP |
| “Make a PDF usable by the reader” | `tools/pdf_to_novel.py`, `tools/pdf_batch.py`, `docs/pdf-to-novel.md` | Boundary report, TXT fidelity, ZIP+EPUB validation |
| “Convert my already-authorised EPUB” | `tools/import_local_epub.py` | Source URL identity, ZIP safety budgets, no silent overwrite |
| “New novels have no synopsis/genre” | `tools/epub_source_metadata.py`, `tools/chunked_download.py` | Source OPF metadata and final EPUB/JSON equality |
| “Old novel ZIP is missing synopsis” | `tools/repair_synopsis.py` | Dry-run first; chapter-manifest preservation |
| “Download only covers” | `tools/download_covers.py`, `tools/novel_covers.py` | Only images; no novel archive mutation |
| “Automate downloading from WebNovel, WTR-Lab, Novel Fire etc.” | `docs/research/source-feasibility-2026-11-15.md`, the specific feasibility modules | First verify permission; do not bypass site restrictions |
| “CI failed on Windows” | `.github/workflows/ci.yml`, PowerShell scripts, Windows test files | PS5.1 parse/parameter rules, paths with spaces, exit status |

## 19. Troubleshooting and expected failure semantics

### Download reports success but appears incomplete

Check whether this was a **direct whole-book CLI** run without `--expected-chapters` or a **bounded Actions** run. Direct mode may have lacked an authoritative external count. For Actions, inspect plan total and selected bounds, complete batch manifests, final assembled `chapters.json` and the EPUB spine. A short or missing chapter must be a failure, not “completed with warnings”.

### A batch re-downloads despite an earlier run

The old artefact may be expired, absent, corrupt, missing the exact range, tied to another source, or missing newer metadata pipeline capabilities. That is intentional. Inspect `reuse_complete_piece()` diagnostics rather than deleting cache checks to save a download.

### A book is in the registry but cannot be downloaded

The registry preserves history after the temporary GitHub artefact expires. Check `expires_at_utc` and GitHub's actual artefact state. If an authorised local ZIP already exists, retain it. The registry is not remote long-term book storage.

### Registry PR did not merge

The book artefact can exist even when metadata publishing is blocked. Inspect the publisher's PR link, branch permissions, GitHub Actions permission to create PRs, merge conflicts and retry logs. Do not record success unless the registry was actually updated.

### A ZIP exists but the Windows downloader does not skip it

The ZIP may not be the expected one-book structure, may have wrong `source_url`, missing EPUB, mismatched manifest, extra unrelated folders or invalid cover. Validate the **contents**, not just the name. Do not overwrite or delete the ZIP simply to suppress the error.

### A PowerShell CMD launcher closes or shows a parameter error

Run `-CheckSetup` first and inspect `download-last-run.log`. Review syntax under **Windows PowerShell 5.1**, not only `pwsh`. Paths must resolve relative to the script and preserve spaces. The CMD's exit status and pause path are intentional.

### The PDF converter refuses a book

Common causes: scanned/image-only pages; no reliable chapter boundaries; missing title/author metadata; numbered gaps; source headers/footers confusing detection; password protection; or the configured resource limits. Use `--inspect` and a manually reviewed boundaries file if appropriate. Never fill missing prose with generated content to force a pass.

### A novel has no cover or synopsis

Not all sources supply those fields. Confirm that the source OPF/book page actually contained them; check metadata pipeline flags on cached ranges and the final EPUB/JSON. Do not hallucinate source data.

### A restricted website responds with 403 or a challenge

Stop. Diagnostic failure is a valid result. Do not automatically retry, spoof an authorised session, use a solver, rotate proxies or expand to hidden APIs. Read the relevant feasibility document before changing site support.

## 20. Known limitations and deliberate trade-offs

These should remain explicit when discussing the project or proposing future work:

1. **No universal completeness guarantee from direct downloads without a known expected count.** The batch workflow is stronger because it discovers and verifies bounds.
2. **Live-site behaviour changes.** FanFicFare adapters, FreeWebNovel HTML selectors, website permissions, redirects and catalogues can change independently of this repo.
3. **Input URL hardening is not a complete network security sandbox.** Avoid presenting it as proof that every DNS resolution, redirect or adapter internal request cannot reach private destinations.
4. **Staged directory replacement is recoverable, not globally atomic.** A crash between renaming the old and new directories can leave a recoverable backup for the next invocation.
5. **A green offline CI run is not a completed real-novel download.** The optional live metadata-only check is neither a rights grant nor a chapter-text acceptance test.
6. **Python lockfiles pin versions, not distribution hashes.** Upstream artefact integrity still depends on package sources and runtime environment.
7. **GitHub Actions artefacts expire.** Local verified ZIP copies or other authorised storage are needed for retention beyond their lifecycle.
8. **Cover-only retrieval does not rewrite old ZIPs.** Synopsis repair is a separate explicit action.
9. **PDF extraction is not OCR, proofreading or guaranteed layout recovery.** Human review of warnings and chapter samples remains necessary.
10. **Other source modules are research or local import only.** WebNovel, WTR-Lab, Royal Road, Novel Fire and Light Novel Pub do not automatically become supported hosted download choices.
11. **Separate downstream repositories may enforce stricter validation or different upload limits.** Test integrations there; do not claim this repo controls their behaviour.
12. **Copyright and site permission constraints remain external prerequisites**, regardless of technical feasibility or how many unit tests pass.

## 21. Documentation cross-reference

When changing a subsystem, also consult the relevant living guide:

- `README.md`: general operation and latest end-user instructions.
- `PDF-to-Novel/README.md` and `docs/pdf-to-novel.md`: one-click Windows conversion, boundary overrides and validation reports.
- `docs/research/source-test-evidence-archive.md`: historical observations, rights limitations and safely archived GitHub-runner diagnostics.
- `docs/research/source-feasibility-2026-11-15.md`: complete, evidence-linked 15 November 2026 candidate matrix with GitHub Actions robots-first reachability runs, blockers and required rights gates. Do not re-enable shut-down/restricted domains or silently add new website options.
- `docs/research/source-test-evidence-archive.md`: archived WuxiaClick, LibRead and NovelBin technical observations; an HTTP 200 is not a full novel download approval.
- `docs/website-support.md`: current FreeWebNovel and other supported website restrictions.
- `docs/research/webnovel-browser-probe.md`: ordinary browser feasibility and challenge stop conditions.
- `docs/research/webnovel-two-chapter-sample.md`: bounded public chapter probe.
- `tools/webnovel_saved_pages.py`: legacy one/two-chapter parser used by the current bulk importer.
- `tools/webnovel_export.py`: legacy limited JSON-to-EPUB/TXT converter retained for local compatibility.
- `docs/research/webnovel-bulk-import.md`: offline, validated/resumable bulk import of saved local chapters.
- `DOWNLOADED_NOVELS.md`: generated historical registry view.

## Operational addendum: campaigns, handovers and later AI sessions (20 November 2026)

This section documents behaviour added after the handbook's original 13 November architecture baseline. For precise procedures and dated facts, consult the [runbook](docs/operations-runbook.md) and [status](docs/current-status.md).

### Three-source source audit and follow-up preflight (21–22 November 2026)

- The one-time [source audit run #44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606) checked 91 eligible Yup/IDK rows using 336 public book-page requests: **26 exact public listings** (18 Yup, 8 IDK) and **65 unresolved** (36 Yup, 29 IDK). It was read-only: no chapter prose and no rights were verified. None of the 26 listing matches is in the 343-record completed registry. The 90 red/Dropped exclusions remain excluded.
- The read-only [five-title TOC preflight #44926984233](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984233) found two index passes: *Doom Lord* (155 chapters) and *Girl, I'll Teach You Cultivation* (283). Three failed: *Beast Piercing The Heavens* (duplicate Chapter 11 links), *Godly Student* (invalid chapter URL), and *The Military Female Soldier With Unwavering Stubbornness* (large missing-number range). All five had `rights_verified=false`; no chapter text or download was produced.
- The 26 listing matches are grouped as 12 older blocked titles from #371, nine titles with 20-Nov source/TOC failures, and five fresh candidates. Do not treat the 26 as a ready-to-download queue.
- Exact #452 logs: *Past Life Returner* expected Chapter 501 but received Chapter 500; *This MC Is Kickass* expected Chapter 101 but received Chapter 102. The ReadNovelFull preparation jobs for *Martial Arts System*, *Path to Heaven* and *Weapon Master* exited during URL validation without a useful surfaced exception; *The Alchemist God* and *The Mightiest Leveling System* explicitly stopped with `Invalid ReadNovelFull chapter URL`. Do not retry these URLs unchanged.
- The #44769541580 child dispatch contained four URLs, but only the *Past Life Returner* and *This MC Is Kickass* matrix jobs actually ran. The other two, *Tomb Raider King* and *World Domination System*, have no chapter logs from that child run; do not describe them as failed chapter downloads. The current bulk workflow uses `fail-fast: false` so one matrix failure does not cancel later titles.
- The targeted *The Alchemist God* retry #44804318431 ran on PR #453's merged commit and still failed during indexing with `Invalid ReadNovelFull chapter URL`. PR #453 adds strict genuine-prologue support, but it did not resolve this different index shape. No retry until the actual offending TOC URL is identified and a regression test is added.
- The 12 older #371 titles remain blocked, but their failure classes differ. Nine have confirmed chapter-identity mismatches: Awakening (2→9), Condemning the Heavens (1→0), Flower Master In The City (1101→1110), Heavenly Star (266→267), Ex Rank Supporting Role’s Replay (851→852), Game Market 1983 (125→124), Parasite in Love (2→1), Sense (1→0) and The S-Classes That I Raised (251→216). Beauty And The Bodyguard timed out after three source attempts; no TOC was obtained. Legend of Swordsman produced no final ZIP and only a partial 5601–5800 batch; issue #371 reports Chapter 5742 returned an empty body. Omega Summoner's run #44447221591 has successful chapter batches 1–3,083, but recovery manifest `14496292098` says 0 ZIPs saved and lists it as missing/failed; the 2069→2070 mismatch claim is not present in that run's logs. Treat Omega as not archived/registered, not as a verified chapter mismatch. See the 22 November reconciliation appended to issue #371.
- [Source-audit report](campaigns/overnight/source-audit-report-20261121.md) and [alternative-source research](campaigns/overnight/alternative-source-research-20261122.md) preserve the current evidence.

### Curated source URLs are preferred to website discovery (20 November 2026)

**New default for user-requested downloads:** Identify missing approved Yup/Idk/fanfiction titles first; look up and manually verify each exact, supported public **book page**, preferring **NovelFull**, then **ReadNovelFull**, then **FreeWebNovel**. Reconcile title/author/source aliases, the 90 global red/Dropped exclusions, 14 prior deterministic failures, the canonical completed registry and every currently active workflow. Record real source URLs plus title, on-site title, platform and verification evidence in a reviewed JSON manifest. Submit the **full verified URL list directly** through existing `Library - Bulk Download`, not through the old runtime source-search dispatcher. The one-time source-reviewed launcher `tools/dispatch_curated_bulk.py` and [operations runbook](docs/operations-runbook.md) demonstrate the pattern; the launcher's **only job** is validation, duplicate prevention, capacity gating and submitting the literal URLs with `force=false`. It must not search websites, generate guessed slugs, bypass source restrictions or mix original and derived titles without evidence. A source link does not itself grant reproduction rights or prove chapter completion. The previously activated search-based large wave remains historical; do not rerun its marker or silently re-enable runtime discovery.

### Source-verified campaigns and throughput

- `campaigns/overnight/excluded-90.json` is a **global denial list**, not merely a scoring preference. Keep all 90 red/Dropped titles out of both Yup and Idk campaigns, including cross-sheet duplicates. Never bypass this with a guessed alternate title.
- `campaigns/yup-pilot/backlog-163.json` and `campaigns/overnight/idk-82.json` are **campaign tracking snapshots**, not the user's full live HF inventory. On 20 November the 163 Yup entries were categorised as six wave-three requests, four wave-four requests and 153 requiring source verification. Do not mistake `needs_source_verification` for `ready_to_download`.
- The reviewed first waves use `tools/campaign_yup_dispatch.py` and new `campaigns/yup-pilot/requests/batch-XX.json` files, traditionally two books per child job. Wave four added batches 09 and 10. Do not re-submit their URLs while those jobs are running.
- `.github/workflows/large-verified-waves-20261120.yml` and `tools/large_batch_dispatch.py` implement a **one-time** larger campaign: live read-only exact-title discovery, Yup before Idk, **up to 40** approved titles, **10 titles per child bulk run**, no more than **two active** `Library - Bulk Download` runs, plus controlled dispatch pacing. Code limits permit at most 12 titles per batch or 48 in a different reviewed invocation; they are **not** automatic targets.
- `campaigns/overnight/blocked-full-retries-20261120.json` excludes **14** specific unresolved failure cases. Handle their real chapter-numbering, absent-content, timeouts or transient network faults individually under [issue #371](https://github.com/RichardDaffern/Novel-Retriever/issues/371); do **not** add a force flag, disable a source index check or automatically restart every batch.
- One-time workflows are activated by an **added** marker file. An existing marker, workflow rerun or code-only doc change does not authorise a second campaign. New work requires a new, reviewed, uniquely named request and duplicate/source/rights checks.
- Before altering `large_batch_dispatch.py`, `overnight_queue.py` or pilot request logic, run `tests/test_large_batch_dispatch.py`, `tests/test_overnight_queue.py`, `tests/test_campaign_yup_dispatch.py` and the relevant full suite. Keep source-title, registry, denied-title and in-flight workflow tests.

### Fanfiction is separate, with explicit source limits

- The immutable 43-title catalogue is `campaigns/fanfiction/webnovel-favourites-43.json`: 24 Naruto and 19 Harry Potter titles. Keep its counts separate from Yup/IDK and from the user's separately confirmed **70 private-HF imports**.
- Its `review_state` is initial campaign/source-review state, not live source discovery or download completion: 1 row is `already_downloaded`, 10 are `public_source_listing_matched` (7 already complete in the registry, 3 blocked), and 32 are `needs_source_verification`. The five exact supported-host candidates found in later rounds remain in those 32 until edition, full-index and permission gates pass. This reconciles to **8 complete, 3 blocked and 32 research targets**. `downloaded_novels.json` is authoritative for completion and run/artifact state.
- Current fanfiction state: **8 registry-complete**, **3 separately blocked/source-matched**, and **32 source-research targets**. The corrected supported-host pass found **5 exact title+credited-author listings**, **2 near/variant matches**, and **25 with no exact supported listing**. No candidate has documented archiving rights; no fanfiction run was dispatched. See [round 3](campaigns/fanfiction/source-verification-round-3-20261122.md) and the [identity ledger](campaigns/fanfiction/source-identity-resolution-20261122.md). Round 5 checked additional WebNovel/alternate-host metadata for 21 title records, found 0 new exact supported-host listings and 0 explicit permissions; see [round 5](campaigns/fanfiction/source-verification-round-5-20261122.md). Round 6 ran 30 author-qualified and 26 title-only searches across the three supported hosts, found 0 additional exact listings and 0 permissions; it identified Gezenshaft as the original author of *The Healer* and documented FirstHokage's warning against unauthorised Amazon use and Devil_Hex's permission requirement before translation. See [round 6](campaigns/fanfiction/source-verification-round-6-20261122.md). Round 7 searched all 32 remaining title/selected-author pairs and checked the three supported hosts, finding 0 additional exact supported-host listings and 0 explicit permissions. It identified IHaveNoNamingSense as translator of *Life of a Villain in The Naruto World* (original author Yun Sixie), confirmed a PinkSnake/1PinkSnake1 cross-post lead for *Konoha's Trickster* without underlying-work clearance, and recorded chapter/edition differences for *The Wind Calamity*, *Konoha's Medical Ninja* and *There Will Be No Third Dark Lord*. The selected *HP: The Arcane Thief* FWN edition has 254 chapters and the +1 auxiliary-entry offset fix from PR #463; its separate 183-chapter FanFiction.net cross-post is not proof that the selected edition is incomplete. The full FWN TOC and rights remain unverified. *Naruto: Kurotsuchi Mayuri* is already complete in the registry at 524 chapters; a 490-chapter WebNovel listing is a duplicate/edition mismatch, not a new target. See [round 7](campaigns/fanfiction/source-verification-round-7-20261122.md). PR #466 adds exact chapter-to-URL examples to FreeWebNovel's non-linear TOC error, with an offline regression test; all four CI jobs passed. It preserves the fail-closed stop and does not retry Wind Calamity.
- The 8 completed entries have seven currently present Actions artifacts and one expired artifact. The seven present artifacts are publicly accessible and rights remain unverified; do not link, download, or create another public copy. The connected GitHub operations do not expose artifact revocation. *The Adventurous Gamer Ninja - Daichi Hekima*'s artifact expired on 21 November. *A New Snake In The Shinobi World* has 423 successful chapter batches and a present archive artifact even though its shared run #44378479201 failed on *The Wind Calamity*.
- PR #463 is merged: the selected 254-chapter FWN edition of HP: The Arcane Thief has the +1 auxiliary-entry URL offset fix; its 183-chapter FanFiction.net cross-post is separate, and archive permission remains unresolved. Wind Calamity's non-linear mapping still hard-stops. PR #466 adds exact mapping diagnostics for that failure and passed CI #44971034816 (4/4); it does not infer URLs or retry the title.
- Run #44379388243's nine chapter-batch jobs succeeded for 444 chapters and the workflow uploaded final novel artifact #14462633408. The assemble job then failed during registry publication: it opened PR #275 and six merge attempts failed after the base branch changed and the PR remained unmergeable. The artifact contents were not fetched or independently verified because rights remain unresolved. Artifact #14462633408 (expires 2027-02-16T19:20:05Z) remains public and rights-unverified. Do not merge, re-download, link, create another public archive or claim it as a cleared acquisition.
- A public listing, English label, translator credit, Patreon page or complete-looking first TOC page is not permission to archive copyrighted text. No account bypass, guessed slug, paywall scrape or access-control workaround.
- The fanfiction source-research pass for the 32 outstanding catalogue entries is complete through round 18; eight are registry-complete, three remain blocked and 32 are researched but rights-unresolved. The three blocked works remain held. The 65 unmatched Yup/IDK audit rows have also completed their first alternative-source pass (36 Yup, 29 IDK). Reconcile aliases before any acquisition: 13 rows now map to completed registry titles, including `Very Pure And Ambiguous` = `So Pure, So Flirtatious` (Fishman The Second; 1,621 chapters, run #42513348683), and one row maps to the global exclusion list. This leaves **51 distinct non-alias titles (23 Yup, 28 IDK)**. Preserve the acquisition order explicitly: (1) triage the 26 exact source matches and their known blocked titles; (2) complete exact title/author source research for the 43 selected fanfictions and repair the three blocked fanfiction sources; (3) only after that fanfiction source-research pass, investigate the 65 unmatched Yup/IDK rows. That fanfiction pass is complete for the current search scope through round 18. Continue deeper alternative-source research Yup first, then IDK. Four URL-pattern 404s do not establish worldwide unavailability. Do not request the user's screenshots again. No rights-cleared title or download run has resulted. See [Yup round 8](campaigns/overnight/yup-alternative-source-research-round-8-20261123.md), [IDK rounds 9–11](campaigns/overnight/idk-alternative-source-research-round-9-20261122.md), [IDK round 10](campaigns/overnight/idk-alternative-source-research-round-10-20261122.md), [IDK round 11](campaigns/overnight/idk-alternative-source-research-round-11-20261122.md) and the [five-candidate preflight](campaigns/overnight/five-source-candidate-triage-20261123.md).
- The 26 source-audit listings and the 65 unresolved Yup/IDK entries remain separate from the 343 completed registry records. The alias set is: Invincible Conqueror=Invincible; Xian Ni=Renegade Immortal; Records of the Human Emperor=The Human Emperor; School Prince is a Girl=National School Prince Is A Girl; A Thought Through Eternity=A Will Eternal; Very Pure And Ambiguous=So Pure, So Flirtatious.
- The audit preflight's `previously_known=349` is a union count, not a download count: 343 registry titles plus 21 prior verified-URL rows with 15 overlaps. The six URL-manifest-only titles are Desolate Era, A Record Of Mortal’s Journey To Immortality, Warlock Of Magus World, Solo Levelling, Advent of Archmage and Charm Of Soul Pet. Keep them separate from the 343 completed records and the 70 user-confirmed private-HF imports.
- Keep the shared bulk-workflow cap at **two active runs** and **no more than ten titles per batch**. No bulk download workflow was queued or in progress at the 22 November 06:39 IST check; documentation CI on PR #464 and diagnostics CI on PR #465 are separate and must not be counted as downloads.

### Hand-off, storage and operator claims

- A successful per-novel ZIP is a **source acquisition artefact**. The [Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller) separately validates/imports to private HF and preserves personal reading fields. Never make a private dataset write from the Retriever repo as a side effect of completing a GitHub Action.
- The historical 104-book export and authentic 104-cover recovery have already been completed and individually verified, including the downstream cover-only import. See [current status](docs/current-status.md). Do not re-upload originals or revive one-shot repair workflows merely because a fresh run sees old evidence.
- For bulk export, put **only individual novel ZIPs** into the Storage Controller's input `novels/`. Keep outer export ZIP, `manifest.json`, `SHA256SUMS.txt`, README and `review-conflicts/` outside it.
- **Every substantial agent session ends** with the [handover template](docs/agent-handover-template.md): exact branch/SHA, PRs, checked-at timestamp, dispatcher and child run IDs, counts at each stage, artefact expiry, remaining failures, tests, rights limitations and the one safe next action. Update [current status](docs/current-status.md) only with evidence.
- Never say that monitoring, downloads or merges will continue on their own unless a real scheduled automation or GitHub workflow is already active and confirmed. Never claim a reader refresh or private HF repair succeeded solely from Retriever logs.

## 22. Concise final rules for coding agents

> **Preserve source identity. Verify every expected chapter. Protect existing novel data. Never mistake a checkpoint for a finished book. Respect source-site permissions. Keep real novel text out of Git. Maintain both Windows and Linux compatibility. Test offline first. Keep the single bulk workflow. Do not silently expand experimental source capabilities. Do not declare a deployment, merge, download or CI result successful until it is confirmed.**

This handbook is designed to lower the cost of understanding a large, interconnected personal utility project. It is intentionally detailed, but it remains **documentation**: the latest executable source, workflow definitions, tests and explicit operator requirements take precedence whenever reality changes.


## Fanfiction source research round 9 (22 November 2026, 09:22 IST)

The latest round-9 report is [campaigns/fanfiction/source-verification-round-9-20261122.md](campaigns/fanfiction/source-verification-round-9-20261122.md). It searched the 25 original 43-catalogue entries that had no exact supported-host listing, plus the three blocked works. It found **0 new exact NovelFull/ReadNovelFull/FreeWebNovel matches**, **8 additional non-supported catalogue/cross-post leads**, **0 explicit archiving permissions**, and **0 new download runs**. These alternate mirrors are identity/edition evidence only; they are not approved downloader sources, and their chapter indexes were not validated end-to-end.

Important author/rights findings:
- DevilHex explicitly requires prospective translators to ask permission first for *Naruto: The Wind Calamity*. No permission grant was found; keep its non-linear FreeWebNovel mapping fail-closed.
- INeedRest states they are not the original writer of *Konoha's Medical Ninja*. Run #44379388243's nine chapter-batch jobs succeeded for 444 chapters and the workflow uploaded final novel artifact #14462633408. The assemble job then failed during registry publication: it opened registry PR #275 and six merge attempts failed after the base branch changed and the PR remained unmergeable. The artifact contents were not fetched or independently verified because rights remain unresolved. Artifact #14462633408 remains rights-unverified. Do not re-download, register, link or create another public copy.
- *HP: The Arcane Thief* remains a 254-numbered-chapter FreeWebNovel edition plus an auxiliary entry; the 183-chapter FanFiction.net cross-post is a separate edition. PR #463's +1 offset fix is merged, but no archive permission was found.

Do not change the immutable 43-title catalogue, do not request screenshots, do not start the deferred 65-title Yup/IDK sweep, and do not dispatch or publish a download without exact work/author, English edition, complete ordered TOC and explicit lawful archiving permission.


## Fanfiction source research round 10 (22 November 2026, 09:59 IST)

The full metadata-only report is [campaigns/fanfiction/source-verification-round-10-20261122.md](campaigns/fanfiction/source-verification-round-10-20261122.md). It searched the 32 unresolved title/author pairs, rechecked the five exact supported-host candidates and two near matches, and investigated the three blocked works. **0 new exact supported-host matches**, **0 explicit lawful archiving permissions**, **0 rights-cleared titles** and **0 new download runs**. The result remains 5 exact supported-host candidates, 2 rejected near/variant matches and 25 without an exact supported-host listing.

The fanfiction source sweep also checked WuxiaClick and the restricted ScribbleHub route; it produced no exact fanfiction candidate. A separate Yup/IDK five-candidate follow-up later found three WuxiaClick alternatives, documented in campaigns/yup-pilot/five-book-alternative-source-check-20261122.md. ScribbleHub is not a general scraper: its downloader accepts only author-verified cross-post pairs in `tools/scribblehub_verified_crossposts.json`; its sole current record is *The Adventurous Gamer Ninja - Daichi Hekima*, already completed. New identity/edition findings include: *Life of a Villain in The Naruto World* is an English translation credited to IHaveNoNamingSense of a Chinese original by Yun Sixie; *Naruto: Konoha's Trickster* credits 杠精萝卜头 as the Chinese original author and PinkSnake as translator; *Reborn into Naruto World with Tenseigan* is a translation credited to Alex_Clive; *Naruto: Starting With Creating A Genius Persona* has 527 FreeWebNovel versus 487 NovelFlick chapters; *There Will Be No Third Dark Lord At Hogwarts!!!* has inconsistent 363/397/430 public counts and locked Patreon advance posts; and *Harry Potter: Platinum Dragon Wizard* has BlurryPinkSnake/BlurryDream author-credit and 422/424 chapter differences. These are metadata/edition leads, not rights clearance.

Blocked-work decisions remain unchanged: Wind Calamity's author explicitly asks translators to contact them first and its FreeWebNovel map remains fail-closed; Run #44379388243's nine chapter-batch jobs succeeded for 444 chapters and the workflow uploaded final novel artifact #14462633408. The assemble job then failed during registry publication: it opened PR #275 and six merge attempts failed after the base branch changed and the PR remained unmergeable. The artifact contents were not fetched or independently verified because rights remain unresolved. Artifact #14462633408 remains public/rights-unverified; Arcane Thief's +1 URL-offset fix is merged but rights remain unresolved. Do not retry or publish another archive.

The live check found 343 completed registry records, 70 separately user-confirmed private-HF imports, 90 exclusions, eight completed fanfiction entries, three blocked and 32 research targets. Seven completed fanfiction final artifacts remain public; the Adventurous Gamer Ninja artifact expired. Konoha Medical artifact #14462633408 is also public but unregistered. Seoul Station's Necromancer remains a 209-chapter completion in run #44922285166, artifact #14714778249. Source audit #44924359606 remains read-only: 26 exact listings (18 Yup, 8 IDK; 16 ReadNovelFull, 8 FreeWebNovel, 2 NovelFull), 65 unresolved (36 Yup, 29 IDK), report artifact #14714644436 expiring 21 December 2026. All 65 unresolved rows returned HTTP_404 on the four attempted URL patterns only; do not infer worldwide unavailability. Four audit rows alias completed registry titles (Invincible Conqueror, Xian Ni, Records of the Human Emperor and The School Prince is a Girl), leaving 61 distinct titles. A Thought Through Eternity is in IDK, not the 65 audit rows, and aliases to A Will Eternal. Post-merge main CI #44986296039 passed 4/4 after PR #469. PR #470 is a documentation-only follow-up with CI pending; no bulk download workflows were active at 10:50 IST. Keep the 65-title Yup/IDK sweep deferred.


## Five-candidate WuxiaClick alternative-source check (22 November 2026, 10:50 IST)

The metadata-only follow-up is documented in [campaigns/yup-pilot/five-book-alternative-source-check-20261122.md](campaigns/yup-pilot/five-book-alternative-source-check-20261122.md). It found three WuxiaClick leads among the five existing candidates: exact title/author listings for *Godly Student* and *Girl, I'll Teach You Cultivation*, plus the associated-title *Doomsday Lord* for *Doom Lord*. These are additional source URLs for existing candidates, not new titles.

None is eligible: Godly Student has 543 entries numbered 1–544 with the final four reusing original labels 537–540, against the official 17K original listing at Chapter 9,742 on 16 November 2026 (a secondary mirror shows 9,754); Girl, I'll Teach You Cultivation has a clean 1–283 English TOC but the original Chinese edition is 812 chapters and Novel Updates marks the English translation incomplete; WuxiaClick's listing ends at 283; Doomsday Lord has 328 chapters against a completed original whose official Hongxiu listing ends at Chapter 856 and its TOC contains duplicate/split/misnumbered entries. Beast Piercing The Heavens still has a duplicate Chapter 11 on ReadNovelFull and no WuxiaClick match. The Military Female Soldier still has 2,104 missing ReadNovelFull chapter numbers and no WuxiaClick match. No explicit archiving permissions were found. No download was dispatched.


## Fanfiction source research round 11 (22 November 2026, 11:15 IST)

The metadata-only report is [campaigns/fanfiction/source-verification-round-11-20261122.md](campaigns/fanfiction/source-verification-round-11-20261122.md). It rechecked the 25 catalogue entries without an exact supported-host listing against NovelFull, ReadNovelFull and FreeWebNovel, then checked newly surfaced author/catalogue pages and the three blocked works. **0 new exact supported-host matches**, **0 explicit archiving permissions**, **0 rights-cleared titles** and **0 new download runs**. The established result remains five exact supported-host candidates, two rejected near/variant matches and 25 without an exact supported-host listing.

New identity/edition evidence is limited to non-supported catalogues or refreshed metadata: *Hogwarts: Bloodline Wizard* (Innocent Angel; 1,049 chapters; translated by Atlas Studios); *Harry Potter: I, Tom Riddle, am not the Dark Lord* (ElvenKing20; WebNovel 701/702 chapter snapshots, older NovelUpdates and CHERREADS counts differ); *Harry Potter: Cael Vale's Journey to Hogwarts* (16622800; WebNovel 294 chapters, one FICOOL chapter endpoint only); *Harry Potter: The Duelist of Hogwarts* (MeowthTL; FICOOL listing); and a refreshed *Naruto: Konoha's Genius is a bit Ordinary?* page (SaintXI; 472 chapters). These are not NovelFull, ReadNovelFull or FreeWebNovel download candidates. The two near matches remain rejected: Talent System In The Naruto Universe credits Rashta rather than the selected Rashita; This Ninja Is Obviously Not Strong but Really Hard to Kill credits Wu Mian Qi Liang rather than selected nyawdao2. *Naruto: Konoha's Trickster* identifies 杠精萝卜头 as original Chinese author and PinkSnake as translator; *Life of a Villain in The Naruto World* identifies Yun Sixie as original author and IHaveNoNamingSense as translator. Neither distinction grants archive rights.

Blocked work remains unchanged: Devil_Hex's Wind Calamity note says translations appeared without the author's knowledge/permission and asks prospective translators to contact them first; this is a permission requirement, not a grant, and the FreeWebNovel map remains fail-closed. INeedRest repeats that they are not Konoha Medical's original writer; Xnovel is another listing under the same editor credit. Run #44379388243 assembled 444 chapters and uploaded artifact #14462633408, but registry PR #275 failed; do not retry, register or publish another copy. The Arcane Thief's selected FreeWebNovel edition remains 254 numbered chapters plus an auxiliary entry, distinct from the 183-chapter FanFiction.net cross-post; a Russian Rulate translation page links to WebNovel and Patreon but grants no archive rights. PR #463's +1 offset fix remains merged.

The original 43-title JSON is unchanged. Keep the reconciliation at **8 complete, 3 blocked, 32 research targets**. No screenshots or chapter text were requested or copied into the repository. Keep the 65 unmatched Yup/IDK rows deferred. At the live 11:15 IST check, main was 707cb0e076ad4db887e236f4ceaf87937349c13c, post-merge CI #44990799907 passed 4/4, and there were 0 queued/in-progress Actions runs. No download workflow was dispatched.


## Fanfiction identity corrections round 12 (22 November 2026, 11:30 IST)

The targeted identity report is [campaigns/fanfiction/source-verification-round-12-20261122.md](campaigns/fanfiction/source-verification-round-12-20261122.md), with the same corrections appended to the identity ledger. It clarifies that the selected credits for *Naruto Birdcage* (DeCakraWnloverz), *Konoha: Gu Master* (HyppoTL) and *Reborn in Konoha; I Think I'm Cultivating Immortality* (HyppoTL) are translation credits, not original authors. Their identified original authors are respectively 易安z, 宝石对影 and 余青衣. All three are non-supported catalogue editions; no archive permissions were found. FirstHokage's *Naruto: Chronicles of a Fire Ninja* author note reports unauthorised Amazon reuse, which is not a licence to this project.

No new exact NovelFull/ReadNovelFull/FreeWebNovel matches, explicit permissions, rights-cleared titles or download runs resulted. The immutable 43-title catalogue remains 8 complete, 3 blocked and 32 requiring research. The 65 unmatched Yup/IDK entries remain deferred. At 11:30 IST, main was a1af161846e72b042eb821e09e26e866205e9cd6, post-merge main CI #44991393466 passed 4/4, and no Actions runs were queued or in progress. PR #472 contains this identity follow-up and remains open pending CI; do not merge until green.


## Fanfiction source research round 13 (22 November 2026)

The latest metadata-only pass checked ten additional unresolved catalogue rows: *Naruto: Uchiha's Genjutsu Demon* (lazarus898), *Naruto: My Unique System* (Cloe23), *Naruto: The Hyuga Mastermind* (NahinS77), *Naruto: Becoming the Soul King* (Junkdog), *Naruto: Konoha's Genius is a bit Ordinary* (SaintXI), *Hogwarts: The Unscientific Wizard* (Crazy_DarkSide_Cat), *Succubus System At Hogwarts* (Dragonel23), *Harry Potter: The Bard of Hogwarts* (Dark_Peace), *Hogwarts: I Started as the Fool* (ulquiorra_cifer_1152) and *The Most Fortunate Malfoy in Harry Potter* (Devilsatan). No exact NovelFull, ReadNovelFull or FreeWebNovel listing surfaced, no explicit archiving permission was found, and no download run was dispatched. The report is [round 13](campaigns/fanfiction/source-verification-round-13-20261122.md).

Important identity/edition findings:
- *Succubus System At Hogwarts* is explicitly labelled a translation of *Hogwarts: I am the savior, and I am breaking up couples*; Dragonel23's Patreon advertises advance chapters, not archive permission.
- *Harry Potter: The Bard of Hogwarts* (Dark_Peace, 431 WebNovel chapters) is not verified as the same work as the 12-chapter FanFiction.net story *The Bard of Hogwarts* by Vindicare40k.
- *Naruto: The Hyuga Mastermind* has 380 catalogue entries but its final entry is labelled Chapter 381. *Naruto: Becoming the Soul King* has substantial count/index drift across WebNovel, WuxiaFull and other mirrors. *Hogwarts: I Started as the Fool* has 178 vs 222 chapter snapshots.
- SaintXI explicitly labels *Konoha's Genius is a bit Ordinary* a translation and says they do not own Naruto rights. A translator credit or public catalogue is not archive permission.

The three blocked sources were rechecked from exact Actions jobs: Wind Calamity #44378479201 job 135064355812 expected Chapter 51 but the page identified Chapter 48; Konoha Medical #44379388243 assembled 444 chapters but registry publication failed after six merge attempts on PR #275; Arcane Thief's old pre-PR-#463 batch expected Chapter 2 but the page identified Chapter 1, and PR #463 now contains the +1 offset fix. No retry is authorised until the specific index/edition issue and lawful rights are resolved. Keep the 65 unmatched Yup/IDK entries deferred until all 32 fanfiction research targets and the three blocked investigations are complete. Do not request screenshots, copy chapter prose, or create public archives without explicit rights.


## Fanfiction source and blocked-TOC follow-up round 14 (22 November 2026)

A targeted exact title/selected-credit pass covered ten unresolved catalogue rows: *Naruto: With Favorability System* (NahinS77), *Naruto: Binding Uchiha Sasuke, Hundredfold Return* (tambeerg), *Naruto: Transmigrated as an Uchiha* (NoviceAuthor), *Harry Potter: Platinum Dragon Wizard* (BlurryPinkSnake), *Hogwarts: Transmigrated as the Top Student* (Hyperbeeam), *Hogwarts: Bloodline Wizard* (Innocent Angel), *Harry Potter: The Duelist of Hogwarts* (MeowthTL), *Harry Potter: The Flaw of Slytherin* (Ghidorah_7074), *Harry Potter: Cael Vale's Journey to Hogwarts* (16622800) and *Harry Potter: I, Tom Riddle, am not the Dark Lord* (ElvenKing20). No new exact NovelFull, ReadNovelFull or FreeWebNovel listing could be verified, and no explicit archive permission was located.

Identity/edition findings:
- WebNovel spells the first title *Naruto: With Favorabiltity System* (465 chapters), labels it a translation, and links to a Xiaoshubao original. NahinS77 explicitly confirms being the translator; the original author remains unidentified. Do not treat NahinS77 as the original author or use the WebNovel page as a supported download source.
- *Naruto: Transmigrated as an Uchiha* is listed by WebNovel under NoviceAuthor at 327 chapters; Xnovel's NoviceAuthor page shows 326. A FreeWebNovel category-search snapshot surfaced the same title at 325 chapters, but no direct title page or author attribution could be verified. This is not an exact supported-host match.
- The other eight exact title/credit searches produced no verifiable exact supported-host listing. Search absence is not worldwide unavailability.

Blocked-source metadata recheck:
- *HP: The Arcane Thief*: the public FreeWebNovel TOC identifies Snollygoster, 254 numbered chapters and one auxiliary entry. This supports the known +1 auxiliary-entry distinction addressed by PR #463, but only the first TOC page was inspected; full post-fix index validation remains incomplete. No archive permission.
- *Naruto: The Wind Calamity*: the public TOC's latest labels pair 949→942, 948→941 and 947→940, confirming that displayed and internal chapter numbers differ. The existing fail-closed mapping is correct; do not retry without a complete one-to-one map and author permission.
- *Konoha's Medical Ninja: One Punch to beat up Madara*: the public TOC lists 444 chapters and credits INeedRest. Run #44379388243 assembled the 444-chapter archive, but registry publication failed after six PR #275 merge attempts. Original-author and archive rights remain unresolved; do not merge, re-download or republish.

The 43-title catalogue remains 8 complete, 3 blocked and 32 research targets. The 65 unmatched Yup/IDK entries remain deferred. No screenshots, chapter prose or archive bytes were fetched; no download run was dispatched. See the [round-14 report](campaigns/fanfiction/source-verification-round-14-20261122.md).


### Fanfiction source research round 15 (22 November 2026, 14:28 IST)

The metadata-only round-15 report is `campaigns/fanfiction/source-verification-round-15-20261122.md`. It ran 20 exact title/credited-author web searches and fresh identity/rights checks. It found **0 new exact NovelFull, ReadNovelFull or FreeWebNovel listings**, **0 explicit archive permissions**, **0 rights-cleared titles** and **0 download runs**. New evidence distinguishes PinkSnake's permitted reuse of their translation from rights to the underlying Naruto derivative work; identifies 黑色炼金师 as the Chinese original author behind the Hyperbeeam Harry Potter translation; and records additional chapter-count drift for *Harry Potter: I, Tom Riddle, am not the Dark Lord*. Paid Patreon access and public mirror listings remain non-permissions. The three blocked works retain their stop conditions. Keep the 65 unmatched Yup/IDK rows deferred.


## Fanfiction source research round 16 (22 November 2026, 14:44 IST)

Round 16 searched 15 exact title/credited-author pairs and rechecked the three blocked works. It found **0 new exact NovelFull, ReadNovelFull or FreeWebNovel listings, 0 explicit archive permissions, 0 rights-cleared titles and 0 download runs**. New metadata confirms SaintXI's *Naruto: Konoha's Genius is a bit Ordinary* is a translation whose author disclaims Naruto rights; *Harry Potter: Cael Vale's Journey to Hogwarts* is by 16622800 and has a third-party FICOOL listing; *Hogwarts: Bloodline Wizard* is a completed 1,049-chapter translation credited to Innocent Angel/Atlas Studios; NoviceAuthor's *Naruto: Transmigrated as an Uchiha* has 327 WebNovel vs 326 Xnovel chapters; and Ghidorah1707/Ghidorah_7074 is the cross-post identity for *The Flaw of Slytherin*. Patreon advance access is not archive permission. Wind Calamity still requires author contact and a complete chapter map; Konoha Medical's credited editor says they are not the original writer; Arcane Thief's FanFiction.net 183-chapter cross-post differs from the 254-chapter FreeWebNovel edition. Keep the 65 unmatched Yup/IDK rows deferred. See the [round-16 report](campaigns/fanfiction/source-verification-round-16-20261122.md).


## Fanfiction source research round 17 (22 November 2026, 15:56 IST)

See [round 17](campaigns/fanfiction/source-verification-round-17-20261122.md).

- Exact title + selected-credit searches were repeated for all 32 unresolved entries across NovelFull, ReadNovelFull, FreeWebNovel and WuxiaClick. **0 additional exact supported-host listings** surfaced; three already-known FreeWebNovel matches resurfaced (Tenseigan, Chronicles of a Fire Ninja and Starting With Creating A Genius Persona). The two near/variant matches remain rejected.
- **0 explicit archive permissions, 0 rights-cleared titles and 0 new download runs.** The 43-title catalogue remains 8 complete, 3 blocked and 32 research targets.
- Fresh metadata reinforces edition/rights blockers: Tenseigan's FreeWebNovel labels are non-linear and differ from WebNovel's 967-chapter snapshot; Chronicles of a Fire Ninja shows a displayed/internal chapter split and advertises Patreon-only advance chapters; Starting With Creating A Genius Persona has 527 FreeWebNovel versus 487 CHERREADS chapters.
- The three blocked works remain held. Wind Calamity's author has publicly objected to unauthorised translations and its TOC remains non-linear; Konoha Medical's credited editor says they are not the original writer and artifact #14462633408 remains public/unregistered/rights-unverified; Arcane Thief remains a distinct 254-chapter FreeWebNovel edition with incomplete full-TOC validation and no archive permission.
- No screenshots, chapter prose or archive bytes were fetched. Keep the 65 unmatched Yup/IDK rows deferred.


### Blocked Yup/IDK title classification corrections (22 November 2026)

The 26 exact source-audit listings are 18 Yup and 8 IDK. Do not classify every prior blocked match as a chapter-number mismatch:

- Issue #371 has nine confirmed identity mismatches: Awakening, Condemning the Heavens, Flower Master In The City, Heavenly Star, Ex Rank Supporting Role’s Replay in a Prestigious School, Game Market 1983, Parasite in Love, Sense and The S-Classes That I Raised.
- Omega Summoner's cited run #44447221591 completed its chapter batches for 1–3,083, but recovery manifest #14496292098 saved **0 final ZIPs**. The often-repeated 2,069/2,070 mismatch is not in that run's logs; no mismatch claim until the original run is located.
- Beauty And The Bodyguard timed out during chapter-list discovery; no index was obtained. Legend of Swordsman failed on an empty Chapter 5742 body; only a partial artifact exists.
- Of the nine other audit matches with 20-Nov issues, Past Life Returner and This MC Is Kickass have deterministic identity mismatches; Martial Arts System and Weapon Master have incomplete/misnumbered indexes; Path to Heaven has a duplicate Chapter 152; The Alchemist God and The Mightiest Leveling System have invalid ReadNovelFull URLs. PR #453 (prologue support) did not resolve The Alchemist God. PR #465 adds diagnostics for rejected ReadNovelFull hrefs and duplicate URLs only. PR #466 adds FreeWebNovel offset diagnostics only.
- Tomb Raider King and World Domination System had no child jobs in dispatch #44769541580, so no chapter failure can be claimed for them.

No affected title was retried. Capture exact public TOC href/index evidence on the merged diagnostic code, add offline regression fixtures, and fix the root cause before any targeted retry. See the corrected [source-audit report](campaigns/overnight/source-audit-report-20261121.md) and [issue #371](https://github.com/RichardDaffern/Novel-Retriever/issues/371).


## Fanfiction source and rights research round 18 (22 November 2026, 16:50 IST)

See `campaigns/fanfiction/source-verification-round-18-20261122.md`. The additional author/translator and rights pass found **0 new exact supported-host listings, 0 explicit archiving permissions, 0 rights-cleared titles and 0 download runs**. It reconfirmed the three blocked works: Wind Calamity needs author permission plus a complete one-to-one TOC map; Konoha Medical's credited editor is not the original writer and its public artifact remains rights-unverified; Arcane Thief still needs complete paginated TOC validation and archive permission. The exact title/credited-author and supported-source search for the 32 unresolved fanfiction entries is complete for the current search scope, but all 32 remain unresolved. Do not download or publish any of them without the required rights and edition checks. The next research priority is the 65 unmatched Yup/IDK titles (36 Yup, 29 IDK), after reconciling the 343 completed registry, 70 separately user-confirmed private-HF imports, 90 exclusions and aliases. The 65 are unresolved by four URL patterns, not unavailable worldwide. Keep the 10-title batch / two-active-workflow limits and do not retry known failures unchanged.


## IDK alternative-source research round 1 (22 November 2026, 17:53 IST)

See [the 29-row evidence matrix](campaigns/overnight/idk-alternative-source-research-20261122.md). All 29 IDK audit rows are in the 82-entry manifest; Xian Ni is already complete as Renegade Immortal. One exact NovelFull/FreeWebNovel lead (*Attack Of The Adorable Kid*, Sweets Flood, 2,612 page-reported chapters) and eight WuxiaClick metadata leads were found. Chapter counts/editions vary across several other catalogues. **0 explicit archive permissions, 0 rights-cleared titles and 0 new download runs.** No chapter prose or archive bytes were fetched. The 65-row source review is complete for the current search scope, not a claim of worldwide unavailability. Do not dispatch without explicit rights and a fully validated index.


## Yup/IDK alias and alternative-source follow-up (22 November 2026)

The fanfiction-first research stage is complete for the current scope (8 registered complete, 3 blocked, 32 source/rights investigations without a verified clearance). The next priority is the 65 unmatched Yup/IDK audit rows, not a repeat of the fanfiction searches.

Reconcile those 65 rows against `downloaded_novels.json` and `campaigns/overnight/excluded-90.json` before any source dispatch. The corrected comparison confirms 12 title aliases already in the 343-record registry and one alias of the 90 red/Dropped exclusions, leaving 52 distinct non-alias rows. The exact mapping, author evidence and existing run IDs are preserved in `campaigns/overnight/alternative-source-research-round-2-20261122.md`.

**Do not re-download aliases** (Invincible Conqueror, Xian Ni, Records of the Human Emperor, The School Prince is a Girl, Arifureta Shokugyou de Sekai Saikyou, Crazy Levelling System, Dungeon Defence, Evil Dragon Against The Heaven, Invincible Dragon Emperor, Levelling Up And Becoming Undefeated, Soul Land, My Fury Will Burn The Heavens). Keep Yong Heng Zhi Zun excluded as Eternal Reverence. Do not conflate Invincible Levelling King with Invincible, Hidden Marriage Sweet Pampering with the separate Hidden Marriage registry entry, I Can Extract Everything with Witcher: I Can Extract Everything, or Very Pure and Ambiguous with its prequel.

The alternative-source pass found public metadata and commercial editions, not archive permission. A complete public TOC, a free reading page, a completed translation or a third-party mirror is not a licence to archive or redistribute. No chapter text was fetched, no new archive was created and no download run was dispatched. Continue only with exact author/edition, English-language, complete-index and explicit rights verification; preserve the maximum of 10 titles per bulk batch and two concurrent workflows.

## Live acquisition handover (22 November 2026, 21:03 IST)

- PR #482 merged as `fc1de1a7c69edd4548616c38a58940a4e7bf665e`; post-merge main CI #45039002062 passed all four jobs.
- The 26 exact source-audit matches remain triaged. The 43-title fanfiction catalogue remains 8 complete, 3 blocked and 32 source-researched but unresolved after round 18; do not call source research a download or permission. Keep Wind Calamity, Konoha Medical and Arcane Thief held.
- The next active stage is the 65 unmatched Yup/IDK audit rows after alias/exclusion reconciliation: 12 completed-registry aliases + 1 excluded alias leave 52 distinct non-alias titles. Continue Yup-side alternative-source research before IDK. Round 5 added two FreeWebNovel page leads (*Gourmet of Another World*, *Joy of Life*) but neither has archive permission; see `campaigns/overnight/alternative-source-research-round-5-20261122.md`.
- Counts remain 343 completed registry records, 70 separately user-confirmed private-HF imports and 90 red/Dropped exclusions. Keep these measures separate.
- **No new download run; no active bulk workflow.** Do not rerun source-audit one-shot activation or unchanged #371/#452 failures. Public source pages, complete TOCs, commercial licences, translator credits and platform access do not grant this project archive/public-distribution rights. Require explicit title-specific rights and a complete, ordered English edition index before dispatch.
- Bulk limits remain max 10 titles per batch and max 2 active bulk workflows. Do not re-download completed titles or publish unlicensed text in public Actions artifacts. Existing public artifact revocation inventory remains unresolved; connected GitHub operations used here do not expose artifact deletion.


## Yup/IDK alternative-source round 6 and blocked-source recheck (22 November 2026, 21:35 IST)

See `campaigns/overnight/alternative-source-research-round-6-20261122.md`. The 26 exact matches remain triaged (18 Yup, 8 IDK). The 65 unmatched rows remain 36 Yup and 29 IDK; alias reconciliation leaves 52 distinct non-alias titles after 12 completed-registry aliases and one excluded alias. The 32 unresolved fanfiction targets have been searched through round 18; the three blocked works remain held.

Round 6 rechecked six Yup-side candidates. It found no new exact supported-host listing and no archive permission. Apotheosis is an already-counted ReadNovelFull match: author 恩赐解脱, page claims 3,913 chapters, but its chapter-list count and independent index evidence do not reconcile. Run #44791453169 job 136480003715 failed before chapter downloads with a missing/misnumbered archive. Do not retry or weaken the index check. About the Reckless Girl is a Japanese work with a ten-entry third-party listing; Genjitsu Shugi Yuusha has a separate J-Novel Club-licensed light-novel edition; Mad God has conflicting third-party chapter/translation metadata; Rise Of The Demon King surfaced as manga, not a verified novel; Skirt Chasing Monarch has an incomplete English index against a 1,374-chapter original.

The blocked fanfiction recheck confirms: Konoha Medical's credited WebNovel editor says they are not the original writer; Arcane Thief's 254 numbered chapters plus auxiliary entry are visible only through a paginated TOC whose last page returned HTTP 403; Wind Calamity's author-note page returned HTTP 403 and no permission response is recorded. Do not bypass access controls or retry any of these works.

Counts remain 343 completed registry, 70 separately user-confirmed private-HF imports and 90 exclusions. No new download runs; no active bulk workflows at 21:35 IST. Preserve Yup-before-IDK order, 10-title batch limit, two-workflow concurrency limit, and explicit rights plus complete-index gate. Do not publicly distribute unlicensed archives.


Round-6 addendum: *I Told You I'm Not 〇〇!!* now has an exact non-supported WuxiaClick/WuxiaWorldEU listing under NaHCO3 (96 entries, latest labelled Chapter 97); Novel Updates records 99 Japanese web-novel chapters on hiatus and no English publisher. This is not a supported complete English edition or archive permission. See the round-6 report. No download.


## Yup/IDK alternative-source research round 7 (22 November 2026, 23:06 IST)

See [round-7 report](campaigns/overnight/alternative-source-research-round-7-20261122.md). Seven unresolved Yup audit rows were checked using public identity, edition and chapter-index metadata only. Four rows resolve to existing registry title/edition records: Crazy Levelling System → Crazy Leveling System (1,456 chapters, run #44780760719, artifact #14656332390); Dungeon Defence → Dungeon Defense (46 registered chapters vs 507-chapter web-novel evidence, so edition mismatch remains); Invincible Dragon Emperor → The Invincible Dragon Emperor (1,295 chapters, run #44791453169, artifact #14661016528); and My Fury Will Burn The Heavens → Fury Towards The Burning Heaven (1,726 registered chapters, run #44781304939, artifact #14657291223). Do not re-download these. Levelling Up And Becoming Undefeated still has no reliable exact identity/source; Omni-Magician has conflicting/incomplete unsupported indexes; Soul Land's 690 WebNovel entries split the 336-chapter original into sub-parts and must not be confused with the separately licensed manhua. **Round-7 outcome: 7 Yup rows checked, 0 net-new supported-host candidates, 0 explicit archive permissions, 0 rights-cleared titles, 0 download runs.** No chapter text or archive bytes fetched. Continue Yup first, then IDK; keep the 32 fanfiction research targets marked researched but rights-unresolved and the three blocked fanfiction works held.

## IDK alternative-source research round 8 (22 November 2026, 23:06 IST)

See [round-8 report](campaigns/overnight/idk-alternative-source-research-round-8-20261122.md). Seven IDK audit rows were checked. One new exact supported-host listing surfaced: *Warrior's Promise* on FreeWebNovel, author Baili Longxia, page-reported 3,336 chapters, ongoing. The fetched page exposed only the first 40 chapter links; the complete ordered index was not validated. FreeWebNovel's terms limit its user-content licence to use through its services, and WebNovel's terms limit user access/use to its service and prohibit reproduction/distribution. No archive permission; do not add a campaign URL or dispatch. Other checks found unsupported/incomplete metadata for *Legend of Mythological Genes* (520), *Super Doctor* (1,126 third-party vs 1,215 original), *The Nine Godheads* (12 Chinese chapters, hiatus), *The Entertainment Circle is Mine* (101 WuxiaClick vs 169+3 original), *The Reincarnated Cop Who Strikes With Wealth* (novel/manhwa edition mismatch) and *Those Years When I Opened a Chinese Medicine Shop* (28 catalogue chapters, author/source unresolved). **Round-8 outcome: 7 IDK rows checked, 1 exact supported-host listing, 0 complete indexes independently validated, 0 explicit archive permissions, 0 rights-cleared titles and 0 download runs.** Yup-side research has covered all 36 Yup audit rows; continue the remaining IDK review. The 32 fanfiction research targets remain rights-unresolved and the three blocked works remain held. No chapter prose or archive bytes fetched.

## Bulk dispatch safety limits (23 November 2026)

The existing `library-bulk-download.yml` workflow must be used only through the paced, reviewed dispatch path:

- Maximum **10 new novel titles per workflow run**, including retries. Already-available titles skipped by the registry do not count.
- Maximum **2 active `library-bulk-download.yml` runs** at once.
- `force=false`; never re-download a complete title.
- The queue dispatcher requires per-title `rights_verified=true`, `public_distribution_rights=true`, a non-empty rights holder and an HTTPS `rights_evidence_url`; it passes `confirm_rights=true` to the workflow only after those fields are present. A public listing is not rights evidence.
- The mixed-source planner and recovery planner both enforce the 10-title cap.
- Do not run source discovery as a download, do not use the old 4-run/2-title dispatcher behaviour, and do not dispatch from the read-only source-audit report because it contains no rights evidence.
- The cap is a campaign policy below GitHub's platform matrix ceiling. Keep batches resumable and independently verified.


The `library-bulk-download.yml` prepare job also checks other active runs through the GitHub Actions API and fails closed when two other bulk runs are already active. The paced dispatcher checks the same workflow before each submission. The workflow planner independently caps each run and retry at ten new titles.

## Yup alternative-source research round 9 (23 November 2026, 00:45 IST)

See [round-9 report](campaigns/overnight/yup-alternative-source-research-round-9-20261123.md). Seven Yup rows were checked: five distinct identities and two completed-registry aliases. `Hidden Marriage Sweet Pampering` is a distinct Helan Yang Yang/WebNovel-licensed work (2,844 original chapters, incomplete English translation), not the registry's Jiong Jiong You Yao `Hidden Marriage`. `I Can Extract Everything` by Water (291 chapters, marked Dropped in COO) is not the registry's `Witcher: I Can Extract Everything` by Lich King Number 13 (393 chapters); the FreeWebNovel page is for the Witcher work. `Invincible Levelling King` is only a three-chapter MTL upload with no verified original author. `In Another World With My Smartphone` is Patora Fuyuhara's completed 636-chapter Japanese WN with a separate J-Novel Club-licensed LN. `The Kind Death God` by Tang Jia San Shao is marked unlicensed/incompletely translated, with 208 vs 226 original-index metadata. `The School Prince is a Girl` and `Records of the Human Emperor` reconfirm as aliases of registered `National School Prince Is A Girl` and `The Human Emperor`.

**Round outcome:** 7 rows checked, 2 aliases reconfirmed, 0 new aliases, 0 new exact supported-host pages, 0 explicit archive permissions, 0 rights-cleared titles and 0 downloads. The 51 distinct non-alias rows (23 Yup, 28 IDK) remain. Preserve 343 completed registry records, 70 separately user-confirmed private-HF imports and 90 exclusions. Fanfiction remains 8 complete, 3 blocked and 32 researched but rights-unresolved.

Artifact review also found public rights-unverified archives: National School Prince run #44444477580 / artifact #14493119599 (expires 17 February 2027 02:27:42 UTC) and Witcher: I Can Extract Everything run #43734417289 / artifact #14225912094 (expires 23 November 2026 12:28:08 UTC). The Human Emperor artifact #13644389821 expired 16 November. Repository-owner revocation is required if rights cannot be established; no artifact-delete operation is exposed by the connected GitHub tools.


## Yup alternative-source research round 10 (23 November 2026, 00:45 IST)

See [round-10 report](campaigns/overnight/yup-alternative-source-research-round-10-20261123.md). Seven Yup rows were rechecked. `Apotheosis` is the 3,913-chapter Chinese web novel (Gift Of Liberation), unlicensed and incompletely translated; ReadNovelFull exposes 3,910 entries, so the three-entry TOC mismatch remains held. Its 1,301-chapter manhua is a separate edition. `Bringing the Nation's Husband Home` has a 969-chapter WebNovel edition versus a 973-entry FanMTL mirror and separately sold Apple Books anthologies. `Eternal Martial Sovereign` has 2,240 completed original chapters and a Gravity Tales licence, but translation-completeness metadata conflicts and no project archive permission exists. `Genjitsu Shugi Yuusha` has distinct WN/LN editions; the 21-volume LN is licensed to J-Novel Club/Seven Seas. `I'm in Hollywood` has a stale 335-chapter FreeWebNovel page versus 345 in an earlier mirror and 1,197 in MTL metadata. `Kujibiki Tokushou` has 398 deleted WN chapters plus six LN-only final chapters, while the English mirror has 320. `Mad God` has 176 completed original chapters, licence No and translation incomplete.

**Round outcome:** 7 Yup rows checked, 2 supported-host pages revalidated but held for TOC/completeness or rights, 0 new aliases, 0 explicit archive permissions, 0 rights-cleared titles and 0 downloads. The distinct alternative-source backlog remains 51 titles (23 Yup, 28 IDK). Do not retry the Apotheosis mismatch unchanged.


## Yup alternative-source research round 11 and phase transition (23 November 2026, 00:45 IST)

See [round-11 report](campaigns/overnight/yup-alternative-source-research-round-11-20261123.md). The final four distinct Yup rows were checked: `I Told You I'm Not 〇〇!!` has no re-verifiable 96-entry supported-host page (Novel Updates currently shows zero translated chapters); `Lonely Loser` is a Japanese WN with 58/63 chapter metadata and a separate 60-entry LN mirror (the earlier 326/320 count was a title/edition cross-match); `Omni-Magician` is 758 original chapters with 775 split translation entries but only 192 WuxiaWorldEU entries; and `Skirt-Chasing Young Monarch: City Lady-Killer` is 1,374 original chapters with 220-entry WuxiaWorldEU/ReadNovelEU mirrors and conflicting completeness metadata.

**Phase transition:** all **23 distinct Yup** rows have now received deeper alternative-source/identity research (rounds 8–11). There are **28 distinct IDK** rows remaining. Proceed to IDK next; do not repeat Yup searches unless new evidence appears. No new aliases, exact supported-host pages, archive permissions, rights clearances or download runs resulted. The 65 rows remain 51 distinct (23 Yup, 28 IDK) after 13 registry aliases and one exclusion alias. The fanfiction pass remains 8 complete, 3 blocked and 32 researched but rights-unresolved.


## IDK alternative-source research round 12 (23 November 2026, 00:45 IST)

See [IDK round-12 report](campaigns/overnight/idk-alternative-source-research-round-12-20261123.md). Seven distinct IDK rows were checked. `Attack of the Adorable Kid` has a NovelFull page with 2,612 entries matching its licensed WebNovel edition; its original metadata records 1,782 chapters. `Beautiful Time With You` has 1,129 completed WebNovel/FreeWebNovel entries, while Qidian metadata notes 1,135 original chapters. `Juvenile Medical God` has 4,144 completed original chapters but licence No and incomplete translation. `Warrior's Promise` is an ongoing 3,336-chapter WebNovel edition with mirror counts from 1,691 to 3,336. `Tensei Shitara Slime Datta Ken` has a 256-chapter WN plus 47 side stories and a separate Yen Press-licensed LN. `The Gloomy Me in Class` has 111 ongoing WN chapters versus 75–85 mirror entries. `Konjiki no Wordmaster` has separate WN/LN/manga editions; WN translation tracking stops at c319 while the source index lists chapters through at least 664.

**Round outcome:** 7 IDK rows checked; 0 registry aliases; 0 excluded rows; 1 new exact NovelFull listing and 1 FreeWebNovel listing reconfirmed, both held for rights; 0 explicit archive permissions, 0 rights-cleared titles and 0 downloads. The distinct backlog remains 51 titles (23 Yup, 28 IDK); deeper Yup research is complete and 7/28 distinct IDK rows have now been checked.


## IDK alternative-source research round 13 (23 November 2026, 00:45 IST)

See [IDK round-13 report](campaigns/overnight/idk-alternative-source-research-round-13-20261123.md). Seven more distinct IDK rows were checked. `An Eye for News` has 776 original chapters (Licensed=No) versus 751 FanMTL/WuxP/MTLN entries and 36 WuxiaWorldEU entries. `For Some Reason, the School Goddess Likes to Hang Out at My House` has 126 ongoing WN chapters and 147–166 mirror entries with split/short-story differences. `Genius Profiler Hansol Im` has 203 completed Korean WN chapters, translation incomplete. `HacKer` has 1,873 completed original chapters (Licensed=No) versus 1,933 WuxiaBox entries. `How To Melt the Ice Lady` has 90 ongoing WN chapters/two LN volumes and a Tentai Books licence; mirror pages expose 98 split entries. `I Know Everything` has 1,293 original chapters versus 1,302 FanMTL entries. `Invisible Dragon` has 50 completed Korean chapters, with a 17-chapter copied mirror.

**Round outcome:** 7 IDK rows checked, 0 registry aliases, 0 excluded rows, 0 new exact supported-host pages, 0 explicit archive permissions, 0 rights-cleared titles and 0 downloads. IDK deep research is now 14/28; 14 distinct IDK titles remain. The total unmatched backlog remains 51 distinct titles (23 Yup, 28 IDK).

# Novel Retriever

Download and organise web novels you are authorised to archive. The toolkit builds **EPUBs, individual TXT chapters and validated ZIP archives**, with GitHub Actions for downloads and a Windows tool for collecting completed files.


**WebNovel:** Authorised locally saved HTML/TXT chapters can be converted to EPUB and an integrity-checked Storage Controller ZIP with `python -m tools.webnovel_bulk_import --storage-zip --source-url <book-URL> --confirm-rights`. This is **not** a WebNovel website downloader or GitHub Action. [Instructions](docs/research/webnovel-bulk-import.md).

**WebNovel local browser check (Windows):** Run [`WebNovel-Check-Local-Browser.cmd`](WebNovel-Check-Local-Browser.cmd) to test three selected public chapters for *Harry Potter: Platinum Dragon Wizard*. This is a **read-only** Chromium check, not a download: it never saves chapter text or uses your existing Chrome account. Install optional Playwright separately as explained in the [browser trial guide](docs/research/webnovel-access-review-2026-11-17.md).

## Project architecture and agent handover

Novel Retriever is the **acquisition and packaging component**, not the web reader or the private Hugging Face Storage Controller. It produces complete, identity-verified EPUB/TXT/ZIP artefacts and a metadata-only download registry. GitHub Actions artefacts are temporary. Private cloud import and front-end reading state belong to the separate [Taiyou Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller) and [Novel Library](https://github.com/AdityaSreevatsaK/Taiyous-Personal-Library).

**Future AI agents and maintainers, begin here:**

| Resource | Read for |
| --- | --- |
| [Agent technical handbook](AGENTS.md) | Architecture, files, contracts, security and code-review rules |
| [Project history and decisions](docs/project-history-and-decisions.md) | Original requirements, design evolution, failure lessons and roadmap |
| [Operations and recovery runbook](docs/operations-runbook.md) | Checking live runs, larger download batches, selective recovery, safe export and HF handover |
| [Current status (dated snapshot)](docs/current-status.md) | Yup/Idk and fanfiction backlog, active run IDs, known failures, registry and cover recovery |
| [Agent session handover template](docs/agent-handover-template.md) | Reproducible evidence and exact next-step checklist |
| [Changelog](CHANGELOG.md) | Operator-relevant modifications and confirmed milestones |

**Current campaign model (checked 22 November 2026):** the 20 November one-shot Yup/IDK activation is historical and must not be re-run. Read-only audit #44924359606 found **26 public listings from 91 eligible rows** (18 Yup, 8 IDK) and **65 unmatched** (36 Yup, 29 IDK); the five-book TOC preflight fetched no chapter text and cleared no rights. The fanfiction-first research stage is complete for the current scope (8 complete, 3 blocked, 32 unresolved). The 36-row Yup and 29-row IDK alternative-source reviews are now documented; the IDK pass found one exact NovelFull/FreeWebNovel listing for *Attack Of The Adorable Kid* (Sweets Flood, 2,612 page-reported chapters) but no archive permission. There are **0 rights-cleared titles and 0 new download runs**. Review [Current Status](docs/current-status.md), [the Yup report](campaigns/overnight/alternative-source-research-20261122.md), [the IDK report](campaigns/overnight/idk-alternative-source-research-20261122.md), and [issue #456](https://github.com/RichardDaffern/Novel-Retriever/issues/456) before launching any download. Public listing alone is not permission; require a complete TOC and explicit lawful rights, use a non-public output route, `force=false`, no more than 10 titles per batch and no more than two active bulk workflows. Never retry deterministic index failures unchanged.

## Curated bulk downloads (preferred workflow)

**Discover and verify sources before dispatch, not inside GitHub Actions.** A maintainer or AI agent checks outstanding books against the completed registry and the original approved Yup/Idk lists, then confirms the actual **book pages** on supported sources, preferring **NovelFull**, then **ReadNovelFull**, then FreeWebNovel where appropriate. Review aliases, the 90 red/Dropped exclusions, 14 known broken full-book retries, site permissions and the presently active runs. Save an evidence-backed URL list, then send those exact URLs through the existing [Library - Bulk Download](.github/workflows/library-bulk-download.yml), with `force=false`.

The historical automatic search-based large-wave dispatcher is **not the preferred entry point** for new campaigns. Its 20 November discovery selected only four eligible URLs and all four were blocked by deterministic FreeWebNovel chapter-number issues. A reusable manually curated URL launcher is implemented in `tools/dispatch_curated_bulk.py`; see [Operations Runbook](docs/operations-runbook.md) for workflow and one-shot activation details. A verified public book page proves **identity**, not authorisation to copy, chapter completeness or upload readiness.

## Download novels

**[Library - Bulk Download](https://github.com/RichardDaffern/Novel-Retriever/actions/workflows/library-bulk-download.yml)** is the shared downloader for **all supported websites**. Paste one or more novel URLs into **Novel links** and select **Run workflow**. You can mix websites in the same request; the source is detected automatically. One link works too.

### Dedicated website Actions

Prefer a dedicated Action when downloading from one particular website.

| Website | Dedicated Action | Support |
| --- | --- | --- |
| [NovelFull](https://novelfull.com/) | [NovelFull - Download](.github/workflows/download-novel.yml) | Full novels and chapter ranges |
| [FreeWebNovel](https://freewebnovel.com/) | [FreeWebNovel - Download](.github/workflows/freewebnovel-download.yml) | Accessible public chapters |
| [ReadNovelFull](https://readnovelfull.com/) | [ReadNovelFull - Download](.github/workflows/readnovelfull-download.yml) | One live full-book success verified; per-title index and access still vary |
| [WuxiaClick](https://wuxia.click/) | [WuxiaClick - Download](.github/workflows/wuxiaclick-download.yml) | Authorised ranges of up to **20 chapters**; full-book export disabled |
| [Scribble Hub](https://www.scribblehub.com/) | [Scribble Hub - Download](.github/workflows/scribblehub-download.yml) | Only the verified author cross-post, series `445037` |

**Note:** WuxiaClick and Scribble Hub require explicit rights confirmation. Respect WuxiaClick’s daily offline-download allowance, including across separate runs. [Website restrictions and supported URL formats](docs/website-support.md).

## Collect completed novels on Windows

Install [GitHub CLI](https://cli.github.com/) and run **[Download-All-Novels.cmd](Download-All-Novels.cmd)**. It saves one verified ZIP per novel in `Downloaded_Novels/` and skips valid files already present.

## FreeWebNovel source metadata

Both **FreeWebNovel - Download** and **Library - Bulk Download** now read
a novel's synopsis, genre tags and publication status from its own public
book page. Where present, these fields are embedded in `source.epub`
and written to `metadata.json`; absent source fields remain absent.
Older cached chapter batches lacking metadata extraction support are not
reused in new runs. This does not modify previously uploaded Hugging Face
books or their personal metadata.

## Covers and safe duplicate ZIP handling

Every completed download now attempts to include a genuine cover and records its provenance. For older individual ZIPs and a consolidated export, use the [offline deduplication and cover guide](docs/cover-and-deduplication.md). Conflicting editions are retained for review, not silently replaced.

The [Taiyou Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller) now supports an **opt-in, duplicate-aware Smart Bulk Upload** (Windows menu option 12, or `--dedupe-local`). A conflict blocks all uploads. Keep originals and preview changes before applying. See the [safe upload and deduplication guide](docs/cover-and-deduplication.md). The repository is now [Novel-Retriever](https://github.com/RichardDaffern/Novel-Retriever); existing clones can update their remote with `git remote set-url origin https://github.com/RichardDaffern/Novel-Retriever.git`.

## Run locally

Requires Python 3.12. From the repository root:

```powershell
python -m pip install -r requirements.lock
python -m unittest discover -s tests -v
python novel_downloader.py --self-test --chapter-range 1-2
```

The self-test uses invented chapters and makes no novel-site requests.

## Verify a consolidated export without uploading

Run [Export Completed Novels](.github/workflows/export-completed-novels-20261116.yml)
manually in GitHub Actions. Download the resulting consolidated artefact,
extract it locally, and inspect `manifest.json`, `SHA256SUMS.txt`, the
`novels/` folder and any `review-conflicts/` entries. Verify the checksums
before handing the **individual** ZIPs to the Storage Controller.

Use Storage Controller Windows menu option 12 to preview duplicate/conflict
handling. Resolve every conflict before approving a separate upload. This
preview must not modify the private Hugging Face dataset. A successful CI run
does not prove that live website covers or historical artefacts are available.

## Security and dependency maintenance

Use Python 3.12 and the committed `requirements.lock` for downloads, or
`requirements-pdf.lock` for PDF conversion. CI checks the locked packages
with `pip-audit` and scans high-severity Python patterns with `bandit`;
Dependabot proposes weekly Python and GitHub Actions updates. Review proposed
updates and regenerate the affected lock file with `pip-compile` before
merging. Keep tokens in GitHub Actions secrets or local environment variables,
not in repository files or command-line arguments.

## Other tools and guides

- [PDF to novel ZIP](docs/pdf-to-novel.md) via [Convert-PDFs.cmd](PDF-to-Novel/Convert-PDFs.cmd)
- [Import an authorised local EPUB](docs/website-support.md) and [manage covers/metadata](docs/metadata-guide.md)
- [Download guide, chapter batching and troubleshooting](docs/download-guide.md)
- [Source research and unsupported sites](docs/research/source-feasibility-2026-11-15.md)
- [Yup/IDK alias reconciliation and alternative-source round 2](campaigns/overnight/alternative-source-research-round-2-20261122.md)
- [Technical handbook for contributors and AI agents](AGENTS.md)
- [Project history, architectural decisions and roadmap](docs/project-history-and-decisions.md)

Only archive material you have permission to store **and share through GitHub Actions artefacts**. The toolkit does not bypass website access restrictions. Never commit novel text, EPUBs or secrets.

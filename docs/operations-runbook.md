# Novel Retriever: Operations and Recovery Runbook

> **Repository cleanup (26 November 2026):** All one-shot campaign manifests, campaign-only scripts/tests and temporary workflow definitions have been retired. Historical records are available at [the pre-cleanup commit](https://github.com/RichardDaffern/Novel-Retriever/blob/6674b26c9959d7b2f506cc32dc115975ab30c275/campaigns). The active exclusion and known-failure lists are now `config/excluded-novels.json` and `config/known-blocked-retries.json`. Use the existing reusable workflows; do not reactivate historical campaigns. Prior authorisation, source validation, completeness and public-output safeguards remain in force. Historical instructions below that refer to retired paths are not executable instructions.


**Audience:** AI coding agents, technical maintainers and authorised operators.
**Maintained:** 21 November 2026. Read [current status](current-status.md) for a dated snapshot; refresh live GitHub and local-worktree state before every substantial operation.

This is the **operational companion** to [AGENTS.md](../AGENTS.md), not a replacement. Source code and current tests govern actual behaviour. Never treat this document as proof that a queued download, external source or private dataset import succeeded.

## 1. System ownership and boundaries

- **Source repository:** `RichardDaffern/Novel-Retriever`, canonical branch `main`.
- **Responsibility:** Source checks, authorised acquisition, bounded chapter jobs, EPUB/TXT assembly, manifests, metadata/covers, complete-book validation, temporary GitHub Actions artefacts, metadata-only registry, and Windows/download exports.
- **Storage importer:** [Taiyou Novels Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller). Owns reviewed writes to private Hugging Face data. It is not automatically invoked by a successful Retriever workflow.
- **Reader:** [Taiyou's Personal Library](https://github.com/AdityaSreevatsaK/Taiyous-Personal-Library). Owns UI and personal reading state. Do not change its progress, ratings, collections or notes from this repository.
- **Permissions:** Archive/download only works the operator is authorised to copy and place in the chosen GitHub Actions visibility context. Publicly readable pages do not confer copying/redistribution rights. Never bypass accounts, paywalls, CAPTCHA, access restrictions, request quotas or anti-bot systems.

## 2. What 'complete' means: separate lifecycle stages

| Stage | Strong evidence | Never infer |
| --- | --- | --- |
| Backlog | Listed in approved Yup/Idk or fanfiction campaign | Source available |
| Source-verified | Exact public book identity, edition/author where necessary, permitted source reviewed | Chapter integrity or copying rights |
| Selected/queued | Present in a dispatcher plan or pending group | GitHub job dispatched |
| Dispatched | A distinct `Library - Bulk Download` workflow run ID exists | Download finished |
| Chapter batches | Each range has validated chapter positions, correct content and checkpoints | A final complete book exists |
| Assembled | Full-book EPUB and individual chapter TXT/JSON pass identity, order, counts and hashes | Registry publication succeeded |
| Registered complete | `downloaded_novels.json` records `status: complete`, `range: all` and a real run/artefact ID | Artefact has not expired, or was imported to HF |
| Exported locally | Outer artefact extracted; individual `novels/*.zip` and manifest/checksums verified | Cover thumbnails exist in private HF |
| Imported | Storage Controller confirms reviewed private-dataset commit and post-import verification | Reader/browser cache refreshed |

A workflow's green conclusion may merely mean the **dispatcher succeeded**. Confirm its child download runs and the final registry entries separately. The registry is metadata-only; GitHub artefacts are temporary and may expire.

## 3. First five minutes of any new session

1. Read [AGENTS.md](../AGENTS.md), especially its **Mandatory dynamic project-state inspection**, then this runbook, [current status](current-status.md), [project history](project-history-and-decisions.md) and the focused component guide.
2. If a local clone exists, inspect it before editing:
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
   Inspect every dirty/untracked change. Never reset, clean, stash, overwrite or switch away from work you did not create. If there is no local clone, explicitly say that local working-tree status cannot be inspected.
3. Verify current `main` SHA, recent commits and changed paths, open PRs/reviews/checks, open issues/comments, and queued/in-progress Actions. For relevant recent runs inspect job and step conclusions, logs, artefacts and expiry. A run name or green dispatcher alone is not sufficient.
4. Re-read the canonical data: `downloaded_novels.json`, `config/excluded-novels.json`, Yup and IDK input manifests, the fanfiction catalogue, the historical blocked-title list and any current source-audit/preflight evidence. Compare by canonical URL and verified author/edition, not fuzzy title alone.
5. Classify the affected capability as implemented/active, live-verification-incomplete, partial/experimental, planned, deprecated/retired/one-shot, or historical. Record evidence and checked-at date. Treat old assistant summaries and status snapshots as leads only.
6. Determine whether the request is investigation, code change, source audit, download dispatch, retry, export or private dataset write. Keep them distinct. The user's current acquisition order is **Harry Potter/Naruto fanfiction first**, then the **65 unresolved Yup/IDK titles** from the 21 November audit.
7. Make a fresh plan that excludes completed, active, rejected, unresolved-permission and known deterministic-failure cases. Check one-shot marker files and current workflow concurrency before any launch.

**Read-only GitHub CLI examples** (after `gh auth status`):

```powershell
gh repo view RichardDaffern/Novel-Retriever
git status --short --branch
git log -15 --oneline --decorate
gh run list --repo RichardDaffern/Novel-Retriever --limit 30
gh run list --repo RichardDaffern/Novel-Retriever --status in_progress
gh run list --repo RichardDaffern/Novel-Retriever --status queued
gh run view RUN_ID --repo RichardDaffern/Novel-Retriever --json status,conclusion,jobs
# Artefact availability is a separate API query:
gh api repos/RichardDaffern/Novel-Retriever/actions/runs/RUN_ID/artifacts
gh pr list --repo RichardDaffern/Novel-Retriever --state open
gh issue list --repo RichardDaffern/Novel-Retriever --state open
```

The examples above are observations only. Do not run a download workflow, rerun jobs or write to Hugging Face merely to collect status. If no local clone exists, omit Git commands rather than implying a clean worktree.

## 4. Workflow selection

| Intent | Entry point | Key constraint |
| --- | --- | --- |
| One or several known, approved sources | `.github/workflows/library-bulk-download.yml` | `novel_urls` or known names; default `force=false`; avoid already active URLs |
| One NovelFull book | `.github/workflows/download-novel.yml` | Strict chapter index, bounded ranges, complete assembly |
| One FreeWebNovel book | `.github/workflows/freewebnovel-download.yml` | Source identity, chapter numbering, bounded retries only for transient errors |
| One ReadNovelFull book | `.github/workflows/readnovelfull-download.yml` | AJAX TOC validation, exact chapter URLs and bounded batches |
| One WuxiaClick book | `.github/workflows/wuxiaclick-download.yml` | Explicit rights gate and maximum 20 chapters per run; no whole-book quota bypass |
| One allowlisted Scribble Hub cross-post | `.github/workflows/scribblehub-download.yml` | Explicit rights gate and one verified same-author cross-post only |
| Failure recovery | `Library - Bulk Download` with `retry_run_id`, where a valid recovery manifest exists | Retry only failed or missing books, not completed ones |
| Export completed archives | `.github/workflows/export-completed-novels-20261116.yml` or `tools/download_all_artifacts.ps1` | Export only verified completed books; check expiry and contents |
| Cover-only recovery | `tools/download_covers.py`, `tools/cover_pipeline.py`, `tools/recover_covers_from_export.py` | No chapter re-download or HF write |
| Authorised local WebNovel content | `tools/webnovel_bulk_import.py` | Saved local chapters and explicit rights; not hosted scraping |
| Selectable-text PDF | `tools/pdf_to_novel.py` / PDF conversion scripts | Offline, original content intact, boundary review |

**Do not add a competing second bulk-download UI.** Existing mixed-site workflow groups by supported source. Keep the original workflows and their caller contracts intact.

## 5. Source discovery, curated campaigns and one-shot workflows

### Historical campaign mechanics

- The 19 November Yup/IDK dispatcher and 20 November large-wave campaign are **one-shot historical activations**. The 20 November wave was configured for up to 40 eligible titles, ten-title child runs, Yup-first ordering and at most two active bulk workflows. Its marker was consumed; do not rerun it or infer that 40 books were selected or downloaded.
- The old `tools/overnight_queue.py` discovery path is read-only when invoked with `discover`; its separate `dispatch` command can submit downloads. Never call dispatch just to inspect sources. Current discovery checks NovelFull, ReadNovelFull (standard and `-v1` URL patterns) and FreeWebNovel, rejects redirects and unrelated title pages, and does not fetch chapter prose.
- `config/known-blocked-retries.json` is a historical 14-title safety manifest. Reconcile each row against later fixes, PRs, run logs and final artefacts before classifying it as still blocked. It is not a blanket instruction to redownload those titles.
- `tools/dispatch_curated_bulk.py` validates a reviewed manifest of literal source URLs; it does **not** search websites or guess slugs. Its current code has a 24-book campaign ceiling and a two-active-bulk-run cap. The user has previously requested batches of up to ten; honour that smaller operational target unless the user changes it. Inspect the current code and workflow before using it.

### 21 November three-source source audit

The one-time [source-audit workflow](https://github.com/RichardDaffern/Novel-Retriever/actions/workflows/source-audit-20261121.yml) was activated by adding `campaigns/overnight/source-audit-20261121.json` and completed as [run #44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606).

- It considered 91 eligible campaign entries (54 Yup, 37 IDK), after checking the 90 global exclusions and existing known records.
- It made 336 public book-page requests across NovelFull, ReadNovelFull and FreeWebNovel. It found 26 exact listings (18 Yup, 8 IDK); 65 had no exact match at the tested URL patterns (36 Yup, 29 IDK). No source host was blocked.
- This was a **listing-only audit**. It did not fetch chapter text, prove author/edition identity for every match, establish copying rights or launch a download.
- The full matched URL table and exact 65-title unresolved list are preserved in [source-audit-2026-11-21.md](https://github.com/RichardDaffern/Novel-Retriever/blob/6674b26c9959d7b2f506cc32dc115975ab30c275/campaigns/overnight/source-audit-report-20261121.md). The GitHub Actions artefact is temporary; the committed report is the durable record.

### Five-book table-of-contents preflight

The one-time [five-book TOC workflow](https://github.com/RichardDaffern/Novel-Retriever/actions/workflows/five-book-toc-preflight-20261121.yml) completed as [run #44926984233](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984233). It fetched only book metadata and the public chapter index: zero chapter bodies and `rights_verified=false`.

- Index passed: *Doom Lord* (155 chapters) and *Girl, I'll Teach You Cultivation* (283 chapters).
- Index failed: *Beast Piercing The Heavens* (duplicate Chapter 11 links), *Godly Student* (invalid chapter URL), and *The Military Female Soldier With Unwavering Stubbornness* (2,104 missing numbered chapters).
- A passed index is not an archive-rights decision or a completed book. A failed index must be fixed at source/adapter level before retry.

### Current acquisition priority and launch gate

1. Research and recover the **43 Harry Potter/Naruto fanfiction requests first** (24 Naruto, 19 Harry Potter). The catalogue contains eight registry-complete works, three source-matched incomplete works and 32 requiring source verification. Verify exact title, author and edition; screenshot-truncated names are unresolved identities, not slug-generation prompts.
2. Then research the **65 unresolved Yup/IDK titles** from the audit. First reconcile alternate titles and completed editions against the current registry. The 65 are unresolved by one bounded search, not proven unavailable online.
3. Reassess the 26 matched pages individually. Most overlap known failure cases; only five were fresh at the time of review, and only two of those passed the TOC preflight.
4. Before a new download, verify the exact source and edition, consecutive complete chapter index, the operator's right to archive/store the work, the target artefact visibility, global exclusions, completed registry, open metadata PRs, known failures and active/queued runs.
5. Dispatch only approved literal URLs through the existing **Library - Bulk Download** workflow with `force=false`. Keep groups to at most ten titles and no more than two active bulk runs where applicable. Verify every child run, assembled EPUB/ZIP, registry record and artefact expiry separately.

The 21 November source-audit and TOC-preflight marker files have already been added and consumed. Do not re-add them or rerun their one-shot jobs. The user's latest priority and the dated counts are also recorded in [current status](current-status.md).

**Launch review checklist:** exact work/author/edition; source-page evidence; TOC and chapter positions; archive permission; not red/Dropped; not complete or active; not a deterministic known failure; current capacity; reviewed manifest diff; CI; new child run IDs; final artefact and registry verification.

## 6. Safe recovery matrix

| Failure or warning | Action | Forbidden shortcut |
| --- | --- | --- |
| `RemoteDisconnected`, temporary connection reset, transient 5xx | Inspect failing job and checkpoint. Use bounded, same-URL retries supported by the source workflow, or a recovery manifest. | Whole-book forced download when only a range failed |
| 403, 429, CAPTCHA, site challenge or denied permissions | Stop this source, record the response; await authorised route/permissions. | Proxy rotation, browser/account bypass, evasion |
| Expected chapter 125 but page says 124 or 126 | Quarantine. Verify TOC, canonical numbering, actual content and edition against source; open a targeted fix with tests. | Disable the numbering check, skip a page or label complete |
| Empty chapter body or missing chapter | Confirm whether the chapter exists; keep chapter/ZIP incomplete and retry only if a justified transient failure. | Publish an incomplete EPUB |
| Chapter discovery timed out | Investigate index pagination and bounded timeouts; make a narrow fix with a synthetic regression. | Arbitrarily increase all timeouts |
| Completed artefact, missing registry entry or open metadata PR | Inspect the final book artefact and publisher PR; reconcile the metadata-only registry safely. | Redownload all chapters merely to make a record appear |
| GitHub artefact expired | Check existing verified local ZIP or approved storage copies; identify source and only re-acquire if authorised and necessary. | Claim downloadable availability from a historical registry row |
| Two archives same title but different canonical source/chapters | Hold for edition/source conflict review using `tools/novel_dedupe.py`. | Silently overwrite or rename as the same book |
| Missing synopsis/author/genre | Inspect source metadata and EPUB/JSON preservation; report absent fields. | Invent summaries or authors |
| Missing standalone thumbnail in library | Inspect authentic embedded or existing cover and use validated cover-only process; audit catalogue `coverPath`. | Re-upload entire novel or insert generic cover |
| Partial batch failure | Preserve successful independent book ZIPs and use `bulk-recovery-manifest-RUN_ID` for selective retry when produced. | Treat whole batch as failed or rerun already-successful books |

Track prior integrity failures in [issue #371](https://github.com/RichardDaffern/Novel-Retriever/issues/371) and FreeWebNovel numbering problems in [issue #257](https://github.com/RichardDaffern/Novel-Retriever/issues/257). These issues are investigation queues, not invitations to bypass validation.

## 7. Verify and collect complete books

1. Check the child workflow **assemble/finalise**, the complete chapter report and artefact upload steps.
2. Confirm a completed `downloaded_novels.json` record with canonical URL, `range: all`, `status: complete`, GitHub run/artefact IDs and expiry where available.
3. Validate the download's EPUB, chapter manifest and ZIP structure; do not equate an `artifact-id` with a future-proof copy.
4. For bulk failures, inspect `bulk-selection-` and `bulk-recovery-manifest-` artefacts to identify the exact missing books.
5. Use the existing Windows `Download-All-Novels.cmd` or a reviewed consolidated export; keep the outer export and any reports until import is verified.
6. In an extracted consolidated package, **only copy individual `novels/*.zip` into the Storage Controller's `novels/` directory**. Keep `manifest.json`, `SHA256SUMS.txt`, README and `review-conflicts/` as review material outside that input folder.
7. In the Storage Controller, run `01_bulk_upload.cmd`, inspect the **private** destination and non-destructive preview, resolve all conflicts, then approve the separate write. Do not copy the registry JSON or outer export ZIP into `novels/`.
8. Validate standalone covers and catalogue references separately; `10_upload_covers.cmd` is a separate controller path. A verified novel ZIP cover does not automatically imply a library thumbnail.

**Historical handover:** The 104-book consolidated export [#44466510737](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44466510737) and 104 authentic cover recovery [#44521807242](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44521807242) were reported successful. The Controller's [cover-only HF repair #44522722197](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller/actions/runs/44522722197) verified 104/104. They are **historic evidence**, not instructions to reactivate one-shot jobs or re-upload those books.

## 8. Implementation, test and merge discipline

- Preserve the current standard: Python 3.12, committed `requirements.lock`; also test Windows PowerShell 5.1 for scripts and archive packaging.
- Offline tests first: `python -m unittest discover -s tests -v`. For specialised workflows, run the corresponding `tests/test_*.py`; check security and Windows CI. No real chapter text in fixtures.
- Commit only metadata, code, synthetic tests and safe docs. No real EPUBs, fanfiction text, private data, secret tokens, screenshots or HF credentials.
- Keep changed workflow names/inputs, paths, permissions, triggers and the public `downloaded_novels.json` schema backward-compatible.
- Update hardcoded test inventories and fixed-count safety assertions when a **reviewed** campaign adds source candidates, while preserving red/blocked filters.
- Prefer narrow PRs; do not delete branches, rerun a one-shot dispatch or alter live downloads simply to tidy history.
- Confirm actual GitHub conclusion and `main` merge commit before announcing success. A PR passing CI is not proof of site/EPUB or HF success.
- Update [current status](current-status.md), [CHANGELOG](../CHANGELOG.md), and provide a [handover](agent-handover-template.md) when ending substantial work.

## 9. End-of-session evidence required

Use the [handover template](agent-handover-template.md) and include:
- Exact `main` SHA and PR links, plus what remains unmerged.
- All newly dispatched and still-running run IDs with **checked-at timestamp**.
- Counts by stage: source-verified, held, dispatched, completed/registered, failed, exported, HF imported. Never combine.
- Exact unresolved novel titles, source URLs, failure types, recovery manifest IDs and next safe action.
- Privacy/permission caveats, file/data contracts changed, tests run and verified result.
- Whether a one-shot activation was consumed and whether another run would create duplicates.
- A single suggested next action that does not need to reconstruct the previous session.

**Status documents are snapshots, not monitoring services.** Updating this repository does not keep the status live or run anything periodically.

# Novel Retriever: Operations and Recovery Runbook

**Audience:** AI coding agents, technical maintainers and authorised operators.
**Maintained:** 20 November 2026. Read [current status](current-status.md) for a dated snapshot; refresh live GitHub state before every operation.

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

1. Read `AGENTS.md`, `README.md`, this runbook, [dated status](current-status.md) and [handover checklist](agent-handover-template.md).
2. Check `main` SHA, open PRs, [GitHub Actions](https://github.com/RichardDaffern/Novel-Retriever/actions), outstanding issues, pending registration PRs and the metadata registry. Read the latest run's **jobs and steps**, not only the run title.
3. Inspect `campaigns/overnight/excluded-90.json`, `campaigns/overnight/blocked-full-retries-20261120.json`, `campaigns/yup-pilot/backlog-163.json`, `campaigns/overnight/idk-82.json`, `campaigns/fanfiction/webnovel-favourites-43.json` and `campaigns/yup-pilot/verified-urls.json`.
4. Determine whether the request is investigation, code change, download dispatch, retry, export or **private dataset write**. Keep these distinct, and confirm the relevant requested action.
5. Make a fresh plan avoiding overlaps with active child runs, previously complete source URLs, rejected titles, already-submitted groups and known failures.
6. Follow `main` and currently verified workflow definitions, not stale examples or an earlier GitHub Actions run ID.

**Read-only GitHub CLI examples** (after `gh auth status`):

```powershell
gh repo view RichardDaffern/Novel-Retriever
gh run list --repo RichardDaffern/Novel-Retriever --limit 30
gh run view RUN_ID --repo RichardDaffern/Novel-Retriever --json status,conclusion,jobs,artifacts
gh pr list --repo RichardDaffern/Novel-Retriever --state open
gh issue list --repo RichardDaffern/Novel-Retriever --state open
```

The above examples are observation only. Do not run a download workflow, rerun jobs or write to HF merely to collect status.

## 4. Workflow selection

| Intent | Entry point | Key constraint |
| --- | --- | --- |
| One or several known, approved sources | `.github/workflows/library-bulk-download.yml` | `novel_urls` or known names; default `force=false`; avoid already active URLs |
| One NovelFull book | `.github/workflows/download-novel.yml` | Strict chapter index, bounded ranges, complete assembly |
| One FreeWebNovel book | `.github/workflows/freewebnovel-download.yml` | Source identity, chapter numbering, bounded retries only for transient errors |
| Previously reviewed pilot sources | `.github/workflows/yup-pilot-dispatch.yml` | Newly added `batch-XX.json` files; legacy two-title pilot |
| Larger Yup/Idk source-verified campaign | `.github/workflows/large-verified-waves-20261120.yml` | **One-time activation already consumed**; see Section 5 |
| Historical source verification/dispatch | `.github/workflows/overnight-yup-idk*.yml` | One-time activation already consumed; do not rerun blindly |
| Failure recovery | `Library - Bulk Download` with `retry_run_id`, where a valid recovery manifest exists | Retry only failed or missing books, not completed ones |
| Export completed archives | `.github/workflows/export-completed-novels-20261116.yml` or `tools/download_all_artifacts.ps1` | Export only verified completed books; check expiry and contents |
| Cover-only recovery | `tools/download_covers.py`, `tools/cover_pipeline.py`, `tools/recover_covers_from_export.py` | No chapter re-download or HF write |
| Authorised local WebNovel content | `tools/webnovel_bulk_import.py` | Saved local chapters and explicit rights; not hosted scraping |
| Selectable-text PDF | `tools/pdf_to_novel.py` / PDF conversion scripts | Offline, original content intact, boundary review |

**Do not add a competing second bulk-download UI.** Existing mixed-site workflow groups by supported source. Keep the original workflows and their caller contracts intact.

## 5. Large-batch operations, 20 November 2026

Implementation:
- `tools/overnight_queue.py discover` checks **public book listings only**: exact-title match, NovelFull first, then supported FreeWebNovel where permitted. This is not a licence check and does not fetch chapter text.
- `tools/large_batch_dispatch.py` selects **Yup first**, then Idk, and uses the approved discovery result. Current one-time workflow requests **up to 40** eligible titles in **batches of 10**. The utility bounds individual batches at 12 and campaign totals at 48, but these are code safeguards, **not evidence 40 were selected**.
- Dispatcher caps the number of concurrently active `Library - Bulk Download` workflows at **two**, with a 90-second delay between new submissions and 75-second polling when slots are full. Per-site child workers retain their own limits.
- The globally excluded 90 red/Dropped titles and 14 known unrepaired failures must not be selected. The validated registry and approved source identity prevent completed books being forced.
- A discovery result may contain fewer than 40 eligible books, and may stop early due to access restrictions. Submit only verified ones. Unresolved items stay unresolved.
- The activation file `campaigns/overnight/activate-large-waves-20261120.json` is **one-shot**: changing it or pressing 'Re-run jobs' must not dispatch duplicate downloads. Create any genuinely new campaign as a distinct, reviewed request with new source evidence and deduplication.
- Track the live [large-wave run #44764626782](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44764626782) as a **dated example**, not a perpetual active run. Its discovery and dispatch results must be rechecked before reporting completion.

**Launch review checklist:** Verify permission and exact source; verify title is not red, blocked, complete or active; compare the proposed URL/edition and chapter index; check current active jobs; review the request diff and CI; merge only approved code; verify a **new** dispatcher run appears; examine each child run and eventual final ZIP.

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

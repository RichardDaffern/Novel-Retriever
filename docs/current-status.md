# Novel Retriever: Current Operational Status

**Snapshot:** 20 November 2026, approximately 21:15 IST.
**This is a dated handover, not a live dashboard.** Re-check GitHub Actions, `main`, `downloaded_novels.json`, current artefact availability and private dataset before acting. For how to investigate or recover, see [Operations Runbook](operations-runbook.md).

## 1. Verified facts at snapshot time

| Subject | Observed state | Evidence / source of truth |
| --- | --- | --- |
| Canonical repository | `RichardDaffern/Novel-Retriever`, branch `main` | [Repository](https://github.com/RichardDaffern/Novel-Retriever) |
| Historical completed downloads in registry | **329** records with an all-range complete download and artefact ID (not a count of currently retrievable artefacts or HF books) | `downloaded_novels.json` checked 20 November |
| Red-highlighted/Dropped exclusions | **90** absolute exclusions across both worksheets, including cross-sheet conflicts | `campaigns/overnight/excluded-90.json` |
| Filtered original Yup gap | **173** initially missing from private HF in the 18 November audit; this is a **historic baseline**, not today's pending count | `campaigns/yup-pilot/README.md` |
| Yup campaign backlog | **163** records: 6 `wave3_requested`, 4 `wave4_requested`, 153 `needs_source_verification` | `campaigns/yup-pilot/backlog-163.json` |
| Curated, approved Yup pilot source list | **20** source URL entries, including four wave-four titles | `campaigns/yup-pilot/verified-urls.json` |
| Idk campaign | **82** reviewed input records | `campaigns/overnight/idk-82.json` |
| Fanfiction requests | **43** titles: 24 Naruto + 19 Harry Potter | `campaigns/fanfiction/webnovel-favourites-43.json` |
| Fanfiction status from registry comparison | **8 registered complete, 3 matched-source works not registered complete, 32 needing supported-source verification** | Fanfiction campaign file + completed registry, checked 20 November |
| Private HF novel inventory | **Not independently verified in this status check** | Storage Controller/private HF is a separate source of truth |

The previous manual Yup/Idk comparison reported approximately **62 Yup and 36 Idk** outstanding after recognised aliases; **do not treat these as current exact pending counts**. It mixed a historical HF gap with present registry matching and may change as running jobs publish results. Recompute from the original workbook or reviewed campaign lists, canonical URLs, aliases, completed registry and private HF inventory before quoting exact 'still missing from library' figures.

## 2. Live campaigns at the last check

| Campaign | Run | Last observed status | What to verify next |
| --- | --- | --- | --- |
| Larger 40-candidate Yup/Idk wave, up to 10 titles per child run | [#44764626782](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44764626782) | Source-discovery job **successful**; dispatcher **in progress** | Read `large-wave-source-audit-` and `large-wave-dispatch-` artefacts; find actual selected/held count and all child runs |
| Legacy wave-four pilot batch 09: Advent of Archmage, Assassin's Chronicle | [#44762457914](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44762457914) | **In progress** | Check chapter batches, final EPUB and registry |
| Legacy wave-four pilot batch 10: Charm Of Soul Pet, The Immortal's Wine Store | [#44762670118](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44762670118) | **Queued** | Confirm first job starts, chapter index, final result |
| Wave-four pilot dispatcher | [#44762437176](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44762437176) | **Successful dispatch** | Do not confuse dispatch with the two novel-download conclusions |

**Large campaign configuration:** `.github/workflows/large-verified-waves-20261120.yml` requests up to **40 source-verified books**, batches of **10**, maximum **two active bulk runs**, Yup before Idk, and 90-second spacing. The workflow was activated once via `campaigns/overnight/activate-large-waves-20261120.json`. Do **not rerun** the old activation or assume all 40 were discoverable/dispatched/completed.

The 14 unresolved full-book failures in `campaigns/overnight/blocked-full-retries-20261120.json` are intentionally excluded from new full-book dispatches. Keep their partial checkpoints and use targeted recovery after investigating [issue #371](https://github.com/RichardDaffern/Novel-Retriever/issues/371).

**Important:** The large dispatcher was started while two previous pilot bulk workflows were active/queued. Verify the current active-workflow count and avoid duplicate book URLs across all campaigns before any additional launch.

## 3. Fanfiction workstream

**Input:** 43 user-selected fanfictions from 11 screenshots: 24 Naruto, 19 Harry Potter. Source-of-truth campaign catalogue is `campaigns/fanfiction/webnovel-favourites-43.json`. Older fanfiction dispatch: [#44378456717](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44378456717).

- **8 source-matched fanfiction titles recorded complete**, including the previously completed *The Adventurous Gamer Ninja - Daichi Hekima*. Registry completion does not guarantee current artefact availability or private HF import.
- **3 with source matches but no complete registry record:** *Naruto: The Wind Calamity* (chapter-number mismatch), *Konoha's Medical Ninja: One Punch to Beat Up Madara* (metadata/registry PR [#275](https://github.com/RichardDaffern/Novel-Retriever/pull/275) still open at snapshot), and *HP: The Arcane Thief* (chapter-number mismatch). Before retrying, verify the current PR and any existing final artefact.
- **32 still recorded as `needs_source_verification`** in the 43-title catalogue. Of these, *Naruto: Chronicles of a Fire Ninja* has a possible supported FreeWebNovel listing, but chapter identity/integrity is **not** established. The remaining 31 lack a verified compatible supported source.
- Source evidence and outstanding list: `campaigns/fanfiction/source-verification-round-1-20261119.md`.
- Author identity, distinct editions/translations, truncated screenshot titles and rights must be resolved before downloads. Do not infer a title/slug or use restricted WebNovel scraping.

**Next fanfiction actions:** reconcile PR #275 with its actual download artefact and merge only if verified; diagnose the two chapter-number mismatches; then continue independent source verification for remaining 32.

## 4. Integrity failures and open registration PRs

- [Issue #371](https://github.com/RichardDaffern/Novel-Retriever/issues/371): 14 incomplete Yup/Idk novels: 2 transport interruptions, 10 chapter-number/identity issues, 2 other blockers (index timeout, empty chapter). **Not** an instruction to blindly redownload 14 full books.
- [Issue #257](https://github.com/RichardDaffern/Novel-Retriever/issues/257): historical source numbering mismatches. Preserve exact positions and complete-story checks.
- [Open registry PR #275](https://github.com/RichardDaffern/Novel-Retriever/pull/275) and [PR #265](https://github.com/RichardDaffern/Novel-Retriever/pull/265): metadata-only completion publication, **not** evidence that source ZIPs are still available. Inspect the actual artefact and PR diff before merging.
- The 90 red/Dropped exclusions and Idk title aliases remain a hard gate; `A Thought Through Eternity` refers to *A Will Eternal*, not another book to download.

## 5. Previous 104-book export and cover repair

These were **completed historical operations**, not active or repeatable imports:

1. [104-novel consolidated export #44466510737](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44466510737): verified book ZIP export and manifest. GitHub artefact retention still applies.
2. [Recovered genuine covers #44521807242](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44521807242): 104/104 covers recovered from original ZIPs and EPUBs, not invented or remotely substituted.
3. [Private Storage Controller repair #44522722197](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller/actions/runs/44522722197): 104/104 cover files and catalogue references rechecked after import.
4. The temporary one-time repair workflows were retired, and the reusable offline extraction tools retained.
5. Future bulk-upload automatic standalone-thumbnail support is tracked in [Storage Controller issue #54](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller/issues/54). Do not assume novel ZIP covers always become frontend thumbnails without the Controller's own cover handling.

For future exports, follow [the Controller handover](../campaigns/controller-handoff/README.md) and Section 7 of the [operations runbook](operations-runbook.md).

## 6. Highest-priority next checks

1. Check the **live** large-wave run #44764626782. If source discovery and dispatch completed, retrieve the exact audit and dispatch artefacts and record how many titles were found, submitted, held or blocked. Locate every resulting child `Library - Bulk Download` run.
2. Inspect the two wave-four pilot runs #44762457914 and #44762670118. Verify chapter completion and publication before marking a title complete.
3. Check the registry, open PR #265/#275 and the 14-failure tracker. Prefer selective recovery rather than force.
4. Update Yup/Idk pending counts by canonical identity and currently held groups; avoid treating the old 173 HF gap as a live inventory.
5. Continue the 3 fanfiction recoveries and the separate 32-title source verification process.
6. Keep status facts and timestamps updated in this document **only after verifying them**. Do not append unsupported success claims.

## 7. Refresh procedure for a future agent

Use the read-only observations in [operations runbook](operations-runbook.md). Reconcile, in order:

```text
latest main SHA + PRs
  -> queued/active GitHub Actions
  -> source audit: verified vs unresolved
  -> dispatch report: submitted vs held
  -> child run outcomes and per-book EPUB/ZIP validation
  -> exact canonical URL records in downloaded_novels.json
  -> available (non-expired) artefacts
  -> verified exported ZIPs
  -> Storage Controller/private HF imports, checked separately
```

Update the **snapshot timestamp**, counts and source references in one reviewed documentation PR. **Do not trigger an Actions workflow just to refresh this status document.** For a new campaign, record its new activation, run IDs, source/rights checks and de-duplication evidence before calling it started.

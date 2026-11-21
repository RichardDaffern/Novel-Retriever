# Novel Retriever: Current Operational Status

**Snapshot:** 22 November 2026, 01:56 IST.
**This is a dated snapshot, not a live dashboard.** It was checked against `main` at `72aa1ae839501cd4ea1552deddaa4d6e689bf044`. Re-check the live repository, Actions, PRs, registry and artefact expiry before acting. See the [dynamic-state rules](../AGENTS.md#mandatory-dynamic-project-state-inspection) and [Operations Runbook](operations-runbook.md).

## 1. Repository and CI state

| Item | Verified state | Evidence |
|---|---|---|
| Canonical repository / branch | `RichardDaffern/Novel-Retriever`, `main` | [Repository](https://github.com/RichardDaffern/Novel-Retriever) |
| Snapshot main SHA | `46d0786e6f9250621efafc96c865f8ffba374e31` | [Commit](https://github.com/RichardDaffern/Novel-Retriever/commit/46d0786e6f9250621efafc96c865f8ffba374e31) |
| Completed registry records | **343** rows with `range: all` and `status: complete`; not a count of currently downloadable artefacts or private-HF books | `downloaded_novels.json`, checked after PR #458 |
| Latest main CI | **Success**, all four jobs: security audit, tests, Windows smoke and ZIP archive smoke | [Run #44926984222](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984222) |
| Named acquisition runs | Source audit #44924359606, TOC preflight #44926984233 and single-title #44922285166 are complete; no new bulk run was dispatched in this update | Live jobs/artifacts checked 22 November; the full Actions queue was not re-enumerated |
| Open PRs | #265 and #275, both metadata-only registry updates | [#265](https://github.com/RichardDaffern/Novel-Retriever/pull/265), [#275](https://github.com/RichardDaffern/Novel-Retriever/pull/275) |
| Private Hugging Face inventory | **70 user-confirmed imports**; not independently verified in this Retriever check and not included in the 343 registry rows | Separate Storage Controller source of truth |

The newest registered completion is *Seoul Station’s Necromancer*: 209 chapters, run [#44922285166](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44922285166), artifact ID `14714778249`. All two chapter batches, final EPUB/TXT assembly and validation steps passed. The live artifact API reports expiry `2027-02-19T16:01:42Z`, while the registry row says `2026-11-28T16:22:43Z`; the registry expiry is stale/inconsistent and must not be treated as authoritative. *Archean Eon Art* remains recorded complete at 766 chapters from run #44791453169; verify its live artifact state before reuse.

## 2. Campaign inputs and exclusions

| Input | Current manifest snapshot | Important qualification |
|---|---:|---|
| Yup backlog | 163 entries: 6 `wave3_requested`, 4 `wave4_requested`, 153 `needs_source_verification` | Historical campaign states; recompute against current registry before selecting |
| IDK backlog | 82 reviewed entries | Campaign input, not a live private-library gap |
| Global red/Dropped exclusions | **90** | Hard exclusion across both worksheets, including cross-sheet conflicts |
| Fanfiction catalogue | **43**: 24 Naruto + 19 Harry Potter | Separate workstream and identity list |

The old 173-title Yup gap and older 62-Yup/36-IDK pending estimates are historical baselines, not current missing-from-library counts. Reconcile canonical source URL, author/edition aliases, the completed registry and the private Storage Controller inventory before quoting a live gap. Never bypass the 90 global exclusions.

## 3. 21 November Yup/IDK source audit

The read-only [source audit #44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606) completed successfully.

| Result | Yup | IDK | Total |
|---|---:|---:|---:|
| Eligible after preflight | 54 | 37 | 91 |
| Exact public book listings found | 18 | 8 | **26** |
| No exact listing at tested URL patterns | 36 | 29 | **65** |

It made 336 public book-page requests across NovelFull, ReadNovelFull (standard and `-v1` patterns) and FreeWebNovel; host split among the 26 listings was ReadNovelFull 16, FreeWebNovel 8 and NovelFull 2. Report artifact ID `14714644436` expires `2026-12-21T16:36:47Z`. The result is preserved in [source-audit-2026-11-21.md](../campaigns/overnight/source-audit-report-20261121.md).

**Interpretation:** the 26 are public listing matches, not a download queue. The audit did not fetch chapter prose, establish exact edition/author for every work, or verify permission to archive. The 65 are unresolved by this bounded search, not proven unavailable online. The 26 include previous integrity failures; do not retry unchanged URLs.

### Five-book TOC preflight

[Run #44926984233](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984233) completed successfully as a read-only check. It fetched book metadata and chapter indexes only; `full_chapter_downloads=0` and `rights_verified=false`.

| Title | Result |
|---|---|
| *Doom Lord* | **Index passed** Exact title, 155 chapters |
| *Girl, I’ll Teach You Cultivation* | <badge color="success">Index passed</badge> Exact title, 283 chapters |
| *Beast Piercing The Heavens* | **Failed** Duplicate Chapter 11 links |
| *Godly Student* | <badge color="danger">Failed</badge> Invalid ReadNovelFull chapter URL |
| *The Military Female Soldier With Unwavering Stubbornness* | <badge color="danger">Failed</badge> 2,104 missing numbered chapters |

Only two of the five passed index validation. Neither pass is an authorisation or full-book download. No bulk download was launched by either audit.

## 4. Fanfiction workstream: highest research priority

The original 43-title catalogue remains `campaigns/fanfiction/webnovel-favourites-43.json`; the 11 screenshot-derived title/author records are preserved and were not requested again.

- **8** fanfiction works remain complete in the canonical registry.
- **3** other source-matched works remain blocked/recovery items:
  - *Naruto: The Wind Calamity*: exact FreeWebNovel author/title match, 951 chapters, but non-linear chapter URL mapping; PR #463 now hard-stops instead of guessing.
  - *Konoha’s Medical Ninja: One Punch to Beat Up Madara*: 444 chapters assembled and validated in run #44379388243, but metadata-only PR #275 remains open/non-mergeable. Its public artifact is a rights blocker; the WebNovel page says the credited editor is not the original writer.
  - *HP: The Arcane Thief*: 254 chapters, consistent +1 URL offset; PR #463 fixed the adapter and passed CI. No targeted retry has been run.
- **32** titles were researched in round 2. Five exact title+credited-author FreeWebNovel listings were located, but none passed full edition/index/rights verification. One author spelling mismatch was rejected; 26 titles had no exact supported listing in this search pass. See [round 2 evidence](../campaigns/fanfiction/source-verification-round-2-20261122.md).
- A similar-title FreeWebNovel page for *This Ninja is Obviously …* has a different author and is a false positive. Do not substitute it.
- No fanfiction source has documented permission to archive or publish its full text. Public listing, English label, translator credit or Patreon page is not permission. Do not publish unlicensed novel text in public Actions artifacts.

**Order:** complete the fanfiction source/identity and blocked-source research before searching the 65 unresolved Yup/IDK titles. Keep the 8 complete registry entries, 3 blocked items, 32 research items and 70 user-confirmed private-HF imports as separate counts.
## 5. Known failures and registration follow-up

- [Issue #456](https://github.com/RichardDaffern/Novel-Retriever/issues/456) is the current combined acquisition tracker for Yup, IDK and fanfiction.
- [Issue #452](https://github.com/RichardDaffern/Novel-Retriever/issues/452) records six ReadNovelFull preparation/index failures: *Apotheosis*, *Martial Arts System*, *Path to Heaven*, *The Alchemist God*, *The Mightiest Leveling System* and *Weapon Master*. It also records an *I Shall Seal the Heavens* empty Chapter 690 failure. The latter was subsequently addressed by [PR #454](https://github.com/RichardDaffern/Novel-Retriever/pull/454) and retry run [#44805071470](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44805071470); do not count it as still blocked without checking the current registry and artefact.
- [Issue #448](https://github.com/RichardDaffern/Novel-Retriever/issues/448) separately tracks the *Apotheosis* ReadNovelFull archive gap.
- The older 14-title `blocked-full-retries-20261120.json` is a historical safety list. Reconcile every entry against later fixes, PRs, child runs and final artefacts before treating it as still blocked or retrying it.
- [PR #463](https://github.com/RichardDaffern/Novel-Retriever/pull/463) merged as `72aa1ae`; CI run [#44938176666](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44938176666) passed Windows smoke, security audit, tests and ZIP archive smoke. It fixes HP: The Arcane Thief's +1 URL offset and rejects Naruto: The Wind Calamity's non-linear mapping.
- Test-fix commit [`df575579`](https://github.com/RichardDaffern/Novel-Retriever/commit/df57557958e1ba56d4082f25f20d06b697ab1996) raised the explicit Yup allowlist test from 20 to 21; main CI [#44926984222](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984222) passed all four jobs.
- Open [PR #265](https://github.com/RichardDaffern/Novel-Retriever/pull/265) and [PR #275](https://github.com/RichardDaffern/Novel-Retriever/pull/275) are metadata-only and non-mergeable. PR #275's 444-chapter Konoha Medical artifact is already public; do not merge or re-download until rights and public artifact handling are resolved. Its API expiry and PR-recorded expiry disagree.

## 6. Historical downstream handover

These operations are complete historical milestones, not active workflows:

1. [104-book consolidated export #44466510737](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44466510737).
2. [104 authentic covers recovered #44521807242](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44521807242).
3. [Storage Controller cover repair #44522722197](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller/actions/runs/44522722197).

Do not reactivate one-time repair workflows or assume a new Retriever registry row is imported into private Hugging Face. The Storage Controller owns private dataset writes; the Personal Library owns reader UI and reading progress.

## 7. Next actions, in order

1. Finish the **32-title fanfiction source research** and the three blocked-source recoveries. Only proceed from exact title+author+edition identity, a complete chapter index and documented archiving rights.
2. After fanfiction research is complete, investigate the **65 unresolved Yup/IDK titles** using full-title, author and documented alias searches; do not treat four failed URL patterns as global unavailability.
3. Reconcile the 26 Yup/IDK public listings against completed/blocked records and the 90 exclusions; dispatch only rights-cleared, complete-index titles in batches of at most 10, with no more than two bulk runs active.
4. Reconcile issues #452/#448 and metadata PRs #265/#275; retry only after root-cause repair and exact evidence.
5. Keep source-verified, rights-cleared, TOC-validated, dispatched, assembled, registered, artifact-available, exported and privately imported counts separate.

## 8. Refresh procedure

Before changing this snapshot, inspect current `main`, Git status if a local worktree exists, recent commits, open PRs/issues, queued/in-progress Actions, relevant job logs/artifacts, the current registry and campaign inputs. Record the exact checked SHA and timestamp. Do **not** trigger an Actions workflow just to refresh documentation.

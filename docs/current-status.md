# Novel Retriever: Current Operational Status

**Snapshot:** 21 November 2026, after the 22:23 IST completion of the five-book TOC preflight.
**This is a dated snapshot, not a live dashboard.** It was checked against `main` at `46d0786e6f9250621efafc96c865f8ffba374e31`. Re-check the live repository, Actions, PRs, registry and artefact expiry before acting. See the [dynamic-state rules](../AGENTS.md#mandatory-dynamic-project-state-inspection) and [Operations Runbook](operations-runbook.md).

## 1. Repository and CI state

| Item | Verified state | Evidence |
|---|---|---|
| Canonical repository / branch | `RichardDaffern/Novel-Retriever`, `main` | [Repository](https://github.com/RichardDaffern/Novel-Retriever) |
| Snapshot main SHA | `46d0786e6f9250621efafc96c865f8ffba374e31` | [Commit](https://github.com/RichardDaffern/Novel-Retriever/commit/46d0786e6f9250621efafc96c865f8ffba374e31) |
| Completed registry records | **343** rows with `range: all` and `status: complete`; not a count of currently downloadable artefacts or private-HF books | `downloaded_novels.json`, checked after PR #458 |
| Latest main CI | **Success**, all four jobs: security audit, tests, Windows smoke and ZIP archive smoke | [Run #44926984222](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984222) |
| Queued / in-progress Actions | **None observed** at the last API check | Actions API, 21 November |
| Open PRs | #265 and #275, both metadata-only registry updates | [#265](https://github.com/RichardDaffern/Novel-Retriever/pull/265), [#275](https://github.com/RichardDaffern/Novel-Retriever/pull/275) |
| Private Hugging Face inventory | **Not checked in this snapshot** | Separate Storage Controller source of truth |

The newest registered completion is *Seoul Station’s Necromancer*: 209 chapters, run [#44922285166](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44922285166), artefact [14714778249](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44922285166/artifacts/14714778249), scheduled to expire 28 November 2026 at 16:22 UTC. *Archean Eon Art* is also recorded complete from ReadNovelFull: 766 chapters, run [#44791453169](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44791453169), artefact [14656214990](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44791453169/artifacts/14656214990), expiry 27 November 2026 at 18:29 UTC. Check actual artifact availability separately.

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

It made 336 public book-page requests across NovelFull, ReadNovelFull (standard and `-v1` patterns) and FreeWebNovel; no source host was blocked. The result is preserved in [source-audit-2026-11-21.md](research/source-audit-2026-11-21.md).

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

The original 43-title catalogue is `campaigns/fanfiction/webnovel-favourites-43.json`; it preserves the title/author details captured from 11 screenshots.

- **8** titles are recorded complete in the registry.
- **3** source-matched works remain incomplete or unresolved in registration: *Naruto: The Wind Calamity* (chapter-number mismatch), *Konoha’s Medical Ninja: One Punch to Beat Up Madara* (open metadata-only PR #275; verify the artefact before merging), and *HP: The Arcane Thief* (chapter-number mismatch).
- **32** remain `needs_source_verification` in the catalogue. *Naruto: Chronicles of a Fire Ninja* has a possible FreeWebNovel listing, but source identity and chapter integrity still require review.
- Some screenshot titles are truncated. Do not guess the missing text, equate a different translator/edition, or treat a WebNovel listing as a supported full-download source.

**User's current priority:** research and recover Harry Potter/Naruto fanfiction first; then work through the 65 unresolved Yup/IDK titles. Keep the counts separate. See [fanfiction campaign notes](../campaigns/fanfiction/README.md) and [issue #456](https://github.com/RichardDaffern/Novel-Retriever/issues/456).

## 5. Known failures and registration follow-up

- [Issue #456](https://github.com/RichardDaffern/Novel-Retriever/issues/456) is the current combined acquisition tracker for Yup, IDK and fanfiction.
- [Issue #452](https://github.com/RichardDaffern/Novel-Retriever/issues/452) records six ReadNovelFull preparation/index failures: *Apotheosis*, *Martial Arts System*, *Path to Heaven*, *The Alchemist God*, *The Mightiest Leveling System* and *Weapon Master*. It also records an *I Shall Seal the Heavens* empty Chapter 690 failure. The latter was subsequently addressed by [PR #454](https://github.com/RichardDaffern/Novel-Retriever/pull/454) and retry run [#44805071470](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44805071470); do not count it as still blocked without checking the current registry and artefact.
- [Issue #448](https://github.com/RichardDaffern/Novel-Retriever/issues/448) separately tracks the *Apotheosis* ReadNovelFull archive gap.
- The older 14-title `blocked-full-retries-20261120.json` is a historical safety list. Reconcile every entry against later fixes, PRs, child runs and final artefacts before treating it as still blocked or retrying it.
- Open [PR #265](https://github.com/RichardDaffern/Novel-Retriever/pull/265) and [PR #275](https://github.com/RichardDaffern/Novel-Retriever/pull/275) publish metadata only. Inspect the exact source artefact and diff before merging; do not redownload a complete work solely to close a registry PR.

## 6. Historical downstream handover

These operations are complete historical milestones, not active workflows:

1. [104-book consolidated export #44466510737](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44466510737).
2. [104 authentic covers recovered #44521807242](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44521807242).
3. [Storage Controller cover repair #44522722197](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller/actions/runs/44522722197).

Do not reactivate one-time repair workflows or assume a new Retriever registry row is imported into private Hugging Face. The Storage Controller owns private dataset writes; the Personal Library owns reader UI and reading progress.

## 7. Next actions, in order

1. Work the **43 Harry Potter/Naruto fanfiction requests first**: exact title/author research, then targeted repair of the three source-matched incomplete works.
2. Research the **65 unresolved Yup/IDK titles** using full-title, author and documented alternate-title searches; inspect supported sources only.
3. Reassess the 26 matched URLs against existing complete/failed records. Only a new, exact, permitted source with a complete chapter index is eligible for dispatch.
4. Reconcile issues #452/#448 and open metadata PRs #265/#275; retry only after root-cause repair and with exact evidence.
5. Keep source-verified, rights-cleared, TOC-validated, dispatched, assembled, registered, artifact-available, exported and privately imported counts separate.

## 8. Refresh procedure

Before changing this snapshot, inspect current `main`, Git status if a local worktree exists, recent commits, open PRs/issues, queued/in-progress Actions, relevant job logs/artifacts, the current registry and campaign inputs. Record the exact checked SHA and timestamp. Do **not** trigger an Actions workflow just to refresh documentation.

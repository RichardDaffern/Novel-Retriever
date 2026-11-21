# Novel Retriever: Current Operational Status

**Snapshot:** 22 November 2026, 03:27 IST.
**This is a dated snapshot, not a live dashboard.** The checked `main` base is `72aa1ae839501cd4ea1552deddaa4d6e689bf044`; the accompanying documentation branch contains the updates described below. Re-check live Actions, PRs and artefacts before acting. Re-check the live repository, Actions, PRs, registry and artefact expiry before acting. See the [dynamic-state rules](../AGENTS.md#mandatory-dynamic-project-state-inspection) and [Operations Runbook](operations-runbook.md).

## 1. Repository and CI state

| Item | Verified state | Evidence |
|---|---|---|
| Canonical repository / checked main base | `RichardDaffern/Novel-Retriever`, `main` at `72aa1ae839501cd4ea1552deddaa4d6e689bf044` | [Repository](https://github.com/RichardDaffern/Novel-Retriever) |
| Completed registry | **343** complete records in `downloaded_novels.json`; this is not a count of currently available artifacts or private-HF imports | Current registry, reconciled 22 November |
| User-confirmed private-HF imports | **70**, user-confirmed but not independently queried in this Retriever run | Separate Storage Controller source of truth |
| Global exclusions | **90** red/Dropped titles; remain excluded from Yup and IDK campaigns | `campaigns/overnight/excluded-90.json` |
| CI baseline | The 21-entry expansion test fix `df57557958e1ba56d4082f25f20d06b697ab1996` is covered by [run #44926984222](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984222), all four jobs green | GitHub Actions |
| Read-only source audit | [Run #44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606), artifact `14714644436`; no chapter text | Source-audit report |
| Read-only five-book preflight | [Run #44926984233](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984233), artifact `14715652405`; no chapter text | Five-book TOC report |
| Latest single-title completion | *Seoul Station’s Necromancer*, 209 chapters, [run #44922285166](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44922285166), artifact `14714778249` | All chapter batches and final EPUB/TXT validation passed |
| PR #463 | Merged at `72aa1ae839501cd4ea1552deddaa4d6e689bf044`; CI [run #44938176666](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44938176666) green | Arcane Thief offset regression test and Wind Calamity fail-closed mapping |
| Open PRs | #265 and #275 remain metadata-only; #275 is held for Konoha Medical rights/public-artifact handling. [PR #464](https://github.com/RichardDaffern/Novel-Retriever/pull/464) records this audit and expiry reconciliation; CI #44956229460 is green, not merged. | [#265](https://github.com/RichardDaffern/Novel-Retriever/pull/265), [#275](https://github.com/RichardDaffern/Novel-Retriever/pull/275), [#464](https://github.com/RichardDaffern/Novel-Retriever/pull/464) |
| Active workflows | **0** queued/in-progress at 03:27 IST; no new bulk run dispatched | Live Actions run list |

The live Actions API reports Seoul Station’s Necromancer artifact expiry as `2027-02-19T16:01:42Z`; the registry value was stale and has been corrected in the accompanying branch. The seven still-present fanfiction artifacts also had stale registry expiry values; those are corrected to the live API dates in the same branch.

## 2. Campaign inputs and exclusions

| Input | Current manifest snapshot | Important qualification |
|---|---:|---|
| Yup backlog | 163 entries: 6 `wave3_requested`, 4 `wave4_requested`, 153 `needs_source_verification` | Historical campaign states; recompute against current registry before selecting |
| IDK backlog | 82 reviewed entries | Campaign input, not a live private-library gap |
| Global red/Dropped exclusions | **90** | Hard exclusion across both worksheets, including cross-sheet conflicts |
| Fanfiction catalogue | **43**: 24 Naruto + 19 Harry Potter | Separate workstream and identity list |

The old 173-title Yup gap and older 62-Yup/36-IDK pending estimates are historical baselines, not current missing-from-library counts. Reconcile canonical source URL, author/edition aliases, the completed registry and the private Storage Controller inventory before quoting a live gap. Never bypass the 90 global exclusions.

## 3. 21 November Yup/IDK source audit and preflight

The source audit [#44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606) used 336 public book-page requests across 91 eligible rows:

- **26 exact public listings:** 18 Yup and 8 IDK.
- **65 unresolved:** 36 Yup and 29 IDK.
- The audit was read-only: it did not fetch chapter prose, create EPUB/ZIP files or establish rights.
- None of the 26 listing matches is already in the 343-record completed registry. The 90 red/Dropped exclusions remain separate.

### Five-book TOC preflight

[Run #44926984233](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984233) was also read-only:

| Candidate | TOC result | Rights |
|---|---|---|
| Doom Lord | Passed, 155 chapters | `rights_verified=false` |
| Girl, I'll Teach You Cultivation | Passed, 283 chapters | `rights_verified=false` |
| Beast Piercing The Heavens | Failed: duplicate Chapter 11 links | `rights_verified=false` |
| Godly Student | Failed: invalid chapter URL | `rights_verified=false` |
| The Military Female Soldier With Unwavering Stubbornness | Failed: large missing-number range | `rights_verified=false` |

The 26 public matches are grouped as 12 older blocked titles from #371, nine titles with 20-Nov source/TOC failures, and five fresh candidates. They are not a download queue.

### Exact #452 failure evidence

- *Past Life Returner*: FreeWebNovel stopped with `Expected Chapter 501, but the page identifies Chapter 500`.
- *This MC Is Kickass*: FreeWebNovel stopped with `Expected Chapter 101, but the page identifies Chapter 102`.
- *Martial Arts System*, *Path to Heaven* and *Weapon Master*: ReadNovelFull preparation exited during URL validation with no useful exception surfaced in the job log. Do not retry the same URLs unchanged.
- *The Alchemist God* and *The Mightiest Leveling System*: ReadNovelFull stopped with `Invalid ReadNovelFull chapter URL`.
- The #44769541580 child dispatch submitted four URLs, but only the *Past Life Returner* and *This MC Is Kickass* matrix jobs ran. *Tomb Raider King* and *World Domination System* have no chapter logs from that run; they were not attempted by that child. The current bulk workflow uses `fail-fast: false` to prevent one matrix failure cancelling later titles.
- The targeted *The Alchemist God* retry #44804318431 ran on PR #453's merged commit and still failed during indexing with `Invalid ReadNovelFull chapter URL`. PR #453 added strict genuine-prologue support but did not resolve this different URL shape. Identify the actual offending TOC URL and add a regression test before retry.

The 12 older #371 titles remain blocked, but their failure classes differ. Nine have confirmed chapter-identity mismatches: Awakening (2→9), Condemning the Heavens (1→0), Flower Master In The City (1101→1110), Heavenly Star (266→267), Ex Rank Supporting Role’s Replay (851→852), Game Market 1983 (125→124), Parasite in Love (2→1), Sense (1→0) and The S-Classes That I Raised (251→216). Beauty And The Bodyguard timed out after three source attempts; no TOC was obtained. Legend of Swordsman produced no final ZIP and only a partial 5601–5800 batch; issue #371 reports Chapter 5742 returned an empty body. Omega Summoner's run #44447221591 has successful chapter batches 1–3,083, but recovery manifest `14496292098` says 0 ZIPs saved and lists it as missing/failed; the 2069→2070 mismatch claim is not present in that run's logs. Treat Omega as not archived/registered, not as a verified chapter mismatch. See the 22 November reconciliation appended to issue #371. Do not weaken source identity or chapter-index checks, force a retry, or treat a public listing as permission.

## 4. Fanfiction workstream: first-pass source research complete

The immutable catalogue has **43 titles**: 24 Naruto and 19 Harry Potter. It remains separate from Yup/IDK and from the user's **70 separately confirmed private-HF imports**.

| State | Count | Evidence |
|---|---:|---|
| Completed in registry | 8 | `downloaded_novels.json` |
| Source-matched but blocked/incomplete | 3 | Wind Calamity, Konoha's Medical Ninja, HP: The Arcane Thief |
| Requiring source research | 32 | `webnovel-favourites-43.json` |

The corrected exact title/credited-author pass across NovelFull, ReadNovelFull and FreeWebNovel found **5 exact supported-host listings**, **2 near/variant matches**, and **25 with no exact supported-host listing**. None passed the complete edition, full-index and rights gate. No new fanfiction download run was dispatched.

- The five exact listings are *Naruto: Chronicles of a Fire Ninja*, *Reborn into Naruto World with Tenseigan*, *Naruto: Starting With Creating A Genius Persona*, *Harry Potter: The Healer* and *There Will Be No Third Dark Lord At Hogwarts!!!*. See [round 3](../campaigns/fanfiction/source-verification-round-3-20261122.md).
- The two near matches are *Talent System In The Naruto Universe* (Rashta vs catalogue Rashita) and *Naruto: This Ninja is Obviously …* (FreeWebNovel author Wu Mian Qi Liang vs selected WebNovel author nyawdao2). Do not substitute either.
- The [identity ledger](../campaigns/fanfiction/source-identity-resolution-20261122.md) resolves full title/credited-author references for all 32 without changing the original JSON strings or requesting screenshots.

### Three blocked fanfiction sources

- **Naruto: The Wind Calamity:** the FreeWebNovel chapter labels/URL numbering are non-linear. PR #463 makes the adapter fail closed instead of guessing. No retry without a complete one-to-one map and rights clearance.
- **Konoha's Medical Ninja: One Punch to beat up Madara:** 444-chapter archive technically assembled and validated, but it is not registered; metadata-only PR #275 remains open. Its GitHub Actions archive artifact is `14462633408` (expires `2027-02-16T19:20:05Z`) and is public; rights are unresolved. Do not merge, re-download, link or create another public archive without permission.
- **HP: The Arcane Thief:** 254-chapter source index has a consistent +1 URL offset. PR #463 merged the narrow fix and regression test. No targeted retry until rights are verified.

### Eight completed entries and artifact state

Seven artifacts are currently present and publicly accessible; rights are unverified. Do not link, download or create another public copy. The connected GitHub operations do not expose artifact revocation. *The Adventurous Gamer Ninja - Daichi Hekima*'s artifact expired on 21 November 2026.

| Work | Chapters | Run | Artifact | Current API expiry |
|---|---:|---:|---:|---|
| The Adventurous Gamer Ninja - Daichi Hekima | 432 | #43589834773 | 14111234860 | Expired 2026-11-21T11:24:36Z |
| A New Snake In The Shinobi World | 423 | #44378479201 | 14464695010 | 2027-02-16T19:14:59Z |
| Naruto: I am Uchiha Shirou | 448 | #44378935249 | 14463647756 | 2027-02-16T19:17:32Z |
| Naruto: Kurotsuchi Mayuri | 524 | #44378935249 | 14463808054 | 2027-02-16T19:17:32Z |
| HP: A Magical Journey | 439 | #44381959077 | 14465975343 | 2027-02-16T19:35:15Z |
| Hogwarts: I'm Truly a Model Wizard | 1,004 | #44381959077 | 14464369346 | 2027-02-16T19:35:15Z |
| Hogwarts' John Wick | 703 | #44389807742 | 14469106672 | 2027-02-16T20:19:28Z |
| The Fool in Hogwarts | 333 | #44389807742 | 14469501148 | 2027-02-16T20:19:28Z |

Run #44378479201 failed overall because *The Wind Calamity* batches failed. *A New Snake*'s own chapter batches 1–423 succeeded and its archive artifact is present; do not mark that novel failed solely from the shared run conclusion. The expired *Adventurous Gamer Ninja* artifact cannot be re-inspected. No archive contents were downloaded or redistributed during this check.

## 5. Known failures, aliases and registration follow-up

- **Yup/IDK registry:** 343 completed records. The 26 public listing matches are not in this registry. The user's 70 private-HF imports are a separate, user-confirmed count and must not be added to the registry total.
- **Aliases already in the registry:** Invincible Conqueror = Invincible; Xian Ni = Renegade Immortal; Records of the Human Emperor = The Human Emperor; School Prince is a Girl = National School Prince Is A Girl; A Thought Through Eternity = A Will Eternal. The first four appear among the 65 unresolved audit rows and should be treated as aliases, not new downloads.
- **Alternative-source sweep of the 65:** after the four registry aliases, 61 distinct titles were searched (33 Yup and 28 IDK). It found **12 exact supported-host listing candidates**, **3 near/variant matches**, and **46 with no exact supported listing**. No candidate has documented lawful archiving permission; no download run was dispatched. See [alternative-source research](../campaigns/overnight/alternative-source-research-20261122.md).
- **Thirteen candidate listings are not thirteen ready downloads.** Several have incomplete/mismatched indexes: *Eternal Martial Sovereign* (140 linked pages but numbering to 191), *Hidden Marriage* (six gaps), *Lonely Loser* (60 pages vs 58 original chapters), *My Plain-looking Fiance* (46 vs 56), *The Gloomy Me* (75 vs 111), plus the known *Apotheosis* failure. No unchanged retries.
- **ReadNovelFull:** PR #453 added genuine prologue handling, but *The Alchemist God* still failed with an invalid chapter URL after that merge. Do not loosen URL validation or retry until the exact invalid TOC URL is captured and tested.
- **Konoha Medical:** PR #275 is metadata-only and held; the 444-chapter artifact is public and rights are unresolved. The repository connector used here cannot revoke that existing artifact. Do not expose its link or create another public copy.
- **Artifact metadata:** the seven present fanfiction artifacts and Seoul Station's Necromancer now have expiry fields corrected to the live Actions API dates in the accompanying branch. The one expired fanfiction artifact remains historical.
- **Throughput:** keep no more than two bulk workflows active and no more than ten titles per batch. No bulk workflows were active at the 03:27 IST check. Never treat a source-audit or TOC-preflight run as a chapter download.

## 6. Historical downstream handover

These operations are complete historical milestones, not active workflows:

1. [104-book consolidated export #44466510737](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44466510737).
2. [104 authentic covers recovered #44521807242](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44521807242).
3. [Storage Controller cover repair #44522722197](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller/actions/runs/44522722197).

Do not reactivate one-time repair workflows or assume a new Retriever registry row is imported into private Hugging Face. The Storage Controller owns private dataset writes; the Personal Library owns reader UI and reading progress.

## 7. Next actions, in order

1. Continue the 61-title alternative-source review from the [dated research report](../campaigns/overnight/alternative-source-research-20261122.md), starting with the 12 exact supported-host candidates. Validate author, edition, English language, complete ordered TOC and explicit lawful archiving permission before any campaign entry.
2. Investigate the 12 older #371 blocked titles and nine #452 names with exact logs. Repair only proven adapter/root causes with regression tests; do not retry deterministic failures unchanged.
3. Continue the 25 unresolved fanfiction supported-source searches and resolve the two near matches only with exact author/edition evidence. Keep the three blocked fanfiction works on hold until rights and index integrity are clear.
4. Dispatch only rights-cleared titles through the existing resumable bulk workflow: at most ten titles per batch, no more than two active workflows, no complete-title duplicates, no force unless separately justified.
5. Keep source-verified, rights-cleared, TOC-validated, dispatched, chapter-complete, assembled, registered, artifact-available, exported and privately imported counts separate.



## 8. Refresh procedure

Before changing this snapshot, inspect current `main`, Git status if a local worktree exists, recent commits, open PRs/issues, queued/in-progress Actions, relevant job logs/artifacts, the current registry and campaign inputs. Record the exact checked SHA and timestamp. Do **not** trigger an Actions workflow just to refresh documentation.

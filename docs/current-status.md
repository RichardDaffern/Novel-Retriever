# Novel Retriever: Current Operational Status

**Snapshot:** 22 November 2026, 10:50 IST.
**This is a dated snapshot, not a live dashboard.** The checked `main` head is `87cbeca671423abce00be7002d1f613142d0eea3`; PRs #464–#469 are merged. Re-check live Actions, PRs and artefacts before acting. See the [dynamic-state rules](../AGENTS.md#mandatory-dynamic-project-state-inspection) and [Operations Runbook](operations-runbook.md).

## 1. Repository and CI state

| Item | Verified state | Evidence |
|---|---|---|
| Canonical repository / checked main head | `RichardDaffern/Novel-Retriever`, `main` at `87cbeca671423abce00be7002d1f613142d0eea3` | [Repository](https://github.com/RichardDaffern/Novel-Retriever) |
| Completed registry | **343** complete records in `downloaded_novels.json`; this is not a count of currently available artifacts or private-HF imports | Current registry, reconciled 22 November |
| User-confirmed private-HF imports | **70**, user-confirmed but not independently queried in this Retriever run | Separate Storage Controller source of truth |
| Global exclusions | **90** red/Dropped titles; remain excluded from Yup and IDK campaigns | `campaigns/overnight/excluded-90.json` |
| CI baseline | The 21-entry expansion test fix `df57557958e1ba56d4082f25f20d06b697ab1996` is covered by [run #44926984222](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984222), all four jobs green | GitHub Actions |
| Read-only source audit | [Run #44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606), artifact `14714644436`; no chapter text | Source-audit report |
| Read-only five-book preflight | [Run #44926984233](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984233), artifact `14715652405`; no chapter text | Five-book TOC report |
| Latest single-title completion | *Seoul Station’s Necromancer*, 209 chapters, [run #44922285166](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44922285166), artifact `14714778249` | All chapter batches and final EPUB/TXT validation passed |

The Seoul Station artifact is publicly available. The run, chapter batches, assembly and registry entry are technically verified, but no explicit public-archiving permission is recorded in this repository. Treat artifact `14714778249` as rights-unverified; do not create additional public novel artifacts without documented permission. If public redistribution is not authorised, repository-owner deletion/revocation is required.
| PR #463 | Merged at `72aa1ae839501cd4ea1552deddaa4d6e689bf044`; CI [run #44938176666](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44938176666) green | Arcane Thief offset regression test and Wind Calamity fail-closed mapping |
| Merged acquisition-research PRs | #464–#469 merged. PR #469 CI [#44986219817](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44986219817) and post-merge main CI [#44986296039](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44986296039) passed all four jobs. | [#464](https://github.com/RichardDaffern/Novel-Retriever/pull/464), [#465](https://github.com/RichardDaffern/Novel-Retriever/pull/465), [#466](https://github.com/RichardDaffern/Novel-Retriever/pull/466), [#467](https://github.com/RichardDaffern/Novel-Retriever/pull/467), [#468](https://github.com/RichardDaffern/Novel-Retriever/pull/468), [#469](https://github.com/RichardDaffern/Novel-Retriever/pull/469) |
| Open PRs | #265, #275 and #470 are open. #470 is documentation-only with CI pending; #275 is held and unmergeable for Konoha Medical. | [#265](https://github.com/RichardDaffern/Novel-Retriever/pull/265), [#275](https://github.com/RichardDaffern/Novel-Retriever/pull/275), [#470](https://github.com/RichardDaffern/Novel-Retriever/pull/470) |
| Bulk download workflows | **0** queued/in-progress at 10:50 IST; no new download run dispatched. Post-merge main CI #44986296039 passed all four jobs and is not a download workflow. | Live Actions run list |

The live Actions API reports Seoul Station’s Necromancer artifact expiry as `2027-02-19T16:01:42Z`, matching the registry. The seven still-present fanfiction final-artifact expiry values also match the live API; *The Adventurous Gamer Ninja* artifact expired on 21 November 2026 and no longer appears in the run’s artifact list. No registry expiry change was needed in this branch.

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
- **Preflight count clarification:** `previously_known=349` is the distinct union of 343 titles in `downloaded_novels.json` and 21 rows in `campaigns/yup-pilot/verified-urls.json`, with 15 overlaps. The six verified-URL-only titles are Desolate Era, A Record Of Mortal’s Journey To Immortality, Warlock Of Magus World, Solo Levelling, Advent of Archmage and Charm Of Soul Pet. They are prior verified source URLs, **not** six extra completed registry downloads or HF imports. The completed registry remains 343; the separately user-confirmed private-HF import count remains 70.

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

### Five-candidate author and edition follow-up

The additional review is recorded in [the source-audit report](../campaigns/overnight/source-audit-report-20261121.md). It resolved the five candidate identities but cleared no downloads: *Beast Piercing The Heavens* is Yao Ye's 1,445-chapter original (ReadNovelFull mirror 224 entries, duplicate Chapter 11); *Doom Lord* is by Wishing For A Pillow To Sleep With (856 original chapters versus 155 in the passing TOC); *Godly Student* is by Such Ink-like Blood (2,783 original chapters; invalid ReadNovelFull chapter URL); *Girl, I'll Teach You Cultivation* is by Watchdog (812 original chapters versus 283 in the passing TOC); and *The Military Female Soldier With Unwavering Stubbornness* is by 直上青云 (5,707 chapters; the ReadNovelFull index has a large missing-number range). The WebNovel credit Mistyfox is not the original-author identity. None has explicit archiving permission. No download run was dispatched.

### Exact #452 failure evidence

- *Past Life Returner*: FreeWebNovel stopped with `Expected Chapter 501, but the page identifies Chapter 500`.
- *This MC Is Kickass*: FreeWebNovel stopped with `Expected Chapter 101, but the page identifies Chapter 102`.
- *Martial Arts System*, *Path to Heaven* and *Weapon Master*: ReadNovelFull preparation exited during URL validation with no useful exception surfaced in the job log. Do not retry the same URLs unchanged.
- *The Alchemist God* and *The Mightiest Leveling System*: ReadNovelFull stopped with `Invalid ReadNovelFull chapter URL`.
- The #44769541580 child dispatch submitted four URLs, but only the *Past Life Returner* and *This MC Is Kickass* matrix jobs ran. *Tomb Raider King* and *World Domination System* have no chapter logs from that run; they were not attempted by that child. The current bulk workflow uses `fail-fast: false` to prevent one matrix failure cancelling later titles.
- The targeted *The Alchemist God* retry #44804318431 ran on PR #453's merged commit and still failed during indexing with `Invalid ReadNovelFull chapter URL`. PR #453 added strict genuine-prologue support but did not resolve this different URL shape. Identify the actual offending TOC URL and add a regression test before retry.

The 12 older #371 titles remain blocked, but their failure classes differ. Nine have confirmed chapter-identity mismatches: Awakening (2→9), Condemning the Heavens (1→0), Flower Master In The City (1101→1110), Heavenly Star (266→267), Ex Rank Supporting Role’s Replay (851→852), Game Market 1983 (125→124), Parasite in Love (2→1), Sense (1→0) and The S-Classes That I Raised (251→216). Beauty And The Bodyguard timed out after three source attempts; no TOC was obtained. Legend of Swordsman produced no final ZIP and only a partial 5601–5800 batch; issue #371 reports Chapter 5742 returned an empty body. Omega Summoner's run #44447221591 has successful chapter batches 1–3,083, but recovery manifest `14496292098` says 0 ZIPs saved and lists it as missing/failed; the 2069→2070 mismatch claim is not present in that run's logs. Treat Omega as not archived/registered, not as a verified chapter mismatch. See the 22 November reconciliation appended to issue #371. Do not weaken source identity or chapter-index checks, force a retry, or treat a public listing as permission.

## 4. Fanfiction workstream: source research ongoing

The immutable catalogue has **43 titles**: 24 Naruto and 19 Harry Potter. It remains separate from Yup/IDK and from the user's **70 separately confirmed private-HF imports**.

| State | Count | Evidence |
|---|---:|---|
| Completed in registry | 8 | `downloaded_novels.json` |
| Source-matched but blocked/incomplete | 3 | Wind Calamity, Konoha's Medical Ninja, HP: The Arcane Thief |
| Requiring source research | 32 | `webnovel-favourites-43.json` |

The catalogue's `review_state` is an initial campaign/source-review state, not live source discovery or download completion. It contains 1 `already_downloaded`, 10 `public_source_listing_matched` and 32 `needs_source_verification` rows. Seven of the ten initial source-matched rows are already complete in `downloaded_novels.json`; the remaining three are the blocked works. The five exact supported-host candidates found in later rounds remain within the 32 `needs_source_verification` rows until edition, full-index and permission gates pass. Together with the first row, this reconciles to **8 complete, 3 blocked and 32 requiring research**. The registry, not the catalogue's `review_state`, is authoritative for completion. The legacy `tools/fanfiction_campaign.py` one-shot queue is not to be rerun: its old 2-title batches and 4-active limit conflict with the current 10-title / 2-active policy.

The corrected exact title/credited-author pass across NovelFull, ReadNovelFull and FreeWebNovel found **5 exact supported-host listings**, **2 near/variant matches**, and **25 with no exact supported-host listing**. None passed the complete edition, full-index and rights gate. No new fanfiction download run was dispatched.

- The five exact listings are *Naruto: Chronicles of a Fire Ninja*, *Reborn into Naruto World with Tenseigan*, *Naruto: Starting With Creating A Genius Persona*, *Harry Potter: The Healer* and *There Will Be No Third Dark Lord At Hogwarts!!!*. See [round 3](../campaigns/fanfiction/source-verification-round-3-20261122.md).
- The two near matches are *Talent System In The Naruto Universe* (Rashta vs catalogue Rashita) and *Naruto: This Ninja is Obviously …* (FreeWebNovel author Wu Mian Qi Liang vs selected WebNovel author nyawdao2). Do not substitute either.
- The [identity ledger](../campaigns/fanfiction/source-identity-resolution-20261122.md) resolves full title/credited-author references for all 32 without changing the original JSON strings or requesting screenshots.
- Round 5 added alternate-host metadata for 21 title records, including raw-title/translator distinctions, author pen-name links and cross-site chapter-count differences. It found **0 new exact supported-host listings**, **0 explicit archiving permissions** and dispatched no download. See [round 5](../campaigns/fanfiction/source-verification-round-5-20261122.md). Round 6 ran 30 author-qualified and 26 title-only searches across NovelFull, ReadNovelFull and FreeWebNovel; it found **0 additional exact supported-host listings** and **0 explicit permissions**. Refreshed evidence confirms edition/index drift for Tenseigan, The Healer and There Will Be No Third Dark Lord. FirstHokage's Royal Road post warns against unauthorised Amazon use; Devil_Hex requires permission before translation; Wind Calamity counts vary from 455 to 951. Round 6 identifies Gezenshaft as the original author of *The Healer*, whose English mirror is a translation with unresolved rights and chapter drift. See [round 6](../campaigns/fanfiction/source-verification-round-6-20261122.md). Round 7 searched all 32 remaining title/selected-author pairs and ran supported-host checks; it found **0 additional exact supported-host listings** and **0 explicit permissions**. New catalogue evidence identifies IHaveNoNamingSense as translator of *Life of a Villain in The Naruto World* (original author Yun Sixie), records a PinkSnake/1PinkSnake1 cross-post lead for *Konoha's Trickster* without underlying-work clearance, and confirms that *Naruto: Kurotsuchi Mayuri* is already complete in the registry at 524 chapters, so its 490-chapter WebNovel listing is not a new target. See [round 7](../campaigns/fanfiction/source-verification-round-7-20261122.md). Round 8 rechecked rights and editions for the five exact supported-host candidates and three blocked works; it found **0 additional exact listings** and **0 explicit archive grants**. Devil_Hex's author note says Wind Calamity translations appeared without permission or knowledge and asks translators to contact the author first. Snollygoster's FanFiction.net cross-post is 183 chapters, while the WebNovel 255-entry catalogue includes an auxiliary page and the selected FreeWebNovel edition has 254 numbered chapters. INeedRest again states they are not Konoha Medical's original writer. Exact run #44379388243 logs show all nine chapter batches 1–444 succeeded and assembly produced 444 verified TXT chapters plus an EPUB; artifact #14462633408 was uploaded before registry PR #275 failed to merge after six attempts. This is assembled but unregistered, not a chapter-integrity failure. See [round 8](../campaigns/fanfiction/source-verification-round-8-20261122.md). No chapter prose or archive bytes were fetched; no retry or download was started. The three blocked works remain unresolved: Wind Calamity has no canonical chapter map; Konoha Medical's credited editor explicitly says they are not the original writer; Arcane Thief remains 183 FanFiction.net chapters versus 254 FreeWebNovel entries (Ranobes lists 254 written/275 available).

### Three blocked fanfiction sources

- **Naruto: The Wind Calamity:** WebNovel shows 951 entries including auxiliary 0.1–0.3 sections; NovelLive shows 832; FreeWebNovel has a non-linear 951-entry index. These are not a verified one-to-one map. PR #463 makes the adapter fail closed instead of guessing. Devil_Hex's FanFiction.net page requires permission before translation. No retry without a canonical TOC map and rights clearance.
- **Konoha's Medical Ninja: One Punch to beat up Madara:** FreeWebNovel and WebNovel both show 444 chapters, but credited editor INeedRest explicitly says they are not the original writer; the underlying author remains unidentified. Run #44379388243's nine chapter-batch jobs succeeded for 444 chapters and the workflow uploaded final novel artifact #14462633408. The assemble job then failed during registry publication: it opened registry PR #275 and six merge attempts failed after the base branch changed and the PR remained unmergeable. The artifact contents were not fetched or independently verified because rights remain unresolved. Its GitHub Actions archive artifact is `14462633408` (expires `2027-02-16T19:20:05Z`) and is public; rights are unresolved. Do not merge, re-download, link or create another public archive without permission.
- **HP: The Arcane Thief:** the selected [FreeWebNovel listing](https://freewebnovel.com/novel/hp-the-arcane-thief) credits Snollygoster, labels the edition English and shows one auxiliary entry before Chapter 1, opening chapters 1–39 and latest chapters 254–249. PR #463 fixed the corresponding +1 URL offset with a regression test. The separate FanFiction.net cross-post lists 183 chapters; [Ranobes](https://ranobes.net/novels/1205620-the-arcane-thief-v741610.html) reports 254 written/275 available. The 183 count is not proof that the selected 254-chapter FWN edition is incomplete. Its full TOC has not been revalidated end-to-end and no archive permission was found. No retry.

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
- **Historical alternative-source sweep of the 65:** this first sweep occurred before all 32 fanfiction targets and the three blocked works were resolved. Do not extend or repeat it until the fanfiction research is complete. After four registry aliases, 61 distinct titles were searched (33 Yup and 28 IDK): **12 exact supported-host listing candidates**, **3 near/variant matches**, and **46 with no exact supported listing**. No candidate has documented lawful archiving permission; no download run was dispatched. This is not a worldwide-unavailability finding. See [alternative-source research](../campaigns/overnight/alternative-source-research-20261122.md).
- **Thirteen candidate listings are not thirteen ready downloads.** Several have incomplete/mismatched indexes: *Eternal Martial Sovereign* (140 linked pages but numbering to 191), *Hidden Marriage* (six gaps), *Lonely Loser* (60 pages vs 58 original chapters), *My Plain-looking Fiance* (46 vs 56), *The Gloomy Me* (75 vs 111), plus the known *Apotheosis* failure. No unchanged retries.
- **ReadNovelFull:** PR #453 added genuine prologue handling, but *The Alchemist God* still failed with an invalid chapter URL after that merge. Do not loosen URL validation or retry until the exact invalid TOC URL is captured and tested.
- **Konoha Medical:** PR #275 is a registry PR, held and unmergeable; the 444-chapter artifact is public and rights are unresolved. The repository connector used here cannot revoke that existing artifact. Do not expose its link or create another public copy.
- **Artifact metadata:** the seven present fanfiction artifacts and Seoul Station's Necromancer now have expiry fields corrected to the live Actions API dates in the accompanying branch. The one expired fanfiction artifact remains historical.
- **Throughput:** keep no more than two bulk workflows active and no more than ten titles per batch. No bulk download workflow was queued or in progress at the 06:39 IST check; PR #464 documentation CI and PR #465 diagnostics CI are separate and are not download runs. Never treat a source-audit or TOC-preflight run as a chapter download.

## 6. Historical downstream handover

These operations are complete historical milestones, not active workflows:

1. [104-book consolidated export #44466510737](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44466510737).
2. [104 authentic covers recovered #44521807242](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44521807242).
3. [Storage Controller cover repair #44522722197](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller/actions/runs/44522722197).

Do not reactivate one-time repair workflows or assume a new Retriever registry row is imported into private Hugging Face. The Storage Controller owns private dataset writes; the Personal Library owns reader UI and reading progress.

## 7. Next actions, in the user's strict order

The first 26-match source triage is complete. The five-book TOC preflight is complete and read-only: only *Doom Lord* (155) and *Girl, I'll Teach You Cultivation* (283) passed structural checks, but all five candidates still have rights_verified=false. Do not launch them without explicit lawful archiving permission.

1. **Finish the fanfiction source research before doing more work on the 65 unmatched Yup/IDK titles.** The 43-title catalogue remains 24 Naruto + 19 Harry Potter: 8 registry-complete, 3 separately blocked/source-matched and 32 requiring source research. The first supported-host pass found 5 exact listings, 2 near/variant matches and 25 with no exact supported-host listing. Round 4 added author-facing identity and alternate-mirror evidence, but found no new exact supported-host listing and no archiving permission. Round 5 added further title/author/edition metadata for 21 records, with no new exact supported-host listing or permission. Round 6 ran another 30 author-qualified and 26 title-only supported-host searches, with no additional exact listing or permission. Round 7 searched all 32 remaining title/selected-author pairs and ran supported-host checks, again with 0 additional exact listings and 0 permissions. It added translator/original-author and alternate-edition evidence; see [round 7](../campaigns/fanfiction/source-verification-round-7-20261122.md). PR #466 now adds exact FreeWebNovel chapter-to-URL mismatch diagnostics with an offline regression test; CI #44971034816 passed all four jobs, and no title was retried. Continue resolving exact title, credited author, underlying original author, edition, English language and complete index. Never request the screenshots again.
2. **Resolve the three blocked fanfiction works without unchanged retries.** *Naruto: The Wind Calamity* has non-linear chapter mapping and now fails closed; *Konoha's Medical Ninja* has 444 successful chapter batches and an uploaded artifact, but the assemble/registry job failed while merging PR #275; the artifact contents were not independently checked and underlying-author identity/rights remain unresolved; *HP: The Arcane Thief* has a +1 URL offset fix in merged PR #463 for the selected 254-chapter FWN edition; the separate 183-chapter FanFiction.net cross-post is not evidence that the selected edition is incomplete. The full FWN TOC and rights remain unverified. Do not re-download or create another public artifact.
3. **Only after the fanfiction research is complete, continue the 65 unmatched Yup/IDK alternative-source investigation** (36 Yup, 29 IDK). Four completed-registry aliases leave 61 distinct titles. The first sweep found 12 exact supported-host listing candidates, 3 near/variant matches and 46 with no exact supported listing; none has documented archiving permission. Do not treat four 404 URL patterns as worldwide unavailability.
4. **Then dispatch only fully cleared titles.** Require exact work/author/edition, English language, a complete ordered TOC and explicit lawful permission to archive, with a safe non-public output route. Fix #371/#452 adapter issues only with exact root-cause evidence and regression tests. Use the existing resumable bulk workflow, at most 10 titles per batch and at most two active runs, no complete-title duplicates and force=false.

No source-audit or TOC-preflight run is a chapter download. Keep Yup, IDK, fanfiction, the 343-record completed registry and the user's separate 70 private-HF imports independently counted. Do not treat the 490-chapter WebNovel listing for Naruto: Kurotsuchi Mayuri as new: its 524-chapter registry record is already complete.

## 8. Refresh procedure

Before changing this snapshot, inspect current `main`, Git status if a local worktree exists, recent commits, open PRs/issues, queued/in-progress Actions, relevant job logs/artifacts, the current registry and campaign inputs. Record the exact checked SHA and timestamp. Do **not** trigger an Actions workflow just to refresh documentation.


## 22 November 2026, 09:22 IST: fanfiction source research round 9

Round 9 searched the 25 catalogue entries that still had no exact NovelFull, ReadNovelFull or FreeWebNovel listing, plus the three separately blocked works. It found **0 new exact supported-host matches**, **8 additional non-supported catalogue/cross-post leads**, **0 explicit archiving permissions**, and **0 new download runs**. The existing totals remain 5 exact supported-host candidates, 2 rejected near/variant matches and 25 without an exact supported-host listing. The 8 additional pages are identity/edition leads only, not supported download sources; their TOCs were not validated end-to-end.

Newly surfaced cross-post/alternate catalogue evidence includes:
- *Naruto: Transmigrated as an Uchiha* (NoviceAuthor): Xnovel, 326 chapters.
- *Hogwarts: Transmigrated as the Top Student* (Hyperbeeam): FanFiction.net, 556 chapters, complete.
- *Naruto: Konoha's Trickster* (PinkSnake/1PinkSnake1): FanFiction.net translation note permits reuse of that translation, not the underlying fanfiction/franchise.
- *Harry Potter: The Flaw of Slytherin* (Ghidorah_7074/Ghidorah1707): FanFiction.net cross-post, 97 chapters, with a note that continuation moved to WebNovel.
- *Harry Potter: The Duelist of Hogwarts* (MeowthTL): FICOOL, 454 chapters.
- *Naruto: Becoming the Soul King* (Junkdog): WuxiaFull, 241 chapters.
- *Naruto Birdcage* (DeCakraWnloverz): FullChapters identifies the Chinese original as 限制级火影 by 易安z.
- *The Most Fortunate Malfoy in Harry Potter* (Devilsatan): NovelFlick mirror.

The three blocked works remain not cleared:
- *Naruto: The Wind Calamity*: DevilHex explicitly requires prospective translators to ask permission first; no grant was found. Keep non-linear FreeWebNovel mapping fail-closed.
- *Konoha's Medical Ninja*: INeedRest says they are not the original writer. Run #44379388243's nine chapter-batch jobs succeeded for 444 chapters and the workflow uploaded final novel artifact #14462633408. The assemble job then failed during registry publication: it opened registry PR #275 and six merge attempts failed after the base branch changed and the PR remained unmergeable. The artifact contents were not fetched or independently verified because rights remain unresolved. public artifact #14462633408 remains rights-unverified.
- *HP: The Arcane Thief*: selected FreeWebNovel edition is 254 numbered chapters plus an auxiliary entry; the 183-chapter FanFiction.net cross-post is separate. PR #463's +1 offset fix remains merged; no archive permission.

The immutable 43-title catalogue remains unchanged. The 65 unmatched Yup/IDK titles remain deferred. No downloads were dispatched. See the full evidence matrix in [round 9](../campaigns/fanfiction/source-verification-round-9-20261122.md).


## Fanfiction source research round 10 (22 November 2026, 09:59 IST)

The full metadata-only report is [campaigns/fanfiction/source-verification-round-10-20261122.md](../campaigns/fanfiction/source-verification-round-10-20261122.md). It searched the 32 unresolved title/author pairs, rechecked the five exact supported-host candidates and two near matches, and investigated the three blocked works. **0 new exact supported-host matches**, **0 explicit lawful archiving permissions**, **0 rights-cleared titles** and **0 new download runs**. The result remains 5 exact supported-host candidates, 2 rejected near/variant matches and 25 without an exact supported-host listing.

The source sweep also checked WuxiaClick and the restricted ScribbleHub route. WuxiaClick produced no exact candidate. ScribbleHub is not a general scraper: its downloader accepts only author-verified cross-post pairs in `tools/scribblehub_verified_crossposts.json`; its sole current record is *The Adventurous Gamer Ninja - Daichi Hekima*, already completed. New identity/edition findings include: *Life of a Villain in The Naruto World* is an English translation credited to IHaveNoNamingSense of a Chinese original by Yun Sixie; *Naruto: Konoha's Trickster* credits 杠精萝卜头 as the Chinese original author and PinkSnake as translator; *Reborn into Naruto World with Tenseigan* is a translation credited to Alex_Clive; *Naruto: Starting With Creating A Genius Persona* has 527 FreeWebNovel versus 487 NovelFlick chapters; *There Will Be No Third Dark Lord At Hogwarts!!!* has inconsistent 363/397/430 public counts and locked Patreon advance posts; and *Harry Potter: Platinum Dragon Wizard* has BlurryPinkSnake/BlurryDream author-credit and 422/424 chapter differences. These are metadata/edition leads, not rights clearance.

Blocked-work decisions remain unchanged: Wind Calamity's author explicitly asks translators to contact them first and its FreeWebNovel map remains fail-closed; Konoha Medical's nine chapter-batch jobs succeeded for 444 chapters and uploaded artifact #14462633408, but the assemble/registry job failed after six attempts to merge PR #275. Artifact contents were not fetched or independently verified, and rights remain unresolved; Arcane Thief's +1 URL-offset fix is merged but rights remain unresolved. Do not retry or publish another archive.

The live check found 343 completed registry records, 70 separately user-confirmed private-HF imports, 90 exclusions, eight completed fanfiction entries, three blocked and 32 research targets. Seven completed fanfiction final artifacts remain public; the Adventurous Gamer Ninja artifact expired. Konoha Medical artifact #14462633408 is also public but unregistered. Seoul Station's Necromancer remains a 209-chapter completion in run #44922285166, artifact #14714778249. Source audit #44924359606 remains read-only: 26 exact listings (18 Yup, 8 IDK; 16 ReadNovelFull, 8 FreeWebNovel, 2 NovelFull), 65 unresolved (36 Yup, 29 IDK), report artifact #14714644436 expiring 21 December 2026. Post-merge main CI #44986296039 passed 4/4 after PR #469. At 10:50 IST, no bulk download workflows were active; PR #470 documentation CI was pending separately. Keep the 65-title Yup/IDK sweep deferred.


## Five-candidate WuxiaClick alternative-source check (22 November 2026, 10:50 IST)

The metadata-only follow-up is documented in [five-book-alternative-source-check-20261122.md](../campaigns/yup-pilot/five-book-alternative-source-check-20261122.md). It found three WuxiaClick leads among the five existing candidates: exact title/author listings for *Godly Student* and *Girl, I'll Teach You Cultivation*, plus the associated-title *Doomsday Lord* for *Doom Lord*. These are additional source URLs for existing candidates, not new titles.

None is eligible: Godly Student has 543 entries numbered 1–544 with the final four reusing original labels 537–540, against the official 17K original listing at Chapter 9,742 on 16 November 2026 (a secondary mirror shows 9,754); Girl, I'll Teach You Cultivation has a clean 1–283 English TOC but the original Chinese edition is 812 chapters and the translation stopped at 283; Doomsday Lord has 328 chapters against a completed original whose official Hongxiu listing ends at Chapter 856 and its TOC contains duplicate/split/misnumbered entries. Beast Piercing The Heavens still has a duplicate Chapter 11 on ReadNovelFull and no WuxiaClick match. The Military Female Soldier still has 2,104 missing ReadNovelFull chapter numbers and no WuxiaClick match. No explicit archiving permissions were found. No download was dispatched.

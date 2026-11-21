# Fanfiction source verification round 3

**Checked:** 22 November 2026, 03:27 IST  
**Repository base:** `72aa1ae839501cd4ea1552deddaa4d6e689bf044`  
**Scope:** all 32 entries still marked `needs_source_verification` in [the immutable 43-title catalogue](webnovel-favourites-43.json): 18 Naruto and 14 Harry Potter. Searches used exact title/credited-author variants across NovelFull, ReadNovelFull and FreeWebNovel. Only public metadata and chapter-index evidence were inspected; no chapter prose was fetched.

## Result

- **5 exact title+credited-author supported-host listings** were located.
- **2 near/variant matches** were rejected as exact matches.
- **25 titles** had no exact supported-host listing in this search pass. This is not a claim that they are unavailable worldwide.
- **0 rights-cleared candidates; 0 new download runs; 0 chapter texts fetched.**

The original title/author identities and source-page references are in [the 32-title identity ledger](source-identity-resolution-20261122.md). The captured screenshot strings in the JSON remain unchanged.

## Five exact supported-host listing candidates

| Catalogue title | Credited/source author | Supported public listing | Evidence and disposition |
|---|---|---|---|
| Naruto: Chronicles of a Fire Ninja | FirstHokage | [FreeWebNovel](https://freewebnovel.com/novel/naruto-chronicles-of-a-fire-ninja) | FWN shows 472 chapters versus 475 on the selected WebNovel listing. Latest FWN labels are non-linear (472→468, 471→466, 470→465, 469→464, 468→463). Hold. |
| Reborn into Naruto World with Tenseigan | Alex_Clive | [FreeWebNovel](https://freewebnovel.com/novel/reborn-into-naruto-world-with-tenseigan) | FWN shows 1,139 chapters versus 967 on WebNovel. Opening labels contain malformed/shifted numbering, including “Chapter 1 - -1”. Hold. |
| Naruto: Starting With Creating A Genius Persona | SweetestDeath | [FreeWebNovel](https://freewebnovel.com/novel/naruto-starting-with-creating-a-genius-persona) | FWN shows 527 chapters versus 534 on WebNovel. The visible opening 40 are sequential, but the complete index and seven-chapter difference remain unexplained. Hold. |
| Harry Potter: The Healer | TheRedSpell | [FreeWebNovel](https://freewebnovel.com/novel/harry-potter-the-healer) | FWN labels it English and shows 349 chapters versus 344 on WebNovel. Its raw title is Russian (Целитель); translation/edition provenance and the complete index are not verified. Hold. |
| There Will Be No Third Dark Lord At Hogwarts!!! | mrfanfiction140 | [FreeWebNovel](https://freewebnovel.com/novel/there-will-be-no-third-dark-lord-at-hogwarts) | FWN shows 430 chapters versus 397 on WebNovel and advertises 30+ Patreon advance chapters. Do not fetch or archive paid/advance chapters. Hold. |

A public listing, English-language label, translator credit or complete-looking first page is not permission to archive the work. None of these five has documented rights clearance.

## Near/variant matches rejected as exact

- **Talent System In The Naruto Universe:** the surfaced source credits author `Rashta`, while the catalogue records `Rashita`. Do not silently equate the names.
- **Naruto: This Ninja is Obviously Not Strong But Really Hard to Kill:** the selected WebNovel listing credits `nyawdao2` (564 chapters); the similar FreeWebNovel listing credits original author `Wu Mian Qi Liang` (547 chapters). This may be the same underlying translated work, but it is not the same credited-author/edition record. Do not substitute it.
- **Naruto: Konoha's Trickster, Starting as the Seven-Tails Jinchuriki:** the translator's WebNovel note permits reuse of that translation, but the underlying Chinese work is credited to a different original author. Translator permission alone does not establish rights to the underlying work or a public archive.

## The three previously blocked fanfiction sources

| Work | Current evidence | Safe state |
|---|---|---|
| Naruto: The Wind Calamity | FreeWebNovel's chapter labels and URL numbering are non-linear; the source adapter now fails closed rather than guessing chapter mappings. | No retry until a complete one-to-one source map and rights clearance exist. |
| Konoha's Medical Ninja: One Punch to beat up Madara | A 444-chapter archive was technically assembled and validated, but it is not registered; metadata-only PR #275 remains open. The existing GitHub Actions archive artifact `14462633408` (expires `2027-02-16T19:20:05Z`) is public and rights are unresolved. | Do not merge PR #275, re-download, link or create another public archive without permission. |
| HP: The Arcane Thief | 254-chapter source index has a consistent +1 URL offset. PR #463 merged the narrow fix and regression test at `72aa1ae839501cd4ea1552deddaa4d6e689bf044`. | No targeted retry until rights are verified. |

## Completed fanfiction registry and artifact reconciliation

The canonical registry still contains **8 completed fanfiction entries**. Seven artifacts are currently present; *The Adventurous Gamer Ninja - Daichi Hekima*'s artifact expired on 21 November 2026 and is no longer listed by the Actions API. Do not count artifact availability as private-HF import.

| Completed work | Chapters | Run | Artifact | Current artifact state |
|---|---:|---:|---:|---|
| The Adventurous Gamer Ninja - Daichi Hekima | 432 | [#43589834773](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/43589834773) | 14111234860 | Expired 2026-11-21T11:24:36Z |
| A New Snake In The Shinobi World | 423 | [#44378479201](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44378479201) | 14464695010 | Present; API expiry 2027-02-16T19:14:59Z |
| Naruto: I am Uchiha Shirou | 448 | [#44378935249](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44378935249) | 14463647756 | Present; API expiry 2027-02-16T19:17:32Z |
| Naruto: Kurotsuchi Mayuri | 524 | [#44378935249](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44378935249) | 14463808054 | Present; API expiry 2027-02-16T19:17:32Z |
| HP: A Magical Journey | 439 | [#44381959077](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44381959077) | 14465975343 | Present; API expiry 2027-02-16T19:35:15Z |
| Hogwarts: I'm Truly a Model Wizard | 1,004 | [#44381959077](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44381959077) | 14464369346 | Present; API expiry 2027-02-16T19:35:15Z |
| Hogwarts' John Wick | 703 | [#44389807742](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44389807742) | 14469106672 | Present; API expiry 2027-02-16T20:19:28Z |
| The Fool in Hogwarts | 333 | [#44389807742](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44389807742) | 14469501148 | Present; API expiry 2027-02-16T20:19:28Z |

Run #44378479201 has an overall failure because the *Wind Calamity* batches failed. The *A New Snake* chapter batches 1–423 succeeded and its own archive artifact exists; do not mark that novel failed solely from the parent run conclusion. The other six successful archives have successful chapter-batch/assembly jobs. The expired *Adventurous Gamer Ninja* archive cannot be re-inspected now.

The registry's artifact expiry fields for the seven present fanfiction artifacts have been corrected from the live Actions API in the accompanying documentation branch. Seoul Station's Necromancer's registry expiry was also corrected to its live API expiry. No archive contents were downloaded or re-distributed during this review.

## Next action

Continue source research on the 25 unresolved exact identities, then review any new exact supported listings for author, edition, English language, complete chapter index and explicit archiving permission. Do not dispatch a fanfiction batch unless all five checks pass. Keep fanfiction counts separate from Yup/IDK and from the user's 70 separately confirmed private-HF imports.

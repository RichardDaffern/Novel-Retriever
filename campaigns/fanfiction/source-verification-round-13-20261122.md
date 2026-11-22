# Fanfiction source research, round 13

**Checked:** 22 November 2026, 11:56 IST  
**Scope:** Ten unresolved rows from the immutable 43-title catalogue, plus a fresh exact-log check of the three blocked works.  
**Method:** Exact title/selected-credit web searches, public catalogue and author-note checks, and targeted NovelFull, ReadNovelFull and FreeWebNovel queries. Only public metadata, chapter counts, author/translator notes and index labels were inspected. No screenshots, chapter prose or archive bytes were fetched.

## Result

- **10 catalogue rows reviewed.**
- **0 exact NovelFull, ReadNovelFull or FreeWebNovel listings surfaced.**
- **0 explicit lawful archiving permissions, 0 rights-cleared titles and 0 new download runs.**
- Public mirrors and WebNovel pages are identity/edition evidence only. They do not grant archive or redistribution rights.
- The immutable catalogue remains 24 Naruto + 19 Harry Potter. The overall reconciliation remains 8 complete, 3 blocked and 32 requiring research.
- Search absence is not proof of worldwide unavailability. Do not alter the original JSON or substitute a translator, title collision or different edition.

## Ten title and author checks

| Selected title | Catalogue credit | Evidence and acquisition decision |
|---|---|---|
| *Naruto: Uchiha's Genjutsu Demon* | lazarus898 | WebNovel catalogue shows 401 chapters. [Catalogue](https://www.webnovel.com/book/23143172205134805/catalog). No exact supported-host listing or archive permission found. |
| *Naruto: My Unique System* | Cloe23 | WebNovel listing shows 304 chapters. [Listing](https://www.webnovel.com/book/naruto-my-unique-system_28572579600144305). No exact supported-host listing or archive permission found. |
| *Naruto: The Hyuga Mastermind* | NahinS77 | WebNovel catalogue shows 380 entries, with the final entry labelled Chapter 381 (final chapter). [Catalogue](https://www.webnovel.com/book/31282473100386105/catalog). Index discrepancy; no supported-host listing or archive permission. |
| *Naruto: Becoming the Soul King* | Junkdog | WebNovel shows 423–424 entries and a final chapter labelled Chapter 426. WuxiaFull shows 241 and ongoing; NovelFlick shows another count. [WebNovel](https://www.webnovel.com/book/34681130400701205), [WuxiaFull](https://www.wuxiafull.com/Naruto-Becoming-the-Soul-King/), [NovelFlick](https://www.novelflick.com/story/34681130400701205). Unsupported mirrors and index/edition drift; no archive permission. |
| *Naruto: Konoha's Genius is a bit Ordinary* | SaintXI | WebNovel shows 472 chapters and explicitly labels the page a translation while stating the credited author does not own Naruto rights. [Listing](https://www.webnovel.com/book/30359049406191005), [author's translation guide](https://www.patreon.com/SaintXI/posts/guide-for-novels-110650000). Not a supported source or archive licence; Patreon advance access is not permission. |
| *Hogwarts: The Unscientific Wizard* | Crazy_DarkSide_Cat | WebNovel chapter page identifies the selected author credit and directs readers to Patreon for advance chapters. [Chapter page](https://www.webnovel.com/ru/book/29448924500256905/81753904236261761). No exact supported-host listing or archive permission found. |
| *Succubus System At Hogwarts* | Dragonel23 | WebNovel shows 73 chapters and labels the page a translation of the MTL title *Hogwarts: I am the savior, and I am breaking up couples*. Patreon advertises 12 advance chapters. [Listing](https://www.webnovel.com/book/31142522908061905/catalog), [Patreon](https://www.patreon.com/cw/Dragonel/membership). Original author unresolved; no supported source or archive permission. |
| *Harry Potter: The Bard of Hogwarts* | Dark_Peace | WebNovel shows 431 chapters. A separate same-title FanFiction.net work by Vindicare40k has 12 chapters, was updated in 2020 and disclaims ownership of D&D and Harry Potter. [WebNovel](https://www.webnovel.com/book/29905212700204005/catalog), [FanFiction.net](https://www.fanfiction.net/s/12246515/1/The-Bard-of-Hogwarts). Title collision, not a verified cross-post; do not substitute the 12-chapter work. |
| *Hogwarts: I Started as the Fool* | ulquiorra_cifer_1152 | English WebNovel snapshot shows 178 chapters; Thai snapshot shows 222 for the same title/author. [English listing](https://www.webnovel.com/book/hogwarts-i-started-as-the-fool_36540569508783705), [Thai listing](https://www.webnovel.com/th/book/hogwarts-i-started-as-the-fool_36540569508783705). Edition/count drift; no exact supported-host listing or archive permission. |
| *The Most Fortunate Malfoy in Harry Potter* | Devilsatan | CHERREADS shows 193 chapters; the earlier WebNovel snapshot showed 206. The mirror note says the author owns only the original character, not the Harry Potter material. [CHERREADS](https://ellatoria.com/story/34592692808708405). Edition drift and no archive permission. |

## Three blocked works: exact run/job evidence

### Naruto: The Wind Calamity

Run [#44378479201](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44378479201), job 135064355812, stopped with:

"Expected Chapter 51, but the page identifies Chapter 48".

The same run separately completed *A New Snake In The Shinobi World* at 423 chapters; that result is not Wind Calamity completion. PR #463's fail-closed mapping remains in place. No retry without a complete one-to-one map and author permission.

### Konoha's Medical Ninja: One Punch to beat up Madara

All nine chapter-batch jobs in run [#44379388243](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44379388243) succeeded for 444 chapters. Artifact 14462633408 remains public (3.37 MB; expiry 16 February 2027). Assemble job 135075510958 failed after six registry-merge attempts: attempt 1 reported that the base branch had changed; attempts 2–6 reported that the PR was not mergeable. [PR #275](https://github.com/RichardDaffern/Novel-Retriever/pull/275) remains open.

This is a registry-publication failure, not a chapter-integrity failure. Do not merge, re-download or republish while original-author and archive rights remain unresolved.

### HP: The Arcane Thief

The old run [#44379388243](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44379388243) predates PR #463. Its first batch job 135067617503 stopped because it expected Chapter 2 while the page identified Chapter 1. PR #463 added the +1 URL-offset fix and regression coverage. No post-fix full TOC validation or new download was performed; rights remain unresolved. Do not retry until the complete selected edition and lawful rights are verified.

## Rights and artefact safeguards

Seven completed fanfiction archives and Konoha Medical's artifact remain publicly accessible without documented redistribution permission. The connected GitHub operations do not expose artifact revocation; repository-owner action is required if permission cannot be established. Do not download, link, recreate or extend public copies.

## Reconciled state and next step

| Category | Count |
|---|---:|
| Completed registry | 343 |
| User-confirmed private-HF imports | 70 |
| Red/Dropped exclusions | 90 |
| Fanfiction complete | 8 |
| Fanfiction blocked | 3 |
| Fanfiction research targets | 32 |

No new download run was dispatched. The 65 unmatched Yup/IDK titles remain deferred until the fanfiction research and blocked-source investigations are complete. Remote API inspection only; local working-tree status is not observable.

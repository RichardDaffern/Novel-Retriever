# IDK alternative-source research round 1

**Checked:** 22 November 2026, 17:53 IST  
**Input:** all 29 IDK rows in `source-audit-results.json` from read-only run [#44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606), artifact [14714644436](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606/artifacts/14714644436).  
**Method:** exact-title and known-alias public metadata searches across NovelFull, ReadNovelFull, FreeWebNovel and alternative catalogues, publisher pages and source indexes. No chapter prose, screenshots, locked material or archive bytes were fetched.

## Reconciliation

- All **29/29 IDK audit rows** are present in `campaigns/overnight/idk-82.json`.
- The 29 rows contain **one completed-registry alias**: *Xian Ni* = *Renegade Immortal*. It is already represented in the 343-record `downloaded_novels.json`; do not download it again.
- *A Thought Through Eternity* = *A Will Eternal* is another alias in the 82-entry IDK campaign manifest, but it is **not** one of the 29 unresolved audit rows and is already registered.
- The completed registry remains **343**; the **70** user-confirmed private-HF imports are separate; all **90** red/Dropped exclusions remain excluded. None of the other 28 distinct IDK rows matches the registry or exclusion list.
- The four 404 URL patterns in the audit are not evidence of worldwide unavailability.

## Supported-source findings

### Exact NovelFull / FreeWebNovel match

*Attack Of The Adorable Kid: President Daddy's Infinite Pampering* has an exact public listing on both [NovelFull](https://novelfull.com/attack-of-the-adorable-kid-president-daddys-infinite-pampering.html) and [FreeWebNovel](https://freewebnovel.com/novel/attack-of-the-adorable-kid-president-daddys-infinite-pampering). Both identify **Sweets Flood**; FreeWebNovel also shows the Chinese title 报告！爹地又追来了 and the author credit 糖果淼淼. The pages report a completed **2,612-chapter** WebNovel edition, with Chapter 1 at the start and Chapter 2612 as the finale. The full paginated TOC has not been independently checked end-to-end. No explicit permission to archive or redistribute was found. **Source lead only, not download clearance.**

No exact ReadNovelFull listing surfaced for the other IDK rows.

### WuxiaClick metadata leads

Eight title pages surfaced on WuxiaClick, which is a constrained source path in this repository, not a full-book export route:

- *For Some Reason, the School Goddess Likes to Hang Out at My House*: credited to 紫ユウ; 166 original chapters versus a 155-chapter listing.
- *How To Melt the Ice Lady*: Takamine Kakeru; 101 original web-novel chapters versus 98 listed.
- *Juvenile Medical God*: Zhu Mei; 4,144 original chapters versus a 126-chapter WuxiaClick listing; FanMTL shows 4,146.
- *My Plain-looking Fiance is Secretly Sweet with Me*: Yuu Hidaka; 56 web-novel chapters and one light-novel volume versus 46 listed.
- *The Gloomy Me in Class is Actually the Vocalist of a Very Popular Band*: Yozakura Yuno; 111 original web-novel chapters versus 75 listed.
- *The Nine Godheads*: Chen Ji Tang Hong Dou; FanMTL shows 556, WuxiaClick 85 and Asura 12.
- *The Reincarnated Cop Who Strikes With Wealth*: Baeppu; 196 listed chapters, ongoing. This is a novel listing; separate manhwa adaptations also exist.
- *The Entertainment Circle is Mine*: Chun Dao Han; 172 original chapters plus three extras, completed, versus 101 on WuxiaClick.

WuxiaClick remains limited to bounded 20-chapter jobs and has no full-book export. None of these listings carries explicit archive permission, and the count differences above are not safe to normalise automatically.

## Full 29-title identity and edition matrix

| Audit title | Public identity / edition evidence | Decision |
|---|---|---|
| *An Eye for News* | Author 星术师; [FullNovels](https://fullnovels.com/an-eye-for-news/) records 776 complete original chapters but marks the English translation incomplete; FanMTL/WuxiaP snapshots end at 751. | Translation is incomplete; no rights. |
| *Attack Of The Adorable Kid: President Daddy's Infinite Pampering* | Sweets Flood / 糖果淼淼; [NovelFull](https://novelfull.com/attack-of-the-adorable-kid-president-daddys-infinite-pampering.html) and [FreeWebNovel](https://freewebnovel.com/novel/attack-of-the-adorable-kid-president-daddys-infinite-pampering) report 2,612 completed chapters. | Exact supported-host lead; full paginated TOC and archive permission still missing. |
| *Beautiful Time With You* | Ye Fei Ye; [WebNovel](https://www.webnovel.com/book/11479410005401305) lists 1,129 completed chapters. | Commercial platform listing; no archive permission. |
| *For Some Reason, the School Goddess Likes to Hang Out at My House* | Author 紫ユウ; [WuxiaCity](https://wuxia.city/book/for-some-reason-the-school-goddess-likes-to-hang-out-at-my-house) / [WuxiaBox](https://www.wuxiabox.com/novel/for-some-reason-the-school-goddess-likes-to-hang-out-at-my-house.html) show 166; WuxiaClick shows 155. | Edition/index mismatch. |
| *Genius Profiler Hansol Im* | Author 수박주스; [NovelUpdates](https://www.novelupdates.com/series/genius-profiler-hansol-im/) records 203 completed Korean chapters and an incomplete English translation. | No complete English index. |
| *HacKer* | The search surfaced a different-looking *Hacker - HEIKE* entry with 38 chapters credited to CHNovelTrans, but no reliable exact-title/author link to this campaign row. | Identity remains ambiguous; do not alias it. |
| *How To Melt the Ice Lady* | Takamine Kakeru; [WuxiaClick](https://wuxia.click/novel/how-to-melt-the-ice-lady) lists 98 against 101 original web-novel chapters. | Incomplete/mismatched index. |
| *I Know Everything* | Jun Xiu Cai; [FanMTL](https://www.fanmtl.com/novel/i-know-everything.html) / WTR-LAB show 1,302; WuxiaWorldEU snapshots show 662–664. | Material edition/count mismatch. |
| *Invisible Dragon* | Duichidak; [Armaell's Library](https://armaell-library.net/novel/invisible-dragon) lists a completed 50-chapter English translation of the Korean work. | Alternative translation lead; no archive permission. |
| *I’m Gonna Live with You Not Because My Parents Left Me Their Debt But Because I Like You* | Original author Amane Megumi; [KADOKAWA](https://www.kadokawa.co.jp/product/322008000692/) identifies the published light-novel work. Several 51-chapter results are manga adaptations, not the novel TOC. | Keep novel and manga editions separate; published/licensed work, no archive permission. |
| *Juvenile Medical God* | Zhu Mei; original 4,144 chapters; WuxiaClick lists 126, while FanMTL lists 4,146. | Severe source/index mismatch. |
| *Konjiki no Wordmaster* | Also *Konjiki no Moji Tsukai*; author Tomoto Sui; [NovelUpdates](https://www.novelupdates.com/series/konjiki-no-moji-tsukai/) records 14 volumes, 691 chapters plus 103 extra chapters, complete. | Japanese original and translation metadata found; no archive permission. |
| *Legend of Mythological Genes* | Fish Leaping to the Peak; [WebNovel](https://www.webnovel.com/book/13071505405554605) lists 520 completed chapters; FullNovels' country-of-origin snapshot shows 486. | Edition/count discrepancy; no archive permission. |
| *Level Up Doctor Choi Kiseok* | Original Korean novel by Yun Baek-hyun; [Novel Translator](https://noveltranslator.com/library/level-up-doctor-choi-kiseok-13650) records 404 chapters and a completed published work. The manhwa adaptation has 111 chapters; WuxiaWorldEU has only seven. | No complete English novel source; do not mistake manhwa chapters for novel chapters. |
| *My Plain-looking Fiance is Secretly Sweet with Me* | Yuu Hidaka; 56 web-novel chapters / one light-novel volume; [WuxiaClick](https://wuxia.click/novel-detail/my-plain-looking-fiance-is-secretly-sweet-with-me) lists 46. | Incomplete/mismatched index. |
| *Rebound: A 2nd Chance* | The_Gaji; [WuxiaWorldEU](https://wuxiaworld.eu/novel/rebound-a-2nd-chance) and [NovelFire](https://novelfire.net/book/rebound-a-2nd-chance/chapters) show 323 numbered chapters through 324, with Chapter 69 unavailable. | English original, but index has a gap and is ongoing; no archive permission. |
| *Shen Mu* | Also *Divine Grave*; Chen Dong; [WuxiaSpot](https://www.wuxiaspot.com/novel/shen-mu-divine-grave.html) and FanMTL show 774 completed chapters; a WuxiaDreams snapshot showed 760. | Alternative listing with count drift; no archive permission. |
| *Soudana, Tashika ni Kawaii Na* | Karino Mikata; [CompleteNovel](https://completenovel.com/soudana-tashika-ni-kawaii-na/) records one Japanese light-novel volume, ongoing, with a completed translation listing. | No archive permission. |
| *Starting Over* | Generic title returns several unrelated works and no exact author/edition match to this campaign row. | Identity remains ambiguous; do not guess. |
| *Super Doctor* | Ye Tian Nan; original 1,215 chapters; FanMTL lists 1,126. | Incomplete translation/index. |
| *Tensei Shitara Slime Datta Ken* | Fuse; [Yen Press](https://yenpress.com/titles/9780316414203-that-time-i-got-reincarnated-as-a-slime-vol-1-light-novel) confirms the licensed English light-novel series. | Commercially licensed edition; no archive permission. |
| *The Entertainment Circle is Mine* | Chun Dao Han; [NovelUpdates](https://www.novelupdates.com/series/the-entertainment-circle-is-mine/) records 172 chapters plus three extras, complete; FullNovels says fully translated, WuxiaClick lists 101. | Incomplete/mismatched WuxiaClick index; no archive permission. |
| *The Gloomy Me in Class is Actually the Vocalist of a Very Popular Band* | Yozakura Yuno; [NovelUpdates](https://www.novelupdates.com/series/the-gloomy-me-in-class-is-actually-the-vocalist-of-a-very-popular-band/) records 111 ongoing original chapters; WuxiaClick lists 75. | Incomplete translation/index. |
| *The Nine Godheads* | Chen Ji Tang Hong Dou; FanMTL 556, WuxiaClick 85, Asura 12. | Material edition/index mismatch. |
| *The Reincarnated Cop Who Strikes With Wealth* | Baeppu; [WuxiaClick](https://wuxia.click/novel/the-reincarnated-cop-who-strikes-with-wealth) lists 196 ongoing novel chapters. | Exact alternate novel listing, but no archive permission or complete edition verification. |
| *Those Years When I Opened a Chinese Medicine Shop* | [NovelUpdates' Chinese catalogue](https://www.novelupdates.com/language/chinese/?order=1&pg=633&sort=6&status=4) lists 28 chapters; author identity was not exposed in the reviewed listing. | Incomplete and author unresolved. |
| *Warrior's Promise* | Baili Longxia; [WebNovel](https://www.webnovel.com/book/9087070605001805/catalog) lists 3,336 chapters; Qidian metadata snapshots differ materially. | Source/edition count conflict; no archive permission. |
| *Xian Ni* | Alias of *Renegade Immortal*, already complete in the registry. | Skip as duplicate. |
| *Yondome Wa Iyana Shi Zokusei Majutsushi* | Densuke; [NovelCodex](https://www.novelcodex.com/novel/008q/the-death-mage-who-doesnt-want-a-fourth-time/reviews) records the English title *The Death Mage Who Doesn't Want a Fourth Time*. The Japanese web novel completed at 513 chapters; the English light novel is commercially licensed by One Peace Books. | Separate web-novel/light-novel editions; no archive permission. |

## Decision and next gate

- **One exact NovelFull/FreeWebNovel source lead** was found: *Attack Of The Adorable Kid*. Its page-level 2,612 count is not yet a fully validated paginated TOC.
- **Eight WuxiaClick metadata listings** were found; several have significant chapter-count differences. The repository's WuxiaClick route is bounded and must not be treated as a full-book exporter.
- **26 rows** produced identifiable title/edition metadata; *HacKer* and *Starting Over* remain ambiguous; *Xian Ni* is a completed-registry alias.
- **0 explicit archiving permissions, 0 rights-cleared titles and 0 new download runs.**
- No chapter text was fetched. No download or retry was dispatched. Do not retry deterministic #371/#452 failures unchanged or publish an unlicensed archive.

The source-research stage for the 65 unmatched rows is now complete for the current search scope: the 36-row Yup sweep is documented in [the existing alternative-source report](alternative-source-research-20261122.md), and this report covers all 29 IDK rows. This does **not** mean the 65 are unavailable worldwide. The next gate is documented author/publisher permission plus complete edition-index validation; only then may a reviewed, non-public, resumable batch be considered.

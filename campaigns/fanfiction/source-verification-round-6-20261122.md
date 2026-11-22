# Fanfiction supported-host rescan, round 6

**Checked:** 22 November 2026, 06:17 IST  
**Scope:** The immutable 43-title catalogue, with priority on the 32 source-research entries and the three separately blocked works.  
**Method:** 30 exact title+credited-author searches and 26 title-only searches restricted to NovelFull, ReadNovelFull and FreeWebNovel. Existing identity-ledger and round 1–5 evidence was used to avoid changing the original catalogue. Metadata/search results only; no chapter prose was fetched.

## Result

- **0 additional exact supported-host listings** beyond the five already recorded in round 3.
- The two near/variant matches remain rejected as exact: *Talent System In The Naruto Universe* (Rashta vs selected author Rashita) and *Naruto: This Ninja is Obviously Not Strong But Really Hard to Kill* (the supported-host credit differs from selected author nyawdao2).
- The existing five exact listings and 25 no-exact-listing results are unchanged.
- **0 explicit archiving permissions**, **0 new download runs**, **0 chapter prose fetched**, and no registry change.
- The original 43-title JSON is unchanged. No screenshots were requested.

## Refreshed listing and edition evidence

| Selected work | Public evidence | Acquisition decision |
|---|---|---|
| Naruto: Chronicles of a Fire Ninja | [FreeWebNovel listing](https://freewebnovel.com/novel/naruto-chronicles-of-a-fire-ninja) credits FirstHokage, labels it an English ongoing fanfic and shows 472 chapters. Latest entries have mixed displayed labels (for example, chapter 472 is labelled 468). | Existing exact candidate only. Preserve displayed chapter identities; no explicit archive permission. |
| Reborn into Naruto World with Tenseigan | [FreeWebNovel listing](https://freewebnovel.com/novel/reborn-into-naruto-world-with-tenseigan) credits Alex_Clive and shows 1,139 chapters; the selected WebNovel edition was previously recorded at 967. The visible FWN opening labels include malformed negative/duplicated numbering. | Material edition/index discrepancy. No retry or slug substitution. |
| Harry Potter: The Healer | [FreeWebNovel chapter 350](https://freewebnovel.com/novel/harry-potter-the-healer/chapter-350) is publicly indexed. The original Russian work [Целитель](https://author.today/work/410949) is by Gezenshaft; WebNovel credits TheRedSpell and labels it a translation. Public mirror snapshots range from 206 to 350 chapters (PYG-KIT 206, WebNovel 275–330, NovelBuddy 340, FWN 350). | Original author now identified as Gezenshaft; English translation/edition and chapter list are not reconciled, and no translation/archive permission was found. |
| There Will Be No Third Dark Lord At Hogwarts!!! | [FreeWebNovel chapter 430](https://freewebnovel.com/novel/there-will-be-no-third-dark-lord-at-hogwarts/chapter-430) is indexed. Other FWN category snapshots returned 381–416 chapters, while the WebNovel listing showed 363. | Exact title/credit candidate, but mirror counts are inconsistent. Do not infer a complete edition from a chapter URL. |

The title-only rescan also reconfirmed that *Naruto: My Unique System* (Cloe23, 304 chapters), *Hogwarts: Bloodline Wizard* (Innocent Angel, 1,049 chapters) and *Harry Potter: Cael Vale's Journey to Hogwarts* (16622800, 294 chapters) have public WebNovel metadata but no newly found exact listing on the three supported downloader hosts. WebNovel/alternate catalogues are identity evidence only, not supported acquisition adapters or permission.

## Author-permission checks

- **FirstHokage / Naruto: Chronicles of a Fire Ninja:** the author’s [Royal Road post](https://www.royalroad.com/fiction/90875/naruto-chronicles-of-a-fire-ninja/chapter/1859197/100-chapters-completed-yayyy) says an Amazon use of the narrative was unauthorised and asks readers to report sightings. This is not archive permission; it is an explicit warning against unauthorised reuse. The post also describes WebNovel/Patreon chapter history, so the 472-entry FWN index is not automatically the same edition.
- **Devil_Hex / Naruto: The Wind Calamity:** the [FanFiction.net author page](https://www.fanfiction.net/s/14178557/1/Naruto-The-Wind-Calamity) says anyone wishing to translate the fanfic must first ask permission. This is a permission requirement, not a grant. The page lists 455 chapters, versus NovelTrust 793, NovelLunar 910 and FreeWebNovel 951; no matching edition/map is established.
- **Gezenshaft / Harry Potter: The Healer:** the original Russian-language fanfic *Целитель* is credited to Gezenshaft on [Author.Today](https://author.today/work/410949). WebNovel credits TheRedSpell and describes the English work as a translation. No explicit translation or archive permission from Gezenshaft was found.
- **SweetestDeath / Naruto: Starting With Creating A Genius Persona:** public Patreon chapter pages exist, but they do not grant permission to archive or republish the work.
- **mrfanfiction140 / There Will Be No Third Dark Lord At Hogwarts!!!:** the author advertises 30+ advance chapters and Patreon chapter posts are locked. Subscription access is not archive permission.
- **Konoha's Medical Ninja:** the credited editor explicitly states they are not the original writer. The original author remains unidentified.
- Searches for explicit archiving/reposting permission from Alex_Clive, TheRedSpell, Snollygoster and Devil_Hex found no permission statement. No selected work has documented permission for this use.

## Three blocked fanfiction sources

- **Naruto: The Wind Calamity:** the selected author is Devil_Hex. Public metadata now gives four different counts: FanFiction.net 455, NovelTrust 793, NovelLunar 910 and FreeWebNovel 951 (the latter includes auxiliary sections). The FanFiction.net author asks translators to obtain permission first. FreeWebNovel's chapter URL mapping is non-linear. PR #463 correctly fails closed; no complete one-to-one map or archiving permission was found.
- **Konoha's Medical Ninja: One Punch to beat up Madara:** the 444-chapter archive is technically assembled, but the credited editor says they are not the original writer and the underlying author remains unidentified. Existing public artifact `14462633408` is still rights-unverified; do not link, re-download or create another copy.
- **HP: The Arcane Thief:** PR #463 merged the +1 URL-offset handling and regression tests. The 254-entry FreeWebNovel index still differs from the 183-chapter FanFiction.net listing. The offset fix does not resolve edition identity or rights; no retry.

## Decision

No title passes all gates for exact selected work/author, English edition, complete ordered index and explicit lawful archiving permission. Keep the 32 research targets and three blocked titles separate from the 65 Yup/IDK rows. Continue fanfiction identity/edition work; do not start another download or revisit the later Yup/IDK sweep yet.

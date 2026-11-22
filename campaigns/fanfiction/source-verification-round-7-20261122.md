# Fanfiction source research, round 7

**Checked:** 22 November 2026, 06:39 IST  
**Scope:** All 32 entries still marked `needs_source_verification` in the immutable 43-title catalogue, plus the three separately blocked works.  
**Method:** 32 exact title + selected-credit searches using the strings and author credits recorded in `campaigns/fanfiction/webnovel-favourites-43.json` (truncated titles were searched as recorded), followed by domain-restricted checks across NovelFull, ReadNovelFull and FreeWebNovel. Additional catalogue checks were used only to resolve title, translator, original-author and edition identity. Metadata/index evidence only; no chapter prose was fetched.

## Result

- **0 additional exact title + selected-author matches** surfaced on the three supported downloader hosts.
- The existing **5 exact supported-host candidates**, **2 rejected near/variant matches** and **25 without an exact supported-host listing** remain unchanged from round 6. The five exact candidates are still among the 32 `needs_source_verification` entries: a public listing is not yet an approved source until edition, full index and permission checks pass.
- The FreeWebNovel result for *This Ninja Is Obviously Not Strong but Really Hard to Kill* still credits original author Wu Mian Qi Liang, not selected WebNovel credit nyawdao2. It remains a rejected author mismatch, not a new exact match.
- Several exact WebNovel/alternate-catalogue identity records were found or reconfirmed, but those sites are not supported downloader adapters and do not establish permission.
- **0 explicit archiving permissions**, **0 rights-cleared titles**, **0 new download runs**, **0 chapter prose fetched**, and no registry change.
- The original 43-title JSON and its title/author credits were not changed. No screenshots were requested.

Search absence is not proof that a work is unavailable worldwide. It only means this pass did not surface a new exact listing on the three supported hosts.

## Fanfiction registry reconciliation

The immutable catalogue's `review_state` is its initial campaign/source-review state, not live source discovery or download completion. Its counts are 1 `already_downloaded`, 10 `public_source_listing_matched` and 32 `needs_source_verification`. Of those 10 initial source-matched rows, seven are already complete in `downloaded_novels.json` and three remain blocked. The five exact supported-host candidates discovered in later research are still within the 32 `needs_source_verification` rows because edition, full-index or permission gates remain open. Together with the first row, the registry reconciles to **8 complete, 3 blocked and 32 requiring research**. The registry is the source of truth for completion:

| Completed fanfiction | Chapters | Run | Final archive artifact | Artifact state at check |
|---|---:|---:|---:|---|
| The Adventurous Gamer Ninja - Daichi Hekima | 432 | [#43589834773](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/43589834773) | `14111234860` | Expired 21 November 2026; no longer returned by the run artefact API |
| A New Snake In The Shinobi World | 423 | [#44378479201](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44378479201) | `14464695010` | Present; expires 16 February 2027 19:14:59 UTC |
| Naruto: I am Uchiha Shirou | 448 | [#44378935249](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44378935249) | `14463647756` | Present; expires 16 February 2027 19:17:32 UTC |
| Naruto: Kurotsuchi Mayuri | 524 | [#44378935249](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44378935249) | `14463808054` | Present; expires 16 February 2027 19:17:32 UTC |
| HP: A Magical Journey | 439 | [#44381959077](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44381959077) | `14465975343` | Present; expires 16 February 2027 19:35:15 UTC |
| Hogwarts: I'm Truly a Model Wizard | 1,004 | [#44381959077](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44381959077) | `14464369346` | Present; expires 16 February 2027 19:35:15 UTC |
| Hogwarts' John Wick | 703 | [#44389807742](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44389807742) | `14469106672` | Present; expires 16 February 2027 20:19:28 UTC |
| The Fool in Hogwarts | 333 | [#44389807742](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44389807742) | `14469501148` | Present; expires 16 February 2027 20:19:28 UTC |

The seven present fanfiction archives remain publicly accessible and rights-unverified. Do not link, download, or create additional public copies. The expired artifact is historical. The user's **70 private-HF imports** remain a separate user-confirmed count and were not changed or re-queried in this run.

## Additional title and edition evidence

| Selected work | Public metadata evidence | Acquisition decision |
|---|---|---|
| Naruto: Transmigrated as an Uchiha — NoviceAuthor | [WebNovel](https://www.webnovel.com/book/28980126008082405/catalog) credits NoviceAuthor and exposes a 327-chapter catalogue. | Exact selected-title/credit metadata, but WebNovel is not a supported downloader host. No archive permission. |
| Life of a Villain in The Naruto World — IHaveNoNamingSense | [WebNovel](https://www.webnovel.com/book/29731253808160705) shows 264 chapters, identifies IHaveNoNamingSense as the English translator and names Yun Sixie as the original author. | Translation/original-author distinction recorded. No supported-host source or permission. |
| Naruto: Konoha's Trickster, Starting as the Seven-Tails Jinchūriki — PinkSnake | [WebNovel](https://www.webnovel.com/book/naruto-konoha%E2%80%99s-trickster-starting-as-the-seven-tails-jinch%C5%ABriki_31772439608943805) credits PinkSnake, shows 815 chapters and identifies a Chinese original author. A [FanFiction.net translation page](https://www.fanfiction.net/s/14439428/627/Naruto-Konoha-s-Trickster-Starting-as-the-Seven-Tails-Jinch%C5%ABriki) credits 1PinkSnake1 and contains a translator note saying that translation may be reused. | Cross-post/translation relationship is plausible, but no supported-host archive source was found. The translator's statement does not establish rights to the underlying fanfiction or franchise; not treated as archive clearance. |
| Naruto: Konoha's Genius is a bit Ordinary? — SaintXI | [WebNovel catalogue](https://www.webnovel.com/book/30359049406191005/catalog) credits SaintXI and shows 472 chapters. | Exact catalogue identity, unsupported host, no permission. |
| Naruto: Kurotsuchi Mayuri — PirateKing24 | [WebNovel](https://www.webnovel.com/book/naruto-kurotsuchi-mayuri_30573955808139405) shows 490 chapters and describes it as a translation of a Chinese work. The completed registry already contains this title at 524 chapters. | Registry collision: do not treat the 490-chapter listing as a new target or re-download. The edition mismatch is not resolved by the new listing. |
| Naruto: Starting With Creating A Genius Persona — SweetestDeath | [WebNovel](https://www.webnovel.com/book/naruto-starting-with-creating-a-genius-persona_35431344400865305) shows 534 chapters; [Ellatoria](https://ellatoria.com/story/35431344400865305) shows 487 and Patreon exposes chapter-post metadata. | Counts differ by mirror; Patreon access is not archive permission. The existing FreeWebNovel candidate remains subject to the earlier edition/index checks. |
| Harry Potter: Cael Vale's Journey to Hogwarts — 16622800 | [WebNovel](https://www.webnovel.com/book/33033577108188605) credits 16622800 and shows 294 chapters; [FICOOL](https://www.ficool.com/story/33033577108188605/89144520263922447) has a chapter excerpt. | Identity metadata only; neither is a supported downloader host or permission. |
| Harry Potter: I, Tom Riddle, am not the Dark Lord — ElvenKing20 | [Author's Patreon post](https://www.patreon.com/ElvenKing20/posts/harry-potter-i-136128687) confirms the selected title and author. | Patreon page/access is not archive permission; no supported-host listing surfaced. |
| There Will Be No Third Dark Lord At Hogwarts!!! — mrfanfiction140 | [WebNovel](https://www.webnovel.com/book/35043770500481305) and [NovelFlick](https://novelflick.com/story/35043770500481305) show 397 chapters; [Bed Novel](https://bednovel.com/bednovel/there-will-be-no-third-dark-lord-at-hogwarts-5400) exposes 430. Patreon advance posts are locked. | Mirror counts remain inconsistent. Existing FreeWebNovel exact candidate is not a rights-cleared or complete-edition decision. |
| Naruto: This Ninja Is Obviously Not Strong but Really Hard to Kill — selected credit nyawdao2 | [FreeWebNovel](https://freewebnovel.com/novel/this-ninja-is-obviously-not-strong-but-really-hard-to-kill) exposes the exact English title and a 547-entry index, but credits Wu Mian Qi Liang / 无面凄凉. | Author mismatch against the selected WebNovel credit. Retain as the existing rejected near match; do not substitute. |

## Three blocked fanfiction sources

### Naruto: The Wind Calamity

- [WebNovel's catalogue](https://www.webnovel.com/book/19921530006000505/catalog) credits Devil_Hex and exposes 951 entries. The opening volume includes auxiliary entries 0.1, 0.2 and 0.3 before the numbered chapters.
- [NovelLive's catalogue](https://novellive.com/book/naruto-the-wind-calamity) exposes 832 entries and also includes auxiliary 0.1-style entries.
- The supported FreeWebNovel listing has 951 entries, but its chapter URL mapping is non-linear. These counts do not form a validated one-to-one map.
- The author's [FanFiction.net page](https://www.fanfiction.net/s/14178557/1/Naruto-The-Wind-Calamity) asks translators to obtain permission first. That is a condition, not permission.
- PR #463's fail-closed behaviour remains correct. No mapping fix or retry is justified without a complete canonical TOC map and permission.

### Konoha's Medical Ninja: One Punch to beat up Madara

- [FreeWebNovel's public listing](https://freewebnovel.com/novel/konohas-medical-ninja-one-punch-to-beat-up-madara) credits INeedRest, labels the page English/ongoing, and shows latest entries 444–439 plus opening TOC entries 1–40. [WebNovel](https://www.webnovel.com/book/29703350508171905) also lists 444 chapters.
- The WebNovel credit is INeedRest, but the page's own note says they are not the original writer and only edited the work. Reviews also describe it as a Chinese work/translation.
- The underlying original author remains unidentified. The public 444-entry TOC and existing assembled archive do not resolve authorship or rights.
- Existing public artifact `14462633408` remains rights-unverified. Do not link, re-download, register, or create another public copy. The connected GitHub operations do not expose artifact revocation.

### HP: The Arcane Thief

- [FreeWebNovel's public listing](https://freewebnovel.com/novel/hp-the-arcane-thief) credits Snollygoster, labels the page English/ongoing, shows one auxiliary entry before Chapter 1, opening chapters 1–39 and latest entries 254–249. This is a 254-chapter Snollygoster edition and is the selected author/title match.
- [FanFiction.net](https://www.fanfiction.net/s/14119836/167/Harry-Potter-The-Arcane-Thief-LitRPG) is a separate Snollygoster cross-post showing 183 chapters; [Ranobes](https://ranobes.net/novels/1205620-the-arcane-thief-v741610.html) reports 254 written/275 available. Do not treat the 183-chapter cross-post as proof that the selected 254-chapter FWN edition is incomplete.
- PR #463 fixed the +1 URL offset caused by the auxiliary entry and added a regression test. The live full TOC has not been revalidated end-to-end after the merge, and no explicit archive permission was found. The technical adapter issue is fixed; the rights gate remains. No retry.

## Decision

No new title passes all gates for exact work/author, English edition, complete ordered index and explicit lawful archiving permission. Keep the 32 research targets and three blocked works separate from the 65 unmatched Yup/IDK entries. Continue fanfiction research; do not start another download or resume the deferred 65-title alternative-source sweep yet.

# Yup/IDK alternative-source research round 6

**Checked:** 22 November 2026, 21:35 IST  
**Scope:** six Yup-side candidates from the 52 distinct non-alias rows, plus a fresh metadata-only recheck of the three blocked fanfiction sources.  
**Method:** public author, publisher, edition and ordinary chapter-index metadata only. No chapter prose, screenshots, locked material, archive bytes or access-control workarounds were used.

## Yup-side findings

| Campaign title | Public identity and edition evidence | Decision |
|---|---|---|
| **Apotheosis** | The existing ReadNovelFull candidate identifies the title as *Apotheosis – Ascension to Godhood*, author 恩赐解脱, source IReader, completed, latest Chapter 3913. The page labels its chapter list as 3,910 and exposes only the first 30 entries in the fetched view. Novel Updates records 3,913 original chapters, **Licensed: No**, **Completely Translated: No**, and no English publisher. WuxiaFull independently shows 3,912 listed chapters with Chapter 3913 as latest. | This is an already-counted exact ReadNovelFull lead, not a new match. The public index evidence is inconsistent/incomplete. Historical prepare job 136480003715 in run #44791453169 stopped before chapter downloads with `Chapter archive is missing or misnumbering chapters`. Keep blocked; no unchanged retry and no archive permission. |
| **About the Reckless Girl Who Kept Challenging a Reborn Man Like Me** | Novel Updates identifies Kohigashi Nora and a completed Japanese one-shot web novel plus three light-novel volumes. WuxiaClick exposes ten entries, including the one-shot and volume material. | Not a supported-host source or a complete English edition. Keep the web novel and Japanese light novel distinct. |
| **Genjitsu Shugi Yuusha No Oukoku Saikenki** | The web novel is split across three Pixiv series: Part I (105+ chapters, with earlier Syosetu chapters removed), Part II (140 chapters, completed), and Part III (ongoing). The separate light-novel edition is by Dojyomaru and licensed in English by J-Novel Club. | No exact supported-host web-novel listing found. Do not substitute or archive the commercially licensed light-novel edition. |
| **Mad God** | Catalogue sources identify Tang Jia San Shao / 唐家三少 and Qidian; counts vary between 176 and 177 chapters, and third-party translation-status metadata conflicts. | No exact supported-host listing or reconciled English edition. Hold. |
| **Rise Of The Demon King** | The surfaced exact-title pages are manga/manhua listings for the Yao Ye work, not a verified book edition. Recent manga catalogue results expose up to Chapter 350. | Do not treat a manga listing as a novel source. No supported book source established. |
| **Skirt Chasing Monarch: City Lady Killer** | Original author Lonely Constant / 孤单常量; the Chinese original is complete at 1,374 chapters. WuxiaClick and WuxiaWorldEU expose only about 220 English entries, with another catalogue showing 286. | The English index is materially incomplete and the source is not a verified complete supported-host edition. Hold. |

### Round 6 result

- **0 new exact supported-host listings.** *Apotheosis* is a recheck of an existing exact ReadNovelFull candidate already counted in the first alternative-source matrix.
- **0 explicit archiving/public-distribution permissions.**
- **0 rights-cleared titles.**
- **0 new download runs.**
- No chapter prose or archive bytes fetched.

Sources: [ReadNovelFull: Apotheosis](https://readnovelfull.com/apotheosis-ascension-to-godhood-v1.html), [Novel Updates: Apotheosis](https://www.novelupdates.com/series/apotheosis-ascension-to-godhood/2022/), [WuxiaFull: Apotheosis](https://www.wuxiafull.com/Apotheosis-Ascension-to-Godhood/), [Novel Updates: About the Reckless Girl](https://www.novelupdates.com/series/about-the-reckless-girl-who-kept-challenging-a-reborn-man-like-me/), [WuxiaClick: About the Reckless Girl](https://wuxia.click/novel/about-the-reckless-girl-who-kept-challenging-a-reborn-man-like-me), [Genjitsu Shugi Yuusha web-novel parts](https://genkoku.fandom.com/wiki/Genjitsu_Shugi_Yuusha_no_Oukoku_Saikenki), [Complete Novel: Mad God](https://completenovel.com/mad-god/), [Fandom: Mad God](https://tjssverse.fandom.com/wiki/Mad_God), [MangaKakalot: Rise of the Demon King](https://www.katamanga.com/manga/rise-of-the-demon-king), [Novel Updates: Skirt-Chasing Young Monarch](https://www.novelupdates.com/series/skirt-chasing-young-monarch-city-lady-killer/), [WuxiaWorldEU: Skirt-Chasing Young Monarch](https://wuxiaworld.eu/novel-detail/skirt-chasing-young-monarch-city-lady-killer).

## Three blocked fanfiction sources rechecked

- **Konoha's Medical Ninja:** the WebNovel page still lists 444 chapters under INeedRest and explicitly says the credited person is not the original writer, only the editor. Original author and archive/public-distribution rights remain unresolved. Do not merge PR #275, fetch artifact contents, retry or republish.
- **HP: The Arcane Thief:** NovelTrust identifies Snollygoster and lists 254 numbered chapters plus Chapter 0 (Auxiliary). Its first TOC page shows Chapters 1–39 and the latest entries show 249–254. The last-page endpoint returned HTTP 403, so the complete paginated index remains unverified. No access workaround or retry. Rights remain unresolved.
- **Naruto: The Wind Calamity:** the FanFiction.net author-note URL returned HTTP 403 during this public recheck. The existing issue record says the author asks prospective translators to contact them first; no permission response is recorded. The FreeWebNovel TOC remains non-linear and fail-closed. No retry.

Sources: [INeedRest's WebNovel listing](https://www.webnovel.com/book/konoha%27s-medical-ninja-one-punch-to-beat-up-madara-%28completed%29_29703350508171905), [NovelTrust: The Arcane Thief](https://noveltrust.com/book/hp-the-arcane-thief), [FanFiction.net: Wind Calamity author note](https://www.fanfiction.net/s/14178557/75/Naruto-The-Wind-Calamity).

## Live reconciliation and next gate

- The 26 exact source-audit matches remain **18 Yup + 8 IDK**; the 65 unmatched rows remain **36 Yup + 29 IDK**.
- The 65 rows reconcile to **12 completed-registry aliases + 1 excluded alias + 52 distinct non-alias titles**. Do not re-download aliases or reintroduce the excluded title.
- The 43 fanfiction catalogue remains **8 complete, 3 blocked, 32 source-researched but unresolved**. This round adds no rights clearance.
- Completed registry: **343**. Separately user-confirmed private-HF imports: **70**. Global red/Dropped exclusions: **90**.
- Source-audit artifact #14714644436 remains unexpired and expires **21 December 2026, 16:36:47 UTC**. It is metadata only and contains no chapter text.
- Seoul Station's Necromancer remains registered at 209 chapters, run #44922285166, artifact #14714778249, expiry **19 February 2027, 16:01:42 UTC**. Its workflow recorded `confirm_rights=false`; do not fetch or redistribute the archive.
- Konoha Medical artifact #14462633408 remains public and unexpired, expiry **16 February 2027, 19:20:05 UTC**. Run #44379388243 has 22 unexpired artifacts. The archive contents were not fetched. Repository-owner action is required to revoke unlicensed public artifacts; the connected GitHub operations used here do not expose artifact deletion.
- Live Actions check at 21:35 IST: **0 queued/in-progress workflows and 0 active bulk-download workflows**.

Continue the 52 distinct alternatives in the required order: Yup first, then IDK. Prioritise full ordered English TOC and exact author/edition checks for the existing leads, then explicit title-specific rights. Public listings, commercial licences, translator credits and free reading access are not archive permission. Keep batches at no more than 10 titles and two active workflows; do not retry deterministic failures unchanged or publish unlicensed archives.

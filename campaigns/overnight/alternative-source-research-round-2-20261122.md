# Yup/IDK alternative-source follow-up round 2

**Checked:** 22 November 2026, 18:43 IST  
**Input:** the 65 unmatched rows from read-only source audit [#44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606), artifact [#14714644436](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606/artifacts/14714644436).  
**Method:** reconciled the exact campaign titles against the live 343-record registry and 90 exclusions, then checked author/edition identities and alternative public metadata listings. No chapter prose, screenshots, locked material or archive bytes were fetched.

## Corrected reconciliation

The original manifests still contain **36 Yup + 29 IDK = 65 audit rows**. Exact title equality alone missed aliases. This follow-up confirms **12 rows are aliases of completed registry entries** and **one row aliases a title in the global red/Dropped exclusion list**. That leaves **52 distinct, non-alias titles** for source follow-up.

| Audit title | Canonical record | Registry evidence |
|---|---|---|
| Invincible Conqueror | Invincible | Shen Jian; 3,753 chapters; run #42513431015 |
| Xian Ni | Renegade Immortal | Er Gen; 2,093 chapters; run #42513372924 |
| Records of the Human Emperor | The Human Emperor | Huangfu Qi; 2,467 chapters; run #42513372924 |
| The School Prince is a Girl | National School Prince Is A Girl | Warring Young Seven; 1,782 chapters; run #44444477580 |
| Arifureta Shokugyou De Sekai Saikyou | Arifureta Shokugyou de Sekai Saikyou (WN) | Chuuni Suki; 575 chapters; run #44780760719 |
| Crazy Levelling System | Crazy Leveling System | Crazy Meng Meng; 1,456 chapters; run #44780760719 |
| Dungeon Defence | Dungeon Defense | Yoo Heonhwa; 46 chapters; run #44780760719 |
| Evil Dragon Against The Heaven | Online Game: Evil Dragon Against The Heaven | Mars Gravity; 518 chapters; run #44781304939 |
| Invincible Dragon Emperor | The Invincible Dragon Emperor | Yao Ye; 1,295 chapters; run #44791453169 |
| Levelling Up And Becoming Undefeated | Leveling Up And Becoming Undefeatable | Wǔ Huā Niú; 1,377 chapters; run #44781304939 |
| Soul Land | Douluo Dalu | Tang Jia San Shao; 337 chapters; run #43734388839 |
| My Fury Will Burn The Heavens | Fury Towards The Burning Heaven | Yao Ye; 1,726 chapters; run #44781304939 |

The remaining alias is **Yong Heng Zhi Zun = Eternal Reverence**, by Jian You Tai Xu. *Eternal Reverence* is in `campaigns/overnight/excluded-90.json`; keep it excluded.

After correcting the aliases, the historical first-sweep counts adjust from 61 searched rows to 52 distinct titles: **11 unique exact supported-host leads**, **2 near/variant matches**, and **39 with no exact supported-host listing in that search scope**. One of the former 12 exact leads, *My Fury Will Burn The Heavens*, is already registered as *Fury Towards The Burning Heaven*. One of the former three near/variant rows, *Yong Heng Zhi Zun*, is an excluded alias. Seven of the former no-match rows are also completed-registry aliases.

**Do not re-download the 12 registry aliases. Do not reintroduce the excluded title.** The 52 remaining titles are still unresolved, not globally unavailable.

## Additional alternative-source findings

### New or strengthened leads

- **Addicted Pampering You: The Mysterious Pampered Wife of The Military Ye**: WuxiaClick identifies Jiu Mo Li and labels 266 chapters. WuxiaWorldEU exposes 250 page entries numbered through 266, so the visible index is incomplete. [WuxiaClick](https://wuxia.click/novel/addicted-pampering-you-the-mysterious-pampered-wife-of-the-military-ye) · [WuxiaWorldEU](https://wuxiaworld.eu/novel/addicted-pampering-you-the-mysterious-pampered-wife-of-the-military-ye). Hold.
- **Attack Of The Adorable Kid: President Daddy's Infinite Pampering**: the official WebNovel page identifies Sweets Flood and translator Atlas Studios, reports 2,612 completed chapters; NovelFull and FreeWebNovel also expose a 2,612-chapter listing. WuxiaClick has 2,484 page entries numbered 1–2,608, while FullNovels' country-of-origin snapshot says 1,782 chapters ongoing. The full paginated edition is not reconciled, and a commercial WebNovel translation or public mirror is not archive permission. [WebNovel](https://www.webnovel.com/book/attack-of-the-adorable-kid-president-daddy%27s-infinite-pampering_12447763405471405) · [NovelFull](https://novelfull.com/attack-of-the-adorable-kid-president-daddys-infinite-pampering.html) · [WuxiaClick](https://wuxia.click/novel/president-daddys-infinite-pampering) · [FullNovels](https://fullnovels.com/novel/attack-of-the-adorable-kid-president-daddys-infinite-pampering/). Source lead only.
- **Hidden Marriage Sweet Pampering: The Conglomerate's Little Wife**: WuxiaClick has 1,812 linked chapters with labels extending to 1,818; another raw catalogue reports 2,845 chapters. Its author is Helan Yang Yang, not the author of the completed registry's separate *Hidden Marriage* (Jiong Jiong You Yao). Do not merge the two identities. [WuxiaClick](https://wuxia.click/novel-read/hidden-marriage-sweet-pampering-the-conglomerates-little-wife) · [Novelgo](https://novelgo.id/novel/hidden-marriage-sweet-pampering-the-conglomerates-little-wife/).
- **Bringing The Nation's Husband Home**: the NovelFull page reports 973 chapters and credits Ye Fei Ye. Apple Books also lists official English anthologies from Beijing Book Co. Inc. (2019). The commercial English edition is not permission to copy or redistribute it. [NovelFull](https://novelfull.com/bringing-the-nations-husband-home.html) · [Apple Books](https://books.apple.com/us/book/bringing-the-nations-husband-home-1-anthology/id1532157678).
- **Eternal Martial Sovereign**: WuxiaClick has 140 linked pages with labels reaching 191, versus 2,240 original chapters. AsianReads marks the English translation licensed and identifies Gravity Tales as English publisher. Do not substitute the short WuxiaClick index or archive the licensed translation. [WuxiaClick](https://wuxia.click/novel-read/eternal-martial-sovereign) · [AsianReads](https://asianreads.com/eternal-martial-sovereign/).
- **Mad God**: CompleteNovel and the Tang Jia San Shao verse catalogue report 176–177 completed original chapters. This is metadata, not a supported downloader route or permission to archive. [CompleteNovel](https://completenovel.com/mad-god/) · [author-series reference](https://tjssverse.fandom.com/wiki/Mad_God).
- **The Kind Death God**: Novel Updates reports 208 completed original chapters, no English publisher, and an incomplete English translation. No complete English edition was verified. [Novel Updates](https://www.novelupdates.com/series/the-kind-death-god/).

### Edition and identity cautions

- *The Gloomy Me in Class is Actually the Vocalist of a Very Popular Band*: WuxiaClick has 75 chapters; Novel Updates records 111 original web-novel chapters. [WuxiaClick](https://wuxia.click/novel-detail/the-gloomy-me-in-class-is-actually-the-vocalist-of-a-very-popular-band) · [Novel Updates](https://www.novelupdates.com/series/the-gloomy-me-in-class-is-actually-the-vocalist-of-a-very-popular-band/).
- *How To Melt the Ice Lady*: WuxiaClick has 98 versus 101 original web-novel chapters. [WuxiaClick](https://wuxia.click/novel/how-to-melt-the-ice-lady).
- *My Plain-looking Fiance is Secretly Sweet with Me*: WuxiaClick has 46 versus 56 web-novel chapters; the Japanese light-novel work is published by Fujimi Fantasia Bunko. [WuxiaClick](https://wuxia.click/novel-detail/my-plain-looking-fiance-is-secretly-sweet-with-me) · [publisher/series discussion](https://forums.j-novel.club/topic/4273/my-plain-looking-fiance-is-secretly-sweet-with-me).
- *Invincible Levelling King* is not the registered *Invincible* by Shen Jian: the surfaced WebNovel MTL listing credits Vaib123 and contains only three chapters. Keep identities separate. [WebNovel](https://www.webnovel.com/book/invincible-levelling-king-%28mtl-novel%29_15568622905877405).
- *I Can Extract Everything* is not the registry's *Witcher: I Can Extract Everything* by Lich King Number 13. *Very Pure and Ambiguous* is not the registry's distinct *Very Pure and Ambiguous: The Prequel*. Do not merge either.
- *Yong Heng Zhi Zun* is the alias of *Eternal Reverence* and is excluded, not a near-match download candidate. [NovelFull identity page](https://novelfull.com/eternal-reverence.html) · [Novel Updates](https://www.novelupdates.com/series/eternal-reverence/).

### Commercially licensed editions

Public publisher/catalogue evidence also identifies licensed English editions for *Arifureta*, *How a Realist Hero Rebuilt the Kingdom*, *That Time I Got Reincarnated as a Slime* and *The Death Mage Who Doesn't Want a Fourth Time*. *In Another World with My Smartphone* is also licensed in English by J-Novel Club. Those licences are not permission to archive third-party copies. Where the underlying web-novel edition is already in the 343-record registry, do not substitute or re-download the separate light-novel edition.

## Current acquisition decision

- **12 registry aliases; 1 excluded alias; 52 distinct non-alias rows.**
- The 11 unique exact listing leads remain metadata leads only. Several have incomplete/mismatched indexes or are official commercial translations.
- **0 explicit lawful archiving permissions; 0 rights-cleared titles; 0 new download runs.**
- Completed registry: **343**. User-confirmed private-HF imports: **70**, separate. Red/Dropped exclusions: **90**.
- Seoul Station's Necromancer remains a verified 209-chapter completion from run #44922285166, artifact #14714778249 (expires 19 February 2027).
- Live Actions check at 18:43 IST: **0 queued/in-progress workflows; 0 active bulk downloads**.

No unchanged #371/#452 retries. No chapter text or archive bytes were fetched. Do not dispatch a batch until exact author/edition, English language, a complete ordered index, explicit lawful archiving permission and a non-public storage route are all verified.

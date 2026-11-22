# Yup/IDK source audit, 21 November 2026

**Read-only evidence:** [GitHub Actions run #44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606), artifact `source-audit-results.json` (30-day retention).

## Scope and result

The audit considered **91 eligible campaign entries** after the global exclusion and known-record preflight: 54 Yup and 37 IDK. It made **336 public book-page requests** across NovelFull, ReadNovelFull (standard and `-v1` URL patterns) and FreeWebNovel. No source host was disabled during the run.

**Preflight count semantics:** the preflight field `previously_known=349` is not the completed registry count. It is the distinct union of 343 titles in `downloaded_novels.json` and 21 titles in `campaigns/yup-pilot/verified-urls.json`, with 15 overlaps. Six verified-URL rows are not in the completed registry: Desolate Era, A Record Of Mortal’s Journey To Immortality, Warlock Of Magus World, Solo Levelling, Advent of Archmage and Charm Of Soul Pet. They are prior source-URL records, not extra completed downloads or private-HF imports. The completed registry remains 343; the user's separately confirmed private-HF import count remains 70.

| Result | Yup | IDK | Total |
|---|---:|---:|---:|
| Exact public listing found | 18 | 8 | **26** |
| No exact listing at the tested URL patterns | 36 | 29 | **65** |
| Eligible entries checked | 54 | 37 | **91** |

**This is discovery evidence only.** It fetched public book pages, not chapter prose. A matching title/URL does not prove the author/edition is the requested work, that the chapter index is complete, that archiving is permitted, or that a public Actions artefact may lawfully contain the work. The 65 are unresolved by this bounded search, not confirmed unavailable online.

## The 26 public book-page matches

| Tier | Requested title | Public book page | Audit follow-up |
|---|---|---|---|
| Yup | Awakening | https://readnovelfull.com/awakening-v1.html | Prior integrity failure; do not retry unchanged |
| Yup | Beast Piercing The Heavens | https://readnovelfull.com/beast-piercing-the-heavens-v1.html | Fresh candidate; TOC failed on duplicate Chapter 11 links |
| Yup | Beauty And The Bodyguard | https://novelfull.com/beauty-and-the-bodyguard.html | Chapter-list discovery timed out after the 15-minute bound; no index was obtained |
| Yup | Condemning the Heavens | https://freewebnovel.com/novel/condemning-the-heavens | Prior integrity failure |
| Yup | Doom Lord | https://readnovelfull.com/doom-lord-v1.html | TOC passed; exact title, 155 chapters |
| Yup | Flower Master In The City | https://readnovelfull.com/flower-master-in-the-city-v1.html | Prior integrity failure |
| Yup | Godly Student | https://readnovelfull.com/godly-student.html | Fresh candidate; invalid chapter URL |
| Yup | Heavenly Star | https://readnovelfull.com/heavenly-star.html | Prior integrity failure |
| Yup | Legend of Swordsman | https://novelfull.com/legend-of-swordsman.html | Prior integrity failure |
| Yup | Martial Arts System | https://readnovelfull.com/martial-arts-system.html | Recent preparation/index failure |
| Yup | Past Life Returner | https://freewebnovel.com/novel/past-life-returner | Recent chapter/index failure |
| Yup | Path to Heaven | https://readnovelfull.com/path-to-heaven-v1.html | Recent duplicate/misnumbered chapter index |
| Yup | The Alchemist God | https://readnovelfull.com/the-alchemist-god.html | Recent invalid chapter URL |
| Yup | The Mightiest Leveling System | https://readnovelfull.com/the-mightiest-leveling-system-v1.html | Recent invalid chapter URL |
| Yup | This MC Is Kickass | https://readnovelfull.com/this-mc-is-kickass-v1.html | Recent index failure; inspect before retry |
| Yup | Tomb Raider King | https://freewebnovel.com/novel/tomb-raider-king | No child job was created in the cited dispatch; no chapter log exists |
| Yup | Weapon Master | https://readnovelfull.com/weapon-master-v1.html | Recent preparation/index failure |
| Yup | World Domination System | https://readnovelfull.com/world-domination-system-v1.html | No child job was created in the cited dispatch; no chapter log exists |
| IDK | Ex Rank Supporting Role’s Replay in a Prestigious School | https://freewebnovel.com/novel/ex-rank-supporting-roles-replay-in-a-prestigious-school | Prior integrity failure |
| IDK | Game Market 1983 | https://freewebnovel.com/novel/game-market-1983 | Prior integrity failure |
| IDK | Girl, I’ll Teach You Cultivation | https://readnovelfull.com/girl-ill-teach-you-cultivation-v1.html | TOC passed; exact title, 283 chapters |
| IDK | Omega Summoner | https://readnovelfull.com/omega-summoner.html | Prior integrity failure |
| IDK | Parasite in Love | https://freewebnovel.com/novel/parasite-in-love | Prior integrity failure |
| IDK | Sense | https://freewebnovel.com/novel/sense | Prior integrity failure |
| IDK | The Military Female Soldier With Unwavering Stubbornness | https://readnovelfull.com/the-military-female-soldier-with-unwavering-stubbornness.html | TOC failed: 2,104 missing numbered chapters |
| IDK | The S-Classes That I Raised | https://freewebnovel.com/novel/the-s-classes-that-i-raised | Prior integrity failure |

## Five-title TOC preflight

[Run #44926984233](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984233) checked only each public book page and its ordinary chapter index. It downloaded **zero chapter bodies** and explicitly recorded `rights_verified: false`.

| Title | Result | Evidence |
|---|---|---|
| Beast Piercing The Heavens | Failed | Duplicate Chapter 11 links |
| Doom Lord | Passed | Exact title; 155 chapters |
| Godly Student | Failed | Invalid ReadNovelFull chapter URL |
| Girl, I’ll Teach You Cultivation | Passed | Exact title; 283 chapters |
| The Military Female Soldier With Unwavering Stubbornness | Failed | 2,104 missing numbered chapters; first missing positions reported from 2681 |

Only *Doom Lord* and *Girl, I’ll Teach You Cultivation* passed this index check. A pass is not rights approval or a completed novel.

## Five-candidate author and edition review (22 November 2026)

The ReadNovelFull book-page matches were compared with author/title metadata and country-of-origin chapter counts. None is rights-cleared.

| Candidate | Author and original-edition evidence | Decision |
|---|---|---|
| Beast Piercing The Heavens | Original title 兽破苍穹; author Yao Ye (妖夜); original publisher Zongheng; 1,445 chapters, complete. Novel Updates records Licensed=No and Completely Translated=No. The ReadNovelFull/WuxiaClick mirror exposes only 224 chapters and the preflight found duplicate Chapter 11 links. | Reject current mirror: index is invalid and edition is far short of the original. No permission. |
| Doom Lord | Original title 末日领主; author Wishing For A Pillow To Sleep With (想枕头的瞌睡); original publisher Qidian; 856 chapters, complete. Full Novels records Licensed=No and Fully Translated=No. The ReadNovelFull TOC passed only 155 entries. | A 155-entry TOC is not the complete 856-chapter edition. Hold; no permission. |
| Godly Student | Original title 神级插班生; author Such Ink-like Blood (如墨似血); original publisher 17k; 2,783 chapters, ongoing. AsianReads records Licensed=No. The ReadNovelFull preflight failed on an invalid chapter URL. | Do not retry unchanged; invalid index and no permission. |
| Girl, I'll Teach You Cultivation | Original title 妹子，我教你修仙; author Watchdog (看门狗); original publisher Heiyan; 812 chapters, complete. Novel Updates has Licensed=N/A. The ReadNovelFull/WuxiaWorldEU 283-entry TOC passed structurally but is only a partial edition against the 812-chapter original. | Do not treat the 283-entry pass as a complete novel or as permission. Hold. |
| The Military Female Soldier With Unwavering Stubbornness | Original title 万里红星不辜负; original author 直上青云. FanMTL lists 5,707 chapters; the WebNovel uploader Mistyfox is not the original-author identity. ReadNovelFull failed with a large missing-number range. | Author identity resolved, index incomplete and no permission. Do not retry unchanged. |

Evidence: [Novel Updates: Beast Piercing](https://www.novelupdates.com/series/beast-piercing-the-heavens/1000/), [Full Novels: Doom Lord](https://fullnovels.com/doom-lord/), [AsianReads: Godly Student](https://asianreads.com/novel/gs/), [Novel Updates: Girl, I'll Teach You Cultivation](https://www.novelupdates.com/series/girl-ill-teach-you-cultivation/), [FanMTL: The Military Female Soldier](https://www.fanmtl.com/novel/the-military-female-soldier-with-unwavering-stubbornness.html).

**Outcome:** 2 structural TOC passes do not represent complete editions; 3 TOC failures remain blocked; 0 lawful archiving permissions; 0 download runs. Do not add any of these five to a download manifest.

## The 65 unresolved titles

The following exact campaign titles had no exact match at the tested URL patterns. They remain in the original campaign files and must be rechecked against the current completed registry, aliases and source evidence before further work.

### Yup (36)

1. About the Reckless Girl Who Kept Challenging a Reborn Man Like Me
2. Addicted Pampering You: The Mysterious Pampered Wife of The Military Ye
3. Apotheosis
4. Arifureta Shokugyou De Sekai Saikyou
5. Bringing The Nation's Husband Home
6. Crazy Levelling System
7. Dungeon Defence
8. Eternal Martial Sovereign
9. Evil Dragon Against The Heaven
10. Genjitsu Shugi Yuusha No Oukoku Saikenki
11. Hidden Marriage Sweet Pampering : The Conglomerate’s Little Wife
12. I Can Extract Everything
13. I Told You I’m Not 〇〇!! ~When I Helped Out the Most Beautiful Girl in My Class, My Identity Got Found Out~
14. I'm In Hollywood
15. In Another World With My Smartphone
16. Invincible Conqueror
17. Invincible Dragon Emperor
18. Invincible Levelling King
19. Kujibiki Tokushou: Musou Haremu ken
20. Levelling Up And Becoming Undefeated
21. Lonely Loser, I’ll Become Blonde Frivolous Gyaru’s Favourite
22. Mad God
23. Man Huang Feng Bao
24. My Daoist Life
25. My Fury Will Burn The Heavens
26. Omni-Magician
27. Records of the Human Emperor
28. Rise Of The Demon King
29. Savage Divinity
30. Skirt Chasing Monarch : City Lady Killer
31. Soul Land
32. The Kind Death God
33. The School Prince is a Girl
34. Top Quality Beauty Cultivation System
35. Very Pure And Ambiguous
36. Yong Heng Zhi Zun

### IDK (29)

1. An Eye for News
2. Attack Of The Adorable Kid: President Daddy's Infinite Pampering
3. Beautiful Time With You
4. For Some Reason, the School Goddess Likes to Hang Out at My House
5. Genius Profiler Hansol Im
6. HacKer
7. How To Melt the Ice Lady
8. I Know Everything
9. Invisible Dragon
10. I’m Gonna Live with You Not Because My Parents Left Me Their Debt But Because I Like You
11. Juvenile Medical God
12. Konjiki no Wordmaster
13. Legend of Mythological Genes
14. Level Up Doctor Choi Kiseok
15. My Plain-looking Fiance is Secretly Sweet with Me
16. Rebound: A 2nd Chance
17. Shen Mu
18. Soudana, Tashika ni Kawaii Na
19. Starting Over
20. Super Doctor
21. Tensei Shitara Slime Datta Ken
22. The Entertainment Circle is Mine
23. The Gloomy Me in Class is Actually the Vocalist of a Very Popular Band
24. The Nine Godheads
25. The Reincarnated Cop Who Strikes With Wealth
26. Those Years When I Opened a Chinese Medicine Shop
27. Warrior's Promise
28. Xian Ni
29. Yondome Wa Iyana Shi Zokusei Majutsushi

**Alias warning:** The unresolved names include works already registered under alternate titles, including Arifureta, Crazy Leveling System, Dungeon Defense, Online Game: Evil Dragon Against The Heaven, The Invincible Dragon Emperor, Leveling Up And Becoming Undefeatable, The Human Emperor, Douluo Dalu, National School Prince Is A Girl, Renegade Immortal and A Will Eternal (the latter is an earlier campaign alias). These are not automatic new downloads. Compare author, edition, canonical URL and existing chapters; in particular, do not silently equate *Very Pure and Ambiguous* with *Very Pure and Ambiguous: The Prequel* or *Invincible Conqueror* with *Invincible* without edition verification.

## Follow-up order

1. Research and recover the user's **Harry Potter and Naruto fanfiction** first, using `campaigns/fanfiction/webnovel-favourites-43.json` (24 Naruto, 19 Harry Potter). The catalogue remains separate from this Yup/IDK audit.
2. Then research the 65 unresolved Yup/IDK titles, beginning with full-title/author/alternate-title checks and supported sources.
3. Reconcile every candidate with the current registry, the 90 global red/Dropped exclusions, issue #452/#448 and active workflows.
4. Before any chapter download, confirm exact work/edition, complete consecutive index and rights to archive and store the content in the target visibility context. Keep batches bounded and use `force=false`.



## Failure-classification corrections from direct log reconciliation (22 November 2026)

The 26 matches remain 18 Yup and 8 IDK. The prior-failure labels above are not all chapter-integrity failures:

### Twelve older blocked matches from issue #371

- **Nine confirmed chapter-identity mismatches:** Awakening (expected 2, page 9), Condemning the Heavens (1, page 0), Flower Master In The City (1101, page 1110), Heavenly Star (266, page 267), Ex Rank Supporting Role’s Replay in a Prestigious School (851, page 852), Game Market 1983 (125, page 124; another batch 151 vs 150), Parasite in Love (2, page 1), Sense (1, page 0), and The S-Classes That I Raised (251, page 216).
- **Omega Summoner:** the cited run #44447221591 has successful chapter-batch jobs for chapters 1–3,083. Recovery manifest artifact #14496292098 records **0 final ZIPs saved** and lists Omega Summoner and Parasite in Love as missing/failed. The previously repeated 2,069/2,070 mismatch is not present in that run's logs; do not repeat it unless the original failing run is located. Treat the title as not archived/registered, not as a verified chapter-number mismatch.
- **Beauty And The Bodyguard:** chapter-list discovery timed out after its 15-minute bound; no chapter index was obtained. The parent log does not expose the inner timeout/HTTP cause.
- **Legend of Swordsman:** job 135216534001 reports `ValueError: Downloaded chapter 5742 was empty`; partial artifact #14485801752 exists, but no final novel ZIP was produced.

### Nine other matches with 20 November source/TOC failures

- **Past Life Returner:** expected Chapter 501, page identifies 500.
- **This MC Is Kickass:** expected Chapter 101, page identifies 102.
- **Martial Arts System:** ReadNovelFull preparation reported a missing/misnumbered archive. PR #453 added strict same-book prologue support, but no post-fix preflight verified this title.
- **Path to Heaven:** duplicate Chapter 152. PR #465 added exact rejected-link diagnostics only; no root-cause repair or retry is recorded.
- **The Alchemist God:** PR #453's prologue support did not fix the later `Invalid ReadNovelFull chapter URL` failure in run #44804318431. PR #465 now preserves the offending href, but no post-merge diagnostic run has captured it.
- **The Mightiest Leveling System:** `Invalid ReadNovelFull chapter URL`; PR #465 adds diagnostics only, with no post-merge diagnostic run.
- **Weapon Master:** preparation reported a missing/misnumbered archive; no complete index was validated.
- **Tomb Raider King** and **World Domination System:** no child job was created in the cited four-title dispatch #44769541580. There is no chapter log for either; do not describe them as failed chapter downloads.

PR #466 adds exact FreeWebNovel URL/offset diagnostics for non-linear chapter labels, but it preserves fail-closed behaviour and does not provide a complete map or permission. No title in these groups was retried during this reconciliation. The exact next action is diagnostics-only TOC capture on the merged code, followed by a regression-tested root-cause fix before any targeted retry.

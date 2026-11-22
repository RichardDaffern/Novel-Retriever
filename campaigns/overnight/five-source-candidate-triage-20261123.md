# Five exact source-candidate rights and edition triage

**Checked:** 23 November 2026, 00:25 IST  
**Evidence:** Read-only source audit #44924359606, artifact #14714644436; five-title TOC preflight #44926984233, metadata artifact #14715652405.  
**Scope:** Exact public book-page candidates only. No chapter prose or archive bytes fetched.

## Audit reconciliation

The source-audit artifact contains 26 exact public listings, 65 unresolved rows and 90 global exclusions checked. The 26 split into 12 older blocked titles, nine titles with earlier 20-Nov source/TOC failures, and these five new candidates. The audit itself was read-only.

The five exact source URLs and tier labels are taken directly from `source-audit-results.json`:

| Candidate | Tier | Exact listing |
|---|---|---|
| Beast Piercing The Heavens | Yup | [ReadNovelFull](https://readnovelfull.com/beast-piercing-the-heavens-v1.html) |
| Doom Lord | Yup | [ReadNovelFull](https://readnovelfull.com/doom-lord-v1.html) |
| Godly Student | Yup | [ReadNovelFull](https://readnovelfull.com/godly-student.html) |
| Girl, I'll Teach You Cultivation | IDK | [ReadNovelFull](https://readnovelfull.com/girl-ill-teach-you-cultivation-v1.html) |
| The Military Female Soldier With Unwavering Stubbornness | IDK | [ReadNovelFull](https://readnovelfull.com/the-military-female-soldier-with-unwavering-stubbornness.html) |

## TOC, author and edition findings

| Candidate | Preflight result | Independent identity / edition evidence | Decision |
|---|---|---|---|
| **Beast Piercing The Heavens** | `index_failed`: duplicate Chapter 11 links. | Original author **Yao Ye / 妖夜**; Novel Updates records 1,445 completed original chapters, unlicensed and not completely translated. ReadNovelFull's ongoing list shows Chapter 209; WuxiaClick/WuxiaWorldEU show 224–225; other mirrors show 218–234 or machine-translated 1,470. | Duplicate chapter link plus large original/translation count mismatch. Hold. |
| **Doom Lord** | `index_passed_title_match`: exact title, author **Wishing For A Pillow To Sleep With / 想枕头的瞌睡**, 155 ordered ReadNovelFull entries. | Novel Updates records 856 completed original chapters, licence No, translation incomplete, English publisher N/A and Qidian as original publisher. WuxiaClick/WuxiaWorldEU expose 328 entries. | Structural pass only. The 155-entry edition is not the complete 856-chapter original; no archive permission. Hold. |
| **Godly Student** | `index_failed`: invalid ReadNovelFull chapter URL. | Original author **Such Ink-like Blood / 如墨似血**. Public metadata is highly inconsistent: 2,783 original chapters in one catalogue, while other mirrors split/label 3,864, 4,935 or 6,664 entries. No English publisher or explicit licence/archiving permission was found. | Adapter/index failure plus unresolved chapter model. Do not retry unchanged. |
| **Girl, I'll Teach You Cultivation** | `index_passed_title_match`: exact title, author **Watchdog / 看门狗**, 283 ordered ReadNovelFull entries. | Novel Updates records 812 completed original chapters, licence N/A, incomplete translation and no English publisher. WuxiaWorldEU also lists 283 entries. | Structural pass only. The 283-entry English listing is not the complete 812-chapter original; no archive permission. Hold. |
| **The Military Female Soldier With Unwavering Stubbornness** | `index_failed`: 2,104 numbered chapters missing; first missing values 2,681–2,688. | Author **Zhi Shang Qing Yun / 直上青云**; aliases include *Reborn at Boot Camp: General, Don't Mess Around!* and TMFS. The selected ReadNovelFull page reports latest Chapter 2,680 / 2,681 entries; another ReadNovelFull alias page reports latest Chapter 5,538. WebNovel has a separate 68-entry listing; other mirrors range roughly 3,526–5,485. | Major edition/numbering conflict. Do not infer missing URLs or retry unchanged. Hold. |

## Rights and dispatch decision

The five preflight records explicitly set `rights_verified=false`. A public listing, an exact title/author match, a complete-looking index, or a third-party translation does not grant permission to archive or redistribute the underlying work.

- Candidates checked: **5**
- Exact public listings: **5**
- Structural TOC passes: **2** (Doom Lord, Girl, I'll Teach You Cultivation)
- Structural TOC failures: **3** (Beast Piercing The Heavens, Godly Student, The Military Female Soldier With Unwavering Stubbornness)
- Complete original-edition indexes established: **0**
- Explicit lawful archive/public-distribution permissions: **0**
- Rights-cleared titles: **0**
- Download runs dispatched: **0**
- Chapter prose or archive bytes fetched: **0**

Do not dispatch any of these five. Keep the 12 older blocked cases and nine 20-Nov failure cases held until their exact root causes are fixed and regression-tested.

## Preflight known-title union reconciled

The `previously_known=349` value is **not** the completed registry count. In `tools/overnight_queue.py`, `manifests()` builds the known-title set as the union of normalized titles in `campaigns/yup-pilot/verified-urls.json` and `downloaded_novels.json`. At the audit commit, the verified-URL manifest has 21 entries, the registry has 343 entries, 15 verified-URL titles overlap the registry, and the union is 349.

The six manifest-only entries are:
- Five aliases of registry titles: Desolate Era → The Desolate Era; Warlock Of Magus World → Warlock of the Magus World; Solo Levelling → I Alone Level-Up; Advent of Archmage → Advent of the Archmage; Charm Of Soul Pet → The Charm of Soul Pets.
- One known source URL not in the registry: **A Record Of Mortal’s Journey To Immortality**. It is a verified URL entry, not a completed/downloaded registry title. The author is Wang Yu; Novel Updates records it as licensed and fully translated by Wuxiaworld, and Wuxiaworld identifies Yuewen as licensor. The stored FreeWebNovel URL is an unofficial mirror, not archive permission. Do not count it among the 343 completed records.

Therefore there is no six-record registry discrepancy. Keep **343** as the completed registry count; use **349** only for the audit's deduplication set, preserving the separate source-URL/alias distinction. This reconciles the preflight count without changing any completion totals.

Other reconciled counts remain 70 separately user-confirmed private-HF imports and 90 red/Dropped exclusions. The 65 unmatched rows remain 36 Yup + 29 IDK; 12 completed-registry aliases plus one excluded alias leave 52 distinct non-alias titles. The 43-fanfiction state remains 8 registry-complete, 3 blocked and 32 source-researched but rights-unresolved.

The known URL-only *A Record Of Mortal’s Journey To Immortality* is also not a download candidate: the authorised English edition is hosted by Wuxiaworld, licensed from Yuewen; the stored FreeWebNovel mirror URL does not grant archive rights. See [Wuxiaworld official listing](https://www.wuxiaworld.com/novel/rmji) and [Novel Updates licence metadata](https://www.novelupdates.com/series/a-record-of-a-mortals-journey-to-immortality/).

## Run and artifact evidence

- [Read-only source audit #44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606), artifact #14714644436.
- [Five-title TOC preflight #44926984233](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44926984233), artifact #14715652405. This artifact contains only the small TOC-preflight JSON; it did not download chapters.

## Sources

- [Beast Piercing The Heavens — Novel Updates](https://www.novelupdates.com/series/beast-piercing-the-heavens/) · [Full Novels](https://fullnovels.com/beast-piercing-the-heavens/) · [WuxiaClick](https://wuxia.click/novel/beast-piercing-the-heavens)
- [Doom Lord — Novel Updates](https://www.novelupdates.com/series/doomsday-lord/) · [Full Novels](https://fullnovels.com/doom-lord/) · [WuxiaWorldEU](https://wuxiaworld.eu/novel/doomsday-lord)
- [Godly Student — AsuraNovel](https://asuranovel.com/novels/godly-student/) · [WTR-LAB](https://wtr-lab.com/en/novel/1696/godly-student) · [NovelHi](https://novelhi.com/novel/fantasy/godly-student/chapters) · [WuxiaBox](https://www.wuxiabox.com/novel/godly-student.html)
- [Girl, I'll Teach You Cultivation — Novel Updates](https://www.novelupdates.com/series/girl-ill-teach-you-cultivation/) · [WuxiaWorldEU](https://wuxiaworld.eu/novel/girl-ill-teach-you-cultivation)
- [The Military Female Soldier — ReadNovelFull](https://readnovelfull.com/the-military-female-soldier-with-unwavering-stubbornness.html) · [Reborn at Boot Camp alias — ReadNovelFull](https://readnovelfull.com/reborn-at-boot-camp-general-dont-mess-around-v1.html) · [WebNovel listing](https://en.webnovel.com/book/15148630906297405) · [FreeWebNovel alias listing](https://freewebnovel.com/novel/reborn-at-boot-camp-general-dont-mess-around)

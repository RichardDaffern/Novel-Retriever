# Yup alternative-source research round 8

**Checked:** 23 November 2026, 00:45 IST  
**Repository baseline:** `main` at `fa459a271677aab8748d7342d4d3a2f6737e4b37`  
**Scope:** Seven remaining Yup-side identity/alternative-title leads, plus one exclusion-alias check. Public metadata and chapter-index metadata only. No chapter prose or archive bytes fetched.

## Findings

### 1. Very Pure And Ambiguous: completed-registry alias, not a new acquisition

The requested title resolves to **So Pure, So Flirtatious**, author **Fishman The Second / 鱼人二代**, Chinese title **很纯很暧昧**, alternative names **SPSF** and **Very Pure Very Vague**. NovelFull has the exact supported-host page:

- [NovelFull: So Pure, So Flirtatious](https://novelfull.com/so-pure-so-flirtatious.html)
- [FullNovels identity and licence metadata](https://fullnovels.com/so-pure-so-flirtatious/)

The directory metadata records 2,385 completed original chapters, Qidian as original publisher, licence status Yes, Gravity Tales as English publisher and translation status incomplete. NovelFull identifies Gravity Tales as its source and shows the English listing through Chapter 1,621. This is not an independently verified complete original-edition index and is not permission for this project to archive or redistribute the work.

**Deduplication correction:** `downloaded_novels.json` already contains `So Pure, So Flirtatious`, 1,621 chapters, completed in run [#42513348683](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/42513348683). Its artifact #13636208314 expired on 15 November 2026. The separate prequel `Very Pure and Ambiguous: The Prequel` is also registered (746 chapters), but is a different related work. Do not confuse the two.

Therefore `Very Pure And Ambiguous` is a **newly identified alias of an existing registry record**, not a new source candidate or download.

### 2. Man Huang Feng Bao / Storm in the Wilderness

- Author: **Gao Po / 高坡**.
- [Gravity Tales page](https://gravitytales.com/story/man-huang-feng-bao/) exposes 695 chapter entries and a next-update timestamp of 23 November 2026.
- [WuxiaWorldEU page](https://www.wuxiaworld.eu/novel/man-huang-feng-bao) reports 696 entries with displayed numbering through Chapter 703.
- [AsianReads metadata](https://asianreads.com/man-huang-feng-bao/) records 695 completed original chapters and 17k as original publisher.

This is a useful exact alternative listing, but Gravity Tales/WuxiaWorldEU are not the configured supported acquisition adapters for this campaign. The chapter numbering differs, and no project-specific archive or public-distribution permission was found. Hold.

### 3. My Daoist Life / My Monastic Life

- Original author: **钓鱼1哥**; original Chinese title **我的修道人生**.
- [CompleteNovel metadata](https://completenovel.com/novel/ta-tu-dao-nhan-sheng/) records 352 completed original chapters and the aliases `My Daoist Life` / `My Monastic Life`.
- [WuxiaClick page](https://wuxia.click/novel/my-daoist-life) credits a different author (`萱草1`) and exposes only 76 chapters.
- [Novel Updates](https://www.novelupdates.com/series/my-daoist-life/) records the 352-chapter original and no English publisher.

The 76-chapter page is not safe to treat as the same author/edition without reconciliation. No exact NovelFull, ReadNovelFull or FreeWebNovel book page or archive permission was verified. Hold.

### 4. Top Quality Beauty Cultivation System

- Author: **Yi Yan Sheng Si Yu**.
- [Novel Updates](https://www.novelupdates.com/series/top-quality-beauty-cultivation-system/) records 707 completed original chapters, licence No and translation incomplete.
- FanMTL/WTR-LAB metadata also exposes 707-entry listings, but neither establishes an authorised supported-host edition or archive rights.

No exact supported-host book page or explicit permission found. Hold.

### 5. Savage Divinity

- Author: **RuffWriter**.
- The author makes the work free to read on [Royal Road](https://www.royalroad.com/fiction/5701/savage-divinity) and their [WordPress site](https://ruffwriter.com/).
- The author's Patreon listing includes a locked Chapter 330.

Free-to-read access is not an archive or redistribution licence. No explicit project archiving permission found. Hold.

### 6. About the Reckless Girl Who Kept Challenging a Reborn Man Like Me

- Author: **Kohigashi Nora**.
- [Novel Updates](https://www.novelupdates.com/series/about-the-reckless-girl-who-kept-challenging-a-reborn-man-like-me/) describes a Japanese web-novel one-shot and a separate three-volume light-novel edition.
- No English publisher or exact supported-host book page was verified.

Do not mix the web-novel and light-novel editions. No archive permission found. Hold.

### 7. Rise Of The Demon King

The surfaced pages identify a **manhua**, not a novel. Treat this as a medium false positive, not a source match. Do not add a novel campaign entry.

## Identity correction: similarly named excluded title

`Addicted Pampering You: The Mysterious Pampered Wife of The Military Ye` is by **Jiu Mo Li / 久陌离**, Chinese title **宠你上瘾：军爷的神秘娇妻**, with a 586-chapter original listing. It is **not** the excluded `Addicted to Boundlessly Pampering You`, which is by **Jing Lan / 静兰**, Chinese title **宠溺无边**, and has a different synopsis/edition. Keep the Jiu Mo Li work distinct from the 90-title exclusion. Its surfaced pages are metadata/mirror listings, not archive permission.

## Reconciliation and outcome

- Yup rows checked in this round: **7**.
- New supported-host alias page: **1** (`Very Pure And Ambiguous` → already-registered `So Pure, So Flirtatious`).
- New non-supported alternative listing: **1** (`Man Huang Feng Bao` / `Storm in the Wilderness`).
- Additional identity/medium clarifications: **5**.
- New completed-registry aliases found: **1**.
- Completed-registry aliases now: **13**.
- Excluded aliases: **1**.
- Distinct unresolved titles after alias reconciliation: **51** (**23 Yup, 28 IDK**).
- Explicit archive permissions: **0**.
- Rights-cleared titles: **0**.
- New download runs: **0**.

The 65 audit rows were 36 Yup + 29 IDK. The fanfiction research pass for the 32 outstanding entries was completed through round 18 before this deeper alternative-source work began. Keep the three blocked fanfiction works held. Continue the 51 distinct alternative-source targets in the required order: Yup first, then IDK. Four URL-pattern 404s do not establish worldwide unavailability.

## Rights and execution

A public page, a licence held by a translator/publisher, or free-to-read access does not grant this project permission to make an archive. No candidate in this round passes the explicit archive-rights gate. No download workflow was dispatched, and no chapter text/archive bytes were fetched.

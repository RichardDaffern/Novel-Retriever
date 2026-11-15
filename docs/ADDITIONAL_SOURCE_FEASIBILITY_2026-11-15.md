# Additional novel-source feasibility review

**Checked: 15 November 2026. Status: research only; no new downloader enabled.**

The project's only supported multi-source entry point is **Library - Bulk Download**. It auto-detects the source from pasted novel links. This report assesses *possible future adapters*, not sites that are already accepted by that workflow.

## How these candidates were assessed

- Read public book pages, chapter catalogue pages, published policies and official download documentation where available.
- Evaluate title/author/synopsis, full chapter ordering, single chapter availability, missing/alternate numbers, hosting or anti-automation limits and portable EPUB potential.
- Distinguish **browser/web retrieval** from access from GitHub Actions. **No new GitHub-hosted live downloader run was performed for these candidates.**
- No chapter text or copyrighted EPUB was saved or committed. No access controls were bypassed.
- A public page being readable **does not** mean automated archiving, copying, sharing or scraping is authorised. Source permissions, rights-holder permission and robustness must be established independently.

## Findings

| Source | Public technical observations | Permission or reliability issue | Decision |
| --- | --- | --- | --- |
| **WuxiaClick**, `wuxia.click` | [Martial World](https://wuxia.click/novel/martial-world) exposes an HTML chapter list with 2,276 entries, numbered 1 through 2,277 (not interchangeable with positions), synopsis, genres, title and author. [First chapter](https://wuxia.click/chapter/martial-world-1) is publicly readable without signing in. [About page](https://wuxia.click/about) says chapters can be read without accounts. [Downloads page](https://wuxia.click/downloads) is offline reading **on that device**, not a verified portable EPUB endpoint. The site [redesigned in October 2026](https://wuxia.click/blog/welcome-to-the-new-site). | No verified permission for server-side chapter archiving; browser readability is not evidence of GitHub runner access. Chapter labels can be nonconsecutive and need ordered URL-index validation. | **Top new technical candidate for cultivation novels; permission + runner metadata probe required before any adapter.** |
| **Archive of Our Own (AO3)**, `archiveofourown.org` | AO3 [officially offers EPUB, AZW3, PDF, HTML and MOBI downloads](https://archive.transformativeworks.org/admin_posts/32441) per publicly accessible work; example [work page](https://archive.transformativeworks.org/works/58530454/chapters/149112340) has a built-in EPUB download. Especially relevant for HP/Naruto fanfiction. | Some works require sign-in or have access restrictions; a user-facing download feature does not itself authorise high-volume automated fetching. Large EPUB exports may fail. Site access and policies for automated calls must be checked. | **Best native-EPUB candidate, subject to official download/rate permissions.** Prefer a validated native EPUB to scraping chapters. |
| **Royal Road**, `royalroad.com` | Public [Mother of Learning](https://www.royalroad.com/fiction/21220/mother-of-learning) metadata and chapters. Repo already recognises URL shapes and has an offline adapter; FanFicFare supports the site. [Author Premium](https://www.royalroad.com/support/knowledgebase/110) provides authors a first-party EPUB export. Chapter IDs are not reading positions. | Authors' export access is not equivalent to a bulk export licence for arbitrary fiction. [Robots rules](https://www.royalroad.com/robots.txt) vary by crawler and restrict chapters for several agents. | **Technically promising for authorised works, but require permission; native author EPUB for an author's own work is preferred.** |
| **LibRead**, `libread.com` | [Re: Tales of the Rune-Tech Sage](https://libread.com/libread/re-tales-of-the-rune-tech-sage-22188) exposes metadata and paginated chapter links. Its first chapters redirect to **FreeWebNovel** chapter pages; not an independent supply for that work. [Terms](https://libread.com/privacy-terms-of-use.html) mention attribution when reusing content. | Mixed hosting, paginated chapter lists and underlying author/translator rights; attribution is not blanket permission to automate or redistribute. | **Low-value separate adapter until books with independent chapter hosting and permission are verified.** |
| **NovelHi**, `novelhi.com` | [Everlasting Dragon Emperor chapter index](https://novelhi.com/novel/fantasy/everlasting-dragon-emperor/chapters) displays a 5,215-chapter catalogue; public metadata available. | [User Agreement §2.2](https://novelhi.com/about/content-policy) permits only limited saves and excludes compilation of extracted content into albums/databases/catalogues. | **Do not enable unrestricted automated full-book download without explicit permission.** |
| **NovelBuddy**, `novelbuddy.me` | [Martial World](https://novelbuddy.me/martial-world) and [prologue](https://novelbuddy.me/martial-world/prologue-magic-cube) publicly readable; chapter list displays limited pagination. | [Terms of Service §4](https://novelbuddy.me/terms-of-service) explicitly forbid automated tools, bots and scrapers. | **No automated adapter without permission.** |
| **Novel Fire**, `novelfire.net` | Existing [experimental source research](experimental-sources.md) records `/book/<slug>` and paginated chapter-index paths. | Previously reviewed terms prohibit automated crawling for general archiving; live terms page was not retrievable in this pass. | **Remain disabled, pending authorised access.** |
| **WTR-Lab**, `wtr-lab.com` | Repo has offline HTML analysis and local authorised-EPUB import; site has ticket-locked chapters. | [Terms](https://wtr-lab.com/en/terms-of-use) restrict copying/downloading and automated requests. | **No live chapter downloader; keep local EPUB import only.** |
| **Wuxiaworld (official)**, `wuxiaworld.com` | Licensed Chinese fantasy catalogue with official reading options. | [Terms](https://www.wuxiaworld.com/terms-of-service) expressly prohibit automated extraction or archiving without prior written permission; some content is locked. | **Do not scrape; use official downloads where authorised.** |
| **WebNovel**, `webnovel.com` | Existing repo has public metadata probes and offline import of authorised saved chapters. | Prior tests encountered 403/challenges; paid and locked chapters are off-limits. | **No general live bulk downloader.** |
| **Light Novel Pub**, `lightnovelpub.com` | Existing offline feasibility parser recognises `/novel/<slug>`. | A complete current live chapter list, website permission and stable content extraction were not verified. | **Unverified; no new adapter yet.** |
| **NovelBin / BoxNovel / NovelGo**, `novelbin.com`, `boxnovel.com`, `novelgo.id` | Public homepage fetches from this research environment returned 503, 502 and 403 respectively. | These results do **not** establish definitive site-wide unavailability or GitHub runner behaviour; no dependable catalogue evidence collected. | **Low priority until basic permitted access is confirmed.** |

## Priority order

1. **WuxiaClick**: most relevant new source for Chinese cultivation novels. First verify publisher/site permission and robots/access rules, then perform a *metadata-only* GitHub runner smoke (book + one index; no text) only if permitted. If passed, test two separately authorised public chapters and prove ordinal positions against exact links, metadata, text integrity and chapter gaps.
2. **AO3**: strongest fit for HP/Naruto fanfiction via its built-in EPUB export. Confirm that the planned automated request volume and method are allowed, whitelist public work IDs, obtain EPUB using the site's published download flow, and verify source identity, chapter count and EPUB/ZIP hashes. Do not access restricted works or defeat throttling.
3. **Royal Road**: use existing offline importer for authors' authorised exports now. A general website adapter should require separately established rights and robust metadata/ordered-chapter testing.
4. Other sites: do not increase supported-domain allowlists until their permission and completeness gates pass.

## Required gates for any new provider

1. Published permission or other valid authorisation for the intended automated archiving (not only reading).
2. Stable canonical source URL, full chapter index and source-specific identity.
3. At most two permitted live chapter checks, with locked/challenge detection and accurate text/body/title extraction.
4. Strict limits on parallelism, delay, timeouts, redirects and rate handling; no proxy, login, paywall or CAPTCHA workaround.
5. Offline Linux/Windows tests with wholly synthetic content, full EPUB/manifest SHA-256 and CRC checks, partial checkpoint reuse, existing artefact preservation and retry-only bulk recovery.
6. Extend **the existing one-click Library - Bulk Download link field**, not a new competing bulk workflow or new website dropdown.

**Do not merge a new website adapter based solely on a web browser being able to read one chapter.**

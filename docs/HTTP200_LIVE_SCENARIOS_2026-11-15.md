# Live HTTP-200 website scenario validation

**Date:** 15 November 2026  
**Subsequent update:** Bounded WuxiaClick chapter ranges have since been implemented with a rights gate, 20-chapter per-run ceiling and direct/bulk Actions workflows. The [live full-index and first/last chapter parser check (archived)](SOURCE_TEST_EVIDENCE_ARCHIVE.md) passed for both *Martial World* and *True Martial World*. Live metadata author, genres and synopsis checks passed in [run #43730710184 (archived)](SOURCE_TEST_EVIDENCE_ARCHIVE.md). This remains distinct from an authorised complete EPUB download.  
**Status:** Completed bounded live technical tests. Research only; no website enabled for automated full-book downloads.

## Evidence and safeguards

Tests ran from ordinary GitHub-hosted Ubuntu Actions runners, using public pages only, and did **not** require login, cookies, paid APIs, CAPTCHA circumvention or other access workarounds. Each target's `robots.txt` was read before its book or chapter pages. All HTTP redirects were **not followed**. The probes made a few serial requests with one-second pacing. Chapter prose was **never printed, exported, committed or uploaded**; only status codes, text-container lengths, page counts and paths appeared in logs.

Live evidence:

1. [Run #43726026737: two WuxiaClick books, two LibRead books, one NovelBin.cc book and chapter probes (archived)](SOURCE_TEST_EVIDENCE_ARCHIVE.md)
2. [Run #43726221266: WuxiaClick first and final chapter URLs and pagination discovery (archived)](SOURCE_TEST_EVIDENCE_ARCHIVE.md)
3. [Run #43726340193: WuxiaClick first, second and final catalogue pages (archived)](SOURCE_TEST_EVIDENCE_ARCHIVE.md)

These were **real website requests**, not mocks. They are technical access checks, **not full-novel EPUB downloads or verified authorisation to archive and redistribute content**.

## Tested scenarios and results

| Source and scenario | Result | Evidence / limitation |
| --- | --- | --- |
| WuxiaClick: [Martial World](https://wuxia.click/novel/martial-world) book page | **PASS: HTTP 200** | Correct title; 258,861-byte HTML; catalogue is paginated |
| WuxiaClick: [True Martial World](https://wuxia.click/novel/true-martial-world) book page | **PASS: HTTP 200** | Correct title; 253,207-byte HTML; catalogue is paginated |
| WuxiaClick: *Martial World* first chapter | **PASS: HTTP 200** | `/chapter/martial-world-1`; `#chapter-content` contained **9,535 characters**; header **Chapter 0 - Magic Cube**; no challenge detected |
| WuxiaClick: *True Martial World* first chapter | **PASS: HTTP 200** | `/chapter/true-martial-world-1`; `#chapter-content` contained **12,367 characters**; header **Chapter 1 - Grave of Yi Yun**; no challenge detected |
| WuxiaClick: *Martial World* last linked chapter | **PASS: HTTP 200** | `/chapter/martial-world-2277`; **Afterword**, 1,388 characters of content |
| WuxiaClick: *True Martial World* last linked chapter | **PASS: HTTP 200** | `/chapter/true-martial-world-1710`; **Epilogue**, 16,247 characters of content |
| WuxiaClick: page navigation | **PASS: linked pages respond 200** | *Martial World* has links to pages 2–23; *True Martial World* to pages 2–18. Explicit `?page=N#chapters` links exist; no need to guess an API |
| WuxiaClick: full index completeness | **NOT PROVEN** | Initial HTML has approximately **100 catalogue chapter links**, with additional **first/latest navigation links**. Page 2 and final page returned 200 and contained more links, but **not every page was enumerated**. Do not mistake navigation anchors for table-of-contents rows |
| WuxiaClick: reported count vs final numbered path | **POTENTIAL GAP** | *Martial World* advertises **2,276** chapter entries, with highest numbered URL **2277**; *True Martial World* advertises **1,709** entries, with highest numbered URL **1710**. The first chapter of *Martial World* has the heading Chapter 0 even though its URL ends in `-1`. The correct mapping is **indexed reading order**, not numerical chapter title or maximal path suffix |
| LibRead: [Re: Tales of the Rune-Tech Sage](https://libread.com/libread/re-tales-of-the-rune-tech-sage-22188) | **Book HTTP 200; chapter HTTP 302** | Book HTML is readable. Its first chapter redirects to **freewebnovel.com**; no redirect followed |
| LibRead: [Ruling Martial World by Infinite Insect Swarms](https://libread.com/libread/ruling-martial-world-by-infinite-insect-swarms-144201) | **Book HTTP 200; chapter HTTP 302** | An independent second title also redirects to **freewebnovel.com**. LibRead isn't currently an independent chapter source for these cases |
| NovelBin.cc: [Cultivation: Being Immortal](https://novelbin.cc/book/cultivation-being-immortal/) | **Book HTTP 200** | 868 chapters reported; HTML displays **30 initial numbered chapter links** |
| NovelBin.cc: first linked chapter | **HTTP 429: RATE LIMITED** | `/book/cultivation-being-immortal/chapter-1`. Test stopped. No retry, proxy or throttling workaround attempted; EPUB feasibility unproven |
| NovelArrow.com | **Not an independent HTTP-200 GET source** | Previous research found **HEAD 200 but GET 302 to NovelPing**; NovelPing robots disallowed subsequent probe. Remains disabled |
| LightNovelPub.com | **Not an HTTP-200 live book source** | The homepage redirects to an announced shutdown. No chapter source remains to test there |

All tests were within the websites' visible public access paths; permission to perform **unattended full-book archiving** still needs separate confirmation. WuxiaClick itself [offers a browser/device-specific offline reading feature](https://wuxia.click/blog/welcome-to-the-new-site), not a verified transferable EPUB export.

## Technical interpretation

### WuxiaClick

**Most promising new website from these tests.** Book data, chapter-body markup, first/last public pages and linked index pagination all behaved successfully on GitHub Actions. A future adapter should:

1. Parse the table-of-contents element, excluding the first/latest navigation links. **Do not assume every `/chapter/<slug>-<number>` anchor belongs to the TOC.**
2. Follow **only existing same-site `?page=N` links** from the book's catalogue, preserving the returned ordering. Avoid guessed sequential chapter URLs, which risk incorrectly treating missing numeric suffixes as missing content.
3. Cross-check the unique chapter-entry count against the advertised **2,276 / 1,709** counts and reject duplicates, gaps in indexed positions, or mismatch. **Do not require URL suffixes to be consecutive** unless verified by the real catalogue.
4. Validate content from `#chapter-content`; exclude nav, comments and advertisements, and preserve actual title (including numbered Chapter 0 or a non-numbered Afterword). Allow legitimate shorter final chapters without opening acceptance to challenge pages.
5. Before implementing, **establish permission** for the particular automated export use case. The site's first-party offline reading is not proof that exporting copies to third-party GitHub Actions artefacts is authorised. In a public repository, those artefacts can be accessible to others.

**No production adapter was enabled:** complete TOC validation, authorisation and private artefact handling are not yet confirmed.

### LibRead

Two independent books both returned 302 to the already supported FreeWebNovel host. A safe future *URL hand-off* may be worth exploring **only if** it maps a verified LibRead book to a canonical FreeWebNovel book, with source identity, rights, and a reproducible mapping. Blindly following redirects to arbitrary sites would violate the downloader's strict allowlist.

**No new LibRead downloader needed for the two sampled titles.**

### NovelBin.cc

The book page is accessible, but the first linked chapter returned HTTP **429**. That is a concrete source-side rate limit, not a parsing failure. **Stop, do not retry to evade the limit**, and do not mark the site as full-book feasible. Book and chapter pages appear paginated; the first page's 30 links do not prove the entire 868-chapter index can be retrieved.

## Next gate

- **WuxiaClick:** permission and actual complete-TOC reconciliation, followed by offline synthetic EPUB/ZIP and multi-site bulk integration tests. Then, and only then, offer it as an automatically detected domain in the **existing** Library - Bulk Download workflow.
- **LibRead:** no duplicate downloader. Consider an explicit, source-verified alias mapping later.
- **NovelBin.cc:** leave disabled because of the observed HTTP 429 and unverified rights.
- **Other HTTP 200 HEAD-only/redirect sites:** do not misclassify them as usable chapter sources.

**Repository production status remains unchanged.** The temporary investigation workflows were deleted from the change branch after the live runs; the live Actions logs remain linked for auditing.

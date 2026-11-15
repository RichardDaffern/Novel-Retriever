# Archived source feasibility and live-parser observations

**Date:** 15 November 2026. **Purpose:** preserve the results of temporary GitHub Actions source investigations after their workflows and 22 artefact-free runs were deleted to declutter the repository.

This report preserves the measured findings, not novel chapter prose. The former run links no longer resolve. This archive is **historical technical evidence**, not a statement that a site currently permits automated book archiving.

## GitHub-hosted public-source observations

| Source | Test scenario | Measured result |
| --- | --- | --- |
| WuxiaClick | Martial World public book page | HTTP 200, catalogue pages linked, **2,276 unique ordered entries** |
| WuxiaClick | True Martial World public book page | HTTP 200, **1,709 unique ordered entries** |
| WuxiaClick | Martial World first and final readable chapter | HTTP 200; parser retrieved 9,576 characters from Chapter 0 and 1,392 from the Afterword |
| WuxiaClick | True Martial World first and final readable chapter | HTTP 200; parser retrieved 12,459 characters from the opening chapter and 16,342 from the Epilogue |
| WuxiaClick | Live book metadata | Author **Cocooned Cow** for both; synopsis lengths 218 and 767 characters; genre and chapter counts present |
| WuxiaClick | Catalogue consistency and pagination | Martial World displayed 2,276 entries with highest source URL suffix **2277**; True Martial World 1,709 with suffix **1710**. All linked pages were parsed and validated, with chapter positions independent of URL suffixes |
| LibRead | Two independently selected book pages | Both HTTP 200; their tested chapter links returned HTTP 302 to **FreeWebNovel**, without following the redirect |
| NovelBin.cc | Book and linked chapter | Book HTTP 200; first chapter HTTP **429**. Probing stopped |
| Royal Road | GitHub runner request to public book page | HEAD and GET HTTP **403** |
| Original NovelBin.com | Site homepage | HTTP **503** |
| NovelArrow | HTTP HEAD/GET | HEAD 200, GET HTTP **302** to NovelPing; NovelPing's robots rules disallowed the probe |
| NovelGo.id | Robots check | HTTP **403**, no book request made |
| BoxNovel | Robots check | Connection/URL error, no book request made |

**Method:** Robots-first checks from GitHub-hosted Linux runners, strict same-site request boundaries, no redirected chapter fetching, no login, proxies or anti-bot bypass. Public HTML was inspected for structure, not stored or published. Readability and response codes are not sufficient to establish permission to archive content.

## Kept production test evidence

The surviving repository's unit, Windows and ZIP tests and the merged implementation PRs remain the audit trail:

- [WuxiaClick implementation PR #148](https://github.com/RichardDaffern/Novel_Library/pull/148), including synthetic pagination, EPUB, checkpoint and bulk-routing tests
- [WuxiaClick post-merge CI](https://github.com/RichardDaffern/Novel_Library/actions/runs/43731066193), 3/3 passed
- [Additional feasibility PR #146](https://github.com/RichardDaffern/Novel_Library/pull/146)
- [HTTP-200 source checks PR #147](https://github.com/RichardDaffern/Novel_Library/pull/147)

The authorised download campaign's **one-off launch run #43733541073 was retained** because it contains an artefact referenced by active download monitoring. No completed novel-download runs or their artefacts were deleted as part of this clean-up.

**Clean-up performed 15 November 2026:** 10 obsolete workflow registrations removed by deleting their 22 artefact-free historical runs. Nine current workflow definitions were retained. Historical results above are preserved for future maintenance without crowding GitHub's Actions sidebar.

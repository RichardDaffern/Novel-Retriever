# Next-site feasibility: Novel Fire and Light Novel Pub

**15 November 2026 verified update:** [Completed multi-site investigation](ADDITIONAL_SOURCE_FEASIBILITY_2026-11-15.md) includes two robots-first GitHub Actions probes of WuxiaClick, Royal Road, LibRead, NovelBin and other candidates. **LightNovelPub.com itself has now shut down**; its successor NovelCodex explicitly does **not** host chapter content. This older document records historical/offline evidence only. No additional live source was enabled.

**Status: research and isolated, offline parsing only. No new live downloader is enabled.**
Last reviewed: 10 November 2026.

This evaluation does not change the stable NovelFull or FreeWebNovel download
pipelines, downloaded registry, cover ZIP formats, or the unified bulk job.

## Source observations and limitations

| Candidate | Observed public URLs and catalogue | Important constraint | Decision |
|---|---|---|---|
| Novel Fire (novelfire.net) | Public book pages use `/book/<slug>`; `/book/<slug>/chapters` lists numbered links such as `/book/martial-world/chapter-1` and `chapter-2`, with paginated indexes | Its own published terms prohibit crawling/scraping and reserve archive exceptions for public search indexing; automated access may also meet challenges | Do not enable chapter crawling or automatic downloading without verified permission |
| Light Novel Pub (lightnovelpub.com) | **Historical** novel URLs used `/novel/<slug>` | **Shut down as of the 15 November live check**; its successor NovelCodex is explicitly a chapter-free tracking site | **No live chapter downloader**; historical saved HTML may still be tested offline |
| Light Novel World / old lightnovelpub.org | `lightnovelpub.org` now explicitly says it has shut down and migrated to chikari.moe | It is not interchangeable with `lightnovelpub.com`; the new service is not established as a chapter source | Reject the retired domain rather than silently redirecting or assuming equivalence |

Public source references checked:

- Novel Fire sample book: https://novelfire.net/book/martial-world
- Novel Fire numbered catalogue: https://novelfire.net/book/martial-world/chapters
- Novel Fire terms: https://novelfire.net/page/terms-of-service
- Former Light Novel Pub (shutdown notice): https://lightnovelpub.com/
- Successor tracking-only site: https://www.novelcodex.com/
- Old Light Novel World shutdown notice: https://lightnovelpub.org/

The terms and website layouts can change. Website reachability alone is
not proof that text can or may be downloaded.

## Implemented now

`tools/source_feasibility.py` is an **offline, non-exporting probe**. It
accepts locally saved HTML book/index pages and zero to two locally saved
chapter pages. It can validate supported public book URL shapes, extract
title, author when present, reported chapter count, synopsis availability,
two numbered chapter links, and the length/hash of a verified chapter-text
container. The report contains no chapter prose.

Example for permitted saved Novel Fire pages:

```powershell
python -m tools.source_feasibility "https://novelfire.net/book/martial-world" --book-html "book.html" --index-html "chapters.html" --report "novelfire-feasibility.json"
```

To inspect up to two chapters **only if permitted and already saved**:

```powershell
python -m tools.source_feasibility "https://novelfire.net/book/martial-world" --book-html "book.html" --index-html "chapters.html" --chapter-html "chapter1.html" --chapter-html "chapter2.html" --confirm-rights
```

For Light Novel Pub, **use only HTML saved before the shutdown**, with a historically valid `https://lightnovelpub.com/novel/<slug>` as provenance. Its current site no longer hosts chapters. Do not attempt new live downloads or treat cached HTML as proof of present-day access.
The tool never requests websites and cannot bypass login/challenges.

## Acceptance criteria before any full downloader

1. Verify an authorised, reachable novel information page and source-specific
   chapter index, with the correct reported chapter count and ordering.
2. Validate exactly two publicly accessible permitted chapters, keeping
   chapter text free of navigation/ads and detecting truncation/locked pages.
3. Check the site's permissions and operational access without evasion.
4. Preserve the exact expected ZIP/EPUB/TXT/metadata/cover schema, including
   synopsis, positions, title, author, hashes and failed-chapter reporting.
5. Add offline fixture-based unit tests on Linux/Windows and a separate
   optional live two-chapter smoke test only when access is permitted.
6. Only then introduce a new, isolated website-specific Actions workflow;
   do not extend an existing NovelFull/FreeWebNovel workflow with unverified
   selectors or backend logic.

Because these conditions are not yet met, current support is **offline
feasibility rather than automated downloads**.


## WTR-Lab and Royal Road: current safe integration

Neither source has been added to live automated downloads. Their source
policies and permissions must be respected.

### WTR-Lab

- Novel URLs now include `https://wtr-lab.com/en/novel/6965/myriad-paths`;
  example chapters use a following `/chapter-1` path.
- Its official Terms restrict automated requests and downloading or
  copying site content unless expressly permitted.
- AI-translated chapters may be ticket-locked. The first 50 chapters can
  initially be unlocked; that is not an export permission.
- Do not use login automation, internal APIs, paywall workarounds or
  harvesting of locked AI content.

Sources:
https://wtr-lab.com/en/terms-of-use
https://wtr-lab.com/en/faq/2/chapter-unlock-system
https://wtr-lab.com/en/news/115

### Royal Road

- Book URLs use `/fiction/<id>/<slug>`. Chapter URLs use
  `/fiction/<id>/<slug>/chapter/<chapter-id>/<chapter-slug>`.
- Chapter IDs are *not* reading positions. Our offline feasibility parser
  preserves the supplied table-of-contents order instead of sorting IDs.
- FanFicFare 4.63 contains an actively maintained Royal Road adapter.
  This does not itself establish permission to crawl or archive content.
- Royal Road's Author Premium allows authors to export EPUBs of their
  own fiction from the author dashboard.

Sources:
https://github.com/JimmXinu/FanFicFare/releases
https://www.royalroad.com/support/knowledgebase/110
https://www.royalroad.com/support/knowledgebase/108

### Offline feasibility

`tools/source_feasibility.py` now supports NovelFire, LightNovelPub,
WTRLab and RoyalRoad URL formats, using only HTML that was already
saved through permitted means. The parser checks the book title,
author where present, chapter list and up to two saved chapter pages
without outputting prose or contacting sites.

~~~powershell
python -m tools.source_feasibility "https://wtr-lab.com/en/novel/6965/myriad-paths" --book-html "book.html" --index-html "chapters.html"
python -m tools.source_feasibility "https://royalroad.com/fiction/21220/mother-of-learning" --book-html "book.html" --index-html "chapters.html"
~~~

### Convert an already-authorised EPUB to a proper novel ZIP

`tools/import_local_epub.py` packages a locally provided EPUB into the
same portable structure as our existing novel ZIPs. It reuses the
existing tested EPUB exporter, then verifies ZIP CRC, chapter SHA-256,
chapter count, source metadata and optional cover before publication.
The input EPUB is never modified; existing output ZIPs are not
overwritten unless `--replace` is explicit.

~~~powershell
python -m tools.import_local_epub --epub "My Author Export.epub" --source-url "https://royalroad.com/fiction/21220/mother-of-learning" --output-dir Imported_Novels --confirm-rights
python -m tools.import_local_epub --epub "My Permitted Export.epub" --source-url "https://wtr-lab.com/en/novel/6965/myriad-paths" --output-dir Imported_Novels --confirm-rights
~~~

The examples illustrate file conversion for content you are permitted to
keep, **not** permission to archive those example novels. The tool never
downloads the EPUB or any chapters. A new WTR-Lab or Royal Road bulk option
is deliberately disabled until reliable, permitted access is confirmed.

## Scribble Hub feasibility

**Last tested:** 14 November 2026. **Status: not enabled for automated downloads.**

The repository's pinned `FanFicFare 4.63.0` already includes a Scribble Hub adapter for `https://www.scribblehub.com/series/<id>/<slug>/` URLs. It reads the public book page and requests the site's chapter table of contents via a `POST` to `/wp-admin/admin-ajax.php`.

We ran an **isolated, metadata-only diagnostic** on a GitHub Actions Ubuntu runner using the repository's pinned dependencies. The test targeted the publicly listed series:

`https://www.scribblehub.com/series/2677327/blueflame-the-starless-king/`

Results:

1. **PASS:** ScribbleHubComAdapter's source URL pattern matched the series ID `2677327`.
2. **FAIL:** FanFicFare `--non-interactive --meta-only --json-meta --no-output` reported **HTTP 403 Forbidden**. There was no verified chapter count.
3. **NOT ATTEMPTED:** live chapter-body downloads, two-chapter EPUB/ZIP output, full-novel batch integration or downloads requiring user authorisation.
4. **PRESERVED:** NovelFull, FreeWebNovel, the unified bulk workflow, real book files and the completed-download registry.

**Evidence:** [Actions diagnostic run #43567663190](https://github.com/RichardDaffern/Novel_Library/actions/runs/43567663190). Its probe step used `continue-on-error` for diagnostic purposes: that run's eventual overall conclusion does not establish Scribble Hub success. The probe suppressed raw stdout/stderr content and reported the **403 error category** only, so the exact failing request (first public book GET versus the table-of-contents AJAX POST) remains unproven.

**Additional references:** [FanFicFare issue #1353](https://github.com/JimmXinu/FanFicFare/issues/1353) and [issue #1397](https://github.com/JimmXinu/FanFicFare/issues/1397) document earlier 403/access-challenge problems and periods of recovery. Scribble Hub's [Terms of Service](https://www.scribblehub.com/terms-of-service/) contain no blanket grant to archive other authors' novels.

**Decision:** keep the source unavailable in the normal Actions and Library - Bulk Download menus. Do not retry rejected requests through proxies or access-control workarounds. Reconsider only with documented permission, permitted accessible public metadata and chapter samples, and deterministic source-specific regression coverage. An already-authorised Scribble Hub EPUB can be converted to a validated novel ZIP using `tools/import_local_epub.py`, without contacting Scribble Hub. The CLI retains the numeric series ID as the ZIP identity. This does not establish full website-download support.

See [website support](WEBSITE_SUPPORT.md#scribble-hub) for the concise support decision.

### Follow-up diagnostics, 14 November 2026

The extra test plan separated public series metadata from RSS and chapter-index retrieval, without trying to bypass the earlier HTTP 403.

- **GitHub Actions ordinary GET for `/robots.txt`: HTTP 403.** The diagnostic immediately stopped, making **zero further requests** to series, RSS, chapter indexes, or novel content. We cannot infer the actual site rules from a rejected robots response.
- **Six synthetic offline regression tests:** installed FanFicFare 4.63.0 recognises Scribble Hub series and chapter URLs; a synthetic book and AJAX chapter-index response produce the expected story fields and chapter links; an invented chapter body can be extracted; a simulated access-denied page is not accepted as a valid chapter; the active combined bulk planner continues rejecting Scribble Hub; and a two-chapter synthetic EPUB can be exported with correct TXT, metadata, ordering and SHA-256.
- **Windows-specific integration discovery:** before correction, the general EPUB exporter wrote CRLF chapter bytes while hashing LF content, causing a manifest mismatch. Fixed independently for the normal exporter and FreeWebNovel in [PR #132](https://github.com/RichardDaffern/Novel_Library/pull/132), with byte-accurate Linux/Windows regression coverage. This was **not** a live Scribble Hub issue.
- **Evidence:** [HTTP 403 robots diagnostic run #43569079591](https://github.com/RichardDaffern/Novel_Library/actions/runs/43569079591); [subsequent synthetic Linux/Windows pass #43569472284](https://github.com/RichardDaffern/Novel_Library/actions/runs/43569472284). There were no authorised chapter downloads or source-site text logs.

**Direct-site blocker remains:** GitHub Actions still has not passed permitted live Scribble Hub metadata discovery, so no *general Scribble Hub website downloader* is enabled. However, on 14 November 2026 the author MonkWithAPen's independently posted FanFiction.net work `14031894` was verified through the documented FicHub API: title, author and 432 story chapters matched, and an EPUB was fetched and inspected on a temporary runner. It contained two preliminary readable sections plus 432 story chapters. The new `tools/verified_crosspost_download.py` accepts only the registered Scribble Hub series ID `445037` and downloads the author's same-title cross-post through FicHub, validating completeness before ZIP publication. It requires `--confirm-rights`. This is **not general Scribble Hub support**. Alternatively, `python -m tools.import_local_epub` remains available for an EPUB the user already holds with permission.

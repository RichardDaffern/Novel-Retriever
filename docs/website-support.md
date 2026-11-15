# Website support and download capabilities

> **Maintained against the Novel_Library implementation, 15 November 2026.** This page describes **which sources this repository can download from**, versus which it can only investigate or import from pre-existing files. Website access and authorisation can change; the presence of code is not a guarantee that a particular live novel downloads successfully.

Back to the [README](../README.md) · [Detailed download guide](download-guide.md) · [Experimental source research](research/experimental-sources.md) · [New-source feasibility](research/source-feasibility-2026-11-15.md) · [Live HTTP-200 tests](research/live-http-200-source-tests-2026-11-15.md)

## At a glance

| Website | Full website download available? | Supported operation | Where |
| --- | --- | --- | --- |
| **NovelFull** (`novelfull.com`) | **Yes** | FanFicFare-powered single or bulk chapter-range downloads; verified whole-book EPUB assembly | [NovelFull workflow](../.github/workflows/download-novel.yml), [bulk workflow](../.github/workflows/library-bulk-download.yml) |
| **FreeWebNovel** (`freewebnovel.com`) | **Yes**, accessible public chapters only | Dedicated sequential downloader; validated range assembly, single or bulk | [FreeWebNovel workflow](../.github/workflows/freewebnovel-download.yml), [bulk workflow](../.github/workflows/library-bulk-download.yml) |
| **ReadNovelFull** (`readnovelfull.com`) | **Implemented, live full-book test pending** | Exact AJAX chapter catalogue; verified single/range/bulk EPUB downloads | [ReadNovelFull workflow](../.github/workflows/readnovelfull-download.yml), [bulk workflow](../.github/workflows/library-bulk-download.yml) |
| **WuxiaClick** (`wuxia.click`) | **Bounded downloads only (max 20 chapters per run)** | Paginated exact TOC, rights gate, verified EPUB/TXT ranges; full-book archiving disabled | [WuxiaClick workflow](../.github/workflows/wuxiaclick-download.yml), [bulk workflow](../.github/workflows/library-bulk-download.yml) |
| **Scribble Hub** (`scribblehub.com`) | **One verified cross-post via GitHub Actions**, not general Scribble Hub website access | [Scribble Hub - Download](../.github/workflows/scribblehub-download.yml) or the [unified bulk workflow](../.github/workflows/library-bulk-download.yml), for registered same-author cross-posts only; authorised offline EPUB import | [Cross-post details](#scribble-hub) |
| **WebNovel** (`webnovel.com`) | **No** | Book metadata probe, at most two public test chapters where accessible; offline saved-HTML/TXT/JSON imports | [WebNovel probes and import tools](#webnovel) |
| **Royal Road** (`royalroad.com`) | **No enabled website-download workflow** | Convert an already-authorised local EPUB; offline saved-page feasibility | [Local EPUB importer](../tools/import_local_epub.py) |
| **WTR-Lab** (`wtr-lab.com`) | **No** | Convert an already-authorised local EPUB; offline saved-page feasibility | [Local EPUB importer](../tools/import_local_epub.py) |
| **Novel Fire** (`novelfire.net`) | **No** | Offline analysis of saved HTML (book, index and up to two chapters) | [Feasibility tool](../tools/source_feasibility.py) |
| **Light Novel Pub** (`lightnovelpub.com`) | **No, service shut down** | Historical **saved HTML only**; successor NovelCodex does not host chapters | [Updated research](research/source-feasibility-2026-11-15.md) |

**Meaning of “Yes”:** an actual chapter-fetching and complete-book assembly workflow exists in this repository. It does **not** mean all titles are currently reachable, have consecutive readable chapters, or are authorised for archiving. In particular, FreeWebNovel's original public two-chapter test was verified on 10 November 2026; a complete live full-book run was **not established by that test**.

**FanFicFare note:** its dependency contains additional site adapters, including Royal Road, but this project's existing hosted download workflows have only been configured for the three full-download websites above, with the new ReadNovelFull parser implemented separately (not via FanFicFare). Do not label every FanFicFare adapter a supported website in the project's Actions menus.

## Full-download websites

### NovelFull

- **Website:** https://novelfull.com/
- **Typical book URL:** `https://novelfull.com/<title-slug>.html`
- **Single-book Action:** **NovelFull - Download**
- **Bulk Action:** **Library - Bulk Download** (NovelFull links auto-detected)
- **Direct CLI:** `python -u novel_downloader.py "<authorised-https-book-url>" --confirm-rights`
- **Implementation:** [`novel_downloader.py`](../novel_downloader.py), [`fanficfare_progress_runner.py`](../fanficfare_progress_runner.py), [`tools/chunked_download.py`](../tools/chunked_download.py).

FanFicFare supplies a supported-site book reader. The Actions pipeline discovers the chapter count, splits the selected inclusive range into normally **200-chapter batches**, and adapts concurrency up to six workers. Only complete, source-matched pieces with all expected positions and valid chapter hashes may be reused or assembled. The final EPUB is checked against the TXT chapter collection.

Each successful novel produces a temporary GitHub Actions artefact and a **metadata-only** registry update in [`downloaded_novels.json`](../downloaded_novels.json). Downloaded content does not become a Git-tracked file. The source EPUB may also supply a synopsis, genre, status and cover; genuinely absent metadata is left absent.

**Caveat:** the direct CLI cannot prove a whole book is complete without an authoritative expected chapter count (use `--expected-chapters` or the bounded Actions workflow). FanFicFare's site adapters depend on the remote site's current layout. The workflow can fail cleanly if a source changes.

### FreeWebNovel

- **Website:** https://freewebnovel.com/
- **Typical book URL:** `https://freewebnovel.com/novel/<title-slug>`
- **Single-book Action:** **FreeWebNovel - Download**
- **Bulk Action:** **Library - Bulk Download** (FreeWebNovel links auto-detected)
- **Direct CLI:** `python -m tools.freewebnovel_downloader "<authorised-https-book-url>" --chapter-range 1-2 --confirm-rights`
- **Implementation:** [`tools/freewebnovel_downloader.py`](../tools/freewebnovel_downloader.py) and [`tools/freewebnovel_chunks.py`](../tools/freewebnovel_chunks.py).

**This is not a FanFicFare adapter.** The independent downloader reads only publicly available book and chapter pages. A standalone call accepts **at most 100 consecutive chapters**, while its Actions workflow normally uses **50-chapter batches** and at most **two simultaneous batches** per book. Requests inside each batch are sequential, with a one-second delay.

Every chapter must be readable and correctly numbered; unexpectedly empty/short text, site-access challenges, locked pages, missing chapters and repeated chapter bodies are rejected rather than silently omitted. Output uses the shared `source.epub`, TXT chapters, manifest, metadata and optional cover conventions. Validated complete batches can be reused while artefacts are available.

**Verification caveat:** an initial live two-chapter test against *The First Order* was reported successful on 10 November 2026, but that does not establish full-book availability for the site as a whole. Site access changes or non-consecutive chapter numbering can prevent a complete download. No login, paywall, CAPTCHA or anti-bot workaround is supported.

### ReadNovelFull

- **Website:** https://readnovelfull.com/
- **Typical book URL:** `https://readnovelfull.com/<title-slug>.html`
- **Single-book Action:** **ReadNovelFull - Download**
- **Bulk Action:** **Library - Bulk Download** (ReadNovelFull links auto-detected)
- **Local range:** `python -m tools.readnovelfull_downloader "https://readnovelfull.com/cultivation-online-v3.html" --chapter-range 1-2 --confirm-rights`
- **Implementation:** `tools/readnovelfull_source.py`, `tools/readnovelfull_downloader.py`, `tools/readnovelfull_chunks.py`.

Unlike the initial book-page preview, the site's ordinary `/ajax/chapter-archive?novelId=...` endpoint provides the chapter catalogue. The parser validates exact same-source chapter links and complete consecutive positions before producing 100-chapter batches. Each batch fetches chapters sequentially with a one-second delay; at most two batches run concurrently per book and only one ReadNovelFull book is dispatched at a time from bulk. Existing EPUB/TXT/manifest checks, per-book artefacts, registry updates, partial-failure recovery and retry-only bulk selection are preserved. No login, CAPTCHA, proxy or access-challenge bypass is supported.

**Verification:** Offline fixtures cover URL safety, AJAX indexing, chapter checks, resumability, EPUB assembly and bulk routing. Live complete-book success is not yet verified. This site can change its structure or block CI requests. Do not claim all listed books are downloadable. Archive only material you have permission to store, and keep its source URL attributed in metadata.

### WuxiaClick (bounded source, not unrestricted full-book export)

- **Website:** https://wuxia.click/
- **Canonical book URL:** `https://wuxia.click/novel/<slug>`
- **Single-book Action:** [WuxiaClick - Download](../.github/workflows/wuxiaclick-download.yml)
- **Bulk Action:** **Library - Bulk Download**, automatically detects WuxiaClick URLs without a website selector
- **Local CLI:** `python -m tools.wuxiaclick_downloader "https://wuxia.click/novel/martial-world" --chapter-range 1-2 --confirm-rights`
- **Modules:** `tools/wuxiaclick_source.py`, `tools/wuxiaclick_downloader.py`, `tools/wuxiaclick_chunks.py`.

The website's [October 2026 update](https://wuxia.click/blog/pick-up-where-you-left-off) introduced an offline download allowance starting at **20 chapters per day for signed-out visitors**. The Actions pipeline enforces a **20-chapter per-run ceiling**, disallows unattended whole-book downloads exceeding that cap, uses one paced batch per novel, and requires explicit confirmation of the work's archiving rights. In the bulk workflow, WuxiaClick chapters across *all selected WuxiaClick books* must total 20 or fewer. **The tool cannot track consumption across independent runs; do not use repeat runs to exceed the site's daily allowance.** The public repository's artefacts may be accessible to others; a checkbox does not itself confer permission to redistribute copyrighted text.

The parser verifies all linked catalogue pages and their exact ordered chapter URLs rather than guessing URL numbers. Display headings can have different chapter numbers from URL suffixes, and some novels contain chapter-number gaps. The HTML reader requires `#chapter-content` and rejects missing, short, locked, repeated or mismatched chapters. Each verified range produces the existing EPUB/TXT/metadata/manifest format, with a checkpoint retained after failures. Robots restrictions, redirects, challenges and request failures stop the process. No login/session/cookie or download-allowance bypass is implemented.

**Tests:** Synthetic regression fixtures cover URL validation, missing pages, numbered offsets, EPUB assembly, checkpoint recovery and mixed source bulk planning. [Live all-page catalogue test (archived)](research/source-test-evidence-archive.md) verified 2,276 chapters for *Martial World* and 1,709 for *True Martial World*. No full-book live EPUB output has been verified or claimed.

### Single or multiple novels

Use **[Library - Bulk Download](../.github/workflows/library-bulk-download.yml)** and paste one or more supported book links into the single **Novel links** field, optionally alongside saved novel names. The source of each link is identified automatically; no website group selection is required. The former ten-novel cap is removed; GitHub allows up to **256 scheduled jobs** per run. Concurrent limits are three NovelFull, two FreeWebNovel, one ReadNovelFull, one capped WuxiaClick novel and one Scribble Hub novel. Unknown/ambiguous names and unsupported or malformed URLs fail before downloading.

This is deliberately the **only** combined bulk menu. A completed artefact recorded in the download registry is skipped unless Force is selected; previously validated chapter batches can also be reused. Details: [download guide](download-guide.md).

## Websites without full-download support

### Scribble Hub

- **Website:** https://www.scribblehub.com/
- **Typical URL:** `https://www.scribblehub.com/series/<numeric-id>/<story-slug>/`
- **Direct Scribble Hub status as tested on 14 November 2026:** **not a supported automated Scribble Hub website downloader**. Separately, one exact title is now supported via its author's verified **FanFiction.net cross-post** and the documented FicHub EPUB export API, without contacting Scribble Hub. Authorised offline EPUB imports also remain available.
- **Existing dependency support:** `fanficfare==4.63.0` includes `adapter_scribblehubcom.py`, which recognises Scribble Hub series URLs, discovers metadata and chapters through the site adapter, and extracts chapter pages when accessible. The adapter performs a POST to `/wp-admin/admin-ajax.php` during chapter-index discovery.
- **Live test:** [GitHub Actions run #43567663190](https://github.com/RichardDaffern/Novel_Library/actions/runs/43567663190), isolated branch `test/scribblehub-metadata-20261114`. The installed adapter **recognised** `https://www.scribblehub.com/series/2677327/blueflame-the-starless-king/`, but FanFicFare's metadata-only CLI returned an **HTTP 403 Forbidden** error. The diagnostic deliberately suppresses raw page contents, so this test does **not** isolate whether the 403 arose on the series-page request or the chapter-index AJAX request.
- **Initial live test boundaries:** no story chapters were requested or saved, no EPUB or ZIP was generated, no proxies/login/challenge handling were used, and no production downloader, bulk menu or registry was altered. The diagnostic step was intentionally `continue-on-error`, so a green overall Actions run must **not** be mistaken for successful Scribble Hub discovery.
- **External evidence:** upstream FanFicFare [issue #1353](https://github.com/JimmXinu/FanFicFare/issues/1353) reported a 403 on the AJAX endpoint in June 2026; [issue #1397](https://github.com/JimmXinu/FanFicFare/issues/1397) recorded an access-challenge/HTML mismatch, with a later September 2026 report of intermittent recovery. Current site access can vary.
- **Legal/permissions:** Scribble Hub's [Terms of Service](https://www.scribblehub.com/terms-of-service/) do not grant blanket permission to archive other authors' chapters. Reading a public series page does not establish permission to download and distribute its novel.
- **Further tests, 14 November 2026:** [diagnostic run #43569079591](https://github.com/RichardDaffern/Novel_Library/actions/runs/43569079591) made a single standard request for the site's `robots.txt` and received **HTTP 403**. It then **stopped** without requesting a series page, RSS feed, chapter index or chapter content. A failed robots request does not establish the site's actual robots rules; it does confirm this runner could not retrieve those rules.
- **Offline adapter checks:** six original-synthetic regression tests cover source URL recognition, site exclusion from the active bulk planner, metadata and AJAX-TOC parsing, chapter selector, error-page rejection and two-chapter EPUB/TXT/manifest construction. After correcting an independent Windows LF/CRLF file-hash bug in [PR #132](https://github.com/RichardDaffern/Novel_Library/pull/132), the isolated Linux and Windows test run [#43569472284](https://github.com/RichardDaffern/Novel_Library/actions/runs/43569472284) passed. These are **offline** fixtures and **not** evidence of successful remote chapter downloads.
- **RSS:** Scribble Hub has publicly documented RSS feeds, but they were **not** tested live from the runner after robots access was refused. RSS notifications do not by themselves prove the completeness of a novel's chapter table of contents.
- **Authorised local EPUB import (no website requests):** if you already possess a legitimately obtained EPUB, convert it with:

~~~powershell
python -m tools.import_local_epub --epub "My Authorised Book.epub" --source-url "https://www.scribblehub.com/series/2677327/blueflame-the-starless-king/" --confirm-rights
~~~

  This example URL is provenance metadata only. The command never downloads this book. It validates the EPUB's chapters, SHA-256 checksums and optional cover, and publishes a single ZIP. ZIP identity uses Scribble Hub's numeric series ID, so a changed title slug cannot silently create a duplicate novel. Existing ZIPs are preserved unless `--replace` is supplied. The provided EPUB must be authorised and complete: the converter verifies its internal consistency but cannot independently prove Scribble Hub's live chapter count.
- **Internet retrieval of one verified author cross-post:** the author **MonkWithAPen** also publishes *The Adventurous Gamer Ninja - Daichi Hekima* as FanFiction.net story **14031894**. On 14 November 2026, FicHub's API returned the correct author, title, story ID and **432 chapters**. A read-only verification fetched the resulting EPUB: it had **434 readable sections**, comprising the two expected preliminary sections followed by the **432 story chapters**. The first story chapter was *My Second Chance* and the 432nd was *Orochimaru's Contingency*. The original export was only inspected on a temporary runner and never uploaded publicly.
- **GitHub Actions without a local EPUB:** use [**Scribble Hub - Download**](https://github.com/RichardDaffern/Novel_Library/actions/workflows/scribblehub-download.yml) and the original series URL, explicitly tick the authorisation checkbox, then run it. This is a **dedicated single-novel Action**, not a second bulk menu. It checks the existing completed-download registry, uploads the validated **unnested** book folder as a seven-day artefact, and uses the existing metadata-only registry publisher. The normal Windows `Download-All-Novels.cmd` can retrieve and repackage the artefact. On a public repository, the EPUB and TXT artefacts may be accessible to others.
- **Verified internet-download command (no EPUB input), local alternative:**

~~~powershell
python -m tools.scribblehub_crosspost_downloader "https://www.scribblehub.com/series/445037/the-adventurous-gamer-ninja--daichi-hekima/" --confirm-rights
~~~

  The same registered cross-post is also available in **Library - Bulk Download** by pasting its URL alongside other supported novel links, with an explicit archiving-rights checkbox and whole-book selection. Completed artefacts survive partial bulk failures, and successful books are repackaged into a separate recovery artefact with a manifest.

  It calls only `https://fichub.net/api/v0/epub` and a validated FicHub EPUB cache URL. It does **not** fetch pages from Scribble Hub or FanFiction.net itself. It rejects unknown Scribble Hub IDs, mismatched source identity, author/title or count, unsafe returned EPUB URLs, unexpected front matter, missing checkpoint chapters and failed ZIP hashes. It never automatically retries HTTP 429 or publishes an incomplete ZIP. The ZIP goes to `Downloaded_Novels/` and can be deliberately refreshed with `--replace`. The separate, regular bulk GitHub Actions workflow is unchanged.
- **Scope:** this is a **specific author-verified cross-post**, not general Scribble Hub coverage. A FicHub cache may be temporarily unavailable or stale, and FicHub's API is explicitly unstable; a valid EPUB can only be claimed once the generated archive actually passes the full downloader's checks. Other Scribble Hub works require their own verifiable author cross-post and explicit registration in [scribblehub_verified_crossposts.json](../tools/scribblehub_verified_crossposts.json), or an EPUB you independently hold with permission.
- **Decision:** retain direct Scribble Hub **website downloading** as feasibility only. Do **not** enable arbitrary Scribble Hub series in the unified bulk downloader, launch chapter downloads, or create a production workflow on the strength of an adapter being present. A future implementation needs verified permitted access, reliable metadata and chapter discovery, two authorised chapter fixtures, and all normal archive-integrity tests. If the site refuses automated access, stop instead of attempting to evade protections.

For development background see [experimental source research](research/experimental-sources.md#scribble-hub-feasibility).

### Royal Road and WTR-Lab

For an EPUB you already hold **with authorisation**, this repository provides an offline converter:

~~~powershell
python -m tools.import_local_epub --epub "My Authorised Novel.epub" --source-url "https://royalroad.com/fiction/21220/mother-of-learning" --confirm-rights
~~~

The URL is illustrative identity metadata; the command does **not** download that book or grant permission to archive it. It reads the local EPUB, checks ZIP safety/CRC, exports chapters, creates a new `novel-<stable-url-hash>.zip` and refuses overwrite unless `--replace` is explicitly requested.

**Royal Road:** FanFicFare has an adapter and the site's author export supports some EPUB use cases, but this project's GitHub workflows do **not** offer a dedicated Royal Road source. Chapter IDs are not reading-order positions. Respect each work's permissions.

**WTR-Lab:** no automated downloader is enabled. Its published rules restrict automated requests and copying, and some chapters are locked. Offline import is possible for a user-supplied, authorised EPUB only, not for automatically collected site text.

For source-policy detail, examples, [completed 15 November 2026 GitHub-runner diagnostics](research/source-feasibility-2026-11-15.md) and offline page analysis, see [experimental-sources.md](research/experimental-sources.md).

### Novel Fire and Light Novel Pub

These sites have **offline feasibility analysis only**. [`tools/source_feasibility.py`](../tools/source_feasibility.py) can parse book information, saved chapter-index HTML and up to two saved chapters; it performs no website requests and does not produce a complete EPUB.

- **Novel Fire** (`novelfire.net`): catalogue routes have been studied, but published terms prohibit scraping/crawling without relevant permission. No chapter-download workflow exists.
- **Light Novel Pub** (`lightnovelpub.com`): **the live novel-hosting platform has shut down**. Its root now leads to a shutdown announcement; [NovelCodex](https://www.novelcodex.com/) explicitly says it does not host novels or chapters. Old saved HTML fixtures can still be analysed offline, but no live chapter-download workflow should be added.
- **Light Novel World / `lightnovelpub.org`** is not equivalent to `lightnovelpub.com`; the older site has been reported shut down. It is not supported here.

The detailed feasibility research, format observations and acceptance requirements are in [experimental-sources.md](research/experimental-sources.md).

### WebNovel

**WebNovel is not a full-book website-download source in this repository.** Its public book metadata pages may expose titles, authors and chapter counts, but this does not permit automated chapter archiving. Paid/locked chapters, login sessions and access-control bypasses are outside the supported scope.

Available **separate, constrained tools**:

| Tool | Purpose | Limitation |
| --- | --- | --- |
| [`tools/webnovel_probe.py`](../tools/webnovel_probe.py) | Inspect public book metadata | No chapter downloads; returns `chapter_export_verified: false` |
| [`tools/webnovel_http_diagnostics.py`](../tools/webnovel_http_diagnostics.py) | Inspect public-page HTTP status | No persisted chapter text |
| [`tools/webnovel_browser_probe.py`](../tools/webnovel_browser_probe.py) | Ordinary browser feasibility | At most two public chapter pages; no challenge bypass |
| [`tools/webnovel_public_two_chapter.py`](../tools/webnovel_public_two_chapter.py) | Limited public chapter export when permitted | One book page plus at most two readable chapter pages |
| [`tools/webnovel_saved_pages.py`](../tools/webnovel_saved_pages.py) | Offline import of user-saved HTML/TXT chapters | One or two chapters |
| [`tools/webnovel_export.py`](../tools/webnovel_export.py) | Offline import of user-supplied JSON chapter text | At most two chapters |
| [`tools/webnovel_bulk_import.py`](../tools/webnovel_bulk_import.py) | Offline import of consecutive saved local HTML/TXT chapters | At most 10,000; **not** a website scraper |

For example, the metadata-only probe is:

~~~powershell
python -m tools.webnovel_probe "https://www.webnovel.com/book/22196546206090805"
~~~

It does not download chapter bodies, and ordinary scripted requests have previously encountered site challenges. Offline saved-page imports require user-held files and permission; they never bypass an access restriction.

See [WebNovel browser probe](research/webnovel-browser-probe.md), [saved-page import](research/webnovel-saved-page-import.md), [bulk local import](research/webnovel-bulk-import.md), [two-chapter public probe](research/webnovel-two-chapter-sample.md), and [JSON import](research/webnovel-export.md).

## Outputs, rights and changes to site support

Supported completed-book outputs contain `metadata.json`, `chapters.json`, `source.epub`, numbered UTF-8 `chapter_*.txt` and an optional cover, generally packaged as a single-book ZIP after local Windows retrieval. The [download guide](download-guide.md) explains transient GitHub Actions artefacts, source URL identity and data-integrity checks.

To add another **live** website, first verify archiving permission, stable public chapter access, complete catalogue ordering, fail-closed extraction and offline regression coverage. Keep the existing NovelFull and FreeWebNovel paths functioning, and extend the **single** bulk menu rather than creating another competing bulk action.

**Download and store only material you have the right to archive.** Neither this project nor the presence of a site adapter authorises redistribution of novels, evasion of site protections or archiving of premium/locked content.

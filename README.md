# Novel Library

A Python toolkit for downloading **authorised** web novels, assembling complete EPUBs and numbered UTF-8 TXT chapters, and packaging them into validated novel ZIP archives. Includes GitHub Actions download workflows, a Windows artefact downloader, and offline PDF/EPUB conversion.

## Websites and download support

**Full-novel website downloading is implemented for these three sources:**

| Website | Download support | How to use |
| --- | --- | --- |
| [NovelFull](https://novelfull.com/) | **Yes**, using FanFicFare and verified chapter batches | **Library - Bulk Download** |
| [FreeWebNovel](https://freewebnovel.com/) | **Yes**, for accessible public chapters, with chapter-by-chapter validation | **Library - Bulk Download** |
| [ReadNovelFull](https://readnovelfull.com/) | **Yes, newly implemented**; full AJAX chapter catalogue, verified EPUB/TXT chapters. Live full-book success not yet established | **Library - Bulk Download** |

Other sources have restricted or specialised options, not general-purpose website downloaders:

| Website | Current capability |
| --- | --- |
| [Scribble Hub](https://www.scribblehub.com/) | **Library - Bulk Download** supports one verified author cross-post (series `445037`) through FicHub; other books need separate verification. Direct Scribble Hub requests remain blocked |
| [WebNovel](https://www.webnovel.com/) | Limited public-page tests and offline import of chapters you have saved with permission; no full website downloader |
| [Royal Road](https://www.royalroad.com/) | Offline conversion of an already-authorised local EPUB; no enabled site-download workflow |
| [WTR-Lab](https://wtr-lab.com/) | Offline conversion of an already-authorised local EPUB; no enabled site-download workflow |
| [Novel Fire](https://novelfire.net/) | Offline feasibility checks only; no website downloader |
| [Light Novel Pub](https://lightnovelpub.com/) | Offline feasibility checks only; no website downloader |

**[Website support guide](docs/WEBSITE_SUPPORT.md)** explains the supported URL formats, download limits, available workflows, current verification level and restrictions for **each** site. A working tool does not guarantee that a source currently permits or serves every novel.

## Download novels using one workflow

**[Open Library - Bulk Download](https://github.com/RichardDaffern/Novel_Library/actions/workflows/library-bulk-download.yml)**, select **Run workflow**, then:

1. Paste **one or more novel links** into **Novel links**. Separate links with spaces, commas or semicolons. You can mix NovelFull, FreeWebNovel and ReadNovelFull freely.
2. Optionally enter saved novel titles, choose a chapter range or select **Force** to redownload.
3. Click **Run workflow**. The downloader identifies the website for **each** link and routes every book automatically. **No website dropdown or manual grouping.**

Example links for the one field (illustrative):

~~~text
https://novelfull.com/the-world-online.html
https://freewebnovel.com/novel/the-first-order
https://readnovelfull.com/cultivation-online-v3.html
~~~

**One link also works.** The supported-source list is limited: unsupported links are rejected before scheduling. A verified Scribble Hub author cross-post can be included by URL, provided you tick the existing **Confirm rights** checkbox and leave Chapter range blank. The earlier ten-novel cap is removed; GitHub allows up to **256 scheduled novel jobs** per run.

If a book fails, other completed books retain their own downloadable artefacts. On partial failure, an additional `bulk-successful-novels-<run-id>` recovery bundle and a retry-only manifest are produced. Successful runs skip unnecessary repackaging. Artefacts remain available for seven days. The workflow also reports timings.


[Detailed downloading and GitHub Actions guide](docs/DOWNLOAD_GUIDE.md)

## Run locally

Requires **Python 3.12**. From the repository root:

~~~powershell
python -m pip install -r requirements.lock
python -m unittest discover -s tests -v
python -u novel_downloader.py --self-test --chapter-range 1-2
~~~

The self-test uses synthetic chapters, without requesting real novels. For an authorised, FanFicFare-supported source:

~~~powershell
python -u novel_downloader.py "https://novelfull.com/your-novel.html" --confirm-rights
~~~

Use a real supported book URL in place of the illustrative URL. For verified full-book completeness, the GitHub Actions workflows are preferable to a direct download without a known chapter count.

## Download the verified Scribble Hub cross-post

For the author's *The Adventurous Gamer Ninja - Daichi Hekima* (series `445037`), use **[Library - Bulk Download](https://github.com/RichardDaffern/Novel_Library/actions/workflows/library-bulk-download.yml)**. Paste its series URL alongside any other supported links, tick **Confirm rights**, leave Chapter range blank, and click **Run workflow**. The Action produces the same single-novel ZIP structure and registry entry as NovelFull, retrievable through `Download-All-Novels.cmd`. No local EPUB is needed.

The equivalent local command is:

~~~powershell
python -m tools.verified_crosspost_download "https://www.scribblehub.com/series/445037/the-adventurous-gamer-ninja--daichi-hekima/" --confirm-rights
~~~

Run from the Novel_Library root after installing `requirements.lock`. The CLI validates the author's cross-post, the full story count, EPUB structure and ZIP checksums, then saves a ZIP in `Downloaded_Novels/`. **Other Scribble Hub IDs are rejected unless a verified same-author cross-post is registered.** The tool does not query Scribble Hub directly or circumvent its HTTP 403. [How it works](docs/WEBSITE_SUPPORT.md#scribble-hub).

## Get completed novels onto Windows

Install [GitHub CLI](https://cli.github.com/), then double-click **[Download-All-Novels.cmd](Download-All-Novels.cmd)**. It downloads *existing* complete GitHub Actions artefacts and saves **one validated ZIP per novel** to `Downloaded_Novels/`. It does not download fresh chapters from websites; valid local ZIPs are skipped.

For offline startup validation:

~~~powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\download_all_artifacts.ps1 -CheckSetup
~~~

[Windows setup, ZIP validation, legacy repacking and troubleshooting](docs/DOWNLOAD_GUIDE.md#windows-download-completed-novels)

## Import existing books and maintain metadata

- **PDF to novel ZIP:** put authorised, selectable-text PDFs in `PDF-to-Novel/PDFs/` and run [Convert-PDFs.cmd](PDF-to-Novel/Convert-PDFs.cmd). See [PDF converter instructions](docs/PDF_TO_NOVEL.md).
- **Local EPUB to novel ZIP:** use `python -m tools.import_local_epub` for an authorised EPUB from Royal Road, WTR-Lab or Scribble Hub. See [website/import capabilities](docs/WEBSITE_SUPPORT.md#scribble-hub).
- **Covers and synopsis repairs:** see [metadata and archive maintenance](docs/METADATA_GUIDE.md).

A complete book normally contains `source.epub`, `metadata.json`, `chapters.json`, `chapter_*.txt` and an optional cover. [DOWNLOADED_NOVELS.md](DOWNLOADED_NOVELS.md) lists completed historical downloads, but its links are **not permanent storage**.

## Documentation

| Guide | Contents |
| --- | --- |
| [Supported websites](docs/WEBSITE_SUPPORT.md) | All sources, download status, URL formats, experimental limitations and offline imports |
| [Download and Windows guide](docs/DOWNLOAD_GUIDE.md) | NovelFull, unified bulk, chapter batching, artefacts, registry and Windows retrieval |
| [Metadata and archive guide](docs/METADATA_GUIDE.md) | Covers, EPUB descriptions, synopsis repair and archive safety |
| [PDF conversion](docs/PDF_TO_NOVEL.md) | PDF chapter detection, validation and manual corrections |
| [Source feasibility research](docs/experimental-sources.md) | Royal Road, WTR-Lab, Novel Fire and Light Novel Pub investigations |
| [Additional website feasibility](docs/ADDITIONAL_SOURCE_FEASIBILITY_2026-11-15.md) | WuxiaClick, AO3, NovelBuddy, LibRead, NovelHi and other new-source candidates |
| [AI agent technical handbook](AGENTS.md) | Full architecture, file contracts, implementation and development invariants |

**Only download and archive material you have permission to store.** The project does not bypass source-site restrictions. Never commit novel text, EPUBs, personal files or secrets. GitHub Actions artefacts from a public repository may be accessible to other users.

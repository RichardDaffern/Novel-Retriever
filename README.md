# Novel Library

Download and organise web novels you are authorised to archive. The toolkit builds **EPUBs, individual TXT chapters and validated ZIP archives**, with GitHub Actions for downloads and a Windows tool for collecting completed files.

## Download novels

**[Library - Bulk Download](https://github.com/RichardDaffern/Novel_Library/actions/workflows/library-bulk-download.yml)** is the shared downloader for **all supported websites**. Paste one or more novel URLs into **Novel links** and select **Run workflow**. You can mix websites in the same request; the source is detected automatically. One link works too.

### Dedicated website Actions

Prefer a dedicated Action when downloading from one particular website.

| Website | Dedicated Action | Support |
| --- | --- | --- |
| [NovelFull](https://novelfull.com/) | [NovelFull - Download](.github/workflows/download-novel.yml) | Full novels and chapter ranges |
| [FreeWebNovel](https://freewebnovel.com/) | [FreeWebNovel - Download](.github/workflows/freewebnovel-download.yml) | Accessible public chapters |
| [ReadNovelFull](https://readnovelfull.com/) | [ReadNovelFull - Download](.github/workflows/readnovelfull-download.yml) | EPUB/TXT supported; live full-book verification pending |
| [WuxiaClick](https://wuxia.click/) | [WuxiaClick - Download](.github/workflows/wuxiaclick-download.yml) | Authorised ranges of up to **20 chapters**; full-book export disabled |
| [Scribble Hub](https://www.scribblehub.com/) | [Scribble Hub - Download](.github/workflows/scribblehub-download.yml) | Only the verified author cross-post, series `445037` |

**Note:** WuxiaClick and Scribble Hub require explicit rights confirmation. Respect WuxiaClick’s daily offline-download allowance, including across separate runs. [Website restrictions and supported URL formats](docs/WEBSITE_SUPPORT.md).

## Collect completed novels on Windows

Install [GitHub CLI](https://cli.github.com/) and run **[Download-All-Novels.cmd](Download-All-Novels.cmd)**. It saves one verified ZIP per novel in `Downloaded_Novels/` and skips valid files already present.

## Run locally

Requires Python 3.12. From the repository root:

```powershell
python -m pip install -r requirements.lock
python -m unittest discover -s tests -v
python novel_downloader.py --self-test --chapter-range 1-2
```

The self-test uses invented chapters and makes no novel-site requests.

## Other tools and guides

- [PDF to novel ZIP](docs/PDF_TO_NOVEL.md) via [Convert-PDFs.cmd](PDF-to-Novel/Convert-PDFs.cmd)
- [Import an authorised local EPUB](docs/WEBSITE_SUPPORT.md) and [manage covers/metadata](docs/METADATA_GUIDE.md)
- [Download guide, chapter batching and troubleshooting](docs/DOWNLOAD_GUIDE.md)
- [Source research and unsupported sites](docs/ADDITIONAL_SOURCE_FEASIBILITY_2026-11-15.md)
- [Technical handbook for contributors and AI agents](AGENTS.md)

Only archive material you have permission to store **and share through GitHub Actions artefacts**. The toolkit does not bypass website access restrictions. Never commit novel text, EPUBs or secrets.

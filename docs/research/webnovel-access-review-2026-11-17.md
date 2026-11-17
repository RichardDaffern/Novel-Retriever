# WebNovel access and integration review, 17 November 2026

## Evidence and restrictions

- WebNovel's public home page, book pages and at least one publicly indexed
  chapter page for *Harry Potter: Platinum Dragon Wizard* were readable through
  an ordinary public web retrieval service on 17 November 2026. The book
  listing identified author BlurryPinkSnake and the current chapter catalogue.
  This is evidence of *some* public browser content, **not** of stable
  programmatic access or permission to copy an entire work.
  - https://www.webnovel.com/
  - https://www.webnovel.com/book/33422293300201205
  - https://www.webnovel.com/book/33422293300201205/91332416869817103
- Earlier real HTTP and browser probes in this repository encountered 403 and
  access restrictions. The new review did **not** reproduce those probes in a
  Python process on a GitHub runner, so their present HTTP status is
  **unverified**, not automatically still 403.
- The published Terms grant access and use of the service under a restricted
  licence and prohibit defeating service security/access controls. Public
  reading does not itself grant blanket extraction or republication rights:
  https://www.webnovel.com/terms_of_service
- No supported official general-purpose chapter export API, transferable mobile
  offline cache, or EPUB export from the **WebNovel app itself** was verified.
  Generic WebNovel Q&A answers about unrelated e-reader applications are not
  proof of a native export feature. Mobile-app encrypted/offline files were not
  inspected or decrypted. A device-level app test remains unverified.
- No automated chapter-text request through Novel Retriever or mass-download experiment was performed.
  In particular, a public page appearing in a search engine cannot verify that
  its returned HTML contains a complete, correctly ordered chapter from the
  user's own session. No API, cookie or undocumented endpoint was probed.

## Decision

| Channel | Verified or supported outcome |
| --- | --- |
| Public book metadata | Present on publicly visible book pages; existing metadata probe retained |
| Public chapter browsing | Selected indexed chapter content is visible via ordinary public web retrieval; completeness across successive pages and automation are unverified |
| Locked chapters | No extraction, unlocking or access-control bypass |
| WebNovel mobile app | In-app reading/offline support does not imply export permission; native export unverified |
| Full website downloading | Not enabled; rights and operational reliability not demonstrated |
| Local saved HTML/TXT | Existing resumable 10,000-chapter importer retained and expanded with a separately verifiable ZIP path |
| Covers | Optional user-supplied image only, with format/dimensions validated; authenticity not independently verified |
| GitHub Actions | No misleading remote download workflow or public chapter artefact upload |
| Private Storage Controller | ZIP layout matches its actual original.zip reader's expected source.epub, metadata.json and chapters.json, with chapter hashes and cover |

## Practical offline workflow

1. Obtain authorised local HTML/TXT pages through a normal supported method;
   WebNovel's offline app cache is not an interchangeable file export.
2. Preview and import consecutive saved chapters with
   `python -m tools.webnovel_bulk_import --dry-run`, then import normally.
3. Use `--storage-zip --source-url https://www.webnovel.com/book/<id>` to build
   a validated one-book ZIP in a local Downloaded_Novels directory.
4. Run the Storage Controller's **read-only preview**. Do not automatically
   upload to Hugging Face or commit the resulting copyrighted content to Git.

The ZIP creator verifies checkpointed source and output hashes, chapter
continuity, duplicate chapter bodies, XHTML-to-TXT content equality, ZIP/EPUB
CRC, source identity, size limits and an optional validated portrait image.
It refuses existing packages rather than replacing them. Genuine source cover
ownership and full source-book completeness remain external assertions.

**Further work is permission-gated:** only revisit automated website
downloading after obtaining a supported provider export contract or explicit
authorisation and proving stable complete pages over several controlled runs.


---

# WebNovel free-access trial: *Harry Potter: Platinum Dragon Wizard*

Checked on 17 November 2026. Book:
https://www.webnovel.com/book/33422293300201205

## Public website observations

- Public book catalogue lists **884 chapters**, author **BlurryPinkSnake**.
- The final entry (Chapter 884) is a conclusion/translator's note that says
  the story is over, rather than an additional normal story chapter.
- Ordinary public reading returned visible story prose for Chapters **1, 2,
  400, and 844**, with no sign-in or coin-purchase prompt on those sampled
  pages. The final editorial Chapter 884 was also publicly readable.
- There was no lock/VIP marker in the publicly rendered catalogue inspected.
  **This does not certify every single chapter is completely free.**
- Public book metadata and accessible rendered pages do not establish that
  GitHub Actions / Python HTTP access works. Earlier runner/browser probes
  encountered 403 and challenges.

Sample pages:
- https://www.webnovel.com/book/33422293300201205/89735050081387238
- https://www.webnovel.com/book/33422293300201205/89735050081387259
- https://www.webnovel.com/book/33422293300201205/94052948610440202
- https://www.webnovel.com/book/33422293300201205/98111515671985466
- https://www.webnovel.com/book/33422293300201205/98111572043430550

## Runner trial and source permission

The repository now has a **read-only** diagnostic:
\`python -m tools.webnovel_access_check\`, available in
[WebNovel - Public Access Diagnostic](../../.github/workflows/webnovel-public-access.yml).

The workflow makes at most four HTTPS requests for this particular book:
the book page and Chapters 1, 400 and 844. It verifies presence of a readable
body using the existing conservative WebNovel page parser; it reports only
metadata, word/character counts, sample statuses and safe error labels.
It does not persist or publish copyrighted prose, cookies, HTML, or EPUBs.
It stops immediately on HTTP 403/429, locked chapters, access challenges,
missing content or unknown page structures. It does not spoof a browser,
authenticate, retry, solve CAPTCHAs or use undocumented endpoints.

The output key \`outcome\` must be inspected. Green workflow execution means
**the diagnostic ran**, not that its sample pages passed. A failure to reach
WebNovel from a GitHub runner must not be mistaken for a Python code defect.

**Important licence distinction:** public/free reading is different from
permission to reproduce/export the work. WebNovel's
[terms](https://www.webnovel.com/terms_of_service) limit the right to use
site materials. This trial does not authorise mass downloading. No bulk website
source or individual full-book download workflow has been enabled.

If the author or platform provides an authorised EPUB or chapter export,
the existing local importer and Storage Controller ZIP packager support it
without contacting WebNovel or committing story text.

## Verified GitHub runner outcome, 17 November 2026

[Read-only GitHub Actions trial #44113781154](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44113781154) installed the pinned dependencies, passed all **12 offline regression tests**, and then made one ordinary HTTPS GET to the WebNovel book URL. WebNovel responded with **HTTP 403 Forbidden**. The diagnostic reported:

~~~json
{"outcome":"blocked","requested_samples":3,"samples":[],"reason":"HTTP_403_access_denied","complete_novel_download_verified":false}
~~~

Because the catalogue request failed, **no chapter requests were sent** from GitHub Actions. The workflow's green result means the *diagnostic handled the denial safely*, not that direct WebNovel downloading works. Do not restart this check repeatedly or work around the access restriction. For this book, only existing local saved-page import remains supported.


## Windows local-browser feasibility check (read-only)

Run [`WebNovel-Check-Local-Browser.cmd`](../../WebNovel-Check-Local-Browser.cmd)
**on your own Windows computer** using the current Novel-Retriever checkout.
This is not a GitHub Actions workflow and was not run on the user's Windows PC.

Install optional browser dependencies once from the repository root:

```powershell
py -m pip install playwright
py -m playwright install chromium
```

The launcher opens unmodified, visible Chromium with a fresh temporary context.
It checks the book listing and three explicitly validated public chapters
(1, 400 and 844), and returns only public metadata, per-chapter word/character
counts, and an explicit `outcome` code. It requests no more than four pages;
any HTTP 403/429, challenge, redirect, locked or unreadable page stops the
trial immediately. No chapters, HTML, cookies, screenshots or ZIPs are saved;
no existing browser profile, login, proxies, hidden APIs, CAPTCHA-solving
or retry loops are used.

The tool can also be invoked for another book using the command:

```powershell
py -m tools.webnovel_local_browser_diagnostic --book-url "https://www.webnovel.com/book/33422293300201205" --sample "1=https://www.webnovel.com/book/33422293300201205/89735050081387238"
```

`sampled_public_readable` means only that the selected pages were readable
in this temporary browser on that computer. It does **not** verify that 884
chapters are free, that an automatic downloader works, or that reproduction
of any chapter is permitted. The website's terms govern use of materials.
If any access restriction occurs, stop: do not attempt to bypass it.

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
- No new chapter-text request or mass-download experiment was performed.
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
| Covers | Optional genuine local image only, with format/dimensions validated and provenance clearly flagged as user supplied |
| GitHub Actions | No misleading remote download workflow or public chapter artefact upload |
| Private Storage Controller | ZIP layout matches its actual original.zip reader's expected source.epub, metadata.json and chapters.json, with chapter hashes and cover |

## Practical offline workflow

1. Obtain authorised local HTML/TXT pages through a normal supported method;
   WebNovel's offline app cache is not an interchangeable file export.
2. Preview and import consecutive saved chapters with
   \`python -m tools.webnovel_bulk_import --dry-run\`, then import normally.
3. Use \`--storage-zip --source-url https://www.webnovel.com/book/<id>\` to build
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

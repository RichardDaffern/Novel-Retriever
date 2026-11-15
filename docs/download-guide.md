# Downloading novels, GitHub Actions and Windows retrieval

This is the detailed operating guide moved out of the short [README](../README.md). For the authoritative list of available websites and their restrictions, see [Website support](website-support.md). For covers, synopsis repairs and archive metadata, see [Metadata maintenance](metadata-guide.md).

**Archiving rights and privacy:** Download only material you may archive. Site access restrictions are not bypassed. Novel text and EPUBs are not committed to this repository. Actions artefacts on a public GitHub repository may be accessible to other users.


## Run locally

Install Python 3.12 and the dependencies:

~~~powershell
python -m pip install -r requirements.lock
python -m unittest discover -s tests -v
~~~

Test the download-to-EPUB pipeline without external network requests:

~~~powershell
python novel_downloader.py --self-test --chapter-range 1-2
~~~

For material you are authorised to download, use a supported HTTPS URL:

~~~powershell
python -u novel_downloader.py "https://example.org/novel" --confirm-rights
python -u novel_downloader.py "https://example.org/novel" --confirm-rights --chapter-range 1-30
~~~

The standalone downloader uses a readable folder name plus a source-URL digest so unrelated novels with the same last URL segment cannot collide. When using an explicit `--slug`, an existing EPUB is reused only if its `metadata.json` records the same source URL. Unverified legacy EPUBs are not silently reused; choose `--overwrite` to fetch again. Two imported EPUBs with the same title require a different `--slug`, or an explicit `--overwrite` if replacement is intended.

For direct whole-book downloads, `--expected-chapters N` rejects incomplete results **before publishing**. Without an authoritative count, the direct CLI warns that it cannot prove completeness; the GitHub Actions batch workflow already discovers and validates the whole novel's chapter count.

Exports are prepared in a sibling staging directory, and prior exports are backed up during replacement. Failed writes roll back, and interrupted backups are recovered on the next export invocation. A short rename gap can occur during a process crash; this is a recoverable swap rather than a truly atomic multi-file filesystem transaction.

Chapter ranges are one-based, inclusive positions in the site's chapter index. The script prints a chapter-completion percentage and writes a TXT file into the chapters_in_progress directory as soon as each chapter finishes. After successful EPUB creation, it exports the final chapters, manifest and metadata and removes temporary checkpoints.

## Reproducible Python installs

CI and GitHub download workflows use `requirements.lock`; the PDF converter uses `requirements-pdf.lock`. Both pin direct and transitive package versions resolved with Python 3.12. Local development can use the original `requirements.txt` / `requirements-pdf.txt` when intentionally upgrading dependencies, but ordinary users should install from the locks. Regenerate and commit locks after testing deliberate dependency updates. The lockfiles pin versions, not wheel hashes.

The PDF converter also limits input to 1 GiB and 50,000 pages by default. Its file hashing and ZIP chapter-member writing avoid whole-document duplicate byte buffers; PDF page analysis and EPUB construction still require memory proportional to novel size.

## Verified Scribble Hub author cross-post: direct internet retrieval

This is a **special-case, verified author cross-post**, not a generic Scribble Hub scraper or a new bulk workflow. Scribble Hub's HTTP 403 blocked direct GitHub Actions retrieval, but the author MonkWithAPen has independently posted the same title as FanFiction.net work `14031894`. FicHub explicitly documents an EPUB export API for FanFiction.net stories and requests serial calls, a project User-Agent and respect for HTTP 429.

**Recommended GitHub Actions workflow:** open [Scribble Hub - Download](https://github.com/RichardDaffern/Novel_Library/actions/workflows/scribblehub-download.yml), choose **Run workflow**, enter the Scribble Hub URL (currently series `445037` only), tick **I confirm that I have permission to archive this work**, and start the run. **Force** bypasses an existing unexpired registry entry; otherwise the Action skips already available downloads.

The Action fetches the registered same-author FanFiction.net cross-post through FicHub and validates all chapters. It then exposes **one novel folder** in the GitHub Actions artefact ZIP, with `source.epub`, `metadata.json`, `chapters.json`, numbered UTF-8 chapter files, and optional cover. No ZIP-inside-ZIP nesting. The finished artefact is retained for **seven days** and registered in `downloaded_novels.json` through the normal metadata-only PR process. Use **Download-All-Novels.cmd** to save it as a normal reader-compatible ZIP. As with NovelFull, **public repository artefacts can be accessed by other people**, so only run this when permitted to archive and potentially share the content.

**Local alternative:** from the **Novel_Library root** on Windows, after `python -m pip install -r requirements.lock`:

~~~cmd
python -m tools.scribblehub_crosspost_downloader "https://www.scribblehub.com/series/445037/the-adventurous-gamer-ninja--daichi-hekima/" --confirm-rights
~~~

The Action and local command use `tools/scribblehub_verified_crossposts.json` to match the numeric Scribble Hub ID to the exact same-author FanFiction.net work. It retrieves the source EPUB from FicHub's documented API, verifies the source identity and chapter count, removes only recognised non-story EPUB front matter, and reuses the atomic `tools.import_local_epub` writer to produce a fully validated `Downloaded_Novels/novel-<stable-ID>.zip`. There is **no need to have an EPUB beforehand**. The raw downloaded EPUB and temporary chapters are removed after the final ZIP validates.

Use `--replace` only for deliberate updates. An existing ZIP is not overwritten automatically. This method does **not** work for arbitrary Scribble Hub IDs; those fail closed rather than guessing an unrelated cross-post. It does not bypass the source site's challenge or read protected/premium chapters. Use only when you have permission to archive the work.

**Troubleshooting FicHub errors:** FicHub's unstable export API sometimes returns HTTP 200 with a nonzero `err` field. A failed workflow must show its numeric `err` (and numeric `ret`, if provided), not the provider's raw untrusted message. `err=-7` means the provider has restricted exports for the work: stop and do not bypass or retry. Other codes can reflect transient service failures or unavailable source content; if appropriate, retry manually later, rather than launching frequent automated attempts. The workflow never uploads a partial novel. On 14 November 2026 [run #43587232385](https://github.com/RichardDaffern/Novel_Library/actions/runs/43587232385) failed at FicHub's export, while a separate same-URL diagnostic returned `err=0`. The original failure did not log an error code, so its specific upstream cause is unknown.

Technical constraints: one FicHub API request and one EPUB request, **no concurrent calls and no automatic retries**; reject HTTP 429/redirects and unrecognised paths; check original title/author/FFN ID against registered values, preserve stable Scribble Hub numeric-series identity, and verify each chapter's byte-level SHA-256, EPUB chapter count and final ZIP CRC before publication.

See the [website capability matrix](website-support.md#scribble-hub) and [offline tests](../tests/test_scribblehub_crosspost_downloader.py).

## GitHub Actions: NovelFull - Download

The NovelFull single-download workflow uses FanFicFare. The separate `CI` workflow runs automatic regression checks and is not a downloadable-novel action.

In **Actions > NovelFull - Download > Run workflow**, enter:

- **Novel URL**: the source URL
- **Chapter range**: optional, e.g. 1-30; blank requests the whole novel
- **Force**: defaults to **off**; select it to bypass the downloaded-novel registry

There is no permission-confirmation checkbox in the Actions form; the workflow passes the script's local --confirm-rights flag internally. Only run authorised downloads.

The workflow checks downloaded_novels.json **before downloading chapters**. It then discovers the full chapter count and divides the requested range into automatically managed batches of **up to 200 chapters**, with **1 to 6 concurrent chapter-download jobs**, calculated from the selected chapter count: one worker per 600 chapters (rounded up), never more than six or the available number of batches. Each batch has its own timeout, so a 4,000-chapter novel is no longer limited by a single 170-minute process. A rerun automatically **reuses complete verified batch artifacts** that have not expired, and downloads only missing or failed batches unless Force is selected. If a batch times out, its temporary chapter checkpoints are uploaded separately, but the incomplete batch is retried on the next run. No partially downloaded book is registered as complete. A completed download is treated as available only while its GitHub Actions artifact has not expired. A full-novel entry covers all smaller ranges; combined completed ranges can also cover a requested range. If already available, the workflow exits successfully with an **Already downloaded** notice. Force bypasses that check. Different novel URLs can run in separate workflows concurrently. Duplicate runs for the same URL queue instead of interrupting an active download. Each completed novel's registry PR is regenerated from the latest `main` and retried on merge conflicts, so simultaneous novels do not overwrite each other's records.

When all batches are complete, an assembly job verifies every selected chapter position, creates **one complete EPUB** and numbered TXT collection, and uploads them as a final artifact retained for **seven days**. Verified intermediate batches also have seven-day retention. The first run using the new workflow cannot automatically reuse the checkpoints from the older, pre-chunking timeout run. The novel content is not committed to the repository. Partial checkpoints may also be uploaded when downloads fail.

After uploading and validating the output, the workflow:

1. Adds the download metadata, range, chapter count, run link and artifact-expiry information to downloaded_novels.json.
2. Regenerates [DOWNLOADED_NOVELS.md](../DOWNLOADED_NOVELS.md), the human-readable index.
3. Regenerates the registry from the latest `main`, then creates a per-novel registry branch and pull request.
4. Attempts to **squash-merge that metadata-only PR into main** automatically; concurrent PR conflicts trigger a fresh registry build and another merge attempt.

For automatic PR creation and merging, the repository owner must enable **Settings > Actions > General > Workflow permissions > Allow GitHub Actions to create and approve pull requests**. The workflow token also needs contents and pull-requests write access, configured in the workflow. Without the repository setting, GitHub rejects PR creation even with YAML write permissions. The chapter/EPUB artifact remains downloadable, and the metadata-only branch is retained with a manual PR link in the job summary. Branch protection requiring approvals or status checks can also prevent automatic merging.

**Important:** Your repository is currently public. GitHub Actions artifacts may be accessible to other users of public repositories. Making a repository private limits exposure but does not grant permission to redistribute copyrighted content.

## FreeWebNovel - Download

The dedicated FreeWebNovel workflow handles a single novel; the unified bulk workflow handles multiple titles from NovelFull, FreeWebNovel and explicitly verified Scribble Hub author cross-posts. This is **not** the NovelFull FanFicFare adapter. Its Actions workflow splits work into normally 50-chapter batches, accepts only publicly readable chapters, verifies chapter content and positions, and does not bypass access challenges.

Read the full [FreeWebNovel capability and limitations](website-support.md#freewebnovel) before running it.

## ReadNovelFull - Download

Use [ReadNovelFull - Download](https://github.com/RichardDaffern/Novel_Library/actions/workflows/readnovelfull-download.yml) for an authorised novel URL such as `https://readnovelfull.com/cultivation-online-v3.html`. Leave **Chapter range** blank for the whole novel, or enter `1-2` for two chapters. The workflow discovers the complete chapter list via the site's public AJAX chapter archive (the initial book page exposes only a subset), then uses the exact chapter links, never guessed slugs.

Each chapter range is downloaded sequentially with a one-second delay between chapter requests; batches are at most **100 chapters**, with at most **two batches per book**. The unified bulk workflow schedules at most **one ReadNovelFull novel at a time**. Missing or mismatched chapters, access challenges and invalid EPUBs stop publication. Complete verified chapter-batch artefacts can be reused; failed chapters remain recoverable by rerunning. Output has the same EPUB/TXT/manifests/cover layout as the other websites.

**Important:** The parser is covered by offline tests, but a complete live download has not yet been proven. Website layout and access restrictions can change. No login, Cloudflare or CAPTCHA bypass is performed. The Action is for content you have permission to archive. For local authorised ranges, after installing `requirements.lock`, run:

~~~powershell
python -m tools.readnovelfull_downloader "https://readnovelfull.com/cultivation-online-v3.html" --chapter-range 1-2 --confirm-rights
~~~

## WuxiaClick - Download (authorised, bounded ranges)

Use [WuxiaClick - Download](https://github.com/RichardDaffern/Novel_Library/actions/workflows/wuxiaclick-download.yml) to download an authorised range, for example from `https://wuxia.click/novel/martial-world`. Enter `1-2` or another inclusive range of **at most 20 chapters**, and explicitly tick **Confirm rights**. The website has a [daily offline-download allowance starting at 20 chapters for signed-out users](https://wuxia.click/blog/pick-up-where-you-left-off). This tool caps one job at 20 chapters but does **not** track cumulative usage across separate runs; respect your total daily entitlement and the rights of the work. Full-book unattended archiving is deliberately disabled.

The implementation validates all paginated `#chapters` index pages, reading order, unique exact chapter links, text headings, readable body and missing/duplicate entries before assembling an EPUB, numbered TXT chapters, metadata, manifest and optional cover. Not every URL suffix matches its displayed chapter number: for example the first URL of *Martial World* has an in-text Chapter 0, and the final chapter URL suffix may be greater than the number of indexed entries. Requests are serial, paced, robots-aware, and never bypass access controls. Failed batches preserve validated checkpoints.

**[Live catalogue verification (archived)](research/source-test-evidence-archive.md):** 2,276 indexed *Martial World* chapters and 1,709 indexed *True Martial World* chapters passed. This verifies metadata catalogue consistency, not an authorised live EPUB download. Content download acceptance depends on the user's permission and site rules.

Local authorised example:

~~~powershell
python -m pip install -r requirements.lock
python -m tools.wuxiaclick_downloader "https://wuxia.click/novel/martial-world" --chapter-range 1-2 --confirm-rights
~~~

## GitHub Actions: Library - Bulk Download

Use **[Library - Bulk Download](https://github.com/RichardDaffern/Novel_Library/actions/workflows/library-bulk-download.yml) > Run workflow** for downloads from NovelFull, FreeWebNovel, ReadNovelFull, **bounded WuxiaClick ranges** and verified Scribble Hub author cross-posts. **This is the only bulk workflow.** Paste multiple links into one field. The website is detected automatically from each URL; no dropdown or manual grouping is required. The workflow internally groups each link into its compatible downloader.

- **Novel links:** Paste one or more complete HTTPS novel URLs from any supported sites. Separate with a comma, space, semicolon or newline. Mixed websites can be submitted together.
- **Saved novel names:** Type names listed in
  [DOWNLOADED_NOVELS.md](../DOWNLOADED_NOVELS.md), separated by commas or
  semicolons. Example: `The World Online; The First Order`. Use semicolons
  when a novel's title itself contains a comma.
- **New titles:** Paste their exact URLs into Novel links. Saved names and new URLs can be mixed in the same submission.
- **Chapter range:** Optional for other sources; blank requests a whole novel. For WuxiaClick a range is required for books with more than 20 chapters and may cover at most 20 chapters per WuxiaClick novel, or fewer when selecting several WuxiaClick novels in one run.
- **Force:** Redownload even if a completed artifact is still available.
- **Confirm rights:** Required when the selection includes **WuxiaClick or Scribble Hub**. WuxiaClick is capped at 20 chapters across the WuxiaClick novels in one bulk run; do not chain runs to exceed the site's daily allowance. Only registered, same-author Scribble Hub cross-posts are supported; for these, chapter range must be blank because only whole-novel exports are verified. A bulk selection containing both WuxiaClick and Scribble Hub is not supported because their chapter-range requirements differ.

GitHub Actions lacks a dynamic multi-select field, so saved names are entered
as multi-value text rather than selected with checkboxes. Example: enter
`True Martial World; The World Online` under Saved novel names. The planner
resolves their URLs automatically. To list recognised titles, run:

~~~powershell
python -m tools.mixed_source_bulk list
~~~

Titles come from the completed-download registry and
[curated_novels.json](../curated_novels.json), a small curated list seeded with
the tested FreeWebNovel example. For a brand-new title, enter its exact URL;
after a successful download and registry update, that title is available by
name. You can also add a title/URL to the curated JSON list beforehand.

Unknown or ambiguous titles, invalid or unsupported URLs, and Scribble Hub
series without an explicitly verified author cross-post are rejected before
downloading. A URL from an otherwise supported site must still match that
site's recognised book URL format. The artificial **ten-novel cap is removed**.
GitHub Actions currently permits at most **256 matrix jobs per workflow run**;
the planner rejects a larger scheduled selection with an explicit explanation,
so split it over separate runs. Cached/skipped novels do not count towards
scheduled jobs. Up to three NovelFull books, two FreeWebNovel books, one ReadNovelFull book and one
Scribble Hub cross-post can run concurrently. Existing per-book chapter
validation and registered download status checks remain unchanged.

**Partial-failure recovery:** each successfully completed book has its own
separately downloadable novel artefact, even if another book fails or the
overall bulk workflow status is red. **If all child groups succeed or are
skipped, the summary avoids redownloading and rezipping those books**:
the existing individual artefacts remain available. If any child group fails
or is cancelled, the always-run summary job downloads the completed child
artefacts, re-verifies source URLs, ZIP/EPUB CRC, chapter positions, manifest
and individual SHA-256 digests, then publishes
`bulk-successful-novels-<run-id>` under the bulk run's **Artifacts** section.
Download that recovery artefact and extract it to obtain **one ordinary ZIP per
successful novel**, plus `bulk_recovery_manifest.json` showing recovered,
missing and rejected books. A failed/incomplete chapter batch is never included
as a completed novel. Original independent completed artefacts are not deleted
during recovery, and remain available if recovery packaging itself fails.

**Retry only failed or missing books:** in **Library - Bulk Download**, set **Retry from previous run ID** to the numeric ID at the end of the earlier workflow URL, such as `43609729867`. Leave novel links, saved names and chapter range blank, and leave **Force** unticked. If the missing list includes a Scribble Hub cross-post, tick the usual permission checkbox. The workflow downloads the previous run's small `bulk-recovery-manifest-<run-id>` artefact (not the large book ZIPs), validates that it belongs to that run, rebuilds the exact missing-novel URLs and original chapter range, and skips anything independently completed since then. Successful books are **never redownloaded merely because the previous overall run failed**.

Retry manifests are available for **seven days** and only for bulk runs created *after* this feature is released. Earlier manifests lack reliable range and run-ID details, so the tool refuses to guess them. If the original summary/recovery job never produced a manifest, use a fresh bulk submission with the remaining URLs instead. A run with no missing work reports that explicitly.

**Synthetic load testing:** `python -m tools.bulk_download_stress` checks 20, 50 and 100 selections, mixed website matrices, duplicates and registry skips without contacting novel websites; it also confirms 256 jobs are accepted and 257 are rejected.

**Bulk performance report:** every new bulk run attempts to read completed job timings from GitHub's own Actions API (no requests to novel websites). Open the run's **Summary** for a breakdown of installation/setup, discovery, chapter download or cached-batch reuse, EPUB assembly, artefact transfers, registry updates and recovery. Download the small `bulk-performance-<run-id>` JSON under **Artifacts** for an auditable baseline. Telemetry runs with `continue-on-error`, so a temporary API failure cannot discard a successful novel.

The report includes **summed per-step durations across parallel jobs**, not a claim about whole-workflow elapsed time. The completed-jobs elapsed window is separate and may exclude an in-progress summary job. A chapter-fetch step can reuse a cached batch without contacting the website. Compare multiple equivalent bulk runs before changing site concurrency or claiming a download speed-up.

**Low-risk packaging optimisation:** successful bulk runs skip duplicate recovery transfers and repackaging entirely. On partial failure, recovery stores already-compressed EPUB/cover files without recompressing them, continues compressing TXT/JSON, and uploads the resulting book ZIPs with Actions compression level zero. The normal completed novel and chapter artefacts retain their existing compression and full integrity checks. Both website workflows already restrict assembly downloads to their own chapter-batch IDs, so no new filtering is required. Source request rates and the existing 3/2/1 per-site concurrency limits are unchanged.

When created after a child failure, the recovery bundle and original individual novel artefacts are retained for seven days. A fully successful bulk run has individual novel artefacts and a performance report, but no redundant recovery bundle or retry manifest.
A large recovery bundle is bounded by a 1.75 GiB packaging safety limit; books
not included because of this limit remain individually retrievable.
Public-repository Actions artefacts may be accessible to other users.
The bulk job remains failed when a child fails, making the failure visible
without sacrificing any verified successes.

`DOWNLOADED_NOVELS.md` is grouped by website automatically. Historical
downloads retain all their artifact links and chapter counts, including
expired artifacts. Only archive content you are authorised to store. In a
public repository, GitHub Actions artifacts may be accessible to others.

## Windows: download completed novels

The [Download-All-Novels.cmd](../Download-All-Novels.cmd) launcher retrieves the already-created, **full-novel** GitHub Actions artifacts listed in [downloaded_novels.json](../downloaded_novels.json). It does **not** download chapters from source websites or trigger new Actions runs.

1. Install [GitHub CLI](https://cli.github.com/) (for example, `winget install --id GitHub.cli --exact`).
2. If GitHub CLI is already signed into an account with repository read access, keep using it. You do **not** have to use the account that owns the repository. Otherwise, the launcher offers a browser-based sign-in.
3. Clone the repository or run `git pull` to get the latest files.
4. Double-click `Download-All-Novels.cmd` from the repository root. The window stays open at the end, including on errors.

The launcher saves a detailed local diagnostic transcript to `download-last-run.log` and shows the actual exit code. The log is ignored by Git and is overwritten on each run. If GitHub CLI needs authentication, choose **Y** when prompted; `gh auth login --web --clipboard --skip-ssh-key` shows a one-time device code and opens a browser to authorise the account you choose. You can also request a browser login explicitly with `Download-All-Novels.cmd -BrowserLogin`. This is an ordinary stored GitHub CLI login, **not** an automatically expiring temporary session. If you add a different account, use `gh auth switch -u AdityaSreevatsaK` to return to your original account or `gh auth logout -u ACCOUNT_NAME` to remove the added login. Avoid sharing your login tokens or diagnostic logs publicly.

Each completed novel is saved as a single `novel-<artifact-id>.zip` in the ignored `Downloaded_Novels/` directory, with a single book folder inside containing `chapter_XXXX.txt`, `chapters.json`, `metadata.json`, and `source.epub`. The downloader checks the book's source URL, manifest and EPUB before saving; unrelated folders in bulk artifacts (including the older Abe the Wizard artifact) are not included. The script reads the **current** index, identifies each novel by its source URL and checks existing ZIP files **before downloading**. A valid local copy is skipped even when its filename or GitHub artifact ID differs from the current registry. Missing or invalid ZIPs can still be retrieved; an invalid existing file is never overwritten. GitHub CLI authentication is only requested when a novel actually needs downloading. Unavailable/expired artifacts are reported in `Downloaded_Novels/failed-downloads.txt`. It cannot resurrect expired artifacts, and it does not bypass access controls. GitHub artifacts normally expire after seven days, so download promptly.

By default, the local duplicate check searches ZIP files in `Downloaded_Novels/`. If you also have ZIPs in another directory (for example, your bulk-uploader's `novels` folder), pass that directory to avoid downloading copies of those books too:

~~~cmd
Download-All-Novels.cmd -ExistingZipDirectory "C:\\Path\\To\\Other\\Novels"
~~~

Only verified, full-novel ZIPs count as present. The script checks ZIP contents, chapter manifest, EPUB and the book's source URL; it doesn't rely on filenames alone. The other directory is not modified. It does not scan arbitrary folders on your computer.

If you already downloaded novels with the older folder-based downloader, **do not download them again**. Repackage the local files into verified book ZIPs using:
 
~~~cmd
Download-All-Novels.cmd -RepackOnly
~~~

This mode does not require GitHub CLI or re-download any artifacts. It moves each successfully repacked original folder to `Downloaded_Novels_Originals/` (outside the ZIP directory) as a recoverable backup. The ZIP directory contains one ZIP per successful novel. After checking your ZIPs, you can manually remove the backup folder to reclaim disk space. If a book cannot be validated, its original folder is left untouched and reported in `failed-downloads.txt`. The ZIP filenames use unique artifact IDs because different books can share a single workflow run ID. For existing folder backups, the full multi-book artifact is preserved while only the expected book is placed in its ZIP.

To verify the Windows launcher can resolve its folders without signing in or downloading anything:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\download_all_artifacts.ps1 -CheckSetup
~~~

For a quick one-book smoke test (after authenticating):

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\download_all_artifacts.ps1 -Limit 1
~~~

To save to another folder, use `-Destination 'D:\Novels'`. You can rerun the command after a network interruption; it skips verified local ZIPs and repacks older complete folders before attempting new downloads. You must have the right to archive the underlying material. Novel contents are never committed to the repository.

## Downloaded-novel list

View [DOWNLOADED_NOVELS.md](../DOWNLOADED_NOVELS.md) for completed downloads. The index includes previously verified completed jobs, including the recovered Abe the Wizard entry from bulk run 42393126629. The registry is an index, **not permanent storage**: once an artifact expires, a normal rerun is allowed so the book can be archived again, subject to permission.

## Other tests

The CI workflow verifies two synthetic chapters on Linux and Windows. A separate probe has confirmed that FanFicFare can retrieve and parse two real NovelFull chapter bodies, but it does not retain their text. Do not confuse retrieval tests with authorisation to publish those chapters.

## When something fails

- **An expired artefact:** `DOWNLOADED_NOVELS.md` keeps history but does not store full books. Run an authorised fresh download or use a verified local copy.
- **A novel is not in the registry:** Check the individual workflow's registry PR, branch and merge diagnostics; the completed download artefact can exist even if its metadata PR failed.
- **An incomplete batch:** Inspect the failed chapter-range artefact and logs. The final book should not be considered complete or recorded until all required positions validate.
- **A Windows ZIP cannot be repacked:** Inspect `download-last-run.log`, `failed-downloads.txt`, source URL metadata and the ZIP's chapters manifest. Existing invalid files are deliberately preserved.
- **A downloaded novel has no synopsis or cover:** See [metadata maintenance](metadata-guide.md); an absent source field is not automatically a downloader failure.

For code-level entry points, architecture diagrams and failure invariants, consult [AGENTS.md](../AGENTS.md).

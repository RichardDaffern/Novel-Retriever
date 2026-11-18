# Approved Yup pilot: three separate small download pipelines

This is a limited pilot, not an attempt to download the entire Excel list in one workflow.

## Selection and exclusions

The reviewed Excel filtering audit identified 173 still-missing **Yup** titles and excluded 90 Dropped or red-highlighted titles from the wider campaign. None of those exclusions is selected here.

This pilot selects **six** titles, all marked **Started** in the original Excel's Yup sheet, in **three separate two-novel workflows**. The verified source page URLs are stored in the explicit allowlist at campaigns/yup-pilot/verified-urls.json. Requests are divided across batch-01.json, batch-02.json and batch-03.json.

Do not guess a URL slug from a novel title. The existing bulk downloader resolves names only from the verified registry or curated list, so this pilot supplies independently checked direct URLs.

## Automatic small-batch dispatcher

Merging the pilot PR adds three new request files on main. The narrowly scoped push workflow, .github/workflows/yup-pilot-dispatch.yml, sees only newly added requests in that push, validates the entire group, checks the completed download registry, and dispatches one independent Library - Bulk Download workflow for each nonempty request.

- At most three new requests per push, with at most two books per request.
- Each title and HTTPS source URL must exactly match the explicitly reviewed allowlist.
- No forced downloads, unrecognised sources, speculative chapters, or automated rights bypass.
- Completed registry URLs are skipped.
- Re-running the dispatcher does not launch batches again.
- Individual downloads keep their existing per-site concurrency limits, checkpoints, per-novel artefacts and recovery files.
- Dispatch calls are spaced apart rather than fired in one immediate burst.

**Archiving rights:** Only download and publish material you are authorised to archive and expose through GitHub Actions artefacts. This workflow does not establish rights and does not bypass site restrictions.

For later waves, add newly verified URLs and new request files in a reviewed change. Continue with eligible Yup titles first; do not add excluded or Idk titles.

## Monitoring

Dispatcher: https://github.com/RichardDaffern/Novel-Retriever/actions/workflows/yup-pilot-dispatch.yml

Independent runs: https://github.com/RichardDaffern/Novel-Retriever/actions/workflows/library-bulk-download.yml

Successful GitHub artefacts are not automatically added to the private Hugging Face dataset. Collect the verified one-book ZIPs and use the Storage Controller Smart Bulk Upload with its conflict/backup review.

## Offline tests

Run: python -m unittest tests.test_campaign_yup_dispatch -v

All campaign tests are offline. They cannot download any novel chapters or dispatch a live workflow.

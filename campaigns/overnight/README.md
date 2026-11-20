# Overnight download queue: Yup first, then Idk

**Historical campaign documentation, last reviewed 20 November 2026.** The 19 November figures and one-shot activation instructions below describe the original queue, **not** live pending books. Four additional Yup sources are now marked `wave4_requested`, leaving **153** in `needs_source_verification` within the historical 163-title Yup backlog. The newer [large-wave workflow](../../.github/workflows/large-verified-waves-20261120.yml) requests up to 40 newly verified Yup-first/Idk books in ten-title child batches with a two-active-workflow cap. The already-added 20 November activation must **not** be re-run. Read the [current status](../../docs/current-status.md) and [operations runbook](../../docs/operations-runbook.md) before starting any new work. The **90 red/Dropped exclusions still apply globally**.

**Start:** 19 November 2026 (IST). **Source:** filtered original Excel audit and the private Hugging Face comparison.

The original **90 red-highlighted/Dropped titles** are recorded in excluded-90.json, a global denial list across BOTH worksheets. All five cross-sheet conflicts remain excluded, even if another worksheet says Started.

## Queue scope

- **Yup:** 173 originally absent from HF; 16 already attempted or queued in waves 1-3. The **157 remaining** need source research.
- **Idk:** **82** other absent titles, newly included at the user's request, with no private reading status included.
- *A Thought Through Eternity* is an alias of *A Will Eternal*, already queued. It must not be fetched twice.
- Only exact-title, verified public book listings qualify for a download. Invented slugs or unrelated titles do not qualify.
- Previously downloaded/queued works and all 90 exclusions are always skipped.

## One-shot GitHub Actions workflow

Adding start-20261119.json to main activates the job **once**. Editing the activation or rerunning the workflow cannot create duplicate dispatches.

1. **Source discovery:** Prefer **NovelFull first** for every title. Only if its public book listing is unavailable or not an exact title match, consider FreeWebNovel. Check no more than 500 public requests, spaced at least two seconds apart. Do not save chapter text. A 403, 429 or access challenge disables the affected source for the rest of that run. No credentials, redirects, browser tricks, proxies or bypass.
2. **Yup dispatch:** Queues verified titles in independent two-book Library - Bulk Download pipelines first, at most four active bulk workflows, spacing dispatches by 150 seconds.
3. **Idk dispatch:** Then queues verified Idk titles under the same limits.
4. **Audit artifacts:** Source verification, unresolved titles and dispatched/held groups are saved for follow-up. Any unverified title remains a research task, not a secretly invented link.

The existing downloaders enforce per-site pacing, completeness checks, metadata/cover validation and partial checkpoints. A source page that presents the wrong chapter number is an integrity failure and never silently accepted. The previously blocked books tracked in issue #257 are deliberately NOT restarted.

**Rights:** A publicly readable book page does not establish archiving or redistribution rights. Only archive works you have permission to copy; respect source limits, and do not use this workflow to evade them. GitHub Actions artifacts may be publicly accessible.

## Where to monitor

- [Overnight research and dispatcher](https://github.com/RichardDaffern/Novel-Retriever/actions/workflows/overnight-yup-idk.yml)
- [Individual download pipelines](https://github.com/RichardDaffern/Novel-Retriever/actions/workflows/library-bulk-download.yml)
- In the overnight run: overnight-discovery-<run>, overnight-yup-dispatch-<run> and overnight-idk-dispatch-<run> artifacts.

Tomorrow, inspect incomplete or blocked titles and use recovery manifests. Never force completed downloads or retry deterministic chapter-number mismatches without addressing the source-index issue. Nothing is uploaded to private Hugging Face by this workflow.

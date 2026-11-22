# Overnight download queue: Yup first, then Idk

**Historical campaign documentation, refreshed 21 November 2026.** The 19 November figures and one-shot activation instructions below describe the original queue, **not** live pending books. Four additional Yup sources are now marked `wave4_requested`, leaving **153** in `needs_source_verification` within the historical 163-title Yup backlog. The newer [large-wave workflow](../../.github/workflows/large-verified-waves-20261120.yml) requests up to 40 newly verified Yup-first/Idk books in ten-title child batches with a two-active-workflow cap. The already-added 20 November activation must **not** be re-run. Read the [current status](../../docs/current-status.md) and [operations runbook](../../docs/operations-runbook.md) before starting any new work. The **90 red/Dropped exclusions still apply globally**.

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

1. **Source discovery:** Prefer **NovelFull**, then **ReadNovelFull**, then **FreeWebNovel** where appropriate. The current `tools/overnight_queue.py` probes NovelFull plus ReadNovelFull standard/`-v1` book-page variants and FreeWebNovel, with a 500-request budget and at least two seconds between requests. Do not save chapter text. A 403, 429 or access challenge disables the affected source for the rest of that run. No credentials, redirects, browser tricks, proxies or bypass.
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

## Later source-audit outcome and follow-up priority (22 November 2026)

The separate read-only [three-source audit #44924359606](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44924359606) found 26 public book listings from 91 eligible Yup/IDK entries (18 Yup, 8 IDK); 65 had no exact match at the tested URL patterns (36 Yup, 29 IDK). The audit made no chapter downloads and did not verify archiving rights. A five-title index preflight #44926984233 passed only *Doom Lord* and *Girl, I'll Teach You Cultivation*; three indexes failed. See [the preserved source-audit report](source-audit-report-20261121.md).

The fanfiction-first research stage is complete for the current scope: 8 complete, 3 blocked and 32 unresolved, with no rights-cleared source. The 36-row Yup and 29-row IDK alternative-source reviews have also been completed after that stage. The IDK report found one exact NovelFull/FreeWebNovel listing for *Attack Of The Adorable Kid* (Sweets Flood, 2,612 page-reported chapters), but no archive permission; eight WuxiaClick metadata listings have index/count caveats. There are **0 rights-cleared titles and 0 new download runs**. This does not make the 65 titles worldwide-unavailable. Do not reactivate the 19 November one-shot dispatcher. Use [current status](../../docs/current-status.md), [IDK report](idk-alternative-source-research-20261122.md), and [issue #456](https://github.com/RichardDaffern/Novel-Retriever/issues/456).


## Corrected alias reconciliation and follow-up round 2 (22 November 2026)

The 65 audit rows (36 Yup, 29 IDK) were re-compared by title, author and edition against the 343-record registry and 90 exclusions. There are **12 aliases of completed registry entries and one alias of excluded *Eternal Reverence***, leaving 52 distinct non-alias titles. The earlier exact/near/no-match counts are corrected in [the round-2 report](alternative-source-research-round-2-20261122.md). Do not treat the 52 as globally unavailable.

New alternative listings include *Addicted Pampering You* (incomplete index), *Attack Of The Adorable Kid* (2,612-page-reported commercial WebNovel edition; rights not cleared), *Hidden Marriage Sweet Pampering* (major chapter-count mismatch), *Bringing The Nation's Husband Home* (official Apple Books edition), *Eternal Martial Sovereign* (licensed Gravity Tales translation; incomplete WuxiaClick index), *Mad God* and *The Kind Death God*. None has explicit archiving permission. No new download run was dispatched.

The fanfiction-first stage remains complete for the current scope. Continue Yup/IDK source and rights verification only after that stage; keep the 90 exclusions and all completed registry aliases out of acquisition batches.
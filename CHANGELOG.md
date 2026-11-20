# Changelog

Changes listed here are **operational/documentation milestones**, not a full commit history. Consult [Git history](https://github.com/RichardDaffern/Novel-Retriever/commits/main), [open issues](https://github.com/RichardDaffern/Novel-Retriever/issues) and [current status](docs/current-status.md) for verified evidence and evolving campaigns. A successful dispatcher or CI run is **not** proof of a completed novel.

## 20 November 2026

### Documentation and AI-agent handover
- Added [Operations Runbook](docs/operations-runbook.md) covering authorisation, launch decisions, live tracking, chapter/edition failure recovery, output validation, Storage Controller import and one-time activation safety.
- Added [dated Current Status](docs/current-status.md) with live-run references and separate states for Yup/Idk, Naruto/Harry Potter fanfiction, incomplete books, registry PRs and private HF.
- Added an [AI Agent Handover Template](docs/agent-handover-template.md) with test evidence, exact run IDs, unresolved titles and next steps.
- Retained the comprehensive [AGENTS handbook](AGENTS.md) and clarified how new agents should use the new guides.

### Larger reviewed download campaign
- [PR #433](https://github.com/RichardDaffern/Novel-Retriever/pull/433) introduced a one-time source-verified campaign using ten-book batches, a two-active-bulk-workflow limit, Yup-first priority, and a separate 14-title known-failure exclusion list.
- [Large-wave workflow #44764626782](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44764626782) was initiated. At the documentation snapshot, discovery had succeeded and dispatch was still underway. **Do not mistake this entry for 40 completed books.**
- [PR #432](https://github.com/RichardDaffern/Novel-Retriever/pull/432) added the prior two-book Yup wave-four pilot. [Batch 09](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44762457914) and [batch 10](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44762670118) were initiated separately.

## 19 November 2026

### Completed-book handover and cover repair
- Exported the then-selected 104 completed books to a consolidated, controller-ready GitHub Actions artefact: [run #44466510737](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44466510737).
- Recovered **104/104** genuine images from original ZIPs and EPUBs, without downloading novel chapters again: [run #44521807242](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44521807242).
- Verified an independent **cover-only** repair in the private Storage Controller workflow: [run #44522722197](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller/actions/runs/44522722197). The temporary one-time repair workflows were subsequently retired; do not reactivate them.
- Documented source verification and bounded dispatch for the Yup, Idk and user-requested fanfiction campaigns under `campaigns/`.
- Recorded deterministic chapter-index failures separately from transient transport problems in [issue #371](https://github.com/RichardDaffern/Novel-Retriever/issues/371) and [issue #257](https://github.com/RichardDaffern/Novel-Retriever/issues/257).

## Earlier work

See [README](README.md), [the detailed agent handbook](AGENTS.md), [website support](docs/website-support.md), [download guide](docs/download-guide.md), and [source-feasibility research](docs/research/source-feasibility-2026-11-15.md). Do not backfill historical success counts without checking run artefacts and registry changes.

## Maintenance rules

- Add entries when behaviour changes, a campaign is **actually** activated, or a recovery is verified.
- Record final success only after checking the relevant final artefact/registry/Controller evidence.
- Keep chronological dates and precise source/PR/run links; distinguish historical success from current availability.
- Do not publish private Hugging Face data, reader history, secrets or full copyrighted source material.

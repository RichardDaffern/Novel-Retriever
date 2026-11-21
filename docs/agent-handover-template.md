# AI Agent Session Handover Template

This is a **copy-and-fill template**, not a live status report. Use for any substantial Novel Retriever coding, source-verification, bulk-download, recovery, metadata publication or Storage Controller handover.

**Read before using:** [AGENTS.md](../AGENTS.md), [Operations Runbook](operations-runbook.md), [Current Status](current-status.md), and the actual changed source/workflow definitions.

## Mandatory handover

### A. Context and scope

- Date/time and timezone checked:
- Repository / exact canonical `main` SHA:
- User-approved goal:
- Work intentionally **not** performed:
- Safety constraints (90 global red/Dropped exclusions, authorisation, source-specific limits, known failed/blocked books):
- Related PRs, issues, workflow runs and GitHub artefact links:

### B. Files and code state

| Item | Exact value / evidence |
| --- | --- |
| Branch | |
| Local working-tree status (or state that no local clone was available) | |
| Current main SHA and local HEAD SHA | |
| Recent commits / changed paths inspected | |
| PR and status | |
| Base/head SHA | |
| Merged to `main`? | |
| Modified files and why | |
| New or changed entry points / data contracts | |
| State classification for affected features (active / live-unverified / partial / planned / retired / historical) and evidence | |
| Tests executed, operating systems and observed conclusions | |
| Secrets, authorisation or permissions required (names only, **never values**) | |
| One-time activation file used? | |
| Cleanup due after a one-time operation | |

If CI is pending, say **pending**. If an Action dispatched but did not complete its child book jobs, say **dispatch successful, books unverified**.
If no local clone was available, explicitly say that the working tree and uncommitted changes were not inspected. Do not report it as clean. Historical status snapshots and prior AI summaries are not current-state evidence.

### C. Download state: do not collapse stages

| Stage | Counts / book names / evidence |
| --- | --- |
| Reviewed input titles, by Yup / Idk / fanfiction | |
| Red/Dropped exclusion count and cross-sheet conflicts | |
| Verified public book listings and source/edition | |
| Eligible after completion, active-job and known-failure de-duplication | |
| Submitted child workflows (exact run IDs) | |
| Still queued / held / unverified listings | |
| Child jobs completed and chapter-integrity-verified | |
| Completed `downloaded_novels.json` records (canonical source URL and artefact IDs) | |
| Failed/incomplete titles, exact issue and recovery checkpoint | |
| Exported controller-ready ZIPs and checksums | |
| Imported to private HF (independently confirmed by Controller) | |

**Evidence hierarchy:** live job steps and successful final artefact; source URL and EPUB/chapter/hash checks; then metadata-only registry; then verified local export; then private Controller outcome. Never infer one from another.

### D. Risks and outstanding work

Record each separately:

- Source/rights restrictions, 403/429/CAPTCHA challenges:
- Broken source table-of-contents, chapter mismatch or empty chapter body:
- Transport interruptions with selective-retry evidence:
- Metadata-only registry PR open or conflicting:
- Expires-soon GitHub artefacts:
- Genuine title/edition ambiguity:
- Missing/invalid cover or synopsis:
- Downstream Storage Controller upload issue:
- Review needed before any code merge or data write:

### E. Next actions

1. **Immediate:** The one safe next investigation or command, with necessary inputs and a direct link.
2. **After verification:** Exact acceptance criteria before treating novel/book/archive as complete.
3. **Later:** Unverified sources, paused campaigns, tests or architectural improvements.

### F. Final statement to user

Use a short status that distinguishes **done**, **running**, **blocked** and **not started**. Give links to the PR(s), GitHub Actions run(s) and artefacts. Never say you will continue working autonomously after the session unless there is an actual scheduled automation.

---

## Example: campaign in progress, not complete

```text
Checked: YYYY-MM-DD HH:mm IST
Repository: RichardDaffern/Novel-Retriever
Main SHA: <sha>
Campaign: <run url>
Discovery: success, N verified sources; M unverified
Dispatcher: in progress, X/Y batches submitted
Child runs: <run links>; 2 active, 1 queued
Completed registry records newly observed: Z
HF import: not attempted / not independently verified
Known exclusions: 90 red/Dropped and 14 targeted-recovery titles
Next: inspect dispatcher artefact, child chapter reports and registry.
Do not rerun the one-shot activation or re-fetch finished titles.
```

Replace every placeholder with verified evidence; if the value cannot be checked, say so explicitly. Do not reuse the example's counts as facts.

## When to update living repository documents

- `AGENTS.md` changes when an invariant, entry point, architecture, maintenance requirement or agent obligation changes.
- `docs/operations-runbook.md` changes when a procedure or failure/recovery step changes.
- `docs/current-status.md` changes when a **dated, verified** campaign milestone materially changes. Refresh timestamps and never claim automatic synchronisation.
- `CHANGELOG.md` changes when an operator-meaningful capability or workflow is introduced, fixed or retired.
- `README.md` changes when the user-facing operation or location of authoritative guides changes.

**No secret values, personally sensitive reading activity, copyrighted book content or private dataset IDs** in a public handover.

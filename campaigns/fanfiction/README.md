# Harry Potter and Naruto fanfictions, 19 November 2026

**Checked 21 November 2026:** The 43-title catalogue is historical input and not an auto-refreshing completion tracker. Comparing the source-matched URLs with the current complete download registry identified **8 completed**, **3 source-matched but incomplete/not yet registered** and **32 needing compatible supported-source verification**. Among the 32, *Naruto: Chronicles of a Fire Ninja* has a possible supported listing but chapter identity remains unverified. The section named 'Tomorrow' below records the original plan, **not an active background task**. For current evidence, outstanding download blockers and source verification, use [the dated status](../../docs/current-status.md) and [operations runbook](../../docs/operations-runbook.md).

**Input:** 11 screenshots inside the user's WhatsApp ZIP, recording 43 visible WebNovel titles and authors: **24 Naruto**, **19 Harry Potter**. This public file contains book titles and author names only, not the private screenshots, user profile, personal ratings or reading progress.

**Current user priority:** work on these Harry Potter/Naruto fanfiction sources and recoveries **before** the 65 unresolved Yup/IDK titles from the 21 November source audit. Keep this catalogue, counts and download batches separate from the Yup/IDK campaigns. See [current status](../../docs/current-status.md), [source-audit report](../overnight/source-audit-report-20261121.md) and [issue #456](https://github.com/RichardDaffern/Novel-Retriever/issues/456).

## Current source research (22 November 2026)

- The 43-title catalogue remains **8 registry-complete**, **3 source-matched but blocked/incomplete**, and **32 requiring source research**. Keep these counts separate from Yup/IDK and from the user's separately confirmed 70 private-HF imports.
- The corrected 32-title supported-host pass found **5 exact title+credited-author listings**, **2 near/variant matches**, and **25 with no exact supported listing**. None passed the complete edition, full-index and lawful-rights gate. No new fanfiction run was dispatched.
- The 5 exact listings are *Naruto: Chronicles of a Fire Ninja*, *Reborn into Naruto World with Tenseigan*, *Naruto: Starting With Creating A Genius Persona*, *Harry Potter: The Healer* and *There Will Be No Third Dark Lord At Hogwarts!!!*. All have chapter-count/edition caveats; see [source verification round 3](source-verification-round-3-20261122.md).
- The two near matches are *Talent System In The Naruto Universe* (Rashta vs catalogue Rashita) and *Naruto: This Ninja is Obviously …* (FreeWebNovel credits Wu Mian Qi Liang, not the selected WebNovel credit nyawdao2). Do not silently substitute either.
- Full title/author identity links for all 32 are recorded in the [identity ledger](source-identity-resolution-20261122.md). The original captured JSON strings remain unchanged; no screenshots were requested again.
- The three blocked/source-matched works remain *Naruto: The Wind Calamity* (non-linear chapter mapping), *Konoha's Medical Ninja: One Punch to beat up Madara* (444-chapter archive technically complete, but public artifact and rights unresolved; PR #275 held) and *HP: The Arcane Thief* (254-chapter +1 offset fix merged in PR #463; no retry without rights).
- The registry has **8 completed fanfiction entries**: seven artifacts are currently present and *The Adventurous Gamer Ninja - Daichi Hekima*'s artifact expired on 21 November. *A New Snake In The Shinobi World*'s run #44378479201 failed overall because *The Wind Calamity* failed; its own 423 chapter batches succeeded and its archive artifact is present.
- No public listing, translator credit, English label, Patreon page or complete-looking first TOC page is permission to archive or publicly publish a full work. Do not create new public GitHub Actions book artifacts until the author/rights holder has explicitly authorised that use.
- After the fanfiction first pass, the 65 Yup/IDK audit entries were searched for alternatives. Four title aliases already map to completed registry entries, leaving 61 distinct titles. The first sweep found **13 exact supported-host listing candidates**, **3 near/variant matches** and **45 with no exact supported listing**; none has documented archiving permission. See [alternative-source research](../overnight/alternative-source-research-20261122.md).

## Overnight downloads

The one-shot [Fanfiction - Queued Naruto and Harry Potter Source Matches](https://github.com/RichardDaffern/Novel-Retriever/actions/workflows/fanfiction-night-queue.yml) dispatcher launches independently of the approved **Yup then Idk** campaign. Adding start-20261119.json to main triggers it once.

The dispatcher:
- Reads the current completed registry, skips any matched novel already present and validates all 43 rows before starting.
- Uses only 10 reviewed HTTPS book-page URLs from FreeWebNovel.
- Launches one **Library - Bulk Download** run per **two books** at most, leaving 150 seconds between submissions.
- Requires fewer than four active bulk workflows across the repository, so this separate campaign does not immediately flood the website while Yup/Idk runs are active.
- Waits for existing jobs to free capacity; if a fixed five-hour dispatcher window runs out, saves remaining candidates as held for next-day requeue, not false success.
- Uses `force=false`, ordinary source limits, the current site's error handling, strict chapter-count and identity checks, and per-book checkpoints.
- Blocks automatic re-dispatch on GitHub Actions rerun and does not perform any private Hugging Face uploads.

### Live download batches

| Batch | Books |
|---|---|
| 1 | Naruto: The Wind Calamity; Naruto: I am Uchiha Shirou |
| 2 | Naruto: Kurotsuchi Mayuri; A New Snake In The Shinobi World |
| 3 | Konoha's Medical Ninja: One Punch to beat up Madara; HP: The Arcane Thief |
| 4 | HP: A Magical Journey; Hogwarts: I'm Truly a Model Wizard |
| 5 | Hogwarts' John Wick; The Fool in Hogwarts |

These are **reviewed source listings**, not a guarantee of complete and authorised EPUB downloads or that all chapters are currently accessible. A source challenge, forbidden page, chapter mismatch or site limitation remains a hard stop.

**Copyright and permission:** An accessible public page does not establish permission to make a personal archive or publish a GitHub Actions artefact. Run archiving only where you are authorised to do so; never bypass access controls or rate limits. Fanfiction translations/editions can have separate rights.

## Tomorrow

1. Inspect the fanfiction dispatcher run for `fanfiction-dispatch-<run-id>` and identify queued/held titles.
2. Inspect each new **Library - Bulk Download** run's successfully verified archive and any failed-source recovery manifest.
3. Use existing recovery tools for transient issues; investigate wrong chapter mappings instead of forcing a download.
4. Review the 32 unmatched titles with author and full-title checks before selecting other sources or importing user-saved pages.

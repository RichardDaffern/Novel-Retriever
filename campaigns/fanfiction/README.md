# Harry Potter and Naruto fanfictions, 19 November 2026

**Checked 21 November 2026:** The 43-title catalogue is historical input and not an auto-refreshing completion tracker. Comparing the source-matched URLs with the current complete download registry identified **8 completed**, **3 source-matched but incomplete/not yet registered** and **32 needing compatible supported-source verification**. Among the 32, *Naruto: Chronicles of a Fire Ninja* has a possible supported listing but chapter identity remains unverified. The section named 'Tomorrow' below records the original plan, **not an active background task**. For current evidence, outstanding download blockers and source verification, use [the dated status](../../docs/current-status.md) and [operations runbook](../../docs/operations-runbook.md).

**Input:** 11 screenshots inside the user's WhatsApp ZIP, recording 43 visible WebNovel titles and authors: **24 Naruto**, **19 Harry Potter**. This public file contains book titles and author names only, not the private screenshots, user profile, personal ratings or reading progress.

**Current user priority:** work on these Harry Potter/Naruto fanfiction sources and recoveries **before** the 65 unresolved Yup/IDK titles from the 21 November source audit. Keep this catalogue, counts and download batches separate from the Yup/IDK campaigns. See [current status](../../docs/current-status.md), [source-audit report](../overnight/source-audit-report-20261121.md) and [issue #456](https://github.com/RichardDaffern/Novel-Retriever/issues/456).

## Source availability and round 2 research

- The original source pass identified **10** FreeWebNovel listings; **8** works are complete in the registry (including *The Adventurous Gamer Ninja - Daichi Hekima*), while **3** other source-matched works remain blocked or unresolved in registration: *Naruto: The Wind Calamity*, *Konoha's Medical Ninja: One Punch to beat up Madara* and *HP: The Arcane Thief*.
- The 22 November exact title+author search of the remaining **32** found **5 additional public FreeWebNovel listings**: *Naruto: Chronicles of a Fire Ninja*, *Reborn into Naruto World with Tenseigan*, *Naruto: Starting With Creating A Genius Persona*, *Harry Potter: The Healer* and *There Will Be No Third Dark Lord At Hogwarts!!!*. None passed the full edition, complete-index and rights gate.
- One near-match was rejected because *Talent System In The Naruto Universe* is credited to **Rashta** on the surfaced source, while the catalogue says **Rashita**. A similar-title *This Ninja is Obviously …* listing is credited to a different author and is not the selected work.
- **26** of the 32 had no exact supported NovelFull/ReadNovelFull/FreeWebNovel title+author listing in this pass. This is not a claim that the works are unavailable worldwide.
- No new fanfiction download was dispatched; no title has documented permission to archive or publish its full text. Public listing, translator credit, an English label or Patreon page is not permission.
- Full title/author evidence, TOC/edition caveats and the three blocked-source findings are recorded in [source verification round 2](source-verification-round-2-20261122.md).
- Some titles were visibly truncated in the original screenshots; the exact captured strings remain unchanged. Never guess missing words or silently substitute another author/translator edition.
- *Hogwarts: I'm Truly a Model Wizard* remains a distinct translation/edition on FreeWebNovel (BlurryDream) versus the selected WebNovel credit (BlurryPinkSnake); do not overwrite a different text silently.

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

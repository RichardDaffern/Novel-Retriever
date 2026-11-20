# Harry Potter and Naruto fanfictions, 19 November 2026

**Checked 20 November 2026:** The 43-title catalogue is historical input and not an auto-refreshing completion tracker. Comparing the source-matched URLs with the current complete download registry identified **8 completed**, **3 source-matched but incomplete/not yet registered** and **32 needing compatible supported-source verification**. Among the 32, *Naruto: Chronicles of a Fire Ninja* has a possible supported listing but chapter identity remains unverified. The section named 'Tomorrow' below records the original plan, **not an active background task**. For current evidence, outstanding download blockers and source verification, use [the dated status](../../docs/current-status.md) and [operations runbook](../../docs/operations-runbook.md).

**Input:** 11 screenshots inside the user's WhatsApp ZIP, recording 43 visible WebNovel titles and authors: **24 Naruto**, **19 Harry Potter**. This public file contains book titles and author names only, not the private screenshots, user profile, personal ratings or reading progress.

## Source availability

- **10** book-title matches found on the supported FreeWebNovel website, with the matched title, source URL and any translation/edition caveat recorded in [webnovel-favourites-43.json](webnovel-favourites-43.json).
- **1** is already in Novel Retriever's completed registry: *The Adventurous Gamer Ninja - Daichi Hekima*, so it is **not** re-downloaded.
- **32** still lack a verified listing on currently supported sources; no invented URLs, unsupported sites or WebNovel scraping.
- Some titles were visibly truncated in the screenshots; those strings are recorded exactly as observed with an ellipsis. They must not be treated as complete work identities until independently verified.
- **Hogwarts: I'm Truly a Model Wizard** is listed by a different translator on FreeWebNovel (BlurryDream; same original work), versus BlurryPinkSnake on WebNovel. Treat source text as an edition and do not overwrite a different text silently.

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

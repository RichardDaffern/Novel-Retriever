# Fanfiction source and rights recheck, round 8

**Checked:** 22 November 2026, 08:25 IST  
**Scope:** The five exact supported-host candidates, the two rejected near matches, and the three blocked fanfiction works.  
**Method:** Exact title/credited-author checks plus permission-focused public searches. Supported-host candidates were checked against NovelFull, ReadNovelFull and FreeWebNovel. Alternate catalogues and author pages were used only for identity, edition and rights evidence. Metadata only; no chapter prose or archive bytes were fetched.

## Result

- **0 additional exact supported-host matches** beyond the five recorded in round 3.
- **0 explicit archiving permissions** and **0 rights-cleared titles**.
- **0 new download runs** and no registry change.
- The original 43-title JSON remains unchanged. No screenshots were requested.

The 32 source-research rows therefore remain 5 exact supported-host candidates, 2 rejected near/variant matches and 25 without an exact supported-host listing. Search absence is not proof of worldwide unavailability.

## New author and edition evidence

### Naruto: The Wind Calamity

- Devil_Hex's [FanFiction.net author note](https://www.fanfiction.net/s/14178557/75/Naruto-The-Wind-Calamity) says translations had appeared without the author's permission or knowledge and asks anyone planning a translation to contact the author first. This is an explicit permission requirement, not a grant.
- The [Royal Road listing](https://www.royalroad.com/fiction/65209/naruto-the-wind-calamity) is another author-controlled publication lead. The supported FreeWebNovel chapter index remains non-linear.
- PR #463 correctly fails closed; PR #466 adds exact displayed-chapter-to-URL offset diagnostics. No canonical one-to-one TOC map or archive permission exists. **Do not retry.**

### Konoha's Medical Ninja: One Punch to beat up Madara

- The [WebNovel listing](https://www.webnovel.com/book/29703350508171905) exposes 444 chapters and explicitly says INeedRest is not the original writer, but edited the work. It also points to Patreon advance chapters.
- The original author remains unidentified. The 444-chapter technical archive does not resolve authorship or permission.
- Exact logs from [run #44379388243](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44379388243) show all nine chapter batches (1–444) succeeded. Assembly logged `ASSEMBLED 444 verified TXT chapters and EPUB` and uploaded artifact `14462633408` (3,370,287 bytes). The assembly job then failed only because `publish_registry` could not merge PR #275 after six attempts (`Base branch was modified` / `Pull Request is not mergeable`). Thus this is **assembled but unregistered**, not a chapter-integrity failure.
- Existing public Actions artifact `14462633408` expires 16 February 2027 19:20:05 UTC and remains rights-unverified. Do not re-download, register, link or create another public copy; repository-owner deletion/revocation is required if rights cannot be documented.

### HP: The Arcane Thief

- Snollygoster's [FanFiction.net profile](https://www.fanfiction.net/u/14988415/Snollygoster) lists the cross-post at 183 chapters and links to Patreon for advance access.
- The [WebNovel catalogue](https://www.webnovel.com/book/the-arcane-thief_20892578405832405/catalog) shows 255 entries including an auxiliary “Read First” page; the selected FreeWebNovel edition shows 254 numbered chapters. The 183-chapter FanFiction.net cross-post is a separate edition, not proof that the selected 254-chapter index is incomplete.
- PR #463 fixed the consistent +1 URL offset and added regression coverage. Patreon access is not archiving permission. No retry.

## The five existing exact supported-host candidates

| Work | Current evidence | Decision |
|---|---|---|
| Naruto: Chronicles of a Fire Ninja | FreeWebNovel lists FirstHokage and 472 entries. The author's [Royal Road notice](https://www.royalroad.com/fiction/90875/naruto-chronicles-of-a-fire-ninja/chapter/1859197/100-chapters-completed-yayyy) warns that an Amazon use of the narrative was unauthorised. | No archive permission; FWN chapter labels are non-linear. Hold. |
| Reborn into Naruto World with Tenseigan | FreeWebNovel lists Alex_Clive and 1,139 entries versus 967 on WebNovel; opening labels include malformed/shifted numbering. | Edition and index unresolved. Hold. |
| Naruto: Starting With Creating A Genius Persona | FreeWebNovel lists SweetestDeath and 527 entries versus 534 on WebNovel. NovelFull's public page also credits SweetestDeath. | Seven-entry edition difference unresolved; no permission. Hold. |
| Harry Potter: The Healer | FreeWebNovel credits translator TheRedSpell; the raw title is Russian `Целитель`, by original author Gezenshaft. Current mirror counts vary. | No permission from the original author or translation rights holder. Hold. |
| There Will Be No Third Dark Lord At Hogwarts!!! | FreeWebNovel has indexed up to Chapter 430; WebNovel/NovelFlick snapshots show 397. Patreon advance chapters are locked. | Inconsistent editions; subscription access is not archive permission. Hold. |

Permission-focused searches for Alex_Clive, SweetestDeath, TheRedSpell/Gezen, mrfanfiction140, Snollygoster and Devil_Hex did not surface an explicit grant to archive or republish these works. A public listing, translator credit or Patreon subscription does not supply that grant.

## Decision

No title passes exact work/author, English edition, complete ordered index and explicit lawful archiving permission together. Keep the 32 research targets and three blocked works separate from Yup/IDK. Do not dispatch a download batch or fetch chapter prose until the rights and source gates are met.

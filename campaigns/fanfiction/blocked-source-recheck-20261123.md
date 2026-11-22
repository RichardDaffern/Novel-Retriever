# Fanfiction blocked-source recheck, 23 November 2026

**Checked:** 23 November 2026, 02:42 IST  
**Scope:** The three blocked selected fanfiction works only. Public author notes and listing metadata were reviewed. No chapter prose, locked Patreon material, archive bytes or existing GitHub artifacts were fetched.

## Result

- **0 new supported-host source matches.**
- **0 explicit archive/public-distribution permissions.**
- **0 rights-cleared titles.**
- **0 download runs dispatched.**
- Fanfiction remains **8 complete, 3 blocked, 32 source-researched but unresolved**. The 32-target source-research pass remains complete for the current search scope; this round only rechecked the three blockers.
- The prescribed order remains: 26-match triage, then 43-title fanfiction research, then the 65 unmatched Yup/IDK alternatives. The latter 51 distinct non-alias rows have already been researched in the current bounded scope.

## Blocked-work evidence

### Naruto: The Wind Calamity — Devil_Hex

- The [FanFiction.net Chapter 75 author note](https://www.fanfiction.net/s/14178557/75/Naruto-The-Wind-Calamity) says the author found translations made without their knowledge or permission, and asks prospective translators to contact them first.
- The [FanFiction.net work page](https://www.fanfiction.net/s/14178557/1/Naruto-The-Wind-Calamity) lists 455 chapters in its current snapshot. The [WebNovel listing](https://www.webnovel.com/book/19921530006000505) reports 952 chapters. These are materially different editions/coverage snapshots and must not be merged into one chapter map.
- The author's statement is a request for prior permission, not a grant to this project. No permission response is recorded.
- **Decision:** keep the source adapter fail-closed. Do not retry until a complete one-to-one chapter map and explicit permission for the intended archive and distribution route are documented.

### Konoha's Medical Ninja: One Punch to beat up Madara — INeedRest

- The [WebNovel listing](https://www.webnovel.com/book/29703350508171905) reports 444 chapters and credits INeedRest, but the page explicitly says INeedRest is **not the original writer** and only edited the work.
- The page also advertises Patreon access to up to 30 extra edited chapters. That does not establish the original author's identity or grant archive/publication rights.
- Existing run #44379388243 completed chapter batches and uploaded artifact #14462633408, but its registry-publication stage failed. The artifact remains public, unregistered and rights-unverified.
- **Decision:** do not merge PR #275, fetch or republish the artifact, or retry. The original author and an authorised archive/distribution grant are still missing.

### HP: The Arcane Thief — Snollygoster

- The [WebNovel listing](https://www.webnovel.com/book/the-arcane-thief_20892578405832405) credits Snollygoster and reports 255 chapters. Its [table of contents](https://dynamic.webnovel.com/story/20892578405832405) exposes an auxiliary entry plus numbered chapters through Chapter 254; this is not evidence that all pages have been independently validated.
- The [FanFiction.net author page](https://www.fanfiction.net/u/14988415/Snollygoster) lists a separate 183-chapter cross-post. Do not treat it as the same edition or substitute its numbering.
- The author's [Patreon profile](https://www.patreon.com/Snollygoster/about) advertises extra chapters for the fanfiction; a specific [Chapter 18 post](https://www.patreon.com/Snollygoster/posts/chapter-18-thief-71377316) is locked. Paid/locked access is not archive permission.
- **Decision:** retain the merged +1 URL-offset fix, but do not retry until the complete paginated TOC is independently validated and explicit archive/distribution permission is documented.

## Live repository and workflow reconciliation

- Read-only audit #44924359606: **completed successfully**; job #136907075720 succeeded; metadata-only artifact #14714644436 remains available until 21 December 2026. The audit fetched no chapter prose.
- Existing Seoul Station's Necromancer run #44922285166: **completed successfully**, 209 chapters; final artifact #14714778249 expires 19 February 2027. This is an existing registry entry, not a new download.
- Latest Actions listing check: **0 queued/in-progress runs**; no active bulk downloads.
- Registry: **343**; separately user-confirmed private-HF imports: **70**; red/Dropped exclusions: **90**.
- No new download run or artifact was created.

## Public artifact exposure requiring repository-owner action

- Run #43734417289 artifact #14242470238 contains nine nested final ZIPs and expires **23 November 2026 at 21:27 IST**. Its individual Witcher ZIP #14225912094 expires **23 November 2026 at 17:58 IST**.
- Konoha Medical artifact #14462633408 remains public and rights-unverified; it expires 16 February 2027.
- Seoul Station's Necromancer artifact #14714778249 is also public and rights-unverified because its workflow recorded `confirm_rights=false`.
- No artifact contents were fetched in this round. The connected GitHub operations expose no artifact-deletion action. The repository owner must revoke any artifact lacking the necessary redistribution permission; do not fetch, link or redistribute its contents.

## Decision

No technical retry is justified by this evidence. The remaining blockers are permission, original-author authority and/or complete edition mapping, not a safe-to-fix transient downloader error. Preserve all existing registry/import/exclusion counts and keep the download backlog held until the required evidence exists.

# Public archive rights-policy check

**Checked:** 22 November 2026, 20:08 IST  
**Repository:** `RichardDaffern/Novel-Retriever` (public)  
**Purpose:** determine whether public source listings or host terms authorise this project to archive and publish downloaded book artefacts.

## Host terms reviewed

- **NovelFull:** [Privacy & Terms of Use](https://novelfull.net/tos) says its content is collected from public internet sources and free to read, but users must research the original copyright and bear responsibility for copyright violations. The page also describes third-party-hosted content. This is not a licence to copy a complete book into this repository's GitHub Actions artefacts.
- **ReadNovelFull:** [Privacy & Terms of Use](https://readnovelfull.com/site/tos) contains materially the same language: public-source collection and free reading do not transfer the original copyright or grant an off-platform archive licence.
- **FreeWebNovel / Novpub:** [Terms of Use](https://freewebnovel.com/termsofuse), clauses 3.3-3.5, limit the user-content licence to use through Novpub's services and allow other users to access/use content as permitted by the terms and service functionality. Uploaders warrant that they own the content or hold the necessary permissions. This does not grant an unrelated downloader blanket permission to reproduce and publish an archive elsewhere.

## Public artefact exposure

The repository is public. GitHub's [Actions artifact REST API documentation](https://docs.github.com/en/rest/actions/artifacts) states that public resources can be requested without authentication. Therefore, an EPUB/ZIP uploaded as a workflow artefact in this repository must be treated as publicly accessible, not private storage.

## Decision

1. A public listing, free-to-read page, translator credit, public TOC or the host's own right to display user content is **not** permission for this project to archive and publicly share the text.
2. Each title needs independently documented rights from the relevant copyright holder or authorised licensee covering both archiving and public sharing. If permission is private-only, do not use the current public Actions-artifact workflow.
3. The workflow's `confirm_rights` boolean is an operator attestation, not evidence. It must never be set merely because a page is public.
4. No title from the 26 exact source matches, five fresh candidates, 32 fanfiction research targets or 52 distinct Yup/IDK alternative-source titles was cleared by this terms review.
5. No download was dispatched. No chapter prose or archive bytes were fetched.

## Workflow change

The current bulk planner had applied `confirm_rights` only to WuxiaClick and Scribble Hub. NovelFull, FreeWebNovel and ReadNovelFull could reach public artifact uploads without a rights gate. PR #481 makes the gate universal and adds the same required input to the three direct source workflows. The fanfiction queue now requires per-title rights and public-distribution evidence and observes the two-active / ten-title-batch limits.

This is an operational fail-closed control, not legal advice or an independent substitute for reviewing the actual rights grant.

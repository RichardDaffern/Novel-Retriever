# Public artifact revocation inventory

**Checked:** 22 November 2026  
**Repository:** `RichardDaffern/Novel-Retriever` (public)

The source workflows for the two runs below recorded `confirm_rights=false`. The repository is public; GitHub documents that public artifact resources can be accessed without authentication. Treat all EPUB/ZIP and chapter-batch artefacts below as publicly accessible until deleted.

## Seoul Station's Necromancer

[Run #44922285166](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44922285166)  
**6 unexpired artefacts; expiry 19 February 2027**

- #14714022859 - chapter plan
- #14714541061 - bulk selection
- #14714742093 - chapter batch 1-200
- #14714778249 - final EPUB/TXT archive (209 chapters)
- #14715007303 - chapter batch 201-209
- #14715376071 - bulk performance report

## Konoha's Medical Ninja / HP: The Arcane Thief

[Run #44379388243](https://github.com/RichardDaffern/Novel-Retriever/actions/runs/44379388243)  
**22 unexpired artefacts; expiry 16 February 2027**

- #14461844843 - Konoha chapter batch 101-150
- #14461889504 - Konoha chapter batch 51-100
- #14462113968 - Konoha chapter batch 1-50
- #14462496706 - Arcane Thief partial batch 151-200
- #14462531280 - Arcane Thief chapter plan
- #14462536432 - Arcane Thief partial batch 1-50
- #14462576377 - Konoha chapter plan
- #14462633408 - Konoha final archive (444 chapters assembled; registry publication failed)
- #14462743018 - Konoha chapter batch 351-400
- #14462756477 - Arcane Thief partial batch 251-255
- #14462772708 - Konoha chapter batch 301-350
- #14463073426 - bulk performance report
- #14463236195 - Arcane Thief partial batch 101-150
- #14463375865 - bulk selection
- #14463572186 - Konoha chapter batch 201-250
- #14463591061 - Arcane Thief partial batch 51-100
- #14463616185 - Arcane Thief partial batch 201-250
- #14463963464 - bulk successful-novels manifest
- #14464031767 - Konoha chapter batch 151-200
- #14464033223 - bulk recovery manifest
- #14464310623 - Arcane Thief partial batch 201-250
- #14464506019 - Konoha chapter batch 401-444

This run contains chapter-batch artefacts for both works, not only the final Konoha archive. Arcane Thief has no verified complete final archive in this run.

## Other previously identified completed fanfiction artefacts

The following seven IDs were identified in the prior inventory. Their source run IDs and current expiry dates were not rechecked in this pass:

- #14464695010
- #14464369346
- #14469106672
- #14465975343
- #14463647756
- #14463808054
- #14469501148

## Owner action

- If redistribution permission cannot be established, delete the affected artefacts, including chapter batches and recovery outputs, not just the final EPUB.
- GitHub's [Actions artifact REST API](https://docs.github.com/en/rest/actions/artifacts) supports artifact deletion with repository Actions write permission. The connected GitHub toolset used for this task exposes artifact listing/download but not deletion, so repository-owner action through GitHub's UI or API is required.
- PR #481's merged rights gate prevents future public source workflows from proceeding without an explicit permission attestation. It does not retroactively remove these existing artefacts.

# Storage Controller integration: implemented

The dedicated [Taiyou Novels Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller)
received its independent [merged PR #28](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller/pull/28)
on 16 November 2026. This Retriever repository does not write to the
private Hugging Face dataset.

**Default mode is unchanged.** The controller's standard upload blocks
multiple ZIPs targeting the same book. For a folder combining earlier ZIPs
and fresh Retriever exports, explicitly enable its safe deduplication
preflight:

~~~powershell
python -m taiyou_storage.upload novels --dedupe-local
python -m taiyou_storage.upload novels --dedupe-local --interactive
~~~

On Windows, choose option **12** in `00_storage_menu.cmd`. Option **1**
retains the original strict workflow.

The preflight uses canonical HTTPS source URLs and exact normalised
title/author with verified EPUB/chapter hashes. Equivalent old ZIPs are
skipped without deletion. Different editions, changed stored chapters or
ambiguous remote identity block **all** cloud writes and require review.

Existing remote IDs, paths and personal metadata (reading progress, ratings,
comments, tags, collections and notes) remain authoritative. The controller
retains private dataset checks, revision locking, immutable local source
hashes, orphaned-data protection and explicit user approval.

**Safe sequence:** Extract the outer GitHub snapshot, keep the individual
ZIPs and old backups, run a read-only preview, resolve every conflict, then
apply interactively. Do not upload the outer export ZIP as an individual
book, do not delete backups and do not force a replacement.

**Outstanding acceptance test:** A real mixed collection of your historical
ZIPs and the current export still needs read-only verification. No live
Hugging Face upload was performed as part of this implementation.

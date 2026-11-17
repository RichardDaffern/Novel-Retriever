# WebNovel free-access trial: *Harry Potter: Platinum Dragon Wizard*

Checked on 17 November 2026. Book:
https://www.webnovel.com/book/33422293300201205

## Public website observations

- Public book catalogue lists **884 chapters**, author **BlurryPinkSnake**.
- The final entry (Chapter 884) is a conclusion/translator's note that says
  the story is over, rather than an additional normal story chapter.
- Ordinary public reading returned visible story prose for Chapters **1, 2,
  400, and 844**, with no sign-in or coin-purchase prompt on those sampled
  pages. The final editorial Chapter 884 was also publicly readable.
- There was no lock/VIP marker in the publicly rendered catalogue inspected.
  **This does not certify every single chapter is completely free.**
- Public book metadata and accessible rendered pages do not establish that
  GitHub Actions / Python HTTP access works. Earlier runner/browser probes
  encountered 403 and challenges.

Sample pages:
- https://www.webnovel.com/book/33422293300201205/89735050081387238
- https://www.webnovel.com/book/33422293300201205/89735050081387259
- https://www.webnovel.com/book/33422293300201205/94052948610440202
- https://www.webnovel.com/book/33422293300201205/98111515671985466
- https://www.webnovel.com/book/33422293300201205/98111572043430550

## Runner trial and source permission

The repository now has a **read-only** diagnostic:
\`python -m tools.webnovel_access_check\`, available in
[WebNovel - Public Access Diagnostic](../../.github/workflows/webnovel-public-access.yml).

The workflow makes at most four HTTPS requests for this particular book:
the book page and Chapters 1, 400 and 844. It verifies presence of a readable
body using the existing conservative WebNovel page parser; it reports only
metadata, word/character counts, sample statuses and safe error labels.
It does not persist or publish copyrighted prose, cookies, HTML, or EPUBs.
It stops immediately on HTTP 403/429, locked chapters, access challenges,
missing content or unknown page structures. It does not spoof a browser,
authenticate, retry, solve CAPTCHAs or use undocumented endpoints.

The output key \`outcome\` must be inspected. Green workflow execution means
**the diagnostic ran**, not that its sample pages passed. A failure to reach
WebNovel from a GitHub runner must not be mistaken for a Python code defect.

**Important licence distinction:** public/free reading is different from
permission to reproduce/export the work. WebNovel's
[terms](https://www.webnovel.com/terms_of_service) limit the right to use
site materials. This trial does not authorise mass downloading. No bulk website
source or individual full-book download workflow has been enabled.

If the author or platform provides an authorised EPUB or chapter export,
the existing local importer and Storage Controller ZIP packager support it
without contacting WebNovel or committing story text.

# Repository rename: completed

The owner renamed the GitHub repository from `RichardDaffern/Novel_Library`
to **[RichardDaffern/Novel-Retriever](https://github.com/RichardDaffern/Novel-Retriever)**
on 16 November 2026. This file is the compatibility record, not an
instruction to rename again.

The follow-up maintenance change corrects the exporter’s GitHub repository
guard, its API endpoint, the Windows artefact collector default, download
registry links, main README and historic guide links. Existing workflow
filenames, branches and completed run IDs remain unchanged. GitHub usually
redirects old URLs, but newly generated links must always target the new
repository directly.

For an existing local clone, run:

~~~powershell
git remote set-url origin https://github.com/RichardDaffern/Novel-Retriever.git
git remote -v
~~~

For unattended scripts, use the new repository name explicitly. The
consolidated export workflow is manual. Select **Actions > Export Completed
Novels - Hugging Face Upload Bundle > Run workflow**, then download the
resulting private-use archive. Do not assume expired GitHub artefacts can
be recovered.

**External integration:** The [Taiyou Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Novels-Storage-Controller)
does not need the Retriever's repository name when uploading a local ZIP.
Check any external links or bookmarked workflow URLs in other applications.
Do not push ZIP archives or novel contents to this Git repository.

**Verification:** Offline Linux and Windows CI covers code, ZIP packaging
and the renamed workflow guard. Live source-site and private Hugging Face
end-to-end validation must be separately performed with owner authorisation.

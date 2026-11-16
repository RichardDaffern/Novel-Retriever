# Proposed GitHub repository rename: Novel-Retriever

**Recommendation:** Novel-Retriever. It describes acquisition, conversion and
packaging; this repository is not a reading library. Do not rename until the
owner explicitly approves the final name.

## Preflight

- Record the repository ID, default branch, active runs, open pull requests,
  release tags and externally linked workflows.
- Merge or coordinate in-flight feature branches; do not rename during a
  long-running download/export campaign.
- Identify every literal RichardDaffern/Novel_Library reference in Python,
  PowerShell, workflow YAML and documentation; update these in one reviewed PR.
  In particular, GitHub API URL constants in the consolidated exporter,
  registry URLs, workflow repository guards, external actions workflow links
  and Windows helper instructions need review.
- Check the Hugging Face Storage Controller and the web reader for any
  hardcoded integration URLs. This is a cross-repository check, not an
  automatic mutation.

## Migration sequence after approval

1. Keep main and workflow filenames stable. Publish a compatibility
   documentation change showing both old and new URLs.
2. Rename the repository in GitHub Settings > General.
3. Update repository description, topics, README headline, AGENTS.md
   explanatory naming, workflows, scripts and integration documentation.
4. Replace absolute GitHub repository URLs and API endpoints with the new
   location. Prefer GITHUB_REPOSITORY in GitHub Actions where it is safe and
   avoids future hardcoded repository names.
5. Update local Git remotes:
   git remote set-url origin https://github.com/RichardDaffern/Novel-Retriever.git
6. Reconfirm GitHub App installation access, runner checkout branches,
   Actions permissions and workflow links; run CI and a small authorised
   smoke test. Verify cross-repository API consumers separately.
7. Retain legacy compatibility notes for users with old scripts.

GitHub generally redirects old repository and source URLs after a rename,
but clients should not rely on redirects for API writes, webhook payloads,
GitHub Actions run/artifact downloads or indefinite artefact retention.
Old artefacts remain subject to their original expiration dates. Test these
links explicitly and preserve release instructions for active campaigns.

**Current status:** Only this plan is committed. No repository settings,
repository name, remote URLs, running jobs or pre-existing artefacts were
modified by the rename proposal.

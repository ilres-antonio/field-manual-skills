# Issue tracker — GitHub Issues

Issues for this project live in GitHub Issues at
<https://github.com/ilres-antonio/field-manual-skills/issues>.

## How skills should interact with the tracker

Skills that file, read, or update issues use the `gh` CLI. The user is
authenticated; `gh auth status` returns "Logged in to github.com" with
the `repo` scope present.

### Creating an issue

```sh
gh issue create \
  --title "<short imperative>" \
  --body  "<markdown body, see template below>" \
  --label "needs-triage"
```

New issues land with the `needs-triage` label so they appear on the triage
queue. `/triage` will reclassify them.

### Issue body template

```markdown
## Context
What problem this addresses, with pointers to relevant code/files.

## Acceptance
- [ ] verifiable check
- [ ] verifiable check

## Out of scope
What this issue does NOT do (so a future agent doesn&#39;t expand it).

## Pointers
- `path/to/file.py:42` &mdash; relevant line
- ADR 000N if a past decision constrains the work
```

### Closing an issue

```sh
gh issue close <NUMBER> --reason "completed" --comment "<one-line resolution>"
```

Use `--reason "not planned"` for issues closed without action; pair with
the `wontfix` label.

### Reading recent issues

```sh
gh issue list --state open --limit 50 --json number,title,labels,createdAt
```

For triage-specific queries, see `docs/agents/triage-labels.md`.

## Conventions

- **One issue per shippable slice.** Use `/to-issues` to break a PRD into
  vertical slices before filing &mdash; not horizontal "backend ticket /
  frontend ticket" splits.
- **Reference the parent PRD as `parent: #N`** in the body so the
  triage labels can carry across the hierarchy.
- **Don&#39;t commit fixes by hand.** Issues are closed by commits whose
  message includes `Closes #N` or `Fixes #N`. The Ralph loop pattern
  relies on this.
- **No silent label deletions.** If a label name needs to change, update
  `docs/agents/triage-labels.md` first and re-run the label migration
  step in `/setup-matt-pocock-skills`.

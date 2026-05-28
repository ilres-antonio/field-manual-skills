# Domain docs — single-context layout

This repo uses the **single-context** layout. One `CONTEXT.md` at the
repo root holds the shared vocabulary; one `docs/adr/` directory at the
root holds past architectural decisions. Skills look here directly &mdash;
no map file, no per-area `CONTEXT.md`s.

## Files

| Path | Purpose |
| --- | --- |
| `CONTEXT.md`              | Domain glossary. Terms used in the tutorial, the Pomodoro module, the research workflow, and the update framework. Read this *before* introducing new jargon. |
| `docs/adr/0000-*.md`      | Meta-ADR. Explains how this repo uses ADRs and what counts as one. |
| `docs/adr/000N-*.md`      | One file per decision. Numbered, immutable once merged. Filename is `<NNNN>-<kebab-summary>.md`. |

## How skills should consume these

- **`/grill-with-docs`** reads `CONTEXT.md` at session start and uses
  the terms there to challenge fuzzy language during the grilling. When
  new terminology gets agreed upon, the skill appends to `CONTEXT.md` &mdash;
  always in the appropriate section (don&#39;t append at the end of file).
- **`/improve-codebase-architecture`** reads both `CONTEXT.md` (for
  domain terms) and `docs/adr/` (for past decisions that constrain
  refactoring). When proposing a refactor that touches a constrained
  area, it must cite the relevant ADR.
- **`/diagnose`** reads `docs/adr/` to understand why edge-case
  handling exists the way it does. Don&#39;t propose "simpler" fixes that
  contradict an accepted ADR &mdash; the ADR exists *because* the simpler
  version was wrong.
- **`/tdd`** reads `CONTEXT.md` when writing test names so the
  vocabulary matches.

## When to write a new ADR

> Only for decisions that calcify the codebase. If undoing the choice
> in six months would be cheap, skip the ADR.
>
> &mdash; Matt Pocock (cited in `notebook_output.json`, `anti-patterns`)

Examples that **belong** in an ADR:
- A module structure that other modules will depend on (ADR 0002).
- A semantic rule that future changes might violate without realizing
  (ADR 0001 &mdash; overrun discard).
- A choice of external service or protocol that&#39;s costly to swap.

Examples that **do not** belong in an ADR:
- "We picked Vitest over Jest" &mdash; trivially swappable.
- "We use 2-space indent" &mdash; that&#39;s `.editorconfig` territory.
- "Variable named `foo` instead of `bar`" &mdash; not a decision.

## Layout invariants

- `CONTEXT.md` lives at the repo root. Don&#39;t move it.
- `docs/adr/` lives at the repo root. Don&#39;t nest it under another
  area folder.
- ADR filenames are `NNNN-kebab-summary.md` &mdash; four-digit numbers,
  zero-padded, sequential, no gaps.
- ADRs are *immutable once merged*. Superseding decisions get a new ADR
  that references the old one as `Supersedes: ADR NNNN`.

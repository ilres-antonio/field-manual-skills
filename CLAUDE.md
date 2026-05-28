# CLAUDE.md — Field Manual vol.01

Agent-facing project notes. For human readers landing fresh, start with
`README.md` instead — it covers workflows. This file covers stack,
conventions, and the agent-skill configuration that downstream skills
need to know about.

## What this project is

A self-contained tutorial that teaches Matt Pocock's eight core Claude Code
skills by actually building a working Pomodoro app end to end, then
verifying every "Matt says" claim against transcripts from ten of his
videos via NotebookLM.

Tutorial + product + tests + NotebookLM research workflow +
update-detection framework, all in this directory.

## Stack & conventions

- **Frontend**: vanilla HTML, CSS, JS — no build step, no framework.
  `app.js` exposes `createPomodoro` and `mountPomodoroUI` on `window` so
  `tests.html` and the tutorial page can both use them.
- **Tests**: open `tests.html`. 12 assertions across 4 TDD slices, all in
  the browser, no `npm test`. The module is pure logic with injected
  dependencies (`now`, `storage`, `notifier`, `audio`).
- **Research tooling**: Python (`build_notebook.py`, `check_skills.py`).
  Two pip deps: `notebooklm-py[browser]` and `defusedxml`. Driven manually,
  no scheduler.
- **No build, no bundler, no minification.** Source files are the
  artifacts.

## Key files to know about

| File | Purpose |
| --- | --- |
| `index.html` / `styles.css` / `app.js` | The tutorial + the embedded Pomodoro UI. |
| `tests.html` | In-browser test harness. Source of truth for the module's contract. |
| `videos.md` | The curated 10-video corpus. Edit this *and* `build_notebook.py` together if extending. |
| `build_notebook.py` | NotebookLM driver. Per-URL + per-question idempotency. |
| `check_skills.py` | Update detector. Compares against `skills_snapshot.json`. |
| `notebook_output.json` | Frozen citation evidence. Every "Matt says" aside traces here. |
| `CONTEXT.md` | Domain language. Read this before adding new terms. |
| `docs/adr/` | Past architectural decisions. ADR 0001 and 0002 are load-bearing. |

## Agent skills

### Issue tracker

GitHub Issues at <https://github.com/ilres-antonio/field-manual-skills>.
Skills create issues via `gh issue create`. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical names — `needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` and `docs/adr/` both at the repo root.
See `docs/agents/domain.md`.

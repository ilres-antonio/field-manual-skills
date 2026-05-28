# Field Manual vol.01 — Building with mattpocock/skills

A self-contained tutorial that teaches Matt Pocock's eight core skills for
Claude Code by **actually building a working Pomodoro app** end to end, then
verifying every "Matt says" claim against transcripts from nine of his videos
via NotebookLM. Tutorial + product + tests + research workflow +
update-detection framework, all in one directory.

```
open index.html   →  read the tutorial
open tests.html   →  run the 12-test contract
py check_skills.py →  see if Matt has shipped anything new since last verified
```

Unaffiliated with Matt Pocock. Built as a reader's companion to
[mattpocock/skills](https://github.com/mattpocock/skills).

---

## What's in this folder

### The tutorial (open in any browser, no build step)

| File | Purpose |
| --- | --- |
| `index.html`  | Six-phase Field Manual. Hero, the four failure modes, the journey, the embedded Pomodoro app, the appendix, the provenance, the CTA. |
| `styles.css`  | The aesthetic — parchment + ink + signal red, Fraunces + Newsreader + JetBrains Mono. Includes the `.pomodoro` and `.callout--side-skill` component scopes. |
| `app.js`      | Tutorial interactions (copy buttons, scroll-spy, terminal sim) **and** the `createPomodoro` factory + `mountPomodoroUI`. The module exposes itself on `window` for `tests.html`. |
| `tests.html`  | In-browser test harness for `createPomodoro`. 12 assertions across 4 TDD slices, runs on open, no `npm test`. |

### The research workflow

| File | Purpose |
| --- | --- |
| `videos.md`              | The corpus — nine Matt Pocock videos with per-video rationale and explicit sourcing notes (which ones came from search, which were user-added, which were excluded and why). |
| `build_notebook.py`      | NotebookLM driver. Creates one notebook, ingests the 9 videos, asks 17 targeted questions. Idempotent: skip already-answered questions, skip already-ingested sources. |
| `notebook_output.json`   | Full structured output: per-question answer + every citation traced to a `source_id`. 17 entries, ~300 KB. The frozen evidence the tutorial cites. |
| `notebook_output.md`     | Human-readable digest of the same data. Used to spot-check quotes before integration. |

### The update-detection framework

| File | Purpose |
| --- | --- |
| `check_skills.py`        | One command. Fetches mattpocock/skills tree + the YouTube channel RSS feed, diffs against the snapshot, prints a classified report with exact next commands. No auto-execute. |
| `skills_snapshot.json`   | Baseline state: per-skill blob SHAs (59 files across `engineering/`, `in-progress/`, `deprecated/`, `productivity/`, `misc/`, `personal/`), plus the latest 15 video IDs. Updated by `--refresh`. |

---

## Common workflows

### 1. Just read the tutorial

```
open index.html
```

Twenty-five minutes start to finish, including pauses at the embedded Pomodoro
in Phase IV. Click the **demo** mode toggle on the timer to watch a full
work → break → work → work → work → long-break cycle in ~30 seconds and see
every phase transition the artifact card references.

### 2. Run the tests

```
open tests.html
```

12 / 12 should pass. The `createPomodoro` factory is exercised with stub
dependencies (fake clock, in-memory storage, captured notifier) — no real
`setInterval`, `localStorage`, or `Notification` needed.

Failure rows expand to show the assertion that broke. The same test
*names* appear as artifact code in Phase IV; the harness is the *real* source.

### 3. Extend the corpus with new videos / questions

Three steps. The first run was 11 questions × 9 videos; idempotent re-runs
will skip everything already in `notebook_output.json`.

```
# 1. Add to videos.md with a rationale, and to build_notebook.py VIDEOS list.
# 2. Add per-video deep-dive questions to QUESTIONS in build_notebook.py.
#    Timestamped keys (e.g. "handoff-changelog-2026-08") preserve history.
# 3. Re-run.
py build_notebook.py
```

Only new questions fire against the existing notebook. Cost: ~30 seconds per
new question, no source re-ingestion.

### 4. Check for skill updates from upstream

```
py check_skills.py             # detect + report + recommend
py check_skills.py --refresh   # capture new baseline, rewrite colophon
```

Manual trigger by design. If anything has changed in `mattpocock/skills` or
on Matt's YouTube channel since the snapshot, you get a classified diff and
the *exact* commands to run next — including suggested `VIDEOS` and
`QUESTIONS` entries to paste into `build_notebook.py`, and the line numbers
in `index.html` that mention affected skill slugs.

**The framework deliberately stops before auto-editing the tutorial.** You
keep judgment over every quote that lands in `index.html`. NotebookLM answers
need spot-checking; the script will not do that for you.

---

## Setup, from scratch

The tutorial itself needs nothing — open `index.html`.

The research and update-check tooling needs Python 3.10+ and two pip packages:

```
py -m pip install "notebooklm-py[browser]" defusedxml
C:\Python313\Scripts\playwright.exe install chromium
C:\Python313\Scripts\notebooklm.exe login        # one-time Google OAuth
```

After login, `build_notebook.py` and `check_skills.py` both work. The
notebook ID is hard-coded into the script via title lookup — you'll create
your own notebook on first run and reuse it idempotently.

---

## Architectural notes worth keeping

**The Pomodoro module owns no clock.** `createPomodoro` exposes `tick()`;
the UI calls `setInterval(() => pomodoro.tick(), 250)`. Tests advance a fake
clock and call `tick()` directly. This is ADR 0002 in Phase V — and the
reason the polish layer (demo mode, duration inputs, SVG ring) was written
entirely in the UI without touching a single line of the module.

**Overrun is discarded at phase transitions.** A 1500ms tick into a 1000ms
work session starts the break at the *full* `breakMs`, not 500ms short. This
is ADR 0001 — caught by the first failing test in slice 2, before the
implementation existed. The test is in `tests.html` if you want to see it.

**The corpus is a citable decision, not just config.** `videos.md` exists as
a separate document from `build_notebook.py` because the rationale for
*which* videos count as authoritative source material is a different artifact
from the runtime list. Per-video "why this is in the corpus" notes + an
"explicitly excluded" section.

**Skills updates fan out across two surfaces.** Skill *text* edits in the
repo are diffed externally via GitHub's compare URL — the diff IS the answer
and NotebookLM adds no value. *New videos* go through NotebookLM's existing
ingestion pipeline because video transcripts genuinely need parsing. The
framework splits the work cleanly across the right tool.

---

## Honesty notes

- **Not affiliated with Matt Pocock.** This is a reader's companion, not an
  official tutorial.
- **The video corpus snapshot is frozen.** Citations point to
  `source_id`s in `notebook_output.json`; NotebookLM may re-index its sources
  later and shift the citation chunk boundaries. The JSON file is the paper
  trail.
- **Two skills are honestly skipped**: `/migrate-to-shoehorn` (TS-only,
  this build is vanilla JS) and `/scaffold-exercises` (for course authors,
  not single-app builds). Listed in the tutorial's appendix with the
  reason for the skip.
- **The colophon's verification line is the source of truth for freshness.**
  If it says "last checked 2026-05-28" and the current date is six months
  later, run `py check_skills.py` and act on what it tells you.

---

## License

The tutorial content (text, markup, styling, sample app code) is offered
as-is for personal use. Quoted material from Matt Pocock's videos remains
his.

The dependencies have their own licenses:
[notebooklm-py](https://github.com/teng-lin/notebooklm-py) (unofficial,
"use at your own risk"), [Playwright](https://playwright.dev/),
[defusedxml](https://pypi.org/project/defusedxml/).

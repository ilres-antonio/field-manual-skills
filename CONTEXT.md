# Field Manual vol.01 — Ubiquitous Language

The shared vocabulary used across the tutorial, the research workflow, and
the agent-skill configuration. Skills like `/grill-with-docs` and
`/improve-codebase-architecture` read this file to align terminology before
asking questions or proposing refactors. Update inline when a new term gets
introduced — don't add unannounced jargon.

## Tutorial structure

- **phase** — one of the six waypoints in the journey (I&nbsp;setup, II&nbsp;align,
  III&nbsp;spec, IV&nbsp;build, V&nbsp;maintain, VI&nbsp;handoff). Each phase has a
  numeral, a kicker, narrative, terminal sim, side-skill callouts, and an
  artifact card.
- **side-skill callout** — an `aside--side-skill` block inside a phase;
  surfaces a skill that's *not* part of the core 8 but naturally fires
  during that phase (e.g. `/git-guardrails-claude-code` in setup,
  `/caveman` in build). The tutorial has exactly 9 side-skill callouts;
  count is structurally verified.
- **failure mode** — one of the four diagnoses in the opening section
  (misalignment, verbosity, broken code, architectural decay). Each
  failure mode is paired with the skills that cure it.

## Pomodoro module

- **session** — one work or break phase. Lengths configurable via
  `workMs`, `breakMs`, `longBreakMs` on construction.
- **phase** (Pomodoro sense, *not* tutorial sense) — `work`, `break`, or
  `longBreak`. The pomodoro&#39;s `state.phase` is this; the tutorial&#39;s
  `phase` is the journey waypoint. Context disambiguates.
- **tick** — one step of forward time. The UI calls `pomodoro.tick()` on
  a `setInterval`; the module advances state based on `now()` since the
  last tick. The module owns no clock — see ADR 0002.
- **auto-flip** — when a session reaches zero remaining, the module
  transitions to the next phase automatically. Overrun is discarded —
  see ADR 0001.
- **completed** — the counter that increments only when a *work* session
  ends. Used to decide when the 4th break becomes a long break.

## Research workflow

- **corpus** — the curated 11 videos in `videos.md` that have been
  ingested into the NotebookLM notebook for citation purposes. Distinct
  from the *snapshot videos* (see below).
- **snapshot videos** — the 15 most-recent uploads from Matt&#39;s YouTube
  channel as captured in `skills_snapshot.json`. Used by
  `check_skills.py` to detect new uploads; *not* the same set as the
  corpus.
- **provenance card** — one of the 11 cards in the `#provenance` section
  of `index.html`. Each card maps a video to the specific claims it
  sourced.
- **freshness signal** — the `<p data-verified-line>` paragraph in the
  colophon, rewritten by `check_skills.py --refresh`. The only piece of
  the tutorial whose content is generated rather than hand-edited.
- **citation** — a `ChatReference` entry in `notebook_output.json`
  linking a "Matt says" claim in the tutorial to a specific source video
  ID + character offset. Treat these as load-bearing &mdash; quotes that
  can&#39;t be traced to a citation shouldn&#39;t survive a review.

## Skill-update framework

- **snapshot** — the JSON file capturing per-skill blob SHAs + recent
  video IDs at the moment of last verification. Lives in
  `skills_snapshot.json` and gets committed.
- **classified diff** — the output of `check_skills.py`. Categorizes
  changes into `ADDED`, `REMOVED`, `CHANGED` (skills) and `NEW VIDEOS`,
  with recommended next commands.
- **idempotency** — both `build_notebook.py` and `check_skills.py` are
  designed to be re-run safely. Already-ingested videos are skipped;
  already-answered questions are skipped; already-captured snapshot
  state is overwritten on `--refresh` only.

## Out of scope

The tutorial covers eight core skills + nine secondary skills.
`/migrate-to-shoehorn` and `/scaffold-exercises` are honestly skipped in
the appendix &mdash; don&#39;t treat them as load-bearing for this project.

Live-stream content (one video in the corpus) is treated as
*contradicting evidence* against the polished videos &mdash; not the canonical
source for the framework, but the evidence of how it actually plays out.

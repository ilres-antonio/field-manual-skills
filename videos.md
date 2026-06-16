# Matt Pocock — skill-related videos for the notebook corpus

The eleven videos below were identified via web search, direct user additions,
and the `check_skills.py` update detector, as the most directly relevant to the
Field Manual tutorial. Each is queued in
`build_notebook.py` to be ingested into a NotebookLM notebook titled
**"Matt Pocock skills — video corpus (tutorial research)"** after interactive
auth (`notebooklm login`) is complete.

If you want to add or remove videos, edit the `VIDEOS` list in `build_notebook.py`
before running the driver. The labels here match the labels used in that file.

---

## The corpus

### 1. 5 Claude Code skills I use every single day
- **URL:** https://www.youtube.com/watch?v=EJyuu6zlQCg
- **Published:** March 16, 2026
- **Why it matters for the tutorial:** Matt names his five most-used skills and the
  daily trigger for each. Lets us replace the tutorial's *implied* daily-rotation
  with Matt's own list and his framing of when each one fires.

### 2. I Tried "grill-me" Skill for Plan Mode. Wow.
- **URL:** https://www.youtube.com/watch?v=rLNLa2dcjG8
- **Published:** April 12, 2026
- **Why it matters:** Direct, focused coverage of `/grill-me`. The tutorial's Phase II
  ("Align") leans on this skill heavily; Matt's own first-person account of what a
  good grilling feels like is the highest-quality content we can quote.

### 3. I stopped using /grill-me for coding. Here's what I use instead
- **URL:** https://www.youtube.com/watch?v=6BB6exR8Zd8
- **Published:** ~2 weeks ago (May 2026)
- **Why it matters:** Introduces `/grill-with-docs` as the evolution of `/grill-me`.
  The tutorial currently treats `/grill-with-docs` as just "the variant that reads
  docs first" — Matt's video apparently makes a stronger case for *replacing*
  `/grill-me` with it for coding tasks. If true, that's a real correction to make.

### 4. Building a REAL feature with Claude Code: every step explained
- **URL:** https://www.youtube.com/watch?v=hX7yG1KVYhI
- **Published:** March 18, 2026
- **Why it matters:** **This is the single most important video for our tutorial.**
  It's *literally* the genre we built — Matt walking through one feature end to end.
  If his stages differ from our six-phase journey (setup → align → spec → build →
  maintain → handoff), we need to know.

### 5. Red Green Refactor is OP With Claude Code
- **URL:** https://www.youtube.com/watch?v=hYZdIwFIy-c
- **Published:** February 23, 2026
- **Why it matters:** Matt's own articulation of the TDD discipline that Phase IV
  ("Build") teaches. Want to confirm we're representing his red-green-refactor
  framing faithfully and pick up any concrete examples he gives.

### 6. How I Test With Claude Code (AI TDD)
- **URL:** https://www.youtube.com/watch?v=Kx7bAwVH_1c
- **Published:** April 11, 2026
- **Why it matters:** Companion to #5. Probably contains the specific assertion
  patterns Matt uses with Claude Code — useful for validating the test style shown
  in the Pomodoro `tests.html`.

### 7. /handoff is my new favourite skill
- **URL:** https://www.youtube.com/watch?v=dtAJ2dOd3ko
- **Published:** ~1 week ago (May 2026)
- **Source:** user-added
- **Why it matters:** Direct first-party content for Phase VI ("Handoff") — the
  most under-researched phase of our tutorial, currently inferred from the repo
  README and the "what is a good handoff" reasoning the model arrived at on its
  own. Matt explains *why he built* `/handoff` and how it differs from naive
  conversation-summary approaches. Likely to reshape Phase VI substantively.

### 8. Burn through the backlog from hell with /triage
- **URL:** https://www.youtube.com/watch?v=MzWIIlx0Gpc
- **Published:** ~3 weeks ago (May 2026)
- **Source:** user-added
- **Why it matters:** Direct first-party content on `/triage`, which the tutorial
  currently treats as a Phase III side-skill ("won't fire today — no bugs yet").
  Matt's video frames it as a way to turn a messy backlog of human ideas into
  agent-actionable tasks. If true, that's a much bigger role than "categorize
  incoming bugs" and the side-skill callout needs to be rewritten.

### 9. How To De-Slop A Codebase Ruined By AI (with one skill)
- **URL:** https://www.youtube.com/watch?v=3MP8D-mdheA
- **Published:** ~1 month ago (April–May 2026)
- **Source:** user-added
- **Why it matters:** The "one skill" is almost certainly
  `/improve-codebase-architecture` (the video's stated topic — deep modules and
  good architecture — matches that skill exactly). Direct first-party content
  for Phase V ("Maintain"). The tutorial currently frames the skill as "find
  shallow modules and deepen them" via the repo README; Matt's video apparently
  frames it as a *rescue* operation for AI-degraded codebases. That's a stronger,
  more actionable framing if accurate.

### 10. LIVE: Watch me build a brand-new project from scratch
- **URL:** https://www.youtube.com/watch?v=K-mA3MZ_EzU
- **Published:** April 17, 2026
- **Source:** user-added
- **Why it matters:** The only **live-stream** in the corpus. Every other video
  is post-produced and polished — Matt knows what he wants to demonstrate. This
  one is unscripted: he reaches for skills in real time, gets stuck, backtracks,
  decides what to do next without an editor's hindsight. The signal we cannot
  get from the other nine videos: the *actual friction points* in the workflow,
  the *order he reaches for skills under pressure*, the moments where he
  ad-libs around the skill text. Risk: long-form (likely 1–3 hours), so the
  NotebookLM ingestion will take longer than the other videos, and the chunk
  density per topic is lower.

### 11. Learn anything with the /teach skill
- **URL:** https://www.youtube.com/watch?v=s5T5oQJcJ6U
- **Published:** June 8, 2026
- **Source:** detected via `check_skills.py` (update detector), 2026-06-16
- **Why it matters:** Announces `/teach`'s graduation from `in-progress` to
  `productivity` in mattpocock/skills. `/teach` is *out of scope* for the
  tutorial's eight core skills (see `CONTEXT.md`), so this video does **not**
  drive a Phase rewrite. It's ingested as first-party evidence of how Matt
  frames a learning/teaching workflow — corpus context for a possible future
  volume, and to keep the corpus aligned with the freshly-refreshed snapshot.

---

## Sourcing notes

- Six of ten titles surfaced via a Google search restricted to `site:youtube.com`
  matching `mattpocockuk` (Matt's channel handle) and at least one of:
  `"Claude Code"`, `"skills"`, `"grill-me"`, `"tdd"`. Entries #7, #8, #9, and
  #10 were added directly by the user during the corpus assembly.
- I was **not** able to fetch the channel page directly to enumerate every video —
  YouTube redirected my fetch to a consent wall (`consent.youtube.com/...`).
- The titles and dates above come from search-result snippets, not from the videos
  themselves. NotebookLM will read the actual content; titles/dates are sanity
  signals only.

## Out of corpus (deliberately excluded)

- **Matt Pocock's skills: the agent skills a real engineer actually uses every day**
  (YouTube Short, `https://www.youtube.com/shorts/pBzem1HTg_Y`) — search did not
  confirm authorship; could be a third party reacting to the repo. Excluded to keep
  the corpus to first-party Matt content only.
- **Matt Pocock's Skills Just Changed AI Coding Forever 🤯**
  (`https://www.youtube.com/watch?v=EkpSSqbPF_k`) — title style and 🤯 emoji are
  uncharacteristic of Matt; almost certainly a third-party commentary video.
  Excluded for the same reason.

---

## Next step

Run interactive auth in a terminal (one-time):

```
C:\Python313\Scripts\notebooklm.exe login
```

A Chromium window opens. Sign in to the Google account that should own the notebook.
The session is saved to `~/.notebooklm/profiles/default/storage_state.json`.

Then:

```
py C:\Users\antonio\Documents\projects\skills\build_notebook.py
```

The driver creates the notebook, ingests all six videos (this typically takes several
minutes — NotebookLM processes each one server-side), runs 8 targeted questions, and
writes the answers to:

- `notebook_output.json` — full structured output (sources, Q&A, citations, errors)
- `notebook_output.md` — human-readable digest used to update `index.html`

Tell me when those files exist and I'll integrate the findings into the tutorial.

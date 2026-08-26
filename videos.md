# Matt Pocock — skill-related videos for the notebook corpus

The twenty-six videos below were identified via web search, direct user additions,
and the `check_skills.py` update detector, as the most directly relevant to the
Field Manual tutorial. Entries 1-11 are the original verified corpus; entries
12-26 were added on 2026-08-26 when the detector found 71 days of channel drift
alongside the upstream v1.2 reorganisation (`694fa30` → `6654f6b`). Those fifteen
are **not yet ingested** — their notes below carry expectations to test, not
findings to cite. Each is queued in
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

### 12. LIVE: Uncle Bob on Software Fundamentals in the Age of AI
- **URL:** https://www.youtube.com/watch?v=zcLPGC-tvgk
- **Published:** August 19, 2026
- **Why it matters:** A long-form conversation with Robert C. Martin. Not a skills video, but the corpus's
  only outside voice on whether the fundamentals the skills encode (small modules, tests
  first, naming) still hold when an agent writes the code. Useful as a check on the
  tutorial's framing in Phase V, which asserts that discipline matters *more* with agents,
  not less — currently our own claim, unsourced.

### 13. New Skills! v1.2 brings /wait-what, /writing-for-agents, and fixes /grill-me
- **URL:** https://www.youtube.com/watch?v=gaDdrDdczO4
- **Published:** August 5, 2026
- **Why it matters:** **The keystone video for this round.** This is the release announcement for the v1.2
  reorganisation that moved upstream from `694fa30` to `6654f6b` — the same change that
  renamed `/diagnose` and `/to-prd`, deleted `/to-issues`, `/zoom-out`, `/write-a-skill`
  and `/caveman`, and split `/domain-modeling` and `/codebase-design` out as new
  model-invoked siblings. The GitHub diff tells us *what* moved; this should tell us *why*.

### 14. /wayfinder: Nothing is too big to plan anymore
- **URL:** https://www.youtube.com/watch?v=F3lL98Pj90o
- **Published:** July 30, 2026
- **Why it matters:** Introduces `/wayfinder`, the closest thing to a replacement for the deleted `/zoom-out`.
  The tutorial's Phase V cites `/zoom-out` as the altitude-gaining precondition for
  spotting shallow modules; `/wayfinder` is framed upstream as planning work too large for
  one agent session, which is a *different* job. Needed to decide whether Phase V's claim
  survives the rename or has to be rewritten.

### 15. Don't waste time on specs: /prototype instead
- **URL:** https://www.youtube.com/watch?v=n0VhIVtviC0
- **Published:** July 23, 2026
- **Why it matters:** Argues prototyping over specification — in direct tension with the tutorial's Phase III,
  which routes idea → `/to-spec` → `/to-tickets` before any code is written. If Matt now
  recommends skipping the spec for some class of work, Phase III needs a stated boundary
  condition rather than a straight-line sequence.

### 16. There is no such thing as greenfield
- **URL:** https://www.youtube.com/watch?v=0l7zOp260yc
- **Published:** July 21, 2026
- **Why it matters:** Challenges the tutorial's premise directly: the Field Manual builds a Pomodoro app from
  nothing, which is a greenfield exercise. If Matt's position is that greenfield is a
  fiction, the tutorial should say what the exercise stands in for rather than implying a
  blank directory is the normal case.

### 17. Using /grill-me for interviews?!
- **URL:** https://www.youtube.com/watch?v=5hYsBUMmr-I
- **Published:** July 20, 2026
- **Why it matters:** An off-label use of `/grill-me` (interviewing people, not plans). Low priority for the
  build sequence, but it bears on Phase II's claim about what grilling *is* — a general
  interrogation engine rather than a planning-specific tool.

### 18. What is the dumb zone?
- **URL:** https://www.youtube.com/watch?v=sOd7svdu_1I
- **Published:** July 20, 2026
- **Why it matters:** **Already sourced by the tutorial, second-hand.** The “dumb zone” aside in Phase IV
  quotes the ~120k-usable-context claim, currently attributed to a different video in the
  corpus. This is the dedicated treatment; it should either confirm that quote or give us
  a better one. It matters more now that `/caveman` — the aside's recommended mitigation
  — has been deleted upstream.

### 19. Do you even need human review?
- **URL:** https://www.youtube.com/watch?v=Yn8h5Ip-L9c
- **Published:** July 20, 2026
- **Why it matters:** Bears on the new `/code-review` skill (which supersedes the in-progress `/review`) and on
  the tutorial's Phase V stance that the human is the “strategic programmer” making the
  calls. If Matt has moved toward agent-only review for some changes, that stance needs
  qualifying.

### 20. This change makes /grill-me SO MUCH BETTER
- **URL:** https://www.youtube.com/watch?v=tLyfDIt9wHg
- **Published:** July 17, 2026
- **Why it matters:** A concrete change to `/grill-me`, which the diff confirms was modified this round.
  Phase II leans on `/grill-me` heavily; this should tell us whether the tutorial's
  description of what a grilling session feels like is still accurate.

### 21. Framework Hell, Tutorial Hell... now Skill Hell
- **URL:** https://www.youtube.com/watch?v=32LyZyFQhCQ
- **Published:** July 17, 2026
- **Why it matters:** A caution about skill proliferation — pointed squarely at a tutorial whose structure is
  “here are eight skills, in order.” Worth surfacing as a counterweight in the closing
  section rather than ignoring; a field manual that never warns about over-tooling is
  selling something.

### 22. Kill your MEMORY.md
- **URL:** https://www.youtube.com/watch?v=A0scuiiGBC4
- **Published:** July 17, 2026
- **Why it matters:** An argued reversal on a common practice. Relevant to the tutorial's Phase I setup advice
  and to anything it says about persistent agent memory versus `CONTEXT.md` and ADRs as
  the durable record.

### 23. Do software fundamentals still matter?
- **URL:** https://www.youtube.com/watch?v=eEjBhVI9Qok
- **Published:** July 16, 2026
- **Why it matters:** Short-form companion to the Uncle Bob stream. Same question, Matt's own framing, and far
  cheaper to quote than a multi-hour livestream.

### 24. My /teach skill is still insane
- **URL:** https://www.youtube.com/watch?v=glaIO6OYh74
- **Published:** July 16, 2026
- **Why it matters:** Follow-up to the `/teach` video already in the corpus (`s5T5oQJcJ6U`), whose
  stateful/stateless insight is already integrated into the tutorial. The diff shows all
  five `/teach` files changed this round, so this is the likeliest source for what moved.

### 25. Claude Code's system tools are SO BLOATED
- **URL:** https://www.youtube.com/watch?v=oLx4yCbeklQ
- **Published:** July 16, 2026
- **Why it matters:** On the context cost of tool definitions. Connects to the dumb-zone material: if system
  tooling eats the budget before your code does, that sharpens the tutorial's advice on
  when to hand off.

### 26. mattpocock/skills: A complete AI Coding workflow, end-to-end
- **URL:** https://www.youtube.com/watch?v=M6mYodf0dJM
- **Published:** July 16, 2026
- **Why it matters:** The end-to-end walkthrough of the whole repo post-reorganisation. The single best source
  for checking whether the tutorial's six-phase journey still matches Matt's own sequence,
  which is the spine of the entire Field Manual.
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

The driver creates the notebook, ingests each video (this typically takes several
minutes — NotebookLM processes each one server-side), runs the question set, and
writes the answers to:

- `notebook_output.json` — full structured output (sources, Q&A, citations, errors)
- `notebook_output.md` — human-readable digest used to update `index.html`

Tell me when those files exist and I'll integrate the findings into the tutorial.

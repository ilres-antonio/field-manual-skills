"""
build_notebook.py — feed Matt Pocock's skill-related videos into a NotebookLM
notebook and capture answers to questions that will inform tutorial updates.

Prereq:
    py -m pip install "notebooklm-py[browser]"
    C:\\Python313\\Scripts\\playwright.exe install chromium
    C:\\Python313\\Scripts\\notebooklm.exe login        # interactive Google OAuth (one-time)

Then:
    py build_notebook.py

Output:
    notebook_output.json   — { sources: [...], qa: [{question, answer, citations}] }
    notebook_output.md     — human-readable digest used to update index.html
"""
from __future__ import annotations

import asyncio
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Force UTF-8 on Windows so the ✓/·/✗ glyphs in our log lines render rather than
# crashing the script with UnicodeEncodeError under cp1252.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from notebooklm import NotebookLMClient
except ImportError:
    sys.exit("notebooklm-py is not installed. Run: py -m pip install \"notebooklm-py[browser]\"")


# ---- Inputs ---------------------------------------------------------------

NOTEBOOK_TITLE = "Matt Pocock skills — video corpus (tutorial research)"

# Matt Pocock videos confirmed (by title) to discuss Claude Code skills.
# Each entry: (url, short label used in the digest).
VIDEOS = [
    ("https://www.youtube.com/watch?v=EJyuu6zlQCg", "5 Claude Code skills I use every single day"),
    ("https://www.youtube.com/watch?v=rLNLa2dcjG8", "I Tried grill-me Skill for Plan Mode"),
    ("https://www.youtube.com/watch?v=6BB6exR8Zd8", "I stopped using /grill-me — what I use instead (/grill-with-docs)"),
    ("https://www.youtube.com/watch?v=hX7yG1KVYhI", "Building a REAL feature with Claude Code: every step explained"),
    ("https://www.youtube.com/watch?v=hYZdIwFIy-c", "Red Green Refactor is OP With Claude Code"),
    ("https://www.youtube.com/watch?v=Kx7bAwVH_1c", "How I Test With Claude Code (AI TDD)"),
    ("https://www.youtube.com/watch?v=dtAJ2dOd3ko", "/handoff is my new favourite skill"),
    ("https://www.youtube.com/watch?v=MzWIIlx0Gpc", "Burn through the backlog from hell with /triage"),
    ("https://www.youtube.com/watch?v=3MP8D-mdheA", "How To De-Slop A Codebase Ruined By AI (with one skill)"),
    ("https://www.youtube.com/watch?v=K-mA3MZ_EzU", "LIVE: Watch me build a brand-new project from scratch"),
    ("https://www.youtube.com/watch?v=s5T5oQJcJ6U", "Learn anything with the /teach skill"),

    # --- added 2026-08-26 from check_skills.py (RSS drift since 2026-06-16) ---
    ("https://www.youtube.com/watch?v=zcLPGC-tvgk", "LIVE: Uncle Bob on Software Fundamentals in the Age of AI"),
    ("https://www.youtube.com/watch?v=gaDdrDdczO4", "New Skills! v1.2 brings /wait-what, /writing-for-agents, and fixes /grill-me"),
    ("https://www.youtube.com/watch?v=F3lL98Pj90o", "/wayfinder: Nothing is too big to plan anymore"),
    ("https://www.youtube.com/watch?v=n0VhIVtviC0", "Don't waste time on specs: /prototype instead"),
    ("https://www.youtube.com/watch?v=0l7zOp260yc", "There is no such thing as greenfield"),
    ("https://www.youtube.com/watch?v=5hYsBUMmr-I", "Using /grill-me for interviews?!"),
    ("https://www.youtube.com/watch?v=sOd7svdu_1I", "What is the dumb zone?"),
    ("https://www.youtube.com/watch?v=Yn8h5Ip-L9c", "Do you even need human review?"),
    ("https://www.youtube.com/watch?v=tLyfDIt9wHg", "This change makes /grill-me SO MUCH BETTER"),
    ("https://www.youtube.com/watch?v=32LyZyFQhCQ", "Framework Hell, Tutorial Hell... now Skill Hell"),
    ("https://www.youtube.com/watch?v=A0scuiiGBC4", "Kill your MEMORY.md"),
    ("https://www.youtube.com/watch?v=eEjBhVI9Qok", "Do software fundamentals still matter?"),
    ("https://www.youtube.com/watch?v=glaIO6OYh74", "My /teach skill is still insane"),
    ("https://www.youtube.com/watch?v=oLx4yCbeklQ", "Claude Code's system tools are SO BLOATED"),
    ("https://www.youtube.com/watch?v=M6mYodf0dJM", "mattpocock/skills: A complete AI Coding workflow, end-to-end"),
]

# Questions designed to extract claims the tutorial currently approximates
# from the repo README. We want Matt's *own framing* in his videos.
QUESTIONS = [
    ("grill-me-rationale",
     "In Matt's own words, what specific failure mode does /grill-me prevent, "
     "and what does a good grilling session feel like compared to a bad one? "
     "Include any concrete examples Matt gives."),

    ("grill-with-docs-distinction",
     "How does /grill-with-docs differ from /grill-me in practice? "
     "When does Matt recommend each one? Quote him directly if possible."),

    ("daily-skills",
     "Which 5 skills does Matt say he uses every single day? "
     "For each one, what is the trigger (the moment he reaches for it) "
     "and the artifact it produces?"),

    ("tdd-discipline",
     "What is Matt's specific TDD workflow with Claude Code? "
     "How does he keep the agent from skipping the red step? "
     "Any concrete examples of catching a bug because the test came first?"),

    ("real-feature-journey",
     "In the 'Building a REAL feature' video, what are the actual stages "
     "Matt walks through from idea to shipped feature? "
     "Are they the same as the 6-phase journey (setup, align, spec, build, maintain, handoff)? "
     "Where do they differ?"),

    ("skill-sequencing",
     "What does Matt say about the ORDER in which skills should be applied? "
     "Are there hard dependencies (X must come before Y), or is order flexible?"),

    ("anti-patterns",
     "What anti-patterns or common mistakes does Matt warn against in these videos? "
     "Anything specific to how people misuse Claude Code skills?"),

    ("surprising-claims",
     "Identify 3-5 claims Matt makes in these videos that would surprise a "
     "developer who has only read the GitHub README. Quote him directly."),

    ("handoff-deepdive",
     "In the '/handoff is my new favourite skill' video specifically, "
     "what does Matt say is the failure mode that triggered him to build /handoff? "
     "How does it differ from naive 'summarize the conversation' approaches? "
     "What concretely goes into a HANDOFF.md that does NOT go into CONTEXT.md? "
     "Quote him directly where possible."),

    ("triage-deepdive",
     "In the 'Burn through the backlog from hell with /triage' video specifically, "
     "is /triage just for incoming bug reports, or does Matt use it for something larger? "
     "What is the actual workflow he describes — does /triage come BEFORE /to-prd "
     "and /to-issues, after, or in parallel? Quote him directly where possible."),

    ("deslop-deepdive",
     "In the 'How To De-Slop A Codebase Ruined By AI' video, which specific skill "
     "does Matt use, and what does the de-slopping process actually look like step by step? "
     "What are the signs of an AI-degraded codebase he names? "
     "How is this different from normal refactoring? Quote him directly where possible."),

    # ---- second-round per-video deep-dives (the 6 videos that didn't get one yet) ----

    ("daily-skills-cadence",
     "In the '5 Claude Code skills I use every single day' video specifically, "
     "what is the typical ORDER Matt chains the skills in a single working day? "
     "Does he show a complete day's chain — e.g., morning grill, midday TDD, "
     "afternoon refactor? Are there approximate time gaps between skills, or does he "
     "describe interleaving multiple sessions? Quote him directly where possible."),

    ("plan-mode-comparison",
     "In the 'I Tried grill-me Skill for Plan Mode' video specifically, "
     "does the source give a concrete side-by-side comparison of Claude Code's "
     "default plan mode versus /grill-me on the same prompt? "
     "How many questions does each ask? What does each produce as final output? "
     "Quote specific numbers and behaviors where given."),

    ("grill-with-docs-changelog",
     "In the 'I stopped using /grill-me — what I use instead' video specifically, "
     "what is the EXACT text difference between /grill-me and /grill-with-docs? "
     "What were the specific moments or sessions that pushed Matt to make the switch? "
     "Quote him directly where possible."),

    ("ralph-loops-mechanics",
     "In the 'Building a REAL feature with Claude Code' video specifically, "
     "what is the technical setup of Matt's 'Ralph loops' / AFK agents? "
     "Is there a Docker container called 'Sand Castle'? What's the iteration cap "
     "he sets? How long does a typical 'night shift' run in wall-clock time, "
     "and what's the day-shift / night-shift cadence he describes?"),

    ("rgr-fake-green-patterns",
     "In the 'Red Green Refactor is OP With Claude Code' video specifically, "
     "what are the concrete patterns LLMs use to 'fake green' tests "
     "(i.e., make tests pass without actually implementing the intended behavior)? "
     "How does the red-green-refactor discipline catch each one? "
     "Quote specific examples where given."),

    ("tdd-when-not-to",
     "In the 'How I Test With Claude Code (AI TDD)' video specifically, "
     "does Matt or the demonstrator (Owain Lewis) describe situations where "
     "TDD is overkill or counterproductive with AI agents? "
     "Any specific examples of when to skip the red step or use a lighter approach? "
     "Quote where possible."),

    ("live-stream-friction",
     "In the LIVE stream 'Watch me build a brand-new project from scratch' specifically — "
     "the only unscripted source in the corpus — what does Matt do that the polished "
     "videos don't show? Specifically: (1) where in the build does he reach for which skill "
     "in real time, and in what ORDER? (2) Are there moments where he gets stuck, backtracks, "
     "or improvises around a skill's text? (3) Does he break his own stated rules at any point, "
     "and if so, what reason does he give in the moment? (4) What does the live audience ask "
     "that he answers, and does any answer surprise the framing in his polished content? "
     "Quote him directly where possible."),

    ("teach-deepdive",
     "In the 'Learn anything with the /teach skill' video specifically, what is "
     "the /teach skill designed to do, and what is the workflow Matt describes? "
     "What artifacts does it produce (e.g., a mission, glossary, learning record, "
     "resources list)? How does /teach differ from simply asking Claude to explain "
     "a topic? Quote him directly where possible."),
    # --- 2026-08 verification round: upstream moved 694fa30 -> 6654f6b ---
    # Scoped to what the notebook can actually answer. The corpus is video
    # transcripts, so it is never asked what changed in a file — step 1 of
    # check_skills.py answers that from the GitHub compare, exactly and for
    # free. These ask for Matt's rationale and usage, which only he can give.
    #
    # Scope follows the TUTORIAL, not the upstream diff: 18 skills changed
    # upstream without being cited on the page, so they carry no claim to
    # verify and get no question. Every question ends with an explicit
    # 'not covered' escape hatch — without one, a skill name alone is enough
    # to invite a plausible invented answer.
    #
    # Keys are timestamped so a future round adds a new generation rather
    # than overwriting these (build_notebook.py skips cached keys).

    ("release-2026-08",
     "Upstream mattpocock/skills moved from 694fa30 to 6654f6b. Do any of these videos announce or explain that change? List the skills Matt says he added, renamed, merged or deleted, and the reason he gives for each. Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("retired-2026-08",
     "These skills were deleted upstream in this round: /design-an-interface, /qa, /request-refactor-plan, /ubiquitous-language, /diagnose, /to-issues, /to-prd, /zoom-out, /review, /edit-article, /obsidian-vault, /caveman, /write-a-skill. For each, do these videos say why it was retired and what took over its job? Answer per skill, only from what Matt actually says. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("grill-with-docs-2026-08",
     "The tutorial makes claims about /grill-with-docs, which changed upstream this round. Across these videos, how does Matt describe /grill-with-docs: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("improve-codebase-architecture-2026-08",
     "The tutorial makes claims about /improve-codebase-architecture, which changed upstream this round. Across these videos, how does Matt describe /improve-codebase-architecture: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("prototype-2026-08",
     "The tutorial makes claims about /prototype, which changed upstream this round. Across these videos, how does Matt describe /prototype: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("setup-matt-pocock-skills-2026-08",
     "The tutorial makes claims about /setup-matt-pocock-skills, which changed upstream this round. Across these videos, how does Matt describe /setup-matt-pocock-skills: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("tdd-2026-08",
     "The tutorial makes claims about /tdd, which changed upstream this round. Across these videos, how does Matt describe /tdd: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("triage-2026-08",
     "The tutorial makes claims about /triage, which changed upstream this round. Across these videos, how does Matt describe /triage: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("git-guardrails-claude-code-2026-08",
     "The tutorial makes claims about /git-guardrails-claude-code, which changed upstream this round. Across these videos, how does Matt describe /git-guardrails-claude-code: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("setup-pre-commit-2026-08",
     "The tutorial makes claims about /setup-pre-commit, which changed upstream this round. Across these videos, how does Matt describe /setup-pre-commit: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("grill-me-2026-08",
     "The tutorial makes claims about /grill-me, which changed upstream this round. Across these videos, how does Matt describe /grill-me: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("handoff-2026-08",
     "The tutorial makes claims about /handoff, which changed upstream this round. Across these videos, how does Matt describe /handoff: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("teach-2026-08",
     "The tutorial makes claims about /teach, which changed upstream this round. Across these videos, how does Matt describe /teach: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("diagnosing-bugs-2026-08",
     "The tutorial makes claims about /diagnosing-bugs, which changed upstream this round. Across these videos, how does Matt describe /diagnosing-bugs: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("domain-modeling-2026-08",
     "The tutorial makes claims about /domain-modeling, which changed upstream this round. Across these videos, how does Matt describe /domain-modeling: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("to-spec-2026-08",
     "The tutorial makes claims about /to-spec, which changed upstream this round. Across these videos, how does Matt describe /to-spec: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("to-tickets-2026-08",
     "The tutorial makes claims about /to-tickets, which changed upstream this round. Across these videos, how does Matt describe /to-tickets: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("implement-spec-2026-08",
     "The tutorial makes claims about /implement-spec, which changed upstream this round. Across these videos, how does Matt describe /implement-spec: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("writing-for-agents-2026-08",
     "The tutorial makes claims about /writing-for-agents, which changed upstream this round. Across these videos, how does Matt describe /writing-for-agents: when he reaches for it, what it produces, and any constraint or warning he attaches to it? Quote him directly. If these videos do not discuss it, answer exactly 'not covered' rather than inferring from the skill name."),

    ("live-uncle-bob-on-software-fundamentals--2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("new-skills-v1-2-brings-wait-what-writing-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("wayfinder-nothing-is-too-big-to-plan-any-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("don-t-waste-time-on-specs-prototype-inst-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("there-is-no-such-thing-as-greenfield-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("using-grill-me-for-interviews-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("what-is-the-dumb-zone-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("do-you-even-need-human-review-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("this-change-makes-grill-me-so-much-bette-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("framework-hell-tutorial-hell-now-skill-h-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("kill-your-memory-md-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("do-software-fundamentals-still-matter-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("my-teach-skill-is-still-insane-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("claude-code-s-system-tools-are-so-bloate-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),

    ("mattpocock-skills-a-complete-ai-coding-w-2026-08",
     "Summarize the central new claim Matt makes in this video that the previous corpus did not cover. Quote where possible."),
]


# ---- Driver ---------------------------------------------------------------

async def build():
    started = datetime.now().isoformat(timespec="seconds")
    print(f"[{started}] starting...")
    print(f"  notebook: {NOTEBOOK_TITLE}")
    print(f"  sources:  {len(VIDEOS)} videos")
    print(f"  queries:  {len(QUESTIONS)} questions")

    # idempotency: if a prior run wrote notebook_output.json, carry forward
    # its sources + answered questions so we only do new work this time.
    prior = None
    prior_path = Path("notebook_output.json")
    if prior_path.exists():
        try:
            prior = json.loads(prior_path.read_text(encoding="utf-8"))
            cached_qa = {q["key"]: q for q in prior.get("qa", []) if q.get("answer")}
            print(f"  found prior output: {len(prior.get('sources', []))} sources, "
                  f"{len(cached_qa)} cached answers (will skip)")
        except Exception as e:
            print(f"  could not load prior output: {e!r}")
            prior = None

    out = {
        "notebook_title": NOTEBOOK_TITLE,
        "started_at": started,
        "sources": (prior or {}).get("sources", []),
        "qa": [q for q in (prior or {}).get("qa", []) if q.get("answer")],
        "errors": [],
        "_cached_qa_keys": {q["key"] for q in (prior or {}).get("qa", []) if q.get("answer")},
        "_skip_ingest": bool(prior and prior.get("sources")),
    }

    try:
        # async-context-manager form (avoids the deprecation warning on .from_storage())
        async with await NotebookLMClient.from_storage() as client:
            # 1) Find or create the notebook (idempotent across re-runs)
            print("\n[step 1/4] resolving notebook...")
            nb = None
            try:
                existing = await client.notebooks.list()
                for n in existing:
                    if getattr(n, "title", None) == NOTEBOOK_TITLE:
                        nb = n
                        print(f"  reusing existing notebook: {nb.id}")
                        break
            except Exception as e:
                print(f"  (could not list existing notebooks: {e!r}; will create new)")

            if nb is None:
                nb = await client.notebooks.create(NOTEBOOK_TITLE)
                print(f"  created notebook: {nb.id}")
            out["notebook_id"] = nb.id

            await _run_pipeline(client, nb, out)

    except SystemExit:
        raise
    except Exception as e:
        sys.exit(
            "\nFailed to load or use NotebookLM session.\n"
            "If this looks like an auth error, re-run:\n"
            "    C:\\Python313\\Scripts\\notebooklm.exe login\n"
            f"Underlying error: {e!r}\n"
        )

async def _run_pipeline(client, nb, out):
    cached_keys = out.pop("_cached_qa_keys", set())
    out.pop("_skip_ingest", None)  # superseded by per-URL idempotency below

    # 2) Per-URL idempotent ingest — only fetch videos not already in prior sources.
    existing_urls = {s.get("url") for s in out["sources"] if s.get("url") and s.get("source_id")}
    pending = [(url, label) for url, label in VIDEOS if url not in existing_urls]

    if not pending:
        print(f"\n[step 2/4] no new sources — all {len(out['sources'])} videos already ingested")
    else:
        print(f"\n[step 2/4] ingesting {len(pending)} new source(s) (skipping {len(existing_urls)} already-ingested)...")
        for url, label in pending:
            print(f"  · {label}\n    {url}")
            try:
                src = await client.sources.add_url(nb.id, url, wait=True)
                src_repr = getattr(src, "id", None) or repr(src)
                print(f"    ✓ ingested ({src_repr})")
                out["sources"].append({"url": url, "label": label, "source_id": str(src_repr)})
            except Exception as e:
                msg = f"add_url failed for {url}: {e!r}"
                print(f"    ✗ {msg}")
                traceback.print_exc()
                out["errors"].append(msg)
                out["sources"].append({"url": url, "label": label, "source_id": None, "error": str(e)})

    # 3) Ask each question — skip ones already answered in a prior run
    new_qs = [(k, q) for k, q in QUESTIONS if k not in cached_keys]
    cached_count = len(QUESTIONS) - len(new_qs)
    print(f"\n[step 3/4] asking {len(new_qs)} new questions ({cached_count} cached, skipped)...")
    for key, q in new_qs:
        print(f"  > {key}")
        try:
            result = await client.chat.ask(nb.id, q)
            answer = getattr(result, "answer", None) or str(result)
            citations = []
            # citations vary by client version; best-effort extraction
            for attr in ("citations", "sources", "references"):
                val = getattr(result, attr, None)
                if val:
                    try:
                        citations = [str(c) for c in val]
                    except Exception:
                        citations = [repr(val)]
                    break
            print(f"    ✓ {len(answer)} chars, {len(citations)} citations")
            out["qa"].append({"key": key, "question": q, "answer": answer, "citations": citations})
        except Exception as e:
            msg = f"ask failed for {key}: {e!r}"
            print(f"    ✗ {msg}")
            traceback.print_exc()
            out["errors"].append(msg)
            out["qa"].append({"key": key, "question": q, "answer": None, "error": str(e)})

    # 4) Write outputs
    print("\n[step 4/4] writing outputs...")
    out["finished_at"] = datetime.now().isoformat(timespec="seconds")
    json_path = Path("notebook_output.json")
    json_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓ {json_path.resolve()}")

    md_lines = [
        f"# Matt Pocock skills — video corpus digest",
        f"",
        f"_Notebook: {NOTEBOOK_TITLE}_  ",
        f"_Generated: {out['finished_at']}_  ",
        f"_Sources: {sum(1 for s in out['sources'] if s.get('source_id'))} / {len(VIDEOS)} ingested_  ",
        f"",
        f"## Sources",
        *[f"- [{s['label']}]({s['url']})" + ("" if s.get("source_id") else f"  _(failed: {s.get('error','?')})_")
          for s in out["sources"]],
        f"",
        f"## Findings",
    ]
    for item in out["qa"]:
        md_lines.append(f"\n### {item['key']}\n")
        md_lines.append(f"> {item['question']}\n")
        md_lines.append(item.get("answer") or f"_(failed: {item.get('error','?')})_")
        if item.get("citations"):
            md_lines.append("")
            md_lines.append("**Citations:**")
            for c in item["citations"]:
                md_lines.append(f"- {c}")
    md_path = Path("notebook_output.md")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"  ✓ {md_path.resolve()}")

    if out["errors"]:
        print(f"\nfinished with {len(out['errors'])} error(s) — see notebook_output.json")
        sys.exit(1)
    print("\n✓ done.")


if __name__ == "__main__":
    asyncio.run(build())

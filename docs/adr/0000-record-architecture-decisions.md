# 0000 — Record architecture decisions

**Status:** accepted &nbsp;&middot;&nbsp; **Date:** 2026-05-28

## Context

We need a lightweight way to capture decisions that constrain the
codebase &mdash; design choices, semantic invariants, technology selections
&mdash; so future contributors (human or agent) can answer "*why* is this
shaped the way it is?" without having to reconstruct the conversation
that produced it.

## Decision

We use Architecture Decision Records (ADRs) as described by Michael
Nygard ([Documenting architecture decisions, 2011]). One ADR per
decision. Numbered, immutable once merged, in `docs/adr/`.

Each ADR has the following sections:

- **Status** &mdash; one of `proposed`, `accepted`, `superseded`. Never
  `rejected` &mdash; rejected proposals don&#39;t need an ADR; they need a
  comment in the relevant PR.
- **Date** &mdash; ISO-8601 (YYYY-MM-DD) of when the decision was made.
- **Context** &mdash; the problem and the forces in play. *Why* this
  decision was needed.
- **Decision** &mdash; the chosen path. Short, declarative.
- **Consequences** &mdash; what becomes easier and what becomes harder.
  Both sides. Be honest about the trade-offs.

ADRs that supersede previous ones include a `Supersedes: ADR NNNN`
line near the top; the superseded ADR's status is updated to
`superseded by ADR NNNN`.

## Consequences

- **+** Future readers can grep `docs/adr/` for "why X" answers without
  needing to read PR histories or chat logs.
- **+** Skills like `/improve-codebase-architecture` and `/diagnose`
  can cite specific ADRs when proposing changes, making the constraints
  visible in the conversation.
- **&minus;** ADRs cost time to write. We mitigate this by only writing
  them for *hard-to-reverse* decisions (per `docs/agents/domain.md`)
  &mdash; not for trivial choices.

[Documenting architecture decisions, 2011]: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions

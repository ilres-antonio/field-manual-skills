# 0001 — Phase transitions discard overrun

**Status:** accepted &nbsp;&middot;&nbsp; **Date:** 2026-05-28

## Context

The Pomodoro module&#39;s `tick()` method advances state based on
real-clock time elapsed between calls. When a tick advances past a phase
boundary (e.g. a 1500ms tick during a 1000ms work session), there are
two coherent ways to handle the 500ms overrun:

1. **Carry forward** &mdash; the break starts with 500ms already consumed
   (`breakMs - overrun` remaining).
2. **Discard** &mdash; the break starts at its full duration; the 500ms is
   thrown away.

Carrying forward is time-accurate. Discarding produces a cleaner UX:
each new phase visibly starts at its full configured duration, no
mid-second numerals on the ring.

The first failing test in slice 2 (`work&rarr;0 auto-flips to break with
full breakMs`) pinned the choice before the implementation existed.

## Decision

**Overrun is discarded.** When `tick()` would advance `remainingMs`
below zero, `transitionOnZero()` runs and sets `remainingMs` to the
*full* duration of the next phase (`breakMs`, `workMs`, or
`longBreakMs`). The overrun amount is dropped.

Implementation: `tick()` checks `if (state.remainingMs <= 0)` after
subtraction and calls `transitionOnZero()` without subtracting overrun
from the new `remainingMs`. See `app.js`.

## Consequences

- **+** Each new phase shows its configured duration on the ring at
  start. The visual cue is unambiguous: "a fresh phase has begun."
- **+** The behavior matches the user&#39;s mental model of a stopwatch
  (each session is its own thing).
- **&minus;** Cumulative elapsed time across many sessions can drift by
  up to one tick duration (250ms in production) per phase boundary.
  Not user-visible at normal cadences; would matter if we tried to
  report total work time and expected sub-second precision.
- **&minus;** A tick of more than two full phase durations (e.g. browser
  put to sleep for 10+ minutes mid-work) would be "noticed" only by a
  single transition rather than catching up to the right phase. Tests
  encode this; if the requirement ever changes, this ADR gets
  superseded.

## Pinned by

- `tests.html` &mdash; slice 2 / test 1 ("on work&rarr;0, auto-flips to
  break with breakMs")
- `tests.html` &mdash; slice 2 / test 2 ("on break&rarr;0, flips back to
  work")

# 0002 — createPomodoro owns no clock

**Status:** accepted &nbsp;&middot;&nbsp; **Date:** 2026-05-28

## Context

The Pomodoro module is a finite state machine that needs forward time to
advance. There are two ways to drive it:

1. **Module owns its clock** &mdash; `createPomodoro` instantiates an
   internal `setInterval` that calls a private tick handler. The
   timer "ticks itself."
2. **External caller drives time** &mdash; the module exposes a public
   `tick()` method; the UI or a test calls it on whatever cadence is
   appropriate.

Option 1 is the obvious shape ("a timer ticks"). It produces a wider
interface (start/pause/reset plus implicit clock-coupling) and makes
the module *shallow*: every test would need to stub `setInterval`,
every duration change would need to tear down and restart the
internal timer, and the boundary between "pure state logic" and
"I/O" would be invisible.

Option 2 makes the module deep: the interface is narrow
(`start/pause/reset/tick/getState/subscribe/destroy`), the state
transitions are referentially transparent given a tick, and every
side effect (storage, notifier, audio) is injected.

## Decision

`createPomodoro` owns no clock. It exposes `tick()`. The UI calls
`setInterval(() => pomodoro.tick(), 250)` in production. Tests call
`tick()` directly after advancing a fake clock.

## Consequences

- **+** Module is trivially testable with no fake-timer scaffolding.
  See `tests.html` &mdash; the 12 assertions use only `makeClock()`,
  `makeStorage()`, `makeNotifier()`, `makeAudio()` stubs; nothing
  patches global `setInterval`.
- **+** The boundary between "pure logic" and "real I/O" is explicit
  and narrow. Every injected dependency is a constructor parameter.
- **+** The polish layer (demo mode, duration inputs, SVG progress
  ring) was added entirely in the UI without touching a single line
  of the module &mdash; because all the integration points already
  existed.
- **&minus;** Callers must remember to wire a tick driver. The failure
  mode is loud (the timer doesn&#39;t move) and immediate, but the first
  time a new caller integrates the module they may forget the
  interval and wonder why nothing happens.

## Pinned by

- `tests.html` &mdash; every test exercises `tick()` directly; if the
  module ever grew an internal `setInterval`, the tests would still
  work but the implementation would be carrying redundant state.
- `app.js` `mountPomodoroUI()` &mdash; the one `setInterval` in the
  production code lives here, in the UI layer.

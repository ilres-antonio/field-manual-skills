/* ================================================================
   FIELD MANUAL vol.01 — interaction layer
   - terminal: render-on-load + click-to-play typewriter
   - copy: skill chips + cta commands → clipboard + toast
   - scroll-spy: highlight masthead nav for current phase
   ================================================================ */

(() => {
  "use strict";

  /* ----------------------------- shared utils ----------------------------- */
  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  /* ----------------------------- toast ----------------------------- */
  const toastEl = $("#toast");
  let toastTimer = null;
  function showToast(message = "copied") {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("is-visible"), 1400);
  }

  /* ----------------------------- copy-to-clipboard ----------------------------- */
  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try { await navigator.clipboard.writeText(text); return true; }
      catch { /* fall through */ }
    }
    // legacy fallback
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "absolute";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    let ok = false;
    try { ok = document.execCommand("copy"); } catch { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  function wireCopyTargets() {
    $$("[data-copy]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const text = btn.getAttribute("data-copy");
        const ok = await copyText(text);
        if (ok) {
          btn.classList.add("is-copied");
          showToast(`copied · ${text.length > 32 ? text.slice(0, 30) + "…" : text}`);
          setTimeout(() => btn.classList.remove("is-copied"), 1400);
        } else {
          showToast("copy blocked — select & ⌘C");
        }
      });
    });
  }

  /* ----------------------------- terminal sim ----------------------------- */
  // map script "who" → CSS class
  const WHO_CLASS = {
    user:   "is-user",
    claude: "is-claude",
    sys:    "is-sys",
  };

  // parse a transcript's data-script JSON safely
  function parseScript(scriptEl) {
    const raw = scriptEl.getAttribute("data-script");
    if (!raw) return [];
    try { return JSON.parse(raw); }
    catch (e) { console.warn("bad terminal script", e); return []; }
  }

  // build a single static .line node for a transcript turn.
  // Entities in data-script (e.g. &mdash;) are already decoded by the HTML
  // parser before getAttribute returns the string, so textContent renders them
  // correctly without needing innerHTML.
  function buildLine(turn) {
    const cls = WHO_CLASS[turn.who] || "is-claude";
    const line = document.createElement("span");
    line.className = `line ${cls}`;
    line.textContent = turn.t;
    return line;
  }

  // initial paint: show the full transcript so skimmers see it immediately
  function renderInitialTranscripts() {
    $$(".terminal").forEach((term) => {
      const codeEl   = $(".terminal__transcript", term);
      if (!codeEl) return;
      const script   = parseScript(codeEl);
      if (!script.length) return;
      // clear and rebuild with DOM nodes only (no innerHTML)
      codeEl.textContent = "";
      const frag = document.createDocumentFragment();
      script.forEach((turn) => frag.appendChild(buildLine(turn)));
      codeEl.appendChild(frag);
    });
  }

  // type out a turn with character-level pacing, into a fresh .line span.
  // returns when the line is fully typed.
  async function typeLine(container, turn, speed) {
    const line = buildLine(turn);
    line.textContent = ""; // start empty; we'll fill char by char
    container.appendChild(line);

    const fullText = turn.t;
    const caret = document.createElement("span");
    caret.className = "caret";

    // textContent is XSS-safe and fast
    for (let i = 1; i <= fullText.length; i++) {
      line.textContent = fullText.slice(0, i);
      line.appendChild(caret);
      const screen = container.closest(".terminal__screen");
      if (screen) screen.scrollTop = screen.scrollHeight;
      const ch = fullText[i - 1];
      let wait = speed;
      if (ch === " ") wait = speed * 0.4;
      else if (",;:".includes(ch)) wait = speed * 4;
      else if (".?!".includes(ch)) wait = speed * 6;
      await sleep(wait);
    }
    caret.remove();
    line.textContent = fullText; // final clean state
  }

  // play the entire script in a terminal
  async function playTerminal(term) {
    const codeEl   = $(".terminal__transcript", term);
    const playBtn  = $(".terminal__play", term);
    const screen   = $(".terminal__screen", term);
    if (!codeEl || !playBtn) return;

    const script = parseScript(codeEl);
    if (!script.length) return;

    // guard against double-play
    if (term.dataset.playing === "1") return;
    term.dataset.playing = "1";

    playBtn.classList.remove("is-done");
    playBtn.classList.add("is-playing");
    playBtn.textContent = "playing";

    // wipe transcript (textContent is safe; no innerHTML anywhere in this file)
    codeEl.textContent = "";
    if (screen) screen.scrollTop = 0;

    const charSpeed = prefersReducedMotion ? 0 : 14; // ms per char
    const lineGap   = prefersReducedMotion ? 0 : 220; // between lines

    for (let i = 0; i < script.length; i++) {
      const turn = script[i];
      await typeLine(codeEl, turn, charSpeed);
      // pause longer between speaker switches; shorter within same speaker
      const next = script[i + 1];
      let gap = lineGap;
      if (next && next.who !== turn.who) gap *= 1.6;
      if (turn.who === "sys")            gap *= 1.4;
      await sleep(gap);
    }

    playBtn.classList.remove("is-playing");
    playBtn.classList.add("is-done");
    playBtn.textContent = "replay";
    term.dataset.playing = "0";
  }

  function wireTerminals() {
    $$(".terminal").forEach((term) => {
      const playBtn = $(".terminal__play", term);
      if (!playBtn) return;
      playBtn.addEventListener("click", () => playTerminal(term));
    });
  }

  /* ----------------------------- scroll-spy nav ----------------------------- */
  function wireScrollSpy() {
    const phases = $$(".phase[data-phase]");
    const links  = $$("[data-phase-link]");
    if (!phases.length || !links.length) return;
    if (!("IntersectionObserver" in window)) return;

    const byPhase = new Map();
    links.forEach((a) => byPhase.set(a.dataset.phaseLink, a));

    const setActive = (phase) => {
      links.forEach((a) => a.classList.remove("is-active"));
      const a = byPhase.get(phase);
      if (a) a.classList.add("is-active");
    };

    const obs = new IntersectionObserver(
      (entries) => {
        // pick the entry closest to top of viewport that is visible
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible.length) {
          setActive(visible[0].target.dataset.phase);
        }
      },
      { rootMargin: "-30% 0px -55% 0px", threshold: 0 }
    );

    phases.forEach((p) => obs.observe(p));
  }

  /* ----------------------------- smooth in-page links ----------------------------- */
  // native smooth-scroll is enabled via CSS; this just makes the masthead
  // height-aware by offsetting after jump (browsers handle scroll-margin too,
  // but anchored sections may sit under the sticky bar without an offset).
  function wireNavOffset() {
    const masthead = $(".masthead");
    if (!masthead) return;
    const offset = masthead.offsetHeight + 8;
    $$('a[href^="#"]').forEach((a) => {
      a.addEventListener("click", (e) => {
        const id = a.getAttribute("href").slice(1);
        if (!id) return;
        const target = document.getElementById(id);
        if (!target) return;
        e.preventDefault();
        const y = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top: y, behavior: prefersReducedMotion ? "auto" : "smooth" });
        // update hash without jumping
        history.replaceState(null, "", `#${id}`);
      });
    });
  }

  /* ----------------------------- boot ----------------------------- */
  function init() {
    renderInitialTranscripts();
    wireTerminals();
    wireCopyTargets();
    wireScrollSpy();
    wireNavOffset();
    // Phase IV embedded demo (only mounts if the root exists on this page)
    const root = document.getElementById("pomodoro-root");
    if (root && typeof window.mountPomodoroUI === "function") {
      window.mountPomodoroUI(root);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();


/* ================================================================
   POMODORO MODULE — the substance behind Phase IV
   - createPomodoro: pure factory, no I/O ownership. The UI (or a test)
     drives time via tick(). Storage, notifier, audio, and clock are
     all injected, so tests in tests.html exercise it with stubs.
   - mountPomodoroUI: wires the module to real DOM + browser deps.
   ================================================================ */

(() => {
  "use strict";

  const STORE_KEY = "pomodoro:state";
  const DEFAULTS = {
    workMs:      25 * 60_000,
    breakMs:      5 * 60_000,
    longBreakMs: 15 * 60_000,
    longBreakEvery: 4, // every Nth completed work session → long break
  };

  function freshState(workMs) {
    return {
      phase: "work",
      remainingMs: workMs,
      completed: 0,
      isRunning: false,
    };
  }

  function safeRead(storage) {
    if (!storage || typeof storage.getItem !== "function") return null;
    try {
      const raw = storage.getItem(STORE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      // sanity: only accept objects with the known phase set
      if (!parsed || !["work", "break", "longBreak"].includes(parsed.phase)) return null;
      return parsed;
    } catch { return null; }
  }

  function safeWrite(storage, state) {
    if (!storage || typeof storage.setItem !== "function") return;
    try { storage.setItem(STORE_KEY, JSON.stringify(state)); } catch { /* quota etc. */ }
  }

  function fireNotifier(notifier, title, body) {
    if (!notifier || typeof notifier.fire !== "function") return;
    try { notifier.fire(title, body); } catch (e) { console.warn("notifier.fire threw", e); }
  }

  function playAudio(audio) {
    if (!audio || typeof audio.play !== "function") return;
    try { audio.play(); } catch (e) { console.warn("audio.play threw", e); }
  }

  /**
   * Pure pomodoro engine. The caller (UI or test) drives time forward via tick().
   * No internal setInterval, no implicit globals.
   */
  function createPomodoro(options = {}) {
    const cfg = {
      workMs:         options.workMs        ?? DEFAULTS.workMs,
      breakMs:        options.breakMs       ?? DEFAULTS.breakMs,
      longBreakMs:    options.longBreakMs   ?? DEFAULTS.longBreakMs,
      longBreakEvery: options.longBreakEvery ?? DEFAULTS.longBreakEvery,
    };
    const now      = typeof options.now === "function" ? options.now : () => Date.now();
    const storage  = options.storage  === undefined ? (typeof localStorage !== "undefined" ? localStorage : null) : options.storage;
    const notifier = options.notifier === undefined ? null : options.notifier;
    const audio    = options.audio    === undefined ? null : options.audio;

    // restore from storage if present; otherwise fresh
    const restored = safeRead(storage);
    let state = restored
      ? {
          phase:       restored.phase,
          remainingMs: Math.max(0, Number(restored.remainingMs) || 0),
          completed:   Math.max(0, Number(restored.completed)   || 0),
          isRunning:   !!restored.isRunning,
        }
      : freshState(cfg.workMs);

    let lastTickAt = now();
    const subs = new Set();

    function snapshot() {
      // defensive copy — callers can't mutate internal state
      return { phase: state.phase, remainingMs: state.remainingMs, completed: state.completed, isRunning: state.isRunning };
    }

    function notify() {
      subs.forEach((fn) => { try { fn(snapshot()); } catch (e) { console.warn("subscriber threw", e); } });
    }

    function persist() { safeWrite(storage, snapshot()); }

    // determine which break follows a completed work session
    function breakAfterWork() {
      const next = state.completed + 1; // we're about to increment
      const isLong = next % cfg.longBreakEvery === 0;
      return isLong
        ? { phase: "longBreak", remainingMs: cfg.longBreakMs }
        : { phase: "break",     remainingMs: cfg.breakMs };
    }

    function transitionOnZero() {
      // session end → fire side effects (gracefully if missing)
      const prevPhase = state.phase;
      const title = prevPhase === "work" ? "Time for a break" : "Back to work";
      const body  = prevPhase === "work"
        ? "Work session done — take a break."
        : "Break over — back to work.";
      fireNotifier(notifier, title, body);
      playAudio(audio);

      if (prevPhase === "work") {
        const next = breakAfterWork();
        state.completed   = state.completed + 1;
        state.phase       = next.phase;
        state.remainingMs = next.remainingMs;
      } else {
        state.phase       = "work";
        state.remainingMs = cfg.workMs;
      }
      // stays running so consecutive ticks would continue the next phase
    }

    function start() {
      if (state.isRunning) return;
      state.isRunning = true;
      lastTickAt = now();
      persist();
      notify();
    }

    function pause() {
      if (!state.isRunning) return;
      state.isRunning = false;
      persist();
      notify();
    }

    function reset() {
      // preserve `completed`; everything else returns to fresh work
      state.phase       = "work";
      state.remainingMs = cfg.workMs;
      state.isRunning   = false;
      lastTickAt = now();
      persist();
      notify();
    }

    function tick() {
      if (!state.isRunning) {
        // keep lastTickAt fresh so a future start() doesn't consume the gap
        lastTickAt = now();
        return;
      }
      const t = now();
      const elapsed = t - lastTickAt;
      lastTickAt = t;
      if (elapsed <= 0) { notify(); return; }
      state.remainingMs -= elapsed;
      if (state.remainingMs <= 0) {
        // overrun is discarded by design — the next phase starts at its full duration.
        // See docs/adr/0001-phase-transitions-discard-overrun.md (artifact in Phase V).
        transitionOnZero();
      }
      persist();
      notify();
    }

    function subscribe(fn) {
      if (typeof fn !== "function") return () => {};
      subs.add(fn);
      // emit current state synchronously so subscribers can render immediately
      try { fn(snapshot()); } catch (e) { console.warn("subscriber threw", e); }
      return () => subs.delete(fn);
    }

    function destroy() {
      subs.clear();
      persist();
    }

    return { start, pause, reset, tick, getState: snapshot, subscribe, destroy, _config: cfg };
  }

  /* ----------------------------- real browser deps ----------------------------- */

  function browserNotifier() {
    const supported = typeof window !== "undefined" && "Notification" in window;
    return {
      isSupported: supported,
      permission: () => (supported ? Notification.permission : "denied"),
      request: async () => {
        if (!supported) return "denied";
        try { return await Notification.requestPermission(); }
        catch { return "denied"; }
      },
      fire: (title, body) => {
        if (!supported) return;
        if (Notification.permission !== "granted") return;
        try { new Notification(title, { body }); } catch (e) { console.warn("Notification ctor threw", e); }
      },
    };
  }

  function beepAudio() {
    let ctx = null;
    function ensureCtx() {
      if (ctx) return ctx;
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
      return ctx;
    }
    return {
      play() {
        const c = ensureCtx();
        if (!c) return;
        // small two-note chirp; total ~280ms
        const t0 = c.currentTime;
        const gain = c.createGain();
        gain.gain.setValueAtTime(0.0001, t0);
        gain.gain.exponentialRampToValueAtTime(0.18, t0 + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.28);
        gain.connect(c.destination);
        const o1 = c.createOscillator();
        o1.frequency.value = 660;
        o1.type = "sine";
        o1.connect(gain);
        const o2 = c.createOscillator();
        o2.frequency.value = 880;
        o2.type = "sine";
        o2.connect(gain);
        o1.start(t0);             o1.stop(t0 + 0.14);
        o2.start(t0 + 0.12);      o2.stop(t0 + 0.28);
      },
    };
  }

  /* ----------------------------- UI mount ----------------------------- */

  const PHASE_LABEL = { work: "work", break: "break", longBreak: "long break" };

  function formatTime(ms) {
    const total = Math.max(0, Math.ceil(ms / 1000));
    const m = Math.floor(total / 60);
    const s = total % 60;
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }

  function build(tag, opts = {}) {
    const el = document.createElement(tag);
    if (opts.class) el.className = opts.class;
    if (opts.text)  el.textContent = opts.text;
    if (opts.attrs) for (const [k, v] of Object.entries(opts.attrs)) el.setAttribute(k, v);
    return el;
  }

  // Ring geometry — SVG <circle r=88>; circumference fixed once.
  const RING_R = 88;
  const RING_C = 2 * Math.PI * RING_R;

  // duration presets
  const DEMO_DURATIONS = { workMs: 5_000, breakMs: 3_000, longBreakMs: 8_000 };
  const STANDARD_DEFAULTS = {
    workMs:      DEFAULTS.workMs,
    breakMs:     DEFAULTS.breakMs,
    longBreakMs: DEFAULTS.longBreakMs,
  };

  function totalMsFor(phase, dur) {
    if (phase === "break")     return dur.breakMs;
    if (phase === "longBreak") return dur.longBreakMs;
    return dur.workMs;
  }
  function clampMin(s, fallback) {
    const n = parseInt(s, 10);
    if (!isFinite(n)) return fallback;
    return Math.max(1, Math.min(120, n));
  }
  function svgEl(tag, attrs = {}) {
    const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
    return el;
  }

  function mountPomodoroUI(root) {
    while (root.firstChild) root.removeChild(root.firstChild);

    const notifier = browserNotifier();
    const audio    = beepAudio();

    // UI state — the module is rebuilt when these change.
    let mode = "standard";                      // "standard" | "demo"
    let durations = { ...STANDARD_DEFAULTS };   // active durations passed to createPomodoro
    let pomodoro     = null;
    let intervalId   = null;
    let unsubscribe  = null;
    let lastPhase    = null;                    // for aria-live transitions

    /* ---------------- DOM (built once, kept across instance swaps) ---------------- */
    const card = build("div", { class: "pomodoro" });

    // head: phase pill + count
    const head = build("div", { class: "pomodoro__head" });
    const phaseBadge = build("span", { class: "pomodoro__phase", text: "work" });
    const completed  = build("span", { class: "pomodoro__count", text: "0 pomodoros" });
    head.append(phaseBadge, completed);

    // dial: SVG ring + centered time text
    const dial = build("div", { class: "pomodoro__dial" });
    const svg = svgEl("svg", {
      class: "pomodoro__ring",
      viewBox: "0 0 200 200",
      "aria-hidden": "true",
      preserveAspectRatio: "xMidYMid meet",
    });
    const ringTrack    = svgEl("circle", { class: "pomodoro__ring-track",    cx: 100, cy: 100, r: RING_R, fill: "none" });
    const ringProgress = svgEl("circle", { class: "pomodoro__ring-progress", cx: 100, cy: 100, r: RING_R, fill: "none",
                                            "stroke-linecap": "round",
                                            "stroke-dasharray": RING_C.toFixed(2),
                                            "stroke-dashoffset": "0",
                                            transform: "rotate(-90 100 100)" });
    svg.append(ringTrack, ringProgress);

    const dialText = build("div", { class: "pomodoro__dial-text" });
    const dialTime  = build("span", { class: "pomodoro__time",       text: "25:00" });
    const dialLabel = build("span", { class: "pomodoro__dial-label", text: "minutes : seconds" });
    dialText.append(dialTime, dialLabel);
    dial.append(svg, dialText);

    // controls: start / pause / reset
    const controls = build("div", { class: "pomodoro__controls" });
    const startBtn = build("button", { class: "pomodoro__btn pomodoro__btn--primary", text: "start", attrs: { type: "button" } });
    const pauseBtn = build("button", { class: "pomodoro__btn",                         text: "pause", attrs: { type: "button" } });
    const resetBtn = build("button", { class: "pomodoro__btn pomodoro__btn--ghost",    text: "reset", attrs: { type: "button" } });
    controls.append(startBtn, pauseBtn, resetBtn);

    // settings: duration inputs + mode toggle
    const settings = build("div", { class: "pomodoro__settings" });

    const durationsRow = build("div", { class: "pomodoro__durations" });
    function durationField(name, valueMin) {
      const label = build("label", { class: "pomodoro__field" });
      const span  = build("span",  { class: "pomodoro__field-name", text: name });
      const input = build("input", { class: "pomodoro__field-input", attrs: {
        type: "number", min: "1", max: "120", step: "1", value: String(valueMin), inputmode: "numeric"
      }});
      input.dataset.field = name;
      const unit  = build("span", { class: "pomodoro__field-unit", text: "min" });
      label.append(span, input, unit);
      return { label, input };
    }
    const workField  = durationField("work",  Math.round(STANDARD_DEFAULTS.workMs      / 60_000));
    const breakField = durationField("break", Math.round(STANDARD_DEFAULTS.breakMs     / 60_000));
    const longField  = durationField("long",  Math.round(STANDARD_DEFAULTS.longBreakMs / 60_000));
    durationsRow.append(workField.label, breakField.label, longField.label);

    const modeRow = build("div", { class: "pomodoro__mode", attrs: { role: "group", "aria-label": "duration preset" } });
    const modeStd  = build("button", { class: "pomodoro__mode-btn pomodoro__mode-btn--active", text: "standard", attrs: { type: "button" } });
    const modeDemo = build("button", { class: "pomodoro__mode-btn",                              text: "demo",     attrs: { type: "button" } });
    modeRow.append(modeStd, modeDemo);

    settings.append(durationsRow, modeRow);

    // keyboard hint
    const shortcuts = build("p", { class: "pomodoro__shortcuts" });
    shortcuts.append(
      kbd("space"), document.createTextNode(" pause · "),
      kbd("r"),     document.createTextNode(" reset · "),
      kbd("d"),     document.createTextNode(" demo · "),
      kbd("esc"),   document.createTextNode(" pause"),
    );

    // aria-live region for phase change announcements (visually hidden)
    const ariaLive = build("div", { class: "pomodoro__live", attrs: { role: "status", "aria-live": "polite" } });

    // note
    const note = build("p", { class: "pomodoro__note" });
    note.textContent = "the same module under test in tests.html — injected deps, no internal clock.";

    card.append(head, dial, controls, settings, shortcuts, ariaLive, note);
    root.appendChild(card);

    function kbd(label) {
      const k = document.createElement("kbd");
      k.textContent = label;
      return k;
    }

    /* ---------------- render fn (subscribed to the current instance) ---------------- */
    function render(state) {
      // numerals + label
      dialTime.textContent   = formatTime(state.remainingMs);
      phaseBadge.textContent = PHASE_LABEL[state.phase] || state.phase;
      phaseBadge.dataset.phase = state.phase;
      completed.textContent  = state.completed === 1 ? "1 pomodoro" : state.completed + " pomodoros";

      // ring progress (depletes as time passes)
      const total = totalMsFor(state.phase, durations);
      const ratio = total > 0 ? Math.max(0, Math.min(1, 1 - state.remainingMs / total)) : 0;
      ringProgress.setAttribute("stroke-dashoffset", (RING_C * ratio).toFixed(2));
      ringProgress.dataset.phase = state.phase;
      svg.dataset.phase = state.phase;

      // running flag drives styles + button state
      card.dataset.running = state.isRunning ? "1" : "0";
      startBtn.disabled    = state.isRunning;
      pauseBtn.disabled    = !state.isRunning;
      startBtn.textContent =
        (state.remainingMs < total && state.phase === "work" && !state.isRunning && state.remainingMs > 0)
          ? "resume" : "start";

      // aria-live announcement only on phase transitions (skip first paint)
      if (lastPhase !== null && lastPhase !== state.phase) {
        const totalMin = Math.max(1, Math.round(total / 60_000));
        const unit = mode === "demo" ? "seconds" : (totalMin === 1 ? "minute" : "minutes");
        const value = mode === "demo" ? Math.max(1, Math.round(total / 1000)) : totalMin;
        ariaLive.textContent = `${PHASE_LABEL[state.phase]} started — ${value} ${unit}`;
      }
      lastPhase = state.phase;
    }

    /* ---------------- instance lifecycle ---------------- */
    function remount() {
      if (unsubscribe)  unsubscribe();
      if (intervalId)   clearInterval(intervalId);
      if (pomodoro)     pomodoro.destroy();

      pomodoro    = createPomodoro({ ...durations, notifier, audio });
      lastPhase   = null;
      unsubscribe = pomodoro.subscribe(render);
      intervalId  = setInterval(() => pomodoro.tick(), 250);
    }

    /* ---------------- mode + duration changes ---------------- */
    function readInputs() {
      const w = clampMin(workField.input.value,  25);
      const b = clampMin(breakField.input.value,  5);
      const l = clampMin(longField.input.value,  15);
      workField.input.value  = String(w);
      breakField.input.value = String(b);
      longField.input.value  = String(l);
      return { workMs: w * 60_000, breakMs: b * 60_000, longBreakMs: l * 60_000 };
    }

    function setMode(next) {
      mode = next;
      modeStd.classList.toggle("pomodoro__mode-btn--active",  mode === "standard");
      modeDemo.classList.toggle("pomodoro__mode-btn--active", mode === "demo");
      [workField, breakField, longField].forEach((f) => { f.input.disabled = (mode === "demo"); });
      durations = mode === "demo" ? { ...DEMO_DURATIONS } : readInputs();
      ariaLive.textContent = mode === "demo"
        ? "demo mode active — 5 second work, 3 second break"
        : "standard durations restored";
      remount();
    }

    function onDurationCommit() {
      if (mode === "demo") return;
      const next = readInputs();
      const changed =
        next.workMs      !== durations.workMs ||
        next.breakMs     !== durations.breakMs ||
        next.longBreakMs !== durations.longBreakMs;
      if (changed) {
        durations = next;
        remount();
      }
    }

    /* ---------------- event wiring ---------------- */
    startBtn.addEventListener("click", async () => {
      if (notifier.isSupported && notifier.permission() === "default") {
        try { await notifier.request(); } catch { /* denied */ }
      }
      audio.play();   // unlock audio context on user gesture
      pomodoro.start();
    });
    pauseBtn.addEventListener("click", () => pomodoro.pause());
    resetBtn.addEventListener("click", () => { lastPhase = null; pomodoro.reset(); });

    [workField, breakField, longField].forEach((f) => {
      f.input.addEventListener("blur",    onDurationCommit);
      f.input.addEventListener("keydown", (e) => { if (e.key === "Enter") f.input.blur(); });
    });
    modeStd.addEventListener("click",  () => { if (mode !== "standard") setMode("standard"); });
    modeDemo.addEventListener("click", () => { if (mode !== "demo")     setMode("demo"); });

    // global keyboard shortcuts — ignore when focus is in an input
    function onKey(e) {
      const t = e.target;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      const k = e.key;
      if (k === " " || k === "Spacebar") {
        e.preventDefault();
        pomodoro.getState().isRunning ? pomodoro.pause() : pomodoro.start();
      } else if (k === "r" || k === "R") {
        e.preventDefault(); lastPhase = null; pomodoro.reset();
      } else if (k === "d" || k === "D") {
        e.preventDefault(); setMode(mode === "demo" ? "standard" : "demo");
      } else if (k === "Escape") {
        if (pomodoro.getState().isRunning) pomodoro.pause();
      }
    }
    window.addEventListener("keydown", onKey);

    // cleanup on navigation
    window.addEventListener("beforeunload", () => {
      window.removeEventListener("keydown", onKey);
      if (intervalId) clearInterval(intervalId);
      if (pomodoro)   pomodoro.destroy();
    });

    // first mount
    remount();
  }

  // expose for tests.html + the tutorial page's init()
  window.createPomodoro  = createPomodoro;
  window.mountPomodoroUI = mountPomodoroUI;
})();


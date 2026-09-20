/* ==========================================================================
   Greek Study — app.js (Agent A)
   Progress store (localStorage) + a few tiny helpers. No frameworks.
   Loaded by every page via the shell. Page scripts (alphabet.js, reading.js,
   library.js) may assume `Progress`, `$`, `$$`, `fmtDate`, `escapeHtml`,
   `ready` are already defined.
   ========================================================================== */
(function (global) {
  'use strict';

  var KEY = 'greek-study:v1';
  var PLAN_DAYS = 14;

  /* --- helpers ---------------------------------------------------------- */
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }
  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else { fn(); }
  }
  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  var DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  /* fmtDate(d) -> "Mon 14 Sep"; fmtDate(d, 'iso') -> "2026-09-14" */
  function fmtDate(d, style) {
    var dt = (d instanceof Date) ? d : (d ? new Date(d) : new Date());
    if (isNaN(dt.getTime())) { return ''; }
    if (style === 'iso') { return isoDay(dt); }
    return DAYS[dt.getDay()] + ' ' + dt.getDate() + ' ' + MONTHS[dt.getMonth()];
  }
  function isoDay(dt) {
    var m = dt.getMonth() + 1, d = dt.getDate();
    return dt.getFullYear() + '-' + (m < 10 ? '0' + m : m) + '-' + (d < 10 ? '0' + d : d);
  }
  function today() { return isoDay(new Date()); }
  function dayBefore(iso) {
    var p = String(iso).split('-');
    var dt = new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]));
    dt.setDate(dt.getDate() - 1);
    return isoDay(dt);
  }
  /* Monday-based start of the current week, as an ISO day string. */
  function weekStart() {
    var dt = new Date();
    var dow = (dt.getDay() + 6) % 7; /* 0 = Monday */
    dt.setDate(dt.getDate() - dow);
    return isoDay(dt);
  }

  /* --- store ------------------------------------------------------------ */
  function blank() {
    return {
      stage: 0, days: {}, ready: {},
      streak: { last: null, count: 0 },
      minutes: [], letters: {}, readings: {}
    };
  }

  function read() {
    var raw = null;
    try { raw = global.localStorage.getItem(KEY); } catch (e) { raw = null; }
    if (!raw) { return blank(); }
    var data;
    try { data = JSON.parse(raw); } catch (e) { return blank(); }
    if (!data || typeof data !== 'object') { return blank(); }
    var base = blank(), k;
    for (k in base) {
      if (Object.prototype.hasOwnProperty.call(base, k) && data[k] == null) {
        data[k] = base[k];
      }
    }
    if (!Array.isArray(data.minutes)) { data.minutes = []; }
    if (typeof data.stage !== 'number') { data.stage = 0; }
    return data;
  }

  function write(state) {
    try { global.localStorage.setItem(KEY, JSON.stringify(state)); }
    catch (e) { /* private mode / quota — the page must still work */ }
    try {
      document.dispatchEvent(new CustomEvent('progress:change', { detail: state }));
    } catch (e) { /* older browsers */ }
    return state;
  }

  var Progress = {
    KEY: KEY,
    PLAN_DAYS: PLAN_DAYS,

    get: function () { return read(); },
    save: function (state) { return write(state); },

    /* Mark plan day n done (on=false unchecks it). Also touches the streak. */
    markDay: function (n, on) {
      var s = read();
      var key = String(n);
      if (on === false) { delete s.days[key]; }
      else { s.days[key] = today(); }
      write(s);
      if (on !== false) { Progress.touch(); }
      return read();
    },

    dayDone: function (n) { return !!read().days[String(n)]; },

    /* Days 1..14 done, as a count. */
    daysDone: function () {
      var s = read(), c = 0, i;
      for (i = 1; i <= PLAN_DAYS; i++) { if (s.days[String(i)]) { c++; } }
      return c;
    },

    /* First plan day not yet done, or null when all 14 are done. */
    nextDay: function (total) {
      var s = read(), n = total || PLAN_DAYS, i;
      for (i = 1; i <= n; i++) { if (!s.days[String(i)]) { return i; } }
      return null;
    },

    /* Updates the streak at most once per calendar day. */
    touch: function () {
      var s = read(), t = today();
      if (s.streak.last === t) { return s; }
      s.streak.count = (s.streak.last === dayBefore(t)) ? (s.streak.count || 0) + 1 : 1;
      s.streak.last = t;
      return write(s);
    },

    logMinutes: function (min, what) {
      var s = read();
      s.minutes.push({ date: today(), min: Number(min) || 0, what: what || '' });
      write(s);
      return Progress.touch();
    },

    minutesThisWeek: function () {
      var s = read(), start = weekStart(), total = 0;
      s.minutes.forEach(function (e) {
        if (e && e.date >= start) { total += Number(e.min) || 0; }
      });
      return total;
    },

    sessionsThisWeek: function () {
      var s = read(), start = weekStart(), n = 0;
      s.minutes.forEach(function (e) { if (e && e.date >= start) { n++; } });
      return n;
    },

    letterResult: function (ch, ok) {
      var s = read();
      var rec = s.letters[ch] || { seen: 0, correct: 0 };
      rec.seen += 1;
      if (ok) { rec.correct += 1; }
      s.letters[ch] = rec;
      write(s);
      return Progress.touch();
    },

    /* "Known" = at least 3 correct AND at least 75% correct. */
    letterKnown: function (ch) {
      var rec = read().letters[ch];
      if (!rec || !rec.seen) { return false; }
      return rec.correct >= 3 && (rec.correct / rec.seen) >= 0.75;
    },

    lettersKnown: function () {
      var s = read(), n = 0, ch;
      for (ch in s.letters) {
        if (Object.prototype.hasOwnProperty.call(s.letters, ch) && Progress.letterKnown(ch)) {
          n++;
        }
      }
      return n;
    },

    /* Letters practised but not yet known, weakest first. */
    weakLetters: function (limit) {
      var s = read(), out = [], ch, r;
      for (ch in s.letters) {
        if (!Object.prototype.hasOwnProperty.call(s.letters, ch)) { continue; }
        r = s.letters[ch];
        if (!r || !r.seen || Progress.letterKnown(ch)) { continue; }
        out.push({ ch: ch, rate: r.correct / r.seen });
      }
      out.sort(function (a, b) { return a.rate - b.rate; });
      return out.slice(0, limit || 5).map(function (o) { return o.ch; });
    },

    /* Stage "ready when" checklist: ready[stage] = [bool, ...] */
    setReady: function (stage, index, on) {
      var s = read(), key = String(stage);
      var list = s.ready[key] || {};
      if (on) { list[String(index)] = true; } else { delete list[String(index)]; }
      s.ready[key] = list;
      return write(s);
    },
    isReady: function (stage, index) {
      var list = read().ready[String(stage)] || {};
      return !!list[String(index)];
    },

    setStage: function (n) {
      var s = read();
      s.stage = Number(n) || 0;
      return write(s);
    },

    markReading: function (slug, patch) {
      var s = read();
      var rec = s.readings[slug] || { opened: null, tasksDone: [] };
      if (patch) {
        if (patch.opened !== undefined) { rec.opened = patch.opened; }
        if (patch.tasksDone !== undefined) { rec.tasksDone = patch.tasksDone; }
      }
      if (!rec.opened) { rec.opened = today(); }
      s.readings[slug] = rec;
      return write(s);
    },

    /* Is anything recorded at all? Used for honest empty states. */
    isEmpty: function () {
      var s = read();
      return !Object.keys(s.days).length && !s.minutes.length &&
             !Object.keys(s.letters).length && !s.streak.last;
    },

    /* Download the store as JSON. */
    export: function () {
      var blob = new Blob([JSON.stringify(read(), null, 2)], { type: 'application/json' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'greek-study-progress-' + today() + '.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    },

    import: function (json) {
      var data = (typeof json === 'string') ? JSON.parse(json) : json;
      if (!data || typeof data !== 'object') { throw new Error('Not a progress file'); }
      var base = blank(), k;
      for (k in base) {
        if (Object.prototype.hasOwnProperty.call(base, k) && data[k] == null) {
          data[k] = base[k];
        }
      }
      return write(data);
    },

    reset: function () {
      try { global.localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
      return write(blank());
    },

    today: today,
    isoDay: isoDay,
    weekStart: weekStart
  };

  global.Progress = Progress;
  global.$ = $;
  global.$$ = $$;
  global.ready = ready;
  global.fmtDate = fmtDate;
  global.escapeHtml = escapeHtml;

  /* Stamp today's date wherever a page asks for it. */
  ready(function () {
    $$('[data-today]').forEach(function (el) { el.textContent = fmtDate(new Date()); });
  });
}(window));

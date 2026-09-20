/* ==========================================================================
   alphabet.js — Alphabet trainer (Agent B)
   Learn mode: 6x4 grid (4 columns on mobile) + focus panel, weak letters
   highlighted from Progress. Quiz mode: 10-question rounds, glyph->name and
   name->glyph alternating, 4 options, look-alike distractors, weak letters
   weighted x3, keys 1-4, round summary. Answers feed Progress.letterResult.
   Depends on app.js (Progress, $, $$, ready, escapeHtml).
   ========================================================================== */
(function () {
  'use strict';

  var PRON_KEY = 'greek-study:pron';       // 'erasmian' | 'koine'
  var ROUND = 10;
  var WEAK_WEIGHT = 3;

  /* Visual / aural look-alike families — the distractors a beginner actually
     confuses. Used to pick wrong options that are worth ruling out. */
  var LOOKALIKE = [
    ['ν', 'υ', 'ω'],                       // nu upsilon omega
    ['η', 'μ', 'ν'],                       // eta mu nu
    ['ρ', 'π', 'ψ'],                       // rho pi psi
    ['ξ', 'χ', 'ψ', 'φ', 'ζ'],   // xi chi psi phi zeta
    ['ε', 'θ', 'ο', 'σ'],             // epsilon theta omicron sigma
    ['γ', 'τ', 'π'],                       // gamma tau pi
    ['ι', 'ιοτα'],               // (iota: nothing much looks like it)
    ['α', 'δ', 'λ'],                       // alpha delta lambda
    ['κ', 'χ'],                                 // kappa chi
    ['ο', 'ω']                                  // omicron omega
  ];

  var state = {
    letters: [],
    diacritics: [],
    pron: 'erasmian',
    mode: 'learn',
    focus: null,
    quiz: null
  };

  function readPron() {
    try {
      var v = localStorage.getItem(PRON_KEY);
      return v === 'koine' ? 'koine' : 'erasmian';
    } catch (e) { return 'erasmian'; }
  }
  function writePron(v) {
    try { localStorage.setItem(PRON_KEY, v); } catch (e) { /* private mode */ }
  }

  function say(letter) { return state.pron === 'koine' ? letter.koine : letter.erasmian; }
  function pronLabel() { return state.pron === 'koine' ? 'Restored Koine' : 'Erasmian'; }
  function glyphs(letter) {
    return letter.upper + ' ' + letter.lower + (letter.final ? '/' + letter.final : '');
  }

  /* --- progress-derived state ------------------------------------------- */
  function letterStats() {
    var s = {};
    try { s = (Progress.get().letters) || {}; } catch (e) { s = {}; }
    return s;
  }
  /* weak = seen at least 3 times and under 75% correct */
  function weakSet() {
    var stats = letterStats(), out = {}, ch, r;
    for (ch in stats) {
      if (!Object.prototype.hasOwnProperty.call(stats, ch)) { continue; }
      r = stats[ch];
      if (r && r.seen >= 3 && (r.correct / r.seen) < 0.75) { out[ch] = true; }
    }
    return out;
  }
  function knownCount() {
    var n = 0;
    state.letters.forEach(function (l) {
      try { if (Progress.letterKnown(l.lower)) { n += 1; } } catch (e) { /* noop */ }
    });
    return n;
  }

  /* --- learn mode -------------------------------------------------------- */
  function renderGrid() {
    var grid = $('#letter-grid');
    var weak = weakSet();
    grid.innerHTML = state.letters.map(function (l, i) {
      var cls = 'letter-card';
      if (weak[l.lower]) { cls += ' highlight'; }
      if (state.focus === i) { cls += ' selected'; }
      return '<button type="button" class="' + cls + '" data-i="' + i + '"' +
        ' aria-pressed="' + (state.focus === i ? 'true' : 'false') + '">' +
        '<span class="lc-glyph" lang="grc">' + escapeHtml(glyphs(l)) + '</span>' +
        '<span class="lc-name">' + escapeHtml(l.name) + '</span>' +
        '<span class="lc-say">' + escapeHtml(say(l)) + '</span>' +
        '</button>';
    }).join('');
    $('#grid-label').textContent = 'All 24 · ' + pronLabel() + ' values';
    var weakN = Object.keys(weak).length;
    var seenN = Object.keys(letterStats()).length;
    $('#grid-legend-text').textContent = weakN
      ? weakN + ' weak — drill these'
      : (seenN ? 'none weak yet — three sightings each to qualify'
               : 'weak letters appear here once you quiz');
    $('#known-count').textContent = seenN
      ? knownCount() + ' of 24 by sight'
      : 'not quizzed yet';
  }

  function renderFocus() {
    var panel = $('#focus-body');
    if (state.focus === null) {
      panel.innerHTML = '<p class="parse-empty">Pick a letter to see both pronunciations ' +
        'and the trap that goes with it.</p>';
      $('#focus-count').textContent = '24 letters';
      return;
    }
    var l = state.letters[state.focus];
    var weak = weakSet();
    var conf = l.confusion
      ? '<div class="callout"><div class="label label-accent">Common confusion</div>' +
        '<div class="small">' + escapeHtml(l.confusion) + '</div></div>'
      : '<div class="parse-empty">No standard trap for this one — it looks like ' +
        'nothing in the Latin alphabet.</div>';
    panel.innerHTML =
      '<div class="focus-glyphs"><div class="fg-big" lang="grc">' + escapeHtml(glyphs(l)) + '</div>' +
      '<div class="stack" style="gap:4px"><div class="fg-name">' + escapeHtml(l.name) + '</div>' +
      '<div class="meta">letter ' + l.i + ' of 24' +
      (weak[l.lower] ? ' · weak' : '') + '</div></div></div>' +
      '<div class="parse-rows">' +
      sayRow('Erasmian', l.erasmian, state.pron === 'erasmian') +
      sayRow('Restored Koine', l.koine, state.pron === 'koine') +
      (l.final ? sayRow('Final form', l.lower + ' → ' + l.final, false) : '') +
      '</div>' + conf;
    $('#focus-count').textContent = l.i + ' of 24';
  }
  function sayRow(key, val, on) {
    return '<div class="say-row' + (on ? ' is-on' : '') + '"><span class="say-key">' +
      escapeHtml(key) + '</span><span class="say-val">' + escapeHtml(val) + '</span></div>';
  }

  /* --- quiz -------------------------------------------------------------- */
  function lookalikesFor(ch) {
    var out = [];
    LOOKALIKE.forEach(function (group) {
      if (group.indexOf(ch) === -1) { return; }
      group.forEach(function (c) { if (c !== ch && out.indexOf(c) === -1) { out.push(c); } });
    });
    return out;
  }

  function shuffle(a) {
    var i, j, t;
    for (i = a.length - 1; i > 0; i--) {
      j = Math.floor(Math.random() * (i + 1));
      t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  /* Pick ROUND letters: weak ones counted three times in the draw. */
  function pickLetters() {
    var weak = weakSet(), pool = [], picked = [], i;
    state.letters.forEach(function (l, idx) {
      var times = weak[l.lower] ? WEAK_WEIGHT : 1;
      for (i = 0; i < times; i++) { pool.push(idx); }
    });
    shuffle(pool);
    for (i = 0; i < pool.length && picked.length < ROUND; i++) {
      if (picked.indexOf(pool[i]) === -1) { picked.push(pool[i]); }
    }
    /* if fewer than ROUND distinct letters came out, allow repeats */
    while (picked.length < ROUND && pool.length) {
      picked.push(pool[Math.floor(Math.random() * pool.length)]);
    }
    return picked;
  }

  function buildQuestion(idx, n) {
    var l = state.letters[idx];
    var kind = (n % 2 === 0) ? 'glyph' : 'name';   // alternate the prompt type
    var likes = lookalikesFor(l.lower);
    var options = [idx];
    var candidates = [];
    likes.forEach(function (ch) {
      state.letters.forEach(function (o, oi) {
        if (o.lower === ch && options.indexOf(oi) === -1 && candidates.indexOf(oi) === -1) {
          candidates.push(oi);
        }
      });
    });
    shuffle(candidates);
    var rest = [];
    state.letters.forEach(function (o, oi) {
      if (oi !== idx && candidates.indexOf(oi) === -1) { rest.push(oi); }
    });
    shuffle(rest);
    candidates.concat(rest).forEach(function (oi) {
      if (options.length < 4 && options.indexOf(oi) === -1) { options.push(oi); }
    });
    return { letter: idx, kind: kind, options: shuffle(options), answered: false };
  }

  function startRound() {
    var picks = pickLetters();
    state.quiz = {
      picks: picks,
      n: 0,
      score: 0,
      missed: [],
      started: Date.now(),
      touched: false,
      q: null,
      done: false
    };
    nextQuestion();
  }

  function nextQuestion() {
    var q = state.quiz;
    if (q.n >= q.picks.length) { finishRound(); return; }
    q.q = buildQuestion(q.picks[q.n], q.n);
    renderQuiz();
  }

  function renderQuiz() {
    var q = state.quiz;
    if (!q) { return; }
    if (q.done) { renderSummary(); return; }
    var cur = q.q;
    var l = state.letters[cur.letter];
    var ask = cur.kind === 'glyph' ? 'Which letter is this?' : 'Which glyph is this?';
    var prompt = cur.kind === 'glyph'
      ? '<div class="quiz-glyph" lang="grc">' + escapeHtml(l.lower) + '</div>'
      : '<div class="quiz-word">' + escapeHtml(l.name) + '</div>';
    var opts = cur.options.map(function (oi, k) {
      var o = state.letters[oi];
      var inner = cur.kind === 'glyph'
        ? escapeHtml(o.name)
        : '<span class="opt-glyph" lang="grc">' + escapeHtml(o.lower) + '</span>';
      return '<button type="button" class="quiz-opt" data-o="' + oi + '">' +
        '<span class="opt-key">' + (k + 1) + '</span>' + inner + '</button>';
    }).join('');
    $('#quiz-count').textContent = (q.n + 1) + ' of ' + ROUND;
    $('#quiz-body').innerHTML =
      '<div class="quiz-prompt"><div class="quiz-ask">' + ask + '</div>' + prompt + '</div>' +
      '<div class="quiz-options" id="quiz-options">' + opts + '</div>' +
      '<div class="quiz-feedback" id="quiz-feedback" role="status" aria-live="polite">' +
      'Press 1–4 or tap an answer.</div>' + pips(q.n);
  }

  function pips(done) {
    var out = '', i;
    for (i = 0; i < ROUND; i++) {
      out += '<div class="pip' + (i < done ? ' on' : '') + '"></div>';
    }
    return '<div class="pips">' + out + '</div>';
  }

  function answer(oi) {
    var q = state.quiz;
    if (!q || q.done || !q.q || q.q.answered) { return; }
    q.q.answered = true;
    var l = state.letters[q.q.letter];
    var ok = (oi === q.q.letter);
    if (!q.touched) { q.touched = true; try { Progress.touch(); } catch (e) { /* noop */ } }
    try { Progress.letterResult(l.lower, ok); } catch (e) { /* noop */ }
    if (ok) { q.score += 1; } else if (q.missed.indexOf(q.q.letter) === -1) { q.missed.push(q.q.letter); }

    $$('#quiz-options .quiz-opt').forEach(function (btn) {
      var i = Number(btn.getAttribute('data-o'));
      btn.disabled = true;
      if (i === q.q.letter) { btn.classList.add('right'); }
      else if (i === oi) { btn.classList.add('wrong'); }
    });
    var fb = $('#quiz-feedback');
    fb.innerHTML = ok
      ? 'Yes — <span lang="grc">' + escapeHtml(l.lower) + '</span> is ' +
        escapeHtml(l.name) + ', ' + escapeHtml(say(l)) + '.'
      : 'No — <span lang="grc">' + escapeHtml(l.lower) + '</span> is ' +
        escapeHtml(l.name) + ', ' + escapeHtml(say(l)) +
        (l.confusion ? '. ' + escapeHtml(l.confusion) : '.');
    q.n += 1;
    setTimeout(function () {
      if (state.mode === 'quiz' && state.quiz === q) { nextQuestion(); }
    }, ok ? 700 : 1500);
  }

  function finishRound() {
    var q = state.quiz;
    q.done = true;
    var mins = Math.max(1, Math.round((Date.now() - q.started) / 60000));
    try { Progress.logMinutes(mins, 'alphabet quiz'); } catch (e) { /* noop */ }
    renderSummary();
    renderGrid();
  }

  function renderSummary() {
    var q = state.quiz;
    var missed = q.missed.map(function (i) {
      var l = state.letters[i];
      return '<span class="missed"><span class="g" lang="grc">' + escapeHtml(l.lower) +
        '</span>' + escapeHtml(l.name) + '</span>';
    }).join('');
    $('#quiz-count').textContent = 'round over';
    $('#quiz-body').innerHTML =
      '<div class="quiz-summary"><div class="quiz-score">' + q.score + '<span class="metric-unit"> / ' +
      ROUND + '</span></div>' +
      '<div class="meta">' + (q.missed.length
        ? 'Letters to drill next: they are now shaded in the grid.'
        : 'Nothing missed. Run another round to keep the letters warm.') + '</div>' +
      (missed ? '<div class="missed-list">' + missed + '</div>' : '') +
      '<button type="button" class="btn btn-primary" id="quiz-again">Again</button></div>';
  }

  /* --- mode / pronunciation switching ------------------------------------ */
  function setMode(mode) {
    state.mode = mode;
    $$('#mode-switch button').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-mode') === mode ? 'true' : 'false');
    });
    $('#focus-panel').classList.toggle('is-hidden', mode !== 'learn');
    $('#quiz-panel').classList.toggle('is-hidden', mode !== 'quiz');
    if (mode === 'quiz') {
      if (!state.quiz || state.quiz.done) { startRound(); } else { renderQuiz(); }
    }
    renderGrid();
  }

  function setPron(p) {
    state.pron = p;
    writePron(p);
    $$('#pron-switch button').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-pron') === p ? 'true' : 'false');
    });
    renderGrid();
    renderFocus();
  }

  /* --- boot -------------------------------------------------------------- */
  var booted = false;
  ready(function () {
    if (booted) { return; }
    var node = document.getElementById('alphabet-data');
    if (!node) { return; }
    booted = true;
    var data;
    try { data = JSON.parse(node.textContent); } catch (e) { return; }
    state.letters = data.letters || [];
    state.diacritics = data.diacritics || [];
    state.pron = readPron();

    $$('#pron-switch button').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-pron') === state.pron ? 'true' : 'false');
      b.addEventListener('click', function () { setPron(b.getAttribute('data-pron')); });
    });
    $$('#mode-switch button').forEach(function (b) {
      b.addEventListener('click', function () { setMode(b.getAttribute('data-mode')); });
    });

    $('#letter-grid').addEventListener('click', function (ev) {
      var card = ev.target.closest ? ev.target.closest('.letter-card') : null;
      if (!card) { return; }
      state.focus = Number(card.getAttribute('data-i'));
      if (state.mode !== 'learn') { setMode('learn'); }
      renderGrid();
      renderFocus();
    });

    $('#quiz-panel').addEventListener('click', function (ev) {
      var t = ev.target.closest ? ev.target.closest('.quiz-opt, #quiz-again') : null;
      if (!t) { return; }
      if (t.id === 'quiz-again') { startRound(); return; }
      answer(Number(t.getAttribute('data-o')));
    });

    document.addEventListener('keydown', function (ev) {
      if (state.mode !== 'quiz' || !state.quiz) { return; }
      if (ev.target && /^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName)) { return; }
      if (state.quiz.done) {
        if (ev.key === 'Enter') { startRound(); }
        return;
      }
      var n = Number(ev.key);
      if (n >= 1 && n <= 4) {
        var btns = $$('#quiz-options .quiz-opt');
        if (btns[n - 1] && !btns[n - 1].disabled) {
          ev.preventDefault();
          answer(Number(btns[n - 1].getAttribute('data-o')));
        }
      }
    });

    document.addEventListener('progress:change', function () {
      if (state.mode === 'learn') { renderGrid(); }
    });

    setMode('learn');
    renderFocus();
  });
}());

/* ==========================================================================
   reading.js — Reading Room (Agent B)
   Clause-by-clause 1 John 1:1-4 (SBLGNT). Click or tap a word for its parse
   card: a sticky side panel on desktop, a bottom sheet below 900px. Arrow
   keys move word focus. Tasks record into Progress; opening the page stamps
   readings["1jn-1-1-4"].opened.
   Depends on app.js (Progress, $, $$, ready, fmtDate, escapeHtml).
   ========================================================================== */
(function () {
  'use strict';

  var state = { data: null, words: [], cur: -1 };

  function isMobile() {
    return window.matchMedia && window.matchMedia('(max-width: 899px)').matches;
  }

  /* --- parse card -------------------------------------------------------- */
  function row(key, val, cls) {
    return '<div class="parse-row"><span class="pr-key">' + escapeHtml(key) +
      '</span><span class="pr-val ' + (cls || '') + '">' + val + '</span></div>';
  }

  function showWord(i) {
    var w = state.words[i];
    if (!w) { return; }
    state.cur = i;
    $$('button.w').forEach(function (b, k) {
      b.classList.toggle('active', k === i);
      b.setAttribute('aria-pressed', k === i ? 'true' : 'false');
    });
    var card = $('#parse-card');
    card.classList.remove('is-hidden');
    $('#parse-surface').innerHTML = '<span lang="grc">' + escapeHtml(w.surface) + '</span>';
    $('#parse-verse').textContent = 'v. ' + w.verse;
    $('#parse-body').innerHTML =
      '<div class="parse-rows">' +
      row('Lemma', '<span lang="grc">' + escapeHtml(w.lemma) + '</span>', 'grc') +
      row('Parse', escapeHtml(w.parse)) +
      row('Gloss', escapeHtml(w.gloss), 'gl') +
      '</div>' +
      (w.note
        ? '<div class="callout"><div class="label label-accent">From the note</div>' +
          '<div class="small">' + escapeHtml(w.note) + '</div></div>'
        : '') +
      '<div class="meta">MorphGNT code <span lang="grc">' + escapeHtml(w.code) + '</span></div>' +
      '<div class="stack" style="gap:8px;padding-top:12px;border-top:1px solid var(--rule)">' +
      '<a class="task-link" href="https://www.stepbible.org/?q=version=SBLGNT|reference=1John.1"' +
      ' target="_blank" rel="noopener">Open 1 John 1 in STEP Bible</a>' +
      '<a class="task-link" href="https://logeion.uchicago.edu/' +
      encodeURIComponent(w.lemma) + '" target="_blank" rel="noopener">Look up ' +
      '<span lang="grc">' + escapeHtml(w.lemma) + '</span> in Logeion</a></div>';
    if (isMobile()) {
      card.setAttribute('aria-hidden', 'false');
      card.scrollTop = 0;
    }
  }

  function closeCard() {
    var card = $('#parse-card');
    $$('button.w').forEach(function (b) {
      b.classList.remove('active');
      b.setAttribute('aria-pressed', 'false');
    });
    if (isMobile()) {
      card.classList.add('is-hidden');
      card.setAttribute('aria-hidden', 'true');
    } else {
      $('#parse-surface').textContent = '';
      $('#parse-verse').textContent = '';
      $('#parse-body').innerHTML = emptyCard();
    }
    state.cur = -1;
  }

  function emptyCard() {
    return '<p class="parse-empty">Click any word for its lemma, its parse and a ' +
      'wooden gloss. Words the bridge note comments on carry an underline.</p>';
  }

  function move(delta) {
    var next = state.cur < 0 ? (delta > 0 ? 0 : state.words.length - 1) : state.cur + delta;
    if (next < 0) { next = state.words.length - 1; }
    if (next >= state.words.length) { next = 0; }
    var btn = $$('button.w')[next];
    if (btn) { btn.focus(); showWord(next); }
  }

  /* --- tasks ------------------------------------------------------------- */
  function taskState() {
    try {
      var rec = (Progress.get().readings || {})[state.data.slug];
      return (rec && rec.tasksDone) || [];
    } catch (e) { return []; }
  }

  function renderTasks() {
    var done = taskState();
    $$('.task').forEach(function (btn) {
      var id = Number(btn.getAttribute('data-task'));
      var on = done.indexOf(id) !== -1;
      btn.classList.toggle('done', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      var mark = $('.t-mark', btn);
      if (mark) {
        mark.innerHTML = on
          ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"' +
            ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tick"' +
            ' aria-hidden="true"><path d="m4 12 5.5 5.5L20 6.5"/></svg>'
          : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"' +
            ' stroke-width="1.6" class="box" aria-hidden="true"><rect x="4" y="4" width="16"' +
            ' height="16"/></svg>';
      }
    });
    var n = done.length;
    var el = $('#task-count');
    if (el) { el.textContent = n ? n + ' of 3 done' : 'none done yet'; }
  }

  function toggleTask(id) {
    var done = taskState().slice();
    var at = done.indexOf(id);
    if (at === -1) { done.push(id); } else { done.splice(at, 1); }
    done.sort(function (a, b) { return a - b; });
    try { Progress.markReading(state.data.slug, { tasksDone: done }); } catch (e) { /* noop */ }
    renderTasks();
  }

  /* --- boot -------------------------------------------------------------- */
  var booted = false;
  ready(function () {
    if (booted) { return; }
    var node = document.getElementById('reading-data');
    if (!node) { return; }
    try { state.data = JSON.parse(node.textContent); } catch (e) { return; }
    booted = true;

    /* flat word list in reading order, for the parse card and arrow keys */
    (state.data.clauses || []).forEach(function (cl) {
      (cl.words || []).forEach(function (w) {
        state.words.push({
          surface: w.surface, lemma: w.lemma, parse: w.parse, code: w.code,
          gloss: w.gloss, note: w.note, verse: cl.verse
        });
      });
    });

    try {
      Progress.markReading(state.data.slug, { opened: fmtDate(new Date(), 'iso') });
    } catch (e) { /* noop */ }

    $('#parse-body').innerHTML = emptyCard();
    if (isMobile()) { $('#parse-card').classList.add('is-hidden'); }

    $('#clauses').addEventListener('click', function (ev) {
      var btn = ev.target.closest ? ev.target.closest('button.w') : null;
      if (!btn) { return; }
      showWord(Number(btn.getAttribute('data-w')));
    });

    $('#sheet-close').addEventListener('click', closeCard);

    $('#tasks').addEventListener('click', function (ev) {
      var btn = ev.target.closest ? ev.target.closest('.task') : null;
      if (!btn) { return; }
      if (ev.target.closest('a')) { return; }
      toggleTask(Number(btn.getAttribute('data-task')));
    });

    document.addEventListener('keydown', function (ev) {
      if (ev.target && /^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName)) { return; }
      if (ev.key === 'ArrowRight') { ev.preventDefault(); move(1); }
      else if (ev.key === 'ArrowLeft') { ev.preventDefault(); move(-1); }
      else if (ev.key === 'Escape' && state.cur >= 0) { closeCard(); }
    });

    renderTasks();
  });
}());

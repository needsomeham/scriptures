/* Library search + filter (Agent C). Reads the JSON embedded on the page
   (script#library-data) so it also works from file://. */
(function () {
  'use strict';

  function debounce(fn, ms) {
    var t = null;
    return function () {
      var args = arguments, ctx = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(ctx, args); }, ms);
    };
  }

  function loadIndex() {
    var el = document.getElementById('library-data');
    if (!el) { return []; }
    try { return JSON.parse(el.textContent); } catch (e) { return []; }
  }

  var ALL = loadIndex();
  var state = { chip: 'all', q: '' };

  function hrefFor(entry) { return entry.url.replace(/^library\//, ''); }

  function rank(entry, q) {
    if (!q) { return 0; }
    var title = entry.title.toLowerCase();
    var tags = (entry.tags || []).join(' ').toLowerCase();
    var body = (entry.search_text || '').toLowerCase();
    if (title.indexOf(q) === 0) { return 3; }
    if (title.indexOf(q) !== -1) { return 2.5; }
    if (tags.indexOf(q) !== -1) { return 2; }
    if (body.indexOf(q) !== -1) { return 1; }
    return -1;
  }

  function matches(entry) {
    if (state.chip !== 'all' && entry.type !== state.chip) { return false; }
    if (!state.q) { return true; }
    return rank(entry, state.q) > 0;
  }

  var TYPE_ORDER = { source: 0, concept: 1, bridge: 2, moc: 3, guide: 4, control: 5 };

  function currentList() {
    var q = state.q;
    var list = ALL.filter(matches);
    if (q) {
      list = list.map(function (e) { return { e: e, r: rank(e, q) }; })
        .sort(function (a, b) { return b.r - a.r || (a.e.title < b.e.title ? -1 : 1); })
        .map(function (x) { return x.e; });
    } else {
      list = list.slice().sort(function (a, b) {
        var oa = TYPE_ORDER[a.type] != null ? TYPE_ORDER[a.type] : 9;
        var ob = TYPE_ORDER[b.type] != null ? TYPE_ORDER[b.type] : 9;
        if (oa !== ob) { return oa - ob; }
        return a.title.toLowerCase() < b.title.toLowerCase() ? -1 : 1;
      });
    }
    return list;
  }

  function showPreview(idx, list) {
    var panel = document.getElementById('lib-preview');
    var body = document.getElementById('lib-preview-body');
    var pathEl = document.getElementById('lib-preview-path');
    var entry = list[idx];
    if (!panel || !body || !entry) { return; }
    panel.classList.remove('is-hidden');
    if (pathEl) { pathEl.textContent = entry.slug; }
    var useInPath = entry.use_in_path
      ? '<div style="padding:12px 14px;background:var(--accent-soft);border:1px solid var(--accent-edge)">'
        + '<div class="label label-accent">Use in the path</div>'
        + '<div class="small" style="color:var(--accent-ink)">' + entry.use_in_path + '</div></div>'
      : '';
    body.innerHTML =
      '<div><div style="font-family:var(--serif);font-size:22px">' + entry.title + '</div>'
      + '<div class="meta">' + [entry.type, entry.tier, entry.level, entry.cost].filter(Boolean).join(' · ') + '</div></div>'
      + '<div><div class="label">In one line</div><div class="small">' + (entry.one_line || '') + '</div></div>'
      + useInPath
      + '<a class="chip" href="' + hrefFor(entry) + '" style="align-self:flex-start">Open note</a>';
  }

  function render() {
    var list = currentList();

    var countEl = document.getElementById('lib-result-count');
    if (countEl) { countEl.textContent = list.length + ' of ' + ALL.length + ' notes'; }

    var filtered = !!state.q || state.chip !== 'all';
    var mocCaption = document.getElementById('moc-caption');
    if (mocCaption) { mocCaption.classList.toggle('is-hidden', !filtered); }

    var html = list.map(function (entry, i) {
      var tier = entry.tier
        ? '<span class="chip" style="cursor:default;min-height:auto;padding:1px 6px;font-size:11px">' + entry.tier + '</span>'
        : '';
      return '<div class="lib-row" data-idx="' + i + '" data-href="' + hrefFor(entry) + '" tabindex="0">'
        + '<div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap">'
        + '<a href="' + hrefFor(entry) + '" style="font-family:var(--serif);font-size:18px;text-decoration:none;color:var(--ink-strong)">' + entry.title + '</a>'
        + '<span class="meta">' + entry.type + '</span>' + tier
        + '</div>'
        + '<div class="small mid">' + (entry.one_line || '') + '</div>'
        + '</div>';
    }).join('');
    var listEl = document.getElementById('lib-list');
    if (listEl) { listEl.innerHTML = html || '<p class="small mid">No notes match.</p>'; }

    $$('#lib-list .lib-row').forEach(function (row) {
      var idx = Number(row.getAttribute('data-idx'));
      row.addEventListener('mouseenter', function () { showPreview(idx, list); });
      row.addEventListener('focus', function () { showPreview(idx, list); });
      row.addEventListener('click', function (ev) {
        if (ev.target.tagName !== 'A') { window.location.href = row.getAttribute('data-href'); }
      });
      row.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter') { window.location.href = row.getAttribute('data-href'); }
      });
    });
    if (list.length) { showPreview(0, list); }
  }

  ready(function () {
    var search = document.getElementById('lib-search');
    if (search) {
      search.addEventListener('input', debounce(function () {
        state.q = search.value.trim().toLowerCase();
        render();
      }, 150));
    }
    $$('.chip[data-chip]').forEach(function (chip) {
      chip.addEventListener('click', function () {
        $$('.chip[data-chip]').forEach(function (c) { c.classList.remove('active'); });
        chip.classList.add('active');
        state.chip = chip.getAttribute('data-chip');
        render();
      });
    });
    render();
  });
}());

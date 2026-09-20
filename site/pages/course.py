"""docs/course.html — stages 0–3 and the 14-day Stage 0 plan (Agent A)."""

import json
import os


def _res_href(item):
    """External URL wins; then an in-site page; then the library note page."""
    if item.get("url"):
        return item["url"], ' target="_blank" rel="noopener"'
    if item.get("page"):
        return item["page"], ""
    if item.get("resource_slug"):
        return "library/%s.html" % item["resource_slug"], ""
    if item.get("note_slug"):
        return "library/%s.html" % item["note_slug"], ""
    return None, ""


def _stage_cards(stages):
    out = ['<div class="label">Stages</div>']
    for st in stages:
        out.append(
            '<button type="button" class="stage-card" data-stage="%d" aria-pressed="false">'
            '<div class="stage-row"><span class="stage-name">Stage %d</span>'
            '<span class="stage-dur">%s</span></div>'
            '<div class="stage-line">%s</div></button>'
            % (st["id"], st["id"], st["duration"], st["title"])
        )
    return "".join(out)


def _day_rows(plan, icon):
    rows = []
    for item in plan:
        href, attrs = _res_href(item)
        link = ""
        if href:
            link = '<a class="check-res" href="%s"%s>%s</a>' % (
                href, attrs, item.get("resource_title", "Resource"))
        rows.append(
            '<div class="day-row" id="day-%d">'
            '<button type="button" class="check-row" data-day="%d" aria-pressed="false">'
            '%s<span class="check-day">Day %d</span>'
            '<span class="check-text grow">%s</span>'
            '<span class="check-min">%d min</span></button>%s</div>'
            % (item["day"], item["day"], icon("box", 14, "box"), item["day"],
               item["title"], item["minutes"], link)
        )
    return "".join(rows)


def _ready_block(st, icon):
    rows = []
    for i, line in enumerate(st["ready_when"]):
        rows.append(
            '<button type="button" class="check-row" data-ready="%d" data-index="%d" '
            'aria-pressed="false">%s<span class="check-text">%s</span></button>'
            % (st["id"], i, icon("box", 15, "box"), line)
        )
    nxt = st["id"] + 1
    advance = ""
    if nxt <= 3:
        advance = (
            '<button type="button" class="btn btn-primary" data-advance="%d" '
            'style="align-self:flex-start">%s<span>Advance to Stage %d</span></button>'
            % (nxt, icon("play", 15), nxt)
        )
    else:
        advance = ('<div class="meta">No fixed end — Stage 3 is ongoing.</div>')
    heading = ("Ready for Stage %d when" % nxt) if nxt <= 3 else "Signs you've arrived"
    return (
        '<div class="callout"><div class="label label-accent">%s</div>'
        '<div class="checklist">%s</div>%s</div>'
    ) % (heading, "".join(rows), advance)


def _plan_pane(st, plan, icon, active):
    head = (
        '<h2>Goal <span class="mid" style="font-size:17px">— %s</span></h2>' % st["goal"]
    )
    if st["id"] == 0:
        days = (
            '<div class="panel-head"><div class="label">Weeks 1–2, day by day</div>'
            '<div class="meta" id="plan-count">14 days</div></div>'
            '<div class="checklist">%s</div>' % _day_rows(plan, icon)
        )
    else:
        days = ('<div class="meta">Stage %d has no fixed day plan — it runs on the '
                'weekly loop: 5× reading · 2× grammar · 1× lecture.</div>' % st["id"])
    note = '<div class="meta">%s</div>' % st.get("note", "") if st.get("note") else ""
    return (
        '<section class="panel stage-pane%s" data-pane="%d" id="stage-%d">'
        '%s%s<div class="grow"></div>%s%s</section>'
    ) % ("" if active else " is-hidden", st["id"], st["id"],
         head, days, note, _ready_block(st, icon))


def _side_pane(st, icon, active):
    par = st.get("parallel") or {}
    href, attrs = _res_href(par)
    cta = ""
    if href:
        cta = ('<a class="btn btn-secondary" href="%s"%s style="align-self:flex-start">'
               '%s<span>%s</span></a>' % (href, attrs, icon("play", 14),
                                          par.get("cta", "Open")))
    parallel = (
        '<section class="panel"><div class="label">Parallel context</div>'
        '<h3>%s</h3><div class="meta">%s</div>'
        '<div class="small mid">%s</div>%s</section>'
    ) % (par.get("title", ""), par.get("meta", ""), par.get("body", ""), cta)

    items = []
    for r in st["resources"]:
        rhref, rattrs = _res_href(r)
        title = ('<a href="%s"%s>%s</a>' % (rhref, rattrs, r["title"])) if rhref \
            else ('<span>%s</span>' % r["title"])
        items.append('<div class="res-item">%s<div class="meta">%s</div></div>'
                     % (title, r.get("meta", "")))
    resources = (
        '<section class="panel"><div class="panel-head">'
        '<div class="label">Resources this stage</div><div class="meta">%d</div></div>'
        '<div class="stack" style="gap:14px">%s</div></section>'
    ) % (len(st["resources"]), "".join(items))

    return ('<div class="stack stage-side%s" data-pane="%d" style="gap:16px">%s%s</div>'
            % ("" if active else " is-hidden", st["id"], parallel, resources))


def build(ctx):
    render_page = ctx["render_page"]
    shell = ctx["shell"]
    icon = shell.icon

    with open(os.path.join(ctx["data_dir"], "course.json"), encoding="utf-8") as fh:
        course = json.load(fh)
    stages, plan = course["stages"], course["plan"]

    rail_col = (
        '<div class="stack" style="gap:8px">%s<div class="grow"></div>'
        '<div class="stack" style="gap:7px;padding-top:14px;'
        'border-top:1px solid var(--rule)">'
        '<div class="meta">Weekly loop from Stage 1</div>'
        '<div class="meta mid">%s</div></div></div>'
    ) % (_stage_cards(stages), course["meta"]["weekly_loop"])

    middle = '<div class="stack" style="gap:16px">%s</div>' % "".join(
        _plan_pane(st, plan, icon, st["id"] == 0) for st in stages)
    side = "".join(_side_pane(st, icon, st["id"] == 0) for st in stages)

    body = (
        shell.page_head("Course", "Reading-first, video-driven, free-first",
                        '<span id="course-status">Stage 0 · 14 days</span>')
        + '<div class="cols cols-course">%s%s%s</div>' % (rail_col, middle, side)
    )

    extra_js = '<script src="course.js"></script>'
    html = render_page("Course", "course", body, extra_js=extra_js)
    with open(os.path.join(ctx["out_dir"], "course.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    with open(os.path.join(ctx["out_dir"], "course.js"), "w", encoding="utf-8") as fh:
        fh.write(COURSE_JS)
    return ["course.html", "course.js"]


COURSE_JS = r"""/* Course page behaviour (generated by site/pages/course.py). */
(function () {
  'use strict';
  var PLAN_DAYS = 14;
  var current = 0;

  function boxSvg(done) {
    return done ? '<path d="m4 12 5.5 5.5L20 6.5"/>'
                : '<rect x="4" y="4" width="16" height="16"/>';
  }
  function paint(row, done) {
    row.classList.toggle('done', done);
    row.setAttribute('aria-pressed', done ? 'true' : 'false');
    var svg = row.querySelector('svg');
    if (svg) { svg.setAttribute('class', done ? 'tick' : 'box'); svg.innerHTML = boxSvg(done); }
  }

  function showStage(n, push) {
    current = n;
    $$('.stage-card').forEach(function (c) {
      var on = Number(c.getAttribute('data-stage')) === n;
      c.classList.toggle('active', on);
      c.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    $$('.stage-pane, .stage-side').forEach(function (p) {
      p.classList.toggle('is-hidden', Number(p.getAttribute('data-pane')) !== n);
    });
    var status = $('#course-status');
    if (status) {
      status.textContent = (n === 0)
        ? ('Stage 0 · ' + Progress.daysDone() + ' of ' + PLAN_DAYS + ' days')
        : ('Stage ' + n);
    }
    if (push && history.replaceState) { history.replaceState(null, '', '#stage-' + n); }
  }

  function renderDays() {
    var nextN = Progress.nextDay(PLAN_DAYS);
    $$('.check-row[data-day]').forEach(function (row) {
      var n = Number(row.getAttribute('data-day'));
      var done = Progress.dayDone(n);
      paint(row, done);
      row.classList.toggle('current', !done && n === nextN);
    });
    var left = PLAN_DAYS - Progress.daysDone();
    var count = $('#plan-count');
    if (count) { count.textContent = Progress.daysDone() + ' done · ' + left + ' left'; }
  }

  function renderReady() {
    $$('.check-row[data-ready]').forEach(function (row) {
      var st = Number(row.getAttribute('data-ready'));
      var i = Number(row.getAttribute('data-index'));
      paint(row, Progress.isReady(st, i));
    });
  }

  function fromHash() {
    var h = (location.hash || '').replace('#', '');
    var m = /^stage-([0-3])$/.exec(h);
    if (m) { showStage(Number(m[1]), false); return; }
    m = /^day-(\d{1,2})$/.exec(h);
    if (m) {
      showStage(0, false);
      var el = document.getElementById('day-' + m[1]);
      if (el) {
        $$('.day-row.target').forEach(function (r) { r.classList.remove('target'); });
        el.classList.add('target');
        el.scrollIntoView({ block: 'center' });
      }
      return;
    }
    showStage(0, false);
  }

  ready(function () {
    $$('.stage-card').forEach(function (card) {
      card.addEventListener('click', function () {
        showStage(Number(card.getAttribute('data-stage')), true);
      });
    });
    $$('.check-row[data-day]').forEach(function (row) {
      row.addEventListener('click', function () {
        var n = Number(row.getAttribute('data-day'));
        Progress.markDay(n, !Progress.dayDone(n));
        renderDays();
        showStage(current, false);
      });
    });
    $$('.check-row[data-ready]').forEach(function (row) {
      row.addEventListener('click', function () {
        var st = Number(row.getAttribute('data-ready'));
        var i = Number(row.getAttribute('data-index'));
        Progress.setReady(st, i, !Progress.isReady(st, i));
        renderReady();
      });
    });
    $$('[data-advance]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var n = Number(btn.getAttribute('data-advance'));
        Progress.setStage(n);
        showStage(n, true);
      });
    });
    renderDays();
    renderReady();
    fromHash();
    window.addEventListener('hashchange', fromHash);
  });
}());
"""

"""docs/index.html — the Dashboard (Agent A).

Static markup is rendered here; everything that depends on the learner's
progress is filled in by the inline script from `Progress` (app.js) and the
embedded course data. The no-JS rendering is the honest empty state.
"""

import json
import os

# 1 John 1:1 per SBLGNT, wooden gloss — both from
# bridges/1-john-1-1-4-first-reading.md
PASSAGE_REF = "1 John 1:1 · SBLGNT"
PASSAGE_GREEK = (
    "Ὃ ἦν ἀπ᾽ <span class=\"highlight\">ἀρχῆς</span>, ὃ ἀκηκόαμεν, "
    "ὃ ἑωράκαμεν τοῖς ὀφθαλμοῖς ἡμῶν"
)
PASSAGE_GLOSS = (
    "That-which was from beginning, that-which we-have-heard, "
    "that-which we-have-seen with the eyes of-us…"
)


def _pips(n=14):
    return '<div class="pips" id="m-pips">%s</div>' % ("<div class=\"pip\"></div>" * n)


def _metric(label, num_id, unit, sub_html, extra=""):
    return (
        '<div class="metric">'
        '<div class="label">%s</div>'
        '<div class="metric-num"><span id="%s">—</span>'
        '<span class="metric-unit">%s</span></div>'
        '%s%s</div>'
    ) % (label, num_id, unit, sub_html, extra)


def _checklist_rows(plan, icon):
    rows = []
    for item in plan[:7]:
        rows.append(
            '<button type="button" class="check-row" data-day="%d" aria-pressed="false">'
            '%s<span class="check-text">Day %d · %s</span></button>'
            % (item["day"], icon("box", 15, "box"), item["day"], item["title"])
        )
    return "".join(rows)


def build(ctx):
    render_page = ctx["render_page"]
    shell = ctx["shell"]
    icon = shell.icon

    with open(os.path.join(ctx["data_dir"], "course.json"), encoding="utf-8") as fh:
        course = json.load(fh)
    stage0 = course["stages"][0]
    plan = course["plan"]

    subtitle = "Stage %d · %s · %s" % (stage0["id"], stage0["title"], stage0["duration"])

    next_action = (
        '<section class="next-action" aria-labelledby="na-label">'
        '<div class="stack" style="gap:7px">'
        '<div class="label" id="na-label">Next action</div>'
        '<div class="next-title" id="na-title">Day 1 · Start here</div>'
        '<div class="next-detail" id="na-detail">%s</div>'
        '</div>'
        '<div class="next-side">'
        '<div class="meta" id="na-min">%d min</div>'
        '<a class="btn btn-primary" id="na-btn" href="course.html#day-1">'
        '%s<span id="na-btn-label">Start</span></a>'
        '</div></section>'
    ) % (plan[0]["detail"], plan[0]["minutes"], icon("play", 15))

    metrics = (
        '<section class="metric-row" aria-label="Progress">'
        + _metric("Streak", "m-streak", " days",
                  '<div class="metric-sub" id="m-streak-sub">no days logged yet</div>')
        + _metric("Stage 0", "m-days", " of 14 days", "", _pips())
        + _metric("Letters known", "m-letters", " of 24",
                  '<div class="metric-sub" id="m-weak">quiz not started</div>')
        + _metric("Minutes this week", "m-minutes", " min",
                  '<div class="metric-sub" id="m-minutes-sub">no sessions logged</div>')
        + "</section>"
    )

    checklist = (
        '<section class="panel" aria-labelledby="cl-label">'
        '<div class="panel-head"><div class="label" id="cl-label">Stage 0 checklist</div>'
        '<div class="meta" id="cl-count">%d left</div></div>'
        '<div class="checklist">%s</div>'
        '<div class="meta">Days 8–14 continue on the '
        '<a href="course.html#stage-0">Course</a> page.</div>'
        '</section>'
    ) % (len(plan[:7]), _checklist_rows(plan, icon))

    passage = (
        '<section class="panel mobile-first" aria-labelledby="pg-label">'
        '<div class="panel-head"><div class="label" id="pg-label">Current passage</div>'
        '<div class="meta">%s</div></div>'
        '<div class="greek passage" lang="grc">%s</div>'
        '<div class="gloss">%s</div>'
        '<div class="grow"></div>'
        '<div class="meta">4 clauses · wooden gloss from the 1 John 1:1–4 bridge note.</div>'
        '<a class="btn btn-secondary" href="reading.html" style="align-self:flex-start">'
        '%s<span>Open in the Reading Room</span></a>'
        '</section>'
    ) % (PASSAGE_REF, PASSAGE_GREEK, PASSAGE_GLOSS, icon("book", 15))

    body = (
        shell.page_head("Dashboard", subtitle, '<span class="hide-mobile" data-today></span>')
        + '<div class="stack" style="gap:18px">'
        + next_action + metrics
        + '<div class="cols cols-1-25">' + checklist + passage + "</div>"
        + "</div>"
    )

    extra_js = (
        '<script id="course-data" type="application/json">%s</script>\n'
        '<script src="index.js"></script>'
    ) % json.dumps({"plan": plan, "stage0": stage0}, ensure_ascii=False)

    html = render_page("Dashboard", "dashboard", body, extra_js=extra_js)
    with open(os.path.join(ctx["out_dir"], "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)

    with open(os.path.join(ctx["out_dir"], "index.js"), "w", encoding="utf-8") as fh:
        fh.write(INDEX_JS)

    return ["index.html", "index.js"]


INDEX_JS = r"""/* Dashboard behaviour (generated by site/pages/dashboard.py). */
(function () {
  'use strict';
  var DATA = JSON.parse(document.getElementById('course-data').textContent);
  var PLAN = DATA.plan;

  function planDay(n) {
    for (var i = 0; i < PLAN.length; i++) { if (PLAN[i].day === n) { return PLAN[i]; } }
    return null;
  }

  function renderNext() {
    var n = Progress.nextDay(PLAN.length);
    var title = $('#na-title'), detail = $('#na-detail'), min = $('#na-min');
    var btn = $('#na-btn'), label = $('#na-btn-label');
    if (n === null) {
      title.textContent = 'Stage 0 complete';
      detail.textContent = 'All fourteen days are done. Review the "ready when" '
        + 'checklist on the Course page and advance to Stage 1.';
      min.textContent = '';
      btn.href = 'course.html#stage-0';
      label.textContent = 'Review Stage 0';
      return;
    }
    var d = planDay(n);
    var fresh = Progress.isEmpty();
    title.textContent = fresh ? 'Day 1 · Start here' : ('Day ' + d.day + ' · ' + d.title);
    detail.textContent = d.detail;
    min.textContent = d.minutes + ' min';
    btn.href = 'course.html#day-' + d.day;
    label.textContent = fresh ? 'Start' : 'Begin the drill';
  }

  function renderMetrics() {
    var streak = Progress.get().streak;
    $('#m-streak').textContent = streak.count ? streak.count : '—';
    $('#m-streak-sub').textContent = streak.last
      ? ('last active ' + fmtDate(streak.last)) : 'no days logged yet';

    var done = Progress.daysDone();
    $('#m-days').textContent = done ? done : '—';
    $$('#m-pips .pip').forEach(function (pip, i) {
      pip.className = 'pip' + (Progress.dayDone(i + 1) ? ' on' : '');
    });

    var known = Progress.lettersKnown();
    $('#m-letters').textContent = known ? known : '—';
    var weak = Progress.weakLetters(5);
    $('#m-weak').textContent = weak.length ? ('weak · ' + weak.join(' ')) : 'quiz not started';

    var mins = Progress.minutesThisWeek();
    $('#m-minutes').textContent = mins ? mins : '—';
    var sessions = Progress.sessionsThisWeek();
    $('#m-minutes-sub').textContent = sessions
      ? ('across ' + sessions + (sessions === 1 ? ' session' : ' sessions'))
      : 'no sessions logged';
  }

  function renderChecklist() {
    var nextN = Progress.nextDay(PLAN.length);
    var left = 0;
    $$('.check-row[data-day]').forEach(function (row) {
      var n = Number(row.getAttribute('data-day'));
      var done = Progress.dayDone(n);
      if (!done) { left++; }
      row.classList.toggle('done', done);
      row.classList.toggle('current', !done && n === nextN);
      row.setAttribute('aria-pressed', done ? 'true' : 'false');
      var svg = row.querySelector('svg');
      if (svg) {
        svg.setAttribute('class', done ? 'tick' : 'box');
        svg.innerHTML = done
          ? '<path d="m4 12 5.5 5.5L20 6.5"/>'
          : '<rect x="4" y="4" width="16" height="16"/>';
      }
    });
    $('#cl-count').textContent = left + ' of 7 left';
  }

  function renderAll() { renderNext(); renderMetrics(); renderChecklist(); }

  ready(function () {
    $$('.check-row[data-day]').forEach(function (row) {
      row.addEventListener('click', function () {
        var n = Number(row.getAttribute('data-day'));
        Progress.markDay(n, !Progress.dayDone(n));
        renderAll();
      });
    });
    renderAll();
  });
}());
"""

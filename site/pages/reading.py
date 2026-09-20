"""docs/reading.html — the Reading Room (Agent B).

1 John 1:1-4, SBLGNT, clause by clause. Greek is taken verbatim from
bridges/1-john-1-1-4-first-reading.md; per-word lemma and parsing come from
MorphGNT (github.com/morphgnt/sblgnt, 83-1Jn-morphgnt.txt, CC BY-SA 3.0) and
are decoded into readable parses in site/static/data/readings/1jn-1-1-4.json.
Glosses, observations and tasks are the vault's own.

The reading JSON is copied to docs/data/readings/ and also embedded in the
page, so the page works from a file:// URL.
"""

import os


def _load(ctx):
    path = os.path.join(ctx["data_dir"], "readings", "1jn-1-1-4.json")
    with open(path, encoding="utf-8") as fh:
        return ctx["json"].load(fh)


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def _clauses(data):
    out = []
    n = 0
    last_verse = None
    for cl in data["clauses"]:
        words = []
        for w in cl["words"]:
            cls = "w has-note" if w.get("note") else "w"
            words.append(
                '<button type="button" class="%s" data-w="%d" aria-pressed="false">%s</button>'
                % (cls, n, _esc(w["surface"]))
            )
            n += 1
        verse = str(cl["verse"]) if cl["verse"] != last_verse else ""
        last_verse = cl["verse"]
        out.append(
            '<div class="clause">'
            '<div class="cl-verse">%s</div>'
            '<div>'
            '<div class="cl-line greek" lang="grc">%s</div>'
            '<div class="cl-gloss">%s</div>'
            '</div></div>' % (verse, "".join(words), _esc(cl["gloss"]))
        )
    return "".join(out)


def _observations(shell, data):
    out = []
    for i, ob in enumerate(data["observations"]):
        caret = (
            '<svg class="caret" width="14" height="14" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>'
        )
        out.append(
            '<details class="obs"%s><summary>%s'
            '<span class="obs-title" lang="grc">%s</span>'
            '<span class="obs-chip">%s</span></summary>'
            '<div class="obs-body">%s</div></details>'
            % (" open" if i == 0 else "", caret, _esc(ob["title"]),
               _esc(ob["claim"]), _esc(ob["body"]))
        )
    return "".join(out)


def _tasks(data):
    out = []
    for t in data["tasks"]:
        link = ""
        if t.get("url"):
            link = ('<a class="task-link" href="%s" target="_blank" rel="noopener">'
                    'open it</a>' % _esc(t["url"]))
        out.append(
            '<button type="button" class="task" data-task="%d" aria-pressed="false">'
            '<span class="t-mark"></span>'
            '<span class="t-n">%d</span>'
            '<span class="t-text">%s %s</span></button>'
            % (t["id"], t["id"], _esc(t["text"]), link)
        )
    return "".join(out)


def build(ctx):
    shell = ctx["shell"]
    data = _load(ctx)
    embedded = ctx["json"].dumps(data, ensure_ascii=False, separators=(",", ":"))
    embedded = embedded.replace("</", "<\\/")

    readings_rail = (
        '<section class="panel readings-rail" aria-labelledby="readings-label">'
        '<div class="label" id="readings-label">Readings</div>'
        '<a class="reading-item active" href="reading.html" aria-current="page">'
        '<span class="ri-ref" lang="grc">1 John 1:1–4</span>'
        '<span class="ri-meta">SBLGNT · Stage 0</span></a>'
        '<div class="reading-more">More passages land here as the bridge notes '
        'are written — one entry per note.</div>'
        '</section>'
    )

    passage_panel = (
        '<section class="panel" aria-labelledby="clauses-label">'
        '<div class="panel-head" style="border-bottom:0;padding-bottom:0">'
        '<div class="label" id="clauses-label">Clause by clause</div>'
        '<div class="meta">v.1 fronted · main verb lands in v.3</div>'
        '</div>'
        '<div class="clauses" id="clauses">%s</div>'
        '<div class="meta" style="padding-top:12px;border-top:1px solid var(--rule)">'
        '%s Click a word for its parse; ← and → step through the passage.'
        '</div></section>' % (_clauses(data), _esc(data["gloss_note"]))
    )

    close_icon = (
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" aria-hidden="true">'
        '<path d="M6 6l12 12"/><path d="M18 6 6 18"/></svg>'
    )
    parse_card = (
        '<section class="panel parse-card" id="parse-card" aria-labelledby="parse-label"'
        ' aria-live="polite">'
        '<div class="sheet-grip"></div>'
        '<div class="parse-head">'
        '<div class="stack" style="gap:6px">'
        '<div class="label" id="parse-label">Parse card</div>'
        '<div class="parse-surface" id="parse-surface"></div>'
        '<div class="meta" id="parse-verse"></div>'
        '</div>'
        '<button type="button" class="sheet-close" id="sheet-close" aria-label="Close the '
        'parse card">%s</button>'
        '</div>'
        '<div id="parse-body"></div>'
        '</section>' % close_icon
    )

    observations = (
        '<section class="panel" aria-labelledby="obs-label" style="margin-top:14px">'
        '<div class="panel-head">'
        '<div class="label" id="obs-label">What the Greek adds</div>'
        '<div class="meta">%d notes · claim ladder marked</div>'
        '</div>%s</section>'
        % (len(data["observations"]), _observations(shell, data))
    )

    tasks = (
        '<section class="panel" aria-labelledby="tasks-label" style="margin-top:14px">'
        '<div class="panel-head">'
        '<div class="stack" style="gap:3px">'
        '<div class="label label-accent" id="tasks-label">Do this</div>'
        '<div class="meta">%s</div></div>'
        '<div class="meta" id="task-count">none done yet</div>'
        '</div>'
        '<div class="tasks" id="tasks">%s</div>'
        '</section>' % (_esc(data["task_note"]), _tasks(data))
    )

    attribution = (
        '<section class="attribution" style="margin-top:14px">'
        'Greek text: <a href="https://sblgnt.com/" target="_blank" rel="noopener">'
        'SBL Greek New Testament</a> (Logos/SBL). '
        'Morphology: <a href="https://github.com/morphgnt/sblgnt" target="_blank" '
        'rel="noopener">MorphGNT</a>, '
        '<a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank" '
        'rel="noopener">CC BY-SA 3.0</a>.'
        '</section>'
    )

    body = (
        shell.page_head(
            data["ref"],
            "%s · %s" % (data["source"], data["subtitle"]),
            right="gloss deliberately wooden",
        )
        + '<div class="read-layout">%s%s%s</div>' % (readings_rail, passage_panel, parse_card)
        + observations
        + tasks
        + attribution
        + '<script type="application/json" id="reading-data">%s</script>' % embedded
    )

    html = ctx["render_page"](
        "Reading Room", "reading", body,
        extra_head='<link rel="stylesheet" href="pages.css">',
        extra_js='<script src="reading.js"></script>',
    )
    path = os.path.join(ctx["out_dir"], "reading.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return ["reading.html"]

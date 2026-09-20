"""docs/alphabet.html — the Alphabet trainer (Agent B).

Learn mode: a 6x4 grid (4 columns on mobile) with a focus panel and a
pronunciation toggle; weak letters (from Progress) are shaded.
Quiz mode: 10-question rounds, alternating glyph->name and name->glyph.

The letter data (site/static/data/alphabet.json, built from
concepts/greek-alphabet-and-diacritics.md) is both copied to docs/data/ and
embedded in the page as <script type="application/json">, so the page works
from a file:// URL where fetch() of a local JSON file is blocked.
"""

import os

DATA_REL = os.path.join("data", "alphabet.json")


def _load(ctx):
    path = os.path.join(ctx["data_dir"], "alphabet.json")
    with open(path, encoding="utf-8") as fh:
        return ctx["json"].load(fh)


def _diacritics(data):
    items = []
    for d in data.get("diacritics", []):
        items.append(
            '<div class="diacritic">'
            '<div class="dc-head"><span class="dc-marks" lang="grc">%s</span>'
            '<span class="dc-title">%s</span></div>'
            '<div class="dc-body">%s</div></div>'
            % (d["marks"], d["title"], d["body"])
        )
    return "".join(items)


def build(ctx):
    shell = ctx["shell"]
    data = _load(ctx)
    embedded = ctx["json"].dumps(data, ensure_ascii=False, separators=(",", ":"))
    # never let a "</script" sequence out of the JSON island ("\/" is legal JSON)
    embedded = embedded.replace("</", "<\\/")

    controls = (
        '<div class="alpha-controls">'
        '<div class="alpha-control">'
        '<span class="label" id="mode-label">Mode</span>'
        '<div class="switch" id="mode-switch" role="group" aria-labelledby="mode-label">'
        '<button type="button" data-mode="learn" aria-pressed="true">Learn</button>'
        '<button type="button" data-mode="quiz" aria-pressed="false">Quiz</button>'
        '</div></div>'
        '<div class="alpha-control">'
        '<span class="label" id="pron-label">Pronunciation</span>'
        '<div class="switch" id="pron-switch" role="group" aria-labelledby="pron-label">'
        '<button type="button" data-pron="erasmian" aria-pressed="true">Erasmian</button>'
        '<button type="button" data-pron="koine" aria-pressed="false">Restored Koine</button>'
        '</div></div>'
        '</div>'
    )

    grid_panel = (
        '<section class="panel" aria-labelledby="grid-label">'
        '<div class="panel-head" style="border-bottom:0;padding-bottom:0">'
        '<div class="label" id="grid-label">All 24 · Erasmian values</div>'
        '<div class="legend"><span class="swatch"></span>'
        '<span id="grid-legend-text">weak — drill these</span></div>'
        '</div>'
        '<div class="letter-grid" id="letter-grid"></div>'
        '<div class="meta" style="padding-top:12px;border-top:1px solid var(--rule)">'
        'Breathings ᾿ ῾ · accents ´ ` ῀ · iota subscript '
        'ᾳ ῃ ῳ · diaeresis ¨ — '
        'punctuation: · is a semicolon, ; is a question mark.'
        '</div>'
        '</section>'
    )

    focus_panel = (
        '<section class="panel" id="focus-panel" aria-labelledby="focus-label">'
        '<div class="panel-head" style="border-bottom:0;padding-bottom:0">'
        '<div class="label" id="focus-label">In focus</div>'
        '<div class="meta" id="focus-count">24 letters</div>'
        '</div>'
        '<div id="focus-body"></div>'
        '</section>'
    )

    quiz_panel = (
        '<section class="panel is-hidden" id="quiz-panel" aria-labelledby="quiz-label">'
        '<div class="panel-head">'
        '<div class="label" id="quiz-label">Quiz · weak letters first</div>'
        '<div class="meta" id="quiz-count">1 of 10</div>'
        '</div>'
        '<div id="quiz-body"></div>'
        '</section>'
    )

    diacritics_panel = (
        '<section class="panel" aria-labelledby="dia-label" style="margin-top:16px">'
        '<div class="panel-head">'
        '<div class="label" id="dia-label">Diacritics</div>'
        '<div class="meta">recognise them; you need not reproduce them yet</div>'
        '</div>'
        '<div class="diacritics">%s</div>'
        '<div class="meta">From the vault note <a href="library/'
        'greek-alphabet-and-diacritics.html">Greek Alphabet and Diacritics</a>.</div>'
        '</section>' % _diacritics(data)
    )

    body = (
        shell.page_head(
            "Alphabet",
            "24 letters · breathings · accents · iota subscript",
            right='<span id="known-count">not quizzed yet</span>',
        )
        + controls
        + '<div class="alpha-layout">%s<div class="stack" style="gap:16px">%s%s</div></div>'
        % (grid_panel, focus_panel, quiz_panel)
        + diacritics_panel
        + '<script type="application/json" id="alphabet-data">%s</script>' % embedded
    )

    html = ctx["render_page"](
        "Alphabet", "alphabet", body,
        extra_head='<link rel="stylesheet" href="pages.css">',
        extra_js='<script src="alphabet.js"></script>',
    )
    path = os.path.join(ctx["out_dir"], "alphabet.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return ["alphabet.html"]

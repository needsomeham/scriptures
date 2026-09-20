# site/ — how the Greek Study site is built

`docs/` is **generated output**. Never hand-edit it; run the build instead.

```bash
python3 site/build.py      # from anywhere; writes <repo>/docs
```

Python 3, stdlib only (see `requirements.txt`). The build deletes and rebuilds
`docs/` on every run, so it is idempotent and takes well under a second.

## Layout

```
site/
  build.py              orchestrator (Agent A)
  templates/shell.py    page shell: head, rail nav, tab bar, footer (Agent A)
  pages/
    dashboard.py        docs/index.html          (A)
    course.py           docs/course.html         (A)
    alphabet.py         docs/alphabet.html       (B — currently a stub)
    reading.py          docs/reading.html        (B — currently a stub)
    library.py          docs/library/*.html      (C — currently a stub)
    stub.py             shared placeholder body for the stubs
  lib/                  shared helpers (C lands md.py here)
  static/               copied verbatim into docs/
    style.css  app.js  data/course.json
docs/
  index.html course.html alphabet.html reading.html 404.html
  library/index.html
  style.css app.js index.js course.js
  data/course.json
  .nojekyll
```

`site/static/` is mirrored into `docs/`: `static/style.css` → `docs/style.css`,
`static/data/course.json` → `docs/data/course.json`. Drop a file in `static/`
and it ships; no build change needed.

## The page contract

`build.py` imports each page module and calls:

```python
paths = module.build(ctx)     # returns a list of paths written, relative to docs/
```

`ctx` is a plain dict:

| key | what |
|---|---|
| `vault_root` | absolute path to the repo root (the Obsidian vault) |
| `out_dir` | absolute path to `docs/` |
| `data_dir` | absolute path to `docs/data/` (static data is already copied there) |
| `render_page` | the shell function below |
| `shell` | the `templates.shell` module — `icon()`, `page_head()`, `NAV`, `REPO_URL` |
| `parse_frontmatter` | `parse_frontmatter(text) -> (dict, body)` — flat `key: value` and `key: [a, b]` |
| `json` | the stdlib module, for convenience |

Write your own files with `open(os.path.join(ctx["out_dir"], ...), "w", encoding="utf-8")`.
Do not touch another agent's output files.

## Shell API

```python
render_page(title, active_nav, body_html, extra_head="", extra_js="", depth=0) -> str
```

* `title` — page name; `<title>` becomes `"<title> · Greek Study"`.
* `active_nav` — `"dashboard" | "course" | "alphabet" | "reading" | "library"`, or
  `None` for a page outside the nav (404).
* `body_html` — your markup; it is dropped inside `<main class="main">`, above the footer.
* `extra_head` — raw HTML appended to `<head>` (an extra stylesheet, an inline `<style>`).
* `extra_js` — raw HTML placed just before `</body>`, **after** `app.js` loads, so
  `Progress`, `$`, `$$`, `ready`, `fmtDate`, `escapeHtml` are already defined.
* `depth` — folder depth below `docs/`. `0` for `docs/foo.html`, `1` for
  `docs/library/foo.html`. Every asset and nav href is prefixed with `"../" * depth`,
  which is how the site stays link-clean under GitHub Pages' `/scriptures/` prefix.
  **All links must be relative — never start an href with `/`.**

Helpers on the shell module:

```python
shell.icon(name, size=16, cls="")   # inline SVG: grid lines alpha book shelf check box play
shell.page_head(title, subtitle="", right="")   # the standard header strip
```

Example page module:

```python
import os

def build(ctx):
    shell = ctx["shell"]
    body = shell.page_head("Alphabet", "24 letters") + '<section class="panel">…</section>'
    html = ctx["render_page"]("Alphabet", "alphabet", body,
                              extra_head='<link rel="stylesheet" href="pages.css">',
                              extra_js='<script src="alphabet.js"></script>')
    with open(os.path.join(ctx["out_dir"], "alphabet.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    return ["alphabet.html"]
```

## CSS you can rely on

`style.css` (Agent A) defines the tokens as custom properties on `:root`
(`--bg --panel --rail --ink --ink-mid --ink-muted --rule --accent --accent-soft
--accent-edge --highlight --serif --ui`) plus the shared components:

`.panel` `.panel-head` `.label` `.btn` `.btn-primary` `.btn-secondary`
`.metric` `.metric-row` `.metric-num` `.pips`/`.pip` `.next-action`
`.checklist`/`.check-row` (`.done`, `.current`) `.chip` `.segmented`
`.stage-card` `.greek` `.passage` `.gloss` `.highlight` `.callout` `.res-item`
`.cols` (+ `.cols-1-25`, `.cols-course`) `.is-hidden` `.mobile-first`
`.small` `.meta` `.mid` `.muted` `.stack` `.grow` `.sr-only`

Breakpoint is **900px**: at or above it the desktop rail shows; below it the
bottom tab bar does. Agent B appends to `static/pages.css`, Agent C owns
`static/library.css`; neither edits `style.css`. Greek text always carries
`lang="grc"` and the `.greek` class.

## Progress store (`app.js`)

`localStorage` key `greek-study:v1`. All reads/writes go through `Progress`;
every write dispatches a `progress:change` event on `document`.

```js
Progress.get()                  // the whole state object
Progress.save(state)
Progress.markDay(n, on)         // on defaults to true; pass false to uncheck
Progress.dayDone(n) / daysDone() / nextDay(total)
Progress.touch()                // advances the streak at most once per calendar day
Progress.logMinutes(min, what)  // also touches the streak
Progress.minutesThisWeek() / sessionsThisWeek()   // week starts Monday
Progress.letterResult(ch, ok)
Progress.letterKnown(ch) / lettersKnown() / weakLetters(limit)
Progress.setReady(stage, i, on) / isReady(stage, i)
Progress.setStage(n)
Progress.markReading(slug, {opened, tasksDone})
Progress.isEmpty()              // true when nothing has been recorded — use for empty states
Progress.export() / Progress.import(json) / Progress.reset()
```

State shape:

```json
{"stage":0,"days":{"1":"2026-09-20"},"ready":{"0":{"1":true}},
 "streak":{"last":"2026-09-20","count":3},
 "minutes":[{"date":"2026-09-20","min":20,"what":"alphabet"}],
 "letters":{"ξ":{"seen":6,"correct":5}},
 "readings":{"1jn-1-1-4":{"opened":"2026-09-20","tasksDone":[1]}}}
```

A letter counts as **known** at ≥3 correct *and* ≥75% correct. When the store is
empty, show `—`, never a fabricated number.

Helpers also on `window`: `$(sel, root)`, `$$(sel, root)`, `ready(fn)`,
`fmtDate(date)` → `"Mon 14 Sep"` (`fmtDate(d, 'iso')` → `"2026-09-14"`),
`escapeHtml(s)`. Any element with a `data-today` attribute is filled with
today's date automatically.

## Data files

* `static/data/course.json` (A) — `{meta, stages:[…], plan:[…]}`.
  A stage has `id, title, duration, goal, ready_when[], parallel{}, note, resources[]`.
  A plan day has `day, title, minutes, detail` and optionally `resource_title`,
  `resource_slug` (a vault note → `library/<slug>.html`), `url` (external),
  `page` (another page of this site). Link precedence: `url` → `page` → `resource_slug`.
* `static/data/alphabet.json` (B) — 24 letters.
* `static/data/readings/1jn-1-1-4.json` (B).
* `library-index.json` + `search.json` (C, generated at build time).

Dashboard and Course embed or fetch what they need from the copy in `docs/data/`,
so a page never needs to read the vault at runtime.

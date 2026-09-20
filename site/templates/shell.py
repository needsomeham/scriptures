"""Page shell for the Greek Study site (Agent A owns this file).

Public API
----------
render_page(title, active_nav, body_html, extra_head="", extra_js="", depth=0) -> str
    Returns a complete HTML document.

    title       str   page name; the <title> becomes "<title> · Greek Study"
    active_nav  str   one of NAV_KEYS: dashboard | course | alphabet | reading | library
    body_html   str   the page's own markup, dropped inside <main class="main">
    extra_head  str   raw HTML injected at the end of <head> (extra <link>/<style>)
    extra_js    str   raw HTML injected before </body> (e.g. '<script src="x.js"></script>'
                      or an inline '<script>…</script>' block)
    depth       int   folder depth of the page below docs/ — 0 for docs/page.html,
                      1 for docs/library/page.html. All asset and nav links are
                      prefixed with "../" * depth so every link stays relative.

Also exported: icon(name, size=16, cls=""), NAV, NAV_KEYS, REPO_URL, page_head().
"""

REPO_URL = "https://github.com/needsomeham/scriptures"
WORDMARK = "Ἐν ἀρχῇ"
WORDMARK_SUB = "a reading course"
FOOTER_LICENSE = (
    "Text: SBLGNT · Morphology: MorphGNT (CC BY-SA 3.0)"
)

FONTS_HREF = (
    "https://fonts.googleapis.com/css2?family=Gentium+Plus:ital,wght@0,400;0,700;1,400"
    "&amp;family=IBM+Plex+Sans:wght@400;500;600&amp;display=swap"
)

# name -> (href relative to docs/, rail label, mobile tab label, icon name)
NAV = [
    ("dashboard", "index.html", "Dashboard", "Dashboard", "grid"),
    ("course", "course.html", "Course", "Course", "lines"),
    ("alphabet", "alphabet.html", "Alphabet", "Alphabet", "alpha"),
    ("reading", "reading.html", "Reading Room", "Reading", "book"),
    ("library", "library/index.html", "Library", "Library", "shelf"),
]
NAV_KEYS = [n[0] for n in NAV]

# Inline SVG paths, 24-grid, stroke 1.6, currentColor-friendly (colour via CSS).
_ICON_PATHS = {
    "grid": ('<rect x="3" y="3" width="7" height="8"/><rect x="14" y="3" width="7" height="5"/>'
             '<rect x="14" y="11" width="7" height="10"/><rect x="3" y="14" width="7" height="7"/>'),
    "lines": '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h10"/>',
    "alpha": '<path d="M5 19 12 5l7 14"/><path d="M8 14h8"/>',
    "book": ('<path d="M4 5h6a2 2 0 0 1 2 2v13a2 2 0 0 0-2-1.5H4z"/>'
             '<path d="M20 5h-6a2 2 0 0 0-2 2v13a2 2 0 0 1 2-1.5h6z"/>'),
    "shelf": '<path d="M4 4h5v16H4z"/><path d="M10 4h4v16h-4z"/><path d="m15.5 5 4 15"/>',
    "check": '<path d="m4 12 5.5 5.5L20 6.5"/>',
    "box": '<rect x="4" y="4" width="16" height="16"/>',
    "play": '<path d="M7 4.5 19 12 7 19.5z"/>',
}


def icon(name, size=16, cls=""):
    """Inline SVG icon. Stroke colour is left to CSS (stroke: currentColor default)."""
    paths = _ICON_PATHS.get(name, "")
    width = 2 if name in ("check", "play") else 1.6
    klass = ' class="%s"' % cls if cls else ""
    return (
        '<svg%s width="%s" height="%s" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="%s" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true" focusable="false">%s</svg>'
        % (klass, size, size, width, paths)
    )


def _rail(active, prefix):
    items = []
    for key, href, label, _tab, ico in NAV:
        cls = "nav-item active" if key == active else "nav-item"
        aria = ' aria-current="page"' if key == active else ""
        items.append(
            '<a class="%s" href="%s%s"%s>%s<span>%s</span></a>'
            % (cls, prefix, href, aria, icon(ico, 16), label)
        )
    return (
        '<nav class="rail" aria-label="Sections">'
        '<div class="rail-mark"><div class="wordmark" lang="grc">%s</div>'
        '<div class="wordmark-sub">%s</div></div>'
        '%s<div class="grow"></div>'
        '<div class="rail-meta"><div>Pronunciation · Erasmian</div>'
        '<div><a href="%s">Vault on GitHub</a></div></div>'
        '</nav>' % (WORDMARK, WORDMARK_SUB, "".join(items), REPO_URL)
    )


def _tabbar(active, prefix):
    tabs = []
    for key, href, _label, tab, ico in NAV:
        cls = "tab active" if key == active else "tab"
        aria = ' aria-current="page"' if key == active else ""
        tabs.append(
            '<a class="%s" href="%s%s"%s>%s<span>%s</span></a>'
            % (cls, prefix, href, aria, icon(ico, 21), tab)
        )
    return '<nav class="tabbar" aria-label="Sections">%s</nav>' % "".join(tabs)


def _masthead():
    return (
        '<header class="masthead">'
        '<div style="display:flex;align-items:baseline;gap:10px">'
        '<div class="wordmark" lang="grc">%s</div>'
        '<div class="wordmark-sub">%s</div></div>'
        '<div class="meta" data-today></div>'
        '</header>' % (WORDMARK, WORDMARK_SUB)
    )


def page_head(title, subtitle="", right=""):
    """Convenience: the standard page header strip used by every page."""
    sub = '<div class="page-sub">%s</div>' % subtitle if subtitle else ""
    rgt = '<div class="page-date">%s</div>' % right if right else ""
    return (
        '<div class="page-head"><div class="page-head-left"><h1>%s</h1>%s</div>%s</div>'
        % (title, sub, rgt)
    )


def _footer(prefix):
    return (
        '<footer class="site-footer">'
        '<div>%s</div>'
        '<div>Built from the <a href="%s">Scriptures vault</a> · '
        '<a href="%sindex.html">Dashboard</a></div>'
        '</footer>' % (FOOTER_LICENSE, REPO_URL, prefix)
    )


def render_page(title, active_nav, body_html, extra_head="", extra_js="", depth=0):
    """Render a full HTML page. See module docstring for the argument contract."""
    if active_nav not in NAV_KEYS and active_nav is not None:
        raise ValueError("active_nav must be one of %s (got %r)" % (NAV_KEYS, active_nav))
    prefix = "../" * int(depth)
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%(title)s · Greek Study</title>\n"
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="%(fonts)s">\n'
        '<link rel="stylesheet" href="%(prefix)sstyle.css">\n'
        "%(extra_head)s\n"
        "</head>\n<body>\n"
        '<div class="layout">\n%(rail)s\n<div>\n%(masthead)s\n'
        '<main class="main">\n%(body)s\n%(footer)s\n</main>\n</div>\n</div>\n'
        "%(tabbar)s\n"
        '<script src="%(prefix)sapp.js"></script>\n'
        "%(extra_js)s\n"
        "</body>\n</html>\n"
    ) % {
        "title": title,
        "fonts": FONTS_HREF,
        "prefix": prefix,
        "extra_head": extra_head,
        "rail": _rail(active_nav, prefix),
        "masthead": _masthead(),
        "body": body_html,
        "footer": _footer(prefix),
        "tabbar": _tabbar(active_nav, prefix),
        "extra_js": extra_js,
    }

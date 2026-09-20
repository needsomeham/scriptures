"""docs/library/index.html + docs/library/<slug>.html (Agent C).

Scans the vault (markdown at repo root), renders every note through
`site/lib/md.py`, and builds the Library section: a searchable index and
one page per note with a frontmatter meta strip, resolved wikilinks,
backlinks and a GitHub source link.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(os.path.dirname(HERE), "lib")
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

import md  # noqa: E402

EXCLUDE_DIRS = {"_templates", "site", "docs", "qa", ".obsidian", ".git"}
EXCLUDE_FILES = {"SPEC.md"}

GUIDE_STEMS = {"readme", "map", "start-here", "learning-path", "progress-log"}

MOC_SLUGS = ["moc-greek-learning", "moc-nt-background", "moc-textual-criticism"]
MOC_TITLES = {
    "moc-greek-learning": "Greek learning",
    "moc-nt-background": "NT background",
    "moc-textual-criticism": "Textual criticism",
}
TYPE_ORDER = ["source", "concept", "bridge", "moc", "guide", "control"]
TYPE_LABEL = {
    "source": "Source", "concept": "Concept", "bridge": "Bridge",
    "moc": "MOC", "guide": "Guide", "control": "Control",
}
CHIPS = [("all", "All"), ("source", "Sources"), ("concept", "Concepts"),
         ("bridge", "Bridges"), ("moc", "MOCs"), ("guide", "Guides")]

REPO_URL = "https://github.com/needsomeham/scriptures/blob/main/"

_ONE_LINE_RE = re.compile(r"\*\*In one line:\*\*\s*(.+)")


def _iter_vault_files(vault_root):
    for root, dirs, files in os.walk(vault_root):
        rel_root = os.path.relpath(root, vault_root)
        parts = [] if rel_root == "." else rel_root.split(os.sep)
        if parts and (parts[0] in EXCLUDE_DIRS or parts[0].startswith(".")):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for name in files:
            if not name.endswith(".md") or name in EXCLUDE_FILES:
                continue
            rel_path = os.path.normpath(os.path.join("" if rel_root == "." else rel_root, name))
            yield rel_path


def _one_line(body):
    m = _ONE_LINE_RE.search(body)
    if m:
        text = m.group(1).strip()
    else:
        # first non-empty paragraph line
        text = ""
        for line in body.split("\n"):
            line = line.strip()
            if line and not line.startswith(("#", "**", "|", ">", "-", "[")):
                text = line
                break
            if line and text == "":
                text = line.lstrip("#*|>- ").strip()
                if text:
                    break
    text = re.sub(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]",
                  lambda m: (m.group(2) or m.group(1)).strip(), text)
    text = re.sub(r"[*_`]", "", text)
    if len(text) > 160:
        text = text[:159].rstrip() + "…"
    return text


def _plain_text(body):
    """Strip markdown-ish syntax to plain text for the search index."""
    t = re.sub(r"```.*?```", " ", body, flags=re.S)
    t = re.sub(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]",
               lambda m: (m.group(2) or m.group(1)), t)
    t = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"[#>*_`|-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _use_in_path(body):
    for key in ("**Use in the path:**", "**Why it matters for reading the NT:**"):
        idx = body.find(key)
        if idx != -1:
            rest = body[idx + len(key):]
            end = rest.find("**")
            return rest[:end if end != -1 else 200].strip()
    return ""


def _load_notes(ctx):
    vault_root = ctx["vault_root"]
    parse_frontmatter = ctx["parse_frontmatter"]
    notes = []
    for rel_path in sorted(_iter_vault_files(vault_root)):
        abs_path = os.path.join(vault_root, rel_path)
        with open(abs_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
        meta, body = parse_frontmatter(raw)
        slug = os.path.splitext(os.path.basename(rel_path))[0]
        stem_lower = slug.lower()

        if stem_lower in GUIDE_STEMS:
            ntype = "guide"
        else:
            ntype = meta.get("type")
            if ntype not in ("source", "concept", "bridge", "moc", "control"):
                top = rel_path.split(os.sep)[0]
                ntype = {"sources": "source", "concepts": "concept",
                         "bridges": "bridge"}.get(top, "concept")

        title = meta.get("title") or slug
        if title.endswith(".md"):
            title = title[:-3]

        tags = meta.get("tags") if isinstance(meta.get("tags"), list) else []

        notes.append({
            "slug": slug,
            "rel_path": rel_path.replace(os.sep, "/"),
            "title": title,
            "type": ntype,
            "tier": meta.get("tier", ""),
            "level": meta.get("level", ""),
            "cost": meta.get("cost", ""),
            "tags": tags,
            "raw": raw,
            "body": body,
        })
    return notes


def _assign_mocs(notes):
    by_slug = {n["slug"]: n for n in notes}
    slug_index = md.build_slug_index(by_slug.keys())
    membership = {}  # slug -> moc slug
    for moc_slug in MOC_SLUGS:
        moc = by_slug.get(moc_slug)
        if not moc:
            continue
        for target in md.extract_wikilink_targets(moc["body"]):
            resolved = md.resolve_wikilink(target, slug_index)
            if resolved and resolved != moc_slug:
                membership.setdefault(resolved, moc_slug)
    for n in notes:
        if n["slug"] in MOC_SLUGS:
            n["moc"] = ""
            continue
        moc = membership.get(n["slug"])
        if not moc:
            if n["slug"].startswith("bg-"):
                moc = "moc-nt-background"
            elif n["slug"].startswith("tc-"):
                moc = "moc-textual-criticism"
            else:
                moc = "moc-greek-learning"
        n["moc"] = moc
    return slug_index


def _backlinks(notes):
    by_slug = {n["slug"]: n for n in notes}
    slug_index = md.build_slug_index(by_slug.keys())
    back = {n["slug"]: [] for n in notes}
    seen = {n["slug"]: set() for n in notes}
    for n in notes:
        for target in md.extract_wikilink_targets(n["body"]):
            resolved = md.resolve_wikilink(target, slug_index)
            if resolved and resolved != n["slug"]:
                if n["slug"] not in seen[resolved]:
                    seen[resolved].add(n["slug"])
                    back[resolved].append(n["slug"])
    for slug, sources in back.items():
        back[slug] = sorted(sources, key=lambda s: by_slug[s]["title"].lower())
    return back


def _meta_strip(note, icon):
    parts = ['<span class="chip" style="cursor:default">%s</span>' % TYPE_LABEL.get(note["type"], note["type"])]
    if note["tier"]:
        parts.append('<span class="chip" style="cursor:default">%s</span>' % note["tier"])
    if note["level"]:
        parts.append('<span class="meta">%s</span>' % note["level"])
    if note["cost"]:
        parts.append('<span class="meta">%s</span>' % note["cost"])
    if note["moc"]:
        parts.append('<a class="meta" href="%s.html">%s</a>'
                      % (note["moc"], MOC_TITLES.get(note["moc"], note["moc"])))
    if note["tags"]:
        parts.append('<span class="meta mid">%s</span>' % ", ".join("#%s" % t for t in note["tags"]))
    return '<div class="segmented" style="align-items:center;gap:10px;flex-wrap:wrap">%s</div>' % "".join(parts)


def _note_page_html(ctx, note, slug_index, backlinks_by_slug):
    shell = ctx["shell"]
    icon = shell.icon
    body_html = md.render(note["body"], slug_index)

    back = backlinks_by_slug.get(note["slug"], [])
    by_slug_lookup = ctx["_by_slug"]
    if back:
        items = "".join(
            '<li><a href="%s.html">%s</a></li>' % (s, by_slug_lookup[s]["title"])
            for s in back
        )
        backlinks_html = (
            '<section class="panel"><div class="label">Linked from</div>'
            '<ul>%s</ul></section>' % items
        )
    else:
        backlinks_html = (
            '<section class="panel"><div class="label">Linked from</div>'
            '<p class="small mid">Nothing in the vault links here yet.</p></section>'
        )

    github_href = REPO_URL + note["rel_path"]
    footer_links = (
        '<div class="segmented" style="gap:12px">'
        '<a class="chip" href="index.html">%s<span>Back to Library</span></a>'
        '<a class="chip" href="%s" target="_blank" rel="noopener">%s<span>Open in vault on GitHub</span></a>'
        '</div>' % (icon("shelf", 14), github_href, icon("box", 14))
    )

    body = (
        shell.page_head(note["title"], TYPE_LABEL.get(note["type"], note["type"]))
        + _meta_strip(note, icon)
        + '<article class="panel note-body">%s</article>' % body_html
        + backlinks_html
        + footer_links
    )
    return ctx["render_page"](note["title"], "library", body,
                              extra_head='<link rel="stylesheet" href="../library.css">', depth=1)


def _moc_tree_html(notes):
    counts = {m: {"total": 0, "source": 0, "concept": 0, "bridge": 0} for m in MOC_SLUGS}
    for n in notes:
        moc = n.get("moc")
        if moc in counts and n["type"] in ("source", "concept", "bridge"):
            counts[moc]["total"] += 1
            counts[moc][n["type"]] += 1
    rows = []
    for moc in MOC_SLUGS:
        c = counts[moc]
        rows.append(
            '<div class="stack" style="gap:7px">'
            '<div style="display:flex;align-items:baseline;justify-content:space-between;gap:10px">'
            '<a href="%s.html" style="font-family:var(--serif);font-size:18px;text-decoration:none">%s</a>'
            '<span class="meta">%d</span></div>'
            '<div class="stack" style="gap:5px;padding-left:12px;border-left:1px solid var(--rule)">'
            '<div style="display:flex;align-items:baseline;justify-content:space-between" class="small mid">'
            '<span>Sources</span><span class="meta">%d</span></div>'
            '<div style="display:flex;align-items:baseline;justify-content:space-between" class="small mid">'
            '<span>Concepts</span><span class="meta">%d</span></div>'
            '<div style="display:flex;align-items:baseline;justify-content:space-between" class="small mid">'
            '<span>Bridges</span><span class="meta">%d</span></div>'
            '</div></div>'
            % (moc, MOC_TITLES[moc], c["total"], c["source"], c["concept"], c["bridge"])
        )
    return (
        '<div class="panel" id="moc-tree">'
        '<div class="panel-head"><div class="label">Maps of content</div>'
        '<div class="meta muted is-hidden" id="moc-caption">(counts show all notes)</div></div>'
        '<div class="stack" style="gap:16px">%s</div>'
        '<div class="grow"></div>'
        '<div class="stack" style="gap:7px;padding-top:14px;border-top:1px solid var(--rule)">'
        '<a class="meta" href="taxonomy.html">Taxonomy</a>'
        '<a class="meta" href="gaps.html">Gap ledger &middot; P1&ndash;P3</a>'
        '</div></div>' % "".join(rows)
    )


def _index_html(ctx, notes, index_json_str):
    shell = ctx["shell"]
    icon = shell.icon

    type_counts = {}
    for n in notes:
        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1
    subtitle = " &middot; ".join(
        "%d %s%s" % (type_counts[t], TYPE_LABEL[t].lower(), "s" if type_counts[t] != 1 else "")
        for t in TYPE_ORDER if type_counts.get(t)
    )

    chips_html = "".join(
        '<button type="button" class="chip%s" data-chip="%s">%s</button>'
        % (" active" if key == "all" else "", key, label)
        for key, label in CHIPS
    )

    search_html = (
        '<div style="display:flex;align-items:center;gap:11px;padding:10px 16px;'
        'background:var(--panel);border:1px solid var(--rule-strong);flex-grow:1">'
        '%s<input id="lib-search" type="search" placeholder="Search %d notes…" '
        'aria-label="Search the library" '
        'style="border:0;background:none;outline:none;flex-grow:1;font:16px var(--ui);color:var(--ink)">'
        '</div>' % (icon("grid", 16), len(notes))
    )
    # search icon: reuse a generic circle via inline svg (not in shell icon set)
    search_icon = (
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="11" cy="11" r="6.5"></circle><path d="m16 16 4.5 4.5"></path></svg>'
    )
    search_html = search_html.replace(icon("grid", 16), search_icon, 1)

    results_html = (
        '<div class="panel" id="lib-results" style="min-height:0">'
        '<div class="panel-head"><div class="label">All notes</div>'
        '<div class="meta" id="lib-result-count">%d notes</div></div>'
        '<div id="lib-list" class="stack" style="gap:2px"></div>'
        '</div>' % len(notes)
    )

    preview_html = (
        '<div class="panel mobile-first is-hidden" id="lib-preview" style="min-height:0">'
        '<div class="panel-head"><div class="label">Preview</div>'
        '<div class="meta" id="lib-preview-path"></div></div>'
        '<div id="lib-preview-body" class="stack" style="gap:14px"></div>'
        '</div>'
    )

    body = (
        shell.page_head("Library", subtitle)
        + '<div class="stack" style="gap:16px">'
        + '<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">%s<div class="segmented">%s</div></div>'
        % (search_html, chips_html)
        + '<div class="cols" id="library-grid" style="grid-template-columns:minmax(0,1fr)">'
        + _moc_tree_html(notes) + results_html + preview_html
        + "</div></div>"
    )

    extra_head = '<link rel="stylesheet" href="../library.css">'
    extra_js = (
        '<script id="library-data" type="application/json">%s</script>\n'
        '<script src="../library.js"></script>' % index_json_str
    )
    return ctx["render_page"]("Library", "library", body, extra_head=extra_head,
                              extra_js=extra_js, depth=1)


def build(ctx):
    out = os.path.join(ctx["out_dir"], "library")
    os.makedirs(out, exist_ok=True)

    notes = _load_notes(ctx)
    slug_index = _assign_mocs(notes)
    backlinks = _backlinks(notes)
    by_slug = {n["slug"]: n for n in notes}
    ctx = dict(ctx)
    ctx["_by_slug"] = by_slug

    written = []

    # per-note pages
    for note in notes:
        html_doc = _note_page_html(ctx, note, slug_index, backlinks)
        path = os.path.join(out, "%s.html" % note["slug"])
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html_doc)
        written.append("library/%s.html" % note["slug"])

    # data files
    index_rows = []
    search_map = {}
    for n in notes:
        one_line = _one_line(n["body"])
        row = {
            "slug": n["slug"], "title": n["title"], "type": n["type"],
            "tier": n["tier"], "level": n["level"], "cost": n["cost"],
            "moc": n["moc"], "one_line": one_line, "tags": n["tags"],
            "url": "library/%s.html" % n["slug"],
            "use_in_path": _use_in_path(n["body"]),
        }
        index_rows.append(row)
        search_text = " ".join([
            n["title"], n["type"], " ".join(n["tags"]), one_line, _plain_text(n["body"]),
        ]).lower()
        search_map[n["slug"]] = search_text

    json = ctx["json"]
    data_dir = ctx["data_dir"]
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "library-index.json"), "w", encoding="utf-8") as fh:
        json.dump(index_rows, fh, ensure_ascii=False, indent=0)
    with open(os.path.join(data_dir, "search.json"), "w", encoding="utf-8") as fh:
        json.dump(search_map, fh, ensure_ascii=False, indent=0)
    written.append("data/library-index.json")
    written.append("data/search.json")

    # index page: embed the same rows plus search_text, so search works from file://
    embedded_rows = []
    for row in index_rows:
        r = dict(row)
        r["search_text"] = search_map[row["slug"]]
        embedded_rows.append(r)
    index_json_str = json.dumps(embedded_rows, ensure_ascii=False)
    # </script> can't appear inside an inline <script> block
    index_json_str = index_json_str.replace("</", "<\\/")

    index_html = _index_html(ctx, notes, index_json_str)
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(index_html)
    written.append("library/index.html")

    ctx["_library_notes"] = notes
    ctx["_library_slug_index"] = slug_index
    return written

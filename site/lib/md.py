"""Small stdlib markdown -> HTML converter for the Scriptures vault (Agent C).

Covers the subset this vault actually uses: headings, paragraphs, bold /
italic, inline code, fenced code, unordered / ordered lists, checkbox list
items (`- [ ]` / `- [x]`), pipe tables, blockquotes, links, horizontal
rules, and Obsidian `[[wikilink]]` / `[[wikilink|alias]]` syntax. Greek
text (Unicode Greek + Greek Extended blocks) passes through untouched
except that runs of two or more Greek letters are wrapped in
`<span lang="grc" class="greek-inline">` for font rendering.

Public API
----------
build_slug_index(slugs) -> dict            lower-stem -> actual slug
extract_wikilink_targets(text) -> [str]    raw targets (no alias, no `#`)
resolve_wikilink(target, slug_index) -> slug or None
render(text, slug_index) -> str            body markdown -> HTML (no frontmatter)
"""

import html
import re

# --- Greek detection -------------------------------------------------------
# Greek block (0370-03FF) + Greek Extended (1F00-1FFF, polytonic combos).
_GREEK_CHAR = "Ͱ-Ͽἀ-῿"
_GREEK_RUN_RE = re.compile("[" + _GREEK_CHAR + "]{2,}")


def _wrap_greek(text):
    """Wrap runs of >=2 Greek letters in a lang=grc span. `text` must not
    contain any HTML tags yet (plain text only) since this is a naive
    substring wrap."""
    return _GREEK_RUN_RE.sub(
        lambda m: '<span lang="grc" class="greek-inline">%s</span>' % m.group(0), text
    )


# --- wikilinks ---------------------------------------------------------------
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")


def build_slug_index(slugs):
    """slugs: iterable of actual output slugs -> {lower-slug: slug}."""
    return {s.lower(): s for s in slugs}


def _stem(target):
    target = target.strip()
    # accept "sources/slug", "concepts/slug", etc: take the last path part.
    if "/" in target:
        target = target.rsplit("/", 1)[-1]
    return target.strip()


def resolve_wikilink(target, slug_index):
    return slug_index.get(_stem(target).lower())


def extract_wikilink_targets(text):
    """Raw wikilink targets found in `text` (frontmatter stripped by caller)."""
    return [m.group(1).strip() for m in _WIKILINK_RE.finditer(text)]


# --- inline rendering --------------------------------------------------------
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)|_([^_\n]+)_")


class _Placeholders:
    """Collects rendered HTML fragments and swaps them for tokens that
    survive the remaining regex passes untouched, then restores them."""

    def __init__(self):
        self._store = []

    def add(self, html_fragment):
        i = len(self._store)
        self._store.append(html_fragment)
        return "\x00P%d\x00" % i

    def restore(self, text):
        for i, frag in enumerate(self._store):
            text = text.replace("\x00P%d\x00" % i, frag)
        return text


def render_inline(text, slug_index):
    """Render one line/paragraph's worth of inline markdown. `text` is raw
    (unescaped) markdown text."""
    escaped = html.escape(text, quote=False)
    ph = _Placeholders()

    # 1. inline code — protect verbatim content from further processing.
    def _code(m):
        return ph.add("<code>%s</code>" % m.group(1))

    escaped = _INLINE_CODE_RE.sub(_code, escaped)

    # 2. wikilinks.
    def _wiki(m):
        target, alias = m.group(1), m.group(2)
        if not target.strip():
            # not a real wikilink (e.g. literal "[[ ]]" critical-apparatus
            # bracket notation used in some textual-criticism notes) —
            # pass the original text through unchanged.
            return m.group(0)
        display = (alias or target).strip()
        display = _wrap_greek(display)
        slug = resolve_wikilink(html.unescape(target), slug_index)
        if slug:
            return ph.add('<a href="%s.html">%s</a>' % (slug, display))
        return ph.add('<span class="missing">%s</span>' % display)

    escaped = _WIKILINK_RE.sub(_wiki, escaped)

    # 3. markdown links [text](url).
    def _link(m):
        label, url = m.group(1), m.group(2)
        label = _wrap_greek(label) if label else url
        attrs = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
        return ph.add('<a href="%s"%s>%s</a>' % (url, attrs, label))

    escaped = _MD_LINK_RE.sub(_link, escaped)

    # 4. bold / italic.
    escaped = _BOLD_RE.sub(lambda m: "<strong>%s</strong>" % m.group(1), escaped)
    escaped = _ITALIC_RE.sub(
        lambda m: "<em>%s</em>" % (m.group(1) or m.group(2)), escaped
    )

    # 5. Greek runs in the remaining plain text (placeholders are opaque).
    escaped = _wrap_greek(escaped)

    return ph.restore(escaped)


# --- block rendering ----------------------------------------------------------
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_HR_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})\s*$")
_UL_RE = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_OL_RE = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
_CHECKBOX_RE = re.compile(r"^\[( |x|X)\]\s+(.*)$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
_BLOCKQUOTE_RE = re.compile(r"^>\s?(.*)$")
_FENCE_RE = re.compile(r"^```")
# A line opening with a bold "**Label:**" field marker (this vault's note
# templates use these as one-per-line pseudo-fields, e.g. "**In one
# line:**", "**Use in the path:**") starts its own paragraph rather than
# folding into the previous line.
_FIELD_LABEL_RE = re.compile(r"^\*\*[^*\n]+:\*\*")


def _split_table_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render(text, slug_index):
    lines = text.split("\n")
    out = []
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        # fenced code block
        if _FENCE_RE.match(line):
            i += 1
            code_lines = []
            while i < n and not _FENCE_RE.match(lines[i]):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            out.append(
                "<pre><code>%s</code></pre>"
                % html.escape("\n".join(code_lines), quote=False)
            )
            continue

        # horizontal rule
        if _HR_RE.match(line):
            out.append("<hr>")
            i += 1
            continue

        # heading
        m = _HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            out.append(
                "<h%d>%s</h%d>" % (level, render_inline(m.group(2), slug_index), level)
            )
            i += 1
            continue

        # blockquote
        if _BLOCKQUOTE_RE.match(line):
            quote_lines = []
            while i < n and _BLOCKQUOTE_RE.match(lines[i]):
                quote_lines.append(_BLOCKQUOTE_RE.match(lines[i]).group(1))
                i += 1
            inner = render("\n".join(quote_lines), slug_index)
            out.append("<blockquote>%s</blockquote>" % inner)
            continue

        # table: a row followed by a separator row
        if "|" in line and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1] or ""):
            header = _split_table_row(line)
            i += 2
            body_rows = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                body_rows.append(_split_table_row(lines[i]))
                i += 1
            thead = "".join(
                "<th>%s</th>" % render_inline(c, slug_index) for c in header
            )
            trs = []
            for row in body_rows:
                tds = "".join(
                    "<td>%s</td>" % render_inline(c, slug_index) for c in row
                )
                trs.append("<tr>%s</tr>" % tds)
            out.append(
                "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>"
                % (thead, "".join(trs))
            )
            continue

        # lists (unordered / ordered / checkbox), single-level
        ul_m, ol_m = _UL_RE.match(line), _OL_RE.match(line)
        if ul_m or ol_m:
            ordered = bool(ol_m)
            items = []
            while i < n:
                m2 = _OL_RE.match(lines[i]) if ordered else _UL_RE.match(lines[i])
                if not m2:
                    break
                content = m2.group(2)
                cb = _CHECKBOX_RE.match(content)
                if cb:
                    checked = cb.group(1).lower() == "x"
                    items.append(
                        '<li class="task"><input type="checkbox" disabled%s> %s</li>'
                        % (" checked" if checked else "", render_inline(cb.group(2), slug_index))
                    )
                else:
                    items.append("<li>%s</li>" % render_inline(content, slug_index))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join(items), tag))
            continue

        # paragraph: gather until blank line or next block-start
        para_lines = [line]
        i += 1
        while i < n and lines[i].strip() and not (
            _HEADING_RE.match(lines[i])
            or _HR_RE.match(lines[i])
            or _BLOCKQUOTE_RE.match(lines[i])
            or _UL_RE.match(lines[i])
            or _OL_RE.match(lines[i])
            or _FENCE_RE.match(lines[i])
            or _FIELD_LABEL_RE.match(lines[i])
            or ("|" in lines[i] and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1] or ""))
        ):
            para_lines.append(lines[i])
            i += 1
        out.append("<p>%s</p>" % render_inline(" ".join(para_lines), slug_index))

    return "\n".join(out)

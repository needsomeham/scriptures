#!/usr/bin/env python3
"""Build the Greek Study site: site/ (sources) -> docs/ (GitHub Pages output).

Run from anywhere:  python3 site/build.py
Stdlib only. Idempotent: docs/ is deleted and rebuilt on every run.
Never hand-edit docs/ — everything there is generated.
"""

import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.dirname(HERE)
STATIC_DIR = os.path.join(HERE, "static")
OUT_DIR = os.path.join(VAULT_ROOT, "docs")

# site/ must be importable as a package root so `from pages import ...` works.
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from templates import shell  # noqa: E402
from pages import alphabet, course, dashboard, library, reading  # noqa: E402

PAGE_MODULES = [
    ("dashboard", dashboard),
    ("course", course),
    ("alphabet", alphabet),
    ("reading", reading),
    ("library", library),
]


# --- tiny frontmatter parser (stdlib only; no pyyaml) -----------------------
def parse_frontmatter(text):
    """Split a note into (frontmatter dict, body str).

    Handles the flat `key: value` and `key: [a, b]` frontmatter this vault
    uses. Values are strings or lists of strings; quotes are stripped.
    Exposed on ctx so page modules do not each reinvent it.
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    meta = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [v.strip().strip("\"'") for v in inner.split(",") if v.strip()] \
                if inner else []
        else:
            meta[key] = value.strip("\"'")
    return meta, "\n".join(lines[end + 1:]).lstrip("\n")


# --- build steps ------------------------------------------------------------
def clean_out():
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)


def copy_static():
    """site/static/* -> docs/*  (style.css, app.js at the root; data/ under docs/data/)."""
    copied = []
    if not os.path.isdir(STATIC_DIR):
        return copied
    for root, dirs, files in os.walk(STATIC_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        rel = os.path.relpath(root, STATIC_DIR)
        target = OUT_DIR if rel == "." else os.path.join(OUT_DIR, rel)
        os.makedirs(target, exist_ok=True)
        for name in files:
            if name.startswith("."):
                continue
            shutil.copy2(os.path.join(root, name), os.path.join(target, name))
            copied.append(os.path.normpath(os.path.join("" if rel == "." else rel, name)))
    return copied


def write_404(ctx):
    body = (
        shell.page_head("Not here", "404")
        + '<section class="panel"><div class="label">Missing page</div>'
        '<p class="small mid">That page does not exist in this build. '
        'The dashboard is the way back in.</p>'
        '<a class="btn btn-secondary" href="index.html" style="align-self:flex-start">'
        '%s<span>Go to the Dashboard</span></a></section>' % shell.icon("grid", 15)
    )
    html = ctx["render_page"]("Not found", None, body)
    with open(os.path.join(OUT_DIR, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    return ["404.html"]


def main():
    started = time.time()
    clean_out()
    static_files = copy_static()

    ctx = {
        "vault_root": VAULT_ROOT,
        "out_dir": OUT_DIR,
        "data_dir": os.path.join(OUT_DIR, "data"),
        "render_page": shell.render_page,
        "shell": shell,
        "parse_frontmatter": parse_frontmatter,
        "json": json,
    }

    written = []
    for name, module in PAGE_MODULES:
        result = module.build(ctx)
        written.extend(result or [])
        print("  %-10s %s" % (name, ", ".join(result or [])))

    written.extend(write_404(ctx))

    # GitHub Pages: do not run Jekyll over docs/.
    with open(os.path.join(OUT_DIR, ".nojekyll"), "w", encoding="utf-8") as fh:
        fh.write("")

    print("  static     %d file(s)" % len(static_files))
    print("built %d page file(s) into %s in %.2fs"
          % (len(written), os.path.relpath(OUT_DIR, os.getcwd()), time.time() - started))


if __name__ == "__main__":
    main()

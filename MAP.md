---
title: MAP.md
type: moc
tags: [map, control]
created: 2026-09-14
sources: []
---
# Map of the vault

Entry point for any new session. Read this file first; do not read
whole folders — go deeper by grep or `[[wikilink]]` lookup only (see
`[[CLAUDE]]` reading protocol).

## Reading order for a new session
1. `README.md` — one paragraph, what this vault is.
2. This file (`MAP.md`).
3. `[[start-here]]` — Jacob's concrete day-by-day Stage 0 on-ramp.
4. `[[learning-path]]` — where Jacob actually is and what's next.
5. Whichever MOC matches the question at hand (below) — read only that
   one, plus at most 2-3 linked notes.
Consult `[[CLAUDE]]` (binding rules) if you haven't internalized them yet,
and `_control/taxonomy.md` / `_control/gaps.md` by grep — not start to
end — to check coverage or open questions.

## The three domains (MOCs)
- **[[moc-greek-learning]]** — Koine Greek: alphabet/pronunciation,
  morphology, syntax, vocabulary, readers, lexicons, tools, courses.
- **[[moc-nt-background]]** — Second Temple Judaism, Greco-Roman world,
  genre, authorship/dating, LXX, social world, Jewish literature.
- **[[moc-textual-criticism]]** — manuscripts, critical editions,
  apparatus, major variants, method, canon formation.

Each MOC links to every `sources/`, `concepts/`, and `bridges/` note in
its domain, and stays ≤8KB. If a MOC is missing a note that belongs to
it, that's a Stitch-agent task, not something to patch ad hoc.

## Curriculum
- **[[start-here]]** — Jacob's concrete Stage 0 on-ramp: pronunciation
  choice, tool setup, day-by-day Weeks 1–2 plan.
- **[[progress-log]]** — lightweight stage-readiness checklist and
  reading log; tells you where Jacob actually is right now.
- **[[learning-path]]** — the actionable Greek curriculum: stages,
  weekly loop, resources by stage. This is what changes most often as
  the vault grows.
- `bridges/` — passage-level "how this Greek/TC/background fact changes
  the reading" notes, e.g. [[1-john-1-1-4-first-reading]]. Linked from
  the relevant MOC(s), not read as a folder.

## Control files (`_control/`)
- **[[_control/taxonomy]]** — domain outline of what the vault should
  eventually cover; `[ ]` = uncovered, ticked as notes land.
- **[[_control/gaps]]** — open questions / missing coverage, P1–P3.
- `_control/references-greek.md`, `_control/references-background.md`,
  `_control/references-textual.md` — sharded bibliographies (ref IDs
  like `[G-03]`, `[B-12]`, `[T-05]`). Grep for a specific ID; never
  read a shard end-to-end.
- `_control/ops-device-shell.md` — Cowork `device_bash` mount outage
  (Windows KB), workaround, and status; grep by lookup only.

## Note counts (as of 2026-09-14 stitch)
| Domain | Sources | Concepts | Bridges |
|---|---|---|---|
| Greek learning | 25 | 1 | 1 |
| NT background | 20 | 8 | 0 |
| Textual criticism | 16 | 7 | 0 |
| **Total** | **61** | **16** | **1** |

Bridges are just starting — [[1-john-1-1-4-first-reading]] is the first
application note, done early as a Stage 0 preview; the rest arrive once
Jacob is reading enough Greek for passage-level notes at Stage 2+ of
[[learning-path]].

## Content folders
- `sources/<slug>.md` — one note per resource (book, course, site,
  tool, dataset). Tiered T1/T2/T2b/T3.
- `concepts/<slug>.md` — one idea per note (e.g. verbal-aspect,
  second-temple-judaism). Pure research, no application.
- `bridges/<slug>.md` — how a concept changes how a passage is read.
  Kept separate from pure research.

Do not enumerate these folders by directory listing to "see what's
there" — use `[[wikilinks]]` from the MOCs, or grep for a slug/topic.

## How to add a note (mini-procedure)
1. Pick the right template: `_templates/source.md`, `concept.md`, or
   `bridge.md` — copy it exactly, don't improvise fields.
2. Fill frontmatter: `title, type, tags, tier (sources only), created
   (YYYY-MM-DD), sources (ref IDs)`.
3. Write the note within its size budget (source ≤3KB, concept ≤4KB,
   bridge ≤3KB). Synopsize; quote ≤2 sentences max.
4. Label any load-bearing scholarly claim on the claim ladder; add a
   textual-confidence line for text-critical claims.
5. Add ref IDs to the matching `_control/references-*.md` shard if the
   source is new (append a row; don't rewrite the shard).
6. Link the note to its MOC. Do **not** edit the MOC yourself unless
   you are the Stitch agent for this wave — leave that link-back to
   Stitch, or note it in `_control/gaps.md` if it's blocking.
7. If anything couldn't be verified or is contested, log it in
   `_control/gaps.md` with a priority.
8. Never touch another agent's in-progress shard or another domain's
   `sources/`/`concepts/` files in the same wave — stay in your lane.

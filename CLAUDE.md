---
title: CLAUDE.md
type: control
tags: [governance]
created: 2026-09-14
sources: []
---
# Vault rules — read this first

**The vault is the durable product.** Not chat transcripts, not this
session's memory — the markdown files under this root. Every wave of
work must leave the vault more complete and still internally consistent
than it found it. If a fact or note isn't written here, it doesn't exist
for the next agent or for Jacob.

## Mission
Help Jacob reach an accurate, contextually grounded understanding of the
New Testament from the Greek source text. Phase 1: learn Koine Greek in
context (reading-first + video-driven, beginner→intermediate), plus NT
historical background and textual criticism. **Lens:** broadly academic /
non-sectarian — where traditions diverge, say so neutrally, never
advocate. Far-off goal (out of scope now): a Greek→English scripture LLM;
note open datasets if you meet them.

## Layout
```
CLAUDE.md, MAP.md, learning-path.md        root governance + curriculum
_templates/source.md|concept.md|bridge.md  note templates
_control/references-{greek,background,textual}.md   sharded bibliography (≤30KB each)
_control/gaps.md, _control/taxonomy.md     open questions, domain coverage
moc-greek-learning.md, moc-nt-background.md, moc-textual-criticism.md
sources/<slug>.md    concepts/<slug>.md    bridges/<slug>.md
```
Slugs: lowercase-kebab, no dates. Every note has frontmatter: `title,
type (source|concept|bridge|moc|control), tags, tier (sources only),
created (YYYY-MM-DD), sources (ref IDs)`.

## Source tiers
- **T1:** academic press monographs, peer-reviewed journals (JBL, NTS,
  NovT, JSNT), reference works (BDAG, LSJ, NA28/UBS5 apparatus, Metzger),
  critical editions (NA28, SBLGNT, THGNT).
- **T2:** seminary-level textbooks/grammars (Mounce, Croy, Decker,
  Wallace, Funk, Runge), reputable readers.
- **T2b:** established open tools/courses with named scholars (Daily
  Dose of Greek, Perseus, STEP Bible, BLC, Logeion, university OCW,
  Mounce's site) — terminal for tools/courses only.
- **T3:** Wikipedia, blogs, forums, uncredentialed YouTube — orient
  only, never terminal. May point to T1/T2; load-bearing claims must
  cite T1/T2.
- **Banned:** SEO farms, uncited listicles, affiliate "top 10" pages,
  vendor-only sourcing for claims about the vendor's own quality.

## Claim ladder (mandatory on load-bearing scholarly claims)
`consensus` → `majority view` → `contested` → `minority view` →
`speculative`. Text-critical claims also carry a **textual confidence**
line (e.g. "UBS5 rating {A}", "NA28 bracketed", "no significant
variants"). Never present a contested view as settled; name at least one
dissenting scholar/school for anything below `consensus`.

## Method rules
1. Synopsize, never republish — no verbatim dumps; quote ≤2 sentences.
2. Text-native only — no bulk PDF ingestion; PDF-only sources are
   `status: queued`, catalogued via what secondary sources say.
3. Every source note answers: what it is, who made it (credentials),
   what it's for in *this* path, level, cost/access, strengths,
   weaknesses, connections (wikilinks).
4. Pure research first — concept notes describe scholarship on its own
   terms; application/reading-practice goes only in `bridges/`.
5. Divergence rule — name traditions and cite a representative from
   each; no filter, no advocacy.
6. Size budgets — source ≤3KB, concept ≤4KB, bridge ≤5KB (Greek text
   is 2 bytes/char; quote the passage once, keep prose ≤3KB), MOC ≤8KB,
   bibliography shard ≤30KB, root files as marked above. Condense
   before appending; never let a file grow past budget.
7. Link integrity — no broken `[[wikilinks]]` ship. Every note links to
   its MOC; every MOC links to every note in its domain.
8. Gap ledger — anything unverified, unfound, or contested goes in
   `_control/gaps.md` with priority P1 (blocks learning) / P2 (matters)
   / P3 (nice-to-have).
9. Citations in-note — ref IDs like `[G-03]`, `[B-12]`, `[T-05]` resolve
   to rows in the matching `_control/references-*.md` shard.

## Reading protocol (binding on every agent, every session)
1. **Open `MAP.md` first.** It is the entry point and reading order.
2. **Go deeper only by lookup** — grep for a term/slug, or follow a
   `[[wikilink]]` — never by reading a whole folder (`sources/`,
   `concepts/`, `bridges/`) end-to-end.
3. **Never read a `references-*.md` shard end-to-end.** Grep for the
   specific ref ID you need.
4. **Read at most the 3 most relevant notes** for any given question
   before answering or acting. If that isn't enough, grep further —
   don't broaden by reading more whole notes.
5. Consult `_control/taxonomy.md` and `_control/gaps.md` by lookup, not
   cover-to-cover, when deciding what to work on next.

## Research loop (per wave)
**Survey** (tiered web search) → **Digest** (researcher writes
source/concept notes to a disjoint manifest — never touches `MAP.md`,
MOCs, or another agent's shard) → **Stitch** (one synthesis agent builds
MOCs, `learning-path.md`, taxonomy, gaps; verifies links and sizes) →
**Architect review**.
Stop criterion per wave: every taxonomy line has ≥1 note, and a fresh
search resurfaces ≥70% of already-catalogued resources.

General rule: researchers write only to their own manifest within
`sources/`, `concepts/`, and `_control/references-*.md` — never touch
another researcher's shard, another domain's notes, `MAP.md`, a MOC,
`learning-path.md`, `_control/taxonomy.md`, or `_control/gaps.md`. Only
the Stitch agent edits MOCs, `MAP.md`, `learning-path.md`,
`_control/taxonomy.md`, and `_control/gaps.md`.

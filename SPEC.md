# Scriptures Vault — Architect Spec (v1)

All agents working in this vault follow this file. It is the contract. Vault root: `/home/claude/scriptures-vault/` (later committed to the user's `Scriptures` folder; Obsidian-compatible markdown with `[[wikilinks]]`).

## Mission
Help Jacob reach an accurate, contextually grounded understanding of the New Testament from the Greek source text. Phase 1 = learn Koine Greek in context (reading-first + video-driven, beginner→intermediate), plus NT historical background and textual criticism. Lens: broadly academic / non-sectarian; where traditions diverge, say so neutrally. Far-off goal: a Greek→English scripture LLM (not in scope now, but note open datasets when met).

## Layout
```
CLAUDE.md               binding rules for any agent opening the vault (≤ 6 KB)
MAP.md                  map of content + reading order (≤ 6 KB)
learning-path.md        the actionable Greek curriculum (stages, weekly loop, resources by stage)
_templates/source.md, concept.md, bridge.md
_control/references-greek.md | references-background.md | references-textual.md   (sharded bibliography, ≤ 30 KB each)
_control/gaps.md        open questions / missing coverage, P1–P3
_control/taxonomy.md    domain outline; every line should eventually have ≥1 note
moc-greek-learning.md, moc-nt-background.md, moc-textual-criticism.md   (hub notes)
sources/<slug>.md       one note per resource (book, course, site, tool, dataset)
concepts/<slug>.md      one idea per note (e.g. verbal-aspect, second-temple-judaism)
bridges/<slug>.md       application notes (how a concept changes how a passage is read); kept separate from pure research
```
Slugs: lowercase-kebab, no dates. Frontmatter on every note: `title, type (source|concept|bridge|moc|control), tags, tier (sources only), created (YYYY-MM-DD), sources (ref IDs)`.

## Source tiers (adapted from LME)
- **T1 (terminal):** university/academic press monographs, peer-reviewed journals (JBL, NTS, NovT, JSNT), standard reference works (BDAG, LSJ, NA28/UBS5 apparatus, Metzger's Textual Commentary), critical editions (NA28, SBLGNT, THGNT).
- **T2 (terminal):** standard seminary-level textbooks and grammars (Mounce, Croy, Decker, Wallace, Funk, Runge), reputable readers.
- **T2b (terminal for tools/courses):** established open tools and courses with named scholars (Daily Dose of Greek, Perseus, STEP Bible, Biblical Language Center, Logeion, university open courseware, Bill Mounce's site).
- **T3 (orient only, never terminal):** Wikipedia, blogs, forum threads, YouTube channels without named credentials. May point to T1/T2; load-bearing claims must cite T1/T2.
- **Banned:** SEO farms, uncited listicles, "top 10 best Greek courses" affiliate pages, vendor pages as the only source for a claim about the vendor's quality.

## Claim ladder (mandatory label on any load-bearing scholarly claim)
`consensus` → `majority view` → `contested` → `minority view` → `speculative`. Text-critical claims additionally carry a **textual confidence** line (e.g., "UBS5 rating {A}", "NA28 bracketed", "no significant variants"). Never present a contested view as settled; name at least one dissenting scholar/school for anything below `consensus`.

## Method rules
1. **Synopsize, never republish.** No verbatim dumps of sources. Quote ≤ 2 sentences when a wording matters.
2. **Text-native only.** No bulk PDF ingestion. If a source is PDF-only, catalog it `status: queued` with what secondary sources say about it.
3. **Every source note answers:** what it is, who made it (credentials), what it's for in *this* learner's path, level (beginner/intermediate/advanced), cost/access, strengths, weaknesses, and how it connects (wikilinks).
4. **Pure research first.** Concept notes describe scholarship on its own terms; application goes in `bridges/`.
5. **Divergence rule.** Where confessional traditions read a text differently, name the traditions and cite a representative from each; no filter, no advocacy.
6. **Size budgets.** source note ≤ 3 KB, concept ≤ 4 KB, bridge ≤ 5 KB (quoted Greek passage excluded from the ≤ 3 KB prose target), MOC ≤ 8 KB, bibliography shard ≤ 30 KB, root files as above. Condense before appending.
7. **Link integrity.** No broken `[[wikilinks]]` ship. Every note links to its MOC; every MOC links to every note in its domain.
8. **Gap ledger.** Anything you couldn't verify, couldn't find, or found contested goes in `_control/gaps.md` with a priority (P1 blocks learning; P2 matters; P3 nice-to-have).
9. **Citations in-note.** Ref IDs like `[G-03]`, `[B-12]`, `[T-05]` resolve to rows in the matching references shard; each row: ID | author/creator | title | year | type | tier | URL | one-line why-it-matters.

## Research loop (per wave)
Survey (web search, tiered) → Digest (researcher writes source/concept notes to a disjoint manifest — never touches MAP.md, MOCs, or another shard) → Stitch (one synthesis agent builds MOCs, learning-path, taxonomy, gaps; verifies links and sizes) → Architect review.
Stop criterion for a wave: each taxonomy line has ≥1 note, and a fresh search resurfaces ≥70% of already-catalogued resources.

## Templates
### source.md
```
---
title: 
type: source
tags: []
tier: T1|T2|T2b|T3
level: beginner|intermediate|advanced|reference
cost: free|paid (approx price)|mixed
created: 
sources: [ref-id]
---
**In one line:** 
**What it is:** (2–4 sentences; creator + credentials)
**Use in the path:** (which stage of [[learning-path]] it serves; how to use it, e.g. "read alongside 1 John")
**Strengths:** 
**Weaknesses / cautions:** 
**Claims to note:** (any scholarly claims the resource makes, with claim-ladder label)
**Links:** [[moc-...]] · related sources/concepts
```
### concept.md
```
---
title: 
type: concept
tags: []
created: 
sources: [ref-ids]
---
**In one line:** 
**What it is:** 
**Why it matters for reading the NT:** 
**State of scholarship:** (claim-ladder label; dissenting views named)
**Where it breaks / cautions:** 
**Links:** [[moc-...]] · [[related]]
```
### bridge.md
```
---
title: 
type: bridge
tags: []
created: 
sources: [ref-ids]
---
**Passage(s):** 
**Concept applied:** [[concept]]
**How the Greek changes the reading:** 
**Traditions' readings (if divergent):** 
**Confidence:** (claim-ladder + textual confidence)
**Links:** 
```

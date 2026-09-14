---
title: Open Greek NT Datasets (MorphGNT, SBLGNT, OpenGNT, Nestle 1904)
type: source
tags: [dataset, open-data, far-off-goal]
tier: T2b
level: reference
cost: free (open licenses; see each repo for terms)
created: 2026-09-14
sources: [G-24]
---
**In one line:** A cluster of freely licensed, machine-readable Greek NT texts with morphological tagging — the raw material for the far-off Greek→English scripture LLM goal, not a learning resource per se.
**What it is:** **SBLGNT** (Society of Biblical Literature Greek New Testament, ed. Michael Holmes, freely downloadable text with its own license terms restricting some derivative uses); **MorphGNT** (github.com/morphgnt — morphological tagging of the SBLGNT text, maintained by James Tauber and collaborators, pip-installable); **Nestle 1904** (public-domain earlier Nestle text, tagged and packaged similarly, e.g. github.com/biblicalhumanities/py-nestle1904); **OpenGNT** (a community-compiled open Greek NT with lemma/morphology/lexicon links). All are text-native, structured data, not PDFs.
**Use in the path:** Not part of the Stage 1–4 learning curriculum — catalogued for the project's far-off Greek→English LLM goal per SPEC. Worth knowing about now mainly because MorphGNT's tagging conventions are a good, free way to spot-check a parsing you're unsure of once past Stage 2.
**Strengths:** Genuinely open (mostly permissive licenses, though SBLGNT itself has usage restrictions — check before redistributing), actively maintained on GitHub, morphology tags are transparent and documented.
**Weaknesses / cautions:** SBLGNT text license restricts commercial/derivative redistribution in some cases — verify current license terms before any downstream LLM use; Nestle 1904 is an older critical text than NA28/UBS5 and should not be treated as the current scholarly consensus text.
**Claims to note:** none load-bearing; catalog entry for future tooling, not for interpretive claims.
**Links:** [[moc-greek-learning]] · [[moc-textual-criticism]] · [[perseus-digital-library]]

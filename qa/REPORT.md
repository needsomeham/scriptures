# QA Report — Scriptures Vault static site

Date: 2026-09-20
Build: `python3 site/build.py` — **clean**, 103 page files built into `docs/` in 0.06s, no errors or warnings.

Served for testing at `http://localhost:8765/scriptures/...` via `python3 -m http.server 8765 --directory /tmp/qa-root`, with `/tmp/qa-root/scriptures` symlinked to `docs/`, to mimic the `/scriptures/` GitHub Pages subpath. Playwright (Chromium, `/opt/pw-browsers/chromium`) drove the checks. Server was killed at the end of the run.

**Environment caveat:** this sandbox has no network egress to `fonts.googleapis.com`, so every page logs one console error (`net::ERR_TUNNEL_CONNECTION_FAILED` fetching the Gentium Plus / IBM Plex Sans stylesheet) and renders with the fallback font stack (`Iowan Old Style, Georgia, serif` / system UI sans). This is **not counted as a page defect** below — it is a property of this offline test environment, not of the site — but it did serve as a real test of the fallback-font requirement in the spec ("Gentium loaded or fallback readable"): Greek text stayed fully legible in every screenshot on the fallback stack, so that gate is satisfied either way. On real GitHub Pages with normal internet access this request will succeed and produce zero console errors.

## 1. Page × viewport matrix

All pages loaded successfully (no navigation errors), had no console errors beyond the Google Fonts issue above, and had no horizontal scroll at 390px (`document.documentElement.scrollWidth <= innerWidth` held exactly, `scrollWidth == innerWidth` in every case).

| Page | 1440 loads | 1440 no console errors* | 1440 no h-scroll | 390 loads | 390 no console errors* | 390 no h-scroll |
|---|---|---|---|---|---|---|
| index.html | PASS | PASS | PASS | PASS | PASS | PASS |
| course.html | PASS | PASS | PASS | PASS | PASS | PASS |
| alphabet.html | PASS | PASS | PASS | PASS | PASS | PASS |
| reading.html | PASS | PASS | PASS | PASS | PASS | PASS |
| library/index.html | PASS | PASS | PASS | PASS | PASS | PASS |
| library/decker-reading-koine-greek.html | PASS | PASS | PASS | PASS | PASS | PASS |
| library/1-john-1-1-4-first-reading.html | PASS | PASS | PASS | PASS | PASS | PASS |
| 404.html | PASS | PASS | PASS | PASS | PASS | PASS |

\* excluding the sandbox-only Google Fonts network error explained above; no other console errors, warnings, page errors, or failed local requests were observed on any page/viewport.

`<title>` present and non-empty, `<html lang="en">` present, and `lang="grc"` spans present (counts: index 3, course 2, alphabet 31, reading 21, library/index 2, library/decker 2, library/1-john-1-1-4 98, 404 2) on every page.

## 2. Interaction results

- **Alphabet quiz** (click "Quiz", answer question 1): worked at both 390 and 1440. Answer buttons correctly disabled after answering, correct option highlighted, wrong option marked, explanatory feedback text shown (e.g. "No — ι is iota…"), pips/progress updated. No console errors.
- **Reading Room, click ἑωράκαμεν** (v.1): worked at both 390 and 1440. The word button was found and clicked; the parse card populated correctly — Lemma ὁράω, Parse "perfect active indicative, 1st plural", Gloss "we have seen", the bridge-note callout, MorphGNT code, and the STEP Bible / Logeion links. Word highlighted as active in the passage.
- **Library search "aspect"** (1440): worked. Search box filtered "ALL NOTES" to "10 of 93 notes" including relevant hits (e.g. "Reading Koine Greek (Decker)" — "an aspect-first (not tense-first) account of the verb"). Note: the "MAPS OF CONTENT" summary counts (Greek learning 27 / NT background 28 / Textual criticism 23, and the header "61 sources · 16 concepts · 1 bridge · 3 mocs · 5 guides · 7 controls") do not update with the search filter — see defect list, item 2.
- **Course, tick Day 1** (1440): worked — row shows checked/struck-through state, "1 done · 13 left" updates, Stage 0 progress reads "1 of 14 days". **Reload of index.html in the same browser context** confirmed the dashboard picks up the change from `localStorage`: "STREAK 1 days", "STAGE 0 1 of 14 days", "STAGE 0 CHECKLIST 6 of 7 left" (Day 1 no longer in the remaining list), "NEXT ACTION → Day 2". Cross-page state persistence via Progress/localStorage confirmed working correctly.

## 3. Link check

Static scan of every `href`/`src` in `docs/**/*.html` (non-`http(s)`, non-`mailto`/`tel`, non-`#`-only) resolved against the filesystem.

- Files scanned: **99**
- Local links/srcs checked: **2,873**
- Broken: **0**
- Absolute (`/…`) links found: **0** (spec requires relative-only for GH Pages subpath serving — confirmed none present)

No unresolved `[[wikilink]]`s were found either (a search for a `.missing` class across `docs/library/*.html` returned 0 matches), consistent with the 0 broken-link result — the vault's wikilinks all currently resolve, so the "render as `.missing` rather than a dead link" fallback path exists in `site/lib/md.py` but isn't exercised by the current content.

## 4. Basics / accessibility gates

- `<title>`: present and non-empty on all 99 built pages.
- `<html lang="en">`: present on all 99 pages (0 missing, 0 with wrong value).
- `lang="grc"` on Greek spans: present wherever Greek text appears (see per-page counts above).
- `<img>` alt text: 0 images missing `alt` across all 99 pages.
- **Focus ring, tab through 5 elements on index.html**: all 5 focusable elements (nav links: Dashboard, Course, Alphabet, Reading Room, Library) showed a clearly visible focus indicator — computed `outline: 2px solid rgb(138, 106, 51)` on each (warm brown, good contrast against the cream background). PASS.

## Defects found

None are blocking. Listed most to least notable:

1. **(Informational, not a defect) Full-page Playwright screenshots at 390px show the fixed bottom tab bar "floating" mid-page over content** (visible in `alphabet-390.png` / `alphabet-quiz-390.png` near the Diacritics section). This is a known artifact of how headless Chromium composites `position: fixed` elements into a `fullPage` screenshot — it is **not a real rendering bug**. Verified directly with a normal (non-full-page) viewport screenshot scrolled to that section: the tab bar is correctly pinned to the bottom of the viewport with no overlap, and the page has correct bottom padding so the last content ("Text: SBLGNT…" footer) is fully visible above the bar. No fix needed; noted only so a future QA pass doesn't misread the full-page captures.

2. **`site/pages/library.py` / `site/static/library.js`** (file: `site/static/library.js`, area: search) — the "MAPS OF CONTENT" summary panel (per-domain note counts) and the top header counts ("61 sources · 16 concepts · 1 bridge · 3 mocs · 5 guides · 7 controls") do not update when a search query is entered, while the "ALL NOTES" list below correctly filters to "10 of 93 notes". This may be intentional (the MOC panel is meant as a static overview, not a search result), but flagging for confirmation since a user could read the unchanged big numbers as meaning the search didn't filter anything. Suggested fix (if judged worth changing): either hide/gray the MOC summary panel when a search query is active, or add a small "(unfiltered)" label to it.

3. No other defects found. Build is clean, all links resolve, no console errors beyond the environment's blocked external font fetch, no horizontal scroll at mobile width, and all interactive features (quiz, reading-room parse card, library search, course-day checkbox → dashboard sync) work correctly on both viewports.

## Screenshots

All 23 screenshots saved to `/home/claude/scriptures-vault/qa/screens/`:

- `index-1440.png`, `index-390.png`
- `course-1440.png`, `course-390.png`
- `alphabet-1440.png`, `alphabet-390.png`
- `reading-1440.png`, `reading-390.png`
- `library_index-1440.png`, `library_index-390.png`
- `library_decker-reading-koine-greek-1440.png`, `library_decker-reading-koine-greek-390.png`
- `library_1-john-1-1-4-first-reading-1440.png`, `library_1-john-1-1-4-first-reading-390.png`
- `404-1440.png`, `404-390.png`
- `alphabet-quiz-1440.png`, `alphabet-quiz-390.png` (interaction)
- `reading-word-1440.png`, `reading-word-390.png` (interaction)
- `library-search-1440.png` (interaction)
- `course-day1-1440.png` (interaction)
- `index-after-day1-1440.png` (interaction, dashboard reflects Day 1 checked)

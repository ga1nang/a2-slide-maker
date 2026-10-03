# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single self-contained HTML slide deck for a **German A2 oral exam presentation about Cologne**.
Not an app — there is no build step, no package manager, no tests. Open `index.html` in a browser
and it runs.

The full spoken script (not published, it contains other people's text) is the and the single source of truth for content.
The slides deliberately show only short German keywords and numbers; the speaker says the full
sentences.

**The authority runs one way: script → slides.** Answer content questions from the script, never by
reading the slides back — the slides are a lossy summary of it. If the two disagree, the script is
right and the slide gets fixed.

**It is a three-person presentation** and `alles_spreachen.md` is split by speaker:

| Speaker | Sections | Slides | Words |
|---|---|---|---|
| **Speaker A** | (private) | 3–10 | 286 |
| **Speaker B** (the user) | Die Uni · Die Kultur | 11–19 | 344 raw |
| **Speaker C** | (private) | 20–24 | 197 |

Each speaker has a 5-minute slot and their own `.slide--divider` slide. Speaker B's block is
**rehearsed — do not reword it** without being asked.

**Speaker B speaks at ~60 words/minute**, so a 5-minute slot is a 300-word ceiling, not the ~500 words a
default 100 w/min estimate would suggest. Always state the assumed pace when quoting a duration, and
re-measure with a script (not by eye) after any content change. `sprechen-mein-teil.md` is Speaker B's
trimmed, A2-corrected speaking version (277 words, ~4:35); the copy inside `alles_spreachen.md` is
the untrimmed 344-word one. Adding a topic means cutting elsewhere.

`sprechen.md` is an older file holding only Speaker B's part — superseded by the two files above.

## Commands

```bash
google-chrome index.html          # open the deck (then F for fullscreen, → to advance)
python3 export_pdf.py             # -> koeln-praesentation.pdf (25 landscape pages)
python3 export_pdf.py --open      # export and open
python3 export_pdf.py -o x.pdf --budget 20000   # custom name / longer asset wait
python3 export_pptx.py            # -> koeln-praesentation.pptx (one full-bleed image per slide)
python3 export_pptx.py --width 2560   # higher-resolution render
```

`export_pptx.py` is **image-based, not a re-implementation in `python-pptx` shapes** — it
screenshots each slide with the same headless-Chrome technique as `export_pdf.py`/manual
verification, then embeds each PNG full-bleed into a standard 13.333″×7.5″ (16:9) slide. That is a
deliberate simplification: the deck's tilted cards, hard-offset shadows, `text-shadow` big numbers
and self-hosted fonts have no PowerPoint equivalent, so trying to rebuild them as native shapes
would drift from the HTML the moment either file changes. The tradeoff is that text in the `.pptx`
is a picture, not editable text — content edits still happen in `index.html`, then re-export.
It reuses `find_browser`/`BROWSERS` from `export_pdf.py` via a plain sibling import — keep both
files in the same directory.

**First run bootstraps a venv.** The system Python here is externally-managed (PEP 668) and
`python-pptx` isn't apt-packaged, so `export_pptx.py` creates `.venv-pptx/` (with
`--system-site-packages`, so it doesn't redownload Pillow) and re-execs itself inside it via
`os.execv`. This happens automatically and only once; don't try to `pip install python-pptx` into
the system interpreter to "fix" this.

**The 87px headless-Chrome viewport deficit is a fixed constant, not proportional to window
size** — verified empirically at 720/1080/1440px (all short by exactly 87px). Both export scripts
and the manual screenshot recipe below rely on `window-size = target + (0, 87)` then crop; don't
replace it with a percentage.

**`export_pptx.py` screenshots the live, animated page — `--virtual-time-budget` does not
guarantee the compositor has finished painting when the screenshot fires.** A real run once
captured slide 9 mid-fade (~8% opacity, nearly blank) because Chrome's virtual clock isn't tied to
CSS transition/animation frames. Two independent fixes, both required:
1. `?static` in the URL (checked in `slides.js`, near the top of the IIFE) adds
   `html.static-export`, which `style.css` uses to force every animation/transition off instantly
   — the same mechanism `@media print` already uses, which is why `export_pdf.py` never had this
   bug. `screenshot_slide()` always appends `?static` before the `#N` hash.
2. `_is_probably_blank()` in `export_pptx.py` computes grayscale stddev on every crop
   (threshold 20 — calibrated against a real broken capture at ~8 vs. every real slide at 30+) and
   retries once before failing loudly. Belt-and-suspenders: don't remove either half on the
   assumption the other one covers it.

There is no lint or test suite. **Verify visual changes by screenshotting, not by reasoning about
the CSS.** Pass `--window-size=1280,807` and crop to 1280×720 to get a true 1:1 slide image:

```bash
google-chrome --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --virtual-time-budget=6000 --window-size=1280,807 \
  --screenshot=/tmp/s7.png "file://$PWD/index.html#7"
```

The `#7` hash jumps straight to slide 7, so any slide can be checked in isolation.

## Architecture

**Fixed-stage scaling.** Every slide is authored at exactly **1280 × 720 px** inside `#stage`.
`slides.js` sets `--scale = min(innerWidth/1280, innerHeight/720)` and the stage is scaled with a
CSS transform. Nothing reflows on resize — the whole deck just gets bigger or smaller. This is why
hard-coded pixel sizes in `style.css` are correct here and must not be "fixed" into responsive
units.

**Slides are all in the DOM at once**; `slides.js` toggles `.is-active` on one `<section class="slide">`.
Navigation: arrows/space/PageUp/PageDown/Home/End, click (left 35% = back), swipe, `F` = fullscreen.
The current slide is mirrored into `location.hash` via `replaceState`.

**Consistency comes from a small vocabulary, not per-slide CSS.** `style.css` is organized
top-to-bottom as: self-hosted `@font-face` → `:root` tokens → stage → shared primitives
(`.card`, `.sticker`, `.bignum`, `.figure`, `.quote`) → **five layout archetypes** → animations →
print. Each slide picks one archetype and reuses the primitives:

| Archetype | Used for |
|---|---|
| `.slide--title` | 1, 25 |
| `.slide--divider` | 3, 11, 20 — one per speaker; `<use href="#dom-shape">` watermark |
| `.slide--numbers` | 2, 6, 7 — big numbers / card stacks, no photo |
| `.slide--photo` | 4, 8, 9, 13, 15, 17, 23, 24 — full-bleed `img.photo-bg` + scrim + caption cards |
| `.slide--split` | 5, 10, 14, 16, 18, 22 — text column / figure column (`.is-flipped` mirrors it) |
| `.slide--duo` | 19, 21 — two `.dish` cards side by side (generic two-card layout despite the name) |

`.slide--somber` is a **modifier**, not an archetype: slide 8 (the war) keeps every component of the
design system but gets a grayscale photo, a cold scrim, plain white cards and
`.sticker { display: none }`. The deck is deliberately playful everywhere else; that one slide must
never carry a punchline.

Adding a slide means picking an archetype, not writing new layout CSS.

**Rotation and animation share the `--rot` variable.** Tilted elements set `--rot` (`.tilt-l`,
`.tilt-r`) and the base rule applies `transform: rotate(var(--rot, 0deg))`. The `rise` keyframe
re-applies `rotate(var(--rot))` in both from/to — if you write a new transform on `.card`/`.sticker`
without carrying `--rot` through, tilted elements snap straight when they animate in.
Entry order is the inline `style="--i:N"` on each `[data-anim]` element.

**Figure sizing is deterministic on purpose.** Photos have wildly different aspect ratios
(`Köbes.jpg` is only 300×430), so `.figure--wide/--square/--tall` pin an `aspect-ratio` and
`.figure--md/--sm` cap the width. Never let a low-res image go full-bleed.

## Gotchas

- **Every `<!-- === N · TITLE === -->` slide marker must close on its own line.** Two markers once
  lost their trailing ` -->` from an external edit. An unterminated HTML comment swallows
  everything up to the *next* `-->` anywhere later in the file — usually the following slide's own
  closing tag — so it silently deletes that slide's `<section>` entirely, with no browser error.
  First symptom was the deck's own counter showing "12/23" instead of "12/25" (`slides.length` in
  `slides.js` comes from `document.querySelectorAll(".slide")`, which simply found fewer elements).
  Check with: `python3 -c "s=open('index.html',encoding='utf-8').read();
  print(s.count('<!--'), s.count('-->'))"` — these two counts must be equal.
- **Umlaut filenames must be percent-encoded in `src`** (`figures/K%C3%B6bes.jpg`,
  `figures/Lat%C3%A4ng.jpeg`, `figures/K%C3%B6lsche_Grundgesetz.jpeg`). Same for the directory
  `Präsentation` in any `file://` URL — `export_pdf.py` uses `Path.as_uri()` for this reason.
- **Fonts are self-hosted in `fonts/`** (Fredoka + Nunito, latin + latin-ext woff2) so the deck
  works offline in the exam room. Do not add a `fonts.googleapis.com` link. The `@font-face` rules
  live at the top of `style.css` with paths relative to it.
- **`figures/` holds originals plus `*-web.jpg` downscaled copies** (`usb.jpg` is 6.8 MB;
  `usb-web.jpg` is 437 KB). The HTML references the `-web` copies. Keep originals untouched.
- **Print/PDF is a first-class output**, not an afterthought: `@page { size: 1280px 720px }` plus a
  `@media print` block forces one slide per page and hides the deck chrome. Changing stage
  dimensions means changing the `@page` rule too.
- The **Dom silhouette is an inline SVG `<symbol id="dom-shape">`** declared once at the top of
  `#stage` and pulled in with `<use href="#dom-shape"/>`; it inherits `currentColor`. It is the
  deck's own motif — the Dom *photo* slides use `dom-web.jpg`.
- **`.venv-pptx/` is a generated artifact** created on first run of `export_pptx.py` (see Commands).
  Safe to delete any time — it's just rebuilt on the next run, roughly 30 seconds.
- **Full-bleed photos whose aspect ratio is far from 16:9 need `object-position`.** `dom-web.jpg`
  (1.41) and `World_War_II-web.jpg` (1.21) both cut the cathedral's spires off at a centred crop;
  they carry inline `object-position: 50% 22%` / `26%`. Check any new tall photo the same way.
- **`figures/domführung.jpeg` is a meme** (Dom at night, English caption „its just a subway exit").
  It is used on purpose on slide 10 at `--sm` width, with a German figcaption carrying the joke.
- `figures/Unconfirmed 943486.crdownload` is an aborted browser download, not an image.

## Language

**Talk to the user in English.** Their German is A2 and this deck is for their exam — explanations,
summaries and questions in German would make the work harder to check, not easier.

**Write the artifacts in German.** Slides, `README.md` and the code comments in
`style.css`/`slides.js`/`export_pdf.py` are all German and stay that way. Keep the German on the
slides at A2 level: short main clauses, no subordinate-clause chains, no passive if it can be
avoided.

When you change German text, quote the old and new wording in your reply so the user can check it
without opening the file.

The scripts contain grammatical slips from all three speakers that are deliberately *not*
reproduced on the slides („im 1388", „Bürger*ihnen", „Nach heute wird die Stadt … genannt",
„Infolge des Bombenangriffe", „Der Grundstein der gotische Kathedrale"). The script files belong to
the users and are not edited without being asked.

**Chapter labels must stay unique.** `Kapitel 1 · Geschichte` (Speaker A), `Kapitel 2 · Die Uni` /
`Kapitel 2 · Die Kultur` (Speaker B), `Kapitel 3 · Freizeit` (Speaker C) appear both in `data-chapter`
and in the visible `.kicker`. Two speakers sharing a chapter number is a real bug — it happened
once when Speaker C's block was added.

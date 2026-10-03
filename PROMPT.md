# The prompt

Paste this into Claude Code **in plan mode** (Shift+Tab twice). Claude inspects your
images and script, asks a few questions, writes a plan, and only then builds.
Put your script as `script.md` and your photos in `figures/` first.

```
I'm preparing a 15-minute group presentation for my German A2 oral exam about
Cologne (Köln). Three speakers, 5 minutes each. Build the slide deck as a
self-contained HTML + CSS + JS website. Enter plan mode first and plan before
writing any code.

INPUTS
- `script.md`: the full spoken script, one `# Speaker` heading per person
  (Speaker A, Speaker B (me), Speaker C), `##` subheadings per topic.
- `figures/`: all photos I downloaded. Inspect every image (size, aspect ratio,
  what it shows) before planning.

STYLE
- Funny, playful, beautiful and *consistent*. Derive the palette from Cologne's
  coat of arms (red/white), Kölsch gold and Rhine blue on a cream background.
- One small design vocabulary reused everywhere: tilted "scrapbook" cards with
  hard shadows, sticker badges, oversized numbers, a shared confetti-dot
  background, emoji as spot illustrations, staggered entry animations.
- Only a few layout archetypes (title, speaker divider, numbers, full-bleed
  photo, text+photo split, two-card duo). A new slide picks an archetype; it
  never needs new layout CSS.
- Serious topics (e.g. war destruction) keep the same components but get a muted
  variant with no jokes or stickers.

CONTENT RULES
- Slides show only short German keywords and numbers (A2 level, short main
  clauses). The speaker says the full sentences. The script is the source of
  truth: if slide and script disagree, the slide is wrong.
- Fix grammar slips from the script on the slides, but never edit the script
  files themselves.
- One divider slide per speaker; unique chapter labels per speaker.
- Dom/landmarks without a photo: draw them in CSS/SVG.
- Timing: I speak ~60 words/minute, so my 5-minute slot is a 300-word ceiling.
  Measure with a script, not by eye, and tell me when my part is too long.

TECHNICAL
- Files: `index.html`, `style.css`, `slides.js`, no build step, works offline
  (self-host fonts, no CDN).
- Fixed 1280x720 stage scaled to the viewport; arrows/space/click/swipe
  navigation, `F` fullscreen, progress bar, hash routing (`#12`).
- Downscale large photos to `*-web.jpg` copies, keep originals; percent-encode
  umlaut filenames; set `object-position` for photos whose crop cuts off the
  subject.
- Exports: `export_pdf.py` (headless Chrome, 1 slide/page) and `export_pptx.py`
  (one full-bleed image per slide; bootstrap its own venv; disable animations
  while screenshotting and retry blank captures).
- Verify by screenshotting every slide at 1:1 and looking at it; check the
  slide counter and that HTML `<!--` and `-->` counts match.
- Write a README (German) and a CLAUDE.md documenting commands and gotchas.

WORKFLOW
Ask me questions where a decision is genuinely mine (scope, style options),
otherwise decide and tell me what you chose.
```

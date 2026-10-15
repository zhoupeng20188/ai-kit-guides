# X Thread — Vibe-coding a PDF→Word Converter (from `vibe-coding-pdf-word-converter`)

6 posts, English, each ≤280 chars. Based on the article published 2026-07 (build-in-public story). This is the macOS app I shipped with Claude Code and open-sourced.

---

**Post 1** (~230 chars)

I'm a Java engineer who'd never written a line of PyQt. Last week I vibe-coded a real macOS app with Claude Code — a PDF→Word converter — from an empty folder to a packaged .dmg. The honest, dead-ends-included story 🧵

---

**Post 2** (~250 chars)

First attempt failed: pdfplumber turned Chinese text into □□□ tofu boxes.

Root cause: subset-embedded fonts (NSimSun) ship without a ToUnicode map. One engine swap to pdf2docx and the garbage became a usable doc. Match the engine to the font, not the other way.

---

**Post 3** (~254 chars)

pdf2docx still got 3 things wrong, so I wrote a post-processing pipeline (python-docx + lxml):
→ heading hierarchy by font size + numbering
→ code blocks restored from single-cell tables
→ strip U+200B zero-width chars that left invisible gaps

The fixes were mine, not the model's.

---

**Post 4** (~232 chars)

Real numbers on a 227-page bilingual banking PDF: 0.00% garbled characters, 461 headings + 347 tables preserved.

The acceptance test? A verify.py script that fails the build if the tofu ratio exceeds 5%. "Looks fine" isn't the bar. A number is.

---

**Post 5** (~222 chars)

Division of labor: Claude Code wrote most of the PyQt + pdf2docx code. I picked the architecture, specified the detection rules, diagnosed the zero-width bug, wrote the verification script, handled macOS packaging.

The AI built it. The judgment was human.

---

**Post 6** (~150 chars)

Full write-up + open source:

👉 https://aikitguides.com/blog/vibe-coding-pdf-word-converter
💻 https://github.com/zhoupeng20188/pdf2word

What would you vibe-code first? 👇

---

## Posting notes
- This is your strongest build-in-public asset — pair with a real screenshot (conversion-done window at 100%) or use og-vibe-coding-pdf-word.jpg.
- Best windows: 21:00–23:00 Beijing time (US West Coast evening + EU late), or 09:00–10:00 (US East morning).
- Also reuse this story for a Show HN (see show-hn-pdf2word.md) and r/macapps / r/ClaudeAI.
- Don't put the Ko-fi link in the thread — it lives in the README and blog post already.

# Show HN Draft — pdf2word (macOS PDF→Word converter)

Submission copy for Hacker News. Paste the body into the submission text box and set the URL to the GitHub repo. Do NOT include the Ko-fi link here — it lives in the README and blog post; HN punishes self-promo in the post.

---

## Submission title

```
Show HN: I vibe-coded a PDF→Word converter for macOS with Claude Code
```

## Submission body (paste into text field; URL = repo)

I'm a Java backend engineer who'd never written a line of PyQt. Last week I used Claude Code to build a real macOS desktop app — a PDF→Word converter — from an empty folder to a packaged .dmg, and open-sourced it.

Why: every few weeks I need a bank/contract PDF in Word to edit a paragraph or copy a table. Online converters upload my file to a server I don't control (hard no for bank docs), and the offline ones flatten tables or choke on Chinese text. So I built my own.

The interesting part is the failure modes, not the win:
- First attempt used pdfplumber → Chinese text came out as □□□ tofu boxes. Root cause: subset-embedded fonts (NSimSun) ship without a ToUnicode CMap. Switched to pdf2docx (PyMuPDF under the hood) and the garbage became a usable doc.
- pdf2docx still got three things wrong, so I added a post-processing pipeline (python-docx + lxml): heading-hierarchy detection by font size + numbering, code-block restoration (single-cell tables → styled paragraphs), and stripping U+200B zero-width chars that left invisible gaps.

On a 227-page bilingual banking API doc: 0.00% garbled characters, 461 headings + 347 tables preserved. The acceptance test is a verify.py script that fails the build if the tofu ratio exceeds 5% — "looks fine" isn't the bar, a number is.

Division of labor: Claude Code wrote most of the PyQt/pdf2docx code; I picked the architecture, specified the detection rules, diagnosed the zero-width bug, wrote the verification script, and handled macOS packaging.

Caveats: macOS 11+ only, the .app is unsigned (Open Anyway), and there's no OCR fallback yet for scanned PDFs.

GitHub: https://github.com/zhoupeng20188/pdf2word

---

## First comment (post right after submitting, to pre-empt common questions)

A few questions I'd ask if I were you:

- "Why not just use LibreOffice?" — LibreOffice is the Word→PDF path in the app, but PDF→Word fidelity (keeping tables/headings) is the hard direction. pdf2docx + my post-processing is what gets 0% garbled on Chinese docs; LO doesn't do that well.
- "Is this just AI slop?" — No. The AI wrote code, I made every architecture call and wrote the verification. The post-processing pipeline (the part that actually fixes the output) is mine, not the model's.
- "Scanned PDFs?" — Not yet. pdf2docx needs a text layer. OCR (PaddleOCR / macOS Vision) is on the roadmap.

---

## Posting notes
- Timing: HN peak is US East Mon–Thu 09:00–11:00 ET (Beijing 21:00–23:00). First-hour engagement decides front-page fate.
- New → fill title + URL (GitHub) → paste body in text field. The "Show HN:" prefix is required.
- Stay in the comments for the first 30 minutes — HN rewards authors who are present.
- Don't mention money, don't link the blog in the post body (the README already does).

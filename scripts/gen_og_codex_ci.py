from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (15, 23, 42)         # slate-900
CARD = (30, 41, 59)       # slate-800
BLUE = (96, 165, 250)     # blue-400
WHITE = (248, 250, 252)
GRAY = (148, 163, 184)
GREEN = (74, 222, 128)
AMBER = (251, 191, 36)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
UNI = "/Library/Fonts/Arial Unicode.ttf"

f_eyebrow = ImageFont.truetype(BOLD, 30)
f_title = ImageFont.truetype(BOLD, 58)
f_sub = ImageFont.truetype(UNI, 32)
f_code = ImageFont.truetype(MONO, 30)
f_domain = ImageFont.truetype(UNI, 30)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.rounded_rectangle([48, 44, W - 48, H - 44], radius=24, fill=CARD)

d.text((118, 96), "Codex in CI \u00d7 Spring Boot", font=f_eyebrow, fill=BLUE)

d.text((118, 162), "7 tests passed.", font=f_title, fill=WHITE)
d.text((118, 236), "It changed the rule.", font=f_title, fill=GREEN)

d.text((118, 340), "exit code 0 in all five runs", font=f_sub, fill=GRAY)

d.text((118, 404), ">=\u00a0100.00   \u2192   >\u00a0100.00", font=f_code, fill=AMBER)

d.text((118, 476), "aikitguides.com  \u00b7  2026", font=f_domain, fill=GRAY)

out = "/Users/forever/github/ai-kit-guides/public/og-codex-ci-green.jpg"
img.save(out, "JPEG", quality=84, progressive=True, optimize=True)

for label, text, font in [
    ("eyebrow", "Codex in CI \u00d7 Spring Boot", f_eyebrow),
    ("t1", "7 tests passed.", f_title),
    ("t2", "It changed the rule.", f_title),
    ("sub", "exit code 0 in all five runs", f_sub),
    ("code", ">=\u00a0100.00   \u2192   >\u00a0100.00", f_code),
]:
    print(label, d.textlength(text, font=font))

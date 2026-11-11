from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (15, 23, 42)
CARD = (30, 41, 59)
BLUE = (96, 165, 250)
WHITE = (248, 250, 252)
GRAY = (148, 163, 184)
GREEN = (74, 222, 128)
AMBER = (251, 191, 36)
RED = (248, 113, 113)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
UNI = "/Library/Fonts/Arial Unicode.ttf"

f_eyebrow = ImageFont.truetype(BOLD, 30)
f_title = ImageFont.truetype(BOLD, 54)
f_sub = ImageFont.truetype(UNI, 32)
f_code = ImageFont.truetype(MONO, 27)
f_domain = ImageFont.truetype(UNI, 30)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.rounded_rectangle([48, 44, W - 48, H - 44], radius=24, fill=CARD)

d.text((118, 92), "trustbut 0.7.0  \u00b7  Maven / JUnit 6", font=f_eyebrow, fill=BLUE)

d.text((118, 158), "A no-op test gets PASS.", font=f_title, fill=GREEN)
d.text((118, 232), "No test gets WARN.", font=f_title, fill=WHITE)

d.text((118, 336), "10 receipts  \u00b7  Surefire defaults", font=f_sub, fill=GRAY)

d.text((118, 400), "assertTrue(true)   \u2192   PASS  (exit 0)", font=f_code, fill=AMBER)
d.text((118, 442), "0 prove the change \u00b7 1 pass without it", font=f_code, fill=RED)

d.text((118, 512), "aikitguides.com  \u00b7  2026", font=f_domain, fill=GRAY)

out = "/Users/forever/github/ai-kit-guides/public/og-trustbut-junit6-receipt.jpg"
img.save(out, "JPEG", quality=84, progressive=True, optimize=True)

for label, text, font in [
    ("eyebrow", "trustbut 0.7.0  \u00b7  Maven / JUnit 6", f_eyebrow),
    ("t1", "A no-op test gets PASS.", f_title),
    ("t2", "No test gets WARN.", f_title),
    ("sub", "10 receipts  \u00b7  Surefire defaults", f_sub),
    ("code1", "assertTrue(true)   \u2192   PASS  (exit 0)", f_code),
    ("code2", "0 prove the change \u00b7 1 pass without it", f_code),
]:
    width = round(d.textlength(text, font=font))
    print(label, width, "OVERFLOW" if 118 + width > W - 118 else "")

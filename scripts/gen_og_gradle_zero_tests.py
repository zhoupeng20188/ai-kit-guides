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
f_title = ImageFont.truetype(BOLD, 56)
f_sub = ImageFont.truetype(UNI, 32)
f_code = ImageFont.truetype(MONO, 30)
f_domain = ImageFont.truetype(UNI, 30)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.rounded_rectangle([48, 44, W - 48, H - 44], radius=24, fill=CARD)

d.text((118, 92), "Claude Code \u00d7 Gradle", font=f_eyebrow, fill=BLUE)

d.text((118, 156), "BUILD SUCCESSFUL", font=f_title, fill=GREEN)
d.text((118, 228), "in 401ms. Zero tests ran.", font=f_title, fill=WHITE)

d.text((118, 332), "> Task :test UP-TO-DATE", font=f_sub, fill=GRAY)

d.text((118, 396), "./gradlew test --rerun  \u2192  1 failed", font=f_code, fill=AMBER)

d.text((118, 468), "Spring Boot 4.1.1  \u00b7  aikitguides.com  \u00b7  2026", font=f_domain, fill=GRAY)

out = "/Users/forever/github/ai-kit-guides/public/og-gradle-zero-tests.jpg"
img.save(out, "JPEG", quality=84, progressive=True, optimize=True)

for label, text, font in [
    ("eyebrow", "Claude Code \u00d7 Gradle", f_eyebrow),
    ("t1", "BUILD SUCCESSFUL", f_title),
    ("t2", "in 401ms. Zero tests ran.", f_title),
    ("sub", "> Task :test UP-TO-DATE", f_sub),
    ("code", "./gradlew test --rerun  \u2192  1 failed", f_code),
]:
    print(label, round(d.textlength(text, font=font)))

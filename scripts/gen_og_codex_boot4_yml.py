from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (15, 23, 42)         # slate-900
CARD = (30, 41, 59)       # slate-800
BLUE = (96, 165, 250)     # blue-400
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

d.text((118, 92), "Spring Boot 4  ·  application.yml", font=f_eyebrow, fill=BLUE)

d.text((118, 158), "17 keys. 1 bound nobody.", font=f_title, fill=WHITE)
d.text((118, 232), "3 tools. 3 blind spots.", font=f_title, fill=GREEN)

d.text((118, 336), "2,936 advertised properties  \u2192  1,161", font=f_sub, fill=GRAY)

d.text((118, 400), "management.endpoint.health.enabled", font=f_code, fill=AMBER)
d.text((118, 442), "\u2192  200 OK   (but absent from all metadata)", font=f_code, fill=RED)

d.text((118, 512), "aikitguides.com  \u00b7  2026", font=f_domain, fill=GRAY)

out = "/Users/forever/github/ai-kit-guides/public/og-codex-boot4-yml.jpg"
img.save(out, "JPEG", quality=84, progressive=True, optimize=True)

for label, text, font in [
    ("eyebrow", "Spring Boot 4  ·  application.yml", f_eyebrow),
    ("t1", "17 keys. 1 bound nobody.", f_title),
    ("t2", "3 tools. 3 blind spots.", f_title),
    ("sub", "2,936 advertised properties  \u2192  1,161", f_sub),
    ("code1", "management.endpoint.health.enabled", f_code),
    ("code2", "\u2192  200 OK   (but absent from all metadata)", f_code),
]:
    print(label, round(d.textlength(text, font=font)))

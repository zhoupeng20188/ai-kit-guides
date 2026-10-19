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

d.text((118, 92), "Spring Boot 4  \u00b7  Hibernate 7", font=f_eyebrow, fill=BLUE)

d.text((118, 158), "Hibernate 7 renamed", font=f_title, fill=WHITE)
d.text((118, 232), "your columns. Silently.", font=f_title, fill=GREEN)

d.text((118, 336), "same entity, two Boot versions", font=f_sub, fill=GRAY)

d.text((118, 400), "base64content  \u2192  base64_content", font=f_code, fill=AMBER)
d.text((118, 442), "v2token  \u2192  v2_token", font=f_code, fill=AMBER)

d.text((118, 512), "aikitguides.com  \u00b7  2026", font=f_domain, fill=GRAY)

out = "/Users/forever/github/ai-kit-guides/public/og-hibernate7-boot4.jpg"
img.save(out, "JPEG", quality=84, progressive=True, optimize=True)

for label, text, font in [
    ("eyebrow", "Spring Boot 4  \u00b7  Hibernate 7", f_eyebrow),
    ("t1", "Hibernate 7 renamed", f_title),
    ("t2", "your columns. Silently.", f_title),
    ("sub", "same entity, two Boot versions", f_sub),
    ("code1", "base64content  \u2192  base64_content", f_code),
    ("code2", "v2token  \u2192  v2_token", f_code),
]:
    print(label, round(d.textlength(text, font=font)))

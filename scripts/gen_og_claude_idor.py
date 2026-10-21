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
f_title = ImageFont.truetype(BOLD, 56)
f_sub = ImageFont.truetype(UNI, 32)
f_code = ImageFont.truetype(MONO, 27)
f_domain = ImageFont.truetype(UNI, 30)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.rounded_rectangle([48, 44, W - 48, H - 44], radius=24, fill=CARD)

d.text((118, 92), "Claude Code  ·  Spring Boot", font=f_eyebrow, fill=BLUE)

d.text((118, 156), "It added the endpoint.", font=f_title, fill=WHITE)
d.text((118, 232), "It forgot who owns the data.", font=f_title, fill=RED)

d.text((118, 338), "GET /api/orders/1 pulled alice's order, as bob", font=f_sub, fill=GRAY)

d.text((118, 404), "Broken Object Level Authorization", font=f_code, fill=AMBER)
d.text((118, 446), "OWASP API1:2023  ·  45% of AI code fails security", font=f_code, fill=GREEN)

d.text((118, 518), "aikitguides.com  ·  2026", font=f_domain, fill=GRAY)

out = "/Users/forever/github/ai-kit-guides/public/og-claude-code-insecure-api.jpg"
img.save(out, "JPEG", quality=84, progressive=True, optimize=True)

for label, text, font in [
    ("eyebrow", "Claude Code  ·  Spring Boot", f_eyebrow),
    ("t1", "It added the endpoint.", f_title),
    ("t2", "It forgot who owns the data.", f_title),
    ("sub", "GET /api/orders/1 pulled alice's order, as bob", f_sub),
    ("code1", "Broken Object Level Authorization", f_code),
    ("code2", "OWASP API1:2023  ·  45% of AI code fails security", f_code),
]:
    print(label, round(d.textlength(text, font=font)))
print("saved", out)

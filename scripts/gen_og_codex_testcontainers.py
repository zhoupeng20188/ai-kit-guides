from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (15, 23, 42)         # slate-900
CARD = (30, 41, 59)       # slate-800
BLUE = (96, 165, 250)     # blue-400
WHITE = (248, 250, 252)
GRAY = (148, 163, 184)
GREEN = (74, 222, 128)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
UNI = "/Library/Fonts/Arial Unicode.ttf"

f_eyebrow = ImageFont.truetype(BOLD, 30)
f_title = ImageFont.truetype(BOLD, 64)
f_sub = ImageFont.truetype(UNI, 34)
f_code = ImageFont.truetype(MONO, 32)
f_domain = ImageFont.truetype(UNI, 30)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.rounded_rectangle([48, 44, W - 48, H - 44], radius=24, fill=CARD)

d.text((118, 100), "Codex CLI \u00d7 Spring Boot 4", font=f_eyebrow, fill=BLUE)

d.text((118, 170), "Codex Can't Run", font=f_title, fill=WHITE)
d.text((118, 250), "Testcontainers", font=f_title, fill=WHITE)

d.text((118, 366), "One config line decides it \u2014 then verify Skipped: 0", font=f_sub, fill=GRAY)

d.text((118, 432), 'unix_sockets { "/var/run/docker.sock" }  \u00b7 2026', font=f_code, fill=GREEN)

d.text((118, 500), "aikitguides.com", font=f_domain, fill=GRAY)

out = "/Users/forever/github/ai-kit-guides/public/og-codex-testcontainers-docker-socket.jpg"
img.save(out, "JPEG", quality=84, progressive=True, optimize=True)

# report widths so overflow is caught instead of shipped
for name, text, font, limit in [
    ("title1", "Codex Can't Run", f_title, 1034),
    ("title2", "Testcontainers", f_title, 1034),
    ("sub", "One config line decides it \u2014 then verify Skipped: 0", f_sub, 1034),
    ("code", 'unix_sockets { "/var/run/docker.sock" }  \u00b7 2026', f_code, 1034),
]:
    w = d.textlength(text, font=font)
    print(f"{name}: {w:.0f}px / {limit}px {'OVERFLOW' if w > limit else 'ok'}")

import os
print("saved", out, os.path.getsize(out) // 1024, "KB")

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

f_eyebrow = ImageFont.truetype(BOLD, 30)
f_title = ImageFont.truetype(BOLD, 64)
f_sub = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 36)
f_code = ImageFont.truetype(MONO, 34)
f_domain = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 30)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.rounded_rectangle([48, 44, W - 48, H - 44], radius=24, fill=CARD)

d.text((118, 100), "Claude Code \u00d7 Spring Boot 4", font=f_eyebrow, fill=BLUE)

d.text((118, 170), "Claude Code Broke", font=f_title, fill=WHITE)
d.text((118, 250), "My @PreAuthorize", font=f_title, fill=WHITE)

d.text((118, 366), "Build green, admin endpoint open to a normal user", font=f_sub, fill=GRAY)

d.text((118, 432), '@EnableMethodSecurity  \u00b7 2026', font=f_code, fill=GREEN)

d.text((118, 500), "aikitguides.com", font=f_domain, fill=GRAY)

img.save(
    "/Users/forever/github/ai-kit-guides/public/og-claude-code-spring-boot-4-preauthorize.jpg",
    "JPEG", quality=84, progressive=True, optimize=True,
)
print("saved")

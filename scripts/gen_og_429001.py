from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (15, 23, 42)        # slate-900
ACCENT = (56, 189, 248)  # sky-400
WHITE = (248, 250, 252)
GRAY = (148, 163, 184)   # slate-400
RED = (248, 113, 113)    # red-400
CARD = (30, 41, 59)      # slate-800

font_path = "/Library/Fonts/Arial Unicode.ttf"
f_label = ImageFont.truetype(font_path, 30)
f_title = ImageFont.truetype(font_path, 86)
f_sub = ImageFont.truetype(font_path, 40)
f_code = ImageFont.truetype(font_path, 38)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# left accent bar
d.rectangle([0, 0, 14, H], fill=ACCENT)

# site label
d.text((80, 70), "AI KIT GUIDES", font=f_label, fill=ACCENT)

# title
d.text((78, 180), "OpenAI 429001 Error", font=f_title, fill=WHITE)

# subtitle
d.text((80, 300), "What it means & how I fixed it", font=f_sub, fill=GRAY)

# code card
card_x, card_y, card_w, card_h = 80, 410, 720, 110
d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=CARD)
d.text((112, 445), '429001 · CodeRateLimitExceeded', font=f_code, fill=RED)
d.text((112, 478), "request rate exceeded the current model threshold", font=f_sub, fill=GRAY)

img.save(
    "/Users/forever/github/ai-kit-guides/public/og-openai-429001-error-code-fix.jpg",
    "JPEG", quality=82, progressive=True, optimize=True,
)
print("saved og image")

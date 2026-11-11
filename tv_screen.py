"""Cozy TV-format Kanalo home screen (fictional titles/channels only). Usage: python3 tv_screen.py OUT.png [W H]"""
import sys
from PIL import Image, ImageDraw, ImageFilter
import kanalo_video as kv

W, H = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (1638, 1000)
S = 2
w, h = W * S, H * S
BG = (17, 17, 21); SIDE = (24, 24, 29); CARD = (34, 34, 40); TXT = (240, 240, 245); MUTED = (150, 150, 160)
ACC = (255, 140, 60)
img = Image.new("RGB", (w, h), BG)
d = ImageDraw.Draw(img)
F = lambda s, b="Bold": kv.F(int(s * S), b)

def rr(box, r, fill):
    d.rounded_rectangle([v * S for v in box], r * S, fill=fill)

def paste_rounded(src, box, r):
    x0, y0, x1, y1 = [v * S for v in box]
    tw, th = x1 - x0, y1 - y0
    sc = max(tw / src.width, th / src.height)
    s = src.resize((int(src.width * sc) + 1, int(src.height * sc) + 1), Image.LANCZOS)
    s = s.crop(((s.width - tw) // 2, (s.height - th) // 2, (s.width - tw) // 2 + tw, (s.height - th) // 2 + th))
    m = Image.new("L", (tw, th), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, tw - 1, th - 1], r * S, fill=255)
    img.paste(s, (x0, y0), m)
    # bottom gradient for text legibility
    g = Image.new("L", (tw, th), 0); gd = ImageDraw.Draw(g)
    for y in range(th):
        gd.line([(0, y), (tw, y)], fill=int(max(0, (y - th * 0.45) / (th * 0.55)) * 210))
    dark = Image.new("RGB", (tw, th), (0, 0, 0))
    gm = Image.composite(g, Image.new("L", (tw, th), 0), m)
    img.paste(dark, (x0, y0), gm)

# warm ambient glow top-right
glow = Image.new("RGB", (w, h), BG); gd = ImageDraw.Draw(glow)
gd.ellipse([w * 0.55, -h * 0.5, w * 1.3, h * 0.6], fill=(70, 40, 30))
img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(160 * S)), 0.55); d = ImageDraw.Draw(img)

# sidebar
SW = 330
d.rectangle([0, 0, SW * S, h], fill=SIDE)
logo = kv.load("logo.png").convert("RGBA").resize((54 * S, 54 * S), Image.LANCZOS)
lm = Image.new("L", logo.size, 0); ImageDraw.Draw(lm).rounded_rectangle([0, 0, logo.width - 1, logo.height - 1], 13 * S, fill=255)
img.paste(logo, (34 * S, 40 * S), lm)
d.text((102 * S, 67 * S), "Kanalo", font=F(34), fill=TXT, anchor="lm")
d.text((300 * S, 67 * S), "20:51", font=F(22, "Regular"), fill=MUTED, anchor="rm")
rr((30, 125, 300, 180), 16, CARD)
d.ellipse([52 * S, 141 * S, 68 * S, 157 * S], outline=MUTED, width=3 * S); d.line([66 * S, 155 * S, 73 * S, 162 * S], fill=MUTED, width=3 * S)
d.text((86 * S, 152 * S), "Zoeken", font=F(23, "Regular"), fill=MUTED, anchor="lm")
items = ["Home", "Zenders", "Films", "Series", "Instellingen"]
for i, t in enumerate(items):
    y = 222 + i * 70
    if i == 0:
        rr((30, y - 28, 300, y + 28), 16, (78, 45, 28))
    d.text((62 * S, y * S), "●" if i == 0 else "○", font=F(18, "Regular"), fill=ACC if i == 0 else MUTED, anchor="mm")
    d.text((90 * S, y * S), t, font=F(25, "Bold" if i == 0 else "Regular"), fill=ACC if i == 0 else (205, 205, 212), anchor="lm")
rr((30, 890, 300, 960), 16, CARD)
d.text((54 * S, 913 * S), "IPTV", font=F(22), fill=TXT, anchor="lm")
d.text((54 * S, 940 * S), "3 playlists", font=F(18, "Regular"), fill=MUTED, anchor="lm")

# hero cards from fictional demo artwork
src = kv.load("atv_movies.png").convert("RGB")
p1 = src.crop((76, 124, 360, 272)); p2 = src.crop((377, 124, 661, 272)); p3 = src.crop((679, 124, 962, 272))
X0 = SW + 40
cards = [(p1, "FILM", "De Laatste Vuurtoren", "★ 8,7 · Drama"), (p2, "SERIE", "Zilveren Horizon", "★ 8,5 · Sci-fi"), (p3, "FILM", "Stille Getuige", "★ 8,3 · Thriller")]
cw, ch = 400, 420
for i, (p, tag, title, meta) in enumerate(cards):
    x = X0 + i * (cw + 24)
    paste_rounded(p, (x, 40, x + cw, 40 + ch), 22)
    rr((x + 18, 58, x + 18 + (len(tag) * 15 + 28), 92), 10, (0, 0, 0))
    d.text(((x + 32) * S, 75 * S), tag, font=F(18), fill=TXT, anchor="lm")
    d.text(((x + 22) * S, (40 + ch - 70) * S), title, font=F(32), fill=TXT, anchor="lm")
    d.text(((x + 22) * S, (40 + ch - 32) * S), meta, font=F(20, "Regular"), fill=(255, 205, 120), anchor="lm")

# now on tv
d.text((X0 * S, 512 * S), "Nu op tv", font=F(30), fill=TXT, anchor="lm")
chans = [("Noordzee TV", (40, 110, 190), "Live"), ("Cinema Max", (190, 50, 70), "Live"), ("Sport Plus", (40, 150, 90), "Live"), ("Weer & Wind", (210, 150, 40), "Live")]
tw_ = 290
for i, (name, col, st) in enumerate(chans):
    x = X0 + i * (tw_ + 22)
    rr((x, 545, x + tw_, 735), 20, CARD)
    rr((x + 18, 563, x + tw_ - 18, 655), 14, col)
    initials = "".join(wd[0] for wd in name.replace("&", "").split())[:2]
    d.text(((x + tw_ / 2) * S, 609 * S), initials, font=F(46), fill=(255, 255, 255), anchor="mm")
    d.text(((x + 20) * S, 685 * S), name, font=F(22), fill=TXT, anchor="lm")
    d.ellipse([(x + 20) * S, 707 * S, (x + 30) * S, 717 * S], fill=(255, 70, 70))
    d.text(((x + 38) * S, 712 * S), st, font=F(18, "Regular"), fill=MUTED, anchor="lm")

# popular list (two rows)
d.text((X0 * S, 785 * S), "Populaire series", font=F(30), fill=TXT, anchor="lm")
rows = [(p2, "1", "Zilveren Horizon", "Sci-fi"), (p3, "2", "Stille Getuige", "Thriller")]
for i, (p, n, t, g) in enumerate(rows):
    x = X0 + i * 560
    d.text(((x + 10) * S, 868 * S), n, font=F(44), fill=(90, 90, 100), anchor="lm")
    paste_rounded(p, (x + 50, 820, x + 190, 915), 12)
    d.text(((x + 205) * S, 852 * S), t, font=F(22), fill=TXT, anchor="lm")
    d.text(((x + 205) * S, 882 * S), g, font=F(18, "Regular"), fill=MUTED, anchor="lm")

img = img.resize((W, H), Image.LANCZOS)
img.save(sys.argv[1]); print(sys.argv[1], img.size)

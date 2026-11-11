"""TV-format Kanalo home screen in the style of the iPad screenshot, with invented poster art.
Usage: python3 tv_screen2.py ASSET_DIR POSTER_DIR OUT.png  (posters p0..p4.png; fonts + logo.png in ASSET_DIR)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AD, PD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, S = 1638, 1000, 2
w, h = W * S, H * S
def F(size, wt="Bold"): return ImageFont.truetype(os.path.join(AD, f"InterDisplay-{wt}.otf"), int(size * S))
BG = (14, 14, 17); SIDE = (22, 22, 26); CARD = (32, 32, 38); TXT = (242, 242, 246); MUTED = (146, 146, 156); ACC = (255, 138, 60)
img = Image.new("RGB", (w, h), BG); d = ImageDraw.Draw(img)
P = [Image.open(os.path.join(PD, f"p{i}.png")).convert("RGB") for i in range(5)]

def rr(b, r, fill): d.rounded_rectangle([v * S for v in b], r * S, fill=fill)
def put(src, b, r, shade=True, focus=0.35):
    x0, y0, x1, y1 = [v * S for v in b]; tw, th = x1 - x0, y1 - y0
    sc = max(tw / src.width, th / src.height); s = src.resize((int(src.width * sc) + 1, int(src.height * sc) + 1), Image.LANCZOS)
    oy = int((s.height - th) * focus); ox = (s.width - tw) // 2
    s = s.crop((ox, oy, ox + tw, oy + th))
    m = Image.new("L", (tw, th), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, tw - 1, th - 1], r * S, fill=255)
    img.paste(s, (x0, y0), m)
    if shade:
        g = Image.new("L", (tw, th), 0); gd = ImageDraw.Draw(g)
        for y in range(th): gd.line([(0, y), (tw, y)], fill=int(max(0, (y - th * 0.5) / (th * 0.5)) * 225))
        img.paste((0, 0, 0), (x0, y0, x1, y1), Image.composite(g, Image.new("L", (tw, th), 0), m))

# sidebar
SW = 330
d.rectangle([0, 0, SW * S, h], fill=SIDE)
logo = Image.open(os.path.join(AD, "logo.png")).convert("RGBA").resize((50 * S, 50 * S), Image.LANCZOS)
lm = Image.new("L", logo.size, 0); ImageDraw.Draw(lm).rounded_rectangle([0, 0, logo.width - 1, logo.height - 1], 12 * S, fill=255)
img.paste(logo, (34 * S, 42 * S), lm)
d.text((98 * S, 67 * S), "Kanalo", font=F(32), fill=TXT, anchor="lm")
d.text((300 * S, 67 * S), "20:51", font=F(21, "Regular"), fill=MUTED, anchor="rm")
rr((30, 122, 300, 176), 16, CARD)
d.ellipse([50 * S, 139 * S, 66 * S, 155 * S], outline=MUTED, width=3 * S); d.line([64 * S, 153 * S, 71 * S, 160 * S], fill=MUTED, width=3 * S)
d.text((84 * S, 149 * S), "Zoeken", font=F(22, "Regular"), fill=MUTED, anchor="lm")
for i, t in enumerate(["Home", "Zenders", "Films", "Series", "Instellingen"]):
    y = 222 + i * 66
    if i == 0: rr((30, y - 27, 300, y + 27), 16, (74, 44, 26))
    col = ACC if i == 0 else (200, 200, 208)
    d.rounded_rectangle([50 * S, (y - 9) * S, 68 * S, (y + 9) * S], 4 * S, outline=col, width=2 * S)
    d.text((86 * S, y * S), t, font=F(24, "SemiBold" if i == 0 else "Regular"), fill=col, anchor="lm")
rr((30, 892, 300, 958), 16, CARD)
d.text((54 * S, 914 * S), "IPTV", font=F(21, "SemiBold"), fill=TXT, anchor="lm")
d.text((54 * S, 939 * S), "3 playlists", font=F(17, "Regular"), fill=MUTED, anchor="lm")

X0 = SW + 34
heroes = [(0, "FILM", "IJslicht", "Een hacker ontdekt een geheim dat...", "7,9 · Thriller"),
          (1, "SERIE", "Het Zwarte Kasteel", "Twee families strijden om de troon...", "8,6 · Fantasy"),
          (2, "FILM", "Rode Horizon", "Alleen op een planeet die sterft...", "8,1 · Sci-fi")]
cw, ch = 402, 430
for i, (pi, tag, title, desc, meta) in enumerate(heroes):
    x = X0 + i * (cw + 22)
    put(P[pi], (x, 34, x + cw, 34 + ch), 22, focus=0.3)
    tw = d.textlength(tag, font=F(17)) / S
    rr((x + 16, 52, x + 16 + tw + 24, 84), 9, (0, 0, 0))
    d.text(((x + 28) * S, 68 * S), tag, font=F(17), fill=TXT, anchor="lm")
    d.text(((x + 22) * S, (34 + ch - 88) * S), title, font=F(33), fill=TXT, anchor="lm")
    d.text(((x + 22) * S, (34 + ch - 54) * S), desc, font=F(18, "Regular"), fill=(215, 215, 222), anchor="lm")
    d.text(((x + 22) * S, (34 + ch - 26) * S), "★ " + meta, font=F(17, "Regular"), fill=(255, 196, 110), anchor="lm")

d.text((X0 * S, 500 * S), "Nu op tv", font=F(27), fill=TXT, anchor="lm")
chans = [("NOORDZEE", "TV", (30, 95, 170), "Noordzee TV"), ("CINE", "MAX", (180, 35, 55), "Cinema Max HD"),
         ("SPORT", "+", (25, 135, 80), "Sport Plus"), ("NATUUR", "&MEER", (200, 140, 30), "Natuur & Meer")]
tw_ = 296
for i, (a, b, col, name) in enumerate(chans):
    x = X0 + i * (tw_ + 20)
    rr((x, 528, x + tw_, 700), 18, CARD)
    rr((x + 16, 544, x + tw_ - 16, 628), 12, (22, 22, 26))
    d.text(((x + tw_ / 2) * S, 576 * S), a, font=F(30), fill=col, anchor="mm")
    d.text(((x + tw_ / 2) * S, 606 * S), b, font=F(20), fill=(230, 230, 235), anchor="mm")
    d.text(((x + 18) * S, 652 * S), name, font=F(19, "SemiBold"), fill=TXT, anchor="lm")
    d.text(((x + 18) * S, 678 * S), "Live", font=F(16, "Regular"), fill=MUTED, anchor="lm")

d.text((X0 * S, 742 * S), "Populaire series op dit moment", font=F(27), fill=TXT, anchor="lm")
rows = [(1, "1", "Het Zwarte Kasteel", "Fantasy"), (3, "2", "Neonregen", "Misdaad"), (4, "3", "Hemeleilanden", "Animatie & avontuur")]
for i, (pi, n, t, g) in enumerate(rows):
    x = X0 + i * 420
    d.text(((x + 6) * S, 842 * S), n, font=F(40), fill=(84, 84, 94), anchor="lm")
    put(P[pi], (x + 44, 780, x + 200, 904), 12, shade=False, focus=0.35)
    d.text(((x + 214) * S, 828 * S), t, font=F(21, "SemiBold"), fill=TXT, anchor="lm")
    d.text(((x + 214) * S, 856 * S), g, font=F(17, "Regular"), fill=MUTED, anchor="lm")

img.resize((W, H), Image.LANCZOS).save(OUT); print("ok", OUT)

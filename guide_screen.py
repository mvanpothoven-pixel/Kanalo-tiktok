"""iPhone TV-guide screen in Kanalo's style (data from the Apple TV guide), for video overlays."""
import sys
from PIL import Image, ImageDraw
import kanalo_video as kv

W, H = 1179, 2556
BG = (11, 11, 15); CARD = (24, 24, 31); GREY = (140, 138, 155); ORANGE = (255, 149, 64)

ROWS = [  # chip text, chip color, channel, time, now, next, progress
    ("NL1", (52, 92, 230), "Noorderlicht TV", "20:00", "De Zilveren Kust", "21:00 Late Avond Live", 0.74),
    ("PS", (232, 92, 52), "Polderstad", "19:45", "Huis vol Verhalen", "20:45 De Kunstroute", 0.88),
    ("HK", (40, 150, 140), "Havenkanaal", "20:15", "Quiz aan Zee", "21:00 Marktdag", 0.55),
    ("DUIN", (230, 180, 60), "Duin & Dijk", "19:30", "Poldergeheimen", "20:50 Weerbericht", 0.93),
    ("Δ", (120, 80, 230), "Delta TV", "20:20", "Zomergasten aan de Kust", "22:00 Nachtvlucht 219", 0.33),
    ("KO", (240, 120, 40), "Kanaal Oranje", "20:00", "Live: Eredivisie Samenvatting", "21:15 Sportjournaal", 0.62),
    ("M", (60, 160, 90), "Meridiaan", "20:30", "Stille Wateren", "21:25 Het Late Journaal", 0.21),
    ("ZZ", (50, 120, 220), "Zuiderzee TV", "19:55", "De Fietsbrug", "20:55 Avondconcert", 0.81),
    ("VT", (220, 60, 70), "Vuurtoren TV", "20:10", "Late Avond Live", "21:40 Marathon", 0.47),
    ("7", (200, 160, 50), "Molen 7", "20:00", "Live: Motorsport Circuit", "22:00 Nachtconcert", 0.39),
]


def chip(d, x, y, s, txt, col):
    d.rounded_rectangle([x, y, x + s, y + s], 26, fill=(36, 36, 44))
    r = int(s * 0.36)
    cx, cy = x + s / 2, y + s / 2
    if len(txt) > 2:
        d.rounded_rectangle([cx - s * 0.38, cy - s * 0.17, cx + s * 0.38, cy + s * 0.17], 14, fill=col)
        d.text((cx, cy), txt, font=kv.F(int(s * 0.2), "Bold"), fill=(20, 18, 10), anchor="mm")
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        d.text((cx, cy), txt, font=kv.F(int(s * 0.26), "Bold"), fill="white", anchor="mm")


LBL = {"nl": ("Tv-gids", ["Vandaag", "Morgen", "Wo 11", "Do 12"]), "en": ("TV Guide", ["Today", "Tomorrow", "Wed 11", "Thu 12"])}


def render(lang="nl"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # status bar
    d.text((150, 92), "20:41", font=kv.F(50, "Bold"), fill="white", anchor="mm")
    d.rounded_rectangle([W / 2 - 190, 38, W / 2 + 190, 146], 54, fill=(0, 0, 0))
    for i, hh in enumerate([14, 22, 30, 38]):
        d.rounded_rectangle([890 + i * 18, 108 - hh, 902 + i * 18, 108], 3, fill="white")
    d.rounded_rectangle([1000, 74, 1078, 110], 10, outline="white", width=3)
    d.rounded_rectangle([1006, 80, 1060, 104], 6, fill="white")
    # header
    kv.logo(img, 104, 250, 64)
    d.text((150, 250), "Kanalo", font=kv.F(44, "Regular"), fill=(200, 198, 210), anchor="lm")
    d.text((60, 380), LBL[lang][0], font=kv.F(104, "Bold"), fill="white", anchor="ls")
    # day pills
    x = 60
    for i, t in enumerate(LBL[lang][1]):
        f = kv.F(38, "Medium"); w = d.textlength(t, font=f) + 64
        d.rounded_rectangle([x, 430, x + w, 506], 38, fill=(255, 255, 255) if i == 0 else (34, 34, 42))
        d.text((x + w / 2, 468), t, font=f, fill=(15, 15, 20) if i == 0 else (200, 198, 210), anchor="mm")
        x += w + 20
    # rows
    y = 556; rh = 196
    for k, (c, col, name, tm, now, nxt, p) in enumerate(ROWS):
        if y + rh > H - 60: break
        hl = k == 0
        d.rounded_rectangle([40, y, W - 40, y + rh - 22], 34, fill=(34, 26, 30) if hl else CARD,
                            outline=ORANGE if hl else None, width=4 if hl else 0)
        chip(d, 70, y + 30, 114, c, col)
        tx = 214
        d.text((tx, y + 52), name, font=kv.F(36, "Medium"), fill=GREY, anchor="lm")
        d.text((tx, y + 102), now, font=kv.F(44, "Bold"), fill="white", anchor="lm")
        bw = W - 40 - 40 - tx - 30
        d.rounded_rectangle([tx, y + 138, tx + bw, y + 148], 5, fill=(52, 52, 62))
        bar = kv.hgrad(max(10, int(bw * p)), 10, (255, 149, 64), (232, 64, 160))
        m = Image.new("L", bar.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, bar.width - 1, 9], 5, fill=255)
        img.paste(bar, (tx, y + 138), m)
        # LIVE pill
        f = kv.F(30, "Bold"); lw = 128
        d.rounded_rectangle([W - 80 - lw, y + 30, W - 80, y + 74], 22, fill=(16, 16, 20))
        d.ellipse([W - 80 - lw + 18, y + 45, W - 80 - lw + 32, y + 59], fill=(255, 64, 80))
        d.text((W - 80 - lw / 2 + 12, y + 52), "LIVE", font=f, fill="white", anchor="mm")
        y += rh
    # bottom fade
    fade = Image.new("L", (W, 220)); fd = ImageDraw.Draw(fade)
    for i in range(220): fd.line([(0, i), (W, i)], fill=int(255 * i / 220))
    img.paste(Image.new("RGB", (W, 220), BG), (0, H - 220), fade)
    return img


if __name__ == "__main__":
    render(sys.argv[2] if len(sys.argv) > 2 else "nl").save(sys.argv[1] if len(sys.argv) > 1 else "guide.png")

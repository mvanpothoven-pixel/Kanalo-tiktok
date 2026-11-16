"""Make English versions of the Dutch demo screens: inpaint the Dutch text, redraw it in English.
Usage: python3 translate_screens.py   -> writes assets/en/<name>.png"""
import os, textwrap
import numpy as np, cv2
from PIL import Image, ImageDraw
import kanalo_video as kv

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets"); OUT = os.path.join(SRC, "en")
WHITE = (236, 236, 240); GREY = (150, 150, 160); DIM = (120, 120, 130); DARK = (22, 22, 28); OR = (240, 150, 90)

# (box x0,y0,x1,y1), text, size, weight, color, anchor ('lm' left-middle / 'mm' centre), [wrap width px]
EDITS = {
    "atv_home": [
        ((425, 62, 483, 84), "Channels", 13, "SemiBold", (215, 215, 222), "mm"),
        ((512, 62, 553, 84), "Movies", 13, "SemiBold", (215, 215, 222), "mm"),
        ((660, 62, 734, 84), "Settings", 13, "SemiBold", (215, 215, 222), "mm"),
        ((72, 262, 512, 312), "The Last Lighthouse", 44, "Bold", WHITE, "lm"),
        ((72, 318, 492, 372), "When the coast is closed and the village leaves, one lighthouse keeper stays behind. "
         "He keeps the light burning for a ship no one expects.", 14, "Regular", (205, 205, 212), "wrap", 430),
        ((118, 420, 196, 445), "Play", 16, "Bold", (255, 255, 255), "lm"),
        ((232, 420, 306, 445), "More info", 15, "SemiBold", WHITE, "mm"),
        ((640, 434, 737, 450), "The Last Lighthouse", 9, "Bold", WHITE, "lm"),
        ((751, 434, 832, 450), "Silver Horizon", 9, "Bold", WHITE, "lm"),
        ((864, 434, 918, 450), "Harbor City", 9, "Bold", WHITE, "lm"),
        ((72, 527, 256, 554), "Recently added", 19, "Bold", WHITE, "lm"),
    ],
    "atv_movies": [
        ((425, 62, 483, 84), "Channels", 13, "SemiBold", (215, 215, 222), "mm"),
        ((505, 62, 561, 84), "Movies", 13, "SemiBold", DARK, "mm"),
        ((660, 62, 734, 84), "Settings", 13, "SemiBold", (215, 215, 222), "mm"),
        ((90, 283, 318, 313), "The Last Lighthouse", 22, "Bold", WHITE, "lm"),
        ((391, 283, 568, 313), "Silver Horizon", 22, "Bold", WHITE, "lm"),
        ((693, 283, 838, 313), "Silent Witness", 22, "Bold", WHITE, "lm"),
        ((116, 399, 180, 419), "All movies", 14, "SemiBold", WHITE, "lm"),
        ((72, 459, 248, 488), "New this month", 19, "Bold", WHITE, "lm"),
    ],
    "atv_gids": [
        ((106, 65, 160, 85), "Back", 13, "SemiBold", WHITE, "lm"),
        ((166, 58, 258, 92), "TV Guide", 22, "Bold", WHITE, "lm"),
    ] + [((134, y - 9, 232, y + 9), n, 12, "SemiBold", WHITE, "lm") for y, n in [
        (131, "Northern Lights TV"), (180, "Polder City"), (229, "Harbor Channel"), (277, "Dune & Dike"),
        (375, "Channel Orange"), (423, "Meridian"), (472, "Southern Sea TV"), (521, "Lighthouse TV"), (569, "Mill 7")]] + [
        ((485, y - 9, 860, y + 9), t, 13, "SemiBold", c, "lm") for y, t, c in [
            (128, "The Great Voyage", WHITE), (185, "The Evening News", WHITE), (245, "The Silver Coast", WHITE),
            (298, "Late Night Live", GREY), (354, "Night Flight 219", GREY), (411, "Still Waters", GREY),
            (467, "The Late News", GREY), (524, "Night Concert", GREY)]] + [
        ((485, y - 7, 925, y + 7), t, 9, "Regular", c, "lm") for y, t, c in [
            (144, "Four friends sail along the coast and moor wherever the story takes them.", (175, 175, 185)),
            (201, "The latest national and international news, with background and analysis.", (175, 175, 185)),
            (314, "Talk show with guests from culture, sport and science. Tonight: designers of the year.", DIM),
            (370, "Feature film. A pilot discovers that a routine flight is anything but routine.", DIM),
            (427, "Drama series. Elin returns to the village she grew up in, with one question nobody wants to hear.", DIM),
            (483, "A short summary of today's news.", DIM),
            (540, "Recordings from the summer festival by the water, with the city's chamber orchestra.", DIM)]] + [
        ((886, y - 8, 946, y + 8), "Catch up", 9, "Bold", OR, "lm") for y in (135, 192)],
    "as_movies": [
        ((58, 966, 300, 1002), "Recently added", 22, "SemiBold", WHITE, "lm"),
        ((58, 1033, 330, 1069), "New Releases 2026", 22, "SemiBold", WHITE, "lm"),
    ],
    "as_manage": [((64, y - 16, 330, y + 16), t, 21, "Regular", (232, 232, 236), "lm") for y, t in [
        (381, "Netherlands"), (442, "Netherlands Catch-up"), (501, "Netherlands HD"), (562, "Local channels"),
        (622, "Sports channels"), (682, "Movies & Series"), (922, "24/7 Channels"), (982, "Belgium (Flemish)"),
        (1101, "Documentaries")]],
    "as_subs": [((300, 556, 480, 618), "English", 24, "Regular", WHITE, "lm")],
}


def apply(name, edits):
    im = Image.open(os.path.join(SRC, name + ".png")).convert("RGB")
    a = np.array(im)
    mask = np.zeros(a.shape[:2], np.uint8)
    gray = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(int)
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    for e in edits:
        x0, y0, x1, y1 = e[0]
        g = gray[y0:y1, x0:x1]; bg = np.median(g)
        txt = (np.abs(g - bg) > 38) | ((hsv[y0:y1, x0:x1, 1] > 120) & (hsv[y0:y1, x0:x1, 2] > 150) & (e[4] == OR))
        mask[y0:y1, x0:x1] |= (txt * 255).astype(np.uint8)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
    a = cv2.inpaint(a, mask, 4, cv2.INPAINT_TELEA)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for e in edits:
        (x0, y0, x1, y1), t, sz, w, col, anc = e[:6]
        f = kv.F(sz, w)
        if anc == "wrap":
            lines = []; cur = ""
            for word in t.split():
                tst = (cur + " " + word).strip()
                if f.getlength(tst) > e[6]: lines.append(cur); cur = word
                else: cur = tst
            lines.append(cur)
            for i, ln in enumerate(lines): d.text((x0 + 4, y0 + 10 + i * int(sz * 1.2)), ln, font=f, fill=col, anchor="lm")
        elif anc == "mm":
            d.text(((x0 + x1) / 2, (y0 + y1) / 2), t, font=f, fill=col, anchor="mm")
        else:
            d.text((x0 + 2, (y0 + y1) / 2), t, font=f, fill=col, anchor="lm")
    os.makedirs(OUT, exist_ok=True); im.save(os.path.join(OUT, name + ".png"))
    return im


if __name__ == "__main__":
    for n, e in EDITS.items():
        apply(n, e); print("ok", n)

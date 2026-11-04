"""Kanalo TikTok video engine.

Usage: python3 kanalo_video.py SPEC.json OUT_DIR [preview]
SPEC.json: {"videos": [{"id": "...", "lang": "en|nl", "scenes": [{"type": ..., "dur": ..., ...}], ...}]}
Renders 1080x1920 30fps H.264 MP4s (no audio) into OUT_DIR/<id>.mp4.
Only uses the brand assets in ./assets (real logo + demo-content screens). Never add screens with
real channels, real film/series posters or a real playlist URL.
"""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/opentype/inter/"
WHITE = (255, 255, 255); RED = (255, 75, 75); GREEN = (70, 220, 140)
VIOLET = (123, 76, 240); PINK = (224, 64, 143); ORANGE = (240, 122, 69)
BG = (10, 9, 16)

_fc = {}
def F(size, w="Bold"):
    k = (size, w)
    if k not in _fc:
        try: _fc[k] = ImageFont.truetype(FD + f"InterDisplay-{w}.otf", size)
        except OSError: _fc[k] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    return _fc[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)

def hgrad(w, h, c1, c2):
    w, h = max(1, int(w)), max(1, int(h))
    g = Image.new("RGB", (256, 1))
    for i in range(256):
        f = i / 255
        g.putpixel((i, 0), tuple(int(c1[j] + (c2[j] - c1[j]) * f) for j in range(3)))
    return g.resize((w, h))

def brand_grad(w, h):
    w, h = max(2, int(w)), max(1, int(h))
    g = Image.new("RGB", (w, h)); a = w // 2
    g.paste(hgrad(a, h, VIOLET, PINK), (0, 0)); g.paste(hgrad(w - a, h, PINK, ORANGE), (a, 0))
    return g

def glow_bg(c, cy=0.4, strength=0.5, r=900):
    base = Image.new("RGB", (W, H), BG); lay = Image.new("RGB", (W, H), BG)
    ImageDraw.Draw(lay).ellipse([W/2 - r, H*cy - r, W/2 + r, H*cy + r], fill=c)
    return Image.blend(base, lay.filter(ImageFilter.GaussianBlur(260)), strength)

BGS = {
    "problem": glow_bg((95, 22, 22), strength=0.5),
    "brand": glow_bg((120, 40, 110), cy=0.38),
    "violet": glow_bg((70, 40, 150), cy=0.5, strength=0.55),
    "warm": glow_bg((140, 60, 50), cy=0.55, strength=0.45),
}

def load(n): return Image.open(os.path.join(HERE, "assets", n)).convert("RGB")
ASSETS = {n: load(n + ".png") for n in ["logo", "atv_home", "atv_gids", "atv_movies", "iphone_detail", "rec_settings", "site_couch"]}

# ---------- drawing helpers ----------
def text(img, s, cx, cy, size, fill=WHITE, alpha=1.0, w="Bold", anchor="mm", grad=False, maxw=980):
    if alpha <= 0 or not s: return
    f = F(size, w)
    d0 = ImageDraw.Draw(img)
    while size > 24 and d0.textlength(s, font=f) > maxw:
        size -= 4; f = F(size, w)
    if grad:
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).text((cx, cy), s, font=f, fill=int(255 * alpha), anchor=anchor)
        bb = mask.getbbox()
        if not bb: return
        full = Image.new("RGB", img.size); full.paste(brand_grad(bb[2] - bb[0], bb[3] - bb[1]), (bb[0], bb[1]))
        img.paste(full, (0, 0), mask); return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((cx, cy), s, font=f, fill=tuple(fill) + (int(255 * alpha),), anchor=anchor)
    img.paste(lay, (0, 0), lay)

def rrect(img, box, r, fill=None, alpha=1.0, outline=None, width=0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); a = int(255 * clamp(alpha))
    ImageDraw.Draw(lay).rounded_rectangle([int(v) for v in box], int(r), fill=(tuple(fill) + (a,)) if fill else None,
                                          outline=(tuple(outline) + (a,)) if outline else None, width=width)
    img.paste(lay, (0, 0), lay)

def paste_round(img, src, box, r, alpha=1.0):
    x0, y0, x1, y1 = [int(v) for v in box]; w, h = x1 - x0, y1 - y0
    if w < 2 or h < 2 or alpha <= 0: return
    s = src.resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], int(r), fill=int(255 * alpha))
    img.paste(s, (x0, y0), m)

def zoomed(src, z, fx=0.5, fy=0.5):
    w, h = src.size; cw, ch = w / z, h / z
    x0 = (w - cw) * fx; y0 = (h - ch) * fy
    return src.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))

def logo(img, cx, cy, s, alpha=1.0):
    if s >= 4: paste_round(img, ASSETS["logo"], (cx - s/2, cy - s/2, cx + s/2, cy + s/2), s * 0.23, alpha)

def spinner(img, cx, cy, r, t, col=WHITE):
    d = ImageDraw.Draw(img)
    for i in range(12):
        ang = (i / 12) * 2 * math.pi + t * 7; fade = (i / 12) ** 1.5
        c = tuple(int(30 + (col[j] - 30) * fade) for j in range(3))
        x, y = cx + math.cos(ang) * r, cy + math.sin(ang) * r
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=c)

def check(img, cx, cy, r, alpha=1.0):
    rrect(img, (cx - r, cy - r, cx + r, cy + r), r, GREEN, alpha)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).line([(cx - r*0.45, cy), (cx - r*0.1, cy + r*0.38), (cx + r*0.5, cy - r*0.35)],
                             fill=(10, 30, 20, int(255*alpha)), width=max(3, int(r*0.22)), joint="curve")
    img.paste(lay, (0, 0), lay)

def cross(img, cx, cy, r, alpha=1.0):
    rrect(img, (cx - r, cy - r, cx + r, cy + r), r, RED, alpha)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); k = r * 0.38; wd = max(3, int(r*0.22))
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=(40, 10, 10, int(255*alpha)), width=wd)
    d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=(40, 10, 10, int(255*alpha)), width=wd)
    img.paste(lay, (0, 0), lay)

_glow = {}
def tv(img, src, k, cy=1030, z0=1.0, z1=1.1, fx=0.5, fy=0.5, rise=0, alpha=1.0):
    tw = 1000; th = int(tw * src.size[1] / src.size[0])
    x0 = (W - tw) // 2; y0 = int(cy - th / 2 + rise)
    key = (tw, th)
    if key not in _glow:
        pad = 160; g = Image.new("L", (tw + 2*pad, th + 2*pad), 0)
        ImageDraw.Draw(g).rounded_rectangle((pad, pad, pad + tw, pad + th), 40, fill=120)
        _glow[key] = (g.filter(ImageFilter.GaussianBlur(60)), pad)
    g, pad = _glow[key]
    img.paste(Image.new("RGB", g.size, (110, 60, 190)), (x0 - pad, y0 - pad), g.point(lambda v: int(v * alpha)))
    rrect(img, (x0 - 18, y0 - 18, x0 + tw + 18, y0 + th + 18), 42, (34, 32, 40), alpha)
    paste_round(img, zoomed(src, z0 + (z1 - z0) * k, fx, fy), (x0, y0, x0 + tw, y0 + th), 26, alpha)
    rrect(img, (W/2 - 130, y0 + th + 40, W/2 + 130, y0 + th + 56), 8, (40, 38, 48), alpha)
    return x0, y0, tw, th

def caption(img, top, sub, t, y=300, size=82):
    p = prog(t, 0.0, 0.35)
    text(img, top, W/2, y + 30 * (1 - ease(p)), size, alpha=ease(p), w="Black")
    if sub:
        p2 = prog(t, 0.2, 0.55)
        text(img, sub, W/2, y + size * 1.28 + 30 * (1 - ease(p2)), size, alpha=ease(p2), w="Black", grad=True)

def small_label(img, s, y, t):
    text(img, s, W/2, y, 36, fill=(190, 180, 210), alpha=ease(prog(t, 0.4, 0.8)), w="SemiBold")

def flash(img, t, strength=0.85):
    fl = 1 - ease(prog(t, 0, 0.25))
    return Image.blend(img, Image.new("RGB", (W, H), WHITE), fl * strength) if fl > 0 else img

def shake(t, t0, amp=18):
    k = prog(t, t0, t0 + 0.35)
    return 0 if k <= 0 or k >= 1 else int(math.sin(k * 40) * amp * (1 - k))

# ---------- scenes: fn(t, dur, p) -> RGB image ----------
def sc_hook(t, d, p):
    img = BGS[p.get("bg", "brand")].copy()
    lines = p["lines"]; acc = p.get("accent", len(lines) - 1); size = p.get("size", 104)
    y0 = H * 0.42 - (len(lines) - 1) * size * 0.62
    for i, ln in enumerate(lines):
        q = 1.0 if p.get("instant") else prog(t, 0.15 + i * 0.35, 0.45 + i * 0.35)
        if q > 0:
            text(img, ln, W/2, y0 + i * size * 1.25 + 26 * (1 - ease(q)), int(size * (0.8 + 0.2 * back(q))),
                 alpha=ease(q), w="Black", grad=(i == acc and p.get("bg") != "problem"),
                 fill=RED if (i == acc and p.get("bg") == "problem") else WHITE)
    if p.get("pov"):
        text(img, p["pov"], W/2, y0 - 150, 46, fill=(210, 200, 230), alpha=1.0 if p.get("instant") else ease(prog(t, 0, 0.3)), w="SemiBold")
    if p.get("foot"):
        text(img, p["foot"], W/2, H * 0.42 + len(lines) * size * 0.75 + 90, 44, fill=(215, 205, 230), w="SemiBold")
    return img

def sc_oldapp(t, d, p):
    img = BGS["problem"].copy()
    words = p.get("words", ["Ads.", "Buffering.", "Again."])
    dx = sum(shake(t, 0.7 + 0.8 * i) for i in range(len(words)))
    text(img, p.get("title", "Your IPTV app:"), W/2, 330, 88, alpha=ease(prog(t, 0, 0.3)))
    px0, py0, px1, py1 = 90 + dx, 560, 990 + dx, 1066
    rrect(img, (px0, py0, px1, py1), 36, (28, 28, 32))
    dr = ImageDraw.Draw(img)
    for i in range(0, 506, 22): dr.line([(px0 + 20, py0 + i), (px1 - 20, py0 + i)], fill=(34, 34, 40), width=2)
    spinner(img, (px0 + px1) / 2, 730, 60, t)
    text(img, p.get("buffering", "Buffering..."), (px0 + px1) / 2, 850, 46, fill=(170, 170, 180), w="Medium")
    a = ease(prog(t, 0.6, 0.9))
    if a > 0:
        by = 1066 - 130 * a
        rrect(img, (px0 + 30, by - 10, px1 - 30, by + 100), 20, (250, 205, 40))
        text(img, p.get("ad", "AD  ·  Skip in 30"), (px0 + px1) / 2, by + 45, 46, fill=(20, 20, 20), w="ExtraBold")
    for i, wd in enumerate(words):
        q = prog(t, 0.7 + 0.8 * i, 0.95 + 0.8 * i)
        if q > 0:
            text(img, wd, W/2, 1230 + i * 120, int(100 * (0.6 + 0.4 * back(q))), fill=RED if i == len(words) - 1 else WHITE,
                 alpha=ease(q), w="Black")
    return img

def sc_wait(t, d, p):
    img = BGS["problem"].copy()
    text(img, p.get("top", "Switching channel..."), W/2, 420, 70, alpha=ease(prog(t, 0, 0.3)))
    spinner(img, W/2, 760, 90, t, col=(220, 220, 230))
    text(img, f"{min(p.get('max', 8.4), t * 3.6):4.1f}s".replace(".", p.get("dec", ".")), W/2, 1010, 170, fill=RED, w="Black")
    q = prog(t, 1.4, 1.7)
    text(img, p.get("bottom", "Every. Single. Channel."), W/2, 1260 + 30 * (1 - ease(q)), 66, alpha=ease(q), w="ExtraBold")
    return img

def sc_reveal(t, d, p):
    img = flash(BGS["brand"].copy(), t)
    text(img, p.get("top", "Time to upgrade."), W/2, 470, 80, alpha=ease(prog(t, 0.05, 0.45)), w="ExtraBold")
    logo(img, W/2, 860, 420 * back(prog(t, 0.3, 0.85)))
    q = prog(t, 0.85, 1.25)
    text(img, "Kanalo", W/2, 1210 + 40 * (1 - ease(q)), 150, alpha=ease(q), w="Black")
    q3 = ease(prog(t, 1.3, 1.7))
    text(img, p.get("tag1", "The ad-free IPTV player"), W/2, 1340, 52, fill=(225, 215, 240), alpha=q3, w="Medium")
    text(img, p.get("tag2", "for iPhone, iPad & Apple TV"), W/2, 1410, 52, alpha=q3, w="Bold", grad=True)
    return img

def sc_tv(t, d, p):
    img = BGS[p.get("bg", "violet")].copy()
    caption(img, p.get("top", ""), p.get("sub", ""), t)
    rise = 80 * (1 - ease(prog(t, 0, 0.5)))
    x0, y0, tw, th = tv(img, ASSETS[p.get("asset", "atv_home")], t / d, z0=p.get("z0", 1.0), z1=p.get("z1", 1.12),
                        fx=p.get("fx", 0.4), fy=p.get("fy", 0.4), rise=rise)
    if p.get("label"): small_label(img, p["label"], y0 + th + 120, t)
    return img

def sc_phone(t, d, p):
    img = BGS[p.get("bg", "warm")].copy()
    caption(img, p.get("top", ""), p.get("sub", ""), t, y=230)
    src = ASSETS["iphone_detail"]; pw = 600; ph = int(pw * src.size[1] / src.size[0])
    x0 = (W - pw) // 2; y0 = int(470 + 120 * (1 - ease(prog(t, 0, 0.5))))
    rrect(img, (x0 - 22, y0 - 22, x0 + pw + 22, y0 + ph + 22), 96, (38, 36, 46))
    paste_round(img, zoomed(src, 1 + 0.06 * (t / d), 0.5, 0.0), (x0, y0, x0 + pw, y0 + ph), 78)
    q = prog(t, 1.6, 2.1)
    if 0 < q < 1:
        px, py = x0 + pw * 0.33, y0 + ph * 0.395; r = 30 + 60 * ease(q)
        rrect(img, (px - r, py - r, px + r, py + r), r, None, alpha=1 - q, outline=WHITE, width=6)
    return img

def sc_list(t, d, p):
    img = BGS[p.get("bg", "violet")].copy()
    text(img, p["title"], W/2, 330, 78, w="Black", alpha=ease(prog(t, 0, 0.3)))
    if p.get("sub"): text(img, p["sub"], W/2, 430, 78, w="Black", grad=True, alpha=ease(prog(t, 0.15, 0.45)))
    items = p["items"]; step = (d - 1.2) / max(1, len(items))
    for i, it in enumerate(items):
        q = prog(t, 0.6 + i * step, 0.9 + i * step)
        if q <= 0: continue
        y = 700 + i * 260 + 40 * (1 - ease(q))
        rrect(img, (90, y - 105, 990, y + 105), 40, (255, 255, 255), alpha=0.07 * ease(q), outline=(255, 255, 255), width=2)
        btn = brand_grad(120, 120); m = Image.new("L", (120, 120), 0)
        ImageDraw.Draw(m).ellipse([0, 0, 119, 119], fill=int(255 * ease(q))); img.paste(btn, (130, int(y - 60)), m)
        text(img, str(i + 1) if p.get("numbered", True) else "", 190, y, 60, w="Black", alpha=ease(q))
        if not p.get("numbered", True): check(img, 190, y, 40, ease(q))
        text(img, it[0], 290, y - (24 if len(it) > 1 else 0), 50, w="ExtraBold", anchor="lm", alpha=ease(q), maxw=670)
        if len(it) > 1: text(img, it[1], 290, y + 34, 36, fill=(200, 190, 220), w="Medium", anchor="lm", alpha=ease(q), maxw=670)
    return img

def sc_compare(t, d, p):
    img = BGS["violet"].copy()
    text(img, p.get("title", "IPTV apps vs Kanalo"), W/2, 300, 76, w="Black", alpha=ease(prog(t, 0, 0.3)))
    hq = ease(prog(t, 0.2, 0.5))
    text(img, p.get("left", "Other apps"), 300, 470, 46, fill=(220, 160, 160), w="ExtraBold", alpha=hq)
    logo(img, 700, 470, 90 * hq); text(img, "Kanalo", 820, 470, 46, w="ExtraBold", alpha=hq, anchor="lm")
    rows = p["rows"]; step = (d - 1.4) / max(1, len(rows))
    for i, (lt, rt) in enumerate(rows):
        q = prog(t, 0.7 + i * step, 1.0 + i * step)
        if q <= 0: continue
        y = 640 + i * 190
        rrect(img, (60, y - 75, 520, y + 75), 30, (120, 30, 40), alpha=0.35 * ease(q))
        rrect(img, (560, y - 75, 1020, y + 75), 30, (60, 140, 90), alpha=0.30 * ease(q))
        cross(img, 115, y, 30, ease(q)); check(img, 615, y, 30, ease(q))
        text(img, lt, 165, y, 38, w="SemiBold", anchor="lm", alpha=ease(q), maxw=340)
        text(img, rt, 665, y, 38, w="Bold", anchor="lm", alpha=ease(q), maxw=340)
    return img

def sc_steps(t, d, p):
    img = BGS["brand"].copy()
    caption(img, p.get("top", "Set up in"), p.get("sub", "under a minute."), t, y=280)
    steps = p["steps"]; step = (d - 1.2) / max(1, len(steps))
    for i, st in enumerate(steps):
        q = prog(t, 0.7 + i * step, 1.0 + i * step)
        if q <= 0: continue
        y = 760 + i * 300
        if i: rrect(img, (W/2 - 4, y - 230, W/2 + 4, y - 80), 4, (255, 255, 255), alpha=0.25 * ease(q))
        btn = brand_grad(140, 140); m = Image.new("L", (140, 140), 0)
        ImageDraw.Draw(m).ellipse([0, 0, 139, 139], fill=int(255 * ease(q))); img.paste(btn, (int(W/2 - 70), int(y - 70 + 30 * (1 - ease(q)))), m)
        text(img, str(i + 1), W/2, y + 30 * (1 - ease(q)), 70, w="Black", alpha=ease(q))
        text(img, st, W/2, y + 115, 50, w="ExtraBold", alpha=ease(q))
    return img

_qr = None
def qr_img(n=25, cell=12):
    global _qr
    if _qr is None:
        rnd = random.Random(7); im = Image.new("RGB", (n * cell, n * cell), WHITE); d = ImageDraw.Draw(im)
        for y in range(n):
            for x in range(n):
                if rnd.random() < 0.48: d.rectangle([x*cell, y*cell, x*cell + cell - 1, y*cell + cell - 1], fill=(10, 10, 14))
        for (fx, fy) in [(0, 0), (n - 7, 0), (0, n - 7)]:
            d.rectangle([fx*cell, fy*cell, (fx+7)*cell - 1, (fy+7)*cell - 1], fill=WHITE)
            d.rectangle([fx*cell, fy*cell, (fx+7)*cell - 1, (fy+7)*cell - 1], outline=(10, 10, 14), width=cell)
            d.rectangle([(fx+2)*cell, (fy+2)*cell, (fx+5)*cell - 1, (fy+5)*cell - 1], fill=(10, 10, 14))
        _qr = im.resize((n*cell + 40, n*cell + 40)) if False else im
    return _qr

def sc_qr(t, d, p):
    img = BGS["violet"].copy()
    caption(img, p.get("top", "iPhone to Apple TV"), p.get("sub", "with one scan."), t, y=260)
    tw, th = 960, 560; x0, y0 = (W - tw) // 2, 560
    rrect(img, (x0 - 18, y0 - 18, x0 + tw + 18, y0 + th + 18), 42, (34, 32, 40))
    swap = ease(prog(t, 2.7, 3.1))
    rrect(img, (x0, y0, x0 + tw, y0 + th), 26, (14, 12, 22))
    if swap < 1:
        q = qr_img(); s = 300; img.paste(q.resize((s, s), Image.NEAREST), (x0 + 80, y0 + (th - s) // 2))
        text(img, p.get("tv1", "Add playlist"), x0 + 440, y0 + 210, 46, w="ExtraBold", anchor="lm", alpha=1 - swap)
        text(img, p.get("tv2", "From iPhone"), x0 + 440, y0 + 280, 40, w="SemiBold", anchor="lm", fill=(200, 190, 220), alpha=1 - swap)
        text(img, p.get("tv3", "Scan with your camera"), x0 + 440, y0 + 340, 32, w="Medium", anchor="lm", fill=(160, 150, 180), alpha=1 - swap)
    if swap > 0: paste_round(img, ASSETS["atv_home"], (x0, y0, x0 + tw, y0 + th), 26, swap)
    rrect(img, (W/2 - 130, y0 + th + 40, W/2 + 130, y0 + th + 56), 8, (40, 38, 48))
    # phone rising
    up = ease(prog(t, 0.6, 1.3)) * (1 - ease(prog(t, 2.5, 2.9)))
    if up > 0:
        pw, ph = 360, 720; px = W/2 + 40; py = H + 40 - (ph * 1.12) * up
        rrect(img, (px - 18, py - 18, px + pw + 18, py + ph + 18), 70, (38, 36, 46))
        rrect(img, (px, py, px + pw, py + ph), 56, (20, 18, 28))
        fx0, fy0 = px + 50, py + 140
        img.paste(qr_img().resize((200, 200), Image.NEAREST), (int(fx0 + 30), int(fy0 + 30)))
        rrect(img, (fx0, fy0, fx0 + 260, fy0 + 260), 24, None, outline=WHITE, width=5)
        sl = prog(t, 1.3, 2.1)
        if 0 < sl < 1:
            yy = fy0 + 260 * (0.5 - 0.5 * math.cos(sl * 2 * math.pi))
            rrect(img, (fx0 + 10, yy - 3, fx0 + 250, yy + 3), 3, PINK)
        ok = prog(t, 2.0, 2.3)
        if ok > 0:
            check(img, px + pw / 2, fy0 + 400, 50, ease(ok))
            text(img, p.get("sent", "Playlists sent"), px + pw / 2, fy0 + 500, 34, w="Bold", alpha=ease(ok), maxw=320)
    small_label(img, p.get("label", "NOTHING TO TYPE ON THE TV"), y0 + th + 130, t - 2.8)
    return img

def sc_price(t, d, p):
    img = BGS["brand"].copy()
    caption(img, p.get("top", "Free to use."), p.get("sub", "Pro for €0.99."), t, y=260)
    cards = [(p.get("free_title", "Free"), p.get("free_items", ["Live TV, movies & series", "TV guide", "Apple TV app", "No ads"]), False),
             (p.get("pro_title", "Pro"), p.get("pro_items", ["Picture in Picture", "AirPlay & Chromecast", "Offline downloads", "Family Sharing"]), True)]
    for i, (ttl, items, pro) in enumerate(cards):
        q = prog(t, 0.6 + i * 0.5, 1.0 + i * 0.5)
        if q <= 0: continue
        x0 = 70 + i * 480; y0 = 600 + 40 * (1 - ease(q)); x1 = x0 + 460; y1 = y0 + 760
        if pro:
            gb = brand_grad(x1 - x0 + 8, y1 - y0 + 8); m = Image.new("L", gb.size, 0)
            ImageDraw.Draw(m).rounded_rectangle([0, 0, gb.size[0]-1, gb.size[1]-1], 44, fill=int(255 * ease(q)))
            img.paste(gb, (int(x0 - 4), int(y0 - 4)), m)
        rrect(img, (x0, y0, x1, y1), 40, (22, 18, 32), alpha=ease(q))
        text(img, ttl, (x0 + x1) / 2, y0 + 80, 64, w="Black", alpha=ease(q), grad=pro)
        for j, it in enumerate(items):
            yy = y0 + 200 + j * 110
            check(img, x0 + 60, yy, 22, ease(q))
            text(img, it, x0 + 100, yy, 32, w="SemiBold", anchor="lm", alpha=ease(q), maxw=330)
        text(img, p.get("free_price", "€0") if not pro else p.get("pro_price", "€0.99 / mo"), (x0 + x1) / 2, y1 - 110, 54, w="Black", alpha=ease(q))
        if pro: text(img, p.get("pro_note", "or €39.99 lifetime"), (x0 + x1) / 2, y1 - 50, 30, w="Medium", fill=(200, 190, 220), alpha=ease(q))
    return img

CTA = {
    "en": dict(feats=["No ads. No account.", "Live TV, movies & series", "iPhone · iPad · Apple TV"],
               btn="Free on the App Store", foot="Bring your own M3U or Xtream playlist"),
    "nl": dict(feats=["Geen ads. Geen account.", "Live TV, films & series", "iPhone · iPad · Apple TV"],
               btn="Gratis in de App Store", foot="Gebruik je eigen M3U- of Xtream-playlist"),
}
def sc_cta(t, d, p):
    c = CTA[p.get("lang", "en")]
    img = BGS["brand"].copy()
    logo(img, W/2, 400, 280 * back(prog(t, 0, 0.45)))
    for i, f in enumerate(c["feats"]):
        q = prog(t, 0.3 + i * 0.22, 0.6 + i * 0.22)
        if q <= 0: continue
        y = 680 + i * 140 + 30 * (1 - ease(q))
        rrect(img, (170, y - 52, 910, y + 52), 52, (255, 255, 255), alpha=0.08 * ease(q), outline=(255, 255, 255), width=2)
        text(img, f, W/2, y, 46, alpha=ease(q), w="SemiBold")
    q = prog(t, 1.1, 1.5)
    if q > 0:
        sc = 0.85 + 0.15 * back(q); bw, bh = 840 * sc, 150 * sc; cy = 1200
        btn = brand_grad(bw, bh); m = Image.new("L", btn.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, btn.size[0]-1, btn.size[1]-1], int(bh/2), fill=int(255 * ease(q)))
        img.paste(btn, (int(W/2 - bw/2), int(cy - bh/2)), m)
        text(img, c["btn"], W/2, cy, int(56 * sc), alpha=ease(q), w="ExtraBold")
    q2 = ease(prog(t, 1.7, 2.1))
    text(img, "kanalo.app", W/2, 1360, 64, alpha=q2, w="Black")
    text(img, c["foot"], W/2, 1440, 34, fill=(200, 190, 220), alpha=q2, w="Medium")
    return img

def sc_screen(t, d, p):
    """Real app screen (from a clean screen recording) in a phone frame, with a highlight ring on one row."""
    img = BGS[p.get("bg", "violet")].copy()
    caption(img, p.get("top", ""), p.get("sub", ""), t, y=200, size=74)
    src = ASSETS[p.get("asset", "rec_settings")]; pw = 640; ph = int(pw * src.size[1] / src.size[0])
    vis = 1440 - 430; x0 = (W - pw) // 2; y0 = int(430 + 100 * (1 - ease(prog(t, 0, 0.5))))
    hy = p.get("hy", 0.74)
    off = int(clamp(hy * ph - vis * 0.55, 0, ph - vis) * ease(prog(t, 0.3, 1.2))) if ph > vis else 0
    crop = src.resize((pw, ph), Image.LANCZOS).crop((0, off, pw, off + vis))
    rrect(img, (x0 - 20, y0 - 20, x0 + pw + 20, y0 + vis + 20), 70, (38, 36, 46))
    paste_round(img, crop, (x0, y0, x0 + pw, y0 + vis), 56)
    q = prog(t, 1.3, 1.7)
    if q > 0:
        yy = y0 + hy * ph - off; a = ease(q)
        rrect(img, (x0 + 14, yy - 40, x0 + pw - 14, yy + 40), 22, None, alpha=a, outline=PINK, width=7)
    if p.get("label"): text(img, p["label"], W/2, 1560, 48, w="ExtraBold", grad=True, alpha=ease(prog(t, 1.6, 2.0)))
    if p.get("label2"): text(img, p["label2"], W/2, 1640, 38, fill=(200, 190, 220), w="Medium", alpha=ease(prog(t, 1.8, 2.2)))
    return img

def sc_tips(t, d, p):
    """Numbered fix-list: problem solving, no selling."""
    img = BGS[p.get("bg", "violet")].copy() if not p.get("site") else site_bg((70, 50, 160), cy=0.6, strength=0.25)
    if p.get("site"): header(img)
    oy = 0
    if p.get("site"):
        headline(img, [p["title"]] + (["*" + p["sub"] + "*"] if p.get("sub") else []), 440, 96, t); oy = 140
    else:
        text(img, p["title"], W/2, 300, 76, w="Black", alpha=ease(prog(t, 0, 0.3)))
        if p.get("sub"): text(img, p["sub"], W/2, 400, 76, w="Black", grad=True, alpha=ease(prog(t, 0.15, 0.45)))
    items = p["items"]; step = (d - 1.2) / max(1, len(items))
    for i, it in enumerate(items):
        q = prog(t, 0.5 + i * step, 0.8 + i * step)
        if q <= 0: continue
        y = 640 + oy + i * 300 + 40 * (1 - ease(q))
        rrect(img, (70, y - 125, 1010, y + 125), 40, (255, 255, 255), alpha=0.07 * ease(q), outline=(255, 255, 255), width=2)
        btn = brand_grad(110, 110); m = Image.new("L", (110, 110), 0)
        ImageDraw.Draw(m).ellipse([0, 0, 109, 109], fill=int(255 * ease(q))); img.paste(btn, (110, int(y - 55)), m)
        text(img, str(i + 1), 165, y, 56, w="Black", alpha=ease(q))
        text(img, it[0], 260, y - 30, 46, w="ExtraBold", anchor="lm", alpha=ease(q), maxw=720)
        if len(it) > 1: text(img, it[1], 260, y + 32, 34, fill=(205, 195, 225), w="Medium", anchor="lm", alpha=ease(q), maxw=720)
    return img

def sc_bill(t, d, p):
    """Costs piling up in a typical (unnamed) IPTV app."""
    img = BGS["problem"].copy() if not p.get("site") else site_bg((150, 30, 40), cy=0.6, strength=0.25)
    if p.get("site"): header(img)
    oy = 0
    if p.get("site"):
        headline(img, p["hl"], 440, 96, t, red=True); oy = 160
        if p.get("note"): text(img, p["note"], 80, 440 + len(p["hl"]) * 112, 36, fill=(200, 170, 175), w="Medium", anchor="ls")
    else:
        text(img, p.get("title", "What it costs you:"), W/2, 330, 80, w="Black", alpha=ease(prog(t, 0, 0.3)))
        if p.get("note"): text(img, p["note"], W/2, 420, 36, fill=(220, 180, 180), w="Medium", alpha=ease(prog(t, 0.1, 0.4)))
    items = p["items"]; step = (d - 1.6) / max(1, len(items))
    x0, x1 = 110, 970
    for i, (a, b) in enumerate(items):
        q = prog(t, 0.4 + i * step, 0.7 + i * step)
        if q <= 0: continue
        y = 620 + oy + i * 170 + 30 * (1 - ease(q))
        rrect(img, (x0, y - 65, x1, y + 65), 30, (255, 255, 255), alpha=0.07 * ease(q), outline=(255, 120, 120), width=2)
        text(img, a, x0 + 40, y, 44, w="SemiBold", anchor="lm", alpha=ease(q), maxw=560)
        text(img, b, x1 - 40, y, 48, w="Black", anchor="rm", fill=RED, alpha=ease(q))
    q = prog(t, d - 1.3, d - 0.9)
    if q > 0:
        y = 620 + oy + len(items) * 170 + 60
        rrect(img, (x0, y - 4, x1, y), 2, (255, 255, 255), alpha=0.4 * ease(q))
        text(img, p.get("total_label", "Per year:"), x0 + 40, y + 90, 54, w="ExtraBold", anchor="lm", alpha=ease(q))
        text(img, p["total"], x1 - 40, y + 90, int(90 * (0.7 + 0.3 * back(q))), w="Black", anchor="rm", fill=RED, alpha=ease(q))
    return img

# ---------- site style (matches kanalo.app): dark, left-aligned headlines, italic gradient accent ----------
SITE_BG = (10, 10, 15)
_fl = {}
def FL(size):
    if size not in _fl:
        f = ImageFont.truetype(os.path.join(HERE, "assets", "Lora-Italic-Variable.ttf"), size)
        try: f.set_variation_by_name("SemiBold Italic")
        except Exception: pass
        _fl[size] = f
    return _fl[size]

def site_bg(tint=None, cy=0.62, strength=0.35):
    img = Image.new("RGB", (W, H), SITE_BG)
    if tint:
        lay = Image.new("RGB", (W, H), SITE_BG); r = 620
        ImageDraw.Draw(lay).ellipse([W/2 - r, H*cy - r, W/2 + r, H*cy + r], fill=tint)
        img = Image.blend(img, lay.filter(ImageFilter.GaussianBlur(240)), strength)
    return img

def header(img):
    logo(img, 120, 190, 76)
    text(img, "Kanalo", 182, 190, 52, w="Regular", anchor="lm")
    rrect(img, (0, 268, W, 270), 0, (40, 40, 52))

def segs(line):
    out = []; parts = line.split("*")
    for i, ptxt in enumerate(parts):
        if ptxt: out.append((ptxt, i % 2 == 1))
    return out

def headline(img, lines, y, size, t=9.0, instant=False, x=80, gap=1.16, red=False):
    """Lines with *accent* parts (Lora italic, brand gradient, or red for problems). Left aligned like the site."""
    d0 = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        q = 1.0 if instant else ease(prog(t, 0.05 + i * 0.18, 0.4 + i * 0.18))
        if q <= 0: continue
        cx = x; yy = y + i * size * gap + 24 * (1 - q)
        for txt, acc in segs(ln):
            f = FL(int(size * 1.08)) if acc else F(size, "Medium")
            wdt = d0.textlength(txt, font=f)
            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).text((cx, yy), txt, font=f, fill=int(255 * q), anchor="ls")
            if acc and not red:
                bb = mask.getbbox()
                if bb:
                    full = Image.new("RGB", img.size); full.paste(brand_grad(bb[2] - bb[0], bb[3] - bb[1]), (bb[0], bb[1]))
                    img.paste(full, (0, 0), mask)
            else:
                img.paste(Image.new("RGB", img.size, RED if acc else WHITE), (0, 0), mask)
            cx += wdt

def tile(img, box, c, alpha=1.0):
    x0, y0, x1, y1 = [int(v) for v in box]; w, h = x1 - x0, y1 - y0
    g = Image.new("RGB", (1, 256))
    for i in range(256):
        f = i / 255; g.putpixel((0, i), tuple(int(c[j] * (1 - 0.75 * f) + 12 * 0.75 * f) for j in range(3)))
    g = g.resize((w, h)); m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 60, fill=int(255 * alpha)); img.paste(g, (x0, y0), m)

def fake_old_app(img, box, t, price="€4,99 / maand", ad="RECLAME  ·  0:30"):
    """Generic ad-filled player (no real brand): dim video frame, spinner, yellow ad bar, price badge."""
    x0, y0, x1, y1 = box
    rrect(img, (x0 - 16, y0 - 16, x1 + 16, y1 + 16), 58, (36, 34, 44))
    rrect(img, (x0, y0, x1, y1), 44, (22, 20, 28))
    vy1 = y0 + (y1 - y0) * 0.5
    paste_round(img, hgrad(400, 200, (60, 50, 70), (30, 26, 40)), (x0 + 30, y0 + 90, x1 - 30, vy1), 24)
    spinner(img, (x0 + x1) / 2, (y0 + 90 + vy1) / 2, 44, t)
    rrect(img, (x0 + 30, vy1 + 30, x1 - 30, vy1 + 130), 22, (250, 205, 40))
    secs = max(0, 30 - int(t * 2))
    text(img, ad.replace("0:30", f"0:{secs:02d}"), (x0 + x1) / 2, vy1 + 80, 42, fill=(20, 20, 20), w="ExtraBold", maxw=x1 - x0 - 80)
    for k in range(3):
        rrect(img, (x0 + 30, vy1 + 170 + k * 70, x1 - 30 - k * 90, vy1 + 200 + k * 70), 12, (46, 44, 56))
    bx, by = x1 - 20, y0 + 40
    rrect(img, (bx - 330, by - 10, bx + 40, by + 80), 45, RED)
    text(img, price, bx - 145, by + 35, 40, w="ExtraBold", maxw=340)

def sc_s_hook(t, d, p):
    img = site_bg((150, 30, 40), cy=0.72, strength=0.3); header(img)
    headline(img, p["lines"], 470, p.get("size", 104), t, instant=True, red=True)
    fake_old_app(img, (230, 900, 850, 1560), t, p.get("price", "€4,99 / maand"), p.get("ad", "RECLAME  ·  0:30"))
    if p.get("foot"): text(img, p["foot"], W/2, 1680, 46, fill=(215, 205, 230), w="Medium")
    return img

def sc_s_photo(t, d, p):
    img = site_bg((90, 50, 140), cy=0.6, strength=0.25); header(img)
    headline(img, p["lines"], 470, p.get("size", 110), t)
    src = ASSETS[p.get("asset", "site_couch")]; bw = 940; bh = int(bw * src.size[1] / src.size[0])
    y0 = 760 + int(60 * (1 - ease(prog(t, 0, 0.5))))
    paste_round(img, zoomed(src, 1.0 + 0.12 * t / d, 0.5, 0.4), (70, y0, 70 + bw, y0 + bh), 48)
    if p.get("sub"): text(img, p["sub"], 80, y0 + bh + 110, 50, fill=(215, 205, 230), w="Medium", anchor="ls", alpha=ease(prog(t, 0.6, 1.0)))
    return img

def sc_s_device(t, d, p):
    c = tuple(p.get("tint", (50, 50, 170)))
    img = site_bg(); header(img)
    headline(img, p["lines"], 470, p.get("size", 104), t)
    ty0 = 760 + int(60 * (1 - ease(prog(t, 0, 0.5))))
    tile(img, (60, ty0, 1020, ty0 + 820), c)
    src = ASSETS[p.get("asset", "atv_home")]; tw = 860; th = int(tw * src.size[1] / src.size[0])
    x0 = (W - tw) // 2; y0 = ty0 + (820 - th) // 2 - 30
    rrect(img, (x0 - 16, y0 - 16, x0 + tw + 16, y0 + th + 16), 36, (30, 30, 36))
    paste_round(img, zoomed(src, p.get("z0", 1.0) + (p.get("z1", 1.08) - p.get("z0", 1.0)) * t / d, p.get("fx", 0.4), p.get("fy", 0.4)), (x0, y0, x0 + tw, y0 + th), 22)
    rrect(img, (W/2 - 200, y0 + th + 40, W/2 + 200, y0 + th + 52), 6, (30, 30, 36))
    if p.get("label"): text(img, p["label"], W/2, ty0 + 900, 40, fill=(160, 160, 175), w="Regular", alpha=ease(prog(t, 0.4, 0.8)))
    return img

def sc_s_end(t, d, p):
    img = site_bg((110, 50, 140), cy=0.45, strength=0.3)
    headline(img, p.get("lines", ["Gewoon *kijken.*"]), 560, 110, t)
    q = back(prog(t, 0.4, 0.9)); logo(img, W/2 - 150, 1000, 150 * q)
    text(img, "Kanalo", W/2 - 50, 1000, 96, w="Regular", anchor="lm", alpha=ease(prog(t, 0.5, 0.9)))
    q2 = ease(prog(t, 0.9, 1.3))
    text(img, p.get("a", "Gratis · geen reclame · geen account"), W/2, 1180, 40, fill=(205, 195, 225), alpha=q2, w="Medium")
    q3 = ease(prog(t, 1.2, 1.6))
    if q3 > 0:
        rrect(img, (W/2 - 230, 1300, W/2 + 230, 1420), 60, (190, 190, 200), alpha=0.55 * q3)
        text(img, "kanalo.app", W/2, 1360, 60, w="Bold", fill=(12, 12, 16), alpha=q3)
    return img

SOFT = {"en": ("I use Kanalo for this.", "Free · no ads · iPhone, iPad & Apple TV"),
        "nl": ("Ik gebruik hier Kanalo voor.", "Gratis · geen reclame · iPhone, iPad & Apple TV")}
def sc_soft(t, d, p):
    """Calm ending: what you use, no button, no hard sell."""
    a, b = SOFT[p.get("lang", "en")]
    img = BGS["brand"].copy()
    if p.get("top"): text(img, p["top"], W/2, 560, 70, w="Black", alpha=ease(prog(t, 0, 0.35)))
    if p.get("sub"): text(img, p["sub"], W/2, 655, 70, w="Black", grad=True, alpha=ease(prog(t, 0.15, 0.5)))
    logo(img, W/2, 960, 220 * back(prog(t, 0.5, 0.95)))
    q = ease(prog(t, 0.9, 1.3))
    text(img, p.get("a", a), W/2, 1180, 54, alpha=q, w="ExtraBold")
    text(img, p.get("b", b), W/2, 1260, 36, fill=(205, 195, 225), alpha=q, w="Medium")
    text(img, p.get("c", "kanalo.app"), W/2, 1340, 40, alpha=ease(prog(t, 1.3, 1.7)), w="Bold", grad=True)
    return img

SCENES = dict(hook=sc_hook, oldapp=sc_oldapp, wait=sc_wait, reveal=sc_reveal, tv=sc_tv, phone=sc_phone,
              list=sc_list, compare=sc_compare, steps=sc_steps, qr=sc_qr, price=sc_price, cta=sc_cta,
              screen=sc_screen, tips=sc_tips, soft=sc_soft, bill=sc_bill,
              s_hook=sc_s_hook, s_photo=sc_s_photo, s_device=sc_s_device, s_end=sc_s_end)

def frames(video):
    for sc in video["scenes"]:
        fn = SCENES[sc["type"]]; d = sc["dur"]
        for f in range(int(d * FPS)):
            yield fn(f / FPS, d, sc)

def render(video, out_dir):
    final = os.path.join(out_dir, video["id"] + ".mp4"); tmp = final[:-4] + ".tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for im in frames(video): pr.stdin.write(im.tobytes())
    pr.stdin.close()
    if pr.wait() != 0: return None
    if video.get("music", True):
        sys.path.insert(0, HERE); from kanalo_music import make_music
        dur = sum(sc["dur"] for sc in video["scenes"]); wav = final[:-4] + ".wav"
        make_music(wav, dur, seed=video.get("seed", abs(hash(video["id"])) % 997))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", final], check=True)
        os.remove(tmp); os.remove(wav)
    else: os.replace(tmp, final)
    return final

def preview(video, out_dir):
    ims = []
    for sc in video["scenes"]:
        ims.append(SCENES[sc["type"]](sc["dur"] * 0.85, sc["dur"], sc).resize((270, 480)))
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for i, im in enumerate(ims): sheet.paste(im, (i * 270, 0))
    path = os.path.join(out_dir, video["id"] + "_preview.jpg"); sheet.save(path, quality=80); return path

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    only = sys.argv[4] if len(sys.argv) > 4 else None
    for v in spec["videos"]:
        if only and v["id"] not in only.split(","): continue
        print(preview(v, out) if (len(sys.argv) > 3 and sys.argv[3] == "preview") else render(v, out), flush=True)

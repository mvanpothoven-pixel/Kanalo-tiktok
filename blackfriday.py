"""Black Friday promo image. Usage: python3 blackfriday.py OUT_DIR"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import kanalo_video as kv
import device_demo as dd

OLD, NEW, PCT = "€39,99", "€19,99", "-50%"
DATES = "Nov 27 – Nov 30"


def make(W, H):
    img = Image.new("RGB", (W, H), (8, 6, 14))
    glow = Image.new("RGB", (W, H), (8, 6, 14)); g = ImageDraw.Draw(glow)
    g.ellipse([-W * 0.3, H * 0.25, W * 1.3, H * 0.95], fill=(120, 40, 190))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(220)), 0.7).convert("RGBA")
    d = ImageDraw.Draw(img)
    s = H / 1920 if H > 1400 else 0.78
    y = int(150 * s) + (170 if H > 1400 else 0)
    kv.logo(img, W // 2 - int(150 * s), y, int(80 * s))
    d.text((W // 2 - int(95 * s), y), "Kanalo", font=kv.F(int(62 * s), "Bold"), fill="white", anchor="lm")
    y += int(170 * s)
    d.text((W // 2, y), "BLACK FRIDAY", font=kv.F(int(130 * s), "Bold"), fill="white", anchor="mm")
    y += int(110 * s)
    d.text((W // 2, y), "Lifetime Pro", font=kv.F(int(60 * s), "SemiBold"), fill=(255, 205, 110), anchor="mm")
    # device
    tw = int(780 * s); src = kv.ASSETS["atv_home"]; th = int(tw * src.height / src.width)
    cy = y + int(80 * s) + th // 2
    dd.tvset(img, W // 2, cy, tw, th, dd.screen_content(src, tw, th))
    d = ImageDraw.Draw(img)
    # price block
    y = cy + th // 2 + int(200 * s)
    fo = kv.F(int(70 * s), "SemiBold"); ow = fo.getlength(OLD)
    fn = kv.F(int(170 * s), "Bold"); nw = fn.getlength(NEW)
    gap = int(40 * s); x0 = (W - (ow + gap + nw)) / 2
    d.text((x0, y), OLD, font=fo, fill=(170, 160, 185), anchor="lm")
    d.line([(x0 - 4, y), (x0 + ow + 4, y)], fill=(255, 80, 110), width=max(4, int(7 * s)))
    d.text((x0 + ow + gap, y), NEW, font=fn, fill="white", anchor="lm")
    # badge
    bx, by, br = int(W - 190 * s), int(y - 170 * s), int(92 * s)
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=(255, 60, 100))
    d.text((bx, by), PCT, font=kv.F(int(62 * s), "Bold"), fill="white", anchor="mm")
    y += int(140 * s)
    d.text((W // 2, y), "Pay once. No ads. Ever.", font=kv.F(int(52 * s), "SemiBold"), fill="white", anchor="mm")
    y += int(75 * s)
    d.text((W // 2, y), "Ad-free IPTV player for iPhone, iPad & Apple TV", font=kv.F(int(36 * s), "Regular"),
           fill=(215, 205, 230), anchor="mm")
    # pill
    y += int(110 * s); pw, ph = int(560 * s), int(96 * s)
    d.rounded_rectangle([(W - pw) / 2, y - ph / 2, (W + pw) / 2, y + ph / 2], ph // 2, fill="white")
    d.text((W // 2, y), DATES + " only", font=kv.F(int(44 * s), "Bold"), fill=(20, 14, 30), anchor="mm")
    return img.convert("RGB")


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    make(1080, 1920).save(f"{out}/blackfriday_9x16.png")
    make(1080, 1350).save(f"{out}/blackfriday_4x5.png")
    print("ok")

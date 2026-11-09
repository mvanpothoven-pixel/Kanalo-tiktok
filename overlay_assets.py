"""Clean overlays for AI videos: a sharp, real Kanalo phone mockup + branded end card.
The AI model garbles app UIs, so the real app is composited over it in post."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import kanalo_video as kv

OUT = sys.argv[1] if len(sys.argv) > 1 else "overlays"
os.makedirs(OUT, exist_ok=True)
GREY = (170, 168, 185)


def phone_mock(screen, width=520, tilt=0):
    s = screen
    h = int(width * s.height / s.width)
    pad = 90; bez = 18
    W, H = width + 2 * (pad + bez), h + 2 * (pad + bez)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # soft purple glow + shadow
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).rounded_rectangle([pad - 10, pad + 20, W - pad + 10, H - pad + 30], 90, fill=(20, 0, 40, 200))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(38)))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(gl).rounded_rectangle([pad, pad, W - pad, H - pad], 90, outline=(190, 90, 255, 160), width=14)
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([pad, pad, W - pad, H - pad], 86, fill=(18, 17, 24, 255))
    d.rounded_rectangle([pad + 3, pad + 3, W - pad - 3, H - pad - 3], 84, outline=(70, 68, 82, 255), width=3)
    m = Image.new("L", (width, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, width - 1, h - 1], 70, fill=255)
    img.paste(s.resize((width, h), Image.LANCZOS).convert("RGBA"), (pad + bez, pad + bez), m)
    # dynamic island
    iw = int(width * 0.3)
    d.rounded_rectangle([W / 2 - iw / 2, pad + bez + 16, W / 2 + iw / 2, pad + bez + 16 + int(width * 0.085)], 40, fill=(0, 0, 0, 255))
    if tilt:
        img = img.rotate(tilt, resample=Image.BICUBIC, expand=True)
    return img


def badge(text, size=46):
    f = kv.F(size, "Bold")
    tw = ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(text, font=f)
    ic = int(size * 1.6); padx = 26
    W = int(ic + 18 + tw + padx * 2 + 10); H = ic + 28
    img = Image.new("RGBA", (W + 60, H + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([30, 38, 30 + W, 38 + H], H // 2, fill=(0, 0, 0, 150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(img).rounded_rectangle([30, 30, 30 + W, 30 + H], H // 2, fill=(255, 255, 255, 255))
    lg = kv.load("logo.png").resize((ic, ic), Image.LANCZOS)
    lm = Image.new("L", (ic, ic), 0); ImageDraw.Draw(lm).rounded_rectangle([0, 0, ic - 1, ic - 1], int(ic * 0.23), fill=255)
    img.paste(lg, (30 + padx - 10, 30 + 14), lm)
    ImageDraw.Draw(img).text((30 + padx - 10 + ic + 18, 30 + H / 2), text, font=f, fill=(20, 18, 28), anchor="lm")
    return img


END = {
    "en": ("IPTV without the ads.", "Free on the", "App Store"),
    "nl": ("IPTV zonder reclame.", "Gratis in de", "App Store"),
    "fr": ("L'IPTV sans les pubs.", "Gratuit sur l'", "App Store"),
    "de": ("IPTV ohne Werbung.", "Kostenlos im", "App Store"),
    "es": ("IPTV sin anuncios.", "Gratis en la", "App Store"),
    "it": ("IPTV senza pubblicità.", "Gratis sull'", "App Store"),
}


def endcard(lang):
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), kv.SITE_BG)
    lay = Image.new("RGB", (W, H), kv.SITE_BG); r = 760
    ImageDraw.Draw(lay).ellipse([W / 2 - r, 760 - r, W / 2 + r, 760 + r], fill=(150, 55, 210))
    img = Image.blend(img, lay.filter(ImageFilter.GaussianBlur(260)), 0.5)
    # big app icon with glow
    ic = 340; x0 = (W - ic) // 2; y0 = 330
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(gl).rounded_rectangle([x0 - 10, y0 - 10, x0 + ic + 10, y0 + ic + 10], 90, fill=(220, 80, 255, 170))
    img = img.convert("RGBA"); img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(60)))
    lg = kv.load("logo.png").resize((ic, ic), Image.LANCZOS)
    lm = Image.new("L", (ic, ic), 0); ImageDraw.Draw(lm).rounded_rectangle([0, 0, ic - 1, ic - 1], 78, fill=255)
    img.paste(lg, (x0, y0), lm); img = img.convert("RGB")
    kv.text(img, "Kanalo", W / 2, y0 + ic + 120, 128, w="Bold")
    tag, l1, l2 = END[lang]
    kv.text(img, tag, W / 2, y0 + ic + 230, 54, fill=GREY, w="Regular")
    # app store pill
    py = 1180; pw = 760; ph = 170
    kv.rrect(img, (W / 2 - pw / 2, py, W / 2 + pw / 2, py + ph), ph // 2, kv.WHITE)
    kv.text(img, l1, W / 2, py + 56, 40, fill=(90, 88, 100), w="Medium")
    kv.text(img, l2, W / 2, py + 114, 64, fill=(16, 14, 22), w="Bold")
    kv.text(img, "iPhone · iPad · Apple TV", W / 2, py + ph + 90, 40, fill=GREY, w="Regular")
    return img


if __name__ == "__main__":
    phone_mock(kv.load("as_movies.png")).save(os.path.join(OUT, "phone_movies.png"))
    phone_mock(kv.load("iphone_detail.png")).save(os.path.join(OUT, "phone_detail.png"))
    for lg, t in {"en": "No ads. Ever.", "nl": "Nooit reclame.", "fr": "Zéro pub.", "de": "Keine Werbung.",
                  "es": "Sin anuncios.", "it": "Zero pubblicità."}.items():
        badge(t).save(os.path.join(OUT, f"badge_{lg}.png"))
        endcard(lg).save(os.path.join(OUT, f"end_{lg}.png"))
    print("ok")

"""Overlays for 'My ex IPTV apps' video: fake (invented) bad apps + Kanalo as the one he married.
Usage: python3 ex_overlays.py OUT_DIR"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import kanalo_video as kv
from chat_breakup import draw_rich, text_w, emoji_img

W, H = 1080, 1920
T = {
 "en": ("My ex IPTV apps 💔", ["ads every 5 min", "wanted my password", "always buffering"], "…and this one I married 💍"),
 "fr": ("Mes ex applis IPTV 💔", ["une pub toutes les 5 min", "voulait mon mot de passe", "toujours en chargement"], "…et elle, je l'ai épousée 💍"),
 "es": ("Mis ex apps de IPTV 💔", ["anuncios cada 5 min", "quería mi contraseña", "siempre cargando"], "…y con esta me casé 💍"),
 "de": ("Meine Ex-IPTV-Apps 💔", ["alle 5 Min. Werbung", "wollte mein Passwort", "lädt ständig"], "…und die hab ich geheiratet 💍"),
 "nl": ("Mijn ex-IPTV-apps 💔", ["elke 5 min reclame", "wilde mijn wachtwoord", "altijd aan het laden"], "…en met deze ben ik getrouwd 💍"),
}
APPS = [("AdPlayer", "📺", (200, 50, 60), (120, 20, 30)), ("LoginTV", "🔑", (230, 150, 40), (150, 80, 10)), ("BufferBox", "⏳", (90, 90, 110), (40, 40, 55))]


def pill(img, s, cx, y, size=52, fg=(15, 14, 22, 255), bg=(255, 255, 255, 245)):
    f = kv.F(size, "Bold"); tw = text_w(s, f, size); pw, ph = tw + 64, int(size * 1.7)
    d = ImageDraw.Draw(img); x0 = max(20, min(W - 20 - pw, cx - pw / 2))
    d.rounded_rectangle([x0, y, x0 + pw, y + ph], ph // 2, fill=bg)
    draw_rich(img, (x0 + 32, y + ph / 2 + size * 0.36), s, f, size, fg)


def icon(name, emo, c1, c2, s=230, cross=False):
    im = Image.new("RGBA", (s + 80, s + 80), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 52, 40 + s, 52 + s], int(s * .23), fill=(0, 0, 0, 160))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    g = Image.new("RGBA", (s, s)); gd = ImageDraw.Draw(g)
    for y in range(s):
        f = y / s; gd.line([(0, y), (s, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * f) for i in range(3)) + (255,))
    m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, s - 1, s - 1], int(s * .23), fill=255)
    im.paste(g, (40, 40), m)
    e = emoji_img(emo, int(s * .5)); im.alpha_composite(e, (40 + (s - e.width) // 2, 40 + int(s * .16)))
    ImageDraw.Draw(im).text((40 + s / 2, 40 + s * .86), name, font=kv.F(int(s * .13), "Bold"), fill="white", anchor="mm")
    if cross:
        d = ImageDraw.Draw(im); w = 22
        d.line([(55, 55), (25 + s, 25 + s)], fill=(255, 45, 60, 235), width=w)
        d.line([(25 + s, 55), (55, 25 + s)], fill=(255, 45, 60, 235), width=w)
    return im


def kanalo_icon(s=300):
    im = Image.new("RGBA", (s + 120, s + 120), (0, 0, 0, 0))
    gl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(gl).rounded_rectangle([50, 50, 70 + s, 70 + s], int(s * .25), fill=(230, 80, 255, 200))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(28)))
    lg = kv.load("logo.png").resize((s, s), Image.LANCZOS)
    m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, s - 1, s - 1], int(s * .23), fill=255)
    im.paste(lg, (60, 60), m)
    for i, (dx, dy, sz) in enumerate([(-10, 10, 70), (s + 60, 30, 60), (s + 40, s + 40, 54)]):
        h = emoji_img("❤", sz); im.alpha_composite(h, (max(0, dx), dy))
    return im


POS = [(65, 380), (745, 260), (195, 70)]  # icon top-lefts (icon canvas 310 px)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for lg, (hook, caps, fin) in T.items():
        h = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pill(h, hook, W / 2, 210, 62); h.save(f"{out}/ex_hook_{lg}.png")
        for i, ((name, emo, c1, c2), cap) in enumerate(zip(APPS, caps)):
            for cross in (False, True):
                im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x, y = POS[i]
                im.alpha_composite(icon(name, emo, c1, c2, s=190, cross=cross), (x, y))
                im.save(f"{out}/ex_a{i}{'x' if cross else ''}_{lg}.png")
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pill(c, cap, W / 2, 1290, 52, fg=(255, 255, 255, 255), bg=(20, 20, 26, 230)); c.save(f"{out}/ex_c{i}_{lg}.png")
        f = Image.new("RGBA", (W, H), (0, 0, 0, 0)); k = kanalo_icon(210); f.alpha_composite(k, ((W - k.width) // 2, 130))
        pill(f, fin, W / 2, 1290, 56); f.save(f"{out}/ex_fin_{lg}.png")
    print("ok")

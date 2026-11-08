"""App Store screenshots for Kanalo (6.9" iPhone, 1320x2868) in the kanalo.app style."""
import os, sys, json
from PIL import Image, ImageDraw, ImageFilter
import kanalo_video as kv

W, H = 1320, 2868
HERE = os.path.dirname(os.path.abspath(__file__))
A = kv.ASSETS
GREY = (170, 168, 185)


def bg(tint):
    img = Image.new("RGB", (W, H), kv.SITE_BG)
    lay = Image.new("RGB", (W, H), kv.SITE_BG); r = 900
    ImageDraw.Draw(lay).ellipse([W / 2 - r, H * 0.66 - r, W / 2 + r, H * 0.66 + r], fill=tint)
    return Image.blend(img, lay.filter(ImageFilter.GaussianBlur(320)), 0.42)


def head(img, l1, l2, sub, size=124):
    kv.logo(img, 132, 170, 84)
    kv.text(img, "Kanalo", 196, 170, 56, w="Regular", anchor="lm")
    d = ImageDraw.Draw(img); x = 96
    f1 = kv.F(size, "Medium"); f2 = kv.FL(int(size * 1.1))
    while max(d.textlength(l1, font=f1), d.textlength(l2, font=f2)) > W - 2 * x:
        size -= 4; f1 = kv.F(size, "Medium"); f2 = kv.FL(int(size * 1.1))
    y1 = 420; y2 = y1 + int(size * 1.18)
    d.text((x, y1), l1, font=f1, fill=kv.WHITE, anchor="ls")
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).text((x, y2), l2, font=f2, fill=255, anchor="ls")
    bb = m.getbbox(); full = Image.new("RGB", img.size)
    full.paste(kv.brand_grad(bb[2] - bb[0], bb[3] - bb[1]), (bb[0], bb[1])); img.paste(full, (0, 0), m)
    kv.text(img, sub, x, y2 + 110, 50, fill=GREY, w="Regular", anchor="ls", maxw=W - 2 * x)


def phone(img, src, top, width=900, crop_top=0):
    s = src
    if crop_top: s = s.crop((0, int(s.height * crop_top), s.width, s.height))
    h = int(width * s.height / s.width); x0 = (W - width) // 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0 - 10, top + 30, x0 + width + 10, top + h + 60], 110, fill=(0, 0, 0, 170))
    img.paste(sh.filter(ImageFilter.GaussianBlur(40)), (0, 0), sh.filter(ImageFilter.GaussianBlur(40)))
    kv.rrect(img, (x0 - 16, top - 16, x0 + width + 16, top + h + 16), 112, (28, 27, 36))
    kv.paste_round(img, s, (x0, top, x0 + width, top + h), 98)


def tv(img, src, top, width=1220):
    h = int(width * src.height / src.width); x0 = (W - width) // 2
    kv.rrect(img, (x0 - 18, top - 18, x0 + width + 18, top + h + 18), 34, (24, 23, 30))
    kv.paste_round(img, src, (x0, top, x0 + width, top + h), 20)
    kv.rrect(img, (W / 2 - 150, top + h + 18, W / 2 + 150, top + h + 34), 8, (40, 39, 48))
    return top + h


def shot1(t):
    img = bg((150, 60, 200)); head(img, *t); phone(img, A["iphone_detail"], 900, 860); return img

def shot2(t):
    img = bg((70, 70, 210)); head(img, *t)
    y = tv(img, A["atv_gids"], 1000)
    phone(img, A["as_movies"], y + 160, 620); return img

def shot3(t):
    img = bg((120, 50, 190)); head(img, *t)
    y = tv(img, A["atv_home"], 1000)
    q = kv.qr_img().resize((300, 300), Image.NEAREST); x0 = (W - 340) // 2; qy = 1000 + (y - 1000) // 2 - 170
    kv.rrect(img, (x0, qy, x0 + 340, qy + 340), 28, kv.WHITE); img.paste(q, (x0 + 20, qy + 20))
    kv.text(img, SCAN.get(LANG, "Scan to sign in"), W / 2, qy + 390, 40, w="Medium")
    phone(img, A["iphone_detail"], y + 200, 560, crop_top=0.0); return img

def shot4(t):
    img = bg((170, 50, 130)); head(img, *t); phone(img, A["as_detail"], 860, 1000); return img

def shot5(t):
    img = bg((60, 90, 200)); head(img, *t); phone(img, A["as_manage"], 860, 1000); return img

def shot6(t):
    img = bg((140, 50, 170)); head(img, *t); phone(img, A["as_subs"], 860, 1000); return img


TEXT = {
 "en": [("IPTV without", "the ads.", "Your playlist. No ads. No account."),
        ("Your TV guide,", "always loaded.", "Fast guide on iPhone, iPad & Apple TV."),
        ("Apple TV login?", "Just scan.", "Sign in with a QR code from your iPhone."),
        ("Movies & series,", "beautifully sorted.", "Posters, trailers and details for everything."),
        ("Only the channels", "you want.", "Hide, rename and lock groups in seconds."),
        ("Subtitles, AirPlay", "& picture-in-picture.", "Everything you expect from a great player.")],
 "nl": [("IPTV zonder", "reclame.", "Jouw playlist. Geen reclame. Geen account."),
        ("Je tv-gids,", "altijd geladen.", "Snelle gids op iPhone, iPad en Apple TV."),
        ("Inloggen op Apple TV?", "Gewoon scannen.", "Log in met een QR-code vanaf je iPhone."),
        ("Films en series,", "mooi geordend.", "Posters, trailers en info bij alles."),
        ("Alleen de zenders", "die jij wilt.", "Groepen verbergen, hernoemen en vergrendelen."),
        ("Ondertitels, AirPlay", "& beeld-in-beeld.", "Alles wat je van een goede speler verwacht.")],
 "fr": [("L'IPTV sans", "les pubs.", "Ta playlist. Zéro pub. Sans compte."),
        ("Ton guide TV,", "toujours chargé.", "Guide rapide sur iPhone, iPad et Apple TV."),
        ("Connexion Apple TV ?", "Il suffit de scanner.", "Connecte-toi avec un QR code depuis ton iPhone."),
        ("Films et séries,", "joliment rangés.", "Affiches, bandes-annonces et infos pour tout."),
        ("Seulement les chaînes", "que tu veux.", "Masque, renomme et verrouille tes groupes."),
        ("Sous-titres, AirPlay", "& image dans l'image.", "Tout ce qu'on attend d'un bon lecteur.")],
 "de": [("IPTV ohne", "Werbung.", "Deine Playlist. Keine Werbung. Kein Konto."),
        ("Dein TV-Guide,", "immer geladen.", "Schneller Guide auf iPhone, iPad & Apple TV."),
        ("Apple TV Login?", "Einfach scannen.", "Per QR-Code vom iPhone anmelden."),
        ("Filme & Serien,", "schön sortiert.", "Poster, Trailer und Infos zu allem."),
        ("Nur die Sender,", "die du willst.", "Gruppen ausblenden, umbenennen, sperren."),
        ("Untertitel, AirPlay", "& Bild-in-Bild.", "Alles, was ein guter Player können muss.")],
 "es": [("IPTV sin", "anuncios.", "Tu playlist. Sin anuncios. Sin cuenta."),
        ("Tu guía de TV,", "siempre cargada.", "Guía rápida en iPhone, iPad y Apple TV."),
        ("¿Login en Apple TV?", "Solo escanea.", "Inicia sesión con un QR desde tu iPhone."),
        ("Pelis y series,", "bien ordenadas.", "Carteles, tráilers y detalles de todo."),
        ("Solo los canales", "que quieres.", "Oculta, renombra y bloquea grupos."),
        ("Subtítulos, AirPlay", "e imagen en imagen.", "Todo lo que esperas de un gran reproductor.")],
 "it": [("IPTV senza", "pubblicità.", "La tua playlist. Zero pubblicità. Nessun account."),
        ("La tua guida TV,", "sempre pronta.", "Guida veloce su iPhone, iPad e Apple TV."),
        ("Login su Apple TV?", "Basta scansionare.", "Accedi con un QR code dal tuo iPhone."),
        ("Film e serie,", "ben ordinati.", "Locandine, trailer e dettagli per tutto."),
        ("Solo i canali", "che vuoi tu.", "Nascondi, rinomina e blocca i gruppi."),
        ("Sottotitoli, AirPlay", "e picture-in-picture.", "Tutto ciò che ti aspetti da un ottimo player.")],
}
LANG = "en"
SCAN = {"en": "Scan to sign in", "nl": "Scan om in te loggen", "fr": "Scanne pour te connecter", "de": "Zum Anmelden scannen", "es": "Escanea para entrar", "it": "Scansiona per accedere"}
SHOTS = [shot1, shot2, shot3, shot4, shot5, shot6]

if __name__ == "__main__":
    out = sys.argv[1]; langs = sys.argv[2].split(",") if len(sys.argv) > 2 else list(TEXT)
    for lg in langs:
        LANG = lg
        os.makedirs(os.path.join(out, lg), exist_ok=True)
        for i, (fn, t) in enumerate(zip(SHOTS, TEXT[lg]), 1):
            p = os.path.join(out, lg, f"{i:02d}.png"); fn(t).save(p); print(p)

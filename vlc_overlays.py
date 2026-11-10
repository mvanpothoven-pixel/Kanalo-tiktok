"""Text overlays + music for the 'I stopped doing the VLC trick' video (AI couch + app walkthrough)."""
import os, sys
from PIL import Image, ImageDraw
import kanalo_video as kv
import kanalo_music as km
from chat_breakup import draw_rich, text_w

W, H = 1080, 1920
HOOK = {
    "en": ("I stopped doing the VLC trick", "this is what I use now 👇"),
    "nl": ("Ik ben gestopt met de VLC-truc", "dit gebruik ik nu 👇"),
    "fr": ("J'ai arrêté l'astuce VLC", "voilà ce que j'utilise 👇"),
    "de": ("Ich hab den VLC-Trick aufgegeben", "das nutze ich jetzt 👇"),
    "es": ("Dejé el truco de VLC", "esto es lo que uso ahora 👇"),
}
OUTRO = {
    "en": "Own playlist. Zero ads. Done.",
    "nl": "Eigen playlist. Geen reclame. Klaar.",
    "fr": "Ta playlist. Zéro pub. C'est tout.",
    "de": "Eigene Playlist. Keine Werbung. Fertig.",
    "es": "Tu playlist. Cero anuncios. Listo.",
}


def card(lines, size=64, y=300):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = kv.F(size, "Bold")
    while max(text_w(l, f, size) for l in lines) > W - 200: size -= 2; f = kv.F(size, "Bold")
    lh = int(size * 1.3); bw = max(text_w(l, f, size) for l in lines) + 90; bh = lh * len(lines) + 60
    d.rounded_rectangle([(W - bw) / 2, y, (W + bw) / 2, y + bh], 36, fill=(255, 255, 255, 245))
    for i, l in enumerate(lines):
        tw = text_w(l, f, size)
        draw_rich(img, ((W - tw) / 2, y + 30 + lh * i + size * 0.95), l, f, size, (15, 14, 22, 255))
    return img


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for lg in HOOK:
        card(HOOK[lg]).save(os.path.join(out, f"vlc_hook_{lg}.png"))
        card([OUTRO[lg]], size=58).save(os.path.join(out, f"vlc_outro_{lg}.png"))
    km.make_music(os.path.join(out, "vlc_music.wav"), 18.5, seed=23)
    print("ok")

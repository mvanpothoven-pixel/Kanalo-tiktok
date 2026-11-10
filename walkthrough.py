"""Clean app walkthrough segment (demo screens only) for mixed AI + app videos.
Usage: python3 walkthrough.py LANG OUT.mp4"""
import os, sys, subprocess
from PIL import Image, ImageDraw
import kanalo_video as kv
import overlay_assets as oa
import guide_screen as gs

W, H, FPS = 1080, 1920, 30
CAP = {
    "en": ["Add your own playlist", "Full TV guide", "Movies & series, sorted", "Zero ads. Ever."],
    "nl": ["Voeg je eigen playlist toe", "Complete tv-gids", "Films & series, netjes", "Nooit reclame."],
    "fr": ["Ajoute ta propre playlist", "Guide TV complet", "Films & séries, bien rangés", "Zéro pub. Jamais."],
    "de": ["Eigene Playlist hinzufügen", "Kompletter TV-Guide", "Filme & Serien, sortiert", "Keine Werbung. Nie."],
    "es": ["Añade tu propia playlist", "Guía de TV completa", "Pelis y series, ordenadas", "Cero anuncios. Nunca."],
}
SEG = 1.7


def screens(lang):
    return [kv.load("rec_settings.png"), gs.render("nl" if lang == "nl" else "en"), kv.load("as_movies.png"), kv.load("iphone_detail.png")]


def render(lang, out):
    bg = kv.glow_bg((120, 45, 190), cy=0.62, strength=0.55)
    mocks = []
    for s in screens(lang):
        m = oa.phone_mock(s.convert("RGB"), width=640, island=False)
        if m.height > 1500:
            r = 1500 / m.height; m = m.resize((int(m.width * r), 1500), Image.LANCZOS)
        mocks.append(m)
    caps = CAP[lang]; n = len(mocks); dur = n * SEG
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        t = i / FPS; k = min(n - 1, int(t // SEG)); lt = t - k * SEG
        img = bg.copy().convert("RGBA")
        # slide transition: incoming from right during first 0.28s
        e = kv.ease(kv.prog(lt, 0, 0.28)) if k > 0 else 1.0
        if k > 0 and e < 1:
            prev = mocks[k - 1]; x = int((W - prev.width) / 2 - e * W)
            img.alpha_composite(prev, (x, 330))
        m = mocks[k]; x = int((W - m.width) / 2 + (1 - e) * W)
        sc = 1 + 0.03 * kv.prog(lt, 0, SEG)
        mm = m.resize((int(m.width * sc), int(m.height * sc))) if sc != 1 else m
        img.alpha_composite(mm, (x - (mm.width - m.width) // 2, 330))
        img = img.convert("RGB")
        # caption pill
        a = kv.ease(kv.prog(lt, 0.1, 0.35))
        if a > 0:
            f = kv.F(66, "Bold"); d = ImageDraw.Draw(img); s = caps[k]
            tw = d.textlength(s, font=f); pw = tw + 90
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([(W - pw) / 2, 190, (W + pw) / 2, 310], 60, fill=(255, 255, 255, int(245 * a)))
            od.text((W / 2, 250), s, font=f, fill=(15, 14, 22, int(255 * a)), anchor="mm")
            img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait(); print(out, dur)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])

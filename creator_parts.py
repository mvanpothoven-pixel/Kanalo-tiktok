"""Parts for creator videos (AI creator talking to camera + real Kanalo app demo + end card).
Renders per language: demo segment (silent mp4, real app screens on a device, no lighthouse home screen),
hook card (top), end overlay is reused from pub/fun/end_<lang>.png, music bed mp3.
Usage: python3 creator_parts.py OUT_DIR"""
import os, sys, subprocess
from PIL import Image
import device_demo as dd
from vlc_overlays import card

FPS = 30
DEMO = {  # lang: (device, screens, line on screen, scroll)
 "fr": ("phone", ["iphone_detail"], "Ta playlist.\nZéro pub.", True),
 "de": ("tv", ["atv_movies", "atv_gids"], "Deine Playlist.\nNull Werbung.", False),
 "es": ("combo", ["atv_movies", "iphone_detail"], "Tu playlist.\nCero anuncios.", False),
 "it": ("phone", ["as_movies", "as_subs"], "La tua playlist.\nZero pubblicità.", False),
 "en": ("tv", ["atv_gids", "atv_movies"], "Your playlist.\nZero ads.", False),
 "nl": ("phone", ["iphone_gids"], "Je eigen playlist.\nNul reclame.", True),
}
HOOK = {
 "fr": ["Une appli IPTV SANS pub ?! 😳", "+ 1 an de Pro offert 🎁"],
 "de": ["Eine IPTV-App OHNE Werbung?! 😳", "+ 1 Jahr Pro geschenkt 🎁"],
 "es": ["¿Una app IPTV SIN anuncios?! 😳", "+ 1 año de Pro gratis 🎁"],
 "it": ["Un'app IPTV SENZA pubblicità?! 😳", "+ 1 anno di Pro in regalo 🎁"],
 "en": ["An IPTV app with ZERO ads?! 😳", "+ a free year of Pro 🎁"],
 "nl": ["Een IPTV-app ZONDER reclame?! 😳", "+ 1 jaar Pro gratis 🎁"],
}
MUSIC = {"fr": ("lofi", 51), "de": ("synthwave", 52), "es": ("afro", 53), "it": ("lofi", 54), "en": ("phonk", 55), "nl": ("afro", 56)}

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for lg, (dev, scr, line, scroll) in DEMO.items():
        v = dict(id=f"demo_{lg}", dev=dev, screens=scr, dur=4.0, hook=line, scroll=scroll)
        path = os.path.join(out, f"demo_{lg}.mp4")
        p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
        for i in range(int(4.0 * FPS)):
            p.stdin.write(dd.frame(v, 0.9 + i / FPS).convert("RGB").tobytes())   # start after the intro rise
        p.stdin.close(); p.wait()
        card(HOOK[lg], size=62, y=300).save(os.path.join(out, f"hook_{lg}.png"))
        st, seed = MUSIC[lg]; wav = os.path.join(out, f"music_{lg}.wav")
        subprocess.run([sys.executable, "music_styles.py", st, wav, "15", str(seed)], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-c:a", "libmp3lame", "-b:a", "160k", wav[:-4] + ".mp3"], check=True); os.remove(wav)
        print(lg)

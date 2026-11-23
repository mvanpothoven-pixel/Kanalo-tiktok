"""Overlays + music for the fun AI-skit videos (weeks/fun-*.json).
Per video: hook card, payoff card (white TikTok-style boxes), end overlay (logo + 'free on the App Store'), music wav.
Usage: python3 fun_overlays.py weeks/fun-2026-11-26.json pub/fun
"""
import os, sys, json, subprocess
from PIL import Image
import kanalo_video as kv
from vlc_overlays import card

W, H = 1080, 1920
FREE = {"en": "Free on the App Store", "nl": "Gratis in de App Store", "fr": "Gratuit sur l'App Store",
        "de": "Gratis im App Store", "es": "Gratis en la App Store", "it": "Gratis sull'App Store"}
SUB = {"en": "Your own playlist · zero ads", "nl": "Je eigen playlist · nul reclame", "fr": "Ta propre playlist · zéro pub",
       "de": "Deine eigene Playlist · null Werbung", "es": "Tu propia playlist · cero anuncios", "it": "La tua playlist · zero pubblicità"}


def end_overlay(lang):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kv.logo(img, W // 2, 760, 220)
    kv.text(img, "Kanalo", W // 2, 990, 120, w="Bold")
    kv.text(img, SUB[lang], W // 2, 1100, 48, w="Medium", fill=(225, 220, 240))
    pill = card([FREE[lang]], size=60, y=1200)
    img.alpha_composite(pill)
    return img


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))["videos"]; out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    for lg in FREE: end_overlay(lg).save(os.path.join(out, f"end_{lg}.png"))
    for v in spec:
        card(v["hook"], size=64, y=330).save(os.path.join(out, v["id"] + "_hook.png"))
        card(v["payoff"], size=64, y=330).save(os.path.join(out, v["id"] + "_pay.png"))
        wav = os.path.join(out, v["id"] + ".wav")
        if v["music"] == "house":
            subprocess.run([sys.executable, "house_music.py", wav, "10.6", str(v["seed"])], check=True, stdout=subprocess.DEVNULL)
        else:
            subprocess.run([sys.executable, "music_styles.py", v["music"], wav, "10.6", str(v["seed"])], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-c:a", "libmp3lame", "-b:a", "160k", wav[:-4] + ".mp3"], check=True)
        os.remove(wav)
    print("ok")

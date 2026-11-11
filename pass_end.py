"""End card for the 250 lifetime pass giveaway: Kanalo logo + how to claim. Usage: python3 pass_end.py OUT_DIR"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import kanalo_video as kv

W, H = 1080, 1920
T = {
    "nl": ("Zo claim je je pass", ["Ga naar kanalo.app", "Claim je gratis code", "Download Kanalo & activeer"], "Op = op · max. 250", "Link in bio 👆"),
    "en": ("How to claim your pass", ["Go to kanalo.app", "Claim your free code", "Download Kanalo & redeem"], "First 250 only", "Link in bio 👆"),
    "fr": ("Comment obtenir ton pass", ["Va sur kanalo.app", "Récupère ton code gratuit", "Télécharge Kanalo et active"], "Seulement les 250 premiers", "Lien en bio 👆"),
    "es": ("Cómo conseguir tu pase", ["Entra en kanalo.app", "Consigue tu código gratis", "Descarga Kanalo y actívalo"], "Solo los 250 primeros", "Enlace en la bio 👆"),
    "de": ("So holst du deinen Pass", ["Geh auf kanalo.app", "Hol dir deinen Gratis-Code", "Kanalo laden & einlösen"], "Nur die ersten 250", "Link in der Bio 👆"),
}

def card(lang):
    title, steps, note, cta = T[lang]
    img = kv.glow_bg((120, 45, 190), cy=0.35, strength=0.6).convert("RGBA")
    d = ImageDraw.Draw(img)
    s = 230
    lg = kv.load("logo.png").resize((s, s), Image.LANCZOS)
    m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, s - 1, s - 1], int(s * .23), fill=255)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).rounded_rectangle([(W - s) / 2 - 20, 250, (W + s) / 2 + 20, 250 + s + 40], 70, fill=(230, 80, 255, 150))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    img.paste(lg, ((W - s) // 2, 270), m)
    d.text((W / 2, 600), "Kanalo", font=kv.F(96, "Bold"), fill="white", anchor="mm")
    d.text((W / 2, 690), "Lifetime Pro Pass", font=kv.F(46, "SemiBold"), fill=(255, 205, 110), anchor="mm")
    d.text((W / 2, 830), title, font=kv.F(52, "Bold"), fill="white", anchor="mm")
    for i, st in enumerate(steps):
        y = 940 + i * 130
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).rounded_rectangle([110, y - 52, W - 110, y + 52], 52, fill=(255, 255, 255, 34))
        img.alpha_composite(ov); d = ImageDraw.Draw(img)
        d.ellipse([140, y - 36, 212, y + 36], fill=(255, 205, 110))
        d.text((176, y), str(i + 1), font=kv.F(40, "Bold"), fill=(30, 20, 40), anchor="mm")
        d.text((240, y), st, font=kv.F(42, "SemiBold"), fill="white", anchor="lm")
    d.text((W / 2, 1360), note, font=kv.F(38, "Regular"), fill=(220, 210, 235), anchor="mm")
    f = kv.F(56, "Bold"); pw = 640
    d.rounded_rectangle([(W - pw) / 2, 1440, (W + pw) / 2, 1560], 60, fill="white")
    from chat_breakup import draw_rich, text_w
    tw = text_w(cta, f, 56)
    draw_rich(img, ((W - tw) / 2, 1500 + 56 * 0.36), cta, f, 56, (20, 14, 30, 255))
    return img.convert("RGB")

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for lg in T:
        card(lg).save(f"{out}/pass_end_{lg}.png")
    print("ok")

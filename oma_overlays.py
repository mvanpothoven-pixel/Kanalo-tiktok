"""Overlays for 'Grandma is faster' video. Usage: python3 oma_overlays.py OUT_DIR"""
import os, sys
from vlc_overlays import card

HOOK = {
    "en": ["My grandma (78) set up IPTV", "faster than me 💀"],
    "nl": ["Mijn oma (78) had IPTV", "sneller werkend dan ik 💀"],
    "fr": ["Ma grand-mère (78 ans) a lancé", "l'IPTV plus vite que moi 💀"],
    "es": ["Mi abuela (78) puso el IPTV", "más rápido que yo 💀"],
    "de": ["Oma (78) hatte IPTV", "schneller am Laufen als ich 💀"],
}
PAY = {
    "en": ["She just uses Kanalo.", "No ads. No hassle."],
    "nl": ["Ze gebruikt gewoon Kanalo.", "Geen reclame. Geen gedoe."],
    "fr": ["Elle utilise juste Kanalo.", "Zéro pub. Zéro prise de tête."],
    "es": ["Ella usa Kanalo.", "Sin anuncios. Sin líos."],
    "de": ["Sie nutzt einfach Kanalo.", "Keine Werbung. Kein Stress."],
}

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for lg in HOOK:
        card(HOOK[lg], size=62, y=1110).save(f"{out}/oma_hook_{lg}.png")
        card(PAY[lg], size=58, y=1110).save(f"{out}/oma_pay_{lg}.png")
    print("ok")

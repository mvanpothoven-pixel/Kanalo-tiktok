"""Overlays for 'Grandma is faster' video. Usage: python3 oma_overlays.py OUT_DIR"""
import os, sys
from vlc_overlays import card

HOOK = {
    "en": ["POV: your IPTV app plays", "4 ads. Again. 😤"],
    "nl": ["POV: je IPTV-app geeft", "wéér 4 reclames 😤"],
    "fr": ["POV : ton appli IPTV te met", "encore 4 pubs 😤"],
    "es": ["POV: tu app de IPTV te pone", "otra vez 4 anuncios 😤"],
    "de": ["POV: deine IPTV-App zeigt", "schon wieder 4 Werbungen 😤"],
}
PAY = {
    "en": ["Grandma (78) just uses Kanalo 👵", "No ads. Ever."],
    "nl": ["Oma (78) gebruikt gewoon Kanalo 👵", "Geen reclame. Nooit."],
    "fr": ["Mamie (78 ans) utilise Kanalo 👵", "Zéro pub. Jamais."],
    "es": ["La abuela (78) usa Kanalo 👵", "Sin anuncios. Nunca."],
    "de": ["Oma (78) nutzt einfach Kanalo 👵", "Keine Werbung. Nie."],
}

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for lg in HOOK:
        card(HOOK[lg], size=62, y=1110).save(f"{out}/oma_hook_{lg}.png")
        card(PAY[lg], size=58, y=1110).save(f"{out}/oma_pay_{lg}.png")
    print("ok")

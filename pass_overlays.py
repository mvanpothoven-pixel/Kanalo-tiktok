"""Overlays for '250 lifetime passes giveaway' video. Usage: python3 pass_overlays.py OUT_DIR"""
import os, sys
from vlc_overlays import card

HOOK = {
    "en": ["🎁 Giving away 250", "free lifetime passes"],
    "nl": ["🎁 We geven 250 gratis", "lifetime-passes weg"],
    "fr": ["🎁 On offre 250 pass", "à vie gratuits"],
    "es": ["🎁 Regalamos 250 pases", "de por vida gratis"],
    "de": ["🎁 Wir verschenken 250", "Lifetime-Pässe gratis"],
}
PAY = {
    "en": ["Kanalo Pro. Free forever.", "Only the first 250."],
    "nl": ["Kanalo Pro. Voor altijd gratis.", "Alleen de eerste 250."],
    "fr": ["Kanalo Pro. Gratuit à vie.", "Seulement les 250 premiers."],
    "es": ["Kanalo Pro. Gratis para siempre.", "Solo los 250 primeros."],
    "de": ["Kanalo Pro. Für immer gratis.", "Nur die ersten 250."],
}
CTA = {
    "en": ["kanalo.app · link in bio 👆"],
    "nl": ["kanalo.app · link in bio 👆"],
    "fr": ["kanalo.app · lien en bio 👆"],
    "es": ["kanalo.app · enlace en la bio 👆"],
    "de": ["kanalo.app · Link in der Bio 👆"],
}

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for lg in HOOK:
        card(HOOK[lg], size=64, y=1300).save(f"{out}/pass_hook_{lg}.png")
        card(PAY[lg], size=58, y=1300).save(f"{out}/pass_pay_{lg}.png")
        card(CTA[lg], size=58, y=1300).save(f"{out}/pass_cta_{lg}.png")
    print("ok")

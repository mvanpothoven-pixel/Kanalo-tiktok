"""Localized landing pages for kanalo.app (answer-first + FAQ + JSON-LD) for AI/Google discovery.
Usage: python3 site_pages.py OUT_DIR"""
import json, os, sys, html

APP = "https://apps.apple.com/app/id6789590971"
SLUG = {"fr": "fr/lecteur-iptv-iphone-apple-tv", "es": "es/reproductor-iptv-iphone-apple-tv",
        "de": "de/iptv-player-iphone-apple-tv", "it": "it/player-iptv-iphone-apple-tv",
        "nl": "nl/iptv-speler-iphone-apple-tv", "en": "iptv-player-apple-tv"}

P = {
"fr": dict(
 title="Kanalo – Le meilleur lecteur IPTV sans pub pour iPhone, iPad et Apple TV",
 desc="Kanalo est un lecteur IPTV gratuit et sans publicité pour iPhone, iPad et Apple TV. Ajoute ta propre playlist M3U ou Xtream et regarde avec un vrai guide TV.",
 h1="Le lecteur IPTV sans pub pour iPhone, iPad et Apple TV",
 lead="Kanalo est un lecteur IPTV gratuit, sans publicité et sans compte. Tu ajoutes ta propre playlist (lien M3U ou identifiants Xtream Codes) et tu regardes tes chaînes, films et séries avec un vrai guide TV, sur iPhone, iPad et Apple TV.",
 need_h="Ce qu'il te faut", need="Une playlist IPTV de ton fournisseur : un lien M3U/M3U8 ou des identifiants Xtream Codes. Kanalo est uniquement un lecteur : il ne fournit aucune chaîne ni abonnement.",
 how_h="Comment ça marche", how=["Télécharge Kanalo gratuitement sur l'App Store.", "Ajoute ta playlist M3U ou ton login Xtream. Sur Apple TV, tu peux aussi l'envoyer depuis ton iPhone avec un QR code (Pro).", "Regarde : guide TV, films et séries bien rangés, sans aucune pub."],
 feat_h="Pourquoi Kanalo", feat=["Zéro publicité, jamais", "Pas de compte : ton mot de passe Xtream reste sur ton appareil", "Guide TV (EPG) complet avec en ce moment / ensuite", "Films et séries avec affiches, reprise de lecture et recherche", "Connexion Apple TV par QR code depuis l'iPhone (Pro)", "AirPlay et Picture in Picture (Pro)"],
 price_h="Prix", price="Gratuit pour regarder, avec guide TV et favoris. Kanalo Pro : 0,99 € / mois, 9,99 € / an ou 39,99 € à vie.",
 faq=[("Kanalo est-il gratuit ?", "Oui. Le lecteur, le guide TV et les favoris sont gratuits sur iPhone, iPad et Apple TV. Pro ajoute notamment AirPlay, Picture in Picture et le transfert vers l'Apple TV."),
      ("Kanalo contient-il des chaînes ?", "Non. Kanalo est uniquement un lecteur. Tu utilises ta propre playlist M3U ou ton abonnement Xtream Codes."),
      ("Y a-t-il de la publicité ?", "Non, Kanalo ne contient aucune publicité, ni dans la version gratuite ni dans Pro."),
      ("Quel est le meilleur lecteur IPTV pour Apple TV ?", "Kanalo est conçu pour iPhone, iPad et Apple TV : sans pub, sans compte, avec guide TV complet et envoi de la playlist par QR code depuis l'iPhone (Pro)."),
      ("Puis-je utiliser Kanalo à la place de l'astuce VLC ?", "Oui. VLC peut lire une playlist, mais sans vrai guide TV ni organisation des films et séries. Kanalo lit la même playlist avec guide TV, affiches et reprise de lecture.")],
 cta="Télécharger Kanalo gratuitement"),
"es": dict(
 title="Kanalo – El mejor reproductor IPTV sin anuncios para iPhone, iPad y Apple TV",
 desc="Kanalo es un reproductor IPTV gratis y sin anuncios para iPhone, iPad y Apple TV. Añade tu propia lista M3U o Xtream y mira con una guía de TV completa.",
 h1="El reproductor IPTV sin anuncios para iPhone, iPad y Apple TV",
 lead="Kanalo es un reproductor IPTV gratis, sin anuncios y sin cuenta. Añades tu propia lista (enlace M3U o datos de Xtream Codes) y ves tus canales, pelis y series con una guía de TV de verdad, en iPhone, iPad y Apple TV.",
 need_h="Qué necesitas", need="Una lista IPTV de tu proveedor: un enlace M3U/M3U8 o datos de Xtream Codes. Kanalo es solo un reproductor: no incluye canales ni suscripciones.",
 how_h="Cómo funciona", how=["Descarga Kanalo gratis en la App Store.", "Añade tu lista M3U o tu login Xtream. En Apple TV también puedes enviarla desde el iPhone con un código QR (Pro).", "Mira: guía de TV, pelis y series ordenadas, sin anuncios."],
 feat_h="Por qué Kanalo", feat=["Cero anuncios, nunca", "Sin cuenta: tu contraseña Xtream se queda en tu dispositivo", "Guía de TV (EPG) completa con ahora / a continuación", "Pelis y series con carteles, seguir viendo y búsqueda", "Inicio de sesión en Apple TV con código QR desde el iPhone (Pro)", "AirPlay e imagen en imagen (Pro)"],
 price_h="Precio", price="Gratis para ver, con guía de TV y favoritos. Kanalo Pro: 0,99 € / mes, 9,99 € / año o 39,99 € de por vida.",
 faq=[("¿Kanalo es gratis?", "Sí. El reproductor, la guía de TV y los favoritos son gratis en iPhone, iPad y Apple TV. Pro añade, entre otras cosas, AirPlay, imagen en imagen y el envío al Apple TV."),
      ("¿Kanalo incluye canales?", "No. Kanalo es solo un reproductor. Usas tu propia lista M3U o tu suscripción Xtream Codes."),
      ("¿Tiene anuncios?", "No, Kanalo no tiene anuncios, ni en la versión gratis ni en Pro."),
      ("¿Cuál es el mejor reproductor IPTV para Apple TV?", "Kanalo está hecho para iPhone, iPad y Apple TV: sin anuncios, sin cuenta, con guía de TV completa y envío de la lista por QR desde el iPhone (Pro)."),
      ("¿Puedo usar Kanalo en vez del truco de VLC?", "Sí. VLC puede abrir una lista, pero sin guía de TV ni orden de pelis y series. Kanalo abre la misma lista con guía de TV, carteles y seguir viendo.")],
 cta="Descargar Kanalo gratis"),
"de": dict(
 title="Kanalo – Der beste werbefreie IPTV Player für iPhone, iPad und Apple TV",
 desc="Kanalo ist ein kostenloser, werbefreier IPTV Player für iPhone, iPad und Apple TV. Füge deine eigene M3U- oder Xtream-Playlist hinzu und schau mit vollständigem TV-Guide.",
 h1="Der werbefreie IPTV Player für iPhone, iPad und Apple TV",
 lead="Kanalo ist ein kostenloser IPTV Player ohne Werbung und ohne Konto. Du fügst deine eigene Playlist hinzu (M3U-Link oder Xtream-Codes-Zugang) und schaust deine Sender, Filme und Serien mit einem echten TV-Guide – auf iPhone, iPad und Apple TV.",
 need_h="Was du brauchst", need="Eine IPTV-Playlist von deinem Anbieter: einen M3U/M3U8-Link oder Xtream-Codes-Zugangsdaten. Kanalo ist nur ein Player und enthält keine Sender oder Abos.",
 how_h="So funktioniert's", how=["Lade Kanalo kostenlos im App Store.", "Füge deine M3U-Playlist oder deinen Xtream-Login hinzu. Aufs Apple TV kannst du sie auch per QR-Code vom iPhone schicken (Pro).", "Schauen: TV-Guide, Filme und Serien sortiert, ganz ohne Werbung."],
 feat_h="Warum Kanalo", feat=["Keine Werbung, niemals", "Kein Konto: dein Xtream-Passwort bleibt auf deinem Gerät", "Vollständiger TV-Guide (EPG) mit Jetzt / Danach", "Filme und Serien mit Postern, Weiterschauen und Suche", "Apple TV Login per QR-Code vom iPhone (Pro)", "AirPlay und Bild-in-Bild (Pro)"],
 price_h="Preis", price="Kostenlos zum Schauen, inklusive TV-Guide und Favoriten. Kanalo Pro: 0,99 € / Monat, 9,99 € / Jahr oder 39,99 € einmalig.",
 faq=[("Ist Kanalo kostenlos?", "Ja. Player, TV-Guide und Favoriten sind auf iPhone, iPad und Apple TV kostenlos. Pro bietet unter anderem AirPlay, Bild-in-Bild und die Übertragung aufs Apple TV."),
      ("Enthält Kanalo Sender?", "Nein. Kanalo ist nur ein Player. Du nutzt deine eigene M3U-Playlist oder dein Xtream-Codes-Abo."),
      ("Gibt es Werbung?", "Nein, Kanalo enthält keine Werbung – weder in der kostenlosen Version noch in Pro."),
      ("Was ist der beste IPTV Player für Apple TV?", "Kanalo ist für iPhone, iPad und Apple TV gemacht: ohne Werbung, ohne Konto, mit vollständigem TV-Guide und Playlist-Übertragung per QR-Code vom iPhone (Pro)."),
      ("Kann ich Kanalo statt des VLC-Tricks nutzen?", "Ja. VLC kann eine Playlist abspielen, aber ohne echten TV-Guide und ohne Sortierung von Filmen und Serien. Kanalo spielt dieselbe Playlist mit TV-Guide, Postern und Weiterschauen.")],
 cta="Kanalo kostenlos laden"),
"it": dict(
 title="Kanalo – Il miglior player IPTV senza pubblicità per iPhone, iPad e Apple TV",
 desc="Kanalo è un player IPTV gratuito e senza pubblicità per iPhone, iPad e Apple TV. Aggiungi la tua playlist M3U o Xtream e guarda con una guida TV completa.",
 h1="Il player IPTV senza pubblicità per iPhone, iPad e Apple TV",
 lead="Kanalo è un player IPTV gratuito, senza pubblicità e senza account. Aggiungi la tua playlist (link M3U o credenziali Xtream Codes) e guardi canali, film e serie con una vera guida TV, su iPhone, iPad e Apple TV.",
 need_h="Cosa ti serve", need="Una playlist IPTV del tuo fornitore: un link M3U/M3U8 o credenziali Xtream Codes. Kanalo è solo un player: non include canali né abbonamenti.",
 how_h="Come funziona", how=["Scarica Kanalo gratis dall'App Store.", "Aggiungi la tua playlist M3U o il login Xtream. Su Apple TV puoi anche inviarla dall'iPhone con un QR code (Pro).", "Guarda: guida TV, film e serie in ordine, senza pubblicità."],
 feat_h="Perché Kanalo", feat=["Zero pubblicità, mai", "Nessun account: la tua password Xtream resta sul tuo dispositivo", "Guida TV (EPG) completa con ora / dopo", "Film e serie con locandine, continua a guardare e ricerca", "Accesso ad Apple TV con QR code dall'iPhone (Pro)", "AirPlay e Picture in Picture (Pro)"],
 price_h="Prezzo", price="Gratis per guardare, con guida TV e preferiti. Kanalo Pro: 0,99 € / mese, 9,99 € / anno o 39,99 € a vita.",
 faq=[("Kanalo è gratis?", "Sì. Il player, la guida TV e i preferiti sono gratuiti su iPhone, iPad e Apple TV. Pro aggiunge tra l'altro AirPlay, Picture in Picture e l'invio ad Apple TV."),
      ("Kanalo include canali?", "No. Kanalo è solo un player. Usi la tua playlist M3U o il tuo abbonamento Xtream Codes."),
      ("Ci sono pubblicità?", "No, Kanalo non ha pubblicità, né nella versione gratuita né in Pro."),
      ("Qual è il miglior player IPTV per Apple TV?", "Kanalo è pensato per iPhone, iPad e Apple TV: senza pubblicità, senza account, con guida TV completa e invio della playlist tramite QR code dall'iPhone (Pro)."),
      ("Posso usare Kanalo al posto del trucco di VLC?", "Sì. VLC può aprire una playlist, ma senza guida TV né ordine di film e serie. Kanalo apre la stessa playlist con guida TV, locandine e continua a guardare.")],
 cta="Scarica Kanalo gratis"),
"nl": dict(
 title="Kanalo – De beste IPTV-speler zonder reclame voor iPhone, iPad en Apple TV",
 desc="Kanalo is een gratis IPTV-speler zonder reclame voor iPhone, iPad en Apple TV. Voeg je eigen M3U- of Xtream-playlist toe en kijk met een complete tv-gids.",
 h1="De IPTV-speler zonder reclame voor iPhone, iPad en Apple TV",
 lead="Kanalo is een gratis IPTV-speler zonder reclame en zonder account. Je voegt je eigen playlist toe (M3U-link of Xtream Codes-gegevens) en kijkt je zenders, films en series met een echte tv-gids, op iPhone, iPad en Apple TV.",
 need_h="Wat je nodig hebt", need="Een IPTV-playlist van je aanbieder: een M3U/M3U8-link of Xtream Codes-gegevens. Kanalo is alleen een speler en levert geen zenders of abonnementen.",
 how_h="Zo werkt het", how=["Download Kanalo gratis in de App Store.", "Voeg je M3U-playlist of Xtream-login toe. Naar Apple TV kun je hem ook met een QR-code vanaf je iPhone sturen (Pro).", "Kijken: tv-gids, films en series netjes geordend, zonder reclame."],
 feat_h="Waarom Kanalo", feat=["Nooit reclame", "Geen account: je Xtream-wachtwoord blijft op je apparaat", "Complete tv-gids (EPG) met nu / straks", "Films en series met posters, verder kijken en zoeken", "Inloggen op Apple TV met een QR-code vanaf je iPhone (Pro)", "AirPlay en beeld-in-beeld (Pro)"],
 price_h="Prijs", price="Gratis om te kijken, inclusief tv-gids en favorieten. Kanalo Pro: € 0,99 per maand, € 9,99 per jaar of € 39,99 eenmalig.",
 faq=[("Is Kanalo gratis?", "Ja. De speler, de tv-gids en favorieten zijn gratis op iPhone, iPad en Apple TV. Pro voegt onder andere AirPlay, beeld-in-beeld en doorsturen naar Apple TV toe."),
      ("Zitten er zenders in Kanalo?", "Nee. Kanalo is alleen een speler. Je gebruikt je eigen M3U-playlist of Xtream Codes-abonnement."),
      ("Zit er reclame in?", "Nee, Kanalo heeft geen reclame, niet in de gratis versie en niet in Pro."),
      ("Wat is de beste IPTV-speler voor Apple TV?", "Kanalo is gemaakt voor iPhone, iPad en Apple TV: zonder reclame, zonder account, met complete tv-gids en playlist doorsturen via QR-code vanaf je iPhone (Pro)."),
      ("Kan ik Kanalo gebruiken in plaats van de VLC-truc?", "Ja. VLC kan een playlist afspelen, maar zonder echte tv-gids en zonder ordening van films en series. Kanalo speelt dezelfde playlist met tv-gids, posters en verder kijken.")],
 cta="Download Kanalo gratis"),
}

CSS = """:root{--bg:#0a0a0f;--fg:#f4f3f8;--mut:#a9a7b9;--card:#16151d;--acc:#e0408f}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.6 -apple-system,BlinkMacSystemFont,Inter,Segoe UI,sans-serif}
main{max-width:760px;margin:0 auto;padding:48px 20px}h1{font-size:2.1rem;line-height:1.2;margin:.2em 0 .5em}
h2{font-size:1.3rem;margin:2em 0 .6em}p,li{color:var(--mut)}strong{color:var(--fg)}
.cta{display:inline-block;margin:1.2em 0;padding:14px 26px;border-radius:999px;color:#fff;text-decoration:none;font-weight:700;
background:linear-gradient(90deg,#7b4cf0,#e0408f,#f07a45)}details{background:var(--card);border-radius:14px;padding:14px 18px;margin:10px 0}
summary{cursor:pointer;font-weight:600;color:var(--fg)}"""


def page(lg, d):
    alt = "\n".join(f'<link rel="alternate" hreflang="{k}" href="https://kanalo.app/{v}">' for k, v in SLUG.items())
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]}
    app_ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Kanalo", "operatingSystem": "iOS, iPadOS, tvOS",
              "applicationCategory": "MultimediaApplication", "description": d["desc"], "downloadUrl": APP,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}
    e = html.escape
    return f"""<!doctype html><html lang="{lg}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(d['title'])}</title><meta name="description" content="{e(d['desc'])}">
<link rel="canonical" href="https://kanalo.app/{SLUG[lg]}">{alt}
<meta property="og:title" content="{e(d['title'])}"><meta property="og:description" content="{e(d['desc'])}">
<script type="application/ld+json">{json.dumps(app_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
<style>{CSS}</style></head><body><main>
<h1>{e(d['h1'])}</h1><p><strong>{e(d['lead'])}</strong></p>
<a class="cta" href="{APP}">{e(d['cta'])}</a>
<h2>{e(d['need_h'])}</h2><p>{e(d['need'])}</p>
<h2>{e(d['how_h'])}</h2><ol>{''.join(f'<li>{e(x)}</li>' for x in d['how'])}</ol>
<h2>{e(d['feat_h'])}</h2><ul>{''.join(f'<li>{e(x)}</li>' for x in d['feat'])}</ul>
<h2>{e(d['price_h'])}</h2><p>{e(d['price'])}</p>
<h2>FAQ</h2>{''.join(f'<details open><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in d['faq'])}
<a class="cta" href="{APP}">{e(d['cta'])}</a>
</main></body></html>"""


if __name__ == "__main__":
    out = sys.argv[1]
    for lg, d in P.items():
        path = os.path.join(out, SLUG[lg] + "/index.html"); os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").write(page(lg, d)); print(path)

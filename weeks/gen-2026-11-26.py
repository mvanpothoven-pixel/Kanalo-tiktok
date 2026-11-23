import json, sys
RED_T = [150, 40, 120]; BLUE_T = [45, 45, 170]; PURP_T = [120, 50, 170]
A = "Kanalo · iPhone · iPad · Apple TV"
TAGS = {"en": "#iptv #iptvusa #appletv #iptvplayer #techtok",
        "fr": "#iptv #iptvfrance #appletv #iptvplayer #astuce",
        "de": "#iptv #iptvdeutschland #appletv #iptvplayer #technik",
        "es": "#iptv #iptvespaña #appletv #iptvplayer #trucos",
        "it": "#iptv #iptvitalia #appletv #iptvplayer #trucchi",
        "nl": "#iptv #iptvnederland #appletv #iptvplayer #techtok"}
END = {"en": ["Free on the", "*App Store.*"], "nl": ["Gratis in de", "*App Store.*"], "fr": ["Gratuit sur", "*l'App Store.*"],
       "de": ["Gratis im", "*App Store.*"], "es": ["Gratis en la", "*App Store.*"], "it": ["Gratis", "*sull'App Store.*"]}
LBL = {  # movies, guide, home
    "en": ("APPLE TV  ·  MOVIES", "APPLE TV  ·  TV GUIDE", "APPLE TV  ·  HOME"),
    "nl": ("APPLE TV  ·  FILMS", "APPLE TV  ·  TV-GIDS", "APPLE TV  ·  HOME"),
    "fr": ("APPLE TV  ·  FILMS", "APPLE TV  ·  GUIDE TV", "APPLE TV  ·  ACCUEIL"),
    "de": ("APPLE TV  ·  FILME", "APPLE TV  ·  TV-GUIDE", "APPLE TV  ·  START"),
    "es": ("APPLE TV  ·  PELÍCULAS", "APPLE TV  ·  GUÍA TV", "APPLE TV  ·  INICIO"),
    "it": ("APPLE TV  ·  FILM", "APPLE TV  ·  GUIDA TV", "APPLE TV  ·  HOME")}
WATCH = {"en": (["Just *watch.*"], "No ads in between."), "nl": (["Gewoon *kijken.*"], "Zonder reclame tussendoor."),
         "fr": (["Juste *regarder.*"], "Sans pub au milieu."), "de": (["Einfach *schauen.*"], "Ohne Werbung dazwischen."),
         "es": (["Solo *mirar.*"], "Sin anuncios en medio."), "it": (["Solo *guardare.*"], "Senza pubblicità in mezzo.")}
GUIDE_OK = {"en": ["A guide that", "*just loads.*"], "nl": ["Een gids die", "*gewoon laadt.*"], "fr": ["Un guide qui", "*charge, tout simplement.*"],
            "de": ["Ein TV-Guide, der", "*einfach lädt.*"], "es": ["Una guía que", "*simplemente carga.*"], "it": ["Una guida che", "*si carica e basta.*"]}
SAME = {"en": ["Same playlist.", "*Zero ads.*"], "nl": ["Zelfde playlist.", "*Nul reclame.*"], "fr": ["Même playlist.", "*Zéro pub.*"],
        "de": ["Gleiche Playlist.", "*Null Werbung.*"], "es": ["Misma playlist.", "*Cero anuncios.*"], "it": ["Stessa playlist.", "*Zero pubblicità.*"]}
NOINT = {"en": ["Films & series,", "*no interruptions.*"], "nl": ["Films & series,", "*zonder onderbreking.*"], "fr": ["Films & séries,", "*sans coupure.*"],
         "de": ["Filme & Serien,", "*ohne Unterbrechung.*"], "es": ["Pelis y series,", "*sin cortes.*"], "it": ["Film e serie,", "*senza interruzioni.*"]}
ANYPL = {"en": ["Your playlist works", "*in any player.*"], "nl": ["Je playlist werkt", "*in elke speler.*"], "fr": ["Ta playlist marche", "*partout.*"],
         "de": ["Deine Playlist läuft", "*in jedem Player.*"], "es": ["Tu playlist funciona", "*en cualquier app.*"], "it": ["La tua playlist va", "*in ogni player.*"]}
FREEPL = {"en": ["Free player.", "*Zero ads.*"], "nl": ["Gratis speler.", "*Nul reclame.*"], "fr": ["Lecteur gratuit.", "*Zéro pub.*"],
          "de": ["Gratis Player.", "*Null Werbung.*"], "es": ["Reproductor gratis.", "*Cero anuncios.*"], "it": ["Player gratis.", "*Zero pubblicità.*"]}
BILL = {
    "en": (["What you", "*pay now:*"], "a typical IPTV app", [["Subscription", "€4.99 /mo"], ["Remove ads", "€2.99"], ["Extra features", "€9.99"]], "Per year:", "± €72"),
    "nl": (["Wat je", "*nu betaalt:*"], "bij een gemiddelde IPTV-app", [["Abonnement", "€4,99 /mnd"], ["Reclame weg", "€2,99"], ["Extra functies", "€9,99"]], "Per jaar:", "± €72"),
    "fr": (["Ce que tu", "*paies :*"], "pour une app IPTV classique", [["Abonnement", "4,99 €/mois"], ["Sans pub", "2,99 €"], ["Options", "9,99 €"]], "Par an :", "± 72 €"),
    "de": (["Was du", "*zahlst:*"], "bei einer typischen IPTV-App", [["Abo", "4,99 €/Monat"], ["Werbefrei", "2,99 €"], ["Extras", "9,99 €"]], "Pro Jahr:", "± 72 €"),
    "es": (["Lo que", "*pagas:*"], "en una app IPTV típica", [["Suscripción", "4,99 €/mes"], ["Sin anuncios", "2,99 €"], ["Extras", "9,99 €"]], "Al año:", "± 72 €"),
    "it": (["Quanto", "*paghi:*"], "con una tipica app IPTV", [["Abbonamento", "4,99 €/mese"], ["Senza pubblicità", "2,99 €"], ["Extra", "9,99 €"]], "All'anno:", "± 72 €")}

def hook(kind, asset, lines, lang, i):
    if kind == "dev":
        return {"type": "s_device", "dur": 2.6, "instant": True, "red": True, "asset": asset, "lines": lines, "size": 92 if len(lines) == 3 else 100,
                "label": LBL[lang][{"atv_movies": 0, "atv_gids": 1, "atv_home": 2}[asset]], "tint": RED_T, "z1": 1.08, "fx": 0.5}
    return {"type": "s_phone", "dur": 2.6, "instant": True, "red": True, "asset": asset, "lines": lines, "size": 82 if len(lines) == 3 else 96, "tint": RED_T, "scroll": 0.3}

def dev(asset, lines, lang, tint=BLUE_T, dur=2.6):
    return {"type": "s_device", "dur": dur, "asset": asset, "lines": lines, "label": LBL[lang][{"atv_movies": 0, "atv_gids": 1, "atv_home": 2}[asset]], "tint": tint, "z1": 1.12, "fx": 0.5}
def phone(asset, lines, tint=BLUE_T, dur=2.8, scroll=0.5): return {"type": "s_phone", "dur": dur, "asset": asset, "lines": lines, "tint": tint, "scroll": scroll}
def photo(lang): l, s = WATCH[lang]; return {"type": "s_photo", "dur": 2.6, "lines": l, "sub": s}
def end(lang): return {"type": "s_end", "dur": 2.4, "lines": END[lang], "a": A}
def bill(lang):
    hl, note, items, tl, tot = BILL[lang]
    return {"type": "bill", "site": True, "dur": 3.2, "hl": hl, "note": note, "items": items, "total_label": tl, "total": tot}

# ---- week 26 Nov – 2 Dec: hooks / titles / captions ----
H = {
 "HI": {  # your playlist isn't the problem, your app is
  "en": (["Your playlist", "isn't the problem.", "*Your app is.*"], "Your IPTV playlist isn't the problem. Your app is. 🤯",
         "Your playlist isn't the problem, your app is 🤯 Same playlist, different player: no ads, a real TV guide, posters. Kanalo is free on iPhone, iPad & Apple TV."),
  "fr": (["Ta playlist", "n'est pas le problème.", "*C'est ton app.*"], "Ta playlist IPTV n'est pas le problème. C'est ton app. 🤯",
         "Ta playlist n'est pas le problème, c'est ton app 🤯 Même playlist, autre lecteur : zéro pub, vrai guide TV, affiches. Kanalo est gratuit sur iPhone, iPad & Apple TV."),
  "de": (["Nicht die Playlist", "ist das Problem.", "*Sondern die App.*"], "Nicht deine IPTV-Playlist ist das Problem. Sondern die App. 🤯",
         "Nicht deine Playlist ist das Problem, sondern die App 🤯 Gleiche Playlist, anderer Player: null Werbung, echter TV-Guide, Cover. Kanalo ist kostenlos für iPhone, iPad & Apple TV."),
  "es": (["Tu playlist", "no es el problema.", "*Es tu app.*"], "Tu playlist IPTV no es el problema. Es tu app. 🤯",
         "Tu playlist no es el problema, es tu app 🤯 Misma playlist, otro reproductor: cero anuncios, guía TV de verdad, carátulas. Kanalo es gratis en iPhone, iPad y Apple TV."),
  "it": (["Il problema non è", "la tua playlist.", "*È la tua app.*"], "Il problema non è la tua playlist IPTV. È la tua app. 🤯",
         "Il problema non è la tua playlist, è la tua app 🤯 Stessa playlist, altro player: zero pubblicità, vera guida TV, copertine. Kanalo è gratis su iPhone, iPad e Apple TV."),
  "nl": (["Je playlist is", "niet het probleem.", "*Je app wel.*"], "Je IPTV-playlist is niet het probleem. Je app wel. 🤯",
         "Je playlist is niet het probleem, je app wel 🤯 Zelfde playlist, andere speler: nul reclame, echte tv-gids, posters. Kanalo is gratis op iPhone, iPad & Apple TV.")},
 "HJ": {  # ads on the Apple TV you paid for
  "en": (["ADS on the", "Apple TV you", "*paid for?!*"], "Ads on the Apple TV you paid for?! 😤",
         "Ads on the Apple TV you paid good money for?! 😤 That's the IPTV app, not your playlist. Kanalo plays your own playlist with zero ads."),
  "fr": (["Des PUBS sur", "l'Apple TV que", "*tu as payée ?!*"], "Des pubs sur l'Apple TV que tu as payée ?! 😤",
         "Des pubs sur l'Apple TV que tu as payée ?! 😤 C'est l'app IPTV, pas ta playlist. Kanalo lit ta propre playlist sans aucune pub."),
  "de": (["WERBUNG auf dem", "Apple TV, das du", "*bezahlt hast?!*"], "Werbung auf dem Apple TV, das du bezahlt hast?! 😤",
         "Werbung auf dem Apple TV, das du teuer bezahlt hast?! 😤 Das liegt an der IPTV-App, nicht an deiner Playlist. Kanalo spielt deine eigene Playlist ohne Werbung."),
  "es": (["¿ANUNCIOS en el", "Apple TV que", "*pagaste?!*"], "¿Anuncios en el Apple TV que pagaste?! 😤",
         "¿Anuncios en el Apple TV que pagaste?! 😤 Es la app IPTV, no tu playlist. Kanalo reproduce tu propia playlist sin anuncios."),
  "it": (["PUBBLICITÀ sulla", "Apple TV che", "*hai pagato?!*"], "Pubblicità sulla Apple TV che hai pagato?! 😤",
         "Pubblicità sulla Apple TV che hai pagato?! 😤 È l'app IPTV, non la tua playlist. Kanalo riproduce la tua playlist senza pubblicità.")},
 "HC": {  # 72 a year?!
  "fr": (["72 € par an", "pour un lecteur", "*IPTV ?!*"], "72 € par an pour un lecteur IPTV ?! 🤯",
         "72 € par an juste pour un lecteur IPTV ?! 🤯 Le lecteur n'améliore pas ta playlist, il la lit. Kanalo est gratuit et sans pub, pour iPhone, iPad & Apple TV."),
  "de": (["72 € im Jahr", "für einen", "*IPTV-Player?!*"], "72 € im Jahr für einen IPTV-Player?! 🤯",
         "72 € im Jahr nur für einen IPTV-Player?! 🤯 Der Player macht deine Playlist nicht besser, er spielt sie nur ab. Kanalo ist kostenlos und ohne Werbung."),
  "es": (["¿72 € al año", "por un", "*reproductor IPTV?!*"], "¿72 € al año por un reproductor IPTV?! 🤯",
         "¿72 € al año solo por un reproductor IPTV?! 🤯 El reproductor no mejora tu playlist, solo la reproduce. Kanalo es gratis y sin anuncios."),
  "en": (["€72 a year", "for an", "*IPTV player?!*"], "€72 a year for an IPTV player?! 🤯",
         "€72 a year just for an IPTV player?! 🤯 The player doesn't make your playlist better, it just plays it. Kanalo is free and ad-free."),
  "nl": (["€72 per jaar", "voor een", "*IPTV-speler?!*"], "€72 per jaar voor een IPTV-speler?! 🤯",
         "€72 per jaar alleen voor een IPTV-speler?! 🤯 De speler maakt je playlist niet beter, hij speelt hem alleen af. Kanalo is gratis en zonder reclame.")},
 "HA": {  # still paying?
  "fr": (["Tu paies ENCORE", "pour une app IPTV", "*pleine de pubs ?*"], "Tu paies encore pour une app IPTV pleine de pubs ? 👀",
         "Tu paies encore pour une app IPTV pleine de pubs ? 👀 Une fois sans pub, tu ne reviens plus en arrière. Kanalo : gratuit, sans pub, pour iPhone, iPad & Apple TV.")},
 "HB": {  # ad in the middle of your film
  "es": (["¿Un ANUNCIO en", "mitad de tu", "*peli IPTV?!*"], "¿Un anuncio en mitad de tu peli IPTV?! 😤",
         "¿Un anuncio en mitad de la peli?! 😤 No es tu playlist, es la app. Kanalo reproduce tu propia playlist sin anuncios, en iPhone, iPad y Apple TV.")},
}
TIPS = {
 "T1": {  # empty guide
  "hook": {"es": ["¿Tu guía TV", "dice", "*«Sin información»?*"], "en": ["TV guide says", "*'No information'?*"]},
  "title": {"es": "¿Guía TV vacía en tu app IPTV? Así se arregla", "en": "Empty TV guide in your IPTV app? Fix it"},
  "cap": {"es": "¿Tu guía TV dice «Sin información»? Casi siempre es una de estas 3 causas. Guárdalo 📌 Yo uso Kanalo, carga la guía en segundo plano.",
          "en": "TV guide says 'No information'? It's almost always one of these 3. Save it 📌 I use Kanalo, it loads the guide in the background."},
  "tips": {"es": ("3 causas", "+ la solución.", [["Sin enlace EPG", "Pide la URL XMLTV a tu proveedor"], ["IDs de canal distintos", "El tvg-id tiene que coincidir"], ["Zona horaria incorrecta", "Ajusta la diferencia (ej. +1 h)"]]),
           "en": ("3 causes", "+ the fix.", [["No EPG link added", "Ask your provider for the XMLTV URL"], ["Channel IDs don't match", "The tvg-id must match"], ["Wrong time zone", "Set the time offset (e.g. +1h)"]])}},
 "T2": {  # black screen
  "hook": {"fr": ["Écran noir", "sur la moitié", "*de tes chaînes ?*"], "nl": ["Zwart beeld", "bij de helft van", "*je zenders?*"]},
  "title": {"fr": "Chaînes IPTV qui ne chargent pas ? Essaie ça d'abord", "nl": "IPTV-zenders laden niet? Probeer dit eerst"},
  "cap": {"fr": "Écran noir sur la moitié de tes chaînes ? Essaie ces 3 choses avant d'accuser l'app. Enregistre 📌",
          "nl": "Zwart beeld bij de helft van je zenders? Probeer eerst deze 3 dingen voordat je de app de schuld geeft. Sla op 📌"},
  "tips": {"fr": ("Essaie ça", "d'abord.", [["Actualise ta playlist", "Les fournisseurs changent les liens"], ["Vérifie ton abonnement", "Expiré = écran noir"], ["Crée une liste de favoris", "Que les chaînes qui marchent"]]),
           "nl": ("Probeer dit", "eerst.", [["Ververs je playlist", "Providers wijzigen links vaak"], ["Check je abonnement", "Verlopen = zwart beeld"], ["Maak een favorietenlijst", "Alleen zenders die werken"]])}},
 "T3": {  # m3u vs xtream (ES version: 1,671 views across platforms last week)
  "hook": {"fr": ["M3U ou Xtream ?", "*Lequel choisir ?*"], "de": ["M3U oder Xtream?", "*Was ist besser?*"], "it": ["M3U o Xtream?", "*Quale scegliere?*"]},
  "title": {"fr": "M3U ou Xtream ? La différence en 15 secondes", "de": "M3U oder Xtream? Der Unterschied in 15 Sekunden", "it": "M3U o Xtream? La differenza in 15 secondi"},
  "cap": {"fr": "Ton fournisseur t'a donné un lien M3U ET des identifiants Xtream ? Voici la différence en 15 secondes. Les deux marchent dans Kanalo.",
          "de": "Dein Anbieter hat dir einen M3U-Link UND Xtream-Daten gegeben? Hier ist der Unterschied in 15 Sekunden. Beides läuft in Kanalo.",
          "it": "Il fornitore ti ha dato un link M3U E i dati Xtream? Ecco la differenza in 15 secondi. Funzionano entrambi in Kanalo."},
  "tips": {"fr": ("La différence", "en 15 secondes.", [["M3U = un long lien", "Tout dans un gros fichier"], ["Xtream = serveur + login", "Films & séries à part, plus rapide"], ["Tu as les deux ? Xtream", "Se met à jour plus vite"]]),
           "de": ("Der Unterschied", "in 15 Sekunden.", [["M3U = ein langer Link", "Alles in einer großen Datei"], ["Xtream = Server + Login", "Filme & Serien separat, schneller"], ["Beides? Nimm Xtream", "Aktualisiert schneller"]]),
           "it": ("La differenza", "in 15 secondi.", [["M3U = un link lungo", "Tutto in un unico file"], ["Xtream = server + login", "Film e serie a parte, più veloce"], ["Hai entrambi? Xtream", "Si aggiorna più in fretta"]])},
  "after": {"fr": ["Les deux marchent", "*dans Kanalo.*"], "de": ["Beides läuft", "*in Kanalo.*"], "it": ["Funzionano entrambi", "*in Kanalo.*"]}},
 "T4": {  # qr login
  "hook": {"de": ["Tippst du deinen", "Login noch mit", "*der Fernbedienung?*"], "fr": ["Tu tapes encore", "ton login avec", "*la télécommande ?*"],
           "es": ["¿Aún escribes", "tu login con", "*el mando?*"], "en": ["Still typing", "your login with", "*the remote?*"]},
  "title": {"de": "IPTV-Login mit der Fernbedienung tippen? Musst du nicht", "fr": "Taper ton login IPTV avec la télécommande ? Plus besoin",
            "es": "¿Escribir tu login IPTV con el mando? Ya no hace falta", "en": "Typing your IPTV login with the remote? You don't have to"},
  "cap": {"de": "Deinen langen Xtream-Login Buchstabe für Buchstabe mit der Fernbedienung tippen? 😩 Geht auch per iPhone: QR-Code scannen, fertig. Kanalo macht das kostenlos.",
          "fr": "Taper ton long login Xtream lettre par lettre avec la télécommande ? 😩 Avec l'iPhone, tu scannes un QR code et c'est fini. Kanalo le fait gratuitement.",
          "es": "¿Escribir tu login Xtream letra a letra con el mando? 😩 Con el iPhone escaneas un código QR y listo. Kanalo lo hace gratis.",
          "en": "Typing your long Xtream login letter by letter with the remote? 😩 Use your iPhone instead: scan one QR code, done. Kanalo does it for free."},
  "qr": {"de": dict(lines=["Einmal scannen", "*mit dem iPhone.*"], tv1="Playlist hinzufügen", tv2="Vom iPhone", tv3="Mit der Kamera scannen", sent="Playlists gesendet", label="NICHTS AM TV TIPPEN"),
         "fr": dict(lines=["Scanne une fois", "*avec l'iPhone.*"], tv1="Ajouter une playlist", tv2="Depuis l'iPhone", tv3="Scanne avec la caméra", sent="Playlists envoyées", label="RIEN À TAPER SUR LA TV"),
         "es": dict(lines=["Escanea una vez", "*con el iPhone.*"], tv1="Añadir playlist", tv2="Desde el iPhone", tv3="Escanea con la cámara", sent="Playlists enviadas", label="NADA QUE ESCRIBIR EN LA TV"),
         "en": dict(lines=["Scan once", "*with your iPhone.*"], tv1="Add playlist", tv2="From iPhone", tv3="Scan with the camera", sent="Playlists sent", label="NOTHING TO TYPE ON THE TV")}},
}

def build(tpl, lang):
    if tpl in H:
        lines, title, cap = H[tpl][lang]
        if tpl == "HI": sc = [hook("dev", "atv_home", lines, lang, 0), dev("atv_movies", SAME[lang], lang), phone("as_detail", FREEPL[lang]), end(lang)]
        if tpl == "HJ": sc = [hook("dev", "atv_movies", lines, lang, 0), photo(lang), dev("atv_gids", GUIDE_OK[lang], lang), end(lang)]
        if tpl == "HA": sc = [hook("dev", "atv_movies", lines, lang, 0), photo(lang), dev("atv_gids", GUIDE_OK[lang], lang), end(lang)]
        if tpl == "HB": sc = [hook("ph", "as_detail", lines, lang, 0), photo(lang), phone("as_movies", NOINT[lang]), end(lang)]
        if tpl == "HC": sc = [hook("dev", "atv_home", lines, lang, 0), bill(lang), phone("as_movies", FREEPL[lang]), end(lang)]
        return title, cap, sc, "hard"
    T = TIPS[tpl]; lines = T["hook"][lang]; title = T["title"][lang]; cap = T["cap"][lang]
    if tpl == "T4":
        q = dict(type="qr", site=True, dur=4.2, **T["qr"][lang])
        return title, cap, [hook("dev", "atv_home", lines, lang, 0), q, photo(lang), end(lang)], "tip"
    tt, sub, items = T["tips"][lang]
    tips = {"type": "tips", "site": True, "dur": 5.4, "title": tt, "sub": sub, "items": items}
    first = {"T1": ("dev", "atv_gids"), "T2": ("dev", "atv_home"), "T3": ("ph", "as_manage")}[tpl]
    after = {"T1": lambda: dev("atv_gids", GUIDE_OK[lang], lang), "T2": lambda: photo(lang),
             "T3": lambda: phone("as_manage", T["after"][lang])}[tpl]()
    return title, cap, [hook(first[0], first[1], lines, lang, 0), tips, after, end(lang)], "tip"

# schedule: 26 Nov – 2 Dec, slots 10/12/14/18 (19–25 Nov already planned)
PLAN = [
 ("fr", "HI"), ("es", "HJ"), ("de", "T3"), ("en", "HC"),   # 26
 ("es", "HI"), ("fr", "HC"), ("it", "HJ"), ("de", "HI"),   # 27
 ("nl", "HI"), ("en", "T4"), ("fr", "HJ"), ("es", "HC"),   # 28
 ("de", "HJ"), ("it", "T3"), ("en", "HI"), ("fr", "T3"),   # 29
 ("es", "HB"), ("nl", "HC"), ("de", "T4"), ("fr", "HA"),   # 30
 ("en", "HJ"), ("es", "T4"), ("it", "HI"), ("de", "HC"),   # 1 Dec
 ("fr", "T2"), ("en", "T1"), ("nl", "T2"), ("es", "T1"),   # 2 Dec
]
SLUG = {"HI": "app-is-problem", "HJ": "ads-on-appletv", "HC": "72-a-year", "HA": "still-paying", "HB": "ad-mid-film",
        "T1": "empty-guide", "T2": "black-screen", "T3": "m3u-xtream", "T4": "qr-login"}
DAYS = ["2026-11-26", "2026-11-27", "2026-11-28", "2026-11-29", "2026-11-30", "2026-12-01", "2026-12-02"]
vids = []; seed = 301
for i, (lang, tpl) in enumerate(PLAN):
    d = DAYS[i // 4]; hh = [10, 12, 14, 18][i % 4]
    title, cap, sc, style = build(tpl, lang)
    vid = f"{d}_{hh:02d}_{lang}-{SLUG[tpl]}"
    vids.append({"id": vid, "publish": f"{d}T{hh:02d}:00:00", "lang": lang, "style": style, "tpl": tpl, "seed": seed + i,
                 "title": title, "caption": cap + " " + TAGS[lang], "scenes": sc})
assert len(vids) == 28 and len({v["id"] for v in vids}) == 28
for v in vids: assert len(v["title"]) <= 90, v["title"]; assert sum(s["dur"] for s in v["scenes"]) > 9
json.dump({"videos": vids}, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(v["lang"] for v in vids), Counter(v["style"] for v in vids))

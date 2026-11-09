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

# ---- hooks / titles / captions per template & language ----
H = {
 "HA": {  # still paying?
  "fr": (["Tu paies ENCORE", "pour une app IPTV", "*pleine de pubs ?*"], "Tu paies encore pour une app IPTV pleine de pubs ? 👀",
         "Tu paies encore pour une app IPTV pleine de pubs ? 👀 Une fois sans pub, tu ne reviens plus en arrière. Kanalo : gratuit, sans pub, pour iPhone, iPad & Apple TV."),
  "de": (["Zahlst du NOCH", "für eine IPTV-App", "*voller Werbung?*"], "Zahlst du noch für eine IPTV-App voller Werbung? 👀",
         "Zahlst du noch für eine IPTV-App voller Werbung? 👀 Wer einmal ohne schaut, will nicht zurück. Kanalo: kostenlos, ohne Werbung, für iPhone, iPad & Apple TV."),
  "es": (["¿SIGUES pagando", "por una app IPTV", "*llena de anuncios?*"], "¿Sigues pagando por una app IPTV llena de anuncios? 👀",
         "¿Sigues pagando por una app IPTV llena de anuncios? 👀 Cuando la pruebas sin anuncios, no vuelves atrás. Kanalo: gratis, sin anuncios, para iPhone, iPad y Apple TV."),
  "it": (["Paghi ANCORA", "per un'app IPTV", "*piena di pubblicità?*"], "Paghi ancora per un'app IPTV piena di pubblicità? 👀",
         "Paghi ancora per un'app IPTV piena di pubblicità? 👀 Quando provi senza, non torni più indietro. Kanalo: gratis, senza pubblicità, per iPhone, iPad e Apple TV.")},
 "HB": {  # ad in the middle of your film
  "fr": (["Une PUB en plein", "milieu de ton film", "*IPTV ?!*"], "Une pub en plein milieu de ton film IPTV ?! 😤",
         "Une pub en plein milieu de ton film ?! 😤 Ce n'est pas ta playlist, c'est l'app. Kanalo lit ta propre playlist sans aucune pub, sur iPhone, iPad & Apple TV."),
  "de": (["WERBUNG mitten", "in deinem", "*IPTV-Film?!*"], "Werbung mitten in deinem IPTV-Film?! 😤",
         "Werbung mitten im Film?! 😤 Das liegt nicht an deiner Playlist, sondern an der App. Kanalo spielt deine eigene Playlist ohne Werbung, auf iPhone, iPad & Apple TV."),
  "es": (["¿Un ANUNCIO en", "mitad de tu", "*peli IPTV?!*"], "¿Un anuncio en mitad de tu peli IPTV?! 😤",
         "¿Un anuncio en mitad de la peli?! 😤 No es tu playlist, es la app. Kanalo reproduce tu propia playlist sin anuncios, en iPhone, iPad y Apple TV."),
  "en": (["An AD in the", "middle of your", "*IPTV movie?!*"], "An ad in the middle of your IPTV movie?! 😤",
         "An ad right in the middle of the movie?! 😤 That's not your playlist, it's the app. Kanalo plays your own playlist with zero ads on iPhone, iPad & Apple TV."),
  "nl": (["RECLAME midden", "in je", "*IPTV-film?!*"], "Reclame midden in je IPTV-film?! 😤",
         "Reclame midden in je film?! 😤 Dat ligt niet aan je playlist, maar aan de app. Kanalo speelt je eigen playlist zonder reclame, op iPhone, iPad & Apple TV.")},
 "HC": {  # 72 a year?!
  "fr": (["72 € par an", "pour un lecteur", "*IPTV ?!*"], "72 € par an pour un lecteur IPTV ?! 🤯",
         "72 € par an juste pour un lecteur IPTV ?! 🤯 Le lecteur n'améliore pas ta playlist, il la lit. Kanalo est gratuit et sans pub, pour iPhone, iPad & Apple TV."),
  "de": (["72 € im Jahr", "für einen", "*IPTV-Player?!*"], "72 € im Jahr für einen IPTV-Player?! 🤯",
         "72 € im Jahr nur für einen IPTV-Player?! 🤯 Der Player macht deine Playlist nicht besser, er spielt sie nur ab. Kanalo ist kostenlos und ohne Werbung."),
  "it": (["72 € all'anno", "per un player", "*IPTV?!*"], "72 € all'anno per un player IPTV?! 🤯",
         "72 € all'anno solo per un player IPTV?! 🤯 Il player non migliora la tua playlist, la riproduce e basta. Kanalo è gratis e senza pubblicità."),
  "nl": (["€72 per jaar", "voor een", "*IPTV-speler?!*"], "€72 per jaar voor een IPTV-speler?! 🤯",
         "€72 per jaar alleen voor een IPTV-speler?! 🤯 De speler maakt je playlist niet beter, hij speelt hem alleen af. Kanalo is gratis en zonder reclame.")},
 "HD": {  # STOP watching ads
  "fr": (["STOP aux pubs", "dans ton", "*appli IPTV !*"], "STOP aux pubs dans ton appli IPTV ! 🛑",
         "STOP aux pubs dans ton appli IPTV 🛑 Ta playlist (M3U ou Xtream) marche dans n'importe quel lecteur. Kanalo : gratuit, sans pub, sans compte."),
  "es": (["¡BASTA de", "anuncios en tu", "*app IPTV!*"], "¡Basta de anuncios en tu app IPTV! 🛑",
         "¡Basta de anuncios en tu app IPTV! 🛑 Tu playlist (M3U o Xtream) funciona en cualquier reproductor. Kanalo: gratis, sin anuncios, sin cuenta."),
  "en": (["STOP watching", "ads in your", "*IPTV app!*"], "STOP watching ads in your IPTV app! 🛑",
         "STOP watching ads in your IPTV app 🛑 Your playlist (M3U or Xtream) works in any player. Kanalo: free, no ads, no account.")},
}
TIPS = {
 "T1": {  # empty guide
  "hook": {"fr": ["Ton guide TV", "affiche", "*« Aucune info » ?*"], "es": ["¿Tu guía TV", "dice", "*«Sin información»?*"], "en": ["TV guide says", "*'No information'?*"]},
  "title": {"fr": "Guide TV vide ? Voici la solution", "es": "¿Guía TV vacía en tu app IPTV? Así se arregla", "en": "Empty TV guide in your IPTV app? Fix it"},
  "cap": {"fr": "Ton guide TV affiche « Aucune information » ? C'est presque toujours l'une de ces 3 causes. Enregistre 📌 J'utilise Kanalo, il charge le guide en arrière-plan.",
          "es": "¿Tu guía TV dice «Sin información»? Casi siempre es una de estas 3 causas. Guárdalo 📌 Yo uso Kanalo, carga la guía en segundo plano.",
          "en": "TV guide says 'No information'? It's almost always one of these 3. Save it 📌 I use Kanalo, it loads the guide in the background."},
  "tips": {"fr": ("3 causes", "+ la solution.", [["Pas de lien EPG", "Demande l'URL XMLTV à ton fournisseur"], ["IDs de chaînes différents", "Le tvg-id doit correspondre"], ["Mauvais fuseau horaire", "Règle le décalage (ex. +1 h)"]]),
           "es": ("3 causas", "+ la solución.", [["Sin enlace EPG", "Pide la URL XMLTV a tu proveedor"], ["IDs de canal distintos", "El tvg-id tiene que coincidir"], ["Zona horaria incorrecta", "Ajusta la diferencia (ej. +1 h)"]]),
           "en": ("3 causes", "+ the fix.", [["No EPG link added", "Ask your provider for the XMLTV URL"], ["Channel IDs don't match", "The tvg-id must match"], ["Wrong time zone", "Set the time offset (e.g. +1h)"]])}},
 "T2": {  # black screen
  "hook": {"de": ["Schwarzes Bild", "bei der Hälfte", "*deiner Sender?*"], "it": ["Schermo nero", "su metà dei", "*tuoi canali?*"], "en": ["Black screen", "on half your", "*channels?*"]},
  "title": {"de": "IPTV-Sender laden nicht? Probier das zuerst", "it": "I canali IPTV non partono? Prova prima questo", "en": "IPTV channels not loading? Try this first"},
  "cap": {"de": "Schwarzes Bild bei der Hälfte deiner Sender? Probier zuerst diese 3 Dinge, bevor du der App die Schuld gibst. Speichern 📌",
          "it": "Schermo nero su metà dei canali? Prova prima queste 3 cose, prima di dare la colpa all'app. Salvalo 📌",
          "en": "Black screen on half your channels? Try these 3 things before you blame the app. Save it 📌"},
  "tips": {"de": ("Probier das", "zuerst.", [["Playlist aktualisieren", "Anbieter ändern Links ständig"], ["Abo prüfen", "Abgelaufen = schwarzes Bild"], ["Favoritenliste anlegen", "Nur Sender, die laufen"]]),
           "it": ("Prova prima", "questo.", [["Aggiorna la playlist", "I fornitori cambiano spesso i link"], ["Controlla l'abbonamento", "Scaduto = schermo nero"], ["Crea una lista preferiti", "Solo i canali che funzionano"]]),
           "en": ("Try this", "first.", [["Refresh your playlist", "Providers change links all the time"], ["Check your subscription", "Expired = black screen"], ["Make a favourites list", "Only the channels that work"]])}},
 "T3": {  # m3u vs xtream
  "hook": {"es": ["¿M3U o Xtream?", "*¿Cuál es mejor?*"]},
  "title": {"es": "¿M3U o Xtream? La diferencia en 15 segundos"},
  "cap": {"es": "¿Tu proveedor te dio un enlace M3U y datos Xtream? Esta es la diferencia en 15 segundos. Los dos funcionan en Kanalo."},
  "tips": {"es": ("La diferencia", "en 15 segundos.", [["M3U = un enlace largo", "Todo en un archivo grande"], ["Xtream = servidor + login", "Pelis y series cargan aparte, más rápido"], ["¿Tienes los dos? Xtream", "Actualiza más rápido"]])}},
 "T4": {  # qr
  "hook": {"de": ["Tippst du deinen", "Login noch mit", "*der Fernbedienung?*"]},
  "title": {"de": "IPTV-Login mit der Fernbedienung tippen? Musst du nicht"},
  "cap": {"de": "Deinen langen Xtream-Login Buchstabe für Buchstabe mit der Fernbedienung tippen? 😩 Geht auch per iPhone: QR-Code scannen, fertig. Kanalo macht das kostenlos."},
  "qr": {"de": dict(lines=["Einmal scannen", "*mit dem iPhone.*"], tv1="Playlist hinzufügen", tv2="Vom iPhone", tv3="Mit der Kamera scannen", sent="Playlists gesendet", label="NICHTS AM TV TIPPEN")}},
 "T5": {  # buffering
  "hook": {"fr": ["Ton IPTV", "*bloque sans arrêt ?*"], "it": ["La tua IPTV", "*si blocca sempre?*"]},
  "title": {"fr": "Ton IPTV bloque sans arrêt ? 3 solutions", "it": "La tua IPTV si blocca sempre? 3 soluzioni"},
  "cap": {"fr": "Ton IPTV bloque sans arrêt ? Essaie ces 3 solutions avant d'abandonner. Enregistre 📌 J'utilise Kanalo sur iPhone et Apple TV.",
          "it": "La tua IPTV si blocca sempre? Prova queste 3 soluzioni prima di arrenderti. Salvalo 📌 Io uso Kanalo su iPhone e Apple TV."},
  "tips": {"fr": ("3 solutions", "rapides.", [["Wi-Fi 5 GHz ou câble", "Le 2,4 GHz sature vite"], ["Passe en HD", "La 4K demande ~25 Mbit/s"], ["Relance le flux une fois", "Souvent un serveur plus rapide"]]),
           "it": ("3 soluzioni", "veloci.", [["Wi-Fi 5 GHz o cavo", "Il 2,4 GHz si satura presto"], ["Passa all'HD", "Il 4K chiede ~25 Mbit/s"], ["Riavvia lo stream", "Spesso trovi un server più veloce"]])}},
 "T6": {  # apple tv settings
  "hook": {"en": ["IPTV on Apple TV", "looks off?", "*Change this.*"]},
  "title": {"en": "IPTV on Apple TV looks off? Change these 3 settings"},
  "cap": {"en": "IPTV on your Apple TV looks off? 3 settings that make it look and sound better. Save it 📌 I use Kanalo as my player on Apple TV."},
  "tips": {"en": ("Apple TV", "settings.", [["Match Content: on", "Video and Audio → Match Content"], ["Use a cable if you can", "Ethernet beats wifi for live TV"], ["Reduce Loud Sounds: on", "Video and Audio → Audio"]])}},
 "T7": {  # too many channels
  "hook": {"en": ["Scrolling past", "*1,000 channels?*"], "nl": ["Scrol jij ook", "langs", "*1.000 zenders?*"]},
  "title": {"en": "Scrolling past 1,000 IPTV channels? Do this", "nl": "Scrol jij ook langs 1.000 IPTV-zenders? Doe dit"},
  "cap": {"en": "Scrolling past 1,000 channels to find the one you watch? 3 quick fixes. Save it 📌 I use Kanalo on iPhone and Apple TV.",
          "nl": "Scrol jij ook langs 1.000 zenders om die ene te vinden? 3 snelle fixes. Sla op 📌 Ik gebruik zelf Kanalo op iPhone en Apple TV."},
  "tips": {"en": ("3 quick", "fixes.", [["Make a favourites list", "Your top 20 channels first"], ["Search, don't scroll", "Type 3 letters, done"], ["Ask for a smaller list", "Many providers filter by country"]]),
           "nl": ("3 snelle", "fixes.", [["Maak een favorietenlijst", "Je top 20 zenders bovenaan"], ["Zoeken, niet scrollen", "3 letters typen, klaar"], ["Vraag een kleinere lijst", "Veel providers filteren per land"]])}},
}

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

def build(tpl, lang):
    if tpl in H:
        lines, title, cap = H[tpl][lang]
        if tpl == "HA": sc = [hook("dev", "atv_movies", lines, lang, 0), photo(lang), dev("atv_gids", GUIDE_OK[lang], lang), end(lang)]
        if tpl == "HB": sc = [hook("ph", "as_detail", lines, lang, 0), photo(lang), phone("as_movies", NOINT[lang]), end(lang)]
        if tpl == "HC": sc = [hook("dev", "atv_home", lines, lang, 0), bill(lang), phone("as_movies", FREEPL[lang]), end(lang)]
        if tpl == "HD": sc = [hook("ph", "as_movies", lines, lang, 0), dev("atv_movies", ANYPL[lang], lang), photo(lang), end(lang)]
        return title, cap, sc, "hard"
    T = TIPS[tpl]; lines = T["hook"][lang]; title = T["title"][lang]; cap = T["cap"][lang]
    if tpl == "T4":
        q = dict(type="qr", site=True, dur=4.2, **T["qr"][lang])
        sc = [hook("dev", "atv_home", lines, lang, 0), q, photo(lang), end(lang)]
        return title, cap, sc, "tip"
    tt, sub, items = T["tips"][lang]
    tips = {"type": "tips", "site": True, "dur": 5.4, "title": tt, "sub": sub, "items": items}
    first = {"T1": ("dev", "atv_gids"), "T2": ("dev", "atv_home"), "T3": ("ph", "as_manage"), "T5": ("ph", "as_movies"),
             "T6": ("dev", "atv_movies"), "T7": ("dev", "atv_home")}[tpl]
    after = {"T1": dev("atv_gids", GUIDE_OK[lang], lang), "T2": photo(lang), "T3": phone("as_manage", ["Los dos funcionan", "*en Kanalo.*"]),
             "T5": photo(lang), "T6": dev("atv_movies", NOINT[lang], lang), "T7": dev("atv_gids", GUIDE_OK[lang], lang)}[tpl]
    return title, cap, [hook(first[0], first[1], lines, lang, 0), tips, after, end(lang)], "tip"

# schedule: 12–18 Nov, slots 10/12/14/18
PLAN = [
 # day 12
 ("fr", "HB"), ("de", "HA"), ("es", "T1"), ("en", "HD"),
 # 13
 ("it", "HA"), ("fr", "HC"), ("nl", "HB"), ("de", "T4"),
 # 14
 ("es", "HA"), ("en", "T6"), ("fr", "T5"), ("de", "HB"),
 # 15
 ("fr", "HA"), ("it", "T2"), ("es", "HB"), ("en", "HB"),
 # 16
 ("de", "HC"), ("nl", "T7"), ("it", "HC"), ("fr", "T1"),
 # 17
 ("es", "HD"), ("en", "T7"), ("nl", "HC"), ("fr", "HD"),
 # 18
 ("it", "T5"), ("de", "T2"), ("en", "T2"), ("es", "T3"),
]
SLUG = {"HA": "still-paying", "HB": "ad-mid-film", "HC": "72-a-year", "HD": "stop-ads", "T1": "empty-guide", "T2": "black-screen",
        "T3": "m3u-xtream", "T4": "qr-login", "T5": "buffering", "T6": "atv-settings", "T7": "1000-channels"}
vids = []; seed = 101
for i, (lang, tpl) in enumerate(PLAN):
    day = 12 + i // 4; hh = [10, 12, 14, 18][i % 4]
    title, cap, sc, style = build(tpl, lang)
    vid = f"2026-11-{day:02d}_{hh:02d}_{lang}-{SLUG[tpl]}"
    vids.append({"id": vid, "publish": f"2026-11-{day:02d}T{hh:02d}:00:00", "lang": lang, "style": style, "tpl": tpl, "seed": seed + i,
                 "title": title, "caption": cap + " " + TAGS[lang], "scenes": sc})
assert len(vids) == 28 and len({v["id"] for v in vids}) == 28
for v in vids: assert len(v["title"]) <= 90, v["title"]; assert sum(s["dur"] for s in v["scenes"]) > 9
json.dump({"videos": vids}, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(v["lang"] for v in vids), Counter(v["style"] for v in vids))

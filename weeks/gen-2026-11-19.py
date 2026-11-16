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

# ---- week 19–25 Nov: hooks / titles / captions ----
H = {
 "HE": {  # wait... still PAYING? (best organic EN hook: 1,688 views)
  "en": (["Wait... you're", "still PAYING for", "*an app with ads?*"], "Wait… you're still PAYING for an IPTV app full of ads? 😳",
         "Wait… you're still PAYING for an IPTV app full of ads? 😳 Your playlist works in any player. Kanalo: free, no ads, no account."),
  "fr": (["Attends... tu PAIES", "encore pour une", "*app pleine de pubs ?*"], "Attends… tu PAIES encore pour une app IPTV pleine de pubs ? 😳",
         "Attends… tu paies encore pour une app IPTV pleine de pubs ? 😳 Ta playlist marche dans n'importe quel lecteur. Kanalo : gratuit, sans pub, sans compte."),
  "de": (["Moment... du ZAHLST", "noch für eine", "*App mit Werbung?*"], "Moment… du ZAHLST noch für eine IPTV-App voller Werbung? 😳",
         "Moment… du zahlst noch für eine IPTV-App voller Werbung? 😳 Deine Playlist läuft in jedem Player. Kanalo: kostenlos, ohne Werbung, ohne Konto."),
  "es": (["Espera... ¿aún", "PAGAS por una", "*app con anuncios?*"], "Espera… ¿aún PAGAS por una app IPTV llena de anuncios? 😳",
         "Espera… ¿aún pagas por una app IPTV llena de anuncios? 😳 Tu playlist funciona en cualquier reproductor. Kanalo: gratis, sin anuncios, sin cuenta."),
  "it": (["Aspetta... PAGHI", "ancora un'app", "*con pubblicità?*"], "Aspetta… PAGHI ancora un'app IPTV piena di pubblicità? 😳",
         "Aspetta… paghi ancora un'app IPTV piena di pubblicità? 😳 La tua playlist funziona in ogni player. Kanalo: gratis, senza pubblicità, senza account."),
  "nl": (["Wacht... BETAAL je", "nog voor een app", "*vol reclame?*"], "Wacht… BETAAL je nog voor een IPTV-app vol reclame? 😳",
         "Wacht… betaal je nog voor een IPTV-app vol reclame? 😳 Je playlist werkt in elke speler. Kanalo: gratis, zonder reclame, zonder account.")},
 "HF": {  # nobody tells you this
  "en": (["Nobody tells you", "this about", "*IPTV...*"], "Nobody tells you this about IPTV 👀",
         "Nobody tells you this about IPTV 👀 Your playlist isn't tied to the app. Put it in any player, like Kanalo: TV guide, posters, zero ads."),
  "fr": (["Personne ne te", "dit ça sur", "*l'IPTV...*"], "Personne ne te dit ça sur l'IPTV 👀",
         "Personne ne te dit ça sur l'IPTV 👀 Ta playlist n'est pas liée à l'app. Mets-la dans le lecteur que tu veux, comme Kanalo : guide TV, affiches, zéro pub."),
  "de": (["Das sagt dir", "keiner über", "*IPTV...*"], "Das sagt dir keiner über IPTV 👀",
         "Das sagt dir keiner über IPTV 👀 Deine Playlist hängt nicht an der App. Nimm sie in jeden Player mit, z. B. Kanalo: TV-Guide, Cover, null Werbung."),
  "es": (["Nadie te cuenta", "esto sobre", "*el IPTV...*"], "Nadie te cuenta esto sobre el IPTV 👀",
         "Nadie te cuenta esto sobre el IPTV 👀 Tu playlist no está atada a la app. Llévala a cualquier reproductor, como Kanalo: guía TV, carátulas, cero anuncios."),
  "nl": (["Niemand vertelt", "je dit over", "*IPTV...*"], "Niemand vertelt je dit over IPTV 👀",
         "Niemand vertelt je dit over IPTV 👀 Je playlist zit niet vast aan de app. Zet hem in elke speler, zoals Kanalo: tv-gids, posters, nul reclame.")},
 "HG": {  # every single time: ad at worst moment
  "en": (["The ad ALWAYS", "hits at the", "*worst moment.*"], "Every. Single. Time. 😭 The ad always hits at the worst moment",
         "Every. Single. Time. 😭 The ad always hits at the worst moment. That's not your playlist, it's the app. Kanalo: your own playlist, zero ads."),
  "fr": (["La pub tombe", "TOUJOURS au", "*pire moment.*"], "À chaque fois 😭 La pub tombe toujours au pire moment",
         "À chaque fois 😭 La pub tombe toujours au pire moment. Ce n'est pas ta playlist, c'est l'app. Kanalo : ta propre playlist, zéro pub."),
  "es": (["El anuncio llega", "SIEMPRE en el", "*peor momento.*"], "Siempre igual 😭 El anuncio llega en el peor momento",
         "Siempre igual 😭 El anuncio llega en el peor momento. No es tu playlist, es la app. Kanalo: tu propia playlist, cero anuncios."),
  "it": (["La pubblicità", "arriva SEMPRE nel", "*momento peggiore.*"], "Ogni. Santa. Volta. 😭 La pubblicità arriva sempre sul più bello",
         "Ogni santa volta 😭 La pubblicità arriva sempre nel momento peggiore. Non è la tua playlist, è l'app. Kanalo: la tua playlist, zero pubblicità.")},
 "HB": {  # ad in the middle of your film
  "fr": (["Une PUB en plein", "milieu de ton film", "*IPTV ?!*"], "Une pub en plein milieu de ton film IPTV ?! 😤",
         "Une pub en plein milieu de ton film ?! 😤 Ce n'est pas ta playlist, c'est l'app. Kanalo lit ta propre playlist sans aucune pub, sur iPhone, iPad & Apple TV."),
  "en": (["An AD in the", "middle of your", "*IPTV movie?!*"], "An ad in the middle of your IPTV movie?! 😤",
         "An ad right in the middle of the movie?! 😤 That's not your playlist, it's the app. Kanalo plays your own playlist with zero ads on iPhone, iPad & Apple TV.")},
 "HD": {  # STOP ads
  "de": (["SCHLUSS mit", "Werbung in deiner", "*IPTV-App!*"], "SCHLUSS mit Werbung in deiner IPTV-App! 🛑",
         "Schluss mit Werbung in deiner IPTV-App 🛑 Deine Playlist (M3U oder Xtream) läuft in jedem Player. Kanalo: kostenlos, ohne Werbung, ohne Konto."),
  "nl": (["STOP met", "reclame in je", "*IPTV-app!*"], "STOP met reclame in je IPTV-app! 🛑",
         "STOP met reclame in je IPTV-app 🛑 Je playlist (M3U of Xtream) werkt in elke speler. Kanalo: gratis, zonder reclame, zonder account.")},
}
TIPS = {
 "T1": {  # empty guide
  "hook": {"de": ["Dein TV-Guide", "zeigt", "*'Keine Infos'?*"], "it": ["La guida TV", "dice", "*'Nessuna info'?*"]},
  "title": {"de": "Leerer TV-Guide in deiner IPTV-App? So klappt's", "it": "Guida TV vuota nella tua app IPTV? Ecco la soluzione"},
  "cap": {"de": "Dein TV-Guide zeigt „Keine Informationen“? Fast immer ist es einer dieser 3 Gründe. Speichern 📌 Ich nutze Kanalo, das lädt den Guide im Hintergrund.",
          "it": "La guida TV dice «Nessuna informazione»? Quasi sempre è una di queste 3 cause. Salvalo 📌 Io uso Kanalo, carica la guida in background."},
  "tips": {"de": ("3 Gründe", "+ die Lösung.", [["Kein EPG-Link", "Frag deinen Anbieter nach der XMLTV-URL"], ["Sender-IDs passen nicht", "Die tvg-id muss stimmen"], ["Falsche Zeitzone", "Zeitversatz einstellen (z. B. +1 h)"]]),
           "it": ("3 cause", "+ la soluzione.", [["Manca il link EPG", "Chiedi l'URL XMLTV al fornitore"], ["ID dei canali diversi", "Il tvg-id deve corrispondere"], ["Fuso orario sbagliato", "Imposta lo scarto (es. +1 h)"]])}},
 "T2": {  # black screen
  "hook": {"es": ["¿Pantalla negra", "en la mitad de", "*tus canales?*"]},
  "title": {"es": "¿Los canales IPTV no cargan? Prueba esto primero"},
  "cap": {"es": "¿Pantalla negra en la mitad de tus canales? Prueba estas 3 cosas antes de culpar a la app. Guárdalo 📌"},
  "tips": {"es": ("Prueba esto", "primero.", [["Actualiza tu playlist", "Los proveedores cambian los enlaces"], ["Revisa tu suscripción", "Caducada = pantalla negra"], ["Crea una lista de favoritos", "Solo los canales que funcionan"]])}},
 "T3": {  # m3u vs xtream
  "hook": {"en": ["M3U or Xtream?", "*Which is better?*"]},
  "title": {"en": "M3U or Xtream? The difference in 15 seconds"},
  "cap": {"en": "Your provider gave you an M3U link AND Xtream details? Here's the difference in 15 seconds. Both work in Kanalo."},
  "tips": {"en": ("The difference", "in 15 seconds.", [["M3U = one long link", "Everything in one big file"], ["Xtream = server + login", "Films & series load separately, faster"], ["Got both? Use Xtream", "It updates faster"]])}},
 "T5": {  # buffering
  "hook": {"es": ["¿Tu IPTV se", "*corta sin parar?*"], "nl": ["Blijft je IPTV", "*steeds hangen?*"]},
  "title": {"es": "¿Tu IPTV se corta sin parar? 3 soluciones", "nl": "Blijft je IPTV steeds hangen? 3 oplossingen"},
  "cap": {"es": "¿Tu IPTV se corta sin parar? Prueba estas 3 soluciones antes de rendirte. Guárdalo 📌 Yo uso Kanalo en iPhone y Apple TV.",
          "nl": "Blijft je IPTV steeds hangen? Probeer deze 3 oplossingen voordat je opgeeft. Sla op 📌 Ik gebruik zelf Kanalo op iPhone en Apple TV."},
  "tips": {"es": ("3 soluciones", "rápidas.", [["Wi-Fi 5 GHz o cable", "El 2,4 GHz se satura rápido"], ["Baja a HD", "El 4K pide ~25 Mbit/s"], ["Reinicia el stream", "A menudo coge un servidor más rápido"]]),
           "nl": ("3 snelle", "oplossingen.", [["Wifi 5 GHz of kabel", "2,4 GHz raakt snel vol"], ["Kies HD", "4K vraagt ~25 Mbit/s"], ["Start de stream opnieuw", "Vaak pakt hij een snellere server"]])}},
 "T7": {  # too many channels
  "hook": {"fr": ["Tu scrolles", "parmi", "*1 000 chaînes ?*"], "it": ["Scorri tra", "*1.000 canali?*"]},
  "title": {"fr": "Tu scrolles parmi 1 000 chaînes IPTV ? Fais ça", "it": "Scorri tra 1.000 canali IPTV? Fai così"},
  "cap": {"fr": "Tu scrolles parmi 1 000 chaînes pour trouver la tienne ? 3 astuces rapides. Enregistre 📌 J'utilise Kanalo sur iPhone et Apple TV.",
          "it": "Scorri tra 1.000 canali per trovare il tuo? 3 trucchi veloci. Salvalo 📌 Io uso Kanalo su iPhone e Apple TV."},
  "tips": {"fr": ("3 astuces", "rapides.", [["Crée une liste de favoris", "Ton top 20 en premier"], ["Cherche, ne scrolle pas", "3 lettres et c'est trouvé"], ["Demande une liste plus courte", "Beaucoup filtrent par pays"]]),
           "it": ("3 trucchi", "veloci.", [["Crea una lista preferiti", "I tuoi 20 canali in cima"], ["Cerca, non scorrere", "3 lettere e l'hai trovato"], ["Chiedi una lista più corta", "Molti filtrano per paese"]])}},
 "T8": {  # movies are just a list of names (posters video: 1,215 views)
  "hook": {"en": ["Your movies are", "just a list", "*of names?*"], "fr": ["Tes films, juste", "une liste", "*de noms ?*"], "de": ["Deine Filme nur", "eine Liste", "*voller Namen?*"]},
  "title": {"en": "Your IPTV movies are just a list of names? Fix it", "fr": "Tes films IPTV ne sont qu'une liste de noms ? La solution",
            "de": "Deine IPTV-Filme sind nur eine Namensliste? So geht's besser"},
  "cap": {"en": "Your IPTV movies are just a long list of names? That's the player, not your playlist. 3 fixes. Save it 📌 I use Kanalo for posters and cast.",
          "fr": "Tes films IPTV ne sont qu'une longue liste de noms ? C'est le lecteur, pas ta playlist. 3 solutions. Enregistre 📌 J'utilise Kanalo pour les affiches et le casting.",
          "de": "Deine IPTV-Filme sind nur eine lange Liste mit Namen? Das liegt am Player, nicht an der Playlist. 3 Tipps. Speichern 📌 Ich nutze Kanalo für Cover und Besetzung."},
  "tips": {"en": ("3 fixes", "for a real library.", [["Use your Xtream login", "Films & series load as a library"], ["Pick a player with posters", "Covers, cast and ratings added"], ["Use 'continue watching'", "Pick up where you left off"]]),
           "fr": ("3 solutions", "pour une vraie vidéothèque.", [["Utilise ton login Xtream", "Films & séries en bibliothèque"], ["Un lecteur avec affiches", "Jaquettes, casting et notes"], ["Active 'Reprendre'", "Reprends là où tu t'es arrêté"]]),
           "de": ("3 Tipps", "für eine echte Mediathek.", [["Nutze deinen Xtream-Login", "Filme & Serien als Mediathek"], ["Player mit Covern wählen", "Cover, Besetzung, Bewertungen"], ["'Weiterschauen' nutzen", "Dort weiter, wo du warst"]])},
  "after": {"en": ["Posters, cast,", "*no ads.*"], "fr": ["Affiches, casting,", "*zéro pub.*"], "de": ["Cover, Besetzung,", "*null Werbung.*"]}},
}
ANYPL.update({"es": ["Tu playlist funciona", "*en cualquier app.*"]})

def build(tpl, lang):
    if tpl in H:
        lines, title, cap = H[tpl][lang]
        if tpl == "HE": sc = [hook("ph", "as_detail", lines, lang, 0), dev("atv_movies", ANYPL[lang], lang), phone("as_movies", FREEPL[lang]), end(lang)]
        if tpl == "HF": sc = [hook("dev", "atv_home", lines, lang, 0), dev("atv_gids", ANYPL[lang], lang), phone("as_movies", FREEPL[lang]), end(lang)]
        if tpl == "HG": sc = [hook("ph", "as_detail", lines, lang, 0), photo(lang), phone("as_movies", NOINT[lang]), end(lang)]
        if tpl == "HB": sc = [hook("ph", "as_detail", lines, lang, 0), photo(lang), phone("as_movies", NOINT[lang]), end(lang)]
        if tpl == "HD": sc = [hook("ph", "as_movies", lines, lang, 0), dev("atv_movies", ANYPL[lang], lang), photo(lang), end(lang)]
        return title, cap, sc, "hard"
    T = TIPS[tpl]; lines = T["hook"][lang]; title = T["title"][lang]; cap = T["cap"][lang]
    tt, sub, items = T["tips"][lang]
    tips = {"type": "tips", "site": True, "dur": 5.4, "title": tt, "sub": sub, "items": items}
    first = {"T1": ("dev", "atv_gids"), "T2": ("dev", "atv_home"), "T3": ("ph", "as_manage"), "T5": ("ph", "as_movies"),
             "T7": ("dev", "atv_home"), "T8": ("dev", "atv_movies")}[tpl]
    after = {"T1": lambda: dev("atv_gids", GUIDE_OK[lang], lang), "T2": lambda: photo(lang), "T3": lambda: phone("as_manage", ["Both work", "*in Kanalo.*"]),
             "T5": lambda: photo(lang), "T7": lambda: dev("atv_gids", GUIDE_OK[lang], lang),
             "T8": lambda: phone("as_detail", T["after"][lang])}[tpl]()
    return title, cap, [hook(first[0], first[1], lines, lang, 0), tips, after, end(lang)], "tip"

# schedule: 19–25 Nov (17–18 Nov already filled by last week's plan), slots 10/12/14/18
PLAN = [
 ("fr", "HE"), ("en", "HG"), ("de", "T8"), ("es", "HF"),   # 19
 ("it", "HE"), ("de", "HF"), ("fr", "T7"), ("en", "HE"),   # 20
 ("es", "HG"), ("nl", "HF"), ("fr", "HB"), ("de", "T1"),   # 21
 ("fr", "HG"), ("es", "T2"), ("en", "T8"), ("it", "HG"),   # 22
 ("de", "HE"), ("nl", "T5"), ("es", "HE"), ("fr", "HF"),   # 23
 ("en", "HB"), ("it", "T1"), ("de", "HD"), ("es", "T5"),   # 24
 ("fr", "T8"), ("nl", "HD"), ("it", "T7"), ("en", "T3"),   # 25
]
SLUG = {"HB": "ad-mid-film", "HD": "stop-ads", "HE": "wait-paying", "HF": "nobody-tells", "HG": "worst-moment",
        "T1": "empty-guide", "T2": "black-screen", "T3": "m3u-xtream", "T5": "buffering", "T7": "1000-channels", "T8": "movie-posters"}
vids = []; seed = 201
for i, (lang, tpl) in enumerate(PLAN):
    day = 19 + i // 4; hh = [10, 12, 14, 18][i % 4]
    title, cap, sc, style = build(tpl, lang)
    vid = f"2026-11-{day:02d}_{hh:02d}_{lang}-{SLUG[tpl]}"
    vids.append({"id": vid, "publish": f"2026-11-{day:02d}T{hh:02d}:00:00", "lang": lang, "style": style, "tpl": tpl, "seed": seed + i,
                 "title": title, "caption": cap + " " + TAGS[lang], "scenes": sc})
assert len(vids) == 28 and len({v["id"] for v in vids}) == 28
for v in vids: assert len(v["title"]) <= 90, v["title"]; assert sum(s["dur"] for s in v["scenes"]) > 9
json.dump({"videos": vids}, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(v["lang"] for v in vids), Counter(v["style"] for v in vids))

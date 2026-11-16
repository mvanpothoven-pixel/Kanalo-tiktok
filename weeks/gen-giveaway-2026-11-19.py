import json, sys
PURP_T = [120, 50, 170]; BLUE_T = [45, 45, 170]
A = "Kanalo · iPhone · iPad · Apple TV"
G = {
 "de": dict(hook=["3.000+ Nutzer!", "Wir verschenken", "*1 Jahr Pro.*"], label="APPLE TV  ·  START", app=["Der IPTV-Player", "*ohne Werbung.*"],
   tt="So geht's:", sub="gratis, dauert 1 Minute.", items=[["Geh auf kanalo.app", "Link in der Bio"], ["Hol dir deinen Code", "E-Mail eingeben, fertig"], ["Kanalo laden & einlösen", "1 Jahr Pro geschenkt"]],
   end=["Link in", "*der Bio.*"], a="Begrenzte Codes · wer zuerst kommt",
   title="🎉 3.000+ Nutzer! Wir verschenken 1 Jahr Kanalo Pro",
   cap="🎉 Über 3.000 Nutzer! Zur Feier verschenken wir 1 Jahr Kanalo Pro. Kanalo ist die werbefreie IPTV-App für iPhone, iPad & Apple TV: eigene Playlist rein und los. 👉 Link in der Bio, E-Mail eingeben, Code holen und in der App einlösen. Nur begrenzte Codes, sei schnell!",
   tags="#iptv #iptvdeutschland #appletv #iptvplayer #gewinnspiel", fbt="#iptv #iptvdeutschland #appletv"),
 "es": dict(hook=["¡3.000+ usuarios!", "Regalamos", "*1 año de Pro.*"], label="APPLE TV  ·  INICIO", app=["El reproductor IPTV", "*sin anuncios.*"],
   tt="Cómo conseguirlo:", sub="gratis, en 1 minuto.", items=[["Entra en kanalo.app", "Enlace en la bio"], ["Consigue tu código", "Pon tu e-mail y listo"], ["Descarga Kanalo y actívalo", "1 año de Pro gratis"]],
   end=["Enlace en", "*la bio.*"], a="Códigos limitados · el primero que llegue",
   title="🎉 ¡3.000+ usuarios! Regalamos 1 año de Kanalo Pro",
   cap="🎉 ¡Más de 3.000 usuarios! Para celebrarlo regalamos 1 año de Kanalo Pro. Kanalo es la app IPTV sin anuncios para iPhone, iPad y Apple TV: añades tu propia playlist y listo. 👉 Enlace en la bio, pon tu e-mail, recibe tu código y actívalo en la app. Códigos limitados, ¡date prisa!",
   tags="#iptv #iptvespaña #appletv #iptvplayer #sorteo", fbt="#iptv #iptvespaña #appletv"),
 "it": dict(hook=["3.000+ utenti!", "Regaliamo", "*1 anno di Pro.*"], label="APPLE TV  ·  HOME", app=["Il player IPTV", "*senza pubblicità.*"],
   tt="Come ottenerlo:", sub="gratis, in 1 minuto.", items=[["Vai su kanalo.app", "Link in bio"], ["Prendi il tuo codice", "Inserisci l'e-mail e basta"], ["Scarica Kanalo e attivalo", "1 anno di Pro in regalo"]],
   end=["Link", "*in bio.*"], a="Codici limitati · chi prima arriva",
   title="🎉 3.000+ utenti! Regaliamo 1 anno di Kanalo Pro",
   cap="🎉 Oltre 3.000 utenti! Per festeggiare regaliamo 1 anno di Kanalo Pro. Kanalo è l'app IPTV senza pubblicità per iPhone, iPad e Apple TV: aggiungi la tua playlist e via. 👉 Link in bio, inserisci la tua e-mail, ricevi il codice e attivalo nell'app. Codici limitati, sbrigati!",
   tags="#iptv #iptvitalia #appletv #iptvplayer #regalo", fbt="#iptv #iptvitalia #appletv"),
 "en": dict(hook=["3,000+ users!", "We're giving away", "*1 year of Pro.*"], label="APPLE TV  ·  HOME", app=["The IPTV player", "*without ads.*"],
   tt="How to claim:", sub="free, takes 1 minute.", items=[["Go to kanalo.app", "Link in bio"], ["Get your free code", "Enter your email, done"], ["Download Kanalo & redeem", "1 year of Pro, on us"]],
   end=["Link in", "*bio.*"], a="Limited codes · first come, first served",
   title="🎉 3,000+ users! We're giving away 1 year of Kanalo Pro",
   cap="🎉 3,000+ users! To celebrate, we're giving away 1 year of Kanalo Pro. Kanalo is the ad-free IPTV app for iPhone, iPad & Apple TV: add your own playlist and go. 👉 Link in bio, enter your email, get your code and redeem it in the app. Limited codes, be quick!",
   tags="#iptv #iptvusa #appletv #iptvplayer #giveaway", fbt="#iptv #iptvusa #appletv"),
}
PLAN = [("de", "2026-11-19T17:00:00"), ("es", "2026-11-19T20:00:00"), ("it", "2026-11-20T17:00:00"), ("en", "2026-11-20T20:00:00")]
vids = []
for i, (lang, pub) in enumerate(PLAN):
    g = G[lang]
    sc = [{"type": "s_device", "dur": 2.8, "instant": True, "asset": "atv_home", "lines": g["hook"], "size": 92, "label": g["label"], "tint": PURP_T, "z1": 1.08, "fx": 0.5},
          {"type": "s_phone", "dur": 2.4, "asset": "as_movies", "lines": g["app"], "tint": BLUE_T, "scroll": 0.5},
          {"type": "tips", "site": True, "dur": 5.0, "title": g["tt"], "sub": g["sub"], "items": g["items"]},
          {"type": "s_end", "dur": 2.6, "lines": g["end"], "a": g["a"]}]
    vid = f"{pub[:10]}_{pub[11:13]}_{lang}-giveaway-pro-year"
    vids.append({"id": vid, "publish": pub, "lang": lang, "style": "giveaway", "seed": 241 + i, "title": g["title"],
                 "caption": g["cap"] + " " + g["tags"], "fb": g["cap"] + " https://apps.apple.com/app/id6789590971 " + g["fbt"], "scenes": sc})
for v in vids: assert len(v["title"]) <= 90
json.dump({"videos": vids}, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print([v["id"] for v in vids])

"""Week 26 Nov – 2 Dec, v2: fun AI skits (people/pets) + white caption cards + baked music + end card.
Replaces the template videos of week-2026-11-26 (owner: 'andere video's, echt leuk, niet steeds dat plaatje').
Clips: Higgsfield seedance_2_0_mini, 6 s, 9:16, in videos/ai/clips/cNN.mp4 (14 clips, each used in 2 languages).
Usage: python3 weeks/fun-2026-11-26.py weeks/fun-2026-11-26.json
"""
import json, sys

TAGS = {"en": "#iptv #iptvusa #appletv #iptvplayer #funny",
        "fr": "#iptv #iptvfrance #appletv #iptvplayer #humour",
        "de": "#iptv #iptvdeutschland #appletv #iptvplayer #lustig",
        "es": "#iptv #iptvespaña #appletv #iptvplayer #humor",
        "it": "#iptv #iptvitalia #appletv #iptvplayer #divertente",
        "nl": "#iptv #iptvnederland #appletv #iptvplayer #humor"}

# clip -> lang -> (hook lines, payoff lines, title, caption body)
T = {
 1: {  # popcorn flies when the ad hits
  "fr": (["Quand la pub tombe PILE", "au meilleur moment 😤"], ["Ta propre playlist.", "Zéro pub. Kanalo."],
         "Quand la pub tombe PILE au meilleur moment 😤",
         "Quand la pub tombe pile au meilleur moment 😤 Ce n'est pas ta playlist, c'est l'app. Kanalo : ta playlist, zéro pub."),
  "en": (["When the ad hits at", "THE moment 😤"], ["Your own playlist.", "Zero ads. Kanalo."],
         "When the ad hits at THE moment 😤",
         "When the ad hits at THE moment 😤 That's not your playlist, it's the app. Kanalo: your own playlist, zero ads.")},
 2: {  # grandma winks
  "es": (["POV: la abuela (78) encontró", "un reproductor IPTV sin anuncios 👵"], ["Tu propia playlist.", "Cero anuncios. Gratis."],
         "POV: la abuela (78) encontró un reproductor IPTV sin anuncios 👵",
         "La abuela (78) lo pilló antes que tú 👵 Tu propia playlist, cero anuncios. Kanalo es gratis en iPhone, iPad y Apple TV."),
  "fr": (["POV : Mamie (78 ans) a trouvé", "un lecteur IPTV sans pub 👵"], ["Ta propre playlist.", "Zéro pub. Gratuit."],
         "POV : Mamie (78 ans) a trouvé un lecteur IPTV sans pub 👵",
         "Mamie (78 ans) a compris avant toi 👵 Ta propre playlist, zéro pub. Kanalo est gratuit sur iPhone, iPad & Apple TV.")},
 3: {  # typing login with the remote, falls asleep
  "de": (["Ich, wie ich meinen IPTV-Login", "mit der Fernbedienung tippe 😴"], ["Kanalo: QR-Code mit dem", "iPhone scannen. Fertig."],
         "Ich, wie ich meinen IPTV-Login mit der Fernbedienung tippe 😴",
         "Jeder, der seinen Xtream-Login schon mal mit der Fernbedienung getippt hat 😴 In Kanalo scannst du einfach einen QR-Code mit dem iPhone."),
  "es": (["Yo escribiendo mi login IPTV", "con el mando 😴"], ["Kanalo: escanea un QR", "con el iPhone. Listo."],
         "Yo escribiendo mi login IPTV con el mando 😴",
         "Todo el que ha escrito su login Xtream con el mando 😴 En Kanalo escaneas un código QR con el iPhone y listo.")},
 4: {  # spits out coffee
  "en": (["When you realise you paid €72", "for an IPTV PLAYER 💀"], ["Kanalo is free.", "No ads. No account."],
         "When you realise you paid €72 for an IPTV PLAYER 💀",
         "When you realise you paid €72 a year just for an IPTV player 💀 The player doesn't make your playlist better. Kanalo is free, no ads, no account."),
  "nl": (["Als je ziet dat je €72 betaalde", "voor een IPTV-SPELER 💀"], ["Kanalo is gratis.", "Geen reclame. Geen account."],
         "Als je ziet dat je €72 betaalde voor een IPTV-SPELER 💀",
         "Als je doorhebt dat je €72 per jaar betaalt voor alleen een IPTV-speler 💀 Kanalo is gratis, zonder reclame en zonder account.")},
 5: {  # dog with remote
  "es": (["Hasta mi perro encontró", "una app IPTV sin anuncios 🐶"], ["Kanalo: gratis.", "Cero anuncios."],
         "Hasta mi perro encontró una app IPTV sin anuncios 🐶",
         "Hasta mi perro sabe saltarse los anuncios 🐶 Kanalo: tu propia playlist, gratis y sin anuncios."),
  "de": (["Sogar mein Hund hat eine", "IPTV-App ohne Werbung gefunden 🐶"], ["Kanalo: kostenlos.", "Null Werbung."],
         "Sogar mein Hund hat eine IPTV-App ohne Werbung gefunden 🐶",
         "Sogar mein Hund ist schlauer als meine alte IPTV-App 🐶 Kanalo: deine eigene Playlist, kostenlos und ohne Werbung.")},
 6: {  # friends throw cushions
  "fr": (["Soirée film + appli IPTV", "pleine de pubs = ça 😤"], ["Même playlist.", "Kanalo. Zéro pub."],
         "Soirée film + appli IPTV pleine de pubs = ça 😤",
         "Soirée film avec une appli IPTV pleine de pubs 😤 Même playlist dans Kanalo, et plus aucune pub."),
  "en": (["Movie night + an IPTV app", "full of ads = this 😤"], ["Same playlist.", "Kanalo. Zero ads."],
         "Movie night + an IPTV app full of ads = this 😤",
         "Movie night with an IPTV app full of ads 😤 Same playlist in Kanalo, zero ads.")},
 7: {  # dad falls asleep scrolling
  "it": (["Papà che scorre", "1.000 canali IPTV 😴"], ["Preferiti + ricerca in Kanalo.", "3 lettere e via."],
         "Papà che scorre 1.000 canali IPTV 😴",
         "Ogni papà che scorre 1.000 canali per trovarne uno 😴 In Kanalo metti i preferiti in cima o cerchi con 3 lettere."),
  "fr": (["Papa qui scrolle", "1 000 chaînes IPTV 😴"], ["Favoris + recherche dans Kanalo.", "3 lettres et c'est trouvé."],
         "Papa qui scrolle 1 000 chaînes IPTV 😴",
         "Tous les papas qui scrollent 1 000 chaînes pour en trouver une 😴 Dans Kanalo : favoris en haut, ou tu cherches avec 3 lettres.")},
 8: {  # kid shows dad, mind blown
  "de": (["Wenn dein Kind dir eine IPTV-App", "OHNE Werbung zeigt 🤯"], ["Kanalo.", "Gratis im App Store."],
         "Wenn dein Kind dir eine IPTV-App OHNE Werbung zeigt 🤯",
         "Wenn dein Kind dir zeigt, dass deine Playlist auch ohne Werbung läuft 🤯 Kanalo, kostenlos für iPhone, iPad & Apple TV."),
  "es": (["Cuando tu hijo te enseña una", "app IPTV SIN anuncios 🤯"], ["Kanalo.", "Gratis en la App Store."],
         "Cuando tu hijo te enseña una app IPTV SIN anuncios 🤯",
         "Cuando tu hijo te enseña que tu playlist funciona sin anuncios 🤯 Kanalo, gratis en iPhone, iPad y Apple TV.")},
 9: {  # bathrobe victory dance
  "nl": (["Ik na het verwijderen van", "mijn IPTV-app vol reclame 💃"], ["Kanalo: mijn eigen playlist.", "Nul reclame."],
         "Ik na het verwijderen van mijn IPTV-app vol reclame 💃",
         "Ik na het verwijderen van mijn IPTV-app vol reclame 💃 Zelfde playlist in Kanalo, nul reclame, gratis."),
  "it": (["Io dopo aver cancellato la mia", "app IPTV piena di pubblicità 💃"], ["Kanalo: la mia playlist.", "Zero pubblicità."],
         "Io dopo aver cancellato la mia app IPTV piena di pubblicità 💃",
         "Io dopo aver cancellato l'app IPTV piena di pubblicità 💃 Stessa playlist in Kanalo, zero pubblicità, gratis.")},
 10: {  # cat vs black screen
  "en": (["Black screen on half", "your channels again? 🐱"], ["Refresh your playlist.", "Then try Kanalo."],
         "Black screen on half your channels again? 🐱",
         "Black screen on half your channels? 🐱 First refresh your playlist (providers change links). Then give it a clean player: Kanalo, free."),
  "de": (["Schon wieder schwarzes Bild", "bei der Hälfte der Sender? 🐱"], ["Playlist aktualisieren.", "Dann Kanalo testen."],
         "Schon wieder schwarzes Bild bei der Hälfte der Sender? 🐱",
         "Schwarzes Bild bei der Hälfte deiner Sender? 🐱 Erst die Playlist aktualisieren (Anbieter ändern Links). Dann ein sauberer Player: Kanalo, kostenlos.")},
 11: {  # skeleton waiting
  "fr": (["Moi qui attends que le guide TV", "de mon appli IPTV charge 💀"], ["Kanalo charge le guide", "en arrière-plan."],
         "Moi qui attends que le guide TV de mon appli IPTV charge 💀",
         "Moi qui attends que le guide TV de mon appli IPTV charge 💀 Kanalo charge le guide en arrière-plan. Gratuit, sans pub."),
  "en": (["Me waiting for my IPTV", "TV guide to load 💀"], ["Kanalo loads the guide", "in the background."],
         "Me waiting for my IPTV TV guide to load 💀",
         "Me waiting for my IPTV guide to load 💀 Kanalo loads the guide in the background. Free, no ads.")},
 12: {  # satisfied popcorn man
  "es": (["POV: por fin encontraste un", "reproductor IPTV sin anuncios 🍿"], ["Kanalo. Gratis.", "iPhone, iPad y Apple TV."],
         "POV: por fin encontraste un reproductor IPTV sin anuncios 🍿",
         "POV: por fin un reproductor IPTV sin anuncios 🍿 Tu propia playlist en Kanalo, gratis en iPhone, iPad y Apple TV."),
  "fr": (["POV : tu as enfin trouvé un", "lecteur IPTV sans pub 🍿"], ["Kanalo. Gratuit.", "iPhone, iPad & Apple TV."],
         "POV : tu as enfin trouvé un lecteur IPTV sans pub 🍿",
         "POV : enfin un lecteur IPTV sans pub 🍿 Ta propre playlist dans Kanalo, gratuit sur iPhone, iPad & Apple TV.")},
 13: {  # walks out with suitcase
  "de": (["Ich, wie ich meine IPTV-App", "nach der 4. Werbung verlasse 💔"], ["Neuer Player: Kanalo.", "Null Werbung."],
         "Ich, wie ich meine IPTV-App nach der 4. Werbung verlasse 💔",
         "Nach der 4. Werbung war Schluss 💔 Gleiche Playlist, neuer Player: Kanalo, ohne Werbung und kostenlos."),
  "nl": (["Ik die mijn IPTV-app verlaat", "na de 4e reclame 💔"], ["Nieuwe speler: Kanalo.", "Nul reclame."],
         "Ik die mijn IPTV-app verlaat na de 4e reclame 💔",
         "Na de 4e reclame was het klaar 💔 Zelfde playlist, nieuwe speler: Kanalo, zonder reclame en gratis.")},
 14: {  # cosy couple
  "it": (["Le nostre serate film da quando", "abbiamo cambiato player IPTV ❤️"], ["Kanalo: niente pubblicità,", "vera guida TV."],
         "Le nostre serate film da quando abbiamo cambiato player IPTV ❤️",
         "Le nostre serate film da quando abbiamo cambiato player ❤️ Kanalo: la nostra playlist, niente pubblicità, vera guida TV."),
  "es": (["Nuestras noches de peli desde que", "cambiamos de reproductor IPTV ❤️"], ["Kanalo: sin anuncios,", "guía TV de verdad."],
         "Nuestras noches de peli desde que cambiamos de reproductor IPTV ❤️",
         "Nuestras noches de peli desde que cambiamos de reproductor ❤️ Kanalo: nuestra playlist, sin anuncios, guía TV de verdad.")},
}

OLD = json.load(open("weeks/week-2026-11-26.json"))["videos"]  # same slots / languages / scheduled posts
R1 = list(range(1, 15)); R2 = [1, 2, 3, 4, 5, 7, 6, 8, 9, 10, 12, 11, 13, 14]
CLIPS = R1 + R2
MUSIC = ["phonk", "afro", "lofi", "synthwave", "house"]
vids = []
for i, (o, c) in enumerate(zip(OLD, CLIPS)):
    lang = o["lang"]; hook, pay, title, body = T[c][lang]
    assert len(title) <= 90, title
    vids.append({"id": o["id"].split("_", 2)[0] + "_" + o["id"].split("_", 2)[1] + f"_{lang}-fun{c:02d}",
                 "old_id": o["id"], "publish": o["publish"], "lang": lang, "clip": c, "music": MUSIC[i % 5], "seed": 401 + i,
                 "hook": hook, "payoff": pay, "title": title, "caption": body + " " + TAGS[lang]})
assert len({v["id"] for v in vids}) == 28
json.dump({"videos": vids}, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print("ok", len(vids))

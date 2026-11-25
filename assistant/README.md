# AI-assistent voor Kanalo en TableJoy (Grok / xAI)

Eén kleine Node-server (geen dependencies) tussen je apps en Grok.
De xAI-sleutel staat alleen op de server. De apps en de werkvloer krijgen hem nooit.

```
iOS-app (KANALO_TOKEN / TABLEJOY_TOKEN) ─┐
                                         ├─► server.mjs ──► Grok (api.x.ai)
Werkvloer (OWNER_TOKEN) ─────────────────┘        │
                                                  ├─► Kanalo MCP-server (bugs, abonnementen, meldingen)
                                                  ├─► App Store Connect (reviews)
                                                  └─► TableJoy-API (reserveringen)
```

## Starten

```sh
cd assistant
cp .env.example .env      # vul in
node --env-file=.env server.mjs
npm test                  # 9 tests tegen een nep-xAI, kost niets
```

## Endpoints

| Methode | Pad | Token | Wat |
|---|---|---|---|
| POST | `/assistant` | app of owner | `{app, messages:[{role,content}]}` of `{app, agent, role, task}` → `{reply, tools_used, demo_data, ms}` |
| GET | `/werkvloer/state?app=kanalo` | owner | echte taken, logboek en cijfers van vandaag |
| GET | `/werkvloer/kanalo`, `/werkvloer/tablejoy` | geen | de werkvloer-pagina zelf (bevat geen geheimen) |
| GET | `/health` | geen | status |

## Tokens en wat elke assistent mag lezen

| Token | Waar | Tools (function calling) |
|---|---|---|
| `KANALO_TOKEN` | Kanalo-app | `mijn_abonnement`, `mijn_bugrapporten`: alleen van het toestel in `X-Device-Id` |
| `TABLEJOY_TOKEN` | TableJoy-app | `reserveringen`: alleen van het restaurant in `X-Restaurant-Id` |
| `OWNER_TOKEN` | werkvloer | Kanalo: `bugrapporten`, `bugrapport`, `reviews`, `abonnementen`, `app_store_meldingen` · TableJoy: `reserveringen` (alle) |

Het device- of restaurant-ID komt uit de request-header, nooit van het model.
E-mailadressen en device-ID's worden uit de toolresultaten gefilterd voordat Grok ze ziet.
Is een bron nog niet ingesteld, dan krijgt de assistent voorbeelddata met `demo: true`. Hij moet dat dan ook zo zeggen.

> Een app-token zit in de app-binary en kan eruit gehaald worden. Het is níet de xAI-sleutel.
> Daarmee kan iemand alleen de app-assistent gebruiken (met rate limit), niet je bedrijfsdata lezen.
> Lekt het, maak dan een nieuw token en zet dat in de volgende build.

## Kanalo-regel

Kanalo is alleen een speler. Dat staat in de systeemprompt.
Daarnaast controleert de server elk Kanalo-antwoord. Belooft het gratis zenders, films of sport, dan laat de server Grok het één keer herschrijven. Lukt dat niet, dan gaat er een vast, veilig antwoord uit.

## Werkvloer

`public/werkvloer.html` is je bestaande werkvloer-artifact, met deze wijzigingen:
- `claude.use("sample")` is weg. `startTask()` doet nu `fetch(server + "/assistant")`.
- Een paneel "Verbinding met de server": je vult het werkvloer-token één keer in en het blijft alleen in je browser.
- Het logboek, de cijfers en "laatste taak" per assistent komen van `/werkvloer/state` (elke 15 s). Nep-afrondingen stoppen zodra je verbonden bent.

Open hem op `https://<jouw-server>/werkvloer/kanalo` of `/werkvloer/tablejoy`.

## Xcode (Kanalo en TableJoy)

1. Sleep `ios/AssistantView.swift` in het project (target aangevinkt).
2. Maak `Secrets.xcconfig` (staat in `.gitignore`):
   ```
   ASSISTANT_BASE_URL = https:/$()/assistent.jouwdomein.nl
   ASSISTANT_TOKEN = <KANALO_TOKEN of TABLEJOY_TOKEN>
   ```
   Koppel hem bij Project → Info → Configurations (Debug en Release).
3. Info.plist:
   ```xml
   <key>AssistantBaseURL</key><string>$(ASSISTANT_BASE_URL)</string>
   <key>AssistantToken</key><string>$(ASSISTANT_TOKEN)</string>
   ```
4. Knop in Instellingen:
   ```swift
   // Kanalo
   NavigationLink { AssistantView(app: .kanalo, deviceID: <jullie device-ID>) } label: {
       Label("Assistent", systemImage: "sparkles")
   }
   // TableJoy
   NavigationLink { AssistantView(app: .tablejoy, restaurantID: <restaurant-ID>) } label: {
       Label("Assistent", systemImage: "sparkles")
   }
   ```
   Gebruik voor Kanalo hetzelfde device-ID dat de app naar de bugrapport-server stuurt.
   Dan kan de assistent het eigen abonnement en de eigen bugrapporten vinden.

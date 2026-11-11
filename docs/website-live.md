# Live website visitors in Kanalo Live

Goal: see in the Kanalo Live dashboard who is on kanalo.app right now, where they come from, and who taps
"Download in the App Store", next to downloads and Pro purchases.

Three parts. Part 1 is done in this repo; parts 2 and 3 live in the kanalo.app server code.

## 1. Landing pages (done: `site_pages.py`)

Every generated page sends small beacons to `POST /api/t` (same origin, `text/plain` JSON body):

| `e`     | When                                                   |
|---------|--------------------------------------------------------|
| `view`  | Page loaded                                            |
| `ping`  | Every 15 s while the tab is visible (max 30 min)       |
| `store` | Click on any `apps.apple.com` link                     |

Body: `{"e": "view", "p": "/nl/iptv-speler-iphone-apple-tv/", "l": "nl", "r": "www.google.com", "s": "m1bqfpfen2"}`
- `p` path, `l` page language, `r` referrer host only (empty when direct), `s` random id for this page load
  (kept in memory only; no cookie, no localStorage).
- Nothing is sent when the browser has Do Not Track or Global Privacy Control on.

Pages on kanalo.app that are not made by `site_pages.py` (home page, /admin excluded) need the same snippet:
copy `TRACK` from `site_pages.py` into their `<script>` tag.

## 2. Server: receive and store (`/api/t`)

- Accept `POST /api/t`, parse the body as JSON, answer `204` immediately (also on bad input).
- Only accept `e` in `view|ping|store`; cut `p` to 200 chars, `l` to 10, `r` to 100, `s` to 16.
- Country: from the CDN/proxy country header (e.g. `CF-IPCountry`). Do **not** store the IP address.
- Drop obvious bots (user agent contains `bot|crawler|spider|preview|curl`).
- Rate limit per IP in memory (e.g. 30 requests/minute), never persisted.
- Table `web_events(at timestamptz, kind text, path text, lang text, country text, referrer text, session text)`,
  keep 90 days.

## 3. Kanalo connector: two read-only tools

`get_web_live` (no arguments) — for the 2-second refresh:
```json
{
  "now": 7,                                   // distinct sessions with any event in the last 60 s
  "by_country": {"FR": 3, "NL": 2, "DE": 2},
  "by_page": {"/fr/lecteur-iptv-iphone-apple-tv/": 3},
  "events": [                                 // newest first, last 30 minutes, max 100; only view and store
    {"at": "2026-11-11T17:42:10Z", "kind": "store", "country": "FR", "path": "/fr/...", "lang": "fr", "referrer": "www.google.com"}
  ]
}
```

`get_web_stats` (`period` or `from`/`to`, same as `get_installs`):
```json
{
  "period": {"from": "2026-11-05", "to": "2026-11-11"},
  "visitors": 1840,                          // distinct sessions
  "views": 2210,
  "store_clicks": 312,
  "by_country": {"FR": {"visitors": 420, "store_clicks": 80}},
  "by_page": {"/fr/...": {"visitors": 420, "store_clicks": 80}},
  "by_referrer": {"www.google.com": 900, "": 600, "www.tiktok.com": 200},
  "days": [{"date": "2026-11-05", "visitors": 250, "store_clicks": 40}]
}
```

## 4. Dashboard (Kanalo Live), once the tools exist

- Header: "**7** nu op de website".
- Globe: blue dots for live visitors by country; a pulse plus toast for "Bezoeker uit Frankrijk tikte op Download".
- Overview, per chosen period: website visitors → App Store clicks → downloads → Pro.
- Live tab: website events in the same live list as downloads and purchases.

## App Store

Apple does not share who is on the App Store page right now. Daily numbers (impressions, product page views,
conversion) come from App Store Connect Analytics with a 1–2 day delay; the server can fetch them with the
App Store Connect Analytics Reports API and expose them as a third tool if wanted.

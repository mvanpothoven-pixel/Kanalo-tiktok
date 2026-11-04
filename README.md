# Kanalo TikTok

Organic TikTok content for [Kanalo](https://kanalo.app), produced and scheduled by Claude.

- `kanalo_video.py` — video engine (1080×1920, 30 fps). Scene types: hook, oldapp, wait, reveal, tv, phone, list, compare, steps, qr, price, cta.
- `assets/` — the real Kanalo logo and app screens with **demo content only**.
- `weeks/YYYY-MM-DD.json` — one spec per week: every video's scenes, publish time, caption and hashtags.
- `videos/` — rendered MP4s. Metricool fetches them from the raw GitHub URL.

Render a week: `python3 kanalo_video.py weeks/2026-11-05.json videos`

## Content rules
1. Never show real channels or broadcaster logos, real film/series posters, the "adult" category, sports-league names or a real playlist URL. Only the demo screens in `assets/`.
2. Always position Kanalo as a player: "bring your own M3U or Xtream playlist". Never promise free channels, films or sports.
3. Captions: one short hook line, the benefit, 4–5 hashtags. No #freemovies, #gratistv or similar.
4. TikTok posts are marked as own-brand commercial content.

## Style v3 (from 5 Nov 2026) — owner's standing rules
1. **Cover first:** frame 0 shows the problem/title (`s_hook`, instant text). Posts use `videoCoverMilliseconds: 200`.
2. **Music always:** `kanalo_music.py` is baked into every render (unique `seed` per video).
3. **Solve a real IPTV problem, don't sell:** hook → causes/fix (`tips`) → result (`s_device`/`s_photo`) → soft `s_end` ("Ik gebruik zelf Kanalo"). No download buttons.
4. **Look of kanalo.app:** dark, left-aligned headlines with an italic gradient accent word, devices on colored tiles.
5. 3 posts per day (10:00, 14:00, 18:00) on TikTok, Instagram and Facebook. Spec: `weeks/2026-11-05-v3.json`.

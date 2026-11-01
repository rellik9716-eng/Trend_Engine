# CLAUDE_BRAIN — Trend Engine

Read this first. It is the architecture source of truth; do not re-derive it from code.

## ARCHITECTURE

```
trend_engine/
├── app.py              ← Streamlit dashboard (MAIN ENTRY). One-click RUN FULL EMPIRE SEQUENCE:
│                         Phase 1 scraper (subprocess) → Phase 2 Claude analysis → Phase 3 edge-tts voiceover.
│                         Renders EMPIRE_STATUS.txt + ad concepts + audio.
├── scraper.py          ← Multi-platform trend scraper (see LOGIC below).
├── run_engine.py       ← Terminal loop: scraper → `claude` CLI analysis pass (niche ad concepts).
├── video_factory.py    ← Kinetic High-Tech video engine (1080x1920 vertical, moviepy 2.x).
├── kinetic_bg.py       ← NumPy per-frame 3D perspective grid + particles + scanlines.
├── glitch.py           ← apply_glitch(): horizontal tear + RGB split + row swap, 0.1s every 4s.
├── config.json         ← agency/product/niche/pain_points/keywords + per-platform enable + API keys.
├── APIKeys.env         ← dotenv keys (YOUTUBE_API_KEY, ...). NOT committed.
├── data/raw_trends.json      ← scraper output (gitignored).
├── EMPIRE_STATUS.txt         ← per-run dashboard report (gitignored).
├── ai_images/              ← drop AI renders for the video factory (gitignored).
└── output/final_ads/         ← rendered 9:16 MP4s (gitignored).
```

## LOGIC

- **scraper.py** — `load_config()` merges config.json over defaults. `platform_status(cfg)` decides Active/Inactive per platform (checks required keys). `main()` runs every active fetcher through a per-source try/except (a dead source never kills the run) and writes `data/raw_trends.json`.
  - Fetchers: `fetch_youtube` (Data API v3 trending + keyword search), `fetch_google_custom_search` (Serper key), `fetch_google_trends` (RSS), `fetch_tiktok` (Playwright async — embedded JSON extraction; the bypass path), `fetch_hackernews` (free), `fetch_techcrunch` (free RSS), `fetch_reddit`, `fetch_instagram`, `fetch_facebook`, `fetch_twitter_x`, `fetch_pinterest`.
  - Semantic niche scoring: trends are scored against `config.search_keywords`; the EMPIRE_STATUS report flags "Niche hits (score >= 2)" and a top-3 signals table. `relevance_score` rides on every trend object.
- **video_factory.py** — `build(image_path, headline, out_path, duration)`. Layer stack, bottom→top: `kinetic_bg` (living grid) → AI image hologram (Gaussian-feathered alpha + cyan tint) → `hud_overlay` (breathing pulse + HUD text) + `decode_text` (scramble→settle headline) → `apply_glitch()` on the composite. moviepy 2.x API only (`from moviepy import ...`, `vfx.*`, NO `moviepy.editor`). Output: 1080x1920, 24fps, libx264.
- **kinetic_bg.py / glitch.py** — pure NumPy frame functions, no per-frame allocations beyond the frame itself.
- **app.py** — thin UI. Never imports scraper internals; calls it via `subprocess` so a scrape crash can't kill the dashboard.

## STATE (as of 2026-11-01)

- Last live run: 40 trends, 8 niche hits, clean source health (YouTube 20 / Google Trends 10 / TikTok 10). Niche pulse: anxiety-driven AI-sales-automation run.
- Video factory: vertical renders confirmed (output/final_ads/*.mp4).
- TikTok runs through the Playwright bypass; no keys needed.

## RULES

- moviepy is 2.x — `with_duration` BEFORE `with_effects([vfx.CrossFadeIn])`; `with_opacity(lambda)` unsupported (bake pulses into the frame fn); `with_position(("right","bottom"))` anchors correctly.
- app.py runs scraper via subprocess with cwd = repo root — keep scraper side-effect-free of the Streamlit runtime.
- config.json holds API keys → keep it out of public repos or use Streamlit Cloud secrets (see README).
- Do not commit: output/, ai_images/, data/, __pycache__/, *.zip, *.env, EMPIRE_STATUS.txt.

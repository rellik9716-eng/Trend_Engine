<div align="center">

# 👻 TREND ENGINE

### **The Deep-Stack Intelligence Pipeline**
*Live trend capture → semantic niche scoring → kinetic video synthesis. One click. Zero friction.*

`STREAMLIT` · `PLAYWRIGHT` · `MOVIEPY` · `NUMPY` · `OPENCV`

[![Python](https://img.shields.io/badge/Python-3.10+-00C8FF)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-Community_Cloud-7AFC8)]()
[![Vertical](https://img.shields.io/badge/Output-1080x1920-9FE8FF)]()

</div>

---

## THE SYSTEM

Trend Engine is a full-stack media intelligence platform. It watches the world's largest
attention markets, isolates the signals that matter to **your** niche with a semantic scoring
model, and synthesizes broadcast-grade 9:16 vertical video — a scrolling kinetic grid,
hologram image compositing, decode-text typography, and a periodic signal-tear glitch —
in a single automated pass.

```
┌─────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌───────────────┐
│  GLOBAL     │   │  SEMANTIC NICHE  │   │  KINETIC VIDEO   │   │   EMPIRE      │
│  SCRAPE     │──▶│  SCORER          │──▶│  SYNTHESIS       │──▶│   DASHBOARD   │
│ 11 sources  │   │ relevance_score  │   │ 1080x1920 MP4    │   │ Streamlit     │
└─────────────┘   └──────────────────┘   └──────────────────┘   └───────────────┘
```

## HOW IT WORKS

**Phase 1 — Global Scrape.** `scraper.py` pulls live signals from YouTube (Data API v3),
Google Trends, TikTok (headless browser with cookie-wall bypass), Hacker News, TechCrunch,
Reddit, Instagram, Facebook, X, and Pinterest. Each source runs in isolation — a dead
endpoint degrades the run, it never kills it.

**Phase 2 — Semantic Niche Scoring.** Every title is scored against your configured niche
vocabulary: weighted phrase matches, word-level fallbacks, and power-word amplification
(viral / trend / breakthrough / urgent). The top signals, source-health telemetry, error
log, and a one-line **Niche Pulse** (hype-vs-anxiety read) are written to `EMPIRE_STATUS.txt`
on every run.

**Phase 3 — Kinetic Video Synthesis.** `video_factory.py` stacks the layers:
a living 3D perspective grid with drifting particles (pure NumPy, per-frame) at the base;
a hologram AI image (Gaussian-feathered alpha, cyan spectre tint) in the middle;
a breathing HUD and scramble-decode headline on top; `apply_glitch()` tears the finished
composite every 4 seconds. Output: 1080×1920 @ 24fps, TikTok/Reels/Shorts-native.

**Phase 4 — The Empire Dashboard.** `app.py` (Streamlit) exposes the whole pipeline as
one button: **RUN FULL EMPIRE SEQUENCE**. Live phase log, the Empire Status readout,
ad-concept renderings, and generated voiceover — in a dark-signal console UI.

## THE AESTHETIC

Dark void backgrounds. Consolas monospace. Cyan `#00C8FF` and mint `#7AFC88` on near-black.
Scanlines. A perspective grid that never stops moving. A glitch that hits like a signal drop.
It does not look like a script. It looks like the feed from a 2049 operations room.

## RUN LOCALLY

```powershell
# 1. Clone + enter
git clone <YOUR_REPO_URL> trend_engine
cd trend_engine

# 2. Isolated environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Dependencies
pip install -r requirements.txt
playwright install chromium        # for the TikTok bypass

# 4. Configure
#    config.json  -> agency, product, target_niche, pain_points, search_keywords
#    APIKeys.env  -> YOUTUBE_API_KEY=...   (only what you enable is required)

# 5. Launch the dashboard
streamlit run app.py
```

Hit **RUN FULL EMPIRE SEQUENCE**. Renders land in `output/final_ads/`.

### Headless run (no UI)

```powershell
python run_engine.py      # scrape -> Claude analysis pass -> output/niche_ad_concepts.json
```

## DEPLOY TO STREAMLIT COMMUNITY CLOUD

1. Push this folder to GitHub (commands in the launch checklist below).
2. [streamlit.io/cloud](https://streamlit.io/cloud) → **New deployment** → select the repo.
3. **Main file: `app.py`**
4. **Python version: 3.11** · Resource: Basic is fine for scraping; Standard recommended
   for in-cloud video renders.
5. Move API keys out of `config.json` into **Settings → Secrets**:
   `YOUTUBE_API_KEY=...`, `SERPER_KEY=...` — then read via `st.secrets` (or keep
   keyless sources enabled: Hacker News, TechCrunch, Google Trends, TikTok bypass).
6. Deploy. The dashboard is live on a `*.streamlit.app` URL.

## REPO LAYOUT

| Path | Role |
|---|---|
| `app.py` | Streamlit dashboard — **main entry** |
| `scraper.py` | Multi-platform scraper + niche scoring + Empire Status |
| `video_factory.py` · `kinetic_bg.py` · `glitch.py` | Kinetic video engine |
| `run_engine.py` | Terminal pipeline loop |
| `config.json` | Agency / niche / platform configuration |
| `requirements.txt` | Full dependency manifest |
| `CLAUDE_BRAIN.md` | Architecture brain for AI-assisted sessions |

---

<div align="center">

**SIGNAL NOISE IS THE ENEMY. THE ENGINE KEEPS ONLY THE SIGNAL.**

`v1.0 — THE EMPIRE BUILD`

</div>

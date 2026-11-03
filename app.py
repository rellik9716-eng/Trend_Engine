"""HAVENWRIGHT INTELLIGENCE ENGINE — the Winning Ad Architect (white-label SaaS).

Two modes:
  HUNT   — find a market gap (high pain, low competition) + its Mood, then
           render a 3-Beat 2049 ad from it.
  RUN    — the original scrape->score->batch flow.

Base footage: client's own (stabilized + brand-graded) OR hyperreal AI (flux).
Run: streamlit run app.py
"""
import json
import os
import sys
import time

import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
TREND_ENGINE = os.path.join(BASE, "trend-engine")
VIDEO_FACTORY = os.path.join(BASE, "video_factory")
for p in (TREND_ENGINE, VIDEO_FACTORY):
    if p not in sys.path:
        sys.path.insert(0, p)

EMPIRE_STATUS = os.path.join(TREND_ENGINE, "EMPIRE_STATUS.txt")
RAW_TRENDS = os.path.join(TREND_ENGINE, "raw_trends.json")
FINAL_ADS = os.path.join(VIDEO_FACTORY, "output", "final_ads")
AI_IMAGES = os.path.join(VIDEO_FACTORY, "ai_images")
LOGO_PATH = os.path.join(BASE, "assets", "havenwright_logo.png")

st.set_page_config(page_title="Havenwright Intelligence Engine", page_icon="👻", layout="wide")
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] { background: #060a12; color: #d8f4ff; }
    h1 { font-family: consolas, monospace; color: #00c8ff; letter-spacing: 3px; font-size: 2.2rem; }
    h2 { font-family: consolas, monospace; color: #7affc8; }
    .stButton > button { background: #00c8ff; color: #060a12; border: none;
      font-family: consolas, monospace; font-weight: bold; letter-spacing: 1px;
      padding: 0.6rem 1.4rem; }
    .stButton > button:hover { background: #7affc8; color: #060a12; }
    pre { background: #0a1220; border: 1px solid #123; color: #9fe8ff;
      font-family: consolas, monospace; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — white-label branding + controls
# ---------------------------------------------------------------------------
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.markdown(
            """
            <div style="text-align:center; padding:0.6rem 0.4rem;border:1px solid #00c8ff44;
                        border-radius:8px;background:linear-gradient(135deg,#0a1220,#060a12);">
              <div style="font-family:consolas, monospace;color:#00c8ff;letter-spacing:4px;font-weight:bold;">HAVENWRIGHT</div>
              <div style="font-family:consolas, monospace;color:#7affc8;font-size:0.7rem;letter-spacing:2px;">INTELLIGENCE ENGINE</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.divider()

    st.header("⚙ CONTROL DECK")
    client_view = st.checkbox("👁️ Client View (Simplified)", value=False)

    st.markdown("**Base footage**")
    source = st.radio("Source", ["Use Hyperreal AI", "Use My Raw Footage"], index=0)
    ai_prompt = st.text_input("AI prompt", value="B2B SaaS founder, futuristic 2049, holographic", disabled=(source == "Use My Raw Footage"))
    raw_upload = st.file_uploader("Raw footage (.mp4)", type=["mp4", "mov"], disabled=(source != "Use My Raw Footage"))

    st.markdown("**A/B batch — render N gaps at once**")
    batch_n = st.slider("Number of Concepts to Render", min_value=1, max_value=5, value=3)

    st.markdown("**Headline (decodes on screen)**")
    headline = st.text_input("Headline", value="THE SIGNAL IS LIVE", max_chars=40)

    # fallback image (used if flux fails on a batch item)
    st.markdown("**Fallback image**")
    imgs = [f for f in os.listdir(AI_IMAGES) if f.lower().endswith((".png", ".jpg", ".jpeg"))] if os.path.isdir(AI_IMAGES) else []
    if imgs:
        fallback_image = os.path.join(AI_IMAGES, st.selectbox("Pick a render", imgs))
    else:
        fallback_image = st.file_uploader("Upload fallback", type=["png", "jpg", "jpeg"]).name

    st.divider()
    _hunt_clicked = st.button("🎯 HUNT FOR WINNING GAPS", use_container_width=True, type="primary")
    _run_clicked = st.button("RUN FULL EMPIRE SEQUENCE", use_container_width=True)

st.title("👻 HAVENWRIGHT INTELLIGENCE ENGINE")
st.caption("Trend-to-Video Intelligence // Deep State // 2049")


def _latest_mp4():
    if not os.path.isdir(FINAL_ADS):
        return None
    files = [f for f in os.listdir(FINAL_ADS) if f.endswith(".mp4")]
    if not files:
        return None
    return os.path.join(FINAL_ADS, max(files, key=lambda f: os.path.getmtime(os.path.join(FINAL_ADS, f))))


def _niche_pulse_from_status():
    if not os.path.exists(EMPIRE_STATUS):
        return None
    with open(EMPIRE_STATUS, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for i, ln in enumerate(lines):
        if "NICHE PULSE" in ln:
            for nxt in lines[i + 1:i + 4]:
                if nxt.strip() and not nxt.startswith("🧠"):
                    return nxt.strip()
    return None


def _save_upload(uploaded, ext):
    """Persist a Streamlit UploadedFile to ai_images/ (Streamlit temps are ephemeral)."""
    name = f"upload_{int(time.time())}{ext}"
    path = os.path.join(AI_IMAGES, name)
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    return path


def meta_ad_copy(gap):
    """High-CTR Meta ad copy (Headline + Primary Text) from a gap's pain + mood.

    Mood drives the hook register; the pain phrase is the 'you' it speaks to.
    Returns {'headline': str, 'primary': str}.
    """
    area = (gap.get("niche_area") or "your niche").strip().capitalize()
    pains = gap.get("top_pains") or {}
    pain = next(iter(pains), "")
    pain_clean = pain.strip().strip(",").strip() or area
    mood = (gap.get("mood") or "Hype").lower()

    # Hook line, register set by the hunted mood (default cyan/hype)
    hooks = {
        "anxiety": f"Still stuck on {pain_clean.lower()}? You're not failing — the tooling is.",
        "hype": f"Stop grinding {pain_clean.lower()} the slow way. There's a faster signal.",
        "urgency": f"{pain_clean}? The window on {area} is closing.",
    }
    hook = hooks.get(mood, hooks["hype"])

    primary = (
        f"{hook}\n\n"
        f"We hunt the real market gaps in {area} — high pain, low competition — and "
        f"turn them into done-for-you assets before your competitors even see the signal.\n\n"
        f"▚ High-CTR creative. Plug-and-Play for Meta & TikTok.\n"
        f"▚ No more guessing. Just the gap that prints.\n\n"
        f"→ Lock your gap now."
    )
    # Meta headline: tight, < 40 chars, curiosity + benefit
    headline = (f"{area}: {pain_clean}" if len(f"{area}: {pain_clean}") <= 40
                else f"The {area} gap that prints")[:40]
    return {"headline": headline, "primary": primary}


# ---------------------------------------------------------------------------
# THE HUNT — niche gap -> 3-Beat 2049 ad
# ---------------------------------------------------------------------------
def run_hunt(source, ai_prompt, raw_path, headline, n=3):
    """A/B hunt: scan for gaps, then render the top N gaps at once (3-Beat 2049 ads)."""
    results = {"mode": "hunt", "renders": [], "skipped": []}
    with st.status("▚ PREDATOR SEQUENCE — HUNTING", expanded=True) as status:
        # PHASE 1 — SCANNING FOR GAPS
        st.write("▚ **PHASE 1/3 — SCANNING FOR GAPS...**")
        import niche_hunter
        gaps = niche_hunter.top_gaps(niche_hunter.hunt_gaps())
        if not gaps:
            results["signal_lost"] = True
            status.update(label="✖ NO GAPS FOUND — WIDEN SUBREDDITS", state="complete")
            return results

        # PHASE 2 — LOCK N GAPS (the A/B set)
        top_gaps = gaps[:n]
        st.write(f"**PHASE 2/3 — LOCKING {len(top_gaps)} GAPS (A/B SET)...**")
        for i, g in enumerate(top_gaps, 1):
            st.write(f"  {i}. [{g['mood']}] pain={g['pain_volume']} comp={g['competition']} "
                     f"(score {g['gap_score']}) — {g['niche_area']}")

        # PHASE 3 — RENDER EACH GAP AS A 2049 ASSET
        st.write("**PHASE 3/3 — RENDERING 2049 ASSETS...**")
        from video_factory import build, generate_free_image
        brand_rgb = load_brand_rgb()
        use_real = source == "Use My Raw Footage" and raw_path
        for i, gap in enumerate(top_gaps, 1):
            mood = gap.get("mood") or "Hype"  # no mood -> default Cyan/Hype
            top_pain = next(iter(gap.get("top_pains", {})), headline)
            gap_headline = (top_pain or headline)[:40]
            gap_prompt = f"{gap['niche_area']} {top_pain} — B2B SaaS, futuristic 2049, holographic"
            st.write(f"▚ [{i}/{len(top_gaps)}] — {gap['niche_area']} / {mood}")
            image_path = video_path = None
            if use_real:
                video_path = raw_path
                st.write("  ✔ stabilizing + brand-grading raw footage")
            else:
                img_out = os.path.join(AI_IMAGES, f"gap_{i}_{int(time.time())}.png")
                try:
                    image_path = generate_free_image(gap_prompt, out_path=img_out)
                    st.write("  ✔ flux image ready")
                except Exception as e:
                    image_path = fallback_image if fallback_image else None
                    results["skipped"].append((gap["niche_area"], f"flux: {e}"))
                    st.warning(f"  ⚠ flux failed ({e}) — fallback image")
            t0 = time.time()
            out = build(image_path=image_path, video_path=video_path,
                        headline=gap_headline, mood=mood, duration=6.0, brand_rgb=brand_rgb,
                        use_bg=(video_path is None))
            st.write(f"  ✔ rendered in {time.time() - t0:.1f}s → {os.path.basename(out)}")
            results["renders"].append({
                "gap": gap, "video": out, "mood": mood, "image": image_path,
                "copy": meta_ad_copy(gap),
            })

        results["renders"][0]  # primary = first (highest gap score)
        status.update(label=f"✔ {len(results['renders'])} 2049 ASSETS RENDERED (A/B SET)", state="complete")
    return results


def load_brand_rgb():
    """Client brand color (RGB) from config brand_colors, or None."""
    cfg = json.load(open(os.path.join(TREND_ENGINE, "config.json"), encoding="utf-8")) if os.path.exists(os.path.join(TREND_ENGINE, "config.json")) else {}
    bc = cfg.get("brand_colors")
    if isinstance(bc, list) and len(bc) >= 3:
        return tuple(int(x) for x in bc[:3])
    return None


# ---------------------------------------------------------------------------
# THE RUN — scrape -> score -> batch
# ---------------------------------------------------------------------------
def run_full_sequence(n, fallback_image, fallback_headline):
    results = {"mode": "run", "renders": [], "hits": [], "skipped": []}
    with st.status("▚ HAVENWRIGHT — DEEP STATE SEQUENCE", expanded=True) as status:
        st.write("▚ **PHASE 1/3 — SCANNING GLOBAL INTEL...**")
        import scraper
        scraper.main()
        with open(RAW_TRENDS, encoding="utf-8") as f:
            raw = json.load(f)
        hits = raw.get("nicheHits", [])
        total = sum(raw.get("sourceCounts", {}).values())
        st.write(f"  ✔ {len(hits)} niche signals locked | {total} raw scanned")

        if not hits:
            results["signal_lost"] = True
            status.update(label="✖ SIGNAL LOST — NO NICHE HITS", state="complete")
            return results

        st.write(f"**PHASE 2/3 — LOCKING TOP {n} SIGNALS...**")
        top_n = sorted(hits, key=lambda t: t["relevance_score"], reverse=True)[:n]
        for i, t in enumerate(top_n, 1):
            st.write(f"  {i}. [{t['relevance_score']} pts] {t['title']}")

        st.write("**PHASE 3/3 — RENDERING HYPERREAL ASSETS...**")
        from video_factory import generate_free_image, build
        for i, t in enumerate(top_n, 1):
            title = t["title"].strip()
            headline_i = (fallback_headline or title)[:40]
            prompt = f"{title} — B2B SaaS, futuristic 2049, holographic"
            img_out = os.path.join(AI_IMAGES, f"concept_{i}_{int(time.time())}.png")
            try:
                image_path = generate_free_image(prompt, out_path=img_out)
                st.write(f"  ✔ [{i}/{n}] flux image")
            except Exception as e:
                image_path = fallback_image
                results["skipped"].append((title, f"flux: {e}"))
                st.warning(f"  ⚠ [{i}/{n}] flux failed ({e}) — fallback image")
            out = build(image_path=image_path, headline=headline_i, duration=6.0)
            st.write(f"  ✔ [{i}/{n}] rendered → {os.path.basename(out)}")
            results["renders"].append({"trend": t, "video": out, "image": image_path})

        results["hits"] = top_n
        results["pulse"] = _niche_pulse_from_status()
        status.update(label=f"✔ {len(results['renders'])} ASSETS RENDERED", state="complete")
    return results


def _copy_gap(copy, key="copy"):
    """'Copy Meta Ad Copy' button — writes Headline+Primary to the clipboard and
    shows the copy in an expandable box (so it's grabbable even if clipboard is blocked)."""
    if not copy:
        return
    blob = f"HEADLINE\n{copy.get('headline','')}\n\nPRIMARY TEXT\n{copy.get('primary','')}"
    if st.button("📋 Copy Meta Ad Copy", key=f"btn_{key}", use_container_width=True):
        try:
            import pyperclip
            pyperclip.copy(blob)
            st.success("Copied to clipboard.")
        except Exception:
            st.info("Copy shown below (clipboard unavailable) — select + copy manually.")
        st.session_state[f"show_{key}"] = True
    if st.session_state.get(f"show_{key}"):
        st.code(blob, language="text")


# ---------------------------------------------------------------------------
# Client view — gap insight / trend insight, video, download
# ---------------------------------------------------------------------------
def render_client_view(last_run):
    if not last_run:
        st.info("No render yet. Hit **🎯 HUNT FOR WINNING GAPS** or **RUN FULL EMPIRE SEQUENCE**.")
        return

    if last_run.get("signal_lost"):
        st.markdown(
            """
            <div style="background:#0a0512;border:2px solid #ff2d55;border-radius:8px;padding:2rem;
                        text-align:center;font-family:consolas, monospace;box-shadow:0 0 32px #ff2d5588;">
              <div style="color:#ff2d55;font-size:3rem;font-weight:bold;letter-spacing:8px;">▚ SIGNAL LOST ▚</div>
              <div style="color:#7affc8;margin-top:0.6rem;">The grid is noise. Recalibrate and re-run.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if last_run.get("mode") == "hunt":
        renders = last_run.get("renders", [])
        if not renders:
            st.info("No assets rendered this hunt.")
            return
        # A/B grid: each gap -> video + gap insight + Meta copy + download
        cols = st.columns(min(len(renders), 3))
        for i, r in enumerate(renders):
            with cols[i % len(cols)]:
                gap = r.get("gap", {})
                mood = r.get("mood", "Hype")
                video = r.get("video")
                st.video(video) if video and os.path.exists(video) else st.caption("(no video)")
                st.markdown(
                    f"""
                    <div style="background:#0a1220;border:1px solid #00c8ff44;border-radius:8px;
                                padding:0.9rem 1rem;font-family:consolas, monospace;margin-top:0.5rem;">
                      <div style="color:#00c8ff;letter-spacing:1px;font-weight:bold;">
                        🎯 GAP #{i+1} — {mood.upper()}</div>
                      <div style="color:#d8f4ff;font-size:0.95rem;margin:0.3rem 0;">
                        Pain {gap.get('pain_volume','?')} · Comp {gap.get('competition','?')} ·
                        Score {gap.get('gap_score','?')}</div>
                      <div style="color:#7affc8;">High pain, low competition in {gap.get('niche_area','the niche')}.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                _copy_gap(r.get("copy"), key=f"copy_{i}")
                if video and os.path.exists(video):
                    with open(video, "rb") as f:
                        st.download_button(f"⬇ ASSET #{i+1}", data=f.read(),
                                           file_name=os.path.basename(video), mime="video/mp4",
                                           key=f"dl_h_{i}", use_container_width=True)
        return

    # run mode
    renders = last_run.get("renders", [])
    video = renders[0]["video"] if renders else _latest_mp4()
    if video and os.path.exists(video):
        st.video(video)
        if renders:
            t = renders[0]["trend"]
            st.markdown(
                f"""
                <div style="background:#0a1220;border:1px solid #00c8ff44;border-radius:8px;
                            padding:1.2rem 1.6rem;font-family:consolas, monospace;margin-top:0.8rem;">
                  <div style="color:#00c8ff;letter-spacing:2px;font-weight:bold;">🎯 TREND INSIGHT</div>
                  <div style="color:#d8f4ff;font-size:1.15rem;margin:0.5rem 0;">“{t['title']}”</div>
                  <div style="color:#7affc8;">Why we picked this: {last_run.get('pulse') or 'Top signal by relevance score.'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with open(video, "rb") as f:
            st.download_button("⬇ DOWNLOAD ASSET", data=f.read(),
                               file_name=os.path.basename(video), mime="video/mp4",
                               use_container_width=True)


# ---------------------------------------------------------------------------
# Engineer view — full grid + EMPIRE_STATUS dump
# ---------------------------------------------------------------------------
def render_engineer_view(last_run):
    if not last_run:
        mp4 = _latest_mp4()
        st.video(mp4) if mp4 else st.info("No renders yet. Hit **RUN** or **HUNT**.")
    elif last_run.get("mode") == "hunt":
        if last_run.get("video"):
            st.video(last_run["video"])
    else:
        renders = last_run.get("renders", [])
        if renders:
            cols = st.columns(min(len(renders), 3))
            for i, r in enumerate(renders):
                with cols[i % len(cols)]:
                    t = r["trend"]
                    st.video(r["video"])
                    st.caption(f"[{t['relevance_score']} pts] {t['title'][:60]}")
                    with open(r["video"], "rb") as f:
                        st.download_button(f"⬇ {os.path.basename(r['video'])}", data=f.read(),
                                           file_name=os.path.basename(r["video"]), mime="video/mp4", key=f"dl_{i}")
        else:
            mp4 = _latest_mp4()
            st.video(mp4) if mp4 else st.info("No renders.")

    st.subheader("📊 EMPIRE STATUS")
    if os.path.exists(EMPIRE_STATUS):
        with open(EMPIRE_STATUS, encoding="utf-8") as f:
            st.code(f.read(), language="text")
    else:
        st.info("No EMPIRE_STATUS.txt yet — run the sequence.")


# ---------------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------------
raw_path = None
if source == "Use My Raw Footage" and raw_upload is not None:
    raw_path = _save_upload(raw_upload, ".mp4")

if _hunt_clicked:
    try:
        st.session_state.last_run = run_hunt(source, ai_prompt, raw_path, headline, n=batch_n)
    except Exception as e:
        st.session_state.last_run = {"mode": "hunt", "error": str(e)}
elif _run_clicked:
    try:
        st.session_state.last_run = run_full_sequence(batch_n, fallback_image, headline)
    except Exception as e:
        st.session_state.last_run = {"mode": "run", "error": str(e)}

last = st.session_state.get("last_run")
if last and last.get("error"):
    st.error(f"SEQUENCE FAILED: {last['error']}")

if client_view:
    render_client_view(last)
else:
    render_engineer_view(last)

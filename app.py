import streamlit as st
import subprocess
import json
import os
import sys

st.set_page_config(page_title="EMPIRE ENGINE", page_icon="🚀", layout="wide")
st.title("🚀 EMPIRE ENGINE: Full Automation Suite")
st.markdown("---")

st.sidebar.header("⚙️ Control Center")
st.sidebar.markdown("**Select Niche:**")
st.sidebar.selectbox("Niche", ["B2B SaaS", "Real Estate", "E-Commerce"])
auto_voice = st.sidebar.checkbox("🎙️ Generate Voiceover", value=True)
auto_analyze = st.sidebar.checkbox("🧠 Run Claude Analysis", value=True)

if st.button("🚀 RUN FULL EMPIRE SEQUENCE", use_container_width=True, type="primary"):
    st.session_state.running = True

if st.session_state.get("running"):
    log_box = st.empty()
    
    def log(msg):
        log_box.write(msg)
        st.spinner("Processing...")

    try:
        log("🛰️ **PHASE 1: SCRAPING GLOBAL TRENDS**")
        log("-----------------------------------")
        p1 = subprocess.run([sys.executable, "scraper.py"], capture_output=True, text=True)
        for line in p1.stdout.split('\n'):
            if line.strip(): log(line)
        if p1.returncode != 0:
            log(f"❌ Scraper Error: {p1.stderr}")
            st.session_state.running = False
            st.stop()
        log("✅ Phase 1 Complete.")
        log("")

        if auto_analyze:
            log("🧠 **PHASE 2: CLAUDE AI ANALYSIS**")
            log("-----------------------------------")
            prompt = "Read data/raw_trends.json and EMPIRE_STATUS.txt. Generate 3 winning ad concepts for the niche. Save to output/ad_concepts.json. Be concise."
            # Note: This runs Claude in non-interactive mode if supported, or just triggers it.
            # For a local terminal, this might just show the prompt for you to paste, 
            # OR we can use a specific CLI flag if you have one.
            log("📝 Prompt generated. (In a full API setup, this would call the model directly).")
            log("✅ Phase 2 Complete.")
            log("")


        if auto_voice:
            log("🎙️ **PHASE 3: VOICEOVER GENERATION**")
            log("-----------------------------------")
            if os.path.exists("output/ad_concepts.json"):
                with open("output/ad_concepts.json") as f:
                    concepts = json.load(f)
                for i, c in enumerate(concepts[:1]):
                    hook = c.get("hook", "Empire Engine")
                    log(f"🎤 Generating voice for: {hook[:30]}...")
                    subprocess.run(f'edge-tts --text "{hook}" --write-media output/vo_0.mp3', shell=True)
                log("✅ Phase 3 Complete.")
            else:
                log("⚠️ No concepts found to voice.")
                
        log("")
        log("🏆 **SEQUENCE COMPLETE**")
        st.session_state.running = False
        st.session_state.finished = True

    except Exception as e:
        log(f"❌ Critical Error: {e}")
        st.session_state.running = False

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📡 Live Intelligence Feed")
    if "finished" in st.session_state and st.session_state.finished:
        if os.path.exists("output/ad_concepts.json"):
            with open("output/ad_concepts.json") as f:
                concepts = json.load(f)
            for i, c in enumerate(concepts):
                with st.expander(f"🏆 Concept {i+1}: {c.get('title', 'Untitled')}"):
                    st.markdown(f"**Hook:** {c.get('hook')}")
                    st.markdown(f"**Angle:** {c.get('angle')}")
                    st.markdown(f"**Visual:** {c.get('visual')}")
                    if auto_voice and os.path.exists("output/vo_0.mp3") and i == 0:
                        st.audio("output/vo_0.mp3")
        else:
            st.success("✅ Data scraped. Run Claude Analysis to see concepts.")
    else:
        st.info("Click 'RUN FULL EMPIRE SEQUENCE' to start.")

with col2:
    st.subheader("📈 Niche Pulse")
    if os.path.exists("EMPIRE_STATUS.txt"):
        with open("EMPIRE_STATUS.txt", encoding="utf-8") as f:
    st.code(f.read(), language="markdown")
    else:
        st.info("Run the engine to generate status.")
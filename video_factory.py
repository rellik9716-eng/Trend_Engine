"""2049 agency video factory — VERTICAL (1080x1920)."""
import os
import string
import sys
import time
import json
from random import Random

import numpy as np
import requests
from PIL import Image, ImageFilter
from moviepy import (
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoClip,
    vfx,
)

from glitch import apply_glitch
from kinetic_bg import make_kinetic_bg

# Vertical 9:16 — TikTok/Reels/Shorts
W, H = 1080, 1920
FONT = "consola"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "final_ads")

def hyperreal_prompt(inject_text):
    """Wraps a simple idea in a 'Higsfield' grade cinematic prompt."""
    # The "2049" Aesthetic Injection
    style_suffix = (
        "hyperrealistic, 8k resolution, shot on ARRI ALEXA 65, 85mm lens, "
        "cinematic lighting, volumetric fog, neon cyan and deep purple accents, "
        "sharp focus, highly detailed textures, futuristic B2B SaaS aesthetic, "
        "minimalist, generational tech, unreal engine 5 render, award-winning photography"
    )
    return f"{inject_text}, {style_suffix}"

def generate_free_image(prompt, save_path="ai_images/auto_render.png"):
    """Generates a 'Higsfield' grade vertical image using the free Pollinations Flux API with Retry Logic."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 1. Inject the "Cinematic" direction
    full_prompt = hyperreal_prompt(prompt)
    
    # 2. The "Cracked" Free URL (Forcing Flux + Enhancement)
    url = (
        f"https://image.pollinations.ai/prompt/{full_prompt}"
        f"?width=1080&height=1920&model=flux&nologo=true&enhance=true&safe=true"
    )
    
    print(f"🎬 [HYPERREAL-STACK] Rendering 8k Cinematic Asset...")
    
    # 3. The "Retry Engine" (Handles 503 errors)
    for attempt in range(1, 4):
        try:
            print(f"   -> Attempt {attempt}/3...")
            response = requests.get(url, timeout=120)
            
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                print("   ✅ HYPERREAL ASSET READY.")
                return save_path
            elif response.status_code == 503:
                print("   ⚠️ Server busy (503). Waiting 5s and retrying...")
                time.sleep(5)
            else:
                raise Exception(f"Hyperreal render failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Network glitch: {e}. Retrying...")
            time.sleep(5)
            
    raise Exception("Failed to render after 3 attempts. The free 'Cloud' is likely crowded.")

# Vertical 9:16 — TikTok/Reels/Shorts
W, H = 1080, 1920
FONT = "consola"  # present on Windows; falls back silently in moviepy if not
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "final_ads")


def load_config():
    """Load config.json from the adjacent trend-engine dir."""
    import json
    p = os.path.join(os.path.dirname(__file__), "..", "trend-engine", "config.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def hologramize(image_path, scale=0.9):
    """AI image with feathered (Gaussian-blurred) alpha edges so it reads as a hologram."""
    img = Image.open(image_path).convert("RGBA")
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)

    # faint cyan hologram tint
    tint = Image.new("RGBA", img.size, (0, 170, 255, 40))
    img = Image.alpha_composite(img, tint)

    # feather the alpha mask: blur a copy, use its luminance as the new alpha
    mask = img.convert("L").filter(ImageFilter.GaussianBlur(28))
    img.putalpha(mask)
    return np.array(img)


def hud_overlay(duration):
    """Top layer: breathing pulse, corner HUD text, niche readout from config."""
    cfg = load_config()
    kws = ", ".join(cfg.get("niche_keywords", [])[:4]) or "AI AUTOMATION"

    # ponytail: ColorClip can't take a time-varying opacity lambda; bake the pulse into the frame.
    def pulse_frame(t):
        f = np.full((H, W, 3), (0, 170, 255), dtype=np.uint8)
        return (f * (0.05 + 0.05 * abs(np.sin(t * 1.5)))).astype(np.uint8)

    pulse = VideoClip(pulse_frame, duration=duration)

    bracket = TextClip(
        text="▚ DEEP STATE FEED // 2049 ◤",
        font=FONT, font_size=40, color=(0, 200, 255),
        method="caption", size=(W, None), text_align="left",
    ).with_position((40, 40)).with_duration(duration)

    readout = TextClip(
        text=f"NICHE VECTOR: {kws.upper()}\nSIGNAL LOCK: ACTIVE  |  GRID: LIVE",
        font=FONT, font_size=28, color=(120, 255, 200),
        method="caption", size=(W, None), text_align="right",
    ).with_position(("right", "bottom")).with_duration(duration)

    return [pulse, bracket, readout]


def decode_text(text, duration):
    """Center headline that 'decodes': scrambled chars settle in over 1.2s."""
    CHARS = string.ascii_uppercase + "█▓▒░#$%&"

    def frame_func(t):
        settled = min(1.0, t / 1.2)
        rng = Random(int(t * 8))
        chars = []
        for i, c in enumerate(text):
            if c == " " or settled >= i / max(1, len(text)):
                chars.append(c)
            else:
                chars.append(rng.choice(CHARS))
        clip = TextClip(
            text="".join(chars), font=FONT, font_size=56, color="white",
            method="caption", size=(W, None), text_align="center",
        )
        return clip.get_frame(0)

    return VideoClip(frame_func, duration=duration).with_position("center")

    
def build(image_path, out_path=None, headline="THE SIGNAL IS LIVE", duration=12.0):
    """Render the full stack to a vertical MP4. Returns the output path."""
    if out_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, f"ad_{int(duration)}s_{os.path.basename(image_path)}.mp4")
    else:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    bg = make_kinetic_bg(W, H, duration)

    holo = ImageClip(hologramize(image_path)).with_duration(duration).with_position(("center", 0.38 * H))
    holo = holo.with_effects([vfx.CrossFadeIn(0.5)])

    headline_clip = decode_text(headline, duration).with_start(1.0)

    final = CompositeVideoClip(
        [bg, holo] + hud_overlay(duration) + [headline_clip],
        size=(W, H),
        use_bgclip=True,
    ).with_duration(duration)

    final = apply_glitch(final)
    final.write_videofile(out_path, fps=24, codec="libx264", audio=False)
    return out_path


if __name__ == "__main__":
    if "--prompt" in sys.argv:
        # NEW "FREE-STACK" WAY: python video_factory.py --prompt "Your Idea" "Headline"
        idx = sys.argv.index("--prompt")
        prompt = sys.argv[idx + 1]
        headline = sys.argv[idx + 2] if len(sys.argv) > idx + 2 else "THE SIGNAL IS LIVE"
        image = generate_free_image(prompt)
        out = sys.argv[idx + 3] if len(sys.argv) > idx + 3 and sys.argv[idx + 3].endswith(".mp4") else None
    elif len(sys.argv) > 1:
        # Old way: python video_factory.py image.png "Headline"
        image = sys.argv[1]
        headline = sys.argv[2] if len(sys.argv) > 2 else "THE SIGNAL IS LIVE"
        out = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3].endswith(".mp4") else None
    else:
        print("Usage: python video_factory.py image_path [headline]")
        print("       OR: python video_factory.py --prompt 'Your AI Idea' 'Headline'")
        sys.exit(1)
        
    print(build(image, out, headline))

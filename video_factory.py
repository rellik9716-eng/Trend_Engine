"""2049 agency video factory — VERTICAL (1080x1920).

THE 3-BEAT:
  0-1s  Pattern interrupt (glitch)
  1-3s  Base (stabilized real footage OR SVD-animated hyperreal image)
  3-5s  Decode headline in the client's brand font, over the 2049 HUD.

Stack: kinetic grid (bottom) -> base layer (mid) -> HUD + brand logo (top) ->
decode headline -> glitch on the first second only.
Usage:  python video_factory.py image_path [headline] [--mood Hype]
        or:  from video_factory import build
"""
import os
import string
import sys
from random import Random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from moviepy import (
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoClip,
    vfx,
)

from glitch import apply_glitch
from kinetic_bg import make_kinetic_bg
from video_editor import brand_grade, safe_box, safe_pad

# Vertical 9:16 — TikTok/Reels/Shorts
W, H = 1080, 1920
FONT = "consola"  # default; brand_font from config overrides
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "final_ads")
LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

MOOD_COLOR = {"Anxiety": (255, 60, 120), "Hype": (0, 200, 255), "Urgency": (255, 170, 0)}


def load_config():
    """Load config.json from the adjacent trend-engine dir."""
    import json
    p = os.path.join(os.path.dirname(__file__), "..", "trend-engine", "config.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def brand_font():
    """Client brand font (config brand_font) with a safe default fallback."""
    return load_config().get("brand_font", FONT)


def mood_color(mood):
    return MOOD_COLOR.get(mood, MOOD_COLOR["Hype"])


# ---------------------------------------------------------------------------
# Hyperreal image generation (free stack)
# ---------------------------------------------------------------------------
def hyperreal_prompt(prompt):
    """Cinematic directives: ARRI ALEXA 65, 8K, shallow DOF, filmic grade."""
    return (
        f"{prompt}. Shot on ARRI ALEXA 65, 8K resolution, photorealistic, "
        f"cinematic color grade, shallow depth of field, volumetric lighting, "
        f"ultra-detailed, hyperrealistic."
    )


def generate_free_image(prompt, out_path=None, out_dir=None):
    """Free-stack image gen (Pollinations flux + enhance). Saves to ai_images/, returns path."""
    import hashlib
    import requests
    import urllib.parse

    if out_path is None:
        if out_dir is None:
            out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_images")
        os.makedirs(out_dir, exist_ok=True)
        digest = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:10]
        out_path = os.path.join(out_dir, f"ai_{digest}.png")
    else:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    url = (
        "https://image.pollinations.ai/prompt/"
        f"{urllib.parse.quote(hyperreal_prompt(prompt))}"
        "?model=flux&enhance=true&width=1080&height=1920&nologo=true"
    )
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path


# ---------------------------------------------------------------------------
# Base-layer builders
# ---------------------------------------------------------------------------
def _crop_to(w, h, frame):
    """Center-crop/fit an (H,W,3) frame into exactly (w,h)."""
    fh, fw = frame.shape[:2]
    scale = max(w / fw, h / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    img = Image.fromarray(frame).resize((nw, nh), Image.LANCZOS)
    x0 = (nw - w) // 2
    y0 = (nh - h) // 2
    return np.array(img.crop((x0, y0, x0 + w, y0 + h)))


def hologramize(image_path, scale=0.9):
    """AI image with feathered alpha edges so it reads as a hologram."""
    img = Image.open(image_path).convert("RGBA")
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    tint = Image.new("RGBA", img.size, (0, 170, 255, 40))
    img = Image.alpha_composite(img, tint)
    mask = img.convert("L").filter(ImageFilter.GaussianBlur(28))
    img.putalpha(mask)
    return np.array(img)


def svd_camera_push(clip_or_image, duration=2.0, push=0.12, fps=24, pad_frac=0.10):
    """Cinematic slow push-in.

    If diffusers (Stable Video Diffusion) is available it animates a static image;
    otherwise a deterministic numpy zoom (1.0 -> 1+push) is applied — same feel,
    no heavy model. `pad_frac` letterboxes the base for the safe 1:1 crop.
    Returns a moviepy VideoClip at (W,H).
    """
    from moviepy import VideoClip

    def numpy_push(t):
        zoom = 1.0 + push * (t / max(0.1, duration))
        base = _base_frame(clip_or_image, t)
        return _pad_sides(_zoom(base, zoom), pad_frac)

    # SVD path: only for static images and only if the lib is present.
    if isinstance(clip_or_image, str):
        try:
            from diffusers import StableVideoDiffusionPipeline
            import torch
            print("  [svd] using Stable Video Diffusion camera push (slow first run)")
            pipe = StableVideoDiffusionPipeline.from_pretrained(
                "stabilityai/stable-video-diffusion-img2vid-xt",
                torch_dtype=torch.float16,
            ).to("cuda")
            image = Image.open(clip_or_image).resize((W, H))
            video = pipe(image, num_frames=16, motion_bucket_id=127).frames[0]
            arr = np.stack([np.array(f) for f in video])
            def svd_frame(t):
                idx = min(int(t / duration * len(arr)), len(arr) - 1)
                return _crop_to(W, H, _zoom(arr[idx], 1.0 + push * (t / duration)))
            return VideoClip(svd_frame, duration=duration).with_fps(fps)
        except Exception as e:
            print(f"  [svd] falling back to numpy push ({e})")

    def _base_frame(src, t):
        if isinstance(src, str):
            return _crop_to(W, H, np.array(Image.open(src).convert("RGB")))
        # a moviepy clip
        f = src.get_frame(min(t, max(0.0, src.duration - 0.01)))
        return _crop_to(W, H, f)

    return VideoClip(numpy_push, duration=duration).with_fps(fps)


def _pad_sides(frame, pad_frac):
    """'Safe export': letterbox the base with `pad_frac` void on each side so the
    subject sits inside the center 720px — survives a 1:1 feed crop on 1080-wide.
    The frame may be wider than the canvas (svd_camera_push pre-scales it), so
    the center crop is extracted from the frame, not assumed to equal it."""
    h, fw = frame.shape[:2]
    px = int(W * pad_frac)
    if px <= 0:
        return frame
    canvas = np.full((h, W, 3), (6, 10, 18), dtype=np.uint8)  # 2049 void
    mid_w = W - 2 * px
    x0 = (fw - mid_w) // 2
    canvas[:, px: W - px] = frame[:, x0: x0 + mid_w]
    return canvas


def _zoom(frame, z):
    """Scale a (H,W,3) frame about its center by z (z>=1 zooms in)."""
    h, w = frame.shape[:2]
    if z <= 1.001:
        return frame
    img = Image.fromarray(frame)
    nw, nh = int(w / z), int(h / z)
    img = img.resize((nw, nh), Image.LANCZOS)
    x0 = (w - nw) // 2
    y0 = (h - nh) // 2
    canvas = Image.new("RGB", (w, h), (6, 10, 18))
    canvas.paste(img, (x0, y0))
    return np.array(canvas)


def make_base_clip(image_path=None, video_path=None, brand_rgb=None,
                   duration=2.0, out_fps=24):
    """Build the 1-3s base layer.

    video_path  -> stabilized + brand-graded real footage, with a camera push
                   on its tail (from video_editor.prepare_base).
    image_path  -> hyperreal image with an SVD/numpy camera push.
    Returns a moviepy VideoClip at (W,H), duration=duration.
    """
    if video_path:
        from video_editor import prepare_base
        clip, _meta = prepare_base(video_path, brand_rgb=brand_rgb)
        base = _fit(clip, W, H, duration)
        # camera push over the last `duration` seconds of the base
        tail = base.with_effects([])
        return svd_camera_push(clip, duration=duration)
    if image_path:
        return svd_camera_push(image_path, duration=duration)
    # nothing supplied: kinetic grid holds the slot
    return make_kinetic_bg(W, H, duration)


def _fit(clip, w, h, duration):
    """Scale/crop a clip to (w,h) and trim/loop to duration."""
    size = clip.size
    scale = max(w / size[0], h / size[1])
    clip = clip.resized(scale)
    clip = clip.cropped(x_center=clip.w / 2, y_center=clip.h / 2, width=w, height=h)
    if clip.duration < duration:
        from moviepy import concatenate_videoclips
        clip = clip.clipped(0, clip.duration)
        reps = int(np.ceil(duration / max(0.1, clip.duration)))
        clip = concatenate_videoclips([clip] * reps)
    return clip.with_duration(duration)


# ---------------------------------------------------------------------------
# 2049 HUD — the star
# ---------------------------------------------------------------------------
def hud_overlay(duration, mood="Hype"):
    """Top layer: breathing pulse, command brackets, niche readout, mood-tinted."""
    cfg = load_config()
    kws = ", ".join(cfg.get("niche_keywords", [])[:4]) or "AI AUTOMATION"
    mc = mood_color(mood)
    x0, y0, x1, y1 = safe_box(W, H)

    def pulse_frame(t):
        f = np.full((H, W, 3), np.array(mc, dtype=np.uint8))
        return (f * (0.05 + 0.05 * abs(np.sin(t * 1.5)))).astype(np.uint8)

    pulse = VideoClip(pulse_frame, duration=duration)

    bracket = TextClip(
        text="▚ HAVENWRIGHT INTEL // 2049 ◤",
        font=brand_font(), font_size=40, color=mc,
        method="caption", size=(x1 - x0, None), text_align="left",
    ).with_position((x0 + 16, y0 + 16)).with_duration(duration)

    readout = TextClip(
        text=f"NICHE VECTOR: {kws.upper()}\nSIGNAL LOCK: ACTIVE  |  GRID: LIVE",
        font=brand_font(), font_size=26, color=(120, 255, 200),
        method="caption", size=(x1 - x0 - 32, None), text_align="right",
    ).with_position((x1 - (x1 - x0) + 16, y1 - 130)).with_duration(duration)

    # corner ticks (the 'command center' frame)
    tick = "└"
    ticks = []
    for (px, py, ch) in [(x0, y0, "┌"), (x1, y0, "┐"), (x0, y1, "└"), (x1, y1, "┘")]:
        ticks.append(TextClip(
            text=ch, font=brand_font(), font_size=64, color=mc,
        ).with_position((px - 32 if px == x1 else px, py - 32 if py == y1 else py)).with_duration(duration))
    return [pulse, bracket, readout] + ticks


def brand_logo(duration, mood="Hype"):
    """Client logo in the corner with a neon glow matching the Mood.

    Uses assets/<brand_logo> (config brand_logo) if present; else a glowing
    monogram so a phone video still reads as a branded command center.
    """
    cfg = load_config()
    mc = mood_color(mood)
    x0, y0, x1, _y1 = safe_box(W, H)
    logo_name = cfg.get("brand_logo")
    path = os.path.join(LOGO_DIR, logo_name) if logo_name else None

    if path and os.path.exists(path):
        arr = np.array(Image.open(path).convert("RGBA"))
        arr = _resize_logo(arr, max_w=200)
        # neon glow: blurred copy tinted to mood behind the logo
        glow = np.zeros_like(arr)
        g = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(12))
        glow = np.array(g)
        glow[:, :, 0:3] = np.maximum(glow[:, :, 0:3], np.array(mc, dtype=np.uint8) * (glow[:, :, 3:4] / 255))
        frame = np.full((arr.shape[0] + 8, arr.shape[1] + 8, 4), 0, dtype=np.uint8)
        frame[4:-4, 4:-4] = np.maximum(glow, arr)
        img = ImageClip(frame).with_duration(duration)
        return img.with_position((x0 + 16, y0 + 70))

    # monogram fallback — glowing brand initial
    brand = cfg.get("brand_name", "HAVENWRIGHT")
    letter = brand[:1].upper()
    txt = TextClip(
        text=letter, font=brand_font(), font_size=90, color=mc,
    ).with_duration(duration)
    return txt.with_position((x0 + 24, y0 + 84))


def _resize_logo(arr, max_w=200):
    img = Image.fromarray(arr)
    if img.width > max_w:
        r = max_w / img.width
        img = img.resize((max_w, int(img.height * r)), Image.LANCZOS)
    return np.array(img)


def decode_text(text, duration, color=(255, 255, 255)):
    """Center headline that 'decodes': scrambled chars settle in over 1.2s."""
    CHARS = string.ascii_uppercase + "█▓▒░#$%&"
    _x0, y0, _x1, _y1 = safe_box(W, H)

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
            text="".join(chars), font=brand_font(), font_size=56, color=color,
            method="caption", size=(W, None), text_align="center",
        )
        return clip.get_frame(0)

    return VideoClip(frame_func, duration=duration).with_position(("center", int(y0 + (0.30 * H))))


def _decode_line(t, text, font_size, color, CHARS):
    """One scrambled->settled line at time t (0-1 settles over 0.9s)."""
    settled = min(1.0, t / 0.9)
    rng = Random(int(t * 8))
    out = []
    for i, c in enumerate(text):
        if c == " " or settled >= i / max(1, len(text)):
            out.append(c)
        else:
            out.append(rng.choice(CHARS))
    return TextClip(
        text="".join(out), font=brand_font(), font_size=font_size, color=color,
        method="caption", size=(W, None), text_align="center",
    )


def _logo_frame(t, duration, mc, brand, url, logo_img):
    """Decoded brand wordmark + client URL card. Fades in over the last second
    of the video and holds at full opacity through the final frames."""
    CHARS = string.ascii_uppercase + "█▓▒░#$%&"
    _x0, _y0, x1, y1 = safe_box(W, H)
    fade = min(1.0, max(0.0, (t / duration - 0.8) / 0.2))  # 0->1 over last 20%
    frame = np.zeros((H, W, 4), dtype=np.uint8)
    if fade <= 0:
        return frame

    card = Image.new("RGBA", (int(x1 * 0.9), 300), (6, 10, 18, int(235 * fade)))
    dr = ImageDraw.Draw(card)
    dr.rectangle([0, 0, card.width - 1, card.height - 1], outline=tuple(mc) + (int(255 * fade),))

    if logo_img is not None:
        card.paste(logo_img, ((card.width - logo_img.width) // 2, 20), logo_img)
    else:
        txt = _decode_line(t, brand, 44, tuple(mc), CHARS)
        txt_img = Image.fromarray(txt.get_frame(0)).convert("RGBA")
        card.paste(txt_img, ((card.width - txt_img.width) // 2, 30), txt_img)

    url_txt = _decode_line(t, url, 26, (120, 255, 200), CHARS)
    url_arr = np.array(Image.fromarray(url_txt.get_frame(0)).convert("RGBA"))
    url_arr[:, :, 3] = (url_arr[:, :, 3].astype(np.float32) * fade).astype(np.uint8)
    card.paste(Image.fromarray(url_arr), ((card.width - url_arr.shape[1]) // 2, 190),
               Image.fromarray(url_arr))

    # Composite onto the 2049 void with per-pixel alpha (no full-canvas mask
    # clip — that recurses through moviepy's convert_masks_to_RGB).
    card_rgba = np.array(card)
    y0 = int(y1 - 300 - 20)
    x0c = (W - card.width) // 2
    if y0 >= 0 and y0 + card.height <= H and x0c >= 0:
        a = card_rgba[:, :, 3:4].astype(np.float32) / 255.0
        region = frame[y0:y0 + card.height, x0c:x0c + card.width]
        frame[y0:y0 + card.height, x0c:x0c + card.width] = (
            card_rgba[:, :, :3] * a + region * (1.0 - a)
        ).astype(np.uint8)
    return frame


def _decode_alpha(img, t, CHARS, n_glitch=6):
    """'Decode' an RGBA logo: swap random pixel rows for scramble noise while
    settling (t < 1.0); returns the original image once settled."""
    if t >= 1.0:
        return img
    rng = np.random.default_rng(int(t * 20))
    arr = np.array(img).copy()
    h, w = arr.shape[:2]
    for _ in range(n_glitch):
        y = int(rng.integers(0, max(1, h - 4)))
        band = arr[y:y + 4]
        noise = rng.integers(0, 255, band.shape, dtype=np.uint8)
        alpha = band[:, :, 3]
        noise[:, :, 3] = alpha  # keep the logo's silhouette while scrambling RGB
        arr[y:y + 4] = np.where(alpha[:, :, None] > 0, noise, band)
    return Image.fromarray(arr)


def _signature_end_card(duration, mc):
    """The 'Fame' signature end: decoded brand logo + client CTA URL.

    Runs the final 1.5s of the video; the card itself fades in over the last
    second and holds. `mc` is the mood color; brand/url/logo come from config.
    """
    cfg = load_config()
    brand = cfg.get("brand_name", "HAVENWRIGHT")
    url = (cfg.get("cta_url") or cfg.get("brand_url") or "LINK IN BIO").upper()
    logo_name = cfg.get("brand_logo")
    logo_path = os.path.join(LOGO_DIR, logo_name) if logo_name else None
    logo_img = None
    if logo_path and os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert("RGBA")
        if logo_img.width > 220:
            r = 220 / logo_img.width
            logo_img = logo_img.resize((220, int(logo_img.height * r)), Image.LANCZOS)
    return VideoClip(lambda t: _logo_frame(t, 1.0, mc, brand, url, logo_img),
                     duration=min(1.5, duration)).with_start(max(0.0, duration - 1.5))


# ---------------------------------------------------------------------------
# THE 3-BEAT build
# ---------------------------------------------------------------------------
def build(image_path=None, video_path=None, out_path=None, headline="THE SIGNAL IS LIVE",
          mood="Hype", duration=6.0, brand_rgb=None, use_bg=True):
    """Render the full 3-Beat stack to a vertical MP4. Returns the output path.

    0-1s pattern interrupt (glitch) | 1-3s base | 3-5s decode headline.
    Base = video_path (real, stabilized/graded) or image_path (hyperreal+SVD).
    """
    base_dur = min(2.0, max(1.0, duration - 1.0))
    if out_path is None:
        src = os.path.basename(video_path or image_path or "base")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, f"ad_{int(duration)}s_{src}.mp4")
    else:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    layers = []
    if use_bg:
        layers.append(make_kinetic_bg(W, H, duration))

    base = make_base_clip(image_path=image_path, video_path=video_path,
                          brand_rgb=brand_rgb, duration=base_dur)
    base = base.with_start(1.0)
    layers.append(base)

    layers += hud_overlay(duration, mood=mood)
    layers.append(brand_logo(duration, mood=mood))

    # 3-Beat decode: headline (the "Gap") + client CTA URL on the decode line
    cta = (load_config().get("cta_url") or "").strip()
    headline_line = headline[:40] + (f"\n→ {cta}" if cta else "")
    headline_clip = decode_text(headline_line, duration=duration - 3.0).with_start(3.0)
    layers.append(headline_clip)

    # 'Fame' signature end: decoded logo + client URL over the last 1s
    layers.append(_signature_end_card(duration, mood_color(mood)))

    final = CompositeVideoClip(layers, size=(W, H), use_bgclip=True).with_duration(duration)

    # Pattern interrupt: glitch only on the first second
    def interrupt(t):
        img = final.get_frame(t)
        if t < 1.0:
            rng = np.random.default_rng(int(t * 1000))
            h = img.shape[0]
            for _ in range(rng.integers(4, 7)):
                y0 = int(rng.integers(0, h - 20))
                band_h = int(rng.integers(6, 40))
                shift = int(rng.integers(-70, 71))
                band = img[y0:y0 + band_h]
                img[y0:y0 + band_h] = np.roll(band, shift, axis=1)
                img[y0:y0 + band_h, :, 0] = np.roll(band[:, :, 0], shift // 2, axis=1)
                img[y0:y0 + band_h, :, 2] = np.roll(band[:, :, 2], -shift // 2, axis=1)
            a, b = (int(x) for x in rng.integers(0, h, 2))
            img[a], img[b] = img[b], img[a]
            img[int(rng.integers(0, h))] = 255
        return img

    final = VideoClip(interrupt, duration=duration).with_fps(24)
    final.write_videofile(out_path, fps=24, codec="libx264", audio=False)
    return out_path


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", help="Path to an AI image (or use --prompt)")
    ap.add_argument("--video", help="Path to real client footage (stabilized+graded)")
    ap.add_argument("--prompt", help="Generate the base image from this prompt (flux)")
    ap.add_argument("--headline", default="THE SIGNAL IS LIVE")
    ap.add_argument("--mood", default="Hype", choices=["Anxiety", "Hype", "Urgency"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    image = args.image or (generate_free_image(args.prompt) if args.prompt else None)
    out = build(image_path=image, video_path=args.video, out_path=args.out,
                headline=args.headline, mood=args.mood)
    print(out)

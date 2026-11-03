"""The Real-World Editor — turns shaky client phone footage into a stable,
brand-graded, meta-safe base layer for the 2049 factory.

- stabilize(): cv2 warp-stabilize. On any failure -> raw frames + a 'Steady' blur.
- brand_grade(): shift color temperature/tint toward the client's brand_colors.
- safe_zone(): Meta/TikTok 9:16 UI safe-zone geometry for overlays.

All functions are frame-level (H,W,3) uint8 in / out, so they compose with
moviepy clips without pulling OpenCV into the render loop.
"""
import json
import os

import cv2
import numpy as np

CONFIG = os.path.join(os.path.dirname(__file__), "..", "trend-engine", "config.json")

# Meta/TikTok 9:16 safe zones (as fractions of W,H). Top bar, bottom caption/CTA,
# side rails. Keep the star HUD + headline inside the inner box.
SAFE_ZONE = {
    "top": 0.11,      # status bar + TikTok top UI
    "bottom": 0.20,   # caption + like/share rail
    "left": 0.04,
    "right": 0.04,
    "pad_x": 0.10,    # 10% side padding so the base survives 1:1 feed crop
}


def load_config():
    if os.path.exists(CONFIG):
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f)
    return {}


def safe_box(w, h):
    """Inner (x0,y0,x1,y1) that clears the Meta/TikTok UI chrome."""
    x0 = int(w * SAFE_ZONE["left"])
    x1 = int(w * (1 - SAFE_ZONE["right"]))
    y0 = int(h * SAFE_ZONE["top"])
    y1 = int(h * (1 - SAFE_ZONE["bottom"]))
    return x0, y0, x1, y1


def safe_pad(w, h):
    """(x0, x1) inner bounds after the 10% side padding — keep the base content
    inside this so a 1:1 feed crop (center 720px) never clips the subject."""
    p = SAFE_ZONE["pad_x"]
    return int(w * p), int(w * (1 - p))


def _frame_stabilizer(max_frame=400):
    """Build an OpenCV warp stabilizer tuned for short phone clips."""
    return cv2.createVideoStabilizer(
        smoothing_size=5,
        max_shifting=3,
        max_angle=0.5,
        crop_border=True,
        zoom_rate=-1.5,
        rolling_shutter_correction=True,
    )


def stabilize_frames(frames, max_frame=400):
    """Warp-stabilize a list of (H,W,3) uint8 frames.

    Robustness: if cv2 throws (or stabilizes to nothing), return the raw frames
    with a light 'Steady' Gaussian blur so the base still reads clean.
    Returns (stable_frames, used_raw_fallback: bool).
    """
    frames = [np.asarray(f) for f in frames]
    if not frames:
        return frames, False
    stab = _frame_stabilizer(max_frame)
    out = []
    try:
        for f in frames:
            err, ok = stab.putFrame(f)
            if err == cv2.STAB_OK or err == cv2.STAB_BAD_FRAME:
                out.append(stab.getStabilizedFrame(f))
            elif err == cv2.STAB_MORE_DATA:
                out.append(f)
        stab.waitForAllFrames()
        good = [o for o in out if o is not None and o.shape == frames[0].shape]
        if len(good) >= max(1, int(0.9 * len(frames))):
            return good, False
    except Exception:
        pass
    # fallback: raw + 'Steady' blur
    return [cv2.GaussianBlur(f, (3, 3), 0) for f in frames], True


def brand_grade(frame, brand_rgb, strength=0.35):
    """Tint a frame toward the client's brand color (temperature shift, not a flood).

    Preserves luminance structure: blends a per-channel target toward the frame
    by `strength`, keeping the video looking graded rather than dyed.
    """
    frame = np.asarray(frame, dtype=np.float32)
    b, g, r = brand_rgb  # pass RGB; convert to BGR for cv2 ops if needed
    target = np.array([r, g, b], dtype=np.float32)
    # scale target to the frame's mean brightness so it acts as a grade, not a wash
    mean = frame.mean()
    scale = mean / max(1.0, target.mean())
    target = np.clip(target * scale, 0, 255)
    graded = frame * (1 - strength) + target * strength
    return np.clip(graded, 0, 255).astype(np.uint8)


def grade_frames(frames, brand_rgb, strength=0.35):
    return [brand_grade(f, brand_rgb, strength) for f in frames]


def to_moviepy_clip(frames, fps=30):
    """Wrap graded/stabilized frames into a moviepy VideoClip for compositing."""
    from moviepy import VideoClip
    if not frames:
        return VideoClip(lambda t: np.zeros((1080, 1080, 3), np.uint8), duration=0.1)
    h, w = frames[0].shape[:2]
    duration = len(frames) / fps

    def frame_func(t):
        idx = int(t * fps)
        return frames[min(idx, len(frames) - 1)]

    return VideoClip(frame_func, duration=duration).with_fps(fps).with_size((w, h))


def prepare_base(video_path, brand_rgb=None, strength=0.35, out_fps=30):
    """One-shot: read a client clip -> stabilize -> brand grade -> moviepy clip.

    Returns (clip, meta) where meta={'stabilized': bool, 'size':(w,h), 'fps': int}.
    If the file can't be read, raises — caller should fall back to the AI base.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"could not open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or out_fps
    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame[:, :, ::-1])  # BGR -> RGB
    cap.release()
    if not frames:
        raise RuntimeError("video had no frames")

    stable, used_fallback = stabilize_frames(frames)
    if brand_rgb:
        stable = grade_frames(stable, brand_rgb, strength)
    clip = to_moviepy_clip(stable, fps=out_fps)
    meta = {"stabilized": not used_fallback, "size": (frames[0].shape[1], frames[0].shape[0])}
    return clip, meta

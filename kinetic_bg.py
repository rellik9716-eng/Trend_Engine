"""Kinetic living grid: scrolling 3D perspective grid + floating particles.
moviepy 2.x: make_frame(t) -> (H, W, 3) uint8, y=0 is the TOP."""
import numpy as np

# ponytail: grid+particles drawn per-frame in numpy (fast enough for 1080p).
# If render time matters, pre-render to a video and loop it.

GRID_COLOR = (0, 170, 255)
GLOW = (8, 14, 24)
HORIZON_FRAC = 0.30  # lower on vertical 9:16 so the floor fills the lower 2/3


def _grid_frame(t, shape):
    h, w = shape[:2]
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:] = GLOW
    horizon = int(h * HORIZON_FRAC)

    # --- perspective floor grid (vanishing point top-center) ---
    # z-lines: depth positions scroll toward the viewer
    for i in range(1, 29):  # z >= 0.5 keeps the grid ahead of the viewer
        z = i * 0.5 - ((t * 1.2) % 0.5)
        depth = 1.0 / (1.0 + z * 4.0)      # perspective squash in (0, 1]
        y = int(horizon + (h - horizon) * (1.0 - depth) ** 2)
        if horizon < y < h:
            np.maximum(frame[y], np.array(GRID_COLOR, dtype=np.uint8) // 2, out=frame[y])

    # x-lines: static rays from vanishing point (narrower spread for vertical 9:16)
    cx = w // 2
    for k in range(-10, 11):
        x_top = cx + k * 5
        x_bot = cx + k * 38
        y0, y1 = horizon, h
        for y in range(y0, y1, 4):
            frac = (y - y0) / max(1, y1 - y0)
            x = int(x_top + (x_bot - x_top) * frac)
            if 0 <= x < w:
                frame[y, x] = (GRID_COLOR[0] // 3, GRID_COLOR[1] // 3, GRID_COLOR[2] // 3)

    # --- horizon glow band ---
    glow_h = 6
    band = frame[horizon - glow_h:horizon + glow_h]
    for i, row in enumerate(band):
        fade = int(70 * (1 - abs(i - glow_h) / glow_h))
        row[:] = (0, fade, min(255, fade + 40))

    # --- floating particles ---
    rng = np.random.default_rng(1234)  # fixed seed: deterministic per frame
    n = 60
    speeds = 14 + rng.random(n) * 40   # px/sec upward drift
    xs = rng.integers(0, w, n)
    ys = (rng.integers(0, h, n) + t * speeds) % h
    sizes = rng.integers(1, 4, n)
    alphas = (90 + 90 * np.sin(t * 2.0 + np.arange(n))) .astype(int)
    ys = ys.astype(int)
    for x, y, s, a in zip(xs, ys, sizes, alphas):
        c = (a // 2, a, min(255, a + 60))
        frame[max(0, y - s):y + s, max(0, x - s):x + s] = np.maximum(
            frame[max(0, y - s):y + s, max(0, x - s):x + s], c)

    # faint scanlines for the 2049 feel
    frame[::3, :] = (frame[::3, :] * 235 // 255)
    return frame


def make_kinetic_bg(width=1080, height=1920, duration=30.0):
    from moviepy import VideoClip

    fps = 24
    return VideoClip(lambda t: _grid_frame(t, (height, width, 3)), duration=duration).with_fps(fps)

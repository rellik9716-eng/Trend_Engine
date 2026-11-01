"""Glitch layer: horizontal tear (RGB split + band shift) every 4s for 0.1s.
Apply to the finished composite, not per-layer."""
import numpy as np

GLITCH_PERIOD = 4.0
GLITCH_DUR = 0.1


def apply_glitch(clip):
    from moviepy import VideoClip

    def frame_func(t):
        img = clip.get_frame(t)
        if (t % GLITCH_PERIOD) >= (GLITCH_PERIOD - GLITCH_DUR):
            rng = np.random.default_rng(int(t * 1000))  # deterministic per t
            h = img.shape[0]
            # 3-5 torn horizontal bands, shifted in x
            for _ in range(rng.integers(3, 6)):
                y0 = int(rng.integers(0, h - 20))
                band_h = int(rng.integers(6, 40))
                shift = int(rng.integers(-60, 61))
                band = img[y0:y0 + band_h]
                img[y0:y0 + band_h] = np.roll(band, shift, axis=1)
                # RGB split on the torn band
                img[y0:y0 + band_h, :, 0] = np.roll(band[:, :, 0], shift // 2, axis=1)
                img[y0:y0 + band_h, :, 2] = np.roll(band[:, :, 2], -shift // 2, axis=1)
            # one loud slice: swap rows between two random y positions
            a, b = (int(x) for x in rng.integers(0, h, 2))
            img[a], img[b] = img[b], img[a]
            # white flash line
            img[int(rng.integers(0, h))] = 255
        return img

    return VideoClip(frame_func, duration=clip.duration).with_fps(clip.fps).with_start(clip.start)

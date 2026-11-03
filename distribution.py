"""The Autopilot "Distribution" Blast — posts the rendered MP4 to client socials.

- TikTok: TikTok Web GraphQL (upload_video). Needs TIKTOK_COOKIE in APIKeys.env.
- Instagram: instagrapi (pip install instagrapi). Needs IG_USERNAME/IG_PASSWORD.

Caption Inject: builds a high-CTR caption from the Gap + Mood with 5-10 niche
hashtags from config. Both platforms get the same caption (TikTok has a 2200
char cap, IG 2200 too — we stay under both).

Keys live in video_factory/APIKeys.env (gitignored). Usage:
    python distribution.py <mp4> --headline "..." --mood Anxiety
"""
import json
import os
import re
import sys

import requests

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(BASE, "..", "trend-engine", "config.json")
ENV_PATH = os.path.join(BASE, "APIKeys.env")
TICKS_LOG = os.path.join(BASE, "post_ticks.json")

TOK_UPLOAD_URL = "https://www.tiktok.com/api/post/v2/upload/"
TOK_CREATE_URL = "https://www.tiktok.com/api/post/v2/create/"


# ---------------------------------------------------------------------------
# Config + keys
# ---------------------------------------------------------------------------
def load_config():
    if os.path.exists(CONFIG):
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_keys():
    """Parse APIKeys.env (KEY=VALUE lines, # comments) into a dict."""
    keys = {}
    if os.path.exists(ENV_PATH):
        for line in open(ENV_PATH, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                keys[k.strip()] = v.strip().strip('"').strip("'")
    return keys


# ---------------------------------------------------------------------------
# Caption Inject
# ---------------------------------------------------------------------------
_MOOD_HOOK = {
    "Anxiety": "Still {pain}? It's not you — it's the stack.",
    "Hype":    "Stop doing {pain} the slow way. The signal is live.",
    "Urgency": "{pain} is costing you. The window closes soon.",
}


def high_ctr_caption(gap, mood, cta_url=None, hashtags_n=8):
    """High-CTR caption from a hunted Gap + Mood, capped at `hashtags_n` tags.

    gap shape: {'niche_area': str, 'top_pains': {phrase: count}} (see top_gaps).
    """
    area = (gap.get("niche_area") or "your niche").strip().title()
    pain = ""
    pains = gap.get("top_pains") or {}
    if pains:
        pain = max(pains, key=lambda k: pains[k]).strip()
    mood_l = (mood or "Hype").lower()
    hook = _MOOD_HOOK.get(mood_l, _MOOD_HOOK["Hype"])
    if pain:
        hook = hook.replace("{pain}", f"{pain} {area}".lower().strip())
    else:
        hook = hook.replace("{pain}", area.lower())

    # Hashtags: niche keywords from config + gap area, 5-10, all #lowercaseword
    tags = set()
    for kw in load_config().get("niche_keywords", []):
        for word in re.split(r"\s+", str(kw).lower()):
            if len(word) > 3:
                tags.add(word)
        if len(tags) >= hashtags_n:
            break
    area_words = re.split(r"\s+", re.sub(r"[^a-z0-9 ]", "", area.lower()))
    for w in area_words:
        if len(w) > 3:
            tags.add(w)
    # always close with the brand tag
    tags.add("havenwright")
    tags.update(["ai", "automation"])
    tags = list(dict.fromkeys(tags))[:hashtags_n]

    caption = (
        f"{hook}\n\n"
        f"👉 {cta_url or 'Link in bio'} — the gap is already hunted, the asset is already rendered.\n\n"
        + " ".join(f"#{t}" for t in tags)
    )
    return caption[:2200]


# ---------------------------------------------------------------------------
# TikTok push
# ---------------------------------------------------------------------------
def push_tiktok(video_path, caption, keys=None, dry_run=False):
    """Upload an MP4 to TikTok via the Web GraphQL API.

    Needs TIKTOT_COOKIE (a full `sessionid=...` cookie header).
    Returns (ok: bool, detail: str).
    """
    keys = keys or load_keys()
    cookie = keys.get("TIKTOK_COOKIE", "").strip()
    if not cookie:
        return False, "TIKTOK_COOKIE not set in APIKeys.env"

    headers = {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    if dry_run:
        return True, f"dry_run: would upload {os.path.basename(video_path)} ({len(caption)} char caption)"

    with open(video_path, "rb") as f:
        files = {"data": (os.path.basename(video_path), f, "video/mp4")}
        r = requests.post(TOK_UPLOAD_URL, headers=headers, files=files, timeout=120)
    if r.status_code != 200:
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    data = r.json()
    vid_id = data.get("data", {}).get("id")
    if not vid_id:
        return False, f"no video id in response: {str(data)[:200]}"

    # Finalize with caption
    body = {
        "id": vid_id,
        "description": caption,
        "privacyLevel": "0",
        "videoTaskType": "0",
    }
    r2 = requests.post(TOK_CREATE_URL, headers=headers, json=body, timeout=60)
    ok = r2.status_code == 200
    detail = str(r2.json())[:300] if ok else f"HTTP {r2.status_code}: {r2.text[:200]}"
    return ok, detail


# ---------------------------------------------------------------------------
# Instagram push
# ---------------------------------------------------------------------------
def push_instagram(video_path, caption, keys=None, dry_run=False):
    """Upload an MP4 to Instagram as a Reel via instagrapi.

    Needs IG_USERNAME + IG_PASSWORD in APIKeys.env.
    Returns (ok: bool, detail: str).
    """
    keys = keys or load_keys()
    user = keys.get("IG_USERNAME", "").strip()
    pw = keys.get("IG_PASSWORD", "").strip()
    if not user or not pw:
        return False, "IG_USERNAME/IG_PASSWORD not set in APIKeys.env"
    if dry_run:
        return True, f"dry_run: would upload {os.path.basename(video_path)} to @{user}"

    try:
        from instagrapi import Instagram
    except ImportError:
        return False, "instagrapi not installed (pip install instagrapi)"

    ig = Instagram()
    try:
        ig.login(user, pw)
        media_id = ig.clips_upload(video_path, caption=caption)
        return True, f"reel_media_id={media_id}"
    except Exception as e:
        return False, f"instagrapi: {e}"
    finally:
        ig.logout()


# ---------------------------------------------------------------------------
# Tick log — every post gets a row so performance_tracker has data to learn from
# ---------------------------------------------------------------------------
def log_tick(platform, video_path, caption, mood, gap_area, ok, detail):
    """Append a post record to post_ticks.json (the tracker's input)."""
    import datetime
    ticks = []
    if os.path.exists(TICKS_LOG):
        with open(TICKS_LOG, encoding="utf-8") as f:
            ticks = json.load(f)
    ticks.append({
        "ts": datetime.datetime.now().isoformat(),
        "platform": platform,
        "video": os.path.basename(video_path),
        "mood": mood,
        "gap_area": gap_area,
        "caption": caption[:200],
        "ok": ok,
        "detail": detail,
        "cpl": None,  # filled in by performance_tracker
        "views": None,
        "leads": None,
    })
    with open(TICKS_LOG, "w", encoding="utf-8") as f:
        json.dump(ticks, f, indent=2)
    return len(ticks)


def blast(video_path, caption, mood, gap_area, keys=None, dry_run=False):
    """Fire the full blast: TikTok + Instagram, then log ticks for both."""
    results = {}
    for name, fn in [("tiktok", push_tiktok), ("instagram", push_instagram)]:
        ok, detail = fn(video_path, caption, keys=keys, dry_run=dry_run)
        results[name] = {"ok": ok, "detail": detail}
        log_tick(name, video_path, caption, mood, gap_area, ok, detail)
        print(f"  [{'✔' if ok else '✖'}] {name}: {detail[:120]}")
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("video", help="Path to the rendered MP4")
    ap.add_argument("--headline", default="THE SIGNAL IS LIVE")
    ap.add_argument("--mood", default="Hype")
    ap.add_argument("--gap", default="ai automation", help="Gap niche area for hashtags")
    ap.add_argument("--cta", default=None, help="Client CTA URL (goes in caption)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    gap = {"niche_area": args.gap, "top_pains": {args.headline.lower(): 1}}
    cap = high_ctr_caption(gap, args.mood, cta_url=args.cta)
    print("CAPTION:\n", cap, "\n")
    if args.dry_run:
        blast(args.video, cap, args.mood, args.gap, dry_run=True)
    else:
        keys = load_keys()
        blast(args.video, cap, args.mood, args.gap, keys=keys)

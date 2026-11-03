"""The Niche Hunter — hunts market gaps in the client's niche.

A "Gap" is a high-volume pain with low competition:
    gap_score = complaint_volume - competition
Scrapes Reddit (no auth, .json) for pain phrases and approximates competition
from the brand/keyword density of the same thread set. Each gap carries a
Mood tag (Anxiety / Hype / Urgency) that drives the downstream 2049 palette.

Usage:  python niche_hunter.py [--subreddit Entrepreneur] [--json]
        or: from niche_hunter import hunt_gaps, top_gaps
"""
import argparse
import json
import os
import re
from collections import Counter

import requests

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# Pain lexicon — each phrase maps to a mood. Volume = how many posts contain it.
PAIN_PHRASES = {
    "Anxiety": [
        "struggling with", "stuck on", "overwhelmed", "no idea how",
        "wasting time", "burned out", "drowning in", "afraid of", "dreading",
        "running out of", "hate doing", "terrified of", "can't figure out",
    ],
    "Hype": [
        "just shipped", "breakthrough", "game changer", "blown away",
        "holy grail", "unfair advantage", "print money", "10x", "secret weapon",
    ],
    "Urgency": [
    "before it's too late", "deadline", "losing deals", "chasing leads",
    "behind the curve", "fomo", "act now", "can't afford to wait", "falling behind",
    ],
}

# Competition = how crowded the niche's top brands/keywords are in the same set.
COMPETITION_TERMS = [
    "crm", "saas", "zapier", "make.com", "hubspot", "salesforce", "clay",
    "instantly", "apollo", "lemlist", "outreach", "lead gen", "ai agent",
    "automation", "workflow", "tool", "platform", "software",
]

DEFAULT_SUBREDDITS = ["Entrepreneur", "startups", "smallbusiness", "marketing"]


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def fetch_reddit(subreddit, limit=100):
    """Latest posts from a subreddit via the public .json endpoint (no auth)."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}&raw_json=1"
    r = requests.get(url, headers={"User-Agent": "niche-hunter/1.0"}, timeout=20)
    r.raise_for_status()
    out = []
    for c in r.json().get("data", {}).get("children", []):
        d = c.get("data", {})
        out.append({
            "title": d.get("title", ""),
            "body": d.get("selftext", ""),
            "score": d.get("score", 0),
            "comments": d.get("num_comments", 0),
        })
    return out


def _count_hits(text, phrases):
    """Return (hits, phrase_counts) for a list of phrases in one text blob."""
    low = text.lower()
    counts = Counter()
    for p in phrases:
        n = low.count(p.lower())
        if n:
            counts[p] = n
    return sum(counts.values()), counts


def scan_subreddit(subreddit, limit=100):
    """Aggregate pain volume + competition + mood for one subreddit."""
    posts = fetch_reddit(subreddit, limit=limit)
    if not posts:
        return None
    blob = "\n".join(p["title"] + "\n" + p["body"] for p in posts)

    mood_volume = {}
    for mood, phrases in PAIN_PHRASES.items():
        vol, counts = _count_hits(blob, phrases)
        if vol:
            mood_volume[mood] = {"volume": vol, "phrases": dict(counts)}

    comp, comp_counts = _count_hits(blob, COMPETITION_TERMS)

    total_pain = sum(v["volume"] for v in mood_volume.values())
    # Gap = lots of pain, little competition. +1 keeps score non-negative.
    gap_score = max(0, total_pain - comp)

    top_mood = max(mood_volume, key=lambda m: mood_volume[m]["volume"]) if mood_volume else None

    return {
        "subreddit": subreddit,
        "posts_scanned": len(posts),
        "pain_total": total_pain,
        "competition": comp,
        "competition_terms": dict(comp_counts),
        "mood_volume": mood_volume,
        "top_mood": top_mood,
        "gap_score": gap_score,
    }


def mood_tag(mood):
    """Map a mood to a 2049 accent color. Default (no mood) -> Cyan/Hype."""
    return {
        "Anxiety": (255, 60, 120),   # neon rose
        "Hype": (0, 200, 255),       # cyan
        "Urgency": (255, 170, 0),    # amber
    }.get(mood, (0, 200, 255))


def hunt_gaps(subreddits=None, limit=100):
    """Scan every subreddit, return one row per subreddit (raw gap stats)."""
    cfg = load_config()
    subs = subreddits or cfg.get("subreddits", DEFAULT_SUBREDDITS)
    rows = []
    for s in subs:
        try:
            row = scan_subreddit(s, limit=limit)
            if row:
                rows.append(row)
        except Exception as e:
            print(f"[{s}] FAILED: {e}")
    return rows


def top_gaps(rows, n=3):
    """The 'top 3 Gaps' — highest gap_score, each with a Mood tag.

    Autopilot 'Vibe Shift': if config.json has mood_bias (written by
    performance_tracker after a Mood wins on CPL), rows whose top_mood matches
    the biased mood get a 1.25x gap_score bump so the next hunt skews there.
    """
    bias = (load_config().get("mood_bias") or {}).get("mood")
    ranked = sorted(rows, key=lambda r: (r["gap_score"] * (1.25 if bias and r.get("top_mood") == bias else 1.0)),
                    reverse=True)[:n]
    gaps = []
    for i, r in enumerate(ranked, 1):
        mood = r["top_mood"] or "Hype"  # no mood -> default Cyan/Hype
        gaps.append({
            "rank": i,
            "niche_area": r["subreddit"],
            "gap_score": r["gap_score"],
            "pain_volume": r["pain_total"],
            "competition": r["competition"],
            "mood": mood,
            "mood_color": mood_tag(mood),
            "top_pains": dict(sorted(
                (r["mood_volume"].get(mood, {}).get("phrases", {}).items()),
                key=lambda kv: -kv[1],
            )[:5]),
        })
    return gaps


def main():
    ap = argparse.ArgumentParser(description="Hunt market gaps")
    ap.add_argument("--subreddit", action="append", help="Subreddit (repeatable)")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--json", action="store_true", help="Dump full JSON")
    args = ap.parse_args()

    rows = hunt_gaps(args.subreddit, limit=args.limit)
    gaps = top_gaps(rows)

    if args.json:
        print(json.dumps({"gaps": gaps, "raw": rows}, indent=2))
        return

    print("=== MARKET GAPS ===")
    for g in gaps:
        print(f"\n#{g['rank']}  [{g['mood']}]  gap_score={g['gap_score']}  "
              f"pain={g['pain_volume']}  comp={g['competition']}  ({g['niche_area']})")
        for phrase, n in g["top_pains"].items():
            print(f"    · {phrase!r}  x{n}")
    if not gaps:
        print("  (no gaps found — widen the subreddits)")


if __name__ == "__main__":
    main()

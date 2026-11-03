"""The Autopilot "Feedback" Loop — the Brain that learns.

Reads post_ticks.json (written by distribution.log_tick) and:
  1. CPL Watch  — average Cost-Per-Lead over the last 5 posts.
  2. Vibe Shift — if one Mood beats another by ≥20% on CPL, biases the
                  Niche Hunter toward the winning Mood in config.json.

CPL source: each tick row has `cpl` (dollars per lead). If the client feeds
real campaign data (Meta/TikTok Ads Manager export), set cpl per row before
running this. If `leads` is populated, CPL is derived: spend/leads.

Usage:
    python performance_tracker.py            # check CPL + shift vibe
    python performance_tracker.py --min-posts 5  # only act after 5+ data points
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(BASE, "..", "trend-engine", "config.json")
TICKS = os.path.join(BASE, "post_ticks.json")

MOODS = ["Anxiety", "Hype", "Urgency"]


def load_config():
    if os.path.exists(CONFIG):
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg):
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def load_ticks():
    if os.path.exists(TICKS):
        with open(TICKS, encoding="utf-8") as f:
            return json.load(f)
    return []


# ---------------------------------------------------------------------------
# CPL Watch
# ---------------------------------------------------------------------------
def cpl_watch(ticks=None, n=5):
    """Average CPL over the last `n` posts that have a CPL value.

    A tick carries `cpl` directly, or `leads` (so CPL = spend/leads when
    `spend` is set on the row). Rows without either are skipped.
    Returns {'avg_cpl': float|None, 'count': int, 'rows': [tick, ...]}.
    """
    ticks = ticks or load_ticks()
    with_cpl = []
    for t in ticks:
        cpl = t.get("cpl")
        if cpl is None and t.get("leads"):
            spend = t.get("spend", 0)
            cpl = spend / t["leads"] if t["leads"] else None
        if cpl is not None and cpl > 0:
            with_cpl.append({**t, "cpl": float(cpl)})
    last = with_cpl[-n:]
    avg = sum(r["cpl"] for r in last) / len(last) if last else None
    return {"avg_cpl": avg, "count": len(last), "rows": last}


# ---------------------------------------------------------------------------
# Vibe Shift
# ---------------------------------------------------------------------------
def vibe_shift(ticks=None, threshold=0.20):
    """If one Mood's CPL is ≥`threshold` (20%) lower than the other's,
    update config.json to bias the Niche Hunter toward the winner.

    Writes config['mood_bias'] = {"mood": <winner>, "edge": <pct>}.
    The Niche Hunter reads this to weight gap ranking toward that Mood.
    Returns {'shifted': bool, 'winner': str|None, 'edge_pct': float|None,
             'by_mood': {mood: {'cpl': float, 'count': int}}}.
    """
    ticks = ticks or load_ticks()
    # Group CPL by mood
    by_mood = {}
    for t in ticks:
        cpl = t.get("cpl")
        if cpl is None and t.get("leads"):
            cpl = (t.get("spend", 0) / t["leads"]) if t["leads"] else None
        if cpl is None or cpl <= 0 or t.get("mood") not in MOODS:
            continue
        by_mood.setdefault(t["mood"], []).append(float(cpl))

    avg = {m: sum(v) / len(v) for m, v in by_mood.items() if v}
    if len(avg) < 2:
        return {"shifted": False, "winner": None, "edge_pct": None,
                "by_mood": {m: {"cpl": (round(avg[m], 2) if m in avg else None),
                                "count": len(by_mood.get(m, []))} for m in MOODS}}

    # Find the best (lowest CPL) mood
    winner = min(avg, key=avg.get)
    # Compare against the worst (highest CPL) mood for the edge
    worst = max(avg, key=avg.get)
    edge = (avg[worst] - avg[winner]) / avg[worst] if avg[worst] > 0 else 0

    cfg = load_config()
    if edge >= threshold:
        cfg["mood_bias"] = {"mood": winner, "edge_pct": round(edge * 100, 1)}
        save_config(cfg)
        return {"shifted": True, "winner": winner,
                "edge_pct": round(edge * 100, 1), "by_mood": {
                    m: {"cpl": (round(avg[m], 2) if m in avg else None),
                        "count": len(by_mood.get(m, []))} for m in MOODS}}

    # No shift — clear any old bias if one exists
    if "mood_bias" in cfg:
        del cfg["mood_bias"]
        save_config(cfg)
    return {"shifted": False, "winner": None, "edge_pct": None,
            "by_mood": {m: {"cpl": (round(avg[m], 2) if m in avg else None),
                            "count": len(by_mood.get(m, []))} for m in MOODS}}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5, help="Window for CPL watch")
    args = ap.parse_args()

    ticks = load_ticks()
    if not ticks:
        print("No post ticks yet. Run distribution.py first.")
        sys.exit(0)

    print(f"=== AUTOPilot FEEDBACK — {len(ticks)} posts logged ===\n")

    cw = cpl_watch(ticks, n=args.n)
    print(f"CPL WATCH (last {cw['count']} with data):")
    if cw["avg_cpl"] is not None:
        print(f"  avg CPL: ${cw['avg_cpl']:.2f}")
        for r in cw["rows"]:
            print(f"    [{r['mood']}] {r['platform']} — ${r['cpl']:.2f}  ({r['video']})")
    else:
        print("  (no CPL data yet — set `cpl` or `leads`+`spend` on tick rows)")

    print("\nVIBE SHIFT:")
    vs = vibe_shift(ticks)
    if vs["shifted"]:
        print(f"  ✔ SHIFTED toward [{vs['winner']}] — {vs['edge_pct']:.1f}% lower CPL")
        for m, d in vs["by_mood"].items():
            if d["cpl"] is not None:
                print(f"    {m:10s} CPL ${d['cpl']:.2f}  ({d['count']} posts)")
    else:
        print("  — no shift (need ≥2 moods with data and ≥20% CPL edge)")
        for m, d in vs["by_mood"].items():
            if d["cpl"] is not None:
                print(f"    {m:10s} CPL ${d['cpl']:.2f}  ({d['count']} posts)")

import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

# Load APIKeys.env (same folder) and any .env if present
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "APIKeys.env"))
load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Required fields per platform (for the Active/Inactive status check)
PLATFORM_REQS = {
    "youtube":               ["api_key"],
    "google_custom_search":  ["api_key", "cx"],
    "google_trends":         [],
    "hackernews":            [],
    "techcrunch":            [],
    "reddit":                [],
    "tiktok":                [],
    "instagram":             ["api_key"],
    "facebook":              ["api_key"],
    "twitter_x":             [],
    "pinterest":             [],
}

DEFAULT_PLATFORMS = {
    "youtube":              {"enabled": True},
    "google_custom_search": {"enabled": False},
    "google_trends":        {"enabled": False},
    "hackernews":           {"enabled": True},
    "techcrunch":           {"enabled": True},
    "reddit":               {"enabled": False},
    "tiktok":               {"enabled": False},
    "instagram":            {"enabled": False},
    "facebook":             {"enabled": False},
    "twitter_x":            {"enabled": False},
    "pinterest":            {"enabled": False},
}


def load_config():
    """
    Load config.json. Returns a dict with all fields.
    'platforms' is a dict: {platform_name: {enabled: bool, api_key: str, cx: str, ...}}
    Missing platforms get default entries.
    """
    defaults = {
        "agency_name": "Your Agency Name",
        "product": "Your AI Product/Service",
        "target_niche": "",
        "pain_points": [],
        "search_keywords": [],
        "search_region": "US",
        "max_results": 10,
        "platforms": DEFAULT_PLATFORMS,
    }

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            user = json.load(f)
    except FileNotFoundError:
        print("⚠️  config.json not found — using built-in defaults.")
        return defaults
    except json.JSONDecodeError as e:
        print(f"❌ config.json is not valid JSON: {e} — using defaults.")
        return defaults

    # Merge user config over defaults
    cfg = dict(defaults)
    for k, v in user.items():
        cfg[k] = v

    # Ensure platforms is a proper dict with all known entries
    if not isinstance(cfg.get("platforms"), dict):
        print("⚠️  config.json 'platforms' is not an object — using defaults.")
        cfg["platforms"] = dict(DEFAULT_PLATFORMS)

    # Fill in any missing platform entries
    for name in DEFAULT_PLATFORMS:
        if name not in cfg["platforms"]:
            cfg["platforms"][name] = {"enabled": False}
        # Ensure each entry has 'enabled'
        if "enabled" not in cfg["platforms"][name]:
            cfg["platforms"][name]["enabled"] = False
        # Ensure each entry is a dict (not a plain true/false in old-format)
        if not isinstance(cfg["platforms"][name], dict):
            cfg["platforms"][name] = {"enabled": bool(cfg["platforms"][name])}

    return cfg


# ---------------------------------------------------------------------------
# Status check (shown in main before scraping)
# ---------------------------------------------------------------------------

def platform_status(cfg):
    status = {}
    platforms = cfg.get("platforms", {})
    no_key_needed = ["google_trends", "hackernews", "techcrunch", "tiktok"]
    for name, settings in platforms.items():
        is_enabled = settings.get("enabled", False)
        has_key = bool(settings.get("api_key", "").strip())
        if not is_enabled:
            status[name] = (False, "disabled in config")
        elif name in no_key_needed:
            status[name] = (True, "")
        elif has_key:
            status[name] = (True, "")
        else:
            status[name] = (False, "enabled but api_key is empty")
    return status


def print_status(cfg):
    """Print the Active/Inactive table required by the task."""
    print("\n📋 Platform Status:")
    print("-" * 44)
    for name, (active, reason) in platform_status(cfg).items():
        label = "✅ Active" if active else "⏭️  Inactive"
        print(f"  {name:<24} {label}")
        if not active:
            print(f"  {' ' * 24} ({reason})")
    print("-" * 44 + "\n")


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

def fetch_youtube(cfg):
    """Trending videos + keyword searches via YouTube Data API v3."""
    p = cfg["platforms"].get("youtube", {})
    key = (p.get("api_key") or "").strip()
    if not key:
        print("⏭️  YouTube: enabled but api_key is empty — skipped.")
        return []

    trends = []
    try:
        # Part 1: Trending
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "maxResults": cfg["max_results"],
                "regionCode": cfg["search_region"],
                "key": key,
            },
            timeout=15,
        )
        if r.status_code == 200:
            for item in r.json().get("items", []):
                stats = item.get("statistics", {})
                trends.append({
                    "platform": "YouTube",
                    "kind": "trending",
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                })
            print(f"  YouTube trending: {len(trends)} items")
        else:
            print(f"  ❌ YouTube trending error {r.status_code}: {r.text[:200]}")

        # Part 2: Niche keyword searches
        for kw in cfg["search_keywords"][:3]:
            r = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": kw,
                    "maxResults": 5,
                    "type": "video",
                    "regionCode": cfg["search_region"],
                    "key": key,
                },
                timeout=15,
            )
            if r.status_code == 200:
                for item in r.json().get("items", []):
                    trends.append({
                        "platform": "YouTube",
                        "kind": f"search: {kw}",
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                    })
            else:
                print(f"  ❌ YouTube search '{kw}' error {r.status_code}")

    except Exception as e:
        print(f"  ❌ YouTube exception: {e}")

    if trends:
        print(f"✅ YouTube: {len(trends)} total items")
    return trends


def fetch_google_custom_search(cfg):
    """
    Programmable Search Engine (CSE).
    Uses the same Google Cloud API key as YouTube, plus a unique cx ID.
    """
    p = cfg["platforms"].get("google_custom_search", {})
    key = (p.get("api_key") or "").strip()
    cx  = (p.get("cx") or "").strip()

    if not key:
        print("⏭️  Google Custom Search: enabled but api_key is empty — skipped.")
        return []
    if not cx or "PASTE" in cx.upper():
        print("⏭️  Google Custom Search: enabled but cx is empty or placeholder — skipped.")
        return []

    trends = []
    for kw in cfg["search_keywords"][:3]:
        try:
            r = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"q": kw, "key": key, "cx": cx, "num": min(cfg["max_results"], 10)},
                timeout=15,
            )
            if r.status_code == 200:
                for item in r.json().get("items", []):
                    trends.append({
                        "platform": "Google Custom Search",
                        "kind": f"search: {kw}",
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", "")[:300],
                    })
                print(f"  CSE '{kw}': {len(r.json().get('items', []))} results")
            else:
                print(f"  ❌ CSE '{kw}' error {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"  ❌ CSE '{kw}' exception: {e}")

    if trends:
        print(f"✅ Google Custom Search: {len(trends)} total items")
    return trends


import asyncio
from playwright.async_api import async_playwright

def fetch_tiktok(cfg):
    """
    Fetches TikTok trends using a Headless Browser (Playwright).
    This bypasses most JavaScript rendering issues.
    """


    async def _scrape():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Set a realistic user agent


            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            try:
                await page.goto("https://www.tiktok.com/discover", wait_until="networkidle", timeout=30000)
                # Wait for the specific element that holds the trends
                # TikTok uses a lot of dynamic classes, so we wait for a generic container


                await page.wait_for_selector("div[class*='discover']", timeout=10000)
                # Extract the data from the embedded JSON which is now loaded
                data = await page.evaluate("""() => {


                    const script = document.getElementById("__NEXT_DATA__");
                    if (script) {
                        return JSON.parse(script.innerHTML);
                    }
                    return null;
                }""")
                
                await browser.close()
                return data
                
            except Exception as e:
                await browser.close()
                raise e

    try:
        print("⏳ TikTok: Launching headless browser...")
        data = asyncio.run(_scrape())
        
        if not data:
            print("⚠️ TikTok: No data returned from browser.")
            return []
            
        trends = []
        # Navigate the Next.js data structure


        try:
            # The path can vary, so we try to find the 'chart' or 'trending' list
            props = data.get("props", {}).get("pageProps", {})
            initial_state = props.get("initialState", {})
            discover = initial_state.get("discover", {})
            chart = discover.get("chart", [])


            for item in chart[:cfg["max_results"]]:
                if isinstance(item, dict):
                    title = item.get("title") or item.get("hashtagName", "")
                    if title:
                        trends.append({
                            "platform": "TikTok",
                            "title": title,
                            "type": "trending_hashtag"
                        })
        except Exception:
            pass
            
        if trends:
            print(f"✅ TikTok: {len(trends)} trends fetched via Headless Browser.")
            return trends
        else:
            print("⚠️ TikTok: Browser loaded but no trends extracted.")
            return []
            
    except Exception as e:
        print(f"❌ TikTok Headless Error: {e}")
        return []
        
def fetch_google_trends(cfg):
    """
    Google Trends — Daily Trends via RSS.
    Filters general trends against your Niche Keywords to find 'Niche Hits'.
    """
    trends = []
    niche_keywords = [kw.lower() for kw in cfg["search_keywords"]]

    try:
        r = requests.get(
            f"https://trends.google.com/trending/rss?geo={cfg['search_region']}",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:cfg["max_results"]]:
                title_tag = item.find("title")
                link_tag = item.find("link")
                if title_tag is not None and title_tag.text:
                    title_text = title_tag.text.strip()
                    # Check if this general trend matches our niche
                    is_niche_hit = any(kw in title_text.lower() for kw in niche_keywords)

                    trends.append({
                        "platform": "Google Trends",
                        "kind": "niche_hit" if is_niche_hit else "daily_general",
                        "title": title_text,
                        "link": link_tag.text.strip() if link_tag is not None and link_tag.text else "",
                    })
            niche_count = sum(1 for t in trends if t["kind"] == "niche_hit")

            print(f"✅ Google Trends: {len(trends)} items ({niche_count} niche hits)")
        else:
            print(f"⚠️ Google Trends RSS returned {r.status_code}")
    except Exception as e:
        print(f"❌ Google Trends RSS exception: {e}")

    return trends


def fetch_hackernews(cfg):
    """Top stories from Hacker News (free, no key)."""
    trends = []
    try:
        r = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=15)
        if r.status_code != 200:
            print(f"  ❌ HN error: {r.text[:200]}")
            return []
        for story_id in r.json()[:cfg["max_results"]]:
            item_r = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=15
            )
            if item_r.status_code == 200:
                item = item_r.json()
                if item:
                    trends.append({
                        "platform": "Hacker News",
                        "kind": "top",
                        "title": item.get("title"),
                        "score": item.get("score"),
                        "url": item.get("url"),
                    })
        print(f"✅ Hacker News: {len(trends)} items")
    except Exception as e:
        print(f"  ❌ HN exception: {e}")
    return trends


def fetch_techcrunch(cfg):
    """Top tech news from TechCrunch RSS (free, no key)."""
    trends = []
    try:
        r = requests.get("https://techcrunch.com/feed/", timeout=15)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:cfg["max_results"]]:
                title = item.find("title")
                link  = item.find("link")
                if title is not None and title.text:
                    trends.append({
                        "platform": "TechCrunch",
                        "kind": "latest",
                        "title": title.text.strip(),
                        "link": link.text.strip() if link is not None and link.text else "",
                    })
            print(f"✅ TechCrunch: {len(trends)} items")
        else:
            print(f"  ❌ TechCrunch error: {r.text[:200]}")
    except Exception as e:
        print(f"  ❌ TechCrunch exception: {e}")
    return trends


def fetch_reddit(cfg):
    """Hot posts in r/all + keyword search (free, no key)."""
    trends = []
    headers = {"User-Agent": "trend-engine/1.0"}
    try:
        r = requests.get(
            "https://www.reddit.com/r/all/hot.json",
            params={"limit": cfg["max_results"]}, headers=headers, timeout=15
        )
        if r.status_code == 200:
            for item in r.json()["data"]["children"]:
                d = item.get("data", {})
                trends.append({
                    "platform": "Reddit",
                    "kind": "hot: r/all",
                    "title": d.get("title"),
                    "score": d.get("score"),
                    "subreddit": d.get("subreddit"),
                    "link": f"https://reddit.com{d.get('permalink', '')}",
                })
        for kw in cfg["search_keywords"][:3]:
            r = requests.get(
                "https://www.reddit.com/search.json",
                params={"q": kw, "limit": 5}, headers=headers, timeout=15
            )
            if r.status_code == 200:
                for item in r.json()["data"]["children"]:
                    d = item.get("data", {})
                    trends.append({
                        "platform": "Reddit",
                        "kind": f"search: {kw}",
                        "title": d.get("title"),
                        "score": d.get("score"),
                        "subreddit": d.get("subreddit_name_prefixed"),
                        "link": f"https://reddit.com{d.get('permalink', '')}",
                    })
        print(f"✅ Reddit: {len(trends)} items")
    except Exception as e:
        print(f"  ❌ Reddit exception: {e}")
    return trends


def fetch_instagram(cfg):
    p = cfg["platforms"].get("instagram", {})
    key = (p.get("api_key") or "").strip()
    if not key:
        print("⏭️  Instagram: enabled but api_key is empty — skipped.")
        return []
    trends = []
    for kw in cfg["search_keywords"][:3]:
        try:
            r = requests.get(
                "https://www.instagram.com/web/search/topsearch/",
                params={"query": kw},
                headers={"User-Agent": "Mozilla/5.0"}, timeout=15
            )
            if r.status_code == 200:
                for item in r.json().get("data", [])[:cfg["max_results"]]:
                    trends.append({
                        "platform": "Instagram",
                        "kind": f"search: {kw}",
                        "title": item.get("label", ""),
                        "link": f"https://www.instagram.com/explore/tags/{kw}/",
                    })
            else:
                print(f"  ⚠️  Instagram '{kw}' returned {r.status_code}")
        except Exception as e:
            print(f"  ❌ Instagram '{kw}' exception: {e}")
    if trends:
        print(f"✅ Instagram: {len(trends)} items")
    return trends


def fetch_facebook(cfg):
    p = cfg["platforms"].get("facebook", {})
    token = (p.get("api_key") or "").strip()
    if not token:
        print("⏭️  Facebook: enabled but api_key is empty — skipped.")
        return []
    trends = []
    try:
        kw = cfg["search_keywords"][0] if cfg["search_keywords"] else "news"
        r = requests.get(
            "https://graph.facebook.com/v19.0/search",
            params={
                "q": kw, "type": "post",
                "fields": "message,shares,created_time",
                "limit": cfg["max_results"],
                "access_token": token,
            },
            timeout=15,
        )
        if r.status_code == 200:
            for item in r.json().get("data", []):
                trends.append({
                    "platform": "Facebook",
                    "kind": "search",
                    "title": (item.get("message") or "")[:160],
                    "shares": item.get("shares", {}).get("count", 0),
                })
            print(f"✅ Facebook: {len(trends)} items")
        else:
            print(f"  ❌ Facebook error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ❌ Facebook exception: {e}")
    return trends


def fetch_twitter_x(cfg):
    """Twitter/X trends via syndication endpoint (no key needed)."""
    trends = []
    try:
        r = requests.get(
            "https://syndication.twitter.com/srv/timeline-profile/screen-name/trends",
            timeout=15, headers={"User-Agent": "Mozilla/5.0"}
        )
        if r.status_code == 200:
            for t in r.json().get("trends", [])[:cfg["max_results"]]:
                trends.append({
                    "platform": "Twitter/X",
                    "kind": "trending",
                    "title": t.get("name"),
                    "volume": t.get("volume"),
                })
        else:
            print(f"  ⚠️  Twitter/X syndication returned {r.status_code} (403 is common)")
    except Exception as e:
        print(f"  ❌ Twitter/X exception: {e}")
    if trends:
        print(f"✅ Twitter/X: {len(trends)} items")
    return trends


def fetch_pinterest(cfg):
    p = cfg["platforms"].get("pinterest", {})
    key = (p.get("api_key") or "").strip()
    # Pinterest works without a key via the public resource endpoint; key is optional
    trends = []
    kw = cfg["search_keywords"][0] if cfg["search_keywords"] else "trending"
    try:
        r = requests.get(
            "https://www.pinterest.com/resource/BaseSearchResource/get/",
            params={
                "source_url": "/search/pins/?q=" + requests.utils.quote(kw),
                "data": json.dumps({"options": {"query": kw, "page_size": cfg["max_results"]}}),
            },
            headers={"User-Agent": "Mozilla/5.0"}, timeout=15
        )
        if r.status_code == 200:
            pins = r.json().get("resource_response", {}).get("data", {}).get("results", [])
            for pin in pins[:cfg["max_results"]]:
                trends.append({
                    "platform": "Pinterest",
                    "kind": f"search: {kw}",
                    "title": pin.get("title") or (pin.get("alt_text", "")[:100] or ""),
                })
        if trends:
            print(f"✅ Pinterest: {len(trends)} items")
    except Exception as e:
        print(f"  ❌ Pinterest exception: {e}")
    return trends


FETCHERS = {
    "youtube":              fetch_youtube,
    "google_custom_search": fetch_google_custom_search,
    "google_trends":        fetch_google_trends,
    "hackernews":           fetch_hackernews,
    "techcrunch":           fetch_techcrunch,
    "reddit":               fetch_reddit,
    "tiktok":               fetch_tiktok,
    "instagram":            fetch_instagram,
    "facebook":             fetch_facebook,
    "twitter_x":            fetch_twitter_x,
    "pinterest":            fetch_pinterest,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("🚀 Trend Engine scraper starting...\n")
    cfg = load_config()

    print(f"   Niche:    {cfg['target_niche'] or '(not set)'}")
    print(f"   Region:   {cfg['search_region']}")
    print(f"   Keywords: {cfg['search_keywords']}")
    print()

    # STEP 3: Show which platforms are Active
    print_status(cfg)

    # Collect trends from all active platforms
    all_trends = []
    active = [name for name, (is_active, _) in platform_status(cfg).items() if is_active]


        
    for name in active:
        print(f"→ Fetching: {name}")
        try:
            all_trends.extend(FETCHERS[name](cfg))
        except Exception as e:
            print(f"  ❌ {name} crashed, continuing: {e}")
        print()

    if not all_trends:
        print("❌ No trends collected. Check your config.json.")
        return

    data_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)

    output = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "target_niche":   cfg["target_niche"],
            "search_keywords": cfg["search_keywords"],
            "search_region":  cfg["search_region"],
            "agency_name":    cfg["agency_name"],
            "product":        cfg["product"],
            "pain_points":    cfg["pain_points"],
        },
        "trends": all_trends,
    }

    out_path = os.path.join(data_dir, "raw_trends.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ DONE. {len(all_trends)} trends saved to:\n   {out_path}")
    print("Next: run run_engine.py step 2 (Claude analysis).")


if __name__ == "__main__":
    main()

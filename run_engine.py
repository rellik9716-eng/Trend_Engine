import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPER = os.path.join(BASE_DIR, "scraper.py")


def run_engine():
    print("🚀 Starting Full Trend Engine Loop...")

    # Step 1: Scrape live trends (reads config.json itself)
    print("1/2: Scraping live trend data...")
    result = subprocess.run([sys.executable, SCRAPER], cwd=BASE_DIR)
    if result.returncode != 0:
        print("❌ Scraper failed. Fix the error above, then rerun.")
        return
    print("✅ Scrape complete.")

    # Step 2: Analyze with Claude Code
    print("2/2: Analyzing trends with Claude Code...")
    prompt = """
    You are the Trend Engine.

    1. Read the file data/raw_trends.json (in this same folder).
    2. Read the file config.json — it holds the agency, product, target_niche, pain_points, search_keywords and search_region for this run.
    3. Read the file output/ad_concepts.json if it exists — that is the previous generic run; use it only as a format reference.

    ANALYZE the raw trends through the lens of the target_niche and pain_points from config.json.
    For each platform with data in raw_trends.json, identify:
    - the viral theme or rising trend
    - how it connects to the target niche's pain points

    SYNTHESIZE into 3 Winning Ad Concepts that a LOCAL agency selling this product/service to this niche would use.
    For each concept, give me:
    - The Hook: first 3 seconds, punchy
    - The Angle: psychological trigger (FOMO, Fear, Greed, Status) and a one-line rationale tied to a specific trend you found
    - The Visual: a detailed prompt for an AI video generator (9:16 vertical)
    - The CTA: call to action

    OUTPUT:
    Save the results to output/niche_ad_concepts.json as valid JSON with this shape:
    {
      "generated": "<YYYY-MM-DD>",
      "source": "data/raw_trends.json",
      "niche_analysis": {
        "agency": "...",
        "service_niche": "...",
        "target_audiences": {"primary": "...", "secondary": "..."},
        "pain_points_inferred": ["..."]
      },
      "concepts": [
        {"name": "...", "audience": "...", "trend_source": "...", "hook": "...", "angle": "...", "angle_rationale": "...", "visual_prompt": "...", "cta": "..."}
      ]
    }
    Do NOT invent trends that are not in raw_trends.json. Do NOT invent claims about the product.
    Then display the 3 concepts in the terminal so the user can review them.
    Execute now.
    """

    result = subprocess.run(["claude", prompt], cwd=BASE_DIR)
    if result.returncode != 0:
        print("⚠️  Claude step returned non-zero. Check the output above.")

    print("✅ Loop complete. Check output/niche_ad_concepts.json")


if __name__ == "__main__":
    run_engine()

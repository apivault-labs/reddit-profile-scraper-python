"""
Quickstart: scrape a few Reddit profiles and print key fields.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from reddit_scraper import RedditScraperClient


def main() -> None:
    client = RedditScraperClient()  # picks up APIFY_API_TOKEN from env

    usernames = [
        "https://www.reddit.com/user/GovSchwarzenegger/",
        "spez",
        "kn0thing",
    ]

    print(f"Scraping {len(usernames)} profiles "
          f"(estimated cost: ${client.estimate_cost(len(usernames))})...\n")

    profiles = client.scrape(usernames)

    for p in profiles:
        if not p.get("success"):
            print(f"❌ {p.get('inputUrl') or p.get('profileUrl')}: {p.get('error', '?')}")
            continue
        print(f"u/{p.get('username')}")
        print(f"   Name:     {p.get('displayName') or '—'}")
        print(f"   Category: {p.get('category') or '—'}")
        print(f"   Bio:      {(p.get('bio') or '—')[:80]}")
        print(f"   URL:      {p.get('profileUrl')}")


if __name__ == "__main__":
    main()

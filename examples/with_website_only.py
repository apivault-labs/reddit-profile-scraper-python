"""
Keep only Reddit profiles that expose a website — useful for outreach /
creator-discovery lists.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/with_website_only.py
"""

from reddit_scraper import RedditScraperClient


def main() -> None:
    client = RedditScraperClient()

    usernames = ["spez", "kn0thing", "GovSchwarzenegger", "reddit"]
    profiles = client.scrape(usernames)

    leads = client.filter_with_website(profiles)
    print(f"{len(leads)}/{len(profiles)} profiles expose a website:\n")
    for p in leads:
        print(f"  u/{p['username']}  ->  {p['website']}")


if __name__ == "__main__":
    main()

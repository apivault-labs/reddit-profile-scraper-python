"""
Bulk scrape Reddit usernames from a list (or a file) and export to CSV.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/bulk_scrape.py > reddit_profiles.csv
"""

import csv
import sys

from reddit_scraper import RedditScraperClient

USERNAMES = ["spez", "kn0thing", "GovSchwarzenegger", "reddit"]
COLUMNS = ["username", "displayName", "category", "bio", "website", "profileUrl"]


def main() -> None:
    client = RedditScraperClient()
    profiles = client.filter_successful(
        client.scrape(USERNAMES, max_concurrency=10)
    )

    writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for p in profiles:
        writer.writerow({c: p.get(c, "") for c in COLUMNS})


if __name__ == "__main__":
    main()

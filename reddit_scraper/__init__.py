"""
Reddit Profile Scraper — Python SDK

Official Python client for the apivault_labs/reddit-scraper Apify actor.
Scrape public Reddit user profiles in real time — no login, no API key.

Returns per profile:
- username, display name, bio
- follower / following / post (karma) counts
- profile URL, website, category
- other public metadata (cake day, trophies, premium)

Quick start:

    from reddit_scraper import RedditScraperClient

    client = RedditScraperClient(api_token="apify_api_xxxxxx")

    profiles = client.scrape([
        "https://www.reddit.com/user/GovSchwarzenegger/",
        "spez",
    ])
    for p in profiles:
        print(p["username"], "—", p.get("displayName"), p.get("category"))

See https://github.com/apivault-labs/reddit-profile-scraper-python for full docs.
"""

from .client import RedditScraperClient
from .exceptions import (
    RedditScraperError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    "RedditScraperClient",
    "RedditScraperError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]

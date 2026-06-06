"""Exception classes for the Reddit Profile Scraper SDK."""


class RedditScraperError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(RedditScraperError):
    """Raised when the Apify API token is missing or invalid."""


class ActorRunError(RedditScraperError):
    """Raised when the actor run fails on Apify infrastructure."""


class ActorTimeoutError(RedditScraperError):
    """Raised when the actor run does not finish within the allowed timeout."""

"""
RedditScraperClient — synchronous wrapper around the Apify
``apivault_labs/reddit-scraper`` actor.

The actor scrapes public Reddit user profiles in real time (no login, no API
key) and returns username, display name, bio, follower/post counts, website,
category and other public metadata. This client forwards inputs, polls the
run until it finishes, then downloads the dataset.

Pricing: $0.002 per profile ($2 / 1000).
"""

from __future__ import annotations

import os
import re
import time
from typing import Any, Iterable, Sequence

import requests

from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    RedditScraperError,
)

ACTOR_ID = "apivault_labs~reddit-scraper"
APIFY_API_BASE = "https://api.apify.com/v2"

TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}

PRICE_PER_PROFILE_USD = 0.002

# friendly field name -> actor input toggle
FIELD_MAP = {
    "username": "extractUsername",
    "displayName": "extractFullName",
    "bio": "extractBio",
    "followers": "extractFollowers",
    "following": "extractFollowing",
    "posts": "extractPosts",
    "profileUrl": "extractProfileUrl",
    "website": "extractWebsite",
    "category": "extractCategory",
    "metadata": "extractMetadata",
}


class RedditScraperClient:
    """Synchronous client for the Reddit Profile Scraper Apify actor.

    Parameters
    ----------
    api_token : str, optional
        Apify Personal API token. Falls back to the ``APIFY_API_TOKEN``
        environment variable.
    timeout : int, optional
        Max seconds to wait for an actor run to finish. Default 900.
    poll_interval : float, optional
        Seconds between status polls. Default 3.
    base_url : str, optional
        Override the Apify API base URL (mostly for testing).
    """

    def __init__(
        self,
        api_token: str | None = None,
        timeout: int = 900,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "Apify API token is required. Pass api_token='apify_api_...' "
                "or set the APIFY_API_TOKEN environment variable. "
                "Get a token at https://console.apify.com/account/integrations"
            )
        self._token = token
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "reddit-profile-scraper-python/0.1.0",
        })

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _normalize_url(value: str) -> str:
        """Accept a bare username or any Reddit profile URL and return a
        canonical ``https://www.reddit.com/user/NAME/`` URL."""
        s = (value or "").strip()
        if not s:
            return ""
        m = re.search(r"reddit\.com/(?:user|u)/([^/?#]+)", s, re.I)
        name = m.group(1) if m else s.lstrip("@/").split("/")[0]
        return f"https://www.reddit.com/user/{name}/"

    # ------------------------------------------------------------------ public

    def scrape(
        self,
        profiles: Iterable[str],
        *,
        fields: Sequence[str] | None = None,
        max_concurrency: int = 5,
        timeout_per_profile: int = 90,
        max_retries: int = 3,
        actor_timeout_secs: int = 600,
    ) -> list[dict[str, Any]]:
        """Scrape a batch of public Reddit profiles.

        Parameters
        ----------
        profiles : iterable of str
            Reddit usernames or profile URLs (both ``/user/`` and ``/u/``
            formats accepted).
        fields : sequence of str, optional
            Which fields to extract. Any of: ``username``, ``displayName``,
            ``bio``, ``followers``, ``following``, ``posts``, ``profileUrl``,
            ``website``, ``category``, ``metadata``. Defaults to all fields.
        max_concurrency : int, optional
            Parallel requests (1-20). Default 5.
        timeout_per_profile : int, optional
            Seconds to wait per profile (30-300). Default 90.
        max_retries : int, optional
            Retries on transient failure (0-5). Default 3.
        actor_timeout_secs : int, optional
            Maximum runtime hint passed to the actor.

        Returns
        -------
        list[dict]
            One record per input profile. Failed lookups carry
            ``success=False`` and an ``error`` message.
        """
        urls = [self._normalize_url(p) for p in profiles if p and str(p).strip()]
        urls = [u for u in urls if u]
        if not urls:
            raise ValueError("profiles must contain at least one username or URL")

        payload: dict[str, Any] = {
            "profileUrls": urls,
            "maxConcurrency": max(1, min(20, int(max_concurrency))),
            "timeout": max(30, min(300, int(timeout_per_profile))),
            "maxRetries": max(0, min(5, int(max_retries))),
        }
        if fields is not None:
            wanted = {f for f in fields}
            unknown = wanted - set(FIELD_MAP)
            if unknown:
                raise ValueError(f"Unknown field(s): {sorted(unknown)}. "
                                 f"Valid: {sorted(FIELD_MAP)}")
            for fname, toggle in FIELD_MAP.items():
                payload[toggle] = fname in wanted

        run_id = self._start_run(payload, actor_timeout_secs=actor_timeout_secs)
        run = self._wait_for_run(run_id)
        return self._fetch_dataset(run["defaultDatasetId"])

    def scrape_one(self, profile: str, **kwargs: Any) -> dict[str, Any]:
        """Scrape a single Reddit profile and return its record.

        Raises ``ActorRunError`` if the actor returned no record or the
        lookup failed.
        """
        results = self.scrape([profile], **kwargs)
        if not results:
            raise ActorRunError(f"Actor returned no records for {profile!r}")
        rec = results[0]
        if not rec.get("success", True):
            raise ActorRunError(f"Scrape failed for {profile!r}: {rec.get('error', '?')}")
        return rec

    # ------------------------------------------------------------------ filters

    def filter_successful(self, profiles: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        """Keep only records that scraped successfully."""
        return [r for r in profiles if r.get("success")]

    def filter_with_website(self, profiles: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        """Keep only profiles that expose a website."""
        return [r for r in profiles if (r.get("website") or "").strip()]

    def filter_with_bio(self, profiles: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        """Keep only profiles that have a non-empty bio."""
        return [r for r in profiles if (r.get("bio") or "").strip()]

    def filter_by_category(
        self,
        profiles: Sequence[dict[str, Any]],
        *categories: str,
    ) -> list[dict[str, Any]]:
        """Keep profiles whose category matches any of ``categories``
        (case-insensitive, substring match)."""
        wanted = [c.lower() for c in categories if c]
        if not wanted:
            return list(profiles)
        out = []
        for r in profiles:
            cat = (r.get("category") or "").lower()
            if cat and any(w in cat for w in wanted):
                out.append(r)
        return out

    def estimate_cost(self, profile_count: int) -> float:
        """Return the estimated USD cost for ``profile_count`` profiles
        ($0.002 per profile, $2 / 1000)."""
        return round(profile_count * PRICE_PER_PROFILE_USD, 4)

    # ------------------------------------------------------------------ internal

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        params = {"timeout": int(actor_timeout_secs)}
        try:
            r = self._session.post(url, params=params, json=payload, timeout=30)
        except requests.RequestException as e:
            raise RedditScraperError(f"Failed to start actor run: {e}") from e

        if r.status_code == 401:
            raise AuthenticationError(
                "Apify rejected the API token. Generate a new one at "
                "https://console.apify.com/account/integrations"
            )
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when starting run: {r.text[:300]}"
            )

        data = r.json().get("data") or {}
        run_id = data.get("id")
        if not run_id:
            raise ActorRunError(f"Apify response missing run id: {r.text[:300]}")
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=30)
            except requests.RequestException as e:
                raise RedditScraperError(f"Failed to poll run status: {e}") from e
            if r.status_code >= 400:
                raise ActorRunError(
                    f"Apify returned HTTP {r.status_code} when polling run: {r.text[:300]}"
                )
            run = r.json().get("data") or {}
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(
                    f"Actor run {run_id} ended with status={status}: "
                    f"{run.get('statusMessage') or '(no message)'}"
                )
            if time.time() > deadline:
                raise ActorTimeoutError(
                    f"Actor run {run_id} did not finish within {self._timeout}s "
                    f"(last status={status}). Increase `timeout=` or fetch the "
                    "dataset manually."
                )
            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        try:
            r = self._session.get(url, params=params, timeout=120)
        except requests.RequestException as e:
            raise RedditScraperError(f"Failed to download dataset: {e}") from e
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when fetching dataset: {r.text[:300]}"
            )
        try:
            data = r.json()
        except ValueError as e:
            raise ActorRunError(f"Apify dataset is not valid JSON: {e}") from e
        if not isinstance(data, list):
            raise ActorRunError(
                f"Unexpected dataset payload (not a list): {type(data).__name__}"
            )
        return data

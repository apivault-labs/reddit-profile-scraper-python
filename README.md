# Reddit Profile Scraper — Python SDK

Official Python client for the **[Reddit Profile Scraper](https://apify.com/apivault_labs/reddit-scraper)** Apify actor. Scrape public Reddit user profiles in real time — **no login, no API key, no browser**.

Built by **[ApiVault Labs](https://apify.com/apivault_labs)**.

## Install

```bash
pip install reddit-profile-scraper
```

## Quick start

```python
from reddit_scraper import RedditScraperClient

client = RedditScraperClient(api_token="apify_api_xxxxxx")  # or APIFY_API_TOKEN env

profiles = client.scrape([
    "https://www.reddit.com/user/GovSchwarzenegger/",
    "spez",  # bare usernames work too
])

for p in profiles:
    print(p["username"], "—", p.get("displayName"), "|", p.get("category"))
```

## What you get per profile

- `username`, `displayName`, `bio`
- `followerCount`, `followingCount`, `postCount`
- `profileUrl`, `website`, `category`
- `otherMetadata` (cake day, trophies, Reddit Premium, …)

## Field selection

Only pull what you need (faster, cleaner output):

```python
profiles = client.scrape(
    ["spez", "kn0thing"],
    fields=["username", "displayName", "bio", "category"],
)
```

Valid fields: `username`, `displayName`, `bio`, `followers`, `following`,
`posts`, `profileUrl`, `website`, `category`, `metadata`.

## Single profile

```python
rec = client.scrape_one("kn0thing")
print(rec["displayName"])  # Alexis Ohanian Sr.
```

## Filters

```python
profiles = client.scrape(usernames)

client.filter_successful(profiles)               # drop failed lookups
client.filter_with_website(profiles)             # only profiles with a website
client.filter_with_bio(profiles)                 # only profiles with a bio
client.filter_by_category(profiles, "social")    # category contains "social"
```

## Cost

```python
client.estimate_cost(1000)   # 2.0  -> $2 per 1,000 profiles ($0.002 each)
```

You are billed only for profiles that scrape successfully.

## Configuration

```python
client = RedditScraperClient(
    api_token="apify_api_xxxxxx",
    timeout=900,        # max seconds to wait for the run
    poll_interval=3.0,  # seconds between status polls
)

profiles = client.scrape(
    usernames,
    max_concurrency=5,        # parallel requests (1-20)
    timeout_per_profile=90,   # seconds per profile (30-300)
    max_retries=3,            # retries on transient failure (0-5)
)
```

## Errors

```python
from reddit_scraper import (
    RedditScraperError, AuthenticationError, ActorRunError, ActorTimeoutError,
)
```

## Resources

- [Reddit Profile Scraper actor on Apify](https://apify.com/apivault_labs/reddit-scraper)
- [All actors by ApiVault Labs](https://apify.com/apivault_labs)
- Prefer no-code? Use the [n8n community node](https://www.npmjs.com/package/n8n-nodes-apivault-reddit)

## License

[MIT](LICENSE)

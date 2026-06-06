# Changelog

## 0.1.0 — 2026-06-06

- Initial release.
- `RedditScraperClient` with `scrape()` and `scrape_one()`.
- Accepts bare usernames or any Reddit profile URL (`/user/` and `/u/`).
- Field selection (`fields=[...]`), concurrency, timeout and retry controls.
- Filters: `filter_successful`, `filter_with_website`, `filter_with_bio`,
  `filter_by_category`.
- `estimate_cost()` helper ($0.002 / profile).
- Wraps the `apivault_labs/reddit-scraper` Apify actor.

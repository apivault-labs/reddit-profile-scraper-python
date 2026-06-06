# Contributing

Thanks for your interest in improving the Reddit Profile Scraper Python SDK!

## Development setup

```bash
git clone https://github.com/apivault-labs/reddit-profile-scraper-python.git
cd reddit-profile-scraper-python
pip install -e .
export APIFY_API_TOKEN=apify_api_xxxxxx
python examples/quickstart.py
```

## Guidelines

- Keep the public API small and stable.
- Match the existing code style (type hints, docstrings).
- Run `python -m py_compile reddit_scraper/*.py examples/*.py` before opening a PR.
- Open an issue first for larger changes.

## Reporting bugs

Open an issue with a minimal reproduction (input, expected vs actual output).
Do not include your Apify API token in issues or PRs.

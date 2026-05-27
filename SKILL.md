---
name: github-trending-crawler
description: Use when needing to scrape GitHub trending repositories, analyze open-source project popularity, or monitor developer ecosystem trends. Handles web scraping, data parsing, and trend analysis.
---

# GitHub Trending Crawler

## Overview

A Python-based web scraper for extracting and analyzing GitHub trending repositories. Provides structured data collection with ethical scraping practices.

**Core Principle:** Respectful data collection with proper rate limiting and error handling.

## When to Use

- Monitor weekly/monthly GitHub trending projects
- Analyze open-source ecosystem trends
- Research popular repositories for specific languages
- Track developer tool adoption patterns
- Study project popularity metrics

## Quick Reference

| Task | Command |
|------|---------|
| Run crawler | `python github_trending_crawler.py` |
| Install dependencies | `pip install -r requirements.txt` |
| View results | Check generated JSON file |

## Implementation

### Core Components

```python
# Main crawler class structure
class GitHubTrendingCrawler:
    def __init__(self):
        self.base_url = "https://github.com/trending"
        self.session = requests.Session()
        self.headers = {...}  # Browser-like headers

    def fetch_trending(self, since="weekly", language=None):
        """Fetch trending page with error handling"""
        ...

    def parse_trending_page(self, html_content):
        """Parse HTML and extract repository data"""
        ...

    def extract_repo_info(self, article):
        """Extract individual repo details"""
        ...
```

### Data Fields Extracted

- Repository name and URL
- Description
- Programming language
- Total stars
- Weekly star growth
- Fork count

## Common Mistakes

### 1. Aggressive Scraping
**Problem:** Sending too many requests too quickly
**Fix:** Implement delays between requests (1-3 seconds)

### 2. Ignoring robots.txt
**Problem:** Violating GitHub's crawling policies
**Fix:** Always check and respect robots.txt

### 3. Missing Error Handling
**Problem:** Crashing on network errors or page changes
**Fix:** Implement try-except blocks and fallback logic

### 4. Hardcoded Selectors
**Problem:** Breaking when GitHub updates their HTML
**Fix:** Use flexible selectors and regular expressions

## Best Practices

### Rate Limiting
```python
import time
import random

# Add random delays between requests
time.sleep(random.uniform(1, 3))
```

### User-Agent Headers
```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
}
```

### Error Recovery
```python
try:
    response = self.session.get(url, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Request failed: {e}")
    return []
```

## Legal and Ethical Considerations

### Compliance Checklist

- [ ] Review GitHub's Terms of Service
- [ ] Check robots.txt compliance
- [ ] Implement rate limiting (max 1 request/second)
- [ ] Add proper User-Agent identification
- [ ] Don't overload GitHub's servers
- [ ] Respect data usage restrictions
- [ ] Consider using GitHub API instead

### GitHub API Alternative

For production use, consider the official GitHub API:
```bash
# Using gh CLI
gh api "/search/repositories?q=stars:>1000&sort=stars&order=desc"
```

**Benefits:**
- Official support
- Better rate limits
- Structured JSON responses
- No HTML parsing needed

## Output Format

```json
{
  "name": "owner/repo",
  "url": "https://github.com/owner/repo",
  "description": "Project description",
  "language": "Python",
  "stars": 12345,
  "forks": 678
}
```

## Troubleshooting

### Issue: Getting 403 Forbidden
**Cause:** GitHub blocking automated requests
**Solution:** Add proper headers and reduce request frequency

### Issue: Empty Results
**Cause:** HTML structure changed
**Solution:** Update CSS selectors in parser

### Issue: Connection Timeout
**Cause:** Network issues or GitHub blocking
**Solution:** Implement retry logic with exponential backoff

## Extension Points

- Add database storage (SQLite/PostgreSQL)
- Implement historical trend tracking
- Add visualization (charts/graphs)
- Support multiple time ranges
- Export to CSV/Excel format

## Related Tools

- `gh` CLI - Official GitHub command-line tool
- `PyGithub` - Python GitHub API wrapper
- `BeautifulSoup` - HTML parsing library
- `Scrapy` - Full-featured web scraping framework
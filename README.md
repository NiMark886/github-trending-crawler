# GitHub Trending Crawler

> ⚠️ **免责声明**：本项目仅供学习交流使用，使用者需自行承担使用风险。详见 [免责声明](免责声明.md)

A Python-based web scraper for extracting and analyzing GitHub trending repositories with ethical scraping practices.

## Features

- 📊 Fetch **daily/weekly/monthly** trending repositories
- 🔍 **Search repositories** by name, keyword, or topic
- 📈 Built-in trend analysis
- 💾 JSON export functionality
- ⏱️ Rate limiting and respectful scraping
- 🛡️ Error handling and retry logic
- ⚡ **Multi-threaded concurrent downloads**
- 📥 Download repository ZIP archives
- 🔄 Resume interrupted downloads
- 📊 Real-time progress tracking with speed statistics
- 📝 **Logging system** with colored output and file rotation
- 🔄 **Proxy support** with health checking and rotation
- 💾 **SQLite database** for data persistence and history tracking
- 🎨 **Rich terminal output** with beautiful tables and progress bars
- 📊 **Data visualization** with charts and graphs
- 🐳 **Docker support** for easy deployment
- ✅ **CI/CD pipeline** with GitHub Actions

## Quick Start

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Usage

#### Basic Crawling

Run the crawler:

```bash
python github_trending_crawler.py
```

The script will:
1. Fetch current weekly trending repositories
2. Display formatted results in the terminal
3. Generate trend analysis
4. Save data to a JSON file

#### Multi-threaded Download

Download repositories with multi-threading:

```bash
# Download from JSON file
python downloader.py github_trending_20260527.json

# Download top 10 with 5 threads
python downloader.py github_trending_20260527.json -n 10 -w 5

# Using CLI
python cli.py all                              # Crawl and download top 10
python cli.py download repos.json -w 10 -n 20  # Download with 10 threads
```

Or use in Python:

```python
from downloader import RepoDownloader

downloader = RepoDownloader(max_workers=5)
downloader.download_with_progress_bar(repositories, output_dir="./downloads")
```

#### Search Repositories (NEW!)

Search GitHub repositories by name, keyword, or topic:

```bash
# Search by keyword
python cli.py search "react"

# Search with limit
python cli.py search "machine learning" -n 30

# Search by language
python cli.py search "web framework" -l python

# Search and save to file
python cli.py search "vue" -o vue_repos.json
```

Output example:
```
#1 facebook/react
   作者: facebook
   描述: The library for web and native user interfaces.
   语言: JavaScript
   ⭐ 星标: 245,287
   🍴 Fork: 51,115
   🔗 链接: https://github.com/facebook/react
```

#### Daily/Weekly/Monthly Trending

Fetch trending repositories for different time ranges:

```bash
# Daily trending (日榜)
python cli.py crawl --since daily

# Weekly trending (周榜)
python cli.py crawl --since weekly

# Monthly trending (月榜)
python cli.py crawl --since monthly

# With language filter
python cli.py crawl --since daily -l python -n 20
```

#### Interactive Selection Download (NEW!)

Interactively select and download repositories with pagination:

```bash
# Search and select download
python cli.py select search "react"

# Trending and select download
python cli.py select trending

# Daily trending and select
python cli.py select trending -s daily

# With language filter
python cli.py select search "vue" -l javascript -n 30
```

**Interactive Commands:**
- `1,3,5` - Select multiple repositories
- `1-5` - Select range
- `all` - Select all on current page
- `n` / `next` - Next page
- `p` / `prev` - Previous page
- `done` - Finish selection
- `quit` - Exit

## Output Format

The crawler generates a JSON file with the following structure:

```json
[
  {
    "name": "owner/repo",
    "url": "https://github.com/owner/repo",
    "description": "Project description",
    "language": "Python",
    "stars": 12345,
    "weekly_stars": 678,
    "forks": 901,
    "crawled_at": "2026-05-27T16:31:42.123456"
  }
]
```

## Multi-threaded Download

### Features

- **Concurrent Downloads**: Download multiple repositories simultaneously
- **Progress Tracking**: Real-time progress bar with speed statistics
- **Auto Retry**: Automatic retry with exponential backoff
- **Resume Support**: Skip already downloaded files
- **Configurable**: Adjust thread count, timeout, and retry settings

### Quick Examples

```bash
# Download all trending repos with 5 threads
python cli.py all -w 5

# Download top 20 Python repos
python cli.py crawl -l python -n 20 -o python_repos.json
python cli.py download python_repos.json -w 10

# Download with custom settings
python downloader.py repos.json -o ./my_downloads -w 8 -n 50
```

### Advanced Usage

```python
from downloader import RepoDownloader

# Custom configuration
downloader = RepoDownloader(
    max_workers=10,      # 10 concurrent threads
    timeout=120,         # 2 minute timeout
    retry_count=5,       # Retry 5 times
    chunk_size=16384     # 16KB chunks
)

# Download with progress bar
results = downloader.download_with_progress_bar(
    repositories,
    output_dir="./downloads"
)

# Process results
for result in results:
    if result['success']:
        print(f"✓ {result['repo']}: {result['size'] / 1024 / 1024:.2f} MB")
    else:
        print(f"✗ {result['repo']}: Failed")
```

### Command Line Options

```
python cli.py download <json_file> [options]

Options:
  -o, --output DIR      Output directory (default: ./downloads)
  -w, --workers N       Number of concurrent threads (default: 5)
  -n, --top N           Only download top N repositories
```

## Customization

### Modify Time Range

Edit the `fetch_trending()` call in `main()`:

```python
# Daily trending
repositories = crawler.fetch_trending(since="daily")

# Monthly trending
repositories = crawler.fetch_trending(since="monthly")
```

### Filter by Language

```python
# Python repositories only
repositories = crawler.fetch_trending(since="weekly", language="python")

# JavaScript repositories
repositories = crawler.fetch_trending(since="weekly", language="javascript")
```

### Adjust Rate Limiting

```python
# Initialize with custom rate limit (seconds between requests)
crawler = GitHubTrendingCrawler(rate_limit=2.0)
```

## Important Considerations

### ⚠️ Legal and Ethical Issues

1. **GitHub Terms of Service**
   - Review [GitHub's ToS](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) before using
   - Automated scraping may violate their terms
   - Consider using [GitHub API](https://docs.github.com/en/rest) instead

2. **robots.txt Compliance**
   - Always check [github.com/robots.txt](https://github.com/robots.txt)
   - Respect crawl-delay directives
   - Don't ignore disallowed paths

3. **Rate Limiting**
   - Implement delays between requests (1-3 seconds minimum)
   - Don't overload GitHub's servers
   - Use exponential backoff for retries

4. **Data Usage**
   - Respect copyright and intellectual property
   - Don't republish data without permission
   - Use data for personal/educational purposes only

### 🔧 Technical Considerations

1. **HTML Structure Changes**
   - GitHub may update their page structure
   - CSS selectors may need updating
   - Monitor for parsing errors

2. **Anti-Scraping Measures**
   - GitHub may block automated requests
   - Use proper User-Agent headers
   - Consider rotating IP addresses

3. **Error Handling**
   - Network timeouts
   - Connection errors
   - Invalid HTML responses

### 🛡️ Best Practices

1. **Use GitHub API When Possible**
   ```bash
   # Using gh CLI (recommended)
   gh api "/search/repositories?q=stars:>1000&sort=stars&order=desc"

   # Using curl
   curl -H "Authorization: token YOUR_TOKEN" \
        "https://api.github.com/search/repositories?q=stars:>1000"
   ```

2. **Implement Proper Rate Limiting**
   ```python
   import time
   import random

   time.sleep(random.uniform(1, 3))  # Random delay
   ```

3. **Add Retry Logic**
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential

   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
   def fetch_with_retry(url):
       ...
   ```

4. **Log Your Activity**
   ```python
   import logging

   logging.basicConfig(filename='crawler.log', level=logging.INFO)
   logging.info(f"Fetching: {url}")
   ```

## Alternative Approaches

### 1. GitHub API (Recommended)

```python
import requests

headers = {
    'Authorization': 'token YOUR_GITHUB_TOKEN',
    'Accept': 'application/vnd.github.v3+json'
}

response = requests.get(
    'https://api.github.com/search/repositories',
    headers=headers,
    params={
        'q': 'stars:>1000',
        'sort': 'stars',
        'order': 'desc'
    }
)
```

### 2. GitHub CLI

```bash
# Install GitHub CLI
# https://cli.github.com/

# Search trending repositories
gh api "/search/repositories?q=stars:>1000&sort=stars&order=desc"
```

### 3. Official GitHub Trending API

GitHub doesn't provide an official trending API, but you can:
- Use the search API with star count filters
- Monitor repository star growth over time
- Use third-party services like [ossinsight.io](https://ossinsight.io/)

## Troubleshooting

### Issue: Getting 403 Forbidden

**Cause:** GitHub blocking automated requests

**Solution:**
- Add proper headers
- Reduce request frequency
- Use a VPN or proxy
- Switch to GitHub API

### Issue: Empty Results

**Cause:** HTML structure changed

**Solution:**
- Update CSS selectors in parser
- Check GitHub's current page structure
- Enable debug logging

### Issue: Connection Timeout

**Cause:** Network issues

**Solution:**
- Check internet connection
- Implement retry logic
- Increase timeout value

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Guidelines

1. Follow PEP 8 style guide
2. Add docstrings to new functions
3. Include error handling
4. Update README if needed
5. Test your changes

## License

This project is for educational purposes only. Use responsibly and in compliance with GitHub's Terms of Service.

## Disclaimer

This tool is provided for educational and research purposes only. The authors are not responsible for any misuse of this tool. Always:

1. Review and comply with GitHub's Terms of Service
2. Respect rate limits and robots.txt
3. Use data ethically and legally
4. Consider using official APIs when available

## Resources

- [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [GitHub CLI Documentation](https://cli.github.com/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Documentation](https://docs.python-requests.org/)

## Contact

If you have questions or suggestions, please open an issue in this repository.
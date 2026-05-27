#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending Crawler
A respectful web scraper for GitHub trending repositories.

Features:
- Weekly/daily/monthly trending
- Language filtering
- JSON export
- Rate limiting
- Error handling

Usage:
    python github_trending_crawler.py

Requirements:
    pip install requests beautifulsoup4 lxml

Legal Notice:
    This tool is for educational purposes only.
    Always respect GitHub's Terms of Service and robots.txt.
    Consider using GitHub API for production use.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from datetime import datetime
from typing import List, Dict, Optional


class GitHubTrendingCrawler:
    """Crawler for GitHub trending repositories with ethical scraping practices."""

    def __init__(self, rate_limit: float = 1.0, token: Optional[str] = None):
        """
        Initialize the crawler.

        Args:
            rate_limit: Minimum seconds between requests (default: 1.0)
            token: GitHub personal access token (optional, for higher API rate limits)
        """
        self.base_url = "https://github.com/trending"
        self.rate_limit = rate_limit
        self.last_request_time = 0

        # Browser-like headers to avoid detection
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Store token for API calls
        self.token = token

    def _respect_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed + random.uniform(0.1, 0.5)
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def fetch_trending(
        self,
        since: str = "weekly",
        language: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch GitHub trending repositories.
        Uses GitHub API (works without proxy) with web scraping as fallback.

        Args:
            since: Time range - 'daily', 'weekly', or 'monthly'
            language: Programming language filter (e.g., 'python', 'javascript')

        Returns:
            List of repository dictionaries
        """
        # Try API first (more reliable, works behind firewalls)
        repos = self._fetch_trending_via_api(since, language)
        if repos:
            return repos

        # Fallback to web scraping
        print("API failed, trying web scraping...")
        return self._fetch_trending_via_web(since, language)

    def _fetch_trending_via_api(
        self,
        since: str = "weekly",
        language: Optional[str] = None
    ) -> List[Dict]:
        """Fetch trending repos using GitHub Search API."""
        from datetime import datetime, timedelta

        # Map time range to date offset
        days_map = {"daily": 1, "weekly": 7, "monthly": 30}
        days = days_map.get(since, 7)
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Build search query
        query = f"stars:>100 pushed:>{since_date}"
        if language:
            query += f" language:{language}"

        # Respect rate limiting
        self._respect_rate_limit()

        try:
            print(f"Fetching via API: {query}")
            api_url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": 30
            }

            # Use token if available for higher rate limits
            headers = {}
            if self.token:
                headers["Authorization"] = f"token {self.token}"

            response = self.session.get(api_url, params=params, timeout=15, headers=headers)

            if response.status_code == 403:
                print("API rate limit exceeded (403). Use a GitHub token for higher limits.")
                return []
            if response.status_code != 200:
                print(f"API returned status {response.status_code}")
                return []

            # Print rate limit info
            remaining = response.headers.get("X-RateLimit-Remaining", "?")
            limit = response.headers.get("X-RateLimit-Limit", "?")
            print(f"API rate limit: {remaining}/{limit}")

            data = response.json()
            items = data.get("items", [])

            if not items:
                return []

            repositories = []
            for item in items:
                repo_info = {
                    "name": item.get("full_name", ""),
                    "url": item.get("html_url", ""),
                    "description": item.get("description") or "No description",
                    "language": item.get("language") or "Unknown",
                    "stars": item.get("stargazers_count", 0),
                    "forks": item.get("forks_count", 0),
                    "weekly_stars": 0,  # API doesn't provide this
                    "crawled_at": datetime.now().isoformat()
                }
                repositories.append(repo_info)

            print(f"API returned {len(repositories)} repositories")
            return repositories

        except Exception as e:
            print(f"API request failed: {e}")
            return []

    def _fetch_trending_via_web(
        self,
        since: str = "weekly",
        language: Optional[str] = None
    ) -> List[Dict]:
        """Fetch trending repos by scraping GitHub web page (fallback)."""
        # Build URL
        url = f"{self.base_url}?since={since}"
        if language:
            url = f"{self.base_url}/{language}?since={since}"

        # Respect rate limiting
        self._respect_rate_limit()

        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Check for login redirect
            if "Sign in to GitHub" in response.text:
                print("Warning: GitHub may require authentication")
                return []

            return self._parse_trending_page(response.text)

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return []

    def _parse_trending_page(self, html_content: str) -> List[Dict]:
        """
        Parse GitHub trending page HTML.

        Args:
            html_content: Raw HTML content

        Returns:
            List of parsed repository data
        """
        soup = BeautifulSoup(html_content, 'lxml')
        repositories = []

        # Find all repository articles
        repo_articles = soup.find_all('article', class_='Box-row')

        for article in repo_articles:
            try:
                repo_info = self._extract_repo_info(article)
                if repo_info:
                    repositories.append(repo_info)
            except Exception as e:
                print(f"Error parsing repository: {e}")
                continue

        return repositories

    def _extract_repo_info(self, article) -> Optional[Dict]:
        """
        Extract repository information from article element.

        Args:
            article: BeautifulSoup Tag object

        Returns:
            Repository dictionary or None if parsing fails
        """
        repo_info = {}

        # Extract repository name and URL
        h2_tag = article.find('h2', class_='h3')
        if not h2_tag:
            return None

        link_tag = h2_tag.find('a')
        if not link_tag:
            return None

        repo_name = link_tag.get_text(strip=True).replace('\n', '').replace(' ', '')
        repo_url = "https://github.com" + link_tag.get('href', '')

        repo_info['name'] = repo_name
        repo_info['url'] = repo_url

        # Extract description
        desc_tag = article.find('p', class_='col-9')
        repo_info['description'] = desc_tag.get_text(strip=True) if desc_tag else "No description"

        # Extract programming language
        lang_tag = article.find('span', attrs={'itemprop': 'programmingLanguage'})
        repo_info['language'] = lang_tag.get_text(strip=True) if lang_tag else "Unknown"

        # Extract star count
        star_links = article.find_all('a', class_='Link--muted')
        for link in star_links:
            href = link.get('href', '')
            if '/stargazers' in href:
                star_text = link.get_text(strip=True).replace(',', '')
                try:
                    repo_info['stars'] = self._parse_number(star_text)
                except ValueError:
                    repo_info['stars'] = 0
                break

        # Extract weekly star growth
        weekly_stars_tag = article.find('span', class_='d-inline-block')
        if weekly_stars_tag:
            weekly_text = weekly_stars_tag.get_text(strip=True)
            numbers = re.findall(r'[\d,]+', weekly_text)
            if numbers:
                try:
                    repo_info['weekly_stars'] = self._parse_number(numbers[0])
                except ValueError:
                    repo_info['weekly_stars'] = 0

        # Extract fork count
        for link in star_links:
            href = link.get('href', '')
            if '/forks' in href:
                fork_text = link.get_text(strip=True).replace(',', '')
                try:
                    repo_info['forks'] = self._parse_number(fork_text)
                except ValueError:
                    repo_info['forks'] = 0
                break

        # Add metadata
        repo_info['crawled_at'] = datetime.now().isoformat()

        return repo_info

    def _parse_number(self, text: str) -> int:
        """
        Parse number text with K/M suffixes.

        Args:
            text: Number text (e.g., '1.2K', '3M', '1234')

        Returns:
            Integer value
        """
        text = text.strip().replace(',', '')

        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        else:
            return int(text)

    def save_to_json(
        self,
        data: List[Dict],
        filename: Optional[str] = None
    ) -> str:
        """
        Save crawled data to JSON file.

        Args:
            data: List of repository dictionaries
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"github_trending_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Data saved to: {filename}")
        return filename

    def print_trending(self, repositories: List[Dict]):
        """
        Print formatted trending results.

        Args:
            repositories: List of repository dictionaries
        """
        print("\n" + "=" * 80)
        print(f"GitHub Trending Repositories")
        print(f"Retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total: {len(repositories)} repositories")
        print("=" * 80)

        for i, repo in enumerate(repositories, 1):
            print(f"\n#{i} {repo.get('name', 'Unknown')}")
            print(f"   Description: {repo.get('description', 'No description')}")
            print(f"   Language: {repo.get('language', 'Unknown')}")
            print(f"   Stars: {repo.get('stars', 0):,}")
            print(f"   Weekly Growth: +{repo.get('weekly_stars', 0):,}")
            print(f"   Forks: {repo.get('forks', 0):,}")
            print(f"   URL: {repo.get('url', '')}")
            print("-" * 80)

    def analyze_trends(self, repositories: List[Dict]) -> Dict:
        """
        Analyze trending data and generate insights.

        Args:
            repositories: List of repository dictionaries

        Returns:
            Analysis dictionary with statistics
        """
        if not repositories:
            return {}

        analysis = {
            'total_repos': len(repositories),
            'total_stars': sum(r.get('stars', 0) for r in repositories),
            'total_weekly_growth': sum(r.get('weekly_stars', 0) for r in repositories),
            'languages': {},
            'top_by_stars': sorted(
                repositories,
                key=lambda x: x.get('stars', 0),
                reverse=True
            )[:5],
            'top_by_weekly_growth': sorted(
                repositories,
                key=lambda x: x.get('weekly_stars', 0),
                reverse=True
            )[:5],
        }

        # Count languages
        for repo in repositories:
            lang = repo.get('language', 'Unknown')
            analysis['languages'][lang] = analysis['languages'].get(lang, 0) + 1

        # Sort languages by count
        analysis['languages'] = dict(
            sorted(
                analysis['languages'].items(),
                key=lambda x: x[1],
                reverse=True
            )
        )

        return analysis


def main():
    """Main entry point for the crawler."""
    print("=" * 80)
    print("GitHub Trending Crawler")
    print("=" * 80)
    print("\nIMPORTANT: This tool is for educational purposes only.")
    print("Always respect GitHub's Terms of Service.")
    print("Consider using GitHub API for production use.\n")

    # Initialize crawler with rate limiting
    crawler = GitHubTrendingCrawler(rate_limit=2.0)

    print("Fetching weekly trending repositories...\n")

    # Fetch trending repositories
    repositories = crawler.fetch_trending(since="weekly")

    if not repositories:
        print("No repositories found. Possible causes:")
        print("  1. Network connection issues")
        print("  2. GitHub page structure changed")
        print("  3. GitHub blocking automated requests")
        print("\nTroubleshooting:")
        print("  - Check your internet connection")
        print("  - Try using a VPN or proxy")
        print("  - Consider using GitHub API instead")
        return

    # Display results
    crawler.print_trending(repositories)

    # Analyze trends
    analysis = crawler.analyze_trends(repositories)

    print("\n" + "=" * 80)
    print("TREND ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Repositories: {analysis.get('total_repos', 0)}")
    print(f"Total Stars: {analysis.get('total_stars', 0):,}")
    print(f"Total Weekly Growth: +{analysis.get('total_weekly_growth', 0):,}")

    print("\nLanguage Distribution:")
    for lang, count in analysis.get('languages', {}).items():
        print(f"  {lang}: {count} repositories")

    print("\nTop 5 by Total Stars:")
    for i, repo in enumerate(analysis.get('top_by_stars', []), 1):
        print(f"  {i}. {repo['name']} ({repo.get('stars', 0):,} stars)")

    print("\nTop 5 by Weekly Growth:")
    for i, repo in enumerate(analysis.get('top_by_weekly_growth', []), 1):
        print(f"  {i}. {repo['name']} (+{repo.get('weekly_stars', 0):,} this week)")

    # Save to JSON
    filename = crawler.save_to_json(repositories)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Retrieved {len(repositories)} trending repositories")
    print(f"✓ Data saved to: {filename}")
    print(f"✓ Analysis complete")

    print("\nNext Steps:")
    print("  - Review the JSON file for detailed data")
    print("  - Use data for trend analysis or research")
    print("  - Consider setting up scheduled runs for tracking")


if __name__ == "__main__":
    main()
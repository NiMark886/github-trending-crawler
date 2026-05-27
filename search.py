#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Repository Search Module

Features:
- Search repositories by name
- Display stars, author, description
- Rate limiting
- Pagination support

Usage:
    from search import RepoSearcher

    searcher = RepoSearcher()
    results = searcher.search("react", limit=20)
"""

import requests
import time
import random
from typing import List, Dict, Optional


class RepoSearcher:
    """GitHub repository searcher with rate limiting."""

    def __init__(self, token: Optional[str] = None, rate_limit: float = 2.0):
        """
        Initialize searcher.

        Args:
            token: GitHub personal access token (optional, for higher rate limits)
            rate_limit: Minimum seconds between requests
        """
        self.base_url = "https://api.github.com/search/repositories"
        self.rate_limit = rate_limit
        self.last_request_time = 0

        # Headers
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Trending-Crawler"
        }

        # Add token if provided
        if token:
            self.headers["Authorization"] = f"token {token}"

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _respect_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed + random.uniform(0.1, 0.5)
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def search(
        self,
        query: str,
        limit: int = 20,
        sort: str = "stars",
        order: str = "desc",
        language: Optional[str] = None
    ) -> List[Dict]:
        """
        Search repositories by name or keyword.

        Args:
            query: Search query (repository name, keyword, etc.)
            limit: Maximum number of results (default: 20)
            sort: Sort by (stars, forks, updated)
            order: Sort order (asc, desc)
            language: Filter by programming language

        Returns:
            List of repository dictionaries
        """
        # Build search query
        search_query = query
        if language:
            search_query += f" language:{language}"

        # Respect rate limiting
        self._respect_rate_limit()

        try:
            print(f"搜索: {query}...")

            params = {
                "q": search_query,
                "sort": sort,
                "order": order,
                "per_page": min(limit, 100)  # GitHub API max 100 per page
            }

            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])

            # Parse results
            results = []
            for item in items[:limit]:
                repo = self._parse_repo(item)
                if repo:
                    results.append(repo)

            print(f"✓ 找到 {len(results)} 个仓库")
            return results

        except requests.RequestException as e:
            print(f"搜索失败: {e}")
            return []

    def _parse_repo(self, item: Dict) -> Optional[Dict]:
        """
        Parse repository data from API response.

        Args:
            item: Repository data from GitHub API

        Returns:
            Parsed repository dictionary
        """
        try:
            # Extract owner info
            owner = item.get("owner", {})
            owner_login = owner.get("login", "Unknown")
            owner_url = owner.get("html_url", "")

            # Extract repository info
            repo = {
                "name": item.get("full_name", ""),
                "owner": owner_login,
                "owner_url": owner_url,
                "url": item.get("html_url", ""),
                "description": item.get("description") or "无描述",
                "language": item.get("language") or "Unknown",
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "watchers": item.get("watchers_count", 0),
                "open_issues": item.get("open_issues_count", 0),
                "created_at": item.get("created_at", ""),
                "updated_at": item.get("updated_at", ""),
                "topics": item.get("topics", []),
                "license": item.get("license", {}).get("name") if item.get("license") else None,
                "archived": item.get("archived", False),
                "disabled": item.get("disabled", False),
            }

            return repo

        except Exception as e:
            print(f"解析仓库数据失败: {e}")
            return None

    def search_by_name(
        self,
        name: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search repositories by exact name.

        Args:
            name: Repository name (e.g., "react", "vue")
            limit: Maximum number of results

        Returns:
            List of matching repositories
        """
        return self.search(name, limit=limit, sort="stars", order="desc")

    def search_by_topic(
        self,
        topic: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search repositories by topic.

        Args:
            topic: Topic name (e.g., "machine-learning", "web-framework")
            limit: Maximum number of results

        Returns:
            List of matching repositories
        """
        query = f"topic:{topic}"
        return self.search(query, limit=limit, sort="stars", order="desc")

    def search_by_language(
        self,
        language: str,
        limit: int = 20,
        min_stars: int = 1000
    ) -> List[Dict]:
        """
        Search popular repositories by language.

        Args:
            language: Programming language (e.g., "python", "javascript")
            limit: Maximum number of results
            min_stars: Minimum star count

        Returns:
            List of matching repositories
        """
        query = f"language:{language} stars:>={min_stars}"
        return self.search(query, limit=limit, sort="stars", order="desc")

    def print_results(self, results: List[Dict]):
        """
        Print search results in a formatted way.

        Args:
            results: List of repository dictionaries
        """
        if not results:
            print("未找到任何仓库")
            return

        print(f"\n{'='*80}")
        print(f"搜索结果 ({len(results)} 个仓库)")
        print(f"{'='*80}")

        for i, repo in enumerate(results, 1):
            print(f"\n#{i} {repo['name']}")
            print(f"   作者: {repo['owner']}")
            print(f"   描述: {repo['description'][:80]}{'...' if len(repo['description']) > 80 else ''}")
            print(f"   语言: {repo['language']}")
            print(f"   ⭐ 星标: {repo['stars']:,}")
            print(f"   🍴 Fork: {repo['forks']:,}")
            print(f"   👁️  Watch: {repo['watchers']:,}")
            print(f"   🔗 链接: {repo['url']}")
            print("-" * 80)

    def to_json(self, results: List[Dict], filename: str):
        """
        Save search results to JSON file.

        Args:
            results: List of repository dictionaries
            filename: Output filename
        """
        import json

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"结果已保存到: {filename}")


def search_repos(
    query: str,
    limit: int = 20,
    token: Optional[str] = None
) -> List[Dict]:
    """
    Convenience function to search repositories.

    Args:
        query: Search query
        limit: Maximum results
        token: GitHub token (optional)

    Returns:
        List of repositories
    """
    searcher = RepoSearcher(token=token)
    return searcher.search(query, limit=limit)


def main():
    """CLI for repository search."""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="GitHub Repository Search"
    )
    parser.add_argument(
        "query",
        help="Search query (repository name, keyword)"
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=20,
        help="Maximum results (default: 20)"
    )
    parser.add_argument(
        "-l", "--language",
        help="Filter by language"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save results to JSON file"
    )
    parser.add_argument(
        "-t", "--token",
        help="GitHub token (for higher rate limits)"
    )

    args = parser.parse_args()

    # Get token from environment if not provided
    token = args.token or os.environ.get("GITHUB_TOKEN")

    # Search
    searcher = RepoSearcher(token=token)
    results = searcher.search(
        args.query,
        limit=args.limit,
        language=args.language
    )

    # Display results
    searcher.print_results(results)

    # Save to file if requested
    if args.output:
        searcher.to_json(results, args.output)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
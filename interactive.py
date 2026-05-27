#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Repository Selector

Features:
- Display repositories with numbers
- User can select which to download
- Pagination for large lists
- Multiple selection support
- Download selected repositories
- Custom download directory selection

Usage:
    from interactive import InteractiveSelector

    selector = InteractiveSelector()
    selector.select_and_download(repositories)
"""

import os
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from downloader import RepoDownloader
from config import ConfigManager, select_directory


class InteractiveSelector:
    """Interactive repository selector with pagination."""

    def __init__(self, page_size: int = 10):
        """
        Initialize selector.

        Args:
            page_size: Number of items per page (default: 10)
        """
        self.page_size = page_size
        self.current_page = 0
        self.repositories = []

    def display_repos(
        self,
        repositories: List[Dict],
        page: int = 0,
        show_full: bool = False
    ) -> Tuple[int, int]:
        """
        Display repositories with numbers.

        Args:
            repositories: List of repository dictionaries
            page: Current page number (0-based)
            show_full: Show full details or compact view

        Returns:
            Tuple of (start_index, end_index) for current page
        """
        if not repositories:
            print("❌ 没有可显示的仓库")
            return (0, 0)

        total = len(repositories)
        total_pages = math.ceil(total / self.page_size)

        # Validate page
        page = max(0, min(page, total_pages - 1))

        # Calculate range
        start = page * self.page_size
        end = min(start + self.page_size, total)

        # Display header
        print(f"\n{'='*90}")
        print(f"📦 仓库列表 (第 {page + 1}/{total_pages} 页，共 {total} 个)")
        print(f"{'='*90}")

        # Display repositories
        for i in range(start, end):
            repo = repositories[i]
            num = i + 1

            if show_full:
                self._display_full(repo, num)
            else:
                self._display_compact(repo, num)

        # Display pagination info
        print(f"{'─'*90}")
        print(f"📄 第 {page + 1}/{total_pages} 页 | 显示 {start + 1}-{end} / 共 {total} 个")

        return (start, end)

    def _display_compact(self, repo: Dict, num: int):
        """Display compact repository info."""
        name = repo.get('name', repo.get('owner', 'Unknown'))
        owner = repo.get('owner', '')
        stars = repo.get('stars', 0)
        language = repo.get('language', 'Unknown')
        desc = repo.get('description', '无描述')[:50]

        # Format stars
        if stars >= 1000:
            stars_str = f"{stars/1000:.1f}k"
        else:
            stars_str = str(stars)

        print(f"  [{num:2d}] {name}")
        print(f"       ⭐ {stars_str:>6} | {language:<12} | {desc}")

    def _display_full(self, repo: Dict, num: int):
        """Display full repository info."""
        print(f"\n  [{num:2d}] {repo.get('name', 'Unknown')}")
        print(f"       作者: {repo.get('owner', 'Unknown')}")
        print(f"       描述: {repo.get('description', '无描述')[:60]}")
        print(f"       语言: {repo.get('language', 'Unknown')}")
        print(f"       ⭐ 星标: {repo.get('stars', 0):,}")
        print(f"       🍴 Fork: {repo.get('forks', 0):,}")
        print(f"       🔗 链接: {repo.get('url', '')}")

    def get_user_selection(
        self,
        repositories: List[Dict],
        page: int = 0
    ) -> List[int]:
        """
        Get user selection for repositories.

        Args:
            repositories: List of repository dictionaries
            page: Current page number

        Returns:
            List of selected indices (0-based)
        """
        total = len(repositories)
        total_pages = math.ceil(total / self.page_size)

        print(f"\n{'─'*90}")
        print("📝 选择操作:")
        print("   • 输入数字选择仓库 (如: 1,3,5)")
        print("   • 输入 'all' 选择当前页所有仓库")
        print("   • 输入 'n' 或 'next' 下一页")
        print("   • 输入 'p' 或 'prev' 上一页")
        print("   • 输入 'f' 或 'first' 第一页")
        print("   • 输入 'l' 或 'last' 最后一页")
        print("   • 输入 'q' 或 'quit' 退出")
        print("   • 输入 'd' 或 'done' 完成选择")
        print(f"{'─'*90}")

        selected = set()

        while True:
            try:
                user_input = input("\n请输入选择: ").strip().lower()

                if not user_input:
                    continue

                # Quit
                if user_input in ['q', 'quit', 'exit']:
                    print("👋 已退出选择")
                    return []

                # Done
                if user_input in ['d', 'done', 'finish']:
                    if selected:
                        print(f"✓ 已选择 {len(selected)} 个仓库")
                        return sorted(list(selected))
                    else:
                        print("⚠️ 未选择任何仓库")
                        continue

                # Navigation
                if user_input in ['n', 'next']:
                    if page < total_pages - 1:
                        return ['next', page + 1]
                    else:
                        print("已经是最后一页了")
                        continue

                if user_input in ['p', 'prev']:
                    if page > 0:
                        return ['prev', page - 1]
                    else:
                        print("已经是第一页了")
                        continue

                if user_input in ['f', 'first']:
                    return ['first', 0]

                if user_input in ['l', 'last']:
                    return ['last', total_pages - 1]

                # Select all on current page
                if user_input in ['a', 'all']:
                    start = page * self.page_size
                    end = min(start + self.page_size, total)
                    for i in range(start, end):
                        selected.add(i)
                    print(f"✓ 已选择当前页所有 {end - start} 个仓库")
                    continue

                # Parse numbers
                if ',' in user_input:
                    # Multiple selection: 1,3,5
                    parts = user_input.split(',')
                    for part in parts:
                        part = part.strip()
                        if '-' in part:
                            # Range: 1-5
                            start_str, end_str = part.split('-')
                            start_idx = int(start_str) - 1
                            end_idx = int(end_str) - 1
                            for i in range(start_idx, end_idx + 1):
                                if 0 <= i < total:
                                    selected.add(i)
                        else:
                            idx = int(part) - 1
                            if 0 <= idx < total:
                                selected.add(idx)
                    print(f"✓ 已选择 {len(selected)} 个仓库")
                elif '-' in user_input and not user_input.startswith('-'):
                    # Range: 1-5
                    start_str, end_str = user_input.split('-')
                    start_idx = int(start_str) - 1
                    end_idx = int(end_str) - 1
                    for i in range(start_idx, end_idx + 1):
                        if 0 <= i < total:
                            selected.add(i)
                    print(f"✓ 已选择 {len(selected)} 个仓库")
                else:
                    # Single selection
                    idx = int(user_input) - 1
                    if 0 <= idx < total:
                        if idx in selected:
                            selected.remove(idx)
                            print(f"✓ 取消选择: {repositories[idx].get('name', 'Unknown')}")
                        else:
                            selected.add(idx)
                            print(f"✓ 已选择: {repositories[idx].get('name', 'Unknown')}")
                    else:
                        print(f"⚠️ 无效编号: {user_input} (1-{total})")

                # Show current selection
                if selected:
                    print(f"\n当前已选择 {len(selected)} 个仓库:")
                    for idx in sorted(selected):
                        repo = repositories[idx]
                        print(f"  • [{idx+1}] {repo.get('name', 'Unknown')}")

            except ValueError:
                print("⚠️ 请输入有效的数字或命令")
            except KeyboardInterrupt:
                print("\n\n👋 已退出选择")
                return []

        return sorted(list(selected))

    def select_from_list(
        self,
        repositories: List[Dict],
        title: str = "选择仓库"
    ) -> List[Dict]:
        """
        Interactive selection from repository list.

        Args:
            repositories: List of repository dictionaries
            title: Display title

        Returns:
            List of selected repositories
        """
        if not repositories:
            print("❌ 没有可选择的仓库")
            return []

        print(f"\n{'='*90}")
        print(f"🎯 {title}")
        print(f"{'='*90}")

        self.repositories = repositories
        self.current_page = 0

        while True:
            # Display current page
            self.display_repos(repositories, self.current_page)

            # Get user selection
            result = self.get_user_selection(repositories, self.current_page)

            # Check if navigation
            if isinstance(result, list) and len(result) > 0:
                if result[0] in ['next', 'prev', 'first', 'last']:
                    self.current_page = result[1]
                    continue

            # Return selection
            if result:
                return [repositories[i] for i in result if i < len(repositories)]
            else:
                return []

    def select_and_download(
        self,
        repositories: List[Dict],
        output_dir: str = None,
        max_workers: int = 5,
        allow_change_dir: bool = True
    ) -> List[Dict]:
        """
        Select repositories and download them.

        Args:
            repositories: List of repository dictionaries
            output_dir: Output directory (None to use default or ask)
            max_workers: Number of download threads
            allow_change_dir: Allow user to change download directory

        Returns:
            List of download results
        """
        # Select repositories
        selected = self.select_from_list(repositories, "选择要下载的仓库")

        if not selected:
            print("❌ 未选择任何仓库")
            return []

        # Get download directory
        config = ConfigManager()

        if output_dir is None:
            output_dir = config.get_download_dir()

        # Allow user to change directory
        if allow_change_dir:
            print(f"\n{'='*90}")
            print(f"📁 下载设置")
            print(f"{'='*90}")
            print(f"当前下载目录: {output_dir}")

            change = input("\n是否修改下载目录? (y/n): ").strip().lower()
            if change in ['y', 'yes', '是']:
                new_dir = select_directory("选择下载目录", output_dir)
                if new_dir:
                    output_dir = new_dir
                    # Save as new default
                    save_default = input("是否保存为默认下载目录? (y/n): ").strip().lower()
                    if save_default in ['y', 'yes', '是']:
                        config.set_download_dir(output_dir)

        # Confirm
        print(f"\n{'='*90}")
        print(f"📋 即将下载 {len(selected)} 个仓库:")
        print(f"{'='*90}")

        for i, repo in enumerate(selected, 1):
            print(f"  {i}. {repo.get('name', 'Unknown')} - ⭐ {repo.get('stars', 0):,}")

        print(f"\n📁 下载目录: {os.path.abspath(output_dir)}")
        print(f"🧵 并发线程: {max_workers}")

        # Ask for confirmation
        confirm = input("\n确认下载? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', '是', '确认']:
            print("❌ 已取消下载")
            return []

        # Download
        print(f"\n🚀 开始下载...")
        downloader = RepoDownloader(max_workers=max_workers)
        results = downloader.download_with_progress_bar(selected, output_dir)

        return results


def interactive_download_from_search(
    query: str,
    limit: int = 30,
    output_dir: str = "./downloads",
    max_workers: int = 5
):
    """
    Search and interactively download repositories.

    Args:
        query: Search query
        limit: Maximum search results
        output_dir: Output directory
        max_workers: Number of download threads
    """
    from search import RepoSearcher

    # Search
    print(f"🔍 搜索: {query}")
    searcher = RepoSearcher()
    repositories = searcher.search(query, limit=limit)

    if not repositories:
        print("❌ 未找到任何仓库")
        return []

    # Interactive selection and download
    selector = InteractiveSelector(page_size=10)
    return selector.select_and_download(repositories, output_dir, max_workers)


def interactive_download_from_trending(
    since: str = "weekly",
    language: Optional[str] = None,
    output_dir: str = "./downloads",
    max_workers: int = 5
):
    """
    Get trending and interactively download repositories.

    Args:
        since: Time range (daily/weekly/monthly)
        language: Language filter
        output_dir: Output directory
        max_workers: Number of download threads
    """
    from github_trending_crawler import GitHubTrendingCrawler

    # Get trending
    print(f"📥 获取 {since} 热榜...")
    crawler = GitHubTrendingCrawler()
    repositories = crawler.fetch_trending(since=since, language=language)

    if not repositories:
        print("❌ 未获取到任何仓库")
        return []

    # Display trending
    crawler.print_trending(repositories)

    # Interactive selection and download
    selector = InteractiveSelector(page_size=10)
    return selector.select_and_download(repositories, output_dir, max_workers)


def main():
    """CLI for interactive download."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive Repository Downloader"
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # Search and download
    search_parser = subparsers.add_parser('search', help='搜索并选择下载')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('-n', '--limit', type=int, default=30, help='最大结果数')
    search_parser.add_argument('-o', '--output', default='./downloads', help='下载目录')
    search_parser.add_argument('-w', '--workers', type=int, default=5, help='并发线程数')

    # Trending and download
    trending_parser = subparsers.add_parser('trending', help='热榜并选择下载')
    trending_parser.add_argument('-s', '--since', choices=['daily', 'weekly', 'monthly'], default='weekly', help='时间范围')
    trending_parser.add_argument('-l', '--language', help='语言过滤')
    trending_parser.add_argument('-o', '--output', default='./downloads', help='下载目录')
    trending_parser.add_argument('-w', '--workers', type=int, default=5, help='并发线程数')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'search':
        interactive_download_from_search(
            query=args.query,
            limit=args.limit,
            output_dir=args.output,
            max_workers=args.workers
        )
    elif args.command == 'trending':
        interactive_download_from_trending(
            since=args.since,
            language=args.language,
            output_dir=args.output,
            max_workers=args.workers
        )

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
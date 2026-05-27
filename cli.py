#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending Crawler CLI

Command-line interface for crawling and downloading GitHub trending repositories.

Usage:
    python cli.py crawl                    # Crawl trending repos
    python cli.py download <json_file>     # Download from JSON file
    python cli.py all                      # Crawl and download top 10
    python cli.py search <query>           # Search repositories
"""

import argparse
import sys
import os
from datetime import datetime

from github_trending_crawler import GitHubTrendingCrawler
from downloader import RepoDownloader, download_trending_repos
from search import RepoSearcher
from interactive import InteractiveSelector, interactive_download_from_search, interactive_download_from_trending
from config import ConfigManager, select_directory


def cmd_crawl(args):
    """Crawl GitHub trending repositories."""
    print("📥 获取 GitHub 热榜...\n")

    crawler = GitHubTrendingCrawler(rate_limit=args.rate_limit)

    # Fetch trending
    repositories = crawler.fetch_trending(
        since=args.since,
        language=args.language
    )

    if not repositories:
        print("❌ 未获取到任何仓库数据")
        return 1

    # Display results
    if args.top:
        repositories = repositories[:args.top]

    crawler.print_trending(repositories)

    # Save to JSON
    if args.output:
        filename = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"github_trending_{timestamp}.json"

    crawler.save_to_json(repositories, filename)

    # Analyze trends
    if args.analyze:
        analysis = crawler.analyze_trends(repositories)
        print(f"\n📊 分析结果:")
        print(f"   总项目数: {analysis.get('total_repos', 0)}")
        print(f"   总星标数: {analysis.get('total_stars', 0):,}")
        print(f"   语言分布: {analysis.get('languages', {})}")

    return 0


def cmd_download(args):
    """Download repositories from JSON file."""
    print(f"📦 从 JSON 文件下载仓库...\n")

    if not os.path.exists(args.json_file):
        print(f"❌ 文件不存在: {args.json_file}")
        return 1

    # Download
    results = download_trending_repos(
        json_file=args.json_file,
        output_dir=args.output,
        max_workers=args.workers,
        top_n=args.top
    )

    # Count results
    success = sum(1 for r in results if r.get('success'))
    failed = len(results) - success

    return 0 if failed == 0 else 1


def cmd_all(args):
    """Crawl and download top repositories."""
    print("🚀 GitHub Trending 爬取 + 下载\n")

    # Step 1: Crawl
    print("=" * 80)
    print("第一步: 获取热榜")
    print("=" * 80)

    crawler = GitHubTrendingCrawler(rate_limit=args.rate_limit)
    repositories = crawler.fetch_trending(
        since=args.since,
        language=args.language
    )

    if not repositories:
        print("❌ 未获取到任何仓库数据")
        return 1

    # Save to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"github_trending_{timestamp}.json"
    crawler.save_to_json(repositories, json_file)

    # Display top repositories
    top_n = args.top or 10
    print(f"\n🏆 本周热门 TOP {top_n}:")
    for i, repo in enumerate(repositories[:top_n], 1):
        print(f"  {i}. {repo['name']} - ⭐ {repo.get('stars', 0):,}")

    # Step 2: Download
    print("\n" + "=" * 80)
    print("第二步: 多线程下载")
    print("=" * 80)

    downloader = RepoDownloader(
        max_workers=args.workers,
        timeout=60,
        retry_count=3
    )

    results = downloader.download_with_progress_bar(
        repositories[:args.top or 10],
        output_dir=args.output
    )

    # Summary
    success = sum(1 for r in results if r.get('success'))
    failed = len(results) - success

    print(f"\n✅ 完成!")
    print(f"   热榜文件: {os.path.abspath(args.json_file or 'github_trending_*.json')}")
    print(f"   下载目录: {os.path.abspath(args.output)}")
    print(f"   成功: {success}, 失败: {failed}")

    return 0


def cmd_search(args):
    """Search repositories by name or keyword."""
    print(f"🔍 搜索仓库: {args.query}\n")

    # Get token from environment if not provided
    token = args.token or os.environ.get("GITHUB_TOKEN")

    # Search
    searcher = RepoSearcher(token=token, rate_limit=args.rate_limit)
    results = searcher.search(
        args.query,
        limit=args.limit,
        language=args.language,
        sort=args.sort,
        order=args.order
    )

    if not results:
        print("❌ 未找到任何仓库")
        return 1

    # Display results
    searcher.print_results(results)

    # Save to file if requested
    if args.output:
        searcher.to_json(results, args.output)

    return 0


def cmd_select(args):
    """Interactive select and download repositories."""
    # Get download directory
    if args.output:
        output_dir = args.output
    else:
        config = ConfigManager()
        output_dir = config.get_download_dir()

    if args.source == 'search':
        if not args.query:
            print("❌ 搜索模式需要提供关键词")
            return 1
        results = interactive_download_from_search(
            query=args.query,
            limit=args.limit,
            output_dir=output_dir,
            max_workers=args.workers
        )
    elif args.source == 'trending':
        results = interactive_download_from_trending(
            since=args.since,
            language=args.language,
            output_dir=output_dir,
            max_workers=args.workers
        )
    else:
        print("❌ 未知来源")
        return 1

    if results:
        success = sum(1 for r in results if r.get('success'))
        failed = len(results) - success
        print(f"\n✅ 下载完成! 成功: {success}, 失败: {failed}")

    return 0


def cmd_config(args):
    """Manage configuration."""
    config = ConfigManager()

    if args.action == 'show':
        config.show()
    elif args.action == 'set-dir':
        if args.path:
            config.set_download_dir(args.path)
        else:
            path = select_directory("选择下载目录", config.get_download_dir())
            if path:
                config.set_download_dir(path)
    elif args.action == 'set-workers':
        config.set_max_workers(args.workers)
        print(f"✓ 并发线程数已设置为: {args.workers}")
    elif args.action == 'set-rate':
        config.set_rate_limit(args.limit)
        print(f"✓ 请求间隔已设置为: {args.limit}s")
    elif args.action == 'reset':
        confirm = input("确认重置配置? (y/n): ").strip().lower()
        if confirm in ['y', 'yes', '是']:
            config.reset()

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub Trending Crawler - 爬取和下载 GitHub 热门仓库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py crawl                           # 获取本周热榜
  python cli.py crawl --since daily --top 20    # 获取每日热榜前20
  python cli.py crawl -l python                 # 获取 Python 热榜
  python cli.py download repos.json             # 从 JSON 下载
  python cli.py download repos.json -w 10 -n 5  # 10线程下载前5个
  python cli.py all                             # 爬取并下载前10个
  python cli.py search react                    # 搜索 react 仓库
  python cli.py search "machine learning" -n 30 # 搜索机器学习仓库
  python cli.py select search react             # 搜索并选择下载
  python cli.py select trending                 # 热榜并选择下载
  python cli.py select trending -s daily        # 日榜并选择下载
  python cli.py config show                     # 显示当前配置
  python cli.py config set-dir ~/Downloads      # 设置下载目录
  python cli.py config set-dir                  # 交互式选择下载目录
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # Crawl command
    crawl_parser = subparsers.add_parser('crawl', help='获取 GitHub 热榜')
    crawl_parser.add_argument(
        '-s', '--since',
        choices=['daily', 'weekly', 'monthly'],
        default='weekly',
        help='时间范围 (默认: weekly)'
    )
    crawl_parser.add_argument(
        '-l', '--language',
        help='编程语言过滤 (例如: python, javascript)'
    )
    crawl_parser.add_argument(
        '-n', '--top',
        type=int,
        help='只显示前 N 个仓库'
    )
    crawl_parser.add_argument(
        '-o', '--output',
        help='输出文件名 (默认: github_trending_<timestamp>.json)'
    )
    crawl_parser.add_argument(
        '-a', '--analyze',
        action='store_true',
        help='显示趋势分析'
    )
    crawl_parser.add_argument(
        '-r', '--rate-limit',
        type=float,
        default=2.0,
        help='请求间隔秒数 (默认: 2.0)'
    )
    crawl_parser.set_defaults(func=cmd_crawl)

    # Download command
    download_parser = subparsers.add_parser('download', help='从 JSON 文件下载仓库')
    download_parser.add_argument(
        'json_file',
        help='JSON 文件路径'
    )
    download_parser.add_argument(
        '-o', '--output',
        default='./downloads',
        help='输出目录 (默认: ./downloads)'
    )
    download_parser.add_argument(
        '-w', '--workers',
        type=int,
        default=5,
        help='并发线程数 (默认: 5)'
    )
    download_parser.add_argument(
        '-n', '--top',
        type=int,
        help='只下载前 N 个仓库'
    )
    download_parser.set_defaults(func=cmd_download)

    # All command
    all_parser = subparsers.add_parser('all', help='爬取并下载热榜前10个仓库')
    all_parser.add_argument(
        '-s', '--since',
        choices=['daily', 'weekly', 'monthly'],
        default='weekly',
        help='时间范围 (默认: weekly)'
    )
    all_parser.add_argument(
        '-l', '--language',
        help='编程语言过滤'
    )
    all_parser.add_argument(
        '-o', '--output',
        default='./downloads',
        help='下载目录 (默认: ./downloads)'
    )
    all_parser.add_argument(
        '-w', '--workers',
        type=int,
        default=5,
        help='并发线程数 (默认: 5)'
    )
    all_parser.add_argument(
        '-n', '--top',
        type=int,
        default=10,
        help='下载前 N 个仓库 (默认: 10)'
    )
    all_parser.add_argument(
        '-j', '--json-file',
        help='热榜 JSON 文件名 (默认: github_trending_<timestamp>.json)'
    )
    all_parser.set_defaults(func=cmd_all)

    # Search command
    search_parser = subparsers.add_parser('search', help='搜索 GitHub 仓库')
    search_parser.add_argument(
        'query',
        help='搜索关键词 (仓库名、关键词)'
    )
    search_parser.add_argument(
        '-n', '--limit',
        type=int,
        default=20,
        help='最大结果数 (默认: 20)'
    )
    search_parser.add_argument(
        '-l', '--language',
        help='按编程语言过滤'
    )
    search_parser.add_argument(
        '-s', '--sort',
        choices=['stars', 'forks', 'updated'],
        default='stars',
        help='排序方式 (默认: stars)'
    )
    search_parser.add_argument(
        '-o', '--order',
        choices=['asc', 'desc'],
        default='desc',
        help='排序顺序 (默认: desc)'
    )
    search_parser.add_argument(
        '-f', '--output',
        help='保存结果到 JSON 文件'
    )
    search_parser.add_argument(
        '-t', '--token',
        help='GitHub token (可选，提高速率限制)'
    )
    search_parser.add_argument(
        '-r', '--rate-limit',
        type=float,
        default=2.0,
        help='请求间隔秒数 (默认: 2.0)'
    )
    search_parser.set_defaults(func=cmd_search)

    # Select command (interactive download)
    select_parser = subparsers.add_parser('select', help='交互式选择下载仓库')
    select_parser.add_argument(
        'source',
        choices=['search', 'trending'],
        help='数据来源 (search: 搜索, trending: 热榜)'
    )
    select_parser.add_argument(
        'query',
        nargs='?',
        help='搜索关键词 (仅 search 模式需要)'
    )
    select_parser.add_argument(
        '-s', '--since',
        choices=['daily', 'weekly', 'monthly'],
        default='weekly',
        help='时间范围 (默认: weekly，仅 trending 模式)'
    )
    select_parser.add_argument(
        '-l', '--language',
        help='语言过滤'
    )
    select_parser.add_argument(
        '-n', '--limit',
        type=int,
        default=30,
        help='最大结果数 (默认: 30)'
    )
    select_parser.add_argument(
        '-o', '--output',
        help='下载目录 (默认: 使用配置中的目录)'
    )
    select_parser.add_argument(
        '-w', '--workers',
        type=int,
        default=5,
        help='并发线程数 (默认: 5)'
    )
    select_parser.set_defaults(func=cmd_select)

    # Config command
    config_parser = subparsers.add_parser('config', help='管理配置')
    config_parser.add_argument(
        'action',
        choices=['show', 'set-dir', 'set-workers', 'set-rate', 'reset'],
        help='操作类型'
    )
    config_parser.add_argument(
        'value',
        nargs='?',
        help='设置值 (set-dir: 路径, set-workers: 线程数, set-rate: 秒数)'
    )
    config_parser.set_defaults(func=cmd_config)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Handle config command specially
    if args.command == 'config':
        if args.action == 'set-dir':
            args.path = args.value
        elif args.action == 'set-workers':
            args.workers = int(args.value) if args.value else None
        elif args.action == 'set-rate':
            args.limit = float(args.value) if args.value else None
        return cmd_config(args)

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending Crawler + Multi-threaded Downloader Example

This script demonstrates:
1. Crawling GitHub trending repositories
2. Downloading repositories with multi-threading
3. Progress tracking and statistics

Usage:
    python download_example.py
"""

from github_trending_crawler import GitHubTrendingCrawler
from downloader import RepoDownloader, download_trending_repos
import os
import json
from datetime import datetime


def example_crawl_and_download():
    """Example: Crawl trending and download top repositories."""
    print("=" * 80)
    print("GitHub Trending + Multi-threaded Downloader")
    print("=" * 80)

    # Step 1: Crawl trending repositories
    print("\n📥 第一步: 获取 GitHub 热榜...")
    crawler = GitHubTrendingCrawler(rate_limit=2.0)
    repositories = crawler.fetch_trending(since="weekly")

    if not repositories:
        print("❌ 未获取到任何仓库数据")
        return

    print(f"✓ 成功获取 {len(repositories)} 个热门仓库")

    # Display top 5
    print("\n🏆 本周热门 TOP 5:")
    for i, repo in enumerate(repositories[:5], 1):
        print(f"  {i}. {repo['name']} - ⭐ {repo.get('stars', 0):,}")

    # Step 2: Save to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"trending_{timestamp}.json"
    crawler.save_to_json(repositories, json_file)

    # Step 3: Download with multi-threading
    print(f"\n📦 第二步: 多线程下载仓库...")

    downloader = RepoDownloader(
        max_workers=5,      # 5 个并发线程
        timeout=60,         # 60 秒超时
        retry_count=3       # 重试 3 次
    )

    # Download top 10 repositories
    output_dir = f"./downloads_{timestamp}"
    results = downloader.download_with_progress_bar(
        repositories[:10],  # 只下载前 10 个
        output_dir=output_dir
    )

    # Print results
    print("\n📊 下载结果:")
    for result in results:
        status = "✓" if result.get('success') else "✗"
        size = result.get('size', 0) / (1024 * 1024)
        print(f"  {status} {result['repo']} ({size:.2f} MB)")


def example_download_from_json():
    """Example: Download from existing JSON file."""
    print("\n" + "=" * 80)
    print("从 JSON 文件下载仓库")
    print("=" * 80)

    # Find most recent JSON file
    json_files = [f for f in os.listdir('.') if f.startswith('trending_') and f.endswith('.json')]

    if not json_files:
        print("❌ 未找到 trending JSON 文件")
        print("   请先运行 example_crawl_and_download() 获取数据")
        return

    json_file = sorted(json_files)[-1]  # Get latest
    print(f"📁 使用文件: {json_file}")

    # Download top 5
    results = download_trending_repos(
        json_file=json_file,
        output_dir="./downloads_from_json",
        max_workers=3,
        top_n=5
    )

    print(f"\n✓ 下载完成!")


def example_advanced_usage():
    """Example: Advanced usage with custom settings."""
    print("\n" + "=" * 80)
    print("高级用法示例")
    print("=" * 80)

    # Custom downloader configuration
    downloader = RepoDownloader(
        max_workers=10,     # 10 个并发线程（更快，但更耗资源）
        timeout=120,        # 120 秒超时
        retry_count=5,      # 重试 5 次
        chunk_size=16384    # 16KB 块大小
    )

    # Manual download example
    repos = [
        {"name": "example/repo1", "url": "https://github.com/octocat/Hello-World"},
        {"name": "example/repo2", "url": "https://github.com/octocat/Spoon-Knife"},
    ]

    print("\n📥 手动下载示例:")
    print(f"   并发线程: {downloader.max_workers}")
    print(f"   超时时间: {downloader.timeout}s")
    print(f"   重试次数: {downloader.retry_count}")

    # Uncomment to actually download:
    # results = downloader.download_with_progress_bar(repos, "./downloads_manual")


def main():
    """Run all examples."""
    print("🚀 GitHub Trending + Multi-threaded Downloader 示例\n")

    try:
        # Example 1: Crawl and download
        example_crawl_and_download()

        # Example 2: Download from JSON
        example_download_from_json()

        # Example 3: Advanced usage
        example_advanced_usage()

        print("\n" + "=" * 80)
        print("✅ 所有示例运行完成!")
        print("=" * 80)

        print("\n💡 提示:")
        print("   - 使用 -w 参数调整并发线程数")
        print("   - 使用 -n 参数限制下载数量")
        print("   - 使用 -o 参数指定输出目录")
        print("   - 安装 tqdm 可以显示更美观的进度条")

    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
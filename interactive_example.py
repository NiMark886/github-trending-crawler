#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Download Example

This script demonstrates:
1. Displaying repositories with numbers
2. User selection with pagination
3. Downloading selected repositories

Usage:
    python interactive_example.py
"""

from interactive import InteractiveSelector, interactive_download_from_search
from search import RepoSearcher


def example_display_and_select():
    """Example: Display and select repositories."""
    print("=" * 80)
    print("示例: 交互式选择下载")
    print("=" * 80)

    # Search repositories
    print("\n🔍 搜索 React 相关仓库...")
    searcher = RepoSearcher()
    repos = searcher.search("react", limit=25)

    if not repos:
        print("❌ 未找到仓库")
        return

    # Create selector with pagination
    selector = InteractiveSelector(page_size=10)

    # Display first page (non-interactive demo)
    print("\n📦 搜索结果 (前10个):")
    selector.display_repos(repos, page=0)

    print("\n💡 交互式选择需要在终端中运行:")
    print("   python cli.py select search 'react'")

    # Simulate selection for demo
    print("\n📋 模拟选择前3个仓库:")
    selected = repos[:3]
    for i, repo in enumerate(selected, 1):
        print(f"  {i}. {repo['name']} - ⭐ {repo.get('stars', 0):,}")


def example_pagination():
    """Example: Pagination demonstration."""
    print("\n" + "=" * 80)
    print("示例: 分页显示")
    print("=" * 80)

    # Create test data (simulate large list)
    repos = []
    for i in range(50):
        repos.append({
            'name': f'example/repo-{i+1}',
            'owner': 'example',
            'stars': 1000 - i * 10,
            'language': 'Python' if i % 3 == 0 else 'JavaScript',
            'description': f'Example repository #{i+1}'
        })

    # Create selector with small page size
    selector = InteractiveSelector(page_size=5)

    # Display first page
    print("\n📦 分页显示示例 (每页5个):")
    selector.display_repos(repos, page=0)

    print("\n💡 提示:")
    print("   - 输入 'n' 或 'next' 查看下一页")
    print("   - 输入 'p' 或 'prev' 查看上一页")
    print("   - 输入 '1,3,5' 选择多个仓库")
    print("   - 输入 '1-5' 选择范围")
    print("   - 输入 'all' 选择当前页所有")
    print("   - 输入 'done' 完成选择")


def example_interactive_search():
    """Example: Interactive search and download."""
    print("\n" + "=" * 80)
    print("示例: 搜索并交互式下载")
    print("=" * 80)

    print("\n💡 使用方法:")
    print("   python cli.py select search 'react'")
    print("   python cli.py select search 'vue' -n 20")
    print("   python cli.py select search 'angular' -l typescript")
    print("\n   或在 Python 中:")
    print("   from interactive import interactive_download_from_search")
    print("   interactive_download_from_search('react', limit=20)")


def example_interactive_trending():
    """Example: Interactive trending download."""
    print("\n" + "=" * 80)
    print("示例: 热榜并交互式下载")
    print("=" * 80)

    print("\n💡 使用方法:")
    print("   python cli.py select trending")
    print("   python cli.py select trending -s daily")
    print("   python cli.py select trending -s monthly -l python")
    print("\n   或在 Python 中:")
    print("   from interactive import interactive_download_from_trending")
    print("   interactive_download_from_trending(since='daily')")


def main():
    """Run all examples."""
    print("🎯 交互式选择下载示例\n")

    try:
        # Example 1: Display and select
        example_display_and_select()

        # Example 2: Pagination
        example_pagination()

        # Example 3: Interactive search
        example_interactive_search()

        # Example 4: Interactive trending
        example_interactive_trending()

        print("\n" + "=" * 80)
        print("✅ 所有示例运行完成!")
        print("=" * 80)

        print("\n🚀 快速开始:")
        print("   1. 搜索并选择下载:")
        print("      python cli.py select search 'react'")
        print("\n   2. 热榜并选择下载:")
        print("      python cli.py select trending")
        print("\n   3. 日榜并选择下载:")
        print("      python cli.py select trending -s daily")

        print("\n📝 选择操作说明:")
        print("   • 输入数字: 1,3,5 选择多个")
        print("   • 输入范围: 1-5 选择范围")
        print("   • 输入 'all': 选择当前页所有")
        print("   • 输入 'n/p': 翻页")
        print("   • 输入 'done': 完成选择")
        print("   • 输入 'quit': 退出")

    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Repository Search Example

This script demonstrates:
1. Searching repositories by keyword
2. Displaying stars, author, description
3. Filtering by language
4. Saving results to JSON

Usage:
    python search_example.py
"""

from search import RepoSearcher
import os


def example_basic_search():
    """Basic search example."""
    print("=" * 80)
    print("示例1: 基本搜索")
    print("=" * 80)

    searcher = RepoSearcher()

    # Search by keyword
    results = searcher.search("react", limit=5)

    # Display results
    searcher.print_results(results)


def example_search_with_filter():
    """Search with language filter."""
    print("\n" + "=" * 80)
    print("示例2: 按语言过滤搜索")
    print("=" * 80)

    searcher = RepoSearcher()

    # Search Python repositories
    results = searcher.search(
        "web framework",
        limit=10,
        language="python"
    )

    # Display results
    searcher.print_results(results)


def example_search_by_topic():
    """Search by topic."""
    print("\n" + "=" * 80)
    print("示例3: 按主题搜索")
    print("=" * 80)

    searcher = RepoSearcher()

    # Search by topic
    results = searcher.search_by_topic("machine-learning", limit=10)

    # Display results
    searcher.print_results(results)


def example_search_and_save():
    """Search and save results."""
    print("\n" + "=" * 80)
    print("示例4: 搜索并保存结果")
    print("=" * 80)

    searcher = RepoSearcher()

    # Search
    results = searcher.search("vue", limit=10)

    # Display results
    searcher.print_results(results)

    # Save to JSON
    searcher.to_json(results, "vue_search_results.json")

    print(f"\n✓ 结果已保存到: vue_search_results.json")


def example_search_popular():
    """Search popular repositories."""
    print("\n" + "=" * 80)
    print("示例5: 搜索热门仓库")
    print("=" * 80)

    searcher = RepoSearcher()

    # Search popular Python repositories
    results = searcher.search_by_language(
        "python",
        limit=10,
        min_stars=10000
    )

    # Display results
    searcher.print_results(results)


def main():
    """Run all examples."""
    print("🔍 GitHub 仓库搜索示例\n")

    try:
        # Example 1: Basic search
        example_basic_search()

        # Example 2: Search with filter
        example_search_with_filter()

        # Example 3: Search by topic
        example_search_by_topic()

        # Example 4: Search and save
        example_search_and_save()

        # Example 5: Search popular
        example_search_popular()

        print("\n" + "=" * 80)
        print("✅ 所有示例运行完成!")
        print("=" * 80)

        print("\n💡 提示:")
        print("   - 使用 -n 参数限制结果数量")
        print("   - 使用 -l 参数按语言过滤")
        print("   - 使用 -o 参数保存结果到文件")
        print("   - 设置 GITHUB_TOKEN 环境变量提高速率限制")

    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
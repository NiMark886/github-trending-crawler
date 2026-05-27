#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending Crawler - 使用示例

本文件展示如何使用 GitHubTrendingCrawler 类的各种功能。
"""

from github_trending_crawler import GitHubTrendingCrawler
import json


def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)

    # 创建爬虫实例
    crawler = GitHubTrendingCrawler(rate_limit=2.0)

    # 获取本周热门项目
    repositories = crawler.fetch_trending(since="weekly")

    # 打印结果
    crawler.print_trending(repositories)

    # 保存到文件
    crawler.save_to_json(repositories, "basic_example.json")

    print(f"\n✓ 成功获取 {len(repositories)} 个热门项目")


def example_language_filter():
    """按编程语言过滤示例"""
    print("\n" + "=" * 60)
    print("示例2: 按编程语言过滤")
    print("=" * 60)

    crawler = GitHubTrendingCrawler(rate_limit=2.0)

    # 获取 Python 语言的热门项目
    python_repos = crawler.fetch_trending(since="weekly", language="python")

    print(f"\nPython 热门项目 ({len(python_repos)} 个):")
    for i, repo in enumerate(python_repos[:5], 1):  # 只显示前5个
        print(f"{i}. {repo['name']} - ⭐ {repo.get('stars', 0):,}")

    # 保存结果
    crawler.save_to_json(python_repos, "python_trending.json")


def example_time_ranges():
    """不同时间范围示例"""
    print("\n" + "=" * 60)
    print("示例3: 不同时间范围")
    print("=" * 60)

    crawler = GitHubTrendingCrawler(rate_limit=2.0)

    # 获取每日热门
    daily_repos = crawler.fetch_trending(since="daily")
    print(f"每日热门: {len(daily_repos)} 个项目")

    # 获取每周热门
    weekly_repos = crawler.fetch_trending(since="weekly")
    print(f"每周热门: {len(weekly_repos)} 个项目")

    # 获取每月热门
    monthly_repos = crawler.fetch_trending(since="monthly")
    print(f"每月热门: {len(monthly_repos)} 个项目")


def example_analysis():
    """数据分析示例"""
    print("\n" + "=" * 60)
    print("示例4: 数据分析")
    print("=" * 60)

    crawler = GitHubTrendingCrawler(rate_limit=2.0)

    # 获取数据
    repositories = crawler.fetch_trending(since="weekly")

    # 分析趋势
    analysis = crawler.analyze_trends(repositories)

    # 打印分析结果
    print(f"\n📊 趋势分析:")
    print(f"   总项目数: {analysis.get('total_repos', 0)}")
    print(f"   总星标数: {analysis.get('total_stars', 0):,}")
    print(f"   总周增长: +{analysis.get('total_weekly_growth', 0):,}")

    print(f"\n📝 语言分布:")
    for lang, count in analysis.get('languages', {}).items():
        print(f"   {lang}: {count} 个项目")

    print(f"\n🏆 星标最多的项目:")
    for i, repo in enumerate(analysis.get('top_by_stars', [])[:3], 1):
        print(f"   {i}. {repo['name']} ({repo.get('stars', 0):,} ⭐)")


def example_custom_processing():
    """自定义处理示例"""
    print("\n" + "=" * 60)
    print("示例5: 自定义处理")
    print("=" * 60)

    crawler = GitHubTrendingCrawler(rate_limit=2.0)

    # 获取数据
    repositories = crawler.fetch_trending(since="weekly")

    # 自定义过滤: 只保留星标超过 10000 的项目
    popular_repos = [
        repo for repo in repositories
        if repo.get('stars', 0) > 10000
    ]

    print(f"\n星标超过 10,000 的项目 ({len(popular_repos)} 个):")
    for repo in popular_repos:
        print(f"  • {repo['name']}: {repo.get('stars', 0):,} ⭐")
        print(f"    {repo.get('description', '无描述')[:80]}...")

    # 按星标排序
    sorted_repos = sorted(
        repositories,
        key=lambda x: x.get('stars', 0),
        reverse=True
    )

    print(f"\n📈 按星标排序的前5个项目:")
    for i, repo in enumerate(sorted_repos[:5], 1):
        print(f"   {i}. {repo['name']}: {repo.get('stars', 0):,} ⭐")


def example_export_formats():
    """导出格式示例"""
    print("\n" + "=" * 60)
    print("示例6: 导出格式")
    print("=" * 60)

    crawler = GitHubTrendingCrawler(rate_limit=2.0)

    # 获取数据
    repositories = crawler.fetch_trending(since="weekly")

    # 导出为 JSON
    json_file = crawler.save_to_json(repositories, "export_example.json")
    print(f"✓ JSON 导出: {json_file}")

    # 导出为 CSV (手动实现)
    csv_file = "export_example.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        # 写入表头
        f.write("name,url,description,language,stars,weekly_stars,forks\n")

        # 写入数据
        for repo in repositories:
            name = repo.get('name', '').replace(',', ';')
            url = repo.get('url', '')
            desc = repo.get('description', '').replace(',', ';').replace('\n', ' ')
            lang = repo.get('language', '')
            stars = repo.get('stars', 0)
            weekly = repo.get('weekly_stars', 0)
            forks = repo.get('forks', 0)

            f.write(f"{name},{url},{desc},{lang},{stars},{weekly},{forks}\n")

    print(f"✓ CSV 导出: {csv_file}")


def main():
    """运行所有示例"""
    print("GitHub Trending Crawler - 使用示例")
    print("=" * 60)

    try:
        # 运行基本示例
        example_basic_usage()

        # 运行语言过滤示例
        example_language_filter()

        # 运行时间范围示例
        example_time_ranges()

        # 运行分析示例
        example_analysis()

        # 运行自定义处理示例
        example_custom_processing()

        # 运行导出示例
        example_export_formats()

        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Display Module with Rich Library

Features:
- Colored terminal output
- Beautiful tables
- Progress bars
- Syntax highlighting
- Panel layouts

Usage:
    from display import Display

    display = Display()
    display.print_repos(repositories)
"""

import os
from typing import List, Dict, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.text import Text
    from rich.columns import Columns
    from rich.markdown import Markdown
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from logger import get_logger

logger = get_logger(__name__)


class Display:
    """Beautiful terminal display using Rich library."""

    def __init__(self):
        """Initialize display."""
        if HAS_RICH:
            self.console = Console()
        else:
            logger.warning("rich 库未安装，使用普通输出")

    def print_header(self, title: str, subtitle: str = ""):
        """
        Print a header.

        Args:
            title: Header title
            subtitle: Header subtitle
        """
        if HAS_RICH:
            text = Text(title, style="bold cyan")
            if subtitle:
                text.append(f"\n{subtitle}", style="dim")
            self.console.print(Panel(text, border_style="cyan"))
        else:
            print("\n" + "=" * 80)
            print(title)
            if subtitle:
                print(subtitle)
            print("=" * 80)

    def print_repos(
        self,
        repos: List[Dict],
        title: str = "仓库列表",
        show_index: bool = True,
        compact: bool = False
    ):
        """
        Print repositories in a table.

        Args:
            repos: List of repository dictionaries
            title: Table title
            show_index: Show row numbers
            compact: Use compact display
        """
        if not repos:
            print("没有可显示的仓库")
            return

        if HAS_RICH:
            table = Table(
                title=title,
                box=box.ROUNDED,
                show_header=True,
                header_style="bold magenta"
            )

            if show_index:
                table.add_column("#", style="dim", width=4)
            table.add_column("仓库名称", style="cyan", min_width=25)
            table.add_column("作者", style="green", min_width=12)
            table.add_column("语言", style="yellow", min_width=10)
            table.add_column("⭐ 星标", justify="right", style="bold yellow")
            table.add_column("🍴 Fork", justify="right")
            table.add_column("描述", max_width=40)

            for i, repo in enumerate(repos, 1):
                name = repo.get('name', 'Unknown')
                owner = repo.get('owner', '')
                language = repo.get('language', 'Unknown')
                stars = repo.get('stars', 0)
                forks = repo.get('forks', 0)
                desc = repo.get('description', '')[:40]

                # Format stars
                if stars >= 1000000:
                    stars_str = f"{stars/1000000:.1f}M"
                elif stars >= 1000:
                    stars_str = f"{stars/1000:.1f}k"
                else:
                    stars_str = str(stars)

                # Format forks
                if forks >= 1000:
                    forks_str = f"{forks/1000:.1f}k"
                else:
                    forks_str = str(forks)

                row = []
                if show_index:
                    row.append(str(i))
                row.extend([name, owner, language, stars_str, forks_str, desc])

                table.add_row(*row)

            self.console.print(table)
        else:
            # Fallback to simple output
            print(f"\n{'=' * 80}")
            print(f"{title} ({len(repos)} 个)")
            print(f"{'=' * 80}")

            for i, repo in enumerate(repos, 1):
                name = repo.get('name', 'Unknown')
                stars = repo.get('stars', 0)
                language = repo.get('language', 'Unknown')
                desc = repo.get('description', '')[:50]

                if show_index:
                    print(f"\n[{i}] {name}")
                else:
                    print(f"\n{name}")
                print(f"   ⭐ {stars:,} | {language} | {desc}")

            print(f"{'=' * 80}")

    def print_search_results(
        self,
        results: List[Dict],
        query: str
    ):
        """
        Print search results.

        Args:
            results: Search results
            query: Search query
        """
        if HAS_RICH:
            title = f"🔍 搜索结果: {query} ({len(results)} 个)"
            self.print_repos(results, title=title)
        else:
            print(f"\n搜索结果: {query} ({len(results)} 个)")
            self.print_repos(results, show_index=True)

    def print_trending(
        self,
        repos: List[Dict],
        trending_type: str = "weekly"
    ):
        """
        Print trending repositories.

        Args:
            repos: Trending repositories
            trending_type: Trending type (daily/weekly/monthly)
        """
        type_names = {
            "daily": "日榜",
            "weekly": "周榜",
            "monthly": "月榜"
        }

        title = f"📈 GitHub {type_names.get(trending_type, trending_type)}热榜"

        if HAS_RICH:
            table = Table(
                title=title,
                box=box.DOUBLE_EDGE,
                show_header=True,
                header_style="bold yellow"
            )

            table.add_column("#", style="dim", width=4)
            table.add_column("仓库名称", style="cyan", min_width=25)
            table.add_column("语言", style="green", min_width=10)
            table.add_column("⭐ 星标", justify="right", style="bold yellow")
            table.add_column("📈 周增长", justify="right", style="bold green")
            table.add_column("描述", max_width=45)

            for i, repo in enumerate(repos, 1):
                name = repo.get('name', 'Unknown')
                language = repo.get('language', 'Unknown')
                stars = repo.get('stars', 0)
                weekly = repo.get('weekly_stars', 0)
                desc = repo.get('description', '')[:45]

                # Format
                stars_str = f"{stars/1000:.1f}k" if stars >= 1000 else str(stars)
                weekly_str = f"+{weekly:,}" if weekly > 0 else "-"

                table.add_row(str(i), name, language, stars_str, weekly_str, desc)

            self.console.print(table)
        else:
            print(f"\n{'=' * 80}")
            print(f"{title}")
            print(f"{'=' * 80}")

            for i, repo in enumerate(repos, 1):
                name = repo.get('name', 'Unknown')
                stars = repo.get('stars', 0)
                weekly = repo.get('weekly_stars', 0)

                print(f"\n[{i}] {name}")
                print(f"   ⭐ {stars:,} | 📈 +{weekly:,}")

            print(f"{'=' * 80}")

    def print_progress(
        self,
        total: int,
        description: str = "下载进度"
    ):
        """
        Create a progress bar.

        Args:
            total: Total items
            description: Progress description

        Returns:
            Progress context manager
        """
        if HAS_RICH:
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console
            )
        else:
            # Return a simple progress tracker
            return SimpleProgress(total, description)

    def print_stats(self, stats: Dict, title: str = "统计信息"):
        """
        Print statistics.

        Args:
            stats: Statistics dictionary
            title: Title
        """
        if HAS_RICH:
            table = Table(
                title=title,
                box=box.SIMPLE,
                show_header=False
            )

            table.add_column("指标", style="cyan")
            table.add_column("值", style="green", justify="right")

            for key, value in stats.items():
                table.add_row(str(key), str(value))

            self.console.print(table)
        else:
            print(f"\n{title}")
            print("-" * 40)
            for key, value in stats.items():
                print(f"  {key}: {value}")

    def print_panel(
        self,
        content: str,
        title: str = "",
        border_style: str = "cyan"
    ):
        """
        Print content in a panel.

        Args:
            content: Panel content
            title: Panel title
            border_style: Border color
        """
        if HAS_RICH:
            self.console.print(Panel(
                content,
                title=title,
                border_style=border_style
            ))
        else:
            print(f"\n{'=' * 80}")
            if title:
                print(title)
                print("-" * 80)
            print(content)
            print(f"{'=' * 80}")

    def print_success(self, message: str):
        """Print success message."""
        if HAS_RICH:
            self.console.print(f"✓ {message}", style="bold green")
        else:
            print(f"✓ {message}")

    def print_error(self, message: str):
        """Print error message."""
        if HAS_RICH:
            self.console.print(f"✗ {message}", style="bold red")
        else:
            print(f"✗ {message}")

    def print_warning(self, message: str):
        """Print warning message."""
        if HAS_RICH:
            self.console.print(f"⚠ {message}", style="bold yellow")
        else:
            print(f"⚠ {message}")

    def print_info(self, message: str):
        """Print info message."""
        if HAS_RICH:
            self.console.print(f"ℹ {message}", style="bold blue")
        else:
            print(f"ℹ {message}")

    def print_separator(self):
        """Print a separator line."""
        if HAS_RICH:
            self.console.print("─" * 80, style="dim")
        else:
            print("-" * 80)

    def clear(self):
        """Clear the console."""
        if HAS_RICH:
            self.console.clear()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')


class SimpleProgress:
    """Simple progress tracker when rich is not available."""

    def __init__(self, total: int, description: str):
        self.total = total
        self.description = description
        self.current = 0

    def update(self, advance: int = 1):
        """Update progress."""
        self.current += advance
        percent = (self.current / self.total) * 100
        bar_length = 40
        filled = int(bar_length * self.current / self.total)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f"\r{self.description}: |{bar}| {percent:.1f}% ({self.current}/{self.total})", end='')

        if self.current >= self.total:
            print()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        print()


# Global display instance
_display = None


def get_display() -> Display:
    """Get global display instance."""
    global _display
    if _display is None:
        _display = Display()
    return _display


# Convenience functions
def print_repos(repos: List[Dict], title: str = "仓库列表"):
    """Print repositories."""
    get_display().print_repos(repos, title)


def print_trending(repos: List[Dict], trending_type: str = "weekly"):
    """Print trending repositories."""
    get_display().print_trending(repos, trending_type)


def print_success(message: str):
    """Print success message."""
    get_display().print_success(message)


def print_error(message: str):
    """Print error message."""
    get_display().print_error(message)


# Example usage
if __name__ == "__main__":
    display = Display()

    # Test repositories
    repos = [
        {
            "name": "facebook/react",
            "owner": "facebook",
            "language": "JavaScript",
            "stars": 245000,
            "forks": 51000,
            "description": "The library for web and native user interfaces"
        },
        {
            "name": "vuejs/vue",
            "owner": "vuejs",
            "language": "JavaScript",
            "stars": 210000,
            "forks": 34000,
            "description": "Vue.js is a progressive JavaScript framework"
        }
    ]

    # Test display
    display.print_header("GitHub Trending Crawler", "测试显示效果")

    display.print_repos(repos, title="热门仓库")

    display.print_success("操作成功!")
    display.print_error("操作失败!")
    display.print_warning("警告信息")
    display.print_info("提示信息")

    # Test stats
    stats = {
        "总仓库数": 18,
        "总星标数": "352,061",
        "语言分布": "5 种"
    }
    display.print_stats(stats, "统计信息")

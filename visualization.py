#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Visualization Module

Features:
- Star history charts
- Language distribution pie charts
- Trending bar charts
- Export to image files

Usage:
    from visualization import Visualizer

    viz = Visualizer()
    viz.plot_star_history(repo_name, history_data)
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.ticker import FuncFormatter
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from logger import get_logger

logger = get_logger(__name__)


class Visualizer:
    """Data visualization using matplotlib."""

    def __init__(self, output_dir: str = "charts", style: str = "seaborn-v0_8"):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory for saving charts
            style: Matplotlib style
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if HAS_MATPLOTLIB:
            try:
                plt.style.use(style)
            except Exception:
                plt.style.use('default')
            logger.info(f"可视化模块初始化完成 (输出目录: {output_dir})")
        else:
            logger.warning("matplotlib 未安装，可视化功能不可用")

    def plot_star_history(
        self,
        repo_name: str,
        history: List[Dict],
        save: bool = True,
        show: bool = False
    ) -> Optional[str]:
        """
        Plot star count history.

        Args:
            repo_name: Repository name
            history: Star history data
            save: Save to file
            show: Show plot

        Returns:
            Path to saved file or None
        """
        if not HAS_MATPLOTLIB:
            logger.error("matplotlib 未安装")
            return None

        if not history:
            logger.warning("没有历史数据")
            return None

        # Parse data
        dates = []
        stars = []
        for record in history:
            try:
                date = datetime.strptime(record['recorded_at'], "%Y-%m-%d")
                dates.append(date)
                stars.append(record['stars'])
            except Exception as e:
                logger.warning(f"解析数据失败: {e}")

        if not dates:
            return None

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot line
        ax.plot(dates, stars, 'b-', linewidth=2, marker='o', markersize=4)

        # Fill area
        ax.fill_between(dates, stars, alpha=0.3)

        # Format axes
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('星标数', fontsize=12)
        ax.set_title(f'{repo_name} - 星标历史', fontsize=14, fontweight='bold')

        # Format y-axis
        def format_stars(x, p):
            if x >= 1000000:
                return f'{x/1000000:.1f}M'
            elif x >= 1000:
                return f'{x/1000:.0f}K'
            return f'{x:.0f}'

        ax.yaxis.set_major_formatter(FuncFormatter(format_stars))

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.xticks(rotation=45, ha='right')

        # Grid
        ax.grid(True, alpha=0.3)

        # Tight layout
        plt.tight_layout()

        # Save
        if save:
            filename = f"star_history_{repo_name.replace('/', '_')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            logger.info(f"图表已保存: {filepath}")

        if show:
            plt.show()
        else:
            plt.close()

        return str(filepath) if save else None

    def plot_language_distribution(
        self,
        language_stats: List[Dict],
        top_n: int = 10,
        save: bool = True,
        show: bool = False
    ) -> Optional[str]:
        """
        Plot language distribution pie chart.

        Args:
            language_stats: Language statistics
            top_n: Show top N languages
            save: Save to file
            show: Show plot

        Returns:
            Path to saved file or None
        """
        if not HAS_MATPLOTLIB:
            logger.error("matplotlib 未安装")
            return None

        if not language_stats:
            logger.warning("没有语言数据")
            return None

        # Get top N languages
        sorted_stats = sorted(language_stats, key=lambda x: x['count'], reverse=True)[:top_n]

        labels = [s['language'] for s in sorted_stats]
        sizes = [s['count'] for s in sorted_stats]

        # Add "Others" if there are more languages
        total = sum(s['count'] for s in language_stats)
        top_total = sum(sizes)
        if top_total < total:
            labels.append('其他')
            sizes.append(total - top_total)

        # Colors
        colors = plt.cm.Set3(range(len(labels)))

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85
        )

        # Style
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')

        # Title
        ax.set_title('编程语言分布', fontsize=14, fontweight='bold')

        # Legend
        ax.legend(
            wedges,
            [f'{l}: {s}' for l, s in zip(labels, sizes)],
            title="语言",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )

        plt.tight_layout()

        # Save
        if save:
            filepath = self.output_dir / "language_distribution.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            logger.info(f"图表已保存: {filepath}")

        if show:
            plt.show()
        else:
            plt.close()

        return str(filepath) if save else None

    def plot_trending_bar(
        self,
        repos: List[Dict],
        title: str = "热门仓库 Top 10",
        metric: str = "stars",
        save: bool = True,
        show: bool = False
    ) -> Optional[str]:
        """
        Plot trending repositories bar chart.

        Args:
            repos: Repository list
            title: Chart title
            metric: Metric to display (stars/forks)
            save: Save to file
            show: Show plot

        Returns:
            Path to saved file or None
        """
        if not HAS_MATPLOTLIB:
            logger.error("matplotlib 未安装")
            return None

        if not repos:
            logger.warning("没有仓库数据")
            return None

        # Sort and get top 10
        sorted_repos = sorted(repos, key=lambda x: x.get(metric, 0), reverse=True)[:10]

        names = [r['name'].split('/')[-1] for r in sorted_repos]
        values = [r.get(metric, 0) for r in sorted_repos]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot horizontal bar chart
        y_pos = range(len(names))
        bars = ax.barh(y_pos, values, color=plt.cm.viridis(range(0, 256, 256 // len(names))))

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            if value >= 1000:
                label = f'{value/1000:.1f}K'
            else:
                label = str(value)
            ax.text(bar.get_width() + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                    label, ha='left', va='center', fontsize=10)

        # Format axes
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10)
        ax.set_xlabel(metric.capitalize(), fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Invert y-axis to show highest at top
        ax.invert_yaxis()

        # Grid
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()

        # Save
        if save:
            filename = f"trending_{metric}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            logger.info(f"图表已保存: {filepath}")

        if show:
            plt.show()
        else:
            plt.close()

        return str(filepath) if save else None

    def plot_weekly_growth(
        self,
        repos: List[Dict],
        save: bool = True,
        show: bool = False
    ) -> Optional[str]:
        """
        Plot weekly star growth.

        Args:
            repos: Repository list with weekly_stars field
            save: Save to file
            show: Show plot

        Returns:
            Path to saved file or None
        """
        if not HAS_MATPLOTLIB:
            logger.error("matplotlib 未安装")
            return None

        # Filter repos with weekly growth
        repos_with_growth = [r for r in repos if r.get('weekly_stars', 0) > 0]

        if not repos_with_growth:
            logger.warning("没有周增长数据")
            return None

        # Sort by weekly growth and get top 10
        sorted_repos = sorted(repos_with_growth, key=lambda x: x['weekly_stars'], reverse=True)[:10]

        names = [r['name'].split('/')[-1] for r in sorted_repos]
        growth = [r['weekly_stars'] for r in sorted_repos]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot bar chart
        bars = ax.bar(names, growth, color='#2ecc71')

        # Add value labels
        for bar, value in zip(bars, growth):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(growth) * 0.01,
                    f'+{value:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Format axes
        ax.set_xlabel('仓库', fontsize=12)
        ax.set_ylabel('周增长星标数', fontsize=12)
        ax.set_title('本周星标增长 Top 10', fontsize=14, fontweight='bold')

        plt.xticks(rotation=45, ha='right')

        # Grid
        ax.grid(True, axis='y', alpha=0.3)

        plt.tight_layout()

        # Save
        if save:
            filepath = self.output_dir / "weekly_growth.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            logger.info(f"图表已保存: {filepath}")

        if show:
            plt.show()
        else:
            plt.close()

        return str(filepath) if save else None

    def generate_report(
        self,
        repos: List[Dict],
        language_stats: List[Dict],
        title: str = "GitHub Trending 报告"
    ) -> List[str]:
        """
        Generate a complete report with multiple charts.

        Args:
            repos: Repository list
            language_stats: Language statistics
            title: Report title

        Returns:
            List of generated chart file paths
        """
        charts = []

        # Language distribution
        chart = self.plot_language_distribution(language_stats, save=True)
        if chart:
            charts.append(chart)

        # Stars bar chart
        chart = self.plot_trending_bar(repos, title=f"{title} - 星标排行", metric="stars")
        if chart:
            charts.append(chart)

        # Forks bar chart
        chart = self.plot_trending_bar(repos, title=f"{title} - Fork 排行", metric="forks")
        if chart:
            charts.append(chart)

        # Weekly growth
        chart = self.plot_weekly_growth(repos)
        if chart:
            charts.append(chart)

        logger.info(f"报告生成完成，共 {len(charts)} 个图表")
        return charts


# Example usage
if __name__ == "__main__":
    viz = Visualizer()

    # Test data
    repos = [
        {"name": "facebook/react", "stars": 245000, "forks": 51000, "weekly_stars": 500},
        {"name": "vuejs/vue", "stars": 210000, "forks": 34000, "weekly_stars": 300},
        {"name": "angular/angular", "stars": 90000, "forks": 24000, "weekly_stars": 200},
    ]

    lang_stats = [
        {"language": "JavaScript", "count": 5},
        {"language": "Python", "count": 3},
        {"language": "TypeScript", "count": 2},
    ]

    # Generate charts
    viz.plot_trending_bar(repos, show=True)
    viz.plot_language_distribution(lang_stats, show=True)

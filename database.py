#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Module for GitHub Trending Crawler

Features:
- SQLite database storage
- Repository history tracking
- Star count history
- Trend analysis
- Data export

Usage:
    from database import Database

    db = Database()
    db.save_repos(repositories)
    history = db.get_history("facebook/react")
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from logger import get_logger

logger = get_logger(__name__)


class Database:
    """SQLite database for storing repository data."""

    def __init__(self, db_path: str = "github_trending.db"):
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
        logger.info(f"数据库初始化完成: {db_path}")

    def _connect(self):
        """Create database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            # Enable WAL mode for better performance
            self.conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def _create_tables(self):
        """Create database tables."""
        try:
            cursor = self.conn.cursor()

            # Repositories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT,
                    language TEXT,
                    stars INTEGER DEFAULT 0,
                    forks INTEGER DEFAULT 0,
                    watchers INTEGER DEFAULT 0,
                    open_issues INTEGER DEFAULT 0,
                    topics TEXT,
                    license TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    crawled_at TEXT NOT NULL,
                    UNIQUE(name, crawled_at)
                )
            """)

            # Star history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS star_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_name TEXT NOT NULL,
                    stars INTEGER NOT NULL,
                    recorded_at TEXT NOT NULL,
                    UNIQUE(repo_name, recorded_at)
                )
            """

            # Trending history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trending_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_name TEXT NOT NULL,
                    trending_type TEXT NOT NULL,
                    position INTEGER,
                    weekly_stars INTEGER DEFAULT 0,
                    recorded_at TEXT NOT NULL,
                    UNIQUE(repo_name, trending_type, recorded_at)
                )
            """)

            # Search history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    results_count INTEGER DEFAULT 0,
                    searched_at TEXT NOT NULL
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_repos_name ON repositories(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_repos_stars ON repositories(stars)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_star_history_repo ON star_history(repo_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trending_repo ON trending_history(repo_name)")

            self.conn.commit()
            logger.debug("数据库表创建完成")

        except sqlite3.Error as e:
            logger.error(f"创建表失败: {e}")
            raise

    def save_repo(self, repo: Dict) -> int:
        """
        Save a single repository.

        Args:
            repo: Repository dictionary

        Returns:
            Row ID
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT OR REPLACE INTO repositories
                (name, owner, url, description, language, stars, forks, watchers,
                 open_issues, topics, license, created_at, updated_at, crawled_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                repo.get('name', ''),
                repo.get('owner', ''),
                repo.get('url', ''),
                repo.get('description', ''),
                repo.get('language', ''),
                repo.get('stars', 0),
                repo.get('forks', 0),
                repo.get('watchers', 0),
                repo.get('open_issues', 0),
                json.dumps(repo.get('topics', [])),
                repo.get('license', ''),
                repo.get('created_at', ''),
                repo.get('updated_at', ''),
                now
            ))

            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.Error as e:
            logger.error(f"保存仓库失败: {repo.get('name')} - {e}")
            return -1

    def save_repos(self, repos: List[Dict]) -> int:
        """
        Save multiple repositories.

        Args:
            repos: List of repository dictionaries

        Returns:
            Number of saved repositories
        """
        saved = 0
        for repo in repos:
            if self.save_repo(repo) > 0:
                saved += 1

        logger.info(f"保存了 {saved}/{len(repos)} 个仓库")
        return saved

    def save_star_count(self, repo_name: str, stars: int):
        """
        Save star count for history tracking.

        Args:
            repo_name: Repository name
            stars: Star count
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT OR REPLACE INTO star_history (repo_name, stars, recorded_at)
                VALUES (?, ?, ?)
            """, (repo_name, stars, now))

            self.conn.commit()

        except sqlite3.Error as e:
            logger.error(f"保存星标历史失败: {repo_name} - {e}")

    def save_trending(
        self,
        repo_name: str,
        trending_type: str,
        position: int,
        weekly_stars: int = 0
    ):
        """
        Save trending record.

        Args:
            repo_name: Repository name
            trending_type: Trending type (daily/weekly/monthly)
            position: Position in trending list
            weekly_stars: Weekly star growth
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT OR REPLACE INTO trending_history
                (repo_name, trending_type, position, weekly_stars, recorded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (repo_name, trending_type, position, weekly_stars, now))

            self.conn.commit()

        except sqlite3.Error as e:
            logger.error(f"保存热榜记录失败: {repo_name} - {e}")

    def save_search(self, query: str, results_count: int):
        """
        Save search history.

        Args:
            query: Search query
            results_count: Number of results
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO search_history (query, results_count, searched_at)
                VALUES (?, ?, ?)
            """, (query, results_count, now))

            self.conn.commit()

        except sqlite3.Error as e:
            logger.error(f"保存搜索历史失败: {query} - {e}")

    def get_repo(self, name: str) -> Optional[Dict]:
        """
        Get repository by name.

        Args:
            name: Repository name

        Returns:
            Repository dictionary or None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM repositories WHERE name = ?
                ORDER BY crawled_at DESC LIMIT 1
            """, (name,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            logger.error(f"获取仓库失败: {name} - {e}")
            return None

    def get_repos(
        self,
        language: Optional[str] = None,
        min_stars: int = 0,
        limit: int = 100,
        order_by: str = "stars"
    ) -> List[Dict]:
        """
        Get repositories with filters.

        Args:
            language: Filter by language
            min_stars: Minimum star count
            limit: Maximum results
            order_by: Order by field

        Returns:
            List of repository dictionaries
        """
        try:
            cursor = self.conn.cursor()

            query = "SELECT * FROM repositories WHERE stars >= ?"
            params = [min_stars]

            if language:
                query += " AND language = ?"
                params.append(language)

            query += f" ORDER BY {order_by} DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"获取仓库列表失败: {e}")
            return []

    def get_star_history(
        self,
        repo_name: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get star count history.

        Args:
            repo_name: Repository name
            days: Number of days to look back

        Returns:
            List of star count records
        """
        try:
            cursor = self.conn.cursor()
            since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT * FROM star_history
                WHERE repo_name = ? AND recorded_at >= ?
                ORDER BY recorded_at ASC
            """, (repo_name, since))

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"获取星标历史失败: {repo_name} - {e}")
            return []

    def get_trending_history(
        self,
        repo_name: Optional[str] = None,
        trending_type: Optional[str] = None,
        days: int = 30
    ) -> List[Dict]:
        """
        Get trending history.

        Args:
            repo_name: Filter by repository name
            trending_type: Filter by trending type
            days: Number of days to look back

        Returns:
            List of trending records
        """
        try:
            cursor = self.conn.cursor()
            since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            query = "SELECT * FROM trending_history WHERE recorded_at >= ?"
            params = [since]

            if repo_name:
                query += " AND repo_name = ?"
                params.append(repo_name)

            if trending_type:
                query += " AND trending_type = ?"
                params.append(trending_type)

            query += " ORDER BY recorded_at DESC, position ASC"

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"获取热榜历史失败: {e}")
            return []

    def get_search_history(self, limit: int = 50) -> List[Dict]:
        """
        Get search history.

        Args:
            limit: Maximum results

        Returns:
            List of search records
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM search_history
                ORDER BY searched_at DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"获取搜索历史失败: {e}")
            return []

    def get_language_stats(self) -> List[Dict]:
        """
        Get language statistics.

        Returns:
            List of language statistics
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT language, COUNT(*) as count, AVG(stars) as avg_stars
                FROM repositories
                WHERE language IS NOT NULL AND language != ''
                GROUP BY language
                ORDER BY count DESC
            """)

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"获取语言统计失败: {e}")
            return []

    def get_top_repos(
        self,
        limit: int = 10,
        language: Optional[str] = None
    ) -> List[Dict]:
        """
        Get top repositories by stars.

        Args:
            limit: Number of results
            language: Filter by language

        Returns:
            List of top repositories
        """
        try:
            cursor = self.conn.cursor()

            if language:
                cursor.execute("""
                    SELECT * FROM repositories
                    WHERE language = ?
                    ORDER BY stars DESC
                    LIMIT ?
                """, (language, limit))
            else:
                cursor.execute("""
                    SELECT * FROM repositories
                    ORDER BY stars DESC
                    LIMIT ?
                """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"获取热门仓库失败: {e}")
            return []

    def get_repo_count(self) -> int:
        """Get total number of unique repositories."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT name) FROM repositories")
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"获取仓库数量失败: {e}")
            return 0

    def export_to_json(self, output_file: str):
        """
        Export all data to JSON.

        Args:
            output_file: Output file path
        """
        try:
            data = {
                "repositories": self.get_repos(limit=10000),
                "language_stats": self.get_language_stats(),
                "exported_at": datetime.now().isoformat()
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"数据已导出到: {output_file}")

        except Exception as e:
            logger.error(f"导出数据失败: {e}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("数据库连接已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def __del__(self):
        self.close()


# Example usage
if __name__ == "__main__":
    # Create database
    db = Database("test.db")

    # Save some repos
    repos = [
        {
            "name": "facebook/react",
            "owner": "facebook",
            "url": "https://github.com/facebook/react",
            "description": "The library for web and native user interfaces",
            "language": "JavaScript",
            "stars": 245000,
            "forks": 51000
        },
        {
            "name": "vuejs/vue",
            "owner": "vuejs",
            "url": "https://github.com/vuejs/vue",
            "description": "Vue.js is a progressive JavaScript framework",
            "language": "JavaScript",
            "stars": 210000,
            "forks": 34000
        }
    ]

    db.save_repos(repos)

    # Save star history
    db.save_star_count("facebook/react", 245000)

    # Get history
    history = db.get_star_history("facebook/react")
    print(f"Star history: {history}")

    # Get stats
    stats = db.get_language_stats()
    print(f"Language stats: {stats}")

    # Close
    db.close()

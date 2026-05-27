#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Repository Multi-threaded Downloader

Features:
- Multi-threaded concurrent downloads
- Download ZIP archives
- Progress tracking with tqdm
- Resume interrupted downloads
- Speed statistics

Usage:
    from downloader import RepoDownloader

    downloader = RepoDownloader(max_workers=5)
    downloader.download_repos(repositories, output_dir="./downloads")

Requirements:
    pip install requests tqdm
"""

import os
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from urllib.parse import urlparse
import hashlib
import json
from pathlib import Path


class DownloadProgress:
    """Track download progress and statistics."""

    def __init__(self):
        self.total = 0
        self.completed = 0
        self.failed = 0
        self.start_time = None
        self.downloaded_bytes = 0

    def start(self, total: int):
        """Start tracking progress."""
        self.total = total
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        self.downloaded_bytes = 0

    def update(self, success: bool, file_size: int = 0):
        """Update progress."""
        if success:
            self.completed += 1
            self.downloaded_bytes += file_size
        else:
            self.failed += 1

    def get_stats(self) -> Dict:
        """Get current statistics."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        speed = self.downloaded_bytes / elapsed if elapsed > 0 else 0

        return {
            'total': self.total,
            'completed': self.completed,
            'failed': self.failed,
            'elapsed': elapsed,
            'downloaded_mb': self.downloaded_bytes / (1024 * 1024),
            'speed_mb': speed / (1024 * 1024),
        }

    def print_progress(self):
        """Print current progress."""
        stats = self.get_stats()
        print(
            f"\r[{stats['completed']}/{stats['total']}] "
            f"下载完成 | "
            f"失败: {stats['failed']} | "
            f"已下载: {stats['downloaded_mb']:.2f} MB | "
            f"速度: {stats['speed_mb']:.2f} MB/s | "
            f"耗时: {stats['elapsed']:.1f}s",
            end=""
        )


class RepoDownloader:
    """Multi-threaded GitHub repository downloader."""

    def __init__(
        self,
        max_workers: int = 5,
        timeout: int = 60,
        retry_count: int = 3,
        chunk_size: int = 8192
    ):
        """
        Initialize downloader.

        Args:
            max_workers: Maximum concurrent download threads (default: 5)
            timeout: Download timeout in seconds (default: 60)
            retry_count: Number of retry attempts (default: 3)
            chunk_size: Download chunk size in bytes (default: 8192)
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.retry_count = retry_count
        self.chunk_size = chunk_size

        # Browser-like headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/octet-stream",
        }

        self.progress = DownloadProgress()

    def _get_zip_url(self, repo_url: str, branch: str = "main") -> str:
        """
        Generate ZIP download URL for a repository.

        Args:
            repo_url: GitHub repository URL
            branch: Branch name (default: main)

        Returns:
            ZIP download URL
        """
        # Extract owner/repo from URL
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')

        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1].replace('.git', '')
            return f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

        return None

    def _download_file(
        self,
        url: str,
        output_path: str,
        repo_name: str
    ) -> bool:
        """
        Download a single file with retry logic.

        Args:
            url: Download URL
            output_path: Output file path
            repo_name: Repository name for display

        Returns:
            True if download succeeded
        """
        for attempt in range(self.retry_count):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    stream=True
                )

                # Handle different branches
                if response.status_code == 404 and attempt == 0:
                    # Try 'master' branch if 'main' fails
                    url = url.replace('/main.zip', '/master.zip')
                    continue

                response.raise_for_status()

                # Get file size
                file_size = int(response.headers.get('content-length', 0))

                # Download with progress
                downloaded = 0
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                self.progress.update(True, file_size)
                return True

            except requests.RequestException as e:
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"\n✗ {repo_name}: 下载失败 - {str(e)}")
                    self.progress.update(False)
                    return False

        return False

    def _download_single_repo(
        self,
        repo: Dict,
        output_dir: str
    ) -> Dict:
        """
        Download a single repository.

        Args:
            repo: Repository information dictionary
            output_dir: Output directory

        Returns:
            Download result dictionary
        """
        repo_name = repo.get('name', 'unknown')
        repo_url = repo.get('url', '')

        # Generate ZIP URL
        zip_url = self._get_zip_url(repo_url)
        if not zip_url:
            return {
                'repo': repo_name,
                'success': False,
                'error': 'Invalid repository URL'
            }

        # Create safe filename
        safe_name = repo_name.replace('/', '_')
        output_path = os.path.join(output_dir, f"{safe_name}.zip")

        # Skip if already downloaded
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 0:
                print(f"⊘ {repo_name}: 已存在，跳过")
                self.progress.update(True, file_size)
                return {
                    'repo': repo_name,
                    'success': True,
                    'path': output_path,
                    'skipped': True
                }

        # Download
        success = self._download_file(zip_url, output_path, repo_name)

        return {
            'repo': repo_name,
            'success': success,
            'path': output_path if success else None,
            'size': os.path.getsize(output_path) if success else 0
        }

    def download_repos(
        self,
        repositories: List[Dict],
        output_dir: str = "./downloads"
    ) -> List[Dict]:
        """
        Download multiple repositories concurrently.

        Args:
            repositories: List of repository dictionaries
            output_dir: Output directory (default: ./downloads)

        Returns:
            List of download results
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Initialize progress tracking
        self.progress.start(len(repositories))

        print(f"\n{'='*80}")
        print(f"开始下载 {len(repositories)} 个仓库")
        print(f"并发线程数: {self.max_workers}")
        print(f"输出目录: {os.path.abspath(output_dir)}")
        print(f"{'='*80}\n")

        results = []

        # Use ThreadPoolExecutor for concurrent downloads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_repo = {
                executor.submit(
                    self._download_single_repo,
                    repo,
                    output_dir
                ): repo
                for repo in repositories
            }

            # Process completed downloads
            for future in as_completed(future_to_repo):
                result = future.result()
                results.append(result)

                # Update progress display
                self.progress.print_progress()

        # Print final statistics
        self._print_summary(results, output_dir)

        return results

    def _print_summary(self, results: List[Dict], output_dir: str):
        """Print download summary."""
        stats = self.progress.get_stats()

        print(f"\n\n{'='*80}")
        print(f"下载完成!")
        print(f"{'='*80}")
        print(f"✓ 成功: {stats['completed']}")
        print(f"✗ 失败: {stats['failed']}")
        print(f"⏱  耗时: {stats['elapsed']:.2f} 秒")
        print(f"📦 总大小: {stats['downloaded_mb']:.2f} MB")
        print(f"🚀 平均速度: {stats['speed_mb']:.2f} MB/s")
        print(f"📁 保存位置: {os.path.abspath(output_dir)}")

        # List downloaded files
        if stats['completed'] > 0:
            print(f"\n下载的文件:")
            for result in results:
                if result.get('success') and not result.get('skipped'):
                    size_mb = result.get('size', 0) / (1024 * 1024)
                    print(f"  • {result['repo']}.zip ({size_mb:.2f} MB)")

    def download_with_progress_bar(
        self,
        repositories: List[Dict],
        output_dir: str = "./downloads"
    ) -> List[Dict]:
        """
        Download with tqdm progress bar (if available).

        Args:
            repositories: List of repository dictionaries
            output_dir: Output directory

        Returns:
            List of download results
        """
        try:
            from tqdm import tqdm
            return self._download_with_tqdm(repositories, output_dir)
        except ImportError:
            print("提示: 安装 tqdm 可以显示更美观的进度条")
            print("      pip install tqdm")
            return self.download_repos(repositories, output_dir)

    def _download_with_tqdm(
        self,
        repositories: List[Dict],
        output_dir: str
    ) -> List[Dict]:
        """Download with tqdm progress bar."""
        from tqdm import tqdm

        os.makedirs(output_dir, exist_ok=True)

        print(f"\n{'='*80}")
        print(f"开始下载 {len(repositories)} 个仓库")
        print(f"并发线程数: {self.max_workers}")
        print(f"{'='*80}\n")

        results = []

        # Create progress bar
        with tqdm(total=len(repositories), desc="下载进度", unit="repo") as pbar:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_repo = {
                    executor.submit(
                        self._download_single_repo,
                        repo,
                        output_dir
                    ): repo
                    for repo in repositories
                }

                for future in as_completed(future_to_repo):
                    result = future.result()
                    results.append(result)

                    # Update progress bar
                    repo_name = result.get('repo', 'unknown')
                    if result.get('success'):
                        pbar.set_postfix_str(f"✓ {repo_name}")
                    else:
                        pbar.set_postfix_str(f"✗ {repo_name}")
                    pbar.update(1)

        # Print summary
        success_count = sum(1 for r in results if r.get('success'))
        failed_count = len(results) - success_count

        print(f"\n{'='*80}")
        print(f"下载完成! 成功: {success_count}, 失败: {failed_count}")
        print(f"{'='*80}")

        return results


def download_trending_repos(
    json_file: str,
    output_dir: str = "./downloads",
    max_workers: int = 5,
    top_n: Optional[int] = None
) -> List[Dict]:
    """
    Download repositories from trending JSON file.

    Args:
        json_file: Path to trending JSON file
        output_dir: Output directory
        max_workers: Number of concurrent threads
        top_n: Only download top N repositories (None for all)

    Returns:
        List of download results
    """
    # Load repository data
    with open(json_file, 'r', encoding='utf-8') as f:
        repositories = json.load(f)

    # Filter top N if specified
    if top_n:
        repositories = repositories[:top_n]

    print(f"加载了 {len(repositories)} 个仓库")

    # Download
    downloader = RepoDownloader(max_workers=max_workers)
    return downloader.download_with_progress_bar(repositories, output_dir)


def main():
    """Command-line interface for the downloader."""
    import argparse

    parser = argparse.ArgumentParser(
        description="GitHub Repository Multi-threaded Downloader"
    )
    parser.add_argument(
        "json_file",
        help="Path to trending JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        default="./downloads",
        help="Output directory (default: ./downloads)"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=5,
        help="Number of concurrent threads (default: 5)"
    )
    parser.add_argument(
        "-n", "--top",
        type=int,
        help="Only download top N repositories"
    )

    args = parser.parse_args()

    # Check if file exists
    if not os.path.exists(args.json_file):
        print(f"错误: 文件不存在 - {args.json_file}")
        sys.exit(1)

    # Download
    results = download_trending_repos(
        json_file=args.json_file,
        output_dir=args.output,
        max_workers=args.workers,
        top_n=args.top
    )

    # Exit with status
    failed = sum(1 for r in results if not r.get('success'))
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
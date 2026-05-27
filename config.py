#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager

Features:
- Save/load default download directory
- Manage user preferences
- Persistent settings

Usage:
    from config import ConfigManager

    config = ConfigManager()
    config.set_download_dir("/path/to/downloads")
    print(config.get_download_dir())
"""

import os
import json
from pathlib import Path
from typing import Optional


class ConfigManager:
    """Manage user configuration and preferences."""

    def __init__(self, config_file: str = None):
        """
        Initialize config manager.

        Args:
            config_file: Path to config file (default: ~/.github_crawler/config.json)
        """
        if config_file is None:
            # Default config location
            home = Path.home()
            config_dir = home / ".github_crawler"
            config_dir.mkdir(exist_ok=True)
            self.config_file = config_dir / "config.json"
        else:
            self.config_file = Path(config_file)

        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载配置失败: {e}")
                return self._default_config()
        return self._default_config()

    def _default_config(self) -> dict:
        """Get default configuration."""
        return {
            "download_dir": str(Path.home() / "Downloads" / "github_repos"),
            "max_workers": 5,
            "rate_limit": 2.0,
            "timeout": 60,
            "retry_count": 3,
            "page_size": 10,
        }

    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存配置失败: {e}")

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """Set configuration value."""
        self.config[key] = value
        self.save()

    def get_download_dir(self) -> str:
        """Get default download directory."""
        return self.config.get("download_dir", str(Path.home() / "Downloads" / "github_repos"))

    def set_download_dir(self, path: str):
        """
        Set default download directory.

        Args:
            path: Directory path
        """
        # Expand user path
        path = os.path.expanduser(path)

        # Create directory if not exists
        os.makedirs(path, exist_ok=True)

        self.config["download_dir"] = path
        self.save()
        print(f"✓ 下载目录已设置为: {path}")

    def get_max_workers(self) -> int:
        """Get max download threads."""
        return self.config.get("max_workers", 5)

    def set_max_workers(self, workers: int):
        """Set max download threads."""
        self.config["max_workers"] = workers
        self.save()

    def get_rate_limit(self) -> float:
        """Get rate limit."""
        return self.config.get("rate_limit", 2.0)

    def set_rate_limit(self, limit: float):
        """Set rate limit."""
        self.config["rate_limit"] = limit
        self.save()

    def reset(self):
        """Reset to default configuration."""
        self.config = self._default_config()
        self.save()
        print("✓ 配置已重置为默认值")

    def show(self):
        """Display current configuration."""
        print("\n" + "=" * 60)
        print("⚙️  当前配置")
        print("=" * 60)
        print(f"  📁 下载目录: {self.get_download_dir()}")
        print(f"  🧵 并发线程: {self.get_max_workers()}")
        print(f"  ⏱️  请求间隔: {self.get_rate_limit()}s")
        print(f"  ⏰ 超时时间: {self.get('timeout', 60)}s")
        print(f"  🔄 重试次数: {self.get('retry_count', 3)}")
        print(f"  📄 每页数量: {self.get('page_size', 10)}")
        print(f"  📝 配置文件: {self.config_file}")
        print("=" * 60)


def select_directory(title: str = "选择目录", default: str = None) -> Optional[str]:
    """
    Interactive directory selection.

    Args:
        title: Display title
        default: Default directory

    Returns:
        Selected directory path or None
    """
    print(f"\n{'='*60}")
    print(f"📁 {title}")
    print(f"{'='*60}")

    if default:
        print(f"当前目录: {default}")

    print("\n常用目录:")
    print(f"  1. 桌面: {Path.home() / 'Desktop'}")
    print(f"  2. 下载: {Path.home() / 'Downloads'}")
    print(f"  3. 文档: {Path.home() / 'Documents'}")
    print(f"  4. 当前目录: {Path.cwd()}")
    print(f"  5. 自定义路径")

    print("\n输入选项 (1-5) 或直接输入路径:")

    try:
        choice = input("请选择: ").strip()

        if choice == '1':
            return str(Path.home() / "Desktop")
        elif choice == '2':
            return str(Path.home() / "Downloads")
        elif choice == '3':
            return str(Path.home() / "Documents")
        elif choice == '4':
            return str(Path.cwd())
        elif choice == '5':
            path = input("请输入路径: ").strip()
            return os.path.expanduser(path) if path else None
        elif choice:
            # Treat as path
            return os.path.expanduser(choice)
        else:
            return default

    except KeyboardInterrupt:
        print("\n已取消")
        return None


def main():
    """CLI for configuration management."""
    import argparse

    parser = argparse.ArgumentParser(
        description="GitHub Crawler Configuration Manager"
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # Show config
    subparsers.add_parser('show', help='显示当前配置')

    # Set download directory
    set_dir_parser = subparsers.add_parser('set-dir', help='设置下载目录')
    set_dir_parser.add_argument('path', nargs='?', help='目录路径')

    # Set max workers
    set_workers_parser = subparsers.add_parser('set-workers', help='设置并发线程数')
    set_workers_parser.add_argument('workers', type=int, help='线程数')

    # Set rate limit
    set_rate_parser = subparsers.add_parser('set-rate', help='设置请求间隔')
    set_rate_parser.add_argument('limit', type=float, help='间隔秒数')

    # Reset
    subparsers.add_parser('reset', help='重置为默认配置')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    config = ConfigManager()

    if args.command == 'show':
        config.show()
    elif args.command == 'set-dir':
        if args.path:
            config.set_download_dir(args.path)
        else:
            # Interactive selection
            path = select_directory("选择下载目录", config.get_download_dir())
            if path:
                config.set_download_dir(path)
    elif args.command == 'set-workers':
        config.set_max_workers(args.workers)
        print(f"✓ 并发线程数已设置为: {args.workers}")
    elif args.command == 'set-rate':
        config.set_rate_limit(args.limit)
        print(f"✓ 请求间隔已设置为: {args.limit}s")
    elif args.command == 'reset':
        config.reset()

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
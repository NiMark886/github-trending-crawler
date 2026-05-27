#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proxy Manager Module

Features:
- Proxy pool management
- Automatic proxy rotation
- Proxy health checking
- Support for HTTP/HTTPS/SOCKS proxies
- Proxy from file or API

Usage:
    from proxy import ProxyManager

    pm = ProxyManager()
    proxy = pm.get_proxy()
    requests.get(url, proxies=proxy)
"""

import os
import json
import random
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from logger import get_logger

logger = get_logger(__name__)


class Proxy:
    """Represents a single proxy."""

    def __init__(
        self,
        host: str,
        port: int,
        protocol: str = "http",
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.username = username
        self.password = password
        self.fail_count = 0
        self.last_used = 0
        self.response_time = 0
        self.is_working = True

    @property
    def url(self) -> str:
        """Get proxy URL."""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"

    @property
    def dict(self) -> Dict[str, str]:
        """Get proxy as dictionary for requests."""
        return {
            "http": self.url,
            "https": self.url
        }

    def __str__(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"

    def __repr__(self) -> str:
        return f"Proxy({self.url})"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "protocol": self.protocol,
            "username": self.username,
            "password": self.password,
            "fail_count": self.fail_count,
            "is_working": self.is_working,
            "response_time": self.response_time
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Proxy':
        """Create from dictionary."""
        proxy = cls(
            host=data["host"],
            port=data["port"],
            protocol=data.get("protocol", "http"),
            username=data.get("username"),
            password=data.get("password")
        )
        proxy.fail_count = data.get("fail_count", 0)
        proxy.is_working = data.get("is_working", True)
        proxy.response_time = data.get("response_time", 0)
        return proxy

    @classmethod
    def from_url(cls, url: str) -> 'Proxy':
        """Create from URL string."""
        # Parse URL: protocol://[user:pass@]host:port
        protocol = "http"
        if "://" in url:
            protocol, url = url.split("://", 1)

        username = None
        password = None

        if "@" in url:
            auth, url = url.rsplit("@", 1)
            if ":" in auth:
                username, password = auth.split(":", 1)

        if ":" in url:
            host, port = url.rsplit(":", 1)
            port = int(port)
        else:
            host = url
            port = 8080

        return cls(host, port, protocol, username, password)


class ProxyManager:
    """Manage proxy pool with health checking and rotation."""

    def __init__(
        self,
        proxy_file: Optional[str] = None,
        proxy_list: Optional[List[str]] = None,
        auto_rotate: bool = True,
        max_failures: int = 3,
        check_url: str = "https://httpbin.org/ip",
        check_timeout: int = 10
    ):
        """
        Initialize proxy manager.

        Args:
            proxy_file: Path to proxy list file (one proxy per line)
            proxy_list: List of proxy URLs
            auto_rotate: Automatically rotate proxies
            max_failures: Max failures before marking proxy as dead
            check_url: URL to test proxy connectivity
            check_timeout: Timeout for proxy check
        """
        self.auto_rotate = auto_rotate
        self.max_failures = max_failures
        self.check_url = check_url
        self.check_timeout = check_timeout

        self.proxies: List[Proxy] = []
        self.current_index = 0
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "proxy_switches": 0
        }

        # Load proxies
        if proxy_file:
            self.load_from_file(proxy_file)
        elif proxy_list:
            self.load_from_list(proxy_list)

        logger.info(f"代理管理器初始化完成 (代理数量: {len(self.proxies)})")

    def load_from_file(self, file_path: str):
        """
        Load proxies from file.

        Args:
            file_path: Path to proxy list file
        """
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"代理文件不存在: {file_path}")
            return

        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        proxy = Proxy.from_url(line)
                        self.proxies.append(proxy)
                    except Exception as e:
                        logger.warning(f"解析代理失败: {line} - {e}")

        logger.info(f"从文件加载了 {len(self.proxies)} 个代理")

    def load_from_list(self, proxy_list: List[str]):
        """
        Load proxies from list.

        Args:
            proxy_list: List of proxy URLs
        """
        for url in proxy_list:
            try:
                proxy = Proxy.from_url(url)
                self.proxies.append(proxy)
            except Exception as e:
                logger.warning(f"解析代理失败: {url} - {e}")

        logger.info(f"从列表加载了 {len(self.proxies)} 个代理")

    def add_proxy(self, proxy_url: str):
        """
        Add a proxy to the pool.

        Args:
            proxy_url: Proxy URL
        """
        try:
            proxy = Proxy.from_url(proxy_url)
            self.proxies.append(proxy)
            logger.info(f"添加代理: {proxy}")
        except Exception as e:
            logger.error(f"添加代理失败: {proxy_url} - {e}")

    def remove_proxy(self, proxy_url: str):
        """
        Remove a proxy from the pool.

        Args:
            proxy_url: Proxy URL to remove
        """
        self.proxies = [p for p in self.proxies if p.url != proxy_url]
        logger.info(f"移除代理: {proxy_url}")

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get a working proxy.

        Returns:
            Proxy dictionary for requests or None
        """
        if not self.proxies:
            logger.debug("没有可用代理")
            return None

        # Filter working proxies
        working_proxies = [p for p in self.proxies if p.is_working]

        if not working_proxies:
            # Reset all proxies if none are working
            logger.warning("所有代理都不可用，重置代理状态")
            for p in self.proxies:
                p.is_working = True
                p.fail_count = 0
            working_proxies = self.proxies

        if self.auto_rotate:
            # Round-robin selection
            proxy = working_proxies[self.current_index % len(working_proxies)]
            self.current_index += 1
        else:
            # Random selection
            proxy = random.choice(working_proxies)

        proxy.last_used = time.time()
        self.stats["total_requests"] += 1

        logger.debug(f"使用代理: {proxy}")
        return proxy.dict

    def report_success(self, proxy_url: str, response_time: float = 0):
        """
        Report successful proxy use.

        Args:
            proxy_url: Proxy URL
            response_time: Response time in seconds
        """
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.fail_count = 0
                proxy.response_time = response_time
                proxy.is_working = True
                self.stats["successful_requests"] += 1
                break

    def report_failure(self, proxy_url: str):
        """
        Report failed proxy use.

        Args:
            proxy_url: Proxy URL
        """
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.fail_count += 1
                self.stats["failed_requests"] += 1

                if proxy.fail_count >= self.max_failures:
                    proxy.is_working = False
                    logger.warning(f"代理已失效: {proxy} (失败次数: {proxy.fail_count})")
                break

    def check_proxy(self, proxy: Proxy) -> bool:
        """
        Check if a proxy is working.

        Args:
            proxy: Proxy to check

        Returns:
            True if proxy is working
        """
        try:
            start_time = time.time()
            response = requests.get(
                self.check_url,
                proxies=proxy.dict,
                timeout=self.check_timeout
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                proxy.response_time = response_time
                proxy.is_working = True
                proxy.fail_count = 0
                logger.debug(f"代理可用: {proxy} (响应时间: {response_time:.2f}s)")
                return True

        except Exception as e:
            logger.debug(f"代理不可用: {proxy} - {e}")

        proxy.is_working = False
        return False

    def check_all(self):
        """Check all proxies and remove dead ones."""
        logger.info(f"检查所有代理 ({len(self.proxies)} 个)...")

        working = []
        for proxy in self.proxies:
            if self.check_proxy(proxy):
                working.append(proxy)
            else:
                logger.info(f"移除不可用代理: {proxy}")

        self.proxies = working
        logger.info(f"可用代理: {len(self.proxies)} 个")

    def get_stats(self) -> Dict:
        """Get proxy usage statistics."""
        working_count = sum(1 for p in self.proxies if p.is_working)

        return {
            **self.stats,
            "total_proxies": len(self.proxies),
            "working_proxies": working_count,
            "dead_proxies": len(self.proxies) - working_count
        }

    def print_stats(self):
        """Print proxy statistics."""
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("📊 代理统计")
        print("=" * 60)
        print(f"  总代理数: {stats['total_proxies']}")
        print(f"  可用代理: {stats['working_proxies']}")
        print(f"  不可用代理: {stats['dead_proxies']}")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  成功请求: {stats['successful_requests']}")
        print(f"  失败请求: {stats['failed_requests']}")
        print(f"  代理切换: {stats['proxy_switches']}")
        print("=" * 60)

    def save_to_file(self, file_path: str):
        """
        Save proxies to file.

        Args:
            file_path: Path to save proxy list
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            for proxy in self.proxies:
                f.write(f"{proxy.url}\n")

        logger.info(f"代理已保存到: {file_path}")

    def save_to_json(self, file_path: str):
        """
        Save proxy details to JSON.

        Args:
            file_path: Path to save JSON file
        """
        data = {
            "proxies": [p.to_dict() for p in self.proxies],
            "stats": self.get_stats()
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"代理详情已保存到: {file_path}")


class FreeProxyFetcher:
    """Fetch free proxies from various sources."""

    @staticmethod
    def fetch_from_api() -> List[str]:
        """
        Fetch free proxies from API.

        Returns:
            List of proxy URLs
        """
        proxies = []

        # List of free proxy APIs
        apis = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        ]

        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    for line in response.text.strip().split('\n'):
                        line = line.strip()
                        if line and ':' in line:
                            proxies.append(f"http://{line}")
            except Exception as e:
                logger.warning(f"获取代理失败: {api_url} - {e}")

        logger.info(f"获取了 {len(proxies)} 个免费代理")
        return proxies

    @staticmethod
    def fetch_from_file(file_path: str) -> List[str]:
        """
        Read proxies from file.

        Args:
            file_path: Path to proxy file

        Returns:
            List of proxy URLs
        """
        proxies = []
        path = Path(file_path)

        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxies.append(line)

        return proxies


# Example usage
if __name__ == "__main__":
    # Create proxy manager with manual proxies
    proxy_list = [
        "http://proxy1:8080",
        "http://proxy2:8080",
        "http://user:pass@proxy3:8080",
    ]

    pm = ProxyManager(proxy_list=proxy_list)

    # Get a proxy
    proxy = pm.get_proxy()
    print(f"使用代理: {proxy}")

    # Report success
    pm.report_success(proxy['http'], response_time=0.5)

    # Print stats
    pm.print_stats()

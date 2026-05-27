# GitHub Trending Crawler

Win11 风格的 GitHub 热门仓库爬虫，支持 GUI 和 CLI 两种模式。

## 功能

- **热榜浏览** — 日榜 / 周榜 / 月榜，支持语言筛选
- **仓库搜索** — 按关键词搜索 GitHub 仓库
- **仓库详情** — 点击查看 README、Issues、评论
- **镜像加速下载** — 多源自动切换（ghfast.top / ghproxy.cn / 直连）
- **翻译功能** — Google Translate / 百度翻译，中英互译
- **多语言界面** — 中文 / English / 日本語 / 한국어 / Français / Deutsch / Español
- **批量下载** — 多线程并发，实时进度条，支持终止
- **GitHub Token** — 可选配置，提升 API 速率限制

## 截图

Win11 资源管理器风格，左侧导航栏 + 白色卡片布局。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动 GUI

```bash
python gui.py
```

### 命令行模式

```bash
python github_trending_crawler.py
```

### 打包为 exe

```bash
pip install pyinstaller
python -m PyInstaller github_crawler.spec
```

生成的 exe 在 `dist/` 目录下。

## 配置

在 GUI 的「设置」页面可配置：

| 配置项 | 说明 |
|--------|------|
| 下载目录 | 仓库 ZIP 保存位置 |
| 并发线程 | 下载线程数 (1-20) |
| 请求间隔 | API 请求间隔 (秒) |
| GitHub Token | 可选，提升 API 速率 10→30 次/分 |
| 界面语言 | 7 种语言可选 |
| 翻译引擎 | Google Translate / 百度翻译 |
| 百度 App ID / Key | 百度翻译 API 凭证 (免费申请) |

配置文件保存在 `~/.github_crawler/config.json`。

## 翻译功能

- **Google Translate**：免费，无需配置，需能访问 Google
- **百度翻译**：国内可用，需在 [fanyi.baidu.com](https://fanyi.baidu.com) 申请 App ID

在仓库详情页的 README 下方，点击「中→英」「英→中」「显示原文」即可翻译。

## 项目结构

```
├── gui.py                  # GUI 主界面 (Win11 风格)
├── github_trending_crawler.py  # 热榜爬虫核心
├── search.py               # 仓库搜索模块
├── config.py               # 配置管理
├── downloader.py           # 下载模块
├── requirements.txt        # Python 依赖
├── github_crawler.spec     # PyInstaller 打包配置
├── icon.ico                # 应用图标
└── LICENSE                 # MIT License
```

## 依赖

- requests
- beautifulsoup4
- lxml
- deep-translator (翻译功能)

## 法律声明

本项目仅供学习交流使用。请遵守 GitHub 的服务条款和 robots.txt。

# Ought Gather 测试指南

本文档教你如何运行、编写和维护本项目的测试。

## 快速开始

### 安装依赖

本项目的所有测试依赖已直接包含在 `requirements.txt` 中：

```bash
pip install -r requirements.txt
```

其中包含的测试核心依赖有：
- `pytest` — 测试框架
- `pytest-mock` — mock 辅助工具
- `pytest-cov` — 代码覆盖率统计工具

### 运行测试

```bash
# 运行所有测试（默认会自动运行覆盖率统计，并显示未覆盖的行数）
python -m pytest tests/

# 显示详细信息
python -m pytest tests/ -v

# 只运行某个文件
python -m pytest tests/test_config.py -v

# 只运行某个测试类
python -m pytest tests/test_config.py::TestTitleConfig -v

# 只运行某个测试方法
python -m pytest tests/test_config.py::TestTitleConfig::test_simple_time_placeholder -v

# 遇到失败时立即停止
python -m pytest tests/ -x

# 显示 print 输出（默认被捕获）
python -m pytest tests/ -s

# 临时禁用覆盖率统计（调试单项测试时可加快执行速度）
python -m pytest tests/ --no-cov
```

## 测试文件结构

```
tests/
├── __init__.py
├── conftest.py              # 共享 fixtures
├── test_config.py           # 配置加载和验证
├── test_content_processor.py # 内容处理规则（清理、剔除等）
├── test_cover_generator.py  # 书籍封面生成及文字叠加效果
├── test_dedup_tracker.py    # 去重追踪器（缓存与记录清理逻辑）
├── test_epub_compliance.py  # EPUB 合规性验证（基于 epubcheck.jar）
├── test_epub_helpers.py     # EPUB 辅助工具（XML 节点操作、章节元数据等）
├── test_fetchers.py         # 各种内容抓取器（mock HTTP，支持 RSS、Mail、Web、Trending/LLM 等）
├── test_helpers.py          # 工具函数（时间戳计算、时间格式化等）
├── test_image_bugs.py       # 特殊图片 Bug 及边界场景测试
├── test_image_processor.py  # 图片压缩、过滤与缩放
├── test_integration.py      # 完整工作流集成测试
├── test_mailer.py           # 邮件发送器（SMTP 传输与 TLS/SSL 校验）
├── test_main.py             # 主控制流/编排逻辑（main.py 的 Mock 与异常逻辑）
├── test_raindropio_fetcher.py # Raindrop.io 书签抓取
├── test_uploader.py         # 备份上传器（WebDAV 接口）
└── test_weather_fetcher.py  # 天气源数据抓取与解析
```

## 核心测试概念

### 1. pytest 基础

每个测试是一个函数，名字以 `test_` 开头。使用类组织相关测试。

### 2. Fixtures（测试夹具）

Fixtures 是 pytest 的核心，在 `conftest.py` 中定义，提供测试所需的依赖。

**常用的 fixtures:**

| Fixture | 描述 |
| :--- | :--- |
| `rss_source` | 标准 RSS 内容源 |
| `rss_full_text_source` | 启用全文抓取的 RSS 内容源 |
| `mail_source` | 标准邮件内容源 |
| `web_source` | 标准网页内容源 |
| `trending_source` | 标准 Trending 内容源（使用 LLM 分析） |
| `tmp_dir` | 临时目录，测试后自动清理 |
| `tmp_config_file` | 自动加载并写入最小化测试配置的临时配置文件路径 |
| `sample_html` | 用于测试内容处理的 HTML 片段 |

在测试中使用：

```python
def test_rss_fetch(rss_source):  # pytest 自动注入 fixture
    assert rss_source.type == "rss"
```

### 3. Mock（模拟外部依赖）

本项目涉及大量外部依赖（HTTP 请求、API 调用、文件系统），必须用 `unittest.mock` 或 `pytest-mock` 隔离。

#### 3.1 模拟 HTTP 请求

使用 `@patch` 替换外部调用或 `httpx.Client`。如果源码在函数内部局部导入模块，直接 patch 模块即可。

#### 3.2 模拟环境变量

```python
@patch.dict("os.environ", {"TESTMAIL_APP_API_KEY": "test_key_123"})
def test_with_api_key():
    # 测试期间环境变量已设置，结束后自动恢复
    pass
```

### 4. 特殊测试场景

#### 4.1 集成测试 (Integration Testing)
`tests/test_integration.py` 包含了完整的流程测试（抓取 -> 内容处理 -> EPUB 生成），用于验证组件间的交互。这是回归测试的关键。

#### 4.2 图片处理与 Bug 测试
`tests/test_image_bugs.py` 和 `tests/test_image_processor.py` 处理复杂的图片逻辑，包括：
- Mock 图片下载与压缩。
- 验证图片尺寸限制逻辑。
- 测试特殊场景（如 lazy loading 属性移除、`<graphic>` 标签转 `<img>`）。

#### 4.3 插件测试
`tests/test_fetchers.py` 演示了如何测试动态注册的抓取器插件：

```python
def test_custom_fetcher_auto_registration():
    # 自定义抓取器只需继承 BaseFetcher 并设置 type_name
    class DummyCustomFetcher(BaseFetcher):
        type_name = "dummy_custom"
    
    assert get_fetcher_class("dummy_custom") is DummyCustomFetcher
```

#### 4.4 EPUB 合规性验证
`tests/test_epub_compliance.py` 使用 `epubcheck` 验证生成的 EPUB。
- **环境要求**: 必须安装 Java 运行时。
- **配置**: `epubcheck.jar` 必须放置在项目根目录下的 `epubcheck/` 文件夹中。
- 测试会自动检测环境，如果缺失则跳过测试。

下载[epubcheck](https://github.com/w3c/epubcheck)

#### 4.5 覆盖率测试 (Coverage Testing)
本项目在 `pytest.ini` 中默认配置了 `pytest-cov`，会在每次测试运行结束时，自动在终端输出当前 `src/` 目录下各文件的覆盖率详情。
- 如果想要生成图形化的 HTML 覆盖率报告，可以运行：
  ```bash
  python -m pytest tests/ --cov-report=html
  ```
  运行后，会在项目根目录下生成 `htmlcov/` 目录，用浏览器打开其下的 `index.html` 即可直观查看哪些代码行未被测试覆盖。

## 最佳实践

1. **测试要快**：避免真实网络请求和磁盘 I/O。
2. **测试要独立**：每个测试不依赖执行顺序。
3. **保持测试组织**：按模块对应关系（如 `src/config.py` → `tests/test_config.py`）。
4. **验证行为而非实现**：测试预期结果，而非内部中间状态。

## 调试测试

1. **查看详细输出**: `python -m pytest tests/ -v -s`
2. **打断点**: 使用 `breakpoint()`。
3. **简短回溯**: `python -m pytest tests/ --tb=short`

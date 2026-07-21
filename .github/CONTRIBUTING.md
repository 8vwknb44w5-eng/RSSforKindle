# Contributing to Ought Gather (贡献指南)

English | [简体中文](#简体中文)

Thank you for your interest in contributing to Ought Gather! We welcome contributions of all forms—bug reports, documentation improvements, new features, and new content fetchers.

To maintain high code quality and compatibility, please read and follow this guide before making a contribution.

---

## English Guide

### 1. Code of Conduct & Core Principles
- **Respect Boundaries:** We follow standard community cooperation etiquette. Please treat others with respect.
- **Privacy & Security First:** Never commit private configuration files, API keys, or database credentials. Ensure mock data is used for testing.

### 2. Architecture & Implementation Guidelines

Ought Gather adheres to a clean, decoupled architecture. Any contributions must conform to these strict architectural guidelines:

#### A. Plugin Architecture Mandate (Extremely Important)
All content sources must be implemented as pluggable modules under `src/fetchers/`.
- **Inheritance:** Your new fetcher must inherit from `BaseFetcher` (defined in `src/fetchers/base.py`).
- **Auto-registration:** Fetchers register automatically via `__init_subclass__` and are resolved dynamically at runtime using `get_fetcher_class(source.type)`.
- **No Hardcoded References:** Do not add specialized, conditional, or hardcoded references to specific fetchers outside of the `src/fetchers/` directory. 
  - ❌ *Never* add logic like `if type == "my_new_fetcher"` in `src/config.py`, `src/epub/toc.py`, or `src/epub/generator.py`.
- **Decoupled Settings:** Keep fetcher-specific configuration validation and defaults inside your fetcher class. Use the generic `metadata` dictionary for any fetcher-specific custom parameters. Do not add fetcher-specific top-level properties to `ContentSource`.
- **Decoupled Formatting & Styling:** Any special title formatting, custom CSS classes (e.g., `.my-item`), or layout requirements must be handled within the fetcher or using generic extensible hooks.

#### B. Timezones & Dates
- **Beijing Time (UTC+8):** All timestamps, datetime calculations, and cover generation must use Beijing Time (UTC+8).
- **Helper:** Always use `src/utils/helpers.py:get_now()` to retrieve the current date and time. Do not use raw `datetime.now()` without specifying the correct timezone.

#### C. EPUB 3.0 Compliance
- **Compliance Rules:** All output EPUBs must be fully compliant with EPUB 3.3.
- **Identifiers & Structure:** The directory structure must use the standard `EPUB/` folder name (to avoid OCF RSC-026 warning). It must include both EpubNcx (`toc.ncx` for EPUB 2 compatibility) and EpubNav (`nav.xhtml` for EPUB 3 compliance) items. XHTML files must have valid namespaces and must not be empty.

---

### 3. Setup & Development Environment
1. Fork the repository and clone your fork locally.
2. Initialize and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies (including dev/test libraries):
   ```bash
   pip install -r requirements.txt
   ```
4. Verify tests are passing:
   ```bash
   python3 -m pytest tests/
   ```

### 4. Writing Tests & Validation
We enforce **100% test verification** for all new features and bug fixes.
- **New Features:** If you add a new fetcher or processor, you **must** add a corresponding test file under `tests/` (e.g., `tests/test_my_new_fetcher.py`).
- **Bug Fixes:** Provide a test case that reproduces the bug, then verify that your fix resolves it.
- **Coverage:** Run tests with coverage checking (enabled by default when running pytest). Ensure your new code is properly covered.

### 5. Git Commit & Pull Request Guidelines
- **Target Branch:** Make your Pull Request against the `main` branch.
- **Atomic Commits:** Keep commits small, descriptive, and atomic.
- **Draft PRs:** If your work is not ready yet, open it as a Draft Pull Request.

---

## 简体中文

感谢您对 Ought Gather 项目的关注！我们非常欢迎来自社区的各种贡献：从纠正拼写错误、改善文档、提交 Bug 修复，到开发新的抓取插件和处理器。

为了维护代码库的高质量和长期可维护性，请在发起 Pull Request (PR) 之前仔细阅读以下指南。

---

### 1. 核心设计原则

Ought Gather 遵循高内聚、低耦合的设计哲学。所有代码合并必须符合以下核心约束：

#### A. 插件化架构规范 (非常重要)
所有的新内容源（Fetcher）必须以**插件**的形式实现，严禁硬编码。
- **继承体系**：所有 fetcher 必须在 `src/fetchers/` 目录下实现，且继承自 `BaseFetcher`。
- **自动注册**：Fetcher 通过基类的 `__init_subclass__` 机制实现动态自动注册，在运行时通过 `get_fetcher_class(source.type)` 进行动态调度。
- **严禁外部硬编码耦合**：禁止在 `src/fetchers/` 目录之外添加针对特定抓取器的特殊、硬编码或条件判断代码。
  - ❌ *严禁*在 `src/config.py`、`src/epub/toc.py` 或 `src/epub/generator.py` 中编写 `if type == "my_new_fetcher"` 这样的脏代码。
- **配置解耦**：抓取器特有的配置验证、默认值和逻辑应该封装在抓取器类内部。如有特殊的抓取参数，应统一放置在 `metadata` 字典中，严禁在 `ContentSource` 的顶层添加特定的属性字段。
- **样式解耦**：任何特定的标题格式化、自定义 CSS 样式（如 `.my-style`）或布局逻辑，必须在抓取器内部处理，或使用通用可扩展钩子。

#### B. 统一时区约束
- **北京时间 (UTC+8)**：由于该项目主要面向中文及东八区读者，所有的日期、时间戳计算、封面叠加字样都必须使用北京时间。
- **规范方法**：请统一使用 `src/utils/helpers.py:get_now()` 获取当前时间。严禁使用不带时区信息的原生 `datetime.now()`。

#### C. EPUB 3.0 合规标准
- 生成的 EPUB 必须通过 `epubcheck` 最新规范（EPUB 3.3 标准）。
- 文件夹命名必须为标准的 `EPUB` (避免出现 OCF RSC-026)。
- 必须同时包含 EpubNcx (`toc.ncx`) 和 EpubNav (`nav.xhtml`)。封面及各个 XHTML 页面不可为空，所有 XHTML 标签必须正确闭合。

---

### 2. 开发环境准备
1. Fork 本仓库并克隆到本地。
2. 建议使用 Python 3.11+，并创建虚拟环境：
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```
3. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
4. 运行现有测试套件，确保环境无误：
   ```bash
   python -m pytest tests/
   ```

---

### 3. 测试与验证标准

我们秉持**测试驱动**的理念。任何功能的增加或问题的修复都不能缺少测试：
- **新增内容源/处理器**：必须在 `tests/` 下建立对应的测试文件（如 `tests/test_xxx_fetcher.py`），对各种正常、异常、边界输入进行完整覆盖。
- **修复 Bug**：必须先在测试用例中重现该 Bug 失败的状态，然后应用修复，确保测试通过，以防止后续重构时出现回归。
- **执行命令**：
  ```bash
  # 运行全部测试并输出覆盖率统计
  python -m pytest tests/
  ```

---

### 4. 提交规范

1. **Commit Message**：请使用清晰、富有解释性的提交说明，推荐使用常规提交规范（Conventional Commits）：
   - `feat(fetcher): add webdev fetcher`
   - `fix(image): repair jpeg compression size boundaries`
   - `docs(op): update docker container runbooks`
2. **安全防护**：在提交前，请使用 `git diff` 仔细核对，**绝对不允许**将本地调试用的 `config.json` 真实内容、邮箱授权码、API KEY 提交至公共仓库。

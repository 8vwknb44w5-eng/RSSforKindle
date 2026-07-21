## Description (描述)

Please provide a brief description of the changes introduced by this Pull Request, including the problem being solved or the new feature added.
请简要描述此 Pull Request 引入的更改，包括正在解决的问题或新添加的功能。

---

## Type of Change (变更类型)

Please check the options that apply to this PR / 请勾选适用于此 PR 的选项:

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue) / Bug 修复
- [ ] ✨ New feature (non-breaking change which adds functionality) / 新增功能
- [ ] 🛠️ Refactoring (improving existing codebase structure without behavioral changes) / 代码重构
- [ ] 📝 Documentation update / 文档更新
- [ ] 🚦 Test suite improvement or additions / 测试套件改进或增加
- [ ] 🚀 Other (please describe) / 其他 (请说明)

---

## Architecture Compliance Checklists (架构合规性自查)

Ought Gather has strict architectural boundaries. Please confirm that your submission complies with the following guidelines:
Ought Gather 拥有严格的架构边界，请确认您的提交符合以下指南：

### 1. Plugin Architecture Mandate (插件化规范)
- [ ] If adding a new fetcher, it inherits from `BaseFetcher` and is located in `src/fetchers/`.
  如果添加了新的抓取器，它继承自 `BaseFetcher` 且位于 `src/fetchers/`。
- [ ] There are **NO hardcoded or conditional references** to this fetcher outside of `src/fetchers/` (e.g., in `src/config.py`, `src/epub/toc.py`, or `src/epub/generator.py`).
  在 `src/fetchers/` 目录之外 **没有任何硬编码或条件判断** 针对该抓取器（例如在 `src/config.py`、`src/epub/toc.py` 或 `src/epub/generator.py` 中）。
- [ ] Fetcher-specific options are located in the generic `metadata` dictionary and validated within the class. No new top-level properties have been added to `ContentSource`.
  抓取器专属的选项位于通用的 `metadata` 字典中，并在类内部进行验证。没有向 `ContentSource` 添加新的顶层属性。
- [ ] Formatting and custom styling/classes are encapsulated inside the fetcher or utilize existing hooks.
  格式化和自定义样式/类被封装在抓取器内部，或使用现有的钩子。

### 2. Timezone Mandate (统一时区规范)
- [ ] All dates and timestamp calculations utilize Beijing Time (UTC+8) via `src/utils/helpers.py:get_now()`.
  所有的日期和时间戳计算均通过 `src/utils/helpers.py:get_now()` 使用北京时间 (UTC+8)。

---

## Verification & Testing Checklist (验证与测试自查)

- [ ] I have run the existing tests using `python -m pytest tests/` and all passed without errors.
  我已使用 `python -m pytest tests/` 运行现有测试，并且全部通过无误。
- [ ] I have added new test cases under `tests/` to verify my changes (mandatory for new features/bug fixes).
  我已在 `tests/` 下添加了新的测试用例来验证我的更改（新增功能/Bug 修复必须提供）。
- [ ] Tests cover normal, error, and boundary inputs.
  测试用例覆盖了正常、异常和边界输入。
- [ ] I have verified that no private credentials (API keys, SMTP passwords, custom configs) are committed or exposed in this PR.
  我已确认在此 PR 中没有提交或暴露任何私有凭证（API 密钥、SMTP 密码、自定义配置）。

---
name: 🐛 Bug report (缺陷报告)
about: Create a report to help us improve Ought Gather / 创建一份报告以帮助我们改进 Ought Gather
title: '[BUG] '
labels: bug
assignees: ''

---

**Please describe the bug / 请描述这个 Bug**
A clear and concise description of what the bug is.
清晰且简要地描述这个 Bug 是什么。

**To Reproduce / 如何复现**
Steps to reproduce the behavior / 复现该行为的步骤:
1. Go to '...'
2. Run command '...'
3. See error '...'

**Expected Behavior / 期望行为**
A clear and concise description of what you expected to happen.
清晰且简要地描述您期望发生的事情。

**Environment Details / 环境信息**
- OS (操作系统): [e.g. Linux Ubuntu 22.04, macOS Darwin, Windows 11]
- Python Version (Python 版本): [e.g. 3.11.4]
- Deployment Mode (部署模式): [e.g. GitHub Actions, Docker, Local cron]
- Kindle Device (Kindle 设备型号, optional): [e.g. Kindle Paperwhite 11]

**Configuration (Masked) / 配置文件 (请隐去密码与密钥!)**
Please paste your `config.json` here. **CRITICAL: Redact or replace your SMTP_PASSWORD, API_KEYS, and other secrets!**
请在此处粘贴您的 `config.json`。**重要提示：请隐去或替换您的 SMTP 密码、API 密钥等隐私信息！**

```json
{
  "title": {
    "text": "{Daily News {time}}"
  },
  "body": [
    // Paste content here ...
  ]
}
```

**Relevant Logs or Error Output / 相关的运行日志或报错信息**
Please paste any relevant error logs or tracebacks here.
请在此处粘贴任何相关的错误日志或回溯堆栈。

```text
[Paste logs here]
```

**Additional Context / 补充信息**
Add any other context about the problem here (e.g. EPUBCheck warnings, specific feed URL that failed).
在此处添加关于该问题的任何其他上下文信息（例如 EPUBCheck 警告、导致失败的特定 feed 链接）。

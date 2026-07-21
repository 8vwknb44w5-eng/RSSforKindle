# Security Policy (安全策略)

English | [简体中文](#简体中文)

## English Version

### Reporting a Vulnerability
**DO NOT create public GitHub Issues for security vulnerabilities or credential exposures.**

If you discover a security vulnerability (such as a potential leak of API keys, vulnerabilities in SMTP mail-relay handling, or sensitive data exposure), please report it responsibly:
1. Contact the maintainer privately by emailing: [liusonwood@outlook.com](mailto:liusonwood@outlook.com)
2. Include the following details in your report:
   - A description of the vulnerability.
   - Step-by-step instructions (with proof-of-concept code, if available) to reproduce the issue.
   - Potential impact of the exploit.
3. We will acknowledge receipt of your report within 48 hours and work with you to patch the issue before any public disclosure is made.

---

### Security Best Practices for Users
Ought Gather handles various third-party integration keys (e.g., SMTP credentials, OpenRouter, Raindrop, Testmail). To protect your secrets:
- **Never commit your `config.json` containing active API keys or SMTP passwords.**
- **Use `CONFIG_JSON` Environment Variable:** In GitHub Actions, store your complete configuration JSON within a Repository Secret named `CONFIG_JSON`.
- **Restrict Token Scopes:** When creating Personal Access Tokens (PAT) or third-party keys, always grant the minimum required scopes (least privilege principle).

---

## 简体中文

### 受支持的版本

### 报告安全漏洞
**请勿针对安全漏洞或凭证泄露创建公开的 GitHub Issue。**

如果您发现安全漏洞（例如 API 密钥可能泄露、SMTP 邮件中转处理漏洞或敏感数据暴露），请以负责任的方式报告：
1. 通过电子邮件私下联系维护者：[liusonwood@outlook.com](mailto:liusonwood@outlook.com)
2. 在报告中包含以下详细信息：
   - 漏洞的详细描述。
   - 复现该漏洞的逐步操作说明（如果有概念验证 Proof-of-concept 代码，请一并附上）。
   - 该漏洞可能造成的安全影响。
3. 我们将在 48 小时内确认收到您的报告，并在公开披露之前与您合作修复该问题。

---

### 用户安全最佳实践
Ought Gather 处理多种第三方集成密钥（例如 SMTP 凭证、OpenRouter、Raindrop、Testmail）。为了保护您的隐私：
- **绝对不要将包含真实 API 密钥或 SMTP 密码的 `config.json` 提交到公开的公共仓库。**
- **使用 `CONFIG_JSON` 环境变量**：在 GitHub Actions 中，将您完整的配置 JSON 存储在名为 `CONFIG_JSON` 的 Repository Secret 中。
- **限制 Token 范围**：创建个人访问令牌（PAT）或第三方 API 密钥时，请始终授予所需的最小权限（最小特权原则）。

# anki-card-formatter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Best practices, formatting standards, and an automated processing pipeline for generating and updating Anki cards with **LaTeX formulas (MathJax)**, **Markdown tables**, and **fenced/inline code blocks**.

旨在彻底解决脚本或 AI Agent 向 Anki（通过 AnkiConnect 等 API）批量导入/更新卡片时常见的：
- **手机端（AnkiMobile / AnkiDroid）公式不渲染**（误用内部 `<anki-mathjax>` 标签导致移动端 Webview 无法捕获定界符）
- **HTML/CSS 注入失控**（`<style>` 或正文中充斥 `<br>` 标签破坏移动端 DOM 树与 MathJax 引擎）
- **Markdown 表格源码暴露**（表格紧贴段落文本缺乏物理空行导致 `tables` 扩展失效）
- **代码块换行折叠**（代码全部挤在单行无法阅读）
- **Markdown 破坏 LaTeX 表达式**（下划线 `_`、星号 `*`、反斜杠 `\` 被误解析为 Markdown 斜体或强调）
- **公式中混用裸 Unicode 希腊字母**（非 ASCII 字符配合 `\quad` 等宏命令导致公式解析崩溃）

---

## ⚡ 快速安装 (Quick Install)

本项目原生支持标准的 **Agent Skills 协议**（兼容 Cursor、Claude Code、Codex、Antigravity 等主流 AI Agent 工具）。

### 方式 1：通过官方 Skills CLI（推荐，一键安装给各 AI 工具）

无需手动下载，直接使用官方标准 `npx skills`：

```bash
# 自动检测并安装到当前项目 Agent 目录（如 .gemini/skills, .agents/skills）
npx skills add mintonight/anki-card-formatter -y

# 全局安装（所有项目通用）：
npx skills add mintonight/anki-card-formatter -g -y

# 指定安装给特定 Agent（如 claude-code, cursor, codex 等）：
npx skills add mintonight/anki-card-formatter --agent claude-code cursor
```

### 方式 2：通过 NPX 一键脚本安装

```bash
# 自动在当前项目创建技能文件
npx github:mintonight/anki-card-formatter install

# 或全局安装至用户主目录 (~/.gemini/, ~/.codex/ 等)
npx github:mintonight/anki-card-formatter install -g
```

---

## 核心特性与跨平台方案

- 📐 **全平台（电脑端 + 移动端）官方标准 MathJax**：
  - **行内公式**：`\( formula \)`（如 `\( E = mc^2 \)`）
  - **独立成行**：`\[ formula \]`（如 `\[ \sum_{i=1}^n i \]`）
  - **严禁手写 `<anki-mathjax>`**：`<anki-mathjax>` 是桌面版富文本编辑器的内部私有 DOM。移动端 Webview 内置 MathJax 脚本只识别 `\(` 与 `\[` 标准定界符，直接写入该标签会导致移动端全部公式无法渲染。
  - **规范 LaTeX 宏命名**：统一使用标准 LaTeX 命令（如 `\Psi`、`\psi`、`\alpha`）替代原始 Unicode 符号。
- 📊 **Markdown 表格自动化避坑**：
  - 自动检测并补齐表格前后物理空行（`\n\n`），彻底解决 CommonMark / Python-Markdown 因段落紧贴导致表格扩展失效的问题。
- 🛡️ **三步占位隔离保护流水线**：
  - 在 Markdown 解析前提取多行代码块、行内代码与数学公式，生成唯一哈希占位符，安全转换 Markdown 后原样恢复，杜绝语法撕裂。
- 🎨 **GitHub 浅色高质感样式**：
  - 代码块预设 GitHub 风格（浅灰底 `#f6f8fa` + 细描边 `#d0d7de` + 等宽字体 + `white-space: pre !important;`）。
  - 表格样式预设轻量质感（浅灰表头 `#f6f8fa` + 斑马线底色 + 紧凑内边距）。

---

## 完整规范与 Python 流水线

规范细节、避坑清单及开箱即用的完整 Python 实现详见 [SKILL.md](./SKILL.md)。

---

## 开源协议

[MIT License](./LICENSE)

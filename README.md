# anki-card-formatter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Best practices, formatting standards, and an automated processing pipeline for generating and updating Anki cards with **LaTeX formulas (MathJax)** and **fenced/inline code blocks**.

旨在解决脚本或 AI Agent 向 Anki（通过 AnkiConnect 等 API）批量导入/更新卡片时常见的：
- **代码块换行丢失**（全部挤在单行无法阅读）
- **Markdown 破坏 LaTeX 公式**（下划线 _、星号 *、反斜杠 \ 被误解析为 Markdown 语法）
- **自定义 HTML 块内裸留 $...$ 导致 MathJax 无法渲染**
- **在数学公式中直接混用 Unicode 希腊字母导致解析崩溃**

---

## ⚡ 快速安装 (Quick Install)

本项目原生支持标准的 **Agent Skills 协议**（兼容 Cursor、Claude Code、Codex、Antigravity 等主流 AI Agent 工具）。

### 方式 1：通过官方 Skills CLI（推荐，一键安装给各 AI 工具）

无需手动下载，直接使用官方标准 
px skills：

`ash
# 自动检测并安装到当前项目 Agent 目录（如 .gemini/skills, .agents/skills）
npx skills add mintonight/anki-card-formatter -y

# 全局安装（所有项目通用）：
npx skills add mintonight/anki-card-formatter -g -y

# 指定安装给特定 Agent（如 claude-code, cursor, codex 等）：
npx skills add mintonight/anki-card-formatter --agent claude-code cursor
`

### 方式 2：通过 NPX 一键脚本安装

`ash
# 自动在当前项目创建技能文件
npx github:mintonight/anki-card-formatter install

# 或全局安装至用户主目录 (~/.gemini/, ~/.codex/ 等)
npx github:mintonight/anki-card-formatter install -g
`

---

## 核心特性

- 🛡️ **三步占位隔离管道**：在 Markdown 解析前自动隔离保护代码块与 LaTeX 公式，渲染后再恢复为 Anki 原生标签。
- 📐 **原生 MathJax 对齐**：
  - 行间公式：<anki-mathjax block="true">[ ... ]</anki-mathjax>
  - 行内公式：<anki-mathjax>( ... )</anki-mathjax>
  - 自动规范使用标准 LaTeX 宏命令（如 \Psi \quad \psi）替代裸 Unicode 符号。
- 🎨 **GitHub 浅色高质感样式**：
  - 代码块预设 GitHub 浅色风格（浅灰底 #f6f8fa + 细描边 #d0d7de + 等宽字体 + 横向滑动支持）。
  - 行内代码徽章风格（#eff1f3 底色 + 红色高亮强调）。

---

## 完整规范与 Python 流水线

规范细节及开箱即用的 Python 代码实现详见 [SKILL.md](./SKILL.md)。

---

## 开源协议

[MIT License](./LICENSE)

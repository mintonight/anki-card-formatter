# anki-card-formatter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Best practices, formatting standards, and an automated processing pipeline for generating and updating Anki cards with **LaTeX formulas (MathJax)** and **fenced/inline code blocks**.

旨在解决脚本或 AI Agent 向 Anki（通过 AnkiConnect 等 API）批量导入/更新卡片时常见的：
- **代码块换行丢失**（全部挤在单行无法阅读）
- **Markdown 破坏 LaTeX 公式**（下划线 _、星号 *、反斜杠 \ 被误解析为 Markdown 语法）
- **自定义 HTML 块内裸留 $...$ 导致 MathJax 无法渲染**
- **在数学公式中直接混用 Unicode 希腊字母导致解析崩溃**

---

## 核心特性

- 🛡️ **三步占位隔离管道**：在 Markdown 解析前自动隔离保护代码块与 LaTeX 公式，渲染后再恢复为 Anki 原生标签。
- 📐 **原生 MathJax 对齐**：
  - 行间公式：<anki-mathjax block="true">[ ... ]</anki-mathjax>
  - 行内公式：<anki-mathjax>( ... )</anki-mathjax>
  - 规范使用标准 LaTeX 宏命令替代裸 Unicode 符号。
- 🎨 **GitHub 浅色高质感样式**：
  - 代码块预设 GitHub 浅色风格（浅灰底 #f6f8fa + 细描边 #d0d7de + 等宽字体 + 横向滑动支持）。
  - 行内代码徽章风格（#eff1f3 底色 + 红色高亮强调）。

---

## 快速使用

完整规范和即用型 Python 转换流水线代码详见 [SKILL.md](./SKILL.md)。

---

## Agent 与技能复用

将本仓库的 [SKILL.md](./SKILL.md) 放入你的 Agent 技能目录（如 .gemini/skills/anki-card-formatter/SKILL.md 或 .agents/skills/anki-card-formatter/SKILL.md），任何 AI 助手均可直接遵循并自动生成高质感的 Anki 卡片。

## 开源协议

MIT License

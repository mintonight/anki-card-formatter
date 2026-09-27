# anki-card-formatter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个 [Agent Skill](https://agentskills.io)：AI Agent 通过 AnkiConnect 制卡时，把含 **LaTeX 公式、代码块、表格** 的 Markdown 转成 Anki 桌面端和手机端（AnkiDroid / AnkiMobile）都能正确渲染的 HTML。

解决的问题：

- 公式不渲染：Anki 不认 `$...$`，`\(` 又会被 Markdown 当成转义吃掉
- 公式里的 `<`（如 `0<x<1`）被当成 HTML 标签，后半段内容消失
- 代码块换行被折叠、表格显示成源码、列表挤成一段或子列表被压平
- 夜间模式下文字看不清

## 安装

用 [skills CLI](https://github.com/vercel-labs/skills)（Vercel Labs）安装：

```bash
# 安装到当前项目，供 Claude Code 使用
npx skills add mintonight/anki-card-formatter -a claude-code -y

# 同时装给多个 Agent
npx skills add mintonight/anki-card-formatter -a claude-code codex cursor -y

# 全局安装（所有项目可用）
npx skills add mintonight/anki-card-formatter -g -a claude-code -y

# 更新 / 卸载
npx skills update anki-card-formatter
npx skills remove anki-card-formatter
```

## 前置依赖

- Anki 桌面版 + [AnkiConnect](https://ankiweb.net/shared/info/2055492159) 插件
- Python 3 + `pip install markdown-it-py`

## 使用

安装后直接让 Agent 制卡，它会按 [SKILL.md](skills/anki-card-formatter/SKILL.md) 调用 `scripts/md2anki.py` 转换每个字段。也可以手动转换：

```bash
python skills/anki-card-formatter/scripts/md2anki.py note.md
```

## 测试

```bash
python tests/test_md2anki.py
```

## 开源协议

[MIT License](./LICENSE)

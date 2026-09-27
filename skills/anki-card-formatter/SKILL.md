---
name: anki-card-formatter
description: Use when writing or updating Anki notes through AnkiConnect (addNote, updateNoteFields) from Markdown containing LaTeX math, code blocks or tables, or when Anki cards show raw $...$, unrendered formulas on desktop, AnkiDroid or AnkiMobile, code squeezed into one line, or table source text. 用于通过 AnkiConnect 制卡、批量导入，或卡片公式不显示、代码挤成一行、表格显示成源码时。
---

# Anki 卡片排版

Anki 字段存的是 HTML。含公式、代码、表格的 Markdown 不能直接写进字段，也不能直接交给 Markdown 库转换：Markdown 会吃掉 `\(` 的反斜杠、把下划线当成斜体，公式里的 `<` 还会被浏览器当成标签。

**每个字段都用 `scripts/md2anki.py` 转换，不要自己写转换逻辑。**

## 用法

依赖：`pip install markdown-it-py`

```python
import sys
sys.path.insert(0, r'<本 skill 目录>/scripts')
from md2anki import md_to_anki

back = md_to_anki(r'若 $0<x<1$，则 $\frac{1}{x} > 1$')  # 必须加 r 前缀，否则 \frac \alpha 里的 \f \a 会变成控制字符
# 把 back 作为字段值，调用 AnkiConnect 的 addNote / updateNoteFields
```

命令行：`python <本 skill 目录>/scripts/md2anki.py note.md`（不给文件则读 stdin，输出 UTF-8）

输入里的公式可以写成 `$...$`、`$$...$$`、`\(...\)`、`\[...\]`，输出统一为 Anki 的标准定界符 `\(...\)` / `\[...\]`；代码里的 `$` 保持原样，要显示美元符号写 `\$`。样式全部内联、不设文字颜色（外层 `<div>` 固定左对齐、15px 字号），不用改笔记类型的 CSS，夜间模式也看得清。

## 手写或修改字段 HTML 时

不经过脚本（直接拼 HTML、改已有卡片）时，自己保证：

- 公式只用 `\(...\)` 和 `\[...\]`。Anki 不认 `$...$`。
- 不要写 `<anki-mathjax>`。它只存在于桌面编辑器内部，保存时会转回 `\(...\)`；直接写进字段，桌面和手机的复习界面都不会渲染。
- 公式里的 `<` `>` `&` 转义成 `&lt;` `&gt;` `&amp;`。
- 不要往字段里放 `<style>`：它会作用于整张卡片，还会在每条笔记里重复一份。
- 不要对整段 HTML 做 `\n` → `<br>` 替换：`<pre>` 里会多出空行，表格上方会出现大片空白。

## 症状速查

遇到下面的现象，用 md2anki 重新转换对应字段即可。

| 卡片上的现象 | 原因 |
|---|---|
| 公式显示成 `( x_1 + x_2 )` 或 `$...$` 原文 | `\(` 被 Markdown 当转义吃掉，或用了 Anki 不认的 `$` |
| 公式后半段和后面的文字消失 | 公式里的 `<` 没转义，被当成 HTML 标签 |
| 字段源码里有 `<anki-mathjax>` 或 `xxx=""` 之类的碎片 | 公式里的 `<` 没转义，之后又在编辑器里打开保存过，被二次破坏 |
| 出现 `XYZMATHBLOCK0XYZ` 之类的字 | 旧版流水线处理相邻公式 `$a$$b$` 时占位符没还原 |
| 代码挤成一行 | 没用 `<pre>`，或代码块没被识别（语言标记含 `+`、CRLF 换行） |
| 列表挤成一段、横杠原样显示，或子列表被压平、编号错乱 | 用了要求列表前空一行、子列表缩进 4 格的老式引擎（如 Python-Markdown） |
| 表格显示成带竖线的原文 | 表格紧贴上一段，中间没有空行 |
| 夜间模式看不清字 | 样式里写死了深色文字颜色 |

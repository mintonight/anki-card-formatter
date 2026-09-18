---
name: anki-card-formatter
description: Best practices and processing pipeline for generating and formatting Anki cards containing LaTeX formulas (MathJax) and code blocks. Solves rendering issues like broken line breaks, unrendered math, escaped character corruption, and Unicode vs LaTeX macro conflicts.
---

# Anki 卡片排版与公式/代码渲染规范指南 (anki-card-formatter)

在利用脚本或 Agent 自动向 Anki（通过 AnkiConnect 等 API）导入/更新笔记时，Markdown 转换、LaTeX 数学公式与多行代码块极易发生**格式错乱**、**换行折叠**、**公式无法渲染**和**语法冲突**。本 Skill 沉淀了一套标准处理流水线与最佳实践。

---

## 核心痛点与避坑指南

### 1. 代码块换行丢失（代码挤成一团）
- **原因**：Markdown 转换为 HTML 时，若直接输出为包含换行的纯文本或普通 `<code>` 标签，Anki 的 Web 渲染内核会将文本物理换行折叠为单个空格。
- **解决方案**：
  - 必须使用标准 `<pre><code>...</code></pre>` 标签包裹。
  - 必须显式声明 CSS：`white-space: pre !important;`。
  - 对代码块中的字符执行 HTML 转义（`html.escape(code)`），防止 `<`、`>`、`&` 破坏 HTML 结构。

### 2. LaTeX 公式被 Markdown 解析器损坏
- **原因**：公式中常见下划线（`W_q`）、星号（`*`）、反斜杠（`\(`、`\frac`），若在 Markdown 阶段直接暴露，会被误识别为斜体、强调或转义，导致公式断裂。
- **解决方案**：采用**“占位隔离 - Markdown 渲染 - 占位恢复”**的三步管道法：
  1. 正则提取并扣除代码块与公式，用唯一哈希占位符替代（如 `XYZMATHBLOCK0XYZ`）。
  2. 对其余文本进行标准 Markdown 转换。
  3. 还原占位符，转换为 Anki 官方标准 MathJax 定界符。

### 3. 公式未渲染与移动端（AnkiMobile / AnkiDroid）兼容性陷阱
- **核心原则**：**一律使用 Anki 官方推荐的标准 LaTeX 定界符！**
  - **行内公式**：`\( formula \)`（例：`\( E = mc^2 \)`）
  - **独立行（行间）公式**：`\[ formula \]`（例：`\[ \sum_{i=1}^n i \]`）
- **致命陷阱（严禁手写 `<anki-mathjax>` 自定义标签）**：
  - 许多用户看到桌面版内部有 `<anki-mathjax>`，容易误以为 API 写入也要用这个标签。
  - **事实**：`<anki-mathjax>` 是桌面版富文本编辑器生成卡片时的内部呈现。在移动端（iOS AnkiMobile / Android AnkiDroid）的 Webview 中，内置的 MathJax 配置直接匹配的是 `\(` 和 `\[` 定界符！
  - 如果字段中直接写入了 `<anki-mathjax>`，移动端 Webview 不仅无法识别，还会因未检测到标准定界符而完全跳过数学公式渲染！
- **严禁滥用 `<br>` 标签**：
  - 严禁在卡片内容特别是 `<style>` 标签内部插入 `<br>`。
  - 移动端对 HTML DOM 规范要求极高，`<style>` 内部出现 `<br>` 会导致样式解析器中断，使得整个页面的脚本与渲染管道瘫痪。
- **严禁裸写 `$...$` 或 Unicode 伪公式**：
  - Anki 默认不识别裸写单美元符号 `$...$`，必须转换为 `\( ... \) `。
  - 严禁在公式中使用原始 Unicode 希腊字母（如 `Ψ`），必须转换为标准宏命令（如 `\Psi`、`\psi`）。

---

### 4. Markdown 表格未渲染（表格源码直接暴露在段落中）
- **原因**：在 Python-Markdown（以及大部分 CommonMark 解析器）中，若 Markdown 表格（`| col1 | col2 |`）紧跟在普通段落文本之后而**缺少前置空行**，解析器会将其当作普通多行段落合并，导致 `tables` 扩展失效，表格源码原样显示为带有竖线的纯文本。
- **解决方案**：
  - 在 Markdown 解析前，编写自动间距函数（`ensure_table_spacing`），检测表格起止边界并确保表格块的前后均有物理空行（`\n\n`）。
  - 在 CSS 中为 `table`、`th`、`td` 显式设置边框（`border-collapse: collapse; border: 1px solid #d0d7de`）和表头底色（`#f6f8fa`），确保渲染风格与 GitHub 一致。

---

## 推荐视觉设计规范（GitHub 浅色清爽风）

为了保证在各类模板和卡片中样式不被覆盖，建议在内容头部注入 scoped 样式或内联样式：

```css
/* 代码块容器 */
pre {
  background-color: #f6f8fa !important;
  color: #24292e !important;
  border: 1px solid #d0d7de !important;
  padding: 12px 14px !important;
  border-radius: 6px !important;
  overflow-x: auto !important;
  font-family: 'Consolas', 'Fira Code', 'SFMono-Regular', Menlo, Courier, monospace !important;
  font-size: 13.5px !important;
  line-height: 1.5 !important;
  white-space: pre !important;
  tab-size: 4 !important;
  margin: 12px 0 !important;
}

/* 行内代码徽章 */
code {
  background-color: #eff1f3 !important;
  color: #cf222e !important;
  padding: 2px 5px !important;
  border-radius: 4px !important;
  font-family: 'Consolas', 'Fira Code', 'SFMono-Regular', Menlo, Courier, monospace !important;
  font-size: 0.9em !important;
}

pre code {
  background-color: transparent !important;
  color: inherit !important;
  padding: 0 !important;
}
```

---

## 标准 Python 转换流水线模块

后续制卡脚本可直接复用以下函数：

```python
import html
import re
import markdown

def ensure_table_spacing(md_text: str) -> str:
    """确保 Markdown 表格前后均有空行，防止 tables 扩展因与上方段落粘连而失效"""
    lines = md_text.split('\n')
    new_lines = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        is_table_row = stripped.startswith('|') and stripped.endswith('|')
        if is_table_row:
            if not in_table:
                if new_lines and new_lines[-1].strip() != '':
                    new_lines.append('')
                in_table = True
        else:
            if in_table:
                if stripped != '':
                    new_lines.append('')
                in_table = False
        new_lines.append(line)
    return '\n'.join(new_lines)

def convert_markdown_math_code(md_text: str) -> str:
    """
    将包含 Markdown、LaTeX 公式和多行/行内代码的原始文本
    转换为完全兼容 Anki 桌面端与移动端（AnkiMobile/AnkiDroid）的 HTML 字符串。
    """
    # 0. 自动补全表格前后空行
    md_text = ensure_table_spacing(md_text)
    # 1. 保护多行代码块 ```lang\ncode\n```
    fenced_blocks = {}
    def save_fenced(m):
        key = f'XYZFENCEDBLOCK{len(fenced_blocks)}XYZ'
        raw_code = m.group(2)
        escaped = html.escape(raw_code.strip('\r\n'))
        html_code = (
            f'<pre style="background-color: #f6f8fa !important; color: #24292e !important; '
            f'border: 1px solid #d0d7de !important; padding: 12px 14px !important; '
            f'border-radius: 6px !important; overflow-x: auto !important; '
            f'font-family: \'Consolas\', \'Fira Code\', \'SFMono-Regular\', Menlo, Courier, monospace !important; '
            f'font-size: 13.5px !important; line-height: 1.5 !important; white-space: pre !important; '
            f'tab-size: 4 !important; margin: 12px 0 !important;">'
            f'<code>{escaped}</code></pre>'
        )
        fenced_blocks[key] = html_code
        return key

    md_text = re.sub(r'```(\w*)\n([\s\S]*?)```', save_fenced, md_text)

    # 2. 保护行内单反引号代码 `code`
    inline_codes = {}
    def save_inline_code(m):
        key = f'XYZINLINECODE{len(inline_codes)}XYZ'
        code_text = html.escape(m.group(1))
        html_span = (
            f'<code style="background-color: #eff1f3 !important; color: #cf222e !important; '
            f'padding: 2px 5px !important; border-radius: 4px !important; '
            f'font-family: \'Consolas\', \'Fira Code\', \'SFMono-Regular\', Menlo, Courier, monospace !important; '
            f'font-size: 0.9em !important;">{code_text}</code>'
        )
        inline_codes[key] = html_span
        return key

    md_text = re.sub(r'`([^`\n]+)`', save_inline_code, md_text)

    # 3. 提取并保护 LaTeX 公式（采用 Anki 跨平台官方标准定界符）
    math_blocks = {}
    def save_block_math(m):
        key = f'XYZMATHBLOCK{len(math_blocks)}XYZ'
        formula = m.group(1).strip()
        # 独立成行：\[ formula \]
        math_blocks[key] = f'\\[ {formula} \\]'
        return key

    math_inlines = {}
    def save_inline_math(m):
        key = f'XYZMATHINLINE{len(math_inlines)}XYZ'
        formula = m.group(1).strip()
        # 行内公式：\( formula \)
        math_inlines[key] = f'\\( {formula} \\)'
        return key

    # 优先匹配块级 $$...$$，再匹配行内 $...$
    md_text = re.sub(r'\$\$([\s\S]+?)\$\$', save_block_math, md_text)
    md_text = re.sub(r'\$([^\$\n]+?)\$', save_inline_math, md_text)

    # 4. Markdown 转 HTML（启用表格扩展）
    html_text = markdown.markdown(md_text, extensions=['tables'])

    # 5. 还原所有占位符
    for k, v in math_blocks.items():
        html_text = html_text.replace(k, v)
    for k, v in math_inlines.items():
        html_text = html_text.replace(k, v)
    for k, v in inline_codes.items():
        html_text = html_text.replace(k, v)
    for k, v in fenced_blocks.items():
        html_text = html_text.replace(k, v)

    # 6. 外层容器包裹（避免任何多余 <br> 污染）
    container = (
        f'<div style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, '
        f'\'Helvetica Neue\', Arial, sans-serif; font-size: 15px; line-height: 1.65; color: #24292e; text-align: left;">\n'
        f'{html_text}\n'
        f'</div>'
    )
    return container
```

---

## 检查清单（发布前自检）

- [ ] **代码块**：是否使用了 `<pre><code>` 并声明了 `white-space: pre !important;`？
- [ ] **代码内容**：字符是否经过 `html.escape` 转义？
- [ ] **公式语法**：是否统一为官方标准 `\( ... \)` 与 `\[ ... \]`，而没有手写 `<anki-mathjax>` 导致移动端失真？
- [ ] **定界符**：是否消除了外层多余的括号（严禁 `\((` 或 `\[[`）？
- [ ] **换行标签**：卡片背面是否有失控的 `<br>` 标签（特别是 `<style>` 标签内部）？
- [ ] **希腊字母**：是否已将 Unicode 字母替换为标准 LaTeX 宏命令？

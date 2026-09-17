---
name: anki-card-formatter
description: Best practices and processing pipeline for generating and formatting Anki cards containing LaTeX formulas (MathJax) and code blocks. Solves rendering issues like broken line breaks, unrendered math, escaped character corruption, and Unicode vs LaTeX macro conflicts.
---

# Anki 卡片排版与公式/代码渲染规范指南 (anki-card-formatter)

在利用脚本或 Agent 自动向 Anki（通过 AnkiConnect 等 API）导入/更新笔记时，Markdown 转换、LaTeX 数学公式与多行代码块极易发生**格式错乱**、**换行折叠**、**公式无法渲染**和**语法冲突**。本 Skill 沉淀了一套标准处理流水线与最佳实践。

---

## 核心痛点与避坑指南

### 1. 代码块换行丢失（代码挤成一团）
- **根因**：Markdown 转换为 HTML 时，若直接输出为包含换行的纯文本或普通 `<code>` 标签，Anki 的 Web 渲染内核会将文本物理换行折叠为单个空格。
- **解决方案**：
  - 必须使用标准 `<pre><code>...</code></pre>` 标签包裹。
  - 必须显式声明 CSS：`white-space: pre !important;`。
  - 对代码块中的字符执行 HTML 转义（`html.escape(code)`），防止 `<`、`>`、`&` 破坏 HTML 结构。

### 2. LaTeX 公式被 Markdown 解析器损坏
- **根因**：公式中常见下划线（`W_q`）、星号（`*`）、反斜杠（`\(`、`\frac`），若在 Markdown 阶段直接暴露，会被误识别为斜体、强调或转义，导致公式断裂。
- **解决方案**：采用**“占位隔离 - Markdown 渲染 - 占位恢复”**的三步管道法：
  1. 正则提取并扣除代码块与公式，用唯一哈希占位符替代（如 `XYZMATHBLOCK0XYZ`）。
  2. 对其余文本进行标准 Markdown 转换。
  3. 还原占位符，转换为 Anki 原生 MathJax 语法。

### 3. 公式未渲染：严禁裸写 `$...$` 或 Unicode 伪公式
- **根因 1（缺乏原生标签）**：在复杂的自定义 HTML（如包含 `<div>`、`<span>` 或 `<style>` 的卡片）中，Anki 内置的 Webview **默认不会自动去扫描和解析裸写在普通 HTML 文本中的单美元符号 `$formula$`**，必须使用 Anki 识别的专用 MathJax 标签。
- **根因 2（Unicode 字符混入 LaTeX）**：在 LaTeX 数学公式块中混入希腊字母或特殊符号的原始 Unicode 字符（例如写作 `\(( Ψ \quad ψ )\)`），MathJax 在遇到非 ASCII 的 Unicode 结合 LaTeX 间距宏（如 `\quad`）时会解析崩溃或降级为无法渲染的生文本。
- **解决方案**：
  - **规范一律使用标准 LaTeX 宏命令**：
    - 大写：`\Psi`、`\Xi`、`\Gamma`、`\Delta`、`\Theta`、`\Lambda`、`\Sigma`、`\Phi`、`\Omega`
    - 小写：`\psi`、`\xi`、`\gamma`、`\delta`、`\theta`、`\lambda`、`\sigma`、`\phi`、`\omega`、`\alpha`、`\beta` 等。
  - **所有公式必须转换为 Anki 原生 MathJax 标签**：
    - **行间（块级）公式**：
      ```html
      <anki-mathjax block="true">[ \text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V ]</anki-mathjax>
      ```
    - **行内公式**：
      ```html
      <anki-mathjax>( \Psi \quad \psi )</anki-mathjax>
      <anki-mathjax>( X \in \mathbb{R}^{n \times d} )</anki-mathjax>
      ```

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

def convert_markdown_math_code(md_text: str) -> str:
    """
    将包含 Markdown、LaTeX 公式和多行/行内代码的原始文本
    转换为完全兼容 Anki 的 HTML 字符串。
    """
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

    # 3. 保护并格式化 LaTeX 公式
    math_blocks = {}
    def save_block_math(m):
        key = f'XYZMATHBLOCK{len(math_blocks)}XYZ'
        formula = m.group(1).strip()
        math_blocks[key] = f'<anki-mathjax block="true">[ {formula} ]</anki-mathjax>'
        return key

    math_inlines = {}
    def save_inline_math(m):
        key = f'XYZMATHINLINE{len(math_inlines)}XYZ'
        formula = m.group(1).strip()
        math_inlines[key] = f'<anki-mathjax>( {formula} )</anki-mathjax>'
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

    # 6. 外层容器包裹
    container = (
        f'<div style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, '
        f'\'Helvetica Neue\', Arial, sans-serif; font-size: 15px; line-height: 1.65; color: #24292e; text-align: left;">\n'
        f'{html_text}\n'
        f'</div>'
    )
    return container
```

---

## 检查清单（Checklist）

在将生成的卡片提交给 AnkiConnect 前，务必确认：
- [ ] 多行代码块是否转义了 HTML 实体字符（避免 `<`、`>` 导致标签闭合异常）。
- [ ] 多行代码容器是否包含 `white-space: pre !important;` 样式，避免换行丢失。
- [ ] 是否严禁直接在公式内使用 Unicode 希腊字母（必须使用标准 `\Psi`、`\psi`、`\Xi`、`\xi` 等宏命令）。
- [ ] 文本中所有需要数学渲染的符号/公式是否已统一转换为 `<anki-mathjax>( ... )</anki-mathjax>` 或块级 `<anki-mathjax block="true">[ ... ]</anki-mathjax>`（严禁在自定义 HTML 中裸留 `$...$`）。
- [ ] 下划线与反斜杠是否在 Markdown 解析前完成保护，避免公式解析破损。

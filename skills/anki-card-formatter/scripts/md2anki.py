"""Markdown（含 LaTeX 公式、代码块、表格）→ Anki 字段 HTML，桌面端和手机端都能渲染。

    python md2anki.py note.md        # 不给文件则读 stdin；输出 UTF-8
    from md2anki import md_to_anki
"""
import html
import re
import sys

from markdown_it import MarkdownIt

# CommonMark + 表格：列表可以紧跟段落、子列表缩进 2 格即可，和 GitHub / LLM 写的 Markdown 一致
MD = MarkdownIt('commonmark', {'html': True}).enable('table')

# 只用半透明灰、不设文字颜色：日间和夜间模式下都看得清
MONO = 'font-family: Consolas, Menlo, monospace;'
PRE = ('background: rgba(127,127,127,.1); border: 1px solid rgba(127,127,127,.3); border-radius: 6px; '
       f'padding: 12px 14px; overflow-x: auto; white-space: pre; {MONO} font-size: 13.5px; line-height: 1.5;')
CODE = f'background: rgba(127,127,127,.15); border-radius: 4px; padding: 2px 5px; {MONO} font-size: .9em;'
TABLE = 'border-collapse: collapse; margin: 8px 0;'
TD = 'border: 1px solid rgba(127,127,127,.4); padding: 4px 8px;'
TH = TD + ' background: rgba(127,127,127,.12);'
BOX = ("font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; "
       'font-size: 15px; line-height: 1.65; text-align: left;')

# 一次从左到右扫描：代码和 \$（字面美元符号）原样保留，公式换成占位符躲开 Markdown
TOKEN = re.compile(
    r'(?P<keep>^(?P<fence>`{3,}|~{3,}).*?^(?P=fence)[ \t]*$|`[^`\n]+`|\\\$)'
    r'|\$\$(?P<d1>.+?)\$\$|\\\[(?P<d2>.+?)\\\]'
    r'|\\\((?P<i1>.+?)\\\)|\$(?P<i2>[^$\n]+?)\$',
    re.S | re.M)


def md_to_anki(md_text):
    if any(c in md_text for c in '\a\b\f\v'):
        raise ValueError(r'输入含控制字符：多半是在普通 Python 字符串里写了 \frac、\alpha、\beta、\vec 这类公式，'
                         r'请改用 r"..." 原始字符串，或从文件读取')
    math = []

    def protect(m):
        if m['keep']:
            return m['keep']
        display = m['d1'] or m['d2']
        tex = html.escape((display or m['i1'] or m['i2']).strip(), quote=False)
        math.append(f'\\[ {tex} \\]' if display else f'\\( {tex} \\)')
        return f'XYZMATH{len(math) - 1}XYZ'

    out = MD.render(TOKEN.sub(protect, md_text.replace('\r\n', '\n')))
    # CommonMark 不认紧挨中文标点的 **（如 这是**「重点」**）：跳过代码，把残留的补成加粗
    parts = re.split(r'(<pre.*?</pre>|<code.*?</code>)', out, flags=re.S)
    parts[::2] = [re.sub(r'\*\*(?=\S)([^*<>\n]+?)(?<=\S)\*\*', r'<strong>\1</strong>', p) for p in parts[::2]]
    out = re.sub(r'XYZMATH(\d+)XYZ', lambda m: math[int(m[1])], ''.join(parts))
    out = re.sub(r'(?<!<pre>)<code>', f'<code style="{CODE}">', out)
    out = out.replace('<pre>', f'<pre style="{PRE}">').replace('<table>', f'<table style="{TABLE}">')
    out = re.sub(r'<(th|td)(?: style="([^"]*)")?>',
                 lambda m: f'<{m[1]} style="{TH if m[1] == "th" else TD} {m[2] or ""}">', out)
    return f'<div style="{BOX}">\n{out}</div>'


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', newline='\n')
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8-sig') as f:
            src = f.read()
    else:
        sys.stdin.reconfigure(encoding='utf-8-sig')
        src = sys.stdin.read()
    print(md_to_anki(src))

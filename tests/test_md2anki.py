"""运行：python tests/test_md2anki.py"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / 'skills' / 'anki-card-formatter' / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from md2anki import md_to_anki  # noqa: E402


def test_less_than_in_formula_is_escaped():
    # 不转义时浏览器把 <x 当成标签，公式后半段连同后文一起消失
    assert r'\( 0&lt;x&lt;1 \)' in md_to_anki('当 $0<x<1$ 时')


def test_backslash_delimiters_survive_markdown():
    # 不保护时 Markdown 把 \( 当转义，输出成普通括号
    out = md_to_anki(r'由 \( x_1 + x_2 \) 得 \[ a \\ b \]')
    assert r'\( x_1 + x_2 \)' in out
    assert r'\[ a \\ b \]' in out


def test_adjacent_inline_formulas_stay_separate():
    # 先块后行内两遍替换时，中间的 $$ 被当成块公式，卡片上残留占位符
    assert r'\( a \)\( b \)\( c \)' in md_to_anki('$a$$b$$c$')


def test_display_math():
    assert r'\[ \sum_{i=1}^n i \]' in md_to_anki('$$\n\\sum_{i=1}^n i\n$$')


def test_dollar_inside_code_is_not_math():
    out = md_to_anki('`$x$`\n\n```\necho $y$\n```')
    assert '$x$</code>' in out
    assert 'echo $y$' in out


def test_escaped_dollar_is_literal():
    out = md_to_anki(r'这本书 \$5，那本 \$10')
    assert '这本书 $5，那本 $10' in out
    assert r'\(' not in out


def test_formula_followed_by_digit():
    # "公式后紧跟数字就不算公式"的金额规则会漏掉 $\sim$10 这种写法
    assert r'\( \sim \)10' in md_to_anki(r'β 取 $\sim$10 或更小')


def test_crlf_fence_with_symbol_language_keeps_code():
    # 语言标记只认 \w、或不处理 CRLF 时：代码块没被识别，换行折叠、代码里的 $ 被当成公式
    out = md_to_anki('```c++\r\nx = $y$;\r\nint b;\r\n```\r\n')
    assert '<pre' in out
    assert 'x = $y$;\nint b;' in out


def test_code_block_not_nested_in_paragraph():
    # <p><pre> 是非法嵌套，浏览器会多出空段落
    assert '<p><pre' not in md_to_anki('段落\n\n```python\nx = 1\n```\n')


def test_table_glued_to_paragraph_renders():
    out = md_to_anki('对比：\n| a | b |\n|---|---|\n| $x_1$ | $|y|$ |')
    assert '<table' in out
    assert r'\( |y| \)' in out


def test_table_cells_have_borders():
    # 浏览器默认的表格没有边框
    out = md_to_anki('| a |\n|---|\n| 1 |')
    assert re.search(r'<th style="[^"]*border', out)
    assert re.search(r'<td style="[^"]*border', out)


def test_table_spacing_leaves_code_blocks_alone():
    # 补空行逻辑不跳过代码块时，会往代码里插空行
    assert 'x\n| a |' in md_to_anki('```\nx\n| a |\n```')


def test_no_forced_text_color():
    # 写死深色文字，在夜间模式的深色背景上看不清
    out = md_to_anki('正文 `code`\n\n```\nx\n```\n\n| a |\n|---|\n| 1 |')
    assert not re.search(r'(?<![\w-])color\s*:', out)


def test_list_right_after_paragraph():
    # Python-Markdown 要求列表前有空行，否则整段挤成一行、横杠原样显示
    assert '<li>a</li>' in md_to_anki('说明：\n- a\n- b')


def test_nested_list_with_narrow_indent():
    # 2~3 格缩进的子列表被压平时，y 会变成有序列表的第 2 项，z 被挤成第 3 项
    assert re.search(r'<ul>\s*<li>y</li>\s*</ul>', md_to_anki('1. x\n   - y\n\n2. z'))


def test_bold_next_to_cjk_punctuation():
    # CommonMark 的定界规则下，紧挨中文标点的 ** 会残留成字面星号
    assert '<strong>「重点」</strong>' in md_to_anki('这是**「重点」**内容')


def test_double_star_in_code_untouched():
    assert 'x**2 + y**2</code>' in md_to_anki('`x**2 + y**2`')


def test_inline_html_passes_through():
    # 不透传 HTML 时，<span> 会被转义成字面文字
    assert '<span class="lv">L2</span>' in md_to_anki('<span class="lv">L2</span> 题目')


def test_latex_mangled_by_python_escapes_raises():
    # 普通字符串里 \f \a \b \v 已变成控制字符：静默输出会得到坏公式
    try:
        md_to_anki('$\frac{1}{2}$')  # 故意不加 r 前缀
    except ValueError:
        return
    raise AssertionError('应该报错')


def run_cli(*args, stdin=None):
    env = {**os.environ, 'PYTHONIOENCODING': 'gbk'}  # 模拟标准输入输出默认 GBK 的中文 Windows
    env.pop('PYTHONUTF8', None)
    r = subprocess.run([sys.executable, str(SCRIPTS / 'md2anki.py'), *args],
                       input=stdin, capture_output=True, env=env, check=True)
    return r.stdout.decode('utf-8')


def test_cli_file_argument_outputs_utf8():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / 'note.md'
        f.write_text('中文 $x$', encoding='utf-8')
        assert r'中文 \( x \)' in run_cli(str(f))


def test_cli_stdin_outputs_utf8():
    assert r'中文 \( x \)' in run_cli(stdin='中文 $x$'.encode('utf-8'))


if __name__ == '__main__':
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            try:
                fn()
                print('PASS', name)
            except Exception as e:
                failed += 1
                print('FAIL', name, '-', type(e).__name__, str(e)[:150])
    print(f'\n{failed} failed')
    sys.exit(failed)

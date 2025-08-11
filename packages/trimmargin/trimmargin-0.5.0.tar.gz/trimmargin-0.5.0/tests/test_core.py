from __future__ import annotations

from trimmargin import (
  prepend_indent,
  replace_indent,
  replace_indent_by_margin,
  trim_indent,
  trim_margin,
)


def test_trim_margin_basic() -> None:
  s = """
        |Hello
        |World
    """
  assert trim_margin(s) == 'Hello\nWorld'


def test_trim_margin_mixed_lines_unaffected() -> None:
  s = '\n   |A\n   B (no prefix)\n   |C\n'
  assert trim_margin(s) == 'A\n   B (no prefix)\nC'


def test_trim_margin_preserves_interior_blanks_and_normalizes_eols() -> None:
  s = '\r\n   |A\r\n\r\n   |B\r\n'
  out = trim_margin(s)
  assert out == 'A\n\nB'
  assert '\r' not in out


def test_replace_indent_by_margin_custom_indent() -> None:
  s = """
        |x
        |y
        z (no prefix)
    """
  expected = '> x\n> y\n        z (no prefix)'
  assert replace_indent_by_margin(s, new_indent='> ') == expected


def test_trim_indent_and_replace_indent() -> None:
  s = """
            alpha
            beta
        """
  assert trim_indent(s) == 'alpha\nbeta'
  assert replace_indent(s, new_indent='.. ') == '.. alpha\n.. beta'


def test_prepend_indent_blank_line_behavior() -> None:
  s = 'a\n\nb\n'
  # Keep interior blank blank; drop edge blanks.
  assert prepend_indent(s, indent='--') == '--a\n\n--b'

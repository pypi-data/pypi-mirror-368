"""Kotlin-style margin and indent helpers built on stdlib textwrap.

Functions here mirror Kotlin's `trimMargin` family. We rely on
`textwrap.dedent` and `textwrap.indent` to avoid reimplementing core
indent logic.
"""

from __future__ import annotations

import textwrap


def trim_margin(text: str, margin_prefix: str = '|') -> str:
  """Trim leading whitespace + margin prefix; drop edge blank lines.

  This matches Kotlin's `trimMargin` behavior. Lines that do not have
  the margin prefix after leading whitespace are left unchanged.

  Args:
    text: Input text. May use mixed newline conventions.
    margin_prefix: Prefix to detect after leading whitespace. Must be
      non-blank. Default: `"|"`.

  Returns:
    Text with matching margin removed and first/last blank lines
    dropped. Output newline is always `\\n`.

  Raises:
    ValueError: If `margin_prefix` is blank.
  """
  return replace_indent_by_margin(
    text,
    new_indent='',
    margin_prefix=margin_prefix,
  )


def replace_indent_by_margin(
  text: str,
  new_indent: str = '',
  margin_prefix: str = '|',
) -> str:
  """Replace whitespace+margin with `new_indent` when present.

  If a line's first non-whitespace segment starts with `margin_prefix`,
  we remove the leading whitespace and the prefix, then prepend
  `new_indent`.

  Args:
    text: Input text.
    new_indent: Indent to add where a margin was found.
    margin_prefix: Margin prefix to detect after leading whitespace.

  Returns:
    Adjusted text with edge blank lines dropped and `\\n` line ends.

  Raises:
    ValueError: If `margin_prefix` is blank.
  """
  if not margin_prefix.strip():
    raise ValueError('margin_prefix must be a non-blank string.')

  lines = text.splitlines()
  last = len(lines) - 1
  out: list[str] = []

  for i, line in enumerate(lines):
    # Remove first/last BLANK lines only.
    if (i == 0 or i == last) and line.strip() == '':
      continue

    idx = _first_non_ws_index(line)
    if idx != -1 and line.startswith(margin_prefix, idx):
      out.append(f'{new_indent}{line[idx + len(margin_prefix) :]}')
    else:
      out.append(line)

  return '\n'.join(out)


def trim_indent(text: str) -> str:
  """Remove minimal common indent; drop edge blank lines.

  Uses `textwrap.dedent` to compute and remove common indent.
  """
  dedented = textwrap.dedent(text)
  lines = dedented.splitlines()
  lines = _drop_edge_blank_lines(lines)
  return '\n'.join(lines)


def replace_indent(text: str, new_indent: str = '') -> str:
  """Dedent then indent non-blank lines with `new_indent`.

  Uses `textwrap.dedent` and `textwrap.indent`. Interior blank lines
  are preserved.
  """
  dedented = textwrap.dedent(text)
  indented = textwrap.indent(
    dedented,
    new_indent,
    predicate=lambda ln: ln.strip() != '',
  )
  lines = indented.splitlines()
  lines = _drop_edge_blank_lines(lines)
  return '\n'.join(lines)


def prepend_indent(text: str, indent: str = '    ') -> str:
  """Prepend `indent` to non-blank lines; Kotlin-compatible blanks.

  Semantics:
    * Keep interior blank lines blank.
    * Drop first/last blank lines.
    * Do not dedent.
  """
  lines = text.splitlines()
  lines = _drop_edge_blank_lines(lines)
  body = '\n'.join(lines)
  return textwrap.indent(body, indent, predicate=lambda ln: ln.strip() != '')


def _drop_edge_blank_lines(lines: list[str]) -> list[str]:
  """Drop first/last lines iff blank; keep interior blanks."""
  if not lines:
    return lines
  last = len(lines) - 1
  out: list[str] = []
  for i, line in enumerate(lines):
    if (i == 0 or i == last) and line.strip() == '':
      continue
    out.append(line)
  return out


def _first_non_ws_index(line: str) -> int:
  """Return index of first non-whitespace char; -1 if none."""
  for i, ch in enumerate(line):
    if not ch.isspace():
      return i
  return -1

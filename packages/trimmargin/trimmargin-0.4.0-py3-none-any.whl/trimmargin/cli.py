"""Console script entry point for `trimmargin`.

The CLI reads from a file or stdin and writes to stdout. Default mode is
`trim-margin` with margin prefix `"|"`.
"""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .core import (
  prepend_indent,
  replace_indent,
  replace_indent_by_margin,
  trim_indent,
  trim_margin,
)


def _read_text(fp: str | None) -> str:
  """Return text from `fp` or stdin if `None` or `"-"`.

  Args:
    fp: Path to file or `None`/`"-"` to read stdin.

  Returns:
    The text contents.
  """
  if not fp or fp == '-':
    return sys.stdin.read()
  return Path(fp).read_text(encoding='utf-8')


def _write_text(s: str) -> None:
  """Write text to stdout without adding a trailing newline."""
  sys.stdout.write(s)


def _build_parser() -> argparse.ArgumentParser:
  """Create the argument parser."""
  p = argparse.ArgumentParser(
    prog='trimmargin',
    description=(
      "Kotlin-style trimMargin utilities. Default mode is 'trim-margin'. "
      'Reads FILE or stdin and writes to stdout.'
    ),
  )
  p.add_argument(
    'file',
    nargs='?',
    default='-',
    help='Input file path (default: stdin).',
  )
  p.add_argument(
    '--mode',
    choices=[
      'trim-margin',
      'replace-by-margin',
      'trim-indent',
      'replace-indent',
      'prepend',
    ],
    default='trim-margin',
    help='Operation to perform (default: trim-margin).',
  )
  p.add_argument(
    '--prefix',
    '-p',
    default='|',
    help="Margin prefix for margin-based modes (default: '|').",
  )
  p.add_argument(
    '--new-indent',
    '-n',
    default='',
    help='New indent for replace-by-margin / replace-indent.',
  )
  p.add_argument(
    '--indent',
    default='    ',
    help='Indent for prepend mode (default: 4 spaces).',
  )
  p.add_argument(
    '--version',
    action='store_true',
    help='Print version and exit.',
  )
  return p


def main(argv: list[str] | None = None) -> int:
  """CLI entry point.

  Args:
    argv: Optional argv override for testing.

  Returns:
    Process exit code (0 on success).
  """
  args = _build_parser().parse_args(argv)

  if args.version:
    try:
      ver = version('trimmargin')
    except PackageNotFoundError:
      ver = '0.0.0'
    _write_text(f'{ver}\n')
    return 0

  text = _read_text(args.file)

  if args.mode == 'trim-margin':
    out = trim_margin(text, margin_prefix=args.prefix)
  elif args.mode == 'replace-by-margin':
    out = replace_indent_by_margin(
      text,
      new_indent=args.new_indent,
      margin_prefix=args.prefix,
    )
  elif args.mode == 'trim-indent':
    out = trim_indent(text)
  elif args.mode == 'replace-indent':
    out = replace_indent(text, new_indent=args.new_indent)
  elif args.mode == 'prepend':
    out = prepend_indent(text, indent=args.indent)
  else:  # pragma: no cover
    raise ValueError(f'Unknown mode: {args.mode}')

  _write_text(out)
  return 0


if __name__ == '__main__':  # pragma: no cover
  raise SystemExit(main())

"""Public API for trimmargin."""

from importlib.metadata import PackageNotFoundError, version

from .core import (
  prepend_indent,
  replace_indent,
  replace_indent_by_margin,
  trim_indent,
  trim_margin,
)

__all__ = [
  'trim_margin',
  'replace_indent_by_margin',
  'trim_indent',
  'replace_indent',
  'prepend_indent',
]

try:
  __version__ = version('trimmargin')
except PackageNotFoundError:  # pragma: no cover
  __version__ = '0.0.0'

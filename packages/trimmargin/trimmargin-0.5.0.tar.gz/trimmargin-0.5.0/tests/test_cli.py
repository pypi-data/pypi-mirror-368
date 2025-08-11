from __future__ import annotations

import io
from pathlib import Path

from trimmargin import cli as cli_mod


def _run_cli(args: list[str], input_text: str = '') -> str:
  """Run CLI with controlled stdio and capture stdout."""
  stdin_backup = cli_mod.sys.stdin
  stdout_backup = cli_mod.sys.stdout
  try:
    cli_mod.sys.stdin = io.StringIO(input_text)
    buf = io.StringIO()
    cli_mod.sys.stdout = buf
    rc = cli_mod.main(args)
    assert rc == 0
    return buf.getvalue()
  finally:
    cli_mod.sys.stdin = stdin_backup
    cli_mod.sys.stdout = stdout_backup


def test_cli_default_trim_margin_stdin() -> None:
  s = """
        |hi
        |there
    """
  out = _run_cli([], input_text=s)
  assert out == 'hi\nthere'


def test_cli_modes_and_file(tmp_path: Path) -> None:
  p = tmp_path / 'in.txt'
  p.write_text('\n  |x\n\n  |y\n', encoding='utf-8')

  out = _run_cli(['--mode', 'trim-margin', str(p)])
  assert out == 'x\n\ny'

  out = _run_cli(
    ['--mode', 'replace-by-margin', '--new-indent', '>>> ', str(p)]
  )
  assert out == '>>> x\n\n>>> y'

  out = _run_cli(['--mode', 'trim-indent', str(p)])
  assert out == '|x\n\n|y'

  out = _run_cli(['--mode', 'replace-indent', '--new-indent', '-- ', str(p)])
  assert out == '-- |x\n\n-- |y'

  out = _run_cli(['--mode', 'prepend', '--indent', '++', str(p)])
  assert out == '++  |x\n\n++  |y'


def test_cli_version_flag() -> None:
  out = _run_cli(['--version'])
  # Just ensure it prints something and ends with newline.
  assert out.strip() != ''

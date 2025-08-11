# trimmargin ✂️📏

Kotlin-style `trimMargin` and friends for Python — with a tiny CLI.

- 🔄 Normalizes line endings to `\n`
- 🧼 Drops first/last **blank** lines (only edges, not interior)
- 🧲 `trim_margin()` strips leading whitespace + a margin prefix (default `|`)
- 🔧 `replace_indent_by_margin()` like Kotlin’s, with a custom replacement indent
- 🪄 `trim_indent()` / `replace_indent()` built on `textwrap.dedent/indent`
- ➕ `prepend_indent()` behaves like Kotlin (blank-line quirk covered)

## Install

```bash
# uv (recommended)
uv pip install trimmargin

# or pip
pip install trimmargin
````

## Quick start

```python
from trimmargin import trim_margin, replace_indent_by_margin

text = """
    |hello
    |world
"""

print(trim_margin(text))
# hello
# world

print(replace_indent_by_margin(text, new_indent=">>> "))
# >>> hello
# >>> world
```

### Behavior notes

* If a line’s first non-whitespace char starts the margin prefix, both the
  leading whitespace **and** the prefix are removed; other lines are unchanged.
* Only the first and last **blank** lines are dropped.
* Input may use `\r\n`, `\n`, or `\r`; output uses `\n`.

## CLI 🚀

The `trimmargin` command reads a file or stdin and writes to stdout.

```bash
# default: trim-margin on stdin using prefix "|"
trimmargin < input.txt

# file input
trimmargin input.txt

# modes
trimmargin --mode replace-by-margin --new-indent ">>> " input.txt
trimmargin --mode trim-indent < input.txt
trimmargin --mode replace-indent --new-indent "  " < input.txt
trimmargin --mode prepend --indent ">> "

# change margin prefix
trimmargin --prefix "§" < input.txt

# version
trimmargin --version
```

**Modes**

* `trim-margin` *(default)*: remove leading whitespace + `prefix`
* `replace-by-margin`: same detection as above, then add `new-indent`
* `trim-indent`: remove common indent via `textwrap.dedent`
* `replace-indent`: `dedent` then `indent` non-blank lines with `new-indent`
* `prepend`: prepend `indent` to non-blank lines; blank-line quirk matches
  Kotlin:

  * if blank and `len(line) < len(indent)`: line becomes exactly `indent`
  * else: leave blank line unchanged

## Dev (uv) 🧑‍💻

```bash
# setup
uv sync --extra dev

# tests
uv run pytest

# lint & types
uv run ruff check .
uv run mypy src

# format
uv run ruff format .

# build & publish
uv build
uv publish
```

## Why this exists ❓

`textwrap.dedent/indent` are great, but Kotlin’s margin-aware trimming is
handy for multiline literals embedded in code and docs.
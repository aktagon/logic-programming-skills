#!/usr/bin/env python3
"""Run every verifiable Prolog / s(CASP) snippet in a skill through swipl.

A fenced block opts in by making its FIRST line a verify directive:

    ```prolog
    % !verify
    ...a complete program; must define main/0...
    ```

    ```prolog
    % !verify-fails
    ...a program we assert does NOT succeed (teaching a trap)...
    ```

Blocks without a directive are treated as illustrative fragments and skipped —
most snippets in a skill are clause fragments or REPL transcripts that are not
standalone programs, and failing them would train the author to stop writing
examples rather than to write correct ones.

A verified block is written to a temp file and run with:

    swipl -q -g main -t halt <file>

so the block itself decides what "correct" means. Exit code is the verdict:
0 when every verified block behaves as declared, 1 otherwise.

Usage:
    uv run scripts/verify_snippets.py [skill_dir]     # default: script's parent
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

FENCE = re.compile(
    r"^```(?P<lang>prolog|scasp)\s*\n(?P<body>.*?)^```\s*$",
    re.MULTILINE | re.DOTALL,
)

DIRECTIVE = re.compile(r"^\s*%\s*!(verify(?:-fails)?)\s*$")

SWIPL = "swipl"
TIMEOUT_SECONDS = 30


class Block:
    def __init__(self, path: Path, line: int, expect_success: bool, source: str):
        self.path = path
        self.line = line
        self.expect_success = expect_success
        self.source = source

    @property
    def where(self) -> str:
        return f"{self.path}:{self.line}"


def blocks_in(path: Path) -> list[Block]:
    text = path.read_text(encoding="utf-8")
    found: list[Block] = []
    for match in FENCE.finditer(text):
        body = match.group("body")
        first, _, rest = body.partition("\n")
        directive = DIRECTIVE.match(first)
        if directive is None:
            continue
        line = text[: match.start()].count("\n") + 2
        found.append(
            Block(
                path=path,
                line=line,
                expect_success=directive.group(1) == "verify",
                source=rest,
            )
        )
    return found


def run(block: Block) -> tuple[bool, str]:
    """Run one block. Returns (behaved_as_declared, detail)."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".pl", delete=False, encoding="utf-8"
    ) as f:
        f.write(block.source)
        tmp = Path(f.name)
    try:
        proc = subprocess.run(
            [SWIPL, "-q", "-g", "main", "-t", "halt", str(tmp)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return (False, f"timed out after {TIMEOUT_SECONDS}s")
    except FileNotFoundError:
        print(f"error: {SWIPL} not on PATH", file=sys.stderr)
        raise SystemExit(2)
    finally:
        tmp.unlink(missing_ok=True)

    succeeded = proc.returncode == 0
    if succeeded == block.expect_success:
        return (True, "")
    detail = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
    if block.expect_success:
        return (False, f"expected success, got failure:\n{detail}")
    return (False, "expected failure, but the program succeeded")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    found: list[Block] = []
    for md in sorted(root.rglob("*.md")):
        found.extend(blocks_in(md))

    if not found:
        print(f"no verifiable blocks under {root} (add `% !verify` to opt a block in)")
        return 0

    failures = 0
    for block in found:
        ok, detail = run(block)
        if ok:
            print(f"  ok    {block.where}")
        else:
            failures += 1
            print(f"  FAIL  {block.where}\n        {detail.replace(chr(10), chr(10) + '        ')}")

    print(f"\n{len(found) - failures}/{len(found)} verified blocks behaved as declared")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

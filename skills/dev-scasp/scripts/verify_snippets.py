#!/usr/bin/env python3
"""Check every checkable Prolog / s(CASP) snippet in a skill against swipl.

There are two tiers, and they are reported as two separate numbers. Never add
them together: one executes the block and asserts on the result, the other only
proves the block is well-formed source.

TIER 1 — executed. A block opts in by making its FIRST line a directive:

    ```prolog
    % !verify
    ...a complete program; must define main/0...
    ```

    ```prolog
    % !verify-fails
    ...a program we assert does NOT succeed (teaching a trap)...
    ```

The block is written to a temp file and run with

    swipl -q -g main -t halt <file>

so the block itself decides what "correct" means.

TIER 2 — load-checked. A fragment that is not a standalone program can still be
proved to parse:

    ```prolog
    % !load
    ...clauses, directives, or a REPL transcript...
    ```

    ```prolog
    % !load scasp
    ...a fragment that needs library(scasp) operators to parse at all...
    ```

Some blocks are reproduced precisely because they do NOT load — an upstream file
kept verbatim as the specimen for a claim the prose makes about it. Assert that
instead of deleting the evidence:

    ```prolog
    % !load-fails scasp
    % !expect Syntax error: Operator expected
    ...a file SWI's reader rejects, quoted to prove that it does...
    ```

`% !expect` is required after `% !load-fails`: "it produced some diagnostic" is
too weak a claim to protect a transcription from rotting into a different error.

The block is consulted and FAILS if swipl writes anything to stderr. The exit
code is useless here — swipl exits 0 on a syntax error — so the gate is stderr
content. Two accommodations make the tier usable on documentation:

  - An optional named preamble (see PREAMBLES) is prepended, so a fragment using
    `not`, `#pred` or `#abducible` has the operators it needs.
  - A line beginning `?- ` is a REPL transcript, not source. Consulting it would
    RUN the goal against a database the fragment never sets up. Each is rewritten
    into a clause instead, so the goal must parse and be callable, but is never
    executed.

Singleton warnings are suppressed in this tier: a documentation fragment
legitimately mentions a variable once, and `#pred` templates reference their head
variables only inside quoted atoms, making every one of them a singleton.

A load-check is genuinely weaker than a verify. It proves the block parses. It
proves nothing about whether the block is *true*. Blocks with no directive at all
are neither, and are counted and listed so the residue stays visible.

Exit code: 0 when every checked block behaved as declared, 1 otherwise.

Usage:
    uv run scripts/verify_snippets.py [skill_dir]     # default: script's parent
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

# The indent group matters: a fence nested inside a list item is indented, and a
# regex anchored at column 0 silently skips it. Skipping a block is worse than
# failing one, because the count then overstates coverage.
FENCE = re.compile(
    r"^(?P<indent>[ \t]*)```(?P<lang>prolog|scasp)[ \t]*\n"
    r"(?P<body>.*?)^(?P=indent)```[ \t]*$",
    re.MULTILINE | re.DOTALL,
)

DIRECTIVE = re.compile(
    r"^\s*%\s*!(verify-fails|verify|load-fails|load)(?:\s+(\S+))?\s*$"
)

EXPECT = re.compile(r"^\s*%\s*!expect\s+(\S.*?)\s*$")

QUERY = re.compile(r"^\?-\s")

PREAMBLES = {
    "scasp": (
        ":- use_module(library(scasp)).\n"
        ":- use_module(library(scasp/human)).\n"
    ),
    "clpfd": ":- use_module(library(clpfd)).\n",
}

LOAD_PREFIX = ":- style_check(-singleton).\n"

SWIPL = "swipl"
TIMEOUT_SECONDS = 30


class Block:
    def __init__(
        self, path: Path, line: int, kind: str, preamble: str, source: str, expect: str = ""
    ):
        self.path = path
        self.line = line
        self.kind = kind
        self.preamble = preamble
        self.source = source
        self.expect = expect

    @property
    def where(self) -> str:
        return f"{self.path}:{self.line}"

    @property
    def executed(self) -> bool:
        return not self.kind.startswith("load")


def dedent_body(body: str, indent: str) -> str:
    """Strip the fence's own indentation from each line of its body."""
    if not indent:
        return body
    return "\n".join(
        line[len(indent):] if line.startswith(indent) else line
        for line in body.split("\n")
    )


def blocks_in(path: Path) -> tuple[list[Block], list[str]]:
    """Return (checked blocks, locations of blocks carrying no directive)."""
    text = path.read_text(encoding="utf-8")
    found: list[Block] = []
    unmarked: list[str] = []
    for match in FENCE.finditer(text):
        body = dedent_body(match.group("body"), match.group("indent"))
        first, _, rest = body.partition("\n")
        directive = DIRECTIVE.match(first)
        line = text[: match.start()].count("\n") + 2
        if directive is None:
            unmarked.append(f"{path}:{line}")
            continue
        name = directive.group(2)
        if name is not None and name not in PREAMBLES:
            print(f"error: {path}:{line}: unknown preamble {name!r}", file=sys.stderr)
            raise SystemExit(2)
        kind = directive.group(1)
        expect = ""
        if kind == "load-fails":
            second, _, tail = rest.partition("\n")
            match_expect = EXPECT.match(second)
            if match_expect is None:
                print(
                    f"error: {path}:{line}: !load-fails requires a following "
                    f"`% !expect <substring>` line",
                    file=sys.stderr,
                )
                raise SystemExit(2)
            expect, rest = match_expect.group(1), tail
        found.append(
            Block(
                path=path,
                line=line,
                kind=kind,
                preamble=PREAMBLES[name] if name else "",
                source=rest,
                expect=expect,
            )
        )
    return found, unmarked


def as_load_program(block: Block) -> str:
    """Rewrite a fragment so consulting it checks the source without running it."""
    lines = []
    query = 0
    for line in block.source.splitlines():
        if QUERY.match(line):
            query += 1
            line = f"'$query'({query}) :- " + line[3:]
        lines.append(line)
    return LOAD_PREFIX + block.preamble + "\n".join(lines) + "\n"


def swipl_run(argv: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        print(f"error: {SWIPL} not on PATH", file=sys.stderr)
        raise SystemExit(2)


def run(block: Block) -> tuple[bool, str]:
    """Check one block. Returns (behaved_as_declared, detail)."""
    loading = block.kind.startswith("load")
    program = as_load_program(block) if loading else block.source
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".pl", delete=False, encoding="utf-8"
    ) as f:
        f.write(program)
        tmp = Path(f.name)
    try:
        goal = "halt" if loading else "main"
        proc = swipl_run([SWIPL, "-q", "-g", goal, "-t", "halt", str(tmp)])
    finally:
        tmp.unlink(missing_ok=True)

    if proc is None:
        return (False, f"timed out after {TIMEOUT_SECONDS}s")

    if loading:
        # The exit code is worthless: swipl exits 0 on a syntax error. Gate on
        # whether it had anything to complain about.
        noise = proc.stderr.strip()
        if block.kind == "load-fails":
            if not noise:
                return (False, f"expected to fail with {block.expect!r}, consulted clean")
            if block.expect not in noise:
                return (
                    False,
                    f"expected {block.expect!r} in the diagnostics, got:\n{noise}",
                )
            return (True, "")
        if noise:
            return (False, f"consulted with diagnostics:\n{noise}")
        return (True, "")

    succeeded = proc.returncode == 0
    expect_success = block.kind == "verify"
    if succeeded == expect_success:
        return (True, "")
    detail = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
    if expect_success:
        return (False, f"expected success, got failure:\n{detail}")
    return (False, "expected failure, but the program succeeded")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    found: list[Block] = []
    unmarked: list[str] = []
    for md in sorted(root.rglob("*.md")):
        blocks, bare = blocks_in(md)
        found.extend(blocks)
        unmarked.extend(bare)

    if not found:
        print(f"no checkable blocks under {root} (add `% !verify` or `% !load`)")
        return 0

    failures = 0
    counts = {"executed": [0, 0], "load": [0, 0]}   # [passed, total]
    for block in found:
        ok, detail = run(block)
        tier = "executed" if block.executed else "load"
        counts[tier][1] += 1
        if ok:
            counts[tier][0] += 1
            print(f"  ok    {'exec' if block.executed else 'load'}  {block.where}")
        else:
            failures += 1
            indented = detail.replace(chr(10), chr(10) + "        ")
            print(f"  FAIL  {'exec' if block.executed else 'load'}  {block.where}\n        {indented}")

    print()
    print(f"{counts['executed'][0]}/{counts['executed'][1]} executed blocks behaved as declared")
    print(f"{counts['load'][0]}/{counts['load'][1]} load-checked blocks consulted without diagnostics")
    if unmarked:
        print(f"{len(unmarked)} blocks checked at neither tier:")
        for where in unmarked:
            print(f"  -     none  {where}")
    print("The two tiers are different guarantees. Do not add them together.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

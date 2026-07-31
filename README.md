# logic-programming-skills

Reference skills for coding agents working in logic programming. Every executable
code sample is run before release.

## Skills

| Skill | Covers | Agent | Verified | Licence |
| --- | --- | --- | --- | --- |
| [`dev-prolog`](skills/dev-prolog/) | SWI-Prolog: relations over procedures, CLP(FD) over `is/2`, `findall`/`bagof`/`setof`, `library(aggregate)`, DCGs and the `S0`/`S` translation, difference lists, `meta_predicate/1`, modes and steadfastness, PlUnit. Three references. | Claude Code | 19 of 38 blocks executed, 0 failures | MIT |
| [`dev-scasp`](skills/dev-scasp/) | s(CASP) via `library(scasp)`: default and classical negation, the dual program, integrity constraints, even-loop choice, abducibles, `model(M)`, `#pred` annotations, human-readable justifications. Three references. | Claude Code | 12 of 38 blocks executed, 0 failures | MIT |

The blocks that are not executed are clause fragments and REPL transcripts. They
are not standalone programs.

Skills under other licences live in their own repositories. A repository has one
`LICENSE`.

## Install

As a plugin marketplace:

```
/plugin marketplace add aktagon/logic-programming-skills
/plugin install dev-prolog@logic-programming-skills
/plugin install dev-scasp@logic-programming-skills
```

Or copy the directory:

```bash
git clone https://github.com/aktagon/logic-programming-skills.git
cp -R logic-programming-skills/skills/dev-prolog ~/.claude/skills/dev-prolog
```

Both routes install the same files.

## Verification

A code block opts in to execution by making `% !verify` its first line. The
checker writes the block to a file and runs it:

```
swipl -q -g main -t halt <file>
```

The block defines `main/0` and fails if an assertion does not hold, so the block
decides what correct means. A `% !verify-fails` block asserts that its program
must not succeed, which is how a trap is documented without shipping code that
appears to work.

Blocks without a marker are not run. Two rounds of expert review found twelve
factual errors across these two skills. Every one was in an unmarked block or in
prose. No marked block was ever wrong.

The checker ships inside each skill. It depends only on the Python standard
library. It installs nothing, downloads nothing, and starts no service:

```bash
python3 skills/<skill>/scripts/verify_snippets.py skills/<skill>
```

It requires `swipl` on `PATH`. `dev-scasp` also requires the s(CASP) pack:

```
?- pack_install(scasp).
```

Verified against SWI-Prolog 9.2.9.

## Editing

This repository is published from another one. Changes committed here are
replaced on the next release. Open an issue instead;
[CONTRIBUTING.md](CONTRIBUTING.md) describes what a report should contain.

## Licence

MIT. See [LICENSE](LICENSE). Each skill ships its own licence and credits.

[Aktagon](https://aktagon.com).

# logic-programming-skills

Reference skills for coding agents working in logic programming. Every executable
code sample is run before release.

## Skills

| Skill | Covers | Agent | Verified | Licence |
| --- | --- | --- | --- | --- |
| [`dev-prolog`](skills/dev-prolog/) | SWI-Prolog: relations over procedures, CLP(FD) over `is/2`, `findall`/`bagof`/`setof`, `library(aggregate)`, DCGs and the `S0`/`S` translation, difference lists, `meta_predicate/1`, modes and steadfastness, PlUnit. Three references. | Claude Code, Codex, Gemini CLI | 30 of 42 blocks executed, 8 load-checked, 0 failures | MIT |
| [`dev-scasp`](skills/dev-scasp/) | s(CASP) via `library(scasp)`: default and classical negation, the dual program, integrity constraints, even-loop choice, abducibles, `model(M)`, `#pred` annotations, human-readable justifications. Three references. | Claude Code, Codex, Gemini CLI | 20 of 39 blocks executed, 18 load-checked, 0 failures | MIT |

The two counts are not added together. An executed block ran under `swipl` and
its own assertions held. A load-checked block consulted as declared, and nothing
ran. Parsing is not correctness. Three rounds of expert review found eighteen
factual errors in these skills, and every one was in a block that parses.

Five blocks are checked at neither tier:

| Block | Why |
| --- | --- |
| `dev-prolog` `SKILL.md`, "Running SWI-Prolog" | `?- [file].` names a file that does not exist. `trace` and `gtrace` are interactive. |
| `dev-prolog` `references/idioms.md`, the four-port model | `?- trace, ancestor(tom, X).` is interactive. |
| `dev-prolog` `references/purity-and-modes.md`, steadfastness, first block | `p(In, Out), Out == Expected` is notation. `p` is a placeholder, not a predicate. |
| `dev-prolog` `references/purity-and-modes.md`, steadfastness, second block | `p(In, Expected)` is the other half of that notation. |
| `dev-scasp` `references/examples.md`, `hamcycle_two.pl` | An abbreviation, not a program. Its `reachable`, `chosen`, and `other` clauses are elided as prose. |

Skills under other licences live in their own repositories. A repository has one
`LICENSE`.

## Install

Pick one route per agent. The package under `skills/<name>/` is the same
directory for every agent.

### Claude Code, as a plugin

```
/plugin install logic-programming-skills --marketplace aktagon/logic-programming-skills
```

This installs every skill in the pack. To install one skill:

```
/plugin install dev-prolog --marketplace aktagon/logic-programming-skills
/plugin install dev-scasp --marketplace aktagon/logic-programming-skills
```

### Any agent, with the `skills` CLI

[`skills`](https://github.com/vercel-labs/skills) is a third-party installer from
Vercel Labs. It needs Node.js.

```bash
npx skills add aktagon/logic-programming-skills
npx skills add aktagon/logic-programming-skills --skill <name>
```

The first command asks which skills and which agents to install. The second
installs one skill. Installs go to the current project. Add `-g` to install for
your user account. The CLI sends anonymous usage data. Set `DISABLE_TELEMETRY=1`
to turn that off.

### By hand

Clone the repository and copy a skill directory into the folder your agent
reads. Create that folder first if it does not exist.

```bash
git clone https://github.com/aktagon/logic-programming-skills.git
cp -R logic-programming-skills/skills/<name> ~/.claude/skills/<name>   # Claude Code
cp -R logic-programming-skills/skills/<name> ~/.agents/skills/<name>   # Codex and Gemini CLI
```

### Two copies of the same skill

Installing a skill by two routes installs it twice. Pick one route per agent,
and delete the other copy before switching.

## Verification

A code block opts in to execution by making `% !verify` its first line. The
checker writes the block to a file and runs it:

```
swipl -q -g main -t halt <file>
```

The block defines `main/0` and fails if an assertion does not hold, so it decides
what correct means. A `% !verify-fails` block asserts that its program must not
succeed. That is how a trap is documented without shipping code that appears to
work.

A `% !load` block is consulted rather than run. The check fails if `swipl` writes
anything to stderr. The exit code is not read, because `swipl` exits 0 on a
syntax error. Singleton warnings are suppressed in this tier, so a misspelled
variable name in a load-checked block is not reported.

A `% !load-fails` block asserts the reverse and names the diagnostic it expects.
That is how `references/examples.md` keeps two upstream files that do not load
under SWI-Prolog, without rewriting them.

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

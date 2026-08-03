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

The package under `skills/<name>/` is the same directory for every agent. Only
the root manifest differs.

### Claude Code

As a plugin marketplace:

```
/plugin marketplace add aktagon/logic-programming-skills
/plugin install dev-prolog@logic-programming-skills
/plugin install dev-scasp@logic-programming-skills
```

The marketplace manifest is `.claude-plugin/marketplace.json`.

### Codex

Codex searches for skills in `$CWD/.agents/skills`, `$CWD/../.agents/skills`,
`$REPO_ROOT/.agents/skills`, `$HOME/.agents/skills`, and `/etc/codex/skills`.
Copy the skill into one of them:

```bash
git clone https://github.com/aktagon/logic-programming-skills.git
mkdir -p ~/.agents/skills
cp -R logic-programming-skills/skills/dev-prolog ~/.agents/skills/dev-prolog
cp -R logic-programming-skills/skills/dev-scasp  ~/.agents/skills/dev-scasp
```

Use `.agents/skills/` inside a repository instead to scope the skills to one
project. The plugin manifest is `.codex-plugin/plugin.json`; the Codex plugin
channel is review-gated through <https://platform.openai.com/plugins>.

### Gemini CLI

Gemini resolves skills from `~/.gemini/skills/` and from its `~/.agents/skills/`
alias, and from `.gemini/skills/` or `.agents/skills/` inside a workspace:

```bash
git clone https://github.com/aktagon/logic-programming-skills.git
mkdir -p ~/.gemini/skills
cp -R logic-programming-skills/skills/dev-prolog ~/.gemini/skills/dev-prolog
cp -R logic-programming-skills/skills/dev-scasp  ~/.gemini/skills/dev-scasp
```

The extension manifest is `gemini-extension.json` at the repository root. To
develop against a local clone, `gemini extensions link` registers the checkout in
`~/.gemini/extensions`.

### Two copies of the same skill

Each agent reads every one of its skill directories, and installing by two routes
installs the skill twice. On Claude Code, adding the plugin while
`~/.claude/skills/dev-prolog` already exists gives two copies of `dev-prolog`.
The same applies to `~/.agents/skills/` on Codex and Gemini, which both read that
path. Pick one route per agent, and delete the other copy before switching.

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

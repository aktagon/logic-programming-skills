# dev-scasp

A coding-agent skill for s(CASP), the goal-directed Answer Set Programming system
that runs inside SWI-Prolog via `library(scasp)`. Every executable code sample is
run against a real `swipl` and a real `scasp` pack before release.

## Verification

39 code blocks, checked at two tiers.

| Tier | Blocks | What the tier establishes |
| --- | --- | --- |
| Executed | 20 | The block ran under `swipl` and its own assertions held. |
| Load-checked | 18 | The block consulted as declared. Nothing ran. |
| Neither | 1 | Named below. |

The two tiers are not added together. An executed block establishes the claim it
makes. A load-checked block establishes only that the source parses.

A block opts in to execution by making `% !verify` its first line. The checker
writes the block to a file and runs it:

```
swipl -q -g main -t halt <file>
```

The block decides what correct means, because it defines `main/0` and fails if an
assertion does not hold. A `% !verify-fails` block asserts the opposite: the
program must not succeed.

A `% !load` block is consulted rather than run. The check fails if `swipl` writes
anything to stderr. The exit code is not read, because `swipl` exits 0 on a
syntax error. Singleton warnings are suppressed in this tier, because a `#pred`
template references its head variables only inside quoted atoms, which makes
every one of them a singleton. A misspelled variable name in a load-checked block
is therefore not reported.

A `% !load-fails` block asserts the reverse and names the diagnostic it expects.
Two upstream examples in `references/examples.md` carry it. `hamcycle.pl` fails
because its headless `:- Body.` constraints run as ordinary Prolog directives.
`queens.pl` fails because s(CASP)'s reader sets `allow_variable_name_as_functor`
and SWI's does not. Both files are reproduced verbatim. Rewriting them to load
cleanly would delete the evidence for what `references/examples.md` says about
them.

One block carries no marker:

| Block | Why |
| --- | --- |
| `references/examples.md`, `hamcycle_two.pl` | An abbreviation, not a program. Its `reachable`, `chosen`, and `other` clauses are elided as prose. |

Verified against SWI-Prolog 9.2.9 and the SWI port of the s(CASP) pack.

Run it:

```bash
cd skills/dev-scasp && python3 scripts/verify_snippets.py
```

The checker depends only on the Python standard library.

## Why the marker matters

Three rounds of expert review found eighteen factual errors across this skill and
its companion `dev-prolog`. Every one was in a block that was not executed, or in
prose. No block carrying `% !verify` was ever wrong.

A load check would have caught none of the eighteen. Every one of them was in a
block that parses. One was a malformed `#pred`, which loads with no diagnostic at
all.

The third round found five more in this skill, all in prose that two earlier
reviews had read and accepted:

| Claim as written | What `swipl` showed |
| --- | --- |
| A `p`/`-p` inconsistency "returns no answers for anything, `p(2)` included" | It is scoped to the inconsistent predicate. With `p(1)`, `-p(1)`, `q(7)`: both `p/1` atoms return nothing, `q(7)` still answers. |
| `birds.pl` errors on consult with `bird/1: Unknown procedure: penguin/2` | No such message exists. The directive fails: `Goal (directive) failed: user:flies(_748)`. |
| `queens.pl` ends with `scasp_predicate 'user:nqueens'/2 does not exist` | Thirteen syntax errors is right; the tail is `catch/3: Unknown procedure: nqueens/2`. |
| "unscoped 5 lines and 3 ms, scoped 30 lines and 6 ms" | The scoped query has no answer, so it renders no tree. There was never a 30-line version to measure. |
| The NMR block emits `it may be the case that alice may borrow book1` | Absent from that program's tree. Its NMR lines all read `there is no evidence that bob may borrow ...`. |

Three of those errors changed the guidance, not the wording:

| Claim as written | What `swipl` showed |
| --- | --- |
| `not p(_)` is a performance problem, fixed by a 0-ary wrapper | It is unsound. With `basis(consent)` established, `not basis(_)` still succeeds. The anonymous variable is quantified inside the negation. |
| `p`/`-p` inconsistency only applies inside `begin_scasp` | It applies in plain consult too. How far it reaches was itself overstated, and the third round corrected it above. |
| Annotate everything with `#pred`, and write constraints inside `begin_scasp` | Following both produces unannotated output. A `#pred` inside the block compiles into `_scasp_<Unit>`, and the renderer resolves against the caller's module. |

The first one is worth following through. The unsound version renders a five-line
proof tree. The correct version renders no tree at all, because it has no answer.
The skill's own "proof-tree size is a linter" heuristic therefore argued for the
bug, and a reader applying that heuristic would have picked the wrong rule.

## What is in the package

| Path | Contents |
| --- | --- |
| `SKILL.md` | When s(CASP) rather than Prolog or clingo, the dual program, the two loading modes, OLONs, even-loop choice, `model(M)` and `scasp_model/1`, `#pred`, the `scasp/2` cut hazard, testing |
| `references/justification.md` | Rendering a tree, suppressing the NMR block, where `#pred` must live, reading a bloated tree, emitting reason terms instead of scraping prose |
| `references/performance.md` | The dual program, the free-variable blowup, unscoped existentials, query ordering, tree-size gates |
| `references/examples.md` | Six worked programs from the upstream port: abduction, defaults, inconsistency, integrity constraints, n-queens |
| `scripts/verify_snippets.py` | The gate |

## Scope

Pinned to the SWI-Prolog port of s(CASP), `library(scasp)`. The Ciao original and
the standalone distribution differ in option names and justification rendering.
Treat any Ciao-specific flag as unverified here.

The skill records five known issues in its frontmatter, including one upstream
packaging bug: the documented `qtest_scasp` entry point resolves tests under
`test/programs/`, and the directory is `test/all_programs/`.

For ordinary Prolog, see `dev-prolog` in this repository.

## Licence

MIT. See [LICENSE](LICENSE).

[Aktagon](https://aktagon.com).

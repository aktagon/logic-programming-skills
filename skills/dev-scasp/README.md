# dev-scasp

A Claude Code skill for s(CASP), the goal-directed Answer Set Programming system
that runs inside SWI-Prolog via `library(scasp)`. Every executable code sample is
run against a real `swipl` and a real `scasp` pack before release.

## Verification

38 code blocks. 12 are complete programs and are executed. 26 are rule fragments
or transcribed upstream examples, which are not standalone programs and are not
run.

A block opts in by making `% !verify` its first line. The checker writes the
block to a file and runs it:

```
swipl -q -g main -t halt <file>
```

Verified against SWI-Prolog 9.2.9 and the SWI port of the s(CASP) pack.

Run it:

```bash
cd skills/dev-scasp && python3 scripts/verify_snippets.py
```

The checker depends only on the Python standard library.

## Why the marker matters

Two rounds of expert review found twelve factual errors across this skill and its
companion `dev-prolog`. Every one was in an unmarked block or in prose. No block
carrying `% !verify` was ever wrong.

Three of those errors changed the guidance, not the wording:

| Claim as written | What `swipl` showed |
| --- | --- |
| `not p(_)` is a performance problem, fixed by a 0-ary wrapper | It is unsound. With `basis(consent)` established, `not basis(_)` still succeeds. The anonymous variable is quantified inside the negation. |
| `p`/`-p` inconsistency only applies inside `begin_scasp` | It applies in plain consult too. A file holding `p(1)` and `-p(1)` answers nothing for any query, `p(2)` included. |
| Annotate everything with `#pred`, and write constraints inside `begin_scasp` | Following both produces unannotated output. A `#pred` inside the block compiles into `_scasp_<Unit>`, and the renderer resolves against the caller's module. |

The first is the sharpest. The unsound version renders a 5-line proof tree where
the correct version renders 30, so the skill's own "proof-tree size is a linter"
heuristic argued for the bug.

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

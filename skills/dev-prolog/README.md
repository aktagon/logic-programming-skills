# dev-prolog

A Claude Code skill for SWI-Prolog. Every executable code sample is run against a
real `swipl` before release.

## Verification

38 Prolog code blocks. 19 are complete programs and are executed. 19 are clause
fragments or REPL transcripts, which are not standalone programs and are not run.

A block opts in by making `% !verify` its first line. The checker writes the
block to a file and runs it:

```
swipl -q -g main -t halt <file>
```

The block decides what correct means, because it defines `main/0` and fails if an
assertion does not hold. A `% !verify-fails` block asserts the opposite: the
program must not succeed. That marker is how a trap is documented without
shipping code that appears to work.

Verified against SWI-Prolog 9.2.9.

Run it:

```bash
cd skills/dev-prolog && python3 scripts/verify_snippets.py
```

The checker depends only on the Python standard library. It installs nothing and
starts no service.

## Why the marker matters

Two rounds of expert review found twelve factual errors in this skill and its
companion `dev-scasp`. Every one was in an unmarked block or in prose. No block
carrying `% !verify` was ever wrong.

Four of those errors were found by running a claim rather than reading it:

| Claim as written | What `swipl` showed |
| --- | --- |
| `meta_predicate/1` rewrites the call site at compile time | `clause/2` returns the body unqualified. The wrapping happens at call time. |
| `-->` compiles to `S0 = [a\|S1], ...` | It folds a leading terminal into the head: `abc([a\|A], B) :- bs(A, C), C=[c\|B].` |
| `atom_concat(?A, ?B, +AB)` | Fully reversible. `atom_concat(A, B, abc)` yields four solutions. |
| Under `double_quotes, codes` the backquote form needs changing | `back_quotes` is a separate flag. Both forms work. |

## What is in the package

| Path | Contents |
| --- | --- |
| `SKILL.md` | Relations over procedures, CLP(FD) over `is/2`, lists, `findall`/`bagof`/`setof`, `library(aggregate)`, strings and codes, DCGs and the `S0`/`S` translation, `meta_predicate/1`, PlUnit |
| `references/purity-and-modes.md` | Modes, steadfastness, determinism and indexing, `dif/2`, termination and tabling, a review checklist |
| `references/idioms.md` | The four-port model, argument-order conventions, recursion patterns, difference lists, cut discipline, common pitfalls |
| `references/reading.md` | External articles, talks, and worked examples |
| `scripts/verify_snippets.py` | The gate |

## Scope

SWI-Prolog. CLP(FD) is `library(clpfd)` here. GNU Prolog and SICStus expose
similar operators through different modules, so treat any module path in this
skill as SWI-specific.

For default reasoning, defeasible rules, and justifications, see `dev-scasp` in
this repository.

## Licence

MIT. See [LICENSE](LICENSE).

[Aktagon](https://aktagon.com).

# dev-prolog

A coding-agent skill for SWI-Prolog. Every executable code sample is run against
a real `swipl` before release.

## Verification

42 Prolog code blocks, checked at two tiers.

| Tier | Blocks | What the tier establishes |
| --- | --- | --- |
| Executed | 30 | The block ran under `swipl` and its own assertions held. |
| Load-checked | 8 | The block consulted with no diagnostic. Nothing ran. |
| Neither | 4 | Named below. |

The two tiers are not added together. An executed block establishes the claim it
makes. A load-checked block establishes only that the source parses.

A block opts in to execution by making `% !verify` its first line. The checker
writes the block to a file and runs it:

```
swipl -q -g main -t halt <file>
```

The block decides what correct means, because it defines `main/0` and fails if an
assertion does not hold. A `% !verify-fails` block asserts the opposite: the
program must not succeed. That marker is how a trap is documented without
shipping code that appears to work.

A `% !load` block is consulted rather than run. The check fails if `swipl` writes
anything to stderr. The exit code is not read, because `swipl` exits 0 on a
syntax error. Singleton warnings are suppressed in this tier, because a
documentation fragment legitimately mentions a variable once. A misspelled
variable name in a load-checked block is therefore not reported.

Four blocks carry no marker:

| Block | Why |
| --- | --- |
| `SKILL.md`, "Running SWI-Prolog" | `?- [file].` names a file that does not exist. `trace` and `gtrace` are interactive. |
| `references/idioms.md`, the four-port model | `?- trace, ancestor(tom, X).` is interactive. |
| `references/purity-and-modes.md`, steadfastness, first block | `p(In, Out), Out == Expected` is notation. `p` is a placeholder, not a predicate. |
| `references/purity-and-modes.md`, steadfastness, second block | `p(In, Expected)` is the other half of that notation. |

Verified against SWI-Prolog 9.2.9.

Run it:

```bash
cd skills/dev-prolog && python3 scripts/verify_snippets.py
```

The checker depends only on the Python standard library. It installs nothing and
starts no service.

## Why the marker matters

Three rounds of expert review found eighteen factual errors in this skill and its
companion `dev-scasp`. Every one was in a block that was not executed, or in
prose. No block carrying `% !verify` was ever wrong.

A load check would have caught none of the eighteen. Every one of them was in a
block that parses.

The third round refuted "tabling changes complexity, not semantics" by running
the same clauses twice. Untabled they yield `[a-b, b-c, a-c, a-c]`. Tabled, they
yield `[a-b, a-c, b-c]`. Two earlier reviews had read that claim and accepted it.

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

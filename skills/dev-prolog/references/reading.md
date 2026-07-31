# Further Reading

Curated external resources for learning Prolog by working through real problems. Grouped by the _kind of problem_ Prolog is being used to solve, not by media type — reach for the section that matches the task in front of you, not the one that matches a keyword.

## Planning and state-space search

Prolog's backtracking engine is a search procedure you do not have to write. Planning problems — given a start state, find a sequence of actions to a goal state — fall out of clause structure plus a goal predicate.

- **Planning container shipping using Prolog** — [Part 1](http://quantumprolog.sgml.io/container-planning-demo/part1.html) · [Part 2](http://quantumprolog.sgml.io/container-planning-demo/part2.html). Worked example of modelling a logistics problem as facts (containers, ships, routes), rules (allowed loadings), and a planner that produces an action sequence. Read this when you are tempted to write a planner imperatively — the Prolog version is almost always shorter and corresponds more directly to the problem statement.

## Constraint Logic Programming over Finite Domains — CLP(FD)

Pure Prolog enumerates solutions; CLP(FD) (in SWI-Prolog: `library(clpfd)`) _constrains_ a search space and lets a constraint solver prune it. Use CLP(FD) when the problem is combinatorial and the naive generate-and-test is too slow — Sudoku, scheduling, n-queens, cryptarithmetic.

- **Solving a Dungeons & Dragons riddle in Prolog** — four solutions to the same puzzle, useful as a study in _style_:
  - [Pure Prolog](https://gist.github.com/Spuffynism/446c7c2d498477491d8137e8f234d4a9) — readable but slow on larger instances.
  - [CLP(FD) variant](https://gist.github.com/Spuffynism/446c7c2d498477491d8137e8f234d4a9?permalink_comment_id=4421962#gistcomment-4421962) — same problem, declarative constraints.
  - [Mikko Tiihonen's solution on SWISH](https://swish.swi-prolog.org/p/OfkjNgmI.pl) and his [HN explanation](https://news.ycombinator.com/item?id=34226269) — runnable in-browser.
  - [Topological sort with `tsort` + bash](https://news.ycombinator.com/item?id=34230891) — the "you might not need Prolog" counterpoint. Useful sanity check before reaching for the heavy tool.

## Deductive databases and Prolog as a query language

A Prolog database with rules is a _deductive database_: facts are tuples and rules are recursive views. This is where Prolog overlaps with Datalog and where it can replace SQL when you need recursive joins or non-trivial inference.

- **Prolog as a database query language** — [XSB textbook, §11](https://www3.cs.stonybrook.edu/~warren/xsbbook/node11.html). Shows how SQL-style queries (selection, projection, join) map to Prolog clauses, and where Prolog goes beyond what SQL can express.
- **Deductive databases** — [XSB textbook, §12](https://www3.cs.stonybrook.edu/~warren/xsbbook/node12.html). Builds on the previous chapter to cover tabling (memoization), well-founded semantics, and recursive views — the techniques that make Prolog/Datalog viable for real query workloads.

XSB is one specific Prolog system but the concepts (tabling, deductive views) transfer to SWI-Prolog with `library(tabling)`.

## Scripting and real-world I/O

Prolog is unfairly stereotyped as an academic toy. The two links below show it doing ordinary glue work — CSV ingestion and a business-rule check — which is most of what production code actually is.

- **SWI-Prolog for scripting (CSV parsing)** — [r/prolog thread](https://www.reddit.com/r/prolog/comments/oqcxp3/swiprolog_for_scripting/?utm_source=reddit&utm_medium=usertext&utm_name=prolog&utm_content=t1_j1ai936). Practical answers on reading delimited input, shelling out, and using SWI-Prolog as a scripting language with `swipl` shebangs.
- **Prolog at work — loan applicant validation** — [old.reddit.com/r/prolog](https://old.reddit.com/r/prolog/comments/zswi13/prolog_at_work/). Business-rule engine for a financial product: eligibility predicates, rule composition, and the case for Prolog when rules change faster than the codebase.

## Talks and longer-form learning

- **The Power of Prolog — Markus Triska's YouTube channel** — [@PowerOfProlog](https://www.youtube.com/channel/UCFFeNyzCEQDS4KCecugmotg). The canonical modern video series on idiomatic SWI-Prolog: pure code, CLP(FD), DCGs, meta-interpreters. If you watch one set of Prolog talks, watch these — Triska is rigorous about declarative style and consistently demonstrates _why_ it matters (testability, reversibility, soundness).

## Where to go next

- For _symbolic reasoning under negation_ (default rules, contradictions, justifications), Prolog alone is awkward — switch to **s(CASP)**, the goal-directed Answer Set Programming system that runs inside SWI-Prolog. See `dev-scasp` for default negation, classic negation, abducibles, integrity constraints, and human-readable justifications.
- For _constraint solving over rationals or reals_, see `library(clpq)` and `library(clpr)` — same idea as CLP(FD) but for non-integer domains.
- For _grammars and parsing_, see Definite Clause Grammars (DCGs) — Prolog's built-in PEG-like parser notation. The Triska channel has a dedicated playlist.

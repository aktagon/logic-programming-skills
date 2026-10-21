# s(CASP) Examples Walkthrough

Six worked examples from the [JanWielemaker/sCASP](https://github.com/JanWielemaker/sCASP) SWI-Prolog port, each chosen because it isolates one core construct. Read in order; each example assumes you have read the previous one.

Four are reproduced here, under Apache-2.0 — see
[ATTRIBUTION.md](ATTRIBUTION.md). Two are linked with a `curl` command instead,
for the licence reason §4 gives.

## How this file is checked

**The reproduced blocks are verbatim upstream transcriptions and are
deliberately not rewritten.** One of them does not load under SWI-Prolog, and
that is the point: this file documents *why*, so replacing it with a
`scasp/2`-driven equivalent would delete the specimen that proves the claim.

They are therefore checked at the load tier rather than the executed one, in both
directions:

| Example | Directive | What is checked |
| --- | --- | --- |
| `rps.pl`, `birds.pl`, `classic_negation_incostistent.pl` | `% !load` | consults with no diagnostic |
| `queens.pl` | `% !load-fails` | SWI's reader rejects `_nqueens` as a functor |
| `hamcycle.pl`, `hamcycle_two.pl` | none | not reproduced here; §4 links them and gives a `curl` command |

`hamcycle.pl` was the second `% !load-fails` specimen until 2026-10-21. It is now
linked rather than printed, for the licence reason §4 gives, so `queens.pl` is the
only live proof of that directive. The trap `hamcycle.pl` demonstrated is still
described in §4 and in SKILL.md; it is no longer demonstrated by a block this
repository ships.

A load check proves a block parses and consults. It proves nothing about whether
the walkthrough around it is *true* — for that, see the executed blocks in
`performance.md` and `justification.md`.

## 1. `rps.pl` — abducibles and predicate annotations

```prolog
% !load scasp
:- use_module(library(scasp)).
:- use_module(library(scasp/human)).

#pred player('G', 'X') :: '@(X) played in @(G)'.
#pred winner('Game','Player') :: 'The winner of @(Game) is @(Player)'.
#pred throw('Player','Sign') :: '@(Player) threw @(Sign)'.
#pred beat('Sign','OtherSign') :: '@(Sign) beats @(OtherSign)'.

beat(rock,scissors).
beat(scissors,paper).
beat(paper,rock).

#abducible player(Game, Player).
#abducible throw(Player, Sign).

winner(Game,Player) :-
  player(Game, Player),
  player(Game, OtherPlayer),
  throw(Player,Sign),
  throw(OtherPlayer,OtherSign),
  beat(Sign,OtherSign).
```

**What it teaches.** The program has no concrete `player/2` or `throw/2` facts — they are declared `#abducible`. When you query `?- winner(g1, alice).`, s(CASP) _abduces_ the facts that would make alice win: `player(g1, alice)`, `player(g1, A)`, `throw(alice, rock)`, `throw(A, scissors)`. Abduction is the inverse of deduction — you get back the assumptions the solver had to make. Note that the opponent stays an unbound `A`: abduction assumes *that there is* such a player, not who.

**Annotation pattern.** The `'G'` quoting in `#pred player('G', 'X')` marks variable _names_ for justifications, and the `@(X)` placeholder is filled with the binding at justification time. The quotes are not load-bearing under `library(scasp)`: `#pred player(G, X)` with ordinary variables renders identically. They matter for files read by the standalone executable's reader.

## 2. `birds.pl` — default reasoning

```prolog
% !load scasp
penguin(sam).
wounded_bird(john).
bird(tweety).
bird(X) :- penguin(X).
bird(X) :- wounded_bird(X).

ab(X) :- penguin(X).
ab(X) :- wounded_bird(X).

flies(X) :- bird(X), not ab(X).

-flies(X) :- ab(X).
-flies(X) :- -bird(X).

-wounded_bird(X) :- not wounded_bird(X).
-bird(X) :- not bird(X).
-penguin(X) :- not penguin(X).
-ab(X) :- not ab(X).

?- flies(X).
```

**What it teaches.** The classic default-reasoning benchmark. `flies(X)` holds for normal birds and is blocked by an _abnormality_ predicate `ab/1` that penguins and wounded birds satisfy. Run `?- flies(X)` and only `tweety` flies.

**Three patterns to internalize:**

1. **Abnormality predicate.** `flies(X) :- bird(X), not ab(X).` reads as "X flies if X is a bird and there is no reason to consider X abnormal." This is the standard way to encode defaults in ASP.
2. **Default vs classic negation interplay.** `-flies(X) :- ab(X).` — penguins are _known_ not to fly (classic). `flies(X) :- bird(X), not ab(X).` — a default. The two coexist because they apply to disjoint cases.
3. **Explicit closed-world axioms.** `-bird(X) :- not bird(X).` makes the closed-world assumption for `bird/1` explicit: if we cannot show X is a bird, treat X as not a bird. Without this axiom, `-bird(X)` would never derive and `-flies(X) :- -bird(X)` would not fire.

The trailing `?- flies(X).` is a **Prolog directive**, and it does not do what the file's shape suggests. Consulted verbatim after `library(scasp)` is loaded, it fires at load time and fails:

```
Warning: birds.pl:20: Singleton variables: [X]
Warning: birds.pl:20: Goal (directive) failed: user:flies(_748)
```

A failed directive, not an error, and nothing is printed. Querying through the solver is what works: `findall(X, scasp(flies(X), [tree(_)]), L)` gives `L == [tweety]`. Treat the trailing directive as an artifact of files written for the standalone `scasp` executable, not as a way to run them from SWI-Prolog.

The `% !load scasp` marker on the block above rewrites that `?-` line into a clause rather than firing it, which is why the block load-checks clean while the verbatim file above does not. The load tier checks that the source parses. It deliberately does not run a transcript's queries.

## 3. `classic_negation_incostistent.pl` — what inconsistency looks like

```prolog
% !load scasp
p(1).
-p(1).

%% no model since the program is inconsistent
?- p(2).
```

**What it teaches.** Three lines. `p(1)` and `-p(1)` both hold, so `p/1` is _inconsistent_ and has no stable model. Querying `p(2)` returns no answer.

Read the upstream comment carefully. `p(2)` here has no clause, so it would return nothing in a consistent program too — this file cannot distinguish "killed by the inconsistency" from "never derivable". Add `p(2).` as a fact and it still returns nothing, which is the real demonstration. Add an unrelated `q(7).` and that one still answers: the check is scoped to `p/1`, not to the program. SKILL.md runs both halves.

**Takeaway.** Classic negation `-p` is not "not p" — it is "p is explicitly false." If both `p(X)` and `-p(X)` are derivable for the same X, every atom of `p/1` is unanswerable, not just `p(X)`. This is one of the easiest s(CASP) mistakes to make and one of the hardest to debug; when a query "mysteriously fails for every input," check the queried predicate for an accidental `p(X)` / `-p(X)` overlap.

## 4 and 5. `hamcycle.pl` and `hamcycle_two.pl` — linked, not reproduced

**Fetch them, they are not printed here:**

```bash
S=https://raw.githubusercontent.com/JanWielemaker/sCASP/72028b02d57e51fe24c4be54234ab75767cd469f
curl -O $S/examples/hamcycle.pl
curl -O $S/examples/hamcycle_two.pl
swipl -g 'use_module(library(scasp/main)), main(["hamcycle.pl"])' -t halt
```

The URL pins commit `72028b0`. Do not swap it for a branch name: upstream's
default branch is `swipl`, a `master` branch also exists, and the two carry
different copies of `hamcycle.pl`. A branch link would drift away from what this
page describes, which is the whole failure a pin prevents.

**Why these two are linked while the other four are printed.** Both appear in
upstream's `test/all_programs/sasp/` as well as its `examples/`, byte-identical
in both places. That directory is named after
[s(ASP)](https://sourceforge.net/projects/sasp-system/) by Kyle Marple, which
SourceForge lists as **GPLv3**, while s(CASP) itself is Apache-2.0. Whether these
files actually originate in the s(ASP) distribution is unverified — the evidence
is a directory name and an identical copy, not a confirmed lineage. Rather than
argue it, this page does not reproduce them. A link carries no licence
obligation, so the question stops mattering.

**What they teach.** A Hamiltonian-cycle solver in about fifteen lines. Two
patterns carry it, and both are worth recognising in your own code.

1. **Choice via negation.** A clause of the form "chosen if the edge exists and
   no *other* edge is chosen from this vertex", paired with a helper defining
   *other* as "a different chosen edge from the same vertex". The two together
   force exactly one selection per vertex, with no counting and no arithmetic.
2. **Integrity constraints as denials.** A headless `:- Body.` clause reads as
   *reject any model where Body holds* — one rejecting models that leave a vertex
   unreachable, another rejecting models where two vertices point at the same
   target. Constraints eliminate models; they never derive facts.

Together that is the standard ASP generate-and-test shape, in three short
clauses.

**`hamcycle_two.pl` changes only the facts.** Same rules, a four-vertex graph
with seven edges instead of a three-vertex one. That is the declarative payoff
stated as plainly as it ever gets: when the rules are stable and the facts change
often, this is the right tool. When the rules churn and the data is fixed, it is
not. Use that as the test before reaching for s(CASP) on a new problem.

**The trap, which is why `hamcycle.pl` was marked `% !load-fails`.** Its headless
`:- Body.` constraints run as ordinary directives under a plain `swipl` load and
fail, rather than acting as constraints. SKILL.md covers that live. Load it
through `library(scasp/main)` as above, not with a bare `swipl hamcycle.pl`.

## 6. `queens.pl` — even-loop choice and Prolog-style recursion

```prolog
% !load-fails scasp
% !expect Syntax error: Operator expected
nqueens(N, Q) :- _nqueens(N, N, [], Q).

_nqueens(X, N, Qi, Qo) :-
    X > 0,
    _pickqueen(X, Y, N),
    not _attack(X, Y, Qi),
    X1 is X - 1,
    _nqueens(X1, N, [q(X, Y) | Qi], Qo).
_nqueens(0, _, Q, Q).

_pickqueen(X, Y, Y) :- Y > 0, q(X, Y).
_pickqueen(X, Y, N) :- N > 1, N1 is N - 1, _pickqueen(X, Y, N1).

_attack(X, _, [q(X, _) | _]).          % same row
_attack(_, Y, [q(_, Y) | _]).          % same col
_attack(X, Y, [q(X2, Y2) | _]) :-      % same diagonal
    Xd is X2 - X, _abs(Xd, Xd2),
    Yd is Y2 - Y, _abs(Yd, Yd2),
    Xd2 = Yd2.
_attack(X, Y, [_ | T]) :- _attack(X, Y, T).

q(X, Y) :- not _negq(X, Y).
_negq(X, Y) :- not q(X, Y).

_abs(X, X) :- X >= 0.
_abs(X, Y) :- X < 0, Y is X * -1.

?- nqueens(4, Q).
```

**What it teaches.** N-queens mixes ASP-style choice with Prolog-style recursion — the two-paradigm-in-one-file mode that is s(CASP)'s real differentiator.

1. **Even loop for choice.** `q(X, Y) :- not _negq(X, Y).` / `_negq(X, Y) :- not q(X, Y).` is the same "construct choice via mutual negation" pattern as `hamcycle.pl`, but applied to the _board square_ relation. The solver explores stable models where each `q(X,Y)` is independently true or false.
2. **Prolog-style recursion drives the search.** `_nqueens/4` is ordinary recursive Prolog — pick a queen, check it does not attack previous ones, recurse with one row fewer. The accumulator `Qi → Qo` is the standard Prolog idiom from `dev-prolog`.
3. **Arithmetic uses `is`, not `=`.** `X1 is X - 1` (evaluation) vs `X1 = X - 1` (unification with the term `-(X,1)`).
4. **`_nqueens` is a variable name used as a functor, not a naming convention.** s(CASP)'s own reader sets `allow_variable_name_as_functor` (`prolog/scasp/input.pl`), which is what makes `_nqueens(...)` and `_attack(...)` parse at all. SWI's ordinary reader rejects them: consulting `queens.pl` after `use_module(library(scasp))` gives thirteen `Syntax error: Operator expected` lines, and then the trailing directive fails against the clauses that never compiled:

```
ERROR: queens.pl:28: catch/3: Unknown procedure: nqueens/2
Warning: queens.pl:28: Goal (directive) failed: user:nqueens(4,_8114)
```

The file runs under the standalone executable (`./scasp -s0 examples/queens.pl`), not by consulting it. Do not copy the leading underscore into rules you intend to consult from SWI-Prolog — Prolog has no "private predicate" convention for it to mean.

The header comment lists the two solutions to 4-queens:

```
% 4-queens: ((1,2),(2,4),(3,1),(4,3)) and ((1,3),(2,1),(3,4),(4,2))
```

Querying `?- nqueens(4, Q).` produces both via backtracking, demonstrating that s(CASP) enumerates _all_ stable models when asked.

## Patterns summary

| Pattern                         | Example          | When to use                                                                   |
| ------------------------------- | ---------------- | ----------------------------------------------------------------------------- |
| `#abducible`                    | rps              | Solver may freely assume these facts to satisfy the query.                    |
| `#pred ... :: '...'`            | rps, birds       | Always add for predicates you want in justifications.                         |
| Abnormality (`ab(X)`)           | birds            | Encode defaults — "X flies unless X is abnormal."                             |
| Classic + default negation      | birds            | Distinguish "X is known false" from "we have no evidence for X."              |
| Explicit closed-world axiom     | birds            | `-p(X) :- not p(X).` makes CWA derivable, not just assumed.                   |
| Integrity constraint `:- Body.` | hamcycle, queens | Eliminate stable models — "this combination is forbidden."                    |
| Even-loop choice                | hamcycle, queens | `p :- not q.` `q :- not p.` constructs a choice point.                        |
| Same rules + different facts    | hamcycle_two (linked) | The declarative win: only data changes between problem instances.        |
| Mix with Prolog-style recursion | queens           | Use Prolog idioms (accumulators, arithmetic, list patterns) within s(CASP).   |
| Top-level `?- Goal.` directive  | birds, queens    | Fires at file consult; convenient for examples, problematic for library code. |

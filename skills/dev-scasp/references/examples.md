# s(CASP) Examples Walkthrough

Six worked examples from the [JanWielemaker/sCASP](https://github.com/JanWielemaker/sCASP) SWI-Prolog port, each chosen because it isolates one core construct. Read in order; each example assumes you have read the previous one.

## 1. `rps.pl` — abducibles and predicate annotations

```prolog
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

The trailing `?- flies(X).` is a **Prolog directive**, and it does not do what the file's shape suggests. Consulted after `library(scasp)` is loaded, it fires at load time and errors (`bird/1: Unknown procedure: penguin/2`); consulted without `library(scasp)` preloaded, every `#pred` line is a syntax error first. Neither prints `tweety`. Querying through the solver does: `findall(X, scasp(flies(X), [tree(_)]), L)` gives `L == [tweety]`. Treat the trailing directive as an artifact of files written for the standalone `scasp` executable, not as a way to run them from SWI-Prolog.

## 3. `classic_negation_incostistent.pl` — what inconsistency looks like

```prolog
p(1).
-p(1).

%% no model since the program is inconsistent
?- p(2).
```

**What it teaches.** Three lines. `p(1)` and `-p(1)` both hold — the program is _inconsistent_ and has no stable model. Querying _anything_, even an unrelated `p(2)`, returns no answer.

**Takeaway.** Classic negation `-p` is not "not p" — it is "p is explicitly false." If both `p(X)` and `-p(X)` are derivable for the same X, the entire program is broken, not just `p(X)`. This is one of the easiest s(CASP) mistakes to make and one of the hardest to debug; when a query "mysteriously fails for every input," check for accidental `p(X)` / `-p(X)` overlap.

## 4. `hamcycle.pl` — integrity constraints and choice

```prolog
vertex(0). vertex(1). vertex(2).
edge(0, 1). edge(1, 2). edge(2, 0).

reachable(V) :- chosen(U, V), reachable(U).
reachable(0) :- chosen(V, 0).

% Every vertex must be reachable.
:- vertex(U), not reachable(U).

% Choose exactly one edge from each vertex.
other(U, V) :-
    vertex(U), vertex(V), vertex(W),
    edge(U, W), V \= W, chosen(U, W).
chosen(U, V) :-
    edge(U, V), not other(U, V).

% You cannot choose two edges to the same vertex
:- chosen(U, W), chosen(V, W), U \= V.
?- chosen(1,2).
```

**What it teaches.** A Hamiltonian-cycle solver in 15 lines. Two patterns dominate:

1. **Choice via negation.** `chosen(U, V) :- edge(U, V), not other(U, V).` The `other/2` helper says "there is a different chosen edge from U." Combining them, `chosen` is true exactly when no _other_ edge is chosen from U — forcing exactly-one selection per vertex.
2. **Integrity constraints as denials.** `:- vertex(U), not reachable(U).` reads as "_reject any model where_ some vertex is unreachable." `:- chosen(U,W), chosen(V,W), U \= V.` rejects models where two distinct vertices both point to W. Constraints eliminate models; they do not derive facts.

The combination — choice + constraints — is the standard ASP "generate and test" pattern, expressed in three short clauses.

## 5. `hamcycle_two.pl` — the same template at scale

```prolog
vertex(0). vertex(1). vertex(2). vertex(3).
edge(0, 1). edge(1, 2). edge(2, 3). edge(3, 0).
edge(2, 0). edge(0, 3). edge(3, 1).

% ... reachable/chosen/other clauses identical to hamcycle.pl ...
:- chosen(U, W), chosen(V, W), U \= V.
?- chosen(1,2).
```

**What it teaches.** _The rules do not change. Only the facts change._ This is the declarative payoff: a 4-vertex graph with 7 edges runs the same Hamiltonian-cycle solver as the 3-vertex graph in example 4, with no edits to the logic. Compare with the procedural equivalent (graph traversal in any imperative language) and the difference in code volume is dramatic.

**Use this as a teaching contrast.** When evaluating "should we use Prolog/s(CASP) here?", look for problems where the _rules_ are stable and the _facts_ change frequently. That is the sweet spot.

## 6. `queens.pl` — even-loop choice and Prolog-style recursion

```prolog
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
4. **`_nqueens` is a variable name used as a functor, not a naming convention.** s(CASP)'s own reader sets `allow_variable_name_as_functor` (`prolog/scasp/input.pl`), which is what makes `_nqueens(...)` and `_attack(...)` parse at all. SWI's ordinary reader rejects them: consulting `queens.pl` after `use_module(library(scasp))` gives thirteen `Syntax error: Operator expected` lines and then `scasp_predicate 'user:nqueens'/2 does not exist`. The file runs under the standalone executable (`./scasp -s0 examples/queens.pl`), not by consulting it. Do not copy the leading underscore into rules you intend to consult from SWI-Prolog — Prolog has no "private predicate" convention for it to mean.

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
| Same rules + different facts    | hamcycle_two     | The declarative win: only data changes between problem instances.             |
| Mix with Prolog-style recursion | queens           | Use Prolog idioms (accumulators, arithmetic, list patterns) within s(CASP).   |
| Top-level `?- Goal.` directive  | birds, queens    | Fires at file consult; convenient for examples, problematic for library code. |

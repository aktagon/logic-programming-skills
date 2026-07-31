---
# DO NOT EDIT — compiled output. Edit the source seed and regenerate; edits made here are overwritten on the next build.
name: dev-scasp
description: 'Use when writing, reviewing, or debugging s(CASP) programs — the goal-directed Answer Set Programming system running inside SWI-Prolog via `library(scasp)`. Covers default negation (`not`), classical negation (`-`), abducibles (`#abducible`), integrity constraints (`:- Body.`), even-loop choice construction, predicate annotations (`#pred ... :: ''@(X)...''`), the dual program and how unbound variables make it explode, and human-readable justifications. Fires on s(CASP) topics even when the user does not say "s(CASP)" explicitly — e.g. "default reasoning in Prolog", "abductive reasoning", "stable models with Prolog syntax", "integrity constraint over a knowledge base", "expert system with defeasible rules", "explainable rules engine", or any task whose source of truth is a set of Horn-ish rules with default negation and goal-directed ASP semantics.'
user-invocable: false
license: MIT
metadata:
  domain: development
  subdomain: backend
  packs:
  - logic-programming-skills
  role: engineer
  version: "2.3.0"
  tags:
  - asp
  - explainability
  - logic-programming
  - prolog
  - scasp
  triggers: scasp, s(casp), answer set programming, asp, default negation, classic negation, abducible, abduction, defeasible rules, stable model, integrity constraint, goal-directed asp, library(scasp), swi-prolog asp, justification, proof tree, explainable rules
  scope: implementation
  output-format: code
  related-skills: dev-prolog, dev-tla-plus, ontologist
  known_issues:
  - '#pred directives make their head variables genuine singletons (the @(X) references live inside quoted atoms), so every rule file needs :- style_check(-singleton). to consult without warnings. The directive is file-scoped, not global: SWI restores style flags at the end of the file load, so a second file consulted afterwards still warns.'
  - 'A #pred written inside a begin_scasp/end_scasp block is silently ignored by human_justification_tree/2. The template compiles pr_pred_predicate/4 into the unit''s private module (_scasp_<Unit>), but the renderer resolves templates against the module the tree''s atoms strip to — the caller''s. Put #pred after :- end_scasp. Verified both ways on SWI-Prolog 9.2.9.'
  - 'Cutting a scasp/2 call (with ->, once/1, or any commit) poisons the process: every later scasp/2 raises determinism_error(scasp_solve:stack_parents/3,det,fail,property). scasp/2 stores its stack via backtrackable b_setval; a cut prevents the untrail, so the next query inherits a stale module-qualified stack. findall/3 around every call PREVENTS it but does not repair it — after a cut has happened, findall-wrapped calls error too. Repair with nb_delete(scasp_stack), nb_delete(scasp_model), nb_delete(scasp_tree).'
  - 'Only the headless `:- Body.` integrity constraint is mode-dependent. In a plain file consulted with library(scasp) and queried via scasp/2, `:- Body.` is an ordinary Prolog directive that runs at load time and constrains nothing; it is compiled into an NMR check only inside :- begin_scasp(...) ... :- end_scasp. The p/-p consistency check runs in BOTH modes — verified: a plain-consult file with p(1) and -p(1) returns no answers for any query, including an unrelated p(2).'
  - Pinned to the SWI-Prolog port of s(CASP) (library(scasp)), verified on SWI-Prolog 9.2.9. The Ciao original and the standalone distribution differ in option names and justification rendering; treat any Ciao-specific flag as unverified here.
  - 'The pack''s documented quick-test entry point (swipl -g qtest_scasp, or the -q flag) is broken in the SWI port: quick_test_file/2 resolves scasp(test/programs/<name>) but the directory is test/all_programs/. Run the harness with an explicit directory argument instead: swipl test/test_scasp.pl test/small_programs.'
  - 'The presence of a trailing ''The global constraints hold'' block does not indicate begin_scasp mode. The NMR check also carries the p/-p consistency constraints, so any plain-consult program using classical negation renders the block too (verified: 13 lines with it, 4 with justify_nmr(false), no begin_scasp anywhere).'
  - human_justification_tree/2 renders constrained variables as 'any number not [a,b,c]' even when the values are atoms rather than numbers. This is upstream wording that leaks the constraint store into user-facing text.
---

# s(CASP) Development

Write goal-directed Answer Set Programs that run inside SWI-Prolog. s(CASP) extends
Prolog with stable-model semantics, classical negation, integrity constraints, and
abducibles — and unlike clingo or DLV it does **not** ground the program first, so
lists, structured terms, and unbound variables work as they do in Prolog.

The reason to pay that price is the **justification**. s(CASP) can tell you *why*
it concluded something, in English, derived from the same proof that produced the
answer. If you do not need the explanation, you probably want plain Prolog or
clingo instead.

## Routing

| You are working on… | Read |
| --- | --- |
| justifications, `#pred`, proof-tree noise, wiring a verdict into an application | `references/justification.md` |
| slow queries, dual-program blowup, `not` over an existential, tree-size gates | `references/performance.md` |
| worked programs: abduction, defaults, integrity constraints, n-queens | `references/examples.md` |

## When s(CASP) instead of plain Prolog

Prolog gives you SLD resolution: try goals, backtrack on failure. That breaks down
when you need:

- **Default reasoning** — "X flies unless we know X is abnormal." Prolog's `\+` is tied to the proof procedure, not to stable semantics, and defaults compose badly under it.
- **Defeasible knowledge** — rules a more specific rule can override.
- **Integrity constraints** — "no model where both X and Y hold." Prolog has no native denial.
- **Justifications** — a proof tree you can show a human.
- **Abduction** — "what would have to be true for this to hold?"

If the problem is state-space search or querying a deductive database, stay in
Prolog (see `dev-prolog`).

## When s(CASP) instead of clingo / DLV

Traditional ASP solvers ground the program before solving — fast on small finite
domains, infeasible on large or infinite ones. s(CASP) is goal-directed and
explores only what the query needs. Choose it when the domain is large or uses
structured terms, when you need a justification per answer, or when you are
already inside SWI-Prolog. Choose clingo for raw throughput on a fully grounded
finite problem.

## Principles

1. **Goal-directed, not grounded.** Execution starts from the query. Recursive rules over arbitrary terms are fine.
2. **`not` is default negation.** `not p` holds when there is a stable model without `p` — not merely when the prover failed. It is not `\+`.
3. **`-p` is a different atom from `p`.** Deriving both makes the program inconsistent: no model. This is how you distinguish "we know it is false" from "we have no reason to believe it".
4. **`:- Body.` eliminates models.** A headless clause is a denial — the idiomatic way to forbid a combination.
5. **Even loops construct choice.** `p :- not q.` `q :- not p.` yields two stable models. This is how you say "pick one".
6. **Annotate everything you will show a human.** Without `#pred`, justifications are unreadable internal goals — and the justification is the whole reason you are here.

## The dual program — the thing that actually bites

To prove `not p`, s(CASP) does not fail-and-return. It compiles a **dual program**
that constructively refutes every clause of `p` for every binding. Two consequences
dominate practical work.

**Unbound variables in a negated context multiply the proof.** Each free variable
position becomes its own "forall" branch in the dual — verified: a negated
three-argument call with two anonymous variables renders as three branches, one
per argument position.

There is a second, *separate* bug that tends to travel with it, and the two are
easy to conflate. Re-deriving from the database a value the caller already knows
is unsound in plain Prolog too — no dual program is involved, because the faulty
unification happens on the **positive** proof path:

```prolog
% BAD: P is unbound, so it matches any processing/3 fact in the database,
% not the one under query. A second, unrelated fact silently defeats the guard.
exception(consent) :-
    claimed(consent),
    processing(_, _, P),
    not high_risk(P).
```

```prolog
% GOOD: the caller binds P. The dual collapses, and the guard cannot be
% satisfied by some other activity's data.
exception(consent, P) :-
    claimed(consent),
    not high_risk(P).
```

This is not hypothetical — it is the most common way a working rule set becomes
unsound as it grows, and it is invisible to any test whose fact base holds a
single instance. Name the rule accurately, though: **do not re-derive from the
database a value the caller already has.** That is a scoping discipline, not an
ASP subtlety. The dual-program cost above is a *separate* reason to bind
variables before a negated goal, and the two problems reinforce each other
because the same sloppy call site causes both.

**Wrap existentials in a 0-ary helper.** `not p(_)` does not mean "no `p`
exists". The anonymous variable is quantified *inside* the negation, so it reads
"there is some value for which `p` is not derivable" — trivially true over an
open domain, whatever the fact base holds. Verified: with `basis(consent)`
established, `not basis(_)` still succeeds. Move the existential into a positive
predicate and the quantifier lands outside the `not`:

```prolog
has_basis :- basis(_).                       % existential inside a POSITIVE goal
decision(X) :- thing(X), not has_basis.      % now `not` negates "a basis exists"
```

This is a correctness fix, not a tuning one, and the failure is silent. Note the
counter-intuitive consequence: the *wrong* version renders the shorter proof
tree, so "the tree got smaller" is not evidence of an improvement here.

Full treatment, with the measurement and how to read a bloated proof tree as a
diagnostic: `references/performance.md`.

## Quick Reference

### Loading and querying

```prolog
:- use_module(library(scasp)).
:- use_module(library(scasp/human)).   % human-readable justifications
```

```prolog
?- scasp(flies(X), [tree(T)]).          % solve, capture the justification
?- ? flies(X).                          % REPL shorthand (also ??, ?--, ?+-, ?-+, ?++)
```

`scasp_justification/2` is `(-Tree, +Options)` and reads the **current answer's**
global — it is not `(Goal, Tree)`. It is for `begin_scasp` mode, where the goal
is an ordinary call with nowhere to hang an options list:

```prolog
?- may_borrow(alice, book1), scasp_justification(T, []).   % begin_scasp exports
```

In plain-consult mode there is no such call to follow — `flies(tweety)` on its
own is an ordinary Prolog goal that never enters the solver, so
`flies(tweety), scasp_justification(T, [])` yields nothing. Use the `tree(T)`
option on `scasp/2` instead.

### Reading the answer: `model(M)` and `scasp_model/1`

An answer has two halves. The **justification tree** is the human half. The
**model** is the machine half — a plain list of literals, and the thing your
application should branch on.

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

bird(tweety).
bird(polly).
penguin(tweety).

flies(X)  :- bird(X), not ab(X).
-flies(X) :- penguin(X).
ab(X)     :- penguin(X).

#pred flies(X) :: '@(X) can fly'.

in_model(M, L) :- memberchk(L, M).

main :-
    findall(M, scasp(flies(polly), [model(M)]), [Model]),
    in_model(Model, flies(polly)),
    in_model(Model, bird(polly)),
    in_model(Model, not ab(polly)),          % default negation, as a term
    \+ in_model(Model, flies(tweety)),       % goal-directed: the model is PARTIAL
    findall(M2, scasp(-flies(tweety), [model(M2)]), [Denied]),
    in_model(Denied, -flies(tweety)),        % classical negation, as a term
    in_model(Denied, penguin(tweety)).
```

Three literal shapes appear: `p` (derived), `not p` (default-negated), `-p`
(classically false). `not` and `-` are operators `library(scasp)` declares, so
these are ordinary Prolog terms — `memberchk/2` and clause-head matching work on
them directly, with no parsing.

The model is **partial**. Goal-directed solving records only the literals the
proof needed: the answer for `flies(polly)` says nothing at all about `tweety`.
This is the sharp difference from clingo, whose models are total over the
grounded program. Never read the *absence* of a literal as "false" — absence
means "not visited".

`model(M)` is an option on `scasp/2`. `scasp_model/1` is the same data read back
from the current answer's global, which is what you need in `begin_scasp` mode,
where exports are called as ordinary goals and there is no options list:

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

:- begin_scasp(coin, [heads/0, tails/0]).
heads :- not tails.
tails :- not heads.
:- end_scasp.

main :-
    findall(M, (heads, scasp_model(M)), [Model]),
    memberchk(heads, Model),
    memberchk(not tails, Model).       % the model records which branch was taken
```

Like `scasp_justification/2`, `scasp_model/1` is `(-Model)` reading a global, not
`(Goal, Model)`. Call it immediately after the goal, inside the same `findall/3`.

### Default vs classical negation

```prolog
flies(X) :- bird(X), not ab(X).      % default: no reason to think X abnormal
-flies(X) :- penguin(X).             % classical: we know X does not fly
ab(X) :- penguin(X).
```

### Declaring 0-ary input flags

Facts asserted only when true should still be declared, so the loader does not
warn about a predicate that legitimately has no clauses:

```prolog
:- dynamic consent_withdrawn/0, legal_mandate/0.
```

Without the declaration you get `Warning: scasp_predicate 'user:consent_withdrawn'/0
does not exist` — a warning, not an error. The query still succeeds and absence is
still treated as falsity, so this is hygiene rather than correctness. Declaring
the flags also documents the rule file's input interface, which is the better
argument for doing it.

Do this for genuine 0-ary input flags only — never for a predicate whose clauses
the rule set itself enumerates.

### Two loading modes — and integrity constraints only work in one

This is the trap that invalidates the most advice. There are two ways to get
s(CASP) rules into SWI-Prolog, and they are not equivalent:

**Plain consult** (`:- use_module(library(scasp)).` then ordinary clauses,
queried with `scasp/2`). Convenient, and what every short example here uses. But
a headless `:- Body.` clause is just a **Prolog directive** — it runs at load
time and constrains nothing. Your own integrity constraints are absent.

Be precise about what is *not* absent. `p`/`-p` consistency **is** enforced in
plain consult, and it is enforced the same brutal way: a file holding both `p(1)`
and `-p(1)` returns no answers for anything, `p(2)` included. There is an NMR
check in this mode; it just contains only the consistency constraints the
compiler derived, not the ones you wrote.

**A `begin_scasp` block.** Only here is `:- Body.` compiled as an integrity
constraint. Note the second difference: exported predicates are then called as
**ordinary goals**, not through `scasp/2`.

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

:- begin_scasp(demo, [ok/1]).
p(1).
p(2).
ok(X) :- p(X).
:- ok(2).                     % integrity constraint: no model may contain ok(2)
:- end_scasp.

holds(G) :- findall(t, G, [_|_]).      % exports are plain goals here

main :-
    \+ holds(ok(2)),          % killed by the constraint, as expected...
    \+ holds(ok(1)).          % ...and so is ok(1): the program has NO model
```

That second line is the point. `ok(2)` is derivable, so the constraint eliminates
every candidate model — including the ones that would have answered `ok(1)`.
Integrity constraints are global; they do not merely prune the goal you asked
about. This is the usual reason a rule set "returns nothing and I cannot see
why".

You cannot tell the two modes apart from the trailing
`The global constraints hold, because …` block. It reports whatever the NMR check
holds, and in plain consult that already includes the `p`/`-p` consistency
constraints — verified: a plain-consult program with `-flies(X) :- penguin(X).`
and no `begin_scasp` anywhere renders the block, 13 lines against 4 with
`justify_nmr(false)`. To confirm *your* constraint is live, read what the block
contains, or test it directly the way the block above does.

Write anything that depends on your own denials or NMR checks inside
`begin_scasp`/`end_scasp`.

**But keep `#pred` outside the block.** The two rules pull in opposite
directions and the conflict is silent. A `#pred` written *inside*
`begin_scasp`/`end_scasp` compiles into the unit's private module
(`_scasp_<Unit>`), while `scasp_justification/2` hands back atoms qualified with
the module you called from. The renderer looks for the template in the latter,
finds nothing, and falls back to `may_borrow holds for alice, and book1` — no
error, no warning, just unannotated output. Moving the same directives after
`:- end_scasp.` renders `alice may borrow book1`. Verified both ways in
`references/justification.md`.

### OLONs — odd loops over negation

An **OLON** is a cycle through `not` of odd length. The minimal case:

```prolog
p :- not p.
```

There is no stable model containing `p` (it would refute itself) and none without
it (then the rule fires). An OLON therefore does not "produce a choice" the way an
even loop does — it **constrains** the models, killing any candidate in which the
loop is not otherwise broken.

This is the machinery behind integrity constraints. `:- Body.` is compiled into an
OLON of the shape `nmr_chk :- Body, not nmr_chk.`, collected into the NMR check
that runs after the query's own proof. That is why:

- the justification shows a trailing "global constraints hold" block — it is the OLON check reporting;
- integrity constraints need `begin_scasp` (above) — outside it, nothing performs that compilation;
- a program can be satisfiable yet have every candidate model killed by a constraint far from the queried goal.

Even loops (below) construct choice; odd loops eliminate it. Confusing them is the
usual reason a rule set "has no models and I cannot see why".

### Choice via even loops

```prolog
q(X, Y) :- not not_q(X, Y).
not_q(X, Y) :- not q(X, Y).
```

The two models are a property of the *program*, not of a query: asking
`q(1, 2)` returns a single answer, whose model records the choice that was made.
Use `scasp/2`'s `model(M)` option, not the answer alone, when you need to see
which branch was taken — the coin example under "Reading the answer" above is
this pattern, executed.

### Abducibles

```prolog
#abducible player(Game, Player).
#abducible throw(Player, Sign).
```

### Constraints, not `is/2`

s(CASP) ships its own constraint operators (`#=`, `#<`, `#>`, `#=<`, `#>=`, and
disequality) via `prolog/scasp/clp/`. Use them for any numeric threshold — an age
limit, a retention period, a monetary cap. They are declared as goals, so the
solver can reason about them in the dual program instead of demanding a bound
value:

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

age(alice, 15).
age(bob, 22).

minor(P) :- age(P, A), A #< 18.
adult(P) :- age(P, A), A #>= 18.

#pred minor(P) :: '@(P) is a minor'.
#pred adult(P) :: '@(P) is an adult'.

holds(G) :- findall(t, scasp(G, [tree(_)]), [_|_]).

main :- holds(minor(alice)), \+ holds(minor(bob)), holds(adult(bob)).
```

`is/2` and `>/2` work when everything is ground, and the classic examples use
them, but they foreclose the modes that make a rule set interesting — you cannot
ask "for which ages would this be permitted?" of an `is/2` program. For a
regulatory rule set, where thresholds are the substance, prefer the `#` forms
from the start.

### Predicate annotations

```prolog
#pred bird(X)    :: '@(X) is a bird'.
#pred flies(X)   :: '@(X) can fly'.
#pred -flies(X)  :: '@(X) can not fly'.
#pred ab(X)      :: '@(X:bird) is abnormal'.
```

`@(Var)` interpolates the binding; `@(Var:Type)` adds a type hint. Annotate the
classically-negated head too — denials are exactly what a human will ask about.

Place these **outside** any `begin_scasp`/`end_scasp` block. Inside one they
compile into the unit's private module and the renderer never finds them —
silently. See "Two loading modes" above and `references/justification.md`.

### Never cut a `scasp/2` call

**Cutting a `scasp/2` call poisons the process.** Every subsequent `scasp/2`
then raises:

```
determinism_error(scasp_solve:stack_parents/3, det, fail, property)
```

The mechanism: `scasp/2` saves its stack with backtrackable `b_setval`. A cut
prevents the untrail, so the next query inherits a stale module-qualified stack
that `stack_parents/3` — declared `:- det` — cannot decompose. The trigger is the
**cut**, not success: a call that simply fails leaves nothing behind.

That makes `->` and `once/1` around `scasp/2` unsafe, which rules out the most
natural way to write a verdict. Exhaust the goal instead:

```prolog
% Prevention. Safe to call repeatedly, in any mix of success and failure.
holds(Goal) :- findall(t, scasp(Goal, [tree(_)]), [_|_]).
```

`findall/3` is **prevention, not a cure**. Once a cut call has run, even
findall-wrapped calls error. To recover — for instance in a long-lived service
that inherited the state from library code you do not control — clear the three
globals:

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).
bird(polly).
flies(X) :- bird(X), not ab(X).
#pred flies(X) :: '@(X) can fly'.

holds(G) :- findall(t, scasp(G, [tree(_)]), [_|_]).
scasp_reset :-
    forall(member(K, [scasp_stack, scasp_model, scasp_tree]), ignore(nb_delete(K))).

poisoned(G) :- catch(holds(G), error(determinism_error(_,_,_,_), _), fail).

main :-
    holds(flies(polly)), holds(flies(polly)),      % findall throughout: fine
    ( scasp(flies(polly), [tree(_)]) -> true ; true ),   % one cut call...
    \+ poisoned(flies(polly)),                     % ...and findall now errors
    scasp_reset,
    holds(flies(polly)).                           % repaired
```

This block is the claim, executed: repeated `findall` calls are fine, a single
cut call breaks the next one even under `findall`, and clearing the globals
restores it.

One fresh process per query sidesteps all of this at the cost of interpreter
startup, which is a legitimate architecture for a request-scoped service rather
than merely a workaround.

### A complete, runnable program

```prolog
% !verify
:- use_module(library(scasp)).
% #pred templates reference variables only inside quoted strings, so the
% variables in the head are genuine singletons. Suppress the warnings.
:- style_check(-singleton).

bird(tweety).
bird(polly).
penguin(tweety).

flies(X) :- bird(X), not ab(X).
ab(X) :- penguin(X).

#pred bird(X)  :: '@(X) is a bird'.
#pred flies(X) :: '@(X) can fly'.
#pred ab(X)    :: '@(X) is abnormal'.

holds(Goal) :- findall(t, scasp(Goal, [tree(_)]), [_|_]).

main :-
    holds(flies(polly)),
    \+ holds(flies(tweety)),
    holds(flies(polly)).       % re-entrant: would error under `->`
```

## Testing an s(CASP) program

Assert on the **model**. Not on the justification tree, and never on its rendered
text.

The pack's own harness (`test/test_scasp.pl`) makes the case. It snapshots
`Stacks-Models` per program into a `.pass` file, then grades in tiers: identical
stacks is `passed`; **different stacks with the same models is reported and
tolerated**; only a model difference that survives canonicalisation is a hard
failure. Upstream treats a changed proof tree as noise and a changed model as a
bug. Your tests should agree.

That leaves three assertion levels, in order of preference:

1. **Does the goal hold?** — the verdict. Cheapest, most stable.
2. **Is this literal in the model?** — the grounds. Use `memberchk/2` on the model, not equality against the whole list: the model is partial and its contents shift as unrelated rules are added.
3. **Snapshot the whole model** — regression detection only. Expect to re-bless it whenever the rule set grows, and never let it be the only test.

```prolog
% !verify
:- use_module(library(scasp)).
:- use_module(library(plunit)).
:- style_check(-singleton).

% --- rule set -------------------------------------------------------
processing(acme, health, insurance_scoring).
processing(acme, health, medical_treatment).   % the SECOND fact is the point
special(health).
consent(medical_treatment).

may_process(C, D, P)  :- processing(C, D, P), not special(D).
may_process(C, D, P)  :- processing(C, D, P), special(D), consent(P).
-may_process(C, D, P) :- processing(C, D, P), special(D), not consent(P).

#pred may_process(C,D,P) :: '@(C) may process @(D) data for @(P)'.

% --- harness --------------------------------------------------------
models(Goal, Ms) :- findall(M, scasp(Goal, [model(M)]), Ms).
holds(Goal)      :- models(Goal, [_|_]).

:- begin_tests(gdpr).

test(consented_purpose_allowed) :-
    holds(may_process(acme, health, medical_treatment)).

test(unconsented_purpose_denied) :-
    \+ holds(may_process(acme, health, insurance_scoring)),
    holds(-may_process(acme, health, insurance_scoring)).

test(model_records_the_grounds) :-
    models(may_process(acme, health, medical_treatment), [M|_]),
    memberchk(consent(medical_treatment), M),
    memberchk(special(health), M).

:- end_tests(gdpr).

main :- run_tests.
```

Four rules that hold up:

- **Every fixture needs at least two facts per input predicate.** A rule that reaches into the database for a value the caller already has is *correct* against a single-instance fixture and unsound against two. That is the most expensive bug in this skill and a one-fact fixture cannot see it — `references/performance.md` runs it.
- **Assert the denial separately from the failure of the permission.** `\+ holds(may_process(…))` and `holds(-may_process(…))` are different claims: the first says "not proved", the second says "proved false". A rule set that returns neither is a gap, and only testing both distinguishes it.
- **Every `scasp/2` goes through `findall/3`, tests included.** PlUnit's `[fail]` and `[throws(_)]` options wrap the goal, and a cut around `scasp/2` poisons every later query in the process — including the rest of the suite. See "Never cut a `scasp/2` call".
- **Gate on justification size.** Add one test asserting the line count of a rendered canonical justification stays under a bound. It is crude, but it catches the free-variable regressions that no verdict-level test will, and unlike a timing assertion it is stable across machines. `references/performance.md` has the measurement.

Run the pack's own suite as a smoke test when you suspect the install rather than
your rules. Pass a directory — the harness takes paths as arguments:

```sh
swipl <pack>/test/test_scasp.pl <pack>/test/small_programs   # seconds
swipl <pack>/test/test_scasp.pl <pack>/test/all_programs     # the full suite
```

Do **not** use the documented `-q` / `qtest_scasp` shortcut: in the SWI pack it
resolves tests under `test/programs/`, which does not exist (the directory is
`test/all_programs/`), and dies with
`source_sink 'scasp(test/programs/pq)' does not exist`. That is an upstream
packaging bug, not a broken install.

## Don't

- **Don't conflate `not` with `\+`.** `\+` is SWI's procedural negation-as-failure; `not` under `library(scasp)` is default negation with stable semantics.
- **Don't put a cut (`!`) in an s(CASP) clause.** It breaks the declarative reading and the stable-model search.
- **Don't leave variables unbound in a negated context.** See the dual-program section — it costs correctness, not just speed.
- **Don't write `not p(_)`.** It means "some value fails `p`", which is true by default over an open domain. Wrap the existential in a 0-ary predicate and negate that.
- **Don't define both `p` and `-p` casually.** Any argument deriving both makes the program inconsistent. Use `-p :- not p.` only when you genuinely intend an explicit closed-world assumption.
- **Don't parse the rendered justification to drive control flow.** The English text is for humans and is coupled to both your `#pred` wording and the pack's phrasing. Emit a reason *term* instead — `references/justification.md`.
- **Don't write top-level `?- Goal.` directives in a library file** you want other code to consult; the directive fires at load time.
- **Don't skip `#pred` annotations.** Without them you have a slower clingo.
- **Don't put `#pred` inside a `begin_scasp` block.** It compiles into the unit's private module, the renderer never finds it, and nothing warns you.
- **Don't assert on a justification tree in a test.** Assert on the model. Upstream's own harness tolerates a changed tree and fails on a changed model.
- **Don't read the absence of a literal from a model as "false".** Goal-directed models are partial; absence means the proof never went there.

## Verification standard

Every fenced block marked `% !verify` in this skill is executed against a real
SWI-Prolog + `scasp` install:

```sh
uv run scripts/verify_snippets.py
```

Blocks without the marker are illustrative fragments. Add the marker to any
example you expect to keep working.

## Attribution

Patterns adapted from the [SWI-Prolog port of s(CASP)](https://github.com/JanWielemaker/sCASP)
by Jan Wielemaker, which ports the original
[s(CASP)](https://gitlab.software.imdea.org/ciao-lang/sCASP) by Joaquín Arias and
the IMDEA / UTD team. Theory: Arias, Carro, Salazar, Marple, Gupta, "Constraint
Answer Set Programming without Grounding" (TPLP 2018).

The dual-program guidance, the `justify_nmr(false)` option, and the reason-term
pattern were derived from debugging a production GDPR rule set, not from the
upstream documentation.


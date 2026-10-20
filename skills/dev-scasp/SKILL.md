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
  - developer-skills
  - logic-programming-skills
  openai:
    display_name: s(CASP)
    short_description: Goal-directed ASP with readable justifications
    default_prompt: Use $SKILL to write this s(CASP) program.
    products:
    - api
    - atlas
    - chatgpt
    - codex
    allow_implicit_invocation: true
  role: engineer
  version: "2.7.0"
  tags:
  - asp
  - explainability
  - logic-programming
  - prolog
  - scasp
  triggers: scasp, s(casp), answer set programming, asp, default negation, classic negation, abducible, abduction, defeasible rules, stable model, integrity constraint, goal-directed asp, library(scasp), swi-prolog asp, justification, proof tree, explainable rules, aggregation in asp, sum over clauses, rules do not add up, negation over a list, host rules boundary, mutation testing rules
  scope: implementation
  output-format: code
  related-skills: dev-prolog, dev-tla-plus, ontologist
  known_issues:
  - '#pred directives make their head variables genuine singletons (the @(X) references live inside quoted atoms), so every rule file needs :- style_check(-singleton). to consult without warnings. The directive is file-scoped, not global: SWI restores style flags at the end of the file load, so a second file consulted afterwards still warns.'
  - 'A #pred written inside a begin_scasp/end_scasp block is silently ignored by human_justification_tree/2. The template compiles pr_pred_predicate/4 into the unit''s private module (_scasp_<Unit>), but the renderer resolves templates against the module the tree''s atoms strip to — the caller''s. Put #pred after :- end_scasp. Verified both ways on SWI-Prolog 9.2.9.'
  - 'Cutting a scasp/2 call (with ->, once/1, or any commit) poisons the process: every later scasp/2 raises determinism_error(scasp_solve:stack_parents/3,det,fail,property). scasp/2 stores its stack via backtrackable b_setval; a cut prevents the untrail, so the next query inherits a stale module-qualified stack. findall/3 around every call PREVENTS it but does not repair it — after a cut has happened, findall-wrapped calls error too. Repair with nb_delete(scasp_stack), nb_delete(scasp_model), nb_delete(scasp_tree).'
  - 'Only the headless `:- Body.` integrity constraint is mode-dependent. In a plain file consulted with library(scasp) and queried via scasp/2, `:- Body.` is an ordinary Prolog directive that runs at load time and constrains nothing; it is compiled into an NMR check only inside :- begin_scasp(...) ... :- end_scasp. The p/-p consistency check runs in BOTH modes, but it is scoped to the offending predicate, not to the program — verified on a plain-consult file holding p(1), p(2), -p(1) and q(7): both p(1) and p(2) return no answers, while q(7) and a rule calling it still answer normally.'
  - Pinned to the SWI-Prolog port of s(CASP) (library(scasp)), verified on SWI-Prolog 9.2.9. The Ciao original and the standalone distribution differ in option names and justification rendering; treat any Ciao-specific flag as unverified here.
  - 'Reserved generated names, verified against pack source: `_false_0` for headless integrity-constraint rules (pr_rules.pl:478, nmr_check.pl:83-84); `o_nmr_check` for the negative-loop check (compile.pl:132,182); the `o_chk<N>` family for global constraints (common.pl:122-127). Note `o_` is used pervasively for generated names but is NOT in reserved_prefix/1, so user atoms starting `o_` are unguarded on input while the compiler emits names that could collide by exact match. Separately, innermost dual predicates are generated as `<Name>_vh<Arity>` (comp_duals.pl:161-164) — a SUFFIX, so no prefix check finds it.'
  - 'The pack''s documented quick-test entry point (swipl -g qtest_scasp, or the -q flag) is broken in the SWI port: quick_test_file/2 resolves scasp(test/programs/<name>) but the directory is test/all_programs/. Run the harness with an explicit directory argument instead: swipl test/test_scasp.pl test/small_programs.'
  - 'The presence of a trailing ''The global constraints hold'' block does not indicate begin_scasp mode. The NMR check also carries the p/-p consistency constraints, so any plain-consult program using classical negation renders the block too (verified on the tweety/polly program with no begin_scasp anywhere: querying -flies(tweety) gives 13 lines with the block and 4 with justify_nmr(false)). The absolute numbers are per-query, not per-program — the same program queried flies(polly) gives 16 and 6.'
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

## Sorts — s(CASP) has no types, and a wrong-KIND term reaches a verdict cleanly

The universe is untyped atoms. Nothing distinguishes a person from a company, a
percentage from a share count, or a date from an id, so a term of the wrong
*kind* unifies, proves, and renders a clean justification tree. This is not
exotic: it is what happens the first time a caller passes an argument in the
wrong position and no rule objects.

**Declare a sort per argument position, and require it in the rules.**

```prolog
% !load scasp
#pred person(X) :: '@(X) on luonnollinen henkilö'.

person(X) :- person_fact(X).                 % a stated finding, never inferred

works_in_leadership(P, C) :- person(P), company(C), ceo(P, C).
```

Four things this section exists to say, each of which cost something to learn.

- **A two-facts-per-predicate fixture cannot help.** That discipline catches a
  goal binding to the wrong *row*; a sort violation binds to another *kind*.
  Different bug, different detector — a fixture with two companies and no person
  is exactly as blind as a fixture with one.
- **Infer nothing.** The tempting one-liner is "anything appearing as a
  shareholder is an entity, anything with a family relation is a person", and it
  certifies whatever the case file happens to contain. A sort is a *finding*
  somebody made, so it comes in as a fact.
- **A sort is a RESTRICTION, so its fixture must expect a REFUSAL.** Deleting a
  sort goal makes strictly *more* provable, so every fixture expecting an answer
  goes on answering and a deletion battery reports the goal untested. See the
  mutation-battery rule below; this is the single most common way a sort ships
  with a test that cannot fail.
- **Place the sort goal BEHIND what binds its variable.** It is a one-argument
  positive guard, which is exactly the shape the dual program multiplies.
  Measured: `person(P)` written ahead of the goal binding `P` took a canonical
  denial from 372 to **590** rendered lines and broke a size gate on two
  fixtures; moved behind, **404** — the same as having no sort at all.

## Irreflexivity — `rel(X, X)` satisfies an existential guard truthfully

Any binary relation meaning "two distinct things" — spouse, parent, intermediate
company, predecessor — needs to say so. Without it `rel(X, X)` is a perfectly
good proof that supplies no relationship, and it defeats existential guards in
particular:

```prolog
% !load scasp
relative(pekka, pekka).                      % the whole defect, in one fact
has_relative(P) :- relative(P, _).           % "does this person have any relative?"
```

One fact, `relative(pekka, pekka)`, makes that true for a person with no family.
The guard is not weakened — it is *satisfied*, truthfully, by a self-relation.

```prolog
% !load scasp
#pred distinct_persons(A, B) :: '@(A) ja @(B) ovat eri henkilöitä'.
distinct_persons(A, B) :- A \= B.

spouse(A, B) :- spouse_fact(A, B).
spouse(A, B) :- spouse_fact(B, A).           % symmetric — see below
family_member(W, S) :- spouse(W, S), distinct_persons(W, S).
```

**Wrap the disequality — do not write a bare `A \= B`.** Measured: a bare `\=`
renders **nothing at all** in the justification tree. Not English, not a
placeholder — the goal is simply absent, so a reader cannot tell the question was
ever asked. If the reason you put the guard in the rules rather than in the
calling code is *visibility* (it usually is), the naive spelling defeats the
decision while appearing to implement it.

**Guard symmetric relations at both ends.** `rel(A, B) :- rel_fact(B, A).` means
a repeated name is not merely redundant; it is the shape that satisfies the
guard through the mirror clause.

**A reflexive instance does not do the same thing in every relation.** Most
*create* a link, so the assertion is "no link is manufactured". One that appears
under `not` — a separation, an exclusion, a revocation — *blocks* a link, so the
assertion is the opposite: a self-instance must not destroy a genuine relation. A
test generated over the relation names alone passes vacuously on that one however
the rules behave.

## Guard in the rules AND at the boundary — refuse, never drop or rewrite

When a host program feeds facts to a rule set, a constraint has two possible
homes and needs both.

| where | what it buys | what it misses alone |
| --- | --- | --- |
| the rules | the question appears in the justification tree | the bad fact silently confers nothing — a value vanishes with no diagnostic |
| the boundary | the caller gets an error instead of a wrong answer | the tree never shows the constraint was considered |

Rules-only is the subtler failure. The goal fails, the route is discarded, the
total comes out lower, and nothing anywhere says a stated fact was ignored.

**Refuse. Do not drop, and above all do not rewrite.** Silently normalising a
caller's fact into the "right" spelling decides the case on facts nobody stated.
When two spellings mean different things, the refusal must *route*:

> `direct_share(x_oy, x_oy, 9)` states that x_oy holds shares in itself; a
> väliyhteisö is a different entity, so this route does not apply. Write
> `treasury_share(x_oy, 9)` instead.

That is "this fact has a home and this predicate is not it" — a weaker and more
defensible act than "this fact is false", and it leaves the caller somewhere to
go. A bare refusal with no destination sends them back to type the same thing.

**Keep the two copies genuinely independent.** The whole argument for duplicating
a constraint is that a guard checked only against a list written beside it can be
wrong *in agreement with its own test*. If the boundary list and the test's list
are the same object, the duplication buys nothing. Generate one from the
declaration and hand-write the other, so they can disagree.

## A stated fact overrides every clause of its predicate

If a caller may state `p/2` directly, then **no guard anywhere in `p/2`'s clauses
can reach that path**. This is obvious in retrospect and reliably missed, because
the guard is right there in the source and looks like it applies.

```prolog
% !load scasp
works_in_leadership(P, C) :- person(P), ceo(P, C).
works_in(P, C) :- works_in_leadership(P, C).   % the gate lives in here
```

A fixture asserting `works_in(pekka, ex_oy).` bypasses `works_in_leadership/2`
entirely, and with it every check that predicate performs.

Two consequences worth carrying:

- **A guard inside a predicate is only as reachable as the calls to it.** A
  mutation that deletes the *call* bypasses the gate without touching the gate,
  so the entry that covers the call is also the entry that covers the guard.
- **Decide deliberately whether test fixtures may override a derived
  predicate.** It is convenient and it removes the rules from the path being
  tested. If they may, say where and why; a fixture that quietly states a derived
  predicate is a test of nothing.

## The dual program — the thing that actually bites

To prove `not p`, s(CASP) does not fail-and-return. It compiles a **dual program**
that constructively refutes every clause of `p` for every binding. Two consequences
dominate practical work.

**Unbound variables in a negated context multiply the proof.** Each free variable
position becomes its own "forall" branch in the dual — verified: a negated
three-argument call with two anonymous variables renders as three branches, one
per argument position.

**Put a goal BEHIND what binds it, regardless of polarity.** The rule is usually
stated for negated goals and that is too narrow — dual branching does not care
which side of a `not` you are on, and the *positive* case is the more expensive
one because nobody is watching for it. Both halves measured on the same rule set:

| move | model count | rendered lines |
| --- | --- | --- |
| reorder a *negation* relative to its binding goal | unchanged (0 with the fact, 1 without, either way) | 171 → 179 |
| a *positive* one-argument guard ahead of its binding goal | unchanged | 372 → **590** |
| the same guard moved behind | unchanged | **404** |

Note what does *not* move in any row: the verdict. This is a **size** discipline,
not a soundness one, and saying otherwise points the next reader away from the
fix — 590 down to 404 is the whole of it, and no test that reads answers can see
it. Gate on justification size or you will not notice.

There is a second, *separate* bug that tends to travel with it, and the two are
easy to conflate. Re-deriving from the database a value the caller already knows
is unsound in plain Prolog too — no dual program is involved, because the faulty
unification happens on the **positive** proof path:

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

processing(acme, health, insurance_scoring).   % the one under query
processing(acme, health, medical_treatment).   % any second, benign activity
high_risk(insurance_scoring).
claimed(consent).

% BAD: P is unbound, so it matches any processing/3 fact in the database,
% not the one under query. A second, unrelated fact silently defeats the guard.
exception(consent) :-
    claimed(consent),
    processing(_, _, P),
    not high_risk(P).

holds(G) :- findall(t, scasp(G, [tree(_)]), [_|_]).

main :-
    % An exception is "established" although the only activity under discussion
    % is high risk. Delete the second fact and this starts failing.
    holds(exception(consent)).
```

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

processing(acme, health, insurance_scoring).
processing(acme, health, medical_treatment).
high_risk(insurance_scoring).
claimed(consent).

% GOOD: the caller binds P. The dual collapses, and the guard cannot be
% satisfied by some other activity's data.
exception(consent, P) :-
    claimed(consent),
    not high_risk(P).

holds(G) :- findall(t, scasp(G, [tree(_)]), [_|_]).

main :-
    \+ holds(exception(consent, insurance_scoring)),   % refuses the right one...
    holds(exception(consent, medical_treatment)),      % ...and still permits the other
    % But note what binding P did NOT buy: the rule no longer mentions
    % processing/3 at all, so it succeeds for a purpose that is not in the fact
    % base. Guarding the activity is now the CALLER's job.
    holds(exception(consent, banana)).
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
% !load scasp
has_basis :- basis(_).                       % existential inside a POSITIVE goal
decision(X) :- thing(X), not has_basis.      % now `not` negates "a basis exists"
```

This is a correctness fix, not a tuning one, and the failure is silent. Note the
counter-intuitive consequence: the *wrong* version renders the shorter proof
tree, so "the tree got smaller" is not evidence of an improvement here.

**Never negate over an enumeration.** This is the previous two traps combined,
and it is the one that survives review, because the rule *reads* correctly. Given
a list of items supplied from outside, the tempting shape is a single goal that
checks them all:

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

contrib(p, f1, 10).
contrib(p, f2, 20).   % the SECOND item is the point
valid(p, f1, 10).     % ...and f2's contribution is NOT valid

% BAD: F and S are bound on the positive path and FREE in the dual, which is
% the path `not unverified/1` enters. Over an open domain the dual always finds
% some F,S it can refute, so the gate passes.
unverified(P) :- contrib(P, F, S), not valid(P, F, S).
verified(P)   :- not unverified(P).

holds(G) :- findall(t, scasp(G, [tree(_)]), [_|_]).

main :-
    holds(unverified(p)),   % there IS an invalid item...
    holds(verified(p)).     % ...and the gate passes anyway. Both hold.
```

`unverified(p)` and `verified(p)` are **both satisfiable**: the program grants on
an item it simultaneously reports invalid. Note the shape — invisible with one
item, present at two.

The fix is not a better rule. It is to stop asking s(CASP) the question:

> **Whoever holds the list does the loop.** The host iterates and issues one
> **ground** query per item; the rules answer "is *this* item valid?" and never
> "are all items valid?".

```python
for c in items:                                    # ground, one query each, no dual
    if not scasp_holds(facts, f"valid({p}, {c.id}, {c.amount})"):
        return refusal(c)
```

s(CASP) cannot aggregate over an unbounded set anyway, so the enumeration was
always going to live outside. The mistake is letting the *check* stay behind when
only the *arithmetic* leaves.

**A benchmark cannot tell you a dual is wrong.** The design above was chosen over
an alternative on a measurement — 188 justification lines against 990 — and the
measurement was accurate. It asked *how expensive is this dual*, never *is this
dual sound*. **An unsound dual is cheap precisely because it is not doing the
work**, so a favourable number is weak evidence at best and misleading at worst.
Establish soundness by execution on a two-instance fact base first; measure after.

Full treatment, with the measurement and how to read a bloated proof tree as a
diagnostic: `references/performance.md`.

## Alternative clauses are disjunction, never summation

Several clauses for one predicate offer several ways to derive it. They do not
combine. That is obvious stated plainly and catches people constantly, because
the natural-language rule being encoded often says "add":

```prolog
% !load scasp
share(P, C, S) :- direct(P, C, S).                      % 8
share(P, C, S) :- via(P, I), stake(I, C, S).            % 7
```

A person holding 8 directly and 7 through an intermediate gets **two answers, 8
and 7 — never 15**. A downstream threshold then binds whichever single route it
reaches first, so `share(P, C, S), S #>= 15` simply fails, silently.

That is correct semantics for *"does some qualifying route exist?"* and wrong
semantics for *"what is the total?"*. If the rule you are encoding sums over a
set whose size is not known until the facts arrive, the sum belongs to the host
under the boundary above: the rules validate each route one at a time, the host
adds the validated ones and feeds the total back as an input.

Mark such an input as host-computed in its `#pred` gloss. A justification ending
in a bare total tells the reader a number and hides where it came from; naming
the parts is what lets a human re-add it, which is the only check available.

## Quick Reference

### Loading and querying

```prolog
% !load
:- use_module(library(scasp)).
:- use_module(library(scasp/human)).   % human-readable justifications
```

```prolog
% !load scasp
?- scasp(flies(X), [tree(T)]).          % solve, capture the justification
?- ? flies(X).                          % REPL shorthand (also ??, ?--, ?+-, ?-+, ?++)
```

`scasp_justification/2` is `(-Tree, +Options)` and reads the **current answer's**
global — it is not `(Goal, Tree)`. It is for `begin_scasp` mode, where the goal
is an ordinary call with nowhere to hang an options list:

```prolog
% !load
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
% !load scasp
flies(X) :- bird(X), not ab(X).      % default: no reason to think X abnormal
-flies(X) :- penguin(X).             % classical: we know X does not fly
ab(X) :- penguin(X).
```

### Declaring 0-ary input flags

Facts asserted only when true should still be declared, so the loader does not
warn about a predicate that legitimately has no clauses:

```prolog
% !load
:- dynamic consent_withdrawn/0, legal_mandate/0.
```

Without the declaration you get ``Warning: scasp_predicate `'user:consent_withdrawn'/0'
does not exist`` — note the backtick-quote form — a warning, not an error. The
query still succeeds and absence is
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
plain consult. There is an NMR check in this mode; it just contains only the
consistency constraints the compiler derived, not the ones you wrote.

Be equally precise about its reach, because it is narrower than it first looks.
The check is scoped to the predicate that is inconsistent, not to the program.
Executed:

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

p(1).
p(2).
-p(1).        % p/1 is now inconsistent
q(7).
r :- q(7).

answers(G, N) :- findall(t, scasp(G, [tree(_)]), L), length(L, N).

main :-
    answers(p(1), 0),      % the inconsistent atom: no answer
    answers(p(2), 0),      % ...and every other p/1 atom goes with it
    answers(q(7), 1),      % an unrelated predicate still answers
    answers(r,    1).      % ...as does a rule that calls one
```

So `-p(1)` costs you the whole of `p/1`, including the `p(2)` nobody disputed.
It does not cost you the rest of the program. When a query "mysteriously fails
for every input", check the predicate in the query for a `p`/`-p` overlap, and do
not assume a single inconsistency anywhere has silenced everything.

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
and no `begin_scasp` anywhere renders the block. Querying `-flies(tweety)` gives
13 lines against 4 with `justify_nmr(false)`. Quote the query alongside any such
count: the same program queried `flies(polly)` gives 16 against 6. To confirm
*your* constraint is live, read what the block contains, or test it directly the
way the block above does.

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
% !load scasp
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
% !load scasp
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
% !load scasp
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
% !load scasp
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

**Wrap every built-in comparison and disequality in an annotated predicate.** A
built-in carries no `#pred`, and what it does to the tree is worse than
unreadable — it differs by operator and neither behaviour is one you want:

| written | rendered |
| --- | --- |
| `S >= 15` | English inside your target language: `14 is less than 15`, with `&(nbsp)` entities |
| `A \= B` | **nothing at all** — the goal is simply absent |

The second is the dangerous one. A reader of the justification cannot tell the
question was ever asked, so a guard you put in the rules *specifically* to make
it visible reads exactly like a guard that is not there. Wrap them:

```prolog
#pred share_at_least(S, T)      :: '@(S) % on vähintään @(T) %'.
#pred distinct_persons(A, B)    :: '@(A) ja @(B) ovat eri henkilöitä'.

share_at_least(S, T)   :- S #>= T.
distinct_persons(A, B) :- A \= B.
```

Use CLP(FD) `#>=` rather than `>=` inside the wrapper — `is/2` and the standard
comparisons demand ground arguments and defeat goal-directed evaluation. See
"Constraints, not `is/2`".

Name the wrappers after the *kinds* they relate rather than sharing one
`distinct/2`, when the kinds differ. Two predicates for people and legal persons
say the two rules are about different things; one predicate used at both sites
asserts they are the same, which is the confusion sorts exist to prevent.

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
% !load
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

% Three outcomes, told apart. `\+ poisoned(G)` would NOT do: it is true both
% when the call raises and when it merely fails, so it cannot prove an error
% happened.
outcome(G, O) :-
    catch(( holds(G) -> O = ok ; O = failed ),
          error(determinism_error(_,_,_,_), _),
          O = poisoned).

main :-
    holds(flies(polly)), holds(flies(polly)),      % findall throughout: fine
    outcome(flies(polly), ok),
    ( scasp(flies(polly), [tree(_)]) -> true ; true ),   % one cut call...
    outcome(flies(polly), poisoned),               % ...and findall now ERRORS,
                                                   % which is not the same as failing
    scasp_reset,
    outcome(flies(polly), ok).                     % repaired
```

This block is the claim, executed: repeated `findall` calls are fine, a single
cut call makes the next one raise `determinism_error` even under `findall`, and
clearing the globals restores it. The three outcomes are distinguished on
purpose. A test that only asserts "the next call did not succeed" passes whether
the call errored or simply failed, and those are different bugs.

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
- **Keep a mutation battery, and assert *named* catchers rather than a count.** Break one goal, and record which fixtures go red. Two failure modes matter and only the second needs the names: `UNCAUGHT` (nothing reddened — the goal is untested) and `DRIFTED` (the catcher set changed — something was re-blessed into vacuity, or new coverage arrived). A battery asking only "did anything redden?" reports green while coverage silently drains from three fixtures to one.

  The reason it drains is worth internalising: **a mutation is observable only when the goal it breaks is the sole reason the fixture's verdict holds.** Move a predicate out of the rules and every clause depending on it acquires a *second, independent* reason to fail — so every mutation sharing a clause with it goes quiet at once, while the suite stays green. Refactoring is exactly when a battery earns its cost, and exactly when a passing suite is least informative.

- **A deleted RESTRICTION is invisible to a deletion battery unless a fixture expects a REFUSAL.** This is the rule that catches people, and it is structural rather than a matter of care. A battery mutates by deleting a goal; deleting a restriction — a sort, an irreflexivity guard, a threshold, a completeness premise — makes strictly *more* provable. So every fixture expecting an answer goes on answering, the battery reports the goal untested, and the natural response is to conclude the guard is dead code and delete it. The only fixture that can redden is one that expects **no answer**, and most suites have none.

  Corollary, and it cuts the other way: **if the boundary refuses the fact base that would exercise a guard, that guard is permanently uncoverable by the battery.** There is no legal input that reaches it. Omit the entry with a note saying why, rather than adding one that will report `UNCAUGHT` forever — an entry that is uncatchable by construction teaches the reader to discount the word, and the whole value of the battery is that `UNCAUGHT` means "untested". Cover it with a test that reaches the rules directly, going around the boundary.

- **Assert WHICH clause fired, not only that the goal holds.** When several clauses reach the same conclusion by different tests, a suite reading verdicts cannot see a case move between them — same answer, different reasoning, different premises for anyone to contest. Measured: lowering one clause's threshold so that a second clause also fires reclassified **nobody**, left every verdict unchanged, and moved seven model counts. The battery reported it as a model-count change; only a test asserting the satisfied clause's *premises* said which provision had decided the case.

  Assert on the premises, never on a label. An `Item` argument threaded through the head is the rule author's claim about which clause is which, so asserting on it tests that the label matches itself. Read the premises out of the model instead and the semantics do the work.

  And check that the battery actually *runs* that test. A battery that mutates the rules and then shells out to the solver never executes a host-language test suite, so the sharpest check you own can sit permanently out of reach of the mutations it was written for — measured, in exactly that configuration, for two days.

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
- **Don't leave a goal ahead of what binds it — in a negated context or a positive one.** See the dual-program section. It costs **size**, not correctness, and the qualifier "in a negated context" is too narrow: dual branching is polarity-independent. Measured both halves: reordering a *negation* gave identical model counts (0 with the fact, 1 without, either ordering) and 171 → 179 rendered lines, while a *positive* one-argument guard placed ahead of the goal binding its variable cost **372 → 590** lines and 404 when moved behind. The adjacent unsoundness is re-derivation, a separate bug on the positive path, and it is described where it belongs in the dual-program section.
- **Don't write `not p(_)`.** It means "some value fails `p`", which is true by default over an open domain. Wrap the existential in a 0-ary predicate and negate that.
- **Don't define both `p` and `-p` casually.** Any argument deriving both makes the program inconsistent. Use `-p :- not p.` only when you genuinely intend an explicit closed-world assumption. Note how far the blast radius reaches: deriving both signs for **one** individual takes the predicate's answers to zero for **every** individual, including ones the two clauses never mention. Measured — adding a second `-p/1` clause that overlapped `p/1` for one subject took an unrelated subject from 1 answer to 0. Prefer one clause with a completeness premise over a second route.
- **Don't reach for `--no_nmr` to quieten a run.** It disables the check that surfaces exactly the `p`/`-p` inconsistency above, so the flag hides the failure mode that is hardest to find by reading. It is also load-bearing in the other direction: an integrity constraint outside a `begin_scasp` block is already inert, and `--no_nmr` removes the remaining signal.
- **Don't start an atom `c_`, `d_` or `n_`.** s(CASP) reserves single-letter prefixes for its own compilation — `reserved_prefix/1`, `prolog/scasp/program.pl:147-149`: `c` classical negation, `n` dual rule, `d` dummy. Exactly three; every other letter and all 676 two-letter prefixes round-trip.

  This is **not** a display artifact. Stripping runs at COMPILE time (`strip_prefixes/2`, `pr_rules.pl:170-196`) into the `pr_rule/3` facts `solve.pl` actually solves, so the fact is unreachable by the name you wrote:

      thing(c_oy).
      ?- thing(c_oy).      % NO answer
      ?- thing('-oy').     % ANSWER  <- the stored form
      ?- thing(not(oy)).   % ANSWER, for thing(n_oy)

  `n_` is the dangerous one: it becomes a negated LITERAL, so it changes the logical reading, not the spelling. Undocumented — nothing in the pack README or upstream docs mentions it. Validate identifiers against `^[cdn]_` where they are minted, and **reject rather than rename**: a host that silently rewrites its inputs names entities that do not exist.

  **Why an argument atom is hit at all.** Tagging is applied only to the head FUNCTOR (`handle_prefixes/2`, `input.pl:326-339`), but stripping recurses into EVERY argument (`format_predicate3/4`, `pr_rules.pl`). A bare atom carries no marker distinguishing a 0-ary predicate symbol from a data atom, so the compiler cannot tell them apart on the way out. The corruption therefore happens purely on the read-back side, to atoms that were never tagged.

  **Reserved generated NAMES, which no prefix rule catches.** From source: `_false_0` (headless integrity-constraint rules), `o_nmr_check` (the negative-loop check), and the `o_chk<N>` family (global constraints). Innermost duals are generated as `<Name>_vh<Arity>` (`comp_duals.pl:161-164`) — a SUFFIX, so a predicate you name `check_vh2/2` can collide and no prefix guard will see it. Note `o_` is used pervasively for generated names yet is NOT in `reserved_prefix/1`, so user `o_` atoms are unguarded on input while the compiler emits names that could collide exactly.
- **Don't expect `:- dynamic foo/1.` to silence "predicate does not exist" loader warnings.** Under the `scasp` CLI it is parsed as a predicate *reference*, so the original warning stays and `` `(dynamic)/1' does not exist `` is added on top. Verified 2026-08-02.
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

There are two tiers and five markers, and the tiers are reported as two numbers
that are never added together:

| Marker | Tier | Establishes |
| --- | --- | --- |
| `% !verify` | executed | the program runs and its assertions hold |
| `% !verify-fails` | executed | the program does **not** succeed |
| `% !load` | load-checked | it consults with no diagnostic on stderr |
| `% !load-fails` | load-checked | it consults **with** the diagnostic named by a following `% !expect` line |
| none | neither | listed in the run's output, so the residue stays visible |

A load check proves the source parses. It proves nothing about whether the block
is true — every one of the twelve errors two review rounds found was in a block
that parses, and one was a malformed `#pred` that loads with no diagnostic at
all. Reach for `% !verify` unless the block genuinely cannot run, and add a
marker to any example you expect to keep working.

## Attribution

Patterns adapted from the [SWI-Prolog port of s(CASP)](https://github.com/JanWielemaker/sCASP)
by Jan Wielemaker, which ports the original
[s(CASP)](https://gitlab.software.imdea.org/ciao-lang/sCASP) by Joaquín Arias and
the IMDEA / UTD team. Theory: Arias, Carro, Salazar, Marple, Gupta, "Constraint
Answer Set Programming without Grounding" (TPLP 2018).

The dual-program guidance, the `justify_nmr(false)` option, and the reason-term
pattern were derived from debugging a production GDPR rule set, not from the
upstream documentation.


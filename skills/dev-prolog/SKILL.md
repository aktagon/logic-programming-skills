---
# DO NOT EDIT — compiled output. Edit the source seed and regenerate; edits made here are overwritten on the next build.
name: dev-prolog
description: Use when writing, reviewing, refactoring, or designing Prolog code — including facts, rules, queries, recursion, lists, DCGs, constraint logic programming (CLP(FD)), tabling, modules, exceptions, and PlUnit testing in SWI-Prolog or GNU Prolog projects. Covers idiomatic clause design, unification, backtracking, steadfastness, mode and termination reasoning, the four-port debugger, and the purity discipline that keeps a predicate usable in every mode. Fires on Prolog topics even when the user does not say "Prolog" explicitly — e.g. `.pl` / `.pro` files, expert-system rules, ":- " clause syntax, "predicate", "unification", "backtracking", "logic programming", "definite clause grammar", "rule-based reasoning over a knowledge base", or any task whose source of truth is a set of declarative Horn clauses.
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
  - constraints
  - logic-programming
  - prolog
  triggers: prolog, swi-prolog, gnu-prolog, logic programming, horn clause, unification, backtracking, predicate, expert system, rule-based reasoning, dcg, definite clause grammar, clpfd, constraint logic programming, tabling, plunit, steadfast, .pl file
  scope: implementation
  output-format: code
  related-skills: dev-racket, dev-scasp, dev-tla-plus, developer, ontologist
  known_issues:
  - Verified against SWI-Prolog 9.2.9. CLP(FD) is library(clpfd) in SWI; GNU Prolog and SICStus expose similar operators through different modules, so treat any module path here as SWI-specific.
  - 'library(clpfd) reuses #=/2 as a declarative relation. Mixing it with is/2 in the same predicate loses the multi-mode behaviour that motivates using it at all.'
---

# Prolog Development

Write clear, declarative Prolog. Facts describe what is true, rules describe how
truths combine, and the engine searches. Lean on that; do not fight it.

The recurring difference between working Prolog and *good* Prolog is whether a
predicate describes a **relation** or computes a **function**. A relation works in
every mode — you can ask it forwards, backwards, or with everything unbound, and
it either answers or terminates. A function-in-disguise works in exactly the mode
its author happened to test.

## Routing

| You are working on… | Read |
| --- | --- |
| modes, steadfastness, termination, `dif/2`, CLP(FD) vs `is/2` | `references/purity-and-modes.md` |
| clause idiom, the four-port model, cut discipline, difference lists, common traps | `references/idioms.md` |
| external articles, talks, worked examples | `references/reading.md` |
| default reasoning, defeasible rules, justifications, ASP | the `dev-scasp` skill |

## Principles

1. **Describe relations, not procedures.** If you are sequencing steps, you have written a procedural program in Prolog syntax.
2. **Argument order is a contract.** Roughly half the meaning of a fact is convention. `parent(Parent, Child)` and `parent(Child, Parent)` are different predicates with the same name — decide, document, never mix.
3. **Prefer pattern matching to conditionals.** Several clauses with distinct head patterns beat one clause with guards.
4. **Prefer the pure builtin to a hand-rolled recursion.** `length/2`, `append/3`, `member/2`, `between/3`, `msort/2` are already steadfast and already terminate in modes your version probably will not.
5. **Cut (`!`) is a smell.** Use it for genuine determinism, never to paper over clause order or a missing case.
6. **A predicate should read aloud.** `student(X) :- owns(X, B), book(B).` reads "X is a student if X owns something that is a book."

## The single most useful habit

Reach for the constraint form of arithmetic. `is/2` evaluates, so it demands a
fully bound right-hand side; `#=/2` states a *relation* and works in every
direction.

```prolog
% !verify
:- use_module(library(clpfd)).

plus_(A, B, S) :- S #= A + B.

main :-
    plus_(2, 3, S), S == 5,            % forwards
    plus_(2, B, 5), B == 3,            % backwards — is/2 would throw here
    findall(X-Y, (X in 0..4, Y in 0..4, plus_(X, Y, 4), label([X,Y])), L),
    length(L, 5).                      % every decomposition of 4

% Note the fresh X-Y in the findall. Reusing B there would silently scope the
% search to B == 3 and yield one solution, not five — variable capture is the
% most common way a correct-looking Prolog example is quietly wrong.
```

Written with `is/2`, the same predicate throws an instantiation error on the
second line. That is the whole argument for CLP(FD) in one example.

## Quick Reference

### Facts, rules, queries

```prolog
owns(bob, book1).
book(book1).

student(X) :- owns(X, B), book(B).     % ":-" reads "if"; variables are Uppercase

ancestor(X, Y) :- parent(X, Y).        % multiple clauses = disjunction
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
```

```prolog
?- student(bob).      % succeed / fail
?- student(X).        % enumerate; `;` for the next solution
?- owns(_, book1).    % existence check
```

### Lists — use the builtins

```prolog
% !verify
main :-
    length(L, 3), L = [a,b,c],         % length/2 also GENERATES
    append([a,b], [c], [a,b,c]),       % works in all modes
    msort([c,a,b], [a,b,c]),           % sorts, keeps duplicates
    sort(0, @>=, [1,3,2], [3,2,1]),    % key + order; @< / @> dedupe, @=< / @>= keep
    numlist(1, 4, [1,2,3,4]),
    sum_list([1,2,3,4], 10),
    last([a,b,c], c),
    nth0(1, [a,b,c], b),
    exclude([X]>>(X == b), [a,b,c], [a,c]).
```

Do **not** hand-roll `length/2`. In SWI you cannot even try — it is a static
builtin, and the textbook definition refuses to load:

```
ERROR: No permission to modify static procedure `length/2'
```

Written under another name, the textbook version shows why:

```prolog
% !verify
len([], 0).
len([_|T], N) :- len(T, N1), N is N1 + 1.

main :-
    len([a,b,c], 3),                          % (+,-) is fine
    findall(L, length(L, 3), [[_,_,_]]),      % builtin (-,+): exactly one answer, det
    once(len(M, 3)), M = [_,_,_].             % len (-,+): first answer only...
% ...because asking for more diverges. Never findall over len(M, 3) — the
% builtin terminates there and the hand-rolled version does not.
```

The failing mode is `(-,+)`: `len(L, 3)` produces one solution and then diverges,
where `length(L, 3)` succeeds deterministically. (With *both* arguments unbound
neither terminates under `fail`-driven backtracking — that mode enumerates an
infinite family of lists, which is correct behaviour, not a bug.) Hand-rolling a
builtin is the canonical way to acquire a mode restriction the library does not
have.

### Collecting solutions: `findall` vs `bagof`/`setof`

`findall/3` always succeeds, returning `[]` when there is nothing. `bagof/3` and
`setof/3` **fail** on no solutions, and — the real surprise — they *backtrack once
per binding of any free variable in the goal*:

```prolog
% !verify
class(peter, a). class(pat, a). class(ann, b). class(tom, b).

main :-
    findall(N, class(N, _), All), All == [peter,pat,ann,tom],
    % C is free, so bagof yields one solution PER class:
    findall(C-Ns, bagof(N, class(N, C), Ns), Grouped),
    Grouped == [a-[peter,pat], b-[ann,tom]],
    % ^ existentially quantifies C away, collapsing them:
    bagof(N, C^class(N, C), Flat), Flat == [peter,pat,ann,tom],
    % setof/3 sorts and deduplicates:
    setof(C, N^class(N, C), Cs), Cs == [a,b].
```

That grouping behaviour is a feature — it is the idiomatic group-by — but it is
the most common way a `findall` gets "optimised" into a query that silently
returns one group at a time.

### Aggregating, and sorting by key

`library(aggregate)` replaces the `findall/3`-then-fold pass you would otherwise
write by hand. `library(pairs)` plus `keysort/2` is the sort-by-key idiom.

```prolog
% !verify
:- use_module(library(aggregate)).
:- use_module(library(pairs)).

score(alice, math, 90).
score(alice, art,  70).
score(bob,   math, 60).

:- dynamic absent/1.

main :-
    aggregate_all(count,    score(_,_,_),     3),
    aggregate_all(sum(S),   score(alice,_,S), 160),
    aggregate_all(max(S),   score(_,_,S),     90),
    aggregate_all(max(S,P), score(P,_,S),     max(90, alice)),   % value + witness
    aggregate_all(bag(P),   score(P,_,_),     [alice,alice,bob]),
    aggregate_all(set(P),   score(P,_,_),     [alice,bob]),
    % count/sum/bag/set are total; max/min FAIL on an empty goal.
    aggregate_all(count,  absent(_), 0),
    aggregate_all(sum(X), absent(X), 0),
    \+ aggregate_all(max(Y), absent(Y), _),
    % Sort by key: pair up, keysort, take the columns back.
    findall(Sc-P, score(P,_,Sc), Pairs),
    keysort(Pairs, Sorted),
    pairs_keys_values(Sorted, [60,70,90], [bob,alice,alice]),
    % keysort/2 compares the KEY and is stable; msort/2 compares whole terms.
    keysort([b-2,a-1,b-1], [a-1,b-2,b-1]),
    msort(  [b-2,a-1,b-1], [a-1,b-1,b-2]),
    sort(1, @=<, [b-2,a-1,b-1], [a-1,b-2,b-1]).
```

Three things worth carrying:

- **`max`/`min` fail on an empty goal** while `count`/`sum`/`bag`/`set` return `0`, `0`, `[]`, `[]`. A pipeline that treats "no rows" as zero silently loses a branch when someone switches `sum` to `max`.
- **`max(Expr, Witness)`** returns `max(Value, Witness)` — the argmax, without a second query to find which row won.
- **`keysort/2` is not `msort/2`.** `msort/2` compares whole terms, so it orders by the value once the keys tie. `sort/4` generalises `keysort/2` to any argument and any order: `sort(1, @=<, …)` matches `keysort/2` on pair lists, and `sort(1, @<, …)` is the same sort with duplicate keys dropped. They are not interchangeable in one respect — `keysort/2` type-checks, throwing `type_error(pair, f(1))` on a non-pair, where `sort(1, @=<, …)` sorts any compound by its first argument and silently accepts it.

`aggregate_all/3` is the `findall`-shaped one: it always succeeds (except for
`max`/`min`) and ignores free variables. `aggregate/3` exists too and behaves
like `bagof/3` — it backtracks once per binding of any free variable. The
grouping trap above applies to it unchanged.

### Strings, atoms, codes, chars

SWI's `double_quotes` flag defaults to `string`, so `"abc"` is none of the things
a textbook says it is:

```prolog
% !verify
main :-
    \+ "abc" == abc,                       % a string is NOT an atom
    \+ is_list("abc"),                     % ...and NOT a code list
    string(  "abc"),
    atom_string(A, "abc"), A == abc,
    atom_codes(abc, Cs), Cs == [0'a,0'b,0'c],
    atom_chars(abc, Ch), Ch == [a,b,c],
    string_concat("ab", "c", S), S == "abc".
```

Backquotes are the code-list literal (`back_quotes` defaults to `codes`), which
is why the DCG example below uses `` `4711` `` rather than `"4711"`. The two
flags are **independent**: under `:- set_prolog_flag(double_quotes, codes).` —
common in portable code — `"4711"` starts working *as well*, and the backquote
form keeps working unchanged. Only `double_quotes` varies between projects in
practice, so backquotes are the portable choice for a code list. Check the flag
before copying string code between projects.

### Arithmetic: four operators, four meanings

```prolog
% !verify
main :-
    X is 2 + 3,   X == 5,          % is/2 EVALUATES (needs RHS bound)
    Y = 2 + 3,    Y == 2+3,        % =/2 UNIFIES — Y is a term, not 5
    2 + 3 =:= 5,                   % =:=/2 compares VALUES
    \+ (2 + 3 == 5),               % ==/2 compares TERMS: 2+3 is not 5
    5 >= 5, 4 =< 5.                % note =<, never <=
```

### Negation and disequality

```prolog
% !verify
:- use_module(library(clpfd)).

main :-
    \+ member(d, [a,b,c]),             % negation as failure: needs a bound goal
    dif(X, a), X = b,                  % dif/2 is a CONSTRAINT: order-independent
    \+ (Y = a, dif(Y, a)),             % ...so this correctly fails
    findall(Z, (Z in 1..3, Z #\= 2, indomain(Z)), [1,3]).
```

`\+ Goal` succeeds when `Goal` fails *right now*. Call it before the relevant
variables are bound and you get a wrong answer silently. `dif/2` postpones instead,
and is almost always what you meant.

### DCGs — parsing, and describing lists generally

```prolog
% !verify
digits([D|T]) --> digit(D), digits(T).
digits([D])   --> digit(D).
digit(D)      --> [D], { code_type(D, digit) }.

main :-
    phrase(digits(Ds), `4711`),
    number_codes(N, Ds), N =:= 4711.
```

`phrase/2,3` connects a DCG body to a list. "Threading state" is not a metaphor:
`-->` is a source-to-source translation that gives every non-terminal two extra
arguments — the list *before* it (`S0`) and the list *after* it (`S`) — and
chains them. Write the translation out and the two versions are the same program:

```prolog
% !verify
abc --> [a], bs, [c].
bs  --> [].
bs  --> [b], bs.

% The same relation, spelled out with the two extra arguments made visible.
abc_(S0, S) :- S0 = [a|S1], bs_(S1, S2), S2 = [c|S].
bs_(S, S).
bs_(S0, S)  :- S0 = [b|S1], bs_(S1, S).

main :-
    findall(R, phrase(abc, [a,b,b,c,z], R), [[z]]),   % phrase/3 exposes S
    findall(R, abc_([a,b,b,c,z], R), [[z]]),          % ...which is just arg 2
    phrase(abc, [a,c]),                               % phrase/2 is phrase/3 with S == []
    findall(L, (length(L, 4), phrase(abc, L)), [[a,b,b,c]]).   % and it generates
```

`phrase/3`'s third argument is that `S` — the unconsumed remainder. Reach for it
whenever a grammar is one stage of a pipeline rather than the whole parse.

The hand-written version above is the same *relation*, not byte-for-byte what the
compiler emits. Ask it yourself with `listing/1`, which is the reliable way to
see what a DCG became:

```
abc([a|A], B) :- bs(A, C), C=[c|B].
bs(A, B) :- A=B.
bs([b|A], B) :- bs(A, B).
```

SWI folds a *leading* terminal into the head argument rather than emitting a body
unification. The two extra arguments and their chaining — the part worth
understanding — are identical either way.

The `S0`/`S` pair is a **difference list**, which is why DCGs cost nothing to
concatenate and why they describe lists as well as parse them. Full treatment,
including the O(1)-append idiom the translation is built on:
`references/idioms.md`.

### Exceptions and type checking

```prolog
% !verify
:- use_module(library(error)).
:- use_module(library(clpfd)).

half(N, H) :- must_be(integer, N), H #= N // 2.

main :-
    half(8, 4),
    catch(half(a, _), error(type_error(integer, a), _), true).
```

`must_be/2` from `library(error)` raises the ISO-standard error term. Prefer it to
hand-written guards so callers can catch a documented shape.

### `meta_predicate/1` — required for anything that takes a goal

A goal passed as an argument is a bare term. `call/1` runs it in **the module
that made the call to `call/1`** — the callee's module, not the caller's. Any
helper that wraps `findall/3`, `forall/2`, `call/N` or a custom control construct
therefore needs a `meta_predicate/1` declaration, or it works in one file and
breaks the moment it is moved into a library.

```prolog
% !verify
% A goal-taking helper lives in module `lib`; the caller lives in module
% `client`. `Module:(Head :- Body)` compiles the BODY in Module too, which is
% what lets one file stand in for two.

lib:count_of(Goal, Tmpl, N) :- findall(Tmpl, Goal, L), length(L, N).

:- meta_predicate lib:count_ok(0, ?, -).      % 0 = "argument 1 is a goal"
lib:count_ok(Goal, Tmpl, N) :- findall(Tmpl, Goal, L), length(L, N).

:- lib:export(count_of/3), lib:export(count_ok/3).
:- client:import(lib:count_of/3), client:import(lib:count_ok/3).

client:small(1).
client:small(2).
client:(undeclared(N) :- count_of(small(X), X, N)).
client:(declared(N)   :- count_ok(small(X), X, N)).

main :-
    % Undeclared: the goal arrives unqualified and is called inside `lib`.
    catch(client:undeclared(_), error(existence_error(procedure, small/1), _), true),
    % Declared: the goal is qualified with the caller's module, so `lib` runs
    % client:small/1.
    client:declared(N), N == 2,
    % ...and NOT by rewriting the caller. The stored clause is untouched:
    clause(client:declared(_), Body),
    Body = count_ok(small(_), _, _).
```

That last check matters, because the obvious mental model is wrong. The
declaration does **not** rewrite the caller's clause at compile time — the stored
body is still the unqualified `count_ok(small(X), X, N)`. The wrapping happens at
call time, from the caller's context module. Two consequences:

- The declaration does **not** have to precede its callers. Verified: moving it below both callers still fixes the call.
- Adding it later changes the behaviour of already-compiled code, silently and retroactively. Nothing recompiles and nothing warns.

The argument specifiers:

| Spec | Meaning |
| --- | --- |
| `0` | a goal, called as-is |
| `1`…`9` | a closure — that many arguments will be appended before calling |
| `:` | a term that needs module qualification but is not called |
| `?`, `+`, `-` | ordinary argument; no qualification |

A helper that hands its argument to `maplist/2` should declare `1`, not `0`,
because `maplist/2` appends one argument. Verified: for *qualification purposes*
`0` and `1`…`9` behave identically, so declaring the wrong number raises nothing
and changes nothing at run time. The number is documentation — for readers and
for the cross-referencer — which is exactly why nothing will tell you it is
wrong. What matters for correctness is only that a spec is present at all.

Note the trap the example dodges: calling `lib:count_of(small(X), …)` with an
explicit `lib:` prefix would qualify the meta-argument with `lib` and mask the
bug. Import the helper — or the test proves nothing.

### Testing with PlUnit

```prolog
:- begin_tests(lists).

test(append_backwards, [true(X == [a])]) :-
    append(X, [b], [a,b]).

test(no_member, [fail]) :-
    member(z, [a,b]).

:- end_tests(lists).
% ?- run_tests.
```

### Running SWI-Prolog

```bash
swipl                              # REPL
swipl script.pl                    # load into REPL
swipl -q -g main -t halt script.pl # run main/0 then exit — the scripting form
```

```prolog
?- [file].                  % consult file.pl from cwd
?- listing(pred/2).         % show clauses
?- trace, Goal.             % four-port debugger
?- gtrace, Goal.            % graphical tracer
```

## Don't

- **Don't hand-roll builtins.** Your `length/2`, `append/3` or `reverse/2` will be less steadfast and terminate in fewer modes than the library version.
- **Don't use `is/2` where `#=/2` will do.** `is/2` forecloses every mode but one.
- **Don't call `\+` before the relevant variables are bound.** Use `dif/2`, or reorder so the goal is sufficiently instantiated.
- **Don't reach for `!` to fix clause order.** Fix the clause order. A file full of cuts is a file whose head patterns are wrong.
- **Don't confuse `=` (unification), `is` (evaluation), `=:=` (value comparison) and `==` (term identity).**
- **Don't drive computation with `assert`/`retract`.** A database mutated mid-search is not a logic program and cannot be reasoned about or replayed.
- **Don't ignore arity.** `owns/2` and `owns/3` are unrelated predicates; always write `name/arity` in prose and comments.
- **Don't export a goal-taking predicate without `meta_predicate/1`.** It works in the file that defines it. From another module it raises `existence_error` if the goal is absent there — or, worse, silently calls a *different* predicate of the same name that the callee's module can see. Nothing warns you either way.
- **Don't hand-fold what `aggregate_all/3` already does.** And when you switch a `sum` to a `max`, remember the empty case stopped returning `0` and started failing.
- **Don't use `write/1` for terms you intend to read back.** Use `write_canonical/1` (or `write_term/2` with `quoted(true), ignore_ops(true)`): `write/1` loses quoting, and `writeq/1` still emits user-defined operators, so `a===>b` is unreadable in any process without that `op/3` declaration. `writeq`/`~q` is for human-facing output, not round-tripping.

## Verification standard

Every fenced block marked `% !verify` in this skill is executed against a real
SWI-Prolog install:

```sh
uv run scripts/verify_snippets.py
```

Blocks without the marker are illustrative fragments. Add the marker to any
example you expect to keep working.

## Attribution

The four-port model and the "roughly half the meaning of a fact is convention"
framing were seeded from ["Prolog" by Andrew Grack](https://grack.com/writing/school/enel553/report/prolog.html)
(ENEL 553 report). The relational/steadfastness emphasis and the CLP(FD)-over-`is/2`
argument follow the mainstream SWI-Prolog teaching tradition.


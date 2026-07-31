# Purity, modes, steadfastness, termination

Four related properties that decide whether a predicate is a relation you can
trust or a function that happens to work.

## Modes

A **mode** describes instantiation at call time, per argument:

| Notation | Meaning |
| --- | --- |
| `+Arg` | bound (at least to a term with a functor) on entry |
| `-Arg` | unbound on entry; the predicate binds it |
| `?Arg` | either — the predicate works both ways |

Document modes on every exported predicate:

```prolog
%!  ancestor(?Ancestor, ?Descendant) is nondet.
%
%   True when Ancestor precedes Descendant in the parent/2 relation.
%   Terminates when at least one argument is bound.
```

The interesting mode is the one you did not test. Anything that only works `(+,-)`
is a function, and calling it any other way gives an instantiation error, a wrong
answer, or a hang. Sometimes that is acceptable — but decide it, document it, and
do not discover it in production.

## Steadfastness

A predicate is **steadfast** when pre-binding the output argument gives the same
answer as computing it and comparing afterwards. That is,

```prolog
p(In, Out), Out == Expected
```

must agree with

```prolog
p(In, Expected)
```

Unifying the output **in the head, before a cut**, is the usual way to break it:

```prolog
% !verify-fails
% NOT steadfast: the head unifies the 3rd argument with X, so a pre-bound
% output participates in clause selection. max(3, 2, 2) matches the SECOND
% clause and wrongly succeeds.
max_bad(X, Y, X) :- X >= Y, !.
max_bad(_, Y, Y).

main :- \+ max_bad(3, 2, 2).      % fails: max_bad(3,2,2) wrongly succeeds
```

```prolog
% !verify
% Steadfast: guards are mutually exclusive and decide on inputs alone, so
% no cut is needed and a pre-bound output is simply checked.
max_ok(X, Y, X) :- X >= Y.
max_ok(X, Y, Y) :- X < Y.

main :- max_ok(3, 2, 3), \+ max_ok(3, 2, 2).
```

Note what is *not* the problem. This version is steadfast, because the guard
`X >= Y` depends only on inputs and the cut fires after it, before any output
unification:

```prolog
% !verify
max_cut(X, Y, Max) :- X >= Y, !, Max = X.
max_cut(_, Y, Y).

main :- \+ max_cut(3, 2, 2), max_cut(3, 2, 3).
```

A cut is not automatically a steadfastness bug. The bug is output unification
that happens *before* the commitment, whether in the head or in the body. The
reliable fix is mutually exclusive guards on inputs, which removes the need for
the cut at all.

## Arithmetic and modes

`is/2` fixes the mode to `(-, +)`: the right side must be fully bound.

```prolog
% Only works one way.
celsius_f(C, F) :- F is C * 9 / 5 + 32.
% ?- celsius_f(C, 212).   ERROR: Arguments are not sufficiently instantiated
```

CLP(FD) states the relation instead, so every mode works and the predicate can
even enumerate:

```prolog
:- use_module(library(clpfd)).

celsius_f(C, F) :- F #= C * 9 // 5 + 32.
% ?- celsius_f(100, F).   F = 212.
% ?- celsius_f(C, 212).   C = 100.
```

Rules of thumb:

- Integers and you want a relation → `library(clpfd)` (`#=`, `#<`, `in`, `ins`, `label/1`).
- Floats, or a genuinely one-directional computation in a hot loop → `is/2`, with the mode documented.
- Never both in one predicate. Mixing them gives you `is/2`'s mode restrictions with CLP(FD)'s overhead.

`label/1` and `indomain/1` are where search happens. Posting constraints is cheap
and does not search; labelling does. Post all constraints first, label last.

## Disequality: `\=` vs `dif/2`

`\=` asks "are these non-unifiable *right now*". On an unbound variable the answer
is no — `X` and `a` unify — so the goal **fails immediately**, and you cannot
state the intent before the binding exists:

```prolog
% !verify
main :-
    \+ (X \= a, X = a),        % \=  fails at once: X and a ARE unifiable
    ( dif(Y, a), Y = b ),      % dif postpones, then permits b
    \+ ( dif(Z, a), Z = a ).   % ...and rejects a when it arrives
```

The contrast that matters is on a satisfiable intent. "These two must differ"
cannot be expressed with `\=` ahead of time:

```prolog
% !verify
main :-
    \+ (X \= Y, X = a, Y = b),      % \=  fails on the FIRST goal, though a \= b
    ( dif(P, Q), P = a, Q = b ).    % dif succeeds — the constraint survives
```

Both are order-sensitive in opposite directions: `\=` needs its arguments bound
*before* the call, `dif/2` does not care when they arrive. If a variable might be
bound after your check, you need `dif/2`.

## Negation and instantiation

`\+ Goal` is sound only when `Goal` is sufficiently instantiated at the moment it
runs. Under the closed-world assumption it means "not provable", not "false":

```prolog
% ?- \+ parent(X, bob), X = tom.
%    Wrong reading: "\+ parent(X,bob)" asks whether ANY X is a parent of bob.
```

Reorder so the goal is ground, or express the intent with a constraint. When you
truly need "we know this is false" as a first-class claim rather than "we cannot
prove it", you have outgrown Prolog's negation — that is what classical negation in
s(CASP) is for (`dev-scasp`).

## Termination

Two questions, always:

1. **Does it terminate for the modes I document?** Left recursion over a database
   relation does not:

   ```prolog
   % Loops on the second clause before consuming input.
   ancestor(X, Y) :- ancestor(X, Z), parent(Z, Y).
   ```

   Put the base case and the consuming goal first:

   ```prolog
   ancestor(X, Y) :- parent(X, Y).
   ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
   ```

2. **Does it terminate on a cyclic graph?** The version above does not, if
   `parent/2` has a cycle. `library(tabling)` fixes it by memoizing and detecting
   the loop:

   ```prolog
   :- table ancestor/2.
   ancestor(X, Y) :- parent(X, Y).
   ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
   ```

   Tabling turns a class of non-terminating transitive-closure programs into
   terminating ones and is the right default for graph reachability over data you
   do not control. It changes complexity, not semantics.

A useful discipline: for any recursive predicate, write down which argument
strictly decreases on each call. If you cannot name one, either add an accumulator
that does, or table it.

## Determinism and indexing

"Avoid cuts" is only actionable if you know what makes a predicate deterministic
without one. SWI indexes on the first argument, and JIT-indexes on others when a
call pattern demands it. Distinct constants in the first argument therefore give
you determinism for free:

```prolog
% !verify
colour(red,   "#f00").
colour(green, "#0f0").
colour(blue,  "#00f").

% Identical head patterns: indexing cannot separate these, so a choice point
% survives even though only one guard can ever hold.
classify(N, neg)  :- N <  0.
classify(N, zero) :- N =:= 0.
classify(N, pos)  :- N >  0.

deterministic_call(G) :- call_cleanup(G, Det = true), Det == true.

main :-
    deterministic_call(colour(green, _)),      % indexed on arg 1: det
    deterministic_call(colour(_, "#0f0")),     % SWI JIT-indexes arg 2 too: det
    \+ deterministic_call(classify(-5, _)),    % succeeds on clause 1: 2 left over
    deterministic_call(classify(5, _)).        % succeeds on the LAST clause: det
```

Three separate effects, easy to confuse:

- SWI will JIT-index a non-first argument when a call pattern demands it, so "indexing is first-argument only" is folklore.
- Indexing cannot separate clauses whose discriminating work happens in a *guard* rather than the head — that is `classify/2`.
- Succeeding on the **last** clause looks deterministic whatever the indexing, because there is nothing left to retry. `classify(5, _)` is det and `classify(-5, _)` is not, from the same predicate. Never infer determinism from one probe.

`call_cleanup/2` binding at the deterministic exit is the cheap way to *assert*
determinism in a test rather than assume it. The standard vocabulary for
documenting it:

| Determinism | Meaning |
| --- | --- |
| `det` | exactly one solution, no choice point |
| `semidet` | zero or one solution |
| `nondet` | any number, may leave choice points |
| `multi` | at least one, may leave choice points |
| `failure` | always fails |

Put it in the mode line — `%! colour(+Name, -Hex) is semidet.` — because it is a
contract, and a caller that assumes `semidet` will wrap your `nondet` predicate
in `once/1` and silently discard answers.

When a predicate leaves a choice point you did not intend, the fix in order of
preference is: reorder or specialise the head patterns so indexing applies; add a
guard that makes the clauses mutually exclusive; and only then consider `once/1`
at the call site. Reaching for a cut inside the predicate is last, because it
changes the predicate for every caller rather than the one that wanted commitment.

## Purity

A predicate is **pure** when it has no side effects and its meaning does not depend
on when it is called. Pure predicates can be reordered, retried, tabled, and
reasoned about.

The things that break purity, in rough order of how often they cause trouble:

- `assert/1`, `retract/1` used as mutable state during search
- `!` used for control rather than to mark genuine determinism
- `\+` over insufficiently instantiated goals
- I/O interleaved with computation instead of at the edges
- `nb_setval/2` and friends

The forced-output idiom (`Goal, write(X), nl, fail`) is impure by construction and
that is fine — it is an output loop, not a computation. Keep such loops at the
boundary and out of the predicates that carry your logic.

## A checklist for reviewing a predicate

- Documented mode, and does it hold for the modes claimed?
- Steadfast — does pre-binding the output still give the right answer?
- Guards mutually exclusive, or is a cut standing in for that?
- Arithmetic: `is/2` (one mode) or `#=/2` (all modes) — and consistently one of them?
- Disequality: `\=` where a later binding could violate the intent?
- Recursion: which argument decreases, or is it tabled?
- Side effects: any, and are they at the boundary?

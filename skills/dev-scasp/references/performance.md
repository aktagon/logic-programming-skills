# Performance and the dual program

Nearly every s(CASP) performance problem — and a surprising share of the
correctness problems — traces back to one mechanism. Understand the dual program
and both classes become predictable.

## What the dual program is

Prolog proves `\+ G` by trying `G` and failing. s(CASP) cannot do that: default
negation under stable-model semantics is a positive claim ("there is a model
without `G`"), so it must be *constructed*, not merely failed into.

s(CASP) therefore compiles, for every predicate `p`, a **dual** predicate that
succeeds exactly when `p` cannot be derived. The dual of a predicate with several
clauses must refute *all* of them. The dual of a clause with several body goals
must refute *at least one*. And the dual of a clause containing a free variable
must show refutation for *every* value that variable could take — a forall.

That last one is where the cost lives.

## Symptom: the proof tree is enormous

A three-argument call with two anonymous variables inside a negated context:

```prolog
exception(consent) :-
    claimed(consent),
    processing(_, _, P),
    not high_risk(P).
```

produces a dual that branches once per argument position. You pay for it only
when the predicate is reached through `not` (or through the NMR check) — the
positive proof stays small, which is why this hides until the deny path runs:

```prolog
% !verify
:- use_module(library(scasp)).
:- use_module(library(scasp/human)).
:- style_check(-singleton).

processing(acme, health, insurance_scoring).
high_risk(insurance_scoring).
claimed(consent).

exception_free(consent)     :- claimed(consent), processing(_, _, P), not high_risk(P).
exception_bound(consent, P) :- claimed(consent), not high_risk(P).

denied_free     :- not exception_free(consent).
denied_bound(P) :- not exception_bound(consent, P).

#pred processing(C,D,P) :: 'the activity is @(C) processing @(D) data for @(P)'.
#pred high_risk(P)      :: '@(P) is high risk'.
#pred claimed(B)        :: 'the controller claims @(B) as a legal basis'.

lines(S, N) :- split_string(S, "\n", "", L), length(L, N).

render(Goal, N, S) :-
    findall(T, scasp(Goal, [tree(T)]), [Tree|_]),
    with_output_to(string(S), human_justification_tree(Tree, [justify_nmr(false)])),
    lines(S, N).

main :-
    render(denied_free, NFree, Free),
    render(denied_bound(insurance_scoring), NBound, _),
    NFree >= 2 * NBound,                       % 13 lines vs 6, on three facts
    % one branch per argument position of the three-argument call:
    sub_string(Free, _,_,_, "any number not [acme] processing anything data"),
    sub_string(Free, _,_,_, "acme processing any number not [health] data"),
    sub_string(Free, _,_,_, "acme processing health data for any number not [insurance_scoring]").
```

Rendered, the free-variable version reads:

```
there is no evidence that the activity is any number not [acme] processing anything data for anything, and
   ... the whole preceding conjunction, repeated ...
there is no evidence that the activity is acme processing any number not [health] data for anything, and
   ... repeated again ...
there is no evidence that the activity is acme processing health data for any number not [insurance_scoring], and
```

Three branches, each re-proving the goals that came before it in the clause —
here just `claimed(consent)`, which is why it appears four times. Above, on a
three-fact program, that is 13 lines against 6. On a real rule set it took one
13-line justification to 47.

## Symptom: a rule is unsound as the fact base grows

The same call site causes a second, **independent** bug — and the two are easy to
conflate. This one is not a dual-program effect at all: the faulty unification
happens on the *positive* proof path, and plain Prolog behaves identically.

`processing(_, _, P)` does not mean "the activity under query" — it means "some
processing fact". With one fact asserted they coincide. With two they do not, and
the guard `not high_risk(P)` can be satisfied by an entirely unrelated record:

```prolog
processing(acme, health, insurance_scoring).   % the one being asked about
processing(acme, health, medical_treatment).   % any second, benign activity
```

`P` binds to `medical_treatment`, `not high_risk(medical_treatment)` succeeds, and
the guard that was supposed to block `insurance_scoring` never fires. Executed:

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

processing(acme, health, insurance_scoring).
processing(acme, health, medical_treatment).   % the second, benign activity
high_risk(insurance_scoring).
claimed(consent).

exception_bad(consent)   :- claimed(consent), processing(_, _, P), not high_risk(P).
exception_ok(consent, P) :- claimed(consent), not high_risk(P).

holds(G) :- findall(t, scasp(G, [tree(_)]), [_|_]).

main :-
    % The guard is defeated: an exception is "established" even though the only
    % activity under discussion is high risk.
    holds(exception_bad(consent)),
    % Bound at the call site, the same guard refuses the right one...
    \+ holds(exception_ok(consent, insurance_scoring)),
    % ...and still permits the other.
    holds(exception_ok(consent, medical_treatment)).
```

Delete the second `processing/3` fact and `exception_bad/1` starts failing —
which is exactly why this is invisible to any test whose fixture holds a single
instance. If a rule set reaches into the database for a value the caller already
knows, treat it as a bug regardless of whether a test currently catches it.

State the rule accurately: **do not re-derive from the database a value the caller
already has.** That is ordinary scoping discipline, not an ASP subtlety. The
dual-program cost above is a *separate* reason to bind variables before a negated
goal. They travel together because one sloppy call site causes both, but fixing
one does not imply the other is fine.

## Fix: bind at the call site

Pass the value down as an argument instead of re-deriving it:

```prolog
exception(consent, P) :-
    claimed(consent),
    not high_risk(P).

has_exception(P) :- exception(_, P).

authority(D, _P) :- not special(D).
authority(D, P)  :- special(D), has_exception(P).

decision(C, D, P) :- processing(C, D, P), has_basis, authority(D, P).
```

Now `P` arrives bound from the top-level query. The dual has nothing to
universally quantify over, the three branches collapse to one, and the rule can
only be satisfied by the activity actually under consideration.

Remember to update the `#pred` annotations for the new arities — an annotation
that no longer matches its predicate silently stops applying.

## Fix: scope existentials in a 0-ary wrapper

This one is filed under performance by habit. It is a **correctness** fix, and
the correctness failure is silent.

`not p(_)` does not mean "no `p` exists". The anonymous variable is existentially
quantified *inside* the negation, so it reads "there is some value for which `p`
is not derivable" — over an open domain, trivially true no matter what the fact
base contains. Wrapping the existential in a positive 0-ary predicate moves the
quantifier outside the `not`, which is what you meant:

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

thing(a).
claimed(consent).
basis(consent)  :- claimed(consent).
basis(contract) :- claimed(contract).

% WRONG: reads "there is SOME value for which basis is not derivable".
unscoped(X) :- thing(X), not basis(_).

% RIGHT: the existential lives inside a positive 0-ary predicate, so `not`
% negates "a basis exists".
has_basis :- basis(_).
scoped(X)  :- thing(X), not has_basis.

holds(G) :- findall(t, scasp(G, [tree(_)]), [_|_]).

main :-
    holds(unscoped(a)),     % succeeds although consent IS an established basis
    \+ holds(scoped(a)).    % correctly fails
```

The justification tells you which one you wrote. The unscoped version renders a
single line —

```
there is no evidence that basis holds for any number not [consent,contract]
```

— which is the constraint store saying out loud that it satisfied the goal by
choosing a value nobody asked about. The scoped version instead walks each clause
of `basis/1` and refutes it, and is longer for that reason. **A shorter tree is
not the better one here**; the short one is the wrong answer. Measured on a
twelve-clause `basis/1`: unscoped 5 lines and 3 ms, scoped 30 lines and 6 ms —
and the scoped one is the only one that is right.

Annotate the wrapper (`#pred has_basis :: 'a legal basis is established'`) and it
also reads better in the justification than the raw existential would.

## Fix: declare 0-ary input flags dynamic

Input flags asserted only when true should still be declared:

```prolog
:- dynamic consent_withdrawn/0, legal_mandate/0.
```

Without the declaration you get `Warning: scasp_predicate 'user:consent_withdrawn'/0
does not exist`. That is a **warning, not an error** — the query still succeeds and
absence is still treated as falsity, so this is hygiene rather than correctness.
The better argument for the declarations is that they document the rule file's
input interface.

The rule is narrow: declare genuine 0-ary *inputs*. Never declare a predicate
whose clauses the rule set enumerates itself — you would be telling the solver its
own rules might change underneath it.

Declaring every input predicate, including the multi-argument ones, has a second
benefit: the rule file then documents its own interface with the fact mapper, and
can be consulted standalone for testing instead of only in the presence of an
asserted fact base.

## Query ordering

Where a program asks both "does this hold?" and "is this explicitly false?", run
the positive query first:

```prolog
% NOTE: never put `->` directly around scasp/2 — a cut scasp/2 poisons every
% later query in the process. Collect with findall/3 and branch on the list.
solutions(G, S) :- findall(G-T, scasp(G, [tree(T)]), S).

decide(C, D, P, Verdict) :-
    solutions(may(C, D, P), Allow),
    (   Allow = [_|_]
    ->  Verdict = allow
    ;   solutions(denial(C, D, P, _), Deny),
        ( Deny = [denial(_,_,_,R)-_|_] -> Verdict = deny(R) ; Verdict = unknown )
    ).
```

The positive query short-circuits on the first proof. The negated query is where
the dual search actually happens, so running it only when no positive path exists
avoids the expensive case in the common one. In policy and legal domains this also
happens to match the burden of proof, which is a pleasant coincidence rather than
a reason.

## Measuring

There is no profiler; use wall clock and tree size. Both are proxies for the same
thing, and tree size is the more diagnostic of the two — a proof that is large
relative to the complexity of the question is telling you the dual is doing work
your rule set did not intend. Fix the shape of the rules, not the timeout.

A practical gate: assert on the *number of lines* in a rendered justification for
a canonical query in your test suite. It is a crude metric that catches
free-variable regressions immediately, and unlike a timing assertion it is stable
across machines. The `lines/2` + `render/3` pair in the first block above is the
whole implementation; point it at a query you care about and assert an upper
bound.

Render with `justify_nmr(false)` when you do this, or the gate measures the NMR
check — which grows with the *program*, not with the query — and every new
integrity constraint trips it.

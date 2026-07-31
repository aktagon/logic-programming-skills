# Justifications

The proof tree is the product. Everything here is about making it readable by a
human and consumable by a program — two different jobs that must not be confused.

## Rendering a tree

```prolog
:- use_module(library(scasp)).
:- use_module(library(scasp/human)).

explain(Goal) :-
    scasp(Goal, [tree(T)]),
    human_justification_tree(T, []).
```

`human_justification_tree/2` prints to `current_output`. The second argument is
an option list, and the default (`[]`) is almost never what you want in an
application.

## Suppressing the global-constraint block

When the program has live global constraints, the renderer appends the NMR
(non-monotonic reasoning) check to every tree. Its phrasing actively misleads:
inside a proof that a goal does **not** hold, it emits lines of the form

```
it may be the case that alice may borrow book1
```

A reader who is not an ASP practitioner reads that as the opposite of the
verdict. Turn it off with `justify_nmr(false)`.

The size is not marginal. Measured on the six-line proof below, the NMR block
takes it to twenty-four:

```prolog
% !verify
:- use_module(library(scasp)).
:- use_module(library(scasp/human)).
:- style_check(-singleton).

:- begin_scasp(lib, [may_borrow/2]).
member_of(alice, library).
member_of(bob, library).
book(book1).
book(book9).
restricted(book9).
overdue(bob).
may_borrow(P, B) :- member_of(P, library), book(B), not overdue(P).
:- may_borrow(P, B), restricted(B).      % nobody may borrow a restricted book
:- end_scasp.

% #pred goes OUTSIDE the block, or it is silently ignored — see below.
#pred may_borrow(P, B) :: '@(P) may borrow @(B)'.
#pred overdue(P)       :: '@(P) has an overdue loan'.

lines(S, N) :- split_string(S, "\n", "", L), length(L, N).

render(Goal, Opts, S) :-
    findall(T, (Goal, scasp_justification(T, [])), [Tree|_]),
    with_output_to(string(S), human_justification_tree(Tree, Opts)).

main :-
    render(may_borrow(alice, book1), [], Full),
    render(may_borrow(alice, book1), [justify_nmr(false)], Short),
    lines(Full, LF), lines(Short, LS),
    LF > LS + 10,                                              % 24 vs 6 here
    sub_string(Full,  _,_,_, "The global constraints hold"),
    \+ sub_string(Short, _,_,_, "The global constraints hold"),
    sub_string(Short, _,_,_, "alice may borrow book1"),        % #pred applied
    sub_string(Short, _,_,_, "no evidence that alice has an overdue loan").
```

Do **not** read the presence of `The global constraints hold` as proof that your
own integrity constraints compiled. The NMR check also carries the `p`/`-p`
consistency constraints, so a plain-consult program with no `begin_scasp` at all
renders the block as soon as it uses classical negation — measured at 13 lines
against 4 with `justify_nmr(false)`. The block tells you the NMR check ran, not
whose constraints are in it. Read its contents, or test the constraint directly.

Where there is genuinely no NMR content — a plain-consult program with no
classical negation — `justify_nmr(false)` changes nothing, because there is
nothing to suppress.

Keep the full tree available behind a flag for debugging the rule set — the NMR
block is genuinely useful when an integrity constraint is misbehaving. Expose it
as `--proof=full` rather than deleting the capability.

## Where `#pred` must live

`#pred` directives must be written **outside** `begin_scasp`/`end_scasp`.

Inside the block, the directive compiles `pr_pred_predicate/4` into the unit's
private module `_scasp_<Unit>`. The renderer resolves templates against the
module the tree's atoms strip to — the module you called from — and additionally
requires the predicate to be *defined* there rather than imported. It finds
nothing, silently falls back to the internal phrasing, and you get:

```
may_borrow holds for alice, and book1, because
   member_of holds for alice, and library, and
```

Move the same directives after `:- end_scasp.` and the identical program renders:

```
alice may borrow book1, because
   member_of holds for alice, and library, and
```

No error, no warning, and the fallback is grammatical enough to survive review.
This is the single easiest way to follow both of this skill's rules — "put
constraints inside `begin_scasp`" and "annotate everything a human will see" —
and end up with neither.

## Reading a bloated tree as a diagnostic

Proof-tree size is a *linter for your rule set*. Two patterns to recognize:

**Repeated sibling goals with `justified above`.** The same subgoal proved once
per branch of a dual. Almost always means a negated call has free variables.

```
there is no evidence that the activity is any number not [acme] processing anything data for anything, and
the controller claims consent as a legal basis, justified above, and
there is no evidence that the activity is acme processing any number not [health] data for anything, and
the controller claims consent as a legal basis, justified above, and
```

Three near-identical branches, one per argument position of a three-argument
predicate called with two anonymous variables. Bind the variables at the call
site and all three collapse. See `performance.md`.

**`any number not [a,b,c]`.** The renderer's phrasing for a constrained variable
`X` with `X ≠ a, X ≠ b, X ≠ c`. It says "number" regardless of the actual type,
which is upstream wording, not something you did wrong. It appears whenever the
dual has to reason about "some value other than these". If it dominates your
output, the underlying cause is usually the same free-variable problem.

## Annotating for a non-technical reader

```prolog
#pred processing(C, D, P) ::
    'the activity is @(C) processing @(D) data for @(P)'.
#pred -may_process(C, D, P) ::
    '@(C) may not process @(D) data for @(P)'.
```

Rules that pay off:

- **Annotate the classically-negated head.** `-p` is what a reader will ask about; leaving it unannotated means your denials render as internal goals.
- **Write the template as a clause of a sentence**, not a label. The renderer joins them with "because" and ", and" — a template that reads as a noun phrase produces broken English.
- **Do not encode the verdict in the template.** `'@(C) may process @(D)'` inside a rule that only fires on the deny path will read backwards when the dual negates it.
- **Keep templates stable.** They are a user-facing contract, and — see below — anything that scrapes them is coupled to their exact wording.

## Never scrape the rendered text

The single most tempting mistake: recovering *why* something was denied by
searching the rendered justification for a phrase.

```python
# BAD — couples you to your own #pred wording AND to the pack's
# negation phrasing ("there is no evidence that ..."), and degrades
# silently to a generic message when either changes.
if "no evidence that an exception is established" in justification:
    reason = "no_exception"
```

The rendered string is the concatenation of two things you do not jointly
control. Reword one `#pred` and the match falls through with no error — the tool
keeps producing verdicts and quietly stops explaining them.

Emit a **term** instead. Name the grounds in the rule set, then drive the
application off the term. Both halves, executed:

```prolog
% !verify
:- use_module(library(scasp)).
:- style_check(-singleton).

processing(acme, health, insurance_scoring).
processing(acme, health, medical_treatment).
special(health).
has_exception(medical_treatment).
has_basis.

may_process(C, D, P)  :- processing(C, D, P), has_basis, not special(D).
may_process(C, D, P)  :- processing(C, D, P), has_basis, special(D), has_exception(P).
-may_process(C, D, P) :- denial(C, D, P, _).

denial(C, D, P, no_exception) :- processing(C, D, P), special(D), not has_exception(P).
denial(C, D, P, no_basis)     :- processing(C, D, P), not has_basis.

#pred may_process(C,D,P) :: '@(C) may process @(D) data for @(P)'.
#pred denial(C,D,P,R)    :: '@(C) may not process @(D) data for @(P), because @(R)'.

% Every scasp/2 goes through findall/3. An `->` around scasp/2 would commit, and
% a cut scasp/2 poisons every later query in the process with
% determinism_error(scasp_solve:stack_parents/3, ...). See the skill's
% "Never cut a scasp/2 call" section.
solutions(Goal, S) :- findall(Goal-T, scasp(Goal, [tree(T)]), S).

decide(C, D, P, Verdict) :-
    solutions(may_process(C, D, P), Allow),
    (   Allow = [_|_]
    ->  Verdict = allow
    ;   solutions(denial(C, D, P, _), Deny),
        (   Deny = [denial(_,_,_,R)-_|_]
        ->  Verdict = deny(R)
        ;   Verdict = unknown
        )
    ).

main :-
    decide(acme, health, medical_treatment, allow),
    decide(acme, health, insurance_scoring, deny(no_exception)),
    decide(acme, health, staff_directory,   unknown),   % not a known activity
    findall(R, scasp(denial(acme,health,insurance_scoring,R), [tree(_)]),
            [no_exception]).
```

The `->`s here test ordinary lists, not solver goals, so they commit nothing
inside s(CASP).

## Driving an application from a verdict

The shape of the driver in the block above:

1. Query the positive goal first. It short-circuits as soon as one path proves, and it matches the burden of proof in most legal and policy domains ("the actor must establish permission").
2. Only if that fails, query the classically-negated goal. The dual search is expensive; run it when it is actually warranted.
3. Capture the reason term from step 2, not the prose.
4. Keep the rendered tree as an artifact attached to the decision — for the human — and never branch on it.

Querying `denial(C, D, P, Reason)` with `Reason` unbound enumerates the grounds,
so an unrecognized value can fail loudly instead of silently. The mapping lives
in one place and survives pack upgrades and template rewording.

Note the ordering subtlety: when an input breaches several grounds at once, clause
order decides which reason surfaces. Make that precedence explicit rather than
letting it be an accident of how the file is arranged.

Whether `unknown` is reachable depends on your rule set. Above it is reached, by
an activity absent from `processing/3`. If `may_process` and `denial` are
exhaustive over your inputs it becomes dead code — but leaving the branch in
place turns a future gap in the rules into a distinguishable outcome rather than
a wrong verdict.

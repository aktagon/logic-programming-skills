# Prolog Idioms

Deeper notes on how the Prolog engine works and how that should shape clause design. Read this when the SKILL.md quick reference is not enough — when you are debugging a non-terminating query, designing a recursive predicate, or wondering why the engine returns the "wrong" answer first.

## The four-port model

Every goal in a Prolog proof tree has four ports the engine moves through. Internalize this — it is the mental model that makes `trace` output legible.

| Port   | When triggered                               |
| ------ | -------------------------------------------- |
| `call` | Engine first attempts to satisfy the goal.   |
| `exit` | Goal succeeds; bindings flow forward.        |
| `redo` | Caller backtracks; engine retries the goal.  |
| `fail` | No (more) clauses match; control returns up. |

When debugging:

```prolog
?- trace, ancestor(tom, X).
```

Read the ports literally. `call ancestor(tom, _)` … `call parent(tom, _)` … `exit parent(tom, bob)` … `exit ancestor(tom, bob)`. On `;` for the next solution you see `redo ancestor(tom, bob)`, then the engine tries the second clause of `ancestor/2`.

Most "why doesn't this terminate?" bugs become obvious in trace: a `redo` keeps firing on a clause that recurses before its base case can prune the search.

## Argument-order conventions

A predicate's _meaning_ is not in its name — it is in the discipline you keep about which argument plays which role. SWI-Prolog documentation uses mode annotations to make this explicit:

- `+Arg` — argument must be bound at call time (input).
- `-Arg` — argument is bound by the predicate (output).
- `?Arg` — either; the predicate is reversible.
- `@Arg` — not unified, only inspected.

Document modes in a comment above every exported predicate:

```prolog
% !load
%! parent(?Parent, ?Child) is nondet.
%  True when Parent is a parent of Child. Usable in any mode.
parent(tom, bob).
parent(tom, liz).
```

Conventional argument ordering in the standard library:

1. Inputs before outputs: `append(?L1, ?L2, ?L3)`, `atom_concat(?A, ?B, ?AB)`. Both are fully reversible — `atom_concat(A, B, abc)` enumerates `''-abc`, `a-bc`, `ab-c`, `abc-''`.
2. The "subject" the predicate is *about* comes first: `length(?List, ?Int)`, `nth0(?Index, ?List, ?Elem)`. The structure being recursed over leads; derived values follow.
3. Accumulator before result in fold-style predicates: `foldl(:Goal, ?List, +Acc0, -Acc)`.

Note that the most-used library predicates are `?` almost everywhere, not `(+,-)`. `length/2` and `append/3` are relations, and writing them as `(+List, -Len)` in your own docs understates what they do.

Violating these makes your code surprising to other Prolog programmers — they will write queries in the wrong direction and conclude your predicate is broken.

## Recursion patterns

### Direct recursion with a base case

```prolog
% !verify
% Named sum_/2, not sum_list/2: sum_list/2 is a library(lists) predicate, and
% defining it here would silently shadow the library version.
sum_([], 0).
sum_([H|T], S) :- sum_(T, S1), S is S1 + H.

main :-
    sum_([1,2,3,4], 10),
    sum_([], 0),
    % `S is S1 + H` fixes the mode to (+,?): a hole anywhere in the list is an
    % instantiation error, not a constraint to solve.
    catch(sum_([1,_,3], _), error(instantiation_error, _), true).
```

Simple and correct, but **not tail-recursive** — every recursive call leaves a pending `S is S1 + H` on the stack.

### Accumulator-passing (tail recursive)

```prolog
% !verify
sum_(L, S) :- sum_(L, 0, S).
sum_([], Acc, Acc).
sum_([H|T], Acc, S) :- Acc1 is Acc + H, sum_(T, Acc1, S).

main :-
    sum_([1,2,3,4], 10),
    % A million elements, folded in constant local stack because the recursive
    % call is the last goal in the clause.
    numlist(1, 1000000, Big),
    sum_(Big, Total), Total =:= 500000500000.
```

In practice reach for `sum_list/2` or `foldl/4` — this is here to show the shape,
not to be copied.

Two clauses, one private helper. The helper's accumulator argument carries the running total. SWI-Prolog will eliminate the tail call; long lists no longer blow the stack.

### `findall/3` instead of manual collection

Reach for `findall(Template, Goal, Bag)` before you write a `write`/`fail` loop that collects results into an assertz'd list. It is the idiomatic way to materialize all solutions.

```prolog
% !verify
parent(tom, bob).
parent(tom, liz).

main :-
    findall(X, parent(tom, X), Children), Children == [bob, liz],
    % setof/3 sorts and dedupes...
    setof(X, parent(tom, X), [bob, liz]),
    % ...and on no solutions findall/3 returns [] where the other two FAIL.
    findall(X, parent(ann, X), []),
    \+ bagof(X, parent(ann, X), _),
    \+ setof(X, parent(ann, X), _).
```

`bagof/3` and `setof/3` are richer variants — `setof` sorts and dedupes; both fail (rather than returning `[]`) when there are no solutions.

## Difference lists

A **difference list** is a list represented as a pair: an open list and the
unbound tail that terminates it — conventionally written `Open-Hole`. The list it
denotes is "everything in `Open` up to `Hole`". Because the tail is a variable,
appending is a single unification instead of a traversal:

```prolog
% !verify
concat(A-B, B-C, A-C).      % the whole implementation

main :-
    A = [1,2|T1]-T1,
    B = [3,4|T2]-T2,
    concat(A, B, Whole-Hole),
    Hole = [],                            % close it to get an ordinary list
    Whole == [1,2,3,4],
    % The price: a CLOSED list is not a difference list, and the same
    % predicate cannot join two of them.
    \+ concat([1,2]-[], [3]-[], _-[]).
```

`concat/3` is O(1) where `append/3` is O(|A|), which is why accumulating output
by repeated `append/3` is the standard Prolog performance mistake and why the
fix is usually "return a difference list and close it once at the end".

Two properties to hold on to:

1. **The hole may only be filled once.** A difference list is single-assignment, so you cannot reuse `A` after `concat/3` has bound its tail. Treat it as consumed.
2. **`length/2`, `member/2` and friends do not work on one.** They see an open list and either loop or generate. Close it first.

This is not an exotic technique you opt into — it is the representation DCGs
already use. `--> ` translates each non-terminal into a predicate over `S0`/`S`,
which is exactly `Open`/`Hole` spread across two arguments instead of joined by
`-`. That is why DCG bodies concatenate for free, and why `phrase/3` can hand you
the unconsumed remainder without copying anything. See the DCG section in
`SKILL.md` for the translation written out beside its DCG.

## Cut (`!`) — when it is and is not a smell

A _green cut_ prunes branches the engine would never have succeeded on anyway. It is a performance hint and removing it does not change the program's logical meaning. These are fine but rarely necessary in modern SWI-Prolog where indexing is good.

A _red cut_ changes the program's logical meaning — without the cut, you would get extra (wrong) answers on backtracking. Red cuts are the smell. Two common cases:

```prolog
% !verify
% Red cut, AND not steadfast. The third argument is unified in the head, so a
% pre-bound output takes part in clause selection: max(3, 2, 2) skips this
% clause, matches the second, and wrongly succeeds.
max(X, Y, X) :- X >= Y, !.
max(_, Y, Y).

main :-
    max(3, 2, M), M == 3,      % computed output: the right answer
    max(3, 2, 2).              % pre-bound output: wrongly succeeds. The defect.
```

Replace with explicit guards that make the cases mutually exclusive:

```prolog
% !verify
max(X, Y, X) :- X >= Y.
max(X, Y, Y) :- X <  Y.

main :-
    max(3, 2, M), M == 3,
    max(2, 3, N), N == 3,
    \+ max(3, 2, 2).           % pre-bound output is now simply checked
```

Now each clause is true in isolation, no cut is required, and `max(3, 2, 2)`
correctly fails. See `purity-and-modes.md` for why the superficially similar
`max(X, Y, Max) :- X >= Y, !, Max = X.` is in fact steadfast — a cut alone is not
the defect; output unification *before* the commitment is.

## Forced-output pattern

From the source: combine goals with `fail` to force backtracking through every solution while using I/O predicates for the side effect.

```prolog
% !verify
student(bob).
student(liz).

print_all_students :- student(X), write(X), nl, fail.
print_all_students.   % second clause succeeds after backtracking exhausts the first.

main :-
    with_output_to(string(S), print_all_students),
    S == "bob\nliz\n",
    % Exactly one solution: clause 1 always fails, clause 2 succeeds once.
    with_output_to(string(_), findall(t, print_all_students, Ts)),
    Ts == [t].
```

This is **not** a general control-flow technique. Use it only when you actually want output for every solution and do not need the results back in Prolog. For any in-language use, prefer `findall/3` or `forall/2`:

```prolog
% !load
?- forall(student(X), (write(X), nl)).
```

`forall(Cond, Action)` succeeds iff `Action` succeeds for every solution of `Cond` — cleaner semantics than the `fail`-driven loop.

## Negation as failure

`\+ Goal` succeeds if Goal cannot be proved from the current database. Two consequences:

1. **Closed-world assumption.** `\+ parent(tom, mary)` says "no clause in the database lets us conclude tom is mary's parent" — not "tom is definitely not mary's parent." If the knowledge base is incomplete, the answer can be misleading.
2. **Mode sensitivity.** `\+ Goal` requires Goal to be ground (or at least sufficiently instantiated) when called, otherwise you can get unsound results. `\+ parent(tom, X)` does _not_ mean "for all X, tom is not a parent of X" — it means "the goal `parent(tom, X)` cannot be proved with X unbound," which is usually false.

If you need genuine universal quantification, use `forall/2`. If you need three-valued logic (true / false / unknown), Prolog is the wrong tool — look at answer-set programming (ASP, e.g. clingo) instead.

## Common pitfalls

- **`=` vs `is` vs `==`**: `X = 2 + 3` unifies X with the term `+(2,3)`. `X is 2 + 3` evaluates and binds X to `5`. `X == Y` is term identity without unification — used to test whether two terms are _already_ the same, not to make them so.
- **Off-by-one on lists**: `[H|T]` peels one element. `[H1, H2 | T]` peels two. Empty list is `[]`, not `nil`.
- **Operators have precedence**: `=` is `700 xfx`, `,` is `1000 xfy`, so `X = a, b` parses as `','(=(X, a), b)` — the conjunction is the *outer* term, not an argument of `=`. The real trap runs the other way: to pass a conjunction as a single argument you must parenthesize it, as in `findall(X, (p(X), q(X)), L)`. Check any case with `?- T = (X = a, b), T =.. L.`
- **`assertz`/`retract` are not your friends**: they mutate the database at runtime and break the declarative reading of your program. Use them only at the system boundary (loading data, recording state across query sessions), never inside the logic of a predicate.
- **Singleton variable warnings are real**: `foo(X, Y) :- bar(X).` warns because Y is mentioned once. Either rename it `_` or `_Unused` to silence the warning intentionally, or fix the typo it is pointing at.

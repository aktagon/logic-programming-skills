# Attribution

`dev-scasp` reproduces four example programs and four predicate annotations from
one Apache-2.0 project. This page records the source, its licence, and what is
and is not from upstream.

## s(CASP)

- **Source:** <https://github.com/JanWielemaker/sCASP>, the SWI-Prolog port by
  Jan Wielemaker of <https://gitlab.software.imdea.org/ciao-lang/sCASP> by
  Joaquín Arias and the IMDEA / UTD team. Compared against upstream commit
  `72028b02d57e51fe24c4be54234ab75767cd469f` on 2026-10-21.
- **Licence:** Apache License 2.0. Copyright 2019 Joaquin Arias. The full text
  travels with this package as [APACHE-2.0.txt](APACHE-2.0.txt), which is what
  §4(a) requires. Neither upstream repository ships a NOTICE file.
- **Reproduced verbatim**, in `examples.md`: `examples/rps.pl`,
  `examples/birds.pl`, `examples/classic_negation_incostistent.pl` and
  `examples/queens.pl`. Changes are limited to reflowing clauses onto fewer lines
  and dropping some upstream comments. `rps.pl` and
  `classic_negation_incostistent.pl` are unchanged.
- **Also reproduced:** the four `#pred` annotation strings in `SKILL.md`
  (`'@(X) is a bird'`, `'@(X) can fly'`, `'@(X) can not fly'`,
  `'@(X:bird) is abnormal'`), from `examples/birds.pl`. Upstream's non-standard
  "can not" and the `@(X:bird)` type hint are why these are attributed rather
  than treated as convergence: nobody arrives at that wording twice.
- **Not from upstream:** everything else. The dual-program and sort guidance, the
  irreflexivity and boundary-refusal rules, the reason-term pattern, the
  mutation-battery rules, every measured line count, `scripts/verify_snippets.py`
  and its markers, and all GDPR, library-loan and Finnish-language `#pred`
  templates were written here, from debugging a production GDPR rule set.
  Upstream API names, option names, source line references and quoted renderer
  output are cited as facts about the software.

The material above is used under Apache-2.0, not under this skill's MIT licence.
Upstream offers it as-is, without warranties or conditions of any kind.

## Two programs are linked rather than reproduced

`hamcycle.pl` and `hamcycle_two.pl` are fetched by a `curl` command in
`examples.md` §4. They were reproduced here until 2026-10-21.

Both sit in upstream's `test/all_programs/sasp/` as well as its `examples/`,
byte-identical in both places. That directory is named after
[s(ASP)](https://sourceforge.net/projects/sasp-system/) by Kyle Marple, which
SourceForge lists as **GPLv3**, while s(CASP) itself is Apache-2.0. Upstream's
README states that s(CASP) "is based on s(ASP) by Kyle Marple".

**Whether those two files originate in the s(ASP) distribution is unverified.**
The evidence is a directory name and an identical copy, not a confirmed lineage;
the s(ASP) archive was not opened. If the lineage holds, Apache-2.0 attribution
would not clear them, and that would be upstream's problem to resolve rather than
this skill's.

Linking carries no licence obligation, so the question stops mattering here. It
cost one of the two `% !load-fails` specimens, and the trade was deliberate: a
licence question nobody could close is not worth shipping to make a point about a
directive.

## Scope of this file

It covers reproduced expression only. Techniques, ideas and facts about how
s(CASP) behaves are not copyrightable and need no permission — naming the source
for those, as `SKILL.md` does under its own Attribution heading, is courtesy and
good practice rather than an obligation.

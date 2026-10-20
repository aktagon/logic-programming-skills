# Contributing

These skills are compiled output. Every file here is generated from a
hand-edited source in a private repository. A pull request against this
repository cannot be merged, because the next release overwrites it.

Open an issue instead. Corrections are welcome and are applied at the source.

## What makes a useful report

- **The skill and the file**, for example `dev-scasp`, `references/examples.md`.
- **What the skill said**, quoted.
- **What actually happened**, with the program and the system's own output.
- **Which version** of SWI-Prolog or s(CASP) you ran.

That report is more useful than a patch, because a patch to a generated file
still has to be rewritten into the source by hand before it can ship.

## Corrections to programs carry a high bar

A program that parses is not a program that is right. `dev-scasp` records that
two review rounds found twelve errors and every one was in a block that loaded
cleanly, including a malformed `#pred` that produced no diagnostic at all.

So paste what the system printed, not a reading of the code. For s(CASP), the
justification tree is the strongest evidence there is: it shows which rules
fired and which defaults applied.

## Attribution

`dev-scasp` adapts work from the SWI-Prolog port of s(CASP) by Jan Wielemaker
and from the original s(CASP) by Joaquín Arias and the IMDEA / UTD team. Both
upstream projects are Apache-2.0. The skill's own `SKILL.md` carries the credit
under its Attribution heading.

If you believe any part of this package reproduces upstream material beyond what
the attribution covers, report it as an issue and it will be corrected at the
source.

## Licensing

Contributions are accepted under the MIT licence this repository ships. Do not
paste code from a source whose licence you have not checked: attribution
obligations travel with derived material, and Apache-2.0 material in particular
cannot be relicensed.

# Contributing

Thanks for wanting to improve these skills. Read this first — the workflow is
not the usual one, and a pull request against the wrong tree will be closed
without being merged, which wastes your time.

## Everything published is build output

The public repository contains compiled packages only. Each `skills/<name>/`
directory is emitted by a compiler from a single markdown seed, and every
generated file carries a DO-NOT-EDIT marker. A change committed to a published
package is overwritten on the next publish, so a pull request against it cannot
survive even if it is correct.

The seeds, the ontology that validates them, and the emitters live in a private
repository maintained by Aktagon.

## What that means for you

**Report the problem, and we will fix it in the seed.** Open an issue with:

- The skill and the file — for example `dev-zig`, `references/build-system.md`.
- What is wrong. A wrong API name, an example that does not compile, advice that
  is stale for the pinned version, a broken cross-reference.
- What it should say instead, if you know.
- How you found out. For code, the compiler output is the strongest evidence
  there is, and it is what gets a fix prioritised.

That report is more useful than a patch, because a patch to a generated file
still has to be rewritten into the seed by hand before it can ship.

## Corrections to Zig code carry a high bar

`dev-zig` claims that every Zig block in the package compiled under a real
`zig 0.16.0` before shipping. If you are reporting a code defect, run the gate
that makes that claim:

```bash
python3 skills/dev-zig/scripts/verify_snippets.py /path/to/zig \
    skills/dev-zig/SKILL.md skills/dev-zig/references/*.md
```

Paste the failure. The skill's design record (`skills/dev-zig/DESIGN.md`,
ZIG-002) explains why compiler output rather than review is the standard here:
Zig 0.16 renamed enough of the standard library that plausible-looking code is
routinely wrong, and only a compiler catches it.

Note that the skill is pinned to exactly one Zig version by design (ZIG-001).
"This does not work on 0.17" is expected, not a defect — though it is a useful
signal about when the skill needs re-pinning.

## Licensing

Contributions to the MIT-licensed packages are accepted under the MIT License.
Do not paste code from a source whose licence you have not checked; attribution
obligations have to travel with derived material, which is what
`skills/dev-zig/references/ATTRIBUTION.md` exists to honour.

## Contact

GitHub issues for anything about a skill. Security problems go through
[SECURITY.md](SECURITY.md), not an issue. Commercial licensing and consulting:
[aktagon.com](https://aktagon.com).

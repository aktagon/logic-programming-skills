# Support

## Install

As a plugin marketplace:

```
/plugin marketplace add aktagon/logic-programming-skills
/plugin install dev-prolog@logic-programming-skills
/plugin install dev-scasp@logic-programming-skills
```

Or copy a single skill directly:

```
git clone https://github.com/aktagon/logic-programming-skills.git
cp -R logic-programming-skills/skills/dev-scasp ~/.claude/skills/dev-scasp
```

Both routes install the same files.

## Getting help

Open an issue. Include the skill name, the program you were working on, and what
the system actually printed.

## What belongs here

- A skill that misstates Prolog or s(CASP) semantics, a built-in, or a flag.
- An example program that does not load or does not produce the stated answer.
- A skill that fires on the wrong question, or fails to fire on the right one.
- A reference file unreachable from its `SKILL.md`.

## What does not belong here

- **SWI-Prolog itself, or the s(CASP) implementations.** A solver bug belongs to
  its maintainers: <https://github.com/SWI-Prolog/swipl-devel>,
  <https://github.com/JanWielemaker/sCASP>,
  <https://gitlab.software.imdea.org/ciao-lang/sCASP>. What belongs here is a
  skill that describes one of them incorrectly.
- **Claude Code itself.** Bugs in the plugin system, the skill loader or the CLI
  belong upstream at <https://github.com/anthropics/claude-code>.
- **Debugging your own rule set.** These skills state how the languages behave.
  They do not audit the program you wrote.

## Response expectations

This is maintained alongside client work. Expect a first response within about a
week for issues, and sooner for anything reported through
[SECURITY.md](SECURITY.md). There is no service-level agreement attached to
these packages; see the LICENSE, which disclaims warranty.

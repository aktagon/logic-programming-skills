# Support

## Installing

These skills are distributed as a Claude Code plugin marketplace:

```
/plugin marketplace add aktagon/llmkit-skills
/plugin install dev-zig@llmkit-skills
```

They also work without the plugin system — clone the repository and copy the
skill directory you want into `~/.claude/skills/`:

```bash
git clone https://github.com/aktagon/llmkit-skills.git
cp -R llmkit-skills/skills/dev-zig ~/.claude/skills/dev-zig
```

Both routes install the same files.

## Getting help

| You want to | Go to |
| --- | --- |
| Report wrong or stale content in a skill | GitHub issues |
| Report a security problem | [SECURITY.md](SECURITY.md) — do not open an issue |
| Ask how to use a skill | GitHub issues |
| Ask about commercial use or consulting | [aktagon.com](https://aktagon.com) |

Before opening an issue about a skill's content, read
[CONTRIBUTING.md](CONTRIBUTING.md). It explains why these files are generated
and what a report needs to contain to be actionable.

## What is not supported here

- **Claude Code itself.** Bugs in the plugin system, the skill loader, or the
  CLI belong upstream at <https://github.com/anthropics/claude-code>.
- **The languages and libraries the skills document.** A Zig compiler bug is a
  Zig issue. What belongs here is a skill that describes Zig incorrectly.

## Response expectations

This is maintained alongside client work. Expect a first response within about
a week for issues, and sooner for anything reported through
[SECURITY.md](SECURITY.md). There is no service-level agreement attached to
these packages; see the LICENSE, which disclaims warranty.

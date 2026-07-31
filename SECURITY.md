# Security Policy

## Reporting a vulnerability

Use GitHub private vulnerability reporting:
<https://github.com/aktagon/llmkit-skills/security/advisories/new>. It is
private to the maintainers. Do not open a public issue for a security problem.

Include what the problem is, which file or skill it is in, and how to reproduce
it. You will get an acknowledgement within three working days and an assessment
within ten. If a fix ships, you will be credited unless you ask not to be.

## What counts as a security problem here

These packages are documentation plus a small number of scripts. The realistic
attack surface is narrow, and these are the things worth reporting:

- **A shipped script that mutates the host.** The snippet verifier
  (`skills/dev-zig/scripts/verify_snippets.py`) takes a compiler path as an
  argument and is designed to install nothing, fetch nothing, and start no
  services (`skills/dev-zig/DESIGN.md`, ZIG-003 and ZIG-006). Any path by which
  it installs a package, reaches the network, or writes outside its working
  directory is a defect, and a serious one.
- **Prompt injection in shipped content.** These files are loaded into an AI
  agent's context. Text that attempts to redirect the agent — instructions to
  exfiltrate data, run commands, ignore its operator, or fetch remote content —
  is a security problem regardless of how it got in.
- **Code samples that teach an unsafe pattern as if it were correct.** A shipped
  example that leaks credentials, disables verification, or demonstrates an
  injectable query without flagging it is in scope.
- **A supply-chain issue in the distribution:** a tampered file, or a plugin
  manifest pointing somewhere it should not.

## Out of scope

- Vulnerabilities in the languages, compilers, or libraries the skills document.
  Report those to their maintainers.
- Vulnerabilities in Claude Code itself — <https://github.com/anthropics/claude-code>.
- Code you wrote by following a skill's advice. The LICENSE disclaims warranty;
  review what an agent produces before you run it.

## Supported versions

Only the current published state of `master` is supported. These packages carry
a version per skill and are re-published as a whole; there are no maintenance
branches and no backports to earlier versions.

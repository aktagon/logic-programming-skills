# Security Policy

## Reporting a vulnerability

Use GitHub private vulnerability reporting:

<https://github.com/aktagon/logic-programming-skills/security/advisories/new>

It is private to the maintainers. Do not open a public issue for a security
problem.

Include what the problem is, which file or skill it is in, and how to reproduce
it. You will get an acknowledgement within three working days and an assessment
within ten. If a fix ships, you will be credited unless you ask not to be.

## What counts as a security problem here

This repository ships two markdown skills and a small number of scripts. The
realistic surface is narrow:

- **Prompt injection in shipped content.** These files are loaded into an AI
  agent's context. Text that tries to redirect the agent — to exfiltrate data,
  run commands, ignore its operator, or fetch remote content — is a security
  problem regardless of how it got in.
- **An example program that is unsafe to run.** A shipped Prolog or s(CASP)
  program that writes outside its working directory, reaches the network, shells
  out, or consumes unbounded memory on the stated input is in scope. Goal-directed
  solving can loop, and an example that loops without saying so is a defect.
- **A rule set that teaches an unsafe pattern as correct.** `dev-scasp` is used
  for defeasible reasoning over real policy, so an example that encodes a wrong
  default or a silent `#pred` failure carries further than an ordinary typo.
- **A supply-chain issue in the distribution:** a tampered file, or a plugin
  manifest pointing somewhere it should not.

## Out of scope

- Vulnerabilities in SWI-Prolog, in either s(CASP) implementation, or in any
  library the skills document. Report those to their maintainers.
- Vulnerabilities in Claude Code itself —
  <https://github.com/anthropics/claude-code>.
- Code you wrote by following a skill's advice. The LICENSE disclaims warranty;
  review what an agent produces before you run it.

## Supported versions

Only the current published state of `master` is supported. These packages carry
a version per skill and are re-published as a whole. There are no maintenance
branches and no backports to earlier versions.

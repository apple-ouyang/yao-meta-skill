# Autonomous Adaptation Method

This reference defines the safe foundation for adaptive self-iteration.

## Scope

Adaptive iteration is a proposal-only loop until a human explicitly approves a patch application workflow. The current implementation may:

- read one user-provided local source file;
- redact sensitive text before storing evidence excerpts;
- summarize repeated preferences and operational signals;
- produce adaptation proposals with target files, risks, tests, and rollback plans.

It must not:

- scan shell history, browser history, chat logs, mail, or private folders by default;
- infer permanent user memory from a single comment;
- write source files as part of scan or proposal generation;
- count proposals as completed implementation evidence.

## Flow

1. `adapt-scan` reads an explicit source path and writes `reports/user_patterns.json` plus `reports/user_patterns.md`.
2. `adapt-propose` reads the pattern report and writes `reports/adaptation_proposals.json` plus `reports/adaptation_proposals.md`.
3. A reviewer decides whether any proposal is worth implementing.
4. Future `adapt-apply` work must require approval evidence, allowlisted targets, regression commands, and rollback metadata before writing files.

## Evidence Standard

Each proposal should include:

- the repeated pattern that triggered it;
- redacted excerpts, never unredacted raw content;
- target files and change intent;
- risk level and boundary;
- verification commands;
- rollback plan;
- a clear `proposal-only` status.

## Review Boundary

The adaptive loop improves iteration quality, but it does not replace normal review. Any proposal touching trigger behavior, reports, packaging, telemetry, privacy, or governance must still pass the same tests and release gates as a manually designed change.

# Review Studio 2.0 Method

Review Studio is the release-facing audit surface for a skill package. It does not replace the detailed reports; it turns them into one reviewer decision page.

## Purpose

- Show release blockers and warnings before the package deepens.
- Link every gate back to a concrete evidence artifact.
- Keep review flow vertical: summary first, gates second, supporting details after.
- Avoid hiding output quality, runtime, trust, and portfolio issues across separate pages.

## Required Gates

1. Intent Canvas: intent confidence and unresolved input/output/exclusion gaps.
2. Trigger Lab: route scorecard, misroutes, ambiguous cases, and near-neighbor safety.
3. Output Lab: with-skill vs baseline delta, case count, file-backed cases, near-neighbor cases, and boundary cases.
4. Context Budget: initial load, budget tier, warnings, and quality density.
5. Runtime Matrix: target conformance pass/fail and degradation notes.
6. Trust Report: secret scan, script surface, dependency pinning, network/interactive flags, and package hash.
7. Skill Atlas: route collisions, stale skills, owner gaps, and no-route opportunities.
8. Release Notes: promotion status, migration notes, known gaps, and next move.

## Gate Semantics

- `pass`: evidence is present and the gate is satisfied.
- `warn`: review can continue, but the issue must be visible before release.
- `block`: do not claim production, library, governed, or public readiness until fixed.

For library and governed skills, Output Lab should have at least five cases and cover file-backed, near-neighbor, and boundary scenarios.

# Packaging Contracts

`cross_packager.py` is not just an export helper. It defines and validates platform contracts.

## Current Targets

- `openai`
- `claude`
- `generic`

## Contract Shape

Each target contract defines:

- required output fields
- required output files
- field mapping from the neutral source metadata
- portable execution metadata
- trust-boundary metadata
- degradation strategy metadata

## Failure Handling

When `--expectations` is provided:

- missing required files cause exit code `2`
- missing required fields cause exit code `2`
- validation failures are emitted in the JSON report

## Source Of Truth

The platform-neutral semantic source is Skill IR when it exists:

- `reports/skill-ir.json`
- `skill-ir/examples/<skill-name>.json`

The structural validation sources remain:

- `SKILL.md`
- `agents/interface.yaml`

Target-specific metadata is generated at packaging time. The adapter must carry
`ir_source`, `ir_schema_version`, `job_to_be_done`, `semantic_contract`, and
`semantic_parity` so reviewers can see whether the target preserved the core
skill meaning or fell back to frontmatter-only metadata.

## Portability Model

The packaging layer now preserves four portable semantics from the neutral source:

- activation
- execution
- trust
- degradation
- platform-neutral skill meaning from Skill IR

This means portability is not just "can it export a file?" but also "does the exported target preserve the source package's activation and safety assumptions?"

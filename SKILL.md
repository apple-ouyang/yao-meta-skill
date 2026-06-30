---
name: yao-meta-skill
description: Create, refactor, evaluate, and package agent skills from workflows, prompts, transcripts, docs, or notes. Use for skill creation, workflow packaging, skill improvement, evals, and distribution.
metadata:
  author: Yao Team
---

# Yao Meta Skill

## 默认语言

默认用简体中文沟通、解释取舍、输出报告和撰写生成 skill 正文；除非用户明确要求其它语言。代码标识、文件路径、YAML keys、JSON fields、命令名、包名和 API 术语保持 English。英文输入的名称和机器契约保持原样。

## Router Rules

- Route by frontmatter `description`.
- Keep `SKILL.md` lean; put guidance in `references/`, logic in `scripts/`, and evidence in `reports/`.
- Use the lightest reliable process.

## Entrypoint Contract

`SKILL.md` is the cockpit, not the knowledge base. Keep job, boundary, workflow, output contract, branch selection, and safe defaults here. Move detail out only when the model can still choose the right path. If a reference is always read, compress critical rules back here or justify it in [Resource Boundaries](references/resource-boundaries.md).

## Compact Workflow

1. For one-off/no reusable process: `Do not create a skill`; prefer `near-neighbor`; require `repeated use` + `reusable output contract`.
2. Capture job, output, exclusions, constraints, standards, and the lightest fit.
3. Scan references: external benchmark, user source, local fit; surface only uncertainty or conflict.
4. Write `description` early, test route quality, then add only earned folders, reports, and gates.

Modes and playbooks: `Scaffold`, `Production`, `Library`, `Governed`; [Method](references/skill-engineering-method.md), [Intent](references/intent-dialogue.md), [Operating Modes](references/operating-modes.md), [Resource Boundaries](references/resource-boundaries.md).

## Skill OS 2.0 Gates

For production, library, governed, or team-distributed work, run only earned release gates: Skill IR, target compiler, trigger + output eval, Skill Atlas, conformance, trust, registry/package/install, upgrade, drift, waiver, and Review Studio.

## Governed Package Boundary

For file-backed, release-critical, or governed packages, include `owner`, `review cadence`, `input_files`, `output contract`, `rollback boundary`, `trust report`, and `reports/output_quality_scorecard.md`; mark unavailable telemetry, approvals, metrics, or benchmarks as `missing evidence`. Preserve audit labels literally.

## First-Turn Style

- Start from the user's work/outcome before structure.
- Ask only `2-3` key questions unless enough detail exists.
- In Chinese, sound companion-like; use [Intent Dialogue](references/intent-dialogue.md).

## Output Contract

Unless asked otherwise, produce `SKILL.md`, aligned `agents/interface.yaml`, justified assets, and a short summary of boundary, exclusions, gates, and next steps.

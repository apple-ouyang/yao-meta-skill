# Architecture Maintainability

Generated at: `2026-06-14`

## Summary

- decision: `watch-maintainability-hotspots`
- python files: `141`
- scripts: `85`
- tests: `56`
- internal modules: `14`
- CLI scripts: `72`
- Yao CLI command handlers: `35`
- largest file lines: `1196`
- hotspots: `3`
- blockers: `0`

This report keeps maintainability risk visible before the Meta Skill grows more gates, renderers, and CLI commands.

## Hotspots

| File | Lines | Kind | Severity | Recommended action |
| --- | ---: | --- | --- | --- |
| `scripts/render_review_studio.py` | `1196` | `cli-script` | `warn` | Move data loading and large section renderers into focused review_studio_* modules. |
| `scripts/yao.py` | `1159` | `cli-script` | `warn` | Split command handlers by domain while keeping scripts/yao.py as the thin CLI orchestrator. |
| `scripts/render_review_viewer.py` | `983` | `cli-script` | `warn` | Split viewer data assembly from HTML section rendering. |

## Largest Files

| File | Lines | Kind | Severity |
| --- | ---: | --- | --- |
| `scripts/render_review_studio.py` | `1196` | `cli-script` | `warn` |
| `scripts/yao.py` | `1159` | `cli-script` | `warn` |
| `scripts/render_review_viewer.py` | `983` | `cli-script` | `warn` |
| `tests/verify_yao_cli.py` | `838` | `test` | `pass` |
| `scripts/skill_report_model.py` | `782` | `internal-module` | `pass` |
| `scripts/compile_skill.py` | `734` | `cli-script` | `pass` |
| `scripts/optimize_description.py` | `723` | `cli-script` | `pass` |
| `scripts/trust_check.py` | `714` | `internal-module` | `pass` |
| `scripts/yao_cli_parser.py` | `691` | `internal-module` | `pass` |
| `scripts/build_skill_atlas.py` | `674` | `cli-script` | `pass` |
| `scripts/skill_report_layout.py` | `653` | `internal-module` | `pass` |
| `scripts/render_reference_synthesis.py` | `644` | `cli-script` | `pass` |

## Release Rule

- `block` hotspots should be split before governed release.
- `warn` hotspots can ship only when Review Studio keeps them visible and a reviewer accepts the modularization plan.
- Do not split a file only for line count; split when a stable responsibility boundary is clear.

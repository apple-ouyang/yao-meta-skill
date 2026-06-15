# Architecture Maintainability

Generated at: `2026-06-13`

## Summary

- decision: `pass`
- python files: `166`
- scripts: `105`
- tests: `61`
- internal modules: `29`
- CLI scripts: `78`
- Yao CLI command handlers: `34`
- largest file lines: `894`
- hotspots: `0`
- blockers: `0`

This report keeps maintainability risk visible before the Meta Skill grows more gates, renderers, and CLI commands.

## Hotspots

No file-size hotspots found.

## Largest Files

| File | Lines | Kind | Severity |
| --- | ---: | --- | --- |
| `tests/verify_yao_cli.py` | `894` | `test` | `pass` |
| `scripts/yao.py` | `882` | `cli-script` | `pass` |
| `scripts/skill_report_layout.py` | `805` | `internal-module` | `pass` |
| `scripts/skill_report_model.py` | `800` | `internal-module` | `pass` |
| `scripts/yao_cli_parser.py` | `765` | `internal-module` | `pass` |
| `tests/verify_review_studio.py` | `749` | `test` | `pass` |
| `scripts/compile_skill.py` | `734` | `cli-script` | `pass` |
| `scripts/build_skill_atlas.py` | `730` | `cli-script` | `pass` |
| `scripts/optimize_description.py` | `723` | `cli-script` | `pass` |
| `scripts/trust_check.py` | `714` | `internal-module` | `pass` |
| `scripts/review_studio_layout.py` | `694` | `internal-module` | `pass` |
| `scripts/render_review_viewer.py` | `685` | `cli-script` | `pass` |

## Release Rule

- `block` hotspots should be split before governed release.
- `warn` hotspots can ship only when Review Studio keeps them visible and a reviewer accepts the modularization plan.
- Do not split a file only for line count; split when a stable responsibility boundary is clear.

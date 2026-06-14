# Benchmark Reproducibility

Generated at: `2026-06-14`
Commit: `5d1d3bbd302aa9c6d0e5f5767c5bdc776b517a03`
Working tree dirty at generation: `true`

## Summary

- reproducibility ready: `true`
- methodology complete: `true`
- required artifacts: `24`
- missing artifacts: `0`
- output cases: `5`
- disclosed failure cases: `3`
- reproduction commands: `21`
- provider evidence complete: `false`
- human review complete: `false`
- world-class ready: `false`
- changed files at generation: `25`

This report proves local benchmark reproducibility only. It keeps external provider and human-review gaps visible instead of counting them as complete.

## Methodology Sections

| Section | Status |
| --- | --- |
| `## Benchmark Types` | present |
| `## Sample Sources` | present |
| `## Evaluation Dimensions` | present |
| `## Weighting Rule` | present |
| `## Failure Disclosure` | present |
| `## Reproduction` | present |

## Required Artifacts

| Label | Path | Status | SHA256 |
| --- | --- | --- | --- |
| methodology | `reports/benchmark_methodology.md` | present | `57025e0123ce` |
| failure_disclosure | `evals/failure-cases.md` | present | `28833c0d4a21` |
| output_cases | `evals/output/cases.jsonl` | present | `a6ae96857116` |
| output_schema | `evals/output/schema.json` | present | `8ee340c95064` |
| output_scorecard | `reports/output_quality_scorecard.json` | present | `0806258a8e08` |
| output_execution | `reports/output_execution_runs.json` | present | `e4b3b5bf45a3` |
| blind_review | `reports/output_blind_review_pack.json` | present | `bbe2db8ec277` |
| review_adjudication | `reports/output_review_adjudication.json` | present | `240485a721af` |
| trigger_scorecard | `reports/route_scorecard.json` | present | `c164e83e36d0` |
| runtime_conformance | `reports/conformance_matrix.json` | present | `8251329e663d` |
| trust_report | `reports/security_trust_report.json` | present | `f518d733e79e` |
| python_compatibility | `reports/python_compatibility.json` | present | `3698aad5388c` |
| registry_audit | `reports/registry_audit.json` | present | `90137332142a` |
| package_verification | `reports/package_verification.json` | present | `6c62c8999479` |
| install_simulation | `reports/install_simulation.json` | present | `97055f63c699` |
| skill_os2_audit | `reports/skill_os2_audit.json` | present | `9c7b86742ed4` |
| world_class_evidence_plan | `reports/world_class_evidence_plan.json` | present | `194d5a681920` |
| world_class_evidence_ledger | `reports/world_class_evidence_ledger.json` | present | `dc4cf8cf1889` |
| world_class_evidence_intake | `reports/world_class_evidence_intake.json` | present | `5fbfcd35ac6a` |
| world_class_submission_review | `reports/world_class_submission_review.json` | present | `185a8cab25e7` |
| world_class_operator_runbook | `reports/world_class_operator_runbook.json` | present | `3d643dc8170b` |
| world_class_operator_runbook_markdown | `reports/world_class_operator_runbook.md` | present | `f67ca3d0aa9c` |
| world_class_operator_runbook_html | `reports/world_class_operator_runbook.html` | present | `963026f551dc` |
| world_class_claim_guard | `reports/world_class_claim_guard.json` | present | `250d616b028c` |

## Reproduction Commands

- `git rev-parse HEAD`
  - evidence: `git commit hash`
- `make eval-suite`
  - evidence: `reports/eval_suite.json`
- `python3 scripts/yao.py output-eval`
  - evidence: `reports/output_quality_scorecard.json`
- `python3 scripts/yao.py output-exec --runner-command '["python3","scripts/local_output_eval_runner.py"]'`
  - evidence: `reports/output_execution_runs.json`
- `python3 scripts/yao.py output-review`
  - evidence: `reports/output_review_adjudication.json`
- `python3 scripts/yao.py skill-ir . --output-json skill-ir/examples/yao-meta-skill.json`
  - evidence: `skill-ir/examples/yao-meta-skill.json`
- `python3 scripts/yao.py conformance .`
  - evidence: `reports/conformance_matrix.json`
- `python3 scripts/yao.py trust .`
  - evidence: `reports/security_trust_report.json`
- `python3 scripts/yao.py python-compat .`
  - evidence: `reports/python_compatibility.json`
- `python3 scripts/yao.py package . --platform openai --platform claude --platform generic --platform vscode --expectations evals/packaging_expectations.json --output-dir dist --zip`
  - evidence: `dist/yao-meta-skill.zip`
- `python3 scripts/yao.py package-verify . --package-dir dist --require-zip`
  - evidence: `reports/package_verification.json`
- `python3 scripts/yao.py install-simulate . --package-dir dist`
  - evidence: `reports/install_simulation.json`
- `python3 scripts/yao.py registry-audit .`
  - evidence: `reports/registry_audit.json`
- `python3 scripts/yao.py skill-os2-audit .`
  - evidence: `reports/skill_os2_audit.json`
- `python3 scripts/yao.py world-class-evidence .`
  - evidence: `reports/world_class_evidence_plan.json`
- `python3 scripts/yao.py world-class-ledger .`
  - evidence: `reports/world_class_evidence_ledger.json`
- `python3 scripts/yao.py world-class-intake .`
  - evidence: `reports/world_class_evidence_intake.json`
- `python3 scripts/yao.py world-class-submission-review .`
  - evidence: `reports/world_class_submission_review.json`
- `python3 scripts/yao.py world-class-runbook .`
  - evidence: `reports/world_class_operator_runbook.json`
- `python3 scripts/yao.py world-class-claim-guard .`
  - evidence: `reports/world_class_claim_guard.json`
- `make ci-test`
  - evidence: `CI target output`

## Failure Disclosure

- path: `evals/failure-cases.md`
- disclosed cases: `3`
- policy: Keep representative failures visible and tied to regression checks.

## Limits

- Local command-runner evidence is reproducible but does not replace provider-backed model holdout evidence.
- Pending blind-review decisions are visible but do not count as human adjudication.
- World-class readiness remains false until external and human evidence gaps close.

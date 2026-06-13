# World-Class Evidence Intake

Generated at: `2026-06-14`

## Summary

- decision: `awaiting-submissions`
- schema present: `true`
- templates: `4` / `4`
- submissions: `0` valid / `0` total
- invalid submissions: `0`
- ready for external collection: `true`
- ready for ledger review: `false`
- ready to claim world-class: `false`
- overclaim guard active: `true`

This report validates the intake contract for human and external evidence. A valid intake packet means the evidence is ready for ledger review; it does not by itself make a world-class claim true.

## Templates

| Evidence | Status | Path | Errors |
| --- | --- | --- | --- |
| `provider-holdout` | `pass` | `evidence/world_class/templates/provider-holdout.intake.json` | none |
| `human-adjudication` | `pass` | `evidence/world_class/templates/human-adjudication.intake.json` | none |
| `native-permission-enforcement` | `pass` | `evidence/world_class/templates/native-permission-enforcement.intake.json` | none |
| `native-client-telemetry` | `pass` | `evidence/world_class/templates/native-client-telemetry.intake.json` | none |

## Submissions

| Evidence | Status | Path | Errors |
| --- | --- | --- | --- |
| `none` | `n/a` | none | none |

## Boundary

- Templates and planned work do not count as accepted evidence.
- Local command-runner output does not count as provider-backed model evidence.
- Metadata fallback does not count as native permission enforcement.
- Pending reviewer work does not count as human adjudication.

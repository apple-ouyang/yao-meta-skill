# World-Class Evidence Intake

This directory defines the intake contract for external and human evidence required before `yao-meta-skill` can honestly claim public world-class completion.

The templates in `templates/` are review aids only. They do not count as accepted evidence. Real submissions belong in `evidence/world_class/submissions/`, which is intentionally gitignored by default so provider metadata, reviewer identity, or client integration notes can be reviewed before anything is committed.

Run:

```bash
python3 scripts/yao.py world-class-intake .
```

The intake validator checks:

- the evidence key matches the current world-class ledger
- the category and source type match the expected human or external evidence path
- artifact references are declared
- credentials, secrets, raw user content, and raw provider prompts are explicitly excluded
- planned work, local command-only output, and metadata fallback are not claimed as completion evidence

The generated intake report also includes an `operator_checklist` for each pending evidence item. Use it to find the template path, target submission path, preparation command, validation command, required provenance, success checks, and privacy boundary before asking a reviewer or external operator to submit evidence.

Accepted intake means "ready for ledger review", not "world-class complete". The ledger remains the source of truth for `ready_to_claim_world_class`.

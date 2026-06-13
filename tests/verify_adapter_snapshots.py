#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path
import yaml


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "cross_packager.py"
EXPECTATIONS = ROOT / "evals" / "packaging_expectations.json"
SNAPSHOTS = ROOT / "tests" / "snapshots"
TMP = ROOT / "tests" / "tmp_snapshot"


def main() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(ROOT),
            "--platform",
            "openai",
            "--platform",
            "claude",
            "--platform",
            "generic",
            "--expectations",
            str(EXPECTATIONS),
            "--output-dir",
            str(TMP),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(proc.returncode)

    failures = []
    for name in ("openai", "claude", "generic"):
        snapshot = json.loads((SNAPSHOTS / f"{name}_adapter.json").read_text(encoding="utf-8"))
        adapter = json.loads((TMP / "targets" / name / "adapter.json").read_text(encoding="utf-8"))
        if adapter.get("platform") != snapshot["platform"]:
            failures.append(f"{name}: platform mismatch")
        if adapter.get("canonical_metadata") != snapshot["canonical_metadata"]:
            failures.append(f"{name}: canonical metadata mismatch")
        for field in snapshot.get("required_fields", []):
            if field not in adapter:
                failures.append(f"{name}: missing required adapter field {field}")
        if adapter.get("ir_source") != "skill-ir/examples/yao-meta-skill.json":
            failures.append(f"{name}: adapter is not sourced from root Skill IR")
        if adapter.get("ir_schema_version") != "2.0.0":
            failures.append(f"{name}: missing Skill IR schema version")
        contract = adapter.get("semantic_contract", {})
        if contract.get("name") != "yao-meta-skill":
            failures.append(f"{name}: semantic contract name mismatch")
        if contract.get("trigger_description") != adapter.get("description"):
            failures.append(f"{name}: trigger description is not adapter description")
        if contract.get("job_to_be_done") != adapter.get("job_to_be_done"):
            failures.append(f"{name}: job-to-be-done not carried into adapter")
        if contract.get("resource_counts", {}).get("references", 0) <= 0:
            failures.append(f"{name}: semantic contract does not include reference counts")
        if contract.get("eval_counts", {}).get("output", 0) <= 0:
            failures.append(f"{name}: semantic contract does not include output eval counts")
        parity = adapter.get("semantic_parity", {})
        if parity.get("source") != "skill-ir":
            failures.append(f"{name}: semantic parity source is not skill-ir")
        if parity.get("name_matches_ir") is not True:
            failures.append(f"{name}: frontmatter name does not match Skill IR")
        if parity.get("description_matches_ir") is not True:
            failures.append(f"{name}: frontmatter description does not match Skill IR")
        if not (TMP / snapshot["required_generated_file"]).exists():
            failures.append(f"{name}: missing generated file {snapshot['required_generated_file']}")
        if name == "openai":
            meta = yaml.safe_load((TMP / "targets" / "openai" / "agents" / "openai.yaml").read_text(encoding="utf-8")) or {}
            compatibility = meta.get("compatibility", {})
            for field in ("canonical_format", "activation_mode", "execution_context", "shell", "trust_level", "remote_inline_execution", "degradation_strategy"):
                if not compatibility.get(field):
                    failures.append(f"{name}: missing portability metadata in generated openai.yaml: {field}")

    report = {"ok": not failures, "failures": failures}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

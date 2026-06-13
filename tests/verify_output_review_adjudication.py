#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_EVAL = ROOT / "scripts" / "run_output_eval.py"
ADJUDICATOR = ROOT / "scripts" / "adjudicate_output_review.py"


def run(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=check,
    )


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_output_review_adjudication"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    scorecard_json = tmp_root / "output_quality_scorecard.json"
    scorecard_md = tmp_root / "output_quality_scorecard.md"
    blind_pack_json = tmp_root / "output_blind_review_pack.json"
    blind_pack_md = tmp_root / "output_blind_review_pack.md"
    answer_key_json = tmp_root / "output_blind_answer_key.json"

    run(
        [
            str(OUTPUT_EVAL),
            "--cases",
            str(ROOT / "evals" / "output" / "cases.jsonl"),
            "--output-json",
            str(scorecard_json),
            "--output-md",
            str(scorecard_md),
            "--blind-pack-json",
            str(blind_pack_json),
            "--blind-pack-md",
            str(blind_pack_md),
            "--blind-answer-key-json",
            str(answer_key_json),
        ]
    )

    pending_json = tmp_root / "pending_adjudication.json"
    pending_md = tmp_root / "pending_adjudication.md"
    pending_proc = run(
        [
            str(ADJUDICATOR),
            "--blind-pack",
            str(blind_pack_json),
            "--answer-key",
            str(answer_key_json),
            "--decisions",
            str(tmp_root / "missing_decisions.json"),
            "--output-json",
            str(pending_json),
            "--output-md",
            str(pending_md),
        ]
    )
    pending_payload = json.loads(pending_proc.stdout)
    assert pending_payload["ok"], pending_payload
    assert pending_payload["summary"]["pair_count"] == 5, pending_payload
    assert pending_payload["summary"]["judgment_count"] == 0, pending_payload
    assert pending_payload["summary"]["pending_count"] == 5, pending_payload
    assert pending_payload["summary"]["agreement_rate"] is None, pending_payload
    assert pending_payload["summary"]["needs_review"], pending_payload
    assert pending_payload["summary"]["answer_revealed_count"] == 0, pending_payload
    assert pending_payload["summary"]["pending_answer_hidden_count"] == 5, pending_payload
    assert pending_payload["summary"]["reviewer_checklist_count"] == 5, pending_payload
    assert pending_payload["summary"]["reviewer_checklist_pending_count"] == 5, pending_payload
    assert pending_payload["summary"]["reviewer_checklist_ready_count"] == 0, pending_payload
    assert pending_payload["summary"]["reviewer_checklist_invalid_count"] == 0, pending_payload
    assert all(not item["expected_winner_variant"] and not item["expected_revealed"] for item in pending_payload["pairs"]), pending_payload
    checklist = {item["case_id"]: item for item in pending_payload["reviewer_checklist"]}
    assert checklist["skill-package-contract"]["readiness"] == "awaiting-decision", checklist["skill-package-contract"]
    assert checklist["skill-package-contract"]["answer_key_visible"] is False, checklist["skill-package-contract"]
    assert checklist["skill-package-contract"]["decisions_path"].endswith("tests/tmp_output_review_adjudication/missing_decisions.json"), checklist["skill-package-contract"]
    assert checklist["skill-package-contract"]["commands"]["write_template"] == "python3 scripts/adjudicate_output_review.py --write-template", checklist["skill-package-contract"]
    assert checklist["skill-package-contract"]["required_fields"]["winner_variant"].startswith("A or B"), checklist["skill-package-contract"]
    assert "No reviewer decisions recorded yet" in pending_md.read_text(encoding="utf-8"), pending_md
    pending_text = pending_md.read_text(encoding="utf-8")
    assert "| skill-package-contract | pending | hidden | pending |" in pending_text, pending_text
    assert "| skill-package-contract | pending | A | pending |" not in pending_text, pending_text
    assert "Reviewer Checklist" in pending_text, pending_text
    assert "Reviewer checklist: `0` ready / `5` total" in pending_text, pending_text
    assert "answer key visible: `false`" in pending_text, pending_text

    template_path = tmp_root / "output_review_decisions.json"
    template_proc = run(
        [
            str(ADJUDICATOR),
            "--blind-pack",
            str(blind_pack_json),
            "--answer-key",
            str(answer_key_json),
            "--decisions",
            str(template_path),
            "--output-json",
            str(tmp_root / "template_adjudication.json"),
            "--output-md",
            str(tmp_root / "template_adjudication.md"),
            "--write-template",
        ]
    )
    template_payload = json.loads(template_proc.stdout)
    assert template_payload["ok"], template_payload
    assert template_payload["template_written"], template_payload
    template = json.loads(template_path.read_text(encoding="utf-8"))
    assert len(template["decisions"]) == 5, template
    assert all(item["winner_variant"] == "" for item in template["decisions"]), template

    answer_key = json.loads(answer_key_json.read_text(encoding="utf-8"))
    decisions = {
        "schema_version": "1.0",
        "reviewer": "Yao QA",
        "reviewed_at": "2026-06-13",
        "decisions": [
            {
                "case_id": item["case_id"],
                "winner_variant": item["expected_winner_variant"],
                "confidence": 0.9,
                "reason": "Matches the rubric better.",
            }
            for item in answer_key["answers"]
        ],
    }
    filled_path = tmp_root / "filled_decisions.json"
    filled_path.write_text(json.dumps(decisions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    filled_proc = run(
        [
            str(ADJUDICATOR),
            "--blind-pack",
            str(blind_pack_json),
            "--answer-key",
            str(answer_key_json),
            "--decisions",
            str(filled_path),
            "--output-json",
            str(tmp_root / "filled_adjudication.json"),
            "--output-md",
            str(tmp_root / "filled_adjudication.md"),
        ]
    )
    filled_payload = json.loads(filled_proc.stdout)
    assert filled_payload["ok"], filled_payload
    assert filled_payload["summary"]["judgment_count"] == 5, filled_payload
    assert filled_payload["summary"]["pending_count"] == 0, filled_payload
    assert filled_payload["summary"]["agreement_count"] == 5, filled_payload
    assert filled_payload["summary"]["agreement_rate"] == 100.0, filled_payload
    assert filled_payload["summary"]["answer_revealed_count"] == 5, filled_payload
    assert filled_payload["summary"]["pending_answer_hidden_count"] == 0, filled_payload
    assert filled_payload["summary"]["reviewer_checklist_ready_count"] == 5, filled_payload
    assert filled_payload["summary"]["reviewer_checklist_pending_count"] == 0, filled_payload
    assert all(item["status"] == "match" for item in filled_payload["pairs"]), filled_payload
    assert all(item["expected_winner_variant"] in {"A", "B"} and item["expected_revealed"] for item in filled_payload["pairs"]), filled_payload
    filled_checklist = {item["case_id"]: item for item in filled_payload["reviewer_checklist"]}
    assert all(item["readiness"] == "adjudicated" and item["answer_key_visible"] for item in filled_checklist.values()), filled_checklist

    invalid = {
        "schema_version": "1.0",
        "reviewer": "Yao QA",
        "reviewed_at": "2026-06-13",
        "decisions": [
            {
                "case_id": answer_key["answers"][0]["case_id"],
                "winner_variant": "C",
                "confidence": 0.9,
                "reason": "Invalid variant should fail validation.",
            }
        ],
    }
    invalid_path = tmp_root / "invalid_decisions.json"
    invalid_path.write_text(json.dumps(invalid, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    invalid_proc = run(
        [
            str(ADJUDICATOR),
            "--blind-pack",
            str(blind_pack_json),
            "--answer-key",
            str(answer_key_json),
            "--decisions",
            str(invalid_path),
            "--output-json",
            str(tmp_root / "invalid_adjudication.json"),
            "--output-md",
            str(tmp_root / "invalid_adjudication.md"),
        ],
        check=False,
    )
    assert invalid_proc.returncode == 2, invalid_proc.stdout
    invalid_payload = json.loads(invalid_proc.stdout)
    assert not invalid_payload["ok"], invalid_payload
    assert invalid_payload["summary"]["invalid_decision_count"] == 1, invalid_payload
    assert invalid_payload["summary"]["answer_revealed_count"] == 0, invalid_payload
    assert invalid_payload["summary"]["reviewer_checklist_invalid_count"] == 1, invalid_payload
    assert invalid_payload["pairs"][0]["expected_winner_variant"] == "", invalid_payload
    assert invalid_payload["pairs"][0]["expected_revealed"] is False, invalid_payload
    invalid_checklist = {item["case_id"]: item for item in invalid_payload["reviewer_checklist"]}
    assert invalid_checklist[answer_key["answers"][0]["case_id"]]["readiness"] == "fix-decision", invalid_checklist
    assert invalid_checklist[answer_key["answers"][0]["case_id"]]["answer_key_visible"] is False, invalid_checklist
    assert invalid_payload["failures"], invalid_payload

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

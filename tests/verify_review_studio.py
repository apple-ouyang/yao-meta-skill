#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "render_review_studio.py"


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_review_studio"
    tmp_root.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "run_output_eval.py")], cwd=ROOT, check=True, capture_output=True, text=True)

    output_html = tmp_root / "review-studio.html"
    output_json = tmp_root / "review-studio.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(ROOT),
            "--output-html",
            str(output_html),
            "--output-json",
            str(output_json),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["ok"], payload
    assert payload["schema_version"] == "2.0", payload
    assert payload["summary"]["gate_count"] == 8, payload
    assert payload["summary"]["world_class_score"] > 0, payload
    gate_keys = {item["key"] for item in payload["gates"]}
    assert {"intent-canvas", "trigger-lab", "output-lab", "runtime-matrix", "trust-report", "skill-atlas", "release-notes"} <= gate_keys, payload
    output_gate = next(item for item in payload["gates"] if item["key"] == "output-lab")
    assert output_gate["status"] == "pass", output_gate
    assert "5/5 cases" in output_gate["detail"], output_gate
    assert "file-backed 1" in output_gate["detail"], output_gate
    assert output_html.exists(), output_html
    assert output_json.exists(), output_json
    html = output_html.read_text(encoding="utf-8")
    assert "Review Studio 2.0" in html, html[:400]
    assert "审查闸门" in html, html[:1200]
    assert "输出实验" in html, html[:2000]
    assert str(ROOT) not in output_json.read_text(encoding="utf-8"), output_json
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

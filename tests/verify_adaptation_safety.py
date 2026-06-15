#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "yao.py"
SCAN_SCRIPT = ROOT / "scripts" / "summarize_user_signals.py"
PROPOSE_SCRIPT = ROOT / "scripts" / "propose_adaptation.py"
TMP = ROOT / "tests" / "tmp_adaptation_safety"


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def main() -> None:
    shutil.rmtree(TMP, ignore_errors=True)
    skill_dir = TMP / "adaptive-demo-skill"
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    source = TMP / "curated-user-signals.jsonl"
    source.write_text(
        "\n".join(
            [
                json.dumps({"text": "报告默认中文简体，同时右上角提供英文切换。"}, ensure_ascii=False),
                json.dumps({"message": "新的 HTML 报告要双语，但默认中文简体。"}, ensure_ascii=False),
                json.dumps({"content": "报告 UI 需要 Kami 白底排版、图表模块和清晰导航。"}, ensure_ascii=False),
                json.dumps({"excerpt": "HTML 报告还是白底 Kami 风格，图表不要挤在一起。"}, ensure_ascii=False),
                json.dumps({"note": "不要自动扫描私人日志；必须由用户提供明确路径。"}, ensure_ascii=False),
                json.dumps({"body": "自适应升级需要先输出提案，授权后再修改，并能回滚。"}, ensure_ascii=False),
                json.dumps({"text": "隐私证据里也要保护 token=abc123456789、sk-1234567890abcdef 和 /Users/laoyao/private/path。"}, ensure_ascii=False),
                json.dumps({"text": "PDF 只提过一次，不能当作稳定偏好。"}, ensure_ascii=False),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    scan_proc = run_script(
        str(SCAN_SCRIPT),
        str(skill_dir),
        "--source",
        str(source),
        "--generated-at",
        "2026-06-15T00:00:00Z",
    )
    assert scan_proc.returncode == 0, scan_proc.stderr
    scan_payload = json.loads(scan_proc.stdout)
    assert scan_payload["ok"], scan_payload
    assert scan_payload["privacy_contract"]["local_only"] is True, scan_payload
    assert scan_payload["privacy_contract"]["implicit_private_log_scan"] is False, scan_payload
    assert scan_payload["privacy_contract"]["raw_content_stored"] is False, scan_payload
    assert scan_payload["privacy_contract"]["writes_repository_files"] is False, scan_payload
    assert scan_payload["source"]["path"].startswith("[external-explicit-source]/"), scan_payload
    pattern_ids = {item["pattern_id"] for item in scan_payload["patterns"]}
    assert {"language_default", "report_ui", "approval_safety"} <= pattern_ids, scan_payload
    serialized = json.dumps(scan_payload, ensure_ascii=False)
    assert "sk-1234567890abcdef" not in serialized, serialized
    assert "token=abc123456789" not in serialized, serialized
    assert "/Users/laoyao/private" not in serialized, serialized
    assert "[REDACTED_SECRET]" in serialized, serialized
    assert "[LOCAL_PATH]" in serialized, serialized
    assert (reports_dir / "user_patterns.json").exists(), reports_dir
    assert (reports_dir / "user_patterns.md").exists(), reports_dir

    propose_proc = run_script(
        str(PROPOSE_SCRIPT),
        str(skill_dir),
        "--generated-at",
        "2026-06-15T00:00:00Z",
    )
    assert propose_proc.returncode == 0, propose_proc.stderr
    proposal_payload = json.loads(propose_proc.stdout)
    assert proposal_payload["ok"], proposal_payload
    assert proposal_payload["summary"]["apply_supported"] is False, proposal_payload
    assert proposal_payload["proposal_contract"]["proposal_only"] is True, proposal_payload
    assert proposal_payload["proposal_contract"]["writes_repository_files"] is False, proposal_payload
    assert proposal_payload["summary"]["proposal_count"] >= 3, proposal_payload
    assert all(item["status"] == "proposal-only" for item in proposal_payload["proposals"]), proposal_payload
    assert all(item["requires_approval"] is True for item in proposal_payload["proposals"]), proposal_payload
    assert all(item["write_allowed_without_approval"] is False for item in proposal_payload["proposals"]), proposal_payload
    assert any(
        any("tests/verify_adaptation_safety.py" in command for command in item["verification_commands"])
        for item in proposal_payload["proposals"]
    ), proposal_payload
    assert not (skill_dir / "scripts" / "apply_adaptation.py").exists(), skill_dir
    assert (reports_dir / "adaptation_proposals.json").exists(), reports_dir
    assert (reports_dir / "adaptation_proposals.md").exists(), reports_dir

    missing_source_proc = run_script(str(SCAN_SCRIPT), str(skill_dir))
    assert missing_source_proc.returncode != 0, missing_source_proc

    history_source = TMP / ".zsh_history"
    history_source.write_text("报告默认中文\n报告默认中文\n", encoding="utf-8")
    history_proc = run_script(str(SCAN_SCRIPT), str(skill_dir), "--source", str(history_source))
    assert history_proc.returncode == 2, history_proc.stdout
    history_payload = json.loads(history_proc.stdout)
    assert history_payload["ok"] is False, history_payload
    assert any("Refusing private history source" in item for item in history_payload["failures"]), history_payload

    cli_skill_dir = TMP / "cli-adaptive-demo-skill"
    cli_skill_dir.mkdir(parents=True, exist_ok=True)
    cli_source = TMP / "cli-user-signals.jsonl"
    cli_source.write_text(
        "\n".join(
            [
                json.dumps({"text": "报告默认中文简体，同时提供英文切换。"}, ensure_ascii=False),
                json.dumps({"text": "新的 HTML 报告还是默认中文简体，并保留英文版。"}, ensure_ascii=False),
                json.dumps({"text": "报告 UI 要保持 Kami 白底排版和图表模块。"}, ensure_ascii=False),
                json.dumps({"text": "HTML 报告的图表和白底 Kami 排版都要清晰。"}, ensure_ascii=False),
                json.dumps({"text": "自适应升级必须先生成提案，授权后再修改。"}, ensure_ascii=False),
                json.dumps({"text": "不要默认扫描私人日志，要由用户提供明确路径。"}, ensure_ascii=False),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    cli_scan = run_script(
        str(CLI),
        "adapt-scan",
        str(cli_skill_dir),
        "--source",
        str(cli_source),
        "--generated-at",
        "2026-06-15T00:00:00Z",
    )
    assert cli_scan.returncode == 0, cli_scan.stderr
    cli_scan_payload = json.loads(cli_scan.stdout)
    assert cli_scan_payload["summary"]["pattern_count"] >= 3, cli_scan_payload
    assert cli_scan_payload["privacy_contract"]["writes_repository_files"] is False, cli_scan_payload
    assert (cli_skill_dir / "reports" / "user_patterns.json").exists(), cli_skill_dir
    cli_propose = run_script(
        str(CLI),
        "adapt-propose",
        str(cli_skill_dir),
        "--generated-at",
        "2026-06-15T00:00:00Z",
    )
    assert cli_propose.returncode == 0, cli_propose.stderr
    cli_proposal_payload = json.loads(cli_propose.stdout)
    assert cli_proposal_payload["summary"]["proposal_count"] >= 3, cli_proposal_payload
    assert cli_proposal_payload["proposal_contract"]["proposal_only"] is True, cli_proposal_payload
    assert cli_proposal_payload["proposal_contract"]["writes_repository_files"] is False, cli_proposal_payload
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

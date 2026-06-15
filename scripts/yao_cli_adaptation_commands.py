"""Adaptive proposal command handlers for the Yao CLI."""

import argparse
import json
from pathlib import Path

from yao_cli_runtime import run_script


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by yao.py to keep adaptive scan/proposal command handlers outside the thin CLI orchestrator."


def command_adapt_scan(args: argparse.Namespace) -> int:
    skill_dir = str(Path(args.skill_dir).resolve())
    cmd = [skill_dir, "--source", args.source]
    if args.output_json:
        cmd.extend(["--output-json", args.output_json])
    if args.output_md:
        cmd.extend(["--output-md", args.output_md])
    if args.min_support is not None:
        cmd.extend(["--min-support", str(args.min_support)])
    if args.generated_at:
        cmd.extend(["--generated-at", args.generated_at])
    if args.allow_history_source:
        cmd.append("--allow-history-source")
    result = run_script("summarize_user_signals.py", cmd)
    print(json.dumps(result["payload"] if result["payload"] is not None else result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


def command_adapt_propose(args: argparse.Namespace) -> int:
    skill_dir = str(Path(args.skill_dir).resolve())
    cmd = [skill_dir]
    if args.patterns_json:
        cmd.extend(["--patterns-json", args.patterns_json])
    if args.output_json:
        cmd.extend(["--output-json", args.output_json])
    if args.output_md:
        cmd.extend(["--output-md", args.output_md])
    if args.generated_at:
        cmd.extend(["--generated-at", args.generated_at])
    result = run_script("propose_adaptation.py", cmd)
    print(json.dumps(result["payload"] if result["payload"] is not None else result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2

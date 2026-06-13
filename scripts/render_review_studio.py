#!/usr/bin/env python3
import argparse
import html
import json
import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def parse_frontmatter(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end_index = lines[1:].index("---") + 1
    except ValueError:
        return {}
    text = "\n".join(lines[1:end_index])
    if yaml is not None:
        payload = yaml.safe_load(text) or {}
        return payload if isinstance(payload, dict) else {}
    data = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def display_path(skill_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(skill_dir.resolve()))
    except ValueError:
        try:
            return str(path.resolve().relative_to(ROOT.resolve()))
        except ValueError:
            return str(path.resolve())


def link_from(output_html: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), output_html.parent.resolve())


def report_link(output_html: Path, skill_dir: Path, rel_path: str) -> str:
    return link_from(output_html, skill_dir / rel_path)


def gate(key: str, label: str, status: str, detail: str, evidence: str, link: str = "") -> dict[str, str]:
    return {
        "key": key,
        "label": label,
        "status": status,
        "detail": detail,
        "evidence": evidence,
        "link": link,
    }


def status_label(status: str) -> str:
    return {"pass": "通过", "warn": "关注", "block": "阻断"}.get(status, status)


def add_blockers_from_gate(gates: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    blockers = [item for item in gates if item["status"] == "block"]
    warnings = [item for item in gates if item["status"] == "warn"]
    return blockers, warnings


def target_maturity(skill_dir: Path, overview: dict[str, Any]) -> str:
    manifest = load_json(skill_dir / "manifest.json")
    if manifest.get("maturity_tier"):
        return str(manifest["maturity_tier"])
    metadata = overview.get("metadata", {}) if isinstance(overview, dict) else {}
    if metadata.get("maturity_tier"):
        return str(metadata["maturity_tier"])
    return "scaffold"


def min_output_cases(maturity: str) -> int:
    if maturity in {"library", "governed"}:
        return 5
    if maturity == "production":
        return 3
    return 1


def build_gates(skill_dir: Path, output_html: Path, data: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    overview = data["overview"]
    maturity = target_maturity(skill_dir, overview)
    gates: list[dict[str, str]] = []

    intent = data["intent_confidence"]
    intent_score = int(intent.get("score", 0) or 0)
    intent_status = "pass" if intent.get("gate_passed") or intent_score >= 75 else "warn"
    gates.append(
        gate(
            "intent-canvas",
            "意图画布",
            intent_status,
            f"intent confidence {intent_score}/100; {intent.get('recommended_action', 'review current intent frame')}",
            "reports/intent-confidence.json",
            report_link(output_html, skill_dir, "reports/intent-confidence.md"),
        )
    )

    route = data["route_scorecard"]
    route_summary = route.get("summary", {})
    misroutes = int(route_summary.get("misroute_count", len(route.get("misroutes", []))) or 0)
    ambiguous = int(route_summary.get("ambiguous_case_count", len(route.get("ambiguous_cases", []))) or 0)
    if not route:
        route_status = "warn"
        route_detail = "route scorecard is missing; run route-scorecard before release review"
    else:
        route_status = "block" if misroutes else ("warn" if ambiguous else "pass")
        route_detail = f"{route_summary.get('total_cases', 0)} trigger cases; {misroutes} misroutes; {ambiguous} ambiguous"
    gates.append(
        gate(
            "trigger-lab",
            "触发实验",
            route_status,
            route_detail,
            "reports/route_scorecard.json",
            report_link(output_html, skill_dir, "reports/route_scorecard.md"),
        )
    )

    output = data["output_quality"]
    output_summary = output.get("summary", {})
    required_cases = min_output_cases(maturity)
    case_count = int(output_summary.get("case_count", 0) or 0)
    file_backed = int(output_summary.get("file_backed_case_count", 0) or 0)
    near_neighbor = int(output_summary.get("near_neighbor_case_count", 0) or 0)
    boundary = int(output_summary.get("boundary_case_count", 0) or 0)
    output_blocked = not output.get("ok", False) or not output_summary.get("gate_pass", False) or case_count < required_cases
    output_warn = file_backed == 0 or near_neighbor == 0 or boundary == 0
    if not output:
        output_status = "warn"
        output_detail = "output eval scorecard is missing; generate it before production review"
    else:
        output_status = "block" if output_blocked else ("warn" if output_warn else "pass")
        output_detail = (
            f"{case_count}/{required_cases} cases; with-skill {output_summary.get('with_skill_pass_rate', 0)}; "
            f"baseline {output_summary.get('baseline_pass_rate', 0)}; file-backed {file_backed}; near-neighbor {near_neighbor}"
        )
    gates.append(
        gate(
            "output-lab",
            "输出实验",
            output_status,
            output_detail,
            "reports/output_quality_scorecard.json",
            report_link(output_html, skill_dir, "reports/output_quality_scorecard.md"),
        )
    )

    context = data["context_budget"]
    context_stats = context.get("stats", {})
    context_status = "pass" if context.get("ok") else "block"
    if context.get("warnings"):
        context_status = "warn" if context_status == "pass" else context_status
    if not context:
        context_status = "warn"
    context_detail = (
        f"initial load {context_stats.get('estimated_initial_load_tokens', 'n/a')}/"
        f"{context_stats.get('context_budget_limit', 'n/a')}; quality density {context_stats.get('quality_density', 'n/a')}"
    )
    gates.append(
        gate(
            "context-budget",
            "上下文",
            context_status,
            context_detail,
            "reports/context_budget.json",
            report_link(output_html, skill_dir, "reports/context_budget.md"),
        )
    )

    conformance = data["conformance"]
    conformance_summary = conformance.get("summary", {})
    fail_count = int(conformance_summary.get("fail_count", 0) or 0)
    if not conformance:
        conformance_status = "warn"
        conformance_detail = "runtime conformance matrix is missing"
    else:
        conformance_status = "block" if fail_count else "pass"
        conformance_detail = f"{conformance_summary.get('pass_count', 0)} / {conformance_summary.get('target_count', 0)} targets pass"
    gates.append(
        gate(
            "runtime-matrix",
            "运行矩阵",
            conformance_status,
            conformance_detail,
            "reports/conformance_matrix.json",
            report_link(output_html, skill_dir, "reports/conformance_matrix.md"),
        )
    )

    trust = data["trust"]
    trust_summary = trust.get("summary", {})
    if not trust:
        trust_status = "warn"
        trust_detail = "security trust report is missing"
    else:
        trust_status = "block" if trust.get("failures") else ("warn" if trust.get("warnings") else "pass")
        trust_detail = (
            f"{trust_summary.get('secret_findings', 0)} secrets; "
            f"{trust_summary.get('script_count', 0)} scripts; "
            f"{trust_summary.get('network_script_count', 0)} network-capable scripts"
        )
    gates.append(
        gate(
            "trust-report",
            "信任报告",
            trust_status,
            trust_detail,
            "reports/security_trust_report.json",
            report_link(output_html, skill_dir, "reports/security_trust_report.md"),
        )
    )

    atlas = data["atlas"]
    atlas_summary = atlas.get("summary", {})
    atlas_issues = int(atlas_summary.get("route_collision_count", 0) or 0) + int(atlas_summary.get("owner_gap_count", 0) or 0)
    if not atlas:
        atlas_status = "warn"
        atlas_detail = "skill atlas is missing; portfolio-level conflicts are unknown"
    else:
        atlas_status = "warn" if atlas_issues else "pass"
        atlas_detail = (
            f"{atlas_summary.get('skill_count', 0)} skills; "
            f"{atlas_summary.get('route_collision_count', 0)} route collisions; "
            f"{atlas_summary.get('owner_gap_count', 0)} owner gaps; "
            f"{atlas_summary.get('stale_count', 0)} stale"
        )
    gates.append(
        gate(
            "skill-atlas",
            "组合治理",
            atlas_status,
            atlas_detail,
            "reports/skill_atlas.json",
            report_link(output_html, skill_dir, "reports/skill_atlas.html"),
        )
    )

    promotion = data["promotion"]
    migration_path = ROOT / "docs" / "migration-v2.md"
    if promotion:
        promotion_summary = promotion.get("summary", {})
        blocked = int(promotion_summary.get("blocked", 0) or 0)
        release_status = "block" if blocked else "pass"
        release_detail = f"{promotion_summary.get('promote', 0)} promote; {promotion_summary.get('keep_current', 0)} keep current; {blocked} blocked"
    else:
        release_status = "warn"
        release_detail = "promotion decisions are missing; release notes need reviewer confirmation"
    gates.append(
        gate(
            "release-notes",
            "发布路线",
            release_status,
            release_detail,
            "reports/promotion_decisions.json + docs/migration-v2.md",
            report_link(output_html, skill_dir, "reports/promotion_decisions.md") if promotion else str(migration_path),
        )
    )

    return gates


def weighted_score(gates: list[dict[str, str]]) -> int:
    weights = {
        "trigger-lab": 15,
        "output-lab": 20,
        "context-budget": 10,
        "runtime-matrix": 10,
        "trust-report": 10,
        "skill-atlas": 10,
        "release-notes": 10,
        "intent-canvas": 10,
    }
    earned = 0.0
    total = 0.0
    for item in gates:
        weight = weights.get(item["key"], 5)
        total += weight
        if item["status"] == "pass":
            earned += weight
        elif item["status"] == "warn":
            earned += weight * 0.6
    return int(round(earned / total * 100)) if total else 0


def evidence_paths(skill_dir: Path) -> dict[str, str]:
    rels = {
        "skill_overview": "reports/skill-overview.html",
        "review_viewer": "reports/review-viewer.html",
        "output_eval": "reports/output_quality_scorecard.md",
        "runtime_conformance": "reports/conformance_matrix.md",
        "trust_report": "reports/security_trust_report.md",
        "skill_atlas": "reports/skill_atlas.html",
        "migration": "docs/migration-v2.md",
        "skill_ir": "reports/skill-ir.json",
    }
    return {key: rel for key, rel in rels.items() if (skill_dir / rel).exists() or (ROOT / rel).exists()}


def load_review_data(skill_dir: Path) -> dict[str, dict[str, Any]]:
    reports = skill_dir / "reports"
    return {
        "overview": load_json(reports / "skill-overview.json"),
        "intent_confidence": load_json(reports / "intent-confidence.json"),
        "intent_dialogue": load_json(reports / "intent-dialogue.json"),
        "route_scorecard": load_json(reports / "route_scorecard.json"),
        "output_quality": load_json(reports / "output_quality_scorecard.json"),
        "conformance": load_json(reports / "conformance_matrix.json"),
        "trust": load_json(reports / "security_trust_report.json"),
        "context_budget": load_json(reports / "context_budget.json"),
        "promotion": load_json(reports / "promotion_decisions.json"),
        "atlas": load_json(reports / "skill_atlas.json"),
        "manifest": load_json(skill_dir / "manifest.json"),
        "frontmatter": parse_frontmatter(skill_dir / "SKILL.md"),
        "interface": load_yaml(skill_dir / "agents" / "interface.yaml"),
    }


def insight_cards(data: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    overview = data["overview"]
    output = data["output_quality"].get("summary", {})
    conformance = data["conformance"].get("summary", {})
    trust = data["trust"].get("summary", {})
    atlas = data["atlas"].get("summary", {})
    cards = [
        {
            "label": "Skill IR",
            "value": str(overview.get("skill_ir", {}).get("schema_version", "missing")),
            "detail": f"{overview.get('skill_ir', {}).get('target_count', 0)} targets in platform-neutral contract",
        },
        {
            "label": "Output Delta",
            "value": str(output.get("delta", "n/a")),
            "detail": f"{output.get('case_count', 0)} cases; {output.get('file_backed_case_count', 0)} file-backed",
        },
        {
            "label": "Runtime",
            "value": f"{conformance.get('pass_count', 0)}/{conformance.get('target_count', 0)}",
            "detail": "target conformance pass rate",
        },
        {
            "label": "Trust",
            "value": str(trust.get("secret_findings", 0)),
            "detail": f"{trust.get('script_count', 0)} scripts scanned; secrets found",
        },
        {
            "label": "Atlas",
            "value": str(atlas.get("route_collision_count", 0)),
            "detail": f"{atlas.get('skill_count', 0)} scanned skills; route collisions",
        },
    ]
    return cards


def render_gate_list(gates: list[dict[str, str]]) -> str:
    items = []
    for item in gates:
        link_html = f"<a href='{html.escape(item['link'])}'>证据</a>" if item.get("link") else ""
        items.append(
            "<article class='gate "
            + html.escape(item["status"])
            + "'>"
            f"<div><span>{html.escape(status_label(item['status']))}</span><h3>{html.escape(item['label'])}</h3></div>"
            f"<p>{html.escape(item['detail'])}</p>"
            f"<footer>{html.escape(item['evidence'])} {link_html}</footer>"
            "</article>"
        )
    return "".join(items)


def render_insights(cards: list[dict[str, str]]) -> str:
    return "".join(
        (
            "<article class='metric'>"
            f"<span>{html.escape(item['label'])}</span>"
            f"<strong>{html.escape(item['value'])}</strong>"
            f"<p>{html.escape(item['detail'])}</p>"
            "</article>"
        )
        for item in cards
    )


def render_issue_list(title: str, items: list[dict[str, str]]) -> str:
    if not items:
        return f"<section><h2>{html.escape(title)}</h2><p class='muted'>无。</p></section>"
    body = "".join(
        (
            "<li>"
            f"<strong>{html.escape(item['label'])}</strong>"
            f"<span>{html.escape(item['detail'])}</span>"
            "</li>"
        )
        for item in items
    )
    return f"<section><h2>{html.escape(title)}</h2><ul class='issues'>{body}</ul></section>"


def render_html(report: dict[str, Any]) -> str:
    summary = report["summary"]
    gates = report["gates"]
    blockers = report["blockers"]
    warnings = report["warnings"]
    insights = insight_cards(report["data"])
    overview = report["data"]["overview"]
    manifest = report["data"]["manifest"]
    frontmatter = report["data"]["frontmatter"]
    title = overview.get("display_name") or overview.get("title") or frontmatter.get("name") or manifest.get("name") or "Skill"
    description = overview.get("description") or frontmatter.get("description", "")
    nav = [
        ("#overview", "审查总览"),
        ("#intent", "意图画布"),
        ("#trigger", "触发实验"),
        ("#output", "输出实验"),
        ("#runtime", "运行矩阵"),
        ("#trust", "信任报告"),
        ("#atlas", "组合治理"),
        ("#release", "发布路线"),
    ]
    nav_html = "".join(f"<a href='{href}'>{label}</a>" for href, label in nav)
    gates_html = render_gate_list(gates)
    metrics_html = render_insights(insights)
    blockers_html = render_issue_list("阻断事项", blockers)
    warnings_html = render_issue_list("关注事项", warnings)
    output_summary = report["data"]["output_quality"].get("summary", {})
    conformance_summary = report["data"]["conformance"].get("summary", {})
    trust_summary = report["data"]["trust"].get("summary", {})
    atlas_summary = report["data"]["atlas"].get("summary", {})
    evidence_html = "".join(
        f"<li><strong>{html.escape(key)}</strong><span>{html.escape(value)}</span></li>"
        for key, value in report["evidence_paths"].items()
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(str(title))} Review Studio 2.0</title>
  <style>
    :root {{
      --ink: #1B365D;
      --text: #24201d;
      --muted: #746d66;
      --line: #e7ded2;
      --soft: #faf8f5;
      --pass: #1e6b52;
      --warn: #9a6718;
      --block: #9b2c2c;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: #ffffff;
      color: var(--text);
      font-family: Georgia, "Times New Roman", "Songti SC", serif;
      line-height: 1.58;
    }}
    nav {{
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      gap: 4px;
      justify-content: center;
      flex-wrap: wrap;
      padding: 10px 16px;
      background: rgba(255,255,255,0.94);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(10px);
    }}
    nav a {{
      color: var(--ink);
      text-decoration: none;
      font-size: 14px;
      padding: 7px 10px;
      border-radius: 6px;
    }}
    nav a:hover {{ background: var(--soft); }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 44px 28px 76px; }}
    header {{ border-bottom: 1px solid var(--line); padding-bottom: 28px; margin-bottom: 28px; }}
    .eyebrow {{ color: var(--ink); font-size: 14px; letter-spacing: .08em; text-transform: uppercase; }}
    h1, h2, h3 {{ color: var(--text); font-weight: 500; margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: clamp(34px, 5vw, 64px); line-height: 1.03; max-width: 920px; margin-top: 12px; }}
    h2 {{ font-size: 30px; margin-bottom: 14px; }}
    h3 {{ font-size: 19px; }}
    p {{ margin: 0; }}
    .lede {{ max-width: 820px; color: var(--muted); font-size: 20px; margin-top: 18px; }}
    .decision {{
      display: inline-flex;
      align-items: baseline;
      gap: 12px;
      margin-top: 24px;
      padding: 12px 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--ink);
      background: var(--soft);
    }}
    .decision strong {{ font-size: 28px; }}
    section {{ padding: 30px 0; border-bottom: 1px solid var(--line); scroll-margin-top: 76px; }}
    .metrics, .gates {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 14px;
    }}
    .gates {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .metric, .gate {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      background: #fff;
      min-width: 0;
    }}
    .metric span, .gate span {{ display: block; color: var(--muted); font-size: 13px; }}
    .metric strong {{ display: block; color: var(--ink); font-size: 34px; line-height: 1.1; margin: 8px 0; }}
    .metric p, .gate p, .gate footer, .issues span, .evidence span {{ color: var(--muted); font-size: 14px; overflow-wrap: anywhere; }}
    .gate {{ display: flex; flex-direction: column; gap: 10px; }}
    .gate.pass {{ border-top: 4px solid var(--pass); }}
    .gate.warn {{ border-top: 4px solid var(--warn); }}
    .gate.block {{ border-top: 4px solid var(--block); }}
    .gate footer {{ border-top: 1px solid var(--line); padding-top: 10px; }}
    a {{ color: var(--ink); }}
    .twocol {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 22px;
      align-items: start;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      background: #fff;
    }}
    .panel p {{ color: var(--muted); }}
    .issues, .evidence {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 12px;
    }}
    .issues li, .evidence li {{
      border-left: 3px solid var(--line);
      padding-left: 12px;
      display: grid;
      gap: 3px;
    }}
    .muted {{ color: var(--muted); }}
    @media (max-width: 980px) {{
      .metrics, .gates, .twocol {{ grid-template-columns: 1fr; }}
      main {{ padding: 32px 18px 60px; }}
      nav {{ justify-content: flex-start; overflow-x: auto; flex-wrap: nowrap; }}
      nav a {{ flex: 0 0 auto; }}
    }}
  </style>
</head>
<body>
  <nav>{nav_html}</nav>
  <main>
    <header id="overview">
      <div class="eyebrow">Review Studio 2.0</div>
      <h1>{html.escape(str(title))}</h1>
      <p class="lede">{html.escape(str(description))}</p>
      <div class="decision">
        <span>审查结论</span>
        <strong>{html.escape(summary['decision'])}</strong>
        <span>Score {html.escape(str(summary['world_class_score']))}/100</span>
      </div>
    </header>

    <section>
      <h2>核心指标</h2>
      <div class="metrics">{metrics_html}</div>
    </section>

    <section>
      <h2>审查闸门</h2>
      <div class="gates">{gates_html}</div>
    </section>

    <div class="twocol">
      {blockers_html}
      {warnings_html}
    </div>

    <section id="intent" class="twocol">
      <div class="panel">
        <h2>意图画布</h2>
        <p>{html.escape(str(report['data']['intent_confidence'].get('anchor_sentence', description)))}</p>
      </div>
      <div class="panel">
        <h2>证据路径</h2>
        <ul class="evidence">{evidence_html}</ul>
      </div>
    </section>

    <section id="trigger" class="twocol">
      <div class="panel"><h2>触发实验</h2><p>{html.escape(gates[1]['detail'])}</p></div>
      <div class="panel"><h2>组合治理</h2><p>{html.escape(str(atlas_summary))}</p></div>
    </section>

    <section id="output" class="twocol">
      <div class="panel"><h2>输出实验</h2><p>{html.escape(str(output_summary))}</p></div>
      <div class="panel"><h2>发布标准</h2><p>Governed 和 Library 至少需要 5 个 output eval cases，并覆盖 file-backed、near-neighbor 和 boundary case。</p></div>
    </section>

    <section id="runtime" class="twocol">
      <div class="panel"><h2>运行矩阵</h2><p>{html.escape(str(conformance_summary))}</p></div>
      <div class="panel"><h2>上下文</h2><p>{html.escape(gates[3]['detail'])}</p></div>
    </section>

    <section id="trust" class="twocol">
      <div class="panel"><h2>信任报告</h2><p>{html.escape(str(trust_summary))}</p></div>
      <div class="panel"><h2>安全边界</h2><p>高风险 secret、远程 inline execution、缺失依赖策略或无法解释的脚本接口应阻断 governed release。</p></div>
    </section>

    <section id="atlas" class="twocol">
      <div class="panel"><h2>组合治理</h2><p>{html.escape(gates[6]['detail'])}</p></div>
      <div class="panel"><h2>下一动作</h2><p>优先处理真实 portfolio 中的 duplicate names、stale skills、owner gaps，再做 registry 或 telemetry。</p></div>
    </section>

    <section id="release" class="twocol">
      <div class="panel"><h2>发布路线</h2><p>{html.escape(gates[7]['detail'])}</p></div>
      <div class="panel"><h2>世界级缺口</h2><p>下一阶段应继续推进 IR-first compiler、registry audit、telemetry drift loop，以及更严格的 governed trust gates。</p></div>
    </section>
  </main>
</body>
</html>
"""


def render_review_studio(skill_dir: Path, output_html: Path | None = None, output_json: Path | None = None) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_html = output_html or reports_dir / "review-studio.html"
    output_json = output_json or reports_dir / "review-studio.json"
    data = load_review_data(skill_dir)
    gates = build_gates(skill_dir, output_html, data)
    blockers, warnings = add_blockers_from_gate(gates)
    score = weighted_score(gates)
    decision = "blocked" if blockers else ("review" if warnings else "ready")
    report = {
        "schema_version": "2.0",
        "ok": True,
        "skill_dir": display_path(skill_dir, skill_dir),
        "summary": {
            "decision": decision,
            "world_class_score": score,
            "gate_count": len(gates),
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
        },
        "gates": gates,
        "blockers": blockers,
        "warnings": warnings,
        "evidence_paths": evidence_paths(skill_dir),
        "data": data,
        "artifacts": {
            "html": display_path(skill_dir, output_html),
            "json": display_path(skill_dir, output_json),
        },
    }
    output_html.write_text(render_html(report), encoding="utf-8")
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {key: value for key, value in report.items() if key != "data"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Review Studio 2.0 for a skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--output-html")
    parser.add_argument("--output-json")
    args = parser.parse_args()
    payload = render_review_studio(
        Path(args.skill_dir),
        output_html=Path(args.output_html).resolve() if args.output_html else None,
        output_json=Path(args.output_json).resolve() if args.output_json else None,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Check a draft against an Anlin stylometric ratio profile.

This script reports corpus-prior drift. It is not an authorship detector and
does not replace blind review or deterministic hard-rule checks.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from build_style_profile import build_profile, extract_document


DEFAULT_CONTINUOUS_FEATURES = {
    "body_chars": "length",
    "body_lines": "length",
    "paragraph_blocks": "structure",
    "title_chars": "title",
    "line_mean_chars": "line_rhythm",
    "line_stdev_chars": "line_rhythm",
    "short_line_ratio": "line_rhythm",
    "long_line_ratio": "line_rhythm",
}

SUGGESTIONS = {
    "length": "Match the chosen evaluation mode: expand through lived action, dialogue, body, money, or social consequence rather than padding.",
    "structure": "Repair structure by changing scene movement, not by adding a decorative paragraph.",
    "title": "Weaken diagnostic or clever title behavior; for standard blind evaluation, plain 日寄 is often safer.",
    "line_rhythm": "Change rhythm through action, speech, body interruption, or thought turns; do not create a visible short-line grid.",
    "ngram_texture": "Inspect repeated local templates and n-gram reuse; replace repeated scaffolds with different actions, objects, or social turns.",
    "punctuation": "Repair punctuation drift through natural spoken/thought continuation, not punctuation sprinkling.",
    "connectors": "Remove explanatory glue and let scenes jump by object, body, app surface, or another person's line.",
    "texture": "Adjust lived texture through necessary body, screen, money, route, object, or social consequence; do not add decorative tags.",
    "cognitive_mechanism": "Repair thinking movement inside existing scenes: concrete entry, crooked read, reality puncture, defensive recovery, or retreat.",
    "ai_slop": "Replace the explanatory scaffold with the physical fact, body consequence, app surface, money action, or plain dialogue.",
    "other": "Inspect this signal manually against placebo originals before treating it as decisive.",
}

TOPIC_SENSITIVE_SOFT_ONLY_FAMILIES = {"structure", "texture", "cognitive_mechanism", "title"}
YELLOW_REVIEW_FAMILY_THRESHOLD = 5
SOFT_REVISE_FAMILY_THRESHOLD = 10


def calibrate_level_for_family(family: str, level: str) -> str:
    if level == "red" and family in TOPIC_SENSITIVE_SOFT_ONLY_FAMILIES:
        return "yellow"
    return level


@dataclass(frozen=True)
class ProfileFinding:
    severity: str
    family: str
    metric: str
    observed: float
    expected: str
    rule: str
    suggestion: str
    level: str = "yellow"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def beta_binomial_log_pmf(k: int, n: int, alpha: float, beta: float) -> float:
    return (
        math.lgamma(n + 1)
        - math.lgamma(k + 1)
        - math.lgamma(n - k + 1)
        + math.lgamma(k + alpha)
        + math.lgamma(n - k + beta)
        - math.lgamma(n + alpha + beta)
        + math.lgamma(alpha + beta)
        - math.lgamma(alpha)
        - math.lgamma(beta)
    )


def beta_binomial_interval(n: int, alpha: float, beta: float, low: float = 0.05, high: float = 0.95) -> tuple[int, int]:
    if n <= 0:
        return 0, 0
    logs = [beta_binomial_log_pmf(k, n, alpha, beta) for k in range(n + 1)]
    maximum = max(logs)
    weights = [math.exp(value - maximum) for value in logs]
    total = sum(weights)
    cumulative = 0.0
    lower = 0
    upper = n
    lower_set = False
    for index, weight in enumerate(weights):
        cumulative += weight / total
        if not lower_set and cumulative >= low:
            lower = index
            lower_set = True
        if cumulative >= high:
            upper = index
            break
    return lower, upper


def robust_z(observed: float, summary: dict[str, float]) -> float:
    mad = summary.get("mad", 0.0)
    if mad <= 0:
        return 0.0
    return 0.6745 * (observed - summary.get("median", observed)) / mad


def continuous_findings(document: Any, profile: dict[str, Any], include_info: bool) -> list[ProfileFinding]:
    findings: list[ProfileFinding] = []
    summaries = profile.get("value_summary", {})
    value_families = profile.get("value_families") or DEFAULT_CONTINUOUS_FEATURES
    for metric, family in sorted(value_families.items()):
        if metric not in summaries:
            continue
        observed = float(document.values.get(metric, 0.0))
        summary = summaries[metric]
        q05 = float(summary.get("q05", 0.0))
        q10 = float(summary.get("q10", 0.0))
        q90 = float(summary.get("q90", 0.0))
        q95 = float(summary.get("q95", 0.0))
        severity = ""
        rule = ""
        level = "yellow"
        z_value = robust_z(observed, summary)
        min_value = float(summary.get("min", q05))
        max_value = float(summary.get("max", q95))
        if observed < min_value or observed > max_value or abs(z_value) >= 7.0:
            severity = "warning"
            level = "red"
            if observed < min_value or observed > max_value:
                rule = "outside corpus observed min-max"
            else:
                rule = "robust z-score strong drift"
        elif observed < q05 or observed > q95:
            severity = "warning"
            level = "yellow"
            rule = "outside corpus q05-q95"
        elif include_info and (observed < q10 or observed > q90):
            severity = "info"
            rule = "outside corpus q10-q90"
        if severity:
            level = calibrate_level_for_family(family, level)
            findings.append(
                ProfileFinding(
                    severity=severity,
                    family=family,
                    metric=metric,
                    observed=observed,
                    expected=f"q10-q90={q10:.3f}..{q90:.3f}; q05-q95={q05:.3f}..{q95:.3f}; robust_z={z_value:.2f}",
                    rule=rule,
                    suggestion=SUGGESTIONS.get(family, SUGGESTIONS["other"]),
                    level=level,
                )
            )
    return findings


def predictive_findings(
    document: Any,
    profile: dict[str, Any],
    include_info: bool,
    draft_gate: bool,
) -> list[ProfileFinding]:
    findings: list[ProfileFinding] = []
    count_summary = profile.get("count_summary", {})
    for metric, summary in sorted(count_summary.items()):
        if metric not in document.counts:
            continue
        observed = int(document.counts.get(metric, 0))
        denominator = int(document.denominators.get(metric, 0))
        family = str(summary.get("family", "other"))
        if denominator <= 0:
            continue

        if draft_gate and summary.get("hard_generated") and observed > 0:
            findings.append(
                ProfileFinding(
                    severity="error",
                    family=family,
                    metric=metric,
                    observed=float(observed),
                    expected="0 in generated-draft gate",
                    rule="generated draft hard gate",
                    suggestion=SUGGESTIONS[family],
                    level="red",
                )
            )
            continue

        alpha = float(summary.get("alpha", 1.0))
        beta = float(summary.get("beta", 1.0))
        p01, p99 = beta_binomial_interval(denominator, alpha, beta, 0.01, 0.99)
        p05, p95 = beta_binomial_interval(denominator, alpha, beta, 0.05, 0.95)
        p10, p90 = beta_binomial_interval(denominator, alpha, beta, 0.10, 0.90)
        severity = ""
        rule = ""
        if observed < p01 or observed > p99:
            severity = "warning"
            level = "red"
            rule = "outside posterior predictive 98% central interval"
        elif observed < p05 or observed > p95:
            severity = "warning"
            level = "yellow"
            rule = "outside posterior predictive 90% central interval"
        elif include_info and (observed < p10 or observed > p90):
            severity = "info"
            level = "yellow"
            rule = "outside posterior predictive 80% central interval"
        else:
            level = "green"

        if severity:
            per_1k = observed / denominator * 1000 if denominator else 0.0
            level = calibrate_level_for_family(family, level)
            findings.append(
                ProfileFinding(
                    severity=severity,
                    family=family,
                    metric=metric,
                    observed=float(observed),
                    expected=f"count80={p10}..{p90}; count90={p05}..{p95}; count98={p01}..{p99}; observed_per_1k={per_1k:.3f}",
                    rule=rule,
                    suggestion=SUGGESTIONS.get(family, SUGGESTIONS["other"]),
                    level=level,
                )
            )
    return findings


def summarize_status(findings: list[ProfileFinding]) -> dict[str, Any]:
    errors = [finding for finding in findings if finding.severity == "error"]
    red_findings = [finding for finding in findings if finding.level == "red" and finding.severity != "error"]
    yellow_findings = [finding for finding in findings if finding.level == "yellow" and finding.severity != "error"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    warning_families = sorted({finding.family for finding in warnings})
    error_families = sorted({finding.family for finding in errors})
    red_families = sorted({finding.family for finding in red_findings})
    yellow_families = sorted(({finding.family for finding in yellow_findings} | {finding.family for finding in warnings}) - set(red_families))
    if errors:
        status = "revise"
    elif len(red_families) >= 3:
        status = "revise"
    elif len(set(red_families) | set(yellow_families)) >= SOFT_REVISE_FAMILY_THRESHOLD:
        status = "revise"
    elif red_families or yellow_families:
        status = "yellow"
    else:
        status = "green"
    return {
        "status": status,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "red_count": len(red_findings),
        "yellow_count": len(yellow_findings),
        "warning_families": warning_families,
        "error_families": error_families,
        "red_families": red_families,
        "yellow_families": yellow_families,
        "yellow_review_threshold": YELLOW_REVIEW_FAMILY_THRESHOLD,
        "soft_revise_threshold": SOFT_REVISE_FAMILY_THRESHOLD,
        "decision_rule": "revise on any hard error, three independent red drift families, or soft family drift beyond original-calibrated threshold; five yellow/red families require strong manual review",
        "principle": "Profile drift is evidence for revision, not proof of authorship or generation.",
    }


def check_draft(draft_path: Path, profile: dict[str, Any], include_info: bool, draft_gate: bool) -> dict[str, Any]:
    document = extract_document(draft_path)
    findings = []
    findings.extend(continuous_findings(document, profile, include_info))
    findings.extend(predictive_findings(document, profile, include_info, draft_gate))
    status = summarize_status(findings)
    return {
        "draft": str(draft_path),
        "profile_version": profile.get("version"),
        "corpus_file_count": profile.get("corpus_file_count"),
        "expected_corpus_count": profile.get("expected_corpus_count"),
        "draft_gate": draft_gate,
        "document": asdict(document),
        "findings": [asdict(finding) for finding in findings],
        "summary": status,
    }


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Anlin style-profile audit",
        f"draft: {report['draft']}",
        f"profile_version: {report['profile_version']}",
        f"corpus_file_count: {report['corpus_file_count']}",
        f"draft_gate: {report['draft_gate']}",
        f"status: {report['summary']['status']}",
        f"errors: {report['summary']['error_count']}",
        f"warnings: {report['summary']['warning_count']}",
        f"red_families: {', '.join(report['summary']['red_families']) or '(none)'}",
        f"yellow_families: {', '.join(report['summary']['yellow_families']) or '(none)'}",
        f"warning_families: {', '.join(report['summary']['warning_families']) or '(none)'}",
        f"error_families: {', '.join(report['summary']['error_families']) or '(none)'}",
        "findings:",
    ]
    if not report["findings"]:
        lines.append("  - (none)")
    for item in report["findings"]:
        lines.append(
            "  - "
            f"{item['severity']}:{item.get('level', 'yellow')} | {item['family']} | {item['metric']} | "
            f"observed={item['observed']} | expected={item['expected']} | {item['rule']} | "
            f"{item['suggestion']}"
        )
    lines.append("note: This audit reports corpus-prior drift only; validate with hard gates, blind rounds, and placebo calibration.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a draft against an Anlin stylometric profile.")
    parser.add_argument("draft", type=Path, help="Draft markdown/text file")
    parser.add_argument("--profile", type=Path, default=None, help="Profile JSON produced by build_style_profile.py")
    parser.add_argument("--corpus-dir", type=Path, default=None, help="Build an in-memory profile from this corpus if --profile is omitted")
    parser.add_argument("--draft-gate", action="store_true", help="Apply generated-draft-only hard gates for AI-surface features")
    parser.add_argument("--include-info", action="store_true", help="Include q10-q90 / 80% predictive informational drift")
    parser.add_argument("--strict", action="store_true", help="Return nonzero when profile status is revise, even without hard errors")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.profile:
        profile = read_json(args.profile)
    elif args.corpus_dir:
        profile = build_profile(args.corpus_dir)
    else:
        parser.error("Must provide --profile or --corpus-dir.")

    report = check_draft(args.draft, profile, args.include_info, args.draft_gate)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report(report))

    if report["summary"]["error_count"] > 0:
        return 1
    if args.strict and report["summary"]["status"] == "revise":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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

from build_style_profile import COGNITIVE_PATTERNS, build_profile, extract_document, read_text, split_title_body


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
    "ngram_texture": "Inspect repeated local templates and n-gram reuse; delete one repeated body/object packet and replace its function with a different action, object, or social turn.",
    "punctuation": "Repair punctuation drift through natural spoken/thought continuation, not punctuation sprinkling.",
    "connectors": "Remove explanatory glue and let scenes jump by object, body, app surface, or another person's line.",
    "texture": "Adjust lived texture through consequence: if body/object texture is high, remove repeated proof-detail before adding social, payment, route, reply, or room movement.",
    "cognitive_mechanism": "Repair thinking movement inside existing scenes: concrete entry, crooked read, reality puncture, defensive recovery, or retreat.",
    "ai_slop": "Replace the explanatory scaffold with the physical fact, body consequence, app surface, money action, or plain dialogue.",
    "other": "Inspect this signal manually against placebo originals before treating it as decisive.",
}

TOPIC_SENSITIVE_SOFT_ONLY_FAMILIES = {"structure", "texture", "cognitive_mechanism", "title"}
YELLOW_REVIEW_FAMILY_THRESHOLD = 5
SOFT_REVISE_FAMILY_THRESHOLD = 11
COGNITIVE_CORE_KEYS = [
    "concrete_entry",
    "crooked_interpretation",
    "reality_puncture",
    "defensive_recovery",
    "exit_retreat",
]
COGNITIVE_SUPPORT_KEYS = [
    "associative_hook",
    "humor_friction",
    "emotion_displaced_logistics",
]


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


def select_audit_profile(
    profile: dict[str, Any],
    phase: str | None,
    genre: str | None,
    min_stratum_docs: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    strata = profile.get("strata") or {}
    candidates: list[tuple[str, dict[str, Any] | None]] = []
    if phase and genre:
        candidates.append((f"phase_genre:{phase}/{genre}", (strata.get("phase_genre") or {}).get(f"{phase}/{genre}")))
    if phase:
        candidates.append((f"phase:{phase}", (strata.get("phase") or {}).get(phase)))
    if genre:
        candidates.append((f"genre:{genre}", (strata.get("genre") or {}).get(genre)))

    skipped: list[str] = []
    for scope, candidate in candidates:
        if not candidate:
            skipped.append(f"{scope}: missing")
            continue
        count = int(candidate.get("document_count", 0))
        if count < min_stratum_docs:
            skipped.append(f"{scope}: document_count={count} < {min_stratum_docs}")
            continue
        selected = dict(profile)
        selected["value_summary"] = candidate.get("value_summary", {})
        selected["value_families"] = candidate.get("value_families", {})
        selected["count_summary"] = candidate.get("count_summary", {})
        return selected, {
            "scope": scope,
            "document_count": count,
            "requested_phase": phase,
            "requested_genre": genre,
            "fallback": False,
            "skipped": skipped,
        }

    return profile, {
        "scope": "global",
        "document_count": profile.get("corpus_file_count"),
        "requested_phase": phase,
        "requested_genre": genre,
        "fallback": bool(candidates),
        "skipped": skipped,
    }


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
    independent_drift_families = sorted(set(red_families) | set(yellow_families))
    if errors:
        status = "revise"
    elif len(red_families) >= 3:
        status = "revise"
    elif len(independent_drift_families) >= SOFT_REVISE_FAMILY_THRESHOLD:
        status = "revise"
    elif len(independent_drift_families) >= YELLOW_REVIEW_FAMILY_THRESHOLD:
        status = "review"
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
        "independent_drift_families": independent_drift_families,
        "independent_drift_family_count": len(independent_drift_families),
        "yellow_review_threshold": YELLOW_REVIEW_FAMILY_THRESHOLD,
        "soft_revise_threshold": SOFT_REVISE_FAMILY_THRESHOLD,
        "decision_rule": "revise on any hard error, three independent red drift families, or soft family drift beyond original-calibrated upper bound; five independent yellow/red families require strong manual review and placebo comparison",
        "principle": "Profile drift is evidence for revision, not proof of authorship or generation.",
    }


def first_hit_line(lines: list[str], pattern: str) -> int | None:
    import re

    compiled = re.compile(pattern, re.IGNORECASE)
    for index, line in enumerate(lines, start=1):
        if compiled.search(line):
            return index
    return None


def ordered_pair_score(positions: dict[str, int | None], keys: list[str]) -> dict[str, Any]:
    pairs = []
    matched = 0
    possible = 0
    for left, right in zip(keys, keys[1:]):
        left_position = positions.get(left)
        right_position = positions.get(right)
        if left_position is None or right_position is None:
            pairs.append({"pair": f"{left}->{right}", "status": "missing", "left": left_position, "right": right_position})
            continue
        possible += 1
        if left_position <= right_position:
            matched += 1
            pair_status = "ordered"
        else:
            pair_status = "reversed"
        pairs.append({"pair": f"{left}->{right}", "status": pair_status, "left": left_position, "right": right_position})
    return {
        "matched_ordered_pairs": matched,
        "possible_pairs": possible,
        "pairs": pairs,
    }


def cognitive_audit(document: Any, draft_path: Path | None = None) -> dict[str, Any]:
    core = {
        key: int(document.counts.get(f"cognitive_{key}", 0))
        for key in COGNITIVE_CORE_KEYS
    }
    support = {
        key: int(document.counts.get(f"cognitive_{key}", 0))
        for key in COGNITIVE_SUPPORT_KEYS
    }
    abstract_labels = int(document.counts.get("cognitive_abstract_emotion_label", 0))
    core_present = [key for key, count in core.items() if count > 0]
    support_present = [key for key, count in support.items() if count > 0]
    score = len(core_present) + min(len(support_present), 2)
    if abstract_labels >= 3:
        score -= 1
    status = "green" if score >= 5 and len(core_present) >= 4 else "yellow" if score >= 3 else "red"
    line_positions: dict[str, int | None] = {}
    order_score: dict[str, Any] = {"matched_ordered_pairs": 0, "possible_pairs": 0, "pairs": []}
    if draft_path is not None:
        _, body, body_lines = split_title_body(read_text(draft_path))
        _ = body
        line_positions = {
            key: first_hit_line(body_lines, COGNITIVE_PATTERNS[key])
            for key in COGNITIVE_CORE_KEYS + COGNITIVE_SUPPORT_KEYS
            if key in COGNITIVE_PATTERNS
        }
        order_score = ordered_pair_score(line_positions, COGNITIVE_CORE_KEYS)
    missing_core = [key for key in COGNITIVE_CORE_KEYS if key not in core_present]
    missing_support = [key for key in COGNITIVE_SUPPORT_KEYS if key not in support_present]
    return {
        "status": status,
        "score": max(score, 0),
        "max_score": 7,
        "core_counts": core,
        "support_counts": support,
        "present_core": core_present,
        "missing_core": missing_core,
        "present_support": support_present,
        "missing_support": missing_support,
        "first_hit_lines": line_positions,
        "order_score": order_score,
        "abstract_emotion_label_count": abstract_labels,
        "repair_rule": "If core links are missing, change how existing scenes move: concrete object -> crooked read -> reality puncture -> defensive recovery -> exit. Do not insert labels to raise counts.",
        "principle": "Soft cognitive audit only: repair by changing how existing scenes think, not by inserting labels.",
    }


def cognitive_findings(audit: dict[str, Any], draft_gate: bool) -> list[ProfileFinding]:
    if not draft_gate or audit.get("status") != "red":
        return []
    return [
        ProfileFinding(
            severity="warning",
            family="cognitive_mechanism",
            metric="cognitive_audit_core",
            observed=float(audit.get("score", 0)),
            expected="soft score >=3 and at least partial concrete/crooked/puncture/recovery/exit movement",
            rule=f"missing_core={audit.get('missing_core', [])}",
            suggestion=SUGGESTIONS["cognitive_mechanism"],
            level="yellow",
        )
    ]


def check_draft(
    draft_path: Path,
    profile: dict[str, Any],
    include_info: bool,
    draft_gate: bool,
    phase: str | None = None,
    genre: str | None = None,
    min_stratum_docs: int = 4,
) -> dict[str, Any]:
    document = extract_document(draft_path)
    audit_profile, profile_scope = select_audit_profile(profile, phase, genre, min_stratum_docs)
    findings = []
    findings.extend(continuous_findings(document, audit_profile, include_info))
    findings.extend(predictive_findings(document, audit_profile, include_info, draft_gate))
    cognitive = cognitive_audit(document, draft_path)
    findings.extend(cognitive_findings(cognitive, draft_gate))
    status = summarize_status(findings)
    return {
        "draft": str(draft_path),
        "profile_version": profile.get("version"),
        "corpus_file_count": profile.get("corpus_file_count"),
        "expected_corpus_count": profile.get("expected_corpus_count"),
        "profile_scope": profile_scope,
        "draft_gate": draft_gate,
        "document": asdict(document),
        "cognitive_audit": cognitive,
        "findings": [asdict(finding) for finding in findings],
        "summary": status,
    }


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Anlin style-profile audit",
        f"draft: {report['draft']}",
        f"profile_version: {report['profile_version']}",
        f"corpus_file_count: {report['corpus_file_count']}",
        f"profile_scope: {json.dumps(report['profile_scope'], ensure_ascii=False)}",
        f"draft_gate: {report['draft_gate']}",
        f"status: {report['summary']['status']}",
        f"errors: {report['summary']['error_count']}",
        f"warnings: {report['summary']['warning_count']}",
        f"red_families: {', '.join(report['summary']['red_families']) or '(none)'}",
        f"yellow_families: {', '.join(report['summary']['yellow_families']) or '(none)'}",
        f"cognitive_audit: {json.dumps(report['cognitive_audit'], ensure_ascii=False)}",
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
    parser.add_argument("--phase", default=None, help="Optional corpus phase for stratified audit, e.g. A/B/C/D")
    parser.add_argument("--genre", default=None, help="Optional genre for stratified audit, e.g. standard/sincere/micro-hope/surreal")
    parser.add_argument("--min-stratum-docs", type=int, default=4, help="Minimum documents required before using a phase/genre stratum")
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

    report = check_draft(
        args.draft,
        profile,
        args.include_info,
        args.draft_gate,
        phase=args.phase,
        genre=args.genre,
        min_stratum_docs=args.min_stratum_docs,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report(report))

    if report["summary"]["error_count"] > 0:
        return 1
    if args.strict and report["summary"]["status"] in {"review", "revise"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

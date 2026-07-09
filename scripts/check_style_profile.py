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

REPAIR_BRIEF_ACTIONS = {
    "length": "change length only through lived action, a failed exchange, body cost, money, route, or social consequence; do not pad.",
    "structure": "change scene movement: cut designed prompt echoes, opening-tail loops, or decorative off-axis material before adding anything.",
    "title": "retitle from the earned side action or weak handle; do not use a diagnostic prompt label.",
    "line_rhythm": "shape first: rebuild the visible body as 6-8 line-broken clusters, not a handful of prose paragraphs or equal sentence rows.",
    "ngram_texture": "delete one repeated local packet or line-start template; replace its function with a different action or social consequence.",
    "punctuation": "let punctuation follow unfinished action/reply/payment/door/body movement; do not globally merge rows or split every sentence.",
    "connectors": "create a turn that naturally needs connection: failed reply, payment handoff, body interruption, route/object change; do not paste connector words.",
    "texture": "remove body/object proof that does not change the next action; replace it with reply, payment, route, room, or social position movement.",
    "cognitive_mechanism": "repair the order of thinking inside scenes; do not insert labels or explain what the scene means.",
    "ai_slop": "replace explanatory scaffold with physical fact, body consequence, app surface, money action, or plain speech.",
    "other": "inspect manually against matched originals; do not treat this as a quota.",
}

REPAIR_FAMILY_ORDER = [
    "ai_slop",
    "punctuation",
    "line_rhythm",
    "connectors",
    "ngram_texture",
    "structure",
    "texture",
    "cognitive_mechanism",
    "length",
    "title",
    "other",
]


def primary_source_rewrite(families: list[str]) -> str:
    family_set = set(families)
    if "ai_slop" in family_set:
        return (
            "rewrite from the local physical fact, not from an explanation. Delete binary reframes, therapeutic "
            "phrases, and meaning-summary sentences first; keep only the hand, reply, payment, door/body, app surface, "
            "or plain speech that makes the next action smaller. Then shape the whole article once and stop."
        )
    if {"punctuation", "line_rhythm"} & family_set:
        return (
            "preserve the scene slate and repair page shape locally: keep the existing title, people, message channel, "
            "refusal facts, body mass, connector turns, and hard-gate-passing consequence. Choose a few existing "
            "action/reply/payment/body rows and reshape their cluster boundaries; micro-edit only inside existing "
            "clusters so some lines continue through real movement, some land with hard stops, and a few short drops "
            "remain earned; preserve working comma-ended continuation rows from the incoming draft, and do not merge "
            "a comma-ended row with its following line into a sealed sentence. do not add a new simile, analogy, or "
            "caption to explain pressure. Do not invent a new group-chat, comment-chain, stranger, route, backstory, "
            "or binary `不是X，是Y` reframe, and do not rewrite the article from a new premise just to change punctuation."
        )
    if {"connectors", "structure"} & family_set:
        return (
            "rebuild one consequence chain so the next action changes by reply, payment, route, body, "
            "door, object, or social position. Do not paste connector words or add a decorative scene."
        )
    if {"texture", "ngram_texture"} & family_set:
        return (
            "delete one repeated proof packet and replace its function with a different practical or "
            "social consequence. Do not thicken the draft with more body, screen, route, money, or object tags."
        )
    if "cognitive_mechanism" in family_set:
        return (
            "change how an existing scene thinks: concrete object -> crooked read -> reality puncture -> "
            "defensive recovery -> practical exit. Do not add abstract labels."
        )
    return "make one source-level rewrite, persist the complete article to draft.md, then stop; the controller reruns formal gates."

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
BUNDLED_PROFILE = Path(__file__).resolve().parents[1] / "references" / "style-profile.json"


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


def resolve_profile(profile_arg: Path | None, corpus_dir: Path | None) -> dict[str, Any]:
    if profile_arg:
        return read_json(profile_arg)
    if corpus_dir:
        return build_profile(corpus_dir)
    if BUNDLED_PROFILE.is_file():
        return read_json(BUNDLED_PROFILE)
    raise FileNotFoundError(
        "Must provide --profile or --corpus-dir; bundled references/style-profile.json was not found."
    )


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
    if status in {"green", "yellow"}:
        checkpoint_decision = "pass"
        checkpoint_pass = True
    elif status == "review":
        checkpoint_decision = "not_pass_review_required"
        checkpoint_pass = False
    else:
        checkpoint_decision = "not_pass_revise"
        checkpoint_pass = False
    if status == "green":
        repair_mode = "none"
        next_repair_action = "No profile repair needed; keep hard-gate, trace, overlap, and blind/placebo validation separate."
    elif status == "yellow":
        repair_mode = "targeted_manual_review"
        next_repair_action = "Review the named drift families against placebo originals; avoid adding rare style features as quotas."
    elif status == "review" and not red_families and len(independent_drift_families) >= YELLOW_REVIEW_FAMILY_THRESHOLD:
        repair_mode = "source_reset_thinning"
        next_repair_action = (
            "Strict hard gate may be clean, but many yellow families mean the article still reads over-shaped. "
            "Do one source-reset/thinning pass: cut repeated body, money, screen, route, and explicit cognition that "
            "does not change action or social position; avoid local punctuation, connector, or line-break chasing."
        )
    elif status == "review" and "line_rhythm" in red_families:
        repair_mode = "rhythm_source_reset"
        next_repair_action = (
            "Reset the rhythm corridor from scene movement: use breathing clusters and real action/speech/thought rows, "
            "then write the complete artifact and stop. Let the controller validate; do not bounce between tiny rows, prose blocks, and comma chains."
        )
    elif status == "review" and "punctuation" in red_families:
        repair_mode = "punctuation_source_reset"
        next_repair_action = (
            "Punctuation is a source-shape problem here, not a comma/period target. Rebuild several breathing clusters "
            "from unfinished action, reply, payment, door/body movement, and short failure drops; do not swing from comma-drag "
            "into one-period-per-row grids or from period grids into huge comma chains."
        )
    elif status == "review":
        repair_mode = "manual_placebo_review"
        next_repair_action = (
            "Use matched-original placebo reading before treating the profile as decisive; if repairing, change scene "
            "function or prompt displacement instead of adding measured markers."
        )
    else:
        repair_mode = "source_rewrite_required"
        next_repair_action = (
            "Profile status is revise. Fix hard/profile red families by changing source structure, rhythm, prompt "
            "displacement, or fact texture before any blind round; do not tune only the metric surface."
        )
    return {
        "status": status,
        "checkpoint_decision": checkpoint_decision,
        "checkpoint_pass": checkpoint_pass,
        "repair_mode": repair_mode,
        "next_repair_action": next_repair_action,
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
        "decision_rule": "checkpoint pass only when status is green/yellow; review is not a finalized checkpoint pass even with zero red families; revise on any hard error, three independent red drift families, or soft family drift beyond original-calibrated upper bound; five independent yellow/red families require strong manual review and placebo comparison",
        "checkpoint_rule": "For finalized checkpoints, require checkpoint_decision=pass plus separate strict hard gate, trace, and corpus/overlap checks as applicable.",
        "principle": "Profile drift is evidence for revision, not proof of authorship or generation.",
    }


NON_STANDARD_GENRES = {"sincere", "micro-hope", "surreal"}


def apply_profile_scope_limits(summary: dict[str, Any], profile_scope: dict[str, Any]) -> dict[str, Any]:
    requested_genre = profile_scope.get("requested_genre")
    fallback = bool(profile_scope.get("fallback"))
    if requested_genre not in NON_STANDARD_GENRES or not fallback or summary.get("error_count", 0) > 0:
        summary["profile_gate_applicable"] = True
        return summary
    limited = dict(summary)
    limited["status"] = "inconclusive"
    limited["checkpoint_decision"] = "profile_inconclusive_fallback"
    limited["checkpoint_pass"] = False
    limited["repair_mode"] = "matched_placebo_required"
    limited["next_repair_action"] = (
        "The requested non-standard genre fell back to global priors. Treat this as review evidence only; use "
        "matched-original placebo reading and do not stretch the draft into standard diary shape to satisfy global ratios."
    )
    limited["profile_gate_applicable"] = False
    limited["decision_rule"] = (
        "Non-standard genre requested but the matching stratum was too small, so the audit fell back to global priors. "
        "Report drift families as review signals, but do not use this profile as a finalized pass/fail gate; rely on hard gates, matched originals, blind rounds, and placebo calibration."
    )
    limited["checkpoint_rule"] = "This profile result is non-blocking because the requested non-standard genre lacks enough corpus documents."
    return limited


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
    status = apply_profile_scope_limits(status, profile_scope)
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
        f"checkpoint_decision: {report['summary']['checkpoint_decision']}",
        f"checkpoint_pass: {str(report['summary']['checkpoint_pass']).lower()}",
        f"formal_gate: {'pass' if report['summary']['checkpoint_pass'] else 'not_pass'}",
        f"repair_mode: {report['summary'].get('repair_mode', 'unknown')}",
        f"next_repair_action: {report['summary'].get('next_repair_action', '')}",
        f"profile_gate_applicable: {str(report['summary'].get('profile_gate_applicable', True)).lower()}",
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
    if not report["summary"]["checkpoint_pass"]:
        lines.append(
            "formal_gate_note: In finalized/formal evaluation this result is unresolved. "
            "Do not call the article clean, stable, ready, or pass until checkpoint_pass=true."
        )
    lines.append("note: This audit reports corpus-prior drift only; validate with hard gates, blind rounds, and placebo calibration.")
    return "\n".join(lines)


def ordered_repair_families(summary: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    families: list[str] = []
    for source in ("error_families", "red_families", "yellow_families", "warning_families"):
        for family in summary.get(source, []):
            if family not in seen:
                families.append(family)
                seen.add(family)
    return sorted(
        families,
        key=lambda family: (
            REPAIR_FAMILY_ORDER.index(family) if family in REPAIR_FAMILY_ORDER else len(REPAIR_FAMILY_ORDER),
            family,
        ),
    )


def format_repair_brief(report: dict[str, Any]) -> str:
    summary = report["summary"]
    document = report.get("document") or {}
    genre = document.get("genre")
    families = ordered_repair_families(summary)
    lines = [
        "Anlin style-profile repair brief",
        f"draft: {report['draft']}",
        "artifact_path: draft.md",
        "artifact_contract: the revised complete article must be written back to draft.md; terminal-only prose does not count.",
        f"status: {summary['status']}",
        f"checkpoint_pass: {str(summary['checkpoint_pass']).lower()}",
        f"formal_gate: {'pass' if summary['checkpoint_pass'] else 'not_pass'}",
        f"repair_mode: {summary.get('repair_mode', 'unknown')}",
        f"root_families: {', '.join(families) or '(none)'}",
        f"next_repair_action: {summary.get('next_repair_action', '')}",
    ]
    if summary["checkpoint_pass"]:
        lines.extend(
            [
                "repair_directive: no profile rewrite is required. Keep hard-gate, overlap, trace, blind, and placebo validation separate.",
                "controller_note: rerun without --repair-brief only when you need the full metric report.",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            "repair_directive: write one complete revised draft.md now, then stop. Do not print the article to terminal only, do not summarize fixes after writing, and do not run post-write gates.",
            "hard_gate_priority: if the preceding hard gate showed blocking findings, the one source rewrite must clear those first; use this profile brief to shape the same move, not to ignore hard-gate roughness or fact failures.",
            "hard_gate_pass_preservation: if the preceding hard gate already passed and this is only a style-profile review, do not clean the draft into a new hard-gate failure. Use micro_cluster_surgery: preserve complete standard-diary mass, natural connector spread, rough/public consequence, mixed comma/hard-stop line endings, and preserve working comma-ended continuation rows from the incoming draft while doing local source surgery; do not add a new simile, analogy, or caption, and do not make line-final comma ratio zero by closing every row with `。`. A repair that introduces `高频词覆盖不足`, `标准日寄句号网格`, a below-900 shrink, or a one-period-per-row surface is worse than the original review.",
            "attempt_contract: use this controller-prepared brief, choose one primary source rewrite, write one complete draft.md, and stop. Do not repair one family at a time. A second write/edit, any repair-agent checker command, post-write gate loop, post-write python -c/Measure-Object/wc counter, Test-Path/Glob/List/source/test/threshold/log search, threshold argument, TODO/checklist panel, or terminal-only final version is invalid controller evidence. If a chat reply is required after writing, output only artifact_written.",
            *(
                [
                    "standard_shape_first: save a titled, line-broken standard diary with roughly 6-8 breathing clusters and a middle corridor. Keep several moving rows that carry hand, reply, payment, body, speech, or thought beyond caption length, plus short failure drops where action actually lands.",
                    "standard_overfill_guard: do not expand beyond the original source mass to satisfy every warning. If the rewrite is trending past about 1250 body Chinese characters, delete repeated proof packets before saving; 140+ rows or a 2000+ character standard repair is usually metric-shaped overfill, not a safer article.",
                    "standard_do_not_save: do not save 8-25 dense prose rows, 70+ equal short rows, a 45-70-line caption grid with 0 real long rows, a comma carpet, a below-900 shrink, a 140+ row overfilled proof ledger, or a draft with only one or two moving long rows.",
                    "standard_preserve_existing: when the incoming standard draft already passed hard gate, preserve its title source, person list, invitation channel, connector spread, rough/public consequence, approximate mass, and existing comma continuations. Preserve working comma-ended continuation rows from the incoming draft when the next row completes the same action or thought. Do micro_cluster_surgery rather than a new premise: Do not add group-chat/comment-chain surfaces, new social witnesses, new route facts, polished simile/caption explanations, or binary `不是X，是Y` lines to solve profile review.",
                    "standard_social_decline_source: for invitation/refusal repairs, use one refusal-coupled consequence that changes hand, reply, payment, route, door, object, body, or social position. Do not add message-order plot glue, group-chat crowd summaries, tidy etiquette settlement, or private wet-room proof as separate fixes.",
                ]
                if genre == "standard"
                else []
            ),
            "exit_note: with --strict --repair-brief, nonzero usually means not passed, not tool failure; revise draft.md from source actions and stop for controller validation.",
            f"primary_source_rewrite: {primary_source_rewrite(families)}",
            "source_action_note: the list below is diagnostic context only. Pick the primary rewrite above; do not make one patch per family.",
            "source_actions:",
        ]
    )
    for family in families[:3]:
        lines.append(f"  - {family}: {REPAIR_BRIEF_ACTIONS.get(family, REPAIR_BRIEF_ACTIONS['other'])}")
    if len(families) > 3:
        lines.append("  - remaining families: ignore during this write unless they are also solved by the same source rewrite; do not chase them one by one.")
    lines.extend(
        [
            "validation_boundary: after writing draft.md, the repair agent stops. The controller reruns strict hard gate and the full style-profile report; if the same or opposite failures bounce, record unresolved repair-path drift instead of sending the same agent into another metric-shaped edit.",
            "controller_note: rerun without --repair-brief for full corpus-prior evidence, calibration, or reporting. The brief is the generator-facing repair interface.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a draft against an Anlin stylometric profile.")
    parser.add_argument("draft", type=Path, help="Draft markdown/text file")
    parser.add_argument(
        "--profile",
        type=Path,
        default=None,
        help="Profile JSON produced by build_style_profile.py; defaults to bundled references/style-profile.json when present",
    )
    parser.add_argument("--corpus-dir", type=Path, default=None, help="Build an in-memory profile from this corpus if --profile is omitted")
    parser.add_argument("--draft-gate", action="store_true", help="Apply generated-draft-only hard gates for AI-surface features")
    parser.add_argument("--phase", default=None, help="Optional corpus phase for stratified audit, e.g. A/B/C/D")
    parser.add_argument("--genre", default=None, help="Optional genre for stratified audit, e.g. standard/sincere/micro-hope/surreal")
    parser.add_argument("--min-stratum-docs", type=int, default=4, help="Minimum documents required before using a phase/genre stratum")
    parser.add_argument("--include-info", action="store_true", help="Include q10-q90 / 80%% predictive informational drift")
    parser.add_argument("--strict", action="store_true", help="Return nonzero when profile status is review or revise, even without hard errors")
    parser.add_argument("--repair-brief", action="store_true", help="Output a compact generator-facing repair brief instead of the full finding list")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    try:
        profile = resolve_profile(args.profile, args.corpus_dir)
    except FileNotFoundError as error:
        parser.error(str(error))

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
    elif args.repair_brief:
        print(format_repair_brief(report))
    else:
        print(format_report(report))

    if report["summary"]["error_count"] > 0:
        return 1
    if args.strict and not report["summary"].get("checkpoint_pass", False):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

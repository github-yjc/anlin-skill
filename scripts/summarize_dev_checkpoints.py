#!/usr/bin/env python3
"""Summarize bounded clean-eval and finalized repair checkpoints.

This is a controller tool. It never proves authorship. It answers a narrower
development question: did the fresh-agent bounded run pass, did ordinary repair
converge later, and which layer should be improved next?
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_anlin_violations.py"
CHECK_PROFILE = ROOT / "scripts" / "check_style_profile.py"
COMPARE_CORPUS = ROOT / "scripts" / "compare_anlin_corpus.py"
CHECK_TRACE = ROOT / "scripts" / "check_clean_eval_trace.py"
DEFAULT_PROFILE = ROOT / "references" / "style-profile.json"
EVALS_JSON = ROOT / "evals" / "evals.json"


@dataclass(frozen=True)
class CommandReport:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class GateSummary:
    status: str
    hard_errors: int = 0
    hard_warnings: int = 0
    style_status: str | None = None
    style_checkpoint_decision: str | None = None
    style_red_families: list[str] | None = None
    style_yellow_families: list[str] | None = None
    trace_errors: int = 0
    trace_warnings: int = 0
    clean_calls: int | None = None
    clean_preflights: int | None = None
    clean_stop_reason: str | None = None
    notes: list[str] | None = None


@dataclass(frozen=True)
class StageAudit:
    name: str
    purpose: str
    draft: str
    audit_draft: str
    status: str
    hard_errors: int
    hard_warnings: int
    style_status: str | None
    style_checkpoint_decision: str | None
    style_red_families: list[str]
    style_yellow_families: list[str]
    notes: list[str]


@dataclass(frozen=True)
class CheckpointReport:
    name: str
    draft: str
    audit_draft: str
    gate: GateSummary
    hard_findings: list[dict[str, Any]]
    style_report: dict[str, Any] | None
    corpus_report: dict[str, Any] | None
    trace_findings: list[dict[str, Any]]
    clean_state: dict[str, Any]
    stage_audits: list[StageAudit]


@dataclass(frozen=True)
class DevelopmentSummary:
    case_dir: str
    bounded: CheckpointReport
    finalized: CheckpointReport | None
    diagnosis: str
    blind_round_readiness: str
    bounded_question: str
    finalized_question: str | None
    bounded_checkpoint_scope: str
    finalized_checkpoint_scope: str | None
    bounded_checkpoint_answer: str
    finalized_checkpoint_answer: str | None
    repair_implication: str
    next_action: str
    principle: str


def run_command(command: list[str]) -> CommandReport:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return CommandReport(command, result.returncode, result.stdout, result.stderr)


def normalize_profile_genre(style: str | None) -> str | None:
    if not style:
        return None
    mapping = {
        "standard-diary": "standard",
        "standard": "standard",
        "sincere": "sincere",
        "micro-hope": "micro-hope",
        "surreal-literary": "surreal",
        "surreal": "surreal",
    }
    return mapping.get(style)


def infer_genre_from_case_dir(case_dir: Path, evals_json: Path = EVALS_JSON) -> str | None:
    """Infer style-profile genre from a controller case directory when possible."""
    try:
        data = json.loads(evals_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    haystack = str(case_dir).replace("\\", "/").lower()
    for item in data.get("evals", []):
        style = normalize_profile_genre(item.get("style"))
        if not style:
            continue
        name = str(item.get("name", "")).lower()
        raw_id = item.get("id")
        id_tokens = []
        if isinstance(raw_id, int):
            id_tokens = [f"eval-{raw_id:02d}", f"eval-{raw_id}-"]
        if name and name in haystack:
            return style
        if any(token in haystack for token in id_tokens):
            return style
    return None


def extract_json(stdout: str) -> Any:
    text = stdout.strip()
    if not text:
        return None
    decoder = json.JSONDecoder()
    starts = sorted(index for index, char in enumerate(text) if char in "[{")
    for start in starts:
        try:
            parsed, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            continue
        if not text[start + end :].strip():
            return parsed
        # Some legacy helpers print a banner before JSON but should not print
        # anything after it. If they do, continue looking for a cleaner root.
    raise json.JSONDecodeError("No JSON object or array found", text, 0)


def read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def stop_lock_path(draft: Path) -> Path:
    digest = hashlib.sha256(str(draft.resolve()).encode("utf-8")).hexdigest()
    return Path(tempfile.gettempdir()) / "anlin-clean-run-locks" / f"{digest}.json"


def load_clean_state(draft: Path) -> dict[str, Any]:
    local = draft.parent / ".anlin-clean-run-state.json"
    for path in (local, stop_lock_path(draft)):
        if not path.exists():
            continue
        try:
            state = read_json_file(path)
        except (OSError, json.JSONDecodeError):
            continue
        if state.get("draft") in {None, str(draft.resolve())} or path == local:
            return state
    return {}


def copy_for_controller(draft: Path, output_root: Path, name: str) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    target = output_root / f"{name}-draft.md"
    shutil.copyfile(draft, target)
    return target


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize_hard_findings(findings: list[dict[str, Any]]) -> tuple[int, int]:
    errors = sum(1 for item in findings if item.get("severity") == "error")
    warnings = sum(1 for item in findings if item.get("severity") == "warning")
    return errors, warnings


def run_hard_gate(draft: Path, corpus_dir: Path | None, genre: str | None = None) -> tuple[list[dict[str, Any]], CommandReport]:
    command = [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"]
    if genre:
        command.extend(["--genre", genre])
    if corpus_dir is not None:
        command.extend(["--corpus-dir", str(corpus_dir)])
    report = run_command(command)
    findings = extract_json(report.stdout)
    if not isinstance(findings, list):
        findings = []
    return findings, report


def run_style_gate(draft: Path, profile: Path | None, phase: str | None, genre: str | None) -> tuple[dict[str, Any] | None, CommandReport | None]:
    if profile is None or not profile.is_file():
        return None, None
    command = [
        sys.executable,
        str(CHECK_PROFILE),
        str(draft),
        "--profile",
        str(profile),
        "--draft-gate",
        "--strict",
        "--json",
    ]
    if phase:
        command.extend(["--phase", phase])
    if genre:
        command.extend(["--genre", genre])
    report = run_command(command)
    parsed = extract_json(report.stdout)
    return parsed if isinstance(parsed, dict) else None, report


def run_corpus_compare(draft: Path, corpus_dir: Path | None) -> tuple[dict[str, Any] | None, CommandReport | None]:
    if corpus_dir is None:
        return None, None
    command = [sys.executable, str(COMPARE_CORPUS), str(draft), "--corpus-dir", str(corpus_dir), "--json"]
    report = run_command(command)
    parsed = extract_json(report.stdout)
    return parsed if isinstance(parsed, dict) else None, report


def run_trace_gate(trace_log: Path | None) -> tuple[list[dict[str, Any]], CommandReport | None]:
    if trace_log is None:
        return [], None
    command = [sys.executable, str(CHECK_TRACE), str(trace_log), "--json"]
    report = run_command(command)
    parsed = extract_json(report.stdout)
    return parsed if isinstance(parsed, list) else [], report


def style_status(style_report: dict[str, Any] | None) -> str | None:
    if not style_report:
        return None
    summary = style_report.get("summary") or {}
    return summary.get("status")


def summarize_gate(
    *,
    hard_findings: list[dict[str, Any]],
    style_report: dict[str, Any] | None,
    trace_findings: list[dict[str, Any]],
    clean_state: dict[str, Any],
    bounded: bool,
) -> GateSummary:
    hard_errors, hard_warnings = summarize_hard_findings(hard_findings)
    trace_errors = sum(1 for item in trace_findings if item.get("severity") == "error")
    trace_warnings = sum(1 for item in trace_findings if item.get("severity") == "warning")
    clean_calls = int(clean_state.get("calls", 0)) if clean_state else None
    clean_preflights = int(clean_state.get("preflights", 0)) if clean_state else None
    clean_stop_reason = clean_state.get("stop_reason")
    summary = style_report.get("summary") if style_report else {}
    profile_status = summary.get("status") if isinstance(summary, dict) else None
    profile_decision = summary.get("checkpoint_decision") if isinstance(summary, dict) else None
    red_families = summary.get("red_families", []) if isinstance(summary, dict) else []
    yellow_families = summary.get("yellow_families", []) if isinstance(summary, dict) else []
    notes: list[str] = []

    if bounded:
        if trace_errors:
            notes.append("clean-eval trace contamination detected")
        if clean_calls is None:
            notes.append("missing clean-run state; confirm the bounded generator used clean_run_checker.py")
        elif clean_calls > 2:
            notes.append("clean-run checker call count exceeded two")
        if clean_stop_reason == "preflight":
            notes.append("bounded run stopped before a checker-ready article")

    if trace_errors or (bounded and clean_calls is not None and clean_calls > 2):
        status = "invalid"
    elif bounded and clean_stop_reason == "preflight":
        status = "invalid"
    elif hard_errors:
        status = "fail"
    elif profile_status == "revise":
        status = "fail"
    elif profile_status == "review":
        status = "review"
    elif profile_status == "inconclusive":
        status = "review"
        notes.append("style-profile gate is inconclusive for the requested phase/genre; use hard gates and blind/placebo review before treating this checkpoint as clean")
    elif bounded and clean_calls is None:
        status = "review"
    elif profile_status is None:
        status = "review"
        notes.append("style-profile audit unavailable")
    else:
        status = "pass"

    return GateSummary(
        status=status,
        hard_errors=hard_errors,
        hard_warnings=hard_warnings,
        style_status=profile_status,
        style_checkpoint_decision=profile_decision,
        style_red_families=list(red_families),
        style_yellow_families=list(yellow_families),
        trace_errors=trace_errors,
        trace_warnings=trace_warnings,
        clean_calls=clean_calls,
        clean_preflights=clean_preflights,
        clean_stop_reason=clean_stop_reason,
        notes=notes,
    )


STAGE_PURPOSES = {
    "first_submission": "natural first draft before checker feedback; this is the source-guidance signal",
    "checker_call_1_submission": "draft admitted to the first clean-eval checker call",
    "checker_call_2_submission": "draft after the limited checker-driven repair, submitted to the second call",
    "bounded_final": "frozen bounded result after preflight stop or two-call checker boundary",
}


def snapshot_candidates(clean_state: dict[str, Any]) -> list[tuple[str, Path]]:
    snapshots = clean_state.get("snapshots") if isinstance(clean_state, dict) else None
    if not isinstance(snapshots, dict):
        return []
    ordered: list[tuple[str, Path]] = []
    for key in (
        "first_submission",
        "checker_call_1_submission",
        "checker_call_2_submission",
        "bounded_final",
    ):
        value = snapshots.get(key)
        if not value:
            continue
        path = Path(str(value))
        if path.is_file():
            ordered.append((key, path))
    return ordered


def stage_status_for(hard_errors: int, style_report: dict[str, Any] | None) -> tuple[str, str | None, str | None, list[str], list[str], list[str]]:
    summary = style_report.get("summary") if style_report else {}
    profile_status = summary.get("status") if isinstance(summary, dict) else None
    profile_decision = summary.get("checkpoint_decision") if isinstance(summary, dict) else None
    red_families = summary.get("red_families", []) if isinstance(summary, dict) else []
    yellow_families = summary.get("yellow_families", []) if isinstance(summary, dict) else []
    notes: list[str] = []
    if hard_errors:
        status = "fail"
    elif profile_status == "revise":
        status = "fail"
    elif profile_status == "review":
        status = "review"
    elif profile_status == "inconclusive":
        status = "review"
        notes.append("style-profile gate is inconclusive for the requested phase/genre")
    elif profile_status is None:
        status = "review"
        notes.append("style-profile audit unavailable")
    else:
        status = "pass"
    return status, profile_status, profile_decision, list(red_families), list(yellow_families), notes


def build_stage_audits(
    *,
    clean_state: dict[str, Any],
    audit_root: Path,
    corpus_dir: Path | None,
    profile: Path | None,
    phase: str | None,
    genre: str | None,
) -> list[StageAudit]:
    audits: list[StageAudit] = []
    seen: set[Path] = set()
    for key, path in snapshot_candidates(clean_state):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        audit_draft = copy_for_controller(resolved, audit_root, f"stage-{key}")
        hard_findings, _hard_command = run_hard_gate(audit_draft, corpus_dir, genre)
        hard_errors, hard_warnings = summarize_hard_findings(hard_findings)
        style_report_data, _style_command = run_style_gate(audit_draft, profile, phase, genre)
        status, profile_status, profile_decision, red_families, yellow_families, notes = stage_status_for(hard_errors, style_report_data)
        audits.append(
            StageAudit(
                name=key,
                purpose=STAGE_PURPOSES.get(key, "bounded clean-eval stage snapshot"),
                draft=str(resolved),
                audit_draft=str(audit_draft),
                status=status,
                hard_errors=hard_errors,
                hard_warnings=hard_warnings,
                style_status=profile_status,
                style_checkpoint_decision=profile_decision,
                style_red_families=red_families,
                style_yellow_families=yellow_families,
                notes=notes,
            )
        )
    return audits


def classify_development_result(bounded_status: str, finalized_status: str | None) -> tuple[str, str]:
    bounded_good = bounded_status == "pass"
    bounded_usable = bounded_status in {"pass", "review"}
    finalized_good = finalized_status == "pass"

    if finalized_status is None:
        if bounded_good:
            return (
                "bounded_pass_finalized_missing",
                "Run the finalized repair checkpoint or proceed only if this was an explicitly bounded-only smoke test.",
            )
        if bounded_usable:
            return (
                "bounded_review_finalized_missing",
                "Run finalized repair before deciding whether the issue is source guidance or repair convergence.",
            )
        return (
            "bounded_fail_finalized_missing",
            "Create a separate finalized directory and test whether ordinary repair can recover before changing only the checker.",
        )

    if bounded_good and finalized_good:
        return (
            "ready_for_blind_rounds",
            "Both checkpoints pass. Move to isolated blind rounds with placebo calibration before reporting recognition rates.",
        )
    if not bounded_good and finalized_good:
        return (
            "source_guidance_gap",
            "Finalized repair cleanly passes, so improve Layer 0/Layer 1 generation guidance before adding more detector rules.",
        )
    if bounded_good and not finalized_good:
        return (
            "repair_or_validator_gap",
            "Bounded output was acceptable but finalized repair did not cleanly pass; inspect ordinary repair instructions, profile thresholds, and validator setup.",
        )
    if not bounded_usable and finalized_status == "review":
        return (
            "systemic_gap",
            "Finalized repair is still review-only, so do not treat this as a source-guidance-only result. Inspect generation, repair, profile drift, and checker assumptions.",
        )
    if not bounded_usable and not finalized_good:
        return (
            "systemic_gap",
            "Both checkpoints failed. Inspect architecture across generation, fact gates, repair references, checker, and blind-review assumptions.",
        )
    if bounded_usable and not finalized_good:
        return (
            "repair_path_gap",
            "Natural guidance reached at least review status but ordinary repair did not cleanly pass; constrain repair loops and avoid metric-chasing edits.",
        )
    return (
        "mixed_review",
        "At least one checkpoint is review-only. Use manual review and placebo-calibrated blind evidence before claiming progress.",
    )


def blind_round_readiness(diagnosis: str) -> str:
    if diagnosis == "ready_for_blind_rounds":
        return "ready_for_blind_rounds"
    return "not_ready_for_blind_rounds"


def bounded_answer(checkpoint: CheckpointReport) -> str:
    gate = checkpoint.gate
    calls = "unknown" if gate.clean_calls is None else str(gate.clean_calls)
    preflights = "unknown" if gate.clean_preflights is None else str(gate.clean_preflights)
    first_audit = next((item for item in checkpoint.stage_audits if item.name == "first_submission"), None)
    first_status = first_audit.status if first_audit else "not recorded"
    if gate.clean_stop_reason == "preflight" and gate.clean_calls == 0:
        boundary = (
            "It stopped at preflight before formal checker call 1/2, so this is source/preflight evidence, "
            "not evidence that the two actual checker corrections were tested."
        )
    elif gate.clean_stop_reason == "missing_draft":
        boundary = (
            "It never persisted a draft.md artifact, so neither preflight nor the two-call checker boundary was tested. "
            "Visible terminal prose or reasoning is an execution/protocol failure, not a reviewable article."
        )
    elif gate.clean_calls == 2:
        boundary = "It reached the two-call checker boundary, so limited checker-driven repair was tested."
    elif gate.clean_calls == 1:
        boundary = "It reached only checker call 1/2, so limited checker repair evidence is partial."
    else:
        boundary = "Checker-boundary evidence is incomplete; inspect trace and clean-run state."
    return (
        f"Natural-guidance checkpoint: first-submission snapshot is {first_status}; bounded clean-eval checkpoint is {gate.status} "
        f"after {calls}/2 actual clean-eval checker calls and {preflights} preflight attempt(s). "
        f"{boundary} This separates source guidance from the frozen two-call checker boundary."
    )


def finalized_answer(checkpoint: CheckpointReport | None) -> str | None:
    if checkpoint is None:
        return None
    gate = checkpoint.gate
    return (
        f"Finalized-repair checkpoint is {gate.status} under strict hard-gate plus style-profile validation. "
        "Only `pass` means the final article is clean enough to attribute the remaining gap mainly to source guidance."
    )


def bounded_scope() -> str:
    return (
        "Fresh generator, realistic prompt, normal access to this skill, bounded preflight, and at most two actual "
        "clean-eval checker calls. This measures source guidance plus limited checker-driven repair, not final polish."
    )


def finalized_scope(has_finalized: bool) -> str | None:
    if not has_finalized:
        return None
    return (
        "Copied bounded draft in a separate finalized directory, ordinary multi-round repair, then strict hard-gate "
        "and style-profile validation. This measures repair convergence and cannot retroactively improve bounded status."
    )


def implication_for(diagnosis: str) -> str:
    if diagnosis == "ready_for_blind_rounds":
        return "Both checkpoints are clean; proceed to isolated blind rounds and placebo calibration before reporting rates."
    if diagnosis == "source_guidance_gap":
        return "The final article can converge, so strengthen the first-draft source loop and natural guidance; do not only tune the checker."
    if diagnosis == "systemic_gap":
        return "The final article is not clean, so broaden diagnosis across source guidance, repair references, fact gates, style profile, and checker design."
    if diagnosis in {"repair_path_gap", "repair_or_validator_gap"}:
        return "The repair/final-validation path is suspect; inspect repair instructions, metric-chasing behavior, and validator thresholds before changing generation."
    if diagnosis.endswith("_finalized_missing"):
        return "The bounded result alone is incomplete evidence; run the finalized repair checkpoint before deciding what to change."
    return "The result is mixed or review-only; do not claim progress until the unresolved checkpoint is diagnosed."


def build_checkpoint(
    *,
    name: str,
    draft: Path,
    audit_root: Path,
    bounded: bool,
    corpus_dir: Path | None,
    profile: Path | None,
    phase: str | None,
    genre: str | None,
    trace_log: Path | None,
) -> CheckpointReport:
    draft = draft.resolve()
    audit_draft = copy_for_controller(draft, audit_root, name)
    hard_findings, _hard_command = run_hard_gate(audit_draft, corpus_dir, genre)
    style_report_data, _style_command = run_style_gate(audit_draft, profile, phase, genre)
    corpus_report_data, _corpus_command = run_corpus_compare(audit_draft, corpus_dir)
    trace_findings, _trace_command = run_trace_gate(trace_log if bounded else None)
    clean_state = load_clean_state(draft) if bounded else {}
    stage_audits = (
        build_stage_audits(
            clean_state=clean_state,
            audit_root=audit_root,
            corpus_dir=corpus_dir,
            profile=profile,
            phase=phase,
            genre=genre,
        )
        if bounded
        else []
    )
    gate = summarize_gate(
        hard_findings=hard_findings,
        style_report=style_report_data,
        trace_findings=trace_findings,
        clean_state=clean_state,
        bounded=bounded,
    )
    return CheckpointReport(
        name=name,
        draft=str(draft),
        audit_draft=str(audit_draft),
        gate=gate,
        hard_findings=hard_findings,
        style_report=style_report_data,
        corpus_report=corpus_report_data,
        trace_findings=trace_findings,
        clean_state=clean_state,
        stage_audits=stage_audits,
    )


def build_missing_draft_checkpoint(
    *,
    name: str,
    draft: Path,
    audit_root: Path,
    bounded: bool,
    trace_log: Path | None,
) -> CheckpointReport:
    audit_root.mkdir(parents=True, exist_ok=True)
    audit_draft = audit_root / f"{name}-draft-missing.md"
    audit_draft.write_text(
        "\n".join(
            [
                "# Missing Draft Artifact",
                "",
                f"Expected draft path: {draft}",
                "The generation run did not persist a draft.md artifact, so hard-gate, style-profile, corpus, and blind-review checks cannot be run for this checkpoint.",
            ]
        ),
        encoding="utf-8",
    )
    trace_findings, _trace_command = run_trace_gate(trace_log if bounded else None)
    trace_errors = sum(1 for item in trace_findings if item.get("severity") == "error")
    trace_warnings = sum(1 for item in trace_findings if item.get("severity") == "warning")
    notes = [
        "draft.md artifact missing; visible terminal prose or reasoning does not count as a bounded clean-eval draft",
    ]
    if bounded:
        notes.append("bounded run never reached persisted draft/checker checkpoint")
    gate = GateSummary(
        status="invalid",
        hard_errors=0,
        hard_warnings=0,
        style_status=None,
        style_checkpoint_decision=None,
        style_red_families=[],
        style_yellow_families=[],
        trace_errors=trace_errors,
        trace_warnings=trace_warnings,
        clean_calls=None,
        clean_preflights=None,
        clean_stop_reason="missing_draft",
        notes=notes,
    )
    return CheckpointReport(
        name=name,
        draft=str(draft),
        audit_draft=str(audit_draft),
        gate=gate,
        hard_findings=[],
        style_report=None,
        corpus_report=None,
        trace_findings=trace_findings,
        clean_state={},
        stage_audits=[],
    )


def flag_unchanged_finalized_artifact(
    *,
    bounded: CheckpointReport,
    finalized: CheckpointReport,
) -> CheckpointReport:
    """Mark finalized repair as invalid when the artifact was never updated.

    A common agent failure is printing a repaired article in the terminal while
    leaving finalized/draft.md identical to the bounded input. That cannot count
    as ordinary repair convergence.
    """
    bounded_path = Path(bounded.draft)
    finalized_path = Path(finalized.draft)
    try:
        unchanged = file_sha256(bounded_path) == file_sha256(finalized_path)
    except OSError:
        return finalized
    if not unchanged or bounded.gate.status == "pass":
        return finalized
    notes = list(finalized.gate.notes or [])
    notes.append(
        "finalized draft unchanged from bounded input after a non-pass bounded checkpoint; printed-only repairs do not count"
    )
    updated_gate = replace(
        finalized.gate,
        status="invalid",
        notes=notes,
    )
    return replace(finalized, gate=updated_gate)


def format_markdown(report: DevelopmentSummary) -> str:
    lines = [
        "# Development Checkpoint Summary",
        "",
        f"- case_dir: `{report.case_dir}`",
        f"- diagnosis: `{report.diagnosis}`",
        f"- blind_round_readiness: `{report.blind_round_readiness}`",
        f"- bounded_question: {report.bounded_question}",
        f"- finalized_question: {report.finalized_question or 'not run'}",
        f"- bounded_checkpoint_scope: {report.bounded_checkpoint_scope}",
        f"- finalized_checkpoint_scope: {report.finalized_checkpoint_scope or 'not run'}",
        f"- bounded_checkpoint_answer: {report.bounded_checkpoint_answer}",
        f"- finalized_checkpoint_answer: {report.finalized_checkpoint_answer or 'not run'}",
        f"- repair_implication: {report.repair_implication}",
        f"- next_action: {report.next_action}",
        f"- principle: {report.principle}",
        "",
        "## Bounded Clean-Eval",
        format_gate(report.bounded),
    ]
    if report.finalized:
        lines.extend(["", "## Finalized Repair", format_gate(report.finalized)])
    return "\n".join(lines) + "\n"


def format_gate(checkpoint: CheckpointReport) -> str:
    gate = checkpoint.gate
    notes = "; ".join(gate.notes or []) or "none"
    red = ", ".join(gate.style_red_families or []) or "none"
    yellow = ", ".join(gate.style_yellow_families or []) or "none"
    lines = [
        f"- draft: `{checkpoint.draft}`",
        f"- audit_draft: `{checkpoint.audit_draft}`",
        f"- status: `{gate.status}`",
        f"- hard_errors: {gate.hard_errors}",
        f"- hard_warnings: {gate.hard_warnings}",
        f"- style_status: `{gate.style_status}`",
        f"- style_checkpoint_decision: `{gate.style_checkpoint_decision}`",
        f"- style_red_families: {red}",
        f"- style_yellow_families: {yellow}",
        f"- trace_errors: {gate.trace_errors}",
        f"- clean_calls: {gate.clean_calls}",
        f"- clean_preflights: {gate.clean_preflights}",
        f"- clean_stop_reason: `{gate.clean_stop_reason}`",
        f"- notes: {notes}",
    ]
    if checkpoint.stage_audits:
        lines.append("- stage_audits:")
        for audit in checkpoint.stage_audits:
            stage_red = ", ".join(audit.style_red_families) or "none"
            stage_yellow = ", ".join(audit.style_yellow_families) or "none"
            lines.append(
                f"  - `{audit.name}`: status={audit.status}, hard_errors={audit.hard_errors}, "
                f"style_status={audit.style_status}, style_checkpoint_decision={audit.style_checkpoint_decision}, "
                f"red={stage_red}, yellow={stage_yellow}"
            )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize anlin-writing two-checkpoint development evaluation.")
    parser.add_argument("case_dir", type=Path, help="External case workspace, not the skill directory")
    parser.add_argument("--bounded-draft", type=Path, default=None, help="Bounded clean-eval draft path")
    parser.add_argument("--finalized-draft", type=Path, default=None, help="Finalized repair draft path")
    parser.add_argument("--trace-log", type=Path, default=None, help="Captured bounded generation log for check_clean_eval_trace.py")
    parser.add_argument("--corpus-dir", type=Path, default=None, help="Optional full original corpus directory")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE, help="style-profile.json path")
    parser.add_argument("--phase", default=None, help="Optional phase for style profile")
    parser.add_argument("--genre", default=None, help="Optional genre for style profile; inferred from eval case directory when omitted")
    parser.add_argument("--output-json", type=Path, default=None, help="Write full JSON summary")
    parser.add_argument("--output-md", type=Path, default=None, help="Write markdown summary")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown")
    args = parser.parse_args()

    case_dir = args.case_dir.resolve()
    bounded_draft = (args.bounded_draft or (case_dir / "draft.md")).resolve()
    finalized_draft = args.finalized_draft.resolve() if args.finalized_draft else None
    if finalized_draft is not None and not finalized_draft.is_file():
        parser.error(f"finalized draft not found: {finalized_draft}")

    audit_root = case_dir / "controller-audit"
    effective_genre = args.genre or infer_genre_from_case_dir(case_dir)

    if bounded_draft.is_file():
        bounded = build_checkpoint(
            name="bounded",
            draft=bounded_draft,
            audit_root=audit_root,
            bounded=True,
            corpus_dir=args.corpus_dir,
            profile=args.profile,
            phase=args.phase,
            genre=effective_genre,
            trace_log=args.trace_log,
        )
    else:
        bounded = build_missing_draft_checkpoint(
            name="bounded",
            draft=bounded_draft,
            audit_root=audit_root,
            bounded=True,
            trace_log=args.trace_log,
        )
    finalized = None
    if finalized_draft is not None:
        finalized = build_checkpoint(
            name="finalized",
            draft=finalized_draft,
            audit_root=audit_root,
            bounded=False,
            corpus_dir=args.corpus_dir,
            profile=args.profile,
            phase=args.phase,
            genre=effective_genre,
            trace_log=None,
        )
        finalized = flag_unchanged_finalized_artifact(bounded=bounded, finalized=finalized)

    diagnosis, next_action = classify_development_result(
        bounded.gate.status,
        finalized.gate.status if finalized else None,
    )
    summary = DevelopmentSummary(
        case_dir=str(case_dir),
        bounded=bounded,
        finalized=finalized,
        diagnosis=diagnosis,
        blind_round_readiness=blind_round_readiness(diagnosis),
        bounded_question="Did the skill naturally guide a fresh generator to a checker-ready article, and what happened by the two-call clean-eval boundary?",
        finalized_question=(
            "Can ordinary multi-round repair converge under strict hard-gate and style-profile validation?"
            if finalized
            else None
        ),
        bounded_checkpoint_scope=bounded_scope(),
        finalized_checkpoint_scope=finalized_scope(finalized is not None),
        bounded_checkpoint_answer=bounded_answer(bounded),
        finalized_checkpoint_answer=finalized_answer(finalized),
        repair_implication=implication_for(diagnosis),
        next_action=next_action,
        principle="Bounded checkpoint measures natural guidance; finalized checkpoint measures repair convergence. Do not merge the scores.",
    )
    payload = asdict(summary)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown = format_markdown(summary)
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(markdown, encoding="utf-8")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(markdown)
    return 0 if summary.blind_round_readiness == "ready_for_blind_rounds" else 1


if __name__ == "__main__":
    raise SystemExit(main())

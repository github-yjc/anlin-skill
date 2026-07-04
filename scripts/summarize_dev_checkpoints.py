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
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_anlin_violations.py"
CHECK_PROFILE = ROOT / "scripts" / "check_style_profile.py"
COMPARE_CORPUS = ROOT / "scripts" / "compare_anlin_corpus.py"
CHECK_TRACE = ROOT / "scripts" / "check_clean_eval_trace.py"
DEFAULT_PROFILE = ROOT / "references" / "style-profile.json"


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
    style_red_families: list[str] | None = None
    style_yellow_families: list[str] | None = None
    trace_errors: int = 0
    trace_warnings: int = 0
    clean_calls: int | None = None
    clean_preflights: int | None = None
    clean_stop_reason: str | None = None
    notes: list[str] | None = None


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


@dataclass(frozen=True)
class DevelopmentSummary:
    case_dir: str
    bounded: CheckpointReport
    finalized: CheckpointReport | None
    diagnosis: str
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


def summarize_hard_findings(findings: list[dict[str, Any]]) -> tuple[int, int]:
    errors = sum(1 for item in findings if item.get("severity") == "error")
    warnings = sum(1 for item in findings if item.get("severity") == "warning")
    return errors, warnings


def run_hard_gate(draft: Path, corpus_dir: Path | None) -> tuple[list[dict[str, Any]], CommandReport]:
    command = [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"]
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
        style_red_families=list(red_families),
        style_yellow_families=list(yellow_families),
        trace_errors=trace_errors,
        trace_warnings=trace_warnings,
        clean_calls=clean_calls,
        clean_preflights=clean_preflights,
        clean_stop_reason=clean_stop_reason,
        notes=notes,
    )


def classify_development_result(bounded_status: str, finalized_status: str | None) -> tuple[str, str]:
    bounded_good = bounded_status == "pass"
    bounded_usable = bounded_status in {"pass", "review"}
    finalized_good = finalized_status == "pass"
    finalized_usable = finalized_status in {"pass", "review"}

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
            "Final repair can recover, so improve Layer 0/Layer 1 generation guidance before adding more detector rules.",
        )
    if bounded_good and not finalized_usable:
        return (
            "repair_or_validator_gap",
            "Bounded output was acceptable but final repair failed; inspect ordinary repair instructions, profile thresholds, and validator setup.",
        )
    if not bounded_usable and not finalized_usable:
        return (
            "systemic_gap",
            "Both checkpoints failed. Inspect architecture across generation, fact gates, repair references, checker, and blind-review assumptions.",
        )
    if bounded_usable and not finalized_usable:
        return (
            "repair_path_gap",
            "Natural guidance reached review status but ordinary repair worsened or failed; constrain repair loops and avoid metric-chasing edits.",
        )
    if not bounded_usable and finalized_usable:
        return (
            "source_guidance_gap",
            "The bounded run did not naturally reach review status, but repair did; strengthen first-draft guidance and keep the checker path.",
        )
    return (
        "mixed_review",
        "At least one checkpoint is review-only. Use manual review and placebo-calibrated blind evidence before claiming progress.",
    )


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
    hard_findings, _hard_command = run_hard_gate(audit_draft, corpus_dir)
    style_report_data, _style_command = run_style_gate(audit_draft, profile, phase, genre)
    corpus_report_data, _corpus_command = run_corpus_compare(audit_draft, corpus_dir)
    trace_findings, _trace_command = run_trace_gate(trace_log if bounded else None)
    clean_state = load_clean_state(draft) if bounded else {}
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
    )


def format_markdown(report: DevelopmentSummary) -> str:
    lines = [
        "# Development Checkpoint Summary",
        "",
        f"- case_dir: `{report.case_dir}`",
        f"- diagnosis: `{report.diagnosis}`",
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
    return "\n".join(
        [
            f"- draft: `{checkpoint.draft}`",
            f"- audit_draft: `{checkpoint.audit_draft}`",
            f"- status: `{gate.status}`",
            f"- hard_errors: {gate.hard_errors}",
            f"- hard_warnings: {gate.hard_warnings}",
            f"- style_status: `{gate.style_status}`",
            f"- style_red_families: {red}",
            f"- style_yellow_families: {yellow}",
            f"- trace_errors: {gate.trace_errors}",
            f"- clean_calls: {gate.clean_calls}",
            f"- clean_preflights: {gate.clean_preflights}",
            f"- clean_stop_reason: `{gate.clean_stop_reason}`",
            f"- notes: {notes}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize anlin-writing two-checkpoint development evaluation.")
    parser.add_argument("case_dir", type=Path, help="External case workspace, not the skill directory")
    parser.add_argument("--bounded-draft", type=Path, default=None, help="Bounded clean-eval draft path")
    parser.add_argument("--finalized-draft", type=Path, default=None, help="Finalized repair draft path")
    parser.add_argument("--trace-log", type=Path, default=None, help="Captured bounded generation log for check_clean_eval_trace.py")
    parser.add_argument("--corpus-dir", type=Path, default=None, help="Optional full original corpus directory")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE, help="style-profile.json path")
    parser.add_argument("--phase", default=None, help="Optional phase for style profile")
    parser.add_argument("--genre", default=None, help="Optional genre for style profile")
    parser.add_argument("--output-json", type=Path, default=None, help="Write full JSON summary")
    parser.add_argument("--output-md", type=Path, default=None, help="Write markdown summary")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown")
    args = parser.parse_args()

    case_dir = args.case_dir.resolve()
    bounded_draft = (args.bounded_draft or (case_dir / "draft.md")).resolve()
    if not bounded_draft.is_file():
        parser.error(f"bounded draft not found: {bounded_draft}")
    finalized_draft = args.finalized_draft.resolve() if args.finalized_draft else None
    if finalized_draft is not None and not finalized_draft.is_file():
        parser.error(f"finalized draft not found: {finalized_draft}")

    audit_root = case_dir / "controller-audit"
    bounded = build_checkpoint(
        name="bounded",
        draft=bounded_draft,
        audit_root=audit_root,
        bounded=True,
        corpus_dir=args.corpus_dir,
        profile=args.profile,
        phase=args.phase,
        genre=args.genre,
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
            genre=args.genre,
            trace_log=None,
        )

    diagnosis, next_action = classify_development_result(
        bounded.gate.status,
        finalized.gate.status if finalized else None,
    )
    summary = DevelopmentSummary(
        case_dir=str(case_dir),
        bounded=bounded,
        finalized=finalized,
        diagnosis=diagnosis,
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
    return 1 if diagnosis in {"systemic_gap", "repair_or_validator_gap", "repair_path_gap"} else 0


if __name__ == "__main__":
    raise SystemExit(main())

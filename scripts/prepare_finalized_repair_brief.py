#!/usr/bin/env python3
"""Prepare the artifact-only finalized repair brief.

This is a controller helper. It runs deterministic gates before the repair
agent starts, then writes a compact `repair-brief.txt` beside `draft.md`.
The repairing agent should read that file and `draft.md`, write one complete
revised `draft.md`, and stop; it should not run these gates itself.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_anlin_violations.py"
CHECK_PROFILE = ROOT / "scripts" / "check_style_profile.py"
VALID_GENRES = ("standard", "sincere", "micro-hope", "surreal")


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def run_command(command: list[str], cwd: Path) -> CommandResult:
    result = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return CommandResult(command, result.returncode, result.stdout, result.stderr)


def parse_hard_findings(stdout: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def hard_status(findings: list[dict[str, Any]]) -> str:
    return "not_pass" if any(item.get("severity") == "error" for item in findings) else "pass"


OVERFULL_SHAPE_RULES = {
    "标准日寄完整文章过满",
    "标准日寄行数缓冲异常",
    "断裂过碎",
}

PERIOD_GRID_RULES = {
    "标准日寄句号网格",
    "行末逗号比例",
}

POLISHED_CAPTION_RULES = {
    "字幕式明喻解释",
}

SOCIAL_DECLINE_RULES = {
    "社交拒绝纹理替代后果不足",
    "社交拒绝普通回复假后果",
    "社交拒绝群聊假后果",
    "社交拒绝礼貌闭合",
}


def hard_rule_name(item: dict[str, Any]) -> str:
    rule = str(item.get("rule", "unknown")).strip()
    if rule.startswith("strict: "):
        return rule.removeprefix("strict: ").strip()
    return rule


def hard_blocker_priority(item: dict[str, Any]) -> tuple[int, str]:
    rule_name = hard_rule_name(item)
    if rule_name in OVERFULL_SHAPE_RULES:
        return (0, rule_name)
    if rule_name in SOCIAL_DECLINE_RULES:
        return (1, rule_name)
    if rule_name in PERIOD_GRID_RULES:
        return (2, rule_name)
    if rule_name in POLISHED_CAPTION_RULES:
        return (3, rule_name)
    if "AI" in rule_name or "解释句式" in rule_name or "治疗式" in rule_name:
        return (4, rule_name)
    return (5, rule_name)


def compact_hard_blockers(findings: list[dict[str, Any]], limit: int = 5) -> list[str]:
    blockers = [
        item
        for item in findings
        if item.get("severity") == "error"
    ] or [
        item
        for item in findings
        if item.get("severity") == "warning"
    ]
    blockers = sorted(blockers, key=hard_blocker_priority)
    lines: list[str] = []
    for item in blockers[:limit]:
        rule = str(item.get("rule", "unknown")).strip()
        suggestion = str(item.get("suggestion", "")).strip()
        excerpt = str(item.get("excerpt", "")).strip()
        parts = [rule]
        if excerpt:
            parts.append(excerpt[:120])
        if suggestion:
            parts.append(suggestion[:180])
        lines.append(" | ".join(parts))
    return lines


def hard_gate_primary_action(findings: list[dict[str, Any]]) -> str:
    error_rules = {hard_rule_name(item) for item in findings if item.get("severity") == "error"}
    if error_rules & OVERFULL_SHAPE_RULES:
        return (
            "delete_and_merge_overfull_standard: first remove repeated proof packets, decorative explanations, "
            "duplicate body/object/screen evidence, and low-consequence memory ledgers; then merge adjacent caption rows "
            "into fewer rough action/speech/thought lines. Aim the single rewrite toward a compact complete standard diary "
            "near 45-70 visible body lines and roughly 950-1250 body Chinese characters. Do not add new scenes while this "
            "overfull/fragmented hard gate is present. Do not solve it by making every row a closed sentence: keep several "
            "unfinished action/reply/body lines ending with a comma, and delete polished simile captions instead of "
            "turning them into shorter explanatory sentences."
        )
    if error_rules & SOCIAL_DECLINE_RULES:
        return (
            "rebuild_refusal_aftermath_engine: the social refusal must become the source engine, not a topic beside "
            "room/screen/water texture. Remove one private room/object proof packet, keep at most one cropped message "
            "surface, and make the post-refusal reply, payment, route, old debt, dirty/wet hand, door/body interruption, "
            "or one plain person asking change the next visible action. The same rebuild should create uneven breathing "
            "clusters: one unfinished reply/payment/body line may trail with a comma, one rough longer row carries the "
            "awkward movement, and one short drop lands the lower answer. Do not solve this by shortening the article "
            "into a summary; keep a complete standard-diary corridor with visible breathing clusters and roughly 950-1150 "
            "body Chinese characters by replacing the deleted packet with a refusal-coupled consequence cluster. Do not save "
            "a 650-899 shrink, and do not save a 900-949 underbuilt boundary draft when engine, roughness, or connector "
            "spread is still weak. The replacement cluster must create rough self-damage or paragraph-engine movement, "
            "not more private wet/body texture. Do not fix this by adding group-chat crowd pressure, tidy etiquette closure, "
            "more ticket/suili ledger, or more water-room texture."
        )
    if error_rules & PERIOD_GRID_RULES:
        return (
            "break_period_grid: rebuild several rows as unfinished action, reply, payment, door/body, or app-surface "
            "movement. Keep some lines open with commas and some short hard stops; do not convert every line into a neat "
            "complete sentence."
        )
    if error_rules & POLISHED_CAPTION_RULES:
        return (
            "delete_polished_caption: remove caption-like similes and feeling subtitles. Keep the object, payment, body, "
            "reply, or social consequence; do not replace the simile with another explanation."
        )
    if any(rule in error_rules for rule in ("AI二元解释句式", "AI治疗式人类化")):
        return (
            "delete_ai_scaffold_first: remove binary reframes, therapeutic phrases, and meaning-summary sentences; "
            "replace them with the existing physical fact, body consequence, app surface, money action, or plain speech."
        )
    if error_rules:
        return "clear_hard_gate_first: make one source-level rewrite that clears the listed hard blockers before considering profile drift."
    return "no_hard_gate_primary_action: use the compact style brief only if profile repair is still required."


def build_profile_command(
    draft_name: str,
    *,
    genre: str,
    profile: Path | None,
    corpus_dir: Path | None,
) -> list[str]:
    command = [
        sys.executable,
        str(CHECK_PROFILE),
        draft_name,
        "--draft-gate",
        "--strict",
        "--repair-brief",
        "--genre",
        genre,
    ]
    if profile is not None:
        command.extend(["--profile", str(profile)])
    if corpus_dir is not None:
        command.extend(["--corpus-dir", str(corpus_dir)])
    return command


def build_hard_command(
    draft_name: str,
    *,
    genre: str,
    corpus_dir: Path | None,
) -> list[str]:
    command = [
        sys.executable,
        str(CHECKER),
        draft_name,
        "--json",
        "--strict",
        "--draft-gate",
        "--genre",
        genre,
    ]
    if corpus_dir is not None:
        command.extend(["--corpus-dir", str(corpus_dir)])
    return command


def format_brief(
    *,
    draft: Path,
    genre: str,
    hard_findings: list[dict[str, Any]],
    profile_result: CommandResult,
) -> str:
    hard_blockers = compact_hard_blockers(hard_findings)
    profile_brief = profile_result.stdout.strip()
    if not profile_brief:
        profile_brief = (
            "Anlin style-profile repair brief\n"
            "status: unavailable\n"
            "checkpoint_pass: false\n"
            "formal_gate: not_pass\n"
            "repair_mode: controller_tool_error\n"
            "next_repair_action: the controller could not produce a style repair brief; use the hard-gate blockers and finalized minimum, then write one complete draft.md."
        )

    lines = [
        "Anlin finalized repair brief",
        "producer: controller",
        f"selected_genre: {genre}",
        "artifact_path: draft.md",
        "first_action_contract: read draft.md and this brief, make the source decision privately, then the first write to draft.md must be the final complete revised article, not a placeholder copy or unchanged draft; after that write, stop.",
        "read_contract: repair agent reads only draft.md and repair-brief.txt unless the user supplied other visible case facts.",
        "write_contract: exactly one artifact mutation is the repair: write one complete revised draft.md, then stop; copying the current draft back unchanged and then rewriting is invalid, and terminal-only prose or planning does not count.",
        "tool_boundary: do not run check_anlin_violations.py, check_style_profile.py, clean_run_checker.py, prepare_finalized_repair_brief.py, python -c, Measure-Object, wc, local counters, Test-Path, Glob/List, source/test/threshold/log searches, or path probes during the repair attempt.",
        "genre_boundary: do not invent unsupported genre labels; use selected_genre exactly as written here.",
        f"hard_gate_status: {hard_status(hard_findings)}",
        f"hard_gate_primary_action: {hard_gate_primary_action(hard_findings)}",
        "hard_gate_blockers:",
    ]
    if hard_blockers:
        lines.extend(f"  - {line}" for line in hard_blockers)
    else:
        lines.append("  - (none)")
    lines.extend(
        [
            "style_repair_brief:",
            profile_brief,
            "controller_boundary: after the single write, the controller reruns strict hard gate and full style-profile reports. The repair agent does not validate the frozen artifact.",
        ]
    )
    if draft.name != "draft.md":
        lines.append(f"controller_warning: expected finalized artifact name draft.md, received {draft.name}.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare repair-brief.txt for artifact-only finalized repair.")
    parser.add_argument("draft", type=Path, help="Finalized draft path, normally finalized/draft.md")
    parser.add_argument("--genre", required=True, choices=VALID_GENRES, help="Frozen validation genre")
    parser.add_argument("--profile", type=Path, default=None, help="Optional style-profile.json override")
    parser.add_argument("--corpus-dir", type=Path, default=None, help="Optional full corpus directory for hard overlap/profile rebuild")
    parser.add_argument("--output", type=Path, default=None, help="Output brief path; defaults to draft parent repair-brief.txt")
    parser.add_argument("--json", action="store_true", help="Print a controller JSON summary instead of the brief text")
    args = parser.parse_args()

    draft = args.draft.resolve()
    if not draft.is_file():
        parser.error(f"draft not found: {draft}")
    output = args.output.resolve() if args.output else draft.parent / "repair-brief.txt"
    profile = args.profile.resolve() if args.profile is not None else None
    corpus_dir = args.corpus_dir.resolve() if args.corpus_dir is not None else None

    hard_result = run_command(
        build_hard_command(draft.name, genre=args.genre, corpus_dir=corpus_dir),
        cwd=draft.parent,
    )
    hard_findings = parse_hard_findings(hard_result.stdout)
    profile_result = run_command(
        build_profile_command(draft.name, genre=args.genre, profile=profile, corpus_dir=corpus_dir),
        cwd=draft.parent,
    )
    brief = format_brief(
        draft=draft,
        genre=args.genre,
        hard_findings=hard_findings,
        profile_result=profile_result,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(brief, encoding="utf-8")

    payload = {
        "draft": str(draft),
        "output": str(output),
        "selected_genre": args.genre,
        "hard_gate_status": hard_status(hard_findings),
        "hard_gate_returncode": hard_result.returncode,
        "profile_returncode": profile_result.returncode,
        "repair_required": hard_status(hard_findings) != "pass" or profile_result.returncode != 0,
        "hard_blocker_count": sum(1 for item in hard_findings if item.get("severity") == "error"),
        "note": "Nonzero hard/profile gate return codes mean the draft needs repair; the brief was still generated for the repair agent.",
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(brief)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

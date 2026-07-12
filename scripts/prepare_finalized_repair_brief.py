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

from check_anlin_violations import chinese_len, split_title_and_content_lines


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_anlin_violations.py"
CHECK_PROFILE = ROOT / "scripts" / "check_style_profile.py"
VALID_GENRES = ("standard", "sincere", "micro-hope", "surreal")
COMPACT_REVIEW_MODES = {
    "punctuation_source_reset": "punctuation",
}
PROFILE_STATUS_REPAIR_MODES = {
    "green": {"none"},
    "yellow": {"targeted_manual_review"},
    "review": {
        "source_reset_thinning",
        "rhythm_source_reset",
        "punctuation_source_reset",
        "manual_placebo_review",
    },
    "revise": {"source_rewrite_required"},
    "inconclusive": {"matched_placebo_required"},
}


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


def parse_hard_findings(stdout: str) -> list[dict[str, Any]] | None:
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list):
        return None
    if any(
        not isinstance(item, dict) or item.get("severity") not in {"info", "warning", "error"}
        for item in data
    ):
        return None
    return data


def hard_status(findings: list[dict[str, Any]] | None, *, returncode: int = 0) -> str:
    if findings is None:
        return "controller_tool_error"
    has_errors = any(item.get("severity") == "error" for item in findings)
    if has_errors:
        return "not_pass" if returncode == 1 else "controller_tool_error"
    return "pass" if returncode == 0 else "controller_tool_error"


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

STANDARD_LENGTH_RULES = {
    "标准日寄完整文章篇幅偏短",
    "标准日寄完整文章篇幅缓冲不足",
}

WEAK_SOURCE_RULES = SOCIAL_DECLINE_RULES | {
    "高频词覆盖不足",
    "段落发动机信号偏弱",
    "私密湿脏纹理替代粗粝",
    "标准日寄行数缓冲异常",
    "标准日寄长行缓冲不足",
    "标准日寄短行网格",
    "标准日寄句号网格",
    "行末逗号比例",
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
        if hard_rule_name(item) in STANDARD_LENGTH_RULES:
            suggestion = ""
        parts = [rule]
        if excerpt:
            parts.append(excerpt[:120])
        if suggestion:
            parts.append(suggestion[:180])
        lines.append(" | ".join(parts))
    return lines


def hard_gate_primary_action(findings: list[dict[str, Any]], *, body_chars: int | None = None) -> str:
    error_rules = {hard_rule_name(item) for item in findings if item.get("severity") == "error"}
    if body_chars is not None and 0 < body_chars < 650:
        return (
            "rebuild_severely_underbuilt_fragment: rebuild the incomplete article from its strongest existing fragment relation; "
            "preserve a complete article within the supplied fact boundary and do not append checker-shaped proof material."
        )
    if body_chars is not None and 650 <= body_chars < 900:
        return (
            "replace_underbuilt_fragment: replace the earliest underdeveloped fragment or relation in place; "
            "preserve the article's existing mass and voice, and do not append an independent scene or proof packet."
        )
    if body_chars is not None and 900 <= body_chars < 950 and error_rules & WEAK_SOURCE_RULES:
        return (
            "preserve_boundary_mass_replace_weak_fragment: keep useful existing facts, replace the earliest weak fragment relation "
            "in place, preserve article mass, and do not shrink or append diagnostic material."
        )
    if error_rules & OVERFULL_SHAPE_RULES:
        return (
            "thin_overfull_fragment_slate: remove repeated proof, decorative explanations, duplicate object/screen evidence, "
            "and low-consequence memory ledgers; merge only the rows needed by the affected movement. Do not add a scene or "
            "new material while the overfull/fragmented gate is present, and do not replace the page with a uniform punctuation template."
        )
    if error_rules & SOCIAL_DECLINE_RULES:
        return (
            "repair_refusal_fragment_relation: keep the invitation or refusal as one fragment and replace the earliest broken "
            "relation only when the draft itself makes a local consequence necessary. A reply, route, payment, body, door, or "
            "ordinary person may change the next action, but do not manufacture a group-chat crowd, etiquette settlement, ticket ledger, "
            "or multi-day subplot. Preserve the existing article and do not append a consequence scene."
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


def compact_source_focus(findings: list[dict[str, Any]], *, body_chars: int | None = None) -> str:
    """Turn valid hard-gate findings into one source-level repair focus.

    The controller keeps the full findings in its audit output.  A not-pass
    repair brief must not hand the agent a checklist of metrics: that invites
    packet-by-packet expansion and punctuation chasing.  Route by the most
    consequential source family and keep the remaining families controller-only.
    """

    route = hard_gate_primary_action(findings, body_chars=body_chars).split(":", 1)[0]
    if route == "rebuild_severely_underbuilt_fragment":
        return (
            "rebuild the existing incomplete article from its strongest fragment relation; preserve a complete article and "
            "do not append checker-shaped material"
        )
    if route == "thin_overfull_fragment_slate":
        return (
            "remove repeated proof from the overfull fragment slate and merge only the rows needed by that movement; "
            "do not add material, a new scene, or a new explanation"
        )
    if route == "replace_underbuilt_fragment":
        return (
            "replace the earliest underdeveloped fragment or relation in place while preserving the existing article; "
            "do not append an independent scene or proof packet"
        )
    if route == "preserve_boundary_mass_replace_weak_fragment":
        return (
            "replace the earliest weak fragment relation in place while preserving article mass and useful existing facts; "
            "let the next thought or action change direction without adding a packet"
        )
    if route == "break_period_grid":
        return (
            "repair one existing action/reply/body movement locally so its continuation or landing is earned; "
            "preserve unrelated row endings and do not apply a page-wide comma or period transformation"
        )
    if route == "repair_refusal_fragment_relation":
        return (
            "replace the earliest broken invitation/refusal fragment relation with a local consequence only when the draft earns it; "
            "keep the same visible facts and do not add a new scene, witness, route, or message chain"
        )
    if route == "delete_polished_caption":
        return (
            "delete one caption-like explanation inside the existing movement and keep the underlying object, body, "
            "reply, or payment consequence; do not replace it with another explanation"
        )
    return (
        "replace one existing overloaded movement in place with the smallest source change that alters what happens next; "
        "do not append an independent scene or proof packet"
    )


def compact_source_rewrite_brief(
    *,
    genre: str,
    findings: list[dict[str, Any]],
    body_chars: int | None,
) -> str:
    """Format the single-action interface used for valid hard-gate failures."""

    route = hard_gate_primary_action(findings, body_chars=body_chars).split(":", 1)[0]
    if route == "rebuild_severely_underbuilt_fragment":
        scope_contract = (
            "scope_contract: rebuild the existing incomplete article across its current fragment relations; do not pretend one local "
            "patch is sufficient, do not append a separate scene, and keep every changed fact within the supplied prompt/source boundary."
        )
        mass_contract = (
            "mass_contract: preserve a complete article and the useful existing material; do not save a short summary or fill the gap "
            "with a checker-shaped proof list."
        )
        shape_contract = (
            "shape_contract: write one complete line-broken article with uneven movement; do not apply a page-wide punctuation transform "
            "or use a caption grid to simulate completeness."
        )
    elif route == "thin_overfull_fragment_slate":
        scope_contract = (
            "scope_contract: remove the smallest repeated proof cluster or adjacent caption rows that cause overfill, merging only rows "
            "needed for that existing movement; do not add a scene, witness, route, or explanation."
        )
        mass_contract = (
            "mass_contract: keep the remaining functional article mass close to the incoming artifact; trim repetition without shrinking "
            "the piece into a summary or rebuilding a new premise."
        )
        shape_contract = (
            "shape_contract: preserve the useful line-broken surface and retain mixed row endings; do not close every row with a period "
            "or merge the page into a comma chain."
        )
    else:
        scope_contract = (
            "scope_contract: choose the earliest existing local fragment relation that carries the failed movement and replace it in place; "
            "keep the title and useful visible facts; do not append a new paragraph, scene, or packet."
        )
        mass_contract = (
            "mass_contract: keep the revised article close to the incoming artifact; restore missing movement inside the chosen relation "
            "rather than expanding the article or shrinking it into a summary."
        )
        shape_contract = (
            "shape_contract: preserve the incoming line-broken surface and mixed row endings; repair only the selected movement; "
            "do not globally merge rows, split every sentence, seal every row with a period, and do not apply a page-wide comma or period transformation."
        )
    lines = [
        "Anlin finalized repair brief",
        "producer: controller",
        f"selected_genre: {genre}",
        "artifact_path: draft.md",
        "repair_mode: source_rewrite_compact",
        "hard_gate_status: not_pass",
        "profile_diagnostics: controller_only",
        f"hard_gate_primary_action: {route}",
        f"source_focus: {compact_source_focus(findings, body_chars=body_chars)}",
        "tool_boundary: do not run check_anlin_violations.py, check_style_profile.py, clean_run_checker.py, prepare_finalized_repair_brief.py, local counters, path probes, source/test/threshold/log searches, or controller helpers during the repair attempt.",
        "read_contract: read draft.md and repair-brief.txt only; do not load finalized-repair-minimum.md for this valid compact brief, and do not read checker, source, test, threshold, log, or controller files.",
        scope_contract,
        mass_contract,
        shape_contract,
        "fact_contract: do not invent a new witness, route, backstory, group chat, second message chain, or independent payment ledger; every changed detail must belong to the selected fragment relation.",
        "write_contract: exactly one complete draft.md write, then stop; do not write a placeholder, validate, count, search, or print an alternate article. If a chat reply is required, output only artifact_written.",
        "controller_boundary: after the single write, the controller reruns strict hard gate and full style-profile reports. The repair agent does not validate the frozen artifact.",
    ]
    return "\n".join(lines) + "\n"


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


def profile_brief_field(profile_brief: str, name: str) -> str:
    prefix = f"{name}:"
    for line in profile_brief.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return ""


def profile_result_valid(profile_result: CommandResult) -> bool:
    profile_brief = profile_result.stdout.strip()
    if not profile_brief.startswith("Anlin style-profile repair brief"):
        return False
    status = profile_brief_field(profile_brief, "status")
    repair_mode = profile_brief_field(profile_brief, "repair_mode")
    checkpoint_pass = profile_brief_field(profile_brief, "checkpoint_pass")
    formal_gate = profile_brief_field(profile_brief, "formal_gate")
    if repair_mode not in PROFILE_STATUS_REPAIR_MODES.get(status, set()):
        return False
    if status in {"green", "yellow"} and checkpoint_pass == "true" and formal_gate == "pass":
        return profile_result.returncode == 0
    if status in {"review", "revise", "inconclusive"} and checkpoint_pass == "false" and formal_gate == "not_pass":
        return profile_result.returncode == 1
    return False


def profile_primary_family(profile_brief: str) -> str:
    root_families = profile_brief_field(profile_brief, "root_families")
    if not root_families or root_families == "(none)":
        return "profile_review"
    return root_families.split(",", 1)[0].strip()


def compact_review_selection(profile_brief: str) -> tuple[str, str] | None:
    if profile_brief_field(profile_brief, "status") != "review":
        return None
    if profile_brief_field(profile_brief, "checkpoint_pass") != "false":
        return None
    if profile_brief_field(profile_brief, "formal_gate") != "not_pass":
        return None
    expected_family = COMPACT_REVIEW_MODES.get(profile_brief_field(profile_brief, "repair_mode"))
    if expected_family is None:
        return None
    primary_family = profile_primary_family(profile_brief)
    if primary_family != expected_family:
        return None
    primary_action = profile_primary_action(profile_brief, primary_family)
    return (primary_family, primary_action) if primary_action else None


def profile_primary_action(profile_brief: str, family: str) -> str:
    action_prefix = f"  - {family}:"
    for line in profile_brief.splitlines():
        if line.startswith(action_prefix):
            return line.removeprefix(action_prefix).strip()
    return ""


def read_text_flexible(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def draft_body_chinese_chars(draft: Path) -> int | None:
    try:
        text = read_text_flexible(draft)
    except OSError:
        return None
    _, content_lines = split_title_and_content_lines(text.splitlines())
    body = "\n".join(line for line in content_lines if not line.startswith("<!--"))
    return chinese_len(body)


def compact_edit_ranges(draft: Path) -> tuple[list[tuple[int, int]], tuple[int, int]] | None:
    try:
        lines = read_text_flexible(draft).splitlines()
    except OSError:
        return None
    title_index = next((index for index, line in enumerate(lines) if line.strip()), None)
    if title_index is None:
        return None

    blocks: list[tuple[int, int]] = []
    block_start: int | None = None
    for index in range(title_index + 1, len(lines)):
        if lines[index].strip():
            if block_start is None:
                block_start = index
        elif block_start is not None:
            blocks.append((block_start + 1, index))
            block_start = None
    if block_start is not None:
        blocks.append((block_start + 1, len(lines)))
    if len(blocks) < 2:
        return None

    protected_tail = blocks[-1]
    candidates = [
        block
        for block in blocks[:-1]
        if 4 <= block[1] - block[0] + 1 <= 6
    ]
    return (candidates, protected_tail) if candidates else None


def format_hard_pass_review_brief(
    *,
    genre: str,
    primary_family: str,
    primary_action: str,
    candidate_ranges: list[tuple[int, int]],
    protected_tail: tuple[int, int],
) -> str:
    candidate_text = ", ".join(f"lines {start}-{end}" for start, end in candidate_ranges)
    tail_start, tail_end = protected_tail
    lines = [
        "Anlin finalized repair brief",
        "producer: controller",
        f"selected_genre: {genre}",
        "artifact_path: draft.md",
        "repair_mode: hard_pass_review_in_place",
        "hard_gate_status: pass",
        "profile_status: review",
        f"primary_family: {primary_family}",
        f"primary_action: {primary_action}",
        "secondary_families: controller_only",
        "read_contract: read only draft.md and repair-brief.txt; this brief is self-contained; do not load references/finalized-repair-minimum.md or any other reference, checker, source, test, log, or controller file.",
        f"eligible_cluster_ranges: {candidate_text}",
        "scope_contract: choose exactly one eligible cluster range above; each range is one existing local cluster of 4-6 consecutive nonblank body rows, using the line numbers shown when draft.md is read.",
        "in_place_contract: replace each selected row with exactly one row in the same position; keep total body row count, row order, and every blank-line boundary unchanged.",
        "untouched_contract: preserve every unselected row exactly, including its wording, punctuation, and line ending.",
        "mutation_boundary: do not delete, merge, split, add, or move rows.",
        "replacement_mass_contract: each replacement row must not be visibly shorter than the original row; preserve the local facts and functional consequence.",
        f"protected_tail_range: lines {tail_start}-{tail_end}",
        "tail_definition: the protected tail range above is the final existing nonblank body block and is the loose tail residue for this attempt.",
        "loose_tail_lock: preserve every row in the protected tail range exactly; do not select it for repair or turn it into a stronger ending.",
        "complete_file_contract: persist the whole article to draft.md with only the selected one-to-one row replacements.",
        "write_contract: exactly one complete draft.md write, then stop; do not write a placeholder, patch after writing, validate, or print an alternate article to terminal/chat. If a chat reply is required, output only artifact_written.",
        "controller_boundary: after the single write, the controller reruns strict hard gate and full style-profile reports. The repair agent does not validate the frozen artifact.",
    ]
    return "\n".join(lines) + "\n"


def format_brief(
    *,
    draft: Path,
    genre: str,
    hard_findings: list[dict[str, Any]] | None,
    hard_returncode: int = 0,
    profile_result: CommandResult,
) -> str:
    parsed_hard_findings = hard_findings or []
    hard_gate_state = hard_status(hard_findings, returncode=hard_returncode)
    hard_blockers = compact_hard_blockers(parsed_hard_findings)
    hard_gate_passed = hard_gate_state == "pass"
    body_chars = draft_body_chinese_chars(draft) if genre == "standard" else None
    profile_brief = profile_result.stdout.strip()
    if not profile_result_valid(profile_result):
        profile_brief = (
            "Anlin style-profile repair brief\n"
            "status: unavailable\n"
            "checkpoint_pass: false\n"
            "formal_gate: not_pass\n"
            "repair_mode: controller_tool_error\n"
            "next_repair_action: the controller could not produce a style repair brief; use the hard-gate blockers and finalized minimum, then write one complete draft.md."
        )

    compact_selection = compact_review_selection(profile_brief) if profile_result_valid(profile_result) else None
    compact_ranges = compact_edit_ranges(draft) if compact_selection is not None else None
    if hard_gate_passed and compact_selection is not None and compact_ranges is not None and draft.name == "draft.md":
        compact_primary_family, compact_primary_action = compact_selection
        candidate_ranges, protected_tail = compact_ranges
        return format_hard_pass_review_brief(
            genre=genre,
            primary_family=compact_primary_family,
            primary_action=compact_primary_action,
            candidate_ranges=candidate_ranges,
            protected_tail=protected_tail,
        )

    if hard_gate_state == "not_pass" and draft.name == "draft.md":
        return compact_source_rewrite_brief(
            genre=genre,
            findings=parsed_hard_findings,
            body_chars=body_chars,
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
        f"hard_gate_status: {hard_gate_state}",
        *(
            [
                "hard_gate_pass_preservation: current artifact already passed the strict hard gate. Treat profile repair as micro_cluster_surgery with line_ending_lock and mass_floor_lock, not cleanup. Preserve connector spread, complete body mass, rough/public consequence, existing comma continuations, mixed line endings, and preserve working comma-ended continuation rows from the incoming draft; keep row-ending punctuation and line breaks for untouched rows; do not remove a functional consequence sentence unless you replace it inside the same local cluster; do not rewrite a review artifact into `高频词覆盖不足`, `标准日寄句号网格`, below-900 shrinkage, line-final comma ratio zero, or a one-period-per-row surface; do not add a new simile, analogy, or caption to explain pressure.",
                "hard_gate_pass_primary_action: preserve_and_nudge_review: keep the existing title source, people, invitation channel, message facts, refusal aftermath, connector turns, and approximate article mass. Rewrite the complete artifact only after micro-editing local clusters inside the existing scene; do not introduce a new group chat, comment chain, stranger witness, new route/backstory packet, polished simile/caption explanation, or binary `不是X，是Y` reframe; do not make line-final comma ratio zero by sealing every row with `。`.",
            ]
            if hard_gate_passed and profile_result.returncode != 0
            else []
        ),
        f"hard_gate_primary_action: {hard_gate_primary_action(parsed_hard_findings, body_chars=body_chars)}",
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
    if draft.name != "draft.md":
        parser.error(f"expected finalized artifact name draft.md, received {draft.name}")
    output = args.output.resolve() if args.output else draft.parent / "repair-brief.txt"
    if output == draft:
        parser.error("repair brief output must not overwrite draft.md")
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
        hard_returncode=hard_result.returncode,
        profile_result=profile_result,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(brief, encoding="utf-8")

    payload = {
        "draft": str(draft),
        "output": str(output),
        "selected_genre": args.genre,
        "hard_gate_status": hard_status(hard_findings, returncode=hard_result.returncode),
        "hard_gate_returncode": hard_result.returncode,
        "profile_returncode": profile_result.returncode,
        "profile_result_valid": profile_result_valid(profile_result),
        "repair_required": (
            hard_status(hard_findings, returncode=hard_result.returncode) != "pass"
            or not profile_result_valid(profile_result)
            or profile_result.returncode != 0
        ),
        "hard_blocker_count": sum(1 for item in (hard_findings or []) if item.get("severity") == "error"),
        "note": (
            "Gate return code 1 with a valid result means not passed; invalid output or any other nonzero "
            "controller-tool result is unavailable, not quality evidence. The brief was still generated for fallback repair."
        ),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(brief)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

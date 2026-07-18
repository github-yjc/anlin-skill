#!/usr/bin/env python3
"""Bounded checker wrapper for clean-eval generation.

This wrapper is for generation agents, not external validation. It delegates to
check_anlin_violations.py while recording how many checker calls have been made
for the current draft. After the second call, the next action should be reading
draft.md and outputting it unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_anlin_violations.py"
SPLIT_LONG_LINES = ROOT / "scripts" / "split_long_lines.py"
SOFTEN_LINE_ENDINGS = ROOT / "scripts" / "soften_line_endings.py"
MERGE_SHORT_LINES = ROOT / "scripts" / "merge_short_lines.py"
REBALANCE_LINE_RHYTHM = ROOT / "scripts" / "rebalance_line_rhythm.py"
SNAPSHOT_DIR_NAME = ".anlin-clean-run-snapshots"
PRIVATE_GRIME_TEXTURE_TERMS = [
    "油渍",
    "油印",
    "汤汁",
    "红油",
    "领口",
    "袖口",
    "裤子上也",
    "裤腿",
    "衣服上沾",
    "胡茬",
    "头发塌",
    "鼻翼",
    "眼睛有点肿",
    "镜子里",
    "打了个嗝",
]
sys.path.insert(0, str(ROOT / "scripts"))
from check_anlin_violations import (  # noqa: E402
    AMBIENT_ENDING_PATTERNS,
    BACKGROUND_DISPLAY_GROUPS,
    ENGINE_SIGNAL_PATTERNS,
    ENGINE_SIGNAL_TERMS,
    HIGH_SIGNAL_OPENING_TERMS,
    PROCESS_LEAK_TERMS,
    HIGH_FREQUENCY_TERMS,
    LEARNED_ENDING_LINES,
    ROUGH_SELF_DAMAGE_PATTERNS,
    ROUGH_SELF_DAMAGE_TERMS,
    STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS,
    STANDARD_DIARY_PREFERRED_TARGET_MIN_CHARS,
    STANDARD_DIARY_DRAFT_OVERFULL_CHARS,
    STANDARD_DIARY_FORMAL_MIN_CHARS,
    STANDARD_PROMPT_PROP_TITLE_TERMS,
    chinese_len,
    comment_chain_formula_hits,
    current_office_persona_hits,
    detect_style,
    feed_inventory_opening_hits,
    meta_ai_topic_hits,
    prompt_performing_dialogue_hits,
    short_genre_literary_story_risk,
    short_genre_local_packet_loop_risk,
    short_genre_main_prop_title_loop_risk,
    short_genre_present_action_anchor_risk,
    short_genre_prompt_prop_too_early_risk,
    short_genre_repair_stuffing_groups,
    social_decline_decoupled_consequence_risk,
    social_decline_group_fake_consequence_risk,
    social_decline_plain_reply_private_loop_risk,
    social_decline_tidy_etiquette_closure_risk,
    standard_prompt_prop_title_loop_risk,
    set_forced_genre,
    split_title_and_content_lines,
)


# These are useful controller diagnostics, but they are too weak to stop a
# bounded first draft on their own. A fragment collage can be coherent through
# association, echo, memory, or a direct voice jump without containing the old
# engine vocabulary or a broad connector sampler.
ADVISORY_PREFLIGHT_PREFIXES = (
    "connectors=",
    "paragraph_engine=weak",
    "rough_self_damage=missing",
)


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def standard_length_evidence(draft: Path) -> dict[str, Any]:
    text = draft.read_text(encoding="utf-8")
    _, content_lines = split_title_and_content_lines(text.splitlines())
    if detect_style(text) != "standard":
        return {}
    body = "\n".join(line for line in content_lines if line.strip() and not line.startswith("<!--"))
    body_chars = chinese_len(body)
    return {
        "standard_body_chars": body_chars,
        "preferred_target_shortfall": body_chars < STANDARD_DIARY_PREFERRED_TARGET_MIN_CHARS,
    }


def stop_lock_path(draft: Path) -> Path:
    digest = hashlib.sha256(str(draft.resolve()).encode("utf-8")).hexdigest()
    return Path(tempfile.gettempdir()) / "anlin-clean-run-locks" / f"{digest}.json"


def save_stop_state(state_path: Path, draft: Path, state: dict[str, Any]) -> None:
    if state.get("stopped"):
        state.setdefault("stopped_draft_sha256", file_sha256(draft))
        bounded_snapshot = (state.get("snapshots") or {}).get("bounded_final")
        if bounded_snapshot:
            state.setdefault("stopped_snapshot", bounded_snapshot)
    save_state(state_path, state)
    lock_path = stop_lock_path(draft)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    save_state(lock_path, state)


def generator_facing_summary(messages: list[str]) -> tuple[list[str], str]:
    """Collapse raw preflight telemetry into a qualitative repair interface.

    The state file keeps the raw messages for controller diagnostics.  The
    bounded generator should not receive exact counts or thresholds: those
    numbers turn a source repair into a metric-filling exercise.
    """

    labels: list[str] = []

    def add(label: str) -> None:
        if label not in labels:
            labels.append(label)

    body_chars: int | None = None
    for message in messages:
        match = re.search(r"body_chinese_chars=(\d+)", message)
        if match:
            body_chars = int(match.group(1))
            break
    underbuilt = (
        (body_chars is not None and body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS)
        or any(message.startswith("body_lines=") and "<" in message for message in messages)
    )
    severely_underbuilt = body_chars is not None and body_chars < STANDARD_DIARY_FORMAL_MIN_CHARS
    overfull = (
        (body_chars is not None and body_chars > STANDARD_DIARY_DRAFT_OVERFULL_CHARS)
        or any(message.startswith("body_lines=") and ">" in message for message in messages)
    )
    shape = any(
        message.startswith(
            (
                "medium_short_line_grid=",
                "long_lines=",
                "short_breath_lines=",
                "period_row_grid=",
                "short_line_grid=",
                "bare_line_grid=",
                "prose_block_shape=",
                "early_comma_ratio=",
                "short_genre_",
            )
        )
        for message in messages
    )
    source = any(
        message.startswith(
            (
                "connectors=",
                "paragraph_engine=weak",
                "rough_self_damage=missing",
                "private_grime_without_public_consequence=",
                "social_decline_plain_reply_private_loop=",
                "social_decline_group_fake_consequence=",
                "social_decline_tidy_etiquette_closure=",
                "social_decline_decoupled_consequence=",
                "feed_inventory_opening=",
                "soft_witness_no_consequence=",
            )
        )
        for message in messages
    )
    surface_prefixes = (
        ("process_leak_terms=", "process_leak_terms"),
        ("comment_chain_markers=", "comment_chain_markers"),
        ("meta_ai_topic_hits=", "meta_ai_topic_hits"),
        ("current_office_persona=", "current_office_persona"),
        ("background_display_groups=", "background_display_groups"),
        ("learned_ending_button=", "learned_ending_button"),
        ("pure_ambient_ending=", "pure_ambient_ending"),
        ("literary_simile_caption=", "literary_simile_caption"),
        ("em_dash=", "em_dash"),
        ("prompt_performing_dialogue=", "prompt_performing_dialogue"),
        ("quoted_dialogue=", "quoted_dialogue"),
        ("binary_reframe=", "binary_reframe"),
    )
    surface_forms = [
        label
        for message in messages
        for prefix, label in surface_prefixes
        if message.startswith(prefix)
    ]
    surface = bool(surface_forms)

    shape_script: str | None = None
    short_page = any(
        message.startswith("body_lines=") and "< 45" in message
        for message in messages
    )
    # A full-article standard draft with too few visible rows needs lineation before
    # comma softening.  Choosing soften_line_endings first leaves a dense source
    # block intact; rebalance_line_rhythm can preserve the existing fragments
    # while creating the breathing rows that the bounded interface is asking for.
    if short_page:
        shape_script = "rebalance_line_rhythm"
    elif any(message.startswith("early_comma_ratio=") for message in messages):
        shape_script = "soften_line_endings"
    elif any(
        message.startswith(
            (
                "period_row_grid=",
                "prose_block_shape=",
                "medium_short_line_grid=",
                "long_lines=",
                "short_line_grid=",
                "bare_line_grid=",
                "short_breath_lines=",
            )
        )
        for message in messages
    ):
        shape_script = "rebalance_line_rhythm"

    if overfull:
        add("source_shape=overfull")
    elif underbuilt:
        add("source_shape=underbuilt")
    elif shape:
        add("rhythm_shape=needs_local_reset")
    if any(message.startswith("connectors=") for message in messages):
        add("movement_connections=thin")
    if any(message.startswith("paragraph_engine=weak") for message in messages):
        add("paragraph_engine=weak")
    if any(
        message.startswith(("rough_self_damage=missing", "private_grime_without_public_consequence="))
        for message in messages
    ):
        add("public_roughness=missing")
    if any(
        message.startswith(
            (
                "social_decline_plain_reply_private_loop=",
                "social_decline_group_fake_consequence=",
                "social_decline_tidy_etiquette_closure=",
                "social_decline_decoupled_consequence=",
            )
        )
        for message in messages
    ):
        add("refusal_consequence=needs_source_action")
    if surface:
        for form in surface_forms:
            add(f"surface_form={form}")
        add("surface_risk=remove_locally")
    if not labels:
        add("source_or_surface_review=required")

    if overfull:
        action = (
            "overfull_action=trim_or_replace_repeated_material_preserve_working_movement; "
            "do_not_add_new_scene_or_proof_packet"
        )
    elif severely_underbuilt:
        action = (
            "source_action=whole_source_rebuild_from_strongest_fragment; "
            "restore_day_shaped_collage_with_independent_thought_turns; "
            "preserve_complete_article_and_existing_source_mass; do_not_shrink_to_a_premise_summary; "
            "do_not_append_checker_shaped_material"
        )
    elif underbuilt or source:
        action = (
            "source_action=replace_one_broken_fragment_or_relation_in_place; preserve_existing_article; "
            "do_not_add_material_for_metrics"
        )
    elif shape:
        if shape_script == "soften_line_endings":
            action = "shape_action=run_soften_line_endings_in_place_as_final_mutation_then_immediate_wrapper_rerun"
        elif shape_script == "rebalance_line_rhythm":
            action = (
                "shape_action=run_rebalance_line_rhythm_in_place_as_final_mutation_then_immediate_wrapper_rerun"
            )
        else:
            action = (
                "shape_action=perform_only_the_named_local_rhythm_step_in_place_as_final_mutation_then_immediate_wrapper_rerun"
            )
    elif surface:
        action = "surface_action=remove_only_the_named_surface_form_and_preserve_scene_movement"
    else:
        action = "source_action=change_one_existing_movement_that_changes_what_happens_next"

    # A severe source deficit is a content-boundary failure, not a shape-tool
    # opportunity.  Do not expose a rhythm script in the same action: a
    # generator can otherwise treat the script's output as an intermediate
    # draft, read it, and write again after the script, invalidating the
    # bounded trace and allowing shape tooling to stand in for missing source.
    if (
        shape_script
        and shape
        and (overfull or underbuilt or source)
        and not severely_underbuilt
        and "shape_action=" not in action
    ):
        action += (
            f"; after_content_write_run_{shape_script}_once_in_place_as_final_mutation_then_immediate_wrapper_rerun"
        )

    return labels, action


def generator_facing_contract(action: str = "", *, stopped: bool = False) -> str:
    if stopped:
        next_action = "next_action=read_draft_once_and_output_unchanged"
    elif "after_content_write_run_" in action:
        next_action = (
            "next_action=one_complete_draft_write_then_run_named_rhythm_script_in_place_"
            "then_immediate_wrapper_rerun"
        )
    elif "shape_action=run_" in action:
        next_action = "next_action=run_named_rhythm_script_in_place_then_immediate_wrapper_rerun"
    else:
        next_action = "next_action=one_complete_draft_write_then_immediate_wrapper_rerun"
    return (
        next_action
        + "; "
        "preflight attempts do not consume actual checker calls; "
        "wait for an explicit CLEAN_RUN_PREFLIGHT_STOP or actual checker result; "
        "do not count characters, lines, punctuation, or connectors; "
        "do not run python counters or other commands; "
        "if a rhythm script is named, run it in-place as the final mutation after the last content write; "
        "do not read its stdout or write draft.md afterward; rerun the wrapper immediately"
    )


def generator_facing_checker_output(stdout: str, stderr: str) -> str:
    """Keep checker findings actionable without exposing metric telemetry."""

    compact: list[str] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        match = re.match(r"^\[(error|warning|info)\]\s+(.+)$", line)
        if match:
            compact.append(f"[{match.group(1)}] {match.group(2)}")
            continue
        if not line.startswith("->"):
            continue
        # Suggestions are useful only when they remain qualitative.  Numeric
        # reports, serialized lists, and metric keys belong to controller
        # validation, not to the bounded generator's repair interface.
        if re.search(
            r"\d|%|\b(?:body_chars|body_lines|content_lines|first_\d+|paragraph_blocks|lines_ge|route_object_lines|social_lines|body_route_lines|present=)",
            line,
            flags=re.IGNORECASE,
        ):
            continue
        compact.append(line)
    if stderr.strip():
        compact.append("checker_tool_error=unavailable")
    if not compact:
        compact.append("checker_result=no_reported_findings")
    return (
        "generator-facing interface: controller-only telemetry; "
        + " ".join(compact)
        + ". "
        + generator_facing_contract()
    )


def load_stop_lock(draft: Path) -> dict[str, Any]:
    lock_path = stop_lock_path(draft)
    state = load_state(lock_path)
    if state.get("draft") == str(draft.resolve()) and state.get("stopped"):
        return state
    return {}


def snapshot_path(draft: Path, key: str) -> Path:
    safe_key = re.sub(r"[^A-Za-z0-9_.-]+", "-", key).strip("-") or "snapshot"
    return draft.parent / SNAPSHOT_DIR_NAME / f"{safe_key}.md"


def record_snapshot(draft: Path, state: dict[str, Any], key: str, *, overwrite: bool = False) -> None:
    snapshots = state.setdefault("snapshots", {})
    path = snapshot_path(draft, key)
    if not overwrite and key in snapshots and Path(str(snapshots[key])).is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(draft.read_bytes())
    snapshots[key] = str(path.resolve())


def normalize_before_final_check(draft: Path) -> None:
    def current_lengths() -> tuple[list[str], list[int], int, float, int, float]:
        text = draft.read_text(encoding="utf-8")
        _, content_lines = split_title_and_content_lines(text.splitlines())
        visible_lines = [line for line in content_lines if line.strip() and not line.strip().startswith("<!--")]
        current = [chinese_len(line) for line in visible_lines]
        current_body_chars = sum(current)
        current_mean = statistics.mean(current) if current else 0.0
        current_long_count = sum(1 for length in current if length >= 28)
        current_stdev = statistics.pstdev(current) if len(current) > 1 else 0.0
        return visible_lines, current, current_body_chars, current_mean, current_long_count, current_stdev

    visible, lengths, body_chars, mean_line, long_count, line_stdev = current_lengths()
    prose_compressed = (
        len(visible) < 45
        or (body_chars >= STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS and mean_line >= 42)
        or (len(visible) > 0 and long_count >= max(6, int(len(visible) * 0.65)))
    )
    if prose_compressed:
        subprocess.run(
            [sys.executable, str(SPLIT_LONG_LINES), str(draft), "--in-place", "--target-lines", "58"],
            text=True,
            encoding="utf-8",
            check=False,
        )
        visible, lengths, body_chars, mean_line, long_count, line_stdev = current_lengths()
    short_ratio = (sum(1 for length in lengths if length <= 12) / len(lengths)) if lengths else 0.0
    true_short_grid = (
        len(visible) > 90
        or (len(visible) > 75 and (short_ratio >= 0.40 or long_count < 4))
        or (short_ratio >= 0.62 and long_count < 8)
        or (short_ratio >= 0.55 and line_stdev <= 6.0)
        or (len(visible) >= 72 and (long_count < 4 or line_stdev <= 6.0))
    )
    if true_short_grid:
        subprocess.run(
            [
                sys.executable,
                str(MERGE_SHORT_LINES),
                str(draft),
                "--in-place",
                "--target-lines",
                "68",
                "--start-min-chars",
                "12",
                "--max-min-chars",
                "22",
            ],
            text=True,
            encoding="utf-8",
            check=False,
        )
    rebalance_medium_grid(draft)
    subprocess.run(
        [
            sys.executable,
            str(REBALANCE_LINE_RHYTHM),
            str(draft),
            "--in-place",
            "--target-min-lines",
            "45",
            "--target-max-lines",
            "70",
            "--preferred-lines",
            "58",
            "--min-long-lines",
            "10",
        ],
        text=True,
        encoding="utf-8",
        check=False,
    )
    subprocess.run(
        [sys.executable, str(SOFTEN_LINE_ENDINGS), str(draft), "--in-place"],
        text=True,
        encoding="utf-8",
        check=False,
    )


def is_title_candidate(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("# "):
        return True
    return not re.search(r"[。！？!?，,：:；;]", stripped) and chinese_len(stripped) <= 24


def content_line_indices(lines: list[str]) -> list[int]:
    indices: list[int] = []
    first_nonempty_seen = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if not first_nonempty_seen:
            first_nonempty_seen = True
            if is_title_candidate(stripped):
                continue
        if stripped.startswith("<!--"):
            continue
        indices.append(index)
    return indices


def join_for_rebalance(left: str, right: str) -> str:
    left = left.rstrip()
    right = right.strip()
    return left + right


def rebalance_medium_grid(draft: Path, *, min_long_lines: int = 6, min_body_lines: int = 45) -> None:
    text = draft.read_text(encoding="utf-8")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    changed = False
    while True:
        indices = content_line_indices(lines)
        lengths = [chinese_len(lines[index]) for index in indices]
        long_lines = sum(1 for length in lengths if length >= 28)
        if long_lines >= min_long_lines or len(indices) <= min_body_lines:
            break
        candidates: list[tuple[int, int]] = []
        index_set = set(indices)
        for left_index in indices:
            right_index = left_index + 1
            if right_index not in index_set:
                continue
            left_len = chinese_len(lines[left_index])
            right_len = chinese_len(lines[right_index])
            combined_len = chinese_len(join_for_rebalance(lines[left_index], lines[right_index]))
            if left_len <= 23 and right_len <= 23 and 24 <= combined_len <= 48:
                candidates.append((abs(combined_len - 32), left_index))
        if not candidates:
            break
        _, left_index = min(candidates)
        right_index = left_index + 1
        lines[left_index] = join_for_rebalance(lines[left_index], lines[right_index])
        del lines[right_index]
        changed = True
    if changed:
        draft.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def binary_reframe_matches(lines: list[str]) -> list[tuple[int, str]]:
    not_prefix = r"(?<!是)不是"
    patterns = [
        re.compile(rf"{not_prefix}[^，。！？\n]{{1,28}}[,，]?(?:而|只|也|这|那)?(?:才)?是"),
        re.compile(rf"{not_prefix}[^，。！？\n]{{1,28}}[,，]?(?:就是|只是)"),
        re.compile(rf"{not_prefix}[^，。！？\n]{{1,28}}[,，](?:我|你|他|她|它)?(?:就是|只是|才是|是)"),
        re.compile(rf"{not_prefix}[^。！？\n]{{1,28}}[。！？]\s*(?:是|就是|只是|而是|才是)"),
        re.compile(rf"{not_prefix}[^。！？\n]{{1,28}}[。！？]\s*(?:我|你|他|她|它)?(?:是|就是|只是|而是|才是)"),
        re.compile(r"其实不是[,，]?(?:好像|就是|只是|而是|是)"),
        re.compile(r"像[^。！？\n]{1,32}其实不是"),
    ]
    matches: list[tuple[int, str]] = []
    seen: set[tuple[int, str]] = set()
    for index, line in enumerate(lines, start=1):
        if any(pattern.search(line) for pattern in patterns):
            excerpt = line.strip()
            key = (index, excerpt)
            if key not in seen:
                matches.append(key)
                seen.add(key)
    for index in range(len(lines) - 1):
        left = lines[index].strip()
        right = lines[index + 1].strip()
        if (
            re.search(rf"{not_prefix}[^。！？\n]{{1,28}}[，,。！？]?$", left)
            and re.match(r"^(?:我|你|他|她|它)?(?:而是|是|就是|只是|这是|那是|才是)[^。！？\n]{1,40}", right)
        ):
            excerpt = f"{left} / {right}"
            key = (index + 1, excerpt)
            if key not in seen:
                matches.append(key)
                seen.add(key)
    return matches


def has_binary_reframe(lines: list[str]) -> bool:
    return bool(binary_reframe_matches(lines))


def learned_ending_button_matches(lines: list[str]) -> list[str]:
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.strip().startswith("<!--")]
    tail = visible_lines[-3:]
    return [line for line in tail if re.sub(r"\s+", "", line) in LEARNED_ENDING_LINES]


def ambient_ending_matches(lines: list[str]) -> list[str]:
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.strip().startswith("<!--")]
    if not visible_lines:
        return []
    last_line = visible_lines[-1]
    return [last_line] if any(re.search(pattern, last_line) for pattern in AMBIENT_ENDING_PATTERNS) else []


def quoted_dialogue_matches(lines: list[str]) -> list[tuple[int, str]]:
    patterns = [
        re.compile(r"(?:说|问|喊|回|继续说|又说|老板|摊主|店员|司机|我妈|室友)[^。！？\n]{0,12}[“\"『「]"),
        re.compile(r"[”\"』」][^。！？\n]{0,12}(?:说|问|喊|回|笑|盯|凑|看)"),
        re.compile(r"^[“\"『「][^。！？\n]{1,42}[。！？]?[”\"』」]$"),
    ]
    matches: list[tuple[int, str]] = []
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if any(pattern.search(stripped) for pattern in patterns):
            matches.append((index, stripped))
    return matches


def literary_simile_caption_matches(lines: list[str]) -> list[tuple[int, str]]:
    patterns = [
        re.compile(r"(?:脑子里|心里|那句话|这句话|消息|简历|人生|命运|裂缝|下午|沉默|孤独|焦虑|压力|屏幕)[^。！？\n]{0,24}像[^。！？\n]{2,36}"),
        re.compile(r"像一(?:颗|根|道|张|块|条|口|层)[^。！？\n]{1,18}(?:钉子|针|刺|井|表|网|墙|裂缝|伤口|洞|锁)"),
    ]
    matches: list[tuple[int, str]] = []
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if any(pattern.search(stripped) for pattern in patterns):
            matches.append((index, stripped))
    return matches


def soft_witness_matches(lines: list[str]) -> list[tuple[int, str]]:
    witness_pattern = re.compile(
        r"(?:看了我一眼|看了我两眼|又往下看|往下看了一眼|往里看了一眼|往屋里看了一眼|瞥了我一眼|看了看我|扫到[^。！？\n]{0,18}(?:油|袖|脚|裤|鞋|房间|屋里))"
    )
    consequence_pattern = re.compile(
        r"(?:"
        r"等我|没走|站着|举着|问|提醒|指了|递回|退回|扫码|付款|二维码|"
        r"袋子[^。！？\n]{0,18}(?:漏|破|洒|断)|"
        r"(?:汤|红油|外卖)[^。！？\n]{0,24}(?:洒|漏|淌|流)|"
        r"我[^。！？\n]{0,24}(?:赶紧|慌|没答|没回|答不上|擦|蹭|掉|摔|滑|差点|跪|塞|缩|躲)|"
        r"(?:门|袋子|手机|手|脚|拖鞋)[^。！？\n]{0,28}(?:撞|夹|掉|滑|断|漏|洒|卡)"
        r")"
    )
    linked_transaction_pattern = re.compile(
        r"(?:"
        r"(?:输|输入|按)[^。！？\n]{0,8}(?:密码|键)[^。！？\n]{0,12}(?:取消|撤销|作废)|"
        r"(?:订单|交易|付款|支付|收银|小票|票据)[^。！？\n]{0,20}(?:取消|撤销|作废|退款|退单|重新付款)|"
        r"(?:取消|撤销|作废|退款|退单)[^。！？\n]{0,20}(?:订单|交易|付款|支付|小票|票据)"
        r")"
    )
    linked_queue_pattern = re.compile(
        r"(?:排队|队伍|后面的人|后面排队的)[^。！？\n]{0,24}(?:往前挪|前移|挪了一步)"
    )
    yielded_position_pattern = re.compile(r"我[^。！？\n]{0,20}(?:让出|让了)[^。！？\n]{0,8}(?:位置|地方)")
    checkout_context_pattern = re.compile(
        r"(?:收银员|店员|柜台|结账|收银|付款|支付|扫码|二维码|密码|机器|小票|票据)"
    )
    detached_context_pattern = re.compile(r"(?:回屋|回家|昨晚|上周|之前|想起|明早|闹钟)")

    def current_match(pattern: re.Pattern[str], text: str, witness_start: int = 0, witness_end: int = 0) -> bool:
        for candidate in pattern.finditer(text):
            if candidate.end() <= witness_start:
                relevant_prefix = text[: candidate.start()]
                between_candidate_and_witness = text[candidate.end() : witness_start]
                if detached_context_pattern.search(between_candidate_and_witness):
                    continue
            elif candidate.start() >= witness_end:
                relevant_prefix = text[witness_end : candidate.start()]
            else:
                relevant_prefix = ""
            if not detached_context_pattern.search(relevant_prefix):
                return True
        return False

    matches: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        witness_match = witness_pattern.search(stripped)
        if not witness_match:
            continue
        window_lines = [item.strip() for item in lines[index : index + 3]]
        has_consequence = current_match(
            consequence_pattern,
            stripped,
            witness_match.start(),
            witness_match.end(),
        ) or any(current_match(consequence_pattern, item) for item in window_lines[1:])
        has_transaction = current_match(
            linked_transaction_pattern,
            stripped,
            witness_match.start(),
            witness_match.end(),
        )
        has_queue = bool(
            current_match(
                linked_queue_pattern,
                stripped,
                witness_match.start(),
                witness_match.end(),
            )
            and yielded_position_pattern.search(stripped)
        )
        previous_line = lines[index - 1].strip() if index > 0 else ""
        checkout_context = "\n".join(
            candidate
            for candidate in (previous_line, stripped)
            if candidate and not detached_context_pattern.search(candidate)
        )
        if not (has_consequence or has_transaction or has_queue) and checkout_context_pattern.search(checkout_context):
            linked_lines = window_lines[1:]
            linked_window = "\n".join(linked_lines)
            has_transaction = current_match(linked_transaction_pattern, linked_window)
            has_queue = bool(
                current_match(linked_queue_pattern, linked_window)
                and (
                    yielded_position_pattern.search(linked_window)
                    or current_match(linked_transaction_pattern, linked_window)
                    or re.search(r"(?:取消|撤销|作废|退款|退单|小票)", linked_window)
                )
            )
        if not (has_consequence or has_transaction or has_queue):
            matches.append((index + 1, stripped))
    return matches


def surface_preflight_messages(lines: list[str], article_text: str) -> list[str]:
    messages: list[str] = []
    leaked_terms = [term for term in PROCESS_LEAK_TERMS if term in article_text]
    if leaked_terms:
        messages.append(f"process_leak_terms={leaked_terms[:3]}")
    comment_markers: list[str] = []
    seen_comment_markers: set[str] = set()
    for line in lines:
        for marker in comment_chain_formula_hits(line):
            if marker not in seen_comment_markers:
                comment_markers.append(marker)
                seen_comment_markers.add(marker)
    if comment_markers:
        messages.append(f"comment_chain_markers={comment_markers[:4]}")
    binary_matches = binary_reframe_matches(lines)
    if binary_matches:
        examples = " | ".join(
            f"L{line_no}:{excerpt[:42]}" for line_no, excerpt in binary_matches[:3]
        )
        messages.append(
            f"binary_reframe=present count={len(binary_matches)} scan_all_occurrences=true examples={examples}"
        )
    prompt_dialogue_matches = prompt_performing_dialogue_hits(lines)
    if prompt_dialogue_matches:
        examples = " | ".join(
            f"L{line_no}:{excerpt[:42]}" for line_no, excerpt in prompt_dialogue_matches[:3]
        )
        messages.append(
            f"prompt_performing_dialogue=present count={len(prompt_dialogue_matches)} examples={examples}"
        )
    ending_matches = learned_ending_button_matches(lines)
    if ending_matches:
        examples = " | ".join(line[:24] for line in ending_matches[:3])
        messages.append(f"learned_ending_button=present examples={examples}")
    ambient_matches = ambient_ending_matches(lines)
    if ambient_matches:
        examples = " | ".join(line[:24] for line in ambient_matches[:3])
        messages.append(f"pure_ambient_ending=present examples={examples}")
    quote_matches = quoted_dialogue_matches(lines)
    if quote_matches:
        examples = " | ".join(f"L{line_no}:{excerpt[:42]}" for line_no, excerpt in quote_matches[:3])
        messages.append(f"quoted_dialogue=present count={len(quote_matches)} examples={examples}")
    simile_matches = literary_simile_caption_matches(lines)
    if simile_matches:
        examples = " | ".join(f"L{line_no}:{excerpt[:42]}" for line_no, excerpt in simile_matches[:3])
        messages.append(f"literary_simile_caption=present count={len(simile_matches)} examples={examples}")
    feed_inventory_matches = feed_inventory_opening_hits(lines)
    if feed_inventory_matches:
        examples = " | ".join(f"L{line_no}:{excerpt[:42]}" for line_no, excerpt in feed_inventory_matches[:3])
        messages.append(f"feed_inventory_opening=present count={len(feed_inventory_matches)} examples={examples}")
    witness_matches = soft_witness_matches(lines)
    if witness_matches:
        examples = " | ".join(f"L{line_no}:{excerpt[:42]}" for line_no, excerpt in witness_matches[:3])
        messages.append(f"soft_witness_no_consequence=present count={len(witness_matches)} examples={examples}")
    dash_lines = [f"L{index}:{line.strip()[:42]}" for index, line in enumerate(lines, start=1) if "——" in line]
    if dash_lines:
        messages.append(f"em_dash=present count={len(dash_lines)} examples={' | '.join(dash_lines[:3])}")
    meta_ai_hits = meta_ai_topic_hits(article_text)
    if meta_ai_hits:
        messages.append(f"meta_ai_topic_hits={meta_ai_hits[:4]}")
    office_hits = current_office_persona_hits(article_text)
    if office_hits:
        messages.append(f"current_office_persona={office_hits[:4]}")
    background_hits = {
        group: [term for term in terms if term in article_text][:3]
        for group, terms in BACKGROUND_DISPLAY_GROUPS.items()
        if any(term in article_text for term in terms)
    }
    if len(background_hits) >= 4:
        messages.append(f"background_display_groups={json.dumps(background_hits, ensure_ascii=False)}")
    return messages


def preflight_messages(draft: Path) -> list[str]:
    text = draft.read_text(encoding="utf-8")
    title, content_lines = split_title_and_content_lines(text.splitlines())
    style = detect_style(text)
    article_lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("<!--")]
    visible_lines = [line for line in content_lines if line.strip() and not line.strip().startswith("<!--")]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    line_lengths = [chinese_len(line) for line in visible_lines]
    body_line_count = len(line_lengths)
    mean_line = statistics.mean(line_lengths) if line_lengths else 0.0
    line_stdev = statistics.pstdev(line_lengths) if len(line_lengths) > 1 else 0.0
    long_line_count = sum(1 for length in line_lengths if length >= 28)
    short_breath_count = sum(1 for length in line_lengths if length <= 8)
    short_line_ratio = (sum(1 for length in line_lengths if length <= 12) / len(line_lengths)) if line_lengths else 0.0
    first_twenty = visible_lines[:20]
    comma_ratio = (sum(1 for line in first_twenty if line.endswith("，")) / len(first_twenty)) if first_twenty else 0.0
    period_count = body.count("。")
    period_per_1k = period_count / body_chars * 1000 if body_chars else 0.0
    line_period_ratio = (
        sum(1 for line in visible_lines if line.endswith("。")) / len(visible_lines)
    ) if visible_lines else 0.0
    bare_line_ratio = (
        sum(
            1
            for line in visible_lines
            if chinese_len(line) >= 2 and not re.search(r"[，。！？；：、,.!?;:]$", line.strip())
        )
        / len(visible_lines)
    ) if visible_lines else 0.0
    time_glue_count = sum(body.count(term) for term in ("后来", "已经", "当时"))
    connectors = [term for term in HIGH_FREQUENCY_TERMS if term in body]
    engine_hits = [term for term in ENGINE_SIGNAL_TERMS if term in body]
    engine_hits.extend(pattern for pattern in ENGINE_SIGNAL_PATTERNS if re.search(pattern, body))
    rough_terms = [term for term in ROUGH_SELF_DAMAGE_TERMS if term in body]
    rough_patterns = [pattern for pattern in ROUGH_SELF_DAMAGE_PATTERNS if re.search(pattern, body)]
    messages: list[str] = []
    if not title:
        first_visible = article_lines[0] if article_lines else ""
        messages.append(f"missing_title=first_visible:{first_visible[:32]}")
    if style != "standard":
        if body_chars < 180:
            messages.append(f"{style}_body_chinese_chars={body_chars} < 180")
        if body_line_count < 24:
            messages.append(f"short_genre_body_lines=style:{style}, body_lines={body_line_count} < 24")
        if body_chars < 520:
            messages.append(
                f"short_genre_underbuilt_complete_article=style:{style}, body_chars={body_chars} < 520"
            )
        if 520 <= body_chars < 650:
            messages.append(
                f"short_genre_complete_article_buffer=style:{style}, body_chars={body_chars} < 650"
            )
        if body_chars < 650 and body_line_count >= 18 and long_line_count == 0:
            messages.append(
                f"short_genre_no_long_clumsy_lines=style:{style}, body_lines={body_line_count}, long_lines={long_line_count}"
            )
        if body_line_count >= 55 and short_line_ratio >= 0.45 and long_line_count < 3:
            messages.append(
                f"short_genre_short_line_grid=style:{style}, body_lines={body_line_count}, "
                f"short_line_ratio={short_line_ratio:.2f}, long_lines={long_line_count}"
            )
        if body_chars >= 520 and (body_line_count <= 20 or mean_line >= 32 or comma_ratio < 0.08):
            messages.append(
                f"short_genre_prose_block_compression=style:{style}, body_lines={body_line_count}, mean_line={mean_line:.1f}, early_comma_ratio={comma_ratio:.2f}"
            )
        if body_chars >= 520 and body_line_count >= 28 and (
            (period_per_1k >= 45 and period_count >= 24)
            or (line_period_ratio >= 0.52 and time_glue_count >= 4)
        ):
            messages.append(
                f"short_genre_period_grid=style:{style}, periods={period_count}, period_per_1k={period_per_1k:.1f}, "
                f"line_period_ratio={line_period_ratio:.2f}, time_glue={time_glue_count}"
            )
        normalized_title = re.sub(r"[\s#]+", "", title)
        if re.search(r"(?:母亲节|五月十二日|5月12日|五月十二|520)", normalized_title):
            messages.append(f"short_genre_diagnostic_date_title={normalized_title}")
        main_prop_title_risk = short_genre_main_prop_title_loop_risk(text.splitlines(), text)
        if main_prop_title_risk:
            messages.append(
                "short_genre_main_prop_title_loop="
                + json.dumps(main_prop_title_risk, ensure_ascii=False)
            )
        short_story_risk = short_genre_literary_story_risk(text.splitlines(), text)
        if short_story_risk:
            messages.append(
                "short_genre_literary_story_closure="
                + json.dumps(short_story_risk, ensure_ascii=False)
            )
        local_loop_risk = short_genre_local_packet_loop_risk(text.splitlines(), text)
        if local_loop_risk:
            messages.append(
                "short_genre_local_packet_loop="
                + json.dumps(local_loop_risk, ensure_ascii=False)
            )
        present_anchor_risk = short_genre_present_action_anchor_risk(text.splitlines(), text)
        if present_anchor_risk:
            messages.append(
                "short_genre_present_action_anchor="
                + json.dumps(present_anchor_risk, ensure_ascii=False)
            )
        prompt_prop_risk = short_genre_prompt_prop_too_early_risk(text.splitlines(), text)
        if prompt_prop_risk:
            messages.append(
                "short_genre_prompt_prop_too_early="
                + json.dumps(prompt_prop_risk, ensure_ascii=False)
            )
        stuffing_groups = short_genre_repair_stuffing_groups(body)
        stuffing_hits = [term for terms in stuffing_groups.values() for term in terms]
        if body_chars >= 850 and (len(stuffing_groups) >= 3 or len(stuffing_hits) >= 5):
            messages.append(
                "short_genre_repair_stuffing="
                + json.dumps(
                    {"style": style, "body_chars": body_chars, "groups": stuffing_groups},
                    ensure_ascii=False,
                )
            )
        messages.extend(surface_preflight_messages(article_lines, "\n".join(article_lines)))
        return messages
    standard_prop_loop_risk = standard_prompt_prop_title_loop_risk(text.splitlines(), text)
    normalized_title = re.sub(r"[\s#]+", "", title)
    opening_text = "\n".join(visible_lines[:5])
    opening_matches = sorted({term for term in HIGH_SIGNAL_OPENING_TERMS if term in opening_text})
    if visible_lines:
        first_line_matches = [term for term in HIGH_SIGNAL_OPENING_TERMS if term in visible_lines[0]]
        if first_line_matches or len(opening_matches) >= 2:
            examples = " | ".join(line[:42] for line in visible_lines[:3])
            messages.append(
                f"high_signal_opening=present terms={opening_matches[:6]} examples={examples}"
            )
    if normalized_title in STANDARD_PROMPT_PROP_TITLE_TERMS:
        messages.append(f"standard_prompt_prop_title={normalized_title}")
    if standard_prop_loop_risk:
        messages.append(
            "standard_prompt_prop_title_loop="
            + json.dumps(standard_prop_loop_risk, ensure_ascii=False)
        )
    plain_reply_loop_risk = social_decline_plain_reply_private_loop_risk(text.splitlines(), text)
    if plain_reply_loop_risk:
        messages.append(
            "social_decline_plain_reply_private_loop="
            + json.dumps(plain_reply_loop_risk, ensure_ascii=False)
        )
    group_fake_consequence_risk = social_decline_group_fake_consequence_risk(text.splitlines(), text)
    if group_fake_consequence_risk:
        messages.append(
            "social_decline_group_fake_consequence="
            + json.dumps(group_fake_consequence_risk, ensure_ascii=False)
        )
    tidy_etiquette_closure_risk = social_decline_tidy_etiquette_closure_risk(text.splitlines(), text)
    if tidy_etiquette_closure_risk:
        messages.append(
            "social_decline_tidy_etiquette_closure="
            + json.dumps(tidy_etiquette_closure_risk, ensure_ascii=False)
        )
    decoupled_consequence_risk = social_decline_decoupled_consequence_risk(text.splitlines(), text)
    if decoupled_consequence_risk:
        messages.append(
            "social_decline_decoupled_consequence="
            + json.dumps(decoupled_consequence_risk, ensure_ascii=False)
        )
    if body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS:
        messages.append(f"body_chinese_chars={body_chars} < {STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS}")
    if body_chars > STANDARD_DIARY_DRAFT_OVERFULL_CHARS:
        messages.append(f"body_chinese_chars={body_chars} > {STANDARD_DIARY_DRAFT_OVERFULL_CHARS}")
    if body_line_count < 45:
        messages.append(f"body_lines={body_line_count} < 45 (write a line-broken article, not prose paragraphs)")
    if body_line_count > 90:
        messages.append(
            f"body_lines={body_line_count} > 90 (overfragmented short-line grid; merge adjacent action/speech lines before checking)"
        )
    if body_line_count > 75 and long_line_count < 3:
        messages.append(f"long_lines={long_line_count} < 3 (keep several rough longer action/speech/thought lines)")
    if (
        STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS <= body_chars < STANDARD_DIARY_PREFERRED_TARGET_MIN_CHARS
        and 45 <= body_line_count <= 75
        and long_line_count < 6
    ):
        messages.append(
            f"medium_short_line_grid=present (long_lines={long_line_count} < 6, line_stdev={line_stdev:.1f}; "
            "rewrite rough action/speech/thought lines before checking)"
        )
    if body_line_count >= 45 and short_breath_count < 4:
        messages.append(
            f"short_breath_lines={short_breath_count} < 4 (keep a few <=8-Chinese-character breath drops; do not make every line a finished caption)"
        )
    if body_chars >= STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS and body_line_count >= 45 and (
        (period_per_1k >= 45 and period_count >= 35)
        or (line_period_ratio >= 0.65 and short_breath_count < 4)
    ):
        messages.append(
            f"period_row_grid=present (periods={period_count}, period_per_1k={period_per_1k:.1f}, "
            f"line_period_ratio={line_period_ratio:.2f}; rebuild breathing clusters instead of one finished sentence per row)"
        )
    if body_line_count >= 70 and short_line_ratio >= 0.45:
        messages.append(f"short_line_grid={short_line_ratio:.2f} (do not create line breaks by deleting punctuation)")
    if body_line_count >= 45 and short_line_ratio >= 0.35 and bare_line_ratio >= 0.35:
        messages.append(
            f"bare_line_grid={bare_line_ratio:.2f} (keep punctuation on broken lines; do not turn the article into caption-like naked rows)"
        )
    if body_chars >= STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS and (body_line_count <= 20 or mean_line >= 42 or long_line_count >= max(6, int(body_line_count * 0.65))):
        messages.append(
            f"prose_block_shape=compressed (body_lines={body_line_count}, mean_line={mean_line:.1f}, long_lines={long_line_count})"
        )
    if len(first_twenty) >= 8 and comma_ratio < 0.15:
        messages.append(f"early_comma_ratio={comma_ratio:.2f} < 0.15")
    if len(connectors) < 3:
        messages.append(f"connectors={connectors} < 3")
    if len(engine_hits) < 3:
        if body_chars < STANDARD_DIARY_FORMAL_MIN_CHARS:
            messages.append(
                "paragraph_engine=weak (source reset: rebuild the incomplete article from the strongest fragment; "
                "preserve a complete article and do not append checker-shaped material; do not inspect checker source/tests)"
            )
        elif body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS:
            messages.append(
                "paragraph_engine=weak (source reset: replace the earliest overloaded fragment or relation in place; preserve the complete article "
                "across the replacement and neighboring existing movements; do not add material for a metric; "
                "do not inspect checker source/tests)"
            )
        else:
            messages.append(
                "paragraph_engine=weak (source reset: replace the earliest inert fragment or relation in place; "
                "preserve the complete article and do not add material for a metric; do not inspect checker source/tests)"
            )
    private_grime_terms = [term for term in PRIVATE_GRIME_TEXTURE_TERMS if term in body]
    if private_grime_terms and not rough_terms and not rough_patterns:
        messages.append(
            "private_grime_without_public_consequence="
            + json.dumps(private_grime_terms[:6], ensure_ascii=False)
            + " (private stain, mirror, burp, hair, or clothing inspection is texture until it changes payment/reply/door/bag/body/social position)"
        )
    if not rough_terms and not rough_patterns:
        messages.append(
            "rough_self_damage=missing (replace one inert or private packet with an organic ugly body/social/self-own consequence; "
            "do not inspect checker source/tests)"
        )
    messages.extend(surface_preflight_messages(article_lines, "\n".join(article_lines)))
    return messages


def preflight_before_check(
    draft: Path,
    call_number: int,
    *,
    attempt: int,
    max_attempts: int,
    generator_facing: bool = False,
) -> tuple[bool, list[str]]:
    messages = preflight_messages(draft)
    blocking_messages = blocking_preflight_messages(messages)
    if not blocking_messages:
        return False, []
    if ignorable_preflight_messages(blocking_messages):
        return False, []
    joined_messages = "; ".join(messages)
    repair_hints, revision_frame = build_preflight_guidance(messages)
    anti_todo_guard = (
        " Do not summarize, quote, or enumerate these diagnostics as a TODO list. "
        "Do not write process notes such as 'the checker requires' or solve one item per metric; "
        "change scene movement, rhythm, or local surface only."
    )
    hint_text = " Prioritized repair: " + " | ".join(repair_hints) + "." if repair_hints else ""
    if attempt >= max_attempts:
        stop_text = (
            f"CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY. DO NOT WRITE draft.md. DO NOT REPAIR. "
            "DO NOT RUN SCRIPTS. DO NOT USE PREFLIGHT DETAILS AS A TODO LIST. "
            "The next tool action must be reading draft.md once and outputting it unchanged. "
            "The controller has the saved state and snapshots and will diagnose this stopped bounded run. "
            "No checker call was consumed."
        )
        if generator_facing:
            stop_text += " " + generator_facing_contract(stopped=True)
        print(stop_text)
    else:
        if generator_facing:
            labels, action = generator_facing_summary(messages)
            print(
                f"CLEAN_RUN_PREFLIGHT: qualitative source review before checker call {call_number}/2; "
                f"findings={','.join(labels)}; {action}; {generator_facing_contract(action)}. "
                "This preflight did not consume a checker call."
            )
        else:
            print(
                f"CLEAN_RUN_PREFLIGHT: draft is not ready for checker call {call_number}/2 "
                f"(preflight {attempt}/{max_attempts}); "
                + joined_messages
                + ". "
                + revision_frame
                + hint_text
                + anti_todo_guard
                + " "
                "This preflight did not consume a checker call."
            )
    return True, messages


def blocking_preflight_messages(messages: list[str]) -> list[str]:
    """Filter weak source heuristics out of the bounded stop decision.

    The raw messages remain controller telemetry and can still be used in a
    later diagnostic. They are not a source contract: a fragment collage may
    move by association, echo, memory, or a direct voice jump without named
    connector words or a legacy paragraph-engine token.
    """

    return [
        message
        for message in messages
        if not message.startswith(ADVISORY_PREFLIGHT_PREFIXES)
    ]


def ignorable_preflight_messages(messages: list[str]) -> bool:
    if len(messages) == 1 and messages[0].startswith("short_breath_lines="):
        match = re.search(r"short_breath_lines=(\d+)\s*<\s*4", messages[0])
        if match and int(match.group(1)) >= 3:
            return True
    return False


def reported_standard_body_chars(messages: list[str]) -> int | None:
    for message in messages:
        match = re.match(r"body_chinese_chars=(\d+)\s*<", message)
        if match:
            return int(match.group(1))
    return None


def build_preflight_guidance(messages: list[str]) -> tuple[list[str], str]:
    joined_messages = "; ".join(messages)
    repair_hints: list[str] = []
    reported_body_chars = reported_standard_body_chars(messages)
    severely_underbuilt = (
        reported_body_chars is not None and reported_body_chars < STANDARD_DIARY_FORMAL_MIN_CHARS
    )
    short_of_full_article = (
        reported_body_chars is not None and reported_body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS
    )
    surface_only_prefixes = (
        "process_leak_terms=",
        "comment_chain_markers=",
        "binary_reframe=",
        "prompt_performing_dialogue=",
        "meta_ai_topic_hits=",
        "current_office_persona=",
        "background_display_groups=",
        "learned_ending_button=",
        "quoted_dialogue=",
        "literary_simile_caption=",
        "em_dash=",
        "standard_prompt_prop_title=",
        "pure_ambient_ending=",
    )
    surface_only = all(message.startswith(surface_only_prefixes) for message in messages)
    compressed_shape = any("< 45" in message or "prose_block_shape=compressed" in message for message in messages)
    overfragmented_shape = any(
        (message.startswith("body_lines=") and "> 90" in message)
        or message.startswith("short_line_grid=")
        or message.startswith("long_lines=")
        or message.startswith("medium_short_line_grid=")
        for message in messages
    )
    underbuilt_short_genre = any(
        message.startswith("short_genre_underbuilt_complete_article=")
        or message.startswith("short_genre_body_lines=")
        or message.startswith("short_genre_complete_article_buffer=")
        or message.startswith("short_genre_no_long_clumsy_lines=")
        or message.startswith("short_genre_short_line_grid=")
        or message.startswith("short_genre_period_grid=")
        or message.startswith("short_genre_prose_block_compression=")
        or message.startswith("short_genre_diagnostic_date_title=")
        or message.startswith("short_genre_repair_stuffing=")
        or message.startswith("short_genre_present_action_anchor=")
        or message.startswith("short_genre_prompt_prop_too_early=")
        or message.startswith("short_genre_main_prop_title_loop=")
        or message.startswith("short_genre_local_packet_loop=")
        for message in messages
    )
    title_issue = any(message.startswith("missing_title=") for message in messages)
    missing_breath = any("short_breath_lines=" in message for message in messages)
    standard_prompt_loop = any(
        message.startswith("standard_prompt_prop_title_loop=") for message in messages
    )
    standard_underbuilt_length = any(
        message.startswith("body_chinese_chars=") and f"< {STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS}" in message
        for message in messages
    )
    near_miss_short = (
        any("body_lines=" in message and "< 45" in message for message in messages)
        and "connectors=" in joined_messages
        and not severely_underbuilt
        and not standard_underbuilt_length
    )
    underbuilt_source = standard_underbuilt_length
    source_content_prefixes = (
        "connectors=",
        "paragraph_engine=weak",
        "rough_self_damage=missing",
        "private_grime_without_public_consequence=",
        "social_decline_plain_reply_private_loop=",
        "social_decline_group_fake_consequence=",
        "social_decline_tidy_etiquette_closure=",
        "social_decline_decoupled_consequence=",
        "standard_prompt_prop_title_loop=",
        "high_signal_opening=present",
        "feed_inventory_opening=present",
        "soft_witness_no_consequence=present",
        "prompt_performing_dialogue=present",
        "quoted_dialogue=present",
        "binary_reframe=present",
    )
    source_content_blocked = underbuilt_source or near_miss_short or any(
        message.startswith(source_content_prefixes) for message in messages
    )
    rebalance_needed = compressed_shape or overfragmented_shape
    mixed_rebalance_source = rebalance_needed and source_content_blocked
    if mixed_rebalance_source:
        if severely_underbuilt:
            repair_hints.append(
                "NEXT_ACTION=repair source/content first; rebuild the incomplete article from the strongest workable movement, restore complete "
                "article, and do not append checker-shaped material; "
                "after the last content write, run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place` as the final shape "
                "step before the wrapper; if you edit draft.md after that script, rerun the script before checking"
            )
        elif short_of_full_article:
            repair_hints.append(
                "NEXT_ACTION=repair source/content first; replace the earliest broken fragment or relation in place, preserve the complete article "
                "across the replacement and neighboring existing movements, and do not add material for a metric; after "
                "the last content write, run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place` as the final shape step "
                "before the wrapper; if you edit draft.md after that script, rerun the script before checking"
            )
        else:
            repair_hints.append(
                "NEXT_ACTION=repair source/content first; replace the earliest broken fragment or relation in place, preserve the complete article, "
                "and do not add material for a metric; after the last content write, run "
                "`python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place` as the final shape step before "
                "the wrapper; if you edit draft.md after that script, rerun the script before checking"
            )
    elif compressed_shape:
        repair_hints.append(
            "NEXT_ACTION=run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place` before any new prose rewrite; "
            "then inspect the actual visible line count and rewrite only inside that line-broken shape; "
            "if you write or edit draft.md after this rhythm reset, rerun rebalance_line_rhythm.py before the wrapper"
        )
    if underbuilt_source:
        if severely_underbuilt:
            repair_hints.append(
                "for a severely underbuilt source shape, do a whole-source rebuild before rhythm tooling: rebuild the incomplete article from "
                "the strongest workable fragment, preserve a complete article, and do not append checker-shaped proof packets or new material"
            )
        elif mixed_rebalance_source:
            mass_action = (
                "preserve the complete article across the replacement and neighboring existing movements"
                if short_of_full_article
                else "preserve the complete article"
            )
            repair_hints.append(
                "for an underbuilt source shape, do one local source replacement before rhythm tooling: keep the strongest fragment, "
                f"replace one repeated or overloaded fragment or relation in place, {mass_action}; write the replacement as visible movement, "
                "then run the rhythm script once at the end"
            )
        else:
            mass_action = (
                "preserve the complete article across the replacement and neighboring existing movements"
                if short_of_full_article
                else "preserve the complete article"
            )
            repair_hints.append(
                "for an underbuilt source shape, do a source-loop rewrite after the visible shape is reset: "
                "keep the strongest fragment, replace one repeated or overloaded relation in place, and preserve the article; "
                f"{mass_action} instead of patching isolated line additions"
            )
    if "paragraph_engine=weak" in joined_messages and not underbuilt_source:
        repair_hints.append(
            "for paragraph_engine=weak, do not append a decorative scene. Replace the earliest inert fragment or relation in place; "
            "let the next thought, action, memory, or joke change direction while preserving the existing article"
        )
    if near_miss_short:
        mass_action = (
            "preserve the complete article across the replacement and neighboring existing movements"
            if short_of_full_article
            else "preserve visible mass"
        )
        repair_hints.append(
            "for a near-miss short draft, replace one decorative packet with an existing lateral fragment that changes the voice or thought; "
            f"{mass_action} and do not append a separate explanatory scene"
        )
    if overfragmented_shape and not mixed_rebalance_source:
        repair_hints.append(
            "NEXT_ACTION=run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place` before hand rewriting; "
            "then inspect the visible rows and preserve or rebuild at least six rough longer action/speech/thought lines; "
            "if you write or edit draft.md after this rhythm reset, rerun rebalance_line_rhythm.py before the wrapper"
        )
        repair_hints.append(
            "for short-grid drift, overfragmented grids, or too few long lines, do not rewrite into many tiny rows or 30-line prose blocks; "
            "after the rhythm reset, repair the source movement rather than counting line breaks"
        )
    if missing_breath:
        repair_hints.append(
            "for short_breath_lines, split a few earned <=8-character landings from an existing ugly reply, failed decision, or small retreat; "
            "do not append decorative one-word captions"
        )
    if "period_row_grid=present" in joined_messages:
        repair_hints.append(
            "for period_row_grid, stop writing one finished `。` sentence per row, but do not globally merge rows into comma chains. "
            "Use local cluster surgery: repair only the smallest local movement that is actually broken where a hand, reply, payment, door, body, or object is still moving; "
            "delete its explanation tail first, restore only the continuation or landing that movement earns, and leave unrelated rows untouched. "
            "The goal is breathing movement, not more punctuation."
        )
    if standard_prompt_loop:
        repair_hints.append(
            "for standard_prompt_prop_title_loop, do a source reset instead of retitling only: choose a side consequence as the title, cut one prompt-prop echo from opening or tail, and rebuild the middle from a door, hallway, payment, dirty hand, wrong reply, sink, rider/shopkeeper, or another person's reaction so the prompt prop appears only as one pressure surface"
        )
    if "high_signal_opening=present" in joined_messages:
        repair_hints.append(
            "for high_signal_opening, rewrite the opening from a body, room, payment, door, charger, sink, or another ordinary action before any holiday/feed/gift/order prop leaks in"
        )
    if "feed_inventory_opening=present" in joined_messages:
        repair_hints.append(
            "for feed_inventory_opening, do not replace one feed list with another. Keep at most one cropped screen surface, start from a side action that would exist without the prompt, and move out of the phone through body, door, payment, room, wrong reply, food/object consequence, or outside contact"
        )
    if "soft_witness_no_consequence=present" in joined_messages:
        repair_hints.append(
            "for soft_witness_no_consequence, do not keep a rider, cashier, neighbor, or stranger as a silent camera. Make the existing handoff change payment, reply, bag/object state, dirty hand/clothing exposure, door movement, or the next action; otherwise remove or replace the cameo"
        )
    if underbuilt_short_genre:
        repair_hints.append(
            "for a short-genre source failure, do not solve by deleting memory or shrinking further; keep uneven movement, a few longer clumsy lines, a present practical turn, a side-action title, and discard or bury one prompt-supplied family prop instead of preserving every prompt noun"
        )
        if "short_genre_prompt_prop_too_early=" in joined_messages:
            repair_hints.append(
                "for short_genre_prompt_prop_too_early, rebuild the opening before any memory proof: make today's practical action fail and change the next move, then let only one mother/egg/rain/message trace leak in; do not open with the prompt-prop inventory"
            )
        if "short_genre_complete_article_buffer=" in joined_messages or "short_genre_short_line_grid=" in joined_messages:
            repair_hints.append(
                "for short-genre completion/rhythm, do not expand into standard diary or split into tiny rows; rebuild with uneven movement, several longer clumsy action/memory/reply lines, and one practical consequence that changes the next move"
            )
        if "short_genre_body_lines=" in joined_messages or "short_genre_prose_block_compression=" in joined_messages:
            repair_hints.append(
                "for short-genre prose compression, do not add one more paragraph; rewrite the visible page into uneven movement, preserving punctuation at line ends and using a few longer clumsy lines plus short factual retreats"
            )
        if "short_genre_period_grid=" in joined_messages:
            repair_hints.append(
                "for short_genre_period_grid, stop writing closed sentence rows. Rebuild 4-7 breathing clusters: let one action/reply line run on with a line-final comma, keep one longer clumsy line, then land a short fact-retreat; remove `后来/已经/当时` glue instead of only changing punctuation"
            )
        if "short_genre_literary_story_closure=" in joined_messages:
            repair_hints.append(
                "for short_genre_literary_story_closure, cut one proof family completely rather than making every family shorter: a childhood-rain/raincoat/school line is still a full memory prop, and an eggs/plastic-bag/home-trip line is still a full object-memory prop. Keep one visible pressure family, let at most one other become a partial residue, and do not preserve no-message + eggs + childhood-rain as the same designed argument"
            )
        if "short_genre_local_packet_loop=" in joined_messages:
            repair_hints.append(
                "for short_genre_local_packet_loop, do not extend by repeating the same phone/message/bowl/water/oil packet. Delete one repeated packet, then either restart from a different present action or add one consequence that changes reply, room position, body, or next action; do not keep counting lines and appending the same tail"
            )
        if "short_genre_repair_stuffing=" in joined_messages:
            repair_hints.append(
                "for short_genre_repair_stuffing, delete the new food/gift/media packet and repair rhythm inside the existing object-message-room material; do not add delivery, branded food, gift boxes, video teaching, or variety-show texture to make the short genre look thicker"
            )
        if "short_genre_present_action_anchor=" in joined_messages:
            repair_hints.append(
                "for short_genre_present_action_anchor, abandon the existing memory-first spine rather than adding one more practical detail: choose a new side-action title and restart from today's practical interruption before the mother-memory proof. Make a room, body, door, reply, neighbor, or chore problem change the next action, keep at most one egg/rain/message trace, and let that trace leak from the action instead of carrying the argument"
            )
        if "short_genre_main_prop_title_loop=" in joined_messages:
            repair_hints.append(
                "for short_genre_main_prop_title_loop, do not keep a title like `鸡蛋` or `一袋鸡蛋` while the body and tail use that prop as proof. Retitle from a side action, wrong chore, sleeve, door, reply, or other low-status handle; if the prompt prop remains in the body, the ending must leave through a different practical action"
            )
    if f"> {STANDARD_DIARY_DRAFT_OVERFULL_CHARS}" in joined_messages:
        repair_hints.append(
            "for overfilled length, cut unsupported/non-consequential texture after the visible shape is stable; do not add more body, screen, route, or money proof"
        )
    if "early_comma_ratio=" in joined_messages:
        repair_hints.append(
            "for early_comma_ratio, treat the first page as closed sentence-row prose. Repair only the smallest local movements whose action or thought is falsely sealed: let a row run on with `，` only when the next row completes it, keep rough longer movement where it already belongs, and preserve landed rows instead of stamping a three-part cluster template"
        )
        if "rough_self_damage=missing" in joined_messages or underbuilt_source or near_miss_short:
            repair_hints.append(
                "for early_comma_ratio combined with content repairs, make the content repair first, then run "
                "`python <skill-dir>/scripts/soften_line_endings.py draft.md --in-place` as the last action before "
                "the wrapper; if you edit draft.md after that script, rerun the script before checking"
            )
        else:
            repair_hints.append(
                "for early_comma_ratio, run `python <skill-dir>/scripts/soften_line_endings.py draft.md --in-place` "
                "before the wrapper; if you edit draft.md after that script, rerun the script before checking"
            )
    if "rough_self_damage=missing" in joined_messages:
        repair_hints.append(
            "for rough_self_damage, replace one private or polite packet with one losing-face body/social consequence; pain or heat alone is too "
            "polite, and so are mirror face, private oil stains, burps, hair, or clothes"
        )
    if "private_grime_without_public_consequence=" in joined_messages:
        repair_hints.append(
            "for private_grime_without_public_consequence, do not add another stain, mirror check, burp, hair, smell, or sleeve detail. Make the existing grime produce a visible practical or social consequence: another person waits/asks/points/holds/returns, payment stalls, the door closes wrong, the bag leaks in the handoff, the narrator drops/wipes/hides/fails to answer, or cut the grime packet"
        )
    if "social_decline_plain_reply_private_loop=" in joined_messages:
        repair_hints.append(
            "for social_decline_plain_reply_private_loop, an OK/plain response plus a private screen mark is still a screen loop. Rebuild the refusal aftermath so the reply changes a visible next action: a worse small reply, door waiting, payment/route stall, someone asking/pointing/waiting, or a body/door/object problem altered while pressure is live"
        )
    if "social_decline_group_fake_consequence=" in joined_messages:
        repair_hints.append(
            "for social_decline_group_fake_consequence, do not repair a refusal with `群里有人问`, `有人@我`, `你怎么说`, or `正在输入` as a public crowd scene. Cut the group-chat summary and make one local consequence change the next action: a smaller reply, a payment/route stall, one person waiting/asking, or a wet/dirty hand/body/door problem while the refusal pressure is still live"
        )
    if "social_decline_tidy_etiquette_closure=" in joined_messages:
        repair_hints.append(
            "for social_decline_tidy_etiquette_closure, do not close the refusal with narrator red-packet apology, `人不到钱到`, `人不到没事`, `下次一起吃饭`, or `心意到了`. Remove the polite moral settlement and leave through unfinished reply, route/payment hesitation, old debt, body/door trouble, or a lower practical residue"
        )
    if "social_decline_decoupled_consequence=" in joined_messages:
        repair_hints.append(
            "for social_decline_decoupled_consequence, do not use unrelated delivery, food burn, room chores, errands, or generic ugly texture as the refusal aftermath. Rebuild one consequence that depends on not going: the reply/payment/route stalls, someone waits while the answer is unfinished, a dirty/wet hand changes the reply, or an old debt/body/door problem changes the next action"
        )
    if "bare_line_grid=" in joined_messages:
        repair_hints.append(
            "for bare_line_grid, keep sentence punctuation and merge naked caption rows into action/reply/thought lines; do not create lineation by stripping punctuation"
        )
    if title_issue:
        repair_hints.append(
            "for missing_title, add a standalone first-line title chosen from the completed side action; do not use a date, holiday label, `标题：`, or a sentence that is actually the first body line"
        )
    if "binary_reframe=present" in joined_messages:
        repair_hints.append(
            "for binary_reframe, scan every line and remove all occurrences; replace each not-X/is-Y move with the physical fact, money action, or ugly reply already in that scene"
        )
    if "em_dash=present" in joined_messages:
        repair_hints.append(
            "for em_dash, replace each `——` with a comma, line break, action, or plain speech fragment; do not use dash as an explanation hinge"
        )
    if "standard_prompt_prop_title=" in joined_messages:
        repair_hints.append(
            "for standard_prompt_prop_title, retitle from a side consequence already in the draft, not from the prompt prop such as 备注、香菜、礼物、朋友圈 or 优惠券"
        )
    if "prompt_performing_dialogue=present" in joined_messages:
        repair_hints.append(
            "for prompt_performing_dialogue, stop letting a stranger or vendor recite identity, school, city, salary, or success-comparison facts; lower it to one rough side remark and carry the damage through payment, object handling, dirty hands, body noise, route, or a failed reply"
        )
    if "learned_ending_button=present" in joined_messages:
        repair_hints.append(
            "for learned_ending_button, replace the tail button with an unfinished practical action, wrong object, payment, route, reply, or body interruption already earned by the scene"
        )
    if "pure_ambient_ending=present" in joined_messages:
        repair_hints.append(
            "for pure_ambient_ending, do not fade out on light, wind, appliance noise, or screen glow. End on the already-earned unfinished action, wrong object, route/payment/reply, or body interruption that the scene forced"
        )
    if "quoted_dialogue=present" in joined_messages:
        repair_hints.append(
            "for quoted_dialogue, remove theatrical quote marks and keep at most one embedded speech surface; let payment, object handling, body noise, dirty hands, or an unfinished reply carry the encounter"
        )
    if "literary_simile_caption=present" in joined_messages:
        repair_hints.append(
            "for literary_simile_caption, delete the explanatory simile and keep the physical fact or next action; do not replace it with another prettier metaphor"
        )
    anti_todo_guard = (
        " Do not summarize, quote, or enumerate these diagnostics as a TODO list. "
        "Do not write process notes such as 'the checker requires' or solve one item per metric; "
        "change scene movement, rhythm, or local surface only."
    )
    hint_text = " Prioritized repair: " + " | ".join(repair_hints) + "." if repair_hints else ""
    if surface_only:
        revision_frame = (
            "Revise locally: scan the whole draft for every flagged surface and remove or lower all occurrences. "
            "Keep the existing title, approximate mass, and fragment slate unless a local relation breaks; do not add new scenes, "
            "short drops, body symptoms, money lines, platform facts, or other texture just because a surface gate fired; "
            "then run this wrapper again."
        )
    else:
        if mixed_rebalance_source:
            if severely_underbuilt:
                revision_frame = (
                    "Rebuild the incomplete source before rhythm tools: do not run the rhythm reset as the first move when the same preflight "
                    "also names source/content blockers. Rebuild from the strongest fragment, preserve a complete article, "
                    "and do not append diagnostic proof packets; then run the named rhythm "
                    "reset once as the final shape step before the next wrapper call."
                )
            elif short_of_full_article:
                revision_frame = (
                    "Replace the broken fragment or relation before rhythm tools: do not run the rhythm reset as the first move when the same "
                    "preflight also names connector, engine, roughness, dialogue, opening, or refusal/source blockers. Preserve the complete article "
                    "across the replacement and neighboring existing movements, then run the named rhythm reset once as "
                    "the final shape step before the next wrapper call."
                )
            else:
                revision_frame = (
                    "Replace the broken fragment or relation before rhythm tools: do not run the rhythm reset as the first move when the "
                    "same preflight also names connector, engine, roughness, dialogue, opening, or refusal/source blockers. "
                    "Preserve the complete article, then run the named rhythm reset "
                    "once as the final shape step before the next wrapper call."
                )
        elif compressed_shape:
            revision_frame = (
                "Reset the visible shape first, then repair the source: do not mentally estimate a line quota and do "
                "not rewrite another prose block. Run the rhythm reset named below, inspect the actual draft, then "
                "rewrite only within the existing article shape, preserving the thought movement."
            )
        elif overfragmented_shape:
            revision_frame = (
                "Reset the short-line grid before content rewriting: run the rhythm reset named below, inspect the "
                "actual body rows, then regroup existing movement inside that corridor into several longer action/speech/thought lines and "
                "earned short breath drops. Preserve the existing fragments and consequence material; do not answer this by writing a new "
                "caption grid, a prose block, or an added proof scene."
            )
        elif "social_decline_plain_reply_private_loop=" in joined_messages:
            revision_frame = (
                "Reset the refusal-aftermath source: do not keep `he said OK -> private screen/water mark -> room object`. "
                "Delete one room/screen packet and rebuild the next cluster so the ordinary response changes hand, reply, "
                "payment, route, door, body, or social position before the article exits the chat."
            )
        elif "social_decline_decoupled_consequence=" in joined_messages:
            revision_frame = (
                "Reset the refusal-coupled consequence: remove the delivery/burn/chore/errand scene if it would still "
                "work without the invitation, then rebuild the next cluster so not going changes reply, payment, route, "
                "door, dirty hand, old debt, body, or social position before the article exits the chat."
            )
        elif underbuilt_source:
            if severely_underbuilt:
                revision_frame = (
                    "Rebuild the incomplete source, not just the metric: keep the strongest fragment, preserve a complete article, and do not append isolated symptoms, app "
                    "lines, or checker-shaped proof packets to the fragment; then run this wrapper again."
                )
            else:
                mass_action = (
                    "preserve the complete article across the replacement and neighboring existing movements"
                    if short_of_full_article
                    else "preserve complete article"
                )
                revision_frame = (
                    "Replace the weak fragment relation, not just the metric: keep useful existing facts, replace one overloaded or repeated "
                    "fragment in place, and let the next thought or action change direction. "
                    f"{mass_action.capitalize()} instead of adding isolated symptoms, app lines, or short captions; then run this wrapper again."
                )
        elif standard_prompt_loop:
            revision_frame = (
                "Reset the standard-diary source loop: the title/opening/tail are all obeying the same prompt prop. "
                "Retitle from a side consequence, cut one visible prompt-prop packet, rebuild the middle through a "
                "practical or social consequence, then run this wrapper again. Do not merely replace the title word."
            )
        elif "high_signal_opening=present" in joined_messages or "feed_inventory_opening=present" in joined_messages:
            revision_frame = (
                "Reset the opening source: do not begin with the prompt topic, feed list, holiday label, gift surface, "
                "wrong-food prop, or inventory of screenshots/posts. Start from a body/room/payment/door/sink/charger "
                "action that would still exist without the assignment, then let one cropped prompt surface leak later "
                "and change the next action."
            )
        elif "soft_witness_no_consequence=present" in joined_messages:
            revision_frame = (
                "Reset the outside-contact source: a look from another person is not movement unless it changes "
                "payment, reply, object state, door speed, dirty hand/clothing exposure, or the next action. Rebuild "
                "the handoff as a consequence or remove it instead of preserving a silent witness."
            )
        elif any(message.startswith("connectors=") for message in messages):
            revision_frame = (
                "Replace one inert connector-bearing fragment relation inside the existing slate: change what an existing action does next (or what an existing thought does next) so the "
                "turn earns a natural connector. Do not add a new scene, material family, proof packet, or visible connector checklist; then run "
                "this wrapper again."
            )
        elif "period_row_grid=present" in joined_messages or "early_comma_ratio=" in joined_messages:
            revision_frame = (
                "Reset the sentence-row rhythm source: the opening page is made of closed `。` rows. Repair only the "
                "smallest local movement that is actually broken and choose the one relation that movement actually needs: "
                "continuation, hard landing, rough longer movement, or short failed retreat. Do not stamp all four into a "
                "cluster, flip three periods into commas, or paste a new metric-shaped first paragraph."
            )
        elif underbuilt_short_genre:
            revision_frame = (
                "Rebuild the short-genre source, not a length target: restart "
                "from a current practical interruption or awkward reply that changes the next action, keep several "
                "longer clumsy lines, use a side-action title, and drop or bury the old title-object/memory proof "
                "instead of arranging it better before running this wrapper again."
            )
        elif title_issue:
            revision_frame = (
                "Repair the article artifact first: add a standalone title line, then keep the body as article text. "
                "The title should come from a side action or object that the body earns, not from the date, holiday, "
                "test prompt, or a body sentence promoted to title."
            )
        else:
            revision_frame = (
                "Revise toward a complete but not overfilled article: write a line-broken article first, use "
                "rebalance_line_rhythm.py for prose-block or short-grid drift, keep punctuation at line endings, replace or deepen the weakest "
                "existing movement when short, and cut unsupported/non-consequential texture when long. Do not append metric-shaped material; "
                "then run this wrapper again."
            )
    return repair_hints, revision_frame


def post_checker_preflight_before_second_check(
    draft: Path,
    state: dict[str, Any],
    *,
    state_path: Path,
    calls: int,
    generator_facing: bool = False,
) -> tuple[bool, list[str]]:
    messages = post_checker_blocking_messages(draft, preflight_messages(draft))
    if not messages or ignorable_preflight_messages(messages):
        return False, []
    post_attempt = int(state.get("post_checker_preflights", 0)) + 1
    joined_messages = "; ".join(messages)
    state["post_checker_preflights"] = post_attempt
    state["last_post_checker_preflight_messages"] = messages
    record_snapshot(draft, state, f"post_checker_preflight_{post_attempt}", overwrite=True)
    if post_attempt > 1:
        state["calls"] = calls
        state["stopped"] = True
        state["stop_reason"] = "post-checker-preflight"
        record_snapshot(draft, state, "bounded_final", overwrite=True)
        save_stop_state(state_path, draft, state)
        stop_text = (
            "CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY after post-check preflight. "
            "The draft was still not ready for checker call 2/2 after the one bounded source-or-shape action. "
            "DO NOT WRITE draft.md. DO NOT REPAIR. Read draft.md once and output it unchanged. "
            "No second checker call was consumed."
        )
        if generator_facing:
            stop_text += " " + generator_facing_contract(stopped=True)
        print(stop_text)
        return True, messages
    repair_hints, revision_frame = build_preflight_guidance(messages)
    source_prefixes = (
        "connectors=",
        "paragraph_engine=weak",
        "rough_self_damage=missing",
        "private_grime_without_public_consequence=",
        "social_decline_plain_reply_private_loop=",
        "social_decline_group_fake_consequence=",
        "social_decline_tidy_etiquette_closure=",
        "social_decline_decoupled_consequence=",
    )
    source_blocked = any(message.startswith(source_prefixes) for message in messages) or any(
        message.startswith("body_chinese_chars=") and "<" in message for message in messages
    )
    overfull = any(message.startswith("body_chinese_chars=") and ">" in message for message in messages)
    connector_only = bool(messages) and all(message.startswith("connectors=") for message in messages)
    reported_body_chars = reported_standard_body_chars(messages)
    severely_underbuilt = (
        reported_body_chars is not None and reported_body_chars < STANDARD_DIARY_FORMAL_MIN_CHARS
    )
    short_of_full_article = (
        reported_body_chars is not None and reported_body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS
    )
    if overfull:
        postcheck_source_note = (
            "Post-check overfull reset: the wrapper left `draft.md` unchanged. "
            "Do not add a new scene, consequence cluster, or material packet. "
            "Use the printed trim/shape action to remove or replace repeated material while preserving the article's working movement, "
            "then call this wrapper again."
        )
    elif connector_only:
        postcheck_source_note = (
            "Post-check connector reset: the wrapper left `draft.md` unchanged. Replace one inert connector-bearing movement inside the existing "
            "fragment slate so an existing thought or action changes direction. Do not add a scene, material family, or new prompt packet, "
            "or invitation/refusal repair branch; then call this wrapper again."
        )
    elif source_blocked and severely_underbuilt:
        postcheck_source_note = (
            "Post-check source reset: do not spend checker call 2/2 on a severely incomplete source. "
            "Rebuild from the strongest fragment, preserve a complete article, and do not add material for a metric or append checker-shaped proof packets. After the content rewrite, run any needed rhythm script only as the "
            "final shape step, then call this wrapper again."
        )
    elif source_blocked:
        mass_action = (
            "preserve the complete article across the replacement and neighboring existing movements"
            if short_of_full_article
            else "preserve the complete article"
        )
        postcheck_source_note = (
            "Post-check source reset: do not spend checker call 2/2 on a known underbuilt source. "
            f"Rewrite by replacing one broken fragment relation in place, not by adding a packet; do not add material for a metric: {mass_action}. "
            "For social-decline or invitation cases, keep the prompt as one fragment and do not append a consequence subplot. "
            "After the content rewrite, run any needed rhythm script only as the final shape step, then call this wrapper again."
        )
    else:
        postcheck_source_note = (
            "Post-check shape reset: the wrapper left `draft.md` unchanged. "
            "Do not add a new scene, consequence cluster, or material packet for a pure shape result. "
            "Perform only the explicit local rhythm action printed below, then call this wrapper again."
        )
    hint_text = " Prioritized repair: " + " | ".join(repair_hints[:4]) + "." if repair_hints else ""
    state["calls"] = calls
    save_state(state_path, state)
    if generator_facing:
        labels, action = generator_facing_summary(messages)
        print(
            "CLEAN_RUN_POSTCHECK_PREFLIGHT: qualitative source review before checker call 2/2; "
            f"findings={','.join(labels)}; {action}; {generator_facing_contract(action)}. "
            "This post-check preflight did not consume checker call 2/2."
        )
    else:
        print(
            "CLEAN_RUN_POSTCHECK_PREFLIGHT: draft is not ready for checker call 2/2; "
            + joined_messages
            + ". "
            + postcheck_source_note
            + " "
            + revision_frame
            + hint_text
            + " This post-check preflight did not consume checker call 2/2."
        )
    return True, messages


def post_checker_blocking_messages(draft: Path, messages: list[str]) -> list[str]:
    """Return only preflight messages worth blocking checker call 2/2 for.

    The first preflight deliberately lets some near-miss drafts reach checker call
    1/2 so the bounded protocol can measure limited repair. After that first
    checker, do not spend call 2/2 on a draft that has already shrunk below the
    standard corridor, still lacks source movement, or still has a known hard
    shape failure. The wrapper must leave the submitted artifact byte-for-byte
    unchanged; any rhythm repair is an explicit generator action before call 2.
    """
    text = draft.read_text(encoding="utf-8")
    style = detect_style(text)
    _, content_lines = split_title_and_content_lines(text.splitlines())
    visible_lines = [line for line in content_lines if line.strip() and not line.strip().startswith("<!--")]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    connectors = [term for term in HIGH_FREQUENCY_TERMS if term in body]
    blocking: list[str] = []
    for message in messages:
        if message.startswith("body_chinese_chars="):
            blocking.append(message)
        elif message.startswith("medium_short_line_grid="):
            blocking.append(message)
        elif message.startswith(
            (
                "body_lines=",
                "long_lines=",
                "short_breath_lines=",
                "period_row_grid=",
                "short_line_grid=",
                "bare_line_grid=",
                "prose_block_shape=",
                "early_comma_ratio=",
            )
        ):
            blocking.append(message)
        elif message.startswith(
            (
                "private_grime_without_public_consequence=",
                "social_decline_plain_reply_private_loop=",
                "social_decline_group_fake_consequence=",
                "social_decline_tidy_etiquette_closure=",
                "social_decline_decoupled_consequence=",
            )
        ):
            blocking.append(message)
    return blocking


def main() -> int:
    parser = argparse.ArgumentParser(description="Run anlin-writing draft checker with a two-call clean-eval limit.")
    parser.add_argument("draft", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--draft-gate", action="store_true")
    parser.add_argument("--corpus-dir", type=Path, default=None)
    parser.add_argument("--genre", default=None, help="Optional clean-eval genre lock: standard, sincere, micro-hope, or surreal")
    parser.add_argument("--fail-on-warning", action="store_true")
    parser.add_argument("--state", type=Path, default=None)
    parser.add_argument("--reset", action="store_true")
    parser.add_argument(
        "--generator-facing",
        action="store_true",
        help="Hide exact preflight telemetry from the bounded generator; keep raw messages in state for controller diagnostics.",
    )
    args = parser.parse_args()
    try:
        set_forced_genre(args.genre)
    except ValueError as error:
        parser.error(str(error))

    draft = args.draft.resolve()
    if not draft.is_file():
        parser.error(f"draft not found: {draft}")
    generator_facing = args.generator_facing or (draft.parent / ".anlin-clean-eval-mode").exists()
    if args.reset:
        try:
            stop_lock_path(draft).unlink()
        except FileNotFoundError:
            pass
    state_path = args.state or (draft.parent / ".anlin-clean-run-state.json")
    state_path = state_path.resolve()
    state = {} if args.reset else load_state(state_path)
    draft_key = str(draft)
    locked_state = {} if args.reset else load_stop_lock(draft)
    if locked_state:
        state = locked_state
    if state.get("draft") != draft_key:
        state = {"draft": draft_key, "calls": 0, "preflights": 0}
    state.update(standard_length_evidence(draft))
    state["generator_facing"] = generator_facing
    if not state.get("stopped"):
        record_snapshot(draft, state, "first_submission")
    calls = int(state.get("calls", 0))
    preflights = int(state.get("preflights", 0))
    if state.get("stopped") or (calls == 0 and preflights >= 3):
        state["stopped"] = True
        state.setdefault("stop_reason", "preflight")
        snapshots = state.setdefault("snapshots", {})
        bounded_snapshot = snapshots.get("bounded_final")
        if not bounded_snapshot or not Path(str(bounded_snapshot)).is_file():
            record_snapshot(draft, state, "bounded_final", overwrite=False)
        stopped_hash = state.get("stopped_draft_sha256")
        current_hash = file_sha256(draft)
        mutated = bool(stopped_hash and current_hash != stopped_hash)
        if mutated:
            state["post_stop_mutation_detected"] = True
        save_stop_state(state_path, draft, state)
        mutation_note = (
            " WARNING: draft.md was modified after the clean-eval stop boundary; "
            "do not treat the current file as the bounded checkpoint. The controller should use the frozen bounded_final snapshot."
            if mutated
            else ""
        )
        print(
            "CLEAN_RUN_STOP: FINAL BOUNDARY already reached for this draft. "
            "DO NOT WRITE draft.md. DO NOT REPAIR. Do not switch to the normal checker in this directory. "
            "The next tool action must be reading draft.md once and outputting it unchanged; use a separate finalized checkpoint directory for ordinary repair."
            + mutation_note
        )
        return 0
    if calls >= 2:
        state["stopped"] = True
        state["stop_reason"] = "checker-limit"
        record_snapshot(draft, state, "bounded_final", overwrite=True)
        save_stop_state(state_path, draft, state)
        print(
            "CLEAN_RUN_STOP: FINAL BOUNDARY, checker call limit already reached for this draft. "
            "DO NOT WRITE draft.md. Do not run another checker or repair command. Read draft.md once and output it unchanged."
        )
        return 0
    if args.draft_gate and calls == 0:
        preflight_attempt = int(state.get("preflights", 0)) + 1
        max_preflight_attempts = 3
        record_snapshot(draft, state, f"preflight_{preflight_attempt}", overwrite=True)
        blocked, messages = preflight_before_check(
            draft,
            calls + 1,
            attempt=preflight_attempt,
            max_attempts=max_preflight_attempts,
            generator_facing=generator_facing,
        )
        if blocked:
            state["preflights"] = min(preflight_attempt, max_preflight_attempts)
            state["last_preflight_messages"] = messages
            if preflight_attempt >= max_preflight_attempts:
                state["stopped"] = True
                state["stop_reason"] = "preflight"
                record_snapshot(draft, state, "bounded_final", overwrite=True)
            if state.get("stopped"):
                save_stop_state(state_path, draft, state)
            else:
                save_state(state_path, state)
            return 0 if preflight_attempt >= max_preflight_attempts else 3

    call_number = calls + 1
    if args.draft_gate and call_number == 2:
        blocked, _messages = post_checker_preflight_before_second_check(
            draft,
            state,
            state_path=state_path,
            calls=calls,
            generator_facing=generator_facing,
        )
        if blocked:
            return 0 if state.get("stopped") else 3

    state["calls"] = call_number
    state["preflights"] = int(state.get("preflights", 0))
    record_snapshot(draft, state, f"checker_call_{call_number}_submission", overwrite=True)
    save_state(state_path, state)

    command = [sys.executable, str(CHECKER), str(draft)]
    if args.strict:
        command.append("--strict")
    if args.draft_gate:
        command.append("--draft-gate")
    if args.genre:
        command.extend(["--genre", args.genre])
    if args.corpus_dir is not None:
        command.extend(["--corpus-dir", str(args.corpus_dir)])
    if args.fail_on_warning:
        command.append("--fail-on-warning")

    if generator_facing:
        result = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        print(generator_facing_checker_output(result.stdout, result.stderr))
        state = load_state(state_path)
        state["generator_facing"] = True
        state["last_checker_call"] = call_number
        state["last_checker_returncode"] = result.returncode
        state["last_checker_stdout"] = result.stdout
        state["last_checker_stderr"] = result.stderr
        save_state(state_path, state)
    else:
        result = subprocess.run(command, text=True, encoding="utf-8", check=False)
    if call_number == 2:
        state = load_state(state_path)
        state["draft"] = draft_key
        state["calls"] = call_number
        state["preflights"] = int(state.get("preflights", 0))
        state["stopped"] = True
        state["stop_reason"] = "checker-limit"
        record_snapshot(draft, state, "bounded_final", overwrite=True)
        save_stop_state(state_path, draft, state)
        print(
            "CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2. "
            "DO NOT WRITE draft.md. Do not edit, split, merge, compare, or run another checker. "
            "Read draft.md once and output it unchanged, even if errors remain."
        )
        return 0
    else:
        print("CLEAN_RUN_NOTE: checker call 1/2. One repair pass remains before final output.")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

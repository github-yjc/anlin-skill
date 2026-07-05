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
sys.path.insert(0, str(ROOT / "scripts"))
from check_anlin_violations import (  # noqa: E402
    BACKGROUND_DISPLAY_GROUPS,
    ENGINE_SIGNAL_PATTERNS,
    ENGINE_SIGNAL_TERMS,
    PROCESS_LEAK_TERMS,
    HIGH_FREQUENCY_TERMS,
    LEARNED_ENDING_LINES,
    ROUGH_SELF_DAMAGE_PATTERNS,
    ROUGH_SELF_DAMAGE_TERMS,
    STANDARD_DIARY_DRAFT_OVERFULL_CHARS,
    chinese_len,
    comment_chain_formula_hits,
    current_office_persona_hits,
    detect_style,
    meta_ai_topic_hits,
    prompt_performing_dialogue_hits,
    short_genre_literary_story_risk,
    short_genre_present_action_anchor_risk,
    short_genre_prompt_prop_too_early_risk,
    short_genre_repair_stuffing_groups,
    split_title_and_content_lines,
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


def stop_lock_path(draft: Path) -> Path:
    digest = hashlib.sha256(str(draft.resolve()).encode("utf-8")).hexdigest()
    return Path(tempfile.gettempdir()) / "anlin-clean-run-locks" / f"{digest}.json"


def save_stop_state(state_path: Path, draft: Path, state: dict[str, Any]) -> None:
    save_state(state_path, state)
    lock_path = stop_lock_path(draft)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    save_state(lock_path, state)


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
    shutil_text = draft.read_text(encoding="utf-8")
    path.write_text(shutil_text, encoding="utf-8", newline="\n")
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
        or (body_chars >= 900 and mean_line >= 42)
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
    quote_matches = quoted_dialogue_matches(lines)
    if quote_matches:
        examples = " | ".join(f"L{line_no}:{excerpt[:42]}" for line_no, excerpt in quote_matches[:3])
        messages.append(f"quoted_dialogue=present count={len(quote_matches)} examples={examples}")
    simile_matches = literary_simile_caption_matches(lines)
    if simile_matches:
        examples = " | ".join(f"L{line_no}:{excerpt[:42]}" for line_no, excerpt in simile_matches[:3])
        messages.append(f"literary_simile_caption=present count={len(simile_matches)} examples={examples}")
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
        if body_line_count < 8:
            messages.append(f"{style}_body_lines={body_line_count} < 8")
        if body_chars < 520:
            messages.append(
                f"short_genre_underbuilt_complete_article=style:{style}, body_chars={body_chars} < 520"
            )
        if body_chars < 650 and body_line_count >= 18 and long_line_count == 0:
            messages.append(
                f"short_genre_no_long_clumsy_lines=style:{style}, body_lines={body_line_count}, long_lines={long_line_count}"
            )
        if body_chars >= 520 and (body_line_count <= 20 or mean_line >= 32 or comma_ratio < 0.08):
            messages.append(
                f"short_genre_prose_block_compression=style:{style}, body_lines={body_line_count}, mean_line={mean_line:.1f}, early_comma_ratio={comma_ratio:.2f}"
            )
        normalized_title = re.sub(r"[\s#]+", "", title)
        if re.search(r"(?:母亲节|五月十二日|5月12日|五月十二|520)", normalized_title):
            messages.append(f"short_genre_diagnostic_date_title={normalized_title}")
        short_story_risk = short_genre_literary_story_risk(text.splitlines(), text)
        if short_story_risk:
            messages.append(
                "short_genre_literary_story_closure="
                + json.dumps(short_story_risk, ensure_ascii=False)
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
    source_shape_weak = (
        body_line_count < 45
        or body_line_count > 90
        or (45 <= body_line_count <= 75 and long_line_count < 6)
        or (len(first_twenty) >= 8 and comma_ratio < 0.15)
        or len(connectors) < 3
        or len(engine_hits) < 3
        or (not rough_terms and not rough_patterns)
    )
    if body_chars < 900:
        messages.append(f"body_chinese_chars={body_chars} < 900")
    elif body_chars < 950 and source_shape_weak:
        messages.append(f"body_chinese_chars={body_chars} < 950 with source_shape_weak")
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
    if 45 <= body_line_count <= 75 and body_chars < 950 and long_line_count < 6:
        messages.append(
            f"medium_short_line_grid=present (long_lines={long_line_count} < 6, line_stdev={line_stdev:.1f}; "
            "rewrite rough action/speech/thought lines before checking)"
        )
    if body_line_count >= 45 and short_breath_count < 4:
        messages.append(
            f"short_breath_lines={short_breath_count} < 4 (keep a few <=8-Chinese-character breath drops; do not make every line a finished caption)"
        )
    if body_line_count >= 70 and short_line_ratio >= 0.45:
        messages.append(f"short_line_grid={short_line_ratio:.2f} (do not create line breaks by deleting punctuation)")
    if body_chars >= 900 and (body_line_count <= 20 or mean_line >= 42 or long_line_count >= max(6, int(body_line_count * 0.65))):
        messages.append(
            f"prose_block_shape=compressed (body_lines={body_line_count}, mean_line={mean_line:.1f}, long_lines={long_line_count})"
        )
    if len(first_twenty) >= 8 and comma_ratio < 0.15:
        messages.append(f"early_comma_ratio={comma_ratio:.2f} < 0.15")
    if len(connectors) < 3:
        messages.append(f"connectors={connectors} < 3")
    if len(engine_hits) < 3:
        messages.append("paragraph_engine=weak (add a scene-level misread, bodily interruption, social wound, or ugly self-own; do not inspect checker source/tests)")
    if not rough_terms and not rough_patterns:
        messages.append("rough_self_damage=missing (add one organic ugly body/social/self-own consequence in your own words; do not inspect checker source/tests)")
    messages.extend(surface_preflight_messages(article_lines, "\n".join(article_lines)))
    return messages


def preflight_before_check(draft: Path, call_number: int, *, attempt: int, max_attempts: int) -> tuple[bool, list[str]]:
    messages = preflight_messages(draft)
    if not messages:
        return False, []
    joined_messages = "; ".join(messages)
    repair_hints: list[str] = []
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
    )
    surface_only = all(message.startswith(surface_only_prefixes) for message in messages)
    compressed_shape = any("< 45" in message or "prose_block_shape=compressed" in message for message in messages)
    overfragmented_shape = any(
        "> 90" in message
        or "short_line_grid=" in message
        or "long_lines=" in message
        or "medium_short_line_grid=" in message
        for message in messages
    )
    underbuilt_short_genre = any(
        message.startswith("short_genre_underbuilt_complete_article=")
        or message.startswith("short_genre_no_long_clumsy_lines=")
        or message.startswith("short_genre_prose_block_compression=")
        or message.startswith("short_genre_diagnostic_date_title=")
        or message.startswith("short_genre_repair_stuffing=")
        or message.startswith("short_genre_present_action_anchor=")
        or message.startswith("short_genre_prompt_prop_too_early=")
        for message in messages
    )
    title_issue = any(message.startswith("missing_title=") for message in messages)
    missing_breath = any("short_breath_lines=" in message for message in messages)
    near_miss_short = (
        any("body_lines=" in message and "< 45" in message for message in messages)
        or any(message.startswith("body_chinese_chars=") and ("< 900" in message or "< 950" in message) for message in messages)
    ) and "connectors=" in joined_messages
    underbuilt_source = any(
        message.startswith("body_chinese_chars=") and ("< 900" in message or "< 950" in message) for message in messages
    ) and any(
        key in joined_messages
        for key in (
            "medium_short_line_grid=",
            "paragraph_engine=weak",
            "rough_self_damage=missing",
            "early_comma_ratio=",
        )
    )
    if compressed_shape:
        repair_hints.append(
            "NEXT_ACTION=run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place` before any new prose rewrite; "
            "then inspect the actual visible line count and rewrite only inside that line-broken shape"
        )
    if underbuilt_source:
        repair_hints.append(
            "for an underbuilt source shape, do a source-loop rewrite after the visible shape is reset: "
            "start from friction, add one off-axis consequence and one rough body/social turn, then write "
            "near 55-68 actual body lines and 950-1150 Chinese characters; do not patch with isolated line additions"
        )
    if near_miss_short:
        repair_hints.append(
            "for a near-miss short draft, add one full off-axis life cluster of 6-10 visible lines that changes action and creates new connector turns; do not add a single explanatory paragraph or one decorative symptom"
        )
    if overfragmented_shape:
        repair_hints.append(
            "for short-grid drift, overfragmented grids, or too few long lines, run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place`; do not rewrite into many tiny rows or 30-line prose blocks"
        )
    if missing_breath:
        repair_hints.append(
            "for short_breath_lines, add a few real <=8-character drops such as an ugly reply, failed decision, or small retreat; do not add decorative one-word captions"
        )
    if underbuilt_short_genre:
        repair_hints.append(
            "for a short-genre source failure, do not solve by deleting memory or shrinking further; rewrite into 4-7 uneven clusters, keep a few longer clumsy lines, add one present practical cluster that changes action or reply, use a side-action title, and discard or bury one prompt-supplied family prop instead of preserving every prompt noun"
        )
        if "short_genre_prompt_prop_too_early=" in joined_messages:
            repair_hints.append(
                "for short_genre_prompt_prop_too_early, rebuild the first 8-12 body lines before any memory proof: make today's practical action fail and change the next move, then let only one mother/egg/rain/message trace leak in; do not open with the prompt-prop inventory"
            )
        if "short_genre_repair_stuffing=" in joined_messages:
            repair_hints.append(
                "for short_genre_repair_stuffing, delete the new food/gift/media packet and repair rhythm inside the existing object-message-room material; do not add delivery, branded food, gift boxes, video teaching, or variety-show texture to make the short genre look thicker"
            )
        if "short_genre_present_action_anchor=" in joined_messages:
            repair_hints.append(
                "for short_genre_present_action_anchor, abandon the existing memory-first spine rather than adding one more practical detail: choose a new side-action title and restart from today's practical interruption before the mother-memory proof. Make a room, body, door, reply, neighbor, or chore problem change the next action, keep at most one egg/rain/message trace, and let that trace leak from the action instead of carrying the argument"
            )
    if f"> {STANDARD_DIARY_DRAFT_OVERFULL_CHARS}" in joined_messages:
        repair_hints.append(
            "for overfilled length, cut unsupported/non-consequential texture after the visible shape is stable; do not add more body, screen, route, or money proof"
        )
    if "early_comma_ratio=" in joined_messages:
        repair_hints.append(
            "for early_comma_ratio, run `python <skill-dir>/scripts/soften_line_endings.py draft.md --in-place` before hand editing; line-final commas must continue an action or thought"
        )
    if "rough_self_damage=missing" in joined_messages:
        repair_hints.append(
            "for rough_self_damage, add one losing-face body/social consequence; pain or heat alone is too polite"
        )
    if title_issue:
        repair_hints.append(
            "for missing_title, add a standalone first-line title chosen from the completed side action; do not use a date, holiday label, `标题：`, or a sentence that is actually the first body line"
        )
    if "binary_reframe=present" in joined_messages:
        repair_hints.append(
            "for binary_reframe, scan every line and remove all occurrences; replace each not-X/is-Y move with the physical fact, money action, or ugly reply already in that scene"
        )
    if "prompt_performing_dialogue=present" in joined_messages:
        repair_hints.append(
            "for prompt_performing_dialogue, stop letting a stranger or vendor recite identity, school, city, salary, or success-comparison facts; lower it to one rough side remark and carry the damage through payment, object handling, dirty hands, body noise, route, or a failed reply"
        )
    if "learned_ending_button=present" in joined_messages:
        repair_hints.append(
            "for learned_ending_button, replace the tail button with an unfinished practical action, wrong object, payment, route, reply, or body interruption already earned by the scene"
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
            "Keep the same length, rhythm, title, and scene slate unless a local sentence breaks; do not add new scenes, "
            "short drops, body symptoms, money lines, platform facts, or other texture just because a surface gate fired; "
            "then run this wrapper again."
        )
    else:
        if compressed_shape:
            revision_frame = (
                "Reset the visible shape first, then repair the source: do not mentally estimate 55-68 lines and do "
                "not rewrite another prose block. Run the rhythm reset named below, inspect the actual draft, then "
                "rewrite only within a 45-70-line article shape with a working middle."
            )
        elif underbuilt_source:
            revision_frame = (
                "Rebuild the article shape, not just the metric: keep only the useful scene facts, restart from "
                "the source loop, and rewrite `draft.md` as a complete line-broken article with a working middle. "
                "Do not add a few isolated symptoms, app lines, or short captions on top of the weak draft; then "
                "run this wrapper again."
            )
        elif underbuilt_short_genre:
            revision_frame = (
                "Rebuild the short-genre source, not the standard-diary length: keep 4-7 uneven clusters, restart "
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
                "rebalance_line_rhythm.py for prose-block or short-grid drift, keep punctuation at line endings, add "
                "concrete action/body/social/off-axis material only when short, or cut unsupported/non-consequential "
                "texture when long; then run this wrapper again."
            )
    if attempt >= max_attempts:
        print(
            f"CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY. DO NOT WRITE draft.md. DO NOT REPAIR. "
            "DO NOT RUN SCRIPTS. DO NOT USE PREFLIGHT DETAILS AS A TODO LIST. "
            "The next tool action must be reading draft.md once and outputting it unchanged. "
            "The controller has the saved state and snapshots and will diagnose this stopped bounded run. "
            "No checker call was consumed."
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run anlin-writing draft checker with a two-call clean-eval limit.")
    parser.add_argument("draft", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--draft-gate", action="store_true")
    parser.add_argument("--corpus-dir", type=Path, default=None)
    parser.add_argument("--fail-on-warning", action="store_true")
    parser.add_argument("--state", type=Path, default=None)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    draft = args.draft.resolve()
    if not draft.is_file():
        parser.error(f"draft not found: {draft}")
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
    if not state.get("stopped"):
        record_snapshot(draft, state, "first_submission")
    calls = int(state.get("calls", 0))
    preflights = int(state.get("preflights", 0))
    if state.get("stopped") or (calls == 0 and preflights >= 3):
        state["stopped"] = True
        state.setdefault("stop_reason", "preflight")
        record_snapshot(draft, state, "bounded_final", overwrite=True)
        save_stop_state(state_path, draft, state)
        print(
            "CLEAN_RUN_STOP: FINAL BOUNDARY already reached for this draft. "
            "DO NOT WRITE draft.md. DO NOT REPAIR. Do not switch to the normal checker in this directory. "
            "The next tool action must be reading draft.md once and outputting it unchanged; use a separate finalized checkpoint directory for ordinary repair."
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
    state["calls"] = call_number
    state["preflights"] = int(state.get("preflights", 0))
    if args.draft_gate and call_number == 2:
        normalize_before_final_check(draft)
    record_snapshot(draft, state, f"checker_call_{call_number}_submission", overwrite=True)
    save_state(state_path, state)

    command = [sys.executable, str(CHECKER), str(draft)]
    if args.strict:
        command.append("--strict")
    if args.draft_gate:
        command.append("--draft-gate")
    if args.corpus_dir is not None:
        command.extend(["--corpus-dir", str(args.corpus_dir)])
    if args.fail_on_warning:
        command.append("--fail-on-warning")

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

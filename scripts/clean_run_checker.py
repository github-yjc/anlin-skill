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
sys.path.insert(0, str(ROOT / "scripts"))
from check_anlin_violations import (  # noqa: E402
    BACKGROUND_DISPLAY_GROUPS,
    COMMENT_CHAIN_FORMULA_MARKERS,
    ENGINE_SIGNAL_TERMS,
    PROCESS_LEAK_TERMS,
    HIGH_FREQUENCY_TERMS,
    ROUGH_SELF_DAMAGE_PATTERNS,
    ROUGH_SELF_DAMAGE_TERMS,
    STANDARD_DIARY_DRAFT_OVERFULL_CHARS,
    chinese_len,
    current_office_persona_hits,
    meta_ai_topic_hits,
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


def normalize_before_final_check(draft: Path) -> None:
    subprocess.run(
        [sys.executable, str(SPLIT_LONG_LINES), str(draft), "--in-place", "--target-lines", "58"],
        text=True,
        encoding="utf-8",
        check=False,
    )
    text = draft.read_text(encoding="utf-8")
    _, content_lines = split_title_and_content_lines(text.splitlines())
    visible = [line for line in content_lines if line.strip() and not line.strip().startswith("<!--")]
    lengths = [chinese_len(line) for line in visible]
    short_ratio = (sum(1 for length in lengths if length <= 12) / len(lengths)) if lengths else 0.0
    long_count = sum(1 for length in lengths if length >= 28)
    line_stdev = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    if len(visible) > 75 or short_ratio >= 0.40 or (len(visible) >= 72 and (long_count < 4 or line_stdev <= 6.0)):
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


def has_binary_reframe(lines: list[str]) -> bool:
    patterns = [
        re.compile(r"不是[^，。！？\n]{1,28}[,，]?(?:而|只|也|这|那)?(?:才)?是"),
        re.compile(r"不是[^，。！？\n]{1,28}[,，]?(?:就是|只是)"),
        re.compile(r"不是[^。！？\n]{1,28}[。！？]\s*(?:就是|只是)"),
        re.compile(r"其实不是[,，]?(?:好像|就是|只是|而是|是)"),
        re.compile(r"像[^。！？\n]{1,32}其实不是"),
    ]
    for line in lines:
        if any(pattern.search(line) for pattern in patterns):
            return True
    for index in range(len(lines) - 1):
        left = lines[index].strip()
        right = lines[index + 1].strip()
        if (
            re.search(r"不是[^。！？\n]{1,28}[，,]?$", left)
            and re.match(r"^(?:而是|是|就是|只是|这是|那是|才是)[^。！？\n]{1,40}", right)
        ):
            return True
    return False


def surface_preflight_messages(lines: list[str], article_text: str) -> list[str]:
    messages: list[str] = []
    leaked_terms = [term for term in PROCESS_LEAK_TERMS if term in article_text]
    if leaked_terms:
        messages.append(f"process_leak_terms={leaked_terms[:3]}")
    comment_markers = [term for term in COMMENT_CHAIN_FORMULA_MARKERS if term in article_text]
    if comment_markers:
        messages.append(f"comment_chain_markers={comment_markers[:4]}")
    if has_binary_reframe(lines):
        messages.append("binary_reframe=present")
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
    _, content_lines = split_title_and_content_lines(text.splitlines())
    article_lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("<!--")]
    visible_lines = [line for line in content_lines if line.strip() and not line.strip().startswith("<!--")]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    line_lengths = [chinese_len(line) for line in visible_lines]
    body_line_count = len(line_lengths)
    mean_line = statistics.mean(line_lengths) if line_lengths else 0.0
    long_line_count = sum(1 for length in line_lengths if length >= 28)
    short_line_ratio = (sum(1 for length in line_lengths if length <= 12) / len(line_lengths)) if line_lengths else 0.0
    first_twenty = visible_lines[:20]
    comma_ratio = (sum(1 for line in first_twenty if line.endswith("，")) / len(first_twenty)) if first_twenty else 0.0
    connectors = [term for term in HIGH_FREQUENCY_TERMS if term in body]
    engine_hits = [term for term in ENGINE_SIGNAL_TERMS if term in body]
    rough_terms = [term for term in ROUGH_SELF_DAMAGE_TERMS if term in body]
    rough_patterns = [pattern for pattern in ROUGH_SELF_DAMAGE_PATTERNS if re.search(pattern, body)]
    messages: list[str] = []
    if body_chars < 950:
        messages.append(f"body_chinese_chars={body_chars} < 950")
    if body_chars > STANDARD_DIARY_DRAFT_OVERFULL_CHARS:
        messages.append(f"body_chinese_chars={body_chars} > {STANDARD_DIARY_DRAFT_OVERFULL_CHARS}")
    if body_line_count < 45:
        messages.append(f"body_lines={body_line_count} < 45 (write a line-broken article, not prose paragraphs)")
    if body_line_count > 90:
        messages.append(
            f"body_lines={body_line_count} > 90 (overfragmented short-line grid; merge adjacent action/speech lines before checking)"
        )
    if body_line_count > 75 and long_line_count < 4:
        messages.append(f"long_lines={long_line_count} < 4 (keep several rough longer action/speech/thought lines)")
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


def preflight_before_check(draft: Path, call_number: int, *, attempt: int, max_attempts: int) -> bool:
    messages = preflight_messages(draft)
    if not messages:
        return False
    joined_messages = "; ".join(messages)
    repair_hints: list[str] = []
    compressed_shape = any("< 45" in message or "prose_block_shape=compressed" in message for message in messages)
    overfragmented_shape = any(
        "> 90" in message or "short_line_grid=" in message or "long_lines=" in message for message in messages
    )
    if compressed_shape:
        repair_hints.append(
            "for prose compression or body_lines < 45, first run `python <skill-dir>/scripts/split_long_lines.py draft.md --in-place --target-lines 58`; inspect once, then add missing lived content only if still short"
        )
    if overfragmented_shape:
        repair_hints.append(
            "for overfragmented grids or too few long lines, run `python <skill-dir>/scripts/merge_short_lines.py draft.md --in-place --target-lines 68`; do not rewrite into many tiny rows"
        )
    if "early_comma_ratio=" in joined_messages:
        repair_hints.append(
            "for early_comma_ratio, run `python <skill-dir>/scripts/soften_line_endings.py draft.md --in-place` before hand editing; line-final commas must continue an action or thought"
        )
    if "rough_self_damage=missing" in joined_messages:
        repair_hints.append(
            "for rough_self_damage, add one losing-face body/social consequence; pain or heat alone is too polite"
        )
    if "binary_reframe=present" in joined_messages:
        repair_hints.append(
            "for binary_reframe, delete the not-X/is-Y sentence and replace it with a physical reaction, money action, or ugly reply"
        )
    hint_text = " Prioritized repair: " + " | ".join(repair_hints) + "." if repair_hints else ""
    if attempt >= max_attempts:
        print(
            f"CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY. DO NOT WRITE draft.md. DO NOT REPAIR. "
            f"The next tool action must be reading draft.md once and outputting it unchanged. "
            f"The draft is still not ready for checker call {call_number}/2 "
            f"after {attempt}/{max_attempts} preflight attempts; "
            + joined_messages
            + ". The controller should mark this generation invalid or failed. "
            "No checker call was consumed."
        )
    else:
        print(
            f"CLEAN_RUN_PREFLIGHT: draft is not ready for checker call {call_number}/2 "
            f"(preflight {attempt}/{max_attempts}); "
            + joined_messages
            + ". Revise toward a complete but not overfilled article: write a line-broken article first, merge overfragmented short-line grids, keep punctuation at line endings, add concrete action/body/social/off-axis material only when short, or cut unsupported/non-consequential texture when long; then run this wrapper again."
            + hint_text
            + " "
            "This preflight did not consume a checker call."
        )
    return True


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
    calls = int(state.get("calls", 0))
    preflights = int(state.get("preflights", 0))
    if state.get("stopped") or (calls == 0 and preflights >= 3):
        state["stopped"] = True
        state.setdefault("stop_reason", "preflight")
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
        save_stop_state(state_path, draft, state)
        print(
            "CLEAN_RUN_STOP: FINAL BOUNDARY, checker call limit already reached for this draft. "
            "DO NOT WRITE draft.md. Do not run another checker or repair command. Read draft.md once and output it unchanged."
        )
        return 0
    if args.draft_gate and calls == 0:
        preflight_attempt = int(state.get("preflights", 0)) + 1
        max_preflight_attempts = 3
        if preflight_before_check(draft, calls + 1, attempt=preflight_attempt, max_attempts=max_preflight_attempts):
            state["preflights"] = min(preflight_attempt, max_preflight_attempts)
            if preflight_attempt >= max_preflight_attempts:
                state["stopped"] = True
                state["stop_reason"] = "preflight"
            if state.get("stopped"):
                save_stop_state(state_path, draft, state)
            else:
                save_state(state_path, state)
            return 0 if preflight_attempt >= max_preflight_attempts else 3

    call_number = calls + 1
    state["calls"] = call_number
    state["preflights"] = int(state.get("preflights", 0))
    save_state(state_path, state)
    if args.draft_gate and call_number == 2:
        normalize_before_final_check(draft)

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

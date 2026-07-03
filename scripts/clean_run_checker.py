#!/usr/bin/env python3
"""Bounded checker wrapper for formal clean generation.

This wrapper is for generation agents, not external validation. It delegates to
check_anlin_violations.py while recording how many checker calls have been made
for the current draft. After the second call, the next action should be reading
draft.md and outputting it unchanged.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_anlin_violations.py"
SPLIT_LONG_LINES = ROOT / "scripts" / "split_long_lines.py"
SOFTEN_LINE_ENDINGS = ROOT / "scripts" / "soften_line_endings.py"
sys.path.insert(0, str(ROOT / "scripts"))
from check_anlin_violations import (  # noqa: E402
    ENGINE_SIGNAL_TERMS,
    HIGH_FREQUENCY_TERMS,
    chinese_len,
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


def normalize_before_final_check(draft: Path) -> None:
    subprocess.run(
        [sys.executable, str(SPLIT_LONG_LINES), str(draft), "--in-place", "--target-lines", "58"],
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


def preflight_before_first_check(draft: Path) -> bool:
    text = draft.read_text(encoding="utf-8")
    _, content_lines = split_title_and_content_lines(text.splitlines())
    body = "\n".join(line for line in content_lines if line.strip() and not line.strip().startswith("<!--"))
    body_chars = chinese_len(body)
    connectors = [term for term in HIGH_FREQUENCY_TERMS if term in body]
    engine_hits = [term for term in ENGINE_SIGNAL_TERMS if term in body]
    messages: list[str] = []
    if body_chars < 950:
        messages.append(f"body_chinese_chars={body_chars} < 950")
    if len(connectors) < 5:
        messages.append(f"connectors={connectors} < 5")
    if len(engine_hits) < 3:
        messages.append(f"engine_hits={engine_hits} < 3")
    if not messages:
        return False
    print(
        "CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2; "
        + "; ".join(messages)
        + ". Continue writing concrete action/body/social/off-axis material, then run this wrapper again. "
        "This preflight did not consume a checker call."
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Anlin draft checker with a two-call clean-run limit.")
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
    state_path = args.state or (draft.parent / ".anlin-clean-run-state.json")
    state_path = state_path.resolve()
    state = {} if args.reset else load_state(state_path)
    draft_key = str(draft)
    if state.get("draft") != draft_key:
        state = {"draft": draft_key, "calls": 0}
    calls = int(state.get("calls", 0))
    if calls >= 2:
        print(
            "CLEAN_RUN_STOP: checker call limit already reached for this draft. "
            "Do not run another checker or repair command. Read draft.md once and output it unchanged."
        )
        return 2
    if args.draft_gate and calls == 0 and preflight_before_first_check(draft):
        return 3

    call_number = calls + 1
    state["calls"] = call_number
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
        print(
            "CLEAN_RUN_STOP: this was checker call 2/2. "
            "Do not edit, split, merge, compare, or run another checker. "
            "Read draft.md once and output it unchanged, even if errors remain."
        )
    else:
        print("CLEAN_RUN_NOTE: checker call 1/2. One repair pass remains before final output.")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

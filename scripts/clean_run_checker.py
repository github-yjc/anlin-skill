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


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


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

    call_number = calls + 1
    state["calls"] = call_number
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

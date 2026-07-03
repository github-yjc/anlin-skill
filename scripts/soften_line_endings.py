#!/usr/bin/env python3
"""Soften over-closed generated line endings without adding content.

This is a narrow repair for generated drafts that have been split into many
article lines but still end almost every early line with a full stop. It changes
eligible line-final `。` marks to `，` until the first-N content-line comma ratio
reaches a target. It does not insert words or reorder lines.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def chinese_len(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def is_title_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    normalized = re.sub(r"^#+\s*", "", stripped)
    normalized = re.sub(r"^\*\*(.+)\*\*$", r"\1", normalized).strip()
    return "。" not in normalized and "，" not in normalized and chinese_len(normalized) <= 24


def content_line_indices(lines: list[str]) -> list[int]:
    indices: list[int] = []
    first_nonempty_seen = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if not first_nonempty_seen:
            first_nonempty_seen = True
            if is_title_line(stripped):
                continue
        if stripped.startswith("<!--"):
            continue
        indices.append(index)
    return indices


def comma_ratio(lines: list[str], indices: list[int], sample_size: int) -> float:
    sample = indices[:sample_size]
    if not sample:
        return 0.0
    comma_endings = sum(1 for index in sample if lines[index].rstrip().endswith(("，", ",")))
    return comma_endings / len(sample)


def eligible_for_softening(lines: list[str], index: int, indices: list[int]) -> bool:
    stripped = lines[index].rstrip()
    if not stripped.endswith("。"):
        return False
    if chinese_len(stripped) < 8:
        return False
    if stripped.endswith(("。”", "。\"", "。』", "。」")):
        return False
    if index == indices[-1]:
        return False
    return True


def eligible_for_hardening(lines: list[str], index: int, indices: list[int]) -> bool:
    stripped = lines[index].rstrip()
    if not stripped.endswith(("，", ",")):
        return False
    if chinese_len(stripped) < 8:
        return False
    if index == indices[-1]:
        return False
    return True


def spaced_indices(indices: list[int], count: int) -> list[int]:
    if count <= 0 or not indices:
        return []
    if count >= len(indices):
        return indices
    step = len(indices) / count
    selected: list[int] = []
    used: set[int] = set()
    for item in range(count):
        position = min(len(indices) - 1, int(round(item * step)))
        while position in used and position + 1 < len(indices):
            position += 1
        if position in used:
            position = next((idx for idx in range(len(indices)) if idx not in used), position)
        used.add(position)
        selected.append(indices[position])
    return selected


def soften_lines(lines: list[str], target_ratio: float, max_ratio: float, sample_size: int) -> dict[str, object]:
    indices = content_line_indices(lines)
    before = comma_ratio(lines, indices, sample_size)
    changed: list[int] = []
    if before < target_ratio and indices:
        needed = int(target_ratio * min(sample_size, len(indices)) + 0.999999)
        current = sum(1 for index in indices[:sample_size] if lines[index].rstrip().endswith(("，", ",")))
        for index in indices[:sample_size]:
            if current >= needed:
                break
            if not eligible_for_softening(lines, index, indices):
                continue
            lines[index] = re.sub(r"。\s*$", "，", lines[index])
            changed.append(index + 1)
            current += 1
    elif before > max_ratio and indices:
        sample = indices[:sample_size]
        current = sum(1 for index in sample if lines[index].rstrip().endswith(("，", ",")))
        allowed = int(max_ratio * len(sample))
        candidates = [index for index in sample if eligible_for_hardening(lines, index, indices)]
        for index in spaced_indices(candidates, current - allowed):
            lines[index] = re.sub(r"[，,]\s*$", "。", lines[index])
            changed.append(index + 1)
    after = comma_ratio(lines, indices, sample_size)
    return {
        "content_lines": len(indices),
        "sample_size": min(sample_size, len(indices)),
        "before_ratio": before,
        "after_ratio": after,
        "changed_line_numbers": changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Soften over-closed line-final periods in a generated Anlin draft.")
    parser.add_argument("draft", type=Path)
    parser.add_argument("--in-place", action="store_true")
    parser.add_argument("--target-ratio", type=float, default=0.55)
    parser.add_argument("--max-ratio", type=float, default=0.75)
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = args.draft.read_text(encoding="utf-8")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    report = soften_lines(lines, args.target_ratio, args.max_ratio, args.sample_size)
    output = "\n".join(lines)
    if text.endswith("\n") and not output.endswith("\n"):
        output += "\n"
    if args.in_place:
        args.draft.write_text(output, encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            "soften_line_endings: "
            f"before={report['before_ratio']:.2f} after={report['after_ratio']:.2f} "
            f"changed={len(report['changed_line_numbers'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

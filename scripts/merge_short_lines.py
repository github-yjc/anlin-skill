#!/usr/bin/env python3
"""Merge over-fragmented Chinese prose lines in a draft.

This is a mechanical lineation repair for generated drafts that already have
content but were cut into a visible short-line grid. It does not add style
markers or new facts.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def chinese_len(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def split_title_body(text: str) -> tuple[list[str], list[list[str]]]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_lines = normalized.split("\n")
    prefix: list[str] = []
    body_start = 0
    for index, line in enumerate(raw_lines):
        if line.strip():
            prefix = raw_lines[: index + 1]
            body_start = index + 1
            break
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in raw_lines[body_start:]:
        if not line.strip():
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(line.strip())
    if current:
        blocks.append(current)
    return prefix, blocks


def join_lines(left: str, right: str) -> str:
    if not left:
        return right
    if left.endswith(("，", "、", "：", "；", "“")):
        return left + right
    return left + right


def merge_block(lines: list[str], min_chars: int) -> list[str]:
    merged: list[str] = []
    current = ""
    for line in lines:
        if not current:
            current = line
            continue
        current_len = chinese_len(current)
        line_len = chinese_len(line)
        if current_len < min_chars or (line_len <= 10 and current_len < min_chars + 12):
            current = join_lines(current, line)
        else:
            merged.append(current)
            current = line
    if current:
        merged.append(current)
    return merged


def body_lines(blocks: list[list[str]]) -> list[str]:
    return [line for block in blocks for line in block]


def merge_short_lines(text: str, target_lines: int, start_min_chars: int, max_min_chars: int) -> tuple[str, dict[str, int | float]]:
    prefix, blocks = split_title_body(text)
    original_lines = body_lines(blocks)
    original_chars = sum(chinese_len(line) for line in original_lines)
    min_chars = start_min_chars
    merged_blocks = [merge_block(block, min_chars) for block in blocks]
    while len(body_lines(merged_blocks)) > target_lines and min_chars < max_min_chars:
        min_chars += 2
        merged_blocks = [merge_block(block, min_chars) for block in blocks]

    output_lines: list[str] = [line.rstrip() for line in prefix]
    output_lines.append("")
    for index, block in enumerate(merged_blocks):
        if index:
            output_lines.append("")
        output_lines.extend(block)
    output = "\n".join(output_lines).rstrip() + "\n"
    merged_lines = body_lines(merged_blocks)
    long_lines = sum(1 for line in merged_lines if chinese_len(line) >= 24)
    short_lines = sum(1 for line in merged_lines if chinese_len(line) <= 10)
    report = {
        "original_body_lines": len(original_lines),
        "merged_body_lines": len(merged_lines),
        "body_chars": original_chars,
        "min_chars_used": min_chars,
        "lines_ge24": long_lines,
        "lines_le10": short_lines,
        "avg_line_chars": round(original_chars / len(merged_lines), 2) if merged_lines else 0.0,
    }
    return output, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge over-fragmented Anlin draft lines.")
    parser.add_argument("draft", type=Path)
    parser.add_argument("--target-lines", type=int, default=68)
    parser.add_argument("--start-min-chars", type=int, default=18)
    parser.add_argument("--max-min-chars", type=int, default=32)
    parser.add_argument("--in-place", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = read_text(args.draft)
    output, report = merge_short_lines(text, args.target_lines, args.start_min_chars, args.max_min_chars)
    if args.in_place:
        args.draft.write_text(output, encoding="utf-8", newline="\n")
    else:
        print(output, end="")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.in_place:
        print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

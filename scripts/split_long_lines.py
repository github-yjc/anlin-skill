#!/usr/bin/env python3
"""Split over-compressed generated Anlin draft lines without adding content."""

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


def content_count(lines: list[str]) -> int:
    count = 0
    first_nonempty_seen = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if not first_nonempty_seen:
            first_nonempty_seen = True
            if is_title_line(stripped):
                continue
        if stripped.startswith("<!--"):
            continue
        count += 1
    return count


def split_candidate(line: str, max_chars: int, min_chunk_chars: int) -> list[str]:
    stripped = line.strip()
    if chinese_len(stripped) <= max_chars:
        return [line]
    pieces = re.split(r"(?<=[，。！？?])", stripped)
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if not piece:
            continue
        candidate = current + piece
        if current and chinese_len(candidate) > max_chars and chinese_len(current) >= min_chunk_chars:
            chunks.append(current)
            current = piece
        else:
            current = candidate
    if current:
        chunks.append(current)
    if len(chunks) <= 1:
        return [line]
    merged: list[str] = []
    for chunk in chunks:
        if merged and chinese_len(chunk) < min_chunk_chars:
            merged[-1] += chunk
        else:
            merged.append(chunk)
    return merged if len(merged) > 1 else [line]


def split_lines(lines: list[str], target_lines: int, max_chars: int, min_chunk_chars: int) -> dict[str, object]:
    original_count = content_count(lines)
    output: list[str] = []
    first_nonempty_seen = False
    changed: list[int] = []
    current_count = 0
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            output.append(line)
            continue
        if not first_nonempty_seen:
            first_nonempty_seen = True
            output.append(line)
            if not is_title_line(stripped):
                current_count += 1
            continue
        if stripped.startswith("<!--"):
            output.append(line)
            continue
        if current_count >= target_lines:
            output.append(line)
            current_count += 1
            continue
        pieces = split_candidate(line, max_chars, min_chunk_chars)
        if len(pieces) > 1:
            changed.append(index)
            output.extend(pieces)
            current_count += len(pieces)
        else:
            output.append(line)
            current_count += 1
    lines[:] = output
    final_count = content_count(lines)
    lengths = [chinese_len(line) for line in lines if line.strip()]
    return {
        "original_body_lines": original_count,
        "split_body_lines": final_count,
        "changed_line_numbers": changed,
        "max_line_chars": max(lengths) if lengths else 0,
        "avg_line_chars": sum(lengths) / len(lengths) if lengths else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Split over-compressed long lines in a generated Anlin draft.")
    parser.add_argument("draft", type=Path)
    parser.add_argument("--in-place", action="store_true")
    parser.add_argument("--target-lines", type=int, default=58)
    parser.add_argument("--max-chars", type=int, default=24)
    parser.add_argument("--min-chunk-chars", type=int, default=7)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = args.draft.read_text(encoding="utf-8")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    report = split_lines(lines, args.target_lines, args.max_chars, args.min_chunk_chars)
    output = "\n".join(lines)
    if text.endswith("\n") and not output.endswith("\n"):
        output += "\n"
    if args.in_place:
        args.draft.write_text(output, encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            "split_long_lines: "
            f"before={report['original_body_lines']} after={report['split_body_lines']} "
            f"changed={len(report['changed_line_numbers'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

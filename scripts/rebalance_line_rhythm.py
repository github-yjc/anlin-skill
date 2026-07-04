#!/usr/bin/env python3
"""Rebalance generated draft line rhythm without adding new facts.

This helper sits between split_long_lines.py and merge_short_lines.py. It is
for drafts that bounce between prose-block compression and visible short-line
grids. The goal is a middle corridor: enough visible breath, several rough
longer action/thought lines, and no collapse into a few essay paragraphs.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path
from typing import Any


def chinese_len(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def is_title_line(line: str) -> bool:
    stripped = re.sub(r"^#+\s*", "", line.strip())
    stripped = re.sub(r"^\*\*(.+)\*\*$", r"\1", stripped).strip()
    return bool(stripped) and chinese_len(stripped) <= 24 and not re.search(r"[。！？!?，,：:；;]", stripped)


def split_title_body(text: str) -> tuple[list[str], list[str]]:
    raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    prefix: list[str] = []
    body: list[str] = []
    first_nonempty = False
    for line in raw_lines:
        stripped = line.strip()
        if not first_nonempty:
            if not stripped:
                continue
            first_nonempty = True
            prefix.append(line.rstrip())
            if not is_title_line(stripped):
                body.append(stripped)
            continue
        if stripped and not stripped.startswith("<!--"):
            body.append(stripped)
    if not prefix:
        prefix = ["日寄"]
    return prefix, body


def line_stats(lines: list[str]) -> dict[str, Any]:
    lengths = [chinese_len(line) for line in lines]
    total = sum(lengths)
    if not lengths:
        return {
            "body_lines": 0,
            "body_chars": 0,
            "mean_line_chars": 0.0,
            "stdev_line_chars": 0.0,
            "short_lines": 0,
            "long_lines": 0,
            "short_line_ratio": 0.0,
            "long_line_ratio": 0.0,
        }
    short_lines = sum(1 for length in lengths if length <= 12)
    long_lines = sum(1 for length in lengths if length >= 28)
    return {
        "body_lines": len(lengths),
        "body_chars": total,
        "mean_line_chars": round(total / len(lengths), 3),
        "stdev_line_chars": round(statistics.pstdev(lengths), 3) if len(lengths) > 1 else 0.0,
        "short_lines": short_lines,
        "long_lines": long_lines,
        "short_line_ratio": round(short_lines / len(lengths), 3),
        "long_line_ratio": round(long_lines / len(lengths), 3),
    }


def split_candidate(line: str, max_chars: int, min_chunk_chars: int) -> list[str]:
    if chinese_len(line) <= max_chars:
        return [line]
    pieces = [piece for piece in re.split(r"(?<=[，。！？?])", line.strip()) if piece]
    if len(pieces) <= 1:
        return [line]
    chunks: list[str] = []
    current = ""
    hard_max_chars = max_chars + 10
    for piece in pieces:
        candidate = current + piece
        if current and chinese_len(candidate) > hard_max_chars and chinese_len(current) >= min_chunk_chars:
            chunks.append(current)
            current = piece
        else:
            current = candidate
    if current:
        chunks.append(current)
    merged: list[str] = []
    for chunk in chunks:
        if merged and chinese_len(chunk) < min_chunk_chars:
            merged[-1] += chunk
        else:
            merged.append(chunk)
    return merged if len(merged) > 1 else [line]


def split_until_corridor(
    lines: list[str],
    *,
    target_min_lines: int,
    preferred_lines: int,
    min_long_lines: int,
    max_chars: int,
    min_chunk_chars: int,
) -> list[str]:
    if len(lines) >= target_min_lines:
        return lines
    output: list[str] = []
    for line in lines:
        stats = line_stats(output)
        if len(output) >= preferred_lines or (
            len(output) >= target_min_lines and int(stats["long_lines"]) >= min_long_lines
        ):
            output.append(line)
            continue
        pieces = split_candidate(line, max_chars=max_chars, min_chunk_chars=min_chunk_chars)
        output.extend(pieces)
    if len(output) >= target_min_lines:
        return output

    # One stricter pass can rescue moderately compressed prose, but still only
    # split at punctuation. No arbitrary character chopping.
    stricter: list[str] = []
    for line in output:
        stats = line_stats(stricter)
        if len(stricter) >= preferred_lines or (
            len(stricter) >= target_min_lines and int(stats["long_lines"]) >= min_long_lines
        ):
            stricter.append(line)
            continue
        stricter.extend(split_candidate(line, max_chars=max_chars - 4, min_chunk_chars=min_chunk_chars))
    return stricter


def join_lines(left: str, right: str) -> str:
    return left.rstrip() + right.strip()


def choose_merge_pair(lines: list[str], *, need_long: bool) -> int | None:
    if len(lines) < 2:
        return None
    candidates: list[tuple[float, int]] = []
    long_making_candidates: list[tuple[float, int]] = []
    for index in range(len(lines) - 1):
        left_len = chinese_len(lines[index])
        right_len = chinese_len(lines[index + 1])
        combined = chinese_len(join_lines(lines[index], lines[index + 1]))
        if combined > 48:
            continue
        if need_long:
            if left_len <= 26 and right_len <= 26:
                if combined >= 28:
                    long_making_candidates.append((abs(combined - 31), index))
                candidates.append((abs(combined - 31), index))
        elif left_len <= 16 or right_len <= 10 or combined <= 24:
            candidates.append((abs(combined - 26), index))
    if need_long and long_making_candidates:
        return min(long_making_candidates)[1]
    if not candidates:
        return None
    return min(candidates)[1]


def merge_until_corridor(
    lines: list[str],
    *,
    target_min_lines: int,
    target_max_lines: int,
    min_long_lines: int,
) -> list[str]:
    output = list(lines)
    while len(output) > target_min_lines:
        stats = line_stats(output)
        need_fewer = len(output) > target_max_lines
        need_long = int(stats["long_lines"]) < min_long_lines
        if not need_fewer and not need_long:
            break
        pair_index = choose_merge_pair(output, need_long=need_long)
        if pair_index is None:
            break
        output[pair_index] = join_lines(output[pair_index], output[pair_index + 1])
        del output[pair_index + 1]
    return output


def rebalance(
    text: str,
    *,
    target_min_lines: int,
    target_max_lines: int,
    preferred_lines: int,
    min_long_lines: int,
    max_split_chars: int,
    min_chunk_chars: int,
) -> tuple[str, dict[str, Any]]:
    prefix, body = split_title_body(text)
    before = line_stats(body)
    lines = split_until_corridor(
        body,
        target_min_lines=target_min_lines,
        preferred_lines=preferred_lines,
        min_long_lines=min_long_lines,
        max_chars=max_split_chars,
        min_chunk_chars=min_chunk_chars,
    )
    lines = merge_until_corridor(
        lines,
        target_min_lines=target_min_lines,
        target_max_lines=target_max_lines,
        min_long_lines=min_long_lines,
    )
    after = line_stats(lines)
    unresolved: list[str] = []
    if int(after["body_lines"]) < target_min_lines:
        unresolved.append("body_lines_below_corridor")
    if int(after["body_lines"]) > target_max_lines:
        unresolved.append("body_lines_above_corridor")
    if int(after["long_lines"]) < min_long_lines:
        unresolved.append("long_lines_below_corridor")
    if int(after["body_lines"]) <= 40 and float(after["mean_line_chars"]) >= 30:
        unresolved.append("still_prose_compressed")

    output_lines = [line.rstrip() for line in prefix]
    output_lines.append("")
    output_lines.extend(lines)
    output = "\n".join(output_lines).rstrip() + "\n"
    report = {
        "before": before,
        "after": after,
        "target": {
            "min_lines": target_min_lines,
            "max_lines": target_max_lines,
            "preferred_lines": preferred_lines,
            "min_long_lines": min_long_lines,
        },
        "unresolved": unresolved,
    }
    return output, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebalance Anlin draft line rhythm into a middle corridor.")
    parser.add_argument("draft", type=Path)
    parser.add_argument("--target-min-lines", type=int, default=45)
    parser.add_argument("--target-max-lines", type=int, default=70)
    parser.add_argument("--preferred-lines", type=int, default=58)
    parser.add_argument("--min-long-lines", type=int, default=6)
    parser.add_argument("--max-split-chars", type=int, default=26)
    parser.add_argument("--min-chunk-chars", type=int, default=7)
    parser.add_argument("--in-place", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    output, report = rebalance(
        read_text(args.draft),
        target_min_lines=args.target_min_lines,
        target_max_lines=args.target_max_lines,
        preferred_lines=args.preferred_lines,
        min_long_lines=args.min_long_lines,
        max_split_chars=args.max_split_chars,
        min_chunk_chars=args.min_chunk_chars,
    )
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

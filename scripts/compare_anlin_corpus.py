#!/usr/bin/env python3
"""Compare an Anlin-style draft against a local corpus directory.

This diagnostic tool reports surface similarity and basic rhythm/vocabulary
signals. It does not prove authenticity or style fit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path


EXPECTED_CORPUS_COUNT = 38
HIGH_FREQUENCY_TERMS = ["其实", "觉得", "发现", "好像", "不过", "突然", "于是", "因为", "所以"]
FORBIDDEN_HINTS = ["有人说", "评论说", "回复说", "热评", "像什么", "算是全国最便宜", "便宜归便宜"]


@dataclass(frozen=True)
class CorpusFileScore:
    file: str
    jaccard_3gram: float
    shared_high_frequency_terms: int


@dataclass(frozen=True)
class ComparisonReport:
    corpus_file_count: int
    draft_chars: int
    draft_lines: int
    draft_scene_blocks: int
    high_frequency_terms_present: list[str]
    forbidden_hints_present: list[str]
    comma_ending_ratio_first_20: float | None
    corpus_average_scene_blocks: float | None
    corpus_average_comma_ratio: float | None
    nearest_files: list[CorpusFileScore]
    notes: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def chinese_chars(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]", text)


def char_ngrams(text: str, n: int = 3) -> set[str]:
    chars = chinese_chars(text)
    return {"".join(chars[index : index + n]) for index in range(max(0, len(chars) - n + 1))}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def scene_blocks(text: str) -> int:
    blocks = [block for block in re.split(r"\n\s*\n|\n\.\s*\n", text) if block.strip()]
    return len(blocks)


def comma_ratio(lines: list[str]) -> float | None:
    content_lines = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if not content_lines:
        return None
    sample = content_lines[:20]
    comma_endings = sum(1 for line in sample if line.endswith("，") or line.endswith(","))
    return comma_endings / len(sample)


def load_corpus(corpus_dir: Path) -> list[tuple[Path, str]]:
    paths = [path for pattern in ("*.md", "*.txt") for path in sorted(corpus_dir.glob(pattern)) if path.is_file()]
    return [(path, read_text(path)) for path in paths]


def average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def compare(draft_path: Path, corpus_dir: Path) -> ComparisonReport:
    draft = read_text(draft_path)
    draft_ngrams = char_ngrams(draft)
    draft_terms = [term for term in HIGH_FREQUENCY_TERMS if term in draft]
    forbidden = [term for term in FORBIDDEN_HINTS if term in draft]
    corpus = load_corpus(corpus_dir)

    scores: list[CorpusFileScore] = []
    corpus_scene_counts: list[float] = []
    corpus_comma_ratios: list[float] = []
    for path, text in corpus:
        original_terms = [term for term in HIGH_FREQUENCY_TERMS if term in text]
        scores.append(
            CorpusFileScore(
                file=str(path),
                jaccard_3gram=jaccard(draft_ngrams, char_ngrams(text)),
                shared_high_frequency_terms=len(set(draft_terms) & set(original_terms)),
            )
        )
        corpus_scene_counts.append(float(scene_blocks(text)))
        ratio = comma_ratio(text.splitlines())
        if ratio is not None:
            corpus_comma_ratios.append(ratio)

    nearest = sorted(scores, key=lambda item: item.jaccard_3gram, reverse=True)[:5]
    notes: list[str] = []
    if not corpus:
        notes.append("No .md or .txt files found in corpus directory; full-corpus validation unavailable.")
    elif len(corpus) != EXPECTED_CORPUS_COUNT:
        notes.append(f"Corpus file count is {len(corpus)}, expected {EXPECTED_CORPUS_COUNT}; statistics may be incomplete or mismatched.")
    if len(draft_terms) < 5:
        notes.append("High-frequency connective coverage is low; compare against vocabulary-rules.md §6.3.")
    if forbidden:
        notes.append("Forbidden or high-risk hints found; run check_anlin_violations.py for line-level details.")
    blocks = scene_blocks(draft)
    if blocks < 4 or blocks > 8:
        notes.append("Scene block count is outside the expected range; inspect montage structure manually.")

    return ComparisonReport(
        corpus_file_count=len(corpus),
        draft_chars=len(chinese_chars(draft)),
        draft_lines=len(draft.splitlines()),
        draft_scene_blocks=blocks,
        high_frequency_terms_present=draft_terms,
        forbidden_hints_present=forbidden,
        comma_ending_ratio_first_20=comma_ratio(draft.splitlines()),
        corpus_average_scene_blocks=average(corpus_scene_counts),
        corpus_average_comma_ratio=average(corpus_comma_ratios),
        nearest_files=nearest,
        notes=notes,
    )


def format_report(report: ComparisonReport) -> str:
    nearest_lines = [
        f"  - {item.file} | jaccard_3gram={item.jaccard_3gram:.4f} | shared_high_frequency_terms={item.shared_high_frequency_terms}"
        for item in report.nearest_files
    ]
    notes = report.notes or ["No automatic notes. Manual style review is still required."]
    return "\n".join(
        [
            "Anlin corpus comparison report",
            f"corpus_file_count: {report.corpus_file_count}",
            f"draft_chars: {report.draft_chars}",
            f"draft_lines: {report.draft_lines}",
            f"draft_scene_blocks: {report.draft_scene_blocks}",
            f"corpus_average_scene_blocks: {report.corpus_average_scene_blocks}",
            f"comma_ending_ratio_first_20: {report.comma_ending_ratio_first_20}",
            f"corpus_average_comma_ratio: {report.corpus_average_comma_ratio}",
            f"high_frequency_terms_present: {', '.join(report.high_frequency_terms_present) or '(none)'}",
            f"forbidden_hints_present: {', '.join(report.forbidden_hints_present) or '(none)'}",
            "nearest_files:",
            *(nearest_lines or ["  - (none)"]),
            "notes:",
            *[f"  - {note}" for note in notes],
            "jaccard_note: >0.15 may indicate heavy surface overlap; 0.05-0.15 may reflect shared topic/phrasing; <0.05 only means low surface overlap, not style mismatch.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare a draft against a local Anlin corpus directory.")
    parser.add_argument("draft", type=Path, help="Draft markdown/text file")
    parser.add_argument("--corpus-dir", type=Path, default=None, help="Directory containing original Anlin .md or .txt files")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    corpus_dir = args.corpus_dir or os.environ.get("ANLIN_CORPUS_DIR")
    if not corpus_dir:
        parser.error("Must provide --corpus-dir or set ANLIN_CORPUS_DIR environment variable.")
    corpus_dir = Path(corpus_dir)
    print(f"Using corpus directory: {corpus_dir}")
    corpus_paths = [path for pattern in ("*.md", "*.txt") for path in sorted(corpus_dir.glob(pattern)) if path.is_file()]
    print(f"Found {len(corpus_paths)} corpus files")

    report = compare(args.draft, corpus_dir)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(format_report(report))
    if report.forbidden_hints_present:
        return 1
    if any(note.startswith("No .md") or note.startswith("Corpus file count") for note in report.notes):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

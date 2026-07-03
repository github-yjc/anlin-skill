#!/usr/bin/env python3
"""Build a small-sample stylometric profile from the local Anlin corpus.

The profile is an audit prior, not an authorship model. It stores per-document
feature distributions and predictive-count parameters for generated-draft
review.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


EXPECTED_CORPUS_COUNT = 38
PROFILE_VERSION = "1.0"

CONNECTORS = [
    "其实",
    "觉得",
    "发现",
    "好像",
    "不过",
    "突然",
    "于是",
    "因为",
    "所以",
    "可能",
    "然后",
    "但是",
    "只是",
    "而且",
]

PUNCTUATION = {
    "comma": "，",
    "period": "。",
    "question": "？",
    "exclamation": "！",
    "enumeration": "、",
    "colon": "：",
    "semicolon": "；",
    "quote_left": "“",
    "quote_right": "”",
    "paren_left": "（",
    "paren_right": "）",
    "dash": "——",
}

PATTERNS = {
    "ai_binary_reframe": r"不是[^，。！？\n]{0,18}[，,]?\s*(?:而是|是)",
    "ai_explainer": r"(?:本质上|真正的问题是|核心是|这说明|这意味着|换句话说|说白了|最终我意识到|我终于明白)",
    "ordered_explainer": r"(?:首先|其次|最后|综上|总之)",
    "therapeutic_humanizer": r"(?:允许自己|接住自己|被看见|和自己和解|跟自己和解|慢慢来|拥抱自己|善待自己)",
    "literary_dash_caption": r"——(?:那种|一种|像是|好像|终于可以|说不上)",
}

FEATURE_FAMILIES = {
    "body_chars": "length",
    "body_lines": "length",
    "paragraph_blocks": "structure",
    "title_chars": "title",
    "line_mean_chars": "line_rhythm",
    "line_stdev_chars": "line_rhythm",
    "short_line_ratio": "line_rhythm",
    "long_line_ratio": "line_rhythm",
}


@dataclass(frozen=True)
class DocumentProfile:
    file: str
    title: str
    counts: dict[str, int]
    denominators: dict[str, int]
    values: dict[str, float]


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-8"):
        try:
            return data.decode(encoding)
        except UnicodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def chinese_len(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def compact_chinese(text: str) -> str:
    return "".join(re.findall(r"[\u4e00-\u9fff，。！？、：；“”（）《》—]", text))


def split_title_body(text: str) -> tuple[str, str, list[str]]:
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n") if line.strip()]
    if not lines:
        return "", "", []
    title = re.sub(r"^#+\s*", "", lines[0]).strip()
    title = re.sub(r"^\*\*(.+)\*\*$", r"\1", title).strip()
    body_lines = lines[1:]
    return title, "\n".join(body_lines), body_lines


def paragraph_blocks(body: str) -> int:
    blocks = [block for block in re.split(r"\n\s*\n|\n\.\s*\n", body) if block.strip()]
    return len(blocks)


def quantile(values: list[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - position) + ordered[high] * (position - low)


def median_abs_deviation(values: list[float]) -> float:
    if not values:
        return 0.0
    median = statistics.median(values)
    deviations = [abs(value - median) for value in values]
    return statistics.median(deviations)


def count_overlapping(text: str, needle: str) -> int:
    if not needle:
        return 0
    start = 0
    count = 0
    while True:
        index = text.find(needle, start)
        if index < 0:
            return count
        count += 1
        start = index + 1


def extract_document(path: Path) -> DocumentProfile:
    text = read_text(path)
    title, body, body_lines = split_title_body(text)
    content_lines = [line for line in body_lines if line and not line.lstrip().startswith("<!--")]
    line_lengths = [chinese_len(line) for line in content_lines if chinese_len(line) > 0]
    body_chars = chinese_len(body)
    body_compact = compact_chinese(body)
    line_count = len(line_lengths)

    counts: dict[str, int] = {}
    denominators: dict[str, int] = {}
    values: dict[str, float] = {
        "body_chars": float(body_chars),
        "body_lines": float(line_count),
        "paragraph_blocks": float(paragraph_blocks(body)),
        "title_chars": float(chinese_len(title)),
        "line_mean_chars": statistics.mean(line_lengths) if line_lengths else 0.0,
        "line_stdev_chars": statistics.pstdev(line_lengths) if len(line_lengths) > 1 else 0.0,
        "short_line_ratio": (sum(1 for length in line_lengths if length <= 8) / line_count) if line_count else 0.0,
        "long_line_ratio": (sum(1 for length in line_lengths if length >= 28) / line_count) if line_count else 0.0,
    }

    counts["short_lines"] = sum(1 for length in line_lengths if length <= 8)
    counts["long_lines"] = sum(1 for length in line_lengths if length >= 28)
    denominators["short_lines"] = line_count
    denominators["long_lines"] = line_count

    for label, punct in PUNCTUATION.items():
        feature = f"punct_{label}"
        counts[feature] = count_overlapping(body_compact, punct)
        denominators[feature] = body_chars
        values[f"{feature}_per_1k"] = counts[feature] / body_chars * 1000 if body_chars else 0.0

    for term in CONNECTORS:
        safe_label = f"connector_{term}"
        counts[safe_label] = count_overlapping(body_compact, term)
        denominators[safe_label] = body_chars
        values[f"{safe_label}_per_1k"] = counts[safe_label] / body_chars * 1000 if body_chars else 0.0

    for label, pattern in PATTERNS.items():
        counts[label] = len(re.findall(pattern, body))
        denominators[label] = body_chars
        values[f"{label}_per_1k"] = counts[label] / body_chars * 1000 if body_chars else 0.0

    return DocumentProfile(
        file=path.name,
        title=title,
        counts=counts,
        denominators=denominators,
        values=values,
    )


def summarize_values(documents: list[DocumentProfile]) -> dict[str, dict[str, float]]:
    feature_names = sorted({name for document in documents for name in document.values})
    summary: dict[str, dict[str, float]] = {}
    for feature in feature_names:
        values = [document.values.get(feature, 0.0) for document in documents]
        summary[feature] = {
            "min": min(values) if values else 0.0,
            "q05": quantile(values, 0.05),
            "q10": quantile(values, 0.10),
            "median": quantile(values, 0.50),
            "q90": quantile(values, 0.90),
            "q95": quantile(values, 0.95),
            "max": max(values) if values else 0.0,
            "mean": statistics.mean(values) if values else 0.0,
            "mad": median_abs_deviation(values),
        }
    return summary


def summarize_counts(documents: list[DocumentProfile]) -> dict[str, dict[str, Any]]:
    feature_names = sorted({name for document in documents for name in document.counts})
    summary: dict[str, dict[str, Any]] = {}
    for feature in feature_names:
        successes = sum(document.counts.get(feature, 0) for document in documents)
        trials = sum(document.denominators.get(feature, 0) for document in documents)
        family = infer_family(feature)
        summary[feature] = {
            "successes": successes,
            "trials": trials,
            "alpha": successes + 1,
            "beta": max(trials - successes, 0) + 1,
            "family": family,
            "denominator": infer_denominator(feature),
            "hard_generated": feature in {
                "ai_binary_reframe",
                "ai_explainer",
                "ordered_explainer",
                "therapeutic_humanizer",
                "literary_dash_caption",
            },
        }
    return summary


def infer_family(feature: str) -> str:
    if feature.startswith("punct_"):
        return "punctuation"
    if feature.startswith("connector_"):
        return "connectors"
    if feature in {"short_lines", "long_lines"}:
        return "line_rhythm"
    if feature.startswith("ai_") or feature in {"ordered_explainer", "therapeutic_humanizer", "literary_dash_caption"}:
        return "ai_slop"
    return FEATURE_FAMILIES.get(feature, "other")


def infer_denominator(feature: str) -> str:
    if feature in {"short_lines", "long_lines"}:
        return "body_lines"
    return "body_chars"


def load_corpus(corpus_dir: Path) -> list[Path]:
    return [
        path
        for pattern in ("*.md", "*.txt")
        for path in sorted(corpus_dir.glob(pattern))
        if path.is_file()
    ]


def build_profile(corpus_dir: Path) -> dict[str, Any]:
    paths = load_corpus(corpus_dir)
    documents = [extract_document(path) for path in paths]
    return {
        "version": PROFILE_VERSION,
        "profile_kind": "corpus_prior_predictive_intervals",
        "corpus_dir": str(corpus_dir),
        "expected_corpus_count": EXPECTED_CORPUS_COUNT,
        "corpus_file_count": len(paths),
        "principles": [
            "This profile is an audit prior, not authorship proof.",
            "Use per-document distributions and predictive intervals, not exact ratio matching.",
            "Do not force rare features to appear.",
            "Do not treat corpus-zero as impossible unless the feature is a hard generated-draft gate.",
            "Use placebo originals to calibrate warnings before blind-evaluation claims.",
        ],
        "documents": [asdict(document) for document in documents],
        "value_summary": summarize_values(documents),
        "count_summary": summarize_counts(documents),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an Anlin stylometric ratio profile from a local corpus.")
    parser.add_argument("corpus_dir", type=Path, help="Directory containing original Anlin .md or .txt files")
    parser.add_argument("--output", type=Path, default=None, help="Write profile JSON to this path")
    parser.add_argument("--json", action="store_true", help="Print full profile JSON to stdout")
    args = parser.parse_args()

    profile = build_profile(args.corpus_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(profile, ensure_ascii=False, indent=2))
    else:
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "corpus_file_count": profile["corpus_file_count"],
                    "expected_corpus_count": profile["expected_corpus_count"],
                    "version": profile["version"],
                },
                ensure_ascii=False,
            )
        )
    if profile["corpus_file_count"] != EXPECTED_CORPUS_COUNT:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


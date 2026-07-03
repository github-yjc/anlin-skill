#!/usr/bin/env python3
"""Calibrate style-profile warnings against the original corpus.

This reports how often each profile family flags originals. It is a sanity
check for thresholds, not an authorship or generation detector.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from check_style_profile import check_draft, read_json


EXPECTED_CORPUS_COUNT = 38


def corpus_paths(corpus_dir: Path) -> list[Path]:
    return [
        path
        for pattern in ("*.md", "*.txt")
        for path in sorted(corpus_dir.glob(pattern))
        if path.is_file()
    ]


def calibrate(corpus_dir: Path, profile: dict[str, Any], include_info: bool) -> dict[str, Any]:
    paths = corpus_paths(corpus_dir)
    reports = [check_draft(path, profile, include_info=include_info, draft_gate=False) for path in paths]
    status_counts = Counter(report["summary"]["status"] for report in reports)
    red_family_counts: Counter[str] = Counter()
    yellow_family_counts: Counter[str] = Counter()
    warning_family_counts: Counter[str] = Counter()
    error_files = []
    for path, report in zip(paths, reports):
        summary = report["summary"]
        if summary["error_count"]:
            error_files.append({"file": path.name, "error_count": summary["error_count"]})
        for family in summary.get("red_families", []):
            red_family_counts[family] += 1
        for family in summary.get("yellow_families", []):
            yellow_family_counts[family] += 1
        for family in summary.get("warning_families", []):
            warning_family_counts[family] += 1

    return {
        "corpus_dir": str(corpus_dir),
        "profile_version": profile.get("version"),
        "expected_corpus_count": EXPECTED_CORPUS_COUNT,
        "corpus_file_count": len(paths),
        "include_info": include_info,
        "status_counts": dict(sorted(status_counts.items())),
        "error_files": error_files,
        "red_family_counts": dict(sorted(red_family_counts.items())),
        "yellow_family_counts": dict(sorted(yellow_family_counts.items())),
        "warning_family_counts": dict(sorted(warning_family_counts.items())),
        "decision_note": "Original warnings are calibration data. Families that often flag originals must be downgraded in blind-review root-cause analysis unless supported by hard gates or placebo-stable evidence.",
    }


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "Anlin style-profile original calibration",
        f"profile_version: {report['profile_version']}",
        f"corpus_file_count: {report['corpus_file_count']} / expected {report['expected_corpus_count']}",
        f"include_info: {report['include_info']}",
        f"status_counts: {json.dumps(report['status_counts'], ensure_ascii=False)}",
        f"error_files: {json.dumps(report['error_files'], ensure_ascii=False)}",
        f"red_family_counts: {json.dumps(report['red_family_counts'], ensure_ascii=False)}",
        f"yellow_family_counts: {json.dumps(report['yellow_family_counts'], ensure_ascii=False)}",
        f"warning_family_counts: {json.dumps(report['warning_family_counts'], ensure_ascii=False)}",
        f"note: {report['decision_note']}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate style-profile warnings against original corpus files.")
    parser.add_argument("corpus_dir", type=Path, help="Directory containing original Anlin .md or .txt files")
    parser.add_argument("--profile", type=Path, required=True, help="Profile JSON produced by build_style_profile.py")
    parser.add_argument("--include-info", action="store_true", help="Include q10-q90 / 80% predictive informational drift")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    profile = read_json(args.profile)
    report = calibrate(args.corpus_dir, profile, include_info=args.include_info)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report(report))

    if report["corpus_file_count"] != EXPECTED_CORPUS_COUNT:
        return 1
    if report["error_files"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

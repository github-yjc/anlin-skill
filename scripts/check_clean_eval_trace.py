#!/usr/bin/env python3
"""Check clean-eval generator logs for protocol contamination."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


FORBIDDEN_PRE_DRAFT_REFERENCES = [
    "references/anti-ai-slop.md",
    "references/structure-patterns.md",
    "references/title-model.md",
    "references/generation-modes.md",
    "references/runtime-brief.md",
    "references/review-rubric.md",
    "references/writing-checklist.md",
    "references/self-check.md",
    "references/blind-judge-angles.md",
    "references/stylometric-ratio-protocol.md",
    "references/corpus-cards/",
]
VISIBLE_PROCESS_CHATTER_PATTERNS = [
    re.compile(r"(?im)^\s*(?:Let me plan|Let me write|Let me draft|I need to|The preflight says|The preflight detected|The main issues are|Scene\s+\d+:|Thinking:)"),
    re.compile(r"(?i)paying attention to:"),
    re.compile(r"(?i)the checker (?:requires|reports|detected|says)"),
]


@dataclass(frozen=True)
class TraceFinding:
    severity: str
    rule: str
    excerpt: str
    suggestion: str


def normalize_log(text: str) -> str:
    # Strip ANSI escapes but keep command text and tool names.
    return re.sub(r"\x1b\[[0-9;]*m", "", text).replace("\\", "/")


def first_index(text: str, patterns: list[str]) -> int:
    indices = [text.find(pattern) for pattern in patterns if text.find(pattern) >= 0]
    return min(indices) if indices else -1


def clean_excerpt(text: str, start: int, width: int = 180) -> str:
    if start < 0:
        return ""
    excerpt = text[start : start + width].replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", excerpt).strip()


def collect_findings(text: str) -> list[TraceFinding]:
    normalized = normalize_log(text)
    findings: list[TraceFinding] = []
    if "clean_run_checker.py" not in normalized:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval未调用clean_run_checker",
                clean_excerpt(normalized, 0),
                "Bounded clean-eval generation must use clean_run_checker.py. A run that uses only the normal checker belongs to ordinary/finalized repair, not the bounded checkpoint.",
            )
        )
    first_write = first_index(normalized, ["Write draft.md", "filesystem_write_file", "write_file"])
    pre_draft = normalized[:first_write] if first_write >= 0 else normalized
    if first_write >= 0 and ".anlin-clean-eval-mode" not in pre_draft:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval写稿前未检查模式标记",
                clean_excerpt(normalized, max(0, first_write - 80)),
                "The first generation tool action in a bounded clean-eval workspace must check `.anlin-clean-eval-mode` before writing `draft.md`; otherwise the generator may use ordinary checker flow.",
            )
        )
    for reference in FORBIDDEN_PRE_DRAFT_REFERENCES:
        index = pre_draft.find(reference)
        if index >= 0:
            findings.append(
                TraceFinding(
                    "error",
                    "clean-eval首稿前加载修复/评审引用",
                    clean_excerpt(pre_draft, index),
                    f"Clean-eval first draft may only load the minimal generation pack; defer `{reference}` until after the first complete draft/checker pass.",
                )
            )

    stop_index = first_index(normalized, ["CLEAN_RUN_PREFLIGHT_STOP", "CLEAN_RUN_STOP"])
    if stop_index >= 0:
        after_stop = normalized[stop_index:]
        post_stop_patterns = [
            ("stop后继续写稿", r"(Write draft\.md|Edit draft\.md|filesystem_write_file|filesystem_edit_file)", 0),
            ("stop后切普通checker", r"check_anlin_violations\.py", re.IGNORECASE),
            ("stop后删除状态", r"(Remove-Item|rm\s+|del\s+).{0,120}\.anlin-clean-run-state\.json", re.IGNORECASE),
            ("stop后读取checker源码", r"scripts/check_anlin_violations\.py.{0,120}(offset|Select-String|Read)", re.IGNORECASE),
        ]
        for rule, pattern, flags in post_stop_patterns:
            match = re.search(pattern, after_stop, flags | re.DOTALL)
            if match:
                findings.append(
                    TraceFinding(
                        "error",
                        rule,
                        clean_excerpt(after_stop, match.start()),
                        "After clean-run stop, the generator may only read the current draft once and output it unchanged. Use a separate finalized checkpoint for ordinary repair.",
                    )
                )

    if "Invalid Tool" in normalized:
        index = normalized.find("Invalid Tool")
        findings.append(
            TraceFinding(
                "warning",
                "无效工具调用",
                clean_excerpt(normalized, index),
                "Invalid tool calls do not prove style failure, but they indicate controller noise or agent confusion and should be recorded.",
            )
        )

    for pattern in VISIBLE_PROCESS_CHATTER_PATTERNS:
        match = pattern.search(normalized)
        if match:
            findings.append(
                TraceFinding(
                    "warning",
                    "clean-eval可见过程计划",
                    clean_excerpt(normalized, match.start()),
                    "The generation trace contains visible planning, thinking, or diagnostic restatement. This may be provider/runtime logging, but clean-eval reports should record it and the runtime guidance should keep the final user-visible answer article-only.",
                )
            )
            break

    return findings


def read_log_flexible(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a clean-eval opencode/output trace for contamination.")
    parser.add_argument("log", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = read_log_flexible(args.log)
    findings = collect_findings(text)
    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            print(f"[{finding.severity}] {finding.rule}: {finding.excerpt}\n  -> {finding.suggestion}")
    else:
        print("No clean-eval trace contamination found.")
    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

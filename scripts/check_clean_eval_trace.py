#!/usr/bin/env python3
"""Check clean-eval generator logs for protocol contamination."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


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
RHYTHM_SCRIPTS_PATTERN = r"(?:rebalance_line_rhythm|split_long_lines|merge_short_lines|soften_line_endings)\.py\b"
FORMATTED_PATCH_DRAFT_CONTEXT_BODY = (
    r"^\s*%\s*Patch\s+\d+\s+files?\b"
    r"(?:(?!^\s*(?:\$|TOOL|TITLE|INPUT|←|Write|Edit|OUTPUT\s+CLEAN_RUN|CLEAN_RUN))[\s\S]){0,600}"
    r"\bdraft\.md\b"
)
FORMATTED_PATCH_DRAFT_CONTEXT_PATTERN = r"(?im)" + FORMATTED_PATCH_DRAFT_CONTEXT_BODY
FORMATTED_PATCH_DRAFT_PRE_CONTEXT_BODY = (
    r"\bdraft\.md\b"
    r"(?:(?!^\s*(?:\$|TOOL|TITLE|INPUT|←|Write|Edit|OUTPUT\s+CLEAN_RUN|CLEAN_RUN))[\s\S]){0,600}"
    r"^\s*%\s*Patch\s+\d+\s+files?\b"
)
FORMATTED_PATCH_DRAFT_PRE_CONTEXT_PATTERN = r"(?im)" + FORMATTED_PATCH_DRAFT_PRE_CONTEXT_BODY


@dataclass(frozen=True)
class TraceFinding:
    severity: str
    rule: str
    excerpt: str
    suggestion: str


def normalize_log(text: str) -> str:
    # Strip ANSI escapes but keep command text and tool names. JSON event logs
    # escape Windows paths as `C:\\...`; collapse those escaped separators so
    # absolute write paths are not hidden as `C://...` after normalization.
    stripped = re.sub(r"\x1b\[[0-9;]*m", "", extract_json_event_trace(text))
    normalized = stripped.replace("\\\\", "/").replace("\\", "/")
    return re.sub(r"([A-Za-z]:)/+", r"\1/", normalized)


def extract_json_event_trace(text: str) -> str:
    """Convert OpenCode JSONL events to an action trace.

    The raw JSON stream can include complete skill/reference contents. Scanning
    those outputs as if they were actions creates false positives, because the
    skill body necessarily names forbidden pre-draft repair files while telling
    the generator not to load them. Keep commands, tool paths, checker output,
    and visible reasoning, but do not scan dumped skill/reference bodies as
    tool actions.
    """
    exported_trace = extract_opencode_export_trace(text)
    if exported_trace is not None:
        return exported_trace

    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return text

    events: list[dict] = []
    parsed_count = 0
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and "type" in event:
            events.append(event)
            parsed_count += 1

    if parsed_count == 0:
        return text

    chunks: list[str] = []
    for event in events:
        part = event.get("part")
        if not isinstance(part, dict):
            continue
        event_type = event.get("type") or part.get("type")

        if event_type == "reasoning":
            reasoning = part.get("text")
            if isinstance(reasoning, str) and reasoning.strip():
                chunks.append(f"Thinking: {reasoning}")
            continue

        if event_type == "text":
            visible_text = part.get("text")
            if isinstance(visible_text, str) and visible_text.strip():
                chunks.append(f"TEXT {visible_text}")
            continue

        if event_type != "tool_use":
            continue

        tool = part.get("tool") or ""
        state = part.get("state")
        if not isinstance(state, dict):
            state = {}
        tool_input = state.get("input")
        title = state.get("title") or part.get("title") or ""
        chunks.append(f"TOOL {tool}")
        if title:
            chunks.append(f"TITLE {title}")
        if tool_input is not None:
            chunks.append(f"INPUT {json.dumps(sanitized_tool_input(tool_input), ensure_ascii=False)}")

        # Loading the skill itself dumps the whole SKILL.md body. That body is
        # instruction text, not an additional pre-draft reference read.
        if tool == "skill":
            continue

        # For normal shell/tool calls, include command output because checker
        # stop boundaries live there. For file/reference reads, include only
        # the path/input; full file contents often contain forbidden names as
        # negative instructions.
        metadata = state.get("metadata")
        output = state.get("output")
        if isinstance(metadata, dict) and isinstance(metadata.get("output"), str):
            output = metadata["output"]
        include_output = tool in {"bash", "shell", "terminal", "cmd", "powershell"} or (
            isinstance(tool_input, dict)
            and isinstance(tool_input.get("command"), str)
        )
        if include_output and isinstance(output, str) and output.strip():
            chunks.append(f"OUTPUT {output}")

    return "\n".join(chunks) if chunks else text


def extract_opencode_export_trace(text: str) -> str | None:
    """Convert `opencode export <session>` JSON to the same compact trace."""
    try:
        exported = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(exported, dict) or not isinstance(exported.get("messages"), list):
        return None

    chunks: list[str] = []
    info = exported.get("info")
    if isinstance(info, dict) and isinstance(info.get("directory"), str):
        chunks.append(f"CWD {info['directory']}")

    for message in exported["messages"]:
        if not isinstance(message, dict):
            continue
        for part in message.get("parts", []):
            if not isinstance(part, dict):
                continue
            part_type = part.get("type")
            if part_type == "reasoning":
                reasoning = part.get("text")
                if isinstance(reasoning, str) and reasoning.strip():
                    chunks.append(f"Thinking: {reasoning}")
                continue
            if part_type == "text":
                visible_text = part.get("text")
                if isinstance(visible_text, str) and visible_text.strip():
                    chunks.append(f"TEXT {visible_text}")
                continue
            if part_type != "tool":
                continue

            tool = part.get("tool") or ""
            state = part.get("state")
            if not isinstance(state, dict):
                state = {}
            tool_input = state.get("input")
            title = state.get("title") or part.get("title") or ""
            chunks.append(f"TOOL {tool}")
            if title:
                chunks.append(f"TITLE {title}")
            if tool_input is not None:
                chunks.append(f"INPUT {json.dumps(sanitized_tool_input(tool_input), ensure_ascii=False)}")

            if tool == "skill":
                continue

            metadata = state.get("metadata")
            output = state.get("output")
            if isinstance(metadata, dict) and isinstance(metadata.get("output"), str):
                output = metadata["output"]
            include_output = tool in {"bash", "shell", "terminal", "cmd", "powershell"} or (
                isinstance(tool_input, dict)
                and isinstance(tool_input.get("command"), str)
            )
            if include_output and isinstance(output, str) and output.strip():
                chunks.append(f"OUTPUT {output}")

    return "\n".join(chunks) if chunks else text


def sanitized_tool_input(value: Any) -> Any:
    """Keep action-bearing fields while omitting large free-text payloads."""
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, child in value.items():
            if key in {"content", "text", "body"} and isinstance(child, str):
                sanitized[key] = "<content omitted>"
            else:
                sanitized[key] = sanitized_tool_input(child)
        return sanitized
    if isinstance(value, list):
        return [sanitized_tool_input(item) for item in value]
    return value


def first_index(text: str, patterns: list[str]) -> int:
    indices = [text.find(pattern) for pattern in patterns if text.find(pattern) >= 0]
    return min(indices) if indices else -1


def regex_action_indices(text: str, patterns: list[str]) -> list[int]:
    indices: set[int] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            indices.add(match.start())
    return sorted(indices)


def first_regex_action_index(text: str, patterns: list[str]) -> int:
    indices = regex_action_indices(text, patterns)
    return indices[0] if indices else -1


def actual_clean_run_checker_indices(text: str) -> list[int]:
    patterns = [
        r"(?im)^\s*\$\s+[^\n]*clean_run_checker\.py\b",
        r"(?im)^\s*TITLE\s+[^\n]*clean_run_checker\.py\b",
        r"(?im)^\s*INPUT\s+[^\n]*(?:command|cmd)[^\n]*clean_run_checker\.py\b",
    ]
    return regex_action_indices(text, patterns)


def actual_clean_run_checker_index(text: str) -> int:
    indices = actual_clean_run_checker_indices(text)
    return indices[0] if indices else -1


def actual_normal_checker_index(text: str) -> int:
    patterns = [
        r"(?im)^\s*\$\s+[^\n]*check_anlin_violations\.py\b",
        r"(?im)^\s*TITLE\s+[^\n]*check_anlin_violations\.py\b",
        r"(?im)^\s*INPUT\s+[^\n]*(?:command|cmd)[^\n]*check_anlin_violations\.py\b",
    ]
    indices: list[int] = []
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            indices.append(match.start())
    return min(indices) if indices else -1


def actual_checker_source_inspection_index(text: str) -> int:
    patterns = [
        r"(?im)^\s*TOOL\s+(?:read|filesystem_read_file)\b(?:\n(?!TOOL\s)[^\n]*){0,4}(?:clean_run_checker|check_anlin_violations)\.py\b",
        r"(?im)^\s*TOOL\s+grep\b(?:\n(?!TOOL\s)[^\n]*){0,4}(?:/scripts\b|/scripts/|\\scripts\b|\\scripts\\)",
        r"(?im)^\s*(?:\$|INPUT|TITLE)\s+[^\n]*(?:rg|grep|Select-String|Get-Content|gc|cat|type|Read)[^\n]*(?:clean_run_checker|check_anlin_violations)\.py\b",
    ]
    return first_regex_action_index(text, patterns)


def actual_draft_write_index(text: str) -> int:
    patterns = [
        r"(?im)^\s*(?:←\s*)?Write\s+\.?[/\\]?draft\.md\b",
        r"(?im)^\s*TITLE\s+Write\s+\.?[/\\]?draft\.md\b",
        # Formatted OpenCode logs can collapse file edits to only
        # `% Patch 1 file`, without the path. Count it only when the same
        # action block still names draft.md, before or after the patch line,
        # so unrelated patches do not hide a missing persisted article.
        FORMATTED_PATCH_DRAFT_CONTEXT_PATTERN,
        FORMATTED_PATCH_DRAFT_PRE_CONTEXT_PATTERN,
        r"(?im)^\s*INPUT\s+[^\n]*\"(?:path|filePath|file)\"\s*:\s*\"(?:\.?/)?draft\.md\"[^\n]*(?:content|write)",
        r"(?im)^\s*INPUT\s+[^\n]*\"(?:path|filePath|file)\"\s*:\s*\"[A-Za-z]:/[^\n\"]*/draft\.md\"[^\n]*(?:content|write)",
        r"(?im)^\s*INPUT\s+[^\n]*(?:content|write)[^\n]*\"(?:path|filePath|file)\"\s*:\s*\"(?:\.?/)?draft\.md\"",
        r"(?im)^\s*INPUT\s+[^\n]*(?:content|write)[^\n]*\"(?:path|filePath|file)\"\s*:\s*\"[A-Za-z]:/[^\n\"]*/draft\.md\"",
        r"(?im)^\s*(?:\$|>|>>)?\s*(?:@['\"]\s*\|\s*)?(?:Set-Content|Out-File)\s+(?:-Path|-LiteralPath)?\s*['\"]?\.?/?draft\.md['\"]?\b",
        r"(?im)^\s*['\"]@?\s*\|\s*(?:Set-Content|Out-File)\s+(?:-Path|-LiteralPath)?\s*['\"]?\.?/?draft\.md['\"]?\b",
    ]
    indices: list[int] = []
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            indices.append(match.start())
    return min(indices) if indices else -1


def actual_current_directory_check_index(text: str) -> int:
    patterns = [
        r"(?im)^\s*\$\s*(?:Get-Location|pwd)\b",
        r"(?im)^\s*\$\s+[^\n;|&]*(?:;|&&|\|\|)\s*(?:Get-Location|pwd)\b",
        r"(?im)^\s*TITLE\s+[^\n]*(?:Get-Location|pwd)\b",
        r"(?im)^\s*INPUT\s+[^\n]*(?:command|cmd)[^\n]*(?:Get-Location|pwd)\b",
    ]
    return first_regex_action_index(text, patterns)


def actual_skill_directory_cwd_index(text: str) -> int:
    patterns = [
        r"(?im)^\s*OUTPUT\s+[^\n]*(?:\.config/opencode/skills|/skills)/anlin-writing\s*$",
        r"(?im)^\s*[A-Za-z]:/[^\n]*(?:\.config/opencode/skills|/skills)/anlin-writing\s*$",
    ]
    return first_regex_action_index(text, patterns)


def actual_draft_mutation_indices(text: str) -> list[int]:
    patterns = [
        r"(?im)^\s*(?:←\s*)?(?:Write|Edit)\s+\.?[/\\]?draft\.md\b",
        r"(?im)^\s*TITLE\s+(?:Write|Edit)\s+\.?[/\\]?draft\.md\b",
        FORMATTED_PATCH_DRAFT_CONTEXT_PATTERN,
        FORMATTED_PATCH_DRAFT_PRE_CONTEXT_PATTERN,
        r"(?im)^\s*TOOL\s+filesystem_(?:write|edit)_file\b[^\n]*(?:\n[^\n]*){0,4}draft\.md\b",
        r"(?im)^\s*INPUT\s+[^\n]*(?:path|file)[^\n]*draft\.md[^\n]*(?:content|write|edit|old_string|new_string)",
        r"(?im)^\s*(?:\$|>|>>)?\s*(?:@['\"]\s*\|\s*)?(?:Set-Content|Out-File)\s+(?:-Path|-LiteralPath)?\s*['\"]?\.?[/\\]?draft\.md['\"]?\b",
        r"(?im)^\s*['\"]@?\s*\|\s*(?:Set-Content|Out-File)\s+(?:-Path|-LiteralPath)?\s*['\"]?\.?[/\\]?draft\.md['\"]?\b",
    ]
    return regex_action_indices(text, patterns)


def actual_rhythm_script_indices(text: str) -> list[int]:
    patterns = [
        rf"(?im)^\s*\$\s+[^\n]*{RHYTHM_SCRIPTS_PATTERN}",
        rf"(?im)^\s*TITLE\s+[^\n]*{RHYTHM_SCRIPTS_PATTERN}",
        rf"(?im)^\s*INPUT\s+[^\n]*(?:command|cmd)[^\n]*{RHYTHM_SCRIPTS_PATTERN}",
    ]
    return regex_action_indices(text, patterns)


def actual_ad_hoc_metric_probe_index(text: str) -> int:
    """Find generator-built metric probes that bypass the clean wrapper."""

    metric_terms = (
        r"Chinese chars|body_chinese_chars|Body lines|body_lines|Avg chars|mean_line|"
        r"line_lengths?|Line lengths|Short lines|short_lines|short breath|Long lines|"
        r"long_lines|comma[-_ ]?ending|period[-_ ]?ending|period per 1k|comma ratio|"
        r"connector|Connectors found|re\.findall|Measure-Object\s+-(?:Character|Line|Word)"
    )
    patterns = [
        rf"(?ims)^\s*\$\s*(?:python|py)\s+-c\s+['\"](?:(?!^\s*\$).){{0,3000}}(?:{metric_terms})",
        rf"(?ims)^\s*INPUT\s+[^\n]*(?:command|cmd)[^\n]*(?:python|py)\s+-c(?:(?!^\s*(?:TOOL|TITLE|INPUT|\$)).){{0,3000}}(?:{metric_terms})",
        r"(?im)^\s*\$\s*\(Get-Content\s+draft\.md\b[^\n]*Measure-Object\s+-(?:Character|Line|Word)",
        r"(?im)^\s*\$\s*Get-Content\s+draft\.md\b[^\n]*Measure-Object\s+-(?:Character|Line|Word)",
        r"(?im)^\s*\$\s*(?:wc|Measure-Object)\b[^\n]*(?:draft\.md|Character|Line|Word)",
    ]
    return first_regex_action_index(text, patterns)


def clean_wrapper_auto_rhythm_index(text: str, checker_index: int) -> int:
    if checker_index < 0:
        return -1
    stop_match = re.search(r"(?m)^\s*(?:OUTPUT\s+)?(?:CLEAN_RUN_PREFLIGHT|CLEAN_RUN_STOP):", text[checker_index:])
    end = checker_index + stop_match.start() if stop_match else len(text)
    segment = text[checker_index:end]
    patterns = [
        r"(?m)^\s*\{\"before\":\s*\{\"body_lines\"",
        r"(?m)^\s*soften_line_endings:\s*before=",
    ]
    return first_regex_action_index(segment, patterns)


def stale_rhythm_rewrite_indices(text: str) -> tuple[int, int] | None:
    rhythm_indices = actual_rhythm_script_indices(text)
    if not rhythm_indices:
        return None
    draft_mutations = actual_draft_mutation_indices(text)
    checker_indices = actual_clean_run_checker_indices(text)
    for mutation_index in draft_mutations:
        if not any(rhythm_index < mutation_index for rhythm_index in rhythm_indices):
            continue
        next_checker = next((checker for checker in checker_indices if checker > mutation_index), None)
        if next_checker is None:
            continue
        rhythm_after_mutation = any(mutation_index < rhythm_index < next_checker for rhythm_index in rhythm_indices)
        wrapper_auto_rhythm = clean_wrapper_auto_rhythm_index(text, next_checker) >= 0
        if not rhythm_after_mutation and not wrapper_auto_rhythm:
            return mutation_index, next_checker
    return None


def actual_nonrelative_draft_write_index(text: str) -> int:
    folded_text = re.sub(r"(?<=\S)\n\s*(?=\S)", "", text)
    loose_text = re.sub(r"\s+", " ", text)
    patterns = [
        r"(?im)^\s*←\s*Write\s+(?!\.?/?draft\.md\b)(?!\.?\\draft\.md\b)[^\n]*draft\.md\b",
        r"(?im)^\s*\?\s*Write\s+(?!\.?/?draft\.md\b)(?!\.?\\draft\.md\b)[^\n]*draft\.md\b",
        r"(?im)^\s*TITLE\s+Write\s+(?!\.?/?draft\.md\b)(?!\.?\\draft\.md\b)[^\n]*draft\.md\b",
        r"(?im)^\s*INPUT\s+[^\n]*(?:path|file)[^\n]*/(?:skills|skill-dir|anlin-writing)/[^\n]*draft\.md[^\n]*(?:content|write)",
        r"(?im)^\s*INPUT\s+[^\n]*(?:content|write)[^\n]*(?:path|file)[^\n]*/(?:skills|skill-dir|anlin-writing)/[^\n]*draft\.md",
        r"(?im)^\s*(?:\$|>|>>)?\s*(?:@['\"]\s*\|\s*)?(?:Set-Content|Out-File)\s+(?:-Path|-LiteralPath)?\s*['\"]?[^'\"]*/(?:skills|skill-dir|anlin-writing)/[^\n]*draft\.md\b",
        r"(?im)^\s*['\"]@?\s*\|\s*(?:Set-Content|Out-File)\s+(?:-Path|-LiteralPath)?\s*['\"]?[^'\"]*/(?:skills|skill-dir|anlin-writing)/[^\n]*draft\.md\b",
    ]
    indices: list[int] = []
    for haystack in (text, folded_text):
        for pattern in patterns:
            match = re.search(pattern, haystack)
            if match:
                indices.append(match.start())
    loose_patterns = [
        r"(?i)(?:←|\?|TITLE)\s*Write\s+(?!\.?[/\\]?draft\.md\b).{0,260}draft\.md\b",
    ]
    for pattern in loose_patterns:
        match = re.search(pattern, loose_text)
        if match:
            indices.append(match.start())
    return min(indices) if indices else -1


def actual_reference_action_index(text: str, reference: str) -> int:
    """Return the index of a real pre-draft reference load.

    Formatted OpenCode logs include visible reasoning that may quote the
    skill's no-load list. Only command/tool/action lines are evidence that the
    generator actually opened a forbidden reference.
    """
    escaped = re.escape(reference)
    patterns = [
        rf"(?im)^\s*(?:→\s*)?Read\s+[^\n]*{escaped}",
        rf"(?im)^\s*TITLE\s+Read\s+[^\n]*{escaped}",
        rf"(?im)^\s*INPUT\s+[^\n]*(?:path|file|command)[^\n]*{escaped}",
        rf"(?im)^\s*\$\s+[^\n]*(?:Get-Content|gc|type|cat|Select-String|rg|python|py)[^\n]*{escaped}",
    ]
    indices: list[int] = []
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            indices.append(match.start())
    return min(indices) if indices else -1


def actual_parent_skill_search_index(text: str) -> int:
    """Find attempts to rediscover the skill through a parent skills folder.

    In clean-eval the skill has already triggered. Searching sibling skills or
    a generic skills root before writing `draft.md` often causes permission
    failures and leaves no artifact, which is a protocol failure distinct from
    prose quality.
    """
    patterns = [
        r"(?im)^\s*!\s*permission requested:\s*external_directory\s*\([^)]*/skills/\*",
        r"(?im)^\s*✗\s*Glob\s+['\"][^'\"]*anlin-writing[^'\"]*['\"]\s+failed\s+in\s+[^\n]*/skills\b",
        r"(?im)^\s*(?:INPUT|TITLE|\$)\s+[^\n]*(?:glob|Get-ChildItem|rg|Select-String|find|ls)[^\n]*/skills/[^\n]*(?:\*|\*\*)",
        r"(?im)^\s*(?:INPUT|TITLE|\$)\s+[^\n]*(?:glob|Get-ChildItem|rg|Select-String|find|ls)[^\n]*(?:\.config/opencode/skills|\.opencode/skills)[^\n]*(?:\*|\*\*)",
    ]
    indices: list[int] = []
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            indices.append(match.start())
    return min(indices) if indices else -1


def actual_clean_stop_index(text: str) -> int:
    """Find a real clean-run stop emitted by the wrapper.

    Raw OpenCode logs can contain the full text of `clean-generation-brief.md`.
    That reference file names `CLEAN_RUN_PREFLIGHT_STOP` while explaining what
    to do later; treating that instruction text as an actual stop makes every
    subsequent draft write look like a protocol escape. A real stop is emitted
    as a standalone checker output line beginning with the stop token.
    """
    pattern = re.compile(r"(?m)^\s*(?:OUTPUT\s+)?(?:CLEAN_RUN_PREFLIGHT_STOP|CLEAN_RUN_STOP):")
    match = pattern.search(text)
    return match.start() if match else -1


def clean_excerpt(text: str, start: int, width: int = 180) -> str:
    if start < 0:
        return ""
    excerpt = text[start : start + width].replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", excerpt).strip()


def collect_findings(text: str) -> list[TraceFinding]:
    normalized = normalize_log(text)
    findings: list[TraceFinding] = []
    if actual_clean_run_checker_index(normalized) < 0:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval未调用clean_run_checker",
                clean_excerpt(normalized, 0),
                "Bounded clean-eval generation must use clean_run_checker.py. A run that uses only the normal checker belongs to ordinary/finalized repair, not the bounded checkpoint.",
            )
        )
    normal_checker_index = actual_normal_checker_index(normalized)
    if normal_checker_index >= 0:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval直接调用普通checker",
                clean_excerpt(normalized, normal_checker_index),
                "Bounded clean-eval generation must use only clean_run_checker.py. Direct normal-checker calls expose diagnostics outside the two-call protocol and contaminate the source-guidance measurement.",
            )
        )
    checker_source_index = actual_checker_source_inspection_index(normalized)
    if checker_source_index >= 0:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval读取checker源码",
                clean_excerpt(normalized, checker_source_index),
                "Clean-eval generators may use only the wrapper output as the repair interface. Do not grep/read checker scripts or tests for hidden tokens after a preflight or checker report.",
            )
        )
    metric_probe_index = actual_ad_hoc_metric_probe_index(normalized)
    if metric_probe_index >= 0:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval自建指标预检",
                clean_excerpt(normalized, metric_probe_index),
                "Do not run homemade counting, line-length, connector, punctuation, or regex metric probes in bounded clean-eval. The wrapper is the metric interface; repair from its reported messages and the article itself.",
            )
        )
    first_write = actual_draft_write_index(normalized)
    if first_write < 0:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval未写入draft.md",
                clean_excerpt(normalized, 0),
                "Bounded clean-eval generation must persist one complete titled article to draft.md before checker flow. Visible scratch prose in the terminal does not count.",
            )
        )
    wrong_write = actual_nonrelative_draft_write_index(normalized)
    if wrong_write >= 0:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval写稿路径不是相对draft.md",
                clean_excerpt(normalized, wrong_write),
                "Clean-eval must write the article as relative `draft.md` in the current case workspace. Do not append the case path under the skill directory or invent an absolute output path.",
            )
        )
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
    if first_write >= 0 and actual_current_directory_check_index(pre_draft) < 0:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval写稿前未确认当前目录",
                clean_excerpt(normalized, max(0, first_write - 120)),
                "Before the first clean-eval draft write, run Get-Location / pwd and confirm the current directory is the external case workspace. Marker checks alone do not prove the write tool is targeting the case directory.",
            )
        )
    skill_cwd_index = actual_skill_directory_cwd_index(pre_draft)
    if skill_cwd_index >= 0:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval当前目录是skill目录",
                clean_excerpt(pre_draft, skill_cwd_index),
                "The distributable skill directory is not an output workspace. Switch to an external case/task directory before writing draft.md.",
            )
        )
    for reference in FORBIDDEN_PRE_DRAFT_REFERENCES:
        index = actual_reference_action_index(pre_draft, reference)
        if index >= 0:
            findings.append(
                TraceFinding(
                    "error",
                    "clean-eval首稿前加载修复/评审引用",
                    clean_excerpt(pre_draft, index),
                    f"Clean-eval first draft may only load the minimal generation pack; defer `{reference}` until after the first complete draft/checker pass.",
                )
            )

    first_checker = actual_clean_run_checker_index(normalized)
    if first_checker >= 0:
        pre_checker = normalized[:first_checker]
        if first_write >= 0:
            writes_before_first_checker = [
                index for index in actual_draft_mutation_indices(pre_checker) if index >= first_write
            ]
            if len(writes_before_first_checker) > 1:
                findings.append(
                    TraceFinding(
                        "error",
                        "clean-eval首个wrapper前多次改写draft",
                        clean_excerpt(normalized, writes_before_first_checker[1]),
                        "The first persisted clean-eval article is part of the measurement. After the first draft.md write, run clean_run_checker.py instead of repeatedly overwriting draft.md to chase visible metrics.",
                    )
                )
        rhythm_before_first_checker = actual_rhythm_script_indices(pre_checker)
        if rhythm_before_first_checker:
            index = rhythm_before_first_checker[0]
            findings.append(
                TraceFinding(
                    "error",
                    "clean-eval首个wrapper前运行节奏脚本",
                    clean_excerpt(pre_checker, index),
                    "The first saved clean-eval draft must be measured before rhythm scripts touch it. Use rhythm scripts only after clean_run_checker.py reports a shape problem.",
                )
            )
    parent_skill_index = actual_parent_skill_search_index(pre_draft)
    if parent_skill_index >= 0:
        findings.append(
            TraceFinding(
                "error",
                "clean-eval首稿前搜索父级skill目录",
                clean_excerpt(pre_draft, parent_skill_index),
                "After anlin-writing has triggered, do not glob/search parent or sibling skill directories to rediscover it. Use the loaded skill instructions, persist draft.md, and let the controller validate the artifact.",
            )
        )

    stale_rhythm = stale_rhythm_rewrite_indices(normalized)
    if stale_rhythm is not None:
        mutation_index, _checker_index = stale_rhythm
        findings.append(
            TraceFinding(
                "error",
                "节奏脚本后重写未重跑节奏修复",
                clean_excerpt(normalized, mutation_index),
                "If draft.md is written or edited after a rhythm script in bounded clean-eval, rerun the relevant rhythm script or preserve the same line-broken corridor before the next clean_run_checker.py call. A previous split/merge/rebalance does not apply to a newly overwritten draft.",
            )
        )

    stop_index = actual_clean_stop_index(normalized)
    if stop_index >= 0:
        after_stop = normalized[stop_index:]
        post_stop_patterns = [
            (
                "stop后继续写稿",
                r"(?m)^\s*(?:←\s*)?(?:Write|Edit)\s+draft\.md\b|^\s*TITLE\s+(?:Write|Edit)\s+draft\.md\b|"
                + FORMATTED_PATCH_DRAFT_CONTEXT_BODY
                + r"|^\s*TOOL\s+filesystem_(?:write|edit)_file\b",
                0,
            ),
            (
                "stop后切普通checker",
                r"(?m)^\s*(?:\$\s*)?(?:python|py|uv|bash|powershell|cmd|INPUT|TITLE)\b[^\n]{0,220}check_anlin_violations\.py",
                re.IGNORECASE,
            ),
            ("stop后删除状态", r"(Remove-Item|rm\s+|del\s+).{0,120}\.anlin-clean-run-state\.json", re.IGNORECASE),
            (
                "stop后读取checker源码",
                r"(?m)^\s*(?:INPUT|TITLE|python|py|uv|bash|powershell|cmd)\b[^\n]{0,220}scripts/check_anlin_violations\.py[^\n]{0,120}(offset|Select-String|Read)",
                re.IGNORECASE,
            ),
            (
                "stop后最终输出带过程前缀",
                r"(?m)^\s*TEXT\s+(?:完成[。:：]?|以下是|.*最终文章|Clean run|按协议|Here\s+(?:is|it is)|---\s*$)",
                re.IGNORECASE,
            ),
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

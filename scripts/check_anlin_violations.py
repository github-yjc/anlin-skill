#!/usr/bin/env python3
"""Deterministic hard-rule checker for Anlin-style drafts.

This script does not judge whether a draft has Anlin's voice. It only reports
searchable violations and weak signals that should trigger manual revision.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    line: int
    excerpt: str
    suggestion: str


# Note: "你见过" removed from FORBIDDEN_TERMS - Anlin uses it once (20220505) as rhetorical question,
# not the "那种笑你见过很多次" abstract generalization pattern. "那种笑" separately caught.
FORBIDDEN_TERMS = [
    "两天前",
    "不久前",
    "前不久",
    "蛮",
    "许多",
    "啥的",
    "顺嘴",
    "有的没的",
    "嘴馋",
    "看了下",
    "不挑",
    "包邮",
    "差不多了",
    "面议",
    "药房",
    "润色",
    "项目经历",
    "政府工作报告",
    "App",
    "便利店",
    "嘿嘿",
    "嘻嘻",
    "写道",
    "那种笑",
    "关机睡觉",
    "按时吃饭",
    "算是全国最便宜",
    "便宜归便宜",
    "像发光的豆腐块",
    "我妈要是知道",
]

COMMENT_CHAIN_TERMS = ["有人说", "评论说", "回复说", "热评"]
LOW_FREQUENCY_TERMS = ["然而", "因此", "可是", "也许", "或许", "认为", "意识到"]
HIGH_FREQUENCY_TERMS = ["其实", "觉得", "发现", "好像", "不过", "突然", "于是", "因为", "所以"]
NORMAL_ROUTINE_TERMS = ["关机", "关灯", "按时睡觉", "关机睡觉"]
DRIFT_TERMS = [
    "压缩机",
    "低频",
    "高频",
    "缓解期",
    "恢复期",
    "发作期",
    "抗争",
    "反抗",
    "挣扎",
    "人生哲学",
    "彻底",
    "已读不回",
    "太熟悉了",
]
HOLLOW_OBSERVATION_TERMS = [
    "其实不知道在吵什么",
    "好像也没什么区别",
    "不就是那点事",
    "无非是又一天",
]
# Note: "沉默了" removed from FAKE_SENTIMENT_TERMS - Anlin uses it 5 times across 4 articles,
# typically followed by concrete action ("她沉默了会/说"). The issue is standalone "沉默了。" as
# scene ender without follow-up action. That pattern is caught by hollow observation check.
FAKE_SENTIMENT_TERMS = [
    "看了好一会",
    "不知道该说什么",
    "就那么看着",
]
DRIFT_MESSAGES = {
    "睡吧": ("warning", "imperative goodnight closure — prefer 睡了/去睡了/不写了"),
    "招聘软件": ("info", "abstract noun — prefer 点开招聘/刷了刷招聘"),
}


def clean_excerpt(line: str) -> str:
    stripped = line.strip()
    return stripped[:120] + ("..." if len(stripped) > 120 else "")


def is_chinese_word_char(char: str) -> bool:
    return bool(re.match(r"[\u4e00-\u9fff]", char))


def has_word_boundary(text: str, term: str, start: int) -> bool:
    """Check that a short term is not embedded in a longer Chinese word."""
    preceding = text[start - 1] if start > 0 else " "
    following = text[start + len(term)] if start + len(term) < len(text) else " "
    return not (is_chinese_word_char(preceding) or is_chinese_word_char(following))


def add_term_findings(findings: list[Finding], lines: list[str], terms: list[str], severity: str, rule: str, suggestion: str) -> None:
    for line_number, line in enumerate(lines, start=1):
        for term in terms:
            start = 0
            while True:
                index = line.find(term, start)
                if index == -1:
                    break
                if len(term) <= 2 and not has_word_boundary(line, term, index):
                    start = index + len(term)
                    continue
                findings.append(Finding(severity, f"{rule}: {term}", line_number, clean_excerpt(line), suggestion))
                break


def add_drift_term_findings(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        for term, (severity, suggestion) in DRIFT_MESSAGES.items():
            if term in line:
                findings.append(Finding(severity, f"词汇域漂移: {term}", line_number, clean_excerpt(line), suggestion))


def check_not_x_is_y(findings: list[Finding], lines: list[str]) -> None:
    pattern = re.compile(r"不是[^，。！？\n]{1,24}[,，]?[而只也]?是")
    matches = [(line_number, line) for line_number, line in enumerate(lines, start=1) if pattern.search(line)]
    if len(matches) <= 1:
        return
    for line_number, line in matches:
        findings.append(Finding("error", "不是X是Y overuse", line_number, clean_excerpt(line), "全篇最多保留一次；优先直接陈述Y。"))


def check_money_suffix(findings: list[Finding], lines: list[str]) -> None:
    arabic_pattern = re.compile(r"\d+(?:\.\d+)?\s*(?:块|元)")
    chinese_pattern = re.compile(r"[零一二两三四五六七八九十百千万亿\d]+(?:\.\d+)?\s*(?:块|元)")
    for line_number, line in enumerate(lines, start=1):
        if arabic_pattern.search(line):
            findings.append(
                Finding(
                    "warning",
                    "金额后缀（阿拉伯数字）",
                    line_number,
                    clean_excerpt(line),
                    "金额后缀通常删除；如需保留，确认是原文式口语而非账本语言。",
                )
            )
        elif chinese_pattern.search(line):
            findings.append(
                Finding(
                    "info",
                    "金额后缀（中文数字）",
                    line_number,
                    clean_excerpt(line),
                    "Chinese numeral money suffix (e.g. 五块) — spoken-colloquial tolerated, but flag for review.",
                )
            )


def check_like_something(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        if "像什么" in line:
            findings.append(Finding("error", "像什么X句式", line_number, clean_excerpt(line), "删除“什么”，改成直接的“像X”或更具体描述。"))


def check_repeated_you(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        if line.count("又") >= 2 and "又" in line:
            findings.append(Finding("warning", "同一行多次使用又", line_number, clean_excerpt(line), "若不是“又A又B”并列结构，拆成短句或换词。"))


def check_dialogue_quotes(findings: list[Finding], lines: list[str]) -> None:
    pattern = re.compile(r"(?:说|问|继续说|又说|他说|她说|我说).{0,8}[“\"『「]")
    for line_number, line in enumerate(lines, start=1):
        if pattern.search(line):
            findings.append(Finding("warning", "疑似日常对话引号", line_number, clean_excerpt(line), "日常对话不用引号；词组/概念引用可以保留。"))


def check_high_frequency_coverage(findings: list[Finding], text: str) -> None:
    present = [term for term in HIGH_FREQUENCY_TERMS if term in text]
    if len(present) < 5:
        findings.append(Finding("warning", "高频词覆盖不足", 0, f"present={present}", "自然补入至少5个高频连接词，不要硬塞。"))


def check_period_comma_ratio(findings: list[Finding], lines: list[str]) -> None:
    content_lines = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if not content_lines:
        return
    sample = content_lines[:20]
    comma_endings = sum(1 for line in sample if line.endswith("，") or line.endswith(","))
    ratio = comma_endings / len(sample)
    if len(content_lines) < 8:
        findings.append(
            Finding(
                "info",
                "行末逗号比例",
                0,
                f"first_{len(sample)}_lines_ratio={ratio:.2f}",
                "short draft, ratio based on limited sample",
            )
        )
    elif ratio < 0.45 or ratio > 0.85:
        findings.append(
            Finding(
                "info",
                "行末逗号比例",
                0,
                f"first_{len(sample)}_lines_ratio={ratio:.2f}",
                "参考区间约60-75%；偏离时人工检查节奏。",
            )
        )


def content_scene_blocks(lines: list[str]) -> list[str]:
    """Return non-empty text blocks separated by blank lines, excluding headings and metadata."""
    filtered = [line for line in lines if not line.strip().startswith(("#", "<!--"))]
    text = "\n".join(filtered)
    return [block.strip() for block in re.split(r"\n\s*\n|\n\.\s*\n", text) if block.strip()]


def detect_style(text: str) -> str:
    """Detect 'sincere'/'truthful' style from title or metadata; default to standard."""
    lower_text = text.lower()
    if any(marker in lower_text for marker in ["真诚", "truthful", "sincere", "真心话"]):
        return "sincere"
    return "standard"


def check_scene_count(findings: list[Finding], lines: list[str], text: str) -> None:
    blocks = content_scene_blocks(lines)
    count = len(blocks)
    style = detect_style(text)
    if style == "sincere":
        expected_range = "4-7"
        low, high = 4, 7
    else:
        # Standard diary: 5-10 is the corpus range (Phase A: 5-8, Phase D: 7-12)
        # Tight 5-7 would fail many Anlin originals (Phase C: 8-12)
        expected_range = "5-10"
        low, high = 5, 10
    if count < low or count > high:
        findings.append(
            Finding(
                "warning",
                "场景数量",
                0,
                f"scene_blocks={count} (expected {expected_range} for {style})",
                "调整蒙太奇密度，删除可删场景或补充必要场景。",
            )
        )
    else:
        findings.append(
            Finding(
                "info",
                "场景数量",
                0,
                f"scene_blocks={count} (expected {expected_range} for {style})",
                "scene count within expected range",
            )
        )


def check_breathing_point(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style != "standard":
        return
    pattern = re.compile(r"^[\u4e00-\u9fff]{1,2}[。，！？]$")
    for line_number, line in enumerate(lines, start=1):
        if pattern.match(line.strip()):
            findings.append(Finding("info", "呼吸点", line_number, clean_excerpt(line), "发现短句呼吸点"))
            return
    findings.append(Finding("warning", "呼吸点缺失", 0, "", "标准日寄建议至少保留一个1-2字独立短句作为呼吸点。"))


def check_metadata_comment(findings: list[Finding], text: str) -> None:
    pattern = re.compile(
        r"<!--\s*Anlin-style\s*\|\s*date-zone:\s*([^\s|]+)\s*\|\s*verification:\s*([^\s|]+)\s*\|\s*corpus:\s*([^\s|]+)\s*-->"
    )
    match = pattern.search(text)
    if not match:
        findings.append(
            Finding(
                "warning",
                "元数据注释",
                0,
                "",
                "缺少或格式错误的 HTML 元数据注释；需要 <!-- Anlin-style | date-zone: ... | verification: ... | corpus: ... -->",
            )
        )
        return
    date_zone, verification, corpus = match.groups()
    valid_date_zones = {"high", "medium", "low", "projection", "current-projection", "inferred"}
    valid_verifications = {"full-corpus", "fragment-level"}
    valid_corpus = {"available", "unavailable"}
    issues = []
    if date_zone not in valid_date_zones:
        issues.append(f"date-zone '{date_zone}' invalid")
    if verification not in valid_verifications:
        issues.append(f"verification '{verification}' invalid")
    if corpus not in valid_corpus:
        issues.append(f"corpus '{corpus}' invalid")
    if issues:
        findings.append(
            Finding(
                "warning",
                "元数据注释",
                0,
                f"date-zone={date_zone}, verification={verification}, corpus={corpus}",
                "; ".join(issues) + "。",
            )
        )


EXPLAINER_TERMS = ["好像多活了", "好像什么都没变", "其实什么都没"]
SECOND_COUNT_PATTERN = r"\d+秒"
DIALOGUE_STACK_PATTERN = r"(?:^|[。，！？\n])([^。，！？\n]{0,5}[说]){3,}"

def check_news_name_drop(findings: list[Finding], lines: list[str]) -> None:
    """Detect '刷到X的新闻' as standalone scene entry — a common agent formula."""
    pattern = re.compile(r"刷到.*的新闻|看到.*的热搜")
    for line_number, line in enumerate(lines, start=1):
        if pattern.search(line):
            findings.append(Finding("warning", "新闻名称独立观察", line_number, clean_excerpt(line), "Anlin 通过具体媒介进入在线内容（'翻X时看到''刷到一条视频''点开评论看到'），不通过新闻标题。如果后面只是公式化的'下面吵了X条，关了'→整个场景删除。"))


def collect_findings(text: str) -> list[Finding]:
    lines = text.splitlines()
    findings: list[Finding] = []
    add_term_findings(findings, lines, COMMENT_CHAIN_TERMS, "warning", "可能的评论链", "Anlin 在线内容入口是'我看到了什么，我什么反应'。检查上下文：如果这是评论链格式（热评→回复→又有人说）→删除。如果是一般观察或转述（'有人说当年我差点就买了'）→可能可接受，但需人工确认。")
    add_term_findings(findings, lines, FORBIDDEN_TERMS, "warning", "禁用/高风险词", "替换为 Anlin 词汇域内的具体动作或感官描述。")
    add_term_findings(findings, lines, LOW_FREQUENCY_TERMS, "info", "低频词", "优先替换为不过/所以/可能/好像/觉得/发现。")
    add_term_findings(findings, lines, NORMAL_ROUTINE_TERMS, "warning", "正常作息词", "确认是否破坏摆烂青年人设；必要时改成更具体的失序动作。")
    add_drift_term_findings(findings, lines)
    add_term_findings(findings, lines, DRIFT_TERMS, "warning", "词汇域漂移", "对照§6.6替换为具体动作、状态或感官描述。")
    add_term_findings(findings, lines, HOLLOW_OBSERVATION_TERMS, "error", "无力观察句式", "空洞落点——读完后无信息增量。删除该场景或改写为携带笑/痛/洞察的具体观察。")
    add_term_findings(findings, lines, FAKE_SENTIMENT_TERMS, "warning", "假感动收尾", "静止情绪画面替代具体动作——用具体动作收束（关了、划掉、回了句去你妈的、又打开了）。")
    check_news_name_drop(findings, lines)
    check_not_x_is_y(findings, lines)
    check_money_suffix(findings, lines)
    check_like_something(findings, lines)
    check_repeated_you(findings, lines)
    check_dialogue_quotes(findings, lines)
    check_high_frequency_coverage(findings, text)
    check_period_comma_ratio(findings, lines)
    check_scene_count(findings, lines, text)
    check_breathing_point(findings, lines, text)
    check_metadata_comment(findings, text)
    return findings


def format_text(findings: list[Finding]) -> str:
    if not findings:
        return "No deterministic violations found. Manual voice review is still required."
    output = []
    for finding in findings:
        location = f"line {finding.line}" if finding.line else "global"
        output.append(f"[{finding.severity}] {location} {finding.rule}\n  {finding.excerpt}\n  -> {finding.suggestion}")
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deterministic Anlin-style hard-rule violations.")
    parser.add_argument("file", type=Path, help="Draft markdown/text file to inspect")
    parser.add_argument("--json", action="store_true", help="Output JSON findings")
    parser.add_argument("--strict", action="store_true", help="Return nonzero for warnings as well as errors")
    args = parser.parse_args()

    text = args.file.read_text(encoding="utf-8")
    findings = collect_findings(text)
    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    else:
        print(format_text(findings))
    if args.strict:
        return 1 if any(finding.severity in {"error", "warning"} for finding in findings) else 0
    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

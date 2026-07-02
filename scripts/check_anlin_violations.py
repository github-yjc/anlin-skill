#!/usr/bin/env python3
"""Deterministic review-signal checker for Anlin-style drafts.

This script does not judge whether a draft has Anlin's voice. It only reports
searchable violations and weak signals that should trigger manual revision.
It is calibrated so original corpus files should not fail with hard errors.
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
PROCESS_LEAK_TERMS = [
    "State Card",
    "Prompt item",
    "prompt item",
    "分桶",
    "visible pressure",
    "driver：",
    "pressure #",
    "preflight",
    "首段 preflight",
    "校验通过",
    "Jaccard",
    "jaccard",
    "与 38 篇",
    "内部）：",
]
PROCESS_LEAK_LINE_PATTERNS = [
    r"^#\s*草拟\s*$",
    r"^草拟\s*$",
    r"^\*\*State Card",
]
TOPIC_DIAGNOSTIC_TITLE_TERMS = [
    "春招",
    "求职",
    "面试",
    "offer",
    "入职",
    "情人节",
    "平安夜",
    "母亲节",
    "婚礼",
    "痛风",
    "跨年",
    "搬家",
    "写作",
    "外卖",
    "中暑",
    "租房",
]
HIGH_SIGNAL_OPENING_TERMS = [
    "春招",
    "offer",
    "入职体检",
    "租房补贴",
    "情人节",
    "母亲节",
    "婚礼",
    "痛风",
    "跨年",
    "搬家",
    "写不出来",
    "无人便利店",
    "简历",
]
LEARNED_ENDING_LINES = {
    "哦。",
    "算了。",
    "睡了。",
    "关屏。",
    "屏幕暗了。",
    "屏幕黑了。",
    "嗡嗡嗡。",
}
THEME_DOMAINS = {
    "job": [
        "春招",
        "求职",
        "offer",
        "入职",
        "体检",
        "租房补贴",
        "大厂",
        "boss",
        "直聘",
        "招聘",
        "岗位",
        "职位",
        "简历",
        "hr",
        "工位",
        "公积金",
        "水杯",
        "同学群",
    ],
    "romance": ["情人节", "礼物", "玫瑰", "情侣", "对象", "恋爱", "结婚", "婚礼", "随礼"],
    "family": ["母亲节", "我妈", "妈妈", "我爸", "鸡蛋", "雨衣", "回家", "饭桌"],
    "illness": ["痛风", "脚踝", "尿酸", "肿", "疼", "富贵病", "腐乳", "可乐"],
}
TASTEFUL_WITHHOLDING_ENDINGS = [
    "没点开",
    "没回",
    "没看",
    "没发",
    "没说话",
    "放下手机",
    "扣在桌上",
]
QUIET_EXPLANATION_PATTERNS = [
    r"大概是因为[^。！？\n]{1,35}",
    r"可能是因为[^。！？\n]{1,35}",
    r"突然觉得[^。！？\n]{1,35}",
]
ENGINE_SIGNAL_TERMS = [
    "还以为",
    "原来",
    "算",
    "尿",
    "厕所",
    "马桶",
    "痔疮",
    "阳痿",
    "傻逼",
    "滚",
    "去你妈",
    "像",
    "算法",
    "系统",
    "ELO",
    "血压",
    "麻木",
]
SEALED_NIGHT_TERMS = ["失眠", "床", "枕", "闹钟", "睡", "手机", "通知", "群", "Boss", "直聘"]
CLOSED_LOOP_TAIL_TERMS = ["到现在也没", "明天再", "还没请", "还没还", "又点开"]
STRICT_ERROR_RULE_PREFIXES = (
    "可能的评论链",
    "题面诊断型标题",
    "题面高信号开头",
    "标准日寄完整文章篇幅偏短",
    "习得式结尾按钮",
    "单主题词密度偏高",
    "文艺悬停式结尾",
    "安静解释句",
    "段落发动机信号偏弱",
    "封闭夜晚短篇结构",
    "高频词覆盖不足",
    "呼吸点缺失",
)
STRICT_ERROR_RULE_NAMES = {"行末逗号比例"}


def clean_excerpt(line: str) -> str:
    stripped = line.strip()
    return stripped[:120] + ("..." if len(stripped) > 120 else "")


def chinese_len(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def normalize_title_line(line: str) -> str:
    title = line.strip()
    title = re.sub(r"^#+\s*", "", title).strip()
    title = re.sub(r"^(标题|题目)\s*[:：]\s*", "", title).strip()
    for marker in ("**", "__", "*", "_"):
        if title.startswith(marker) and title.endswith(marker) and len(title) > len(marker) * 2:
            title = title[len(marker):-len(marker)].strip()
    return title


def split_title_and_content_lines(lines: list[str]) -> tuple[str, list[str]]:
    nonempty = [(index, line.strip()) for index, line in enumerate(lines) if line.strip()]
    if not nonempty:
        return "", []
    first_index, first = nonempty[0]
    if first.startswith("# "):
        return normalize_title_line(first), [line.strip() for line in lines[first_index + 1 :] if line.strip()]
    if not re.search(r"[。！？!?，,：:；;]", first) and chinese_len(first) <= 24:
        return normalize_title_line(first), [line.strip() for line in lines[first_index + 1 :] if line.strip()]
    return "", [line.strip() for line in lines if line.strip()]


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


def check_process_leakage(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        for pattern in PROCESS_LEAK_LINE_PATTERNS:
            if re.search(pattern, stripped):
                findings.append(
                    Finding(
                        "error",
                        "过程说明泄漏",
                        line_number,
                        clean_excerpt(line),
                        "用户要文章时最终输出只能包含标题和正文；删除草稿标记、分隔线、状态卡、校验说明和控制器说明。",
                    )
                )
                break
        for term in PROCESS_LEAK_TERMS:
            if term in line:
                findings.append(
                    Finding(
                        "error",
                        f"过程说明泄漏: {term}",
                        line_number,
                        clean_excerpt(line),
                        "用户要文章时最终输出只能包含标题和正文；内部状态卡、prompt分桶、校验结果和语料对比必须留在过程或报告中。",
                    )
                )
                break


def check_not_x_is_y(findings: list[Finding], lines: list[str]) -> None:
    pattern = re.compile(r"不是[^，。！？\n]{1,24}[,，]?[而只也]?是")
    matches = [(line_number, line) for line_number, line in enumerate(lines, start=1) if pattern.search(line)]
    if len(matches) <= 1:
        return
    for line_number, line in matches:
        findings.append(Finding("warning", "不是X是Y overuse", line_number, clean_excerpt(line), "高风险句式；若是解释性二元对比，优先直接陈述Y。若来自自然对话或原文式复杂句，人工保留。"))


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
    pattern = re.compile(r"(?<!好)像什么(?!都|也|特别|要紧|没|不)[^，。！？\n]{1,16}")
    for line_number, line in enumerate(lines, start=1):
        if pattern.search(line):
            findings.append(Finding("warning", "像什么X句式", line_number, clean_excerpt(line), "若是装饰性'像什么X'，删除“什么”或改成更具体描述；不要误改'好像什么都...'类正常句。"))


def check_repeated_you(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        if line.count("又") >= 2 and "又" in line:
            findings.append(Finding("warning", "同一行多次使用又", line_number, clean_excerpt(line), "若不是“又A又B”并列结构，拆成短句或换词。"))


def check_dialogue_quotes(findings: list[Finding], lines: list[str]) -> None:
    pattern = re.compile(r"(?:说|问|继续说|又说|他说|她说|我说).{0,8}[“\"『「]")
    for line_number, line in enumerate(lines, start=1):
        if pattern.search(line):
            findings.append(Finding("info", "疑似日常对话引号", line_number, clean_excerpt(line), "原文中存在引号；这里只提示人工检查是否为代理生成稿的戏剧化对话。"))


def check_high_frequency_coverage(findings: list[Finding], text: str) -> None:
    present = [term for term in HIGH_FREQUENCY_TERMS if term in text]
    if len(present) < 5:
        findings.append(Finding("warning", "高频词覆盖不足", 0, f"present={present}", "自然补入至少5个高频连接词，不要硬塞。"))


def check_diagnostic_title(findings: list[Finding], lines: list[str]) -> None:
    title, _ = split_title_and_content_lines(lines)
    if not title:
        return
    if title != "日寄" and title.endswith("日寄"):
        matched = [term for term in TOPIC_DIAGNOSTIC_TITLE_TERMS if term in title]
        if matched:
            findings.append(
                Finding(
                    "warning",
                    "题面诊断型标题",
                    1,
                    title,
                    f"标题含高信号主题词 {matched}；标准日寄盲评通常优先弱化为“日寄”，除非修饰词来自正文里的侧面把手。",
                )
            )


def check_high_signal_opening(findings: list[Finding], lines: list[str]) -> None:
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [line for line in content_lines if not line.startswith("<!--")][:5]
    if not visible_lines:
        return
    first_line_matches = [term for term in HIGH_SIGNAL_OPENING_TERMS if term in visible_lines[0]]
    opening_text = "\n".join(visible_lines)
    opening_matches = sorted({term for term in HIGH_SIGNAL_OPENING_TERMS if term in opening_text})
    if first_line_matches or len(opening_matches) >= 2:
        findings.append(
            Finding(
                "warning",
                "题面高信号开头",
                1,
                " / ".join(visible_lines[:3]),
                "开头过早暴露题面压力；标准日寄应从身体、物件、app残留或无用动作进入，再让主题晚一点漏出。",
            )
        )


def check_standard_diary_length(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    style = detect_style(text)
    if style != "standard" or "日寄" not in title:
        return
    body = "\n".join(line for line in content_lines if not line.startswith("<!--"))
    chars = chinese_len(body)
    if 0 < chars < 650:
        findings.append(
            Finding(
                "warning",
                "标准日寄完整文章篇幅偏短",
                0,
                f"body_chinese_chars={chars}",
                "完整文章盲评建议约650-1200字；扩展具体动作、对话、身体/金钱后果和非主题残留，或改为短体裁匹配评估。",
            )
        )


def check_learned_ending_button(findings: list[Finding], lines: list[str]) -> None:
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if not visible_lines:
        return
    tail = visible_lines[-3:]
    normalized_tail = [re.sub(r"\s+", "", line) for line in tail]
    matched = [line for line in normalized_tail if line in LEARNED_ENDING_LINES]
    if matched:
        findings.append(
            Finding(
                "warning",
                "习得式结尾按钮",
                len(lines),
                " / ".join(tail),
                "哦/算了/睡了/关屏/屏幕暗等只在被前文强迫时保留；否则换成未完成动作、回复、路线、物件、付款或身体中断。",
            )
        )


def check_theme_density(findings: list[Finding], text: str) -> None:
    lower_text = text.lower()
    for domain, terms in THEME_DOMAINS.items():
        matched_terms = [term for term in terms if term.lower() in lower_text]
        hit_count = sum(lower_text.count(term.lower()) for term in terms)
        if len(matched_terms) >= 7 or hit_count >= 12:
            findings.append(
                Finding(
                    "warning",
                    f"单主题词密度偏高: {domain}",
                    0,
                    f"terms={matched_terms}, hits={hit_count}",
                    "盲评高风险：场景可能都在服务同一主轴。替换一段为由气味、身体、路线、无关社交或脏物件触发的旁逸分支。",
                )
            )


def check_tasteful_withholding_ending(findings: list[Finding], lines: list[str]) -> None:
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if not visible_lines:
        return
    tail_text = "\n".join(visible_lines[-3:])
    if any(term in tail_text for term in TASTEFUL_WITHHOLDING_ENDINGS):
        findings.append(
            Finding(
                "warning",
                "文艺悬停式结尾",
                len(lines),
                " / ".join(visible_lines[-3:]),
                "没点开/没回/放下手机等结尾容易变成漂亮短篇收束；确认是否有低处后果，否则改成身体、付款、路线、冷饭、错物件或第二条消息。",
            )
        )


def check_quiet_explanation(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        for pattern in QUIET_EXPLANATION_PATTERNS:
            if re.search(pattern, line):
                findings.append(
                    Finding(
                        "warning",
                        "安静解释句",
                        line_number,
                        clean_excerpt(line),
                        "这类句子容易把伤口解释干净；优先删除解释，让外部人物、app、身体或低处后果回答。",
                    )
                )
                break


def check_engine_signal_density(findings: list[Finding], text: str) -> None:
    style = detect_style(text)
    if style != "standard":
        return
    hits = [term for term in ENGINE_SIGNAL_TERMS if term in text]
    if len(hits) < 3:
        findings.append(
            Finding(
                "warning",
                "段落发动机信号偏弱",
                0,
                f"present={hits}",
                "标准日寄不能只是安静低落；至少需要误读、自毁、社交误伤、身体降格或荒谬系统解释中的几种。",
            )
        )


def check_sealed_nocturne(findings: list[Finding], text: str) -> None:
    title, content_lines = split_title_and_content_lines(text.splitlines())
    body = "\n".join(content_lines)
    night_hits = [term for term in SEALED_NIGHT_TERMS if term in text]
    tail = "\n".join(content_lines[-6:]) if content_lines else ""
    tail_hits = [term for term in CLOSED_LOOP_TAIL_TERMS if term in tail]
    if ("失眠" in title or "失眠" in body) and len(night_hits) >= 6 and tail_hits:
        findings.append(
            Finding(
                "warning",
                "封闭夜晚短篇结构",
                0,
                f"night_terms={night_hits}, tail={tail_hits}",
                "标准日寄高风险：文章可能封闭在一夜、一房间、一串通知里，并用早期物件/旧债闭环。加入时间/空间横跳，或改掉整齐回收结尾。",
            )
        )


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
        severity = "warning" if ratio < 0.15 or ratio > 0.9 else "info"
        findings.append(
            Finding(
                severity,
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
    if count < low:
        findings.append(
            Finding(
                "warning",
                "段落块数量偏少",
                0,
                f"paragraph_blocks={count} (rough expected {expected_range} for {style})",
                "粗略段落块偏少；检查是否缺少场景、呼吸句或内部转向。",
            )
        )
    elif count > high:
        findings.append(
            Finding(
                "info",
                "段落块数量偏多",
                0,
                f"paragraph_blocks={count} (rough expected {expected_range} for {style})",
                "段落块不是可靠场景数；原文常一行一段。只作为人工节奏提示。",
            )
        )
    else:
        findings.append(
            Finding(
                "info",
                "段落块数量",
                0,
                f"paragraph_blocks={count} (rough expected {expected_range} for {style})",
                "rough paragraph block count within expected range",
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
                "info",
                "控制器元数据",
                0,
                "",
                "未发现控制器元数据；匿名盲评正文不应强制包含元数据，验证报告可单独记录 date-zone/verification/corpus。",
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
                "控制器元数据",
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
    check_process_leakage(findings, lines)
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
    check_diagnostic_title(findings, lines)
    check_high_signal_opening(findings, lines)
    check_standard_diary_length(findings, lines, text)
    check_learned_ending_button(findings, lines)
    check_theme_density(findings, text)
    check_tasteful_withholding_ending(findings, lines)
    check_quiet_explanation(findings, lines)
    check_engine_signal_density(findings, text)
    check_sealed_nocturne(findings, text)
    check_period_comma_ratio(findings, lines)
    check_scene_count(findings, lines, text)
    check_breathing_point(findings, lines, text)
    check_metadata_comment(findings, text)
    return findings


def apply_strict_mode(findings: list[Finding]) -> list[Finding]:
    strict_findings: list[Finding] = []
    for finding in findings:
        should_promote = (
            finding.severity == "warning"
            and (
                finding.rule in STRICT_ERROR_RULE_NAMES
                or any(finding.rule.startswith(prefix) for prefix in STRICT_ERROR_RULE_PREFIXES)
            )
        )
        if should_promote:
            strict_findings.append(
                Finding(
                    "error",
                    f"strict: {finding.rule}",
                    finding.line,
                    finding.excerpt,
                    finding.suggestion,
                )
            )
        else:
            strict_findings.append(finding)
    return strict_findings


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
    parser.add_argument("--strict", action="store_true", help="Promote blind-evaluation high-risk warnings to errors")
    parser.add_argument("--fail-on-warning", action="store_true", help="Return nonzero for warnings as well as errors")
    args = parser.parse_args()

    text = args.file.read_text(encoding="utf-8")
    findings = collect_findings(text)
    if args.strict:
        findings = apply_strict_mode(findings)
    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    else:
        print(format_text(findings))
    if args.fail_on_warning:
        return 1 if any(finding.severity in {"error", "warning"} for finding in findings) else 0
    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

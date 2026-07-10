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
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


EXPECTED_CORPUS_COUNT = 38
PROFILE_VERSION = "1.6"
MIN_STRATUM_DOCUMENTS = 4

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
    "还是",
    "已经",
    "现在",
    "结果",
    "后来",
    "以前",
    "当时",
    "原来",
    "反正",
    "毕竟",
    "要不然",
    "还以为",
    "突然想起",
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
    "ai_binary_reframe": r"(?:不是[^，。！？\n]{0,18}[，,]?\s*(?:我|你|他|她|它)?(?:而是|是|就是|只是|才是)|不是[^。！？\n]{1,28}[。！？]\s*(?:我|你|他|她|它)?(?:是|就是|只是|而是|才是))",
    "ai_explainer": r"(?:本质上|真正的问题是|核心是|这说明|这意味着|换句话说|说白了|现在我意识到|最终我意识到|我终于明白)",
    "ordered_explainer": r"(?:首先|其次|综上|总之)",
    "therapeutic_humanizer": r"(?:允许自己|接住自己|被看见|和自己和解|跟自己和解|慢慢来|拥抱自己|善待自己)",
    "literary_dash_caption": r"——(?:那种|一种|像是|好像|终于可以|说不上)",
}

TEXTURE_GROUPS = {
    "dialogue_social": [
        "我说",
        "他说",
        "她说",
        "问我",
        "问了一句",
        "回我",
        "骂",
        "笑",
        "群里",
        "室友",
        "舍友",
        "老板",
        "摊主",
        "店员",
        "收银",
        "骑手",
        "外卖员",
        "快递员",
        "保安",
        "司机",
        "楼管",
        "房东",
        "邻居",
        "朋友",
        "同学",
        "我妈",
        "我爸",
        "狗哥",
        "水哥",
        "Java大哥",
        "没收手",
        "没松手",
        "他没走",
        "拿点纸",
        "拿稳点",
        "递过去",
        "接过",
        "催了一下",
    ],
    "screen_platform": ["手机", "屏幕", "消息", "群", "评论", "帖子", "视频", "小红书", "知乎", "微博", "B站", "抖音", "贴吧", "NGA", "boss", "Boss", "直聘", "GPT", "AI"],
    "body": ["脚", "脚踝", "尿", "厕所", "胃", "胸口", "疼", "肿", "汗", "痔疮", "痛风", "口腔", "牙", "眼睛", "手", "裤子"],
    "money": ["钱", "块", "元", "工资", "房租", "外卖", "便宜", "贵", "补贴", "报销", "红包", "可乐", "泡面"],
    "route_object": ["楼下", "门口", "路上", "电动车", "车", "公交", "地铁", "楼道", "快递", "钥匙", "塑料袋", "水龙头", "杯子", "充电", "空调", "冰箱"],
    "food_weather": ["泡面", "米线", "饭", "烧烤", "黄焖鸡", "腐乳", "苹果", "西瓜", "可乐", "雨", "太阳", "风", "热", "冷", "湿"],
    "game": ["王者", "王者荣耀", "星耀五", "ELO", "elo", "蔡文姬", "游戏"],
    "family_cast": ["我妈", "我爸", "我姐", "外公", "外婆", "狗哥", "水哥", "Java大哥", "室友", "舍友"],
}

THEME_DOMAINS = {
    "job": ["春招", "求职", "offer", "入职", "体检", "租房补贴", "大厂", "boss", "直聘", "招聘", "岗位", "简历", "hr", "工位"],
    "romance": ["情人节", "礼物", "玫瑰", "情侣", "对象", "恋爱", "结婚", "婚礼", "随礼"],
    "family": ["母亲节", "我妈", "妈妈", "我爸", "鸡蛋", "雨衣", "回家", "饭桌"],
    "illness": ["痛风", "脚踝", "尿酸", "肿", "疼", "富贵病", "腐乳", "可乐"],
}

OFF_AXIS_TERMS = [
    "楼下",
    "小卖部",
    "水龙头",
    "厕所",
    "马桶",
    "尿",
    "胃",
    "汗",
    "裤子",
    "鞋",
    "袜",
    "塑料袋",
    "杯子",
    "筷子",
    "泡面",
    "米线",
    "香菜",
    "苹果",
    "西瓜",
    "可乐",
    "硬币",
    "电动车",
    "保安",
    "老头",
    "老奶奶",
    "快递",
    "路由器",
    "钥匙",
    "充电",
    "门口",
    "楼道",
    "风",
    "雨",
    "空调",
    "冰箱",
    "脏",
    "臭",
    "摔",
    "洗",
    "漏",
    "烫",
    "酸",
]

ENDING_PATTERNS = {
    "ending_button": r"(?:^|\n)(?:哦。|算了。|睡了。|睡吧。|今天先这样。|今天就这样。|今天就先这样。|就先这样。|先这样吧。|关屏。|屏幕暗了。|屏幕黑了。)\s*$",
    "ambient_tail": r"(?:空调|外机|风扇|雨|灯|屏幕|手机|机器|冰箱)[^。！？\n]{0,16}(?:嗡|响|亮|暗|黑|震)[^。！？\n]{0,8}[。！？]?\s*$",
    "withholding_tail": r"(?:没点开|没回|没看|没发|没说话|放下手机|扣在桌上)\s*$",
}

COGNITIVE_PATTERNS = {
    "concrete_entry": r"(?:楼下|门口|水龙头|手机|屏幕|杯子|塑料袋|电动车|脚|厕所|小卖部|群里|消息)",
    "crooked_interpretation": r"(?:还以为|原来|像|算|等于|相当于|机制|算法|系统|ELO|elo|逻辑)",
    "reality_puncture": r"(?:尿|厕所|痔疮|阳痿|傻逼|滚|去你妈|漏|摔|疼|肿|钱|块|元)",
    "defensive_recovery": r"(?:算了|没事|还行|挺好|不管|下次|我说哦|我说嗯|也行)",
    "exit_retreat": r"(?:关|睡|回去|走了|删了|退出|去尿|去厕所|不写了)",
    "associative_hook": r"(?:突然想起|想起|以前|那时候|当时|有次|上次|后来)",
    "humor_friction": r"(?:还以为|原来|傻逼|滚|阳痿|痔疮|ELO|elo|算法|系统|他妈)",
    "emotion_displaced_logistics": r"(?:房租|外卖|工资|报销|水龙头|塑料袋|电动车|厕所|脚踝|尿|充电|钥匙)",
    "abstract_emotion_label": r"(?:孤独|难过|悲伤|释然|自洽|松弛|破碎感|命运感|真实感)",
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
    "unique_2gram_ratio": "ngram_texture",
    "unique_3gram_ratio": "ngram_texture",
    "unique_4gram_ratio": "ngram_texture",
    "max_3gram_repeat": "ngram_texture",
    "max_4gram_repeat": "ngram_texture",
    "dominant_theme_line_share": "structure",
    "off_axis_line_share": "structure",
    "title_body_bigram_overlap": "title",
    "early_tail_3gram_overlap": "structure",
    "early_tail_4gram_overlap": "structure",
    "title_tail_bigram_overlap": "title",
    "opening_theme_line_share": "structure",
    "middle_theme_line_share": "structure",
    "tail_theme_line_share": "structure",
    "middle_off_axis_line_share": "structure",
    "texture_any_line_share": "texture",
    "texture_diversity_count": "texture",
    "body_money_social_line_share": "texture",
    "line_count_per_1k_chars": "line_rhythm",
}


@dataclass(frozen=True)
class DocumentProfile:
    file: str
    title: str
    date: str
    phase: str
    genre: str
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


def infer_date_from_text_or_name(text: str, filename: str) -> str:
    date_match = re.search(r"发布日期\*\*\s*[:：]\s*([0-9-]+)", text)
    if date_match:
        return date_match.group(1).strip()
    filename_match = re.search(r"(20\d{2})(\d{2})?(\d{2})?", filename)
    if not filename_match:
        return "unknown"
    year, month, day = filename_match.groups()
    if month and day:
        return f"{year}-{month}-{day}"
    if month:
        return f"{year}-{month}"
    return year


def phase_for(date: str) -> str:
    if date.startswith(("2022-04", "2022-05")):
        return "A"
    if date.startswith(("2022-07", "2022-08", "2022-10")):
        return "B"
    if date.startswith("2023"):
        return "C"
    if date.startswith(("2024", "2025", "2026")):
        return "D"
    return "unknown"


def genre_for(title: str, body: str) -> str:
    if "母亲节" in title or "谢谢你" in title:
        return "sincere"
    if "活着就是" in title:
        return "micro-hope"
    if "存在主义" in title or "迷失" in title:
        return "surreal"
    return "standard"


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


def chinese_sequence(text: str) -> str:
    return "".join(re.findall(r"[\u4e00-\u9fff]", text))


def char_ngrams(text: str, n: int) -> list[str]:
    sequence = chinese_sequence(text)
    if len(sequence) < n:
        return []
    return [sequence[index : index + n] for index in range(len(sequence) - n + 1)]


def repeated_ngram_count(text: str, n: int, minimum: int) -> int:
    counts = Counter(char_ngrams(text, n))
    return sum(1 for count in counts.values() if count >= minimum)


def max_ngram_repeat(text: str, n: int) -> int:
    counts = Counter(char_ngrams(text, n))
    return max(counts.values()) if counts else 0


def unique_ngram_ratio(text: str, n: int) -> float:
    grams = char_ngrams(text, n)
    return len(set(grams)) / len(grams) if grams else 0.0


def line_hit_count(lines: list[str], terms: list[str]) -> int:
    return sum(1 for line in lines if any(term in line for term in terms))


def line_hit_any_count(lines: list[str], term_groups: list[list[str]]) -> int:
    return sum(1 for line in lines if any(any(term in line for term in terms) for terms in term_groups))


def line_share(lines: list[str], terms: list[str]) -> float:
    if not lines:
        return 0.0
    return line_hit_count(lines, terms) / len(lines)


def line_pattern_count(lines: list[str], pattern: str) -> int:
    compiled = re.compile(pattern, re.IGNORECASE)
    return sum(1 for line in lines if compiled.search(line))


def repeated_line_prefix_count(lines: list[str], width: int, minimum: int = 2) -> int:
    prefixes = []
    for line in lines:
        seq = chinese_sequence(line)
        if len(seq) >= width:
            prefixes.append(seq[:width])
    counts = Counter(prefixes)
    return sum(1 for count in counts.values() if count >= minimum)


def consecutive_prefix_template_count(lines: list[str], width: int = 2) -> int:
    previous = ""
    repeats = 0
    for line in lines:
        seq = chinese_sequence(line)
        prefix = seq[:width] if len(seq) >= width else ""
        if prefix and previous and prefix == previous:
            repeats += 1
        previous = prefix
    return repeats


def title_body_bigram_overlap(title: str, body: str) -> int:
    title_grams = set(char_ngrams(title, 2))
    if not title_grams:
        return 0
    return len(title_grams & set(char_ngrams(body, 2)))


def early_tail_ngram_overlap(lines: list[str], n: int = 3) -> int:
    if len(lines) < 6:
        return 0
    split = max(1, len(lines) // 3)
    early = "\n".join(lines[:split])
    tail = "\n".join(lines[-split:])
    return len(set(char_ngrams(early, n)) & set(char_ngrams(tail, n)))


def title_tail_bigram_overlap(title: str, lines: list[str]) -> int:
    title_grams = set(char_ngrams(title, 2))
    if not title_grams or not lines:
        return 0
    tail = "\n".join(lines[-max(3, len(lines) // 5) :])
    return len(title_grams & set(char_ngrams(tail, 2)))


def line_thirds(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    if not lines:
        return [], [], []
    first = max(1, len(lines) // 3)
    second = max(first + 1, (len(lines) * 2) // 3)
    return lines[:first], lines[first:second], lines[second:]


def dominant_theme_share(lines: list[str]) -> float:
    if not lines:
        return 0.0
    shares = []
    for terms in THEME_DOMAINS.values():
        shares.append(line_hit_count(lines, terms) / len(lines))
    return max(shares) if shares else 0.0


def extract_document(path: Path) -> DocumentProfile:
    text = read_text(path)
    title, body, body_lines = split_title_body(text)
    date = infer_date_from_text_or_name(text, path.name)
    content_lines = [line for line in body_lines if line and not line.lstrip().startswith("<!--")]
    line_lengths = [chinese_len(line) for line in content_lines if chinese_len(line) > 0]
    body_chars = chinese_len(body)
    body_compact = compact_chinese(body)
    line_count = len(line_lengths)
    body_line_denominator = max(line_count, 1)
    opening_lines, middle_lines, tail_lines = line_thirds(content_lines)
    all_theme_terms = [term for terms in THEME_DOMAINS.values() for term in terms]
    any_texture_groups = list(TEXTURE_GROUPS.values())
    body_money_social_groups = [
        TEXTURE_GROUPS["body"],
        TEXTURE_GROUPS["money"],
        TEXTURE_GROUPS["dialogue_social"],
    ]
    texture_counts = {
        label: line_hit_count(content_lines, terms)
        for label, terms in TEXTURE_GROUPS.items()
    }

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
        "unique_2gram_ratio": unique_ngram_ratio(body, 2),
        "unique_3gram_ratio": unique_ngram_ratio(body, 3),
        "unique_4gram_ratio": unique_ngram_ratio(body, 4),
        "max_3gram_repeat": float(max_ngram_repeat(body, 3)),
        "max_4gram_repeat": float(max_ngram_repeat(body, 4)),
        "dominant_theme_line_share": dominant_theme_share(content_lines),
        "off_axis_line_share": line_hit_count(content_lines, OFF_AXIS_TERMS) / body_line_denominator,
        "title_body_bigram_overlap": float(title_body_bigram_overlap(title, body)),
        "early_tail_3gram_overlap": float(early_tail_ngram_overlap(content_lines, 3)),
        "early_tail_4gram_overlap": float(early_tail_ngram_overlap(content_lines, 4)),
        "title_tail_bigram_overlap": float(title_tail_bigram_overlap(title, content_lines)),
        "opening_theme_line_share": line_share(opening_lines, all_theme_terms),
        "middle_theme_line_share": line_share(middle_lines, all_theme_terms),
        "tail_theme_line_share": line_share(tail_lines, all_theme_terms),
        "middle_off_axis_line_share": line_share(middle_lines, OFF_AXIS_TERMS),
        "texture_any_line_share": line_hit_any_count(content_lines, any_texture_groups) / body_line_denominator,
        "texture_diversity_count": float(sum(1 for count in texture_counts.values() if count > 0)),
        "body_money_social_line_share": line_hit_any_count(content_lines, body_money_social_groups) / body_line_denominator,
        "line_count_per_1k_chars": (line_count / body_chars * 1000) if body_chars else 0.0,
    }

    counts["short_lines"] = sum(1 for length in line_lengths if length <= 8)
    counts["long_lines"] = sum(1 for length in line_lengths if length >= 28)
    denominators["short_lines"] = line_count
    denominators["long_lines"] = line_count
    counts["repeated_2gram_templates"] = repeated_ngram_count(body, 2, 4)
    counts["repeated_3gram_templates"] = repeated_ngram_count(body, 3, 3)
    counts["repeated_4gram_templates"] = repeated_ngram_count(body, 4, 2)
    denominators["repeated_2gram_templates"] = body_chars
    denominators["repeated_3gram_templates"] = body_chars
    denominators["repeated_4gram_templates"] = body_chars
    counts["line_start_2_repeats"] = repeated_line_prefix_count(content_lines, 2)
    counts["line_start_4_repeats"] = repeated_line_prefix_count(content_lines, 4)
    counts["consecutive_line_start_2_templates"] = consecutive_prefix_template_count(content_lines, 2)
    denominators["line_start_2_repeats"] = line_count
    denominators["line_start_4_repeats"] = line_count
    denominators["consecutive_line_start_2_templates"] = line_count

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

    for label, terms in TEXTURE_GROUPS.items():
        feature = f"texture_{label}_lines"
        counts[feature] = texture_counts[label]
        denominators[feature] = line_count
        values[f"texture_{label}_line_ratio"] = counts[feature] / body_line_denominator

    counts["texture_any_lines"] = line_hit_any_count(content_lines, any_texture_groups)
    denominators["texture_any_lines"] = line_count
    counts["body_money_social_lines"] = line_hit_any_count(content_lines, body_money_social_groups)
    denominators["body_money_social_lines"] = line_count
    counts["middle_off_axis_lines"] = line_hit_count(middle_lines, OFF_AXIS_TERMS)
    denominators["middle_off_axis_lines"] = max(len(middle_lines), 1)
    counts["opening_theme_lines"] = line_hit_count(opening_lines, all_theme_terms)
    denominators["opening_theme_lines"] = max(len(opening_lines), 1)
    counts["middle_theme_lines"] = line_hit_count(middle_lines, all_theme_terms)
    denominators["middle_theme_lines"] = max(len(middle_lines), 1)
    counts["tail_theme_lines"] = line_hit_count(tail_lines, all_theme_terms)
    denominators["tail_theme_lines"] = max(len(tail_lines), 1)

    for label, terms in THEME_DOMAINS.items():
        feature = f"theme_{label}_lines"
        counts[feature] = line_hit_count(content_lines, terms)
        denominators[feature] = line_count
        values[f"theme_{label}_line_ratio"] = counts[feature] / body_line_denominator

    counts["off_axis_lines"] = line_hit_count(content_lines, OFF_AXIS_TERMS)
    denominators["off_axis_lines"] = line_count

    for label, pattern in ENDING_PATTERNS.items():
        counts[label] = len(re.findall(pattern, "\n".join(content_lines), flags=re.IGNORECASE))
        denominators[label] = max(len(content_lines[-5:]), 1)

    for label, pattern in COGNITIVE_PATTERNS.items():
        counts[f"cognitive_{label}"] = len(re.findall(pattern, body, flags=re.IGNORECASE))
        denominators[f"cognitive_{label}"] = body_chars
        values[f"cognitive_{label}_per_1k"] = counts[f"cognitive_{label}"] / body_chars * 1000 if body_chars else 0.0

    for label, pattern in PATTERNS.items():
        counts[label] = len(re.findall(pattern, body))
        denominators[label] = body_chars
        values[f"{label}_per_1k"] = counts[label] / body_chars * 1000 if body_chars else 0.0

    return DocumentProfile(
        file=path.name,
        title=title,
        date=date,
        phase=phase_for(date),
        genre=genre_for(title, body),
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


def infer_value_family(feature: str) -> str:
    if feature.startswith("punct_"):
        return "punctuation"
    if feature.startswith("connector_"):
        return "connectors"
    if feature.startswith("texture_") or feature == "body_money_social_lines":
        return "texture"
    if feature.startswith("theme_"):
        return "structure"
    if feature.startswith("cognitive_"):
        return "cognitive_mechanism"
    return FEATURE_FAMILIES.get(feature, "other")


def infer_family(feature: str) -> str:
    if feature.startswith("punct_"):
        return "punctuation"
    if feature.startswith("connector_"):
        return "connectors"
    if feature.startswith("texture_") or feature == "body_money_social_lines":
        return "texture"
    if feature.startswith("theme_") or feature in {
        "off_axis_lines",
        "middle_off_axis_lines",
        "opening_theme_lines",
        "middle_theme_lines",
        "tail_theme_lines",
        "ending_button",
        "ambient_tail",
        "withholding_tail",
    }:
        return "structure"
    if feature.startswith("cognitive_"):
        return "cognitive_mechanism"
    if feature.startswith("repeated_") or feature.startswith("line_start_") or feature.startswith("consecutive_line_start_"):
        return "ngram_texture"
    if feature in {"short_lines", "long_lines"}:
        return "line_rhythm"
    if feature.startswith("ai_") or feature in {"ordered_explainer", "therapeutic_humanizer", "literary_dash_caption"}:
        return "ai_slop"
    return FEATURE_FAMILIES.get(feature, "other")


def infer_denominator(feature: str) -> str:
    if (
        feature in {"short_lines", "long_lines", "off_axis_lines", "ending_button", "ambient_tail", "withholding_tail"}
        or feature in {"middle_off_axis_lines", "opening_theme_lines", "middle_theme_lines", "tail_theme_lines", "texture_any_lines", "body_money_social_lines"}
        or feature.startswith("texture_")
        or feature.startswith("theme_")
        or feature.startswith("line_start_")
        or feature.startswith("consecutive_line_start_")
    ):
        return "body_lines"
    return "body_chars"


def load_corpus(corpus_dir: Path) -> list[Path]:
    return [
        path
        for pattern in ("*.md", "*.txt")
        for path in sorted(corpus_dir.glob(pattern))
        if path.is_file()
    ]


def summarize_document_subset(documents: list[DocumentProfile]) -> dict[str, Any]:
    value_summary = summarize_values(documents)
    count_summary = summarize_counts(documents)
    return {
        "document_count": len(documents),
        "files": [document.file for document in documents],
        "value_summary": value_summary,
        "value_families": {feature: infer_value_family(feature) for feature in value_summary},
        "count_summary": count_summary,
    }


def build_strata(documents: list[DocumentProfile]) -> dict[str, Any]:
    strata: dict[str, Any] = {
        "min_documents_for_default_use": MIN_STRATUM_DOCUMENTS,
        "phase": {},
        "genre": {},
        "phase_genre": {},
    }
    phases = sorted({document.phase for document in documents})
    genres = sorted({document.genre for document in documents})
    for phase in phases:
        subset = [document for document in documents if document.phase == phase]
        strata["phase"][phase] = summarize_document_subset(subset)
    for genre in genres:
        subset = [document for document in documents if document.genre == genre]
        strata["genre"][genre] = summarize_document_subset(subset)
    for phase in phases:
        for genre in genres:
            subset = [document for document in documents if document.phase == phase and document.genre == genre]
            if subset:
                strata["phase_genre"][f"{phase}/{genre}"] = summarize_document_subset(subset)
    return strata


def build_profile(corpus_dir: Path) -> dict[str, Any]:
    paths = load_corpus(corpus_dir)
    documents = [extract_document(path) for path in paths]
    value_summary = summarize_values(documents)
    count_summary = summarize_counts(documents)
    return {
        "version": PROFILE_VERSION,
        "profile_kind": "corpus_prior_predictive_intervals",
        "corpus_dir": "<corpus-dir>",
        "expected_corpus_count": EXPECTED_CORPUS_COUNT,
        "corpus_file_count": len(paths),
        "principles": [
            "This profile is an audit prior, not authorship proof.",
            "Use per-document distributions and predictive intervals, not exact ratio matching.",
            "Do not force rare features to appear.",
            "Do not treat corpus-zero as impossible unless the feature is a hard generated-draft gate.",
            "Use placebo originals to calibrate warnings before blind-evaluation claims.",
            "Use phase/genre strata only when explicitly requested and sample size is adequate; fall back to global priors otherwise.",
        ],
        "documents": [asdict(document) for document in documents],
        "value_summary": value_summary,
        "value_families": {feature: infer_value_family(feature) for feature in value_summary},
        "count_summary": count_summary,
        "strata": build_strata(documents),
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

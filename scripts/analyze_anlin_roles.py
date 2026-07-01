#!/usr/bin/env python3
"""Analyze recurring and archetypal Anlin roles across a local corpus.

The script counts article-level appearances, not raw mention counts. It is a
guardrail for skill documentation: it prevents hand-written role frequencies
from drifting away from the 38-article corpus.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path


EXPECTED_CORPUS_COUNT = 38


@dataclass(frozen=True)
class RoleRule:
    name: str
    aliases: tuple[str, ...]
    tier: str
    function: str
    confirmed_articles: tuple[str, ...] = ()


@dataclass(frozen=True)
class RoleCount:
    name: str
    tier: str
    function: str
    article_count: int
    articles: list[str]


ROLE_RULES: tuple[RoleRule, ...] = (
    RoleRule("狗哥", ("狗哥",), "fixed-frequent", "残酷真相投掷器", ("20220404", "20220406", "20220413", "20220426", "20220427", "20220428", "20220501", "20230102", "20231209")),
    RoleRule("舍友/室友", ("舍友", "室友"), "fixed-frequent", "正常人变形镜", ("20220404", "20220409", "20220421", "20220505", "20220524", "202210", "20230226", "20231209")),
    RoleRule("我妈", ("我妈",), "fixed-frequent", "家庭温度锚点", ("20220429", "20220505", "20220507", "20220508", "20220731", "20240111", "20251017")),
    RoleRule("Java大哥", ("Java大哥", "java大哥"), "fixed-frequent", "草台班子终极哲学家", ("20220406_2", "20220413", "20220415", "20220418", "20220426", "20220429")),
    RoleRule("水哥", ("水哥",), "fixed-frequent", "荒诞镜像体", ("20220729", "20220731", "20220803", "20230226", "20230729", "20231209")),
    RoleRule("我姐", ("我姐",), "fixed-frequent", "暴力现实校准器", ("20220404", "20220428", "20220524")),
    RoleRule("我爸", ("我爸",), "fixed-occasional", "精准毒舌父权", ("20220404_2", "20220413", "20220505")),
    RoleRule("我叔", ("我叔",), "fixed-occasional", "温暖长辈/底层工作哲学", ("20220427", "20220729", "20230729")),
    RoleRule("堂妹/我妹", ("堂妹", "我妹", "妹闹着", "老妹"), "fixed-occasional", "纯真视角", ("20220427", "20220729")),
    RoleRule("周（我姐前男友）", ("周跟我姐", "周旁边", "周系上围裙", "周跟我姐闺蜜"), "fixed-single", "喜剧旁观者", ("20220428",)),
    RoleRule("周（叙述者朋友）", ("周打语音", "周听完"), "fixed-single", "云南天气/病中语音朋友", ("20220512",)),
    RoleRule("王姐", ("王姐",), "fixed-single", "被裁镜像", ("20230226",)),
    RoleRule("刘哥", ("刘哥",), "fixed-single", "裸辞理想主义者", ("20230226",)),
    RoleRule("杨哥", ("杨哥",), "fixed-single", "创作焦虑镜像", ("20220729",)),
    RoleRule("辰", ("我说辰", "辰，"), "fixed-single", "比狗哥更毒舌的朋友", ("20220501",)),
    RoleRule("芝士雪豹", ("芝士雪豹", "雪豹"), "surreal-single", "超现实同行者", ("202210",)),
    RoleRule("蓝头发青年", ("蓝头发",), "random-single", "火车上的任务型陌生人", ("202210",)),
    RoleRule("下棋青年", ("下棋", "棋局"), "random-single", "火车上的荒诞秩序", ("202210",)),
    RoleRule("高三老师", ("高三老师", "杀鸡儆猴"), "random-memory", "校园权威/羞辱记忆", ("20220512",)),
    RoleRule("学姐", ("学姐",), "random-memory", "青春社交入口", ("20220409",)),
    RoleRule("初中女神", ("女神", "一尿就化"), "random-memory", "被时间破坏的暗恋", ("20220509",)),
    RoleRule("高中女朋友", ("高中交了个女朋友", "课间别一直睡"), "random-memory", "旧亲密关系", ("20220421",)),
    RoleRule("北漂朋友", ("北漂", "七位数"), "random-mirror", "阶级镜像", ("20220419",)),
    RoleRule("学长", ("学长", "我们就是柴"), "random-mirror", "算法/阶级寓言", ("20220427",)),
    RoleRule("送外卖小哥", ("外卖小哥",), "random-occupation", "同行底层劳动镜像"),
    RoleRule("面试官", ("面试官",), "random-authority", "荒谬权威"),
    RoleRule("HR", ("hr", "HR"), "random-authority", "招聘系统面孔"),
    RoleRule("经理", ("经理",), "random-authority", "职场甩锅者"),
    RoleRule("保安大爷", ("保安大爷",), "random-wisdom", "街头智者"),
    RoleRule("煎饼阿姨", ("煎饼", "阿姨"), "random-wisdom", "街头生活秩序"),
    RoleRule("清洁阿姨", ("清洁阿姨",), "random-tender", "沉默劳动者"),
    RoleRule("盘核桃大爷", ("盘核桃",), "random-wisdom", "陌生人歪理入口"),
    RoleRule("老奶奶", ("老奶奶", "奶奶"), "random-tender", "温柔过客"),
    RoleRule("40岁阿姨", ("40岁", "口红"), "random-tender", "中年女性生活裂缝"),
    RoleRule("小孩/孩子", ("小孩", "孩子", "谢谢叔叔"), "random-tender", "纯真视角"),
    RoleRule("鬼火少年", ("鬼火", "孤勇者"), "random-absurd", "荒诞路人"),
    RoleRule("水哥女朋友", ("水哥女朋友", "女朋友买", "冷冻虾"), "random-absurd", "荒诞伴侣"),
    RoleRule("我哥", ("我哥", "这是鸭子"), "random-family", "家庭荒诞同伴"),
)


def phase_for(filename: str) -> str:
    if re.search(r"20220[45]", filename):
        return "A"
    if re.search(r"20220(7|8)|202210", filename):
        return "B"
    if re.search(r"2023", filename):
        return "C"
    return "D"


def read_corpus(corpus_dir: Path) -> list[tuple[Path, str]]:
    paths = sorted(path for path in corpus_dir.glob("*.md") if path.is_file())
    return [(path, path.read_text(encoding="utf-8", errors="ignore")) for path in paths]


def matches(text: str, aliases: tuple[str, ...]) -> bool:
    return any(alias in text for alias in aliases)


def count_roles(corpus_dir: Path) -> list[RoleCount]:
    corpus = read_corpus(corpus_dir)
    counts: list[RoleCount] = []
    for rule in ROLE_RULES:
        articles = list(rule.confirmed_articles) or [
            path.stem.replace("Anlin_", "") for path, text in corpus if matches(text, rule.aliases)
        ]
        counts.append(
            RoleCount(
                name=rule.name,
                tier=rule.tier,
                function=rule.function,
                article_count=len(articles),
                articles=articles,
            )
        )
    return sorted(counts, key=lambda item: (-item.article_count, item.tier, item.name))


def format_markdown(counts: list[RoleCount], corpus_count: int) -> str:
    lines = [
        "# Anlin Role Frequency Report",
        "",
        f"Corpus size: {corpus_count} articles. Counts are article-level appearances, not raw mentions.",
        "",
        "## All Tracked Roles",
        "",
        "| Role | Type | Articles | Function | Evidence |",
        "|---|---:|---:|---|---|",
    ]
    for item in counts:
        evidence = ", ".join(item.articles[:8])
        if len(item.articles) > 8:
            evidence += f", +{len(item.articles) - 8}"
        lines.append(f"| {item.name} | {item.tier} | {item.article_count} | {item.function} | {evidence or '-'} |")

    frequent = [item for item in counts if item.tier.startswith("fixed") and item.article_count >= 3]
    randoms = [item for item in counts if item.tier.startswith(("random", "surreal"))]

    lines.extend([
        "",
        "## Skill-Relevant Frequent Roles",
        "",
        "Use these only when the scene naturally calls for their function. Frequency does not mean obligation.",
        "",
        "| Role | Articles | Function |",
        "|---|---:|---|",
    ])
    for item in frequent:
        lines.append(f"| {item.name} | {item.article_count} | {item.function} |")

    lines.extend([
        "",
        "## Non-Fixed / Random Role Pool",
        "",
        "These are not reusable canon characters. They are patterns for inventing one-off people with Anlin-compatible labels.",
        "",
        "| Pattern | Articles | Function |",
        "|---|---:|---|",
    ])
    for item in randoms:
        lines.append(f"| {item.name} | {item.article_count} | {item.function} |")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Anlin role frequencies across a local corpus.")
    parser.add_argument("--corpus-dir", type=Path, default=None, help="Directory containing 38 Anlin .md files")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    args = parser.parse_args()

    corpus_dir = args.corpus_dir or os.environ.get("ANLIN_CORPUS_DIR")
    if not corpus_dir:
        parser.error("Must provide --corpus-dir or set ANLIN_CORPUS_DIR.")
    corpus_dir = Path(corpus_dir)
    corpus_count = len(list(corpus_dir.glob("*.md")))
    counts = count_roles(corpus_dir)

    if args.json:
        print(json.dumps([asdict(item) for item in counts], ensure_ascii=False, indent=2))
    else:
        print(format_markdown(counts, corpus_count))

    if corpus_count != EXPECTED_CORPUS_COUNT:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

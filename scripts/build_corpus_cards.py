#!/usr/bin/env python3
"""Build lightweight corpus cards from the local Anlin originals."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


APPS = ["知乎", "小红书", "美团", "饿了么", "B站", "抖音", "微信", "QQ", "支付宝", "拼多多", "GPT", "AI", "MBTI", "星座", "招聘", "校招", "王者荣耀"]
BODY_TERMS = ["痔疮", "尿", "厕所", "疼", "痛风", "脚踝", "肚子", "拉", "吐", "病", "医院", "胸口", "喷嚏", "过敏", "肿"]
MONEY_TERMS = ["钱", "块", "元", "余额", "工资", "年薪", "收入", "支付", "银行卡", "房租"]
META_TERMS = ["日寄", "写", "知乎", "评论", "读者", "文章"]
CONNECTORS = ["其实", "觉得", "发现", "好像", "不过", "突然", "于是", "因为", "所以"]
KNOWN_ROLES = ["狗哥", "Java大哥", "水哥", "我姐", "舍友", "室友", "我妈", "我爸", "我叔", "堂妹", "王姐", "刘哥", "杨哥", "辰"]


@dataclass(frozen=True)
class Card:
    filename: str
    title: str
    date: str
    phase: str
    genre: str
    chars: int
    lines: int
    mean_line: float
    roles: list[str]
    signals: list[str]
    connectors: list[str]
    ending: str
    anchor_lines: list[str]


def read_body(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    title_match = re.search(r"^#\s+(.+)$", text, flags=re.M)
    date_match = re.search(r"发布日期\*\*:\s*([0-9-]+)", text)
    title = title_match.group(1).strip() if title_match else path.stem
    date = date_match.group(1).strip() if date_match else infer_date(path.name)
    body = text.split("---", 1)[1].strip() if "---" in text else text.strip()
    return title, date, body


def infer_date(filename: str) -> str:
    match = re.search(r"(20\d{2})(\d{2})?(\d{2})?", filename)
    if not match:
        return "unknown"
    year, month, day = match.groups()
    if month and day:
        return f"{year}-{month}-{day}"
    if month:
        return f"{year}-{month}"
    return year


def phase_for(date: str) -> str:
    if date.startswith("2022-04") or date.startswith("2022-05"):
        return "A"
    if date.startswith("2022-07") or date.startswith("2022-08") or date.startswith("2022-10"):
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


def chinese_chars(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]", text)


def content_lines(body: str) -> list[str]:
    return [line.strip() for line in body.splitlines() if line.strip()]


def mean_line_len(lines: list[str]) -> float:
    lengths = [len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", line)) for line in lines if line]
    return round(sum(lengths) / len(lengths), 1) if lengths else 0.0


def collect_signals(body: str) -> list[str]:
    signals: list[str] = []
    if any(term in body for term in APPS):
        signals.append("screen-platform")
    if any(term in body for term in BODY_TERMS):
        signals.append("body")
    if any(term in body for term in MONEY_TERMS):
        signals.append("money")
    if any(term in body for term in META_TERMS):
        signals.append("meta")
    if "说" in body or "问" in body:
        signals.append("dialogue")
    if re.search(r"^\.|-+$", body, flags=re.M):
        signals.append("hard-cut")
    return signals


def select_anchor_lines(lines: list[str]) -> list[str]:
    anchors: list[str] = []
    for line in lines:
        if len(line) < 6:
            continue
        if any(token in line for token in ("说", "问", "其实", "突然", "我想", "发现", "疼", "钱", "日寄")):
            anchors.append(line)
        if len(anchors) >= 6:
            break
    return anchors or lines[: min(6, len(lines))]


def build_card(path: Path) -> Card:
    title, date, body = read_body(path)
    lines = content_lines(body)
    roles = [role for role in KNOWN_ROLES if role in body]
    return Card(
        filename=path.name,
        title=title,
        date=date,
        phase=phase_for(date),
        genre=genre_for(title, body),
        chars=len(chinese_chars(body)),
        lines=len(lines),
        mean_line=mean_line_len(lines),
        roles=roles,
        signals=collect_signals(body),
        connectors=[term for term in CONNECTORS if term in body],
        ending=lines[-1] if lines else "",
        anchor_lines=select_anchor_lines(lines),
    )


def format_card(card: Card) -> str:
    def csv(items: list[str]) -> str:
        return ", ".join(items) if items else "none"

    anchors = "\n".join(f"- {line}" for line in card.anchor_lines)
    return f"""# {card.title}

source: {card.filename}
date: {card.date}
phase: {card.phase}
genre: {card.genre}

## Metrics

- chars: {card.chars}
- lines: {card.lines}
- mean-line: {card.mean_line}
- roles: {csv(card.roles)}
- signals: {csv(card.signals)}
- connectors: {csv(card.connectors)}

## Ending

{card.ending}

## Anchors

{anchors}

## Use

Use this card for calibration only. Do not copy anchor phrasing into generated prose.
"""


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build Anlin corpus cards from original markdown files.")
    parser.add_argument("--corpus-dir", type=Path, default=Path(r"C:\Users\34025\Desktop\Anlin"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent.parent / "references" / "corpus-cards")
    args = parser.parse_args(argv)

    if not args.corpus_dir.is_dir():
        parser.error(f"Corpus directory not found: {args.corpus_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(path for path in args.corpus_dir.glob("*.md") if path.is_file())
    for path in paths:
        card = build_card(path)
        output = args.output_dir / f"{path.stem}.md"
        output.write_text(format_card(card), encoding="utf-8")

    index_lines = [
        "# Corpus Cards Index",
        "",
        "Generated from local originals. Cards are calibration summaries, not source text replacements.",
        "",
        "| date | phase | genre | file | chars | signals |",
        "|---|---|---|---|---:|---|",
    ]
    for path in paths:
        card = build_card(path)
        index_lines.append(f"| {card.date} | {card.phase} | {card.genre} | [{path.stem}.md]({path.stem}.md) | {card.chars} | {', '.join(card.signals) or 'none'} |")
    (args.output_dir / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    print(f"wrote {len(paths)} cards to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


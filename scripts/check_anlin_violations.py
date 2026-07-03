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

COMMENT_CHAIN_TERMS = ["有人说", "有人回", "评论说", "回复说", "热评"]
COMMENT_CHAIN_FORMULA_MARKERS = [
    "有人说",
    "有人回",
    "有人问",
    "有人发了",
    "有人发了张",
    "有个人问",
    "另一个人说",
    "一个说",
    "又有人",
    "又发了个",
    "发截图的人",
    "群里回",
    "跟了个",
    "评论说",
    "回复说",
    "热评",
    "第一条",
    "第二条",
    "下面一排",
    "下面三个人",
    "一排人",
    "底下跟了一串",
    "底下追了一串",
    "跟了一串回答",
    "一串回答",
    "一串问号",
    "被人回",
    "底下跟了一排",
    "跟了一排",
    "下面跟了一排",
    "底下回了个",
    "底下有人",
    "第一条回复",
    "热评",
    "评论区",
    "谢邀人在美国刚下飞机",
]
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
AI_SLOP_TERMS = [
    "首先",
    "其次",
    "综上",
    "这说明",
    "这意味着",
    "说白了",
    "换句话说",
    "换言之",
    "翻译过来就是",
    "本质上",
    "核心是",
    "真正的问题",
    "真正让",
    "最终我意识到",
    "我终于明白",
    "这就是为什么",
    "简单来说",
    "从某种意义上",
    "更重要的是",
    "总之",
    "一方面",
    "另一方面",
]
AI_PARALLEL_TEMPLATE_TERMS = [
    "不是为了",
    "更像是",
    "像是在提醒",
    "像是某种",
    "变成了一个",
    "完成了某种",
]
AI_SELF_ANNOTATION_TERMS = [
    "说不上是那种",
    "其实就是那种",
    "那种怎么说呢",
    "大概就是这个意思",
    "怎么说呢",
]
PSEUDO_COLLOQUIAL_TERMS = [
    "稳稳的接住",
    "稳稳接住",
    "不崩、不爆",
    "不崩不爆",
    "松弛感",
    "氛围感",
    "颗粒度",
    "落地感",
    "高级感",
    "钝感力",
]
THERAPEUTIC_HUMANIZER_TERMS = [
    "允许自己",
    "接住自己",
    "被看见",
    "和自己和解",
    "跟自己和解",
    "慢慢来",
    "好好生活",
    "拥抱自己",
    "善待自己",
    "自我接纳",
]
ORDERED_EXPLAINER_TERMS = ["首先", "其次", "最后", "综上"]
ABSTRACT_EMOTION_TERMS = [
    "放松",
    "释然",
    "自洽",
    "真实感",
    "完整感",
    "命运感",
    "松弛",
    "破碎感",
]
UNSUPPORTED_DISTRICT_TERMS = [
    "黄埔区",
    "天河区",
    "南山区",
    "福田区",
    "浦东新区",
    "西湖区",
    "海淀区",
    "朝阳区",
]
UNSUPPORTED_CITY_REVIEW_TERMS = [
    "广州",
    "深圳",
    "上海",
    "杭州",
    "成都",
    "重庆",
    "武汉",
    "南京",
    "天津",
    "苏州",
    "珠海",
    "东莞",
    "佛山",
    "长沙",
    "湖南",
    "昆明",
]
BACKGROUND_DISPLAY_GROUPS = {
    "school_work": ["211", "春招", "外卖", "送外卖", "程序员", "被裁", "失业"],
    "game": ["王者", "王者荣耀", "星耀五", "ELO", "elo", "蔡文姬"],
    "platform": ["知乎", "小红书", "贴吧", "豆瓣", "nga", "NGA", "b站", "B站", "微博", "抖音", "GPT", "gpt", "AI", "ai"],
    "cast": ["狗哥", "Java大哥", "水哥", "我姐", "室友", "舍友", "我妈", "我爸"],
    "body": ["痛风", "脚踝", "尿急", "口腔溃疡", "褪黑素", "胸口痛"],
    "place": ["云南", "小城市", "五线", "老家", "学校门口"],
}
UNSUPPORTED_GAME_ROLE_TERMS = [
    "排位",
    "星耀一",
    "星耀二",
    "星耀三",
    "星耀四",
    "星耀段",
    "打原神",
    "玩原神",
    "打野教学",
    "打野",
    "辅助位",
    "补了个辅助",
    "中路被抓",
    "秒选法师",
    "队友秒选",
    "压血线",
    "大腿带",
    "战令",
    "福利局",
    "撤退信号",
    "二塔",
    "团战",
    "三换二",
    "结算界面",
    "结算页面",
    "MVP",
    "复活点",
    "加血",
    "加盾",
    "奶不到",
    "输出全靠",
    "队友全死",
    "退出匹配",
    "阵容",
    "泉水",
    "经济面板",
    "输出比辅助",
    "干得漂亮",
    "晋级赛",
    "硬辅",
    "下路",
    "装备",
    "队友点",
    "开局频道",
    "信号响",
    "adc",
    "ADC",
    "ad",
    "AD",
    "上单",
    "中单",
    "射手",
    "法师",
    "辅助装",
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
    "second checker call",
    "per protocol",
    "current `draft.md`",
    "Here is the article",
    "final article",
    "首段 preflight",
    "校验通过",
    "Jaccard",
    "jaccard",
    "与 38 篇",
    "内部）：",
    "现在构建状态卡",
    "构建状态卡",
    "开始写草稿",
    "检查器发现",
    "需要重写",
    "最后一次修复",
    "协议内",
    "按协议",
    "修复机会",
    "仿写",
    "生成文本",
    "AI生成",
    "ai生成",
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
    "睡吧。",
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
ROUGH_SELF_DAMAGE_TERMS = [
    "他妈",
    "傻逼",
    "嘴贱",
    "破口大骂",
    "滚蛋",
    "滚回去",
    "滚出去",
    "屎",
    "拉屎",
    "尿",
    "痔疮",
    "阳痿",
    "舔狗",
    "社死",
    "丢人",
    "好家伙",
    "工贼",
]
ROUGH_SELF_DAMAGE_PATTERNS = [
    r"(?<![一二两三四五六七八九十百千万\d])滚(?![一二两三四五六七八九十百千万\d年月日天点分秒])",
    r"我[^。！？\n]{0,12}(?:丢人|社死|嘴贱|像个傻逼|像傻逼)",
    r"(?:拉屎|尿|痔疮|阳痿)[^。！？\n]{0,24}(?:我|自己|本人|室友|同学|群|厕所)?",
]
AMBIENT_ENDING_PATTERNS = [
    r"(空调|外机|风扇|雨|灯|屏幕|手机|机器|冰箱)[^。！？\n]{0,16}(嗡|响|亮|暗|黑|震)[^。！？\n]{0,8}[。！？]?$",
    r"^(嗡|嗡嗡|嗡嗡嗡|滴|滴滴|哗啦|呼呼)[。！？]?$",
]
MATERIAL_ECHO_TERMS = [
    "奥美拉唑还剩最后一片",
    "明天记得买",
    "Type-C",
]
PROMPT_CHAIN_TERMS = sorted(
    {
        term
        for terms in THEME_DOMAINS.values()
        for term in terms
    },
    key=len,
    reverse=True,
)
OFF_AXIS_SIGNAL_TERMS = [
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
STRICT_ERROR_RULE_PREFIXES = (
    "题面高信号开头",
    "习得式结尾按钮",
    "文艺悬停式结尾",
    "封闭夜晚短篇结构",
    "纯环境音结尾",
    "材料钩子重复过直",
    "散文块压缩",
)
STRICT_ERROR_RULE_NAMES: set[str] = set()
DRAFT_GATE_RULE_PREFIXES = (
    "缺少标题",
    "标题标签泄漏",
    "来源身份声明",
    "复制重叠风险",
    "题面诊断型标题",
    "标准日寄完整文章篇幅偏短",
    "标准日寄完整文章篇幅缓冲不足",
    "单主题词密度偏高",
    "题面链条过于完整",
    "评论链公式化转述",
    "高频词覆盖不足",
    "AI二元解释句式",
    "AI解释腔",
    "AI平行解释模板",
    "AI自我注解",
    "AI变量代称",
    "AI文艺解释面",
    "AI伪口语",
    "AI完整结构",
    "破折号解释连接",
    "破折号稀有连接",
    "无依据具体地名",
    "无依据游戏角色细节",
    "日常对话引号",
    "对话接力过密",
    "游戏复盘细节",
    "Offer具体化编造",
    "AI治疗式人类化",
    "背景展示堆砌",
    "行末逗号比例",
    "节奏过度均匀",
    "中段旁逸不足",
    "孤立中文标点",
    "断裂过碎",
    "粗粝自毁信号不足",
    "段落发动机信号偏弱",
    "短行诗化表面",
)
DRAFT_GATE_RULE_NAMES: set[str] = set()

STANDARD_DIARY_FORMAL_MIN_CHARS = 650
STANDARD_DIARY_DRAFT_SAFE_MIN_CHARS = 850


def clean_excerpt(line: str) -> str:
    stripped = line.strip()
    return stripped[:120] + ("..." if len(stripped) > 120 else "")


def chinese_len(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def compact_chinese_text(text: str) -> str:
    return "".join(re.findall(r"[\u4e00-\u9fff]", text))


def char_ngram_set(text: str, n: int) -> set[str]:
    chars = compact_chinese_text(text)
    if len(chars) < n:
        return set()
    return {chars[index : index + n] for index in range(len(chars) - n + 1)}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


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


def is_corpus_metadata_line(line: str) -> bool:
    stripped = line.strip()
    return (
        stripped == "---"
        or stripped.startswith("<!--")
        or re.match(r"^-\s*\*\*(?:作者|原链接|发布日期|标题)\*\*\s*[:：]", stripped)
        is not None
    )


def visible_article_lines(lines: list[str]) -> list[tuple[int, str]]:
    return [
        (line_number, line.strip())
        for line_number, line in enumerate(lines, start=1)
        if line.strip() and not is_corpus_metadata_line(line)
    ]


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


def check_missing_title(findings: list[Finding], lines: list[str]) -> None:
    visible = visible_article_lines(lines)
    if not visible:
        findings.append(
            Finding(
                "warning",
                "缺少标题",
                0,
                "",
                "正式盲评稿必须是完整文章，第一行必须是标题。补一个正文级标题，通常优先弱化为“日寄”。",
            )
        )
        return
    first_line_number, first = visible[0]
    title, _ = split_title_and_content_lines(lines)
    if not title:
        findings.append(
            Finding(
                "warning",
                "缺少标题",
                first_line_number,
                clean_excerpt(first),
                "正式盲评稿必须把标题作为第一行文章内容；不要让正文第一句冒充标题。",
            )
        )
        return
    if re.match(r"^(标题|题目)\s*[:：]", first):
        findings.append(
            Finding(
                "warning",
                "标题标签泄漏",
                first_line_number,
                clean_excerpt(first),
                "标题应直接作为第一行文章文本，不要写“标题：”或“题目：”这类控制器标签。",
            )
        )


def check_provenance_claims(findings: list[Finding], lines: list[str]) -> None:
    patterns = [
        r"(?:Anlin|安林)[^。！？\n]{0,12}本人",
        r"本人[^。！？\n]{0,8}(?:写|创作|会这么写)",
        r"(?:原作者|真实作者)[^。！？\n]{0,12}(?:写|身份|口吻)",
        r"(?:本人级|原文级|原作者级)",
        r"(?:无法|不能|不可|不被)[^。！？\n]{0,10}(?:区分|分辨|识别)",
        r"(?:看不出来|看不出)[^。！？\n]{0,10}(?:AI|生成|仿写)",
        r"(?:不是|非)[^。！？\n]{0,4}AI[^。！？\n]{0,8}(?:生成|写)",
        r"真人[^。！？\n]{0,8}(?:写|创作)",
        r"(?:冒充|伪造|伪称)[^。！？\n]{0,12}(?:作者|身份|来源)",
    ]
    compiled = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for line_number, line in visible_article_lines(lines):
        if line.startswith("#"):
            continue
        if any(pattern.search(line) for pattern in compiled):
            findings.append(
                Finding(
                    "warning",
                    "来源身份声明",
                    line_number,
                    clean_excerpt(line),
                    "文章正文不得声明真实作者身份、来源、真假、非AI或不可分辨。匿名盲评只能在报告里写测试条件、样本量和识别率。",
                )
            )


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


def check_isolated_punctuation(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped in {"。", "，", "、", "；"}:
            findings.append(
                Finding(
                    "warning",
                    "孤立中文标点",
                    line_number,
                    stripped,
                    "生成稿故障：原文偶有英文句点作呼吸，但孤立中文标点像写作/格式错误。删除该行，或改成真实呼吸短句。",
                )
            )


def check_not_x_is_y(findings: list[Finding], lines: list[str]) -> None:
    patterns = [
        re.compile(r"不是[^，。！？\n]{1,28}[,，]?(?:而|只|也)?是"),
        re.compile(r"不是[^，。！？\n]{1,28}[,，]?(?:就是|只是)"),
        re.compile(r"不是[^。！？\n]{1,28}[。！？]\s*(?:就是|只是)"),
        re.compile(r"其实不是[,，]?(?:好像|就是|只是|而是|是)"),
        re.compile(r"像[^。！？\n]{1,32}其实不是"),
    ]
    matches = [
        (line_number, line)
        for line_number, line in enumerate(lines, start=1)
        if any(pattern.search(line) for pattern in patterns)
    ]
    for line_number, line in matches:
        findings.append(
            Finding(
                "warning",
                "AI二元解释句式",
                line_number,
                clean_excerpt(line),
                "生成稿高风险：不是X是Y/而是Y/只是Y常像AI在宣布重构。优先删除否定框架，让动作、人物、身体或物件直接呈现事实。原文校准时人工区分自然对话。",
            )
        )


def check_ai_slop_terms(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        for term in AI_SLOP_TERMS:
            if term in line:
                findings.append(
                    Finding(
                        "warning",
                        f"AI解释腔: {term}",
                        line_number,
                        clean_excerpt(line),
                        "该词常把场景翻译成结论。删除解释句，改由具体动作、对话、app表面、付款或身体反应承载转向。",
                    )
                )
                break
        for term in AI_PARALLEL_TEMPLATE_TERMS:
            if term in line:
                findings.append(
                    Finding(
                        "warning",
                        f"AI平行解释模板: {term}",
                        line_number,
                        clean_excerpt(line),
                        "这类句子常把日常细节翻译成可迁移的漂亮解释。删除模板词，让下一步动作、身体反应或对方原话接住。",
                    )
                )
                break
        for term in AI_SELF_ANNOTATION_TERMS:
            if term in line:
                findings.append(
                    Finding(
                        "warning",
                        f"AI自我注解: {term}",
                        line_number,
                        clean_excerpt(line),
                        "生成稿高风险：这类'我来解释我的感觉'会把场景变成模型注解。删掉自我注解，接一个物件、身体、支付、路线或对方原话。",
                    )
                )
                break


def check_pseudo_humanizer_surface(findings: list[Finding], lines: list[str], text: str) -> None:
    for line_number, line in enumerate(lines, start=1):
        for term in PSEUDO_COLLOQUIAL_TERMS:
            if term in line:
                findings.append(
                    Finding(
                        "warning",
                        f"AI伪口语: {term}",
                        line_number,
                        clean_excerpt(line),
                        "生成稿高风险：伪俗语/伪口语常像模型拼接高频网感零件。改成场景里某个人会说的笨话，或删掉概念词保留具体动作。",
                    )
                )
                break

    present = [term for term in ORDERED_EXPLAINER_TERMS if term in text]
    if len(present) >= 2:
        findings.append(
            Finding(
                "warning",
                "AI完整结构",
                0,
                f"present={present}",
                "生成稿高风险：首先/其次/最后/综上这类顺序骨架会让文章像标准答案。把顺序说明改成物件、身体、app、对话或路线触发的跳转。",
            )
        )


def check_therapeutic_humanizer_surface(findings: list[Finding], lines: list[str]) -> None:
    speaker_context = re.compile(r"(?:我|他|她|老板|老板娘|我妈|我爸|室友|舍友|朋友|同学|狗哥|水哥|Java大哥)[^。！？\n]{0,18}(?:说|问|回|劝|安慰)")
    for line_number, line in enumerate(lines, start=1):
        for term in THERAPEUTIC_HUMANIZER_TERMS:
            if term in line:
                if speaker_context.search(line):
                    continue
                findings.append(
                    Finding(
                        "warning",
                        f"AI治疗式人类化: {term}",
                        line_number,
                        clean_excerpt(line),
                        "生成稿高风险：通用安慰/人类化词会把伤口修得太体面。删除该词，让动作、身体、付款、饭、路线、物件或对方原话承载情绪。",
                    )
                )
                break


def check_literary_ai_surface(findings: list[Finding], lines: list[str]) -> None:
    dash_patterns = [
        re.compile(r"——[^”\"。！？\n]{0,36}(?:那种|一种|终于|其实|好像|可以|变成|像|让人|让我)"),
        re.compile(r"[^”\"\n]{4,48}——(?:[^。！？\n]{0,24})(?:放松|释然|自洽|真实感|完整感|命运感|松弛|破碎感)"),
    ]
    literary_patterns = [
        re.compile(r"那种[^。！？\n]{0,28}(?:放松|释然|自洽|真实感|完整感|命运感|松弛|破碎感)"),
        re.compile(r"终于可以[^。！？\n]{0,28}(?:放松|喘气|把话说得|做自己|不用)"),
        re.compile(r"(?:有了|获得|抵达|完成)[^。！？\n]{0,16}(?:自洽|释然|真实感|完整感|命运感|松弛)"),
    ]
    for line_number, line in enumerate(lines, start=1):
        if "——" in line:
            findings.append(
                Finding(
                    "warning",
                    "破折号稀有连接",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：破折号在原文中极少，多为引语拖音或中断。正式生成稿默认不用破折号承接听觉、解释或情绪；改成逗号、换行、对方原话或动作。",
                )
            )
        if any(pattern.search(line) for pattern in dash_patterns):
            findings.append(
                Finding(
                    "warning",
                    "破折号解释连接",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：破折号后接解释、抽象情绪或'那种'补充，常像模型在替画面加注解。删掉破折号解释，改成下一步动作、对方原话、身体反应或低处后果。",
                )
            )
        if any(term in line for term in ABSTRACT_EMOTION_TERMS) or any(pattern.search(line) for pattern in literary_patterns):
            findings.append(
                Finding(
                    "warning",
                    "AI文艺解释面",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：放松/释然/自洽/真实感等抽象情绪命名容易把场景写成文学腔。用具体动作、付款、食物、身体、路线或一句笨拙回复替代。",
                )
            )


def check_ai_variable_placeholders(findings: list[Finding], lines: list[str]) -> None:
    patterns = [
        re.compile(r"(?<![A-Za-z])A(?![A-Za-z])[^。！？\n]{0,48}(?<![A-Za-z])B(?![A-Za-z])"),
        re.compile(r"[甲乙丙丁][^。！？\n]{0,48}[甲乙丙丁]"),
    ]
    for line_number, line in enumerate(lines, start=1):
        if any(pattern.search(line) for pattern in patterns):
            findings.append(
                Finding(
                    "warning",
                    "AI变量代称",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：A/B、甲乙这类变量代称会把日常失败抽象成模型解释。删除变量句，保留具体物件、价格、动作或人的原话。",
                )
            )


def check_background_fact_specificity(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        for term in UNSUPPORTED_DISTRICT_TERMS:
            if term in line:
                findings.append(
                    Finding(
                        "warning",
                        f"无依据具体地名: {term}",
                        line_number,
                        clean_excerpt(line),
                        "Anlin语料支持云南/小城/老家等纹理，不支持随手编具体城区。除非用户或检索提供背景，删掉地名，保留实际动作/路线失败。",
                    )
                )
                break
        for term in UNSUPPORTED_GAME_ROLE_TERMS:
            if term in line:
                findings.append(
                    Finding(
                        "warning",
                        f"无依据游戏角色细节: {term}",
                        line_number,
                        clean_excerpt(line),
                        "语料支持的是粗颗粒游戏事实：王者荣耀、5000局、最高星耀五、ELO、蔡文姬/补血心理；不支持排位、当前段位、角色路线、装备或原神本人游玩。除非用户提供或锚点支持，降级为粗表面或删除游戏场景。",
                    )
                )
                break
        for term in UNSUPPORTED_CITY_REVIEW_TERMS:
            if term in line:
                findings.append(
                    Finding(
                        "info",
                        f"具体城市需核实: {term}",
                        line_number,
                        clean_excerpt(line),
                        "城市名不一定错误，但必须来自用户背景、检索或语料锚点；否则优先降级为小城/那边/一个园区/学校门口等低断言表面。",
                    )
                )
                break


def check_game_match_report_surface(findings: list[Finding], lines: list[str]) -> None:
    patterns = [
        re.compile(r"点撤退"),
        re.compile(r"输出[^。！？\n]{0,12}辅助"),
        re.compile(r"对面[^。！？\n]{0,12}辅助"),
        re.compile(r"等复活"),
        re.compile(r"复活[^。！？\n]{0,12}(?:塔|泉水|团)"),
        re.compile(r"(?:第一把|第二把|第三把)[^。！？\n]{0,20}(?:王者|蔡文姬|游戏|赢|输|队友|elo|ELO)"),
        re.compile(r"(?:王者|蔡文姬|游戏|elo|ELO)[^。！？\n]{0,28}(?:第一把|第二把|第三把|连跪|赢了|输了|队友|英雄|排位界面)"),
        re.compile(r"(?:队友|英雄|连跪|排位界面)[^。！？\n]{0,28}(?:王者|蔡文姬|游戏|elo|ELO|赢|输|排位)"),
    ]
    for line_number, line in enumerate(lines, start=1):
        if any(pattern.search(line) for pattern in patterns):
            findings.append(
                Finding(
                    "warning",
                    "游戏复盘细节",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：游戏段变成比赛复盘会暴露无依据 MOBA 细节。只保留王者、5000局、最高星耀五、ELO、蔡文姬/补血心理等粗表面，把结果转成状态伤口或实际动作。",
                )
            )


def check_offer_specificity_surface(findings: list[Finding], lines: list[str]) -> None:
    offer_markers = ["offer", "入职", "签了", "体检", "租房补贴", "住房补贴"]
    specificity_markers = [
        "签字费",
        "股票",
        "base",
        "住房补贴",
        "租房补贴",
        "到手",
        "月薪",
        "年薪",
        "前端offer",
        "字节跳动",
        "腾讯",
        "阿里",
        "美团",
        "广州",
        "深圳",
        "上海",
        "杭州",
        "北京",
    ]
    for line_number, line in enumerate(lines, start=1):
        lower_line = line.lower()
        offer_hits = [term for term in offer_markers if term.lower() in lower_line]
        specificity_hits = [term for term in specificity_markers if term.lower() in lower_line]
        if offer_hits and len(specificity_hits) >= 2:
            findings.append(
                Finding(
                    "warning",
                    "Offer具体化编造",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：给同学/室友offer补公司、城市、签字费、股票、base、补贴、到手薪资等细节，像模型在补现实感。除非用户提供，降级为一个模糊屏幕表面或实际动作。",
                )
            )


def check_background_display_stuffing(findings: list[Finding], text: str) -> None:
    hits: dict[str, list[str]] = {}
    for group, terms in BACKGROUND_DISPLAY_GROUPS.items():
        present = [term for term in terms if term in text]
        if present:
            hits[group] = present[:4]
    if len(hits) >= 4:
        findings.append(
            Finding(
                "warning",
                "背景展示堆砌",
                0,
                json.dumps(hits, ensure_ascii=False),
                "生成稿高风险：多个支持背景标签同时出现，容易像读过人物档案后展示配料。背景事实只用于避免矛盾；删除不改变动作、身体、社交位置或下一场景的标签。",
            )
        )


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
        else:
            chinese_match = chinese_pattern.search(line)
            if not chinese_match:
                continue
            matched = chinese_match.group(0)
            following = line[chinese_match.end() : chinese_match.end() + 1]
            if matched == "一块" and following not in {"钱", "五"}:
                continue
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
    standalone_pattern = re.compile(r"^[“\"『「][^。！？\n]{1,40}[。！？]?[”\"』」]$")
    for line_number, line in enumerate(lines, start=1):
        if pattern.search(line):
            findings.append(Finding("info", "疑似日常对话引号", line_number, clean_excerpt(line), "原文中存在引号；这里只提示人工检查是否为代理生成稿的戏剧化对话。"))
        elif standalone_pattern.search(line.strip()):
            findings.append(
                Finding(
                    "warning",
                    "日常对话引号",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：普通微信/饭桌/室友对话不应像剧本台词一样单独加引号。改成“他说/我回/她问”引导的散文化对话，或只保留一条屏幕表面。",
                )
            )


def check_dialogue_stack(findings: list[Finding], lines: list[str]) -> None:
    speaker_pattern = re.compile(r"^(?:我|他|她|室友|舍友|有人|有个人|另一个人)[^。！？\n]{0,16}(?:说|问|回|说明)")
    run_start = 0
    run_count = 0
    excerpts: list[str] = []
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if speaker_pattern.search(stripped):
            if run_count == 0:
                run_start = index
                excerpts = []
            run_count += 1
            excerpts.append(stripped)
            continue
        if run_count >= 5:
            findings.append(
                Finding(
                    "warning",
                    "对话接力过密",
                    run_start,
                    " / ".join(excerpts[:6]),
                    "生成稿高风险：我说/他说连续接力容易让人物配合交代题面。压成一两句散文化对话，并让一个动作、误会、身体反应或沉默打断。",
                )
            )
        run_count = 0
        excerpts = []
    if run_count >= 5:
        findings.append(
            Finding(
                "warning",
                "对话接力过密",
                run_start,
                " / ".join(excerpts[:6]),
                "生成稿高风险：我说/他说连续接力容易让人物配合交代题面。压成一两句散文化对话，并让一个动作、误会、身体反应或沉默打断。",
            )
        )


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
    if 0 < chars < STANDARD_DIARY_FORMAL_MIN_CHARS:
        findings.append(
            Finding(
                "warning",
                "标准日寄完整文章篇幅偏短",
                0,
                f"body_chinese_chars={chars}",
                "完整文章盲评最低比较边界约650字；正式生成稿以850字以上为安全缓冲、900-1100字为常规目标。扩展具体动作、对话、身体/金钱后果和非主题残留，或改为短体裁匹配评估。",
            )
        )
    elif chars < STANDARD_DIARY_DRAFT_SAFE_MIN_CHARS:
        findings.append(
            Finding(
                "warning",
                "标准日寄完整文章篇幅缓冲不足",
                0,
                f"body_chinese_chars={chars}",
                "650-849字容易在生成波动和修复中变成长度识别点；正式生成稿应补到850字以上，并优先接近900-1100字，增加行动链、社交误伤、身体/金钱后果或无用日常残留。",
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


def check_ambient_ending(findings: list[Finding], lines: list[str]) -> None:
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if not visible_lines:
        return
    last_line = visible_lines[-1]
    if any(re.search(pattern, last_line) for pattern in AMBIENT_ENDING_PATTERNS):
        findings.append(
            Finding(
                "warning",
                "纯环境音结尾",
                len(lines),
                last_line,
                "纯声音/灯光/屏幕作为最后一行容易变成文学按钮；让声音造成具体身体、社交、付款、路线或回复后果，或改用该后果收束。",
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


def check_comment_chain_formula(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        marker_hits = sum(line.count(marker) for marker in COMMENT_CHAIN_FORMULA_MARKERS)
        actor_hits = len(re.findall(r"(?:有人|有个人|另一个人)(?:说|回|问|发|开始)", line))
        if marker_hits >= 1 or actor_hits >= 2:
            findings.append(
                Finding(
                    "warning",
                    "评论链公式化转述",
                    line_number,
                    clean_excerpt(line),
                    "群聊/评论入口不能写成多人接力摘要；正式生成稿不要用“有人发/有人说/有个人问/另一个人说”修补。改成屏幕视觉、未读数字、截图缩略图、手指动作、延迟回复、身体反应或现实后果。",
                )
            )


def check_rough_self_damage(findings: list[Finding], text: str) -> None:
    style = detect_style(text)
    if style != "standard" or chinese_len(text) < 650:
        return
    present = [term for term in ROUGH_SELF_DAMAGE_TERMS if term in text]
    pattern_present = [pattern for pattern in ROUGH_SELF_DAMAGE_PATTERNS if re.search(pattern, text)]
    if not present:
        present = pattern_present
    if not present:
        findings.append(
            Finding(
                "warning",
                "粗粝自毁信号不足",
                0,
                "present=[]",
                "标准日寄不能只靠安静观察和物件真实感；加入一个粗粝自嘲、身体尴尬、社交误伤或不好看的笑点。",
            )
        )


def check_material_echo(findings: list[Finding], text: str) -> None:
    normalized = re.sub(r"[，,。！？；;\s]+", "", text)
    present = [term for term in MATERIAL_ECHO_TERMS if normalized.count(term) >= 2]
    if present:
        findings.append(
            Finding(
                "warning",
                "材料钩子重复过直",
                0,
                f"terms={present}",
                "同一药、线、温度或app钩子重复得太工整；保留一次，或让第二次改变行动/社交/身体后果。",
            )
        )


def check_prompt_chain_surface(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    visible_lines = [line for line in content_lines if line.strip() and not line.startswith("<!--")]
    if not visible_lines:
        return
    opening = "\n".join(visible_lines[:6])
    tail = "\n".join(visible_lines[-4:])
    surface = "\n".join([title, opening, tail])
    matched = [term for term in PROMPT_CHAIN_TERMS if term.lower() in surface.lower()]
    if len(matched) >= 5:
        findings.append(
            Finding(
                "warning",
                "题面链条过于完整",
                0,
                f"title/opening/tail_terms={matched[:10]}",
                "标题、开头和结尾暴露太多题面名词；删除或后移至少两个高信号元素，让文章先像一天，再像回答题目。",
            )
        )


def check_mid_article_offaxis_gap(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style != "standard" or chinese_len(text) < 650:
        return
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [line for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 24:
        return
    lower_text = text.lower()
    domain_counts = {
        domain: sum(lower_text.count(term.lower()) for term in terms)
        for domain, terms in THEME_DOMAINS.items()
    }
    dominant_domain, dominant_hits = max(domain_counts.items(), key=lambda item: item[1])
    if dominant_hits < 8:
        return
    start = len(visible_lines) // 3
    end = max(start + 1, (len(visible_lines) * 2) // 3)
    middle_text = "\n".join(visible_lines[start:end])
    lower_middle = middle_text.lower()
    middle_domain_hits = sum(lower_middle.count(term.lower()) for term in THEME_DOMAINS[dominant_domain])
    off_axis_hits = [term for term in OFF_AXIS_SIGNAL_TERMS if term in middle_text]
    if middle_domain_hits >= 3 and len(off_axis_hits) < 2:
        findings.append(
            Finding(
                "warning",
                "中段旁逸不足",
                0,
                f"domain={dominant_domain}, middle_domain_hits={middle_domain_hits}, off_axis_hits={off_axis_hits}",
                "中段仍在执行主提示，旁逸细节不足或没有后果。替换一段为由身体、食物、路线、脏物件、他人误伤或小额消费触发的分支，并让它改变动作。",
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


def check_prose_block_compression(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style != "standard":
        return
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    lengths = [chinese_len(line) for line in visible_lines if chinese_len(line)]
    body_chars = chinese_len("\n".join(visible_lines))
    if body_chars < 550 or not lengths:
        return
    avg_len = sum(lengths) / len(lengths)
    sorted_lengths = sorted(lengths)
    mid = len(sorted_lengths) // 2
    if len(sorted_lengths) % 2:
        median_len = sorted_lengths[mid]
    else:
        median_len = (sorted_lengths[mid - 1] + sorted_lengths[mid]) / 2
    long_lines = sum(1 for length in lengths if length >= 80)
    if len(visible_lines) < 20 or avg_len >= 40 or median_len >= 35 or long_lines >= 3:
        findings.append(
            Finding(
                "warning",
                "散文块压缩",
                0,
                f"body_chars={body_chars}, content_lines={len(visible_lines)}, avg_line_chars={avg_len:.2f}, median_line_chars={median_len:.2f}, lines_ge80={long_lines}",
                "完整标准日寄不能压成少数大散文段；拆成更接近原文的短行/碎段，让动作、对话、误读和低处后果逐行推进。",
            )
        )


def check_short_line_poem_surface(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style != "standard" or chinese_len(text) < 450:
        return
    content_lines = [
        line.strip()
        for line in split_title_and_content_lines(lines)[1]
        if line.strip() and not line.startswith("<!--")
    ]
    if len(content_lines) < 12:
        return
    lengths = [chinese_len(line) for line in content_lines]
    short_ratio = sum(1 for length in lengths if length <= 12) / len(lengths)
    long_count = sum(1 for length in lengths if length >= 28)
    if short_ratio >= 0.70 and long_count <= 1:
        findings.append(
            Finding(
                "warning",
                "短行诗化表面",
                0,
                f"short_line_ratio={short_ratio:.2f}, long_lines={long_count}",
                "标准日寄不应全是漂亮短行；合并若干行，加入更粗糙的长口语句、对话或行动链。",
            )
        )


def check_line_length_uniformity(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style != "standard" or chinese_len(text) < 650:
        return
    content_lines = [
        line.strip()
        for line in split_title_and_content_lines(lines)[1]
        if line.strip() and not line.startswith("<!--")
    ]
    lengths = [chinese_len(line) for line in content_lines if chinese_len(line)]
    if len(lengths) < 35:
        return
    avg_len = sum(lengths) / len(lengths)
    variance = sum((length - avg_len) ** 2 for length in lengths) / len(lengths)
    stdev = variance ** 0.5
    unique_ratio = len(set(lengths)) / len(lengths)
    long_count = sum(1 for length in lengths if length >= 28)
    very_short_ratio = sum(1 for length in lengths if length <= 8) / len(lengths)
    if stdev < 5.5 and unique_ratio < 0.28 and long_count <= 2:
        findings.append(
            Finding(
                "warning",
                "节奏过度均匀",
                0,
                f"content_lines={len(lengths)}, avg={avg_len:.2f}, stdev={stdev:.2f}, unique_ratio={unique_ratio:.2f}, long_lines={long_count}, very_short_ratio={very_short_ratio:.2f}",
                "生成稿高风险：行长像被统一切齐。不要机械撒短句；用真实动作链、较长口语、对话误伤和低处后果自然打乱节奏。",
            )
        )


def check_overfragmented_lineation(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style != "standard":
        return
    content_lines = [
        line.strip()
        for line in split_title_and_content_lines(lines)[1]
        if line.strip() and not line.startswith("<!--")
    ]
    lengths = [chinese_len(line) for line in content_lines if chinese_len(line)]
    body_chars = sum(lengths)
    if body_chars < 850 or not lengths:
        return
    avg_len = body_chars / len(lengths)
    if len(lengths) > 115 or (len(lengths) > 90 and avg_len < 11):
        findings.append(
            Finding(
                "warning",
                "断裂过碎",
                0,
                f"body_chars={body_chars}, content_lines={len(lengths)}, avg_line_chars={avg_len:.2f}",
                "生成稿高风险：正文被切成过多碎行，像模型在机械制造断裂。合并连续短行，保留少数硬切，让口语句和行动链自然变长。",
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
    check_missing_title(findings, lines)
    check_provenance_claims(findings, lines)
    check_process_leakage(findings, lines)
    check_isolated_punctuation(findings, lines)
    check_comment_chain_formula(findings, lines)
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
    check_ai_slop_terms(findings, lines)
    check_pseudo_humanizer_surface(findings, lines, text)
    check_therapeutic_humanizer_surface(findings, lines)
    check_literary_ai_surface(findings, lines)
    check_ai_variable_placeholders(findings, lines)
    check_background_fact_specificity(findings, lines)
    check_game_match_report_surface(findings, lines)
    check_offer_specificity_surface(findings, lines)
    check_background_display_stuffing(findings, text)
    check_money_suffix(findings, lines)
    check_like_something(findings, lines)
    check_repeated_you(findings, lines)
    check_dialogue_quotes(findings, lines)
    check_dialogue_stack(findings, lines)
    check_high_frequency_coverage(findings, text)
    check_diagnostic_title(findings, lines)
    check_high_signal_opening(findings, lines)
    check_standard_diary_length(findings, lines, text)
    check_learned_ending_button(findings, lines)
    check_ambient_ending(findings, lines)
    check_theme_density(findings, text)
    check_rough_self_damage(findings, text)
    check_material_echo(findings, text)
    check_prompt_chain_surface(findings, lines, text)
    check_mid_article_offaxis_gap(findings, lines, text)
    check_tasteful_withholding_ending(findings, lines)
    check_quiet_explanation(findings, lines)
    check_engine_signal_density(findings, text)
    check_sealed_nocturne(findings, text)
    check_period_comma_ratio(findings, lines)
    check_prose_block_compression(findings, lines, text)
    check_short_line_poem_surface(findings, lines, text)
    check_line_length_uniformity(findings, lines, text)
    check_overfragmented_lineation(findings, lines, text)
    check_scene_count(findings, lines, text)
    check_breathing_point(findings, lines, text)
    check_metadata_comment(findings, text)
    return findings


def apply_strict_mode(findings: list[Finding], *, draft_gate: bool = False) -> list[Finding]:
    strict_findings: list[Finding] = []
    for finding in findings:
        should_promote = (
            finding.severity == "warning"
            and (
                finding.rule in STRICT_ERROR_RULE_NAMES
                or any(finding.rule.startswith(prefix) for prefix in STRICT_ERROR_RULE_PREFIXES)
                or (
                    draft_gate
                    and (
                        finding.rule in DRAFT_GATE_RULE_NAMES
                        or any(finding.rule.startswith(prefix) for prefix in DRAFT_GATE_RULE_PREFIXES)
                    )
                )
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


def read_text_flexible(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def check_corpus_overlap(
    findings: list[Finding],
    *,
    draft_path: Path,
    text: str,
    corpus_dir: Path | None,
    jaccard_threshold: float,
    shared_24gram_threshold: int,
) -> None:
    if corpus_dir is None:
        return
    if not corpus_dir.is_dir():
        findings.append(
            Finding(
                "error",
                "复制重叠风险: 语料目录不可用",
                0,
                str(corpus_dir),
                "正式全语料验证必须提供可读语料目录；否则不能声称完成复制重叠门禁。",
            )
        )
        return

    draft_5grams = char_ngram_set(text, 5)
    draft_24grams = char_ngram_set(text, 24)
    if not draft_5grams and not draft_24grams:
        return

    resolved_draft = draft_path.resolve()
    risky: list[str] = []
    for corpus_path in sorted(
        path
        for pattern in ("*.md", "*.txt")
        for path in corpus_dir.glob(pattern)
        if path.is_file()
    ):
        try:
            if corpus_path.resolve() == resolved_draft:
                continue
        except OSError:
            pass
        source_text = read_text_flexible(corpus_path)
        similarity = jaccard(draft_5grams, char_ngram_set(source_text, 5))
        shared_24grams = len(draft_24grams & char_ngram_set(source_text, 24))
        if similarity >= jaccard_threshold or shared_24grams >= shared_24gram_threshold:
            risky.append(f"{corpus_path.name}: jaccard5={similarity:.4f}, shared24={shared_24grams}")

    if risky:
        findings.append(
            Finding(
                "error",
                "复制重叠风险",
                0,
                " | ".join(risky[:5]),
                "生成稿与原文表面重叠过高或共享长片段。必须重写相关场景，不要从原文搬运句组、顺序或独有包裹。",
            )
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deterministic Anlin-style hard-rule violations.")
    parser.add_argument("file", type=Path, help="Draft markdown/text file to inspect")
    parser.add_argument("--json", action="store_true", help="Output JSON findings")
    parser.add_argument("--strict", action="store_true", help="Promote blind-evaluation high-risk warnings to errors")
    parser.add_argument("--draft-gate", action="store_true", help="Promote generated-draft-only formal article gates; do not use for original-corpus calibration")
    parser.add_argument("--corpus-dir", type=Path, default=None, help="Optional corpus directory for high-overlap copy gate")
    parser.add_argument("--copy-jaccard-threshold", type=float, default=0.16, help="5-gram Jaccard threshold for corpus copy gate")
    parser.add_argument("--copy-shared-24gram-threshold", type=int, default=2, help="Shared 24-character n-gram count threshold for corpus copy gate")
    parser.add_argument("--fail-on-warning", action="store_true", help="Return nonzero for warnings as well as errors")
    args = parser.parse_args()

    text = read_text_flexible(args.file)
    findings = collect_findings(text)
    check_corpus_overlap(
        findings,
        draft_path=args.file,
        text=text,
        corpus_dir=args.corpus_dir,
        jaccard_threshold=args.copy_jaccard_threshold,
        shared_24gram_threshold=args.copy_shared_24gram_threshold,
    )
    if args.strict or args.draft_gate:
        findings = apply_strict_mode(findings, draft_gate=args.draft_gate)
    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    else:
        print(format_text(findings))
    if args.fail_on_warning:
        return 1 if any(finding.severity in {"error", "warning"} for finding in findings) else 0
    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

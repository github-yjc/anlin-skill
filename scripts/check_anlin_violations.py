#!/usr/bin/env python3
"""Deterministic review-signal checker for Anlin-style drafts.

This script does not judge whether a draft has Anlin's voice. It only reports
searchable violations and weak signals that should trigger manual revision.
It is calibrated so original corpus files should not fail with hard errors.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


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
COMMENT_CHAIN_CONTEXT_TERMS = [
    "底下",
    "下面",
    "评论",
    "评论区",
    "回复",
    "热评",
    "群里",
    "群聊",
    "帖子",
    "视频",
    "弹幕",
    "第一条",
    "第二条",
    "被人",
]
CONTEXTUAL_COMMENT_CHAIN_MARKERS = ["跟了个", "被人回", "又发了个"]
COMMENT_CHAIN_ACTOR_MARKERS = {
    "有人说",
    "有人回",
    "有人问",
    "有人发了",
    "有人发了张",
    "有个人问",
    "另一个人说",
    "一个说",
    "又有人",
}
ONLINE_COMMENT_CONTEXT_TERMS = [
    "底下",
    "下面",
    "评论",
    "评论区",
    "回复",
    "热评",
    "群里",
    "群聊",
    "微信群",
    "帖子",
    "视频",
    "弹幕",
    "朋友圈",
    "转发",
    "截图",
    "第一条",
    "第二条",
]
LOW_FREQUENCY_TERMS = ["然而", "因此", "可是", "也许", "或许", "认为", "意识到"]
HIGH_FREQUENCY_TERMS = ["其实", "觉得", "发现", "好像", "不过", "突然", "于是", "因为", "所以"]
CONNECTOR_OVERUSE_TERMS = [
    "其实",
    "觉得",
    "发现",
    "好像",
    "不过",
    "突然",
    "于是",
    "因为",
    "所以",
    "已经",
    "当时",
    "然后",
    "结果",
    "后来",
]
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
    "现在我意识到",
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
LITERAL_SEEN_SUBJECTS = [
    "备注",
    "订单",
    "消息",
    "评论",
    "截图",
    "照片",
    "屏幕",
    "提示",
    "字",
    "名字",
    "标签",
    "二维码",
    "通知",
    "文件",
    "单号",
    "外卖单",
]
META_AI_TOPIC_TERMS = [
    "AI写",
    "AI 写",
    "AI写的文章",
    "AI文章",
    "AI对话",
    "识别AI",
    "识别 AI",
    "检测AI",
    "检测 AI",
    "生成文本",
    "机器生成",
    "模型写",
    "模型生成",
    "大模型",
    "人工智能写",
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
UNSUPPORTED_LANDMARK_PATTERNS = [
    re.compile(r"[\u4e00-\u9fff]{2,6}(?:山|湖|江|河|桥|公园|广场|车站|火车站|高铁站)(?:出来|旁边|附近|后面|那边)?[^。！？\n]{0,24}(?:川菜馆|烧烤|饭店|餐馆|小吃|店|馆|摊)"),
    re.compile(r"(?:东门|南门|西门|北门)[^。！？\n]{0,18}(?:外面|出来|旁边|后面|那边)[^。！？\n]{0,24}(?:烧烤|川菜|饭店|餐馆|小吃|店|馆|摊)"),
]
UNSUPPORTED_FAMILY_IDENTITY_TERMS = [
    "老婆",
    "妻子",
    "媳妇",
    "太太",
    "我儿子",
    "我女儿",
    "孩子他妈",
    "我家孩子",
]
THIRD_PERSON_SPEECH_CUES = [
    "他说",
    "她说",
    "他问",
    "她问",
    "老板说",
    "卖瓜的说",
    "摊主说",
    "大叔说",
    "大妈说",
    "店员说",
    "司机说",
    "对方说",
]
THIRD_PERSON_ATTRIBUTION_CUES = [
    "他",
    "她",
    "老板",
    "卖瓜的",
    "摊主",
    "大叔",
    "大妈",
    "店员",
    "司机",
    "对方",
    "朋友",
    "同学",
    "室友",
    "邻居",
]
BACKGROUND_DISPLAY_GROUPS = {
    "school_work": ["211", "春招", "外卖", "送外卖", "程序员", "被裁", "失业"],
    "game": ["王者", "王者荣耀", "星耀五", "ELO", "elo", "蔡文姬"],
    "platform": ["知乎", "小红书", "贴吧", "豆瓣", "nga", "NGA", "b站", "B站", "微博", "抖音", "GPT", "gpt", "AI", "ai"],
    "cast": ["狗哥", "Java大哥", "水哥", "我姐", "室友", "舍友", "我妈", "我爸"],
    "body": ["痛风", "脚踝", "尿急", "口腔溃疡", "褪黑素", "胸口痛"],
    "place": ["云南", "小城市", "五线", "老家", "学校门口"],
}
TEXTURE_OVERFILL_GROUPS = {
    "body": ["脚", "脚踝", "尿", "厕所", "胃", "胸口", "疼", "肿", "汗", "痔疮", "痛风", "口腔", "牙", "眼睛", "手", "裤子"],
    "screen": ["手机", "屏幕", "消息", "群", "评论", "帖子", "视频", "小红书", "知乎", "微博", "B站", "抖音", "贴吧", "NGA", "boss", "Boss", "直聘", "GPT", "AI"],
    "route_object": ["楼下", "门口", "路上", "电动车", "车", "公交", "地铁", "楼道", "快递", "钥匙", "塑料袋", "水龙头", "杯子", "充电", "空调", "冰箱"],
}
TEXTURE_SOCIAL_TERMS = [
    "我说",
    "他说",
    "她说",
    "问我",
    "问了一句",
    "回我",
    "骂",
    "笑",
    "老板",
    "摊主",
    "店员",
    "收银",
    "外卖员",
    "骑手",
    "快递员",
    "阿姨",
    "保安",
    "司机",
    "楼管",
    "房东",
    "邻居",
    "室友",
    "舍友",
    "同学",
    "朋友",
    "我妈",
    "我爸",
]
ILLNESS_CASE_REPORT_TERMS = [
    "痛风",
    "尿酸",
    "脚踝",
    "大脚趾",
    "脚趾",
    "肿",
    "疼",
    "胀",
    "富贵病",
]
ILLNESS_CASE_SCREEN_TERMS = [
    "搜",
    "搜索",
    "页面",
    "帖子",
    "网上",
    "富贵病",
    "手机",
    "屏幕",
]
ILLNESS_CASE_ROOM_FOOD_TERMS = [
    "冰箱",
    "腐乳",
    "可乐",
    "外机",
    "空调",
    "房间",
    "厨房",
    "味道",
    "药膏",
    "药",
    "碗",
]
EXPOSED_SOCIAL_CONSEQUENCE_TERMS = [
    "我说",
    "他说",
    "她说",
    "问我",
    "问了一句",
    "回我",
    "老板",
    "摊主",
    "店员",
    "收银",
    "外卖员",
    "骑手",
    "快递员",
    "保安",
    "司机",
    "楼管",
    "房东",
    "邻居",
    "室友",
    "舍友",
    "同学",
    "朋友",
    "我妈",
    "我爸",
    "敲门",
    "递给",
    "递过去",
    "接过",
    "扶了一下",
    "看了我",
    "盯着我",
    "等我扫码",
    "站那里没走",
    "他没走",
    "没收手",
    "没松手",
    "拿点纸",
    "拿稳点",
    "催了一下",
]
SOCIAL_DECLINE_TERMS = [
    "狗哥",
    "结婚",
    "婚礼",
    "随礼",
    "红包",
    "份子钱",
    "高铁",
    "车票",
    "恭喜",
    "来不来",
    "来不",
    "去不了",
    "走不开",
    "抱拳",
]
SOCIAL_DECLINE_PLAIN_RESPONSE_RE = re.compile(
    r"(?:狗哥|他|她|对方|同学|朋友)?[^。！？\n]{0,8}(?:回|发|说)[^。！？\n]{0,18}"
    r"(?:好的|好|行|嗯|OK|ok|抱拳|表情|收到|知道了|你先忙|没事)"
)
SOCIAL_DECLINE_REPLY_PRIVATE_LOOP_TERMS = [
    "手机",
    "屏幕",
    "水",
    "水滴",
    "水龙头",
    "热水器",
    "袖口",
    "袖子",
    "裤腿",
    "湿",
    "油印",
    "白印",
    "指纹",
    "充电",
    "暖气",
    "泡面",
    "杯子",
    "碗",
    "厨房",
    "房间",
    "床",
    "桌上",
]
SOCIAL_DECLINE_REPLY_VISIBLE_ACTION_TERMS = [
    "门口",
    "楼道",
    "邻居",
    "阿姨",
    "外卖员",
    "骑手",
    "店员",
    "收银",
    "老板",
    "房东",
    "室友",
    "问我",
    "问了一句",
    "指",
    "等我",
    "等着",
    "站着没走",
    "没走",
    "扫码",
    "付款",
    "二维码",
    "地址",
    "定位",
    "退票",
    "车票",
    "打车",
    "路线",
    "下楼",
    "出门",
    "走到",
    "扶墙",
    "让路",
    "答不上",
    "没答",
    "掉在",
    "洒在",
    "漏到",
    "摔",
    "滑",
    "跪",
    "递给",
    "接过",
    "关门",
    "门夹",
    "门撞",
]
SOCIAL_DECLINE_GROUP_FAKE_CONSEQUENCE_TERMS = [
    "群里有人问",
    "群里有人说",
    "群里有人发",
    "群里回",
    "有人@我",
    "@我",
    "你怎么说",
    "你不是",
    "你们项目",
    "项目不是",
    "正在输入",
    "没有下文",
]
SOCIAL_DECLINE_TIDY_ETIQUETTE_CLOSURE_TERMS = [
    "人不到钱到",
    "人不到没事",
    "下次一起吃饭",
    "下次一起喝",
    "下次补上",
    "心意到了",
    "心意到就行",
    "沾点喜气",
    "抱歉人不到",
    "不用随礼",
    "别转了",
    "到时候请你",
]
SOCIAL_DECLINE_DECOUPLED_CONSEQUENCE_TERMS = [
    "外卖",
    "骑手",
    "包装袋",
    "袋子",
    "汤",
    "红油",
    "洒",
    "漏",
    "烫",
    "泡面",
    "水槽",
    "水龙头",
    "热水器",
    "洗碗",
    "洗手",
    "厨房",
    "拖地",
    "垃圾袋",
    "快递",
    "取快递",
    "便利店",
    "超市",
    "下楼买",
    "下楼取",
]
SOCIAL_DECLINE_COUPLED_CONSEQUENCE_PATTERNS = [
    re.compile(r"(?:等我|等着|催|问我|指|没走|站着)[^。！？\n]{0,28}(?:扫码|付款|回|回复|手机|屏幕|手|门口)"),
    re.compile(r"(?:扫码|付款|二维码|余额|支付)[^。！？\n]{0,35}(?:狗哥|婚礼|随礼|回复|回|手机|手|等|门口)"),
    re.compile(r"(?:路线|定位|车票|退票|打车|地址)[^。！？\n]{0,35}(?:婚礼|狗哥|随礼|去不了|走不开|回复|回|卡|没)"),
    re.compile(r"(?:手|袖口|水|油|脏|湿)[^。！？\n]{0,28}(?:回复|回|发|发送|打字|按|屏幕)"),
    re.compile(r"(?:回复|回|发送|打字|手机|屏幕)[^。！？\n]{0,28}(?:手|袖口|水|油|脏|湿)"),
    re.compile(r"(?:他|她|对方|外卖员|骑手|店员|老板|邻居)[^。！？\n]{0,24}(?:问|催|等|指|站着|没走)"),
]
SOCIAL_DECLINE_REFUSAL_TERMS = [
    "去不了",
    "走不开",
    "最近忙",
    "忙项目",
    "赶项目",
    "不来了",
    "来不了",
    "算了吧",
]
SOCIAL_DECLINE_TIME_EXPANSION_TERMS = [
    "第二天",
    "第二天早上",
    "第二天出门",
    "中午",
    "下午",
    "晚上去",
    "回家上楼",
    "下楼",
    "出门",
    "到站",
    "地铁",
    "班群",
    "合照",
    "朋友圈",
]
SOCIAL_DECLINE_SCRIPTED_EXTENSION_TERMS = [
    "伴郎",
    "喜酒",
    "不强求",
    "人不到心意到",
    "心意到",
    "酒店外景",
    "西装试装",
]
SOCIAL_DECLINE_OFFICE_COMMUTE_DRIFT_TERMS = [
    "同事",
    "工位",
    "座位",
    "领导",
    "组长",
    "下班",
    "地铁",
    "到站",
]
THIRD_PERSON_NARRATOR_SLIP_PATTERNS = [
    re.compile(r"^他(?:把手机|翻了个身|躺在床|坐在床|拉(?:了)?被子|关(?:了)?屏幕|打开手机|塞(?:到|进)枕头)"),
    re.compile(r"^他[^。！？\n]{0,16}(?:枕头|床上|被子|天花板|窗帘|充电线|手机屏幕)"),
]
THIRD_PERSON_CONTEXT_MARKERS = [
    "狗哥",
    "同学",
    "朋友",
    "老板",
    "店员",
    "骑手",
    "邻居",
    "他说",
    "他问",
    "他回",
    "他发",
    "他没再回",
]
ROOM_COLD_FILLER_TERMS = [
    "暖气",
    "冷",
    "凉",
    "冰",
    "手指",
    "脚趾",
    "拖鞋",
    "泡面",
    "筷子",
    "袖口",
    "油",
    "水龙头",
    "洗手",
    "厨房",
    "窗户",
    "冷风",
]
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
GAME_CONTEXT_TERMS = [
    "王者",
    "王者荣耀",
    "游戏",
    "蔡文姬",
    "ELO",
    "elo",
    "队友",
    "英雄",
    "排位",
    "匹配",
    "复活",
    "满血",
    "辅助",
    "法师",
    "射手",
    "团战",
    "二塔",
    "MVP",
    "结算",
    "经济面板",
    "装备",
    "adc",
    "ADC",
    "ad",
    "AD",
]
CURRENT_OFFICE_PERSONA_TERMS = [
    "到了公司",
    "到公司",
    "下班的时候",
    "上班",
    "下班",
    "工位",
    "部门",
    "KPI",
    "kpi",
    "营收",
    "财务",
    "领导",
    "王总",
    "同事小",
    "张哥",
    "开会",
    "散会",
    "饭卡",
    "实习生",
    "季度",
]
CURRENT_OFFICE_HIGH_SPECIFIC_TERMS = ["到了公司", "工位", "KPI", "kpi", "营收", "王总", "同事小", "张哥"]
WORK_CONSEQUENCE_CHAIN_TERMS = [
    "领导",
    "主管",
    "组长",
    "经理",
    "同事",
    "公司",
    "上班",
    "下班",
    "请假",
    "病假",
    "半天假",
    "请不了假",
    "请不下来",
    "请不掉假",
    "调休",
    "排班",
    "换班",
    "轮班",
    "值班",
    "假条",
    "批假",
    "扣钱",
    "工资",
    "考勤",
    "打卡",
    "周一",
    "月底",
    "周报",
    "项目",
    "交付",
    "文件",
    "表格",
    "汇报",
    "开会",
    "绩效",
    "KPI",
    "kpi",
]
WORK_CONSEQUENCE_CHAIN_PATTERNS = [
    re.compile(r"(?:领导|主管|组长|经理)[^。！？\n]{0,50}(?:文件|表格|周一|明天|今天|请假|扣钱|上班|开会|汇报|KPI|kpi|绩效|打卡|考勤)"),
    re.compile(r"(?:领导|主管|组长|经理)[^。！？\n]{0,50}(?:项目|交付|月底)"),
    re.compile(r"(?:请假|病假)[^。！？\n]{0,35}(?:扣钱|工资|领导|主管|组长|经理|公司|上班|考勤|打卡)"),
    re.compile(r"(?:半天假|请假|病假|调休|排班|换班|轮班|值班|假条|批假)[^。！？\n]{0,35}(?:请不下来|请不了|请不掉|批不下来|批不了|调不开|排不开|换不了|不好请|没法请|不让请)"),
    re.compile(r"(?:请不了假|请不下来|请不掉假|假请不下来|假请不了|批不了假|批不下来|调休调不开|排班排不开)"),
    re.compile(r"(?:周一|月底|明天|今天)[^。！？\n]{0,35}(?:要交|要发|交材料|交表|交文件|交付|汇报|开会)"),
]
THIRD_PERSON_OFFICE_SURFACE_MARKERS = [
    "朋友圈",
    "动态",
    "配图",
    "照片",
    "文案",
    "截图",
    "屏幕",
    "消息",
    "群里",
    "工牌",
    "同学",
    "老同学",
    "朋友",
    "前同事",
    "别人",
    "人家",
    "他",
    "她",
    "晒",
    "发了",
]
FIRST_PERSON_OFFICE_SURFACE_MARKERS = [
    "我",
    "自己",
    "坐回",
    "回到",
    "走到",
    "到了公司",
    "到公司",
    "上班",
    "下班",
    "开会",
    "散会",
    "饭卡",
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
    "Now let me",
    "write the draft article",
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
    "结婚",
    "婚礼",
    "痛风",
    "跨年",
    "新年",
    "元旦",
    "年度总结",
    "聊天记录",
    "旧聊天",
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
    "结婚",
    "婚礼",
    "痛风",
    "跨年",
    "新年",
    "元旦",
    "年度总结",
    "聊天记录",
    "旧聊天",
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
    "今天先这样。",
    "今天就这样。",
    "今天就先这样。",
    "就先这样。",
    "先这样吧。",
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
    "time_feed": [
        "跨年",
        "新年",
        "元旦",
        "年度总结",
        "朋友圈",
        "flag",
        "聊天记录",
        "旧聊天",
        "毕业论文",
        "毕业旅行",
        "室友",
        "2021",
        "2022",
        "2023",
        "2024",
    ],
}
STANDARD_PROMPT_PROP_TITLE_TERMS = [
    "备注",
    "香菜",
    "麻辣烫",
    "外卖",
    "订单",
    "优惠券",
    "朋友圈",
    "玫瑰",
    "礼物",
    "红包",
    "转账",
    "收款",
    "已读",
    "点赞",
    "短视频",
    "情人节",
    "康乃馨",
]
STANDARD_PROMPT_PROP_CONTEXT_TERMS = sorted(
    {
        "备注",
        "香菜",
        "麻辣烫",
        "外卖",
        "订单",
        "优惠券",
        "配送",
        "骑手",
        "店家",
        "朋友圈",
        "玫瑰",
        "礼物",
        "情侣",
        "对象",
        "情人节",
        "红包",
        "转账",
        "收款",
        "已读",
        "点赞",
        "短视频",
        "康乃馨",
        "母亲节",
        "跨年",
        "新年",
        "年度总结",
        "聊天记录",
    },
    key=len,
    reverse=True,
)
STANDARD_PROMPT_PROP_SECONDARY_TERMS = [
    term
    for term in STANDARD_PROMPT_PROP_CONTEXT_TERMS
    if term not in {"配送", "店家", "对象", "情侣"}
]
TIME_ARCHIVE_TERMS = [
    "跨年",
    "新年",
    "元旦",
    "年度总结",
    "朋友圈",
    "flag",
    "聊天记录",
    "旧聊天",
    "旧手机",
    "备份",
    "语音条",
    "红叹号",
    "加载不出来",
    "毕业论文",
    "查重",
    "2021",
    "二一年",
]
SCREEN_ARCHAEOLOGY_TERMS = [
    "手机",
    "屏幕",
    "朋友圈",
    "年度总结",
    "往上翻",
    "往下滑",
    "翻到",
    "点进",
    "退出来",
    "锁屏",
    "按亮",
    "相册",
    "缓存",
    "旧手机",
    "备份",
    "聊天记录",
    "语音条",
    "红叹号",
    "对话框",
    "联系人",
    "通讯录",
    "群聊",
]
SOCIAL_FEED_SURFACE_TERMS = [
    "朋友圈",
    "动态",
    "小红书",
    "微博",
    "空间",
    "短视频",
    "评论区",
    "屏幕",
]
SOCIAL_FEED_INVENTORY_TERMS = [
    "晒花",
    "晒礼物",
    "晒转账",
    "晒红包",
    "晒电影票",
    "晒合照",
    "花",
    "玫瑰",
    "礼物",
    "转账",
    "红包",
    "电影票",
    "康乃馨",
    "合照",
    "截图",
    "点赞",
]
SOCIAL_FEED_INVENTORY_WORDS = [
    "满屏",
    "全是",
    "都是",
    "一条一条",
    "刷到头",
    "刷了一屏",
    "刷了几屏",
    "往下刷",
]
OUTSIDE_CONTACT_TERMS = [
    "老板",
    "摊主",
    "店员",
    "收银",
    "骑手",
    "司机",
    "保安",
    "阿姨",
    "邻居",
    "室友",
    "舍友",
    "同学",
    "朋友",
    "大爷",
    "大妈",
    "楼下有人",
    "隔壁楼有人",
    "问我",
    "回我",
    "看了我",
    "瞥了我",
]
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
    "丢人",
    "要命",
    "恶心",
    "吐出来",
    "黑泥",
    "指甲断",
    "胃疼",
    "咕噜",
    "抽筋",
    "干呕",
    "不是东西",
    "脏东西",
    "差点跪",
    "胀袋",
    "硌牙",
    "油蹭",
    "劣汰",
    "欠了",
    "没躲过",
    "没躲过去",
    "拖鞋穿反",
    "鼻涕差点",
    "黏糊糊",
    "脚后跟磨",
    "大拇指快顶",
    "裤腿上也脏",
    "探头看",
    "甩不掉",
    "胃响",
    "假装没听见",
    "纸巾擦",
    "擦了擦手",
]
ENGINE_SIGNAL_PATTERNS = [
    # Public low-status reactions can drive a paragraph even when the surface
    # words are quiet. Keep this narrow so private grime does not pass.
    r"(?:老板|摊主|店员|收银|他|她)[^。！？\n]{0,30}(?:看|瞥)[^。！？\n]{0,18}(?:我的)?(?:手|手指|指甲|指甲缝)[^。！？\n]{0,40}(?:嘴角|停|顿|没接|纸巾|擦|零钱|硬币)",
    r"(?:我的)?(?:手|手指|指甲|指甲缝)[^。！？\n]{0,24}(?:灰|黑|脏|泥|汁)[^。！？\n]{0,50}(?:老板|摊主|店员|收银|他|她)[^。！？\n]{0,35}(?:看|瞥|嘴角|停|顿|纸巾|擦|零钱|硬币)",
    r"(?:以为|还以为)[^。！？\n]{0,24}(?:老鼠|虫|玻璃|血|坏了|漏了|有人)",
    r"(?:拖鞋|鞋)[^。！？\n]{0,36}(?:左右脚不一样|一个高一个低|穿反|穿错)[\s\S]{0,90}(?:绊|摔|门槛|楼道|差点|看)",
    r"(?:绊|摔|栽|跪)[^。！？\n]{0,36}(?:门槛|楼道|墙|快递盒|泡沫|纸箱|手印|湿手印)",
    r"(?:快递盒|泡沫|纸箱)[^。！？\n]{0,40}(?:碰倒|倒|滚|撒|散了一地)",
    r"(?:外卖员|骑手|快递员|老板|摊主|店员|收银)[\s\S]{0,100}(?:等(?:我)?扫码|站(?:在)?[^。！？\n]{0,16}(?:没走|等)|看着|举着)[\s\S]{0,120}(?:手机卡|没扫上|扫(?:了)?(?:一|两|二)?次|扫码|付款|二维码)",
    r"(?:手机卡|没扫上|扫(?:了)?(?:一|两|二)?次|扫码|付款|二维码)[\s\S]{0,120}(?:外卖员|骑手|快递员|老板|摊主|店员|收银|他|她)[^。！？\n]{0,40}(?:等|站|看着|没走|举着)",
    r"(?:提手|塑料袋|袋子)[^。！？\n]{0,24}(?:断|裂|破)[\s\S]{0,120}(?:粥|汤|饭|面|外卖)[^。！？\n]{0,30}(?:淌|洒|漏|流|泼)[\s\S]{0,120}(?:外卖员|骑手|快递员|老板|摊主|店员|收银|他看着|她看着|门口|楼道|扫码|付款)",
    r"(?:粥|汤|饭|面|外卖)[^。！？\n]{0,30}(?:淌|洒|漏|流|泼)[^。！？\n]{0,40}(?:手|裤|鞋|拖鞋|地)[\s\S]{0,120}(?:外卖员|骑手|快递员|老板|摊主|店员|收银|他看着|她看着|等(?:我)?扫码|门口|楼道)",
    r"(?:汤|红油|外卖)[^。！？\n]{0,50}(?:渗|滴|淌|流|漏|洒)[^。！？\n]{0,50}(?:裤腿|裤子|裤脚|手|鞋|地)[\s\S]{0,120}(?:外卖员|骑手|快递员|他|她)[^。！？\n]{0,70}(?:等|没说话|没应|提醒|问|指|递回|退回|扫码|付款|门|袋子(?:断|漏|破)|掉|滑|摔|跪)",
    r"(?:外卖员|骑手|快递员)[^。！？\n]{0,80}(?:视线|看|瞥)[^。！？\n]{0,60}(?:裤腿|裤子|裤脚|油|汤)[\s\S]{0,120}(?:袋子(?:断|漏|破)|扫码|付款|等|没扫上|门|掉|滑|摔|跪|扶墙|递回|提醒|问|擦到(?:墙|门|裤))",
    r"(?:外卖员|骑手|快递员)[\s\S]{0,140}(?:问我有没有纸|问有没有纸|要纸|找纸)[\s\S]{0,100}(?:口袋[^。！？\n]{0,24}空|没有纸|没纸|手[^。！？\n]{0,24}空|等了[^。！？\n]{0,20}才松手|没答|答不上)",
    r"(?:外卖员|骑手|快递员)[\s\S]{0,130}(?:没收手|没松手|这才把袋子递过来)[\s\S]{0,130}(?:问了一句|问|备注|拿稳|袋子|门口)",
    r"(?:外卖员|骑手|快递员|他)[\s\S]{0,90}(?:没走|站着没走)[\s\S]{0,100}(?:纸|拿点纸|拿纸)[\s\S]{0,100}(?:不用|关上门|门关|答不上|没答)",
    r"(?:楼管|保安|邻居|房东)[\s\S]{0,100}(?:裤子|裤腿|裤脚|油|汤|脏|垃圾袋|房租|催)[\s\S]{0,120}(?:递过去|接过|洗洁精|一起扔|催|没回|扣在桌上)",
    r"(?:楼道|门口|半层)[\s\S]{0,80}(?:阿姨|邻居|大妈)[\s\S]{0,120}(?:袋子(?:破|漏)|汤|地上|袖口|袖子|黑印|脏|味道)[\s\S]{0,140}(?:等|让路|关上|关门|擦|按|抹|绊|滑|摔|没答|答不上|声音[^。！？\n]{0,12}小|不知道手该放哪)",
    r"(?:阿姨|邻居|大妈)[\s\S]{0,80}(?:说|问|指|看|等)[\s\S]{0,80}(?:袖口|袖子|袋子|汤|地上|味道|越擦越黑)[\s\S]{0,140}(?:我(?:嗯|说好|蹲|擦|按|关|让|抬脚|差点)|门|墙角|拖鞋|声音[^。！？\n]{0,12}小|不知道手该放哪)",
    r"(?:袖口|袖子|黑印|汤|垃圾袋)[\s\S]{0,100}(?:阿姨|邻居|大妈)[\s\S]{0,100}(?:别拿袖子擦|越擦越黑|你先关上|味道出来了|袋子破了|地上都是汤|让一下|等着我让路)",
    r"(?:阿姨|邻居|大妈)[\s\S]{0,100}(?:说|问|指|看|等|绕)[\s\S]{0,100}(?:水都到门外|水线|水[^。！？\n]{0,18}门外|潮|湿印|鞋边|裤腿)[\s\S]{0,140}(?:擦|蹲|按|蹭|抹|湿袜子|湿拖鞋|声音[^。！？\n]{0,12}小|垃圾袋|绕过去)",
    r"(?:水线|水都到门外|湿印子)[\s\S]{0,100}(?:门外|玄关|门槛|鞋边|过道|楼道)[\s\S]{0,120}(?:湿袜子|袜子|蹲|擦|按|蹭|抹|膝盖|湿拖鞋)",
    r"(?:湿袜子|湿拖鞋|裤脚|裤腿|膝盖)[\s\S]{0,100}(?:阿姨|邻居|大妈|她)[\s\S]{0,90}(?:说|问|指|看|绕|等)",
    r"(?:房东|中介|室友|邻居|朋友)[\s\S]{0,80}(?:微信|消息|房租|催)[\s\S]{0,80}(?:没回|扣在桌上|删掉|回了个|没敢回)",
    r"(?:外卖员|骑手|快递员)[^。！？\n]{0,90}(?:看了我一眼|看了[^。！？\n]{0,20}(?:袖|脚|拖鞋)|瞥)[\s\S]{0,140}(?:把袖口往下扯|让人家等|门[^。！？\n]{0,20}(?:夹|撞|关)|袋子(?:断|漏|破)|扫码|付款|没扫上|掉|滑|摔|跪|扶墙|没答|没回)",
    r"(?:门口|楼道|门缝)[\s\S]{0,120}(?:粥|汤|外卖)[^。！？\n]{0,40}(?:脚底|踩到|拖鞋|鞋)[^。！？\n]{0,40}(?:滑|打滑|差点|摔)",
    r"(?:手背|手上|手指)[^。！？\n]{0,36}(?:灰|黑|脏)[\s\S]{0,100}(?:手机|屏幕)[^。！？\n]{0,50}(?:黑印|留下|蹭|指纹|印)",
    r"(?:外卖员|骑手|快递员|他|她)[\s\S]{0,120}(?:往里看|往屋里看|往房间看|看了(?:我)?一眼|瞥了(?:我)?一眼)[\s\S]{0,100}(?:屋里|房间|桌上|地上)[^。！？\n]{0,60}(?:乱|快餐盒|外卖盒|外卖袋|垃圾|没收)",
    r"(?:屋里|房间|桌上|地上)[^。！？\n]{0,60}(?:乱|快餐盒|外卖盒|外卖袋|垃圾|没收)[\s\S]{0,100}(?:外卖员|骑手|快递员|他|她)[^。！？\n]{0,40}(?:往里看|往屋里看|往房间看|看了(?:我)?一眼|瞥了(?:我)?一眼)",
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
    "廉价",
    "养不起",
    "冻不死",
    "好家伙",
    "工贼",
    "塞牙",
    "牙缝",
    "韭菜",
    "痘",
    "黑泥",
    "指甲断",
    "抽筋",
    "干呕",
    "不是东西",
    "脏东西",
    "差点跪",
    "胀袋",
    "硌牙",
    "油蹭",
    "咕噜咕噜",
    "拉肚子",
    "憋都憋不住",
    "碰瓷",
    "断掉的卡",
    "卡太软",
    "指甲缝里都是灰",
    "拖鞋穿反",
    "鼻涕差点",
    "黏糊糊",
    "脚后跟磨",
    "大拇指快顶",
    "裤腿上也脏",
    "头发几天没洗",
    "嘴角干裂",
    "快餐盒",
]
ROUGH_SELF_DAMAGE_PATTERNS = [
    r"(?<![一二两三四五六七八九十百千万\d])滚(?![一二两三四五六七八九十百千万\d年月日天点分秒])",
    r"我[^。！？\n]{0,12}(?:丢人|社死|嘴贱|像个傻逼|像傻逼)",
    r"(?:拉屎|尿|痔疮|阳痿)[^。！？\n]{0,24}(?:我|自己|本人|室友|同学|群|厕所)?",
    r"(?:牙齿|牙缝)[^。！？\n]{0,16}(?:塞|卡)",
    r"指甲[^。！？\n]{0,16}(?:断|黑泥|油)",
    r"肚子[^。！？\n]{0,16}咕噜",
    r"(?:火腿肠|包装|袋)[^。！？\n]{0,16}胀袋",
    r"黑泥[^。！？\n]{0,16}(?:咽|蹭)",
    r"吐[^。！？\n]{0,8}出来",
    r"干呕[^。！？\n]{0,16}",
    r"不是东西",
    r"不能吃[^。！？\n]{0,8}脏东西",
    r"差点跪[^。！？\n]{0,12}",
    r"脚趾[^。！？\n]{0,16}(?:露|缩|黑|脏)",
    r"(?:拉肚子|拉了[一二两三四五六七八九十\d]+回|憋都憋不住)",
    r"腿一软[^。！？\n]{0,12}跪",
    r"好像我是碰瓷",
    r"头[^。！？\n]{0,16}(?:肿|包)",
    r"闻[^。！？\n]{0,12}袜",
    r"(?:后背|脖子|脸|身上)[^。！？\n]{0,24}(?:痘|痒|疼)",
    r"(?:馅|汤|外卖盒|垃圾桶)[^。！？\n]{0,30}(?:泥|酸|臭|发霉)",
    r"(?:废卡|卡)[^。！？\n]{0,24}(?:门缝|防盗门|门板|锁)[^。！？\n]{0,30}(?:断|弯|折|撬)",
    r"(?:撬门|撬开|插进门缝)[^。！？\n]{0,30}(?:断|弯|折|没用|打不开)",
    r"膝盖[^。！？\n]{0,14}(?:响|嘎吱)[^。！？\n]{0,18}(?:楼道|走廊|门口|清清楚楚)",
    r"(?:邻居|对门|中年女|别人|人家)[\s\S]{0,90}(?:看到|看见|看|瞥|顿)[\s\S]{0,110}(?:断掉的卡|断卡|胶带|撬门|门缝)",
    r"指甲缝[^。！？\n]{0,18}(?:灰|脏|泥)",
    r"(?:裤子|裤脚|裤腿)[^。！？\n]{0,28}(?:灰|泥|脏)[^。！？\n]{0,48}(?:看得很清楚|看了我|收银|老板|店员|邻居|别人|走廊灯)",
    r"(?:收银|老板|店员|年轻女|中年女)[^。！？\n]{0,50}看了[^。！？\n]{0,18}(?:手|裤|鞋|脚)",
    r"拖鞋[^。！？\n]{0,12}穿反",
    r"鼻涕[^。！？\n]{0,12}(?:出来|擦|流)",
    r"(?:手背|手上|手指)[^。！？\n]{0,24}(?:灰|黑|脏)[^。！？\n]{0,48}(?:裤腿|裤子|衣服|蹭)",
    r"(?:水槽|下水道|地漏|洗手池)[^。！？\n]{0,60}(?:头发|黏糊糊|堵)",
    r"头发[^。！？\n]{0,24}(?:黏糊糊|甩不掉)",
    r"(?:袜子|袜)[^。！？\n]{0,40}(?:洞|脚后跟磨|大拇指快顶|露|破)",
    r"(?:裤腿|裤子|裤脚)[^。！？\n]{0,35}(?:灰|泥|脏)[\s\S]{0,90}(?:阳台|邻居|中年女|别人|看了我|探头|瞥)",
    r"(?:阳台|邻居|中年女|别人)[\s\S]{0,90}(?:看了我|探头看|瞥)[\s\S]{0,90}(?:裤腿|裤子|灰|脏|纸箱)",
    r"胃[^。！？\n]{0,16}响[^。！？\n]{0,40}(?:店里|老板|店员|收银|他|她|抬头|安静|看)",
    r"(?:碰到我的手|看了我的手|看我的手)[\s\S]{0,90}(?:灰|黑|脏)[\s\S]{0,90}(?:纸巾擦|擦了擦手|零钱|老板|店员|收银)",
    r"(?:手|手背|手上)[^。！？\n]{0,36}(?:灰|黑|脏)[\s\S]{0,120}(?:纸巾擦|擦了擦手|零钱|老板|店员|收银)",
    r"(?:拖鞋|鞋)[^。！？\n]{0,36}(?:左右脚不一样|一个高一个低|穿反|穿错)[\s\S]{0,90}(?:绊|摔|门槛|楼道|差点)",
    r"(?:绊|摔|栽|跪)[^。！？\n]{0,36}(?:门槛|楼道|墙|快递盒|泡沫|纸箱|手印|湿手印)",
    r"(?:外卖员|骑手|快递员|老板|摊主|店员|收银)[\s\S]{0,100}(?:等(?:我)?扫码|站(?:在)?[^。！？\n]{0,16}(?:没走|等)|看着|举着)[\s\S]{0,120}(?:手机卡|没扫上|扫(?:了)?(?:一|两|二)?次|扫码|付款|二维码)",
    r"(?:手机卡|没扫上|扫(?:了)?(?:一|两|二)?次|扫码|付款|二维码)[\s\S]{0,120}(?:外卖员|骑手|快递员|老板|摊主|店员|收银|他|她)[^。！？\n]{0,40}(?:等|站|看着|没走|举着)",
    r"(?:提手|塑料袋|袋子)[^。！？\n]{0,24}(?:断|裂|破)[\s\S]{0,120}(?:粥|汤|饭|面|外卖)[^。！？\n]{0,30}(?:淌|洒|漏|流|泼)[\s\S]{0,120}(?:外卖员|骑手|快递员|老板|摊主|店员|收银|他看着|她看着|门口|楼道|扫码|付款)",
    r"(?:粥|汤|饭|面|外卖)[^。！？\n]{0,30}(?:淌|洒|漏|流|泼)[^。！？\n]{0,40}(?:手|裤|鞋|拖鞋|地)[\s\S]{0,120}(?:外卖员|骑手|快递员|老板|摊主|店员|收银|他看着|她看着|等(?:我)?扫码|门口|楼道)",
    r"(?:汤|红油|外卖)[^。！？\n]{0,50}(?:渗|滴|淌|流|漏|洒)[^。！？\n]{0,50}(?:裤腿|裤子|裤脚|手|鞋|地)[\s\S]{0,120}(?:外卖员|骑手|快递员|他|她)[^。！？\n]{0,70}(?:等|没说话|没应|提醒|问|指|递回|退回|扫码|付款|门|袋子(?:断|漏|破)|掉|滑|摔|跪)",
    r"(?:外卖员|骑手|快递员)[^。！？\n]{0,80}(?:视线|看|瞥)[^。！？\n]{0,60}(?:裤腿|裤子|裤脚|油|汤)[\s\S]{0,120}(?:袋子(?:断|漏|破)|扫码|付款|等|没扫上|门|掉|滑|摔|跪|扶墙|递回|提醒|问|擦到(?:墙|门|裤))",
    r"(?:外卖员|骑手|快递员)[\s\S]{0,140}(?:问我有没有纸|问有没有纸|要纸|找纸)[\s\S]{0,100}(?:口袋[^。！？\n]{0,24}空|没有纸|没纸|手[^。！？\n]{0,24}空|等了[^。！？\n]{0,20}才松手|没答|答不上)",
    r"(?:外卖员|骑手|快递员)[^。！？\n]{0,90}(?:看了我一眼|看了[^。！？\n]{0,20}(?:袖|脚|拖鞋)|瞥)[\s\S]{0,140}(?:把袖口往下扯|让人家等|门[^。！？\n]{0,20}(?:夹|撞|关)|袋子(?:断|漏|破)|扫码|付款|没扫上|掉|滑|摔|跪|扶墙|没答|没回)",
    r"(?:楼道|门口|半层)[\s\S]{0,80}(?:阿姨|邻居|大妈)[\s\S]{0,120}(?:袋子(?:破|漏)|汤|地上|袖口|袖子|黑印|脏|味道)[\s\S]{0,140}(?:等|让路|关上|关门|擦|按|抹|绊|滑|摔|没答|答不上|声音[^。！？\n]{0,12}小|不知道手该放哪)",
    r"(?:阿姨|邻居|大妈)[\s\S]{0,80}(?:说|问|指|看|等)[\s\S]{0,80}(?:袖口|袖子|袋子|汤|地上|味道|越擦越黑)[\s\S]{0,140}(?:我(?:嗯|说好|蹲|擦|按|关|让|抬脚|差点)|门|墙角|拖鞋|声音[^。！？\n]{0,12}小|不知道手该放哪)",
    r"(?:袖口|袖子|黑印|汤|垃圾袋)[\s\S]{0,100}(?:阿姨|邻居|大妈)[\s\S]{0,100}(?:别拿袖子擦|越擦越黑|你先关上|味道出来了|袋子破了|地上都是汤|让一下|等着我让路)",
    r"(?:阿姨|邻居|大妈)[\s\S]{0,100}(?:说|问|指|看|等|绕)[\s\S]{0,100}(?:水都到门外|水线|水[^。！？\n]{0,18}门外|潮|湿印|鞋边|裤腿)[\s\S]{0,140}(?:擦|蹲|按|蹭|抹|湿袜子|湿拖鞋|声音[^。！？\n]{0,12}小|垃圾袋|绕过去)",
    r"(?:水线|水都到门外|湿印子)[\s\S]{0,100}(?:门外|玄关|门槛|鞋边|过道|楼道)[\s\S]{0,120}(?:湿袜子|袜子|蹲|擦|按|蹭|抹|膝盖|湿拖鞋)",
    r"(?:湿袜子|湿拖鞋|裤脚|裤腿|膝盖)[\s\S]{0,100}(?:阿姨|邻居|大妈|她)[\s\S]{0,90}(?:说|问|指|看|绕|等)",
    r"(?:门口|楼道|门缝)[\s\S]{0,120}(?:粥|汤|外卖)[^。！？\n]{0,40}(?:脚底|踩到|拖鞋|鞋)[^。！？\n]{0,40}(?:滑|打滑|差点|摔)",
    r"(?:手背|手上|手指)[^。！？\n]{0,36}(?:灰|黑|脏)[\s\S]{0,100}(?:手机|屏幕)[^。！？\n]{0,50}(?:黑印|留下|蹭|指纹|印)",
    r"(?:外卖员|骑手|快递员|他|她)[\s\S]{0,120}(?:往里看|往屋里看|往房间看|看了(?:我)?一眼|瞥了(?:我)?一眼)[\s\S]{0,100}(?:屋里|房间|桌上|地上)[^。！？\n]{0,60}(?:乱|快餐盒|外卖盒|外卖袋|垃圾|没收)",
    r"(?:屋里|房间|桌上|地上)[^。！？\n]{0,60}(?:乱|快餐盒|外卖盒|外卖袋|垃圾|没收)[\s\S]{0,100}(?:外卖员|骑手|快递员|他|她)[^。！？\n]{0,40}(?:往里看|往屋里看|往房间看|看了(?:我)?一眼|瞥了(?:我)?一眼)",
]
PRIVATE_ROUGH_TEXTURE_TERMS = [
    "湿袖口",
    "袖口还是潮",
    "袖口",
    "裤腿",
    "裤管",
    "裤子也是潮",
    "湿拖鞋",
    "拖鞋",
    "小滩水",
    "盆",
    "接水",
    "漏水",
    "热水器",
    "滴滴答答",
    "水龙头",
]
AMBIENT_ENDING_PATTERNS = [
    r"(空调|外机|风扇|雨|灯|屏幕|手机|机器|冰箱)[^。！？\n]{0,16}(嗡|响|亮|暗|黑|震)[^。！？\n]{0,8}[。！？]?$",
    r"^(嗡|嗡嗡|嗡嗡嗡|滴|滴滴|哗啦|呼呼)[。！？]?$",
]
MATERIAL_ECHO_TERMS = [
    "奥美拉唑还剩最后一片",
    "明天记得买",
    "Type-C",
    "空调外机还在响",
    "空调外机一直响",
    "空调外机嗡嗡",
    "窗外的空调外机一直响着",
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
# Fragment-slate diagnostics remain observable warnings. Their lexical/window
# heuristics are useful review lenses but are not universal draft-gate quotas.
DRAFT_GATE_RULE_PREFIXES = (
    "缺少标题",
    "标题标签泄漏",
    "来源身份声明",
    "复制重叠风险",
    "题面诊断型标题",
    "标准日寄完整文章篇幅偏短",
    "标准日寄完整文章篇幅缓冲不足",
    "标准日寄完整文章过满",
    "单主题词密度偏高",
    "题面链条过于完整",
    "社交动态库存式开头",
    "旧记录私密考古链",
    "评论链公式化转述",
    "AI二元解释句式",
    "提示词报幕式对话",
    "AI解释腔",
    "AI平行解释模板",
    "AI自我注解",
    "AI变量代称",
    "AI文艺解释面",
    "字幕式明喻解释",
    "AI伪口语",
    "AI完整结构",
    "破折号解释连接",
    "破折号稀有连接",
    "无依据具体地名",
    "无依据具体地标",
    "无依据游戏角色细节",
    "无依据当前职场身份",
    "无依据工作后果链",
    "无依据家庭身份",
    "日常对话引号",
    "对话接力过密",
    "游戏复盘细节",
    "Offer具体化编造",
    "AI治疗式人类化",
    "反AI参考污染",
    "背景展示堆砌",
    "具体纹理堆叠过密",
    "疾病病例报告闭环",
    "疾病身体证明过密",
    "社交拒绝室内冷感过密",
    "社交拒绝纹理替代后果不足",
    "社交拒绝普通回复假后果",
    "社交拒绝群聊假后果",
    "社交拒绝编剧化回礼",
    "社交拒绝礼貌闭合",
    "社交拒绝私密转账假后果",
    "社交拒绝无关后果替代",
    "社交拒绝后果过度生长",
    "叙述人称滑移",
    "标准日寄提示物标题闭环",
    "标准日寄句号网格",
    "逗号密度过高",
    "行末逗号比例",
    "节奏过度均匀",
    "孤立中文标点",
    "断裂过碎",
    "标准日寄行数缓冲异常",
    "标准日寄长行缓冲不足",
    "标准日寄长行过密",
    "标准日寄短行网格",
    "短行诗化表面",
    "短体裁完整度不足",
    "短体裁整齐散文",
    "短体裁句号网格",
    "短体裁题面日期标题",
    "短体裁修复堆新素材",
    "短真诚当前动作锚点不足",
    "短真诚题面物件过早",
    "短真诚标题物件闭环",
    "短真诚小小说闭合",
    "短体裁局部材料回环",
    "短体裁误扩成标准日寄",
    "无依据重大家庭变故",
)
DRAFT_GATE_RULE_NAMES: set[str] = {"呼吸点缺失"}

STANDARD_DIARY_FORMAL_MIN_CHARS = 650
STANDARD_DIARY_ATTEMPT_MIN_CHARS = 300
STANDARD_DIARY_ATTEMPT_MIN_LINES = 12
STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS = 850
STANDARD_DIARY_PREFERRED_TARGET_MIN_CHARS = 900
STANDARD_DIARY_DRAFT_OVERFULL_CHARS = 1350
VALID_GENRES = {"standard", "sincere", "micro-hope", "surreal"}
FORCED_GENRE: str | None = None


def set_forced_genre(genre: str | None) -> None:
    global FORCED_GENRE
    if not genre:
        FORCED_GENRE = None
        return
    normalized = genre.strip().lower()
    aliases = {
        "standard-diary": "standard",
        "standard_diary": "standard",
        "microhope": "micro-hope",
        "micro_hope": "micro-hope",
        "surreal-literary": "surreal",
        "surreal_literary": "surreal",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in VALID_GENRES:
        raise ValueError(f"unsupported genre: {genre}")
    FORCED_GENRE = normalized


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
                "正式盲评稿必须是完整文章，第一行必须是标题。按正文完成后的标题模型选择：可用“日寄”，但不要把它当作 universal default。",
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
    not_prefix = r"(?<!是)不是"
    patterns = [
        re.compile(rf"{not_prefix}[^，。！？\n]{{1,28}}[,，]?(?:而|只|也|这|那)?(?:才)?是"),
        re.compile(rf"{not_prefix}[^，。！？\n]{{1,28}}[,，]?(?:就是|只是)"),
        re.compile(rf"{not_prefix}[^，。！？\n]{{1,28}}[,，](?:我|你|他|她|它)?(?:就是|只是|才是|是)"),
        re.compile(rf"{not_prefix}[^。！？\n]{{1,28}}[。！？]\s*(?:是|就是|只是|而是|才是)"),
        re.compile(rf"{not_prefix}[^。！？\n]{{1,28}}[。！？]\s*(?:我|你|他|她|它)?(?:是|就是|只是|而是|才是)"),
        re.compile(r"其实不是[,，]?(?:好像|就是|只是|而是|是)"),
        re.compile(r"像[^。！？\n]{1,32}其实不是"),
    ]
    matches = [
        (line_number, line)
        for line_number, line in enumerate(lines, start=1)
        if any(pattern.search(line) for pattern in patterns)
    ]
    for index in range(len(lines) - 1):
        left = lines[index].strip()
        right = lines[index + 1].strip()
        if (
            re.search(rf"{not_prefix}[^。！？\n]{{1,28}}[，,。！？]?$", left)
            and re.match(r"^(?:我|你|他|她|它)?(?:而是|是|就是|只是|这是|那是|才是)[^。！？\n]{1,40}", right)
        ):
            matches.append((index + 1, f"{left} / {right}"))
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


PROMPT_PERFORMING_DIALOGUE_TERMS = [
    "大学",
    "学校",
    "小吃街",
    "后面",
    "以前",
    "老家",
    "北京",
    "上海",
    "深圳",
    "杭州",
    "上班",
    "公司",
    "大厂",
    "计算机",
    "程序员",
    "工资",
    "月薪",
    "不少钱",
    "年轻人",
    "出去闯",
]
PROMPT_PERFORMING_SPEAKER_TERMS = [
    "问我",
    "问了一句",
    "问",
    "他说",
    "她说",
    "老板",
    "摊主",
    "卖瓜",
    "店员",
    "收银员",
    "司机",
    "路人",
    "客户",
]
PROMPT_PERFORMING_SUCCESS_TERMS = [
    "北京",
    "上海",
    "深圳",
    "杭州",
    "上班",
    "公司",
    "大厂",
    "计算机",
    "程序员",
    "一个月",
    "月薪",
    "工资",
    "不少钱",
    "新车",
    "买了台",
]
PROMPT_PERFORMING_RELATION_TERMS = ["儿子", "女儿", "孩子", "家里"]


def prompt_performing_dialogue_hits(lines: list[str]) -> list[tuple[int, str]]:
    """Find dialogue that exists mainly to deliver prompt/background facts."""
    hits: list[tuple[int, str]] = []
    seen: set[tuple[int, str]] = set()
    identity_probe = re.compile(
        r"(?:问我|问了一句|问|他说|她说|老板|摊主|卖瓜|店员|收银员|司机|路人|客户)"
        r"[^。！？\n]{0,24}(?:你)?是不是[^。！？\n]{1,42}"
    )
    bare_probe = re.compile(r"(?:你)?是不是[^。！？\n]{1,36}就是[^。！？\n]{1,36}")
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        has_probe = identity_probe.search(stripped) or bare_probe.search(stripped)
        if has_probe and any(term in stripped for term in PROMPT_PERFORMING_DIALOGUE_TERMS):
            key = (index + 1, stripped)
            if key not in seen:
                hits.append(key)
                seen.add(key)
        window = "\n".join(lines[max(0, index - 1) : min(len(lines), index + 2)])
        if (
            any(term in window for term in PROMPT_PERFORMING_RELATION_TERMS)
            and sum(1 for term in PROMPT_PERFORMING_SUCCESS_TERMS if term in window) >= 2
            and any(term in window for term in PROMPT_PERFORMING_SPEAKER_TERMS)
        ):
            key = (index + 1, stripped)
            if key not in seen:
                hits.append(key)
                seen.add(key)
    return hits


def check_prompt_performing_dialogue(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in prompt_performing_dialogue_hits(lines):
        findings.append(
            Finding(
                "warning",
                "提示词报幕式对话",
                line_number,
                clean_excerpt(line),
                "陌生人/摊贩/司机/店员的口语不能替题面交代学校、城市、职业、工资或成功对比。把这类身份探问压低成一个粗糙侧面，并让付款、物件、脏手、身体噪音、路线或失败回复承担后果。",
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
    literal_seen_context = re.compile(
        rf"(?:{'|'.join(map(re.escape, LITERAL_SEEN_SUBJECTS))})[^。！？\n]{{0,24}}(?:没|没有|根本没|根本就没|不)?被看见"
    )
    for line_number, line in enumerate(lines, start=1):
        for term in THERAPEUTIC_HUMANIZER_TERMS:
            if term in line:
                if speaker_context.search(line):
                    continue
                if term == "被看见" and literal_seen_context.search(line):
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


def meta_ai_topic_hits(text: str) -> list[str]:
    hits = [term for term in META_AI_TOPIC_TERMS if term in text]
    ai_count = len(re.findall(r"\b(?:AI|ai|GPT|gpt)\b|人工智能|大模型", text))
    if ai_count >= 3:
        hits.append(f"ai_topic_count={ai_count}")
    return hits


def check_meta_ai_topic_contamination(findings: list[Finding], text: str) -> None:
    hits = meta_ai_topic_hits(text)
    if not hits:
        return
    findings.append(
        Finding(
            "warning",
            "反AI参考污染",
            0,
            ", ".join(hits[:6]),
            "生成稿高风险：反AI规则里的AI/识别/生成词被吸收到正文主题。除非用户明确要求或场景有原文锚点，删除AI/GPT/识别文章/模型写作话题，换成本日自然产生的物、身体、钱、路线、社交或屏幕表面。",
        )
    )


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


def check_literary_simile_caption(findings: list[Finding], lines: list[str]) -> None:
    caption_patterns = [
        re.compile(r"(?:脑子里|心里|那句话|这句话|消息|简历|人生|命运|裂缝|下午|沉默|孤独|焦虑|压力|屏幕)[^。！？\n]{0,24}像[^。！？\n]{2,36}"),
        re.compile(r"像一(?:颗|根|道|张|块|条|口|层)[^。！？\n]{1,18}(?:钉子|针|刺|井|表|网|墙|裂缝|伤口|洞|锁)"),
    ]
    for line_number, line in enumerate(lines, start=1):
        if any(pattern.search(line) for pattern in caption_patterns):
            findings.append(
                Finding(
                    "warning",
                    "字幕式明喻解释",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：抽象压力后接漂亮明喻，容易像模型给画面加字幕。保留实际物、对话、身体或付款后果；删掉帮读者解释感受的比喻句。",
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


def unsupported_game_term_present(term: str, line: str) -> bool:
    if term == "泉水":
        if "矿泉水" in line:
            return False
        return "泉水" in line and any(context in line for context in GAME_CONTEXT_TERMS)
    if term == "下路":
        if "下路线" in line:
            return False
        if term not in line:
            return False
        return bool(
            re.search(
                r"下路[^。！？\n]{0,12}(?:送|被抓|对线|一塔|二塔|兵线|射手|辅助|AD|adc|队友|经济|压线|崩|炸)",
                line,
            )
            or any(context in line for context in GAME_CONTEXT_TERMS)
        )
    if term in {"ad", "AD"}:
        return bool(re.search(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", line))
    return term in line


def unsupported_family_identity_present(term: str, line: str) -> bool:
    for match in re.finditer(re.escape(term), line):
        prefix = line[: match.start()]
        suffix = line[match.end() :]
        nearby_prefix = prefix[-28:]
        nearby_suffix = suffix[:40]

        if term == "太太" and match.start() > 0 and line[match.start() - 1] in {"老", "老太"}:
            continue

        if any(cue in nearby_prefix for cue in THIRD_PERSON_SPEECH_CUES):
            continue

        if term in {"我儿子", "我女儿", "我家孩子"}:
            starts_as_quote = re.match(r'^\s*["“「『]?\s*' + re.escape(term), line) is not None
            has_third_person_attribution = re.search(
                r'["”」』][^。！？\n]{0,30}(?:'
                + "|".join(map(re.escape, THIRD_PERSON_ATTRIBUTION_CUES))
                + r")",
                nearby_suffix,
            )
            if starts_as_quote and has_third_person_attribution:
                continue

        if term in {"老婆", "妻子", "媳妇", "太太"} and re.search(
            r"(?:" + "|".join(map(re.escape, THIRD_PERSON_ATTRIBUTION_CUES)) + r")(?:的)?$",
            nearby_prefix,
        ):
            continue

        return True
    return False


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
            if unsupported_game_term_present(term, line):
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
        for pattern in UNSUPPORTED_LANDMARK_PATTERNS:
            if pattern.search(line):
                findings.append(
                    Finding(
                        "warning",
                        "无依据具体地标",
                        line_number,
                        clean_excerpt(line),
                        "生成稿高风险：不要凭空发明山名、校门方位、具体饭店/烧烤摊来制造大学旧事真实感。除非用户或语料锚点支持，降级为学校门口、那家店、以前吃饭的地方，或让记忆通过动作/付款/回复后果出现。",
                    )
                )
                break
        for term in UNSUPPORTED_FAMILY_IDENTITY_TERMS:
            if unsupported_family_identity_present(term, line):
                findings.append(
                    Finding(
                        "warning",
                        f"无依据家庭身份: {term}",
                        line_number,
                        clean_excerpt(line),
                        "生成稿高风险：语料不支持把叙述者默认写成已婚、有配偶或有子女。送外卖、家庭、父母可以出现，但不要把提示里的职业/压力改写成另一个人的婚育传记；除非用户明确提供，删除或降级为父母/朋友/室友/路人关系。",
                    )
                )
                break


MAJOR_FAMILY_LOSS_PATTERNS = [
    re.compile(r"(?:我妈|妈妈|母亲)[^。！？\n]{0,18}(?:不在了|去世|过世|没了|走了)"),
    re.compile(r"(?:不在了|去世|过世|没了|走了)[^。！？\n]{0,18}(?:我妈|妈妈|母亲)"),
]
PRONOUN_MAJOR_FAMILY_LOSS_PATTERNS = [
    re.compile(r"她[^。！？\n]{0,18}(?:不在了|去世|过世|没了|(?<!搬)走了)"),
    re.compile(r"(?:不在了|去世|过世|没了|(?<!搬)走了)[^。！？\n]{0,18}她"),
]
LOCAL_MOTHER_CONTEXT_TERMS = ("我妈", "妈妈", "母亲")


def check_major_family_status_fabrication(findings: list[Finding], lines: list[str]) -> None:
    joined = "\n".join(lines)
    family_context = any(term in joined for term in ("我妈", "妈妈", "母亲", "母亲节", "吃了没有", "吃了吗"))
    if not family_context:
        return
    for line_number, line in enumerate(lines, start=1):
        local_window = "\n".join(lines[max(0, line_number - 6) : min(len(lines), line_number + 3)])
        explicit_loss = any(pattern.search(line) for pattern in MAJOR_FAMILY_LOSS_PATTERNS)
        pronoun_loss = (
            any(pattern.search(line) for pattern in PRONOUN_MAJOR_FAMILY_LOSS_PATTERNS)
            and any(term in local_window for term in LOCAL_MOTHER_CONTEXT_TERMS)
        )
        if explicit_loss or pronoun_loss:
            findings.append(
                Finding(
                    "warning",
                    "无依据重大家庭变故",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：不要为了修复短真诚厚度或情感重量，凭空写母亲去世、不在、重大失联等关系事实。除非用户明确给出，把它降级为未回、说不出口、电话没打通、手上动作停住等当前可见后果。",
                )
            )


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


def _has_any_marker(text: str, markers: list[str]) -> bool:
    return any(marker in text for marker in markers)


def _is_third_person_office_surface(lines: list[str], index: int) -> bool:
    window = "".join(lines[max(0, index - 2) : min(len(lines), index + 3)])
    work_chain_terms = ["项目", "交付", "月底", "请假", "病假", "扣钱", "考勤", "打卡"]
    work_authority_terms = ["领导", "主管", "组长", "经理"]
    if _has_any_marker(window, work_chain_terms) and _has_any_marker(window, work_authority_terms):
        return False
    if not _has_any_marker(window, THIRD_PERSON_OFFICE_SURFACE_MARKERS):
        return False
    return not _has_any_marker(lines[index], FIRST_PERSON_OFFICE_SURFACE_MARKERS)


def current_office_persona_hits(text: str) -> list[str]:
    lines = text.splitlines()
    hits: list[str] = []
    high_specific: list[str] = []
    for index, line in enumerate(lines):
        for term in CURRENT_OFFICE_PERSONA_TERMS:
            if term not in line:
                continue
            if _is_third_person_office_surface(lines, index):
                continue
            hits.append(term)
            if term in CURRENT_OFFICE_HIGH_SPECIFIC_TERMS:
                high_specific.append(term)
    hits = list(dict.fromkeys(hits))
    high_specific = list(dict.fromkeys(high_specific))
    if len(set(hits)) >= 4 or high_specific:
        return hits[:8]
    return []


def check_current_office_persona(findings: list[Finding], text: str) -> None:
    hits = current_office_persona_hits(text)
    if not hits:
        return
    findings.append(
        Finding(
            "warning",
            "无依据当前职场身份",
            0,
            f"terms={hits}",
            "生成稿高风险：默认当前日期/无用户事实时，不要把叙述者写成办公室职员、公司同事、领导/KPI/营收叙事。公司和同事在语料中有阶段/人称边界；若无明确日期或用户材料，降级为招聘、旧同事、他人公司、屏幕消息或普通生活场景。",
        )
    )


def work_consequence_chain_hits(lines: list[str]) -> list[str]:
    hits: list[str] = []
    for index, line in enumerate(lines):
        if _is_third_person_office_surface(lines, index):
            continue
        for pattern in WORK_CONSEQUENCE_CHAIN_PATTERNS:
            if pattern.search(line):
                hits.append(clean_excerpt(line))
                break

    for index in range(len(lines)):
        window_lines = lines[max(0, index - 1) : min(len(lines), index + 2)]
        if not window_lines:
            continue
        if all(_is_third_person_office_surface(lines, i) for i in range(max(0, index - 1), min(len(lines), index + 2))):
            continue
        window = "".join(window_lines)
        present = {term for term in WORK_CONSEQUENCE_CHAIN_TERMS if term in window}
        has_work_authority = any(term in present for term in {"领导", "主管", "组长", "经理"})
        has_leave_penalty = {"请假", "扣钱"}.issubset(present) or {"病假", "扣钱"}.issubset(present)
        has_deadline_package = any(term in present for term in {"周一", "月底", "项目", "交付", "周报", "文件", "表格", "汇报"}) and any(
            term in present for term in {"领导", "主管", "组长", "经理", "公司", "上班", "开会"}
        )
        if len(present) >= 3 and (has_work_authority or has_leave_penalty or has_deadline_package):
            hits.append(clean_excerpt(window))

    return list(dict.fromkeys(hits))[:5]


def check_work_consequence_chain(findings: list[Finding], lines: list[str]) -> None:
    hits = work_consequence_chain_hits(lines)
    if not hits:
        return
    findings.append(
        Finding(
            "warning",
            "无依据工作后果链",
            0,
            " | ".join(hits),
            "生成稿高风险：为了给身体/疾病/现实压力找后果而凭空写领导、请假、半天假请不下来、调休/排班、扣钱、周一交文件、考勤或当前上班身份。除非用户提供，降级为屏幕表面、旧同事/他人公司、普通群消息、邻居/店员接触、路线或身体实际阻碍。",
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
            if matched.endswith("块") and following and is_chinese_word_char(following) and following not in {"钱", "五", "多", "半"}:
                continue
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
    style = detect_style(text)
    present = [term for term in HIGH_FREQUENCY_TERMS if term in text]
    if style != "standard":
        if chinese_len(text) >= 250 and len(present) < 2:
            findings.append(
                Finding(
                    "warning",
                    "短体裁连接信号偏少",
                    0,
                    f"style={style}, present={present}",
                    "短真诚/微小希望/超现实不按标准日寄连接词配额修；只检查是否完全变成静态抒情。优先让动作或记忆自然转动，不要硬撒连接词。",
                )
            )
        return
    if len(present) < 5:
        findings.append(
            Finding(
                "warning",
                "高频词覆盖不足",
                0,
                f"present={present}",
                "只作关系诊断：检查是否缺少真实的思想或动作转向；片段可以通过联想、回声、记忆或直接跳接保持连贯，不要为了覆盖词表硬撒连接词。",
            )
        )


def check_short_genre_polished_minimalism(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style == "standard":
        return
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body_chars = chinese_len("\n".join(visible_lines))
    if body_chars < 300 or len(visible_lines) < 18:
        return
    lengths = [chinese_len(line) for line in visible_lines]
    long_lines = sum(1 for length in lengths if length >= 24)
    short_drops = sum(
        1
        for line, length in zip(visible_lines, lengths)
        if 1 <= length <= 8 and re.search(r"[。！？]$", line)
    )
    mean_length = sum(lengths) / len(lengths)
    variance = sum((length - mean_length) ** 2 for length in lengths) / len(lengths)
    line_stdev = variance ** 0.5
    if long_lines == 0 and short_drops <= 1 and line_stdev <= 5.5:
        findings.append(
            Finding(
                "warning",
                "短体裁整齐散文",
                0,
                f"style={style}, body_chars={body_chars}, body_lines={len(visible_lines)}, long_lines={long_lines}, short_drops={short_drops}, line_stdev={line_stdev:.2f}",
                "短真诚/微小希望可以短，但不能变成每行长度相近的抛光散文。用现有动作或记忆制造不均匀呼吸：合并一两处为较长笨拙动作/口头句，保留一处很短的失败、沉默或事实后撤；不要拉长成标准日寄，也不要为指标硬切行。",
            )
        )


def check_short_genre_period_grid(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style == "standard":
        return
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 520 or len(visible_lines) < 28:
        return
    period_count = body.count("。")
    comma_count = body.count("，") + body.count(",")
    period_per_1k = period_count / body_chars * 1000 if body_chars else 0.0
    line_period_ratio = sum(1 for line in visible_lines if line.endswith("。")) / max(1, len(visible_lines))
    time_glue_hits = {
        term: body.count(term)
        for term in ("后来", "已经", "当时")
        if body.count(term)
    }
    if period_per_1k < 45 and line_period_ratio < 0.52:
        return
    if period_count < 24 and sum(time_glue_hits.values()) < 4:
        return
    findings.append(
        Finding(
            "warning",
            "短体裁句号网格",
            0,
            f"style={style}, body_chars={body_chars}, body_lines={len(visible_lines)}, periods={period_count}, commas={comma_count}, period_per_1k={period_per_1k:.1f}, line_period_ratio={line_period_ratio:.2f}, time_glue={time_glue_hits}",
            "短真诚/微小希望不能写成一排封闭句号和时间胶水。重写成4-7个呼吸簇：让动作或回复拖到下一行，用少量行末逗号承接同一动作；删弱`后来/已经/当时`这类顺序胶水，让物件、身体或对话失误自然转场。",
        )
    )


def check_short_genre_underbuilt_complete_article(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style == "standard":
        return
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 180 or len(visible_lines) < 12:
        return
    lengths = [chinese_len(line) for line in visible_lines]
    long_lines = sum(1 for length in lengths if length >= 24)
    short_lines = sum(1 for length in lengths if length <= 12)
    short_line_ratio = short_lines / max(1, len(lengths))
    underbuilt = body_chars < 520
    line_grid = (
        ((body_chars < 760 and len(visible_lines) >= 18) or len(visible_lines) >= 55)
        and long_lines < 3
        and short_line_ratio >= 0.45
    )
    if not underbuilt and not line_grid:
        return
    findings.append(
        Finding(
            "warning",
            "短体裁完整度不足",
            0,
            f"style={style}, body_chars={body_chars}, body_lines={len(visible_lines)}, long_lines={long_lines}, short_line_ratio={short_line_ratio:.2f}",
            "短真诚/微小希望可以短，但不能像提纲或压缩小品。保留短体裁，不要扩成标准日寄；增加一组当前实际动作、笨拙回复或生活打断，并删弱一个提示物件/记忆证明，避免把所有题面素材保留下来。",
        )
    )


def check_short_genre_prose_block_compression(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style == "standard":
        return
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 520 or not visible_lines:
        return
    lengths = [chinese_len(line) for line in visible_lines]
    mean_line = sum(lengths) / max(1, len(lengths))
    first_twenty = visible_lines[:20]
    comma_ratio = (sum(1 for line in first_twenty if line.endswith("，")) / len(first_twenty)) if first_twenty else 0.0
    if len(visible_lines) <= 20 or mean_line >= 32 or comma_ratio < 0.08:
        findings.append(
            Finding(
                "warning",
                "短体裁散文块压缩",
                0,
                f"style={style}, body_chars={body_chars}, body_lines={len(visible_lines)}, mean_line={mean_line:.1f}, early_comma_ratio={comma_ratio:.2f}",
                "短真诚/微小希望不是顺滑散文段。保留短体裁，但要改成4-7个不均匀呼吸簇：有几条较长笨拙动作/记忆线，也有短事实后撤；不要把每个段落写成完整解释句。",
            )
        )


def check_short_genre_diagnostic_date_title(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style == "standard":
        return
    title, _ = split_title_and_content_lines(lines)
    normalized = re.sub(r"[\s#]+", "", title)
    if re.search(r"(?:母亲节|五月十二日|5月12日|五月十二|520)", normalized):
        findings.append(
            Finding(
                "warning",
                "短体裁题面日期标题",
                0,
                normalized,
                "短真诚/微小希望标题不能把提示日期或节日直接端出来。选当前动作、错误物件、笨拙回复或不服务主题的生活残留作标题。",
            )
        )


def short_genre_repair_stuffing_groups(text: str) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for group, terms in SINCERE_REPAIR_STUFFING_FAMILIES.items():
        hits = [term for term in terms if term in text]
        if hits:
            groups[group] = hits
    return groups


def short_genre_repair_stuffing_hits(text: str) -> list[str]:
    return [
        term
        for terms in short_genre_repair_stuffing_groups(text).values()
        for term in terms
    ]


def check_short_genre_repair_stuffing(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style not in {"sincere", "micro-hope"}:
        return
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 850:
        return
    groups = short_genre_repair_stuffing_groups(body)
    hits = [term for terms in groups.values() for term in terms]
    if len(groups) < 3 and len(hits) < 5:
        return
    findings.append(
        Finding(
            "warning",
            "短体裁修复堆新素材",
            0,
            f"style={style}, body_chars={body_chars}, groups={groups}",
            "短真诚/微小希望修复不能靠新增外卖、食品、礼物包、媒体、游戏、路线或背景包来凑厚度和长行。保留短体裁，在已选对象、消息、房间、身体、记忆事实内重排动作、回复和事实后撤；必要时删一个新素材包。",
            )
        )


SHORT_GENRE_RELATION_EXPOSITION_TERMS = [
    "平时",
    "每次",
    "去年",
    "有时候",
    "小时候",
    "上次",
    "那时候",
    "转钱",
    "支付宝",
    "其实想说",
    "就没什么好说的",
]


def check_short_genre_standard_expansion_drift(findings: list[Finding], lines: list[str], text: str) -> None:
    style = detect_style(text)
    if style not in {"sincere", "micro-hope"}:
        return
    title, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 850 or len(visible_lines) < 55:
        return
    exposition_hits = [term for term in SHORT_GENRE_RELATION_EXPOSITION_TERMS if term in body]
    stuffing_groups = short_genre_repair_stuffing_groups(body)
    family_context = sincere_mother_surface("\n".join([title, body])) or any(
        term in body for term in ("我妈", "妈妈", "母亲", "母亲节")
    )
    if not family_context:
        return
    drift_score = 0
    reasons: list[str] = []
    if body_chars >= 900:
        drift_score += 1
        reasons.append(f"body_chars={body_chars}")
    if len(visible_lines) >= 65:
        drift_score += 2
        reasons.append(f"body_lines={len(visible_lines)}")
    if len(exposition_hits) >= 3:
        drift_score += 1
        reasons.append(f"relation_exposition={exposition_hits[:6]}")
    if len(stuffing_groups) >= 2:
        drift_score += 1
        reasons.append(f"new_material_groups={list(stuffing_groups)[:4]}")
    if drift_score < 3:
        return
    findings.append(
        Finding(
            "warning",
            "短体裁误扩成标准日寄",
            0,
            json.dumps(
                {
                    "style": style,
                    "body_chars": body_chars,
                    "body_lines": len(visible_lines),
                    "exposition_hits": exposition_hits[:8],
                    "stuffing_groups": stuffing_groups,
                    "reasons": reasons,
                },
                ensure_ascii=False,
            ),
            "短真诚/微小希望修复不能因为全局比例或行数压力扩成标准日寄。锁定原体裁：删关系说明和新素材包，回到一个当前动作、一个记忆漏点、一个笨拙回复或事实后撤；不要用更多人物、转账、旧年说明、邻居功能戏来制造完整感。",
        )
    )


def short_genre_present_action_anchor_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    """Detect short sincere drafts that start from proof-memory instead of today's action."""
    style = detect_style(text)
    if style not in {"sincere", "micro-hope"}:
        return None
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 220 or len(visible_lines) < 12:
        return None

    family_hits = [term for term in SINCERE_MOTHER_SUBJECT_MARKERS if term in body]
    message_hits = [term for term in SINCERE_HOLIDAY_OR_MESSAGE_MARKERS if term in body]
    care_hits = [term for term in SINCERE_CARE_MEMORY_MARKERS if term in body]
    if not family_hits or not (message_hits or len(care_hits) >= 2):
        return None

    proof_terms = (
        SINCERE_MOTHER_SUBJECT_MARKERS
        + SINCERE_HOLIDAY_OR_MESSAGE_MARKERS
        + SINCERE_CARE_MEMORY_MARKERS
        + SHORT_GENRE_MEMORY_ARC_TERMS
    )
    proof_indices = [
        index
        for index, line in enumerate(visible_lines)
        if any(term in line for term in proof_terms)
    ]
    first_proof_index = min(proof_indices) if proof_indices else 0
    before_proof = "\n".join(visible_lines[:first_proof_index])
    early_window = "\n".join(visible_lines[: max(3, min(len(visible_lines), first_proof_index + 2))])

    anchor_hits_before = [
        term for term in SHORT_GENRE_PRESENT_ANCHOR_TERMS if term in before_proof
    ]
    grouped_before = {
        group: [term for term in terms if term in before_proof]
        for group, terms in SHORT_GENRE_PRESENT_ANCHOR_GROUPS.items()
        if any(term in before_proof for term in terms)
    }
    anchor_hits_early = [term for term in SHORT_GENRE_PRESENT_ANCHOR_TERMS if term in early_window]
    all_anchor_hits = [term for term in SHORT_GENRE_PRESENT_ANCHOR_TERMS if term in body]
    memory_hits = [term for term in SHORT_GENRE_MEMORY_ARC_TERMS if term in body]

    risk_score = 0
    reasons: list[str] = []
    if not anchor_hits_before:
        risk_score += 2
        reasons.append("no_present_anchor_before_family_proof")
    if first_proof_index <= 2:
        risk_score += 1
        reasons.append(f"proof_starts_too_early=line_index:{first_proof_index}")
    if len(memory_hits) >= 3 and message_hits:
        risk_score += 1
        reasons.append(f"memory_message_chain={memory_hits[:4]}")
    if not anchor_hits_early:
        risk_score += 1
        reasons.append("early_window_has_no_practical_interrupt")
    elif not grouped_before and all_anchor_hits:
        risk_score += 1
        reasons.append("practical_interrupt_arrives_after_proof")

    if risk_score < 3:
        return None
    return {
        "style": style,
        "body_chars": body_chars,
        "body_lines": len(visible_lines),
        "risk_score": risk_score,
        "reasons": reasons[:6],
        "anchor_hits_before": anchor_hits_before[:6],
        "anchor_hits_total": all_anchor_hits[:8],
        "family_hits": family_hits[:4],
        "message_hits": message_hits[:4],
        "care_hits": care_hits[:5],
    }


def check_short_genre_present_action_anchor(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = short_genre_present_action_anchor_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "短真诚当前动作锚点不足",
            0,
            json.dumps(risk, ensure_ascii=False),
            "短真诚/微小希望生成稿高风险：母亲、节日、鸡蛋、雨衣、未发消息等证明链太早接管文章。正式生成稿里这不是局部补丁问题；应整篇换源头，重选标题和入口，只保留一个记忆碎片或屏幕碎片作为漏出来的压力。先让今天一个不靠题面物件成立的动作坏掉：水槽/门口/邻居/回复/身体/房间小事故改变下一步；回忆只能从这个动作里漏出来，不要从回忆直接证明愧疚。",
        )
    )


def short_genre_prompt_prop_too_early_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    """Detect short sincere drafts where prompt props take over the opening.

    This is narrower than missing a present-action anchor. A draft may technically
    begin with a sink, bowl, phone, or room action, but still turn that action into
    a runway for every supplied mother-memory prop within a few lines.
    """
    style = detect_style(text)
    if style not in {"sincere", "micro-hope"}:
        return None
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 260 or len(visible_lines) < 12:
        return None

    family_hits = [term for term in SINCERE_MOTHER_SUBJECT_MARKERS if term in body]
    message_hits = [term for term in SINCERE_HOLIDAY_OR_MESSAGE_MARKERS if term in body]
    care_hits = [term for term in SINCERE_CARE_MEMORY_MARKERS if term in body]
    if not family_hits or not (message_hits or len(care_hits) >= 2):
        return None

    proof_terms = (
        SINCERE_MOTHER_SUBJECT_MARKERS
        + SINCERE_HOLIDAY_OR_MESSAGE_MARKERS
        + SINCERE_CARE_MEMORY_MARKERS
        + SHORT_GENRE_MEMORY_ARC_TERMS
    )
    early_limit = min(len(visible_lines), 10)
    early_lines = visible_lines[:early_limit]
    proof_indices = [
        index
        for index, line in enumerate(early_lines)
        if any(term in line for term in proof_terms)
    ]
    if not proof_indices:
        return None
    first_proof_index = min(proof_indices)
    before_proof = "\n".join(visible_lines[:first_proof_index])
    grouped_before = {
        group: [term for term in terms if term in before_proof]
        for group, terms in SHORT_GENRE_PRESENT_ANCHOR_GROUPS.items()
        if any(term in before_proof for term in terms)
    }
    anchor_hits_before = [
        term for term in SHORT_GENRE_PRESENT_ANCHOR_TERMS if term in before_proof
    ]
    early_proof_terms = sorted({term for line in early_lines for term in proof_terms if term in line})

    risk_score = 0
    reasons: list[str] = []
    if first_proof_index <= 4:
        risk_score += 2
        reasons.append(f"proof_enters_opening=line_index:{first_proof_index}")
    if len(proof_indices) >= 3:
        risk_score += 1
        reasons.append(f"proof_line_count_first_10={len(proof_indices)}")
    if len(grouped_before) < 2:
        risk_score += 1
        reasons.append(f"anchor_group_count_before_proof={len(grouped_before)}")
    if len(anchor_hits_before) < 3:
        risk_score += 1
        reasons.append(f"anchor_hits_before_proof={anchor_hits_before[:4]}")
    if len(early_proof_terms) >= 4:
        risk_score += 1
        reasons.append(f"early_proof_terms={early_proof_terms[:6]}")

    if risk_score < 4:
        return None
    return {
        "style": style,
        "body_chars": body_chars,
        "body_lines": len(visible_lines),
        "risk_score": risk_score,
        "reasons": reasons[:6],
        "first_proof_index": first_proof_index,
        "early_proof_terms": early_proof_terms[:8],
        "anchor_groups_before_proof": grouped_before,
    }


def check_short_genre_prompt_prop_too_early(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = short_genre_prompt_prop_too_early_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "短真诚题面物件过早",
            0,
            json.dumps(risk, ensure_ascii=False),
            "短真诚/微小希望生成稿高风险：开头虽然有当前动作，但母亲、节日、鸡蛋、雨、未发消息等题面强物件过早接管，读者会看到按素材清单搭出的证明链。重写前8-12行：先让一个不靠题面成立的当前动作失败并改变下一步，再只漏入一个记忆/屏幕碎片；其余强物件后撤、合并或删除。",
        )
    )


SHORT_GENRE_STORY_OBJECT_TERMS = [
    "鸡蛋",
    "蛋壳",
    "塑料袋",
    "雨衣",
    "雨伞",
    "伞",
    "冰箱",
    "油",
    "碗",
    "米饭",
    "拖鞋",
    "裤子",
    "水印",
    "水龙头",
    "康乃馨",
    "朋友圈",
    "屏幕",
    "消息",
    "月亮",
    "月亮表情",
]

SHORT_GENRE_MEMORY_ARC_TERMS = [
    "小时候",
    "以前",
    "上次",
    "那时候",
    "当时",
    "下雨",
    "送我上学",
    "校门口",
    "回家",
]

SHORT_GENRE_MESSAGE_CLOSURE_TERMS = [
    "没发",
    "没有发",
    "没回",
    "没有回",
    "发送键",
    "发消息",
    "翻过去",
    "放下",
    "没有换",
    "还在",
]

SHORT_GENRE_PROMPT_PROP_TITLE_TERMS = [
    "鸡蛋",
    "蛋壳",
    "塑料袋",
    "雨衣",
    "雨伞",
    "康乃馨",
    "母亲节",
    "五月十二",
    "屏幕",
    "消息",
    "祝福",
]


def short_genre_main_prop_title_loop_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    """Detect short-genre drafts whose title turns a prompt prop into proof.

    The guard is intentionally narrow: a prop title is risky only when a
    mother/holiday/memory chain also appears and the title prop is echoed by the
    body or tail. Side-action titles such as sink, sleeve, door, or wrong reply
    should remain available.
    """
    style = detect_style(text)
    if style not in {"sincere", "micro-hope"}:
        return None
    title, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 260 or len(visible_lines) < 12:
        return None

    normalized_title = re.sub(r"[\s#《》「」『』“”\"'，。！？!?:：、]+", "", title)
    title_hits = [
        term for term in SHORT_GENRE_PROMPT_PROP_TITLE_TERMS if term in normalized_title
    ]
    if not title_hits:
        return None

    family_hits = [term for term in SINCERE_MOTHER_SUBJECT_MARKERS if term in body]
    message_hits = [term for term in SINCERE_HOLIDAY_OR_MESSAGE_MARKERS if term in body]
    care_hits = [term for term in SINCERE_CARE_MEMORY_MARKERS if term in body]
    memory_hits = [term for term in SHORT_GENRE_MEMORY_ARC_TERMS if term in body]
    closure_hits = [term for term in SHORT_GENRE_MESSAGE_CLOSURE_TERMS if term in body]
    if not family_hits or not (message_hits or len(care_hits) >= 2 or len(memory_hits) >= 2):
        return None

    tail = "\n".join(visible_lines[-8:])
    title_echo_count = max(body.count(term) for term in title_hits)
    title_tail_echo = any(term in tail for term in title_hits)

    proof_family_count = 0
    proof_family_count += 1 if message_hits else 0
    proof_family_count += 1 if len(care_hits) >= 2 else 0
    proof_family_count += 1 if len(memory_hits) >= 2 else 0
    proof_family_count += 1 if len(closure_hits) >= 1 else 0

    risk_score = 0
    reasons: list[str] = []
    if title_echo_count >= 2:
        risk_score += 2
        reasons.append(f"title_prop_echo_count={title_echo_count}")
    if title_tail_echo:
        risk_score += 1
        reasons.append("title_prop_tail_echo")
    if proof_family_count >= 3:
        risk_score += 2
        reasons.append(f"proof_family_count={proof_family_count}")
    elif proof_family_count == 2:
        risk_score += 1
        reasons.append("two_proof_families")
    if any(term in normalized_title for term in ("母亲节", "五月十二")):
        risk_score += 1
        reasons.append("date_or_holiday_title")

    if risk_score < 4:
        return None
    return {
        "style": style,
        "body_chars": body_chars,
        "body_lines": len(visible_lines),
        "title": normalized_title,
        "title_hits": title_hits[:4],
        "title_echo_count": title_echo_count,
        "title_tail_echo": title_tail_echo,
        "proof_family_count": proof_family_count,
        "family_hits": family_hits[:4],
        "message_hits": message_hits[:4],
        "care_hits": care_hits[:5],
        "memory_hits": memory_hits[:5],
        "closure_hits": closure_hits[:4],
        "reasons": reasons[:6],
    }


def check_short_genre_main_prop_title_loop(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = short_genre_main_prop_title_loop_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "短真诚标题物件闭环",
            0,
            json.dumps(risk, ensure_ascii=False),
            "短真诚/微小希望生成稿高风险：标题直接拿题面强物件，正文又让同一物件承接母亲/节日/未发消息/照料记忆并在尾部回收，容易读成一条被设计好的证明链。重选侧面动作或低状态把手作标题，正文保留一个记忆压力即可；如果标题物件必须保留，结尾不要再回到它。",
        )
    )


def short_genre_literary_story_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    """Return a conservative risk summary for polished short-genre story closure.

    This is intentionally a generated-draft warning, not an authorship claim.
    It targets the repeated failure where a short sincere piece becomes a clean
    memory story: one symbolic object, one mother-memory arc, one unsent message,
    and a tasteful ending that closes the title.
    """
    style = detect_style(text)
    if style == "standard":
        return None
    title, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 220 or len(visible_lines) < 12:
        return None

    title_key = title.lstrip("#").strip()
    title_key = re.sub(r"\s+", "", title_key)
    if len(title_key) > 6:
        title_key = ""

    family_hits = [term for term in SINCERE_MOTHER_SUBJECT_MARKERS if term in body]
    holiday_or_message_hits = [term for term in SINCERE_HOLIDAY_OR_MESSAGE_MARKERS if term in body]
    care_hits = [term for term in SINCERE_CARE_MEMORY_MARKERS if term in body]
    object_hits = [term for term in SHORT_GENRE_STORY_OBJECT_TERMS if term in body]
    memory_hits = [term for term in SHORT_GENRE_MEMORY_ARC_TERMS if term in body]
    closure_hits = [term for term in SHORT_GENRE_MESSAGE_CLOSURE_TERMS if term in body]
    tail = "\n".join(visible_lines[-8:])

    title_echo_count = body.count(title_key) if title_key else 0
    title_tail_echo = bool(title_key and title_key in tail)
    object_density = len(object_hits) / max(1, body_chars / 100)

    risk_score = 0
    reasons: list[str] = []
    if family_hits and (holiday_or_message_hits or len(care_hits) >= 2):
        risk_score += 2
        reasons.append("mother_message_memory")
    if len(memory_hits) >= 3:
        risk_score += 1
        reasons.append(f"linear_memory_terms={memory_hits[:4]}")
    if len(object_hits) >= 6 or object_density >= 1.35:
        risk_score += 1
        reasons.append(f"object_density={object_density:.2f}")
    if len(closure_hits) >= 2:
        risk_score += 1
        reasons.append(f"message_withholding={closure_hits[:4]}")
    if title_echo_count >= 3 or title_tail_echo:
        risk_score += 1
        reasons.append(f"title_echo_count={title_echo_count},tail={title_tail_echo}")
    if re.search(r"(?:我)?没有(?:换|回|发|点开)|(?:水印|拖鞋|鸡蛋|屏幕|消息)[^。！？\n]{0,18}还在", tail):
        risk_score += 1
        reasons.append("tasteful_tail_residue")

    if risk_score < 4:
        return None
    return {
        "style": style,
        "body_chars": body_chars,
        "body_lines": len(visible_lines),
        "risk_score": risk_score,
        "reasons": reasons[:6],
        "title": title_key,
    }


def check_short_genre_literary_story_closure(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = short_genre_literary_story_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "短真诚小小说闭合",
            0,
            json.dumps(risk, ensure_ascii=False),
            "短真诚/微小希望生成稿高风险：一个标题物件、母亲/记忆、未发消息和漂亮尾巴组成了完整小小说，盲评容易读成设计好的AI转写。不要加更多感官物件；删弱一个象征回环，加入已经在当天发生的笨拙回复、实际打断或不服务主题的生活残留，让结尾退到未完成动作而不是证明标题。",
        )
    )


LOCAL_PACKET_LOOP_FAMILIES = {
    "screen_message": ["手机", "屏幕", "亮", "消息", "通知", "朋友圈", "微信"],
    "chore_water_oil": ["碗", "水池", "水龙头", "油", "油渍", "洗洁精", "热水", "水壶"],
    "withheld_reply": ["没回", "没点", "倒扣", "翻过", "没打字", "还在"],
}


def family_hit_count(lines: list[str], terms: list[str]) -> int:
    return sum(1 for line in lines if any(term in line for term in terms))


def regex_count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text))


def short_genre_local_packet_loop_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    """Detect short-genre repair that repeats one local packet to satisfy shape."""
    style = detect_style(text)
    if style not in {"sincere", "micro-hope"}:
        return None
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 430 or len(visible_lines) < 28:
        return None

    opening = visible_lines[: max(8, len(visible_lines) // 3)]
    tail = visible_lines[-max(8, len(visible_lines) // 3) :]
    opening_text = "\n".join(opening)
    tail_text = "\n".join(tail)

    family_repeats: dict[str, dict[str, int]] = {}
    risk_score = 0
    reasons: list[str] = []
    for family, terms in LOCAL_PACKET_LOOP_FAMILIES.items():
        open_hits = family_hit_count(opening, terms)
        tail_hits = family_hit_count(tail, terms)
        total_hits = family_hit_count(visible_lines, terms)
        if open_hits >= 2 and tail_hits >= 2 and total_hits >= 5:
            family_repeats[family] = {
                "opening": open_hits,
                "tail": tail_hits,
                "total": total_hits,
            }
            risk_score += 1

    phone_light_count = regex_count(r"手机[^。！？\n]{0,8}亮", body)
    bowl_water_count = regex_count(r"(?:碗|水池|水龙头|油渍|洗洁精|水壶)[^。！？\n]{0,10}(?:还|泡|凉|黏|擦|响|挤)", body)
    withheld_count = regex_count(r"(?:没回|没点|倒扣|翻过|没打字|还在)", body)
    if phone_light_count >= 3:
        risk_score += 2
        reasons.append(f"phone_light_count={phone_light_count}")
    if bowl_water_count >= 6:
        risk_score += 2
        reasons.append(f"bowl_water_count={bowl_water_count}")
    if withheld_count >= 5:
        risk_score += 1
        reasons.append(f"withheld_count={withheld_count}")

    overlap_5 = len(char_ngram_set(opening_text, 5) & char_ngram_set(tail_text, 5))
    overlap_6 = len(char_ngram_set(opening_text, 6) & char_ngram_set(tail_text, 6))
    if overlap_5 >= 8 or overlap_6 >= 4:
        risk_score += 2
        reasons.append(f"early_tail_overlap_5={overlap_5},6={overlap_6}")

    if len(family_repeats) >= 2:
        risk_score += 1
        reasons.append(f"family_repeats={list(family_repeats)}")

    if risk_score < 4:
        return None
    return {
        "style": style,
        "body_chars": body_chars,
        "body_lines": len(visible_lines),
        "risk_score": risk_score,
        "family_repeats": family_repeats,
        "phone_light_count": phone_light_count,
        "bowl_water_count": bowl_water_count,
        "withheld_count": withheld_count,
        "early_tail_overlap_5": overlap_5,
        "early_tail_overlap_6": overlap_6,
        "reasons": reasons[:6],
    }


def check_short_genre_local_packet_loop(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = short_genre_local_packet_loop_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "短体裁局部材料回环",
            0,
            json.dumps(risk, ensure_ascii=False),
            "短真诚/微小希望修复高风险：同一组手机亮、消息、碗水油、未回复动作被拿来扩写尾部，像按检测项补稿。不要继续加同组细节；删除一轮重复包，换成会改变下一步动作的不同现实后果，或直接从新的当前动作重写。",
        )
    )


def check_connector_overuse(findings: list[Finding], text: str) -> None:
    style = detect_style(text)
    if style != "standard" or chinese_len(text) < 650:
        return
    counts = {term: text.count(term) for term in CONNECTOR_OVERUSE_TERMS}
    overused = {
        term: count
        for term, count in counts.items()
        if count >= 6 or (term in {"其实", "已经", "当时"} and count >= 5)
    }
    if overused:
        findings.append(
            Finding(
                "warning",
                "连接词胶水过量",
                0,
                json.dumps(overused, ensure_ascii=False),
                "生成稿高风险：同一连接词反复承担转场，会像模型在补口语感。删掉解释胶水，让场景靠物件、动作、对话、身体或屏幕表面跳过去。",
            )
        )


def standard_prompt_prop_title_loop_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    """Detect standard-diary drafts organized by one prompt prop.

    A concrete prop is not a problem by itself. It becomes risky when the title,
    opening, and tail all keep the same prop or prompt packet as the article's
    proof structure.
    """
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return None
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < STANDARD_DIARY_FORMAL_MIN_CHARS or len(visible_lines) < 30:
        return None

    normalized_title = re.sub(r"[\s#《》「」『』“”\"'，。！？!?:：、]+", "", title)
    title_hits = [
        term for term in STANDARD_PROMPT_PROP_TITLE_TERMS if term in normalized_title
    ]
    if not title_hits:
        return None

    surface = "\n".join([normalized_title, body])
    prompt_context_hits = [
        term for term in STANDARD_PROMPT_PROP_CONTEXT_TERMS if term in surface
    ]
    if len(prompt_context_hits) < 3:
        return None

    opening = "\n".join(visible_lines[:8])
    tail = "\n".join(visible_lines[-8:])
    title_echo_count = max(body.count(term) for term in title_hits)
    title_open_echo = any(term in opening for term in title_hits)
    title_tail_echo = any(term in tail for term in title_hits)
    secondary_hits = [
        term
        for term in STANDARD_PROMPT_PROP_SECONDARY_TERMS
        if term not in title_hits and term in body
    ]
    secondary_echo_count = sum(body.count(term) for term in secondary_hits)
    side_engine_lines = sum(
        1
        for line in visible_lines
        if any(term in line for term in OUTSIDE_CONTACT_TERMS)
        or any(term in line for term in EXPOSED_SOCIAL_CONSEQUENCE_TERMS)
        or any(term in line for term in ROUGH_SELF_DAMAGE_TERMS)
        or any(re.search(pattern, line) for pattern in ROUGH_SELF_DAMAGE_PATTERNS)
    )

    risk_score = 0
    reasons: list[str] = []
    if title_echo_count >= 4:
        risk_score += 3
        reasons.append(f"title_prop_echo_count={title_echo_count}")
    elif title_echo_count >= 2:
        risk_score += 1
        reasons.append(f"title_prop_echo_count={title_echo_count}")
    if title_open_echo:
        risk_score += 1
        reasons.append("title_prop_opening_echo")
    if title_tail_echo:
        risk_score += 2
        reasons.append("title_prop_tail_echo")
    if len(prompt_context_hits) >= 5:
        risk_score += 2
        reasons.append(f"prompt_context_count={len(prompt_context_hits)}")
    elif len(prompt_context_hits) >= 3:
        risk_score += 1
        reasons.append(f"prompt_context_count={len(prompt_context_hits)}")
    if len(secondary_hits) >= 2 or secondary_echo_count >= 4:
        risk_score += 1
        reasons.append(f"secondary_prompt_echo={secondary_hits[:6]}")
    if side_engine_lines <= 2:
        risk_score += 1
        reasons.append(f"side_engine_lines={side_engine_lines}")

    if risk_score < 4:
        return None
    return {
        "body_chars": body_chars,
        "body_lines": len(visible_lines),
        "title": normalized_title,
        "title_hits": title_hits[:4],
        "title_echo_count": title_echo_count,
        "title_open_echo": title_open_echo,
        "title_tail_echo": title_tail_echo,
        "prompt_context_hits": prompt_context_hits[:8],
        "secondary_hits": secondary_hits[:8],
        "secondary_echo_count": secondary_echo_count,
        "side_engine_lines": side_engine_lines,
        "reasons": reasons[:8],
    }


def check_standard_prompt_prop_title_loop(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = standard_prompt_prop_title_loop_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "标准日寄提示物标题闭环",
            0,
            json.dumps(risk, ensure_ascii=False),
            "标准日寄生成稿高风险：一个提示物或题面小物同时当标题、开头发动机和尾部回收，容易读成按题目搭出的完整证明链。这不是局部换词问题；重选侧面后果作标题，删弱一个提示物回声，从门口/楼道/付款/脏手/错回复/水槽/骑手或别人的反应重建中段，让题面物件只作为一次压力表面。",
        )
    )


def check_diagnostic_title(findings: list[Finding], lines: list[str]) -> None:
    title, _ = split_title_and_content_lines(lines)
    if not title:
        return
    if title != "日寄":
        matched = [term for term in TOPIC_DIAGNOSTIC_TITLE_TERMS if term in title]
        if re.search(r"(?:19|20)\d{2}(?:年)?日寄$", title):
            matched.append("four_digit_year")
        if re.search(r"(?:\d{1,2}月\d{1,2}日|元旦|新年|跨年)(?:日寄|寄)$", title):
            matched.append("calendar_label")
        if matched:
            findings.append(
                Finding(
                    "warning",
                    "题面诊断型标题",
                    1,
                    title,
                    f"标题含高信号主题词 {matched}；先按 title-model.md 弱化诊断词。可改为“日寄”，也可改为正文里的侧面把手、问题、短句或低状态物件。",
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
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
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
                "文章明显偏短时，从最强可用 fragment 整体重建，恢复完整文章和必要的多个 thought-turn；不要把残稿保留为一换一 packet repair，也不要追加检查器形状的证明场景；若本来就是短体裁则改用匹配评估。",
            )
        )
    elif chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS:
        findings.append(
            Finding(
                "warning",
                "标准日寄完整文章篇幅缓冲不足",
                0,
                f"body_chinese_chars={chars}",
                "篇幅缓冲不足时容易在生成波动和修复中变成长度识别点；一换一替换最早过载或重复的 fragment relation，把缺失质量恢复到 replacement 与相邻既有 movement；不要追加独立行动链、社交误伤、身体/金钱证明或无用残留。",
            )
        )
    elif chars > STANDARD_DIARY_DRAFT_OVERFULL_CHARS:
        findings.append(
            Finding(
                "warning",
                "标准日寄完整文章过满",
                0,
                f"body_chinese_chars={chars}",
                "正式标准日寄生成稿过长时常是为了过检查而堆身体、屏幕、物件和解释。优先删掉不改变行动、社交位置、身体后果或下一片段的材料；不要用篇幅数字决定内容。",
            )
        )


def check_generated_texture_overfill(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS or len(visible_lines) < 35:
        return
    group_hits: dict[str, int] = {}
    for group, terms in TEXTURE_OVERFILL_GROUPS.items():
        group_hits[group] = sum(1 for line in visible_lines if any(term in line for term in terms))
    active_groups = {group: count for group, count in group_hits.items() if count >= 9}
    any_texture_lines = sum(
        1
        for line in visible_lines
        if any(any(term in line for term in terms) for terms in TEXTURE_OVERFILL_GROUPS.values())
    )
    texture_ratio = any_texture_lines / len(visible_lines)
    if body_chars > 1150 and len(active_groups) >= 3 and texture_ratio >= 0.50:
        findings.append(
            Finding(
                "warning",
                "具体纹理堆叠过密",
                0,
                f"body_chars={body_chars}, texture_ratio={texture_ratio:.2f}, group_hits={json.dumps(active_groups, ensure_ascii=False)}",
                "生成稿高风险：身体、屏幕、路物细节同时过密，容易像把生活气味清单塞满。删掉不改变动作、社交位置、身体后果或下一场景的具体名词，保留有后果的两三处。",
            )
        )
    social_lines = sum(1 for line in visible_lines if any(term in line for term in TEXTURE_SOCIAL_TERMS))
    body_route_lines = group_hits.get("body", 0) + group_hits.get("route_object", 0)
    if body_chars >= STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS and group_hits.get("body", 0) >= 10 and group_hits.get("route_object", 0) >= 8 and social_lines <= 3:
        findings.append(
            Finding(
                "warning",
                "纹理替代社交不足",
                0,
                f"body_chars={body_chars}, body_lines={group_hits.get('body', 0)}, route_object_lines={group_hits.get('route_object', 0)}, social_lines={social_lines}, body_route_lines={body_route_lines}",
                "生成稿高风险：身体/物件纹理已经很多，但社交后果太少，修复时容易继续堆手、灰、案板、垃圾桶。删掉一个重复纹理簇，换成会改变回复、付款、路线、房间位置或社交处境的真实小动作。",
            )
        )


def check_illness_case_report_loop(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 30:
        return
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS:
        return
    lower_body = body.lower()
    illness_hits = sum(lower_body.count(term.lower()) for term in ILLNESS_CASE_REPORT_TERMS)
    illness_lines = sum(1 for line in visible_lines if any(term in line for term in ILLNESS_CASE_REPORT_TERMS))
    body_texture_lines = sum(1 for line in visible_lines if any(term in line for term in TEXTURE_OVERFILL_GROUPS["body"]))
    screen_lines = sum(1 for line in visible_lines if any(term in line for term in ILLNESS_CASE_SCREEN_TERMS))
    room_food_lines = sum(1 for line in visible_lines if any(term in line for term in ILLNESS_CASE_ROOM_FOOD_TERMS))
    exposed_social_lines = sum(1 for line in visible_lines if any(term in line for term in EXPOSED_SOCIAL_CONSEQUENCE_TERMS))
    if (
        illness_hits >= 7
        and illness_lines >= 6
        and body_texture_lines >= 12
        and screen_lines >= 2
        and room_food_lines >= 6
        and exposed_social_lines == 0
    ):
        findings.append(
            Finding(
                "warning",
                "疾病病例报告闭环",
                0,
                (
                    f"illness_hits={illness_hits}, illness_lines={illness_lines}, "
                    f"body_texture_lines={body_texture_lines}, screen_lines={screen_lines}, "
                    f"room_food_lines={room_food_lines}, exposed_social_lines={exposed_social_lines}"
                ),
                "生成稿高风险：疾病/身体 prompt 变成症状、搜索、冰箱食物、房间味道和环境声的私密病例报告。删除一个症状/食物/屏幕包，换成别人看见、问话、递东西、付款、门口/楼道接触或路线受阻等会改变行动和社交位置的暴露后果；手机消息不等于真实社交暴露。",
            )
        )


def check_illness_body_proof_overdensity(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 40:
        return
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS:
        return
    lower_body = body.lower()
    illness_hits = sum(lower_body.count(term.lower()) for term in ILLNESS_CASE_REPORT_TERMS)
    illness_lines = sum(1 for line in visible_lines if any(term in line for term in ILLNESS_CASE_REPORT_TERMS))
    body_texture_lines = sum(1 for line in visible_lines if any(term in line for term in TEXTURE_OVERFILL_GROUPS["body"]))
    screen_lines = sum(1 for line in visible_lines if any(term in line for term in ILLNESS_CASE_SCREEN_TERMS))
    room_food_lines = sum(1 for line in visible_lines if any(term in line for term in ILLNESS_CASE_ROOM_FOOD_TERMS))
    exposed_social_lines = sum(1 for line in visible_lines if any(term in line for term in EXPOSED_SOCIAL_CONSEQUENCE_TERMS))
    if (
        illness_hits >= 7
        and illness_lines >= 6
        and body_texture_lines >= 18
        and screen_lines >= 4
        and room_food_lines >= 4
        and 1 <= exposed_social_lines <= 4
    ):
        findings.append(
            Finding(
                "warning",
                "疾病身体证明过密",
                0,
                (
                    f"illness_hits={illness_hits}, illness_lines={illness_lines}, "
                    f"body_texture_lines={body_texture_lines}, screen_lines={screen_lines}, "
                    f"room_food_lines={room_food_lines}, exposed_social_lines={exposed_social_lines}"
                ),
                "生成稿高风险：已经有外部后果，但症状、搜索、手机、房间食物和身体动作仍反复证明同一个病痛。删掉一个症状/屏幕/房间包，让外部后果改变回复、付款、路线、门口位置或下一步行动。",
            )
        )


def check_social_decline_room_texture_overfill(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 40:
        return
    body = "\n".join(visible_lines)
    body_chars = chinese_len(body)
    if body_chars < 850:
        return
    social_hits = sum(body.count(term) for term in SOCIAL_DECLINE_TERMS)
    social_lines = sum(1 for line in visible_lines if any(term in line for term in TEXTURE_SOCIAL_TERMS))
    body_route_lines = sum(
        1
        for line in visible_lines
        if any(term in line for term in TEXTURE_OVERFILL_GROUPS["body"])
        or any(term in line for term in TEXTURE_OVERFILL_GROUPS["screen"])
        or any(term in line for term in TEXTURE_OVERFILL_GROUPS["route_object"])
    )
    room_cold_lines = sum(1 for line in visible_lines if any(term in line for term in ROOM_COLD_FILLER_TERMS))
    room_cold_tail_lines = sum(1 for line in visible_lines[-10:] if any(term in line for term in ROOM_COLD_FILLER_TERMS))
    if social_hits >= 5 and body_route_lines >= 22 and social_lines <= 4:
        findings.append(
            Finding(
                "warning",
                "社交拒绝纹理替代后果不足",
                0,
                f"social_hits={social_hits}, body_route_lines={body_route_lines}, social_lines={social_lines}",
                "生成稿高风险：婚礼/邀请/随礼/拒绝线已经足够明显，但文章主要靠身体、屏幕、路线、物件纹理运转，真实社交后果不足。删掉一个纹理簇，让拒绝后的回复、钱/路线决定、旧债、错话或对方反应改变下一步行动。",
            )
        )
    if social_hits >= 5 and room_cold_lines >= 14 and room_cold_tail_lines >= 2:
        findings.append(
            Finding(
                "warning",
                "社交拒绝室内冷感过密",
                0,
                (
                    f"social_hits={social_hits}, room_cold_lines={room_cold_lines}, "
                    f"room_cold_tail_lines={room_cold_tail_lines}"
                ),
                "生成稿高风险：婚礼/邀请/随礼压力被暖气、冷、手指、泡面、洗手等室内冷感包反复替代。保留一个房间侧物即可；让拒绝回复、钱、旧关系、路程、错话或对方反应改变下一步行动。",
            )
        )


def social_decline_plain_reply_private_loop_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return None
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 3:
        return None
    body = "\n".join(visible_lines)
    if chinese_len(body) < STANDARD_DIARY_ATTEMPT_MIN_CHARS:
        return None
    social_hits = sum(body.count(term) for term in SOCIAL_DECLINE_TERMS)
    has_invitation_context = any(
        term in body
        for term in ("狗哥", "结婚", "婚礼", "随礼", "份子钱", "高铁", "来不来", "去不了", "走不开")
    )
    if social_hits < 4 or not has_invitation_context:
        return None

    refusal_index = None
    for index, line in enumerate(visible_lines):
        if any(term in line for term in SOCIAL_DECLINE_REFUSAL_TERMS):
            refusal_index = index
            break
    if refusal_index is None:
        return None

    response_index = None
    for index in range(refusal_index + 1, min(len(visible_lines), refusal_index + 9)):
        line = visible_lines[index]
        if line.startswith("我"):
            continue
        if SOCIAL_DECLINE_PLAIN_RESPONSE_RE.search(line):
            response_index = index
            break
    if response_index is None:
        return None

    response_line = visible_lines[response_index]
    # A response that itself changes address, headcount, route, or ticket state
    # is less likely to be the narrow "OK then private stain" failure.
    if re.search(r"(?:不把你|不算你|人数|名单|桌|座|地址|定位|时间|车票|退票|路线|不用来|留位)", response_line):
        return None

    post_lines = visible_lines[response_index + 1 : response_index + 13]
    if not post_lines:
        return None
    post_text = "\n".join(post_lines)
    visible_action_hits = [term for term in SOCIAL_DECLINE_REPLY_VISIBLE_ACTION_TERMS if term in post_text]
    if len(visible_action_hits) >= 2:
        return None
    private_hits = [term for term in SOCIAL_DECLINE_REPLY_PRIVATE_LOOP_TERMS if term in post_text]
    if not private_hits:
        return None

    private_lines = [
        line
        for line in post_lines
        if any(term in line for term in SOCIAL_DECLINE_REPLY_PRIVATE_LOOP_TERMS)
    ]
    if visible_action_hits and len(private_lines) < 3:
        return None
    return {
        "response_line": response_index + 1,
        "response": clean_excerpt(response_line),
        "private_hits": private_hits[:8],
        "visible_action_hits": visible_action_hits[:6],
        "private_line_count": len(private_lines),
    }


def check_social_decline_plain_reply_private_loop(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = social_decline_plain_reply_private_loop_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "社交拒绝普通回复假后果",
            int(risk["response_line"]),
            str(risk["response"]),
            "生成稿高风险：拒绝后用“好的/OK/抱拳”等普通回复接一段屏幕、水痕、油印、袖口或房间纹理，仍是私密屏幕循环。普通回复必须改变下一步可见动作：更差的回复、门口等待、付款/路线停住、他人问/指/等、或身体/门/物件问题被社交压力当场改写；否则从 reply aftermath 重建。",
        )
    )


def check_social_decline_scripted_return_gift(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 30:
        return
    body = "\n".join(visible_lines)
    social_hits = sum(body.count(term) for term in SOCIAL_DECLINE_TERMS)
    has_invitation_context = any(term in body for term in ("狗哥", "结婚", "婚礼", "随礼", "份子钱", "高铁", "来不来", "去不了"))
    if social_hits < 4 or not has_invitation_context:
        return
    scripted_patterns = [
        r"^(?:狗哥|他|对方)[^。！？\n]{0,24}发(?:了|来)?(?:个|一个)?红包",
        r"红包[^。！？\n]{0,24}(?:六块六|6\.6|一块两毛五|沾点喜气|心意到了|项目忙就算了)",
        r"(?:附言|备注)[^。！？\n]{0,30}(?:心意到了|项目忙就算了|沾点喜气)",
    ]
    for line_number, line in enumerate(visible_lines, start=1):
        if any(re.search(pattern, line) for pattern in scripted_patterns):
            findings.append(
                Finding(
                    "warning",
                    "社交拒绝编剧化回礼",
                    line_number,
                    clean_excerpt(line),
                    "生成稿高风险：婚礼拒绝后的对方回红包、沾喜气、心意到了等反转太像模型在补一个精巧后果。让对方保持普通短回复、沉默、改话题、发地址/照片、或让现实付款/路线/身体失败承担后果；不要用礼貌反转替文章收束。",
                )
            )
            return


def social_decline_group_fake_consequence_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    title, content_lines = split_title_and_content_lines(lines)
    if detect_style(text) != "standard":
        return None
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 3:
        return None
    body = "\n".join(visible_lines)
    if chinese_len(body) < STANDARD_DIARY_ATTEMPT_MIN_CHARS:
        return None
    social_hits = sum(body.count(term) for term in SOCIAL_DECLINE_TERMS)
    has_invitation_context = any(
        term in body
        for term in ("狗哥", "结婚", "婚礼", "随礼", "份子钱", "高铁", "来不来", "去不了", "走不开", "忙项目")
    )
    if social_hits < 4 or not has_invitation_context:
        return None

    refusal_index = None
    for index, line in enumerate(visible_lines):
        if any(term in line for term in SOCIAL_DECLINE_REFUSAL_TERMS):
            refusal_index = index
            break
    if refusal_index is None:
        return None

    post_refusal_lines = visible_lines[refusal_index + 1 : refusal_index + 18]
    if not post_refusal_lines:
        return None
    post_refusal_text = "\n".join(post_refusal_lines)
    group_term_hits = [term for term in SOCIAL_DECLINE_GROUP_FAKE_CONSEQUENCE_TERMS if term in post_refusal_text]
    group_lines = [
        line
        for line in post_refusal_lines
        if any(term in line for term in SOCIAL_DECLINE_GROUP_FAKE_CONSEQUENCE_TERMS)
        or ("群里" in line and any(marker in line for marker in ("有人", "@", "问", "说", "回", "发")))
    ]
    group_crowd_pattern_hits = re.findall(r"(?:群里|群聊|班群)[^。！？\n]{0,80}(?:有人|@|问|说|回|发)", post_refusal_text)
    if len(group_lines) < 2 and len(group_term_hits) < 2 and len(group_crowd_pattern_hits) < 1:
        return None
    private_or_closed_lines = [
        line
        for line in post_refusal_lines
        if any(term in line for term in SOCIAL_DECLINE_REPLY_PRIVATE_LOOP_TERMS)
        or any(term in line for term in ("屏幕", "手机", "外套", "水龙头", "热水器", "沙发", "桌上", "没有下文"))
    ]
    active_low_consequence_lines = [
        line
        for line in post_refusal_lines
        if any(term in line for term in ("门口", "外卖", "扫码", "付款", "下楼", "让路", "摔", "洒", "漏", "递", "接", "问了一句", "等我"))
    ]
    if active_low_consequence_lines and len(active_low_consequence_lines) >= len(group_lines):
        return None
    first_group = group_lines[0]
    return {
        "line": visible_lines.index(first_group) + 1,
        "excerpt": clean_excerpt(first_group),
        "group_line_count": len(group_lines),
        "group_term_hits": group_term_hits[:8],
        "private_or_closed_line_count": len(private_or_closed_lines),
        "active_low_consequence_line_count": len(active_low_consequence_lines),
    }


def check_social_decline_group_fake_consequence(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = social_decline_group_fake_consequence_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "社交拒绝群聊假后果",
            int(risk["line"]),
            str(risk["excerpt"]),
            "生成稿高风险：拒绝后用“群里有人问/有人@我/正在输入”等群聊接力来制造公共后果，仍像模型把社交压力摘要成剧情。删掉群体盘问，换成一个局部可见动作：回复变小、付款/路线卡住、门口有人等、身体/脏手改写手机动作，或一个人一句话直接改变下一步。",
        )
    )


def social_decline_tidy_etiquette_closure_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    title, content_lines = split_title_and_content_lines(lines)
    if detect_style(text) != "standard":
        return None
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 3:
        return None
    body = "\n".join(visible_lines)
    if chinese_len(body) < 520:
        return None
    social_hits = sum(body.count(term) for term in SOCIAL_DECLINE_TERMS)
    has_invitation_context = any(
        term in body
        for term in ("狗哥", "结婚", "婚礼", "随礼", "份子钱", "高铁", "来不来", "去不了", "走不开", "忙项目")
    )
    if social_hits < 4 or not has_invitation_context:
        return None
    tidy_lines = [
        line
        for line in visible_lines
        if any(term in line for term in SOCIAL_DECLINE_TIDY_ETIQUETTE_CLOSURE_TERMS)
        or re.search(r"发(?:了)?(?:一个|个)?红包[^。！？\n]{0,20}(?:抱歉|人不到|心意|下次)", line)
    ]
    if not tidy_lines:
        return None
    tail_text = "\n".join(visible_lines[-10:])
    tidy_tail = any(line in visible_lines[-12:] for line in tidy_lines)
    closes_with_polite_reply = any(term in tail_text for term in ("下次一起吃饭", "人不到没事", "心意到了", "抱歉人不到", "人不到钱到"))
    if not (tidy_tail or closes_with_polite_reply):
        return None
    first_tidy = tidy_lines[0]
    return {
        "line": visible_lines.index(first_tidy) + 1,
        "excerpt": clean_excerpt(first_tidy),
        "tidy_terms": [term for term in SOCIAL_DECLINE_TIDY_ETIQUETTE_CLOSURE_TERMS if term in body][:6],
        "tidy_tail": tidy_tail,
    }


def check_social_decline_tidy_etiquette_closure(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = social_decline_tidy_etiquette_closure_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "社交拒绝礼貌闭合",
            int(risk["line"]),
            str(risk["excerpt"]),
            "生成稿高风险：拒绝婚礼后用“人不到钱到/人不到没事/下次一起吃饭/心意到了”把关系处理成礼貌闭合，太像修复代理在补道德结尾。不要用红包和客气话收束；让未完成的回复、付款/路线犹豫、门口/身体小麻烦、旧债或低处动作留下松散尾巴。",
        )
    )


def social_decline_decoupled_consequence_risk(lines: list[str], text: str) -> dict[str, Any] | None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return None
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 30:
        return None
    body = "\n".join(visible_lines)
    if chinese_len(body) < STANDARD_DIARY_ATTEMPT_MIN_CHARS:
        return None
    social_hits = sum(body.count(term) for term in SOCIAL_DECLINE_TERMS)
    has_invitation_context = any(
        term in body
        for term in ("狗哥", "结婚", "婚礼", "随礼", "份子钱", "高铁", "来不来", "去不了", "走不开", "忙项目")
    )
    if social_hits < 4 or not has_invitation_context:
        return None

    refusal_index = None
    for index, line in enumerate(visible_lines):
        if any(term in line for term in SOCIAL_DECLINE_REFUSAL_TERMS):
            refusal_index = index
            break
    if refusal_index is None:
        return None

    response_index = refusal_index
    for index in range(refusal_index + 1, min(len(visible_lines), refusal_index + 9)):
        line = visible_lines[index]
        if line.startswith("我"):
            continue
        if SOCIAL_DECLINE_PLAIN_RESPONSE_RE.search(line):
            response_index = index
            break

    post_lines = visible_lines[response_index + 1 : response_index + 17]
    if not post_lines:
        return None
    post_text = "\n".join(post_lines)
    fake_lines = [
        line
        for line in post_lines
        if any(term in line for term in SOCIAL_DECLINE_DECOUPLED_CONSEQUENCE_TERMS)
    ]
    fake_hits = [term for term in SOCIAL_DECLINE_DECOUPLED_CONSEQUENCE_TERMS if term in post_text]
    if len(fake_lines) < 2 and len(fake_hits) < 3:
        return None

    coupled_lines = [
        line
        for line in post_lines
        if any(pattern.search(line) for pattern in SOCIAL_DECLINE_COUPLED_CONSEQUENCE_PATTERNS)
    ]
    if not coupled_lines:
        paired_lines = zip(post_lines, post_lines[1:])
        for previous, current in paired_lines:
            pair = previous + current
            if any(pattern.search(pair) for pattern in SOCIAL_DECLINE_COUPLED_CONSEQUENCE_PATTERNS):
                coupled_lines.append(previous + " / " + current)
                break
    if coupled_lines:
        return None

    private_after_reply_lines = [
        line
        for line in post_lines
        if any(term in line for term in SOCIAL_DECLINE_REPLY_PRIVATE_LOOP_TERMS)
    ]
    first_fake = fake_lines[0]
    return {
        "line": visible_lines.index(first_fake) + 1,
        "excerpt": clean_excerpt(first_fake),
        "fake_terms": fake_hits[:8],
        "fake_line_count": len(fake_lines),
        "private_line_count": len(private_after_reply_lines),
    }


def check_social_decline_decoupled_consequence(findings: list[Finding], lines: list[str], text: str) -> None:
    risk = social_decline_decoupled_consequence_risk(lines, text)
    if not risk:
        return
    findings.append(
        Finding(
            "warning",
            "社交拒绝无关后果替代",
            int(risk["line"]),
            str(risk["excerpt"]),
            "生成稿高风险：拒绝婚礼/邀请之后，用外卖、烫手、房间活、取快递或下楼 errands 伪装成后果，但这些动作删掉邀请仍能成立。不要把具体生活纹理当作社交后果；重建一个 refusal-coupled consequence，让回复、付款、路线、门口等待、脏手/湿手或旧关系直接改变下一步动作。",
        )
    )


def check_social_decline_private_transfer_loop(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 35:
        return
    body = "\n".join(visible_lines)
    social_hits = sum(body.count(term) for term in SOCIAL_DECLINE_TERMS)
    has_invitation_context = any(term in body for term in ("狗哥", "结婚", "婚礼", "随礼", "份子钱", "高铁", "来不来", "去不了", "走不开"))
    if social_hits < 4 or not has_invitation_context:
        return
    transfer_terms = ("转账", "支付宝", "微信钱包", "微信转", "备注", "收款", "余额")
    private_status_terms = ("没领", "未领取", "钱没收", "交易失败", "已读但钱", "备注写不上", "等了一会儿")
    transfer_lines = [line for line in visible_lines if any(term in line for term in transfer_terms)]
    private_status_lines = [line for line in visible_lines if any(term in line for term in private_status_terms)]
    if len(transfer_lines) < 2 or not private_status_lines:
        return
    transfer_index = min(
        visible_lines.index(line)
        for line in transfer_lines + private_status_lines
    )
    post_transfer_lines = visible_lines[transfer_index + 1 :]
    visible_consequence_terms = (
        "门口",
        "楼道",
        "邻居",
        "店员",
        "收银",
        "外卖",
        "老板",
        "摊主",
        "等我扫码",
        "地址",
        "打车",
        "车票",
        "退票",
        "出门",
        "下楼",
        "走到",
        "弄洒",
        "洒在",
        "漏在",
        "蹭到",
        "踩",
        "摔",
        "肚子响",
        "咕噜",
        "裤脚",
        "鞋底",
        "手抖",
    )
    consequence_lines = [line for line in post_transfer_lines if any(term in line for term in visible_consequence_terms)]
    if len(consequence_lines) >= 2:
        return
    first_private = next(line for line in visible_lines if any(term in line for term in private_status_terms))
    findings.append(
        Finding(
            "warning",
            "社交拒绝私密转账假后果",
            visible_lines.index(first_private) + 1,
            clean_excerpt(first_private),
            "生成稿高风险：拒绝婚礼后用旧饭钱、转账、备注、已读、未领取等私密 app 循环替代真实后果，仍然停在屏幕里。让转账触发可见回复、门口/路线/付款/身体麻烦，或删掉转账，改用会改变行动的低状态后果。",
        )
    )


def check_social_decline_overextended_aftermath(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 35:
        return
    body = "\n".join(visible_lines)
    if chinese_len(body) < 850:
        return
    social_hits = sum(body.count(term) for term in SOCIAL_DECLINE_TERMS)
    has_invitation_context = any(term in body for term in ("狗哥", "结婚", "婚礼", "随礼", "份子钱", "高铁", "来不来", "去不了", "走不开"))
    if social_hits < 4 or not has_invitation_context:
        return

    refusal_index = None
    for index, line in enumerate(visible_lines):
        if any(term in line for term in SOCIAL_DECLINE_REFUSAL_TERMS):
            refusal_index = index
            break
    if refusal_index is None:
        return

    post_refusal_lines = visible_lines[refusal_index + 1 :]
    if len(post_refusal_lines) < 12:
        return
    time_lines = [
        line
        for line in post_refusal_lines
        if any(term in line for term in SOCIAL_DECLINE_TIME_EXPANSION_TERMS)
    ]
    scripted_lines = [
        line
        for line in post_refusal_lines
        if any(term in line for term in SOCIAL_DECLINE_SCRIPTED_EXTENSION_TERMS)
    ]
    office_commute_lines = [
        line
        for line in post_refusal_lines
        if any(term in line for term in SOCIAL_DECLINE_OFFICE_COMMUTE_DRIFT_TERMS)
    ]
    post_refusal_social_lines = [
        line
        for line in post_refusal_lines
        if any(term in line for term in ("狗哥", "同学", "班群", "合照", "伴郎", "喜酒", "西装", "酒店"))
    ]

    overgrown_time = len(time_lines) >= 3 and len(post_refusal_social_lines) >= 3
    scripted_extension = len(scripted_lines) >= 1 and len(time_lines) >= 1
    office_from_excuse = "忙项目" in body and len(office_commute_lines) >= 2
    if not (overgrown_time or scripted_extension or office_from_excuse):
        return

    excerpt_source = (scripted_lines or office_commute_lines or time_lines)[0]
    findings.append(
        Finding(
            "warning",
            "社交拒绝后果过度生长",
            visible_lines.index(excerpt_source) + 1,
            clean_excerpt(excerpt_source),
            "生成稿高风险：拒绝婚礼/聚会后的后果链被扩成多天连续剧情、伴郎/喜酒反转、通勤同事或办公室人生。社交拒绝的后果应在同晚或一个很小的余波里转移一两次行动；删掉跨日剧情和新身份，让一个普通回复、钱/路线犹豫、错话、旧债或身体/门口麻烦留下未完成的动作。",
        )
    )


def check_third_person_narrator_slip(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    body = "\n".join(content_lines)
    if body.count("我") < 5:
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    for index, line in enumerate(visible_lines):
        if not any(pattern.search(line) for pattern in THIRD_PERSON_NARRATOR_SLIP_PATTERNS):
            continue
        window = "".join(visible_lines[max(0, index - 2) : min(len(visible_lines), index + 3)])
        if any(marker in window for marker in THIRD_PERSON_CONTEXT_MARKERS):
            continue
        findings.append(
            Finding(
                "warning",
                "叙述人称滑移",
                index + 1,
                clean_excerpt(line),
                "生成稿高风险：第一人称日寄突然变成第三人称卧室/手机叙述，会像模型把草稿改成短篇小说。改回第一人称动作，或删掉这一段故事化收束。",
            )
        )
        return


def check_standard_diary_formal_shape(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    lengths = [chinese_len(line) for line in visible_lines if chinese_len(line)]
    body_chars = sum(lengths)
    if body_chars < STANDARD_DIARY_FORMAL_MIN_CHARS or not lengths:
        return
    line_count = len(lengths)
    avg_len = body_chars / line_count
    long_24 = sum(1 for length in lengths if length >= 24)
    long_28 = sum(1 for length in lengths if length >= 28)
    short_10_ratio = sum(1 for length in lengths if length <= 10) / line_count
    long_28_ratio = long_28 / line_count

    if body_chars >= STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS and (line_count < 40 or line_count > 75):
        findings.append(
            Finding(
                "warning",
                "标准日寄行数缓冲异常",
                0,
                f"body_chars={body_chars}, content_lines={line_count}, avg_line_chars={avg_len:.2f}",
                "正式标准日寄生成稿建议在45-70行附近；行数过少像压缩短篇，行数过多像短行网格。只修最小的真实坏点：合并被误切开的既有 movement，或拆开被压成散文块的同一 movement，不要机械换行或追加素材。",
            )
        )

    if body_chars >= STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS and long_24 < 6:
        findings.append(
            Finding(
                "warning",
                "标准日寄长行缓冲不足",
                0,
                f"body_chars={body_chars}, content_lines={line_count}, lines_ge24={long_24}, lines_ge28={long_28}",
                "生成稿缺少承载完整 movement 的粗糙长行；只修最小的真实坏点，合并同一既有动作/回复/身体移动中被误切开的相邻短行，不要另补一条长口语或证明动作。",
            )
        )

    if body_chars >= STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS and (avg_len >= 29 or long_28_ratio >= 0.48):
        findings.append(
            Finding(
                "warning",
                "标准日寄长行过密",
                0,
                f"body_chars={body_chars}, content_lines={line_count}, avg_line_chars={avg_len:.2f}, lines_ge28={long_28}, long_28_ratio={long_28_ratio:.2f}",
                "生成稿不能从短行网格反弹成长句散文。把长行按动作、对话、误读、身体中断和物件后果拆开，目标是45-70行且平均行长更接近原文。",
            )
        )

    if (line_count > 75 and body_chars < 1000) or (line_count > 90 and avg_len < 13) or short_10_ratio >= 0.68:
        findings.append(
            Finding(
                "warning",
                "标准日寄短行网格",
                0,
                f"body_chars={body_chars}, content_lines={line_count}, avg_line_chars={avg_len:.2f}, short_10_ratio={short_10_ratio:.2f}",
                "这不是自然断裂，而像模型把正文切成均匀小格。只修最小的真实坏点，合并同一既有 movement 中被人工切开的4-10字行，并保留原有功能后果；不要再补一条长动作、对话或身体证明线。",
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
    style = detect_style(text)
    lower_text = text.lower()
    for domain, terms in THEME_DOMAINS.items():
        matched_terms = [term for term in terms if term.lower() in lower_text]
        hit_count = sum(lower_text.count(term.lower()) for term in terms)
        if len(matched_terms) >= 7 or hit_count >= 12:
            rule = f"单主题词密度偏高: {domain}" if style == "standard" else f"短体裁主题集中: {domain}"
            suggestion = (
                "盲评高风险：场景可能都在服务同一主轴。替换一段为由气味、身体、路线、无关社交或脏物件触发的旁逸分支。"
                if style == "standard"
                else "短真诚/微小希望/超现实允许主题更集中；只检查是否变成题面复述或 polished prose。保留具体代价、笨动作和非象征性细节，不要硬塞标准日寄旁逸。"
            )
            findings.append(
                Finding(
                    "warning",
                    rule,
                    0,
                    f"terms={matched_terms}, hits={hit_count}",
                    suggestion,
                )
            )


def comment_chain_formula_hits(line: str) -> list[str]:
    """Return formulaic online-comment/group-chain markers for a single line."""
    hits: list[str] = []
    contextual_markers = set(CONTEXTUAL_COMMENT_CHAIN_MARKERS)
    has_online_context = any(context in line for context in ONLINE_COMMENT_CONTEXT_TERMS)
    has_contextual_marker = any(marker in line for marker in CONTEXTUAL_COMMENT_CHAIN_MARKERS)
    for marker in COMMENT_CHAIN_FORMULA_MARKERS:
        if marker in contextual_markers:
            continue
        if marker in COMMENT_CHAIN_ACTOR_MARKERS:
            if marker in line and (has_online_context or has_contextual_marker):
                hits.append(marker)
            continue
        if marker in line:
            hits.append(marker)
    if has_online_context or any(context in line for context in COMMENT_CHAIN_CONTEXT_TERMS):
        for marker in CONTEXTUAL_COMMENT_CHAIN_MARKERS:
            if marker in line:
                hits.append(marker)
    actor_hits = len(re.findall(r"(?:有人|有个人|另一个人)(?:说|回|问|发|开始)", line))
    if actor_hits >= 2 and has_online_context:
        hits.append("multi_actor_chain")
    return hits


def check_comment_chain_formula(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in enumerate(lines, start=1):
        marker_hits = comment_chain_formula_hits(line)
        if marker_hits:
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
        private_texture = [term for term in PRIVATE_ROUGH_TEXTURE_TERMS if term in text]
        if private_texture:
            findings.append(
                Finding(
                    "warning",
                    "私密湿脏纹理替代粗粝",
                    0,
                    f"terms={private_texture[:6]}",
                    "室内湿袖口、湿裤腿、拖鞋、漏水、盆、热水器声音仍是私密纹理，不等于粗粝自毁。让它改变外部/社交/付款/路线/回复动作，或删掉这包纹理重建后果。",
                )
            )
        findings.append(
            Finding(
                "warning",
                "粗粝自毁信号不足",
                0,
                "present=[]",
                "标准日寄不能只靠安静观察和物件真实感。不要用脏话硬补；让身体尴尬、付款失败、他人等待、东西弄脏、社交误伤或不好看的笑点改变动作；屋里湿裤腿/拖鞋/漏水如果没有外部或社交后果，仍然只是私密纹理。",
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


def feed_inventory_opening_hits(lines: list[str]) -> list[tuple[int, str]]:
    """Find social-feed opening lines that enumerate prompt surfaces."""
    _, content_lines = split_title_and_content_lines(lines)
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.strip().startswith("<!--")
    ]
    hits: list[tuple[int, str]] = []
    for offset, line in enumerate(visible_lines[:12], start=1):
        payload_hits = [term for term in SOCIAL_FEED_INVENTORY_TERMS if term in line]
        repeated_screens = len(re.findall(r"晒[^，。！？\n]{0,8}", line))
        has_surface = any(term in line for term in SOCIAL_FEED_SURFACE_TERMS) or repeated_screens >= 2
        has_inventory_word = any(term in line for term in SOCIAL_FEED_INVENTORY_WORDS) or repeated_screens >= 2
        if has_surface and has_inventory_word and (len(payload_hits) >= 2 or repeated_screens >= 2):
            hits.append((offset, line))
    return hits


def check_feed_inventory_opening(findings: list[Finding], lines: list[str]) -> None:
    for line_number, line in feed_inventory_opening_hits(lines)[:3]:
        findings.append(
            Finding(
                "warning",
                "社交动态库存式开头",
                line_number,
                clean_excerpt(line),
                "社交动态/朋友圈入口不要在开头列库存。保留一个裁剪过的屏幕表面，然后立刻离开手机，让身体、门口、付款、房间、错误回复、食物/物件后果或外部接触改变下一步。",
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


def check_time_archive_private_chain(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    style = detect_style(text)
    if style != "standard":
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 30 or chinese_len("\n".join(visible_lines)) < 650:
        return
    surface = "\n".join([title, *visible_lines])
    archive_hits = [term for term in TIME_ARCHIVE_TERMS if term in surface]
    if len(archive_hits) < 5:
        return
    screen_lines = sum(1 for line in visible_lines if any(term in line for term in SCREEN_ARCHAEOLOGY_TERMS))
    outside_lines = sum(1 for line in visible_lines if any(term in line for term in OUTSIDE_CONTACT_TERMS))
    engine_hits = [term for term in ENGINE_SIGNAL_TERMS if term in surface]
    engine_hits.extend(pattern for pattern in ENGINE_SIGNAL_PATTERNS if re.search(pattern, surface))
    if screen_lines >= 7 and outside_lines <= 1 and len(engine_hits) < 3:
        findings.append(
            Finding(
                "warning",
                "旧记录私密考古链",
                0,
                f"archive_hits={archive_hits[:8]}, screen_lines={screen_lines}, outside_lines={outside_lines}, engine_hits={engine_hits[:4]}",
                "跨年、年度总结、旧聊天或回忆题材不能停在屏幕考古和室内物件。保留一个旧记录切片，让它造成当下错误回复、外界接触、付款/路线/身体后果或低处动作；不要继续补旧消息列表。",
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
    pattern_hits = [pattern for pattern in ENGINE_SIGNAL_PATTERNS if re.search(pattern, text)]
    if len(hits) + len(pattern_hits) < 3:
        findings.append(
            Finding(
                "warning",
                "段落发动机信号偏弱",
                0,
                f"present={hits + pattern_hits}",
                "标准日寄不能只是安静低落。不要靠骂词补信号；让误读、自毁、社交误伤、身体降格、公共交易失败或荒谬系统解释推动段落。",
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
                "这里检查的是内容行实际以中文逗号结尾的比例，不是行内逗号数量。把仍在继续的动作/想法断在逗号后面；不要只把多行合成内部逗号长句。",
            )
        )


def check_global_comma_density(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    body = "\n".join(line for line in content_lines if line.strip() and not line.startswith("<!--"))
    chars = chinese_len(body)
    if chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS:
        return
    comma_count = body.count("，") + body.count(",")
    comma_per_1k = comma_count / chars * 1000 if chars else 0.0
    if comma_per_1k > 100:
        findings.append(
            Finding(
                "warning",
                "逗号密度过高",
                0,
                f"body_chars={chars}, comma_count={comma_count}, comma_per_1k={comma_per_1k:.2f}",
                "生成稿高风险：过多逗号会像模型为了制造口语呼吸而持续拖句。只修最小的真实坏点：删掉解释尾巴，把一条失真的逗号链恢复成它实际需要的硬停顿或既有动作边界；不要再补长行动句、继续撒逗号/连接词，或把短行机械合并成内部逗号长句。",
            )
        )


def check_standard_period_row_grid(findings: list[Finding], lines: list[str], text: str) -> None:
    title, content_lines = split_title_and_content_lines(lines)
    if not looks_like_standard_diary_gate_target(title, content_lines, text):
        return
    visible_lines = [line.strip() for line in content_lines if line.strip() and not line.startswith("<!--")]
    if len(visible_lines) < 45:
        return
    body = "\n".join(visible_lines)
    chars = chinese_len(body)
    if chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS:
        return
    period_count = body.count("。")
    period_per_1k = period_count / chars * 1000 if chars else 0.0
    line_period_ratio = sum(1 for line in visible_lines if line.endswith("。")) / max(1, len(visible_lines))
    short_breath_count = sum(
        1
        for line in visible_lines
        if 1 <= chinese_len(line) <= 8 and re.search(r"[。！？]$", line) and not re.search(r"[，,；;：:]", line)
    )
    if (period_per_1k >= 45 and period_count >= 35) or (line_period_ratio >= 0.65 and short_breath_count < 4):
        findings.append(
            Finding(
                "warning",
                "标准日寄句号网格",
                0,
                (
                    f"body_chars={chars}, body_lines={len(visible_lines)}, periods={period_count}, "
                    f"period_per_1k={period_per_1k:.1f}, line_period_ratio={line_period_ratio:.2f}, "
                    f"short_breath_lines={short_breath_count}"
                ),
                "生成稿高风险：标准日寄不能修成一排封闭句号句。不要把逗号问题反向修成句号网格；只修最小的真实坏点，从 continuation、hard landing、rough long row、short failed retreat 中选择该 movement 实际需要的一种关系，不要配齐模板。",
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


SINCERE_TITLE_MARKERS = [
    "真诚",
    "真心话",
    "母亲节",
    "谢谢你",
    "陪我走过",
    "不想祝",
]
SINCERE_BODY_MARKERS = [
    "母亲节快乐",
    "不做母亲",
    "谢谢你",
    "陪我走过",
    "陪我熬",
]
SINCERE_MOTHER_SUBJECT_MARKERS = ["妈妈", "我妈", "母亲"]
SINCERE_DIRECT_MOTHER_CONTEXT_MARKERS = [
    "母亲节",
    "康乃馨",
    "五月十二",
    "5月12",
]
SINCERE_HOLIDAY_OR_MESSAGE_MARKERS = [
    "母亲节",
    "康乃馨",
    "祝福",
    "没发",
    "发消息",
    "朋友圈",
    "五月十二",
    "5月12",
]
SINCERE_CARE_MEMORY_MARKERS = [
    "鸡蛋",
    "雨衣",
    "下雨",
    "送我上学",
    "撑着伞",
    "书包",
    "饭盒",
    "头发全湿",
    "发烧",
    "摸我的额头",
]
SINCERE_CARE_LOGISTICS_MARKERS = [
    "塑料袋",
    "带回去",
    "外面的鸡蛋",
    "别忘了吃",
    "还有没有菜",
    "天冷了多穿",
    "吃了吗",
    "吃了没有",
    "吃饭没有",
    "自己留着花",
    "多买点好吃",
    "转钱",
]
SHORT_GENRE_PRESENT_ANCHOR_GROUPS = {
    "body_or_dirty": [
        "袜子",
        "拖鞋",
        "脚趾",
        "蚊子包",
        "挠破",
        "血印",
        "裤子湿",
        "湿了一身",
        "袖口",
        "指甲",
        "洗洁精",
        "油花",
        "油",
        "脏",
        "灰",
        "烫",
    ],
    "room_or_chore": [
        "水槽",
        "水龙头",
        "洗锅",
        "洗碗",
        "碗",
        "冰箱门",
        "弹开",
        "热水",
        "冷水",
        "管子",
        "堵",
        "阳台",
        "钥匙",
        "门响",
        "敲门",
    ],
    "outside_or_reply": [
        "隔壁",
        "邻居",
        "快递",
        "门口",
        "楼道",
        "电话",
        "未接",
        "回微信",
        "发错",
        "打错",
        "回了个",
        "问我",
        "看了一眼",
        "看了我",
    ],
}
SHORT_GENRE_PRESENT_ANCHOR_TERMS = sorted(
    {term for terms in SHORT_GENRE_PRESENT_ANCHOR_GROUPS.values() for term in terms}
)
SINCERE_REPAIR_STUFFING_FAMILIES = {
    "delivery": [
        "外卖",
        "骑手",
        "配送",
        "订单",
        "取餐",
        "送餐",
        "叫外卖",
        "都叫外卖",
    ],
    "extra_food": [
        "黄焖鸡",
        "桂花糕",
        "酥糖",
        "溏心蛋",
        "奶茶",
        "麻辣烫",
        "炸鸡",
        "烧烤",
        "蛋糕",
        "粽子",
    ],
    "gift_packet": [
        "礼物",
        "礼盒",
        "买了两盒",
        "阿姨送过去",
        "寄回去",
        "花束",
        "快递盒",
    ],
    "media_packet": [
        "综艺",
        "短视频",
        "视频教",
        "教程",
        "直播",
        "博主",
        "转场",
    ],
    "game_packet": [
        "王者",
        "游戏",
        "排位",
        "打野",
        "星耀",
        "蔡文姬",
        "队友",
    ],
    "route_packet": [
        "导航",
        "打车",
        "公交",
        "地铁",
        "高铁",
        "站台",
        "路线",
        "小区门口",
    ],
    "background_label": [
        "云南",
        "湖南",
        "知乎",
        "狗哥",
        "211",
        "计算机",
        "痛风",
    ],
}
SINCERE_REPAIR_STUFFING_TERMS = sorted(
    {term for terms in SINCERE_REPAIR_STUFFING_FAMILIES.values() for term in terms}
)
MICRO_HOPE_TITLE_MARKERS = ["活着就是"]
SURREAL_TITLE_MARKERS = ["存在主义", "迷失"]


def sincere_mother_surface(surface: str) -> bool:
    has_mother_subject = any(marker in surface for marker in SINCERE_MOTHER_SUBJECT_MARKERS)
    message_hits = {marker for marker in SINCERE_HOLIDAY_OR_MESSAGE_MARKERS if marker in surface}
    care_hits = {marker for marker in SINCERE_CARE_MEMORY_MARKERS if marker in surface}
    care_logistics_hits = {marker for marker in SINCERE_CARE_LOGISTICS_MARKERS if marker in surface}
    care_evidence = care_hits | care_logistics_hits
    direct_mother_context = any(marker in surface for marker in SINCERE_DIRECT_MOTHER_CONTEXT_MARKERS)
    pronoun_mother_context = (
        direct_mother_context
        and "她" in surface
        and len(care_evidence) >= 2
    )
    explicit_mother_holiday_or_care = (
        direct_mother_context
        and ((has_mother_subject and len(care_evidence) >= 2) or pronoun_mother_context)
    )
    dense_mother_memory_without_holiday = (
        has_mother_subject
        and len(care_hits) >= 2
        and len(care_evidence) >= 3
        and bool(message_hits)
    )
    return explicit_mother_holiday_or_care or dense_mother_memory_without_holiday


def detect_style(text: str) -> str:
    """Conservatively infer genre for draft-gate routing."""
    if FORCED_GENRE:
        return FORCED_GENRE
    lower_text = text.lower()
    if any(marker in lower_text for marker in ["truthful", "sincere"]):
        return "sincere"

    lines = text.splitlines()
    title, content_lines = split_title_and_content_lines(lines)
    surface = "\n".join([title, *content_lines[:40]])
    full_surface = "\n".join([title, *content_lines])
    if any(marker in title for marker in MICRO_HOPE_TITLE_MARKERS):
        return "micro-hope"
    if any(marker in title for marker in SURREAL_TITLE_MARKERS):
        return "surreal"
    if any(marker in title for marker in SINCERE_TITLE_MARKERS):
        return "sincere"
    sincere_hits = {marker for marker in SINCERE_BODY_MARKERS if marker in surface}
    if len(sincere_hits) >= 2:
        return "sincere"
    if "日寄" not in title:
        if sincere_mother_surface(surface) or sincere_mother_surface(full_surface):
            return "sincere"
    return "standard"


NON_STANDARD_TITLE_HINTS = [
    "真诚",
    "希望",
    "微小",
    "梦",
    "超现实",
    "写不出来",
    "母亲节",
    "谢谢你",
    "陪我走过",
    "不想祝",
]


def looks_like_standard_diary_gate_target(title: str, content_lines: list[str], text: str) -> bool:
    """Return whether generated-draft standard diary gates should apply.

    Title selection is part of the generation task, so a standard diary draft
    must not escape length/rhythm gates merely by choosing a non-`日寄` title.
    Keep this conservative to avoid forcing short sincere/micro-hope pieces
    into the standard-diary corridor.
    """
    if detect_style(text) != "standard":
        return False
    normalized_title = title.lstrip("#").strip()
    if "日寄" in normalized_title:
        return True
    early_surface = normalized_title + "\n" + "\n".join(content_lines[:8])
    if any(hint in early_surface for hint in NON_STANDARD_TITLE_HINTS):
        return False
    visible_lines = [
        line.strip()
        for line in content_lines
        if line.strip() and not line.startswith("<!--")
    ]
    body_chars = chinese_len("\n".join(visible_lines))
    if body_chars >= STANDARD_DIARY_FORMAL_MIN_CHARS and len(visible_lines) >= 35:
        return True
    return body_chars >= STANDARD_DIARY_ATTEMPT_MIN_CHARS and len(visible_lines) >= STANDARD_DIARY_ATTEMPT_MIN_LINES


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
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if (
            1 <= chinese_len(stripped) <= 8
            and re.search(r"[。！？]$", stripped)
            and not re.search(r"[，,；;：:]", stripped)
        ):
            findings.append(Finding("info", "呼吸点", line_number, clean_excerpt(line), "发现短句呼吸点"))
            return
    findings.append(Finding("warning", "呼吸点缺失", 0, "", "标准日寄建议保留真实<=8字独立短落点，落在失败决定、笨回复、身体/社交降低或实际撤退上。"))


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
    check_prompt_performing_dialogue(findings, lines)
    check_ai_slop_terms(findings, lines)
    check_pseudo_humanizer_surface(findings, lines, text)
    check_therapeutic_humanizer_surface(findings, lines)
    check_meta_ai_topic_contamination(findings, text)
    check_literary_ai_surface(findings, lines)
    check_literary_simile_caption(findings, lines)
    check_ai_variable_placeholders(findings, lines)
    check_background_fact_specificity(findings, lines)
    check_major_family_status_fabrication(findings, lines)
    check_game_match_report_surface(findings, lines)
    check_current_office_persona(findings, text)
    check_work_consequence_chain(findings, lines)
    check_offer_specificity_surface(findings, lines)
    check_background_display_stuffing(findings, text)
    check_money_suffix(findings, lines)
    check_like_something(findings, lines)
    check_repeated_you(findings, lines)
    check_dialogue_quotes(findings, lines)
    check_dialogue_stack(findings, lines)
    check_high_frequency_coverage(findings, text)
    check_short_genre_underbuilt_complete_article(findings, lines, text)
    check_short_genre_prose_block_compression(findings, lines, text)
    check_short_genre_diagnostic_date_title(findings, lines, text)
    check_short_genre_repair_stuffing(findings, lines, text)
    check_short_genre_standard_expansion_drift(findings, lines, text)
    check_short_genre_polished_minimalism(findings, lines, text)
    check_short_genre_period_grid(findings, lines, text)
    check_short_genre_present_action_anchor(findings, lines, text)
    check_short_genre_prompt_prop_too_early(findings, lines, text)
    check_short_genre_main_prop_title_loop(findings, lines, text)
    check_short_genre_literary_story_closure(findings, lines, text)
    check_short_genre_local_packet_loop(findings, lines, text)
    check_connector_overuse(findings, text)
    check_standard_prompt_prop_title_loop(findings, lines, text)
    check_diagnostic_title(findings, lines)
    check_high_signal_opening(findings, lines)
    check_feed_inventory_opening(findings, lines)
    check_standard_diary_length(findings, lines, text)
    check_standard_diary_formal_shape(findings, lines, text)
    check_learned_ending_button(findings, lines)
    check_ambient_ending(findings, lines)
    check_theme_density(findings, text)
    check_rough_self_damage(findings, text)
    check_material_echo(findings, text)
    check_prompt_chain_surface(findings, lines, text)
    check_time_archive_private_chain(findings, lines, text)
    check_mid_article_offaxis_gap(findings, lines, text)
    check_tasteful_withholding_ending(findings, lines)
    check_quiet_explanation(findings, lines)
    check_engine_signal_density(findings, text)
    check_sealed_nocturne(findings, text)
    check_period_comma_ratio(findings, lines)
    check_global_comma_density(findings, lines, text)
    check_standard_period_row_grid(findings, lines, text)
    check_generated_texture_overfill(findings, lines, text)
    check_illness_case_report_loop(findings, lines, text)
    check_illness_body_proof_overdensity(findings, lines, text)
    check_social_decline_room_texture_overfill(findings, lines, text)
    check_social_decline_plain_reply_private_loop(findings, lines, text)
    check_social_decline_scripted_return_gift(findings, lines, text)
    check_social_decline_group_fake_consequence(findings, lines, text)
    check_social_decline_tidy_etiquette_closure(findings, lines, text)
    check_social_decline_decoupled_consequence(findings, lines, text)
    check_social_decline_private_transfer_loop(findings, lines, text)
    check_social_decline_overextended_aftermath(findings, lines, text)
    check_third_person_narrator_slip(findings, lines, text)
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


def stop_lock_path(draft_path: Path) -> Path:
    digest = hashlib.sha256(str(draft_path.resolve()).encode("utf-8")).hexdigest()
    return Path(tempfile.gettempdir()) / "anlin-clean-run-locks" / f"{digest}.json"


def load_clean_run_state(draft_path: Path) -> dict:
    draft = draft_path.resolve()
    states: list[dict] = []
    for state_path in (draft.parent / ".anlin-clean-run-state.json", stop_lock_path(draft)):
        if not state_path.exists():
            continue
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if state.get("draft") == str(draft):
            states.append(state)
    for state in states:
        if state.get("stopped"):
            return state
    for state in states:
        if int(state.get("calls", 0)) == 0 and int(state.get("preflights", 0)) >= 3:
            return state
    return {}


def check_clean_run_stop_boundary(findings: list[Finding], draft_path: Path) -> None:
    """Block normal-checker bypass after the bounded clean-eval wrapper has stopped."""
    state = load_clean_run_state(draft_path)
    if not state:
        return
    stopped = bool(state.get("stopped")) or (int(state.get("calls", 0)) == 0 and int(state.get("preflights", 0)) >= 3)
    if not stopped:
        return
    findings.append(
        Finding(
            "error",
            "clean-eval停止边界越过",
            0,
            f"stop_reason={state.get('stop_reason')}, calls={state.get('calls')}, preflights={state.get('preflights')}",
            "当前 draft 已触发 clean-run 停止边界；不能切换到普通 checker 或继续修稿。若要做 finalized repair，请复制草稿到新的 finalized 工作目录并单独记录。",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deterministic Anlin-style hard-rule violations.")
    parser.add_argument("file", type=Path, help="Draft markdown/text file to inspect")
    parser.add_argument("--json", action="store_true", help="Output JSON findings")
    parser.add_argument("--strict", action="store_true", help="Promote blind-evaluation high-risk warnings to errors")
    parser.add_argument("--draft-gate", action="store_true", help="Promote generated-draft-only formal article gates; do not use for original-corpus calibration")
    parser.add_argument("--genre", default=None, help="Optional genre lock for formal evaluation: standard, sincere, micro-hope, or surreal")
    parser.add_argument("--corpus-dir", type=Path, default=None, help="Optional corpus directory for high-overlap copy gate")
    parser.add_argument("--copy-jaccard-threshold", type=float, default=0.16, help="5-gram Jaccard threshold for corpus copy gate")
    parser.add_argument("--copy-shared-24gram-threshold", type=int, default=2, help="Shared 24-character n-gram count threshold for corpus copy gate")
    parser.add_argument("--fail-on-warning", action="store_true", help="Return nonzero for warnings as well as errors")
    args = parser.parse_args()
    try:
        set_forced_genre(args.genre)
    except ValueError as error:
        parser.error(str(error))

    text = read_text_flexible(args.file)
    findings = collect_findings(text)
    check_clean_run_stop_boundary(findings, args.file)
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

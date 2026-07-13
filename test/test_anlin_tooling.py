from __future__ import annotations

import json
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CORPUS_ENV = os.environ.get("ANLIN_CORPUS_DIR")
CORPUS = Path(CORPUS_ENV) if CORPUS_ENV else Path("__ANLIN_CORPUS_DIR_NOT_SET__")
HAS_CORPUS = CORPUS_ENV is not None and CORPUS.is_dir()
CHECKER = ROOT / "scripts" / "check_anlin_violations.py"
BLIND_PREP = ROOT / "scripts" / "prepare_blind_test.py"
RUN_BLIND = ROOT / "scripts" / "run_blind_test.py"
BUILD_CARDS = ROOT / "scripts" / "build_corpus_cards.py"
BUILD_PROFILE = ROOT / "scripts" / "build_style_profile.py"
CHECK_PROFILE = ROOT / "scripts" / "check_style_profile.py"
CALIBRATE_PROFILE = ROOT / "scripts" / "calibrate_style_profile.py"
CLEAN_RUN_CHECKER = ROOT / "scripts" / "clean_run_checker.py"
PREPARE_FINALIZED_REPAIR_BRIEF = ROOT / "scripts" / "prepare_finalized_repair_brief.py"
CHECK_TRACE = ROOT / "scripts" / "check_clean_eval_trace.py"
SUMMARY_CHECKPOINTS = ROOT / "scripts" / "summarize_dev_checkpoints.py"
MERGE_SHORT_LINES = ROOT / "scripts" / "merge_short_lines.py"
SOFTEN_LINE_ENDINGS = ROOT / "scripts" / "soften_line_endings.py"
SPLIT_LONG_LINES = ROOT / "scripts" / "split_long_lines.py"
REBALANCE_LINE_RHYTHM = ROOT / "scripts" / "rebalance_line_rhythm.py"
CARDS = ROOT / "references" / "corpus-cards"
STYLE_PROFILE = ROOT / "references" / "style-profile.json"
BACKGROUND_FACT_CLASSES = ROOT / "references" / "background-fact-classes.json"
EVALS = ROOT / "evals" / "evals.json"
sys.path.insert(0, str(ROOT / "scripts"))
from check_anlin_violations import check_high_frequency_coverage, detect_style  # noqa: E402
from build_style_profile import split_title_body as split_style_title_body  # noqa: E402
from calibrate_style_profile import calibrate as calibrate_style_profile  # noqa: E402
from check_style_profile import SOFT_REVISE_FAMILY_THRESHOLD, read_json as read_style_profile  # noqa: E402
from clean_run_checker import (  # noqa: E402
    build_preflight_guidance,
    blocking_preflight_messages,
    generator_facing_contract,
    generator_facing_summary,
    normalize_before_final_check,
    post_checker_preflight_before_second_check,
    preflight_messages,
    soft_witness_matches,
)
from summarize_dev_checkpoints import classify_development_result, infer_genre_from_case_dir, summarize_gate  # noqa: E402


def short_sincere_prose_block_sample() -> str:
    return "\n".join(
        [
            "# 五月十二日",
            "",
            "手机屏幕亮着，微信对话框停在和妈妈的聊天界面，上一条消息还是她说天冷多穿点，我回了个好。",
            "今天是母亲节，朋友圈里很多人在发红包截图，配文妈妈辛苦了，我划过去，没点赞，也没评论。",
            "冰箱里还有上个月回家时她塞给我的一袋鸡蛋，塑料袋系得死紧，我到现在都没拆。",
            "我伸手去拿的时候，袋子底下粘着一点水，冰箱门被我撞了一下，冷气贴在小腿上。",
            "小时候下雨，她骑自行车送我上学，雨衣不够大，她把大半边让给我，自己肩膀全湿了。",
            "那条路后来修过很多次，我已经记不清坑在哪里，只记得她下车推车的时候鞋里灌了水。",
            "现在想想，那会儿她好像从来不觉得累，或者觉得累也不说，我只是坐在后座上嫌书包勒肩膀。",
            "我盯着屏幕看了很久，手指在键盘上敲了又删，打了妈，又删掉，又打了节日快乐。",
            "楼上有人拖椅子，声音很长，像一个人故意把家里的地板刮给全楼听。",
            "我关上冰箱，又打开，想着把鸡蛋煮两个，锅里却还有昨晚没洗的碗，油花贴在边上。",
            "她以前也会把这种碗泡很久，边泡边说等一下洗，最后还是自己站起来洗掉。",
            "我把碗挪到水槽里，水龙头先空响了两下，出来的水很细，冲不掉碗边那圈油。",
            "手机放在灶台旁边，输入框里还剩一个妈字，屏幕暗下去以后只剩一个黑边。",
            "我想把这句话补完，手又伸去拧水，袖口沾到一点冷水，贴在手腕上很久。",
            "窗外有车经过，声音很远，冰箱还在响，鸡蛋还在里面，塑料袋的结还是原来那个死结。",
            "最后我站起来，去厨房把鸡蛋从冰箱里拿出来，放在台面上，塑料袋还是没拆。",
            "明天吧，明天再说。",
        ]
    )


def finalized_hard_pass_profile_review_sample() -> str:
    return """去不了

垃圾袋在门口破了，
底下那道口子昨天就在渗，今天一拎整个顺着我手往下淌，
橘子皮、一撮吃剩的面、还有半张湿纸全滑到地上，
我蹲下去捡，指头缝里立马是那股泛酸的馊味，怎么捏都捏不干净，

刚捡了一半，手机在裤兜里亮起来，我腾不出一只干净手，只能拿手背去蹭屏幕，
蹭了两下才点亮。
是狗哥。
说下个月十六他结婚，让我一定过去，别推，

下面还压着一条四十几秒的语音，我手上全是油，那个键怎么按都划走，
连着两回，结果干脆没听，
就盯着那行字看，

十六号，一个星期六。
我先没回他，先拿油手在裤子上蹭了蹭去查票。
从这边过去没有直达，于是中间还得换一趟，高铁两百八，来回算下来快六百。
我又翻日历看那两天排得开排不开。
随礼这边关系不算最铁，可也是一个宿舍睡了四年的人，六百拿不出手，八百、一千，
我在心里来回摆。

手指在屏幕上戳，戳出来一个油乎乎的印子，我拿衣角去擦，越擦那块越花，
字都快看不清了。
先打了一句说最近在忙个项目，看着太假，删了。
改成可能赶不过去，又嫌太软。
来回改了三四遍，最后发出去的还是忙项目、去不了了、兄弟对不住。
发完就后悔那个对不住，像是先把自己说亏了。

他回得很快，就一个行字，隔了两秒又补了句让我忙完过来玩。
就这么两句，我反倒卡住了。
本来想打句恭喜新婚白头到老，打到一半觉得前面都说去不了了，这句显得多余，
停在输入框里没发。

我坐在地上，脚边这摊还没收拾，低头才发现自己哪忙了，
就这么蹲着捡了半天垃圾，

转头跟人说在忙项目。
心里那点东西往下坠了一下。
大二那年寒假，因为卡里就剩几十块回不去，是他先替我垫的车票，
说等我方便再给。

后来钱是还了，一顿饭还的，可那顿饭最后好像也是他抢着付的。
其实这么一想，反倒更别扭。
我点开转账，输了两百盯了两秒删掉，改成五百，手指停在确认上没敢按下去。
两百显得寒碜，五百又像是花钱给自己买个心安。
发过去他准觉得我拿钱堵嘴，不发又像真把那回事忘得干干净净。

反正也拿不定那个数，金额框空在那儿，光标一闪一闪，我到底还是退了出来。
破袋子从中间又系了一道，勉强兜住底下，拎起来还是往下滴。
拎到楼道口，对门阿姨正好出来倒水，看了一眼地上那道水迹，又看看我手。
我说了句这袋子破了，声音含糊得自己都听着别扭，手上味还没洗，
她想搭把手扶下门，我也没敢伸。

她哦了一声，绕开那道印子下楼去了。
我站在原地又拿手背蹭了下裤子，那味蹭上去也没散。
我把袋子拎回门口又放下了，这个点下去倒垃圾，楼道声控灯还得跺半天脚。
手上这股味一直没去洗。
狗哥那条已经显示已读，没再冒出新的。
破袋子歪在鞋跟边上，底下洇出来一小片，我看着那片，没起身。
"""


def finalized_profile_repair_brief(
    *,
    repair_mode: str = "punctuation_source_reset",
    root_families: str = "punctuation, ngram_texture",
    next_action: str = "Punctuation is a source-shape problem here.",
    source_actions: tuple[str, ...] = (
        "punctuation: let punctuation follow unfinished action inside the selected rows.",
    ),
) -> str:
    lines = [
        "Anlin style-profile repair brief",
        "status: review",
        "checkpoint_pass: false",
        "formal_gate: not_pass",
        f"repair_mode: {repair_mode}",
        f"root_families: {root_families}",
        f"next_repair_action: {next_action}",
    ]
    if source_actions:
        lines.append("source_actions:")
        lines.extend(f"  - {action}" for action in source_actions)
    return "\n".join(lines)


def short_sincere_period_grid_sample() -> str:
    return "\n".join(
        [
            "# 拖着",
            "",
            "右脚的拖鞋带子断了。",
            "那个塑料扣松了，走两步就滑出来。",
            "断了一半。",
            "得拖着走，不然鞋子会掉。",
            "在屋里走了几个来回。",
            "去厨房倒水，右脚抬起来的时候，拖鞋留在原地。",
            "又弯下腰去穿，穿上走了三步，又掉了。",
            "有点烦。",
            "但也不想蹲下来修它。",
            "那个扣子本来就是坏的，买了没多久就松了。",
            "平时也不太注意，今天突然就觉得受不了了。",
            "可能因为屋里太安静了。",
            "那个拖地的声音特别大。",
            "手机亮了一下。",
            "锁屏上写着五月十二号，周日。",
            "底下还有一行小字，母亲节。",
            "看了两眼。",
            "解锁，又锁上。",
            "想发点什么，打了两个字又删了。",
            "我妈不怎么用微信，朋友圈也不发。",
            "去年教她用，教了半天，她记不住，后来就算了。",
            "平时打打电话，每次也就几分钟。",
            "她问吃了没有，我说吃了。",
            "问工作累不累，我说还行。",
            "然后就没什么好说的了。",
            "但是也不知道说什么。",
            "有时候给她转钱，她也不收。",
            "说你一个人在外面，自己留着花。",
            "厨房台子上放着上次从家里带回来的鸡蛋。",
            "塑料袋扎着口，放在角落里。",
            "那天走的时候她非要装。",
            "我说够了够了，她还是往袋子里又塞了两个。",
            "说放在冰箱里，早上煮一个吃。",
            "后来打开看，里面有八个。",
            "当时想拍张照片发给她，说收到了。",
            "后来忙着忙着也忘了。",
            "已经过去好几天了。",
            "大概已经有坏的了。",
            "小时候下雨，她骑车送我上学。",
            "那条路后来修过很多次。",
            "我已经记不清坑在哪里。",
            "只记得她下车推车的时候鞋里灌了水。",
            "当时我坐在后座上。",
            "书包勒着肩膀。",
            "她说快到了。",
            "后来我也没问她冷不冷。",
            "握着杯子站在厨房，水是凉的。",
            "拖鞋又掉了。",
            "没捡。",
            "明天要是记得就刷一下。",
        ]
    )


def short_sincere_expanded_repair_sample() -> str:
    return "\n".join(
        [
            "# 拖着",
            "",
            "右脚的拖鞋带子断了。",
            "那个塑料扣松了，走两步就滑出来。",
            "断了一半，得拖着走，不然鞋子会掉。",
            "在屋里走了几个来回。",
            "去厨房倒水，右脚抬起来的时候，拖鞋留在原地。",
            "弯下腰去穿，穿上走了三步，又掉了。",
            "脚趾头磕在门槛上，疼得嘶了一声。",
            "有点烦。",
            "但也不想蹲下来修它。",
            "那个扣子本来就是坏的，买了没多久就松了，一直没换。",
            "平时也不太注意，今天突然就觉得受不了了。",
            "可能因为屋里太安静了，那个拖地的声音特别大。",
            "走在瓷砖上，啪嗒啪嗒的。",
            "好像整个房间都在响。",
            "手机亮了一下。",
            "锁屏上写着五月十二号，周日。",
            "底下还有一行小字，母亲节。",
            "看了两眼，解锁，又锁上。",
            "想发点什么，打了两个字又删了。",
            "不小心按了发送，发了个哭脸，撤回也来不及了。",
            "以为是她发来的消息，点开看只是日历提醒。",
            "我妈不怎么用微信，朋友圈也不发。",
            "去年教她用，教了半天，她记不住，就算了。",
            "平时打打电话，每次也就几分钟。",
            "她问吃了没有，我说吃了。",
            "问工作累不累，我说还行。",
            "然后就没什么好说的了。",
            "挂了电话又想，是不是应该说点别的。",
            "好像听见她叹了口气，又好像没有。",
            "但是也不知道说什么。",
            "有时候给她转钱，她也不收。",
            "说你一个人在外面，自己留着花。",
            "多买点好吃的。",
            "我回了个笑脸，其实打了一串字又删了。",
            "敲门声突然响了。",
            "是隔壁的老王。",
            "他端着一碗刚煮好的面，问我有没有盐。",
            "我愣了一下，说有，转身去拿。",
            "拖鞋又差点绊倒，他伸手扶了一下。",
            "我把盐递过去，他笑了笑，说谢了。",
            "关上门，手心还沾着面粉。",
            "忽然想起小时候我妈也这样借过盐。",
            "不过那时候她会多送一碗汤。",
            "他低头看了一眼我的拖鞋，没说话。",
            "我却觉得脚趾头缩了一下，好像被他看穿了什么。",
            "脱口而出，我妈买的。",
            "说完就后悔了，脸有点热。",
            "他愣了一下，说，你妈对你真好。",
            "我点点头，没接话。",
            "其实想说她不在了，但没说出口。",
            "他转身的时候又说，你这拖鞋该换了。",
            "我笑了笑，说习惯了。",
            "握着杯子站在厨房。",
            "水是凉的。",
            "喝了一口，不太想喝了。",
            "拖鞋又掉了，没捡，就这么穿着。",
            "半个脚掌踩在地上。",
            "凉丝丝的。",
            "站了一会儿，脚底有点凉了。",
            "把脚缩回来，踩在另一只拖鞋上。",
            "杯子搁在台子上，没喝完。",
            "手一抖，杯子差点掉地上，水洒了一地。",
            "回房间的时候，右脚的拖鞋又滑出来一次。",
            "懒得管了，走了两步，左脚那只也开始松了。",
            "猛地发现脚底有点脏，没穿袜子。",
            "蹲下来想擦一下，膝盖咔嚓响了一声。",
            "走到门口的时候停了一下。",
            "鞋架上放着上次回来穿的那双鞋。",
            "鞋帮边上蹭了一块泥，一直没擦。",
            "蹲下来看了看，也没擦，又站起来了。",
            "明天要是记得就刷一下，但也不一定。",
            "其实心里清楚，明天还是会忘。",
            "转身的时候，拖鞋又掉了一次。",
            "弯腰去捡，手机又亮了。",
            "没理它，继续往房间走。",
            "忽然想起还没转钱，打开支付宝。",
            "网络卡了一下，转了半天没转出去。",
            "最后也没转成。",
            "把手机扔到沙发上，去洗了个手。",
        ]
    )


def standard_prompt_prop_title_loop_sample(title: str = "# 备注") -> str:
    return "\n".join(
        [
            title,
            "",
            "外卖袋放在门口的时候，我还以为漏汤了，",
            "蹲下去看，先看到小票上的备注。",
            "不要香菜四个字印得很黑，",
            "比我今天任何一句话都像正事。",
            "骑手站在楼道口等我确认收货，",
            "我手上还沾着洗碗的油。",
            "朋友圈里有人晒情人节礼物，",
            "玫瑰插在那种透明袋子里，看起来很会活。",
            "我点的麻辣烫倒是不透明，",
            "透明的是汤从袋子底下渗出来的路线。",
            "其实我备注了两遍不要香菜，",
            "下单的时候还检查了一遍，像在给命运发工单。",
            "结果打开盖子，香菜浮在上面，",
            "绿得很有单位归属感。",
            "我把筷子伸进去挑，",
            "挑了半天，挑出来的全是粉丝。",
            "骑手还没走，问是不是有问题。",
            "我说没事，声音小得像优惠券过期。",
            "他哦了一声，电梯正好上来，",
            "门开的时候里面有个阿姨拎着垃圾袋。",
            "垃圾袋碰到我的裤腿，",
            "我往后退了一下，汤袋又擦到鞋面。",
            "那一下挺丢人的，",
            "人还没吃上饭，先像被节日收拾了一遍。",
            "这反应挺恶心的，",
            "像系统把两个毫不相关的错误合并报了。",
            "阿姨看了我一眼，",
            "又看了看我手里那碗绿的东西。",
            "我说不用进不用进，",
            "结果她往旁边让了一步，我反而卡在门口。",
            "楼道灯闪了两下，",
            "我的手心被塑料袋勒出一道白印。",
            "备注贴在袋子侧面，",
            "被汤泡得翘起来，像一块很小的失败证明。",
            "手机又亮了一下，",
            "是店家自动发的评价提醒。",
            "上面写亲亲记得五星，",
            "我看着那个亲亲，觉得今天的中文有点不守法。",
            "我本来想打电话说一下，",
            "号码拨出去又挂了。",
            "因为一想到要解释香菜这件事，",
            "嘴里已经先有了香菜味。",
            "房间里水槽还没冲干净，",
            "碗边那圈油贴着白瓷，像不肯下班。",
            "我把香菜挑到小票上，",
            "小票吸了汤，备注那一行慢慢糊掉。",
            "筷子尖沾着一点绿色，",
            "放到桌上又把桌面染出一条细线。",
            "我抽纸去擦，",
            "擦完发现纸盒也空了。",
            "朋友圈那张玫瑰照又被人点赞，",
            "红点挂在屏幕上，很小，也很稳。",
            "我吃了一口，",
            "香菜味从牙缝里冒出来。",
            "备注还在小票上，",
            "但已经看不清了。",
            "我拿纸去擦，",
            "纸一碰就破，香菜粘在手指上。",
            "最后我把小票揉成一团，",
            "丢进垃圾桶的时候没丢准。",
            "它掉在地上，",
            "备注朝上。",
        ]
    )


class AnlinToolingTests(unittest.TestCase):
    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_checker_has_no_hard_errors_on_original_corpus(self) -> None:
        self.assertTrue(CORPUS.is_dir(), f"missing corpus: {CORPUS}")
        originals = sorted(CORPUS.glob("*.md"))
        self.assertEqual(len(originals), 38)

        failures: list[str] = []
        for path in originals:
            for mode in (["--json"], ["--json", "--strict"]):
                result = subprocess.run(
                    [sys.executable, str(CHECKER), str(path), *mode],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                findings = json.loads(result.stdout)
                errors = [item for item in findings if item["severity"] == "error"]
                if errors:
                    failures.append(f"{path.name} {' '.join(mode)}: {errors}")
        self.assertEqual(failures, [])

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_checker_draft_gate_keeps_fragment_advisories_as_warnings_on_originals(self) -> None:
        self.assertTrue(CORPUS.is_dir(), f"missing corpus: {CORPUS}")
        originals = sorted(CORPUS.glob("*.md"))
        self.assertEqual(len(originals), 38)

        promoted: list[str] = []
        for path in originals:
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(path), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            targeted = [
                item
                for item in findings
                if "中段旁逸不足" in item["rule"] or "粗粝自毁信号不足" in item["rule"]
            ]
            if any(item["severity"] == "error" for item in targeted):
                promoted.append(f"{path.name}: {targeted}")
        self.assertEqual(promoted, [])

    def test_checker_flags_prompt_shape_risks_without_hard_failure(self) -> None:
        body = "\n".join(
            [
                "# 春招日寄",
                "",
                "群里又在聊入职体检。",
                "我躺在床上点开群看了一眼。",
                "满屏都是租房补贴几号发。",
                "室友说他签了大厂 offer。",
                "我说哦。",
                "",
                *(["今天有点热。"] * 70),
                "",
                "哦。",
                "关屏。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            severities = {item["rule"]: item["severity"] for item in findings}
            self.assertTrue(any("题面诊断型标题" in rule for rule in rules))
            self.assertTrue(any("题面高信号开头" in rule for rule in rules))
            self.assertTrue(any("标准日寄完整文章篇幅偏短" in rule for rule in rules))
            self.assertTrue(any("习得式结尾按钮" in rule for rule in rules))
            self.assertTrue(any("行末逗号比例" in rule for rule in rules))
            self.assertTrue(all(severity != "error" for severity in severities.values()))
            length_findings = [
                item
                for item in findings
                if item["rule"] in {"标准日寄完整文章篇幅偏短", "标准日寄完整文章篇幅缓冲不足"}
            ]
            self.assertTrue(length_findings)
            self.assertTrue(all("carrier" not in item["suggestion"].lower() for item in length_findings))
            self.assertTrue(any("fragment" in item["suggestion"].lower() for item in length_findings))

    def test_checker_rejects_process_leakage(self) -> None:
        body = "\n".join(
            [
                "# 草拟",
                "",
                "**State Card（内部）：**",
                "- driver：春招失败",
                "",
                "日寄",
                "",
                "今天没什么事。",
                "",
                "---",
                "校验通过：Jaccard 0.01。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            errors = [item for item in findings if item["severity"] == "error"]
            self.assertTrue(any("过程说明泄漏" in item["rule"] for item in errors))

    def test_checker_rejects_protocol_preamble_leakage(self) -> None:
        body = "\n".join(
            [
                "This is the second checker call — per protocol, I must stop all tool use.",
                "Here is the article:",
                "",
                "日寄",
                "",
                "今天没什么事。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            errors = [item for item in findings if item["severity"] == "error"]
            self.assertTrue(any("过程说明泄漏" in item["rule"] for item in errors))

    def test_checker_rejects_chinese_generation_process_leakage(self) -> None:
        body = "\n".join(
            [
                "现在构建状态卡并起草。",
                "检查器发现三个硬伤，需要重写。",
                "最后一次修复。",
                "",
                "日寄",
                "",
                "今天没什么事。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            errors = [item for item in findings if item["severity"] == "error"]
            self.assertTrue(any("过程说明泄漏" in item["rule"] for item in errors))

    def test_checker_reads_utf16_drafts_from_windows_tools(self) -> None:
        body = "# 日寄\n\n手机充电口又松了。\n"
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-16")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            self.assertIsInstance(findings, list)

    def test_checker_flags_theme_density_and_tasteful_withholding(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "offer 邮件在桌上。",
                "同学群聊入职体检和租房补贴，",
                "大厂工位有水杯，公积金也到账了，",
                "boss 直聘上招聘岗位和职位描述都写着抗压，",
                "hr 说简历还在看。",
                "",
                "我把手机放下。",
                "没点开。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertTrue(any("单主题词密度偏高" in rule for rule in rules))
            self.assertTrue(any("题面链条过于完整" in rule for rule in rules))
            self.assertTrue(any("文艺悬停式结尾" in rule for rule in rules))
            self.assertTrue(all(item["severity"] != "error" for item in findings))

    def test_checker_flags_short_line_poem_surface_without_strict_failure(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                *("我坐着。", "灯亮了。", "风很小。", "饭冷了。", "群响了。", "我没动。") * 30,
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("短行诗化表面" in item["rule"] for item in findings))
            self.assertFalse(any(item["rule"] == "strict: 短行诗化表面" for item in findings))

    def test_checker_rejects_compressed_prose_blocks_in_strict_mode(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "充电线脏了，接口那里有黑色的垢，用指甲抠了抠，没抠掉。好像从上个月就这样了，一直没注意。充电的时候接触不良，得按着才能充进去。手机电量百分之三十七，充了半小时还是三十七。",
                "",
                "室友说他过了腾讯，我正在打游戏，团战输了，他说到时候一起去深圳，我说再说吧。其实我连深圳在哪个方向都不知道，他说深圳机会多，我说嗯，然后又点开招聘页面看了一眼。",
                "",
                "同学群里在聊体检和补贴，我设置了消息免打扰。打开看了一次，群里又刷到租房、入职、报到、体检，像一张表格从手机里倒出来，每一格都不是我的。",
                "",
                "楼下买泡面，收银员问毕业了没，我说快了。她说现在工作不好找吧，我说嗯。硬币掉到货架底下，我蹲下去捡，看见底下还有别人掉的硬币，积了灰。",
                "",
                "手机屏幕使用时间七小时四十二分钟，其中招聘占了三小时。系统建议我适当休息，我点了忽略。后来梦到面试官问职业规划，我说希望在平台里成长，说完自己先醒了。",
                "",
                "小卖部老板娘说现在年轻人都不容易，我说还行。她把塑料袋递给我的时候又问了一句，你们学校是不是马上毕业，我说嗯。泡面桶烫手，我换了一只手拿，汤从封口那里漏出来一点。",
                "",
                "回去路上看见一个快递柜在报警，声音很小，像有人在柜子里叹气。我站那儿看了两秒，觉得自己如果被塞进去，可能也会显示取件码过期。",
                "",
                "室友回来以后问我吃不吃水果，我说不吃，后来还是拿了一个最小的苹果，咬下去很酸，牙齿被冻了一下。",
                "",
                "醒了，枕头湿了一块。不知道是汗还是口水。微信有人问找到工作没，我回在看。他发了个红包，我领了八毛八。充电线还是脏的，手机只剩百分之十二，得按着才能充进去。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 散文块压缩" for item in findings))

    def test_checker_flags_clean_observation_and_ambient_ending(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "充电器的口松了，桌角有个拉环，抠了半天没抠出来。",
                "室友还没回来，桌上那份邮件开头写着恭喜。",
                "点开招聘刷了刷，角标99+，每条都显示已送达。",
                "微信群在刷，有人发名单，有人回收到。",
                "下楼买了份卤肉饭，微波炉转一分半，米饭还是硬。",
                "胃有点疼，吃了一片奥美拉唑，还剩最后一片，明天记得买。",
                "厕所灯坏了两天，第三次用扫把柄戳的，亮了。",
                "空调师傅说不加氟也行，就是启动慢一点。",
                "打开备忘录，某厂一面挂，某厂笔试挂，某厂没下文。",
                "室友问要不要内推，我说到时候看看吧。",
                "他打开空调调到24，我看了一眼，把我的调到26。",
                "胃还是有点疼，奥美拉唑还剩最后一片，明天记得下楼买。",
                "手机放枕头边，屏幕朝下。",
                "我把校招群免打扰，又点开，像欠了它两百块。",
                "桌上的塑料袋被风吹起来，我以为是室友回来了，抬头看了一眼，没有人。",
                "我把杯子拿去洗，水龙头先咳了一下，喷到裤子上。",
                "群里有人问体检报告要不要彩印，下面三个人回了不用。",
                "我把那条消息看完，回到招聘页面，发现刚才投的岗位已经变灰。",
                "老板直聘的头像排成一列，每个都像刚从会议室里出来。",
                "我又看了一眼邮件，恭喜两个字还是很亮，亮得像不是写给人的。",
                "室友回来时带了一袋水果，问我吃不吃，我说不吃，过了十分钟拿了一个最小的。",
                "苹果有点酸，我咬了一口，牙齿被冻了一下。",
                "我想起下午面试官问职业规划，我说希望在平台里成长。",
                "说完自己也听见了，像把别人简历上的字偷出来贴在嘴上。",
                "洗完澡出来，镜子起雾，我用手背擦了一条，脸在里面分成两半。",
                "一半像刚睡醒，一半像刚从会议纪要里逃出来。",
                "我把那条内推消息又看了一遍，输入框里打了谢谢，删掉，又打麻烦你了。",
                "最后只发了一个表情，那个表情看起来比我本人有礼貌。",
                "室友在阳台打电话，说下个月要先住公司附近，通勤别超过四十分钟。",
                "我在屋里查从这里到那个园区要多久，地图给我三条路线，每条都像绕开我。",
                "窗台上有一只死掉的小飞虫，我吹了一下，它没动。",
                "我忽然想起来下午还有一份测评没做，链接过期了。",
                "空调外机嗡嗡嗡。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertTrue(any("粗粝自毁信号不足" in rule for rule in rules))
            self.assertTrue(any("纯环境音结尾" in rule for rule in rules))
            self.assertTrue(any("材料钩子重复过直" in rule for rule in rules))

    def test_checker_flags_repeated_ambient_refrain_as_material_echo(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "窗外的空调外机一直响着。",
                "我把杯子拿去洗，水龙头先咳了一下，喷到裤腿上。",
                "窗外的空调外机一直响着。",
                *(["其实我觉得厕所灯突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"] * 34),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("材料钩子重复过直" in item["rule"] for item in findings))

    def test_checker_draft_gate_promotes_quiet_standard_diary_risks(self) -> None:
        body = "\n".join(["# 日寄", "", *(["杯子脏了。"] * 180)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            rough = [item for item in findings if "粗粝自毁信号不足" in item["rule"]]
            self.assertTrue(rough, findings)
            self.assertFalse(any(item["severity"] == "error" for item in rough), rough)
            self.assertTrue(any(rule == "strict: 短行诗化表面" for rule in rules))

    def test_checker_draft_gate_rejects_short_standard_diary_even_without_riji_title(self) -> None:
        lines = [
            "空调外机又开始响了，脚踝从骨头缝里往外顶。",
            "扶着柜子挪到厨房，冰箱里半瓶可乐，两盒腐乳。",
            "灯管闪了一下才亮全，我把手机按亮，又按灭。",
            "页面上写着富贵病三个字，问号被我看漏了。",
            "女的在楼道里看了我一眼，又看了一眼我的拖鞋。",
            "我拎着垃圾袋往下挪，汤水顺着墙往下淌。",
        ] * 7
        body = "\n".join(["# 半瓶可乐", "", *lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(
                any(rule == "strict: 标准日寄完整文章篇幅缓冲不足" for rule in rules),
                rules,
            )

    def test_checker_draft_gate_rejects_very_short_standard_attempt_without_riji_title(self) -> None:
        lines = [
            "脚踝在被子里动了一下，手机从枕头边滑下去。",
            "楼下有人关门，我以为是我的骨头响。",
            "冰箱里剩半瓶可乐，我看了很久。",
            "屏幕上那个词又跳出来，像欠费通知。",
            "我扶着墙去倒水，拖鞋把水踩成一条线。",
        ] * 5
        body = "\n".join(["# 半瓶可乐", "", *lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(
                any(rule == "strict: 标准日寄完整文章篇幅偏短" for rule in rules),
                rules,
            )

    def test_checker_draft_gate_does_not_force_mothers_day_sincere_short_form_into_standard_length(self) -> None:
        body = "\n".join(
            [
                "# 不想祝我妈母亲节快乐",
                "",
                "早上我妈发来一个表情。",
                "一朵花，红得像楼下水果摊没卖完的塑料袋。",
                "我看了半天，没回。",
                "我知道可以回一句快乐。",
                "手指停在键盘上，又退回去了。",
                "她以前下雨天给我送伞，鞋底进水，",
                "到教室门口还先把伞上的水甩干。",
                "我那时候只觉得丢人。",
                "现在想起来，丢人的地方还是我。",
                "她如果没有生我，可能会过得轻一点。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertFalse(any("标准日寄完整文章篇幅" in rule for rule in rules), rules)
            self.assertFalse(any("标准日寄行数" in rule for rule in rules), rules)

    def test_checker_infers_sincere_from_mother_care_memory_cluster_without_diagnostic_title(self) -> None:
        body = "\n".join(
            [
                "# 鸡蛋",
                "",
                "手机屏幕亮着，朋友圈里有人发康乃馨，",
                "我看了几秒，没有给妈妈发消息。",
                "上次回家，她煮了一袋鸡蛋让我带走，",
                "背包侧面的网兜鼓起来，像长了个瘤子。",
                "小时候下雨，她骑自行车送我上学，",
                "我穿着她的雨衣，风一吹就鼓起来。",
                "到了校门口，她头发全湿了，",
                "还让我快进去。",
                "我现在想给她发点什么，",
                "手指停在发送键旁边，又放下了。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertFalse(any("标准日寄完整文章篇幅" in rule for rule in rules), rules)
            self.assertFalse(any("高频词覆盖不足" in rule for rule in rules), rules)
            self.assertFalse(any("呼吸点缺失" in rule for rule in rules), rules)
            self.assertFalse(any("粗粝自毁信号不足" in rule for rule in rules), rules)

    def test_clean_run_preflight_uses_short_genre_gate_for_sincere_mother_memory(self) -> None:
        body = "\n".join(
            [
                "# 鸡蛋",
                "",
                "手机屏幕亮着，朋友圈里有人发康乃馨，",
                "我看了几秒，没有给妈妈发消息。",
                "上次回家，她煮了一袋鸡蛋让我带走，",
                "背包侧面的网兜鼓起来，像长了个瘤子。",
                "小时候下雨，她骑自行车送我上学，",
                "我穿着她的雨衣，风一吹就鼓起来。",
                "到了校门口，她头发全湿了，",
                "还让我快进去。",
                "我现在想给她发点什么，",
                "手指停在发送键旁边，又放下了。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertFalse(any("< 900" in message for message in messages), messages)
            self.assertFalse(any("short_breath" in message for message in messages), messages)
            self.assertFalse(any("rough_self_damage" in message for message in messages), messages)

    def test_checker_does_not_promote_sincere_family_theme_density_as_standard_diary_error(self) -> None:
        lines = [
            "手机屏幕亮着，朋友圈里有人发康乃馨，妈妈的头像还在下面。",
            "上次回家，妈妈煮了一袋鸡蛋让我带走，鸡蛋在背包里一直晃。",
            "小时候下雨，妈妈骑车送我上学，我穿着她的雨衣。",
            "雨衣太大，风一吹就鼓起来，鸡蛋后来在桌上放凉。",
        ] * 4
        body = "\n".join(["# 鸡蛋", "", *lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule.startswith("短体裁主题集中: family") for rule in rules), rules)
            self.assertFalse(any(rule.startswith("strict: 单主题词密度偏高: family") for rule in error_rules), error_rules)

    def test_checker_warns_on_short_sincere_polished_minimalism_without_standard_gate(self) -> None:
        body = "\n".join(
            [
                "# 母亲节",
                "",
                "空调按了几下才关掉，",
                "电池仓还是松的",
                "我把后盖推回去，",
                "房间里还是闷着",
                "",
                "米饭热了一遍",
                "榨菜还剩半袋",
                "我端着碗坐在床边，",
                "手机亮了一下",
                "朋友圈都是母亲节的图，",
                "花和合照挤在一起",
                "我划过去没有点开",
                "米饭有一点硬",
                "吃着想起上次回家，",
                "我妈塞了一袋鸡蛋",
                "塑料袋裹了两层",
                "她说路上别压碎了，",
                "我说好",
                "她没提今天是什么日子，",
                "",
                "楼下有人跳广场舞，",
                "喇叭声断断续续，",
                "抽油烟机盖掉一半，",
                "快递提醒又亮起来，",
                "昨天就该取的，",
                "我把它划掉，",
                "",
                "鸡蛋还剩四个，",
                "有一个裂了，",
                "蛋壳上有一小块灰，",
                "应该是塑料袋磨的，",
                "裂的那个也没坏，",
                "我还是煮了，",
                "水龙头开了很久，",
                "热水才出来，",
                "隔壁门响了一下，",
                "钥匙转了两圈，",
                "",
                "小时候下雨，",
                "她送我上学，",
                "雨鞋在田埂上很滑，",
                "她一直拉着我，",
                "手掌上有裂口，",
                "到校门口的时候，",
                "她裤腿湿了一半，",
                "她没说什么，",
                "把我送进去就走了，",
                "我那时候没有回头，",
                "",
                "手机又亮了，",
                "我把屏幕翻过去。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any("短体裁整齐散文" in rule for rule in rules), rules)
            self.assertTrue(any("短体裁整齐散文" in rule for rule in error_rules), error_rules)
            self.assertFalse(any("标准日寄完整文章篇幅" in rule for rule in error_rules), error_rules)

    def test_checker_warns_on_short_sincere_literary_story_closure(self) -> None:
        body = "\n".join(
            [
                "# 鸡蛋",
                "",
                "手机从早上亮到中午，朋友圈里全是康乃馨和月亮表情。",
                "我把屏幕扣在桌上，没给我妈发消息，",
                "因为手上还有洗洁精的味道，",
                "碗里那点油被冷水冲了半天还在。",
                "",
                "冰箱里有她上次塞给我的鸡蛋，",
                "塑料袋打了两个结，像怕我在路上把生活过碎一样。",
                "我拆的时候有一个壳裂了，",
                "蛋清没有流出来，",
                "只是裂缝卡了一点灰。",
                "",
                "小时候下雨，她骑车送我上学，雨衣罩在我身上，",
                "我坐在后座，觉得自己像一袋要被退货的米。",
                "到校门口她裤腿湿了一半，",
                "还让我快进去，",
                "我那时候只嫌她车铃太响。",
                "",
                "中午水烧开了，",
                "鸡蛋在锅里碰来碰去，",
                "手机又亮了一次。",
                "我看见输入框里只剩一个节日快乐，",
                "删掉以后，",
                "厨房反而安静了。",
                "",
                "裤子上的水印还在，拖鞋也是反的。",
                "我没有换。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any("短真诚小小说闭合" in rule for rule in rules), rules)
            self.assertTrue(any("短真诚小小说闭合" in rule for rule in error_rules), error_rules)
            self.assertFalse(any("标准日寄完整文章篇幅" in rule for rule in rules), rules)

    def test_clean_run_preflight_flags_short_sincere_literary_story_closure(self) -> None:
        body = "\n".join(
            [
                "# 鸡蛋",
                "",
                "手机屏幕亮着，朋友圈里有人发康乃馨，",
                "我看了几秒，没有给妈妈发消息。",
                "上次回家，她煮了一袋鸡蛋让我带走，塑料袋在背包里晃了一路。",
                "袋子口打得很紧，",
                "我拆的时候还把指甲掰了一下。",
                "小时候下雨，她骑自行车送我上学，雨衣罩在我身上，风一吹就鼓起来。",
                "到了校门口，她头发全湿了，还让我快进去。",
                "我那时候只觉得雨衣太丑，",
                "像一只被批发来的青蛙。",
                "我现在想给她发点什么，手指停在发送键旁边，又放下了。",
                "冰箱里的鸡蛋还剩四个，有一个裂了，蛋壳上有一小块灰。",
                "水烧开以后，厨房里全是白汽。",
                "锅盖被顶得咔咔响，",
                "我站在旁边看它响完。",
                "裤子上的水印还在，拖鞋也是反的。",
                "我没有换。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(any(message.startswith("short_genre_literary_story_closure=") for message in messages), messages)

    def test_clean_run_preflight_short_sincere_closure_demands_family_cut(self) -> None:
        body = "\n".join(
            [
                "# 鸡蛋",
                "",
                "手机屏幕亮着，朋友圈里有人发康乃馨，",
                "我看了几秒，没有给妈妈发消息。",
                "上次回家，她煮了一袋鸡蛋让我带走，塑料袋在背包里晃了一路。",
                "袋子口打得很紧，",
                "我拆的时候还把指甲掰了一下。",
                "小时候下雨她送我上学，雨衣给我穿，那把破伞断了一根。",
                "雨水顺着伞骨漏到她背上，她说没事，马上到了学校。",
                "我那时候只觉得雨衣太丑，",
                "像一只被批发来的青蛙。",
                "我现在想给她发点什么，手指停在发送键旁边，又放下了。",
                "冰箱里的鸡蛋还剩四个，有一个裂了，蛋壳上有一小块灰。",
                "水烧开以后，厨房里全是白汽。",
                "锅盖被顶得咔咔响，",
                "我站在旁边看它响完。",
                "裤子上的水印还在，拖鞋也是反的。",
                "我没有换。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertIn("CLEAN_RUN_PREFLIGHT", result.stdout)
            self.assertIn("cut one proof family completely", result.stdout)
            self.assertIn("childhood-rain/raincoat/school line is still a full memory prop", result.stdout)
            self.assertIn("no-message + eggs + childhood-rain", result.stdout)

    def test_checker_flags_short_sincere_main_prop_title_loop(self) -> None:
        body = "\n".join(
            [
                "# 一袋鸡蛋",
                "",
                "水槽里那个碗翻不过来，",
                "底下有一圈油，冷水冲了半天还在。",
                "我手背被洗洁精泡得有点红，",
                "袖口也湿了。",
                "手机在旁边亮了一下，",
                "朋友圈里都是母亲节。",
                "我没有点开。",
                "上次回家，我妈塞给我一袋鸡蛋，塑料袋结打得很紧，",
                "路上鸡蛋在包里碰来碰去。",
                "我拎到车站的时候，袋子勒在手指上，",
                "那道红印到晚上还没消。",
                "小时候下雨，她骑车送我上学，雨衣往我这边偏，",
                "她肩膀湿了一路。",
                "到校门口她把书包递给我，",
                "我嫌书包带上全是水，皱了一下眉。",
                "我现在想给她发点什么，",
                "打了一个妈字又删掉。",
                "锅里的水开了，",
                "鸡蛋在里面撞了两下。",
                "有一个壳裂了，白沫浮起来，",
                "我拿筷子戳了一下，像在确认它还能不能装作完整。",
                "楼道里有人关门，",
                "我把手机扣过去。",
                "最后那袋鸡蛋还在台面上，",
                "塑料袋的结没有拆开。",
                "袖口贴着手腕，",
                "我也没有换衣服。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            findings = json.loads(result.stdout)
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            suggestions = "\n".join(item["suggestion"] for item in findings)
            self.assertTrue(any("短真诚标题物件闭环" in rule for rule in error_rules), error_rules)
            self.assertIn("重选侧面动作", suggestions)

    def test_clean_run_preflight_flags_short_sincere_main_prop_title_loop(self) -> None:
        body = "\n".join(
            [
                "# 一袋鸡蛋",
                "",
                "水槽里那个碗翻不过来，",
                "底下有一圈油，冷水冲了半天还在。",
                "我手背被洗洁精泡得有点红，",
                "袖口也湿了。",
                "手机在旁边亮了一下，",
                "朋友圈里都是母亲节。",
                "我没有点开。",
                "上次回家，我妈塞给我一袋鸡蛋，塑料袋结打得很紧，",
                "路上鸡蛋在包里碰来碰去。",
                "我拎到车站的时候，袋子勒在手指上，",
                "那道红印到晚上还没消。",
                "小时候下雨，她骑车送我上学，雨衣往我这边偏，",
                "她肩膀湿了一路。",
                "到校门口她把书包递给我，",
                "我嫌书包带上全是水，皱了一下眉。",
                "我现在想给她发点什么，",
                "打了一个妈字又删掉。",
                "锅里的水开了，",
                "鸡蛋在里面撞了两下。",
                "有一个壳裂了，白沫浮起来，",
                "我拿筷子戳了一下，像在确认它还能不能装作完整。",
                "楼道里有人关门，",
                "我把手机扣过去。",
                "最后那袋鸡蛋还在台面上，",
                "塑料袋的结没有拆开。",
                "袖口贴着手腕，",
                "我也没有换衣服。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("short_genre_main_prop_title_loop=") for message in messages),
                messages,
            )

    def test_checker_draft_gate_rejects_standard_prompt_prop_title_loop(self) -> None:
        body = standard_prompt_prop_title_loop_sample()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECKER),
                    str(draft),
                    "--json",
                    "--strict",
                    "--draft-gate",
                    "--genre",
                    "standard",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("strict: 标准日寄提示物标题闭环", rules)
            suggestions = "\n".join(item["suggestion"] for item in findings)
            self.assertIn("重选侧面后果", suggestions)
            self.assertIn("不是局部换词", suggestions)

    def test_clean_run_preflight_flags_standard_prompt_prop_title_loop(self) -> None:
        body = standard_prompt_prop_title_loop_sample()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("standard_prompt_prop_title_loop=") for message in messages),
                messages,
            )

    def test_clean_run_preflight_flags_overloaded_beizulan_title(self) -> None:
        body = standard_prompt_prop_title_loop_sample("# 备注栏")
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("standard_prompt_prop_title_loop=") for message in messages),
                messages,
            )

    def test_clean_run_preflight_flags_exact_standard_prompt_prop_title(self) -> None:
        body = "\n".join(
            [
                "# 备注",
                "",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertIn("standard_prompt_prop_title=备注", messages)

    def test_clean_run_preflight_flags_high_signal_opening_before_checker(self) -> None:
        body_lines = [
            "情人节晚上刷了会儿朋友圈，有晒花的，有晒转账的，有晒电影票的，",
            "我点外卖的时候备注不要香菜，手指还在屏幕上停了一下。",
            "其实我觉得门口那个灯很烦，",
            "突然一闪，外卖袋子上那点红油看起来像别人发错的通知。",
            "于是我把袋子拎进来，因为门缝里还夹着一张小广告，",
            "好像提醒我这栋楼也在过节。",
            "不过水槽里的碗先翻了一下，",
            "我伸手去扶，袖口蹭到红油，门外的人还没走远。",
        ] * 8
        body = "\n".join(["# 门口", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("CLEAN_RUN_PREFLIGHT", preflight.stdout)
            self.assertIn("high_signal_opening=present", preflight.stdout)
            self.assertIn("Reset the opening source", preflight.stdout)
            self.assertIn("rewrite the opening", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_checker_draft_gate_flags_single_line_feed_inventory_opening(self) -> None:
        body = "\n".join(
            [
                "# 门口",
                "",
                "朋友圈有个红点，点进去，满屏都是花和转账截图。",
                "我把充电线按了三次才亮，",
                "其实插头也没坏，就是手上有水，一直按不到底。",
                "门口有人敲了一下，我拖着一只棉拖鞋过去，",
                "外卖员站在楼梯口等我扫码，手机卡了一下没扫上。",
                "袋子提手裂开，汤顺着手背往下淌，他看着也没说话。",
                "我把门关小一点，袖口蹭到门框上，",
                "回去踩到那点汤，拖鞋一滑，扶着墙站了半天。",
                *(["不过水龙头咳了一下，我发现杯子边上还有油，因为手指一直黏着。"] * 26),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertIn("strict: 社交动态库存式开头", rules)

    def test_clean_run_preflight_flags_single_line_feed_inventory_opening(self) -> None:
        body_lines = [
            "朋友圈有个红点，点进去，满屏都是花和转账截图。",
            "我把充电线按了三次才亮，",
            "其实插头也没坏，就是手上有水，一直按不到底。",
            "门口有人敲了一下，我拖着一只棉拖鞋过去，",
            "外卖员站在楼梯口等我扫码，手机卡了一下没扫上。",
            "袋子提手裂开，汤顺着手背往下淌，他看着也没说话。",
            "我把门关小一点，袖口蹭到门框上，",
            "回去踩到那点汤，拖鞋一滑，扶着墙站了半天。",
        ] * 8
        body = "\n".join(["# 门口", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("feed_inventory_opening=present", preflight.stdout)
            self.assertIn("Reset the opening source", preflight.stdout)
            self.assertIn("one cropped prompt surface", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_preflight_flags_soft_witness_without_consequence(self) -> None:
        body_lines = [
            "醒来以后水龙头还是冷的，",
            "其实我把脸洗了一半，发现毛巾有一股潮味。",
            "不过门口那个塑料袋被风吹了一下，",
            "于是我去拿外卖，因为手机一直在震。",
            "骑手看了我一眼，又往下看了一眼，然后骑车走了。",
            "我把门带上，才发现棉裤膝盖那里磨得发白。",
            "袖口也有油渍，不知道什么时候蹭上去的。",
            "好像今天也就这样。",
        ] * 8
        body = "\n".join(["# 红油", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("soft_witness_no_consequence=present", preflight.stdout)
            self.assertIn("do not keep a rider, cashier, neighbor, or stranger as a silent camera", preflight.stdout)
            self.assertIn("Make the existing handoff change payment, reply, bag/object state", preflight.stdout)
            self.assertIn("silent witness", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_preflight_flags_oil_stain_scan_without_consequence(self) -> None:
        body_lines = [
            "醒来以后水龙头还是冷的，",
            "其实我把脸洗了一半，发现毛巾有一股潮味。",
            "不过门口那个塑料袋被风吹了一下，",
            "于是我去拿外卖，因为手机一直在震。",
            "骑手把袋子递过来，扫到我裤腿上那块油渍。",
            "我侧了一下腿，说了声谢谢，他转身就走了。",
            "我回屋坐下，把手机翻过去，",
            "好像今天也就这样。",
        ] * 8
        body = "\n".join(["# 油渍", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("soft_witness_no_consequence=present", preflight.stdout)
            self.assertIn("do not keep a rider, cashier, neighbor, or stranger as a silent camera", preflight.stdout)
            self.assertIn("Make the existing handoff change payment, reply, bag/object state", preflight.stdout)

    def test_clean_run_preflight_explains_private_grime_is_not_public_roughness(self) -> None:
        body_lines = [
            "暖气的管子摸上去只有一点温，",
            "其实我坐在沙发边上看手机，发现充电线不够长。",
            "不过后来还是点了麻辣烫，因为别的也想不出来。",
            "塑料袋勒着手指，袋底有点湿，油印子渗出来。",
            "骑手已经转身走了，楼道灯晃了一下就没了。",
            "我进屋才发现手指上沾了汤汁，在裤子上蹭了一下。",
            "擦手的时候看见镜子里的人，头发塌着，领口也有油渍。",
            "靠在沙发上打了个嗝，全是香菜味。",
        ] * 8
        body = "\n".join(["# 充电线", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("private_grime_without_public_consequence=") for message in messages),
                messages,
            )
            self.assertTrue(any("rough_self_damage=missing" in message for message in messages), messages)

    def test_clean_run_preflight_allows_witness_that_changes_action(self) -> None:
        body = "\n".join(
            [
                "# 红油",
                "",
                "外卖员把袋子递过来，说路上洒了一点。",
                "他看了我一眼，又看了一眼我的手，我把手往口袋里塞了一下，",
                "袋子提手突然裂开，红油顺着塑料袋往下淌。",
                "我赶紧把门关小一点，拿旧报纸垫在地上。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertFalse(
                any(message.startswith("soft_witness_no_consequence=") for message in messages),
                messages,
            )

    def test_soft_witness_allows_iteration_147_transaction_cancellation_consequence(self) -> None:
        self.assertEqual(
            soft_witness_matches(
                [
                    "她看了我一眼，叫旁边的人过来输密码取消，",
                    "后面排队的男生把两瓶水放到柜台上，往前挪了一步。",
                    "取消的小票从机器里吐出来，很长一截。",
                ]
            ),
            [],
        )

    def test_soft_witness_allows_checkout_linked_queue_movement(self) -> None:
        self.assertEqual(
            soft_witness_matches(
                [
                    "收银员看了我一眼，把扫码枪放回柜台。",
                    "后面排队的人往前挪了一步，我让出了位置。",
                    "机器又响了一声。",
                ]
            ),
            [],
        )

    def test_soft_witness_allows_checkout_context_from_previous_line(self) -> None:
        self.assertEqual(
            soft_witness_matches(
                [
                    "收银员把手机拿过去，站在柜台里面。",
                    "她看了我一眼。",
                    "订单作废，小票从机器里吐出来。",
                ]
            ),
            [],
        )

    def test_soft_witness_allows_current_checkout_after_later_marker(self) -> None:
        self.assertEqual(
            soft_witness_matches(
                [
                    "后来收银员看了我一眼，叫旁边的人过来输密码取消。",
                    "后面排队的人往前挪了一步。",
                    "取消的小票从机器里吐出来。",
                ]
            ),
            [],
        )

    def test_soft_witness_does_not_use_unrelated_alarm_cancellation_as_consequence(self) -> None:
        self.assertEqual(
            soft_witness_matches(
                [
                    "骑手看了我一眼，转身就走。",
                    "我低头取消了手机里明早的闹钟。",
                    "门口还是没人说话。",
                ]
            ),
            [(1, "骑手看了我一眼，转身就走。")],
        )

    def test_soft_witness_rejects_detached_transaction_or_queue_keywords(self) -> None:
        cases = [
            [
                "骑手看了我一眼，说他上周那笔订单退款了。",
                "门口还是没人说话。",
            ],
            [
                "骑手看了我一眼，说他上周付款取消了。",
                "门口还是没人说话。",
            ],
            [
                "订单退款是上周的，骑手看了我一眼，转身就走。",
                "门口还是没人说话。",
            ],
            [
                "付款取消是之前的，骑手看了我一眼，转身就走。",
                "门口还是没人说话。",
            ],
            [
                "骑手看了我一眼，转身就走。",
                "我回屋后想起上周那笔付款已经取消。",
                "门口还是没人说话。",
            ],
            [
                "骑手看了我一眼，转身就走。",
                "我回屋后取消了昨晚买书的订单。",
                "门口还是没人说话。",
            ],
            [
                "骑手看了我一眼，转身就走。",
                "我想起上周那笔交易还没退款。",
                "门口还是没人说话。",
            ],
            [
                "邻居看了我一眼，关门回屋。",
                "楼下排队的人往前挪了一步。",
                "我把灯关了。",
            ],
        ]
        for lines in cases:
            with self.subTest(lines=lines):
                self.assertEqual(soft_witness_matches(lines), [(1, lines[0])])

    def test_clean_run_preflight_flags_em_dash_surface(self) -> None:
        body = "\n".join(
            [
                "# 水槽",
                "",
                "拿筷子翻了翻——最底下还是有一小撮香菜。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(any(message.startswith("em_dash=present") for message in messages), messages)

    def test_checker_allows_standard_side_action_title_with_prompt_props(self) -> None:
        body = standard_prompt_prop_title_loop_sample("# 水槽")
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECKER),
                    str(draft),
                    "--json",
                    "--strict",
                    "--draft-gate",
                    "--genre",
                    "standard",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(
                any("标准日寄提示物标题闭环" in item["rule"] for item in findings),
                [item["rule"] for item in findings],
            )

    def test_clean_run_preflight_flags_short_sincere_local_packet_loop(self) -> None:
        body = "\n".join(
            [
                "洗洁精快用完了",
                "",
                "我挤了半天，只出来一点稀的",
                "碗边的油渍擦不掉",
                "手在水里泡得发皱，指节都泛白了",
                "手机在客厅充电，屏幕突然亮了",
                "我走过去，看见是微信弹窗",
                "母亲节快乐",
                "四个字，底下是十几个同学发的同款",
                "我划掉通知，没点进去",
                "其实想回一句，但不知道发给谁",
                "上次回家，我妈煮了一袋鸡蛋让我带走，塑料袋装着，还是温的，",
                "我拎着那袋鸡蛋走到车站，手心被勒出红印，一路都没松手。",
                "雨声从窗户缝里钻进来，小时候她送我上学，也是这样的雨，",
                "她举着一把破伞，我躲在她腋下，书包还是湿了。",
                "现在手机屏幕又亮了，是室友发来的消息",
                "问要不要一起吃宵夜",
                "我回了个好，然后放下手机",
                "水池里的碗还泡着",
                "水已经凉了",
                "我回到水池边，发现油渍还在",
                "手指搓了搓，搓出一点黏的",
                "油已经凝了",
                "我拿起洗洁精瓶子晃了晃，里面有水声",
                "还是挤不出来",
                "手机又亮了，这次是妈妈发的",
                "你吃了吗",
                "三个字",
                "我盯着屏幕，手还泡在水里",
                "水很凉，指尖发白",
                "我没回，把手机倒扣在台面上",
                "碗还泡着，水更凉了",
                "我关掉水龙头，水滴声还在响",
                "手机屏幕暗了，但消息还在那儿",
                "我擦干手，手背有点痒，明天再说吧，我想",
                "然后去拿另一条干毛巾擦碗，碗边的油渍还在，得用热水泡",
                "我走到灶台边，拧开火，水壶开始响",
                "手机又亮了，这次还是妈妈发的消息",
                "我盯着屏幕，手还泡在水里，水很凉，指尖发白",
                "我没回，把手机倒扣在台面上，碗还泡着，水更凉了",
                "水壶响得更急了，我关掉火，水开了，但碗还没泡",
                "我倒了点热水进碗里，油渍化开一点，用毛巾擦了擦，还是黏",
                "雨还在下，我听见隔壁在关门，有人出去了",
                "我站了一会儿，觉得有点饿，但不想吃宵夜",
                "碗还没泡完，明天再说吧",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("short_genre_local_packet_loop=") for message in messages),
                messages,
            )

            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            findings = json.loads(result.stdout)
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any("短体裁局部材料回环" in rule for rule in error_rules), error_rules)

    def test_checker_does_not_flag_side_action_title_as_main_prop_loop(self) -> None:
        body = "\n".join(
            [
                "# 袖口",
                "",
                "水槽里那个碗翻不过来，",
                "底下有一圈油，冷水冲了半天还在。",
                "我手背被洗洁精泡得有点红，",
                "袖口也湿了。",
                "手机在旁边亮了一下，",
                "朋友圈里都是母亲节。",
                "我没有点开。",
                "上次回家，我妈塞给我一袋鸡蛋，塑料袋结打得很紧，",
                "路上鸡蛋在包里碰来碰去。",
                "我拎到车站的时候，袋子勒在手指上，",
                "那道红印到晚上还没消。",
                "小时候下雨，她骑车送我上学，雨衣往我这边偏，",
                "她肩膀湿了一路。",
                "到校门口她把书包递给我，",
                "我嫌书包带上全是水，皱了一下眉。",
                "我现在想给她发点什么，",
                "打了一个妈字又删掉。",
                "锅里的水开了，",
                "鸡蛋在里面撞了两下。",
                "有一个壳裂了，白沫浮起来，",
                "我拿筷子戳了一下，像在确认它还能不能装作完整。",
                "楼道里有人关门，",
                "我把手机扣过去。",
                "最后那袋鸡蛋还在台面上，",
                "塑料袋的结没有拆开。",
                "袖口贴着手腕，",
                "我也没有换衣服。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertFalse(any("短真诚标题物件闭环" in rule for rule in rules), rules)

    def test_checker_warns_on_short_sincere_missing_present_action_anchor(self) -> None:
        body = "\n".join(
            [
                "# 屏朝下",
                "",
                "下午煮鸡蛋。冰箱里那几个放了快一周，",
                "上回回家我妈塞的，塑料袋扎了两层，",
                "拿出来的时候还是那个样子。",
                "挑了两个下锅。有一个放下去就裂了口子，",
                "蛋清散出来在水里白花花一团往上翻。",
                "我站在灶台前面看了好一阵子。",
                "",
                "小时候下雨天她送我上学，雨衣套在我身上，",
                "她自己打一把破伞，那伞半边是断的。",
                "雨从断了的那根骨架漏下来淋在她肩膀上。",
                "到村口那段路全是稀泥，",
                "她把我背过去，鞋子陷在里面拔了一下才拔出来。",
                "到学校门口她头发贴在脸上。",
                "我看了她一眼，没说话，就进去了。",
                "这事隔了二十年，我不知道为什么煮鸡蛋的时候想起来了。",
                "",
                "把破的那个捞出来，蛋清碎得不成形，",
                "蛋黄倒还完整。有点烫，站在灶台前面吃了。",
                "",
                "手机在房间床上，屏朝下搁着。",
                "朋友圈里全是母亲节，",
                "康乃馨，合照，转账截图，一条一条。",
                "我没发。",
                "想不出来发什么。",
                "我妈不识字，发文字她要拿给隔壁王姨看，",
                "发语音也不一定回，上次发了一条隔了两天才回个表情。",
                "",
                "把剩下的几个鸡蛋捞出来装在碗里。",
                "小时候觉得她烦，煮个鸡蛋都念叨半天，",
                "现在她不说了，我也不说。",
                "隔壁好像在放什么节目，电视声音很大，",
                "嗡嗡嗡一句也听不清。",
                "",
                "洗锅的时候水龙头开太大溅了一身，",
                "裤子湿了一大片，我没换就坐回床上。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any("短真诚当前动作锚点不足" in rule for rule in rules), rules)
            self.assertTrue(any("短真诚当前动作锚点不足" in rule for rule in error_rules), error_rules)
            suggestions = "\n".join(item["suggestion"] for item in findings)
            self.assertIn("整篇换源头", suggestions)
            self.assertIn("重选标题", suggestions)

    def test_clean_run_preflight_flags_short_sincere_missing_present_action_anchor(self) -> None:
        body = "\n".join(
            [
                "# 屏朝下",
                "",
                "下午煮鸡蛋。冰箱里那几个放了快一周，",
                "上回回家我妈塞的，塑料袋扎了两层，",
                "拿出来的时候还是那个样子。",
                "挑了两个下锅。有一个放下去就裂了口子，",
                "蛋清散出来在水里白花花一团往上翻。",
                "小时候下雨天她送我上学，雨衣套在我身上。",
                "她自己打一把破伞，那伞半边是断的。",
                "到学校门口她头发贴在脸上。",
                "我看了她一眼，没说话，就进去了。",
                "这事隔了二十年，我不知道为什么煮鸡蛋的时候想起来了。",
                "手机在房间床上，屏朝下搁着。",
                "朋友圈里全是母亲节，康乃馨，合照，转账截图，一条一条。",
                "我没发。",
                "我妈不识字，发文字她要拿给隔壁王姨看。",
                "把剩下的几个鸡蛋捞出来装在碗里。",
                "小时候觉得她烦，煮个鸡蛋都念叨半天。",
                "现在她不说了，我也不说。",
                "洗锅的时候水龙头开太大溅了一身。",
                "裤子湿了一大片，我没换。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("short_genre_present_action_anchor=") for message in messages),
                messages,
            )

    def test_checker_warns_when_short_sincere_prompt_props_enter_too_early(self) -> None:
        body = "\n".join(
            [
                "# 油没冲掉",
                "",
                "碗底还有点油，水凉了，手背有点红。",
                "洗洁精快用完了，",
                "挤了半天才出来一点，瓶底咕噜响。",
                "水槽边那个塑料袋是上次回家装鸡蛋的，",
                "妈煮好了一袋让我带走，袋口拧了个结。",
                "鸡蛋在冰箱里吃了几个，",
                "袋子没扔，搁在水槽边上。",
                "小时候下雨她送我上学。",
                "雨衣裹着我，她没穿。",
                "手机在桌上亮了一下。",
                "朋友圈里全是母亲节。",
                "我点开对话框，打了几个字，又删了。",
                "碗还没洗完，水更凉了。",
                "手在里面泡久了，指节有点皱。",
                "走廊里有人关门，砰的一声。",
                "我把碗摞起来，底下那个盘子滑了一下，",
                "水溅到袖口上。",
                "手机又亮了一下，我没拿。",
                "水龙头关不紧，滴了几下。",
                "抹布有点硬，擦过去还是一条油光。",
                "我站了一会儿，觉得脚底凉。",
                "厨房灯没开，窗户那边有一点雨声。",
                "塑料袋还搁在水槽边。",
                "袋口那个结看着很死。",
                "裤子湿了一块。",
                "我没换。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            findings = json.loads(result.stdout)
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any("短真诚题面物件过早" in rule for rule in error_rules), error_rules)

    def test_clean_run_preflight_flags_short_sincere_prompt_props_enter_too_early(self) -> None:
        body = "\n".join(
            [
                "# 油没冲掉",
                "",
                "碗底还有点油，水凉了，手背有点红。",
                "洗洁精快用完了，",
                "挤了半天才出来一点，瓶底咕噜响。",
                "水槽边那个塑料袋是上次回家装鸡蛋的，",
                "妈煮好了一袋让我带走，袋口拧了个结。",
                "鸡蛋在冰箱里吃了几个，",
                "袋子没扔，搁在水槽边上。",
                "小时候下雨她送我上学。",
                "雨衣裹着我，她没穿。",
                "手机在桌上亮了一下。",
                "朋友圈里全是母亲节。",
                "我点开对话框，打了几个字，又删了。",
                "碗还没洗完，水更凉了。",
                "手在里面泡久了，指节有点皱。",
                "走廊里有人关门，砰的一声。",
                "我把碗摞起来，底下那个盘子滑了一下，",
                "水溅到袖口上。",
                "手机又亮了一下，我没拿。",
                "水龙头关不紧，滴了几下。",
                "抹布有点硬，擦过去还是一条油光。",
                "我站了一会儿，觉得脚底凉。",
                "厨房灯没开，窗户那边有一点雨声。",
                "塑料袋还搁在水槽边。",
                "袋口那个结看着很死。",
                "裤子湿了一块。",
                "我没换。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("short_genre_prompt_prop_too_early=") for message in messages),
                messages,
            )

    def test_checker_does_not_warn_present_action_anchor_when_current_friction_leads(self) -> None:
        body = "\n".join(
            [
                "# 下午走回来的",
                "",
                "电风扇对着脚吹。",
                "袜子脱了一只，",
                "脚趾头露在外面。",
                "手机亮了一下。",
                "微信里全是母亲节。",
                "我没给我妈发消息。",
                "冰箱里有妈妈塞给我的鸡蛋，",
                "吃了四个，剩下的忘了。",
                "隔壁男的敲门，",
                "说阳台管子堵了。",
                "他看了一眼我的袜子。",
                "我假装没看见。",
                "想起小时候下雨，",
                "妈妈骑车送我上学。",
                "雨衣里面有洗衣粉味。",
                "这个念头很快滑过去。",
                "我给隔壁男的发微信，",
                "说应该是弯头堵了。",
                "右腿上有三个蚊子包，",
                "已经挠破了。",
                "血印子干了之后是深褐色的。",
                "冰箱门又弹开一点。",
                "我用腿顶回去。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertFalse(any("短真诚当前动作锚点不足" in rule for rule in rules), rules)

    def test_clean_run_preflight_flags_missing_title_before_checker(self) -> None:
        body = "\n".join(
            [
                "碗底还有点油，水凉了，手背有点红。",
                "洗洁精快用完了，",
                "挤了半天才出来一点，瓶底咕噜响。",
                "水槽边那个塑料袋是上次回家装鸡蛋的，",
                "妈煮好了一袋让我带走。",
                "朋友圈里全是母亲节。",
                "我没发。",
                "裤子湿了一块。",
                "我没换。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(any(message.startswith("missing_title=") for message in messages), messages)

    def test_checker_warns_on_underbuilt_short_sincere_complete_article(self) -> None:
        body = "\n".join(
            [
                "# 下午走回来的",
                "",
                "电风扇对着脚吹。",
                "袜子脱了一只，",
                "脚趾头露在外面。",
                "手机亮了一下。",
                "微信里全是母亲节。",
                "我没给我妈发消息。",
                "冰箱里有妈妈塞给我的鸡蛋，",
                "吃了四个，剩下的忘了。",
                "隔壁男的敲门，",
                "说阳台管子堵了。",
                "他看了一眼我的袜子。",
                "我假装没看见。",
                "想起小时候下雨，",
                "妈妈骑车送我上学。",
                "雨衣里面有洗衣粉味。",
                "这个念头很快滑过去。",
                "我给隔壁男的发微信，",
                "说应该是弯头堵了。",
                "右腿上有三个蚊子包，",
                "已经挠破了。",
                "血印子干了之后是深褐色的。",
                "房间里灯太暗，",
                "看不清指甲缝。",
                "坐了一会儿，",
                "还是没有给我妈发祝福。",
                "冰箱门又弹开一点。",
                "我用腿顶回去，",
                "塑料袋在里面响了一下。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any("短体裁完整度不足" in rule for rule in rules), rules)
            self.assertTrue(any("短体裁完整度不足" in rule for rule in error_rules), error_rules)
            self.assertFalse(any("标准日寄完整文章篇幅" in rule for rule in rules), rules)

    def test_clean_run_preflight_flags_underbuilt_short_sincere(self) -> None:
        body = "\n".join(
            [
                "# 下午走回来的",
                "",
                "电风扇对着脚吹。",
                "袜子脱了一只，",
                "脚趾头露在外面。",
                "手机亮了一下。",
                "微信里全是母亲节。",
                "我没给我妈发消息。",
                "冰箱里有妈妈塞给我的鸡蛋，",
                "吃了四个，剩下的忘了。",
                "隔壁男的敲门，",
                "说阳台管子堵了。",
                "他看了一眼我的袜子。",
                "我假装没看见。",
                "想起小时候下雨，",
                "妈妈骑车送我上学。",
                "雨衣里面有洗衣粉味。",
                "这个念头很快滑过去。",
                "我给隔壁男的发微信，",
                "说应该是弯头堵了。",
                "右腿上有三个蚊子包，",
                "已经挠破了。",
                "血印子干了之后是深褐色的。",
                "房间里灯太暗，",
                "看不清指甲缝。",
                "坐了一会儿，",
                "还是没有给我妈发祝福。",
                "冰箱门又弹开一点。",
                "我用腿顶回去，",
                "塑料袋在里面响了一下。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("short_genre_underbuilt_complete_article=") for message in messages),
                messages,
            )
            self.assertTrue(
                any(message.startswith("short_genre_no_long_clumsy_lines=") for message in messages),
                messages,
            )

    def test_detect_style_routes_mother_date_and_care_memory_to_sincere(self) -> None:
        body = "\n".join(
            [
                "# 红痕",
                "",
                "晚上煮面，水放多了，",
                "手背红了一小片。",
                "屏幕顶端：五月十二号，",
                "星期天。",
                "上次回家冰箱里有一袋鸡蛋，",
                "我妈说煮好了你带回去。",
                "小时候下雨我妈骑自行车接我，",
                "雨衣短，小腿全湿了。",
            ]
        )
        self.assertEqual(detect_style(body), "sincere")

    def test_detect_style_routes_pronoun_mother_care_logistics_to_sincere(self) -> None:
        body = "\n".join(
            [
                "# 油",
                "",
                "洗完那个碗，手上还有油，",
                "冰箱里的灯是白的，",
                "那袋鸡蛋还在，",
                "塑料袋扎得很紧。一个结叠一个结，我拆了一会儿才打开。",
                "上次回去，走之前她在厨房忙了一阵，",
                "出来拎着这个袋子，说带回去吧，外面的鸡蛋不好。",
                "我接过来的时候碰到她的手，比我的凉很多。",
                "她又说了句别忘了吃。",
                "五月十二号，手机在洗手池旁边亮了一下。",
                "我没点开。",
                "上一次聊天是周二，",
                "她问还有没有菜，我说有。",
                "她说那就好，又说天冷了多穿点。",
                "我打了一个字，又删了。",
            ]
        )
        self.assertNotIn("妈妈", body)
        self.assertNotIn("我妈", body)
        self.assertNotIn("母亲", body)
        self.assertEqual(detect_style(body), "sincere")

        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertFalse(any(message.startswith("body_chinese_chars=") for message in messages), messages)
            self.assertTrue(any(message.startswith("short_genre_") for message in messages), messages)

    def test_detect_style_keeps_standard_diary_with_generic_mother_message_standard(self) -> None:
        lines = [
            "外卖袋子放在门口，汤漏了一点，",
            "我先看鞋面，红油顺着鞋带往下走。",
            "手机上面还有朋友圈，两个高中同学晒花，",
            "我划过去的时候手指有点油，没划动。",
            "楼下麻辣烫老板在群里说今天爆单，",
            "其实我只想问他为什么不要香菜还能有香菜。",
            "不过也没问，",
            "问了显得我把人生最后一点尊严交给香菜了。",
            "银行卡余额弹出来，像一个人站在门口看我吃饭，",
            "我把它关掉，又打开优惠券。",
            "有张三块的，过期时间是今晚。",
            "突然觉得这张券比我更懂情人节，",
            "它至少还有过期的资格。",
            "我妈发消息问吃了吗，",
            "我回吃了。",
            "她又发一个句号。",
            "那个句号停在屏幕上，跟香菜叶子差不多，",
            "都很小，都很烦。",
            "楼道有人说话，像在搬一个很轻的箱子，",
            "我听了一会儿，发现不是找我。",
            "饭已经凉了，粉丝坨在一起。",
            "我挑香菜挑到最后，筷子上全是绿点。",
            "有一片粘在手背，",
            "洗了两次还闻得到。",
            "于是去厕所洗手，水龙头先咳了一下，",
            "喷到裤子上。",
            "很丢人。",
            "我低头看那块水印，像刚从一个很失败的约会回来。",
            "其实也没约会。",
            "只是裤子替我参加了一下。",
            "外卖软件又推情人节第二份半价，",
            "我点开看了看，发现第二份也要钱。",
            "这系统很公平，",
            "它对单身的人也不打折。",
            "吃到最后嘴里都是香菜味，",
            "我想喝水，杯子里有昨天的茶渍。",
            "刷杯子的时候手机又亮，",
            "我妈问是不是太晚了。",
            "我说不晚。",
            "发送完才发现这句话像客服。",
            "好像我不是她儿子，",
            "我是一个营业时间比较长的废物。",
            "窗外有电动车过去，刹车声很尖，",
            "我把剩下的汤倒进袋子。",
            "袋口没系好，",
            "又漏了一点。",
            "最后我蹲在地上擦那点红油，",
            "纸巾越擦越薄。",
            "手机在桌上亮着。",
            "我没拿。",
            "先把鞋带解了。",
        ]
        body = "\n".join(["# 香菜", "", *lines])
        self.assertEqual(detect_style(body), "standard")
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertFalse(any(message.startswith("short_genre_") for message in messages), messages)

    def test_detect_style_keeps_expanded_mother_care_repair_in_sincere(self) -> None:
        body = short_sincere_expanded_repair_sample()
        self.assertEqual(detect_style(body), "sincere")

    def test_checker_flags_short_sincere_standard_expansion_drift(self) -> None:
        body = short_sincere_expanded_repair_sample()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any("短体裁误扩成标准日寄" in rule for rule in error_rules), error_rules)
            self.assertTrue(any("无依据重大家庭变故" in rule for rule in error_rules), error_rules)
            self.assertFalse(any("标准日寄行数缓冲异常" in rule for rule in error_rules), error_rules)

    def test_checker_does_not_treat_shop_owner_moved_away_as_family_loss(self) -> None:
        body = "\n".join(
            [
                "# 门口",
                "",
                "母亲节那天手机亮了一下。",
                "我没点开，手上还有一点油。",
                "楼下那家粉店以前是个老板娘看着，",
                "她去年搬走了，店面兑给了别人。",
                "现在汤有点咸，塑料勺子也软，",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("无依据重大家庭变故" in item["rule"] for item in findings), findings)

    def test_clean_run_preflight_flags_short_sincere_tiny_row_grid(self) -> None:
        body = "\n".join(
            [
                "# 红痕",
                "",
                "晚上煮面，水放多了，",
                "扑出来的时候火苗闪了一下。",
                "关了，端锅的时候耳朵烫了手，",
                "缩了一下，锅差点翻。",
                "捞面的时候滑了一下，",
                "几根面条掉水槽里，",
                "捡起来冲了冲，",
                "手背红了一小片。",
                "不疼，但是看着不舒服。",
                "端上桌才想起没拿筷子，",
                "回去拿。",
                "灶台边有一层油灰，",
                "拇指擦了擦，滑腻腻的，",
                "懒得管了。",
                "手机亮了一下，",
                "运营商余额。",
                "屏幕顶端：五月十二号，",
                "星期天。",
                "上次回家冰箱里有一袋鸡蛋，",
                "我妈说煮好了你带回去。",
                "塑料袋系了两个结，",
                "一个死结扯不开。",
                "我用牙咬了一下，撕了个口，",
                "鸡蛋挤在一起，",
                "有一个裂了缝，蛋清渗出来，",
                "黏糊糊的。",
                "我放回冰箱第二层，",
                "后来每次拉开冰箱都看见它，",
                "蛋白干了，发黄，",
                "一直没吃。",
                "小时候下雨我妈骑自行车接我，",
                "雨衣短，小腿全湿了。",
                "到学校她把雨衣给我，",
                "自己推车回去，",
                "背上深了一块，",
                "也没说什么。",
                "吃完想把碗洗了，",
                "水龙头开了才发现没洗洁精，",
                "又关上了。",
                "碗泡在水槽里，",
                "水面浮着一层油花，",
                "那几根掉下去的面条泡发了，",
                "漂在水上。",
                "我突然觉得有点恶心，",
                "走开了。",
                "去楼下买洗洁精，",
                "扫码的时候手滑了一下，",
                "屏幕没反应。",
                "又扫了一次，",
                "收银员看了我一眼，又看了看我的手，",
                "没说话。",
                "塑料袋提手很细，",
                "勒进那道红痕里，",
                "有点疼，我换了一只手。",
                "回来的时候楼道灯坏了，",
                "踩着台阶边缘摸上去。",
                "钥匙捅了半天，",
                "锁有点涩，转不动，",
                "用力拧了一下，",
                "开了。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("short_genre_short_line_grid=") for message in messages),
                messages,
            )
            self.assertFalse(any(message.startswith("body_chinese_chars=") and "< 900" in message for message in messages), messages)

    def test_checker_warns_on_short_sincere_prose_block_and_date_title(self) -> None:
        body = short_sincere_prose_block_sample()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertIn("短体裁散文块压缩", rules)
            self.assertTrue(any("短体裁题面日期标题" in rule for rule in rules), rules)

    def test_clean_run_preflight_flags_short_sincere_prose_block_and_date_title(self) -> None:
        body = short_sincere_prose_block_sample()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(any(message.startswith("short_genre_body_lines=") for message in messages), messages)
            self.assertTrue(any(message.startswith("short_genre_prose_block_compression=") for message in messages), messages)
            self.assertTrue(any(message.startswith("short_genre_diagnostic_date_title=") for message in messages), messages)

    def test_checker_flags_short_sincere_period_grid(self) -> None:
        body = short_sincere_period_grid_sample()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            findings = json.loads(result.stdout)
            error_rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any("短体裁句号网格" in rule for rule in error_rules), error_rules)
            self.assertFalse(any("标准日寄完整文章篇幅" in rule for rule in error_rules), error_rules)

    def test_clean_run_preflight_flags_short_sincere_period_grid(self) -> None:
        body = short_sincere_period_grid_sample()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(any(message.startswith("short_genre_period_grid=") for message in messages), messages)

    def test_checker_warns_on_short_sincere_repair_stuffing(self) -> None:
        lines = [
            "# 锅盖",
            "",
            "水龙头开了很久，锅里还是凉的，",
            "我妈早上发消息问我吃没吃饭，我回了个吃了。",
            "上次回家，她把鸡蛋装进塑料袋，结打得很紧，",
            "小时候下雨，她骑车送我上学，雨衣大半边都盖在我身上。",
            "我想把母亲节快乐打出来，手指停了一下，",
            "又去看锅盖有没有动。",
            "后来我叫外卖，订单卡在配送中，",
            "页面上黄焖鸡、桂花糕、酥糖和溏心蛋挤在一起，",
            "短视频里有人教怎么煮溏心蛋，下一条综艺还在笑，",
            "游戏也弹出来，说王者有活动，",
            "导航显示小区门口堵了，",
            "我看了一眼，又把手机扣回灶台。",
            *(
                [
                    "锅盖边上有水，一点点往下滑，我拿抹布擦了一下，袖口贴在手腕上。",
                    "屏幕又亮，我没有拿起来，只把火调小了一点，",
                    "厨房灯管响了一声，好像也不太想参与这个节日。",
                ]
                * 12
            ),
        ]
        body = "\n".join(lines)
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("短体裁修复堆新素材" in item["rule"] for item in findings), findings)

    def test_clean_run_preflight_flags_short_sincere_repair_stuffing(self) -> None:
        body = "\n".join(
            [
                "# 锅盖",
                "",
                "我妈问吃饭没有，我说吃了，其实锅里还是凉的。",
                "上次她给我塞鸡蛋，小时候下雨又骑车送我上学，雨衣全往我这边偏。",
                "我盯着输入框，不知道怎么把母亲节快乐发出去。",
                "后来叫外卖，订单卡着不动，",
                "黄焖鸡、桂花糕、酥糖、溏心蛋排在一个页面里。",
                "短视频又教煮蛋，综艺在旁边笑，",
                "王者也弹活动，导航说小区门口堵着。",
                *(
                    [
                        "锅盖边上冒白汽，我用袖口去擦，手腕上湿了一块，",
                        "手机又亮，我没拿，只把那行字删掉。",
                        "水槽里的碗还泡着，油花贴在边上，不太肯走。",
                    ]
                    * 14
                ),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertTrue(any(message.startswith("short_genre_repair_stuffing=") for message in messages), messages)

    def test_checker_does_not_warn_repair_stuffing_for_plain_short_sincere(self) -> None:
        body = "\n".join(
            [
                "# 锅盖",
                "",
                "我妈问吃饭没有，我说吃了，其实锅里还是凉的。",
                "上次她给我塞鸡蛋，塑料袋结打得很紧，",
                "小时候下雨，她骑车送我上学，雨衣一直往我这边偏。",
                "我盯着输入框，不知道怎么把母亲节快乐发出去。",
                *(
                    [
                        "锅盖边上冒白汽，我用袖口去擦，手腕上湿了一块，",
                        "手机又亮，我没拿，只把那行字删掉。",
                        "水槽里的碗还泡着，油花贴在边上，不太肯走。",
                    ]
                    * 4
                ),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("短体裁修复堆新素材" in item["rule"] for item in findings), findings)

    def test_checker_infers_sincere_from_full_body_not_only_first_forty_lines(self) -> None:
        lead = ["我坐在桌边看锅盖，水汽贴着灯管往上爬。"] * 42
        mother_cluster = [
            "我妈发消息问我吃没吃饭。",
            "上次回家，她煮了一袋鸡蛋让我带走，",
            "小时候下雨，她骑车送我上学，雨衣往我这边偏。",
            "我想发母亲节快乐，最后只把手机扣过去。",
        ]
        body = "\n".join(["# 锅盖", "", *lead, *mother_cluster])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertFalse(any("标准日寄完整文章篇幅" in rule for rule in rules), rules)

    def test_checker_draft_gate_still_treats_plain_family_diary_as_standard_attempt(self) -> None:
        lines = [
            "我妈在饭桌上问我什么时候回去。",
            "我把筷子放下来，又拿起来。",
            "碗里那块肉肥得很认真，像一个不会看脸色的亲戚。",
            "我说再看吧，她嗯了一声。",
            "厨房的灯闪了一下，照得我指甲缝里全是酱油。",
            "我去洗手，水龙头先咳了一口黄水。",
        ] * 7
        body = "\n".join(["# 半碗饭", "", *lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule.startswith("strict: 标准日寄完整文章篇幅") for rule in rules), rules)

    def test_clean_run_checker_enforces_two_call_limit(self) -> None:
        ready_lines = [
            "其实我觉得厕所灯坏了以后，我站在门口有点丢人，",
            "很丢人。",
            "突然发现杯子边上有黑泥，好像还蹭到指甲缝里，",
            "于是洗手洗到一半想吐出来，因为水龙头又喷到裤子上。",
            "不过镜子里那张脸像没睡醒，还以为自己要去面试。",
        ] * 12
        body = "\n".join(["# 日寄", "", *ready_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            third = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("CLEAN_RUN_NOTE: checker call 1/2", first.stdout)
            self.assertIn("CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2", second.stdout)
            self.assertIn("DO NOT WRITE draft.md", second.stdout)
            self.assertEqual(third.returncode, 0)
            self.assertIn("FINAL BOUNDARY already reached", third.stdout)

    def test_clean_run_checker_records_stage_snapshots(self) -> None:
        ready_lines = [
            "其实我觉得厕所灯坏了以后，我站在门口有点丢人，",
            "很丢人。",
            "突然发现杯子边上有黑泥，好像还蹭到指甲缝里，",
            "于是洗手洗到一半想吐出来，因为水龙头又喷到裤子上。",
            "不过镜子里那张脸像没睡醒，还以为自己要去面试。",
        ] * 12
        repaired_lines = [
            "其实第二次我把厕所灯看成面试通知，站在门口有点丢人，",
            "没说。",
            "突然发现杯子边上有黑泥，好像还蹭到指甲缝里，",
            "于是洗手洗到一半想吐出来，因为水龙头又喷到裤子上。",
            "不过镜子里那张脸像没睡醒，还以为自己要去面试。",
        ] * 12
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            first_submission_bytes = "\r\n".join(["# 日寄", "", *ready_lines]).encode("utf-8")
            draft.write_bytes(first_submission_bytes)
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("checker call 1/2", first.stdout)
            submitted_bytes = "\r\n".join(["# 日寄", "", *repaired_lines]).encode("utf-8")
            draft.write_bytes(submitted_bytes)
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("FINAL BOUNDARY", second.stdout)
            self.assertEqual(draft.read_bytes(), submitted_bytes)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            snapshots = state["snapshots"]
            for key in [
                "first_submission",
                "checker_call_1_submission",
                "checker_call_2_submission",
                "bounded_final",
            ]:
                self.assertIn(key, snapshots)
                self.assertTrue(Path(snapshots[key]).is_file())
            self.assertIn("厕所灯坏了以后", Path(snapshots["first_submission"]).read_text(encoding="utf-8"))
            self.assertIn("其实第二次", Path(snapshots["checker_call_2_submission"]).read_text(encoding="utf-8"))
            self.assertIn("其实第二次", Path(snapshots["bounded_final"]).read_text(encoding="utf-8"))
            self.assertEqual(Path(snapshots["first_submission"]).read_bytes(), first_submission_bytes)
            self.assertEqual(Path(snapshots["checker_call_1_submission"]).read_bytes(), first_submission_bytes)
            self.assertEqual(Path(snapshots["checker_call_2_submission"]).read_bytes(), submitted_bytes)
            self.assertEqual(Path(snapshots["bounded_final"]).read_bytes(), submitted_bytes)

    def test_clean_run_checker_preflight_does_not_consume_checker_call(self) -> None:
        short_body = "\n".join(["# 日寄", "", "杯子脏了。"])
        ready_line = "其实我觉得厕所灯突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(short_body, encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3)
            self.assertIn("CLEAN_RUN_PREFLIGHT", preflight.stdout)
            self.assertIn("do not inspect checker source", preflight.stdout)
            self.assertNotIn("engine_hits", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)
            ready_lines = [
                "其实我觉得厕所灯坏了以后，我站在门口有点丢人，",
                "很丢人。",
                "突然发现杯子边上有黑泥，好像还蹭到指甲缝里，",
                "于是洗手洗到一半想吐出来，因为水龙头又喷到裤子上。",
                "不过镜子里那张脸像没睡醒，还以为自己要去面试。",
            ] * 12
            draft.write_text("\n".join(["# 日寄", "", *ready_lines]), encoding="utf-8")
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("CLEAN_RUN_NOTE: checker call 1/2", first.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 1)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_generator_interface_hides_numeric_preflight_telemetry(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("# 日寄\n\n杯子脏了。", encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
                "--generator-facing",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)

            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("CLEAN_RUN_PREFLIGHT", preflight.stdout)
            self.assertIn("source_shape=underbuilt", preflight.stdout)
            self.assertIn("next_action=one_complete_draft_write_then_immediate_wrapper_rerun", preflight.stdout)
            self.assertIn("do not count characters, lines, punctuation, or connectors", preflight.stdout)
            self.assertNotRegex(preflight.stdout, r"body_chinese_chars=\d")
            self.assertNotRegex(preflight.stdout, r"body_lines=\d")
            self.assertNotIn("connectors=[", preflight.stdout)
            self.assertNotIn("long_lines=", preflight.stdout)

            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)
            self.assertTrue(any(message.startswith("body_chinese_chars=") for message in state["last_preflight_messages"]))

    def test_clean_run_checker_generator_interface_hides_numeric_checker_telemetry(self) -> None:
        ready_lines = [
            "其实我觉得厕所灯坏了以后，我站在门口有点丢人，",
            "很丢人。",
            "突然发现杯子边上有黑泥，好像还蹭到指甲缝里，",
            "于是洗手洗到一半想吐出来，因为水龙头又喷到裤子上。",
            "不过镜子里那张脸像没睡醒，还以为自己要去面试。",
        ] * 12
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 日寄", "", *ready_lines]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
                "--generator-facing",
            ]
            checker = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)

            self.assertIn("CLEAN_RUN_NOTE: checker call 1/2", checker.stdout)
            self.assertIn("generator-facing interface: controller-only telemetry", checker.stdout)
            self.assertNotRegex(checker.stdout, r"body_chinese_chars=\d")
            self.assertNotRegex(checker.stdout, r"first_20_lines_ratio=\d")
            self.assertNotIn("present=[", checker.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 1)
            self.assertEqual(state["last_checker_returncode"], checker.returncode)
            self.assertIn("body_chars=", state["last_checker_stdout"])

    def test_generator_facing_summary_preserves_mass_routing_boundaries(self) -> None:
        labels, action = generator_facing_summary(["body_chinese_chars=875 < 900", "paragraph_engine=weak"])
        self.assertIn("source_shape=underbuilt", labels)
        self.assertIn("replace_one_broken_fragment_or_relation_in_place", action)
        self.assertNotIn("whole_source_rebuild", action)

        labels, action = generator_facing_summary(["body_chinese_chars=913 < 950 with source_shape_weak", "paragraph_engine=weak"])
        self.assertIn("source_shape=underbuilt", labels)
        self.assertIn("replace_one_broken_fragment_or_relation_in_place", action)
        self.assertNotIn("whole_source_rebuild", action)

        labels, action = generator_facing_summary(["body_chinese_chars=1450 > 1350", "rough_self_damage=missing"])
        self.assertIn("source_shape=overfull", labels)
        self.assertNotIn("source_shape=underbuilt", labels)
        self.assertIn("overfull", action)

    def test_generator_facing_summary_keeps_severe_source_rebuild_before_shape_tools(self) -> None:
        labels, action = generator_facing_summary(
            [
                "body_chinese_chars=480 < 650",
                "medium_short_line_grid=present",
                "paragraph_engine=weak",
            ]
        )
        self.assertIn("source_shape=underbuilt", labels)
        self.assertIn("whole_source_rebuild_from_strongest_fragment", action)
        self.assertIn("day_shaped_collage", action)
        self.assertIn("independent_thought_turns", action)
        self.assertIn("do_not_shrink_to_a_premise_summary", action)
        self.assertNotIn("breathing_rows", action)
        self.assertNotIn("rebalance_line_rhythm", action)
        self.assertNotIn("after_content_write_run_", action)

    def test_generator_facing_summary_names_shape_script(self) -> None:
        _labels, action = generator_facing_summary(["early_comma_ratio=0.00 < 0.15"])
        self.assertIn("soften_line_endings", action)
        self.assertIn("in_place_as_final_mutation", action)

        _labels, action = generator_facing_summary(["period_row_grid=present"])
        self.assertIn("rebalance_line_rhythm", action)
        self.assertIn("in_place_as_final_mutation", action)

    def test_generator_facing_summary_routes_surface_only_findings_locally(self) -> None:
        for message, surface_form in (
            ("binary_reframe=present count=1", "binary_reframe"),
            ("quoted_dialogue=present count=1", "quoted_dialogue"),
            ("prompt_performing_dialogue=present count=1", "prompt_performing_dialogue"),
        ):
            labels, action = generator_facing_summary([message])
            self.assertIn("surface_risk=remove_locally", labels)
            self.assertIn(f"surface_form={surface_form}", labels)
            self.assertNotIn("source_shape=underbuilt", labels)
            self.assertIn("surface_action=remove_only_the_named_surface_form", action)

    def test_generator_facing_contract_separates_preflight_from_checker_budget(self) -> None:
        contract = generator_facing_contract()
        self.assertIn("preflight attempts do not consume actual checker calls", contract)
        self.assertIn("wait for an explicit CLEAN_RUN_PREFLIGHT_STOP", contract)

    def test_generator_facing_contract_routes_named_rhythm_actions_in_order(self) -> None:
        _labels, mixed_action = generator_facing_summary(
            [
                "body_chinese_chars=910 < 950 with source_shape_weak",
                "body_lines=28 < 45",
                "prose_block_shape=compressed",
            ]
        )
        mixed_contract = generator_facing_contract(mixed_action)
        self.assertIn(
            "next_action=one_complete_draft_write_then_run_named_rhythm_script_in_place_then_immediate_wrapper_rerun",
            mixed_contract,
        )
        self.assertNotIn(
            "next_action=one_complete_draft_write_then_immediate_wrapper_rerun",
            mixed_contract,
        )

        _labels, shape_action = generator_facing_summary(["period_row_grid=present"])
        shape_contract = generator_facing_contract(shape_action)
        self.assertIn(
            "next_action=run_named_rhythm_script_in_place_then_immediate_wrapper_rerun",
            shape_contract,
        )
        self.assertNotIn("one_complete_draft_write", shape_contract)

    def test_generator_facing_contract_keeps_source_only_and_stop_actions_unambiguous(self) -> None:
        _labels, source_action = generator_facing_summary(
            ["body_chinese_chars=480 < 650", "paragraph_engine=weak"]
        )
        source_contract = generator_facing_contract(source_action)
        self.assertIn(
            "next_action=one_complete_draft_write_then_immediate_wrapper_rerun",
            source_contract,
        )
        self.assertNotIn("run_named_rhythm_script", source_contract)

        stop_contract = generator_facing_contract(stopped=True)
        self.assertIn("next_action=read_draft_once_and_output_unchanged", stop_contract)
        self.assertNotIn("one_complete_draft_write", stop_contract)
        self.assertNotIn("run_named_rhythm_script", stop_contract)

    def test_clean_run_checker_marker_forces_generator_facing_without_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case = Path(temp)
            draft = case / "draft.md"
            draft.write_text("# 日寄\n\n杯子脏了。", encoding="utf-8")
            (case / ".anlin-clean-eval-mode").write_bytes(b"")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("qualitative source review", preflight.stdout)
            self.assertNotRegex(preflight.stdout, r"body_chinese_chars=\d")
            self.assertNotIn("connectors=[", preflight.stdout)
            state = json.loads((case / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertTrue(state["generator_facing"])

    def test_clean_run_checker_preflight_blocks_overfull_without_consuming_call(self) -> None:
        long_line = "其实我觉得厕所灯突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"
        ready_line = "其实我觉得厕所灯坏了，于是发现杯子好像脏，因为我差点吐出来，丢人。"
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 日寄", "", *([long_line] * 46)]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3)
            self.assertIn("body_chinese_chars=", preflight.stdout)
            self.assertIn("> 1350", preflight.stdout)
            self.assertIn("cut unsupported/non-consequential texture", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)
            ready_lines = [
                "其实我觉得厕所灯坏了以后，我站在门口有点丢人，",
                "很丢人。",
                "突然发现杯子边上有黑泥，好像还蹭到指甲缝里，",
                "于是洗手洗到一半想吐出来，因为水龙头又喷到裤子上。",
                "不过镜子里那张脸像没睡醒，还以为自己要去面试。",
            ] * 12
            draft.write_text("\n".join(["# 日寄", "", *ready_lines]), encoding="utf-8")
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("CLEAN_RUN_NOTE: checker call 1/2", first.stdout)

    def test_clean_run_checker_preflight_blocks_overfragmented_grid_without_consuming_call(self) -> None:
        fragments = [
            "车把是烫的",
            "手套也是烫的",
            "其实我觉得腿麻了",
            "突然发现杯子脏",
            "于是洗手",
            "因为裤子湿了",
            "好像要吐",
            "但是没吐出来",
            "丢人得很",
            "反正也没人看",
        ]
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 下午三点半", "", *(fragments * 12)]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3)
            self.assertIn("body_lines=120 > 90", preflight.stdout)
            self.assertIn("long_lines=0 < 3", preflight.stdout)
            self.assertIn("short_line_grid=", preflight.stdout)
            self.assertIn("rebalance_line_rhythm.py", preflight.stdout)
            self.assertIn("NEXT_ACTION=repair source/content first", preflight.stdout)
            self.assertIn("after the last content write, run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place`", preflight.stdout)
            self.assertIn("if you edit draft.md after that script, rerun the script before checking", preflight.stdout)
            self.assertNotIn("before hand rewriting", preflight.stdout)
            self.assertIn("Do not summarize, quote, or enumerate these diagnostics as a TODO list", preflight.stdout)
            self.assertIn("change scene movement, rhythm, or local surface only", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_preflight_blocks_medium_short_line_grid_without_consuming_call(self) -> None:
        fragments = [
            "车把烫手",
            "手机也烫",
            "其实我想坐下",
            "突然看见人倒了",
            "于是我停了一下",
            "因为腿在抖",
            "好像没人说话",
            "我也没说话",
        ]
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 下午三点半", "", *(fragments * 8)]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3)
            self.assertIn("body_chinese_chars=", preflight.stdout)
            self.assertIn("< 900", preflight.stdout)
            self.assertIn("medium_short_line_grid=present", preflight.stdout)
            self.assertIn("long_lines=0 < 6", preflight.stdout)
            self.assertIn("NEXT_ACTION=repair source/content first", preflight.stdout)
            self.assertIn("after the last content write, run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place`", preflight.stdout)
            self.assertIn("underbuilt source shape", preflight.stdout)
            self.assertIn("whole-source rebuild before rhythm tooling", preflight.stdout)
            self.assertIn("rebuild the incomplete article from the strongest workable movement", preflight.stdout)
            self.assertIn("preserve a complete article", preflight.stdout)
            self.assertNotIn("release each carrier after one consequence transfer", preflight.stdout)
            self.assertNotIn("one-for-one source replacement before rhythm tooling", preflight.stdout)
            self.assertNotIn("2-3 load-bearing action clusters", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_preflight_blocks_under_900_as_incomplete(self) -> None:
        fragments = [
            "其实我把车停在楼下，",
            "觉得手心还在冒汗，",
            "突然发现钥匙掉了，",
            "于是低头找了一下，",
            "因为裤子上有菜汤。",
            "好像很丢人。",
        ]
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 晚饭", "", *(fragments * 7)]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3)
            self.assertIn("body_chinese_chars=", preflight.stdout)
            self.assertIn("< 900", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_mixed_short_page_prefers_line_rebalance_over_comma_soften(self) -> None:
        long_line = "我翻了半天还是没有找到那只袜子，床底下只有一团灰和一个瓶盖，洗衣机里也没有，阳台上更没有，最后我开始怀疑它是不是自己跑去过一种不用成双的生活。"
        short_line = "我把抽屉重新关上，暂时不想管它。"
        body_lines = [long_line] * 10 + [short_line] * 16
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 差不多", "", *body_lines]), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLEAN_RUN_CHECKER),
                    str(draft),
                    "--strict",
                    "--draft-gate",
                    "--generator-facing",
                    "--genre",
                    "standard",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("after_content_write_run_rebalance_line_rhythm_once", result.stdout)
            self.assertIn(
                "next_action=one_complete_draft_write_then_run_named_rhythm_script_in_place_then_immediate_wrapper_rerun",
                result.stdout,
            )
            self.assertNotIn(
                "next_action=one_complete_draft_write_then_immediate_wrapper_rerun",
                result.stdout,
            )
            self.assertNotIn("soften_line_endings.py", result.stdout)

    def test_clean_run_checker_preflight_blocks_900s_only_with_weak_source_shape(self) -> None:
        from check_anlin_violations import chinese_len

        fragments = [
            "车把烫得像饭碗边上一圈油",
            "手机在口袋里一直发热",
            "其实我只想在楼下坐一会儿",
            "突然看见路口的灯牌亮了",
            "于是我把车停在白线旁边",
            "因为腿抖得有点不像自己的",
            "好像没人真的在等我回去",
            "我也没办法把这句话说出来",
            "饭味还在嘴里往上顶",
            "裤脚那块菜汤已经干了",
        ]
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            body_lines = fragments * 6
            while chinese_len("\n".join(body_lines)) < 910:
                body_lines.insert(-1, "我又在路口停了一小会儿")
            while chinese_len("\n".join(body_lines)) > 949 and len(body_lines) > 50:
                body_lines.pop(-2)
            body_chars = chinese_len("\n".join(body_lines))
            self.assertGreaterEqual(body_chars, 900)
            self.assertLess(body_chars, 950)
            self.assertLess(sum(1 for line in body_lines if chinese_len(line) >= 28), 6)
            lines = ["# 晚饭", "", *body_lines]
            draft.write_text("\n".join(lines), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("body_chinese_chars=", preflight.stdout)
            self.assertIn("< 950 with source_shape_weak", preflight.stdout)
            self.assertIn("underbuilt source shape", preflight.stdout)
            self.assertIn("one local source replacement before rhythm tooling", preflight.stdout)
            self.assertIn("NEXT_ACTION=repair source/content first", preflight.stdout)
            self.assertIn("replace one repeated or overloaded fragment or relation in place", preflight.stdout)
            self.assertIn("Preserve the complete article", preflight.stdout)
            self.assertNotIn("change medium after its first consequence transfer", preflight.stdout)
            self.assertNotIn("2-3 load-bearing action clusters", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_preflight_allows_900s_when_source_shape_is_ready(self) -> None:
        from check_anlin_violations import chinese_len

        lines = [
            "其实我把车从小区门口推出来的时候，后座还挂着我妈塞的半袋水果，",
            "我说不用。",
            "她说拿着。",
            "饭味还在嘴里，",
            "蒜味也在。",
            "突然想起饭桌上我爸问我最近是不是还在写东西，我筷子停在半空很久，不知道怎么接，",
            "觉得那片青菜掉在裤子上以后，问题就已经替我回答了一大半，像把题目写在膝盖上，",
            "我低头去捡。",
            "汤沾到指甲缝里。",
            "有点黑泥。",
            "于是我说也没写什么，因为嘴里那口饭还没咽下去，人也坐得很低，只好看碗边，",
            "我妈在旁边说多吃点，声音轻得像怕把我从桌子边上吓跑，又像怕我真走了。",
            "我嗯了一声，",
            "很小声。",
            "碗边全是油。",
            "不过门口风一吹，胃里那点蒜味又顶上来，还以为饭桌跟着我追到楼下，",
            "我还以为自己要吐出来，结果只是打了个嗝，声音小得像一个没擦干净的证据。",
            "丢人得很。",
            "电动车车座烫得像刚挨过骂，我坐上去时差点又站起来，膝盖先软了一下，",
            "钥匙插进去的时候，手心还在滑，水果袋在车把上撞来撞去，像一袋没用的关心。",
            "路口那个卤味灯牌亮起来，",
            "红得很正经。",
            "它比我更像一个回家的人。",
            "我骑过去，",
            "没看太久。",
            "小时候每天上学都经过那里，",
            "那时候路边卖文具。",
            "现在卖鸭脖。",
            "我突然发现城市也不怎么换工作，",
            "只是把招牌换成更下饭的样子。",
            "后来手机在口袋里震了两下，我没有看，怕里面又是问我到没到的消息，",
            "路边有人把垃圾袋系得很紧，汤水还是滴到白线边上，像一条小路，",
            "我绕了一点。",
            "车头歪了一下。",
            "有个小孩看我，",
            "像看一个不会骑车的大人。",
            "我想笑。",
            "没笑出来。",
            "喉咙里像卡着米饭，",
            "刚才那口太急了。",
            "回到屋里以后，",
            "钥匙掉在鞋柜下面。",
            "我蹲下去捡。",
            "膝盖响了一声。",
            "非常正式。",
            "像身体替我回答饭桌上的问题。",
            "我最近在干什么。",
            "在捡钥匙。",
            "在擦裤子上的菜汤。",
            "在把钥匙从鞋柜下面抠出来。",
        ]
        boost_targets = [0, 5, 6, 10, 11, 16, 18, 19, 30, 31]
        boost_index = 0
        while chinese_len("\n".join(lines)) < 920:
            lines[boost_targets[boost_index % len(boost_targets)]] += "，那点饭味还在往上顶"
            boost_index += 1
        while chinese_len("\n".join(lines)) > 949 and len(lines) > 48:
            lines.pop(22)

        body_chars = chinese_len("\n".join(lines))
        self.assertGreaterEqual(body_chars, 900)
        self.assertLess(body_chars, 950)
        self.assertGreaterEqual(sum(1 for line in lines if chinese_len(line) >= 28), 6)

        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 晚饭", "", *lines]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("CLEAN_RUN_NOTE: checker call 1/2", result.stdout)
            self.assertNotIn("CLEAN_RUN_PREFLIGHT", result.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 1)
            self.assertEqual(state["preflights"], 0)

    def test_clean_run_checker_preflight_blocks_compressed_prose_shape(self) -> None:
        long_line = (
            "其实我摸了摸手机，觉得六条未读有点多，突然发现三条是运营商的催缴短信，"
            "于是去厕所洗了把脸，因为差点吐出来，丢人得很，好像还是没躲过去。"
            "楼道灯又闪了一下，我还以为有人在后面叫我，回头只有一个快递盒歪在门口，"
            "盒角湿了一块，像谁把一口气吐在那里。"
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 日寄", "", *([long_line] * 9)]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3)
            self.assertIn("CLEAN_RUN_PREFLIGHT", preflight.stdout)
            self.assertIn("body_lines=9 < 45", preflight.stdout)
            self.assertIn("prose_block_shape=compressed", preflight.stdout)
            self.assertIn("NEXT_ACTION=run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place`", preflight.stdout)
            self.assertIn("do not mentally estimate a line quota", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_preflight_orders_content_repair_before_rebalance_for_mixed_blockers(self) -> None:
        line = (
            '狗哥发微信说下个月结婚，我看高铁票和随礼看了半天，觉得那个数字像一张没盖章的罚单，'
            '他问能不能来，我其实打了"项目走不开"，手指停在发送键上，水杯底下的纸巾慢慢变软，'
            '桌角还有一圈灰，我坐着没有动，椅子腿也跟着歪了一下。'
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 纸巾", "", *([line] * 10)]), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLEAN_RUN_CHECKER),
                    str(draft),
                    "--strict",
                    "--draft-gate",
                    "--genre",
                    "standard",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("prose_block_shape=compressed", result.stdout)
            self.assertIn("connectors=", result.stdout)
            self.assertIn("rough_self_damage=missing", result.stdout)
            self.assertIn("quoted_dialogue=present", result.stdout)
            self.assertIn("NEXT_ACTION=repair source/content first", result.stdout)
            self.assertIn(
                "after the last content write, run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place`",
                result.stdout,
            )
            self.assertIn("if you edit draft.md after that script, rerun the script before checking", result.stdout)
            self.assertNotIn("before any new prose rewrite", result.stdout)
            self.assertNotIn("before hand rewriting", result.stdout)

    def test_clean_run_checker_postcheck_preflight_blocks_shrunken_second_call(self) -> None:
        lines = [
            "晚上十点多，水槽里泡着早上剩的那只碗，洗洁精已经没了泡，",
            "拿抹布擦了两圈，油污还在，又拧开水冲，水太凉，手指发僵，",
            "干脆先不洗了，倒掉水，把碗扣在沥水架上，先去换拖鞋。",
            "拖鞋底断了一只，踩在卫生间地砖上打滑，",
            "啪一声轻微响，差点跪下去，扶住洗脸台站稳。",
            "另外那双绿色硬底拖鞋挂在阳台夹子上，白天晒的，",
            "取下来往地上磕了两下，确实硬，",
            "还是套进去了，脚后跟立刻有点硌，磨得疼。",
            "坐在床边拿起手机，微信列表里狗哥的消息攒了几天没点开，",
            "通知栏上他的头像旁边露出请柬截图的一角，浅金色，点进去，",
            "十二月二十一号，在通程，他说备了一桌，问我有没有空来。",
            "退出微信打开12306看了一眼，七号的票还没开售，",
            "往年差不多二十七块硬座，动车一百一，",
            "随礼的话大学室友一般六百，狗哥不是一个宿舍的，四百差不多，",
            "加起来小一千，加上请两天假，还有住宿。",
            "心算完了放下手机上厕所，上完洗了手，凉水又激了一下，",
            "回来看着那条消息，打了几个字又删掉，",
            "发了句：最近项目忙，可能去不了，到时候看情况。",
            "手是湿的，在睡裤上蹭了两下，又看了一眼，",
            "消息上墙了。",
            "对方正在输入，消失，又出现，消失。",
            "他回了一句：没事，理解的，工作要紧。",
            "我把屏幕朝下扣在枕头边，坐下来觉得脚后跟疼，",
            "绿色硬拖鞋磨出一个小水泡，摁了一下，没破，",
            "但指腹沾了一丁点湿，有一点胀。",
            "其实想回句什么，比如下次吃饭我请，但没打。",
            "打开微信转账页，琢磨了一会儿金额，",
            "觉得随四百像是补过，又像是硬撑，最后还是锁了屏。",
            "垃圾满了两天没倒，前天拎到楼道尽头发现大桶满了拎回来，",
            "放在鞋柜旁边，今天又多了外卖盒和饮料瓶。弯腰把袋子拎起来系紧，",
            "走到门口开门，楼道感应灯没亮，可能是坏了。",
            "犹豫了两秒，",
            "提着垃圾往楼道走，硬拖鞋敲在地砖上响声太大。",
            "走到一半对面邻居的门开了一条缝，有光透出来，但门没开全，",
            "我没吭声，加快几步走过去，",
            "扔完往回走的时候灯才亮，发现自己刚才一直屏着呼吸，",
            "凉拖鞋底沾了楼道里的灰，湿脚印从门口一直延伸到玄关。",
            "关门，反锁，低头看到脚后跟那个水泡在荧光灯下发亮，",
            "拿手摸了一下有点滑，赶紧在裤子上蹭掉。",
            "结果翻了一圈没找到针线盒。",
            "算了。",
            "回到卧室打开12306看了一眼，硬座二十七块，确认订单那页停了几秒，没点，退了出来。",
            "关掉床头灯，硬拖鞋放在床脚，磨破的脚后跟碰到被子有点刺，",
            "我侧了个身，觉得那杯水放得太远，不想起来拿，",
            "意识慢慢往下沉，脚后跟的胀一直不消。",
        ]
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 碗跟拖鞋", "", *lines]), encoding="utf-8")
            state_path = draft.parent / ".anlin-clean-run-state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "draft": str(draft.resolve()),
                        "calls": 1,
                        "preflights": 2,
                        "snapshots": {},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLEAN_RUN_CHECKER),
                    str(draft),
                    "--strict",
                    "--draft-gate",
                    "--genre",
                    "standard",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("CLEAN_RUN_POSTCHECK_PREFLIGHT", result.stdout)
            self.assertIn("do not spend checker call 2/2", result.stdout)
            self.assertIn("body_chinese_chars=", result.stdout)
            self.assertNotIn("connectors=", result.stdout)
            self.assertIn("Rewrite by replacing one broken fragment relation in place", result.stdout)
            self.assertIn(
                "preserve the complete article across the replacement and neighboring existing movements",
                result.stdout,
            )
            self.assertIn("not by adding a packet", result.stdout)
            self.assertIn("do not add material for a metric", result.stdout)
            self.assertNotIn("add one functional consequence cluster", result.stdout)
            self.assertNotIn("add one refusal-coupled consequence cluster", result.stdout)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 1)
            self.assertEqual(state.get("post_checker_preflights"), 1)
            self.assertFalse(state.get("stopped", False))
            self.assertIn("post_checker_preflight_1", state["snapshots"])
            self.assertNotIn("checker_call_2_submission", state["snapshots"])

    def test_clean_run_checker_shape_only_postcheck_does_not_add_source_material(self) -> None:
        lines = [
            "其实我在厕所门口差点跪下，裤腿蹭上黑泥很丢人。",
            "我觉得收银员还在等付款，手机却卡在二维码那页。",
            "突然发现袋子漏汤，鞋底一滑，我扶着墙才没摔。",
            "不过后面的人咳了一声，我把脏手藏到袖子里面。",
            "因为胃里咕噜咕噜，扫码两次都没扫上，店员没走。",
            "所以我拿纸巾擦了擦手，油印反而蹭到屏幕上。",
            "于是我把袋子递回去，收银员看了裤脚一眼没接。",
            "好像这单饭要命，塑料袋又裂了，汤流到拖鞋边。",
            "原来我还以为是水，低头才发现裤子上都是红油。",
            "结果我又去厕所洗手，门口那个人一直等着我让路。",
        ] * 5
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 袋子", "", *lines]), encoding="utf-8")
            submitted_bytes = draft.read_bytes()
            state_path = draft.parent / ".anlin-clean-run-state.json"
            state_path.write_text(
                json.dumps({"draft": str(draft.resolve()), "calls": 1}, ensure_ascii=False),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate", "--genre", "standard"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("CLEAN_RUN_POSTCHECK_PREFLIGHT", result.stdout)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            messages = state["last_post_checker_preflight_messages"]
            shape_prefixes = ("short_breath_lines=", "period_row_grid=", "early_comma_ratio=")
            self.assertTrue(messages)
            self.assertTrue(all(message.startswith(shape_prefixes) for message in messages), messages)
            self.assertNotIn("known underbuilt source", result.stdout)
            self.assertNotIn("add one functional consequence cluster", result.stdout)
            self.assertIn("wrapper left `draft.md` unchanged", result.stdout)

            stopped = subprocess.run(
                [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate", "--genre", "standard"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(stopped.returncode, 0, stopped.stdout + stopped.stderr)
            self.assertIn("CLEAN_RUN_PREFLIGHT_STOP", stopped.stdout)
            self.assertIn("source-or-shape action", stopped.stdout)
            self.assertNotIn("source-rewrite chance", stopped.stdout)
            self.assertEqual(draft.read_bytes(), submitted_bytes)
            stopped_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(stopped_state["calls"], 1)
            self.assertEqual(stopped_state["stop_reason"], "post-checker-preflight")
            self.assertEqual(Path(stopped_state["snapshots"]["bounded_final"]).read_bytes(), submitted_bytes)

    def test_clean_run_checker_overfull_postcheck_routes_to_trim_without_mutating_submission(self) -> None:
        long_line = "其实我觉得厕所灯突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            submitted_bytes = "\r\n".join(["# 日寄", "", *([long_line] * 46)]).encode("utf-8")
            draft.write_bytes(submitted_bytes)
            state_path = draft.parent / ".anlin-clean-run-state.json"
            state_path.write_text(
                json.dumps({"draft": str(draft.resolve()), "calls": 1}, ensure_ascii=False),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate", "--genre", "standard"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("CLEAN_RUN_POSTCHECK_PREFLIGHT", result.stdout)
            self.assertIn("Post-check overfull reset", result.stdout)
            self.assertIn("remove or replace repeated material", result.stdout)
            self.assertNotIn("Perform only the explicit local rhythm action", result.stdout)
            self.assertNotIn("add one functional consequence cluster", result.stdout)
            self.assertEqual(draft.read_bytes(), submitted_bytes)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 1)

    def test_clean_run_checker_preflight_blocks_missing_true_short_breaths(self) -> None:
        lines = [
            "其实我觉得手背一直发烫，突然发现客户还在催我",
            "于是我把车停在树下，因为裤脚湿得有点丢人",
            "好像这单送完就能歇一下，结果手机又亮了一次",
        ] * 20
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 下午三点半", "", *lines]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3)
            self.assertIn("short_breath_lines=0 < 4", preflight.stdout)
            self.assertIn("<=8-Chinese-character breath drops", preflight.stdout)
            self.assertIn("split a few earned <=8-character landings", preflight.stdout)
            self.assertIn("do not append decorative one-word captions", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_preflight_blocks_54_line_draft_without_short_breaths(self) -> None:
        lines = [
            "其实我把饭盒挂到车把上的时候，塑料袋一直蹭着手腕，",
            "突然发现路口的灯牌亮得很正经，好像比我更像一个人，",
            "于是我低头看裤脚那块菜汤，因为它已经干成一小块地图，",
        ] * 18
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 路口寄", "", *lines]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("short_breath_lines=0 < 4", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_allows_single_short_breath_near_miss_to_reach_checker(self) -> None:
        cluster = [
            "其实门口那条毛巾又弹出来，冷风贴到脚踝上，",
            "我用脚尖去顶，拖鞋后跟一歪，脚趾露出来有点丢人，",
            "突然发现外卖袋底下也在渗汤，手心被塑料勒出一道白印，",
            "于是去厕所找纸巾，抽纸盒空得很干净，只剩一个纸芯，",
            "原来水壶也没插紧，灯亮了一下又灭，我把插头怼回去，",
            "碗边那片香菜贴着筷子，夹了两次还是滑回汤里，",
        ]
        lines = (cluster * 8) + ["很丢人。", "没回。", "脚冷。", "我把碗推远了一点，手背还在发紧，"]
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join(["# 门缝", "", *lines]), encoding="utf-8")
            messages = preflight_messages(draft)
            self.assertEqual(len(messages), 1, messages)
            self.assertTrue(messages[0].startswith("short_breath_lines=3 < 4"), messages)
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLEAN_RUN_CHECKER),
                    str(draft),
                    "--strict",
                    "--draft-gate",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotIn("CLEAN_RUN_PREFLIGHT", result.stdout)
            self.assertIn("CLEAN_RUN_NOTE: checker call 1/2", result.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 1)
            self.assertEqual(state["preflights"], 0)

    def test_clean_run_checker_allows_near_miss_long_line_count_to_reach_checker(self) -> None:
        long_lines = [
            "其实我蹲在地上拆箱子的时候，指甲缝里都是灰，手背还被胶带划了一道口子，",
            "收银员扫完水以后看了我一眼，又看了一眼我的手，我把手往口袋里塞了一下，",
            "裤子后面全是灰，在走廊灯下面看得很清楚，像我把便宜房间穿在身上出来了，",
        ]
        medium_lines = [
            "于是我坐在地上继续拆那个纸箱，",
            "胶带粘到手背上，撕下来还有点疼，",
            "突然发现地址还停在输入框里。",
            "好像这屋子也没完全认得我，",
            "收银小票被水泡软了，贴在鞋边。",
        ] * 14
        short_lines = ["很丢人。", "没发。", "手很脏。", "要命。"]
        body = "\n".join(["# 小票", "", *long_lines, *medium_lines, *short_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate"]
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertNotIn("CLEAN_RUN_PREFLIGHT", result.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["preflights"], 0)
            self.assertEqual(state["calls"], 1)

    def test_clean_run_checker_preflight_stops_after_three_attempts(self) -> None:
        short_body = "\n".join(["# 日寄", "", "杯子脏了。"])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(short_body, encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            third = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(first.returncode, 3)
            self.assertIn("rebalance_line_rhythm.py", first.stdout)
            self.assertIn("pain or heat alone is too polite", first.stdout)
            self.assertEqual(second.returncode, 3)
            self.assertEqual(third.returncode, 0)
            self.assertIn("CLEAN_RUN_PREFLIGHT_STOP", third.stdout)
            self.assertIn("FINAL BOUNDARY. DO NOT WRITE draft.md", third.stdout)
            self.assertIn("DO NOT USE PREFLIGHT DETAILS AS A TODO LIST", third.stdout)
            self.assertIn("No checker call was consumed", third.stdout)
            self.assertNotIn("body_lines=", third.stdout)
            self.assertNotIn("connectors=", third.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 3)
            self.assertTrue(state["stopped"])
            self.assertEqual(state["stop_reason"], "preflight")
            self.assertIn("last_preflight_messages", state)
            fourth = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(fourth.returncode, 0)
            self.assertIn("FINAL BOUNDARY already reached", fourth.stdout)
            bypass = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(bypass.returncode, 0)
            findings = json.loads(bypass.stdout)
            errors = [item for item in findings if item["severity"] == "error"]
            self.assertTrue(any(item["rule"] == "clean-eval停止边界越过" for item in errors))
            (draft.parent / ".anlin-clean-run-state.json").unlink()
            bypass_after_delete = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(bypass_after_delete.returncode, 0)
            findings_after_delete = json.loads(bypass_after_delete.stdout)
            errors_after_delete = [item for item in findings_after_delete if item["severity"] == "error"]
            self.assertTrue(any(item["rule"] == "clean-eval停止边界越过" for item in errors_after_delete))

    def test_clean_run_checker_preflight_names_soften_script_for_overclosed_early_lines(self) -> None:
        line = "其实我觉得厕所灯突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"
        body = "\n".join(["# 日寄", "", *([line] * 46)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLEAN_RUN_CHECKER),
                    str(draft),
                    "--strict",
                    "--draft-gate",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 3)
            self.assertIn("early_comma_ratio", result.stdout)
            self.assertIn("soften_line_endings.py", result.stdout)
            self.assertIn("if you edit draft.md after that script, rerun the script before checking", result.stdout)

    def test_clean_run_checker_preflight_orders_content_repair_before_soften_script(self) -> None:
        line = "其实我觉得窗户有点冷，好像手机也卡，于是把杯子放回桌上。"
        body = "\n".join(["# 日寄", "", *([line] * 46)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLEAN_RUN_CHECKER),
                    str(draft),
                    "--strict",
                    "--draft-gate",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("early_comma_ratio", result.stdout)
            self.assertIn("rough_self_damage=missing", result.stdout)
            self.assertIn("combined with content repairs", result.stdout)
            self.assertIn("as the last action before the wrapper", result.stdout)
            self.assertIn("if you edit draft.md after that script, rerun the script before checking", result.stdout)

    def test_clean_run_checker_preflight_names_bare_short_line_grid(self) -> None:
        lines = [
            "手机亮了",
            "又暗了",
            "没点开",
            "其实我觉得杯子有点旧",
            "不过水龙头响了一下",
            "因为接口又开始渗水",
            "所以纸巾也湿了",
            "手指蹭到裤子上",
        ] * 9
        body = "\n".join(["# 日寄", "", *lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLEAN_RUN_CHECKER),
                    str(draft),
                    "--strict",
                    "--draft-gate",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 3)
            self.assertIn("bare_line_grid=", result.stdout)
            self.assertIn("do not turn the article into caption-like naked rows", result.stdout)

    def test_clean_run_checker_allows_near_miss_connector_draft_to_reach_checker(self) -> None:
        lines = [
            "其实我把杯子拿去洗，水龙头先咳了一下喷到裤子上，",
            "没动。",
            "觉得这事有点丢人，鞋底还粘着菜市场的汤，差点跪在门口，",
            "好像脚趾头也露在外面，缩了一下还是被楼道灯照见，还以为自己没躲过去，",
            "于是把手机翻过去，假装没看到那条快超时的提醒。",
        ] * 12
        body = "\n".join(["# 日寄", "", *lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertNotIn("CLEAN_RUN_PREFLIGHT", result.stdout)
            self.assertIn("CLEAN_RUN_NOTE: checker call 1/2", result.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 1)
            self.assertEqual(state["preflights"], 0)

    def test_clean_run_checker_surface_preflight_blocks_high_risk_forms_without_consuming_call(self) -> None:
        filler = "其实我觉得厕所灯突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"
        cases = [
            ("binary_reframe=present", ["不是包装袋漏，是电动车前面那个篮子。"]),
            ("binary_reframe=present", ["不是不想帮。是帮了还要继续站在太阳底下。"]),
            ("binary_reframe=present", ["我不是叔叔，我只是失败得比较显老。"]),
            ("comment_chain_markers=", ["评论区有一行字写着展示给谁看。"]),
            ("process_leak_terms=", ["final article"]),
            ("meta_ai_topic_hits=", ["驿站老板刷短视频，说怎么识别AI写的文章。", "我又打开AI对话窗口。"]),
            ("current_office_persona=", ["到了公司，同事小李喊我张哥，领导说KPI和营收都要看。"]),
            (
                "background_display_groups=",
                [
                    "211毕业之后我在云南送外卖，狗哥发消息问我王者打不打。",
                    "我点开知乎，又想起自己被裁之后痛风，脚踝还疼。",
                ],
            ),
        ]
        for expected_message, risky_lines in cases:
            with self.subTest(expected_message=expected_message):
                with tempfile.TemporaryDirectory() as temp:
                    draft = Path(temp) / "draft.md"
                    draft.write_text("\n".join(["# 日寄", "", *risky_lines, *([filler] * 30)]), encoding="utf-8")
                    command = [
                        sys.executable,
                        str(CLEAN_RUN_CHECKER),
                        str(draft),
                        "--strict",
                        "--draft-gate",
                    ]
                    preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
                    self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
                    self.assertIn("CLEAN_RUN_PREFLIGHT", preflight.stdout)
                    self.assertIn(expected_message, preflight.stdout)
                    state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
                    self.assertEqual(state["calls"], 0)
                    self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_binary_preflight_requires_global_local_repair(self) -> None:
        filler = "其实我觉得厕所灯突然坏了，因为我站着很丢人，像系统坏了，手指还蹭着黑泥，"
        risky_lines = [
            "到家手还在抖，不是怕，是热的，吹了一路热风吹得脑袋发懵，",
            "第一反应不是看伤口而是蹲下捡没洒的米饭，",
        ]
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(
                "\n".join(["# 日寄", "", *risky_lines, *([filler, "没动。"] * 26)]),
                encoding="utf-8",
            )
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("binary_reframe=present count=2", preflight.stdout)
            self.assertIn("scan_all_occurrences=true", preflight.stdout)
            self.assertIn("L2:", preflight.stdout)
            self.assertIn("L3:", preflight.stdout)
            self.assertIn("Revise locally", preflight.stdout)
            self.assertIn("do not add new scenes", preflight.stdout)
            self.assertIn("short drops", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)
            self.assertEqual(state["last_preflight_messages"][0].split()[0], "binary_reframe=present")

    def test_clean_run_checker_does_not_treat_shi_bu_shi_as_binary_reframe(self) -> None:
        cluster = [
            "其实楼下水管又响了一下，",
            "我觉得像有人在墙里拖塑料袋。",
            "突然发现指甲缝里黑泥还在，",
            "于是换手去拿杯子，因为那只手看起来更丢人。",
            "不过收银员看了我一眼。",
            "很丢人。",
            "胃响了一声。",
            "我假装没听见。",
        ]
        body = "\n".join(
            [
                "# 水管",
                "",
                "室友在旁边问我是不是还没吃饭，我说吃了，其实只吃了半个冷包子。",
                *(cluster * 7),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotIn("binary_reframe=present", result.stdout)

    def test_clean_run_checker_flags_prompt_performing_identity_probe(self) -> None:
        cluster = [
            "其实楼下水管又响了一下，",
            "我觉得像有人在墙里拖塑料袋。",
            "突然发现指甲缝里黑泥还在，",
            "于是换手去拿杯子，因为那只手看起来更丢人。",
            "不过收银员看了我一眼。",
            "很丢人。",
            "胃响了一声。",
            "我假装没听见。",
        ]
        body = "\n".join(
            [
                "# 水管",
                "",
                "他突然问我，你是不是以前那个大学的，就是后面有条小吃街那个。",
                *(cluster * 7),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("prompt_performing_dialogue=present", result.stdout)
            self.assertNotIn("binary_reframe=present", result.stdout)

    def test_clean_run_checker_preflight_blocks_learned_ending_button_without_consuming_call(self) -> None:
        cluster = [
            "其实水龙头咳了一下，水从接口那边斜着喷出来，",
            "我觉得裤脚湿得像刚从鱼摊回来。",
            "丢人。",
            "后来发现胶带粘不上，手上全是灰，老板还问我要不要换贵的那种。",
            "不过我没换，因为手机余额看起来比水管还紧。",
            "很冷。",
        ]
        body = "\n".join(["# 胶带", "", *(cluster * 10), "算了。"])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate"]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)

            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("CLEAN_RUN_PREFLIGHT", preflight.stdout)
            self.assertIn("learned_ending_button=present", preflight.stdout)
            self.assertIn("unfinished practical action", preflight.stdout)

            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_preflight_blocks_today_first_like_this_tail(self) -> None:
        cluster = [
            "其实水龙头咳了一下，水从接口那边斜着喷出来，",
            "我觉得裤脚湿得像刚从鱼摊回来。",
            "丢人。",
            "后来发现胶带粘不上，手上全是灰，老板还问我要不要换贵的那种。",
            "不过我没换，因为手机余额看起来比水管还紧。",
            "很冷。",
        ]
        body = "\n".join(["# 胶带", "", *(cluster * 10), "今天先这样。"])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("CLEAN_RUN_PREFLIGHT", result.stdout)
            self.assertIn("learned_ending_button=present", result.stdout)
            self.assertIn("unfinished practical action", result.stdout)

            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_preflight_blocks_pure_ambient_ending_without_consuming_call(self) -> None:
        cluster = [
            "其实水龙头咳了一下，水从接口那边斜着喷出来，",
            "我觉得裤脚湿得像刚从鱼摊回来。",
            "丢人。",
            "后来发现胶带粘不上，手上全是灰，老板还问我要不要换贵的那种。",
            "不过我没换，因为手机余额看起来比水管还紧。",
            "很冷。",
        ]
        body = "\n".join(["# 胶带", "", *(cluster * 10), "外面路灯还亮着。"])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate"]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)

            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("CLEAN_RUN_PREFLIGHT", preflight.stdout)
            self.assertIn("pure_ambient_ending=present", preflight.stdout)
            self.assertIn("already-earned unfinished action", preflight.stdout)

            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

    def test_clean_run_checker_preflight_blocks_standard_period_row_grid(self) -> None:
        cluster = [
            "充电线压在杯子下面，手机还是一会儿亮一会儿灭。",
            "我把外卖袋放到桌上，油从袋底慢慢洇出来。",
            "骑手站在门口等我找纸，我手上全是洗手液泡沫。",
            "门关得太快，袋子角撞到门框，又滴了一点汤。",
            "我低头擦裤脚，发现那块酱油印比刚才更大。",
        ]
        body = "\n".join(["# 充电线", "", *(cluster * 11)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            command = [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate", "--genre", "standard"]
            preflight = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)

            self.assertEqual(preflight.returncode, 3, preflight.stdout + preflight.stderr)
            self.assertIn("period_row_grid=present", preflight.stdout)
            self.assertIn("one finished `。` sentence per row", preflight.stdout)
            self.assertIn("breathing clusters", preflight.stdout)

    def test_clean_run_final_normalize_preserves_existing_line_corridor(self) -> None:
        cluster = [
            "昨天搬到这边，搬家公司的人问我几楼，",
            "他抬头看了一眼楼梯，像看见我欠他钱。其实也没有很多东西，只是每个袋子都很难看，",
            "我说收。",
            "很丢人。",
            "小票后面粘着一点米粒，硬硬的，抠不下来。我突然想起以前租的那个房间，",
            "输入框空了。",
        ]
        body = "\n".join(["# 朝东寄", "", *(cluster * 10)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            normalize_before_final_check(draft)
            lines = draft.read_text(encoding="utf-8").splitlines()
            content = []
            seen_title = False
            for line in lines:
                stripped = line.strip()
                if not seen_title and stripped:
                    seen_title = True
                    continue
                if stripped and not stripped.startswith("<!--"):
                    content.append(stripped)
            lengths = [len("".join(ch for ch in line if "\u4e00" <= ch <= "\u9fff")) for line in content]
            self.assertGreaterEqual(len(content), 55)
            self.assertLessEqual(len(content), 70)
            self.assertGreaterEqual(sum(1 for length in lengths if length <= 8), 10)
            self.assertGreaterEqual(sum(1 for length in lengths if length >= 28), 10)

    def test_clean_eval_trace_flags_pre_draft_refs_and_stop_escape(self) -> None:
        log = """
        → Read C:/skill/references/clean-generation-brief.md
        $ Test-Path .anlin-clean-eval-mode
        → Read C:/skill/references/anti-ai-slop.md
        ← Write draft.md
        CLEAN_RUN_PREFLIGHT_STOP: draft is still not ready
        ← Write draft.md
        Remove-Item "case/.anlin-clean-run-state.json"
        $ python scripts/check_anlin_violations.py draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval首稿前加载修复/评审引用", rules)
            self.assertIn("stop后继续写稿", rules)
            self.assertIn("stop后删除状态", rules)
            self.assertIn("stop后切普通checker", rules)

    def test_clean_eval_trace_accepts_minimal_clean_flow(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
        → Read C:/skill/references/clean-generation-brief.md
        → Read C:/skill/references/era-state.md
        ← Write draft.md
        $ python scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_NOTE: checker call 1/2
        ← Write draft.md
        $ python scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            findings = json.loads(result.stdout)
            self.assertFalse(any(item["severity"] == "error" for item in findings), findings)

    def test_clean_eval_trace_accepts_marker_then_standalone_location(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Get-ChildItem -Force .anlin-clean-eval-mode -ErrorAction SilentlyContinue
        $ Get-Location
        目录: C:/eval-workspace/iteration-67/eval-03
        Path : C:/eval-workspace/iteration-67/eval-03
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval写稿前未确认当前目录", rules)

    def test_clean_eval_trace_rejects_combined_marker_and_location_action(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Get-ChildItem -Force .anlin-clean-eval-mode -ErrorAction SilentlyContinue; Get-Location
        目录: C:/eval-workspace/iteration-67/eval-03
        → Read C:/skill/references/clean-eval-first-draft-minimum.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval写稿前未确认当前目录", rules)

    def test_clean_eval_trace_rejects_cwd_after_reference_read(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path -LiteralPath ".anlin-clean-eval-mode"
        True
        → Read C:/skill/references/clean-eval-first-draft-minimum.md
        $ Get-Location
        C:/eval-workspace/iteration-67/eval-03
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval当前目录确认顺序错误", rules)

    def test_clean_eval_trace_rejects_shell_path_probe_before_cwd(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path -LiteralPath ".anlin-clean-eval-mode"
        True
        $ Get-ChildItem references -Filter *.md
        $ Get-Location
        C:/eval-workspace/iteration-67/eval-03
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval当前目录确认顺序错误", rules)

    def test_clean_eval_trace_requires_real_marker_action_not_path_substring(self) -> None:
        log = """
        → Glob C:/eval-workspace/iteration-67/eval-03/.anlin-clean-eval-mode
        → Read C:/skill/references/clean-eval-first-draft-minimum.md
        $ Get-Location
        C:/eval-workspace/iteration-67/eval-03
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval写稿前未检查模式标记", rules)

    def test_clean_eval_trace_ignores_bash_workdir_field_as_path_probe(self) -> None:
        log = '''
        TOOL bash
        TITLE Test-Path -LiteralPath ".anlin-clean-eval-mode"
        INPUT {"command": "Test-Path -LiteralPath ".anlin-clean-eval-mode"", "workdir": "C:/eval-workspace/iteration-158/eval-09"}
        OUTPUT True
        TOOL bash
        TITLE Get-Location
        INPUT {"command": "Get-Location", "workdir": "C:/eval-workspace/iteration-158/eval-09"}
        OUTPUT C:/eval-workspace/iteration-158/eval-09
        TOOL read
        TITLE C:/skill/references/clean-eval-first-draft-minimum.md
        INPUT {"filePath": "C:/skill/references/clean-eval-first-draft-minimum.md"}
        TOOL read
        TITLE C:/skill/references/anlin-collage-source-model.md
        INPUT {"filePath": "C:/skill/references/anlin-collage-source-model.md"}
        ← Write draft.md
        TOOL bash
        TITLE clean_run_checker.py draft.md
        INPUT {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing --genre standard", "workdir": "C:/eval-workspace/iteration-158/eval-09"}
        OUTPUT CLEAN_RUN_STOP: FINAL BOUNDARY
        TOOL read
        TITLE C:/eval-workspace/iteration-158/eval-09/draft.md
        INPUT {"filePath": "draft.md"}
        '''
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval当前目录确认顺序错误", rules)

    def test_clean_eval_trace_accepts_powershell_relative_set_content_write(self) -> None:
        log = '''
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
        → Read C:/skill/references/clean-generation-brief.md
        ✗ Invalid Tool
        The arguments provided to the tool are invalid: Invalid input for tool write.
        "@ | Set-Content -Path "draft.md" -Encoding UTF8
        $ python "C:/skill/scripts/clean_run_checker.py" draft.md --strict --draft-gate
        CLEAN_RUN_NOTE: checker call 1/2
        "@ | Set-Content -Path "draft.md" -Encoding UTF8
        $ python "C:/skill/scripts/clean_run_checker.py" draft.md --strict --draft-gate
        CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2. DO NOT WRITE draft.md.
        → Read draft.md
        '''
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            findings = json.loads(result.stdout)
            self.assertFalse(any(item["severity"] == "error" for item in findings), findings)
            self.assertTrue(any(item["rule"] == "无效工具调用" for item in findings), findings)

    def test_clean_eval_trace_accepts_formatted_opencode_patch_write(self) -> None:
        log = """
        opencode.exe : At C:/Users/34025/AppData/Roaming/npm/opencode.ps1:14 char:3
        +   & "$basedir/node_modules/opencode-ai/bin/opencode.exe" $args
        → Skill "anlin-writing"
        $ Test-Path -LiteralPath ".anlin-clean-eval-mode"
        True
        $ Get-Location
        Path
        ----
        C:/eval-workspace/iteration-92/eval-09/bounded
        → Read C:/skill/references/clean-generation-brief.md
        → Read C:/skill/references/standard-diary-source-engine.md
        Thinking: **Drafting a project plan**
        % Patch 1 file
        已写入第一版 `draft.md`。
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval未写入draft.md", rules)

    def test_clean_eval_trace_accepts_patch_when_draft_context_precedes_patch(self) -> None:
        log = """
        opencode.exe : At C:/Users/34025/AppData/Roaming/npm/opencode.ps1:14 char:3
        +   & "$basedir/node_modules/opencode-ai/bin/opencode.exe" $args
        → Skill "anlin-writing"
        $ Test-Path -LiteralPath ".anlin-clean-eval-mode"
        $ Get-Location
        True
        C:/eval-workspace/iteration-95/eval-09/bounded
        → Read C:/skill/references/clean-generation-brief.md
        → Read C:/skill/references/standard-diary-source-engine.md
        我现在写入首版 `draft.md`。主题会压低成一个晚上的实际动作链。
        % Patch 1 file
        首版已保存，接下来只用 clean-eval wrapper 检查。
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2. DO NOT WRITE draft.md.
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval未写入draft.md", rules)

    def test_clean_eval_trace_rejects_formatted_patch_without_draft_context(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path -LiteralPath ".anlin-clean-eval-mode"
        True
        $ Get-Location
        C:/eval-workspace/iteration-93/eval-09/bounded
        → Read C:/skill/references/clean-generation-brief.md
        % Patch 1 file
        已更新说明。
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval未写入draft.md", rules)

    def test_clean_eval_trace_rejects_missing_persisted_draft_even_if_reference_mentions_checker(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        True
        → Read C:/skill/references/clean-generation-brief.md
        The brief says run python scripts/clean_run_checker.py draft.md --strict --draft-gate later.
        It also says Write draft.md after drafting.
        我坐在桌前，手机屏幕亮着。群聊里有人发母亲节快乐，但我没回复。
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval未调用clean_run_checker", rules)
            self.assertIn("clean-eval未写入draft.md", rules)

    def test_clean_eval_trace_ignores_reference_text_that_mentions_relative_write(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-77/eval-03/bounded
        → Read C:/skill/references/clean-generation-brief.md
        Write the complete titled article to relative `draft.md` in the current task working directory. The write/file tool path must be exactly `draft.md` or `./draft.md`.
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval写稿路径不是相对draft.md", rules)

    def test_clean_eval_trace_flags_direct_normal_checker_even_after_clean_wrapper(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2
        $ python C:/skill/scripts/check_anlin_violations.py draft.md 2>&1 | Select-Object -First 5
        [warning] line 33 AI二元解释句式
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval直接调用普通checker", rules)

    def test_clean_eval_trace_flags_ad_hoc_metric_probe(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-86/eval-03/bounded
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python -c "
        import re
        with open('draft.md', 'r', encoding='utf-8') as f:
            body_lines = [line for line in f if line.strip()]
        body_text = ''.join(body_lines)
        print(f'Chinese chars in body: {len(re.findall(r"[\\u4e00-\\u9fff]", body_text))}')
        print(f'Body lines: {len(body_lines)}')
        print('Connectors found: 其实, 觉得')
        "
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval自建指标预检", rules)

    def test_clean_eval_trace_flags_multiple_pre_wrapper_draft_writes(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-86/eval-03/bounded
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval首个wrapper前多次改写draft", rules)

    def test_clean_eval_trace_flags_rewrite_after_rhythm_script_without_rerun(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2
        $ python C:/skill/scripts/rebalance_line_rhythm.py draft.md --in-place
        ← Read draft.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("节奏脚本后重写未重跑节奏修复", rules)

    def test_clean_eval_trace_flags_named_rhythm_action_skipped_after_content_write(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-164/eval-09/bounded
        → Read C:/skill/references/clean-eval-first-draft-minimum.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing
        CLEAN_RUN_PREFLIGHT: findings=source_shape=underbuilt; source_action=replace_one_broken_fragment_or_relation_in_place; after_content_write_run_rebalance_line_rhythm_once_in_place_as_final_mutation_then_immediate_wrapper_rerun; next_action=one_complete_draft_write_then_run_named_rhythm_script_in_place_then_immediate_wrapper_rerun
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("已命名节奏动作被跳过", rules)

    def test_clean_eval_trace_accepts_named_rhythm_action_after_last_content_write(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-165/eval-09/bounded
        → Read C:/skill/references/clean-eval-first-draft-minimum.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing
        CLEAN_RUN_PREFLIGHT: findings=source_shape=underbuilt; source_action=replace_one_broken_fragment_or_relation_in_place; after_content_write_run_rebalance_line_rhythm_once_in_place_as_final_mutation_then_immediate_wrapper_rerun; next_action=one_complete_draft_write_then_run_named_rhythm_script_in_place_then_immediate_wrapper_rerun
        ← Write draft.md
        $ python C:/skill/scripts/rebalance_line_rhythm.py draft.md --in-place
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("已命名节奏动作被跳过", rules)

    def test_clean_eval_trace_flags_content_write_before_pure_shape_action(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-165/eval-09/bounded
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing
        CLEAN_RUN_PREFLIGHT: findings=rhythm_shape=needs_local_reset; shape_action=run_rebalance_line_rhythm_in_place_as_final_mutation_then_immediate_wrapper_rerun; next_action=run_named_rhythm_script_in_place_then_immediate_wrapper_rerun
        ← Write draft.md
        $ python C:/skill/scripts/rebalance_line_rhythm.py draft.md --in-place
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("纯shape动作前额外写稿", rules)

    def test_clean_eval_trace_flags_rhythm_script_after_stop(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-165/eval-09/bounded
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        $ python C:/skill/scripts/rebalance_line_rhythm.py draft.md --in-place
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("stop后运行节奏脚本", rules)

    def test_clean_eval_trace_flags_rhythm_script_before_first_wrapper(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-81/eval-03/bounded
        → Read C:/skill/references/clean-generation-brief.md
        → Read C:/skill/references/standard-diary-source-engine.md
        ← Write draft.md
        $ python C:/skill/scripts/soften_line_endings.py draft.md --in-place
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval首个wrapper前运行节奏脚本", rules)

    def test_clean_eval_trace_allows_rewrite_after_rhythm_script_when_rerun_before_checker(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2
        $ python C:/skill/scripts/rebalance_line_rhythm.py draft.md --in-place
        ← Write draft.md
        $ python C:/skill/scripts/rebalance_line_rhythm.py draft.md --in-place
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("节奏脚本后重写未重跑节奏修复", rules)

    def test_clean_eval_trace_allows_wrapper_internal_rhythm_after_rewrite(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2
        $ python C:/skill/scripts/rebalance_line_rhythm.py draft.md --in-place
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        {"before": {"body_lines": 68}, "after": {"body_lines": 64}, "target": {"min_lines": 45}, "unresolved": []}
        soften_line_endings: before=0.45 after=0.55 changed=2
        CLEAN_RUN_STOP: FINAL BOUNDARY
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("节奏脚本后重写未重跑节奏修复", rules)

    def test_clean_eval_trace_flags_parent_skill_directory_rediscovery(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        ! permission requested: external_directory (C:/agent/config/opencode/skills/*); auto-rejecting
        ✗ Glob "**/anlin-writing/**" failed in C:/agent/config/opencode/skills
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval首稿前搜索父级skill目录", rules)
            self.assertIn("clean-eval未写入draft.md", rules)

    def test_clean_eval_trace_flags_nonrelative_draft_write_path(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        → Read C:/skill/references/clean-generation-brief.md
        ← Write C:/agent/config/opencode/skills/anlin-writing/iteration-44/eval-07-mothers-day-sin
        cere/draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval写稿路径不是相对draft.md", rules)
            self.assertIn("clean-eval未写入draft.md", rules)

    def test_clean_eval_trace_flags_powershell_nonrelative_set_content_path(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
        → Read C:/skill/references/clean-generation-brief.md
        "@ | Set-Content -Path "C:/agent/config/opencode/skills/anlin-writing/iteration-49/eval-07/draft.md" -Encoding UTF8
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval写稿路径不是相对draft.md", rules)
            self.assertIn("clean-eval未写入draft.md", rules)

    def test_clean_eval_trace_flags_missing_current_directory_before_write(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval写稿前未确认当前目录", rules)

    def test_clean_eval_trace_flags_skill_directory_as_current_directory(self) -> None:
        log = """
        → Skill "anlin-writing"
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/Users/agent/.config/opencode/skills/anlin-writing
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval当前目录是skill目录", rules)

    def test_clean_eval_trace_flags_jsonl_absolute_file_path_under_skill_dir(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Test-Path .anlin-clean-eval-mode"},
                        "metadata": {"output": "True\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Get-Location"},
                        "metadata": {"output": "C:/eval-workspace/iteration-55/eval-09\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "filesystem_write_file",
                    "state": {
                        "input": {
                            "filePath": "C:\\Users\\agent\\.config\\opencode\\skills\\anlin-writing\\iteration-55\\eval-09\\draft.md",
                            "content": "日寄\n\n正文",
                        }
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY\n"},
                    },
                },
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval写稿路径不是相对draft.md", rules)

    def test_clean_eval_trace_allows_jsonl_absolute_file_path_under_current_workspace(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Test-Path .anlin-clean-eval-mode"},
                        "metadata": {"output": "True\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Get-Location"},
                        "metadata": {
                            "output": "C:\\Users\\34025\\Documents\\Codex\\anlin-eval-workspace\\iteration-20260706-57\\eval-09-2024-classmate-wedding\n"
                        },
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "write",
                    "state": {
                        "title": "C:\\Users\\34025\\Documents\\Codex\\anlin-eval-workspace\\iteration-20260706-57\\eval-09-2024-classmate-wedding\\draft.md",
                        "input": {
                            "content": "日寄\n\n正文",
                            "filePath": "C:\\Users\\34025\\Documents\\Codex\\anlin-eval-workspace\\iteration-20260706-57\\eval-09-2024-classmate-wedding\\draft.md",
                        }
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY\n"},
                    },
                },
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval写稿路径不是相对draft.md", rules)
            self.assertNotIn("clean-eval未写入draft.md", rules)

    def test_clean_eval_trace_accepts_relative_apply_patch_draft_mutations(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Test-Path .anlin-clean-eval-mode; Get-Location"},
                        "metadata": {"output": "True\nC:\\case\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "apply_patch",
                    "state": {
                        "title": "Success. Updated the following files:\nA case/draft.md",
                        "input": {
                            "patchText": "*** Begin Patch\n*** Add File: draft.md\n+# 日寄\n+\n+正文\n*** End Patch"
                        },
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_PREFLIGHT: rewrite source\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "apply_patch",
                    "state": {
                        "title": "Success. Updated the following files:\nM case/draft.md",
                        "input": {
                            "patchText": "*** Begin Patch\n*** Update File: draft.md\n@@\n-正文\n+修订正文\n*** End Patch"
                        },
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {
                            "command": "python C:/skill/scripts/rebalance_line_rhythm.py draft.md --in-place; python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"
                        },
                        "metadata": {"output": "CLEAN_RUN_STOP: FINAL BOUNDARY\n"},
                    },
                },
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval未写入draft.md", rules)
            self.assertNotIn("clean-eval写稿路径不是相对draft.md", rules)
            self.assertNotIn("clean-eval改写后未复跑wrapper", rules)

    def test_clean_eval_trace_flags_unchecked_post_wrapper_apply_patch(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Test-Path .anlin-clean-eval-mode; Get-Location"},
                        "metadata": {"output": "True\nC:\\case\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "apply_patch",
                    "state": {
                        "input": {
                            "patchText": "*** Begin Patch\n*** Add File: draft.md\n+# 日寄\n+\n+正文\n*** End Patch"
                        }
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_PREFLIGHT: rewrite source\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "apply_patch",
                    "state": {
                        "input": {
                            "patchText": "*** Begin Patch\n*** Update File: draft.md\n@@\n-正文\n+修订正文\n*** End Patch"
                        }
                    },
                },
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval未写入draft.md", rules)
            self.assertIn("clean-eval改写后未复跑wrapper", rules)

    def test_clean_eval_trace_accepts_opencode_export_json(self) -> None:
        session = {
            "info": {"directory": "C:\\case", "title": "eval"},
            "messages": [
                {
                    "parts": [
                        {
                            "type": "tool",
                            "tool": "bash",
                            "state": {"input": {"command": "Test-Path .anlin-clean-eval-mode; Get-Location"}, "output": "True\nC:\\case\n"},
                        }
                    ]
                },
                {
                    "parts": [
                        {"type": "tool", "tool": "skill", "state": {"input": {"name": "anlin-writing"}, "output": "do not read references/anti-ai-slop.md"}},
                        {"type": "tool", "tool": "read", "state": {"input": {"filePath": "C:\\skill\\references\\clean-generation-brief.md"}, "output": "brief"}},
                        {"type": "tool", "tool": "write", "state": {"title": "C:\\case\\draft.md", "input": {"filePath": "C:\\case\\draft.md", "content": "日寄\n\n正文"}, "output": "Wrote file successfully."}},
                        {
                            "type": "tool",
                            "tool": "bash",
                            "state": {"input": {"command": "python C:\\skill\\scripts\\clean_run_checker.py draft.md --strict --draft-gate"}, "output": "CLEAN_RUN_STOP: FINAL BOUNDARY\n"},
                        },
                        {"type": "tool", "tool": "read", "state": {"input": {"filePath": "C:\\case\\draft.md"}, "output": "日寄\n\n正文"}},
                    ]
                },
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-export.json"
            path.write_text(json.dumps(session, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval未调用clean_run_checker", rules)
            self.assertNotIn("clean-eval未写入draft.md", rules)
            self.assertNotIn("clean-eval首稿前加载修复/评审引用", rules)

    def test_clean_eval_trace_flags_checker_source_inspection(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {"tool": "bash", "state": {"input": {"command": "Test-Path .anlin-clean-eval-mode; Get-Location"}, "metadata": {"output": "True\nC:\\case\n"}}},
            },
            {
                "type": "tool_use",
                "part": {"tool": "write", "state": {"input": {"filePath": "draft.md", "content": "日寄\n\n正文"}}},
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_PREFLIGHT: early_comma_ratio=0.00\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {"tool": "grep", "state": {"input": {"pattern": "early_comma_ratio", "path": "C:/skill/scripts"}}},
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval读取checker源码", rules)

    def test_clean_eval_trace_allows_jsonl_relative_input_with_absolute_display_title(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Test-Path .anlin-clean-eval-mode"},
                        "metadata": {"output": "True\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Get-Location"},
                        "metadata": {
                            "output": "C:\\Users\\34025\\.config\\opencode\\skills\\anlin-writing-workspace\\iteration-20260706-58\\eval-09-2024-classmate-wedding\n"
                        },
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "write",
                    "state": {
                        "title": "C:\\Users\\34025\\.config\\opencode\\skills\\anlin-writing-workspace\\iteration-20260706-58\\eval-09-2024-classmate-wedding\\draft.md",
                        "input": {
                            "filePath": "draft.md",
                            "content": "日寄\n\n正文里偶尔出现 C:/shown/title/draft.md 这种调试残影也不能覆盖 input.filePath。",
                        },
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "read",
                    "state": {
                        "title": "C:\\Users\\34025\\.config\\opencode\\skills\\anlin-writing-workspace\\iteration-20260706-58\\eval-09-2024-classmate-wedding\\draft.md",
                        "input": {"filePath": "draft.md"},
                        "output": "日寄\n\n正文里偶尔出现 C:/shown/title/draft.md 这种调试残影也不能覆盖 input.filePath。",
                    },
                },
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("clean-eval写稿路径不是相对draft.md", rules)

    def test_clean_eval_trace_flags_final_answer_process_prefix_after_stop(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {"tool": "bash", "state": {"input": {"command": "Test-Path .anlin-clean-eval-mode"}, "metadata": {"output": "True\n"}}},
            },
            {
                "type": "tool_use",
                "part": {"tool": "bash", "state": {"input": {"command": "Get-Location"}, "metadata": {"output": "C:\\case\n"}}},
            },
            {
                "type": "tool_use",
                "part": {"tool": "write", "state": {"input": {"filePath": "draft.md", "content": "油\n\n正文"}}},
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_STOP: FINAL BOUNDARY\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {"tool": "read", "state": {"input": {"filePath": "draft.md"}, "output": "油\n\n正文"}},
            },
            {
                "type": "text",
                "part": {"text": "完成。以下是最终文章：\n\n---\n\n油\n\n正文"},
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("stop后最终输出带过程前缀", rules)

    def test_clean_eval_trace_allows_article_only_text_after_stop(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {"tool": "bash", "state": {"input": {"command": "Test-Path .anlin-clean-eval-mode"}, "metadata": {"output": "True\n"}}},
            },
            {
                "type": "tool_use",
                "part": {"tool": "bash", "state": {"input": {"command": "Get-Location"}, "metadata": {"output": "C:\\case\n"}}},
            },
            {
                "type": "tool_use",
                "part": {"tool": "write", "state": {"input": {"filePath": "draft.md", "content": "油\n\n正文"}}},
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_STOP: FINAL BOUNDARY\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {"tool": "read", "state": {"input": {"filePath": "draft.md"}, "output": "油\n\n正文"}},
            },
            {
                "type": "text",
                "part": {"text": "油\n\n正文"},
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertNotIn("stop后最终输出带过程前缀", rules)

    def test_clean_eval_trace_jsonl_ignores_dumped_skill_body_reference_names(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "tool": "skill",
                    "state": {
                        "input": {"name": "anlin-writing"},
                        "output": "The skill says do not load references/anti-ai-slop.md before drafting. It also mentions CLEAN_RUN_PREFLIGHT_STOP and check_anlin_violations.py in instructions.",
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Test-Path .anlin-clean-eval-mode"},
                        "metadata": {"output": "True\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Get-Location"},
                        "metadata": {"output": "C:/eval-workspace/iteration-1/eval-01\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "filesystem_read_file",
                    "state": {
                        "input": {"path": "C:/skill/references/clean-generation-brief.md"},
                        "output": "This brief mentions references/anti-ai-slop.md only as a negative no-load instruction.",
                        "title": "C:/skill/references/clean-generation-brief.md",
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "filesystem_write_file",
                    "state": {"input": {"path": "draft.md", "content": "日寄\n\n正文"}},
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {
                            "output": "CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY. DO NOT WRITE draft.md. The next tool action must be reading draft.md once."
                        },
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "filesystem_read_file",
                    "state": {"input": {"path": "draft.md"}, "output": "日寄\n\n正文"},
                },
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout), [])

    def test_clean_eval_trace_mixed_log_ignores_dumped_skill_body_reference_names(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "tool": "skill",
                    "state": {
                        "input": {"name": "anlin-writing"},
                        "output": "The skill body mentions references/anti-ai-slop.md and check_anlin_violations.py as negative instructions.",
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Test-Path .anlin-clean-eval-mode"},
                        "metadata": {"output": "True\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Get-Location"},
                        "metadata": {"output": "C:/eval-workspace/iteration-1/eval-01\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "filesystem_write_file",
                    "state": {"input": {"path": "draft.md", "content": "日寄\n\n正文"}},
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_NOTE: checker call 1/2\n"},
                    },
                },
            },
        ]
        mixed_lines = [
            "timestamp=2026-07-05T20:05:13.760Z level=INFO message=bootstrapping",
            "some non-json runtime line",
            *[json.dumps(event, ensure_ascii=False) for event in events],
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text("\n".join(mixed_lines), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout), [])

    def test_clean_eval_trace_formatted_log_ignores_reasoned_no_load_list(self) -> None:
        log = """
        Thinking: I should not read `references/anti-ai-slop.md`, `references/title-model.md`, or `references/runtime-brief.md` before the first complete `draft.md`.
        $ Get-ChildItem -Force .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
        → Read C:/skill/references/clean-generation-brief.md
        → Read C:/skill/references/era-state.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_NOTE: checker call 1/2
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            findings = json.loads(result.stdout)
            self.assertFalse(any(item["severity"] == "error" for item in findings), findings)

    def test_clean_eval_trace_formatted_log_flags_actual_forbidden_reference_read(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        → Read C:/skill/references/clean-generation-brief.md
        → Read C:/skill/references/runtime-brief.md
        ← Write draft.md
        $ python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_NOTE: checker call 1/2
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval首稿前加载修复/评审引用", rules)

    def test_clean_eval_trace_jsonl_still_flags_actual_forbidden_reference_read(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "tool": "filesystem_read_file",
                    "state": {
                        "input": {"path": "C:/skill/references/clean-generation-brief.md"},
                        "title": "C:/skill/references/clean-generation-brief.md",
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "filesystem_read_file",
                    "state": {
                        "input": {"path": "C:/skill/references/anti-ai-slop.md"},
                        "title": "C:/skill/references/anti-ai-slop.md",
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "Test-Path .anlin-clean-eval-mode"},
                        "metadata": {"output": "True\n"},
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "filesystem_write_file",
                    "state": {"input": {"path": "draft.md", "content": "日寄\n\n正文"}},
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "bash",
                    "state": {
                        "input": {"command": "python C:/skill/scripts/clean_run_checker.py draft.md --strict --draft-gate"},
                        "metadata": {"output": "CLEAN_RUN_NOTE: checker call 1/2\n"},
                    },
                },
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.jsonl"
            path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval首稿前加载修复/评审引用", rules)

    def test_clean_eval_trace_records_visible_process_chatter_as_warning(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2
        Let me plan the new draft with more substance:
        The preflight says the main issues are length and connector spread.
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            findings = json.loads(result.stdout)
            self.assertTrue(
                any(item["rule"] == "clean-eval可见过程计划" and item["severity"] == "warning" for item in findings)
            )

    def test_clean_eval_trace_flags_rewrite_after_preflight_without_wrapper_recheck(self) -> None:
        session = {
            "info": {"directory": "C:\\case", "title": "eval"},
            "messages": [
                {
                    "parts": [
                        {
                            "type": "tool",
                            "tool": "bash",
                            "state": {
                                "input": {"command": "Test-Path .anlin-clean-eval-mode; Get-Location"},
                                "output": "True\nC:\\case\n",
                            },
                        },
                        {
                            "type": "tool",
                            "tool": "write",
                            "state": {
                                "input": {"filePath": "C:\\case\\draft.md", "content": "日寄\n\n首稿"},
                                "output": "Wrote file successfully.",
                            },
                        },
                        {
                            "type": "tool",
                            "tool": "bash",
                            "state": {
                                "input": {
                                    "command": "python C:\\skill\\scripts\\clean_run_checker.py draft.md --strict --draft-gate"
                                },
                                "output": "CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2\n",
                            },
                        },
                        {
                            "type": "tool",
                            "tool": "read",
                            "state": {
                                "input": {"filePath": "C:\\skill\\references\\clean-generation-brief.md"},
                                "output": "repair guidance",
                            },
                        },
                        {
                            "type": "tool",
                            "tool": "write",
                            "state": {
                                "input": {"content": "日寄\n\n修订稿", "filePath": "C:\\case\\draft.md"},
                                "output": "Wrote file successfully.",
                            },
                        },
                    ]
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-export.json"
            path.write_text(json.dumps(session, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval改写后未复跑wrapper", rules)

    def test_clean_eval_trace_does_not_treat_stop_instruction_as_write(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY. DO NOT WRITE draft.md. DO NOT REPAIR. The next tool action must be reading draft.md once and outputting it unchanged.
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout), [])

    def test_clean_eval_trace_ignores_todo_after_stop_boundary(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2. DO NOT WRITE draft.md.
        - [✓] Write draft.md
        - [ ] Read draft.md and output unchanged
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout), [])

    def test_clean_eval_trace_ignores_stop_token_in_raw_reference_dump(self) -> None:
        log = """
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
        → Read C:/skill/references/clean-generation-brief.md
        If the wrapper prints `CLEAN_RUN_PREFLIGHT_STOP`, the draft still is not ready.
        Do not write `draft.md`, do not repair, and do not switch to `check_anlin_violations.py`.
        ← Write draft.md
        $ python scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT: draft is not ready for checker call 1/2
        ← Write draft.md
        $ python scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_PREFLIGHT_STOP: FINAL BOUNDARY. DO NOT WRITE draft.md. DO NOT REPAIR.
        → Read draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout), [])

    def test_clean_run_checker_does_not_overwrite_bounded_snapshot_after_stop_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            draft = root / "draft.md"
            snapshot_dir = root / ".anlin-clean-run-snapshots"
            bounded = snapshot_dir / "bounded_final.md"
            state_path = root / ".anlin-clean-run-state.json"
            original = "日寄\n\n第一行。\n"
            mutated = "日寄\n\n后来我又把它改成了一整段长句，这已经越过停止边界。\n"
            draft.write_text(original, encoding="utf-8")
            snapshot_dir.mkdir()
            bounded.write_text(original, encoding="utf-8")
            state = {
                "draft": str(draft.resolve()),
                "calls": 2,
                "preflights": 1,
                "stopped": True,
                "stop_reason": "checker-limit",
                "snapshots": {"bounded_final": str(bounded.resolve())},
                "stopped_draft_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
            }
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            draft.write_text(mutated, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLEAN_RUN_CHECKER),
                    str(draft),
                    "--strict",
                    "--draft-gate",
                    "--state",
                    str(state_path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("modified after the clean-eval stop boundary", result.stdout)
            self.assertEqual(bounded.read_text(encoding="utf-8"), original)
            updated_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertTrue(updated_state["post_stop_mutation_detected"])

    def test_clean_eval_trace_rejects_missing_clean_run_checker(self) -> None:
        log = """
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        $ python scripts/check_anlin_violations.py draft.md
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "opencode-output.txt"
            path.write_text(log, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_TRACE), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertIn("clean-eval未调用clean_run_checker", rules)
            self.assertIn("clean-eval写稿前未检查模式标记", rules)

    def test_dev_checkpoint_classifier_keeps_bounded_and_finalized_separate(self) -> None:
        self.assertEqual(classify_development_result("fail", "pass")[0], "source_guidance_gap")
        self.assertEqual(classify_development_result("invalid", "pass")[0], "source_guidance_gap")
        self.assertEqual(classify_development_result("fail", "review")[0], "systemic_gap")
        self.assertEqual(classify_development_result("fail", "fail")[0], "systemic_gap")
        self.assertEqual(classify_development_result("pass", "pass")[0], "ready_for_blind_rounds")
        self.assertEqual(classify_development_result("pass", "fail")[0], "repair_or_validator_gap")
        self.assertEqual(classify_development_result("pass", "review")[0], "repair_or_validator_gap")
        self.assertEqual(classify_development_result("fail", None)[0], "bounded_fail_finalized_missing")

    def test_dev_checkpoint_infers_genre_from_eval_case_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            evals = Path(temp) / "evals.json"
            evals.write_text(
                json.dumps(
                    {
                        "evals": [
                            {"id": 7, "name": "2024-mothers-day-sincere", "style": "sincere"},
                            {"id": 11, "name": "2025-surreal-introspection-projection", "style": "surreal-literary"},
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                infer_genre_from_case_dir(Path(temp) / "iteration-36" / "eval-07-2024-mothers-day-sincere", evals),
                "sincere",
            )
            self.assertEqual(
                infer_genre_from_case_dir(Path(temp) / "iteration" / "2025-surreal-introspection-projection", evals),
                "surreal",
            )
            self.assertIsNone(infer_genre_from_case_dir(Path(temp) / "unmatched-case", evals))

    def test_dev_checkpoint_treats_inconclusive_style_profile_as_review_not_pass(self) -> None:
        gate = summarize_gate(
            hard_findings=[],
            style_report={
                "summary": {
                    "status": "inconclusive",
                    "checkpoint_decision": "profile_inconclusive_fallback",
                    "red_families": ["line_rhythm"],
                    "yellow_families": ["punctuation"],
                    "profile_gate_applicable": False,
                }
            },
            trace_findings=[],
            clean_state={},
            bounded=False,
        )
        self.assertEqual(gate.status, "review")
        self.assertEqual(gate.style_status, "inconclusive")
        self.assertEqual(gate.style_checkpoint_decision, "profile_inconclusive_fallback")
        self.assertTrue(any("inconclusive" in note for note in gate.notes or []))

    def test_dev_checkpoint_summary_creates_controller_audit_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            case_dir.mkdir()
            draft = case_dir / "draft.md"
            draft.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(draft),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                    "--output-json",
                    str(case_dir / "controller-audit" / "summary.json"),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["diagnosis"], "bounded_fail_finalized_missing")
            self.assertEqual(payload["blind_round_readiness"], "not_ready_for_blind_rounds")
            self.assertIn("naturally guide", payload["bounded_question"])
            self.assertIsNone(payload["finalized_question"])
            self.assertIn("limited checker-driven repair", payload["bounded_checkpoint_scope"])
            self.assertIsNone(payload["finalized_checkpoint_scope"])
            self.assertIn("Natural-guidance checkpoint", payload["bounded_checkpoint_answer"])
            self.assertIsNone(payload["finalized_checkpoint_answer"])
            self.assertIn("bounded result alone is incomplete evidence", payload["repair_implication"])
            self.assertTrue((case_dir / "controller-audit" / "bounded-draft.md").is_file())
            self.assertTrue((case_dir / "controller-audit" / "summary.json").is_file())

    def test_dev_checkpoint_summary_records_missing_bounded_draft_as_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            case_dir.mkdir()
            trace = case_dir / "opencode-output.txt"
            trace.write_text(
                "\n".join(
                    [
                        "$ Test-Path .anlin-clean-eval-mode",
                        "True",
                        "→ Read C:/skill/references/clean-generation-brief.md",
                        "The brief says python scripts/clean_run_checker.py draft.md later.",
                        "我坐在桌前，手机屏幕亮着。",
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                    "--output-json",
                    str(case_dir / "controller-audit" / "summary.json"),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["bounded"]["gate"]["status"], "invalid")
            self.assertEqual(payload["bounded"]["gate"]["clean_stop_reason"], "missing_draft")
            self.assertIn("never persisted a draft.md artifact", payload["bounded_checkpoint_answer"])
            self.assertTrue((case_dir / "controller-audit" / "bounded-draft-missing.md").is_file())
            trace_rules = [item["rule"] for item in payload["bounded"]["trace_findings"]]
            self.assertIn("clean-eval未写入draft.md", trace_rules)

    def test_dev_checkpoint_summary_reports_clean_run_stage_audits(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            snapshot_dir = case_dir / ".anlin-clean-run-snapshots"
            snapshot_dir.mkdir(parents=True)
            first = snapshot_dir / "first_submission.md"
            second = snapshot_dir / "checker_call_2_submission.md"
            final = snapshot_dir / "bounded_final.md"
            first.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            second.write_text("\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]), encoding="utf-8")
            final.write_text(second.read_text(encoding="utf-8"), encoding="utf-8")
            draft = case_dir / "draft.md"
            draft.write_text(final.read_text(encoding="utf-8"), encoding="utf-8")
            (case_dir / ".anlin-clean-run-state.json").write_text(
                json.dumps(
                    {
                        "draft": str(draft.resolve()),
                        "calls": 2,
                        "preflights": 0,
                        "stopped": True,
                        "stop_reason": "checker-limit",
                        "snapshots": {
                            "first_submission": str(first.resolve()),
                            "checker_call_2_submission": str(second.resolve()),
                            "bounded_final": str(final.resolve()),
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(draft),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                    "--output-json",
                    str(case_dir / "controller-audit" / "summary.json"),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertIn("first-submission snapshot", payload["bounded_checkpoint_answer"])
            self.assertIn("two-call checker boundary", payload["bounded_checkpoint_answer"])
            names = [item["name"] for item in payload["bounded"]["stage_audits"]]
            self.assertIn("first_submission", names)
            self.assertIn("checker_call_2_submission", names)
            self.assertIn("bounded_final", names)
            self.assertTrue((case_dir / "controller-audit" / "stage-first_submission-draft.md").is_file())

    def test_dev_checkpoint_summary_distinguishes_preflight_stop_from_two_call_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            case_dir.mkdir(parents=True)
            draft = case_dir / "draft.md"
            draft.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 60)]), encoding="utf-8")
            (case_dir / ".anlin-clean-run-state.json").write_text(
                json.dumps(
                    {
                        "draft": str(draft.resolve()),
                        "calls": 0,
                        "preflights": 3,
                        "stopped": True,
                        "stop_reason": "preflight",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(draft),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertIn("stopped at preflight before formal checker call 1/2", payload["bounded_checkpoint_answer"])
            self.assertIn("not evidence that the two actual checker corrections were tested", payload["bounded_checkpoint_answer"])

    def test_dev_checkpoint_summary_fails_when_finalized_still_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            body = "\n".join(["# 春招日寄", "", *(["杯子脏了。"] * 90)])
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text(body, encoding="utf-8")
            finalized.write_text(body + "\n其实我又看了看杯子，还是脏。", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["diagnosis"], "systemic_gap")
            self.assertEqual(payload["blind_round_readiness"], "not_ready_for_blind_rounds")
            self.assertIn("strict hard-gate", payload["finalized_question"])
            self.assertIn("cannot retroactively improve bounded status", payload["finalized_checkpoint_scope"])
            self.assertIn("Only `pass` means", payload["finalized_checkpoint_answer"])
            self.assertIn("final article is not clean", payload["repair_implication"])
            self.assertIn(payload["finalized"]["gate"]["status"], {"fail", "review"})

    def test_dev_checkpoint_summary_marks_unchanged_finalized_artifact_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            body = "\n".join(["# 2024日寄", "", *(["杯子脏了。"] * 90)])
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text(body, encoding="utf-8")
            finalized.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            self.assertTrue(
                any(
                    "finalized draft unchanged from bounded input" in note
                    for note in payload["finalized"]["gate"]["notes"]
                )
            )

    def test_dev_checkpoint_summary_marks_finalized_checker_source_trace_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.txt"
            nul_source_line = "\x00".join("→ Read C:/Users/34025/.config/opencode/skills/anlin-writing/scripts/check_style_profile.py")
            trace.write_text(
                "\n".join(
                    [
                        nul_source_line,
                        "$ rg YELLOW_REVIEW_FAMILY_THRESHOLD scripts\\check_style_profile.py",
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            self.assertEqual(payload["finalized"]["gate"]["trace_errors"], 2)
            self.assertTrue(
                any(
                    "finalized repair trace contamination detected" in note
                    for note in payload["finalized"]["gate"]["notes"]
                )
            )
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertIn("finalized修复读取checker源码", rules)
            self.assertIn("finalized修复反查checker阈值", rules)

    def test_dev_checkpoint_summary_marks_finalized_threshold_only_trace_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.txt"
            trace.write_text("I searched for SOFT_REVISE_FAMILY_THRESHOLD before editing.\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            self.assertEqual(payload["finalized"]["gate"]["trace_errors"], 1)
            self.assertEqual(payload["finalized"]["trace_findings"][0]["rule"], "finalized修复反查checker阈值")

    def test_dev_checkpoint_summary_marks_finalized_checker_glob_trace_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.txt"
            trace.write_text(
                '\x1b[0m✱ \x1b[0mGlob "**/*check_anlin_violations*" in <skill-dir> · 1 match\n'
                '✱ Glob "**/*check_style_profile*" in <skill-dir> · 1 match\n',
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            self.assertEqual(payload["finalized"]["gate"]["trace_errors"], 2)
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertEqual(rules, ["finalized修复重新搜索checker路径", "finalized修复重新搜索checker路径"])

    def test_dev_checkpoint_summary_marks_finalized_metric_loop_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.txt"
            trace.write_text(
                "\n".join(
                    [
                        "$ python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "[error] global strict: 标准日寄句号网格",
                        "← Write draft.md",
                        "$ python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "[error] global strict: 逗号密度过高",
                        "[error] global strict: 社交拒绝纹理替代后果不足",
                        "← Edit draft.md",
                        "$ python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "[error] global strict: 标准日寄句号网格",
                        "[error] global strict: 社交拒绝纹理替代后果不足",
                        "← Write draft.md",
                        "$ python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "[error] global strict: 逗号密度过高",
                        "[error] global strict: 社交拒绝纹理替代后果不足",
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            self.assertEqual(payload["finalized"]["gate"]["trace_errors"], 2)
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertIn("finalized修复运行本地检查器", rules)
            self.assertIn("finalized修复指标循环", rules)
            loop_finding = next(item for item in payload["finalized"]["trace_findings"] if item["rule"] == "finalized修复指标循环")
            self.assertIn("controller-prepared repair-brief.txt", loop_finding["suggestion"])
            self.assertIn("unresolved repair-path", loop_finding["suggestion"])

    def test_dev_checkpoint_summary_reads_utf16_jsonl_finalized_trace_and_counts_single_patch_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output-utf16.jsonl"
            events = [
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "read",
                        "state": {"status": "completed", "input": {"filePath": str(finalized)}},
                    },
                },
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "read",
                        "state": {"status": "completed", "input": {"filePath": str(finalized_dir / "repair-brief.txt")}},
                    },
                },
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "apply_patch",
                        "state": {
                            "status": "completed",
                            "input": {
                                "patchText": (
                                    "*** Begin Patch\n"
                                    f"*** Delete File: {finalized}\n"
                                    f"*** Add File: {finalized}\n"
                                    "+# 日寄\n"
                                    "+\n"
                                    "+我把杯子放回去。\n"
                                    "*** End Patch\n"
                                )
                            },
                            "output": "Success. Updated the following files:\nD finalized/draft.md\nA finalized/draft.md",
                        },
                    },
                },
                {"type": "text", "part": {"type": "text", "text": "artifact_written"}},
            ]
            trace.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-16")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            payload = json.loads(result.stdout)
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertNotIn("finalized修复指标循环", rules)
            self.assertNotIn("finalized修复运行本地检查器", rules)
            self.assertNotIn("finalized修复未写回artifact", rules)

    def test_dev_checkpoint_summary_marks_finalized_analysis_without_write_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.jsonl"
            events = [
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "read",
                        "state": {"status": "completed", "input": {"filePath": str(finalized)}},
                    },
                },
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "read",
                        "state": {"status": "completed", "input": {"filePath": str(finalized_dir / "repair-brief.txt")}},
                    },
                },
                {
                    "type": "text",
                    "part": {
                        "type": "text",
                        "text": "Let me analyze the repair brief carefully. 我先分析一下修复方案，然后再决定怎么写。",
                    },
                },
            ]
            trace.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            self.assertEqual(payload["finalized"]["gate"]["trace_errors"], 1)
            finding = payload["finalized"]["trace_findings"][0]
            self.assertEqual(finding["rule"], "finalized修复未写回artifact")
            self.assertIn("draft_mutations=0", finding["excerpt"])
            self.assertIn("requires one immediate complete draft.md write", finding["suggestion"])

    def test_dev_checkpoint_summary_counts_jsonl_write_tool_as_finalized_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.jsonl"
            events = [
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "read",
                        "state": {"status": "completed", "input": {"filePath": str(finalized)}},
                    },
                },
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "read",
                        "state": {"status": "completed", "input": {"filePath": str(finalized_dir / "repair-brief.txt")}},
                    },
                },
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "write",
                        "state": {
                            "status": "completed",
                            "input": {"content": "# 日寄\n\n我把杯子放回去。\n", "filePath": str(finalized)},
                            "output": "Wrote file successfully.",
                        },
                    },
                },
                {"type": "text", "part": {"type": "text", "text": "artifact_written"}},
            ]
            trace.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            payload = json.loads(result.stdout)
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertNotIn("finalized修复未写回artifact", rules)
            self.assertNotIn("finalized修复指标循环", rules)

    def test_dev_checkpoint_summary_marks_jsonl_placeholder_then_second_write_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            original = "\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)])
            bounded.write_text(original, encoding="utf-8")
            finalized.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            trace = finalized_dir / "opencode-output.jsonl"
            events = [
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "read",
                        "state": {"status": "completed", "input": {"filePath": str(finalized)}},
                    },
                },
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "read",
                        "state": {"status": "completed", "input": {"filePath": str(finalized_dir / "repair-brief.txt")}},
                    },
                },
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "write",
                        "state": {
                            "status": "completed",
                            "input": {"content": original, "filePath": str(finalized)},
                            "output": "Wrote file successfully.",
                        },
                    },
                },
                {
                    "type": "text",
                    "part": {"type": "text", "text": "我再想一下，刚才只是先写回旧稿，下面写修订版。"},
                },
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "write",
                        "state": {
                            "status": "completed",
                            "input": {"content": "# 日寄\n\n我把杯子放回去。\n", "filePath": str(finalized)},
                            "output": "Wrote file successfully.",
                        },
                    },
                },
            ]
            trace.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertIn("finalized修复指标循环", rules)
            finding = next(item for item in payload["finalized"]["trace_findings"] if item["rule"] == "finalized修复指标循环")
            self.assertIn("draft_mutations=2", finding["excerpt"])

    def test_dev_checkpoint_summary_marks_post_write_gate_loop_invalid_without_second_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.txt"
            trace.write_text(
                "\n".join(
                    [
                        "$ python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "$ python <skill-dir>/scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre standard",
                        "← Write draft.md",
                        "$ python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "[error] global strict: 标准日寄句号网格",
                        "$ python <skill-dir>/scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre standard",
                        "formal_gate: not_pass",
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            self.assertEqual(payload["finalized"]["gate"]["trace_errors"], 2)
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertIn("finalized修复运行本地检查器", rules)
            self.assertIn("finalized修复指标循环", rules)
            loop_finding = next(item for item in payload["finalized"]["trace_findings"] if item["rule"] == "finalized修复指标循环")
            self.assertIn("hard_gate_runs=2", loop_finding["excerpt"])
            self.assertIn("repair_brief_runs=2", loop_finding["excerpt"])

    def test_dev_checkpoint_summary_marks_post_write_metric_probe_invalid(self) -> None:
        commands = [
            "$ python -c \"from pathlib import Path; print(len(Path('draft.md').read_text(encoding='utf-8')))\"",
            "$ Get-Content draft.md | Measure-Object -Line -Character",
            "$ wc -l draft.md",
        ]
        for command in commands:
            with self.subTest(command=command):
                with tempfile.TemporaryDirectory() as temp:
                    case_dir = Path(temp) / "case"
                    finalized_dir = case_dir / "finalized"
                    finalized_dir.mkdir(parents=True)
                    bounded = case_dir / "draft.md"
                    finalized = finalized_dir / "draft.md"
                    bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
                    finalized.write_text(
                        "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                        encoding="utf-8",
                    )
                    trace = finalized_dir / "opencode-output.txt"
                    trace.write_text(
                        "\n".join(
                            [
                                "$ python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                                "$ python <skill-dir>/scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre standard",
                                "← Write draft.md",
                                command,
                            ]
                        ),
                        encoding="utf-8",
                    )
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(SUMMARY_CHECKPOINTS),
                            str(case_dir),
                            "--bounded-draft",
                            str(bounded),
                            "--finalized-draft",
                            str(finalized),
                            "--finalized-trace-log",
                            str(trace),
                            "--profile",
                            str(STYLE_PROFILE),
                            "--json",
                        ],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        check=False,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
                    rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
                    self.assertIn("finalized修复运行本地检查器", rules)
                    self.assertIn("finalized修复写后自测计数", rules)
                    finding = next(
                        item for item in payload["finalized"]["trace_findings"] if item["rule"] == "finalized修复写后自测计数"
                    )
                    self.assertIn("controller performs validation after the artifact is frozen", finding["suggestion"])

    def test_dev_checkpoint_summary_marks_any_finalized_checker_command_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.txt"
            trace.write_text(
                "\n".join(
                    [
                        "$ python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "[error] global strict: 标准日寄句号网格",
                        "$ python <skill-dir>/scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre standard",
                        "repair_directive: write one complete revised draft.md now, then stop",
                        "controller_note: full profile reports belong outside the repair-agent trace",
                        "findings:",
                        "  - warning:red | line_rhythm | line_mean_chars | observed=11.0",
                        "← Write draft.md",
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertIn("finalized修复运行本地检查器", rules)
            self.assertNotIn("finalized修复指标循环", rules)

    def test_dev_checkpoint_summary_marks_finalized_todo_planning_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.txt"
            trace.write_text(
                "\n".join(
                    [
                        "timestamp message=evaluated permission=todowrite pattern=*",
                        "# Todos",
                        "[ ] 运行 formal hard gate",
                        "$ python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "$ python <skill-dir>/scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre standard",
                        "← Write draft.md",
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertIn("finalized修复运行本地检查器", rules)
            self.assertIn("finalized修复TODO计划", rules)

    def test_dev_checkpoint_summary_marks_finalized_second_write_and_threshold_reasoning_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 热水", "", *(["热水器响了一下，我没管，手机亮了又灭。"] * 12)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.txt"
            trace.write_text(
                "\n".join(
                    [
                        "$ python scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "$ python scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre standard",
                        "single_write_budget: after this brief, exactly one Write/Edit draft.md is allowed",
                        "← Write draft.md",
                        "$ python scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "[error] global strict: 逗号密度过高",
                        "$ python scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre standard",
                        "现在要逐行计算逗号和句号的频率，因为工具给出了具体的阈值限制，逗号每千字不超过35个。",
                        "← Edit draft.md",
                        "$ python scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre standard",
                        "[error] global strict: 行末逗号比例",
                        "$ python scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre standard",
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["status"], "invalid")
            rules = [item["rule"] for item in payload["finalized"]["trace_findings"]]
            self.assertIn("finalized修复运行本地检查器", rules)
            self.assertIn("finalized修复指标推理", rules)
            self.assertIn("finalized修复指标循环", rules)
            self.assertGreaterEqual(payload["finalized"]["gate"]["trace_errors"], 3)

    def test_dev_checkpoint_summary_marks_public_checker_metric_output_in_repair_trace_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case_dir = Path(temp) / "case"
            finalized_dir = case_dir / "finalized"
            finalized_dir.mkdir(parents=True)
            bounded = case_dir / "draft.md"
            finalized = finalized_dir / "draft.md"
            bounded.write_text("\n".join(["# 日寄", "", *(["杯子脏了。"] * 90)]), encoding="utf-8")
            finalized.write_text(
                "\n".join(["# 日寄", "", *(["其实我觉得杯子脏了，于是洗手差点吐出来，丢人。"] * 50)]),
                encoding="utf-8",
            )
            trace = finalized_dir / "opencode-output.txt"
            trace.write_text(
                "\n".join(
                    [
                        "$ python scripts/check_style_profile.py draft.md --draft-gate --strict --genre standard",
                        "warning:red | punctuation | punct_comma_per_1k | observed=107.0 | expected=q10-q90=67.0..94.0",
                        '{"before": {"short_breath_lines": 27}, "after": {"short_breath_lines": 16}}',
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUMMARY_CHECKPOINTS),
                    str(case_dir),
                    "--bounded-draft",
                    str(bounded),
                    "--finalized-draft",
                    str(finalized),
                    "--finalized-trace-log",
                    str(trace),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["finalized"]["gate"]["trace_errors"], 1)
            self.assertEqual(payload["finalized"]["trace_findings"][0]["rule"], "finalized修复运行本地检查器")
            self.assertIn("controller prepares repair-brief.txt", payload["finalized"]["trace_findings"][0]["suggestion"])

    def test_clean_run_checker_blocks_uniform_medium_grid_without_mutating_submission(self) -> None:
        fragments = [
            "其实厕所灯坏了我站着很丢人",
            "觉得杯子好像也脏我又拿回去",
            "突然发现手机没电屏幕黑着",
            "于是我又去厕所洗了手",
            "因为尿急没躲过电梯里那眼神",
        ]
        body = "\n".join(["# 日寄", "", *(fragments * 16)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            state = draft.parent / ".anlin-clean-run-state.json"
            state.write_text(
                json.dumps({"draft": str(draft.resolve()), "calls": 1}, ensure_ascii=False),
                encoding="utf-8",
            )
            submitted_bytes = draft.read_bytes()
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(second.returncode, 3, second.stdout + second.stderr)
            self.assertIn("CLEAN_RUN_POSTCHECK_PREFLIGHT", second.stdout)
            self.assertEqual(draft.read_bytes(), submitted_bytes)
            saved = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(saved["calls"], 1)

    def test_clean_run_checker_blocks_medium_grid_without_mutating_submission(self) -> None:
        fragments = [
            "其实厕所灯坏了我站着很丢人还假装没事",
            "觉得杯子好像也脏我又拿回去冲了一下",
            "突然发现手机没电屏幕黑着像块砖头",
            "于是我去厕所洗手差点吐出来还得忍着",
            "因为尿急没躲过电梯里那眼神",
        ]
        body = "\n".join(["# 日寄", "", *(fragments * 12)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            state = draft.parent / ".anlin-clean-run-state.json"
            state.write_text(
                json.dumps({"draft": str(draft.resolve()), "calls": 1}, ensure_ascii=False),
                encoding="utf-8",
            )
            submitted_bytes = draft.read_bytes()
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(second.returncode, 3, second.stdout + second.stderr)
            self.assertIn("CLEAN_RUN_POSTCHECK_PREFLIGHT", second.stdout)
            self.assertEqual(draft.read_bytes(), submitted_bytes)
            saved = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(saved["calls"], 1)

    def test_clean_run_checker_blocks_prose_compression_without_mutating_submission(self) -> None:
        long_line = (
            "其实我摸了摸手机，觉得六条未读有点多，突然发现三条是运营商的催缴短信，"
            "于是去厕所洗了把脸，因为差点吐出来，丢人得很，好像还是没躲过去。"
        )
        body = "\n".join(["# 日寄", "", *([long_line] * 18)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            state = draft.parent / ".anlin-clean-run-state.json"
            state.write_text(
                json.dumps({"draft": str(draft.resolve()), "calls": 1}, ensure_ascii=False),
                encoding="utf-8",
            )
            submitted_bytes = draft.read_bytes()
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(second.returncode, 3, second.stdout + second.stderr)
            self.assertIn("CLEAN_RUN_POSTCHECK_PREFLIGHT", second.stdout)
            self.assertEqual(draft.read_bytes(), submitted_bytes)
            saved = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(saved["calls"], 1)

    def test_clean_run_checker_blocks_short_grid_without_mutating_submission(self) -> None:
        fragments = [
            "其实我觉得杯子脏了",
            "突然发现厕所灯坏了",
            "于是差点吐出来",
            "因为这事有点丢人",
            "好像还是没躲过去",
        ]
        body = "\n".join(["# 日寄", "", *(fragments * 24)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            state = draft.parent / ".anlin-clean-run-state.json"
            state.write_text(
                json.dumps({"draft": str(draft.resolve()), "calls": 1}, ensure_ascii=False),
                encoding="utf-8",
            )
            submitted_bytes = draft.read_bytes()
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(second.returncode, 3, second.stdout + second.stderr)
            self.assertIn("CLEAN_RUN_POSTCHECK_PREFLIGHT", second.stdout)
            self.assertEqual(draft.read_bytes(), submitted_bytes)
            saved = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(saved["calls"], 1)

    def test_checker_accepts_ugly_low_engine_terms_as_paragraph_engine(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "我觉得今天这个事有点丢人，",
                "香菜味冲上来的时候差点吐出来，",
                "后来发现自己又欠了全世界香菜制造商一笔债，",
                *(["其实水龙头咳了一下，裤子湿了一片，因为我没躲过那一下，"] * 28),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings))

    def test_checker_accepts_low_rough_terms_from_food_and_status_damage(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "衣服味道廉价，",
                "吃到香菜差点吐出来，",
                "想了想自己也快养不起自己，",
                *(["其实我觉得杯子有点脏，因为水龙头咳了一下喷到裤子上，"] * 30),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    def test_checker_accepts_v15_like_dirty_body_material_as_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "指甲里还藏着点黑泥，",
                "蹭在白菜叶上我想了想，还是一块咽了，",
                "火腿肠胀袋，",
                *(["其实我觉得杯子有点脏，因为水龙头咳了一下喷到裤子上，"] * 30),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    def test_checker_accepts_v15_like_body_material_as_paragraph_engine(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "胃从中午就开始疼，",
                "肚子咕噜咕噜响，",
                "指甲断了一小块，",
                "指头上的油蹭到了墙上，",
                *(["不过我还是点开手机看了一眼，因为楼下水龙头一直咳，"] * 30),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings))

    def test_checker_accepts_v35_like_low_body_and_social_self_own_as_engine(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "我打了两个字又删了，觉得自己确实不是东西。",
                "趴在马桶边干呕了几声，什么也没吐出来。",
                "老太太拽了小孩一下说不能吃脏东西，我嚼了几口吞了。",
                "站到一半腿又麻了，差点跪在地上。",
                *(["其实我觉得杯子有点脏，因为水龙头咳了一下喷到裤子上，"] * 30),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings))

    def test_checker_draft_gate_rejects_over_dense_long_line_prose(self) -> None:
        long_line = "其实我觉得杯子有点脏，因为水龙头咳了一下喷到裤子上，后来发现自己差点吐出来，还是没躲过那一下。"
        body = "\n".join(["# 日寄", "", *([long_line] * 42)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 标准日寄长行过密" for item in findings))

    def test_checker_strict_promotes_blind_eval_risks(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "群里有人说入职体检要空腹。",
                "offer 和招聘岗位都在刷屏。",
                "简历、hr、boss直聘、公积金、租房补贴也都在。",
                "屏幕暗了。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            errors = [item for item in findings if item["severity"] == "error"]
            self.assertTrue(any(item["rule"].startswith("strict:") for item in errors))

    def test_checker_draft_gate_promotes_generated_draft_only_risks(self) -> None:
        body = "\n".join(
            [
                "# 春招日寄",
                "",
                "群里有人说入职体检要空腹。",
                "offer 和招聘岗位都在刷屏。",
                "简历、hr、boss直聘、公积金、租房补贴也都在。",
                "我看着屏幕，觉得自己像一张被系统退回来的表。",
                "屏幕亮着。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            strict_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            draft_gate_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            strict_findings = json.loads(strict_result.stdout)
            draft_gate_findings = json.loads(draft_gate_result.stdout)
            strict_rules = [item["rule"] for item in strict_findings if item["severity"] == "error"]
            draft_gate_rules = [item["rule"] for item in draft_gate_findings if item["severity"] == "error"]
            self.assertFalse(any("标准日寄完整文章篇幅偏短" in rule for rule in strict_rules))
            self.assertTrue(any("标准日寄完整文章篇幅偏短" in rule for rule in draft_gate_rules))
            self.assertTrue(any("题面诊断型标题" in rule for rule in draft_gate_rules))

    def test_checker_draft_gate_rejects_year_label_title(self) -> None:
        body = "\n".join(
            [
                "# 2024日寄",
                "",
                *(["其实杯子有点脏，于是我拿去洗，水龙头喷到裤子上，收银台灯一亮我发现手上还有灰。"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            errors = [item for item in findings if item["severity"] == "error"]
            self.assertTrue(any(item["rule"] == "strict: 题面诊断型标题" for item in errors))
            self.assertTrue(any("four_digit_year" in item["suggestion"] for item in findings))

    def test_checker_draft_gate_rejects_near_minimum_article_length(self) -> None:
        filler_line = "我把杯子拿去洗水龙头先咳了一下喷到裤子上"
        body = "\n".join(["# 日寄", "", *([filler_line] * 33)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            strict_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            draft_gate_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(draft_gate_result.returncode, 0)
            strict_findings = json.loads(strict_result.stdout)
            draft_gate_findings = json.loads(draft_gate_result.stdout)
            self.assertFalse(
                any(
                    item["rule"] == "strict: 标准日寄完整文章篇幅缓冲不足"
                    for item in strict_findings
                )
            )
            self.assertTrue(
                any(
                    item["rule"] == "strict: 标准日寄完整文章篇幅缓冲不足"
                    for item in draft_gate_findings
                )
            )

    def test_checker_draft_gate_rejects_overfull_standard_article(self) -> None:
        filler_line = "我把杯子拿到楼下水龙头旁边手机屏幕亮了我又放回去"
        body = "\n".join(["# 日寄", "", *([filler_line] * 62)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            draft_gate_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(draft_gate_result.returncode, 0)
            findings = json.loads(draft_gate_result.stdout)
            self.assertTrue(
                any(item["rule"] == "strict: 标准日寄完整文章过满" for item in findings)
            )

    def test_checker_draft_gate_rejects_texture_overfill(self) -> None:
        body_lines = (
            ["脚踝一疼我就想去厕所其实手机还在裤兜里震着丢人"] * 20
            + ["屏幕上群消息一直亮我觉得杯子也脏于是没回"] * 20
            + ["楼下水龙头旁边电动车钥匙掉进塑料袋里好像很响"] * 20
        )
        body = "\n".join(["# 日寄", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(
                any(item["rule"] == "strict: 具体纹理堆叠过密" for item in findings)
            )

    def test_checker_draft_gate_rejects_private_illness_case_report_loop(self) -> None:
        body_lines = (
            ["痛风又犯了，大脚趾肿得发亮，脚踝疼得像从里面顶出来。"] * 8
            + ["我搜了一下痛风，屏幕上写着富贵病，帖子下面还有尿酸两个字。"] * 8
            + ["冰箱里剩半瓶可乐和两盒腐乳，厨房的碗边有油，空调外机一直响。"] * 10
            + ["房间里的味道很闷，药膏味、腐乳味、手上的油味混在一起。"] * 10
            + ["脚趾又胀了一下，我把手机扣在枕头边，继续看那个页面。"] * 8
        )
        body = "\n".join(["# 空调外机", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 疾病病例报告闭环" for item in findings))

    def test_checker_draft_gate_allows_illness_when_exposed_social_consequence_exists(self) -> None:
        body_lines = (
            ["痛风又犯了，大脚趾肿得发亮，脚踝疼得像从里面顶出来。"] * 5
            + ["我搜了一下痛风，屏幕上写着富贵病，手指停了一下。"] * 4
            + ["冰箱里剩半瓶可乐和两盒腐乳，厨房的碗边有油。"] * 4
            + ["楼下药店老板看我拖着脚进门，问我是不是又疼了，我说还行。"] * 5
            + ["店员递袋子的时候看了一眼我的拖鞋，我把脚往后缩了一下。"] * 5
            + ["回到门口钥匙掉在地上，弯不下去，后面的人等了一会儿。"] * 5
            + ["房间里的味道很闷，药膏味、腐乳味、手上的油味混在一起。"] * 8
        )
        body = "\n".join(["# 空调外机", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("疾病病例报告闭环" in item["rule"] for item in findings))

    def test_checker_draft_gate_rejects_illness_body_proof_overdensity_after_exposure(self) -> None:
        body_lines = (
            ["脚趾又烧起来了，大脚趾关节发酸，整只脚不敢挨地。"] * 7
            + ["我拿起手机搜痛风，屏幕上写着富贵病和尿酸。"] * 5
            + ["冰箱里剩半瓶可乐，厨房有腐乳，空调外机一直响。"] * 6
            + ["外卖员站在门口等我扫码，提手断了，粥淌到手上。"] * 3
            + ["我再坐回沙发，脚趾又胀了一下，手机还亮着那个页面。"] * 12
            + ["房间里的味道很闷，药膏味和腐乳味混在一起。"] * 12
        )
        body = "\n".join(["# 外机", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 疾病身体证明过密" for item in findings), findings)

    def test_checker_draft_gate_allows_illness_when_body_packet_is_thinned(self) -> None:
        body_lines = (
            [
                "脚趾疼了一下，我把拖鞋踢到一边。",
                "手机上那个页面还没关，我只看见富贵病三个字。",
                "门铃响的时候我没站起来，外卖员又敲了一下。",
                "我挪到门口扫码，手机卡了一下，他站着没走。",
                "提手断了，粥淌到我手上。",
                "我回屋踩到一点，拖鞋打滑，扶着墙站住。",
                "表弟问还来不来，我打了个脚不行，又删了。",
                "最后发了个嗯。",
            ]
            + ["楼道灯亮了一下，杯子还在茶几边上，粥慢慢凉了。"] * 24
        )
        body = "\n".join(["# 外机", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("疾病身体证明过密" in item["rule"] for item in findings), findings)

    def test_checker_warns_when_body_object_texture_replaces_social_movement(self) -> None:
        body_lines = (
            ["手上有灰，裤子上也有灰，水龙头边的杯子放在楼道里，门口的塑料袋也湿了。"] * 14
            + ["钥匙在门口掉了一下，塑料袋勒着手，冰箱里只有半个西瓜，楼道灯一直亮着。"] * 12
            + ["其实我觉得这事也说不上什么，后来把手机扣在桌上，又去洗手。"] * 14
        )
        body = "\n".join(["# 日寄", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "纹理替代社交不足" for item in findings))
            self.assertTrue(all(item["severity"] != "error" for item in findings))

    def test_checker_does_not_warn_texture_replaces_social_when_social_movement_exists(self) -> None:
        body_lines = (
            ["手上有灰，老板看了我一眼，我把硬币又往回收了一点。"] * 6
            + ["摊主问我要不要切，我说不用，声音小得像从塑料袋里出来。"] * 6
            + ["邻居在楼道里说垃圾别堆门口，我嗯了一声，钥匙又掉到地上。"] * 6
            + ["水龙头边的杯子放着，手机扣在桌上，冰箱里只有半个西瓜。"] * 18
        )
        body = "\n".join(["# 日寄", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            self.assertFalse(any(item["rule"] == "纹理替代社交不足" for item in findings))

    def test_checker_draft_gate_rejects_formulaic_comment_chain(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "群里有人回四管。有人说他们公司体检费报销，有人说不报销。然后又有人开始算公积金基数。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(
                any(item["rule"] == "strict: 评论链公式化转述" for item in findings)
            )

    def test_checker_draft_gate_rejects_ai_binary_reframe(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "酸梅汤漏了一路。",
                "不是包装袋漏，是电动车前面那个篮子。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            strict_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            draft_gate_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(strict_result.returncode, 0, strict_result.stderr)
            self.assertNotEqual(draft_gate_result.returncode, 0)
            findings = json.loads(draft_gate_result.stdout)
            self.assertTrue(any(item["rule"] == "strict: AI二元解释句式" for item in findings))

    def test_checker_draft_gate_rejects_now_i_realized_caption(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "水还在滴。",
                "现在我意识到水龙头已经完全坏了，胶带也救不了，得让房东来换新的。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"].startswith("strict: AI解释腔") for item in findings))

    def test_checker_draft_gate_rejects_pronoun_binary_reframe(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "旁边小孩看了我一眼。",
                "我不是叔叔，我只是失败得比较显老。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: AI二元解释句式" for item in findings))

    def test_checker_draft_gate_rejects_this_is_binary_reframe(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "我说这不是独居，这是ins上的租房广告。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: AI二元解释句式" for item in findings))

    def test_checker_draft_gate_rejects_prompt_performing_identity_probe_not_binary(self) -> None:
        cluster = [
            "其实楼下水管又响了一下，",
            "我觉得像有人在墙里拖塑料袋。",
            "突然发现指甲缝里黑泥还在，",
            "于是换手去拿杯子，因为那只手看起来更丢人。",
            "不过收银员看了我一眼。",
            "很丢人。",
            "胃响了一声。",
            "我假装没听见。",
        ]
        body = "\n".join(
            [
                "# 水管",
                "",
                "他突然问我，你是不是以前那个大学的，就是后面有条小吃街那个。",
                *(cluster * 7),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertIn("strict: 提示词报幕式对话", rules)
            self.assertNotIn("strict: AI二元解释句式", rules)

    def test_checker_draft_gate_allows_plain_shi_bu_shi_question(self) -> None:
        cluster = [
            "其实楼下水管又响了一下，",
            "我觉得像有人在墙里拖塑料袋。",
            "突然发现指甲缝里黑泥还在，",
            "于是换手去拿杯子，因为那只手看起来更丢人。",
            "不过收银员看了我一眼。",
            "很丢人。",
            "胃响了一声。",
            "我假装没听见。",
        ]
        body = "\n".join(
            [
                "# 水管",
                "",
                "室友在旁边问我是不是还没吃饭，我说吃了，其实只吃了半个冷包子。",
                *(cluster * 7),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertNotIn("strict: AI二元解释句式", rules)
            self.assertNotIn("strict: 提示词报幕式对话", rules)

    def test_checker_draft_gate_rejects_english_process_preamble(self) -> None:
        body = "\n".join(
            [
                "Now let me write the draft article:",
                "# 日寄",
                "",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"].startswith("过程说明泄漏") for item in findings))

    def test_checker_draft_gate_rejects_meta_ai_reference_contamination(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "驿站老板刷短视频，说怎么识别AI写的文章。",
                "我又打开AI对话窗口。",
                "AI写周报三个字挂在屏幕上。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            strict_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            draft_gate_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            strict_findings = json.loads(strict_result.stdout)
            draft_gate_findings = json.loads(draft_gate_result.stdout)
            self.assertFalse(
                any(item["rule"] == "strict: 反AI参考污染" for item in strict_findings)
            )
            self.assertTrue(
                any(item["rule"] == "strict: 反AI参考污染" for item in draft_gate_findings)
            )

    def test_checker_draft_gate_rejects_unsupported_current_office_persona(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "到了公司，同事小李喊我张哥，领导说部门KPI和营收都要看。",
                "我坐回工位，财务又发了个表。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            strict_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            draft_gate_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            strict_findings = json.loads(strict_result.stdout)
            draft_gate_findings = json.loads(draft_gate_result.stdout)
            self.assertFalse(
                any(item["rule"] == "strict: 无依据当前职场身份" for item in strict_findings)
            )
            self.assertTrue(
                any(item["rule"] == "strict: 无依据当前职场身份" for item in draft_gate_findings)
            )

    def test_checker_draft_gate_rejects_unsupported_work_consequence_chain(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "脚踝肿起来的时候，领导在群里发了个文件，说周一要交。",
                "我想请假，又想起请假要扣钱，只好把手机扣回枕头边。",
                *(["其实我觉得厕所灯突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"] * 34),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 无依据工作后果链" for rule in rules))

    def test_checker_draft_gate_rejects_project_excuse_made_real_work_chain(self) -> None:
        body = "\n".join(
            [
                "# 暖气片",
                "",
                "狗哥问我下个月结婚来不来。",
                "我说最近忙项目，去不了。",
                "这个项目月底要交付，",
                "组长上周在群里说了，",
                "最近别想请假的事。",
                *(["其实我觉得水龙头突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"] * 34),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 无依据工作后果链" for rule in rules), findings)

    def test_checker_draft_gate_rejects_half_day_leave_escape_chain(self) -> None:
        body = "\n".join(
            [
                "# 插线板",
                "",
                "狗哥问我下个月结婚来不来。",
                "我说最近忙项目，去不了。",
                "他回了个好的。",
                "我盯着手机，想起那半天假请不下来，",
                "手上的水还把屏幕按出一个油印。",
                *(["其实我觉得水龙头突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"] * 34),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 无依据工作后果链" for rule in rules), findings)

    def test_checker_allows_third_person_social_feed_office_surface(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "大学同学发了新动态，配图是一张工牌，",
                "文案写的是新工位，新开始。",
                "我把手机扣在床上，手指上还有拖鞋盒子的灰。",
                *(["其实我觉得厕所灯突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"] * 34),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            strict_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            clean_result = subprocess.run(
                [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            draft_gate_findings = json.loads(strict_result.stdout)
            self.assertFalse(
                any(item["rule"] == "strict: 无依据当前职场身份" for item in draft_gate_findings)
            )
            self.assertNotIn("current_office_persona=", clean_result.stdout)

    def test_checker_allows_third_person_social_feed_shift_surface(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "大学同学发了张截图，",
                "说他们这周排班满了，调休也调不开。",
                "我把手机扣回床上，手指上还有拖鞋盒子的灰。",
                *(["其实我觉得厕所灯突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"] * 34),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(
                any(item["rule"] == "strict: 无依据工作后果链" for item in findings),
                findings,
            )

    def test_checker_draft_gate_rejects_unsupported_family_identity(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "上周连续中暑两天，老婆让我去医院看看。",
                "我说不用，孩子他妈就不理我了。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 无依据家庭身份: 老婆" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据家庭身份: 孩子他妈" for rule in rules))

    def test_checker_draft_gate_does_not_treat_old_lady_as_spouse_identity(self) -> None:
        body = "\n".join(
            [
                "# 水龙头",
                "",
                "楼下老太太隔着门说，你家是不是又漏水了。",
                "我手上还沾着肥皂，扶着门框说马上弄。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertFalse(any(rule == "strict: 无依据家庭身份: 太太" for rule in rules), findings)

    def test_checker_draft_gate_allows_third_person_quoted_child_identity(self) -> None:
        body = "\n".join(
            [
                "# 生瓜",
                "",
                "\"我儿子也学计算机的，\"卖瓜的把袋子递过来，袋口打了个死结。",
                "他说他儿子在北京上班，我蹲久了站起来膝盖响了一下。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertFalse(any(rule == "strict: 无依据家庭身份: 我儿子" for rule in rules))

    def test_checker_draft_gate_rejects_missing_title(self) -> None:
        body = "\n".join(
            [
                "今天楼下水龙头先咳了一下，喷到裤子上。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            normal_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            draft_gate_result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(normal_result.returncode, 0, normal_result.stderr)
            self.assertNotEqual(draft_gate_result.returncode, 0)
            findings = json.loads(draft_gate_result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 缺少标题" for item in findings))

    def test_checker_draft_gate_rejects_provenance_claims(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "这篇已经接近原文级，基本看不出来是AI生成。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 来源身份声明" for item in findings))

    def test_checker_corpus_overlap_gate_rejects_copied_source_package(self) -> None:
        source = (
            "# 日寄\n\n"
            "校招网站上有个统计offer数量的帖子，下面一排整整齐齐的0，还以为不小心点到了blued。\n"
            "投简历的时候要写爱好特长，我填会用三种方法泡出五种口感不同的泡面。\n"
        )
        draft_text = (
            "# 日寄\n\n"
            "校招网站上有个统计offer数量的帖子，下面一排整整齐齐的0，还以为不小心点到了blued。\n"
            "投简历的时候要写爱好特长，我填会用三种方法泡出五种口感不同的泡面。\n"
            + "\n".join(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36)
        )
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            corpus = temp_path / "corpus"
            corpus.mkdir()
            (corpus / "source.md").write_text(source, encoding="utf-8")
            draft = temp_path / "draft.md"
            draft.write_text(draft_text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--corpus-dir", str(corpus)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "复制重叠风险" for item in findings))

    def test_checker_draft_gate_rejects_split_binary_reframe(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "也不是故意的。就是想拿充电器而已。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: AI二元解释句式" for item in findings))

    def test_checker_draft_gate_rejects_sentence_split_binary_reframe(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "不是不想帮。是帮了得继续站在四十度底下说很多话。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: AI二元解释句式" for item in findings))

    def test_checker_draft_gate_rejects_cross_line_sentence_binary_reframe(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "不是不想帮。",
                "是帮了得继续站在四十度底下说很多话。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: AI二元解释句式" for item in findings))

    def test_checker_draft_gate_rejects_cross_line_binary_reframe(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "其实不是没投，",
                "是投完之后连已读都等不来，",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: AI二元解释句式" for item in findings))

    def test_checker_draft_gate_rejects_unsupported_background_specifics(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "上周去黄埔区面了一家公司，出了站发现走错了口。",
                "回来刷了个打野教学。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 无依据具体地名: 黄埔区" for item in findings))
            self.assertTrue(any(item["rule"] == "strict: 无依据游戏角色细节: 打野教学" for item in findings))

    def test_checker_draft_gate_rejects_invented_specific_landmark_and_restaurant(self) -> None:
        body = "\n".join(
            [
                "# 暖气片",
                "",
                "再往前是毕业那年六月底，群里发的散伙饭定位，翠屏山出来那家川菜馆。",
                "后来又想起西门外面那家烧烤摊，十块钱一把肉筋。",
                *(["其实我觉得水龙头突然坏了，于是发现杯子好像也脏，因为我差点吐出来，丢人得很。"] * 34),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 无依据具体地标" for item in findings), findings)

    def test_checker_draft_gate_rejects_social_decline_room_cold_overfill(self) -> None:
        body_lines = (
            [
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，红包加起来差不多一千多。",
                "最后发了句最近走不开，恭喜啊。",
                "他回了个抱拳。",
            ]
            + ["暖气片还是凉的，手指在袖口里缩着，泡面汤上有油。"] * 24
            + ["水龙头拧开还是冰的，厨房窗户漏着冷风，我去洗手。"] * 12
            + ["回来坐下，暖气片还是凉的，手指又开始僵了。"] * 8
        )
        body = "\n".join(["# 暖气片", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 社交拒绝室内冷感过密" for item in findings), findings)

    def test_checker_draft_gate_rejects_social_decline_texture_without_consequence(self) -> None:
        body_lines = (
            [
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，红包加路费有点顶。",
                "最后回他说最近走不开，恭喜啊。",
                "他回了个抱拳。",
            ]
            + ["手机屏幕亮了一下，手指在充电线旁边停住，水龙头还在响。"] * 18
            + ["我把杯子拿起来又放下，裤脚蹭到灰，快递盒还在门口。"] * 18
            + ["回来时手机还亮着，屏幕有点烫，手背上有一道白印。"] * 8
        )
        body = "\n".join(["# 充电线", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 社交拒绝纹理替代后果不足" for item in findings), findings)

    def test_checker_draft_gate_rejects_plain_reply_private_screen_loop_in_social_decline(self) -> None:
        body_lines = (
            [
                "水槽下面又漏了一点水，我把盆挪过去，手背先湿了。",
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，最后回他说最近忙项目，去不了，恭喜啊。",
                "他回了个好的。",
                "手上的水还把屏幕按出一个油印。",
            ]
            + ["袖口还是潮，屏幕有水印，水龙头响。"] * 35
        )
        body = "\n".join(["# 水印日寄", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 社交拒绝普通回复假后果" for item in findings), findings)

            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("social_decline_plain_reply_private_loop=") for message in messages),
                messages,
            )

    def test_checker_draft_gate_rejects_decoupled_delivery_as_social_decline_consequence(self) -> None:
        body_lines = (
            [
                "水槽下面又漏了一点水，我把盆挪过去，手背先湿了。",
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，最后回他说最近忙项目，去不了，恭喜啊。",
                "他回了个好的。",
                "外卖到了，我去门口拿。",
                "包装袋有点漏，汤顺着手背流下来。",
                "我把袋子放在桌上，烫得吹了两口气。",
            ]
            + ["厨房水龙头还在响，袖口贴着手腕，我把手机扣在桌上。"] * 31
        )
        body = "\n".join(["# 汤袋", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 社交拒绝无关后果替代" for item in findings), findings)

            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("social_decline_decoupled_consequence=") for message in messages),
                messages,
            )

    def test_checker_allows_plain_reply_when_it_changes_visible_social_action(self) -> None:
        body_lines = (
            [
                "水槽下面又漏了一点水，我把盆挪过去，手背先湿了。",
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，最后回他说最近忙项目，去不了，恭喜啊。",
                "他回了句行，那我先不把你算进桌了。",
                "门口外卖员还举着袋子等我扫码，我手上全是水，手机按了两次都没扫上。",
                "他又站了一会儿，问我是不是门口信号不好。",
            ]
            + ["我把袋子接过来，水顺着手腕往袖口里走，因为屏幕上那个付款页面还停着。"] * 34
        )
        body = "\n".join(["# 水印日寄", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("社交拒绝普通回复假后果" in item["rule"] for item in findings), findings)
            self.assertFalse(any("社交拒绝无关后果替代" in item["rule"] for item in findings), findings)

    def test_checker_draft_gate_rejects_scripted_return_gift_in_social_decline(self) -> None:
        body_lines = (
            [
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，红包加路费有点顶。",
                "最后回他说最近忙项目，去不了。",
                "狗哥隔了一会儿又发了个红包，附言说项目忙就算了，心意到了。",
            ]
            + ["我把手机扣在桌上，去门口捡掉下去的充电线。"] * 18
            + ["回来时椅子轮子卡住，我弯腰拽了一下，裤脚沾到灰。"] * 18
        )
        body = "\n".join(["# 充电线", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 社交拒绝编剧化回礼" for item in findings), findings)

    def test_checker_draft_gate_rejects_social_decline_group_crowd_fake_consequence(self) -> None:
        body_lines = (
            [
                "热水器响了一下，我把水龙头拧开，袖口先湿了。",
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，最后回他说最近忙项目，去不了。",
                "他回了个好的。",
                "第二天群里有人问，狗哥婚礼你们去几个。",
                "过了会儿有人@我，你怎么说项目忙，你们项目不是上星期就结了吗。",
                "我回了个哈哈，手机顶上有个人正在输入，闪了半天又没有下文。",
            ]
            + ["我把手机扣在桌上，水龙头还在响，袖口贴着手腕。"] * 30
        )
        body = "\n".join(["# 热水", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 社交拒绝群聊假后果" for item in findings), findings)

            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("social_decline_group_fake_consequence=") for message in messages),
                messages,
            )

    def test_checker_draft_gate_rejects_social_decline_theater_inside_prose_blocks(self) -> None:
        body = "\n".join(
            [
                "# 热水",
                "",
                "房东换热水器以后，我去问押金剩下那点钱，他发了一条语音说过两天退。电梯里碰到他的时候，两个人都看着楼层数字跳，谁也没提。",
                "晚上洗手的时候袖口被水打湿，手机在茶几上震了一下，狗哥问下个月结婚来不来。我把水关了，手上的水没擦，先去看高铁票，再看随礼，算来算去都不太对。",
                "我打出最近忙项目可能去不了，又删了一半，最后只发最近忙项目可能去不了。过了几分钟他回了一条好的，没有表情没有省略号。",
                "手机扣下去以后，水龙头还在滴，一下一下敲在盆沿上。我去厨房拿纸，纸盒空了，只剩一个压扁的纸芯，手上的水蹭到裤子上，又把屏幕按亮了一次。",
                "外套搭在沙发扶手上，两天没洗，口袋里还有一张超市小票。我把它抽出来看了一眼，上面速冻水饺十九块八，字被水汽泡得有点散，又塞了回去。",
                "第二天群里有人问，狗哥婚礼你们去几个，我看了一眼没回。过了会儿有人@我，你怎么说项目忙，你们项目不是上星期就结了吗，我盯着那个@看了几秒，打了哈哈你也知道我们那项目结是结了尾款没结，项目嘛总有事，发完把手机放下了。然后屏幕顶上有个人正在输入，闪了半天又消了。",
                "晚上我把银行打开，给他发了一个红包，四百块，附了一句抱歉人不到钱到。发完截图看了一眼，余额五百六，够交房租。",
                "过了一会儿他回了一个抱拳，说人不到没事，下次一起吃饭。我打了一个好字，发完之后觉得那个好字比昨天的可能去不了要轻得多。",
                "热水器这回声音小了点，水龙头还是滴，袖口贴在手腕上，我坐了一会儿，把手机扣在桌上。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = {item["rule"] for item in findings}
            self.assertIn("strict: 社交拒绝群聊假后果", rules)
            self.assertIn("strict: 社交拒绝礼貌闭合", rules)

    def test_checker_draft_gate_rejects_narrator_red_packet_etiquette_closure(self) -> None:
        body_lines = (
            [
                "热水器响了一下，我把水龙头拧开，袖口先湿了。",
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，最后回他说最近忙项目，去不了。",
                "他回了个好的。",
                *(["我坐下来，右手还有点潮，热水器在墙里响。"] * 32),
                "我把银行打开，给他发了一个红包，四百块。",
                "附了一句抱歉人不到钱到。",
                "过了一会儿他回了一个抱拳，说人不到没事，下次一起吃饭。",
                "我打了一个好字，发完把手机扣在桌上。",
            ]
        )
        body = "\n".join(["# 热水", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 社交拒绝礼貌闭合" for item in findings), findings)

            messages = preflight_messages(draft)
            self.assertTrue(
                any(message.startswith("social_decline_tidy_etiquette_closure=") for message in messages),
                messages,
            )

    def test_checker_allows_social_decline_local_consequence_without_crowd_or_etiquette(self) -> None:
        body_lines = (
            [
                "热水器响了一下，我把水龙头拧开，袖口先湿了。",
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，最后回他说最近忙项目，去不了。",
                "他回了句那我先不把你算进桌了。",
                "门口外卖员还举着袋子等我扫码，我手上全是水，手机按了两次都没扫上。",
                "他问我是不是门口信号不好，我回了一句可能是手不行。",
            ]
            + ["我把袋子接过来，水顺着手腕往袖口里走，屏幕还停在付款页。"] * 30
        )
        body = "\n".join(["# 热水", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            forbidden = {"strict: 社交拒绝群聊假后果", "strict: 社交拒绝礼貌闭合"}
            self.assertFalse(any(item["rule"] in forbidden for item in findings), findings)

    def test_checker_draft_gate_rejects_private_transfer_loop_in_social_decline(self) -> None:
        body_lines = (
            [
                "洗碗的时候漏网上卡着几片菜叶，我伸手抠了一下。",
                "狗哥发微信说下个月结婚，问我来不来。",
                "往前翻还有几条他让我帮他取快递的语音，他问我在不在宿舍。",
                "我看了高铁和随礼，红包加路费有点顶。",
                "最后回他说最近忙项目，去不了，恭喜啊兄弟。",
                "突然想起那顿饭钱，打开支付宝找到狗哥。",
                "我输了六十六，备注写不上，发了。",
                "等了一会儿，交易失败，系统提示对方未领取。",
                "我又打开看了一眼，已读但钱没收。",
            ]
            + ["手机屏幕亮了一下，手指在充电线旁边停住，水龙头还在响。"] * 16
            + ["我把杯子拿起来又放下，客厅蓝光照着茶几。"] * 16
        )
        body = "\n".join(["# 下个月", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 社交拒绝私密转账假后果" for item in findings), findings)

    def test_checker_draft_gate_allows_social_decline_with_congratulations_not_refusal(self) -> None:
        body_lines = (
            [
                "晚上拖地，拖把杆拧到一半又缩回去。",
                "狗哥说下个月结婚，问我能不能来。",
                "我先回恭喜，后面本来接着肯定，打出来又删了。",
                "因为我已经点开了日历。",
                "查了查票，周五到得太晚，周六又赶不上中午。",
                "我点到付款，停住了。",
                "狗哥问票是不是不好买，我说还在看。",
                "大叔在外面敲门，帮我送快递，垃圾袋掉了两卷。",
                "我在楼道里穿着湿袜子追垃圾袋。",
                "回屋以后打了一句最近忙项目，又改成实在去不了。",
                "狗哥回好，没事，忙你的。",
                "门锁没扣住，弹开一点。",
                "我站在门缝后面，打了几个字又删了。",
                "地拖了一半，水已经凉了。",
                "垃圾袋套进桶里，袋口太松，压进去一团纸就滑下去。",
                "湿袜子踩在鞋印上，滑了一步。",
            ]
            + ["窗外安静下来，没人再下楼。"] * 20
        )
        body = "\n".join(["# 最后一班", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("社交拒绝后果过度生长" in item["rule"] for item in findings), findings)

    def test_checker_draft_gate_rejects_overextended_social_decline_aftermath(self) -> None:
        body_lines = (
            [
                "充电线从桌子下面伸上来，插头有点松。",
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁票和随礼，最后回他说最近忙项目，去不了。",
                "他回了个表情。",
                "第二天早上班群里发了合照，我点开放大看了半天。",
                "中午到站以后同事问我谁结婚，我说大学同学。",
                "下午狗哥又发了个红包，问兄弟能不能来当伴郎。",
                "我回座位打了几个字，说伴郎可能当不了，到时候喝喜酒。",
                "他回不强求，我把手机扣在桌上。",
            ]
            + ["回来时椅子轮子卡住，我弯腰拽了一下，裤脚沾到灰，又把手机翻过来。"] * 40
        )
        body = "\n".join(["# 充电线", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 社交拒绝后果过度生长" for item in findings), findings)

    def test_checker_draft_gate_allows_small_next_day_residue_in_social_decline(self) -> None:
        body_lines = (
            [
                "洗碗的时候漏网上卡着几片菜叶，我伸手抠了一下。",
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁和随礼，最后回他说最近走不开，恭喜啊。",
                "他隔了半天回了个好。",
                "第二天早上醒来，看见那条好还在最下面，没再点开。",
                "我把垃圾袋拎到门口，袋口没系紧，汤水顺着手腕流下来。",
            ]
            + ["回来时椅子轮子卡住，我弯腰拽了一下，裤脚沾到灰。"] * 30
        )
        body = "\n".join(["# 袋口", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("社交拒绝后果过度生长" in item["rule"] for item in findings), findings)

    def test_checker_draft_gate_rejects_third_person_narrator_slip(self) -> None:
        body_lines = (
            [
                "我把杯子拿去洗，水龙头先咳了一下，喷到裤子上。",
                "我站在那儿没动，手背上全是水。",
                "我把手机扣在桌上。",
                "他把手机塞到枕头底下，灭了屏幕。",
            ]
            + ["我把杯子拿去洗水龙头先咳了一下喷到裤子上。"] * 38
        )
        body = "\n".join(["# 枕头", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 叙述人称滑移" for item in findings), findings)

    def test_checker_draft_gate_allows_third_person_bedroom_context_when_attributed(self) -> None:
        body_lines = (
            [
                "狗哥发微信说他最近搬家。",
                "他说他把手机塞到枕头底下，闹钟还是响。",
                "我回了个哦，手背上还有水。",
            ]
            + ["我把杯子拿去洗水龙头先咳了一下喷到裤子上。"] * 38
        )
        body = "\n".join(["# 枕头", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("叙述人称滑移" in item["rule"] for item in findings), findings)

    def test_checker_draft_gate_rejects_non_diary_diagnostic_wedding_title(self) -> None:
        body_lines = (
            [
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了一眼高铁票，又把手机扣在桌上。",
                "水池里有个碗没洗，油浮在上面。",
                "最后回他说最近走不开，恭喜啊。",
            ]
            + ["我把手机扣在桌上，去门口捡掉下去的充电线。"] * 20
            + ["回来时椅子轮子卡住，我弯腰拽了一下，裤脚沾到灰。"] * 12
        )
        body = "\n".join(["# 狗哥的婚礼", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 题面诊断型标题" for item in findings), findings)

    def test_checker_allows_social_decline_with_one_room_side_object(self) -> None:
        body_lines = (
            [
                "狗哥发微信说下个月结婚，问我来不来。",
                "我看了高铁，又问了随礼，红包加路费有点顶。",
                "暖气片响了一声就停了。",
                "我把泡面推到桌角，手指在输入框里停了一下。",
                "最后发了句最近走不开，恭喜啊。",
                "他回了个抱拳，又问还记不记得大学时候那家店。",
            ]
            + ["我把手机扣在桌上，去门口捡掉下去的充电线。"] * 20
            + ["回来时椅子轮子卡住，我弯腰拽了一下，裤脚沾到灰。"] * 12
        )
        body = "\n".join(["# 日寄", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("社交拒绝室内冷感过密" in item["rule"] for item in findings), findings)

    def test_checker_draft_gate_rejects_background_display_stuffing(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "211毕业之后我在云南送外卖，狗哥发消息问我王者打不打。",
                "我点开知乎，又想起自己被裁之后痛风，脚踝还疼。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 背景展示堆砌" for item in findings))

    def test_checker_allows_coarse_game_when_it_has_scene_consequence(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "以前打王者打了很多局，最高也就星耀五，",
                "我把这个事想起来，发现有些东西确实不是努力就能解决。",
                "后来水龙头先咳了一下，喷到裤子上，",
                *(["其实我把杯子拿去洗，洗到一半又想起那张没回的表，"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertFalse(any("无依据游戏角色细节" in rule for rule in rules))
            self.assertFalse(any("游戏复盘细节" in rule for rule in rules))
            self.assertFalse(any("背景展示堆砌" in rule for rule in rules))

    def test_checker_does_not_treat_mineral_water_as_game_fountain(self) -> None:
        body = "\n".join(
            [
                "# 凉水日寄",
                "",
                "我买了一瓶矿泉水，瓶盖拧到一半掉在地上，",
                "脚趾头露在拖鞋外面，尴尬地缩了一下，",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertFalse(any("无依据游戏角色细节: 泉水" in rule for rule in rules))

    def test_checker_does_not_treat_route_lookup_as_bot_lane(self) -> None:
        body = "\n".join(
            [
                "# 路线日寄",
                "",
                "我查了下路线，导航说还要转两趟车，",
                "门口的水还没擦，鞋底踩过去响了一下，",
                *(["其实我把杯子拿去洗，洗到一半又想起那张没回的表，"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertFalse(any("无依据游戏角色细节: 下路" in rule for rule in rules))

    def test_checker_flags_unsupported_province_or_city_for_review(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "我回湖南住了几天。",
                "到长沙的时候手机没电。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "具体城市需核实: 湖南" for item in findings))
            self.assertTrue(any(item["rule"] == "具体城市需核实: 长沙" for item in findings))

    def test_checker_draft_gate_rejects_blog_like_explainer_voice(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "手机红点一直亮。",
                "本质上这说明我还在等一个根本不会来的消息。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"].startswith("strict: AI解释腔") for item in findings))

    def test_checker_draft_gate_rejects_literary_ai_explanation_surface(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "听不太清，但能认出那句没问题下周可以的语气——那种终于可以把话说得很轻的放松。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 破折号解释连接" for rule in rules))
            self.assertTrue(any(rule == "strict: AI文艺解释面" for rule in rules))

    def test_checker_draft_gate_rejects_caption_simile_surface(self) -> None:
        body = "\n".join(
            [
                "# 生瓜",
                "",
                "那句话像一颗钉子，钉在那里拔不出来。",
                "招聘消息像扔进井里，连个回声都没有。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 字幕式明喻解释" for item in findings))

    def test_checker_draft_gate_rejects_residual_comment_chain_surface(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "底下跟了一串回答。",
                "底下追了一串问号，被人回了个笑哭。",
                "下面跟了一排恭喜。",
                "第一条回复是谢邀人在美国刚下飞机。",
                "评论区还有一个热评。",
                "有人问尿酸查不查，跟了个捂脸。",
                "又发了个文档。",
                "发截图的人又发了一条。",
                "群里回了两个人，一个说看看。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 评论链公式化转述" for item in findings))

    def test_checker_does_not_treat_one_to_one_emoji_as_comment_chain(self) -> None:
        body = "\n".join(
            [
                "# 灯泡",
                "",
                "房东回了句好的，后面跟了个笑脸，我看了没回，把手机扣在桌上。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("评论链公式化转述" in item["rule"] for item in findings))

    def test_checker_does_not_treat_one_to_one_red_packet_as_comment_chain(self) -> None:
        body = "\n".join(
            [
                "# 22日寄",
                "",
                "他隔了一会儿又发了个红包，说让我沾点喜气，我点开只有一块两毛五。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("评论链公式化转述" in item["rule"] for item in findings))

    def test_checker_does_not_treat_ambient_someone_talking_as_comment_chain(self) -> None:
        body = "\n".join(
            [
                "# 门口",
                "",
                "外面好像有人说话，听不清，",
                "我把塑料袋往门后塞了一下，手背上还有油。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("评论链公式化转述" in item["rule"] for item in findings))

    def test_checker_still_flags_group_redocument_reaction_surface(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "群里又发了个文档，下面跟了一排收到。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 评论链公式化转述" for item in findings))

    def test_checker_still_flags_contextual_followed_emoji_comment_surface(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "下面跟了个表情，底下又追了一串问号。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 评论链公式化转述" for item in findings))

    def test_checker_draft_gate_rejects_standalone_daily_dialogue_quotes(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "\"晚上吃的啥。\"",
                "\"面。\"",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 日常对话引号" for item in findings))

    def test_clean_run_preflight_flags_embedded_quote_and_caption_simile(self) -> None:
        body_lines = [
            "其实我下楼买水的时候，",
            "卖瓜的说他儿子在北京一个月两万多，我手上黑泥还没洗干净。",
            "\"好好干，年轻人机会多。\"他笑起来。",
            "那句话像一颗钉子，钉在那里拔不出来。",
            "不过我发现袋子勒得手指疼，于是换了一只手，",
            "胃响了一声，旁边店员抬头看我。",
            "很丢人。",
        ] * 8
        body = "\n".join(["# 生瓜", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLEAN_RUN_CHECKER), str(draft), "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("quoted_dialogue=present", result.stdout)
            self.assertIn("literary_simile_caption=present", result.stdout)
            self.assertIn("payment, object handling, body noise", result.stdout)
            self.assertIn("delete the explanatory simile", result.stdout)

    def test_checker_draft_gate_rejects_adc_game_role_but_not_one_piece_surface(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "第一把选了蔡文姬，adc走位像在送。",
                "嘴皮上烫了一块。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: 无依据游戏角色细节: adc" for item in findings))
            self.assertFalse(any(item["rule"] == "金额后缀（中文数字）" for item in findings))

    def test_checker_does_not_flag_piece_counter_as_money_suffix(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "墙皮上印了个湿手印，蹲下去捡了两块泡沫。",
                "桌上还有三块石头和一块旧布。",
                "手机里那杯水显示五块钱。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            money_infos = [item for item in findings if item["rule"] == "金额后缀（中文数字）"]
            self.assertEqual(len(money_infos), 1)
            self.assertIn("五块钱", money_infos[0]["excerpt"])

    def test_checker_draft_gate_rejects_ai_variable_placeholder_sentence(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "你准备好的是A，拿到的却是B，而且不能退货，得咽下去。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(any(item["rule"] == "strict: AI变量代称" for item in findings))

    def test_checker_draft_gate_rejects_general_em_dash_and_game_surface(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "门没关严，声音漏进来——下个月，入职，公积金。",
                "第二把两个秒选法师。",
                "我补了个辅助。",
                "看到战令还有两级。",
                "打了一把排位。",
                "星耀二掉到星耀三。",
                "我打原神打到半夜。",
                "我满血站在复活点。",
                "面板弹出个MVP。",
                "全程加血。",
                "全程加盾。",
                "蔡文姬一直奶不到人。",
                "输出全靠队友。",
                "队友全死了。",
                "退出匹配以后手机还亮着。",
                "队友秒选以后我把手机放下。",
                "他一直发撤退信号。",
                "二塔那波我没过去。",
                "团战开得太快。",
                "最后三换二。",
                "结算界面还有红点。",
                "阵容从一开始就不对。",
                "我在泉水等复活。",
                "经济面板打开看了一眼。",
                "输出比辅助低。",
                "队友一直发干得漂亮。",
                "王者晋级赛输了。",
                "我关了结算页面。",
                "开局频道里一直亮。",
                "有人喊来硬辅。",
                "下路送了俩。",
                "队友点了好几次。",
                "装备栏还亮着。",
                *(["我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 破折号稀有连接" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 补了个辅助" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 秒选法师" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 战令" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 排位" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 星耀二" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 打原神" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 复活点" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: MVP" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 加血" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 加盾" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 奶不到" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 输出全靠" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 队友全死" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 退出匹配" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 队友秒选" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 撤退信号" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 二塔" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 团战" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 三换二" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 结算界面" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 阵容" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 泉水" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 经济面板" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 输出比辅助" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 干得漂亮" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 晋级赛" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 结算页面" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 开局频道" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 硬辅" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 下路" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 队友点" for rule in rules))
            self.assertTrue(any(rule == "strict: 无依据游戏角色细节: 装备" for rule in rules))

    def test_checker_draft_gate_rejects_sub_850_standard_diary_buffer(self) -> None:
        line = "其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"
        body = "\n".join(["# 日寄", "", *([line] * 29)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            self.assertTrue(
                any(item["rule"] == "strict: 标准日寄完整文章篇幅缓冲不足" for item in findings)
            )

    def test_checker_draft_gate_rejects_pseudo_colloquial_and_ordered_skeleton(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "我稳稳的接住了这次失眠。",
                "首先我把杯子拿去洗，最后水龙头先咳了一下喷到裤子上。",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: AI伪口语: 稳稳的接住" for rule in rules))
            self.assertTrue(any(rule == "strict: AI完整结构" for rule in rules))

    def test_skill_runtime_docs_do_not_depend_on_external_stop_slop_skill(self) -> None:
        files = [
            ROOT / "SKILL.md",
            ROOT / "references" / "clean-generation-brief.md",
            ROOT / "references" / "anti-ai-slop.md",
            ROOT / "references" / "feature-budget.md",
            ROOT / "references" / "generation-modes.md",
            ROOT / "references" / "writing-checklist.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in files).lower()
        self.assertNotIn("stop-slop", combined)
        self.assertNotIn("stopslop", combined)
        self.assertIn("self-contained", combined)
        self.assertIn("not ingredients", combined)
        self.assertIn("game is allowed", combined)
        self.assertIn("prompt silence does not ban", combined)
        self.assertNotIn("缺一条就不是", combined)

    def test_runtime_layer_map_keeps_generation_and_validation_separate(self) -> None:
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Layer 0: Entry Contract", layer_map)
        self.assertIn("Layer 4: Controller Validation", layer_map)
        self.assertIn("background facts are contradiction boundaries", layer_map.lower())
        self.assertIn("Do not solve a generation failure only by adding a new checker rule", layer_map)
        self.assertIn("Mode Router", skill)
        self.assertIn("Artifact-Backed Entry Contract", skill)
        self.assertIn("do not compose the article directly in the final chat response", skill)
        self.assertIn("The first prose artifact must be a real `draft.md`", skill)
        self.assertIn("A terminal-only article is a failed run", skill)
        self.assertIn('"Output prose only" means output only the final article after the artifact-backed draft/check path', skill)
        self.assertIn("Controller validation mode", skill)
        self.assertIn("generator and controller separated", layer_map.lower())
        self.assertIn("Deep references in Layer 3 are repair libraries", layer_map)
        self.assertIn("runtime-layer-map.md", readme)
        self.assertIn("runtime-layer-map.md", skill)
        self.assertIn("not load it during ordinary article generation", (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8").lower())
        self.assertIn("Own the clean-eval first-draft source loop", layer_map)
        self.assertIn("Layer 1 is not a pre-draft requirement", layer_map)

    def test_bounded_repair_uses_wrapper_output_without_long_reference_reload(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        first_draft_min = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(
            encoding="utf-8"
        )
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")

        for text in (skill, first_draft_min, runtime):
            lowered = text.lower()
            self.assertIn("the wrapper output is the complete repair interface", lowered)
            self.assertIn("do not load `references/clean-generation-brief.md`", lowered)
            self.assertIn("if no rhythm script is named, rerun the wrapper immediately after the content write", lowered)
            self.assertIn(
                "if a rhythm script is named after a content write, run that exact script with `--in-place` as the final mutation",
                lowered,
            )
            self.assertNotIn("after any `draft.md` rewrite, rerun the wrapper immediately", lowered)
            self.assertIn("when the action says `whole_source_rebuild`", lowered)
            self.assertIn("without running a rhythm script", lowered)
            self.assertIn("do not read its stdout", lowered)
            self.assertIn("day-shaped collage", lowered)
            self.assertIn("independent thought-turns", lowered)
            self.assertIn("do not shrink it to a short premise summary", lowered)

        self.assertNotIn(
            "use `references/clean-generation-brief.md` as the detailed repair interface",
            skill,
        )
        self.assertIn("wrapper output only; no additional reference read", readme)
        self.assertIn("Controller/developer reference only", clean)
        self.assertIn("do not load this file inside a bounded clean-eval generator", clean.lower())
        self.assertIn("expanded controller/developer repair reference", layer_map)

    @unittest.skip("superseded by fragment-source ownership and artifact-boundary regression tests")
    def test_formal_first_draft_uses_source_loop_not_long_repair_files(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        first_draft_min = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        standard_engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        title_model = (ROOT / "references" / "title-model.md").read_text(encoding="utf-8")
        anti_ai = (ROOT / "references" / "anti-ai-slop.md").read_text(encoding="utf-8")
        modes = (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8")
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        eval_readme = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
        clean_run = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")

        self.assertIn("clean-eval-first-draft-minimum.md", skill)
        self.assertIn("Use this file for the first complete draft", first_draft_min)
        self.assertIn("It is intentionally short", first_draft_min)
        self.assertLess(len(first_draft_min.splitlines()), len(clean.splitlines()) // 2)
        self.assertIn("the wrapper output is the complete repair interface", skill)
        self.assertIn("`references/runtime-brief.md`", skill)
        self.assertIn("references/clean-generation-brief.md", skill)
        self.assertIn("CLEAN_RUN_PREFLIGHT_STOP", skill)
        self.assertIn("stop repairing, read `draft.md` once, and output that exact article", skill)
        self.assertIn("Do not skip the temporary artifact just because the final reply should contain prose only", skill)
        self.assertIn("output prose only after the article has existed as `draft.md`", skill)
        self.assertIn("The bounded generator must not read this file", clean)
        self.assertIn("references/anlin-collage-source-model.md", skill)
        self.assertIn("anlin-collage-source-model.md", skill)
        # The old standard-diary-source-engine.md is preserved for reference, but the new routing
        # uses anlin-collage-source-model.md. The old file still exists on disk.
        self.assertIn("fragment slate", first_draft_min)
        self.assertIn("anlin-collage-source-model.md", clean)
        self.assertIn("The bounded generator starts from `references/clean-eval-first-draft-minimum.md`", clean)
        # The old engine file is preserved; test its content
        self.assertIn("after `clean-eval-first-draft-minimum.md` and before the first `draft.md`", standard_engine)
        self.assertNotIn("after `clean-generation-brief.md` and before the first `draft.md`", standard_engine)
        self.assertIn("Build The Middle First", standard_engine)
        self.assertIn("something happens, so I must do the next thing", standard_engine)
        self.assertIn("Do not run `rebalance_line_rhythm.py`, `split_long_lines.py`, `merge_short_lines.py`, or `soften_line_endings.py` before the first `clean_run_checker.py` call", standard_engine)
        self.assertIn("Do not use a prose-block escape hatch", standard_engine)
        self.assertIn("The first saved file is not allowed to be a prose draft waiting for later lineation", first_draft_min)
        self.assertIn("5-7 long paragraphs", first_draft_min)
        self.assertIn("the `content` field itself should already show broken body rows", first_draft_min)
        self.assertIn("do not paste five dense body paragraphs", standard_engine)
        self.assertIn("The controller is measuring that first saved shape", standard_engine)
        self.assertIn("phone/feed -> order food -> wrong item -> wash bowl -> bed", standard_engine)
        self.assertIn("Private grime is not an event", standard_engine)
        self.assertIn("A rider or cashier who only looks once, points once, or speaks once and then leaves is still decoration", standard_engine)
        self.assertIn("One material family cannot become proof for every function", standard_engine)
        self.assertIn("it has become a stain ledger", standard_engine)
        self.assertIn("First Two Clusters", standard_engine)
        self.assertIn("Snag first", standard_engine)
        self.assertIn("Topic late", standard_engine)
        self.assertIn("Outside pressure active", standard_engine)
        self.assertIn("Medium changes", standard_engine)
        self.assertIn("This is not a five-item content quota", standard_engine)
        self.assertIn("Start from friction, not from the prompt noun", first_draft_min)
        self.assertIn("The user's topic is pressure, not the route map", first_draft_min)
        self.assertIn("Prompt Displacement", first_draft_min)
        self.assertIn("the refusal aftermath must be carried by the moving chain itself", first_draft_min)
        self.assertIn("Use the water-drip test for this family", standard_engine)
        self.assertIn("prompt-object ledgers", clean)
        self.assertIn("Do not repair an engine warning by adding another oil/stain/body line", clean)
        self.assertIn("they should not route the generator into deeper references from here", clean)
        self.assertIn("Use this loop instead of opening the long runtime or review files", clean)
        self.assertIn("repair by replacing failed scene functions, not by adding feature labels", clean)
        self.assertIn("Before the first complete `draft.md`, do not open long repair", skill)
        self.assertIn("do not load `references/clean-generation-brief.md`", skill)
        self.assertIn("Reference Routing", skill)
        self.assertIn("do not reuse a prior run path", skill)
        self.assertIn("Do not rediscover this skill by globbing, `Test-Path`, listing parent skill directories", (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8"))
        self.assertIn("Extra pre-draft files contaminate the source-guidance measurement", clean)
        self.assertIn("Before writing `draft.md`, do a private source preflight", clean)
        self.assertIn("If a candidate title and body already exist in your head, write `draft.md` immediately", clean)
        self.assertIn("A persisted imperfect article is a valid clean-eval artifact", clean)
        self.assertIn("a long visible calculation with no `draft.md` is an invalid run", clean)
        self.assertIn("no group/comment chain markers", clean)
        self.assertIn("no theatrical ordinary dialogue in quote marks", clean)
        self.assertIn("no polished simile caption after abstract pressure", clean)
        self.assertIn("one coarse body/social/self-own consequence", clean)
        self.assertIn("Use the preflight message as a shape diagnosis", clean)
        self.assertIn("Known failed source shape", clean)
        self.assertIn("fluent 10-15 paragraph article", clean)
        self.assertIn("complete small realist story", clean)
        self.assertIn("the visible article itself should already look like clusters of breath", clean)
        self.assertIn("do not restate diagnostic words as a checklist", clean)
        self.assertIn("the metric names changed", clean)
        self.assertIn("For 朋友圈, short-video feeds, annual-summary feeds", clean)
        self.assertIn("Do not write a feed montage", clean)
        self.assertIn("phone/feed -> order food -> wrong item -> wash bowl -> bed", clean)
        self.assertIn("run `soften_line_endings.py` last before the next wrapper call", clean)
        self.assertIn("final-line phrase such as `明天再说吧`", clean)
        self.assertIn("tail-button sentence titles", title_model)
        self.assertIn("makes the last line feel written to justify the title", title_model)
        self.assertIn("screen-archaeology chain", clean)
        self.assertIn("old-chat records", clean)
        self.assertIn("Use visible breathing clusters before the first file write", clean)
        self.assertIn("quick page-shape glance only", clean)
        self.assertIn("Do not produce a visible numbered draft", clean)
        self.assertIn("let the checker measure exact rows and characters", clean)
        self.assertNotIn("count actual visible body rows", clean)
        self.assertIn("Near-miss drafts are a repeated failure", clean)
        self.assertIn("visibly lacks a full middle corridor", clean)
        self.assertIn("for a near-miss short draft", clean_run)
        self.assertIn("Rough self-damage is narrower than ordinary awkwardness", clean)
        self.assertIn("脸应该挺难看", clean)
        self.assertIn("也不是疼，就是", clean)
        self.assertIn("其实不是想X，就是", clean)
        self.assertIn("最疼的不是X，是Y", clean)
        self.assertIn("Scan the whole article for this surface", clean)
        self.assertIn("Remove all occurrences before the next checker call", clean)
        self.assertIn("make a local replacement only", clean)
        self.assertIn("medium-length short-line grid", clean)
        self.assertIn("A 900-949 character draft can still be underbuilt", clean)
        self.assertIn("source-loop rewrite before the first file write", clean)
        self.assertIn("Do not patch it by adding five more symptoms", clean)
        self.assertNotIn("2-3 load-bearing action clusters", clean)
        self.assertIn("release that carrier after one consequence transfer", clean)
        self.assertIn("deleting it would break the next action", clean)
        self.assertIn("phone/feed -> order food -> wrong item -> wash bowl -> bed", clean)
        self.assertIn("do not automatically insert an outside person", clean)
        self.assertIn("If contact is used, it must be load-bearing", clean)
        runtime_brief = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        self.assertNotIn("2-3 load-bearing action clusters", runtime_brief)
        self.assertIn("release that carrier after one consequence transfer", runtime_brief)
        self.assertIn("Layer 2 contradiction gates", (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8"))
        self.assertIn("A 900-949 character draft can still be underbuilt", clean)
        self.assertIn("do not make nearly every line carry body, money, route, screen", clean)
        self.assertIn("rebalance_line_rhythm.py draft.md --in-place", clean)
        self.assertIn("Do not let the repair bounce from short-line grid into 30-40 prose lines", clean)
        self.assertIn("Do not write a prose version first", clean)
        self.assertIn("true short breath means about 8 Chinese characters or fewer", clean)
        self.assertIn("true short breath drops", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("Do not write a prose version first and then promise to restructure it", clean)
        self.assertIn("do not hand-count characters or rows before saving", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("let the checker measure exact rows and characters", clean)
        self.assertIn("rough visual corridor", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("clean_run_checker.py", (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8"))
        self.assertIn("Do not hand-count characters or line totals before the first file write", (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8"))
        self.assertIn("Status 0 at a stop boundary only means the protocol message was delivered", clean)
        self.assertIn("After the first clean-eval `draft.md` write, do not run your own counting or metric probe before the wrapper", clean)
        self.assertIn("homemade regex counters", clean)
        self.assertIn("Do not rewrite `draft.md` repeatedly before the first wrapper", clean)
        self.assertIn("line count as the target", standard_engine)
        self.assertIn("generated caption grid", standard_engine)
        self.assertIn("6-8 breathing clusters", standard_engine)
        self.assertIn("several rough long rows", standard_engine)
        self.assertIn("Do not turn the message surface into a numbered chat log", standard_engine)
        self.assertIn("Do not move the plot by message order such as `X发了第二条`", clean)
        self.assertIn("`第二条只...`", clean)
        self.assertIn("`下面还有一个...`", standard_engine)
        self.assertIn("Before saving a standard diary draft, look at the visible body shape", clean)
        self.assertIn("80+ one-sentence rows", standard_engine)
        self.assertIn("`OK` reply or silence is not enough", clean)
        self.assertIn("The roughness must be active, not ornamental", standard_engine)
        self.assertIn("Cluster Grammar, Not Metrics", standard_engine)
        self.assertIn("what is still happening after this line?", standard_engine)
        self.assertIn("Do not let `已经/现在/只是/可能` carry most of the article's movement", standard_engine)
        self.assertIn("Hallway witnesses work only when the witness and the ugly fact stay in the same action chain", standard_engine)
        self.assertIn("For hallway or stairwell witnesses", clean)
        self.assertIn("For hallway/aunt/neighbor repairs", (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8"))
        self.assertIn("ask only these five questions", standard_engine)
        self.assertNotIn("ask only these four questions", standard_engine)
        self.assertIn("This is a hard tool-order rule", clean)
        self.assertIn("the next wrapper call is valid only if `draft.md` was not rewritten", clean)
        self.assertIn("or if the relevant rhythm script was rerun after the rewrite", clean)
        self.assertIn("`后面跟着...`", first_draft_min)
        self.assertIn("Do not print an English or Chinese scene plan", clean)
        self.assertIn("Complete article` does not mean complete prompt coverage", clean)
        self.assertIn("quiet interior prompts", clean.lower())
        self.assertIn("phone/feed + room + food/order + bed", clean)
        self.assertIn("one outside contact or practical handoff", clean)
        self.assertIn("A mere glance, mirror inspection, or private \"I look bad\" line is usually not enough", runtime)
        self.assertIn("Explicit negative constraints outrank scene instincts", clean)
        self.assertIn("no store checkout, buying water, delivery order, receipt, payment gesture", clean)
        self.assertIn("不要写金钱、消费或价格", clean)
        self.assertIn("Shopping, parcel, wrong-size, coupon, delivery, or household-object", runtime)
        self.assertIn("split the user's prompt nouns into five buckets", runtime)
        self.assertIn("`forbidden`: any explicit \"do not write\" domain", runtime)
        self.assertIn("Do not keep `超市`, `收银台`, `矿泉水`", runtime)
        self.assertIn("If the draft only says the object is wrong", clean)
        self.assertIn("no long action/speech/thought rows", clean)
        self.assertIn("not as an extra bounded repair prompt", runtime)
        self.assertIn("Do not load this file or `clean-generation-brief.md` inside that bounded repair", anti_ai)
        self.assertIn("wrapper output alone owns repair", modes)
        self.assertIn("source-load conflict", readme)
        self.assertIn("runtime-brief.md`, `generation-modes.md`, and `anti-ai-slop.md` remain available for ordinary repair", readme)
        self.assertIn("Explicit prompt prohibitions were manually checked", validation)
        self.assertIn("blocking prompt-compliance failure", eval_readme)
        self.assertIn("visible same-domain replacement is a blocking prompt-compliance failure", validation)
        self.assertIn("not to write money/consumption/price", readme)

    def test_model_rotation_is_controller_protocol_not_runtime_branching(self) -> None:
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        eval_readme = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
        development_log = (ROOT / "references" / "development-log.md").read_text(encoding="utf-8")
        runtime_files = [
            ROOT / "SKILL.md",
            ROOT / "references" / "clean-generation-brief.md",
            ROOT / "references" / "runtime-brief.md",
            ROOT / "references" / "runtime-layer-map.md",
        ]
        runtime_combined = "\n".join(path.read_text(encoding="utf-8") for path in runtime_files).lower()

        self.assertIn("rotate generation models across a declared external pool", validation)
        self.assertIn("Keep the concrete pool outside the distributable skill", validation)
        self.assertIn("Do not add model-name branches", validation)
        self.assertIn("Development tests should rotate across multiple available model surfaces", readme)
        self.assertIn("Concrete local model pools belong in `references/development-log.md`, not in this user-facing README", readme)
        self.assertNotIn("longcat/LongCat-2.0", readme)
        self.assertIn("longcat/LongCat-2.0", development_log)
        self.assertIn("lowest-use available surfaces", readme)
        self.assertIn("runtime instructions should stay model-agnostic", readme)
        self.assertIn("开发测试应轮换生成模型", eval_readme)
        self.assertIn("不要把某个模型上轮失败的分析追加给下轮生成 agent", eval_readme)
        validation_lower = validation.lower()
        for provider_token in ["deepseek", "mimo", "minimax", "gpt-5.5", "big-pickle", "longcat"]:
            self.assertNotIn(provider_token, validation_lower)
            self.assertNotIn(provider_token, runtime_combined)

    def test_isolated_judge_templates_are_active_without_legacy_prompt_file(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        judge_templates = (ROOT / "references" / "judge-prompt-templates.md").read_text(encoding="utf-8")
        development_log = (ROOT / "references" / "development-log.md").read_text(encoding="utf-8")
        prepare_blind = (ROOT / "scripts" / "prepare_blind_test.py").read_text(encoding="utf-8")
        run_blind = (ROOT / "scripts" / "run_blind_test.py").read_text(encoding="utf-8")

        self.assertIn("judge-prompt-templates.md", readme)
        self.assertIn("references/judge-prompt-templates.md", layer_map)
        self.assertIn("Controller Judge Prompt Templates", judge_templates)
        self.assertIn("They do not require any special parallel-agent capability", judge_templates)
        self.assertIn("8 impostor + 2 placebo", validation)
        self.assertNotIn("3 impostor + 1 placebo", validation)
        self.assertNotIn("3+1", validation)
        self.assertNotIn("--rounds 3", validation)
        self.assertFalse((ROOT / "references" / "subagent-prompts.md").exists())
        self.assertIn("Documentation architecture cleanup on 2026-07-07", development_log)
        self.assertIn("Strict blind-package correction on 2026-07-07", development_log)
        self.assertIn("not new evidence that the `<=10%` target has been reached", development_log)
        self.assertIn('default=8, help="Number of impostor rounds"', run_blind)
        self.assertIn('default=2, help="Number of all-original placebo calibration rounds"', run_blind)
        self.assertIn("build_judge_prompt", prepare_blind)
        self.assertIn("build_judge_prompt", run_blind)
        self.assertNotIn("build_subagent_prompt", prepare_blind)
        self.assertNotIn("build_subagent_prompt", run_blind)

        active_docs = [
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "evals" / "README.md",
            ROOT / "references" / "runtime-layer-map.md",
            ROOT / "references" / "validation-protocol.md",
            ROOT / "references" / "self-check.md",
            ROOT / "references" / "portable-corpus.md",
            ROOT / "references" / "evals.md",
        ]
        for path in active_docs:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("references/subagent-prompts.md", text)
            self.assertNotIn("子代理", text)
            self.assertNotIn("3 impostor + 1 placebo", text)
            self.assertNotIn("3+1", text)
            self.assertNotIn("--rounds 3", text)

    def test_validation_protocol_verifies_resolved_opencode_isolation(self) -> None:
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")

        self.assertIn("opencode debug paths", validation)
        self.assertIn("resolved config root", validation)
        self.assertIn("opencode debug skill", validation)
        self.assertIn("all non-built-in skills", validation)
        self.assertIn("`OPENCODE_CONFIG_DIR` alone is not isolation evidence", validation)
        self.assertIn("`XDG_CONFIG_HOME`", validation)

    def test_progress_report_every_ten_iterations_uses_valid_blind_rate_or_na(self) -> None:
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        development_log = (ROOT / "references" / "development-log.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Every tenth development iteration", validation)
        self.assertIn("stable generated-sample identification rate", validation)
        self.assertIn("placebo false-accusation rate", validation)
        self.assertIn("N/A - no valid blind package yet", validation)
        self.assertIn("do not substitute hard-gate pass rate, style-profile status, or a legacy small diagnostic round", validation)
        self.assertIn("Current active-protocol recognition rate: `N/A - no valid 8 impostor + 2 placebo blind package yet`", development_log)
        self.assertIn("after every ten development iterations", development_log)
        self.assertIn("Current active-protocol recognition rate is `N/A`", readme)

    def test_readme_reclassifies_iteration_164_after_named_rhythm_trace_fix(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        lowered = readme.lower()
        self.assertIn("iteration-164", lowered)
        self.assertIn("invalid-controller-evidence", lowered)
        self.assertIn("named rhythm", lowered)
        self.assertNotIn("latest bounded controller evidence remains process-valid but quality-invalid", lowered)

    def test_readme_routes_clean_placebo_calibration_back_to_source_formation(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("compact hard-pass/review experiment is now closed", readme)
        self.assertIn("style-profile remained `review` with punctuation/ngram drift", readme)
        self.assertIn("Stop repairing the same artifact", readme)
        self.assertIn("Targeted all-original calibration produced 0/2 raw and 0/2 stable false accusations", readme)
        self.assertIn("did not reproduce punctuation/ngram as an accusation cue", readme)
        self.assertIn("calibration-only and does not validate the generated draft", readme)
        self.assertIn("does not count toward the formal `8 impostor + 2 placebo` readiness package", readme)
        self.assertIn("bounded source formation", readme)
        self.assertIn("Do not change profile thresholds from this result", readme)

    def test_route_coverage_matrix_uses_stable_owner_anchors(self) -> None:
        matrix = (ROOT / "references" / "route-coverage-matrix.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        self.assertIn("stable owner files and short evidence anchors", matrix)
        self.assertIn("Current target status: not proven", matrix)
        self.assertIn("Missing owner rows: 0", matrix)
        self.assertIn("Do not load this file during ordinary article generation", matrix)
        self.assertIn("route/information-loss tests should verify the correct owner file or stage", matrix)
        self.assertNotRegex(matrix, r"\bLines? \d")
        self.assertNotIn("remaining test failures", matrix)
        self.assertNotIn("3 remaining", matrix)
        self.assertIn("references/anlin-collage-source-model.md", matrix)
        self.assertNotIn("references/standard-diary-source-engine.md", matrix)
        self.assertIn("refusal may be one fragment", matrix)
        self.assertIn("route-coverage-matrix.md", readme)
        self.assertIn("route-coverage-matrix.md", layer_map)
        self.assertIn("developer audit documents", layer_map)
        self.assertIn("references/anlin-collage-source-model.md", readme)
        self.assertNotIn("add `references/standard-diary-source-engine.md` for standard diary", readme)
        self.assertNotIn("standard-diary-source-engine.md # compact standard-diary middle engine", readme)

        owner_anchors = {
            "SKILL.md": [
                "Do not claim real authorship, provenance, or indistinguishability",
                "Artifact-Backed Entry Contract",
                "first prose artifact",
                "Do not write generated articles into the skill directory",
                "A present marker overrides \"write an article\"",
                "Ask at most one intake round",
                "Short-genre profile fallback is not strong evidence",
            ],
            "references/runtime-brief.md": [
                "Clean-eval misroute guard",
                "stop using this file before drafting",
                "clean-eval-first-draft-minimum.md` owns the first-draft source loop",
            ],
            "references/anti-ai-slop.md": [
                "Clean-eval misroute guard",
                "stop using this file before drafting",
                "Do not keep reading this file as a negative checklist",
            ],
            "references/clean-eval-first-draft-minimum.md": [
                "Use whichever relationships the movement earns",
                "refusal",
            ],
            "references/anlin-collage-source-model.md": [
                "causal movement is allowed but optional",
                "An invitation or refusal may be one fragment",
            ],
            "references/finalized-repair-minimum.md": [
                "first write to `draft.md` must be the final complete revision",
                "Do not write the old draft back as a placeholder",
            ],
            "references/validation-protocol.md": [
                "8 impostor + 2 placebo",
                "without `--repair-brief` for the full report",
            ],
            "README.md": [
                "Current active-protocol recognition rate is `N/A`",
                "runtime instructions should stay model-agnostic",
            ],
        }
        for relative_path, anchors in owner_anchors.items():
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn(relative_path, matrix)
            for anchor in anchors:
                self.assertIn(anchor, text)
                self.assertIn(anchor, matrix)

    def test_architecture_convergence_plan_is_developer_only_and_current(self) -> None:
        plan = (ROOT / "references" / "architecture-convergence-plan.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        clean_eval = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        finalized = (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8")

        self.assertIn("developer-facing convergence plan", plan)
        self.assertIn("Do not load it during ordinary article generation", plan)
        self.assertIn("Current recognition-rate evidence is still unchanged", plan)
        self.assertIn("Maintain `references/route-coverage-matrix.md`", plan)
        self.assertNotIn("18 failures", plan)
        self.assertNotIn("2 errors", plan)
        self.assertNotIn("358 tests", plan)

        self.assertIn("architecture-convergence-plan.md", readme)
        self.assertIn("architecture-convergence-plan.md", layer_map)
        self.assertIn("route-coverage, or architecture-convergence files", readme)
        self.assertNotIn("architecture-convergence-plan.md", clean_eval)
        self.assertNotIn("architecture-convergence-plan.md", finalized)

    def test_clean_eval_marker_priority_and_reference_misroute_guards(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        anti_ai = (ROOT / "references" / "anti-ai-slop.md").read_text(encoding="utf-8")
        matrix = (ROOT / "references" / "route-coverage-matrix.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Clean-eval mode has priority over ordinary article wording", skill)
        self.assertIn("before deciding ordinary mode", skill)
        self.assertIn("A present marker overrides \"write an article\"", skill)
        self.assertIn("use only after clean-eval mode has been ruled out", skill)
        self.assertIn("normal checker because it contaminates the bounded source-guidance measurement", skill)

        for text in (runtime, anti_ai):
            self.assertIn("Clean-eval misroute guard", text)
            self.assertIn("if `.anlin-clean-eval-mode` exists", text)
            self.assertIn("have not yet checked that marker", text)
            self.assertIn("stop using this file before drafting", text)
            self.assertIn("load `references/clean-eval-first-draft-minimum.md`", text)
            self.assertIn("references/anlin-collage-source-model.md", text)
            self.assertNotIn("references/standard-diary-source-engine.md", text)

        self.assertIn("clean-eval-first-draft-minimum.md` owns the first-draft source loop", runtime)
        self.assertNotIn("clean-generation-brief.md` owns the first-draft source loop", runtime)
        self.assertIn("Clean-eval marker priority over ordinary article wording", matrix)
        self.assertIn("Misloaded runtime/anti-slop references return to minimum route", matrix)
        self.assertIn("Mixed preflight repair order", matrix)
        self.assertIn("source/content blockers before `rebalance_line_rhythm.py`", matrix)
        self.assertIn("Post-check preflight before checker call 2/2", matrix)
        self.assertIn("CLEAN_RUN_POSTCHECK_PREFLIGHT", matrix)
        self.assertIn("Total constraints tracked: 51", matrix)
        self.assertIn("Ordinary runtime article generation", readme)
        self.assertIn("Formal clean-eval first draft", readme)
        self.assertIn("references/runtime-brief.md", readme)
        self.assertIn("references/clean-eval-first-draft-minimum.md", readme)

    def test_active_clean_eval_contract_requires_separate_marker_then_cwd_action(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        minimum = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for text in (skill, minimum, runtime):
            self.assertIn("two separate tool actions", text)
            self.assertIn("standalone `Get-Location` / `pwd`", text)
            self.assertIn("before any reference read, glob/path probe, or draft write", text)
            self.assertIn("controller `--dir`", text)
        self.assertNotIn("Test-Path .anlin-clean-eval-mode; Get-Location", skill)
        self.assertLess(
            readme.index("Check `.anlin-clean-eval-mode`"),
            readme.index("Load `references/clean-eval-first-draft-minimum.md`"),
        )

    def test_clean_eval_contract_names_direct_marker_probe(self) -> None:
        texts = [
            (ROOT / "SKILL.md").read_text(encoding="utf-8"),
            (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8"),
            (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8"),
            (ROOT / "README.md").read_text(encoding="utf-8"),
        ]

        for text in texts:
            self.assertIn('Test-Path -LiteralPath ".anlin-clean-eval-mode"', text)
            self.assertIn("a directory listing that merely shows the filename is not a marker check", text.lower())

    def test_scattered_source_contract_de_linearizes_linear_prompts(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        minimum = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        collage = (ROOT / "references" / "anlin-collage-source-model.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        matrix = (ROOT / "references" / "route-coverage-matrix.md").read_text(encoding="utf-8")

        for text in (skill, minimum, collage, runtime):
            lowered = text.lower()
            self.assertIn("punctuation-bearing movement units", lowered)
            self.assertIn("a line break does not remove punctuation", lowered)
            self.assertIn("naked caption rows are not breathing rows", lowered)
            self.assertIn("do not split every sentence into its own line", lowered)
            self.assertIn(
                "keep short clauses attached to the action, reply, object, or thought they complete",
                lowered,
            )
            self.assertIn("punctuation inside a long row is not lineation", lowered)
            self.assertIn(
                "when the next row completes the same movement, let the previous row keep the natural comma or unfinished landing",
                lowered,
            )
            self.assertIn("do not hide every continuation inside long prose rows", lowered)
            self.assertIn("do not seal every visible row with a period", lowered)
            self.assertIn("fragment slate", lowered)
            self.assertIn("independent thought-turn", lowered)
            self.assertIn("day-shaped collage", lowered)
            self.assertNotIn("split multi-turn paragraphs into breathing rows before writing", lowered)
            self.assertNotIn("a movement unit may occupy one or several uneven rows", lowered)

        for text in (minimum, collage, runtime, clean):
            lowered = text.lower()
            self.assertIn("a prompt's sequence is a fact constraint, not the article's outline", lowered)
            self.assertIn("start with a non-prompt fragment before the prompt surface", lowered)
            self.assertIn("after the prompt fragment, leave it for an independent thought-turn", lowered)
            self.assertIn("a thought-turn is not a paragraph", lowered)
            self.assertIn("observation, crooked read, and next move", lowered)
            self.assertIn("a rhythm script cannot invent missing source movement", lowered)
            self.assertIn("a complete standard diary is a day-shaped collage, not a premise summary", lowered)
            self.assertIn("if the body only has the prompt surface, one memory, and a final reply, it is a sketch", lowered)
            self.assertIn("continue through another independent thought-turn before the required residue", lowered)
        self.assertIn("prompt sequence is not the article's outline", matrix)

    def test_postcheck_preflight_contract_keeps_submission_read_only(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        clean_brief = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        matrix = (ROOT / "references" / "route-coverage-matrix.md").read_text(encoding="utf-8")

        self.assertIn("The wrapper does not rewrite `draft.md`", skill)
        self.assertIn("If the output contains only shape findings, do not add material", skill)
        self.assertIn("If the output is shape-only, do not add material", first_draft)
        self.assertIn("known underbuilt source or hard shape failure", clean_brief)
        self.assertIn("Pure shape findings permit only the named local rhythm action and no new material", clean_brief)
        self.assertIn("known underbuilt source or hard shape failure", runtime)
        self.assertIn("The wrapper does not rewrite `draft.md`", runtime)
        self.assertNotIn("Treat it as a source-rewrite stop sign before the final checker", runtime)
        self.assertIn("known underbuilt source or hard shape failure", validation)
        self.assertIn("byte-read-only wrapper", matrix)

    def test_readme_uses_portable_skill_and_corpus_paths(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("<skill-dir>", readme)
        self.assertIn("<corpus-dir>", readme)
        self.assertIn("ANLIN_CORPUS_DIR", readme)
        self.assertIn("distributable skill does not require every user to own the 38 original articles", readme)
        self.assertNotIn(r"C:\Users\34025", readme)
        self.assertNotIn(r"skills\Anlin", readme)
        self.assertNotIn("Claude Code", readme)
        self.assertIn("not yet proven", readme)

    def test_validation_protocol_uses_portable_skill_and_corpus_paths(self) -> None:
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        self.assertIn("<skill-dir>", validation)
        self.assertIn("<corpus-dir>", validation)
        self.assertIn("ANLIN_CORPUS_DIR", validation)
        self.assertIn("The distributable skill is usable without a local copy of the 38 originals", validation)
        self.assertIn("OPENCODE_DISABLE_EXTERNAL_SKILLS", validation)
        self.assertIn("other than the recorded `<skill-dir>`", validation)
        self.assertNotIn(r"C:\Users\34025", validation)
        self.assertNotIn(r"C:\Users\34025\.claude\skills\anlin-writing", validation)

    def test_distributable_files_do_not_embed_local_machine_paths(self) -> None:
        checked_roots = [ROOT / "README.md", ROOT / "SKILL.md", ROOT / "references", ROOT / "evals", ROOT / "scripts"]
        offenders: list[str] = []
        for root in checked_roots:
            paths = [root] if root.is_file() else list(root.rglob("*"))
            for path in paths:
                if not path.is_file():
                    continue
                if path.suffix.lower() not in {".md", ".py", ".json"}:
                    continue
                text = path.read_text(encoding="utf-8")
                local_path_markers = (
                    "C:\\Users\\",
                    "C:/Users/",
                    "Desktop\\Anlin",
                    "Desktop/Anlin",
                    ".claude\\skills\\anlin-writing",
                    ".codex\\skills",
                    ".codex/skills",
                )
                if any(marker in text for marker in local_path_markers):
                    offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_voice_model_summary_does_not_use_must_include_recipe(self) -> None:
        voice = (ROOT / "references" / "voice-model.md").read_text(encoding="utf-8")
        self.assertNotIn("写作必含", voice)
        self.assertNotIn("每篇至少三种", voice)
        self.assertNotIn("按 §8.6 迭代机制修复所有违规后才输出", voice)
        self.assertIn("高价值候选，不是必含配方", voice)
        self.assertIn("不要把背景、游戏、平台、熟人或身体标签当配料", voice)

    def test_self_check_respects_clean_eval_boundaries(self) -> None:
        self_check = (ROOT / "references" / "self-check.md").read_text(encoding="utf-8")
        self.assertIn("clean-eval 例外", self_check)
        self.assertIn("两次 `clean_run_checker.py` 上限", self_check)
        self.assertIn("不允许因为 warning 或普通 error 继续第三次写稿/第三次检查", self_check)
        self.assertIn("clean-eval 不使用无限循环", self_check)

    def test_short_sincere_prompt_prop_gate_is_source_guidance_not_only_checker(self) -> None:
        files = [
            ROOT / "SKILL.md",
            ROOT / "references" / "clean-generation-brief.md",
            ROOT / "references" / "runtime-brief.md",
            ROOT / "references" / "generation-modes.md",
            ROOT / "references" / "feature-budget.md",
            ROOT / "references" / "runtime-layer-map.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        self.assertIn("present-action anchor", combined)
        self.assertIn("no universal short character or line corridor", combined)
        self.assertIn("Do not impose a fixed opening line count", clean)
        self.assertIn("poem-shaped grid", combined)
        self.assertIn("short_genre_prompt_prop_too_early", clean)
        self.assertIn("short_genre_main_prop_title_loop", checker)
        self.assertIn("short_genre_period_grid", checker)
        self.assertIn("many sealed `。` rows", runtime.lower())
        self.assertIn("closed sentence rows", checker)
        self.assertIn("source reset must choose a new side-action title", layer_map)
        self.assertIn("sentence-row normalization", layer_map)
        self.assertNotIn("650-850 body Chinese characters", clean)
        self.assertNotIn("520-649", combined)

    def test_standard_prompt_prop_loop_is_source_guidance_not_only_checker(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        budget = (ROOT / "references" / "feature-budget.md").read_text(encoding="utf-8")
        layer = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, budget, layer])
        self.assertIn("标准日寄提示物标题闭环", combined)
        self.assertIn("standard_prompt_prop_title_loop", combined)
        self.assertIn("备注", combined)
        self.assertIn("香菜", combined)
        self.assertIn("source reset", combined.lower())
        self.assertIn("side consequence", combined)
        self.assertIn("door/hallway", combined)
        self.assertIn("not a retitle-only patch", combined)
        self.assertIn("do not let food/body texture become the new loop", runtime)
        self.assertIn("fragment slate", clean)
        self.assertIn("period-row", clean)
        self.assertIn("Choose after the body exists", clean)
        self.assertIn("read `draft.md` once, and output that exact article", skill)

    def test_standard_diary_carrier_release_is_source_guidance_not_background_quota(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        layer = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, layer, checker])

        self.assertIn("deleting it would break", clean)
        self.assertIn("Background is a contradiction boundary, not a content quota", skill)
        self.assertIn("fragment slate", combined)
        self.assertIn("decoration rather than paragraph engine", clean)
        self.assertIn("Layer 2 contradiction gates", layer)
        self.assertIn("source reset: replace the earliest overloaded fragment or relation in place", checker)
        self.assertIn("inactive historical reference", engine.lower())
        self.assertIn("active standard generation uses", engine.lower())
        self.assertNotIn("release the current person/place/transaction/object carrier after one consequence transfer", combined)
        self.assertNotIn("source reset: rebuild 2-3 load-bearing action clusters", checker)

    def test_standard_diary_source_engine_is_layer0_not_repair_library(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")
        layer = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, layer])

        self.assertIn("anlin-collage-source-model.md", clean)
        self.assertIn("Inactive Historical Reference", engine)
        self.assertIn("not an active clean-eval or ordinary-runtime source guide", engine)
        self.assertIn("active standard generation uses `clean-eval-first-draft-minimum.md` plus `anlin-collage-source-model.md`", engine.lower())
        self.assertIn("fragment slate", combined)
        self.assertNotIn("standard-diary-source-engine.md", clean)
        self.assertNotIn("side engine", combined.lower())
        self.assertNotIn("public hinge", combined.lower())
        self.assertNotIn("off-axis residue", combined.lower())
        self.assertNotIn("deepseek", engine.lower())
        self.assertNotIn("mimo", engine.lower())
        self.assertNotIn("minimax", engine.lower())
        self.assertNotIn("gpt", engine.lower())

    def test_bounded_source_formation_avoids_kernel_packets_and_inventory_texture(self) -> None:
        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")

        self.assertIn("fragment slate", first_draft)
        self.assertIn("Do not compress amounts, reply candidates, or object choices into an `A、B、C` inventory", first_draft)
        self.assertIn("let one plain action/object phrase return unchanged", first_draft)
        self.assertIn("not a decorative refrain or repetition quota", first_draft)
        # The old engine file still has the overlapping-functions text
        self.assertIn(
            "The three functions may overlap; they are not three scene modules, paragraph slots, or proof packets",
            engine,
        )
        # But first_draft now uses the fragment model instead
        self.assertNotIn(
            "The three functions may overlap; they are not three scene modules, paragraph slots, or proof packets",
            first_draft,
        )

        self.assertIn("Do not allocate one period to each line or cluster", first_draft)
        self.assertIn("Do not allocate one period to each line or cluster", engine)
        self.assertIn("Do not compress amounts, reply candidates, or object choices into an `A、B、C` inventory", engine)
        self.assertIn("let one plain action/object phrase return unchanged", engine)
        self.assertIn("not a decorative refrain or repetition quota", engine)

        self.assertNotIn("Then choose three consequence kernels", first_draft)
        self.assertNotIn("choose three private consequence kernels", engine)
        self.assertNotIn("Each kernel needs enough visible movement", engine)

    def test_carrier_release_replaces_additive_repair_for_iteration_147_failure(self) -> None:
        messages = [
            "body_chinese_chars=846 < 900",
            "medium_short_line_grid=present (long_lines=2 < 6, line_stdev=5.9; rewrite rough action/speech/thought lines before checking)",
            "paragraph_engine=weak (source reset: rebuild 2-3 load-bearing action clusters that change reply/body/route/payment/room/social position; do not inspect checker source/tests)",
            "quoted_dialogue=present count=1 examples=L35:我看着“不算你”三个字，收银员又问了一遍，",
            "soft_witness_no_consequence=present count=1 examples=L39:她看了我一眼，叫旁边的人过来输密码取消，",
        ]
        repair_hints, revision_frame = build_preflight_guidance(messages)
        guidance = " | ".join([revision_frame, *repair_hints])

        self.assertIn("replace the earliest broken fragment or relation in place", guidance)
        self.assertNotIn("release the current person/place/transaction/object carrier after one consequence transfer", guidance)
        self.assertIn("preserve the complete article across the replacement and neighboring existing movements", guidance)
        self.assertNotIn("rebuild 2-3 load-bearing action clusters", guidance)
        self.assertNotIn("include one off-axis consequence and one rough body/social turn", guidance)
        self.assertNotIn("add one full off-axis life cluster", guidance)

        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        finalized = (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        # The old carrier-release language is retained only in the inactive historical file.
        for text in (engine,):
            self.assertIn("A carrier is the combined person/place/transaction/object chain", text)
            self.assertIn("Multiple diagnostic labels may describe the same single consequence transfer", text)
            self.assertIn("After one consequence transfer, release that carrier", text)
            self.assertIn("cashier, rider, counter, payment, or object chain", text)
        # first_draft now uses the fragment slate model instead
        self.assertIn("fragment slate", first_draft)
        self.assertNotIn("A carrier is the combined person/place/transaction/object chain", first_draft)
        self.assertNotIn("One moving chain may carry side engine and public hinge at once", first_draft)
        self.assertNotIn("may carry more than one function", engine)
        self.assertNotIn("Let one chain carry more than one job", engine)
        self.assertNotIn("A public hinge should open a second consequence", engine)
        self.assertNotIn("Add one off-axis life cluster", clean)
        self.assertNotIn("add one off-axis consequence and one rough body/social turn", clean)
        self.assertNotIn("Add one active consequence cluster", finalized)
        self.assertNotIn("add one active consequence cluster", finalized)
        self.assertIn("source reset: replace the earliest overloaded fragment or relation in place", checker)
        self.assertNotIn("source reset: rebuild 2-3 load-bearing action clusters", checker)

    def test_standard_underbuilt_guidance_keeps_severe_and_replacement_boundaries_exclusive(self) -> None:
        cases = [
            (
                649,
                "body_chinese_chars=649 < 900",
                "do a whole-source rebuild",
                "preserve a complete article",
            ),
            (
                650,
                "body_chinese_chars=650 < 900",
                "replace one repeated or overloaded relation in place",
                "preserve the complete article across the replacement and neighboring existing movements",
            ),
            (
                899,
                "body_chinese_chars=899 < 900",
                "replace one repeated or overloaded relation in place",
                "preserve the complete article across the replacement and neighboring existing movements",
            ),
            (
                900,
                "body_chinese_chars=900 < 950 with source_shape_weak",
                "replace one repeated or overloaded relation in place",
                "preserve complete article",
            ),
        ]

        for body_chars, body_message, route_text, mass_text in cases:
            with self.subTest(body_chars=body_chars):
                repair_hints, revision_frame = build_preflight_guidance(
                    [
                        body_message,
                        "connectors=[] < 3",
                        "paragraph_engine=weak (source reset required)",
                    ]
                )
                guidance = " | ".join([revision_frame, *repair_hints])
                self.assertIn(route_text.lower(), guidance.lower())
                self.assertIn(mass_text.lower(), guidance.lower())
                if body_chars < 650:
                    self.assertNotIn("for a near-miss short draft", guidance)
                    self.assertNotIn("replace one decorative packet", guidance)
                    self.assertNotIn("across the replacement", guidance)
                else:
                    self.assertNotIn("whole-source rebuild", guidance)

    def test_standard_underbuilt_length_routes_without_extra_source_labels(self) -> None:
        cases = [
            (
                ["body_chinese_chars=649 < 900"],
                "do a whole-source rebuild",
                "preserve a complete article",
            ),
            (
                ["body_chinese_chars=649 < 900", "connectors=[] < 3"],
                "do a whole-source rebuild",
                "preserve a complete article",
            ),
            (
                ["body_chinese_chars=650 < 900"],
                "replace one repeated or overloaded relation in place",
                "preserve the complete article across the replacement and neighboring existing movements",
            ),
            (
                ["body_chinese_chars=899 < 900", "connectors=[] < 3"],
                "replace one repeated or overloaded relation in place",
                "preserve the complete article across the replacement and neighboring existing movements",
            ),
            (
                ["body_chinese_chars=913 < 950 with source_shape_weak"],
                "replace one repeated or overloaded relation in place",
                "preserve complete article",
            ),
        ]

        for messages, route_text, mass_text in cases:
            with self.subTest(messages=messages):
                repair_hints, revision_frame = build_preflight_guidance(messages)
                guidance = " | ".join([revision_frame, *repair_hints])
                self.assertIn(route_text.lower(), guidance.lower())
                self.assertIn(mass_text.lower(), guidance.lower())
                self.assertNotIn("for a near-miss short draft", guidance)
                self.assertNotIn("Replace one inert connector-bearing movement", revision_frame)

    @unittest.skip("superseded by the active fragment-contract regression tests")
    def test_carrier_release_removes_additive_runtime_quotas_and_shape_templates(self) -> None:
        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")
        finalized = (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        hard_checker = (ROOT / "scripts" / "check_anlin_violations.py").read_text(encoding="utf-8")
        repair_controller = (ROOT / "scripts" / "prepare_finalized_repair_brief.py").read_text(encoding="utf-8")
        style_checker = (ROOT / "scripts" / "check_style_profile.py").read_text(encoding="utf-8")

        self.assertIn("These functions are diagnostic lenses, not separate content slots", clean)
        self.assertIn("Blind-judge angles are review lenses, not pre-draft content requirements", runtime)
        self.assertIn("Use whichever relationships the movement earns", first_draft)
        self.assertIn("If neither exists, this is not a missing ingredient", engine)
        self.assertIn("Choose only the smallest local movement that is actually broken", engine)
        self.assertIn("Choose only the relation the current movement earns", engine)
        self.assertIn("choose only the smallest unfinished action spot that is actually broken", runtime)
        self.assertIn("repair only the smallest local movement that is actually broken", checker)
        self.assertIn("choose the one relation that movement actually needs", checker)
        self.assertIn("restore whichever single relation that movement earns", repair_controller)
        self.assertIn("neighboring existing movements", repair_controller)
        self.assertIn("Repair only the smallest existing movement that is actually broken", style_checker)
        self.assertIn("只修最小的真实坏点", hard_checker)
        self.assertIn("Do not repeat a comma/long-row/short-drop template across clusters", finalized)
        self.assertIn("preserve the existing page shape and untouched rows", finalized)
        self.assertIn("repair only the smallest existing movement that is actually broken", finalized)
        self.assertNotIn("rebuild page shape first", finalized)
        self.assertNotIn("should usually become 6-8 visible breathing clusters", finalized)
        self.assertIn("neighboring existing movements", checker)
        self.assertIn("Below 650 body Chinese characters, rebuild the incomplete source", clean)
        self.assertIn("replace the earliest underdeveloped fragment or relation", clean)

        for text in (clean, runtime, engine, finalized, checker):
            self.assertNotIn("inside that replacement", text)
            self.assertNotIn("inside the replacement", text)

        self.assertNotIn("Add one off-axis branch", clean)
        self.assertNotIn("Give the middle one off-axis branch", clean)
        self.assertNotIn("one crooked misread or system joke", clean)
        self.assertNotIn("two small residues that do not summarize the theme", clean)
        self.assertNotIn("add one full off-axis life cluster", clean)
        self.assertNotIn("add one outside contact before the first `draft.md`", clean)
        self.assertNotIn("scene slate must satisfy all four gates", runtime)
        self.assertNotIn("gates 2 and 3 are not optional", runtime)
        self.assertNotIn("at least four selected scenes should be non-plain", runtime)
        self.assertNotIn("Pick 3-5 places", engine)
        self.assertNotIn("each cluster should have multiple actual body lines, an unfinished action/reply/body/payment/object movement, one rougher line", first_draft)
        self.assertNotIn("Every cluster must contain an unfinished action question", first_draft)
        self.assertNotIn("In most clusters, at least one visible row should be long", engine)
        self.assertNotIn("Write clusters like this in the article", engine)
        self.assertNotIn("but it also needs hard-stop action lines and a few short failure drops", engine)
        for text in (first_draft, clean, runtime, engine, finalized, checker):
            self.assertNotIn("choose 3-5", text.lower())
        self.assertNotIn("one unfinished reply/payment/body line may trail with a comma", repair_controller)
        self.assertNotIn("refusal-coupled consequence cluster", repair_controller)
        self.assertNotIn("Choose a few existing", style_checker)
        self.assertNotIn("some lines continue through real movement, some land with hard stops, and a few short drops", style_checker)
        self.assertNotIn("rebuild the visible body as 6-8 line-broken clusters", style_checker)
        self.assertNotIn("a continuing action can end with `，`, a longer line should carry real movement or speech, and a short drop should land a consequence", checker)
        self.assertNotIn("再补一条有后果的长动作", hard_checker)
        self.assertNotIn("另一些行用硬停顿或短落点", hard_checker)
        self.assertNotIn("再补少数真正较长的行动句", hard_checker)
        self.assertNotIn("Expand with action, dialogue, body/material pressure, and useless daily residue", runtime)
        self.assertNotIn("replace it with a concrete action or off-axis residue", runtime)
        self.assertNotIn("Repeat this across several clusters", finalized)

    def test_source_contract_uses_fragment_slate_not_carrier_engine(self) -> None:
        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")

        self.assertIn("fragment slate", first_draft)
        self.assertNotIn(
            "Carrier release is local: the article still needs several distinct action transfers",
            first_draft,
        )
        # The old engine file still contains the carrier-release language
        self.assertIn("Carrier release is local: the article still needs", engine)

    def test_calibrate_style_profile_help_does_not_raise_on_percent(self) -> None:
        import subprocess

        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "calibrate_style_profile.py"), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertNotIn("ValueError", proc.stderr)

    def test_connector_only_postcheck_guidance_replaces_existing_movement_without_addition(self) -> None:
        repair_hints, revision_frame = build_preflight_guidance(
            ["connectors=['其实', '觉得', '发现'] < 5 before checker_call_2"]
        )
        guidance = " | ".join([revision_frame, *repair_hints])

        self.assertIn("Replace one inert connector-bearing fragment relation inside the existing slate", guidance)
        self.assertIn("change what an existing action does next", guidance)
        self.assertNotIn("add concrete action/body/social/off-axis material", guidance)
        self.assertIn("Do not add a new scene", guidance)

    def test_connector_only_postcheck_output_stays_local_not_underbuilt_or_refusal_specific(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("# 门口\n\n其实我把门关了一半。", encoding="utf-8")
            state_path = draft.parent / ".anlin-clean-run-state.json"
            state = {"draft": str(draft.resolve()), "calls": 1, "preflights": 1, "snapshots": {}}
            connector_message = "connectors=['其实', '觉得', '发现'] < 5 before checker_call_2"

            with (
                mock.patch("clean_run_checker.preflight_messages", return_value=[]),
                mock.patch("clean_run_checker.post_checker_blocking_messages", return_value=[connector_message]),
                redirect_stdout(io.StringIO()) as output,
            ):
                blocked, messages = post_checker_preflight_before_second_check(
                    draft,
                    state,
                    state_path=state_path,
                    calls=1,
                )

            guidance = output.getvalue()
            self.assertTrue(blocked)
            self.assertEqual(messages, [connector_message])
            self.assertIn("CLEAN_RUN_POSTCHECK_PREFLIGHT", guidance)
            self.assertIn("Replace one inert connector-bearing fragment relation", guidance)
            self.assertNotIn("known underbuilt source", guidance)
            self.assertNotIn("person/place/transaction/object carrier", guidance)
            self.assertNotIn("social-decline or invitation", guidance)
            self.assertNotIn("refusal-coupled", guidance)

    def test_clean_eval_source_reads_handoff_directly_to_artifact_write(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        for text in (first_draft,):
            lowered = text.lower()
            self.assertIn(
                "after the minimal source reads finish, the next tool action must be one complete write to relative `draft.md`",
                lowered,
            )
            self.assertIn("do not spend another model turn comparing openings", lowered)
            self.assertIn("choose the first workable fragment slate", lowered)
            self.assertIn("an unwritten better plan is not evidence", lowered)

    def test_punctuation_pendulum_is_source_guidance_not_only_checker(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")
        profile = (ROOT / "scripts" / "check_style_profile.py").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "check_anlin_violations.py").read_text(encoding="utf-8")
        clean_run = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, engine, profile, checker, clean_run])

        self.assertIn("Punctuation Pendulum Guard", engine)
        self.assertIn("comma-drag", combined)
        self.assertIn("period-row grid", combined)
        self.assertIn("标准日寄句号网格", combined)
        self.assertIn("punctuation_source_reset", profile)
        self.assertIn("Choose only the smallest local movement that is actually broken", engine)
        self.assertIn("restore whichever relation the action earns", engine)
        self.assertIn("not all of them", engine)
        self.assertIn("local cluster surgery", combined)
        self.assertIn("do not globally merge rows into comma chains", combined)
        self.assertIn("delete explanation tails", combined)
        self.assertIn("do not swing", combined.lower())
        self.assertNotIn("deepseek", engine.lower())
        self.assertNotIn("mimo", engine.lower())
        self.assertNotIn("minimax", engine.lower())

    def test_social_decline_refusal_aftermath_is_layer0_source_kernel(self) -> None:
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        collage = (ROOT / "references" / "anlin-collage-source-model.md").read_text(encoding="utf-8")
        engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")

        active = "\n".join([clean, runtime, collage])
        self.assertIn("An invitation or refusal may be one fragment", collage)
        self.assertIn("do not default to", collage.lower())
        self.assertIn("one fragment among memories", runtime)
        self.assertIn("explicit cross-day expansion", runtime)
        self.assertIn("refusal-coupled consequence only when", clean)
        self.assertNotIn("one load-bearing kernel must be the refusal aftermath itself", active)
        self.assertNotIn("at least one later cluster should be driven by the refusal aftermath itself", active)
        self.assertIn("message -> ticket -> money -> refusal -> same-night consequence", active)
        self.assertIn("inactive historical reference", engine.lower())
        self.assertNotIn("standard-diary-source-engine.md", runtime)

    def test_clean_eval_rhythm_repair_order_is_unambiguous_in_runtime_docs(self) -> None:
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        self.assertIn("Any later `Write draft.md`, `Edit draft.md`, `Set-Content`, or `Out-File` cancels", clean)
        self.assertIn("Reading the file, thinking about the repair, or visually deciding the rhythm looks okay does not refresh it", clean)
        self.assertIn("节奏脚本后重写未重跑节奏修复", (ROOT / "scripts" / "check_clean_eval_trace.py").read_text(encoding="utf-8"))

    def test_runtime_docs_use_current_skill_name_and_output_locations(self) -> None:
        files = [
            ROOT / "README.md",
            ROOT / "SKILL.md",
            ROOT / "references" / "clean-generation-brief.md",
            ROOT / "references" / "runtime-brief.md",
            ROOT / "references" / "runtime-layer-map.md",
            ROOT / "references" / "validation-protocol.md",
            ROOT / "evals" / "README.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
        self.assertNotIn("Anlin Skill", combined)
        self.assertNotIn("Anlin skill", combined)
        self.assertNotIn("formal clean-run", combined)
        self.assertNotIn("formal clean generation", combined)
        self.assertNotIn("正式 clean-run", combined)
        self.assertNotIn("evals/outputs", combined)
        self.assertNotIn("maintainer", combined.lower())
        self.assertIn("anlin-writing", combined)
        self.assertIn("<eval-workspace>/iteration-<n>/eval-<id>/draft.md", combined)
        self.assertIn("Do not write generated articles into the skill directory", combined)

    @unittest.skip("superseded by fragment-source ownership and mode-boundary regression tests")
    def test_runtime_docs_distinguish_clean_eval_from_ordinary_use(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        finalized_minimum = (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8")
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        eval_readme = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        finalized_combined = "\n".join([skill, runtime, finalized_minimum, validation])
        generator_facing_finalized = "\n".join([skill, runtime, finalized_minimum])
        self.assertIn("Ordinary user mode", skill)
        self.assertIn("Clean-eval mode", skill)
        self.assertIn(".anlin-clean-eval-mode", skill)
        self.assertIn(".anlin-clean-eval-mode", validation)
        self.assertIn("the checker loop may continue until hard errors are cleared", clean)
        self.assertIn("The two-call stop rule belongs to clean-eval only", clean)
        self.assertIn("CLEAN_RUN_PREFLIGHT_STOP", skill)
        self.assertIn("CLEAN_RUN_PREFLIGHT_STOP", clean)
        self.assertIn("CLEAN_RUN_PREFLIGHT_STOP", runtime)
        self.assertIn("FINAL BOUNDARY", clean)
        self.assertIn("do not write `draft.md`, do not repair", runtime)
        self.assertIn("The next tool action must be reading the current `draft.md`", clean)
        self.assertIn("Do not switch to ordinary checker flow after the bounded stop", skill)
        self.assertIn("In any workspace containing `.anlin-clean-eval-mode`", skill)
        self.assertIn("use `clean_run_checker.py`, not the normal checker", skill)
        self.assertIn("check that marker", skill.lower())
        self.assertIn("First tool action must check the marker", skill)
        self.assertIn("Clean-eval mode", skill)
        self.assertIn("check the marker", skill.lower())
        self.assertIn("using relative `draft.md` or `.\\draft.md`", skill)
        self.assertIn("relative `draft.md` or `.\\draft.md`", skill)
        self.assertIn("Do not write `<skill-dir>/.../draft.md`", skill)
        self.assertIn("Use the relative path `draft.md` or `.\\draft.md`", clean)
        self.assertIn("Do not construct an absolute path from memory", clean)
        self.assertIn("`Get-Location` / `pwd` is mandatory before the first write", clean)
        self.assertIn("`<skill-dir>` is only for resolving bundled references and scripts", skill)
        self.assertIn("it must not appear in the article write path", clean)
        self.assertIn("Do not write `<skill-dir>/<iteration-or-case>/draft.md`", clean)
        self.assertIn("If `Get-Location` shows `<skill-dir>` or a path ending in `anlin-writing`, do not write", clean)
        self.assertIn("Draft in breathing clusters, not sentence rows", clean)
        self.assertIn("write the saved file as the broken article, not as paragraphs", clean)
        self.assertIn("the `content` being written must already visibly contain the line-broken body", clean)
        self.assertIn("it has become a stain ledger", (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8"))
        self.assertIn("bare caption rows are dangerous", clean)
        self.assertIn("16-25 dense rows", clean)
        self.assertIn("16-25 dense rows", (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8"))
        self.assertIn("Do not depend on `rebalance_line_rhythm.py`", (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8"))
        self.assertIn("below 900 body Chinese characters is usually not restrained", clean)
        self.assertIn("below 900 body Chinese characters is usually not restrained", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("Do not separate the witness and the ugly fact", clean)
        self.assertIn("Treat a silent witness as decoration", (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8"))
        self.assertIn("pain, heat, and fatigue alone are too polite", clean)
        self.assertIn("private case-report chain", runtime)
        self.assertIn("symptom -> search page -> refrigerator inventory -> room smell -> ambient sound", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("A phone message about meeting someone is still too private unless it changes action, route, social exposure", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("If the user gives `有人说痛风是富贵病`", runtime)
        self.assertIn("delete a whole packet before adding anything", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("This marker check should be the first tool action", clean)
        self.assertIn("Do not write `draft.md` until both the marker check and current-directory confirmation are visible in the run trace", clean)
        self.assertIn("marker check -> current-directory confirmation -> read `clean-eval-first-draft-minimum.md` -> for standard diary read `standard-diary-source-engine.md` -> write one complete `draft.md` -> run `clean_run_checker.py`", clean)
        self.assertIn("Do not rediscover this skill after it has already triggered", clean)
        self.assertIn("Do not rediscover this skill by globbing, `Test-Path`, listing parent skill directories", (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8"))
        self.assertIn("If a tool cannot resolve a bundled reference path", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("still persist `draft.md`", clean)
        self.assertIn("visible scratch article without `draft.md` is still a failed run", clean.lower())
        self.assertIn("The wrapper `clean_run_checker.py` is the only checker entrypoint", clean)
        self.assertIn("uses that printed result as the complete repair interface", clean)
        self.assertIn("without reading this file, inspecting checker source/tests, grepping thresholds", clean)
        self.assertIn("do not switch to `check_anlin_violations.py`", runtime)
        self.assertIn("Developer Two-Checkpoint Evaluation", validation)
        self.assertIn("Bounded clean-eval checkpoint", validation)
        self.assertIn("Finalized repair checkpoint", validation)
        self.assertIn("natural source guidance and limited checker-driven repair", validation)
        self.assertIn(".anlin-clean-run-snapshots", validation)
        self.assertIn("first-submission source guidance", validation)
        self.assertIn("stage snapshots", readme)
        self.assertIn("first_submission", eval_readme)
        self.assertIn("A clean finalized draft cannot retroactively make the bounded draft a success", validation)
        self.assertIn("Normal `check_anlin_violations.py draft.md` success is not sufficient", validation)
        self.assertIn("Do not start with plain `--strict` and treat a clean result as a pass", runtime)
        self.assertIn("controller reruns `check_anlin_violations.py draft.md --strict --draft-gate --genre <selected-genre>`", runtime)
        self.assertIn("A `revise` status means finalized repair failed", validation)
        self.assertIn("Style-profile `yellow` with zero errors is acceptable for the finalized checkpoint", validation)
        self.assertIn("style-profile `yellow` 可作为 finalized checkpoint 的通过条件之一", eval_readme)
        self.assertIn("它衡量自然引导能力加有限检查器修复能力", eval_readme)
        self.assertIn("不要只看“最后有没有修好”", eval_readme)
        self.assertIn("Zero red families is not enough", runtime)
        self.assertIn("roughly 45-70 non-empty body lines", runtime)
        self.assertIn("keep 4-7 uneven clusters", runtime)
        self.assertIn("A finalized `review` status still means the final article has unresolved risk", runtime)
        self.assertIn("avoid 30-line prose blocks", runtime)
        self.assertIn("controller validation then finds the same or opposite failures", finalized_minimum)
        self.assertIn("style-profile remains `revise`, or remains `review` with red `line_rhythm`", runtime)
        self.assertIn("independent drift families stay above the review threshold", runtime)
        self.assertIn("the finalized checkpoint is still not a pass", runtime)
        self.assertIn("Do not start with plain `--strict` and treat a clean result as a pass", runtime)
        self.assertIn("Replace private texture with a consequence", runtime)
        self.assertIn("thin the draft instead of decorating it", runtime)
        self.assertIn("not all four as a repeated cluster template", runtime)
        self.assertIn("references/finalized-repair-minimum.md", skill)
        self.assertIn("The controller records local validation as unresolved", finalized_minimum)
        self.assertIn("generator-facing minimum path", finalized_minimum)
        self.assertIn("write a complete `draft.md`", finalized_minimum)
        self.assertIn("Do not load `validation-protocol.md`, `development-log.md`, full style-profile reports", finalized_minimum)
        finalized_lines = [line for line in skill.splitlines() if "Finalized repair mode" in line]
        self.assertEqual(len(finalized_lines), 1)
        self.assertLess(len(finalized_lines[0]), 650)
        self.assertNotIn("YELLOW_REVIEW_FAMILY_THRESHOLD", generator_facing_finalized)
        self.assertNotIn("SOFT_REVISE_FAMILY_THRESHOLD", generator_facing_finalized)
        self.assertIn("`finalized=review` is not a clean final success", validation)
        self.assertIn("exits nonzero unless both checkpoints are ready for blind rounds", validation)
        self.assertIn("separate `finalized/` case directory", validation)
        self.assertIn("direct normal-checker use in that directory is a protocol violation", validation)
        self.assertIn("bounded failure with a finalized pass means source guidance should be strengthened", readme)
        self.assertIn("natural guidance plus limited checker-driven repair", readme)
        self.assertIn("finalized `review/fail/invalid` means the final article is still unresolved", readme)
        self.assertIn("blind_round_readiness", readme)
        self.assertIn("双检查点记录", eval_readme)
        self.assertIn("最终稿不能只凭普通检查器通过", eval_readme)
        self.assertIn("artifact failure", eval_readme)
        self.assertIn("terminal/log-only final prose is an artifact failure", layer_map.lower())
        summary_script = (ROOT / "scripts" / "summarize_dev_checkpoints.py").read_text(encoding="utf-8")
        self.assertIn("finalized draft unchanged from bounded input", summary_script)
        self.assertIn("Missing Draft Artifact", summary_script)
        self.assertIn("finalized 仍为 review/fail/invalid", eval_readme)
        self.assertIn("bounded clean-eval checkpoint", layer_map)
        self.assertIn("finalized repair checkpoint", layer_map)
        self.assertIn("normal checker success alone is not a finalized pass", layer_map)
        self.assertIn("finalized is only `review`, it is still unresolved", layer_map)
        self.assertIn("The repair agent must not run `check_anlin_violations.py`", layer_map)
        self.assertIn("read or grep checker source, tests, hidden threshold constants", layer_map)
        self.assertIn("must not run local gates, controller helpers, counters, path probes, source/test reads, threshold searches, or old-log searches", validation)
        self.assertIn("Generated articles do not belong in the skill directory", runtime)
        self.assertIn("Natural connector coverage should be solved before the checker", clean)
        self.assertIn("`connectors`: change what happens next so a turn is needed", finalized_minimum)
        self.assertIn("If the hard gate already passed and the brief only reports style-profile `review`", finalized_minimum)
        self.assertIn("A hard-gate pass with unresolved style drift is better evidence", finalized_minimum)
        self.assertIn("preserve the existing title source, people, invitation channel", finalized_minimum)
        self.assertIn("micro-cluster surgery", finalized_minimum)
        self.assertIn("do not add a new simile, analogy, or caption", finalized_minimum)
        self.assertIn("do not make line-final comma ratio zero", finalized_minimum)
        self.assertIn("Preserve working comma-ended continuation rows from the incoming draft", finalized_minimum)
        self.assertIn("line_ending_lock", finalized_minimum)
        self.assertIn("mass_floor_lock", finalized_minimum)
        self.assertIn("do not remove a functional consequence sentence unless you replace it inside the same local cluster", finalized_minimum)
        self.assertIn("If connector spread is thin, replace one inert observation", runtime)
        self.assertIn("do not append a connector scene or swap synonyms", runtime)
        self.assertIn("The reverse priority also matters", runtime)
        self.assertIn("do not clean the article into a new hard-gate failure", runtime)
        self.assertIn("do not change the premise", runtime)
        self.assertIn("If the brief reports `高频词覆盖不足`", runtime)
        self.assertIn("For 朋友圈, short-video, annual-summary, old-chat", runtime)
        self.assertIn("A feed is not a scene slate", runtime)
        self.assertIn("sealed story shape", runtime)
        self.assertIn("finish any content repair first", runtime)
        self.assertIn("For invitations, weddings, reunions", clean)
        self.assertIn("For stranger, shopkeeper, vendor", clean)
        self.assertIn("do not turn the encounter into a quoted transcript", clean)
        self.assertIn("first draft should usually contain zero quote marks", clean)
        self.assertIn("Do not let the stranger speak the prompt in a neat script", clean)
        self.assertIn("For stranger, shopkeeper, vendor", runtime)
        self.assertIn("Do not write five standalone quote lines", runtime)
        self.assertIn("caption metaphors that explain pressure for the reader", runtime)
        self.assertIn("one-screen chronology failure", runtime)
        self.assertIn("Do not turn many hard-stop lines into one huge comma chain", runtime)
        self.assertIn("Line-final comma means the visible content line itself ends with", clean)
        self.assertIn("A draft with many short rows and no visible punctuation is a generated line grid", runtime)
        self.assertIn("actual line endings, not comma count inside long lines", runtime)
        self.assertIn("--genre standard", clean)
        self.assertIn("generic family/screen surface does not reroute the article by accident", clean)
        self.assertIn("`逗号密度过高` means the repair has become comma-drag", runtime)
        self.assertIn("long lines made only by chaining clauses with commas", clean)
        self.assertIn("repair must not create semantic breaks", runtime)
        self.assertIn("FINALIZED_THRESHOLD_PROBE_RE", summary_script)
        self.assertIn("--finalized-trace-log", summary_script)

    def test_short_genre_repair_stuffing_is_source_guidance_not_only_checker(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        modes = (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8")
        budget = (ROOT / "references" / "feature-budget.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, modes, budget, layer_map])
        self.assertIn("Do not repair short sincere", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("Short sincere repair has a second overfill trap", clean)
        self.assertIn("Treat `短体裁修复堆新素材` the same way", runtime)
        self.assertIn("Mode C repair should not import a new inventory", modes)
        self.assertIn("No short-genre repair stuffing", budget)
        self.assertIn("repair stuffing", layer_map)
        self.assertIn("existing object/message/room/body/memory set", modes)
        self.assertIn("new material", combined)

    def test_short_sincere_present_anchor_requires_source_reset_not_local_patch(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        modes = (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8")
        budget = (ROOT / "references" / "feature-budget.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        review = (ROOT / "references" / "review-rubric.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, modes, budget, layer_map, review, checker])
        self.assertIn("short_genre_present_action_anchor", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("source reset", clean.lower())
        self.assertIn("When repairing `短真诚当前动作锚点不足`", runtime)
        self.assertIn("短真诚标题物件闭环", runtime)
        self.assertIn("source reset", modes)
        self.assertIn("No local patch for a failed sincere spine", budget)
        self.assertIn("No main-prop title loop in short sincere", budget)
        self.assertIn("source reset must choose a new side-action title", layer_map)
        self.assertIn("without replacing the old spine", review)
        self.assertIn("abandon the existing memory-first spine", checker)
        self.assertNotIn("add one current detail around the same spine", combined)

    def test_short_sincere_prop_budget_and_connector_sampler_are_source_guidance(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, checker])
        self.assertIn("cropped trace", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("childhood rain", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("a cropped trace means less than a scene", clean.lower())
        self.assertIn("childhood rain + raincoat + broken umbrella + school arrival", clean)
        self.assertIn("do not mistake compression for deletion", runtime)
        self.assertIn("connector sampler", clean)
        self.assertIn("connector sampler", clean)
        self.assertIn("Keep one visible pressure family", checker)
        self.assertNotIn("keep all three family props briefly", combined)

    def test_title_model_prevents_universal_ri_default(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        modes = (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8")
        budget = (ROOT / "references" / "feature-budget.md").read_text(encoding="utf-8")
        title = (ROOT / "references" / "title-model.md").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, modes, budget, title])
        self.assertIn("references/title-model.md", skill)
        self.assertIn("Choose after the body exists", clean)
        self.assertIn("Standard diary does not have one safe default", modes)
        self.assertIn("Bare `日寄` is valid, but not a universal default", budget)
        self.assertIn("not a safe universal default", title)
        self.assertIn("calendar labels", title)
        self.assertIn("2024日寄", clean)
        self.assertIn("2024日寄", modes)
        self.assertNotIn("Standard diary defaults to `日寄`", combined)
        self.assertNotIn("default to `日寄`; use", combined)

    def test_deep_repair_references_are_not_content_quotas(self) -> None:
        generation_modes = (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8")
        structure = (ROOT / "references" / "structure-patterns.md").read_text(encoding="utf-8")
        reference_library = (ROOT / "references" / "anlin-reference-library.md").read_text(encoding="utf-8")
        portable = (ROOT / "references" / "portable-corpus.md").read_text(encoding="utf-8")
        characters = (ROOT / "references" / "anlin-characters.md").read_text(encoding="utf-8")
        self.assertIn("If the day's material has no natural misread", generation_modes)
        self.assertIn("do not satisfy this by adding a decorative named friend or game scene", generation_modes)
        self.assertIn("不要为了凑线条补背景素材", structure)
        self.assertIn("大多数保留场景应有转向", structure)
        self.assertIn("天气通常不能直说成气象播报", reference_library)
        self.assertNotIn("每篇至少混入三类", portable)
        self.assertIn("不能全篇只有一种低温情绪", portable)
        self.assertNotIn("每次出场三人格必须齐全", characters)
        self.assertIn("不要只写成负责骂人的工具人", characters)
        self.assertNotIn("出场必须携带", characters)
        self.assertNotIn("每个角色出场必须", characters)
        self.assertIn("若出场，应携带", characters)

    def test_high_signal_opening_is_source_guidance_not_only_checker(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, checker, layer_map])
        self.assertIn("high-signal opening", clean)
        self.assertIn("Do not impose a fixed opening line count", clean)
        self.assertIn("ordinary body, room, payment, door, charger, sink", clean)
        self.assertIn("prompt prop or feed inventory", clean)
        self.assertIn("high_signal_opening", checker)
        self.assertIn("Reset the opening source", checker)
        self.assertIn("changes the next action", combined)
        self.assertNotIn("first 8-12 body lines", combined)

    def test_soft_witness_is_source_guidance_not_only_checker(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        budget = (ROOT / "references" / "feature-budget.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, budget, checker])
        self.assertIn("not a camera angle", (ROOT / "references" / "feature-budget.md").read_text(encoding="utf-8"))
        self.assertIn("rider or cashier who only looks once and leaves is still decoration", clean)
        self.assertIn("Treat a silent witness as decoration", runtime)
        self.assertIn("the contact has failed", runtime)
        self.assertIn("soft_witness_no_consequence", checker)
        self.assertIn("Reset the outside-contact source", checker)
        self.assertIn("payment, reply, bag/object state", combined)
        self.assertIn("consequence verb before drafting", combined)
        self.assertIn("not a camera angle", combined)
        self.assertIn("look, glance, sweep, notice", combined)
        self.assertIn("No gaze-first contact repair", budget)
        self.assertIn("bag, payment, door", budget)

    def test_private_grime_is_source_guidance_not_only_checker(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        budget = (ROOT / "references" / "feature-budget.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, budget, checker])
        self.assertIn("Private grime is not an event", (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8"))
        self.assertIn("Private grime is not an event", clean)
        self.assertIn("No private-grime substitute", budget)
        self.assertIn("private_grime_without_public_consequence", checker)
        self.assertIn("Oil stains, sleeve dirt, sticky fingers, burps, mirror face", runtime)
        self.assertIn("change payment, reply, door, bag, body movement, or social position", combined)
        self.assertIn("do not add another stain, mirror check, burp, hair, smell, or sleeve detail", checker)

    def test_pure_ambient_ending_is_source_guidance_not_only_checker(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        budget = (ROOT / "references" / "feature-budget.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, budget, checker])
        self.assertIn("pure_ambient_ending", checker)
        self.assertIn("pure ambient", (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8"))
        self.assertIn("Do not end by fading out on light, wind, appliance noise, screen glow", clean)
        self.assertIn("No learned ending button or ambient fade-out", budget)
        self.assertIn("End on an earned unfinished action", budget)
        self.assertIn("unfinished thought", clean)
        self.assertIn("unfinished action", budget)
        self.assertIn(
            "administrative button",
            (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8"),
        )

    def test_skill_load_order_keeps_background_as_post_scene_fact_gate(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean_eval = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        self.assertIn("references/clean-eval-first-draft-minimum.md", skill)
        self.assertIn("references/clean-generation-brief.md", skill)
        self.assertIn("background is a contradiction boundary", skill.lower())
        self.assertNotIn("anlin-background.md", clean_eval.lower())
        self.assertNotIn("background-fact-classes.json", clean_eval.lower())
        self.assertIn("Fact or background check after scene selection", skill)
        self.assertIn("only after selected scenes already contain facts that need checking", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("Background is a contradiction boundary, not a content quota", skill)
        self.assertIn("background-fact-classes.json", skill)
        self.assertIn("背景展示堆砌", (ROOT / "references" / "self-check.md").read_text(encoding="utf-8"))
        self.assertIn("Before the first complete `draft.md`, do not open long repair", skill)

    @unittest.skip("superseded by the concise active-runtime fragment contract")
    def test_clean_generation_brief_carries_core_runtime_gates(self) -> None:
        brief = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        self.assertIn("Skill references are local bundled files", brief)
        self.assertIn("Do not call `read_mcp_resource`", brief)
        self.assertIn("Source Loop", brief)
        self.assertIn("friction and consequence before any audit vocabulary", brief)
        self.assertIn("exact character counting belongs to the checker", brief)
        self.assertIn("exact line counting belongs to the checker", brief)
        self.assertIn("not 100+ tiny rows", brief)
        self.assertIn("Standard diary source contract", brief)
        self.assertIn("use the standard source contract below before considering any short-sincere", brief)
        self.assertIn("breathing clusters, not as one sentence per row", brief)
        self.assertIn("Do not manually enumerate every line", brief)
        self.assertIn("negative list, not subject material", brief)
        self.assertIn("Game is allowed, not required", brief)
        self.assertIn("Do not invent a current office-worker identity", brief)
        self.assertIn("Do not convert delivery work into a different biography", brief)
        self.assertIn("wife, spouse, child", brief)
        self.assertIn("scan the candidate for narrator-owned spouse/child phrasing", brief)
        self.assertIn("If `我儿子/我女儿` belongs to another speaker", brief)
        self.assertIn("A rider video with `有人说...` is still a comment chain", brief)
        self.assertIn("clean_run_checker.py draft.md --strict --draft-gate", brief)
        self.assertIn("Known failed source shape", brief)
        self.assertIn("soft binary repair", brief)
        self.assertIn("not a caption row", brief)

    def test_background_fact_classes_are_boundaries_not_requirements(self) -> None:
        table = json.loads(BACKGROUND_FACT_CLASSES.read_text(encoding="utf-8"))
        self.assertIn("王者荣耀", table["classes"]["supported"]["game"])
        self.assertIn("打野教学", table["classes"]["unsupported"]["game_specifics"])
        self.assertIn("KPI", table["classes"]["unsupported"]["current_office_persona"])
        self.assertIn("老婆", table["classes"]["unsupported"]["family_identity"])
        self.assertIn("Background facts are contradiction boundaries", table["principle"])
        self.assertIn("does not change action", table["runtime_rule"])

    def test_checker_draft_gate_rejects_therapeutic_humanizer_terms(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "我允许自己慢慢来，试着和自己和解。",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: AI治疗式人类化: 允许自己" for rule in rules))

    def test_checker_does_not_treat_literal_unseen_note_as_therapeutic_humanizer(self) -> None:
        body = "\n".join(
            [
                "# 充电线",
                "",
                "备注大概根本就没被看见。",
                "外卖员把袋子递过来，我低头看了一眼订单。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("AI治疗式人类化: 被看见" in item["rule"] for item in findings), findings)

    def test_checker_draft_gate_rejects_current_game_match_sequence(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "打了两把王者，第一把蔡文姬，第二把还是蔡文姬，队友一直点我，退出之后又点开排位界面。",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 游戏复盘细节" for rule in rules))

    def test_checker_draft_gate_rejects_offer_compensation_specificity(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "有个同学拿到了字节跳动的前端offer，在广州，签字费加股票。",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: Offer具体化编造" for rule in rules))

    def test_checker_strict_rejects_sleep_ba_learned_ending(self) -> None:
        body = "\n".join(["# 日寄", "", *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35), "睡吧。"])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 习得式结尾按钮" for rule in rules))

    def test_checker_strict_rejects_today_first_like_this_learned_ending(self) -> None:
        body = "\n".join(
            [
                "# 楼下那张红纸",
                "",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
                "今天先这样。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 习得式结尾按钮" for rule in rules), findings)

    def test_checker_draft_gate_rejects_dialogue_stack_and_game_report(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "我说那还行。",
                "他说体检周五。",
                "我说挺好的。",
                "他说那边很远。",
                "我说远点也行。",
                "他说租房补贴还可以。",
                "我在泉水等复活。",
                "队友一直点撤退。",
                "输出比对面辅助低。",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 对话接力过密" for rule in rules))
            self.assertTrue(any(rule == "strict: 游戏复盘细节" for rule in rules))

    def test_checker_warns_on_connector_glue_overuse_without_hard_failure(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                *(["其实我把杯子拿去洗水龙头先咳了一下喷到裤子上"] * 36),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            glue = [item for item in findings if item["rule"] == "连接词胶水过量"]
            self.assertEqual(len(glue), 1)
            self.assertEqual(glue[0]["severity"], "warning")

    def test_checker_draft_gate_promotes_comma_rhythm_in_sparse_draft(self) -> None:
        body = "\n".join(["# 日寄", "", *(["杯子脏了。"] * 120)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any("行末逗号比例" in rule for rule in rules))

    def test_checker_draft_gate_comma_density_repair_guidance_rejects_comma_drag(self) -> None:
        line = "其实我拿起杯子，水还没倒，手机又亮，门口有人敲，鞋底还湿。"
        body = "\n".join(["# 日寄", "", *([line] * 46)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            comma_findings = [item for item in findings if "逗号密度过高" in item["rule"]]
            self.assertTrue(comma_findings, findings)
            suggestion = comma_findings[0]["suggestion"]
            self.assertIn("逗号链", suggestion)
            self.assertIn("实际需要的硬停顿", suggestion)
            self.assertIn("不要再补长行动句", suggestion)
            self.assertIn("继续撒逗号", suggestion)

    def test_checker_draft_gate_rejects_standard_period_row_grid(self) -> None:
        lines = [
            "水龙头开小了还是溅出来。",
            "碗沿那圈黑线怎么蹭都没掉。",
            "手机在枕头边亮了一下。",
            "我把袖口往下拽了拽。",
            "门口有人把垃圾袋拎过去。",
            "我站在那里看了几秒。",
            "消息列表里那条还是没回。",
            "锅里的水也没开。",
            "冰箱响了一声。",
            "后来就没动。",
        ]
        body = "\n".join(["# 洗到一半", "", *(lines * 12)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate", "--genre", "standard"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            period_findings = [item for item in findings if "标准日寄句号网格" in item["rule"]]
            self.assertTrue(period_findings, findings)
            self.assertEqual(period_findings[0]["severity"], "error")
            self.assertIn("不要把逗号问题反向修成句号网格", period_findings[0]["suggestion"])

    def test_checker_draft_gate_rejects_uniform_line_rhythm(self) -> None:
        lines = [
            "我坐在床边看手机又亮了一下。",
            "杯子放在桌上看起来有点脏。",
            "群里还在说体检和租房补贴。",
            "室友翻了个身像一袋旧衣服。",
            "我点开招聘页面又退了出来。",
            "屏幕亮得像没睡醒的灯泡。",
            "椅子有点歪坐上去会吱一声。",
            "窗外的空调外机一直响着。",
        ]
        body = "\n".join(["# 日寄", "", *(lines * 9)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 节奏过度均匀" for rule in rules))

    def test_checker_draft_gate_rejects_overfragmented_lineation(self) -> None:
        lines = ["充电线怼了三次才亮，", "我把手机翻过去，", "屏幕又亮了一下，", "没读数字又变大。"]
        body = "\n".join(["# 日寄", "", *(lines * 50)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 断裂过碎" for rule in rules))

    def test_checker_draft_gate_rejects_formal_line_shape_buffers(self) -> None:
        short_line = "我坐着看杯子又亮了，"
        longish = "其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"
        body = "\n".join(["# 日寄", "", *([short_line] * 105), *([longish] * 3)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 标准日寄行数缓冲异常" for rule in rules))
            self.assertTrue(any(rule == "strict: 标准日寄长行缓冲不足" for rule in rules))
            self.assertTrue(any(rule == "strict: 标准日寄短行网格" for rule in rules))

    def test_checker_draft_gate_rejects_mid_article_prompt_loop(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                *(["杯子有点脏，洗的时候水龙头先咳了一下，"] * 10),
                *(["群里还在聊 offer、体检、租房补贴和入职，招聘页面也一直亮着，"] * 18),
                *(["我下楼买了个苹果，回来发现充电线又松了，"] * 10),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            mid = [item for item in findings if "中段旁逸不足" in item["rule"]]
            self.assertTrue(mid, findings)
            self.assertFalse(any(item["severity"] == "error" for item in mid), mid)

    def test_checker_draft_gate_rejects_parallel_explainer_template(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "我看着群里的体检通知，觉得这不是为了入职，更像是某种提醒。",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: AI平行解释模板: 不是为了" for rule in rules))

    def test_checker_draft_gate_rejects_self_annotation_and_chinese_punctuation_line(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "听起来像隔壁施工，其实不是，好像就是风扇坏了。",
                "。",
                "心里有点堵，说不上是那种不舒服。",
                "其实就是那种怎么说呢，",
                "大概就是这个意思。",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: AI二元解释句式" for rule in rules))
            self.assertTrue(any(rule == "strict: 孤立中文标点" for rule in rules))
            self.assertTrue(any(rule == "strict: AI自我注解: 说不上是那种" for rule in rules))
            self.assertTrue(any(rule == "strict: AI自我注解: 其实就是那种" for rule in rules))
            self.assertTrue(any(rule == "strict: AI自我注解: 大概就是这个意思" for rule in rules))

    def test_checker_flags_quiet_explanation_and_weak_engine(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "楼道里的灯坏了。",
                "我看了一会手机。",
                "突然觉得这六个字挺刺耳的，大概是因为我也没怎么成长。",
                "我坐回床上。",
                "明天再说。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            rules = [item["rule"] for item in findings]
            self.assertTrue(any("安静解释句" in rule for rule in rules))
            self.assertTrue(any("段落发动机信号偏弱" in rule for rule in rules))
            self.assertTrue(all(item["severity"] != "error" for item in findings))

    def test_checker_flags_sealed_nocturne(self) -> None:
        body = "\n".join(
            [
                "# 失眠日寄",
                "",
                "我躺在床上看手机。",
                "枕头边的群通知一直亮。",
                "Boss直聘也弹了一条。",
                "室友睡了，闹钟在床头。",
                "到现在也没请他喝那杯奶茶。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            self.assertTrue(any("封闭夜晚短篇结构" in item["rule"] for item in findings))
            self.assertTrue(all(item["severity"] != "error" for item in findings))

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_blind_prep_supports_fragments_and_placebo(self) -> None:
        draft = next(iter(sorted(CORPUS.glob("*.md"))))
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "round"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BLIND_PREP),
                    str(draft),
                    str(CORPUS),
                    "--output-dir",
                    str(output_dir),
                    "--num-samples",
                    "2",
                    "--fragment-chars",
                    "120",
                    "--placebo",
                    "--include-skill-context",
                    "--seed",
                    "11",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            samples = sorted(output_dir.glob("sample-*.txt"))
            self.assertEqual(len(samples), 3)
            mapping = json.loads((output_dir / "mapping.json").read_text(encoding="utf-8"))
            self.assertTrue(all(not item["is_draft"] for item in mapping.values()))
            prompt = (output_dir / "prompt.txt").read_text(encoding="utf-8")
            self.assertIn("NONE", prompt)
            self.assertIn("DETAILED_REASONS", prompt)
            self.assertIn("MOST_SOURCE_LIKE", prompt)
            self.assertNotIn("MOST_ANLIN_LIKE", prompt)
            self.assertIn("Do not use outside", prompt)
            self.assertIn("SOURCE_COHESION_CHECK", prompt)
            self.assertIn("title", prompt.lower())
            trigger_terms = (
                "Anlin",
                "style skill",
                "author-specific",
                "skill references",
                "mapping.json",
                "impostor",
                "original corpus",
            )
            for term in trigger_terms:
                self.assertNotIn(term, prompt)
            self.assertFalse((output_dir / "portable-corpus.md").exists())
            self.assertFalse((output_dir / "vocabulary-rules.md").exists())

    def test_blind_prep_can_match_short_sincere_genre_without_full_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            corpus = root / "corpus"
            corpus.mkdir()
            draft = root / "draft.md"
            draft.write_text(
                "# 母亲节\n\n"
                + "\n".join(["我妈把鸡蛋塞进袋子里，我骑车到楼下才发现破了一个。"] * 18),
                encoding="utf-8",
            )
            (corpus / "sincere-1.md").write_text(
                "# 母亲节日寄\n\n" + "\n".join(["我妈说鸡蛋放久了不好，我说知道了。"] * 16),
                encoding="utf-8",
            )
            (corpus / "sincere-2.md").write_text(
                "# 谢谢你\n\n" + "\n".join(["下雨的时候她递过来一把伞，我把伞骨弄弯了。"] * 16),
                encoding="utf-8",
            )
            (corpus / "standard-1.md").write_text(
                "# 春招破防日寄\n\n" + "\n".join(["群里说体检，我看了一眼手机又放下。"] * 40),
                encoding="utf-8",
            )
            (corpus / "standard-2.md").write_text(
                "# 日寄\n\n" + "\n".join(["楼下风很大，外卖袋子贴在电动车把手上。"] * 40),
                encoding="utf-8",
            )

            output_dir = root / "matched-round"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BLIND_PREP),
                    str(draft),
                    str(corpus),
                    "--output-dir",
                    str(output_dir),
                    "--num-samples",
                    "3",
                    "--match-genre",
                    "sincere",
                    "--length-tolerance",
                    "1.0",
                    "--seed",
                    "31",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            mapping = json.loads((output_dir / "mapping.json").read_text(encoding="utf-8"))
            originals = [item for item in mapping.values() if not item["is_draft"]]
            self.assertEqual(len(originals), 3)
            self.assertEqual(sum(1 for item in originals if item["genre"] == "sincere"), 2)
            self.assertTrue(all(item["match"]["target_genre"] == "sincere" for item in originals))
            self.assertEqual(sum(1 for item in originals if item["match"]["selection_reason"].startswith("genre")), 2)

            placebo_dir = root / "matched-placebo"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BLIND_PREP),
                    str(draft),
                    str(corpus),
                    "--output-dir",
                    str(placebo_dir),
                    "--num-samples",
                    "3",
                    "--placebo",
                    "--match-genre",
                    "sincere",
                    "--length-tolerance",
                    "1.0",
                    "--seed",
                    "32",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            placebo_mapping = json.loads((placebo_dir / "mapping.json").read_text(encoding="utf-8"))
            self.assertTrue(all(not item["is_draft"] for item in placebo_mapping.values()))
            self.assertTrue(all(item["match"]["target_genre"] == "sincere" for item in placebo_mapping.values()))
            self.assertEqual(sum(1 for item in placebo_mapping.values() if item["genre"] == "sincere"), 2)

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_blind_prep_keeps_titles_and_rejects_short_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            draft = temp_path / "draft.md"
            draft.write_text("# 日寄\n\n太短了。", encoding="utf-8")

            output_dir = temp_path / "short-round"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BLIND_PREP),
                    str(draft),
                    str(CORPUS),
                    "--output-dir",
                    str(output_dir),
                    "--num-samples",
                    "2",
                    "--fragment-chars",
                    "120",
                    "--min-fragment-chars",
                    "80",
                    "--seed",
                    "12",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("below --min-fragment-chars", result.stderr)

            long_draft = temp_path / "long.md"
            long_draft.write_text("# 日寄\n\n" + "今天有点热。" * 40, encoding="utf-8")
            output_dir = temp_path / "ok-round"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BLIND_PREP),
                    str(long_draft),
                    str(CORPUS),
                    "--output-dir",
                    str(output_dir),
                    "--num-samples",
                    "2",
                    "--min-fragment-chars",
                    "80",
                    "--length-tolerance",
                    "1.0",
                    "--seed",
                    "13",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            mapping = json.loads((output_dir / "mapping.json").read_text(encoding="utf-8"))
            draft_sample = next(name for name, item in mapping.items() if item["is_draft"])
            sample_text = (output_dir / draft_sample).read_text(encoding="utf-8")
            self.assertTrue(sample_text.startswith("# 日寄"))
            self.assertEqual(mapping[draft_sample]["title"], "日寄")

            bold_title_draft = temp_path / "bold-title.md"
            bold_title_draft.write_text("**日寄**\n\n" + "今天有点热。" * 40, encoding="utf-8")
            output_dir = temp_path / "bold-title-round"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BLIND_PREP),
                    str(bold_title_draft),
                    str(CORPUS),
                    "--output-dir",
                    str(output_dir),
                    "--num-samples",
                    "2",
                    "--min-fragment-chars",
                    "80",
                    "--length-tolerance",
                    "1.0",
                    "--seed",
                    "15",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            mapping = json.loads((output_dir / "mapping.json").read_text(encoding="utf-8"))
            draft_sample = next(name for name, item in mapping.items() if item["is_draft"])
            sample_text = (output_dir / draft_sample).read_text(encoding="utf-8")
            self.assertTrue(sample_text.startswith("# 日寄\n\n"))
            self.assertNotIn("**日寄**", sample_text)
            self.assertEqual(mapping[draft_sample]["title"], "日寄")

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_blind_prep_removes_metadata_from_draft(self) -> None:
        draft = next(iter(sorted(CORPUS.glob("*.md"))))
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "round"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BLIND_PREP),
                    str(draft),
                    str(CORPUS),
                    "--output-dir",
                    str(output_dir),
                    "--num-samples",
                    "2",
                    "--min-fragment-chars",
                    "200",
                    "--length-tolerance",
                    "1.0",
                    "--seed",
                    "14",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            mapping = json.loads((output_dir / "mapping.json").read_text(encoding="utf-8"))
            draft_sample = next(name for name, item in mapping.items() if item["is_draft"])
            sample_text = (output_dir / draft_sample).read_text(encoding="utf-8")
            self.assertTrue(sample_text.startswith("# "))
            self.assertNotIn("**作者**", sample_text)
            self.assertNotIn("原链接", sample_text)

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_corpus_cards_exist(self) -> None:
        result = subprocess.run(
            [sys.executable, str(BUILD_CARDS), "--corpus-dir", str(CORPUS)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        cards = [path for path in CARDS.glob("*.md") if path.name != "INDEX.md"]
        self.assertEqual(len(cards), 38)
        self.assertTrue((CARDS / "INDEX.md").is_file())

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_style_profile_builds_corpus_prior(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            profile_path = Path(temp) / "style-profile.json"
            result = subprocess.run(
                [sys.executable, str(BUILD_PROFILE), str(CORPUS), "--output", str(profile_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(profile["corpus_file_count"], 38)
            self.assertEqual(profile["corpus_dir"], "<corpus-dir>")
            self.assertEqual(len(profile["documents"]), 38)
            self.assertEqual(profile["profile_kind"], "corpus_prior_predictive_intervals")
            self.assertEqual(profile["version"], "1.7")
            self.assertIn("body_chars", profile["value_summary"])
            self.assertIn("ai_binary_reframe", profile["count_summary"])
            self.assertIn("unique_3gram_ratio", profile["value_summary"])
            self.assertIn("repeated_3gram_templates", profile["count_summary"])
            self.assertIn("texture_body_lines", profile["count_summary"])
            self.assertIn("texture_any_line_share", profile["value_summary"])
            self.assertIn("body_money_social_line_share", profile["value_summary"])
            self.assertIn("middle_off_axis_line_share", profile["value_summary"])
            self.assertIn("title_tail_bigram_overlap", profile["value_summary"])
            self.assertIn("dominant_theme_line_share", profile["value_summary"])
            self.assertIn("cognitive_crooked_interpretation", profile["count_summary"])
            self.assertEqual(profile["value_families"]["unique_3gram_ratio"], "ngram_texture")
            self.assertEqual(profile["count_summary"]["texture_body_lines"]["family"], "texture")
            self.assertEqual(profile["count_summary"]["body_money_social_lines"]["family"], "texture")
            self.assertEqual(profile["count_summary"]["middle_off_axis_lines"]["family"], "structure")
            self.assertEqual(profile["count_summary"]["cognitive_crooked_interpretation"]["family"], "cognitive_mechanism")
            self.assertIn("strata", profile)
            self.assertIn("A", profile["strata"]["phase"])
            self.assertIn("standard", profile["strata"]["genre"])
            self.assertIn("A/standard", profile["strata"]["phase_genre"])
            self.assertTrue(profile["count_summary"]["ai_binary_reframe"]["hard_generated"])
            self.assertIn("Do not force rare features to appear.", profile["principles"])

    def test_style_profile_help_renders_percent_text(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECK_PROFILE), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("80% predictive informational drift", result.stdout)

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_style_profile_has_no_hard_errors_on_original_corpus(self) -> None:
        self.assertTrue(STYLE_PROFILE.is_file(), f"missing style profile: {STYLE_PROFILE}")
        failures: list[str] = []
        for path in sorted(CORPUS.glob("*.md")):
            result = subprocess.run(
                [sys.executable, str(CHECK_PROFILE), str(path), "--profile", str(STYLE_PROFILE), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            if report["summary"]["error_count"]:
                failures.append(f"{path.name}: {report['summary']['error_count']} errors")
        self.assertEqual(failures, [])

    def test_style_profile_draft_gate_rejects_ai_binary_reframe(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "不是包装袋漏，是电动车前面那个篮子。",
                "不是不想帮。是帮了还要继续站在太阳底下。",
                "我不是叔叔，我只是失败得比较显老。",
                "酸梅汤顺着车篮子滴了一路。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            normal_result = subprocess.run(
                [sys.executable, str(CHECK_PROFILE), str(draft), "--profile", str(STYLE_PROFILE), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(normal_result.returncode, 0, normal_result.stderr)
            normal_report = json.loads(normal_result.stdout)
            self.assertEqual(normal_report["summary"]["error_count"], 0)

            draft_gate_result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(STYLE_PROFILE),
                    "--draft-gate",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(draft_gate_result.returncode, 0)
            draft_gate_report = json.loads(draft_gate_result.stdout)
            errors = [item for item in draft_gate_report["findings"] if item["severity"] == "error"]
            self.assertTrue(any(item["metric"] == "ai_binary_reframe" for item in errors))
            self.assertEqual(draft_gate_report["summary"]["status"], "revise")
            self.assertEqual(draft_gate_report["summary"]["checkpoint_decision"], "not_pass_revise")
            self.assertFalse(draft_gate_report["summary"]["checkpoint_pass"])
            self.assertIn("red_families", draft_gate_report["summary"])
            self.assertIn("decision_rule", draft_gate_report["summary"])
            self.assertIn("checkpoint_rule", draft_gate_report["summary"])
            self.assertIn("cognitive_audit", draft_gate_report)
            self.assertIn("missing_core", draft_gate_report["cognitive_audit"])
            self.assertIn("first_hit_lines", draft_gate_report["cognitive_audit"])
            self.assertIn("independent_drift_family_count", draft_gate_report["summary"])
            self.assertIn("profile_scope", draft_gate_report)
            self.assertEqual(draft_gate_report["summary"]["repair_mode"], "source_rewrite_required")
            self.assertIn("source structure", draft_gate_report["summary"]["next_repair_action"])

    def test_style_profile_defaults_to_bundled_profile(self) -> None:
        self.assertTrue(STYLE_PROFILE.is_file(), f"missing style profile: {STYLE_PROFILE}")
        body = "\n".join(
            [
                "# 水池",
                "",
                "水龙头先空响了一下，",
                "我把杯子拿过去，发现杯底还有一点灰。",
                "于是又冲了一遍，手背蹭到裤腿上。",
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECK_PROFILE), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["profile_version"], "1.7")
            self.assertEqual(report["corpus_file_count"], 38)

    def test_style_profile_strict_returns_nonzero_for_review_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 日寄",
                        "",
                        "我在楼下看见水龙头又漏了一点。",
                        "还以为这是系统在结算我今天的钱。",
                        "手机亮了一下，我说算了。",
                        "杯子放在桌上，底下有一圈水，我关了屏幕。",
                    ]
                ),
                encoding="utf-8",
            )
            profile = Path(temp) / "profile.json"
            yellow_summary = {
                "min": 0.0,
                "q05": 0.0,
                "q10": 0.0,
                "median": 0.0,
                "q90": 0.0,
                "q95": 0.0,
                "max": 100000.0,
                "mean": 0.0,
                "mad": 0.0,
            }
            profile.write_text(
                json.dumps(
                    {
                        "version": "test",
                        "corpus_file_count": 38,
                        "expected_corpus_count": 38,
                        "value_summary": {
                            "body_chars": yellow_summary,
                            "title_chars": yellow_summary,
                            "line_mean_chars": yellow_summary,
                            "paragraph_blocks": yellow_summary,
                            "punct_period_per_1k": yellow_summary,
                        },
                        "value_families": {
                            "body_chars": "length",
                            "title_chars": "title",
                            "line_mean_chars": "line_rhythm",
                            "paragraph_blocks": "structure",
                            "punct_period_per_1k": "punctuation",
                        },
                        "count_summary": {},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            json_result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(json_result.returncode, 0, json_result.stderr)
            report = json.loads(json_result.stdout)
            self.assertEqual(report["summary"]["status"], "review")
            self.assertEqual(report["summary"]["checkpoint_decision"], "not_pass_review_required")
            self.assertFalse(report["summary"]["checkpoint_pass"])
            self.assertIn("review is not a finalized checkpoint pass", report["summary"]["decision_rule"])
            self.assertEqual(report["summary"]["independent_drift_family_count"], 5)
            self.assertEqual(report["summary"]["repair_mode"], "source_reset_thinning")
            self.assertIn("many yellow families", report["summary"]["next_repair_action"])

            strict_result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--strict",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(strict_result.returncode, 0)

            text_result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(text_result.returncode, 0, text_result.stderr)
            self.assertIn("checkpoint_decision: not_pass_review_required", text_result.stdout)
            self.assertIn("checkpoint_pass: false", text_result.stdout)
            self.assertIn("formal_gate: not_pass", text_result.stdout)
            self.assertIn("Do not call the article clean", text_result.stdout)
            self.assertIn("repair_mode: source_reset_thinning", text_result.stdout)
            self.assertIn("next_repair_action:", text_result.stdout)

    def test_style_profile_repair_brief_is_compact_generator_interface(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 水龙头",
                        "",
                        *(["水龙头开小了还是溅出来。"] * 52),
                    ]
                ),
                encoding="utf-8",
            )
            red_summary = {
                "min": 0.0,
                "q05": 0.0,
                "q10": 0.0,
                "median": 0.0,
                "q90": 0.0,
                "q95": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "mad": 0.0,
            }
            profile = Path(temp) / "profile.json"
            profile.write_text(
                json.dumps(
                    {
                        "version": "test",
                        "corpus_file_count": 38,
                        "expected_corpus_count": 38,
                        "value_summary": {
                            "body_chars": red_summary,
                            "paragraph_blocks": red_summary,
                            "line_mean_chars": red_summary,
                            "punct_period_per_1k": red_summary,
                        },
                        "value_families": {
                            "body_chars": "length",
                            "paragraph_blocks": "structure",
                            "line_mean_chars": "line_rhythm",
                            "punct_period_per_1k": "punctuation",
                        },
                        "count_summary": {},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--strict",
                    "--repair-brief",
                    "--genre",
                    "standard",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Anlin style-profile repair brief", result.stdout)
            self.assertIn("artifact_path: draft.md", result.stdout)
            self.assertIn("artifact_contract: the revised complete article must be written back to draft.md", result.stdout)
            self.assertIn("repair_directive: write one complete revised draft.md now, then stop", result.stdout)
            self.assertIn("Do not print the article to terminal only", result.stdout)
            self.assertIn("hard_gate_priority: if the preceding hard gate showed blocking findings", result.stdout)
            self.assertIn("hard_gate_pass_preservation: if the preceding hard gate already passed", result.stdout)
            self.assertIn("A repair that introduces `高频词覆盖不足`, `标准日寄句号网格`", result.stdout)
            self.assertIn("micro_cluster_surgery", result.stdout)
            self.assertIn("do not add a new simile, analogy, or caption", result.stdout)
            self.assertIn("do not make line-final comma ratio zero", result.stdout)
            self.assertIn("preserve working comma-ended continuation rows from the incoming draft", result.stdout)
            self.assertIn("line_ending_lock", result.stdout)
            self.assertIn("mass_floor_lock", result.stdout)
            self.assertIn("attempt_contract: use this controller-prepared brief", result.stdout)
            self.assertIn("choose one primary source rewrite", result.stdout)
            self.assertIn("Do not repair one family at a time", result.stdout)
            self.assertIn("post-write python -c/Measure-Object/wc counter", result.stdout)
            self.assertIn("Test-Path/Glob/List/source/test/threshold/log search", result.stdout)
            self.assertIn("artifact_written", result.stdout)
            self.assertIn("standard_shape_first: preserve the titled, line-broken standard diary", result.stdout)
            self.assertIn("middle corridor", result.stdout)
            self.assertIn("standard_overfill_guard", result.stdout)
            self.assertIn("1250 body Chinese characters", result.stdout)
            self.assertIn("2000+ character standard repair", result.stdout)
            self.assertIn("standard_do_not_save: do not save 8-25 dense prose rows", result.stdout)
            self.assertIn("45-70-line caption grid with 0 real long rows", result.stdout)
            self.assertIn("140+ row overfilled proof ledger", result.stdout)
            self.assertIn("standard_preserve_existing: when the incoming standard draft already passed hard gate", result.stdout)
            self.assertIn("Do not add group-chat/comment-chain surfaces", result.stdout)
            self.assertIn("standard_social_decline_source: for invitation/refusal repairs", result.stdout)
            self.assertIn("refusal-coupled consequence", result.stdout)
            self.assertIn("Do not add message-order plot glue", result.stdout)
            self.assertIn("exit_note: with --strict --repair-brief", result.stdout)
            self.assertIn("not tool failure", result.stdout)
            self.assertIn("primary_source_rewrite:", result.stdout)
            self.assertIn("preserve the scene slate and repair page shape locally", result.stdout)
            self.assertIn("Repair only the smallest existing movement that is actually broken", result.stdout)
            self.assertIn("restore whichever single relation that movement earns", result.stdout)
            self.assertIn("Do not stamp all four into the cluster", result.stdout)
            self.assertIn("do not merge a comma-ended row with its following line into a sealed sentence", result.stdout)
            self.assertIn("keep row-ending punctuation and line breaks for untouched rows", result.stdout)
            self.assertIn("do not remove a functional consequence sentence unless you replace it inside the same local cluster", result.stdout)
            self.assertIn("keep the existing title, people, message channel", result.stdout)
            self.assertIn("do not rewrite the article from a new premise", result.stdout)
            self.assertIn("source_action_note: the list below is diagnostic context only", result.stdout)
            self.assertIn("root_families:", result.stdout)
            self.assertIn("punctuation:", result.stdout)
            self.assertIn("line_rhythm:", result.stdout)
            self.assertIn("remaining families: ignore during this write", result.stdout)
            self.assertNotIn("standard_shape_guard:", result.stdout)
            self.assertNotIn("single_write_budget:", result.stdout)
            self.assertNotIn("path_contract:", result.stdout)
            self.assertNotIn("4-6 breathing clusters", result.stdout)
            self.assertNotIn("findings:", result.stdout)
            self.assertNotIn("observed=", result.stdout)
            self.assertNotIn("q10-q90", result.stdout)
            self.assertNotIn("q05-q95", result.stdout)
            self.assertNotIn("count80", result.stdout)
            self.assertNotIn("robust_z", result.stdout)

            full_result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--strict",
                    "--genre",
                    "standard",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(full_result.returncode, 0)
            self.assertIn("findings:", full_result.stdout)
            self.assertIn("observed=", full_result.stdout)
            self.assertIn("q05-q95", full_result.stdout)
            self.assertIn("robust_z=", full_result.stdout)

    def test_style_profile_repair_brief_preserves_natural_repetition_when_ngram_reuse_is_too_low(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 门口",
                        "",
                        "甲乙丙丁戊己庚辛壬癸。",
                        "子丑寅卯辰巳午未申酉。",
                        "天地玄黄宇宙洪荒日月盈昃。",
                    ]
                ),
                encoding="utf-8",
            )
            profile = Path(temp) / "profile.json"
            profile.write_text(
                json.dumps(
                    {
                        "version": "test",
                        "corpus_file_count": 38,
                        "expected_corpus_count": 38,
                        "value_summary": {
                            "line_mean_chars": {
                                "min": 0.0,
                                "q05": 0.0,
                                "q10": 0.0,
                                "median": 0.0,
                                "q90": 0.0,
                                "q95": 0.0,
                                "max": 0.0,
                                "mean": 0.0,
                                "mad": 0.0,
                            },
                            "punct_period_per_1k": {
                                "min": 0.0,
                                "q05": 0.0,
                                "q10": 0.0,
                                "median": 0.0,
                                "q90": 0.0,
                                "q95": 0.0,
                                "max": 0.0,
                                "mean": 0.0,
                                "mad": 0.0,
                            },
                        },
                        "value_families": {
                            "line_mean_chars": "line_rhythm",
                            "punct_period_per_1k": "punctuation",
                        },
                        "count_summary": {
                            "repeated_4gram_templates": {
                                "family": "ngram_texture",
                                "alpha": 100.0,
                                "beta": 1.0,
                            }
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            full_result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(full_result.returncode, 0, full_result.stderr)
            report = json.loads(full_result.stdout)
            ngram_finding = next(
                finding for finding in report["findings"] if finding["family"] == "ngram_texture"
            )
            self.assertEqual(ngram_finding["direction"], "low")
            self.assertIn("Natural local repetition is below", ngram_finding["suggestion"])
            self.assertIn("do not synonym-scrub repeated words", ngram_finding["suggestion"])
            self.assertNotIn("delete one repeated body/object packet", ngram_finding["suggestion"])

            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--strict",
                    "--repair-brief",
                    "--genre",
                    "standard",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("root_families: punctuation, line_rhythm, ngram_texture", result.stdout)
            self.assertIn("preserve one plain action or object phrase that genuinely recurs", result.stdout)
            self.assertIn("do not synonym-scrub repeated words", result.stdout)
            self.assertNotIn(
                "ngram_texture: delete one repeated local packet or line-start template",
                result.stdout,
            )

    def test_runtime_ngram_repair_guidance_is_direction_aware(self) -> None:
        runtime_files = [
            ROOT / "references" / "runtime-brief.md",
            ROOT / "references" / "clean-generation-brief.md",
            ROOT / "references" / "finalized-repair-minimum.md",
        ]
        for path in runtime_files:
            text = path.read_text(encoding="utf-8")
            self.assertIn("If n-gram reuse is too low or uniqueness is too high", text)
            self.assertIn("do not synonym-scrub repeated words", text)
            self.assertIn("If repetition is too high or templates repeat mechanically", text)

    def test_prepare_finalized_repair_brief_writes_compact_artifact_only_brief(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            finalized_dir = Path(temp) / "finalized"
            finalized_dir.mkdir()
            draft = finalized_dir / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 水龙头",
                        "",
                        "不是包装袋漏，是电动车前面那个篮子。",
                        *(["水龙头开小了还是溅出来。"] * 8),
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_FINALIZED_REPAIR_BRIEF),
                    str(draft),
                    "--genre",
                    "standard",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            brief_path = finalized_dir / "repair-brief.txt"
            self.assertEqual(Path(payload["output"]), brief_path)
            self.assertTrue(payload["repair_required"])
            self.assertEqual(payload["selected_genre"], "standard")
            self.assertTrue(brief_path.is_file())

            brief = brief_path.read_text(encoding="utf-8")
            self.assertIn("Anlin finalized repair brief", brief)
            self.assertIn("producer: controller", brief)
            self.assertIn("selected_genre: standard", brief)
            self.assertIn("hard_gate_status: not_pass", brief)
            self.assertIn("repair_mode: source_rewrite_compact", brief)
            self.assertIn("hard_gate_primary_action:", brief)
            self.assertIn("source_focus:", brief)
            self.assertIn("scope_contract: rebuild the existing incomplete article", brief)
            self.assertIn("mass_contract: preserve a complete article", brief)
            self.assertIn("profile_diagnostics: controller_only", brief)
            self.assertIn("tool_boundary: do not run check_anlin_violations.py", brief)
            self.assertIn("read draft.md and repair-brief.txt", brief)
            self.assertIn("exactly one complete draft.md write", brief)
            self.assertIn("controller_boundary: after the single write", brief)
            self.assertNotIn("hard_gate_blockers:", brief)
            self.assertNotIn("style_repair_brief:", brief)
            self.assertNotIn("Anlin style-profile repair brief", brief)
            self.assertNotIn("findings:", brief)
            self.assertNotIn("observed=", brief)
            self.assertNotIn("body_chinese_chars=", brief)
            self.assertNotIn("AI二元解释句式", brief)
            self.assertNotIn("q10-q90", brief)
            self.assertNotIn("q05-q95", brief)
            self.assertNotIn("count80", brief)
            self.assertNotIn("robust_z", brief)

    def test_prepare_finalized_repair_brief_hard_gate_failure_uses_compact_source_interface(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("下次聚\n\n" + ("我" * 889), encoding="utf-8")
            findings = [
                {
                    "severity": "error",
                    "rule": "strict: 标准日寄完整文章篇幅缓冲不足",
                    "excerpt": "body_chinese_chars=889",
                    "suggestion": "restore mass",
                },
                {
                    "severity": "error",
                    "rule": "strict: 社交拒绝纹理替代后果不足",
                    "excerpt": "private room loop",
                    "suggestion": "make the refusal change the next action",
                },
                {
                    "severity": "warning",
                    "rule": "私密湿脏纹理替代粗粝",
                    "excerpt": "裤腿",
                    "suggestion": "replace the private packet",
                },
            ]
            brief = format_brief(
                draft=draft,
                genre="standard",
                hard_findings=findings,
                hard_returncode=1,
                profile_result=CommandResult(command=[], returncode=2, stdout="", stderr="unavailable"),
            )

        self.assertIn("repair_mode: source_rewrite_compact", brief)
        self.assertIn("hard_gate_primary_action: replace_underbuilt_fragment", brief)
        self.assertIn("source_focus:", brief)
        self.assertIn("existing local fragment relation", brief)
        self.assertIn("do not append an independent scene or proof packet", brief)
        self.assertNotIn("one refusal-coupled consequence", brief)
        self.assertIn("profile_diagnostics: controller_only", brief)
        self.assertNotIn("hard_gate_blockers:", brief)
        self.assertNotIn("style_repair_brief:", brief)
        self.assertNotIn("Anlin style-profile repair brief", brief)
        self.assertNotRegex(brief, r"body_chinese_chars=\d|roughly 950|650-899|900-949|1250")

    def test_compact_source_interface_matches_primary_route_boundaries(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        profile_error = CommandResult(command=[], returncode=2, stdout="", stderr="unavailable")

        def render(body_chars: int, findings: list[dict[str, str]]) -> str:
            with tempfile.TemporaryDirectory() as temp:
                draft = Path(temp) / "draft.md"
                draft.write_text("# 日寄\n\n" + ("我" * body_chars), encoding="utf-8")
                return format_brief(
                    draft=draft,
                    genre="standard",
                    hard_findings=findings,
                    hard_returncode=1,
                    profile_result=profile_error,
                )

        severe = render(
            568,
            [
                {"severity": "error", "rule": "标准日寄完整文章篇幅偏短"},
                {"severity": "error", "rule": "社交拒绝纹理替代后果不足"},
            ],
        )
        self.assertIn("hard_gate_primary_action: rebuild_severely_underbuilt_fragment", severe)
        self.assertIn("scope_contract: rebuild the existing incomplete article", severe)
        self.assertNotIn("choose one existing local cluster", severe)

        overfull = render(
            1450,
            [
                {"severity": "error", "rule": "标准日寄完整文章过满"},
                {"severity": "error", "rule": "社交拒绝纹理替代后果不足"},
            ],
        )
        self.assertIn("hard_gate_primary_action: thin_overfull_fragment_slate", overfull)
        self.assertIn("source_focus: remove repeated proof", overfull)
        self.assertIn("scope_contract: remove the smallest repeated proof cluster", overfull)
        self.assertNotIn("refusal-coupled consequence", overfull)

        period = render(
            1000,
            [
                {"severity": "error", "rule": "标准日寄句号网格"},
                {"severity": "warning", "rule": "社交拒绝纹理替代后果不足"},
            ],
        )
        self.assertIn("hard_gate_primary_action: break_period_grid", period)
        self.assertIn("source_focus: repair one existing action/reply/body movement", period)
        self.assertNotIn("refusal-coupled consequence", period)

    def test_prepare_finalized_repair_brief_hard_pass_review_uses_compact_in_place_interface(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            finalized_dir = Path(temp) / "finalized"
            finalized_dir.mkdir()
            draft = finalized_dir / "draft.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_FINALIZED_REPAIR_BRIEF),
                    str(draft),
                    "--genre",
                    "standard",
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["hard_gate_status"], "pass")
            self.assertNotEqual(payload["profile_returncode"], 0)

            brief = (finalized_dir / "repair-brief.txt").read_text(encoding="utf-8")
            self.assertIn("repair_mode: hard_pass_review_in_place", brief)
            self.assertIn("read only draft.md and repair-brief.txt", brief)
            self.assertIn("self-contained", brief)
            self.assertIn("do not load references/finalized-repair-minimum.md", brief)
            self.assertIn("eligible_cluster_ranges: lines ", brief)
            self.assertIn("each range is one existing local cluster of 4-6 consecutive nonblank body rows", brief)
            self.assertIn("replace each selected row with exactly one row in the same position", brief)
            self.assertIn("total body row count, row order, and every blank-line boundary unchanged", brief)
            self.assertIn("preserve every unselected row exactly", brief)
            self.assertIn("do not delete, merge, split, add, or move rows", brief)
            self.assertIn("must not be visibly shorter than the original row", brief)
            self.assertIn("preserve every row in the protected tail range exactly", brief)
            self.assertIn("protected_tail_range: lines ", brief)
            self.assertIn("the final existing nonblank body block", brief)
            self.assertIn("primary_family: punctuation", brief)
            self.assertEqual(brief.count("primary_family:"), 1)
            self.assertIn("secondary_families: controller_only", brief)
            self.assertIn("exactly one complete draft.md write, then stop", brief)
            self.assertNotIn("style_repair_brief:", brief)
            self.assertNotIn("Anlin style-profile repair brief", brief)
            self.assertNotRegex(brief, r"\b(?:900|950|1250)\b|per[- ]?1k|per-thousand|profile threshold")

    def test_prepare_finalized_repair_brief_hard_checker_tool_failure_never_claims_pass(self) -> None:
        import prepare_finalized_repair_brief as controller

        with tempfile.TemporaryDirectory() as temp:
            finalized_dir = Path(temp) / "finalized"
            finalized_dir.mkdir()
            draft = finalized_dir / "draft.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-8")
            brief_path = finalized_dir / "repair-brief.txt"
            argv = [
                "prepare_finalized_repair_brief.py",
                str(draft),
                "--genre",
                "standard",
                "--profile",
                str(STYLE_PROFILE),
                "--output",
                str(brief_path),
                "--json",
            ]
            stdout = io.StringIO()
            with (
                mock.patch.object(controller, "CHECKER", Path(temp) / "missing-checker.py"),
                mock.patch.object(sys, "argv", argv),
                redirect_stdout(stdout),
            ):
                returncode = controller.main()

            self.assertEqual(returncode, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["hard_gate_returncode"], 2)
            self.assertEqual(payload["hard_gate_status"], "controller_tool_error")
            self.assertIn("unavailable, not quality evidence", payload["note"])
            brief = brief_path.read_text(encoding="utf-8")
            self.assertIn("hard_gate_status: controller_tool_error", brief)
            self.assertIn("style_repair_brief:", brief)
            self.assertNotIn("repair_mode: hard_pass_review_in_place", brief)

    def test_prepare_finalized_repair_brief_rejects_invalid_hard_finding_schema(self) -> None:
        from prepare_finalized_repair_brief import hard_status, parse_hard_findings

        for payload in ("[{}]", "[1]"):
            with self.subTest(payload=payload):
                findings = parse_hard_findings(payload)
                self.assertEqual(hard_status(findings, returncode=0), "controller_tool_error")

        valid_error = parse_hard_findings('[{"severity": "error"}]')
        self.assertEqual(hard_status(valid_error, returncode=0), "controller_tool_error")

    def test_finalized_repair_compact_mode_routes_brief_only(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        finalized_minimum = (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8")
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")

        for text in (skill, runtime):
            self.assertIn("repair_mode: hard_pass_review_in_place", text)
            self.assertIn("repair_mode: source_rewrite_compact", text)
            self.assertIn("read only `draft.md` and `repair-brief.txt`", text)
            self.assertIn("do not load `references/finalized-repair-minimum.md`", text)
            self.assertIn("missing/invalid brief", text)
        self.assertIn(
            "Do not use this file for `repair_mode: hard_pass_review_in_place`",
            finalized_minimum,
        )
        self.assertIn("or `repair_mode: source_rewrite_compact`", finalized_minimum)
        for text in (skill, runtime, finalized_minimum, validation):
            self.assertIn("schema-valid", text)
            self.assertIn("unavailable, not quality evidence", text)

    def test_prepare_finalized_repair_brief_preserves_hard_gate_pass_on_profile_review(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        profile_brief = finalized_profile_repair_brief()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-8")
            brief = format_brief(
                draft=draft,
                genre="standard",
                hard_findings=[],
                profile_result=CommandResult(
                    command=[],
                    returncode=1,
                    stdout=profile_brief,
                    stderr="",
                ),
            )

        self.assertIn("hard_gate_status: pass", brief)
        self.assertIn("repair_mode: hard_pass_review_in_place", brief)
        self.assertIn("primary_family: punctuation", brief)
        self.assertIn(
            "primary_action: let punctuation follow unfinished action inside the selected rows.",
            brief,
        )
        self.assertIn("secondary_families: controller_only", brief)
        self.assertIn("preserve every unselected row exactly", brief)
        self.assertIn("exactly one complete draft.md write, then stop", brief)
        self.assertNotIn("style_repair_brief:", brief)
        self.assertNotIn("ngram_texture", brief)

    def test_prepare_finalized_repair_brief_without_eligible_cluster_keeps_full_interface(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        profile_brief = finalized_profile_repair_brief()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "没有四行簇",
                        "",
                        "第一行。",
                        "第二行。",
                        "第三行。",
                        "",
                        "尾巴一。",
                        "尾巴二。",
                    ]
                ),
                encoding="utf-8",
            )
            brief = format_brief(
                draft=draft,
                genre="standard",
                hard_findings=[],
                profile_result=CommandResult(
                    command=[],
                    returncode=1,
                    stdout=profile_brief,
                    stderr="",
                ),
            )

        self.assertIn("style_repair_brief:", brief)
        self.assertNotIn("repair_mode: hard_pass_review_in_place", brief)

    def test_prepare_finalized_repair_brief_compact_ranges_accept_utf16_draft(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        profile_brief = finalized_profile_repair_brief()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-16")
            brief = format_brief(
                draft=draft,
                genre="standard",
                hard_findings=[],
                profile_result=CommandResult(
                    command=[],
                    returncode=1,
                    stdout=profile_brief,
                    stderr="",
                ),
            )

        self.assertIn("repair_mode: hard_pass_review_in_place", brief)
        self.assertIn("eligible_cluster_ranges: lines 3-6", brief)
        self.assertIn("protected_tail_range: lines 56-61", brief)

    def test_prepare_finalized_repair_brief_profile_tool_error_never_uses_compact_mode(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        profile_brief = finalized_profile_repair_brief()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-8")
            brief = format_brief(
                draft=draft,
                genre="standard",
                hard_findings=[],
                profile_result=CommandResult(
                    command=[],
                    returncode=2,
                    stdout=profile_brief,
                    stderr="profile tool failed after partial output",
                ),
            )

        self.assertIn("style_repair_brief:", brief)
        self.assertIn("status: unavailable", brief)
        self.assertIn("repair_mode: controller_tool_error", brief)
        self.assertNotIn("repair_mode: punctuation_source_reset", brief)
        self.assertNotIn("repair_mode: hard_pass_review_in_place", brief)

    def test_prepare_finalized_repair_brief_rejects_inconsistent_profile_schema(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, profile_result_valid

        valid_review = finalized_profile_repair_brief()
        invalid_briefs = (
            valid_review.replace("status: review", "status: nonsense"),
            valid_review.replace("repair_mode: punctuation_source_reset", "repair_mode: source_rewrite_required"),
        )
        for profile_brief in invalid_briefs:
            with self.subTest(profile_brief=profile_brief):
                self.assertFalse(
                    profile_result_valid(
                        CommandResult(command=[], returncode=1, stdout=profile_brief, stderr="")
                    )
                )

    def test_prepare_finalized_repair_brief_unsupported_review_mode_keeps_full_interface(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        profile_brief = finalized_profile_repair_brief(
            repair_mode="rhythm_source_reset",
            root_families="punctuation, line_rhythm, ngram_texture",
            next_action="Rebuild the whole page rhythm before local punctuation work.",
            source_actions=(
                "punctuation: let punctuation follow unfinished action.",
                "line_rhythm: rebuild the visible body as 6-8 line-broken clusters.",
            ),
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-8")
            brief = format_brief(
                draft=draft,
                genre="standard",
                hard_findings=[],
                profile_result=CommandResult(
                    command=[],
                    returncode=1,
                    stdout=profile_brief,
                    stderr="",
                ),
            )

        self.assertIn("hard_gate_status: pass", brief)
        self.assertIn("style_repair_brief:", brief)
        self.assertIn("repair_mode: rhythm_source_reset", brief)
        self.assertNotIn("repair_mode: hard_pass_review_in_place", brief)
        self.assertNotIn("in_place_contract:", brief)

    def test_prepare_finalized_repair_brief_incomplete_profile_review_keeps_full_interface(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        profile_brief = finalized_profile_repair_brief(source_actions=())
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-8")
            brief = format_brief(
                draft=draft,
                genre="standard",
                hard_findings=[],
                profile_result=CommandResult(
                    command=[],
                    returncode=1,
                    stdout=profile_brief,
                    stderr="",
                ),
            )

        self.assertIn("hard_gate_status: pass", brief)
        self.assertIn("style_repair_brief:", brief)
        self.assertIn("repair_mode: punctuation_source_reset", brief)
        self.assertNotIn("repair_mode: hard_pass_review_in_place", brief)

    def test_prepare_finalized_repair_brief_nonstandard_artifact_name_never_uses_compact_mode(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        profile_brief = finalized_profile_repair_brief()
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "article.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-8")
            brief = format_brief(
                draft=draft,
                genre="standard",
                hard_findings=[],
                profile_result=CommandResult(
                    command=[],
                    returncode=1,
                    stdout=profile_brief,
                    stderr="",
                ),
            )

        self.assertIn("style_repair_brief:", brief)
        self.assertIn("controller_warning: expected finalized artifact name draft.md, received article.md.", brief)
        self.assertNotIn("repair_mode: hard_pass_review_in_place", brief)

    def test_prepare_finalized_repair_brief_cli_rejects_nonstandard_artifact_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            finalized_dir = Path(temp) / "finalized"
            finalized_dir.mkdir()
            draft = finalized_dir / "article.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_FINALIZED_REPAIR_BRIEF),
                    str(draft),
                    "--genre",
                    "standard",
                    "--profile",
                    str(STYLE_PROFILE),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("expected finalized artifact name draft.md", result.stderr)
            self.assertFalse((finalized_dir / "repair-brief.txt").exists())

    def test_prepare_finalized_repair_brief_cli_rejects_output_overwriting_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            finalized_dir = Path(temp) / "finalized"
            finalized_dir.mkdir()
            draft = finalized_dir / "draft.md"
            draft.write_text(finalized_hard_pass_profile_review_sample(), encoding="utf-8")
            before_hash = hashlib.sha256(draft.read_bytes()).hexdigest()

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_FINALIZED_REPAIR_BRIEF),
                    str(draft),
                    "--genre",
                    "standard",
                    "--profile",
                    str(STYLE_PROFILE),
                    "--output",
                    str(draft),
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("repair brief output must not overwrite draft.md", result.stderr)
            self.assertEqual(hashlib.sha256(draft.read_bytes()).hexdigest(), before_hash)

    def test_prepare_finalized_repair_brief_resolves_relative_profile_before_external_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            finalized_dir = Path(temp) / "external-finalized"
            finalized_dir.mkdir()
            draft = finalized_dir / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 水龙头",
                        "",
                        "不是包装袋漏，是电动车前面那个篮子。",
                        *(["水龙头开小了还是溅出来。"] * 8),
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_FINALIZED_REPAIR_BRIEF),
                    str(draft),
                    "--genre",
                    "standard",
                    "--profile",
                    "references/style-profile.json",
                    "--json",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertNotEqual(payload["profile_returncode"], 2, payload)
            brief = (finalized_dir / "repair-brief.txt").read_text(encoding="utf-8")
            self.assertIn("repair_mode: source_rewrite_compact", brief)
            self.assertIn("profile_diagnostics: controller_only", brief)
            self.assertNotIn("Anlin style-profile repair brief", brief)
            self.assertNotIn("repair_mode: controller_tool_error", brief)

    def test_prepare_finalized_repair_brief_prioritizes_overfull_delete_merge_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            finalized_dir = Path(temp) / "finalized"
            finalized_dir.mkdir()
            draft = finalized_dir / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 水龙头没关严",
                        "",
                        *(["手机又响了一下，我把扳手从柜子里拖出来，袖口蹭到黑灰，"] * 95),
                        "不是项目赶，是支付页把话替我说完了。",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_FINALIZED_REPAIR_BRIEF),
                    str(draft),
                    "--genre",
                    "standard",
                    "--profile",
                    "references/style-profile.json",
                    "--json",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            brief = (finalized_dir / "repair-brief.txt").read_text(encoding="utf-8")
            self.assertIn("hard_gate_primary_action: thin_overfull_fragment_slate", brief)
            self.assertIn("source_focus: remove repeated proof", brief)
            self.assertIn("do not add material, a new scene, or a new explanation", brief)
            self.assertIn("do not close every row with a period", brief)
            self.assertNotIn("hard_gate_blockers:", brief)
            self.assertNotIn("Anlin style-profile repair brief", brief)

    def test_prepare_finalized_repair_brief_prioritizes_period_grid_after_overfull_repair(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            finalized_dir = Path(temp) / "finalized"
            finalized_dir.mkdir()
            draft = finalized_dir / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 水龙头没关严",
                        "",
                        *(["我坐在厨房地上看手机，水龙头还滴着。"] * 55),
                        "手上的水滴到屏幕上，那个字被按成长条，像哭出来的一笔。",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_FINALIZED_REPAIR_BRIEF),
                    str(draft),
                    "--genre",
                    "standard",
                    "--profile",
                    "references/style-profile.json",
                    "--json",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            brief = (finalized_dir / "repair-brief.txt").read_text(encoding="utf-8")
            self.assertIn("hard_gate_primary_action: preserve_boundary_mass_replace_weak_fragment", brief)
            self.assertIn("shape_contract: preserve the incoming line-broken surface", brief)
            self.assertIn("do not apply a page-wide comma or period transformation", brief)
            self.assertNotIn("hard_gate_blockers:", brief)
            self.assertNotIn("Anlin style-profile repair brief", brief)

    def test_prepare_finalized_repair_brief_prioritizes_social_decline_engine_over_period_grid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            finalized_dir = Path(temp) / "finalized"
            finalized_dir.mkdir()
            draft = finalized_dir / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 水龙头没关严",
                        "",
                        "晚上十一点多，厨房地上湿了一片。",
                        "狗哥问婚礼来不来，高铁票看了没有。",
                        "我说去不了，随礼红包先转，恭喜恭喜。",
                        "狗哥回得快，发了个抱拳。",
                        *(["我坐在厨房地上看手机，水龙头还滴着。"] * 56),
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_FINALIZED_REPAIR_BRIEF),
                    str(draft),
                    "--genre",
                    "standard",
                    "--profile",
                    "references/style-profile.json",
                    "--json",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            brief = (finalized_dir / "repair-brief.txt").read_text(encoding="utf-8")
            self.assertIn("hard_gate_primary_action: repair_refusal_fragment_relation", brief)
            self.assertIn("source_focus: replace the earliest broken invitation/refusal fragment relation", brief)
            self.assertNotIn("one refusal-coupled consequence", brief)
            self.assertIn("do not add a new scene, witness, route, or message chain", brief)
            self.assertIn("mass_contract: keep the revised article close", brief)
            self.assertNotIn("hard_gate_blockers:", brief)
            self.assertNotIn("Anlin style-profile repair brief", brief)

    def test_finalized_repair_brief_routes_standard_mass_before_social_family(self) -> None:
        from prepare_finalized_repair_brief import CommandResult, format_brief

        cases = [
            (568, "标准日寄完整文章篇幅偏短", "rebuild_severely_underbuilt_fragment"),
            (875, "标准日寄完整文章篇幅缓冲不足", "replace_underbuilt_fragment"),
            (913, None, "preserve_boundary_mass_replace_weak_fragment"),
        ]

        for body_chars, length_rule, route in cases:
            with self.subTest(body_chars=body_chars):
                with tempfile.TemporaryDirectory() as temp:
                    draft = Path(temp) / "draft.md"
                    draft.write_text("去不了\n\n" + ("我" * body_chars), encoding="utf-8")
                    findings = [
                        {
                            "severity": "error",
                            "rule": "strict: 社交拒绝纹理替代后果不足",
                            "excerpt": "reply aftermath stayed private",
                            "suggestion": "replace the room loop with a refusal-coupled next action",
                        }
                    ]
                    if length_rule is not None:
                        findings.append(
                            {
                                "severity": "error",
                                "rule": f"strict: {length_rule}",
                                "excerpt": f"body_chinese_chars={body_chars}",
                                "suggestion": "扩展具体动作、对话、身体/金钱后果和非主题残留，增加行动链、社交误伤和无用日常残留。",
                            }
                        )
                    brief = format_brief(
                        draft=draft,
                        genre="standard",
                        hard_findings=findings,
                        hard_returncode=1,
                        profile_result=CommandResult(command=[], returncode=2, stdout="", stderr="unavailable"),
                    )

                self.assertIn(f"hard_gate_primary_action: {route}", brief)
                if body_chars < 650:
                    self.assertIn("scope_contract: rebuild the existing incomplete article", brief)
                    self.assertIn("mass_contract: preserve a complete article", brief)
                else:
                    self.assertIn("scope_contract: choose the earliest existing local fragment relation", brief)
                    self.assertIn("mass_contract: keep the revised article close", brief)
                self.assertNotIn("扩展具体动作", brief)
                self.assertNotIn("增加行动链", brief)
                self.assertNotIn("无用日常残留", brief)

        for weak_rule in ("标准日寄长行缓冲不足", "标准日寄句号网格"):
            with self.subTest(body_chars=913, weak_rule=weak_rule):
                with tempfile.TemporaryDirectory() as temp:
                    draft = Path(temp) / "draft.md"
                    draft.write_text("去不了\n\n" + ("我" * 913), encoding="utf-8")
                    brief = format_brief(
                        draft=draft,
                        genre="standard",
                        hard_findings=[
                            {
                                "severity": "error",
                                "rule": f"strict: {weak_rule}",
                                "excerpt": "source shape stayed weak",
                                "suggestion": "repair the weak shape",
                            }
                        ],
                        hard_returncode=1,
                        profile_result=CommandResult(command=[], returncode=2, stdout="", stderr="unavailable"),
                    )

                self.assertIn("hard_gate_primary_action: preserve_boundary_mass_replace_weak_fragment", brief)
                self.assertIn("mass_contract: keep the revised article close", brief)

    @unittest.skip("superseded by finalized fragment-brief and controller-boundary tests")
    def test_finalized_repair_docs_route_profile_brief_and_full_report_separately(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        finalized_minimum = (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8")
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        layer = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            "check_anlin_violations.py draft.md --strict --draft-gate --genre <selected-genre>",
            runtime,
        )
        self.assertIn("prepare_finalized_repair_brief.py", validation)
        self.assertIn("repair-brief.txt", runtime)
        self.assertIn("full `check_style_profile.py draft.md --draft-gate --strict --genre <selected-genre>` report", runtime)
        for text in (skill, runtime, finalized_minimum, validation, layer):
            self.assertIn("draft.md", text)
        for text in (skill, finalized_minimum, validation, readme):
            self.assertIn("--repair-brief", text)
        for text in (skill, runtime, finalized_minimum, layer):
            self.assertIn("terminal", text.lower())
        self.assertIn("The repair brief is the generator-facing interface", validation)
        self.assertIn("the repair agent reads `draft.md` plus `repair-brief.txt`", validation)
        self.assertIn("After the finalized artifact is frozen", validation)
        self.assertIn("without `--repair-brief` for the full report", validation)
        self.assertIn("full profile metrics remain controller evidence after the artifact is frozen", layer)
        self.assertIn("Terminal/log-only final prose is an artifact failure", (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8"))
        self.assertIn("terminal-only prose is an artifact failure", runtime)
        self.assertIn("Do not print a proposed final article to the terminal and keep thinking", finalized_minimum)
        self.assertIn("first write to `draft.md` must be the final complete revision", finalized_minimum)
        self.assertIn("Do not write the old draft back as a placeholder", finalized_minimum)
        self.assertIn("Do not rediscover this skill by globbing", finalized_minimum)
        self.assertIn("reasoning aloud about how to find the skill directory", finalized_minimum)
        self.assertIn("If `repair-brief.txt` is absent, do not search for checker scripts", finalized_minimum)
        self.assertIn("Do not use TODO tools, checklist panels, plans, or long diagnostic narration", finalized_minimum)
        self.assertIn("one complete source rewrite after the not-pass brief, writes the artifact, and stops", finalized_minimum)
        self.assertIn("A second `Write draft.md` or `Edit draft.md` in the same finalized attempt is invalid", finalized_minimum)
        self.assertIn("copying the current draft back unchanged", runtime)
        self.assertIn("After writing `draft.md`, stop on artifact persisted", finalized_minimum)
        self.assertIn("The single write is atomic", finalized_minimum)
        self.assertIn("do not patch it with `Edit draft.md`", finalized_minimum)
        self.assertIn("Do not run `check_anlin_violations.py`, `check_style_profile.py`, `clean_run_checker.py`", finalized_minimum)
        self.assertIn("`python -c`, `Measure-Object`, `wc`, `Get-Content` length probes", finalized_minimum)
        self.assertIn("Because the single write is atomic, do a visible body-shape check before saving", finalized_minimum)
        self.assertIn("75-80+ body lines", finalized_minimum)
        self.assertIn("45-70 short caption rows with zero true long rows", finalized_minimum)
        self.assertIn("beyond about 24 Chinese characters", finalized_minimum)
        self.assertIn("almost every line trailing with `，` and almost no landed `。`", finalized_minimum)
        self.assertIn("8-25 dense prose rows", finalized_minimum)
        self.assertNotIn("should usually become 6-8 visible breathing clusters", finalized_minimum)
        self.assertIn("split the draft into tiny rows", finalized_minimum)
        self.assertIn("Room-only water, wet sleeves, wet pants, wet slippers", finalized_minimum)
        self.assertIn("A public hinge is not the same as a cameo", finalized_minimum)
        self.assertIn("only one or two rows carrying speech/action/thought movement", finalized_minimum)
        self.assertIn("Line-final comma is not the goal either", finalized_minimum)
        self.assertIn("650-899 body Chinese characters", finalized_minimum)
        self.assertIn("Door threshold imagery alone does not count", finalized_minimum)
        self.assertIn("A 45-70-line corridor is not a target count", finalized_minimum)
        self.assertIn("If the planned local rewrite would leave zero obvious long rows, only one or two rows carrying", finalized_minimum)
        self.assertIn("53 short rows and 580 body characters", finalized_minimum)
        self.assertIn("8-15 long paragraphs", finalized_minimum)
        self.assertIn("15-line \"better story\"", finalized_minimum)
        self.assertIn("Do not repair social-decline message surfaces by enumerating message order", finalized_minimum)
        self.assertIn("`第二条只...`", finalized_minimum)
        self.assertIn("`下面还有一个...`", finalized_minimum)
        self.assertIn("If a standard-diary hard gate reports `粗粝自毁信号不足`", finalized_minimum)
        self.assertIn("message -> calculation -> refusal -> he said OK -> room object", finalized_minimum)
        self.assertIn("choose one primary source rewrite from the brief", runtime)
        self.assertIn("Hard-gate findings outrank profile-family repair", runtime)
        self.assertIn("The finalized rewrite is atomic", runtime)
        self.assertIn("80+ one-sentence rows", runtime)
        self.assertIn("reject a comma carpet", runtime)
        self.assertIn("If `repair-brief.txt` is absent, do not search for scripts or ask how to run gates", runtime)
        self.assertIn("`Test-Path`, glob/list/path probes", runtime)
        self.assertIn("A neighbor/cashier/rider cameo is not a public hinge", runtime)
        self.assertIn("the repair agent writes the artifact; only the controller validates it", validation)
        self.assertIn("post-write python -c/Measure-Object/wc counters", layer)
        self.assertIn("post-write `python -c`, `Measure-Object`, `wc`", readme)
        self.assertIn("local line/character counters", readme)
        self.assertIn("mostly one short sentence per row", (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8"))
        self.assertIn("8-25 dense prose rows", (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8"))
        self.assertIn("45-70-line caption grid", layer)
        self.assertIn("has almost every line trailing with `，` and almost no landed `。`", finalized_minimum)

    def test_finalized_reference_routing_keeps_both_compact_modes_brief_only(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(
            "| Finalized repair checkpoint | `repair-brief.txt` only for `hard_pass_review_in_place` or `source_rewrite_compact`;",
            skill,
        )
        self.assertNotIn(
            "| Finalized repair checkpoint | `repair-brief.txt` only for `hard_pass_review_in_place`; otherwise",
            skill,
        )

    @unittest.skip("superseded by fragment rhythm and witness regression tests")
    def test_runtime_source_docs_guard_comma_carpet_and_public_hinge_cameos(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        source = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        finalized_minimum = (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8")
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        layer = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, source, runtime, finalized_minimum, validation, layer, readme])

        self.assertIn("comma carpet", combined)
        self.assertIn("almost no landed `。`", combined)
        self.assertIn("neutral question about the heater", clean)
        self.assertIn("neutral question about a heater", source)
        self.assertIn("does not touch the wet/dirty/payment/reply/body fact", source)
        self.assertIn("does not touch the wet/dirty/payment/reply/body fact", clean)
        self.assertIn("neighbor light under the door", combined)
        self.assertIn("threshold atmosphere", combined)
        self.assertIn("75-80+ body lines", (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8"))
        self.assertIn("do not mistake private wet texture for rough exposure", runtime)
        self.assertIn("16-25 dense rows", (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8"))
        self.assertIn("A second `Write draft.md` or `Edit draft.md` in the same finalized attempt is invalid controller evidence", runtime)
        self.assertIn("When multiple families appear, do not make one patch per family", finalized_minimum)
        self.assertIn("makes one complete source rewrite, persists `finalized/draft.md`, and stops", validation)
        self.assertIn("a post-write repair-agent gate loop, post-write `python -c`", validation)
        self.assertIn("or explicit threshold arithmetic in the same finalized attempt", validation)
        self.assertIn("post-write repair-agent gate loop", layer)
        self.assertIn("If the revised article is only printed in a log/chat but `draft.md` is unchanged", finalized_minimum)
        self.assertIn("prints a repaired article to chat or a log but leaves that file unchanged", validation)
        self.assertIn("finalized/draft.md", combined)
        self.assertIn("10-18-character captions", combined)
        self.assertIn("24 Chinese characters", combined)
        self.assertIn("45-70-line caption grid", layer)
        self.assertIn("nonzero, treat that as a normal not-pass signal, not a broken tool", runtime)
        self.assertIn("full profile report after the artifact is frozen", readme)

    def test_style_profile_review_with_red_punctuation_gets_source_reset_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 洗到一半",
                        "",
                        *(["水龙头开小了还是溅出来。"] * 52),
                    ]
                ),
                encoding="utf-8",
            )
            yellow_summary = {
                "min": 0.0,
                "q05": 0.0,
                "q10": 0.0,
                "median": 0.0,
                "q90": 0.0,
                "q95": 0.0,
                "max": 100000.0,
                "mean": 0.0,
                "mad": 0.0,
            }
            red_summary = dict(yellow_summary)
            red_summary["max"] = 0.0
            profile = Path(temp) / "profile.json"
            profile.write_text(
                json.dumps(
                    {
                        "version": "test",
                        "corpus_file_count": 38,
                        "expected_corpus_count": 38,
                        "value_summary": {
                            "body_chars": yellow_summary,
                            "title_chars": yellow_summary,
                            "line_mean_chars": yellow_summary,
                            "paragraph_blocks": yellow_summary,
                            "punct_period_per_1k": red_summary,
                        },
                        "value_families": {
                            "body_chars": "length",
                            "title_chars": "title",
                            "line_mean_chars": "line_rhythm",
                            "paragraph_blocks": "structure",
                            "punct_period_per_1k": "punctuation",
                        },
                        "count_summary": {},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["summary"]["status"], "review")
            self.assertIn("punctuation", report["summary"]["red_families"])
            self.assertEqual(report["summary"]["repair_mode"], "punctuation_source_reset")
            self.assertIn("Punctuation is a source-shape problem", report["summary"]["next_repair_action"])
            self.assertIn("one-period-per-row grids", report["summary"]["next_repair_action"])

    def test_style_profile_nonstandard_fallback_is_inconclusive_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(
                "\n".join(
                    [
                        "# 不想祝我妈母亲节快乐",
                        "",
                        "我妈发消息问我吃没吃饭。",
                        "我说吃了，其实泡面还没拆。",
                        "窗台上那个塑料袋被风吹了一下。",
                        "我看了半天，最后把手机扣过去。",
                    ]
                ),
                encoding="utf-8",
            )
            profile = Path(temp) / "profile.json"
            yellow_summary = {
                "min": 0.0,
                "q05": 0.0,
                "q10": 0.0,
                "median": 0.0,
                "q90": 0.0,
                "q95": 0.0,
                "max": 100000.0,
                "mean": 0.0,
                "mad": 0.0,
            }
            profile_payload = {
                "version": "test",
                "corpus_file_count": 38,
                "expected_corpus_count": 38,
                "value_summary": {
                    "body_chars": yellow_summary,
                    "title_chars": yellow_summary,
                    "line_mean_chars": yellow_summary,
                    "paragraph_blocks": yellow_summary,
                    "punct_period_per_1k": yellow_summary,
                },
                "value_families": {
                    "body_chars": "length",
                    "title_chars": "title",
                    "line_mean_chars": "line_rhythm",
                    "paragraph_blocks": "structure",
                    "punct_period_per_1k": "punctuation",
                },
                "count_summary": {},
                "strata": {
                    "genre": {
                        "sincere": {
                            "document_count": 2,
                            "value_summary": {},
                            "value_families": {},
                            "count_summary": {},
                        }
                    }
                },
            }
            profile.write_text(json.dumps(profile_payload, ensure_ascii=False), encoding="utf-8")

            global_result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--strict",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(global_result.returncode, 0)
            global_report = json.loads(global_result.stdout)
            self.assertEqual(global_report["summary"]["status"], "review")
            self.assertTrue(global_report["summary"]["profile_gate_applicable"])

            sincere_result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--strict",
                    "--genre",
                    "sincere",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(sincere_result.returncode, 0)
            sincere_report = json.loads(sincere_result.stdout)
            self.assertEqual(sincere_report["profile_scope"]["scope"], "global")
            self.assertTrue(sincere_report["profile_scope"]["fallback"])
            self.assertIn("genre:sincere: document_count=2 < 4", sincere_report["profile_scope"]["skipped"])
            self.assertEqual(sincere_report["summary"]["status"], "inconclusive")
            self.assertEqual(sincere_report["summary"]["checkpoint_decision"], "profile_inconclusive_fallback")
            self.assertFalse(sincere_report["summary"]["checkpoint_pass"])
            self.assertFalse(sincere_report["summary"]["profile_gate_applicable"])
            self.assertEqual(sincere_report["summary"]["repair_mode"], "matched_placebo_required")
            self.assertIn("matched-original placebo", sincere_report["summary"]["next_repair_action"])

            text_result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_PROFILE),
                    str(draft),
                    "--profile",
                    str(profile),
                    "--draft-gate",
                    "--strict",
                    "--genre",
                    "sincere",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(text_result.returncode, 0)
            self.assertIn("formal_gate: not_pass", text_result.stdout)
            self.assertIn("Do not call the article clean", text_result.stdout)
            self.assertIn("profile_gate_applicable: false", text_result.stdout)

    def test_merge_short_lines_reduces_generated_line_grid(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                *(["我坐着看杯子又亮了，", "屏幕又震了一下。", "我没动。"] * 40),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(MERGE_SHORT_LINES),
                    str(draft),
                    "--in-place",
                    "--target-lines",
                    "65",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertLessEqual(report["merged_body_lines"], 65)
            self.assertGreaterEqual(report["lines_ge24"], 6)
            merged_text = draft.read_text(encoding="utf-8")
            self.assertTrue(merged_text.startswith("# 日寄"))

    def test_soften_line_endings_repairs_over_closed_first_twenty_lines(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                *(["我坐着看杯子又亮了，屏幕又震了一下。"] * 30),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SOFTEN_LINE_ENDINGS),
                    str(draft),
                    "--in-place",
                    "--target-ratio",
                    "0.55",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertLess(report["before_ratio"], 0.45)
            self.assertGreaterEqual(report["after_ratio"], 0.55)
            checker = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(checker.stdout)
            self.assertFalse(any("行末逗号比例" in item["rule"] for item in findings))

    def test_soften_line_endings_rebalances_over_comma_first_twenty_lines(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                *(["我坐着看杯子又亮了，"] * 30),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SOFTEN_LINE_ENDINGS),
                    str(draft),
                    "--in-place",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertGreater(report["before_ratio"], 0.85)
            self.assertLessEqual(report["after_ratio"], 0.85)
            checker = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(checker.stdout)
            self.assertFalse(any("行末逗号比例" in item["rule"] for item in findings))

    def test_soften_line_endings_adds_commas_to_unpunctuated_early_lines(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                *(["我坐着看杯子又亮了"] * 30),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SOFTEN_LINE_ENDINGS),
                    str(draft),
                    "--in-place",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["before_ratio"], 0.0)
            self.assertGreaterEqual(report["after_ratio"], 0.55)
            checker = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(checker.stdout)
            self.assertFalse(any("行末逗号比例" in item["rule"] for item in findings))

    def test_split_long_lines_repairs_over_compressed_generated_lines(self) -> None:
        long_line = (
            "我摸了摸手机，六条未读，三条是运营商的催缴短信，两条是前同事群的消息，还有一条是妈的，"
            "她说你也老大不小了，我没点开听，直接把手机扣在桌上。"
        )
        body = "\n".join(["# 日寄", "", *([long_line] * 12)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SPLIT_LONG_LINES),
                    str(draft),
                    "--in-place",
                    "--target-lines",
                    "50",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertGreater(report["split_body_lines"], report["original_body_lines"])
            self.assertGreaterEqual(report["split_body_lines"], 24)

    def test_split_long_lines_defaults_repair_clean_run_paragraph_compression(self) -> None:
        long_lines = [
            "电动车钥匙插进去的时候，我才发现后座的蛇皮袋没扎紧，中午剩的西红柿滚了一个到路边。我弯腰去捡的时候，脖子后面的汗蹭到了衣领，黏得人想把短袖脱了扔了。我爸在厨房窗户那喊，汤要热第二遍啊，我说好，汤洒到地砖上滑了我一下，差点把碗摔了。",
            "我妈把筷子搁在碗沿上问我，最近天天往外面跑，到底忙些啥呢。我扒拉一口饭说，改那个纸头，投了几个地方。她说投哪的，我说都有，有几个流程在走在面试。其实流程在走的那两个，上周已经给我发那个不匹配的邮件了，我手机里的垃圾短信比她发的养生链接还多。",
            "我爸突然插嘴说隔壁陈叔的儿子考选调试上了，说那小子毕业就一直在考，头两年都没有上班。我哦了一声，扒拉最后两口饭，嘴里还塞着饭就说吃饱了骑车回去，晚上还有个活要干。那个活其实是我约的帮忙搬东西的顺风车单，把一台洗衣机扛上三楼，能挣八十块钱。",
            "骑到半路闻到烧烤味，有人往地上泼了一泼泔水，我的车胎碾过去的时候滑了一下，手把差点没握住，我骂了一句，裤子屁股那里蹭到了车座上的灰，怎么拍都拍不干净。前面路口的红绿灯在闪黄，这是去我租房那个方向的灯，好像和我小时候去小学那个路口的是一个。",
            "小学的时候我总觉得那个路口特别大，过马路要跑着走，还要被我妈拽着书包带，她总怕我被车撞。现在走到这里的时候我发现，那条路窄得要并排走两辆电动车都费劲，连个人行道线都描得模模糊糊，被外卖小哥的车轮碾得只剩个印子。",
            "到租房楼下的时候，顺风车单取消了，说那个人自己找了货拉拉，不用我去了。我把电动车停好，拔了钥匙算了算今天的账，汤喝了两碗，没花钱，白跑一趟少挣八十块，手机里又多了三条招人的推送，都是招推销的，底薪三千五，抽成另算。",
            "上楼的时候楼道里的声控灯又坏了，我摸黑爬了三层楼，脚踢到了门口的快递盒，里面是我买的便宜洗面奶，寄过来盖子都漏了，蹭得盒子里全是白色的膏体。钥匙插锁孔的时候划了一下手，没出血，就是有点疼，疼得我把钥匙都掉地上了。",
            "开门后我先坐在床边没开灯，窗外的路灯照进来，照到桌面的简历打印版，纸张边角都卷了，我拿起来看了一眼，上面写的会的东西其实也就那样，到了估计也用不上。突然想起我妈问我在忙啥的时候，我其实想说我在想下个月的房租怎么凑，在想这个月的电费还没交。",
            "算了，先去洗个脸，明天再改一版简历吧，这次多写点会的东西，反正面试的时候也不会问，大家走个流程，就像那个闪黄灯的红绿灯一样，大家慢慢蹭过去，谁也别停，停了后面还有人按喇叭。",
            "洗面奶挤多了，弄到眼睛里，疼得我差点把镜子砸了，用凉水冲了好一会才舒服点。我擦脸的时候想，明天再跑两个吧，不管能不能面上，先把流程走了，万一呢？虽然大概率也没啥用，不过总比在家坐着听他们聊别人家孩子强。",
            "毛巾有点硬，蹭得脸疼，算了，睡了。",
        ]
        body = "\n".join(["# 日寄", "", *long_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SPLIT_LONG_LINES),
                    str(draft),
                    "--in-place",
                    "--target-lines",
                    "58",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertGreaterEqual(report["split_body_lines"], 45)
            self.assertLessEqual(report["split_body_lines"], 70)
            checker = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(checker.stdout)
            line_rules = [
                "标准日寄行数缓冲异常",
                "标准日寄长行过密",
                "散文块压缩",
            ]
            self.assertFalse(
                any(any(rule in item["rule"] for rule in line_rules) for item in findings),
                [item["rule"] for item in findings],
            )

    def test_rebalance_line_rhythm_repairs_short_grid_without_prose_compression(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                *(
                    [
                        "我坐着",
                        "屏幕亮了",
                        "杯子没洗",
                        "我没动",
                        "楼下很吵",
                    ]
                    * 22
                ),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(REBALANCE_LINE_RHYTHM),
                    str(draft),
                    "--in-place",
                    "--target-min-lines",
                    "45",
                    "--target-max-lines",
                    "70",
                    "--preferred-lines",
                    "58",
                    "--min-long-lines",
                    "6",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            after = report["after"]
            self.assertGreaterEqual(after["body_lines"], 45)
            self.assertLessEqual(after["body_lines"], 70)
            self.assertGreaterEqual(after["long_lines"], 6)
            self.assertNotIn("still_prose_compressed", report["unresolved"])

    def test_rebalance_line_rhythm_repairs_prose_blocks_without_short_grid(self) -> None:
        long_line = (
            "手机电量从百分之三十七掉到二十八，我把充电线按在接口上，手指按得发酸，"
            "室友在旁边问我是不是还没吃饭，我说吃了，其实只吃了半个冷包子，胃里像有个塑料袋。"
        )
        body = "\n".join(["# 日寄", "", *([long_line] * 16)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(REBALANCE_LINE_RHYTHM),
                    str(draft),
                    "--in-place",
                    "--target-min-lines",
                    "45",
                    "--target-max-lines",
                    "70",
                    "--preferred-lines",
                    "58",
                    "--min-long-lines",
                    "6",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            after = report["after"]
            self.assertGreaterEqual(after["body_lines"], 45)
            self.assertLessEqual(after["body_lines"], 70)
            self.assertGreaterEqual(after["long_lines"], 6)
            self.assertLess(after["mean_line_chars"], 30)
            self.assertNotIn("still_prose_compressed", report["unresolved"])

    def test_rebalance_line_rhythm_preserves_existing_paragraph_blocks(self) -> None:
        paragraph = [
            "手机电量从百分之三十七掉到二十八，我把充电线按在接口上，手指按得发酸。",
            "楼下有人喊小孩回家吃饭，小孩没应，我跟着停了一下。很丢人。",
        ]
        body = "\n\n".join(["\n".join(paragraph) for _ in range(5)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("# 生瓜\n\n" + body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(REBALANCE_LINE_RHYTHM),
                    str(draft),
                    "--in-place",
                    "--target-min-lines",
                    "20",
                    "--target-max-lines",
                    "70",
                    "--preferred-lines",
                    "35",
                    "--min-long-lines",
                    "4",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = draft.read_text(encoding="utf-8").replace("\r\n", "\n")
            body_after = output.split("\n\n", 1)[1].strip()
            blocks = [block for block in re.split(r"\n\s*\n", body_after) if block.strip()]
            self.assertGreaterEqual(len(blocks), 5)

    def test_rebalance_line_rhythm_splits_existing_short_breaths_from_uniform_rows(self) -> None:
        unit = [
            "我把饭盒挂在车把上，塑料袋一直蹭着手腕。其实会。",
            "路口的灯牌亮得很正经，好像比我更像一个人。很丢人。",
            "我低头看裤脚那块菜汤，它已经干成一小块地图。没有人记。",
        ]
        body = "\n".join(["# 路口寄", "", *(unit * 18)])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(REBALANCE_LINE_RHYTHM),
                    str(draft),
                    "--in-place",
                    "--target-min-lines",
                    "45",
                    "--target-max-lines",
                    "70",
                    "--preferred-lines",
                    "58",
                    "--min-long-lines",
                    "6",
                    "--min-short-breaths",
                    "4",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            after = report["after"]
            self.assertGreaterEqual(after["body_lines"], 45)
            self.assertLessEqual(after["body_lines"], 70)
            self.assertGreaterEqual(after["short_breath_lines"], 4)
            self.assertNotIn("short_breath_lines_below_corridor", report["unresolved"])

    def test_checker_accepts_low_body_roughness_as_self_damage_signal(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "牙齿塞了一根韭菜。",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    def test_checker_accepts_dirty_foot_stomach_and_status_damage_as_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 凉水日寄",
                "",
                "我低头看见大脚趾头露在外面，尴尬地缩了缩脚趾，",
                "中午又拉了两回肚子，憋都憋不住，",
                "路口那一下腿一软差点跪在地上，好像我是碰瓷的，",
                *(["其实我觉得杯子有点脏，洗的时候水龙头咳了一下喷到裤子上，"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    def test_checker_accepts_lockout_practical_failure_as_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 胶带",
                "",
                "我试了试用一张没用的废卡插进门缝里想撬开，卡太软了，弯了一下就从中间断了。",
                "站起来的时候膝盖响了一声，楼道里听得清清楚楚。",
                "对门那个中年女的看到我的时候脚步顿了一下。",
                "我站在门口，手里捏着胶带和一张断掉的卡。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    def test_checker_accepts_visible_grime_as_low_status_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 小票",
                "",
                "指甲缝里都是灰，刚才拆胶带的时候划了一道口子，",
                "裤子后面全是灰，在走廊灯下面看得很清楚。",
                "收银员扫完水以后看了我一眼，又看了一眼我的手。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    def test_checker_accepts_ordinary_mess_as_low_status_rough_and_engine_signal(self) -> None:
        body = "\n".join(
            [
                "# 抽屉",
                "",
                "到门口才发现拖鞋穿反了。",
                "打了个喷嚏，鼻涕差点出来，只好用手背擦。",
                "手背上有灰，黑黑的，就在裤腿上蹭。",
                "水槽里掏出一坨头发，黏糊糊的，甩了两下甩不掉。",
                "袜子脚后跟磨了个洞，大拇指快顶出来了。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings))

    def test_checker_accepts_public_body_noise_and_dirty_hand_reaction_as_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 东窗",
                "",
                "五金店里很安静，站起来的时候胃响了一声，老板抬头看了看我。",
                "找零的时候他手碰到我的手，全是拆箱子的灰，他拿纸巾擦了擦手才把零钱推过来。",
                "我假装没听见。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings))

    def test_checker_accepts_public_payment_spill_as_rough_and_engine_signal(self) -> None:
        body = "\n".join(
            [
                "# 外机",
                "",
                "门铃又响了一下，我拖着脚挪到门口。",
                "外卖员站在楼梯口没走，手机举着等我扫码。",
                "我一手拎袋子一手掏手机，提手断了，粥淌到手上。",
                "手机卡了一下，没扫上，他又站了一会儿。",
                "我再扫了一次，这次响了。",
                "回去的时候踩到粥，拖鞋打滑，差点摔，扶着墙站住。",
                *(["水龙头在厨房响了一下，杯子边上有水，窗帘半挂着，脚趾又抽了一下。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings), findings)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings), findings)

    def test_checker_accepts_public_oil_stain_seen_by_rider_as_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 油花",
                "",
                "骑手站在单元门口，手上拎着塑料袋。",
                "我换了个手拎，袋子歪了一下，汤从盖子缝渗出来，滴在裤腿上。",
                "骑手的视线跟着那滴油落到裤子上。",
                "我拿手去蹭那块湿的地方，油已经渗进去了，越抹越大。",
                "手机卡了一下没扫上，他又站在门口等了一会儿。",
                "楼道门口那点汤被我踩到，拖鞋打滑，扶了一下墙才站稳。",
                *(["水龙头在厨房响了一下，杯子边上有水，窗帘半挂着，脚趾又抽了一下。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings), findings)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings), findings)

    def test_checker_accepts_hallway_aunt_dirty_sleeve_as_rough_and_engine_signal(self) -> None:
        body = "\n".join(
            [
                "# 堵住的下水口",
                "",
                "我用旧牙刷去戳下水口，袖口粘了一块黑东西。",
                "门外有人敲，我拎着垃圾袋出去，垃圾袋先漏了。",
                "楼道里的阿姨停在半层，说你这个袋子破了，地上都是汤。",
                "我蹲下去擦，袖口那块黑印蹭到墙角，留了一道灰。",
                "阿姨把青菜换到另一只手，等着我让路，又说你别拿袖子擦，越擦越黑。",
                "我嗯了一声，更不知道手该放哪。",
                "她又指了一下门，说你先关上吧，味道出来了。",
                "我说好，声音有点小。",
                *(["不过水龙头咳了一下，我发现杯子边上还有油，因为手指一直黏着。"] * 30),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings), findings)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings), findings)

            clean_draft = Path(temp) / "clean-draft.md"
            clean_draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(clean_draft)
            self.assertFalse(any(message.startswith("private_grime_without_public_consequence=") for message in messages), messages)
            self.assertFalse(any(message.startswith("rough_self_damage=missing") for message in messages), messages)

    def test_checker_accepts_public_waterline_sock_exposure_as_rough_and_engine(self) -> None:
        body = "\n".join(
            [
                "# 没拧紧",
                "",
                "热水器又跳了一下，",
                "我把花洒举到耳朵边，听里面那点水晃来晃去。",
                "手机亮着，有个老同学发来一句，下个月我结婚，你能来就来。",
                "我穿着湿拖鞋去开门，裤脚贴在脚踝上。",
                "隔壁阿姨拎着垃圾站在外面，往我脚下一指，说你这水都到门外了，她要从这边过。",
                "我低头看见一条水线从浴室拖到玄关，弯到她鞋边。",
                "抹布一时找不到，只好把盆里那只湿袜子捞出来，按在门槛上来回蹭。",
                "我说马上好，声音比她手里的垃圾袋还瘪。",
                "关门以后拿手机，手背蹭到鞋底的灰，屏幕上留了一道黑印。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 28),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings), findings)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings), findings)

            clean_draft = Path(temp) / "clean-draft.md"
            clean_draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(clean_draft)
            self.assertFalse(any(message.startswith("rough_self_damage=missing") for message in messages), messages)

    def test_checker_does_not_count_private_waterline_sock_cleanup_as_public_engine(self) -> None:
        body = "\n".join(
            [
                "# 没拧紧",
                "",
                "热水器又跳了一下，",
                "我低头看见一条水线从浴室拖到玄关。",
                "抹布一时找不到，只好把盆里那只湿袜子捞出来，按在门槛上来回蹭。",
                "手机亮着，有个老同学发来一句，下个月我结婚，你能来就来。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("段落发动机信号偏弱" in item["rule"] for item in findings), findings)

    def test_checker_counts_rider_paper_exchange_as_paragraph_engine(self) -> None:
        body = "\n".join(
            [
                "# 门口",
                "",
                "我还以为袋子只是热，拎起来才发现汤从角上慢慢漏出来，",
                "骑手问我有没有纸，我手在口袋里摸了一下，空的，",
                "他等了两秒才松手，系统里倒是已经显示送达，",
                *(["不过我还是把碗端到桌上，因为水龙头咳了一下，门口那块油印还在往外扩。"] * 30),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings), findings)

    def test_checker_counts_rider_manager_and_rent_chain_as_public_engine(self) -> None:
        body = "\n".join(
            [
                "# 楼下那张红纸",
                "",
                "门铃响的时候，门口站着骑手，手套上全是油，递过来的袋子已经有点洇。",
                "我伸手去接，他没收手。",
                "问了一句是不是备注不要香菜那个。",
                "我说嗯，他这才把袋子递过来。",
                "他没走，说我下去给你拿点纸上来。",
                "我赶紧说不用，已经把门关上了。",
                "楼管在二楼拐角比着红纸，说裤子前头沾了油，回去拿点洗洁精擦擦，你这是要扔？一起扔了得了。",
                "我点头，把袋子递过去。",
                "他顺手接过，又低头去看那张红纸。",
                "屏幕亮一下，是房东的微信，房租又该交，催了一下。",
                "我点开看了看，没回，把手机扣在桌上。",
                *(["不过我还是把碗端到桌上，因为水龙头咳了一下，门口那块油印还在往外扩。"] * 26),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings), findings)
            self.assertFalse(any(item["rule"] == "纹理替代社交不足" for item in findings), findings)

    def test_checker_does_not_count_oil_stain_glance_without_consequence_as_rough(self) -> None:
        body = "\n".join(
            [
                "# 油渍",
                "",
                "骑手把袋子递过来，扫到我裤腿上那块油渍。",
                "我侧了一下腿，说了声谢谢，他转身就走了。",
                "我回屋坐下，把手机翻过去，",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("粗粝自毁信号不足" in item["rule"] for item in findings), findings)

    def test_checker_explains_private_wet_texture_is_not_rough_exposure(self) -> None:
        body = "\n".join(
            [
                "# 热水",
                "",
                "屏幕上狗哥问下个月婚礼来不来。最近项目忙，可能去不了，我打了又删。",
                "热水器底下积了一小滩水，我蹲下去摸了摸地面。",
                "裤管立刻湿了半截，拖鞋也湿了。",
                "我找了个盆搁底下接水，热水器还在滴滴答答。",
                *(["其实我觉得水龙头有点旧，不过手机又响了一下，因为那条消息还没回。"] * 34),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("私密湿脏纹理替代粗粝" in item["rule"] for item in findings), findings)
            self.assertTrue(any("粗粝自毁信号不足" in item["rule"] for item in findings), findings)
            wet_finding = next(item for item in findings if "私密湿脏纹理替代粗粝" in item["rule"])
            self.assertIn("私密纹理", wet_finding["suggestion"])
            self.assertIn("外部/社交/付款/路线/回复动作", wet_finding["suggestion"])

    def test_checker_accepts_dirty_sleeve_or_bare_foot_seen_by_rider_as_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 袖口",
                "",
                "骑手递袋子的时候看了我一眼，又看了我的袖子。",
                "袖口上脏了一块，不知道什么时候蹭上去的。",
                "我把袖口往下扯了扯，接过来说了声谢谢。",
                "光着一只脚踩在瓷砖上，脚趾冻得发白。",
                "楼道门口那点汤被我踩到，拖鞋打滑，扶了一下墙才站稳。",
                *(["水龙头在厨房响了一下，杯子边上有水，窗帘半挂着，脚趾又抽了一下。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings), findings)

    def test_checker_does_not_count_private_spill_as_public_engine(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "我在房间里把外卖袋子提手扯断，粥淌到手上。",
                "手机卡了一下，屋里没别人。",
                "回沙发的时候踩到粥，拖鞋打滑，扶着墙站住。",
                *(["其实我觉得杯子有点旧，洗的时候水龙头轻轻响了一下。"] * 38),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("段落发动机信号偏弱" in item["rule"] for item in findings), findings)

    def test_checker_counts_quiet_dirty_hand_reaction_as_paragraph_engine(self) -> None:
        body = "\n".join(
            [
                "# 生瓜日寄",
                "",
                "付钱的时候手指甲缝里有灰，摊主接过去看了我手一眼，嘴角动了一下。",
                "我把硬币往回收了一点，又放过去。",
                "这事算不上什么，那个瓜白得像没睡醒。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings))

    def test_checker_does_not_count_private_dirty_hand_as_paragraph_engine(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "手指甲缝里有灰，杯子边上也有灰。",
                *(["其实我觉得杯子有点旧，洗的时候水龙头轻轻响了一下。"] * 38),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("段落发动机信号偏弱" in item["rule"] for item in findings))

    def test_checker_does_not_count_plain_dirty_room_as_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "房间很脏，纸箱很多，地上有灰。",
                *(["其实我觉得杯子有点旧，洗的时候水龙头轻轻响了一下。"] * 38),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    def test_checker_counts_delivery_person_room_glance_as_rough_and_engine(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "外卖员把袋子递过来，说路上洒了一点。",
                "他好像往里看了一眼，屋里太乱了，桌上还有昨天的快餐盒。",
                "我赶紧说了声谢谢，把门关上。",
                "回去的时候踩到门口那点汤，拖鞋打滑，差点跪在门槛上。",
                "手机又响了一下，我假装没听见。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings))

    def test_checker_does_not_let_single_delivery_glance_carry_whole_standard_piece(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "外卖员把袋子递过来，说路上洒了一点。",
                "他好像往里看了一眼，屋里太乱了，桌上还有昨天的快餐盒。",
                "我赶紧说了声谢谢，把门关上。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))
            self.assertTrue(any("段落发动机信号偏弱" in item["rule"] for item in findings))

    def test_checker_does_not_count_private_stomach_noise_as_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "坐在房间里胃响了一声。",
                *(["其实我觉得杯子有点旧，洗的时候水龙头轻轻响了一下。"] * 38),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    def test_checker_accepts_true_short_breath_drop_for_draft_gate(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "很丢人。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("呼吸点缺失" in item["rule"] for item in findings))
            self.assertTrue(any(item["rule"] == "呼吸点" and item["excerpt"] == "很丢人。" for item in findings))

    def test_checker_does_not_count_plain_knee_pain_as_rough_signal(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "膝盖有点疼。",
                *(["其实我觉得杯子有点脏，洗的时候水龙头轻轻响了一下。"] * 38),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_style_profile_uses_phase_genre_stratum_when_requested(self) -> None:
        draft = next(iter(sorted(CORPUS.glob("Anlin_20220404.md"))))
        result = subprocess.run(
            [
                sys.executable,
                str(CHECK_PROFILE),
                str(draft),
                "--profile",
                str(STYLE_PROFILE),
                "--phase",
                "A",
                "--genre",
                "standard",
                "--json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["profile_scope"]["scope"], "phase_genre:A/standard")
        self.assertFalse(report["profile_scope"]["fallback"])
        self.assertIn("cognitive_audit", report)

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_style_profile_falls_back_when_stratum_is_too_small(self) -> None:
        draft = next(iter(sorted(CORPUS.glob("*.md"))))
        result = subprocess.run(
            [
                sys.executable,
                str(CHECK_PROFILE),
                str(draft),
                "--profile",
                str(STYLE_PROFILE),
                "--genre",
                "micro-hope",
                "--json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["profile_scope"]["scope"], "global")
        self.assertTrue(report["profile_scope"]["fallback"])

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_style_profile_calibration_reports_original_warning_families(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(CALIBRATE_PROFILE),
                str(CORPUS),
                "--profile",
                str(STYLE_PROFILE),
                "--json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["corpus_file_count"], 38)
        self.assertEqual(report["error_files"], [])
        self.assertIn("red_family_counts", report)
        self.assertIn("yellow_family_counts", report)
        self.assertIn("family_count_distribution", report)
        self.assertIn("recommended_thresholds", report)
        self.assertIn("per_file", report)
        self.assertGreaterEqual(report["recommended_thresholds"]["soft_revise_threshold"], 10)

    def test_skill_links_style_profile_without_loading_as_generation_pack(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean_eval = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        self.assertIn("references/stylometric-ratio-protocol.md", skill)
        self.assertIn("scripts/check_style_profile.py", skill)
        self.assertIn("Style-ratio audit", skill)
        self.assertNotIn("stylometric-ratio-protocol", clean_eval)
        self.assertNotIn("check_style_profile", clean_eval)
        self.assertIn("Do not use corpus ratio targets as a pre-draft recipe.", skill)

    def test_clean_generation_protocol_does_not_treat_checker_findings_as_tool_failure(self) -> None:
        combined = "\n".join(
            [
                (ROOT / "SKILL.md").read_text(encoding="utf-8"),
                (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8"),
                (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8"),
            ]
        )
        self.assertIn("Checker findings are not tool failures", combined)
        self.assertIn("not a broken tool", combined)
        self.assertIn("Do not edit, write, compare, explain, invoke fallback", combined)
        self.assertIn("unpersisted manual repair invalidates the clean test", combined)

    def test_realistic_eval_prompts_do_not_carry_style_hints(self) -> None:
        data = json.loads(EVALS.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "2.2")
        self.assertEqual(data["skill_name"], "anlin-writing")
        self.assertIn("anlin-writing", data["trigger_aliases"])
        self.assertIn("anlinwriting", data["trigger_aliases"])
        self.assertIn("Anlin", data["trigger_aliases"])
        self.assertEqual(data["installed_skill_path"], "<skill-dir>")
        self.assertEqual(data["corpus_path"], "<corpus-dir or ANLIN_CORPUS_DIR>")
        banned_helpers = (
            "蒙太奇",
            "不总结",
            "不升华",
            "场景",
            "标题用",
            "标题「",
            "方法标签",
            "验证条件",
            "语料",
            "片段级",
            "judge",
            "rubric",
            "门禁",
        )
        self.assertEqual(len(data["evals"]), 15)
        for item in data["evals"]:
            self.assertIn("realistic_prompt", item, item["name"])
            realistic_prompt = item["realistic_prompt"]
            self.assertTrue(realistic_prompt.startswith("用 anlin-writing skill 写"), item["name"])
            for banned in banned_helpers:
                self.assertNotIn(banned, realistic_prompt, item["name"])

    def test_checker_blocks_private_old_record_archive_chain_in_draft_gate(self) -> None:
        archive_lines = [
            "# 六十秒",
            "",
            "凌晨快三点，手机显示两度。",
            "朋友圈刷到头，年度总结和新年flag挤在一起。",
            "往上滑是歌单，往下滑是结婚证。",
            "退出来又按亮屏幕，手滑点进旧手机备份。",
            "二一年三月的聊天记录还在。",
            "毕业论文那阵子，红叹号一直挂着。",
            "语音条播放不了，加载不出来。",
            "对话框里全是查重、参考文献和页码。",
        ]
        filler = "其实我觉得厨房灯管突然闪了一下，手机屏幕还亮着，于是发现房间里很冷，因为窗户没关严。"
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("\n".join([*archive_lines, *([filler] * 42)]), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertTrue(any("旧记录私密考古链" in item["rule"] for item in findings))
            self.assertTrue(any(item["severity"] == "error" and "旧记录私密考古链" in item["rule"] for item in findings))

    def test_checker_counts_practical_misread_and_wrong_slipper_as_engine(self) -> None:
        body = "\n".join(
            [
                "# 六十秒",
                "",
                "蹲下去摸，发现灰腻腻的还拉丝，心里一紧，以为老鼠。",
                "开手电筒照，是糖，化了一大半，剩下的粘着灰。",
                "鞋柜里只剩一双夏天的，左右脚不一样，穿上以后一个高一个低。",
                "走回客厅左脚绊在门槛上，手撑在墙上才没倒。",
                "碰倒了门边那个快递盒，泡沫滚了一地。",
                *(["其实水龙头咳了一下，洗的时候水顺着管道往下走，因为接口又开始渗水。"] * 35),
            ]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            self.assertFalse(any("段落发动机信号偏弱" in item["rule"] for item in findings))
            self.assertFalse(any("粗粝自毁信号不足" in item["rule"] for item in findings))

    def test_old_record_positive_source_lens_is_in_runtime_layers(self) -> None:
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        modes = (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for text in (clean, runtime, modes, skill):
            self.assertIn("old", text.lower())
        self.assertIn("the old record is a trigger, not the engine", clean)
        self.assertIn("one present humiliation", clean)
        self.assertIn("The old record should not be a museum tour", runtime)
        self.assertIn("make the present day answer it badly", modes)

    def test_social_decline_source_guidance_requires_reply_aftermath_engine(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        source_engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")
        finalized = (ROOT / "references" / "finalized-repair-minimum.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "check_anlin_violations.py").read_text(encoding="utf-8")
        self.assertIn("post-refusal section", clean)
        self.assertIn("reply aftermath", clean)
        self.assertIn("reply aftermath", runtime)
        self.assertIn("an invitation or refusal may be one fragment among many", first_draft)
        self.assertIn("Keep a local consequence only when the text naturally creates one", first_draft)
        self.assertIn("fragment slate", first_draft)
        self.assertIn("source relation", finalized)
        self.assertIn("inactive historical reference", source_engine.lower())
        self.assertIn("社交拒绝群聊假后果", checker)
        self.assertIn("社交拒绝礼貌闭合", checker)
        self.assertIn("social_decline_group_fake_consequence", (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8"))
        self.assertIn("social_decline_tidy_etiquette_closure", (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8"))
        self.assertNotIn("post-refusal consequence", runtime)
        self.assertNotIn("one load-bearing kernel must be the refusal aftermath itself", "\n".join([first_draft, finalized, clean, runtime]))

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_run_blind_test_supports_multiple_placebo_rounds(self) -> None:
        draft = next(iter(sorted(CORPUS.glob("*.md"))))
        with tempfile.TemporaryDirectory() as temp:
            output_root = Path(temp) / "blind-rounds"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUN_BLIND),
                    str(draft),
                    str(CORPUS),
                    "--rounds",
                    "1",
                    "--num-samples",
                    "2",
                    "--placebo-rounds",
                    "2",
                    "--min-fragment-chars",
                    "100",
                    "--length-tolerance",
                    "1.0",
                    "--output-root",
                    str(output_root),
                    "--seed",
                    "21",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output_root / "controller-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["placebo_rounds"], 2)
            self.assertEqual(len(manifest["rounds"]), 3)
            self.assertIn("literary-annotation", manifest["profiles"])
            placebo_rounds = [item for item in manifest["rounds"] if item["kind"].startswith("placebo:")]
            self.assertEqual(len(placebo_rounds), 2)
            self.assertTrue(all(item["generated_sample"] == "NONE" for item in placebo_rounds))
            self.assertIn("original-text calibration", manifest["controller_rule"])
            self.assertIn("OPENCODE_CONFIG_DIR", manifest["controller_rule"])
            self.assertIn("OPENCODE_DISABLE_EXTERNAL_SKILLS", manifest["controller_rule"])
            self.assertIn("OPENCODE_DISABLE_CLAUDE_CODE_SKILLS", manifest["controller_rule"])
            trigger_terms = (
                "Anlin",
                "style skill",
                "author-specific",
                "skill references",
                "mapping.json",
                "impostor",
                "original corpus",
            )
            for item in manifest["rounds"]:
                prompt = Path(item["prompt"]).read_text(encoding="utf-8")
                for term in trigger_terms:
                    self.assertNotIn(term, prompt)
            for item in placebo_rounds:
                round_dir = Path(item["directory"])
                mapping = json.loads((round_dir / "mapping.json").read_text(encoding="utf-8"))
                self.assertTrue(all(not sample["is_draft"] for sample in mapping.values()))
                prompt = (round_dir / "prompt.txt").read_text(encoding="utf-8")
                self.assertIn("SOURCE_COHESION_CHECK", prompt)
                judge_dir = Path(item["judge_directory"])
                self.assertTrue(judge_dir.is_dir())
                self.assertTrue((judge_dir / "prompt.txt").is_file())
                self.assertFalse((judge_dir / "mapping.json").exists())
                self.assertEqual(len(list(judge_dir.glob("sample-*.txt"))), 3)
                self.assertNotIn("placebo", judge_dir.name)
                self.assertNotIn("impostor", judge_dir.name)

    def test_blind_manifest_requires_resolved_opencode_isolation_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            draft = root / "draft.md"
            corpus = root / "corpus"
            output_root = root / "blind-rounds"
            corpus.mkdir()
            draft.write_text("# 临时草稿\n\n" + "今天下楼又忘了带钥匙，回头时鞋底还粘着水。" * 30, encoding="utf-8")
            for index in range(3):
                (corpus / f"original-{index}.md").write_text(
                    f"# 原文{index}\n\n" + "早上出门时楼道很暗，我摸到口袋里的纸才想起昨天的事。" * 30,
                    encoding="utf-8",
                )

            result = subprocess.run(
                [
                    sys.executable,
                    str(RUN_BLIND),
                    str(draft),
                    str(corpus),
                    "--rounds",
                    "1",
                    "--num-samples",
                    "2",
                    "--placebo-rounds",
                    "0",
                    "--length-tolerance",
                    "1.0",
                    "--output-root",
                    str(output_root),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output_root / "controller-manifest.json").read_text(encoding="utf-8"))
            self.assertIn("opencode_isolation_preflight", manifest)
            preflight = manifest["opencode_isolation_preflight"]
            self.assertEqual(preflight["commands"], ["opencode debug paths", "opencode debug skill"])
            self.assertEqual(
                preflight["resolved_config_root_policy"],
                "must_match_controller_recorded_isolated_root",
            )
            self.assertEqual(preflight["required_non_builtin_skill_count"], 0)
            self.assertTrue(preflight["fail_closed_on_mismatch"])
            required_evidence = " ".join(preflight["required_evidence"])
            self.assertIn("resolved config root", required_evidence)
            self.assertIn("all non-built-in skills", required_evidence)
            self.assertIn("OPENCODE_CONFIG_DIR alone is not isolation evidence", manifest["controller_rule"])
            self.assertIn("XDG_CONFIG_HOME", manifest["controller_rule"])
            self.assertIn("any non-built-in skill", manifest["controller_rule"].lower())


    # ── RED tests: fragment-based source model ────────────────────

    def test_fragment_collage_not_rejected_for_missing_engine_signal(self) -> None:
        """Corpus-like multi-fragment draft with topic jumps, self-correction, conversation.
        Must NOT produce hard errors for missing engine signal or connector words."""
        body_lines = [
            "今天下午去超市，发现洗衣液涨价了。",
            "结账的时候前面排了个大爷，拿了一整购物车的酱油。",
            "我寻思这是买了几年份的。",
            "晚上狗哥发消息问我最近在干嘛。",
            "我说在找工作。他说你不是刚找过吗。",
            "我说那是去年的了。",
            "挂掉电话刷到高中同学晒结婚照。",
            "我放大看了看新娘的脸，又退出来。",
            "其实没认出来是谁。",
            "就跟了个赞。",
            "突然想起上周我妈打电话说隔壁阿姨的女儿考上了公务员。",
            "她问我最近怎么样，我说还行。",
            "她说那就好。",
            "厨房水龙头一直滴答滴答。",
            "我拧了几次，还是漏。",
            "算了明天买生料带。",
            "其实也不是买不到，就是懒得出门。",
        ]
        body = "\n".join(["# 日寄", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            engine_errors = [item for item in findings if item["severity"] == "error" and "段落发动机信号偏弱" in item["rule"]]
            connector_errors = [item for item in findings if item["severity"] == "error" and "高频词覆盖不足" in item["rule"]]
            self.assertFalse(engine_errors, f"Corpus-like fragment collage should not trigger engine signal hard errors: {engine_errors}")
            self.assertFalse(connector_errors, f"Corpus-like fragment collage should not trigger connector hard errors: {connector_errors}")

    def test_same_night_refusal_not_overgrowth(self) -> None:
        """Same-night route calculation, ticket check, refusal activities must NOT be flagged
        as cross-day social consequence overgrowth."""
        body_lines = [
            "晚上拖地，拖把杆拧到一半又缩回去。",
            "狗哥说下个月结婚，问我能不能来。",
            "我先回恭喜，后面本来接着肯定，打出来又删了。",
            "因为我已经点开了日历。",
            "查了查票，周五到得太晚，周六又赶不上中午。",
            "我点到付款，停住了。",
            "狗哥问票是不是不好买，我说还在看。",
            "大叔在外面敲门，帮我送快递，垃圾袋掉了两卷。",
            "我在楼道里穿着湿袜子追垃圾袋。",
            "回屋以后打了一句最近忙项目，又改成实在去不了。",
            "狗哥回好，没事，忙你的。",
            "门锁没扣住，弹开一点。",
            "我站门缝后面，打了几个字又删了。",
            "垃圾袋套进桶里，袋口太松。",
            "湿袜子踩在鞋印上，滑了一步。",
        ]
        body = "\n".join(["# 最后一班", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            overgrowth = [item for item in findings if "社交拒绝后果过度生长" in item["rule"]]
            self.assertFalse(overgrowth, f"Same-night refusal must not trigger overgrowth: {overgrowth}")

    def test_next_day_overgrowth_still_flagged(self) -> None:
        """A draft with explicit next day events, new characters, and continued wedding
        plot must still be flagged as overgrowth."""
        body_lines = (
            [
                "充电线从桌子下面伸上来，插头有点松。",
                "狗哥说下个月结婚，问我能不能来。",
                "我回他说最近忙项目，去不了。",
                "他回了个表情。",
                "第二天早上班群里发了合照，我点开放大看了半天。",
                "中午到站以后同事问我谁结婚，我说大学同学。",
                "下午狗哥又发了个红包，问能不能当伴郎。",
                "我回座位打了几个字，说伴郎可能当不了，到时候喝喜酒。",
                "他回不强求，我把手机扣在桌上。",
            ]
            + ["回来时椅子轮子卡住，我弯腰拽了一下，裤脚沾到灰。"] * 40
        )
        body = "\n".join(["# 充电线", "", *body_lines])
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            findings = json.loads(result.stdout)
            overgrowth = [item for item in findings if "社交拒绝后果过度生长" in item["rule"]]
            self.assertTrue(overgrowth, f"Next-day overgrowth must still be flagged: {findings}")

    def test_active_runtime_uses_fragment_source_contract(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        collage = (ROOT / "references" / "anlin-collage-source-model.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        anti_ai = (ROOT / "references" / "anti-ai-slop.md").read_text(encoding="utf-8")
        old_engine = (ROOT / "references" / "standard-diary-source-engine.md").read_text(encoding="utf-8")

        self.assertIn("references/anlin-collage-source-model.md", skill)
        self.assertNotIn("load `references/standard-diary-source-engine.md`", skill)
        self.assertNotIn("side engine -> public hinge -> off-axis residue", first_draft)
        self.assertNotIn("950-1150", first_draft)
        self.assertIn("fragment slate", first_draft)
        self.assertIn("226-1923", collage)
        self.assertIn("13-87", collage)
        self.assertIn("references/anlin-collage-source-model.md", clean)
        self.assertNotIn("load `references/standard-diary-source-engine.md`", runtime)
        self.assertNotIn("load `references/standard-diary-source-engine.md`", anti_ai)
        self.assertIn("inactive", old_engine.lower())

    def test_active_fragment_contract_blocks_single_carrier_social_template(self) -> None:
        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        collage = (ROOT / "references" / "anlin-collage-source-model.md").read_text(encoding="utf-8")
        combined = "\n".join((first_draft, collage))

        self.assertIn(
            "present desk/room -> message -> ticket/money -> old-friend inventory -> work excuse -> refusal -> friendship thesis",
            combined,
        )
        self.assertIn("If the slate follows that carrier chain, replace one middle fragment", combined)
        self.assertIn("A dense body of a few prose paragraphs is prose-block compression", combined)

    def test_active_fragment_contract_keeps_busy_project_as_excuse_boundary(self) -> None:
        first_draft = (ROOT / "references" / "clean-eval-first-draft-minimum.md").read_text(encoding="utf-8")
        collage = (ROOT / "references" / "anlin-collage-source-model.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        combined = "\n".join((first_draft, collage, runtime))

        self.assertIn(
            'If the prompt only says `忙项目`, keep it as an excuse surface; do not invent a client, deadline, leave, team, coworker, city, or office biography.',
            combined,
        )

    def test_style_profile_splitter_excludes_corpus_metadata(self) -> None:
        title, body, body_lines = split_style_title_body(
            "\n".join(
                [
                    "# 日寄",
                    "",
                    "- **作者**: Anlin",
                    "- **原链接**: https://example.invalid/article",
                    "- **发布日期**: 2022-04-11",
                    "",
                    "---",
                    "正文第一行，",
                    "",
                    "正文第二行。",
                ]
            )
        )

        self.assertEqual(title, "日寄")
        self.assertEqual(body, "正文第一行，\n正文第二行。")
        self.assertEqual(body_lines, ["正文第一行，", "正文第二行。"])
        self.assertEqual(read_style_profile(STYLE_PROFILE)["version"], "1.7")

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_style_profile_soft_revise_threshold_matches_corpus_calibration(self) -> None:
        report = calibrate_style_profile(CORPUS, read_style_profile(STYLE_PROFILE), include_info=False)

        self.assertEqual(
            SOFT_REVISE_FAMILY_THRESHOLD,
            report["recommended_thresholds"]["soft_revise_threshold"],
        )

    @unittest.skipUnless(HAS_CORPUS, "set ANLIN_CORPUS_DIR to run full-corpus regression")
    def test_corpus_observed_range_matches_source_model(self) -> None:
        rows: list[tuple[int, int]] = []
        for path in sorted(CORPUS.glob("*.md")):
            _, body, body_lines = split_style_title_body(path.read_text(encoding="utf-8"))
            rows.append((len(re.findall(r"[\u4e00-\u9fff]", body)), len(body_lines)))

        self.assertEqual(len(rows), 38)
        self.assertEqual(min(chars for chars, _ in rows), 226)
        self.assertEqual(max(chars for chars, _ in rows), 1923)
        self.assertEqual(min(lines for _, lines in rows), 13)
        self.assertEqual(max(lines for _, lines in rows), 87)

        collage = (ROOT / "references" / "anlin-collage-source-model.md").read_text(encoding="utf-8")
        self.assertIn("226-1923", collage)
        self.assertIn("13-87", collage)
        self.assertNotIn("950-1150", collage)
        self.assertNotIn("45-70", collage)

    def test_fragment_and_social_decline_checker_pairs(self) -> None:
        fragment_body = "\n".join(
            [
                "# 日寄",
                "",
                "今天下午去超市，发现洗衣液涨价了。",
                "结账的时候前面排了个大爷，拿了一整购物车的酱油。",
                "我寻思这是买了几年份的。",
                "晚上狗哥发消息问我最近在干嘛。",
                "我说在找工作。他说你不是刚找过吗。",
                "我说那是去年的了。",
                "挂掉电话刷到高中同学晒结婚照。",
                "我放大看了看新娘的脸，又退出来。",
                "其实没认出来是谁，就跟了个赞。",
                "突然想起上周我妈打电话说隔壁阿姨的女儿考上了公务员。",
                "她问我最近怎么样，我说还行。",
                "厨房水龙头一直滴答滴答，我拧了几次，还是漏。",
                "算了明天买生料带，其实也不是买不到，就是懒得出门。",
            ]
        )
        same_night_body = "\n".join(
            [
                "# 最后一班",
                "",
                "晚上拖地，拖把杆拧到一半又缩回去。",
                "狗哥说下个月结婚，问我能不能来。",
                "我先回恭喜，后面本来接着肯定，打出来又删了。",
                "查了查票，周五到得太晚，周六又赶不上中午。",
                "我点到付款，停住了。",
                "狗哥问票是不是不好买，我说还在看。",
                "回屋以后打了一句最近忙项目，又改成实在去不了。",
                "狗哥回好，没事，忙你的。",
                "门锁没扣住，弹开一点，我站门缝后面又删了几个字。",
            ]
        )
        next_day_body = "\n".join(
            [
                "# 充电线",
                "",
                "充电线从桌子下面伸上来，插头有点松。",
                "狗哥说下个月结婚，问我能不能来。",
                "我回他说最近忙项目，去不了。",
                "他回了个表情。",
                "第二天早上班群里发了合照，我点开放大看了半天。",
                "中午到站以后同事问我谁结婚，我说大学同学。",
                "下午狗哥又发了个红包，问能不能当伴郎。",
                "我回座位打了几个字，说伴郎可能当不了，到时候喝喜酒。",
                "他没有马上回我，头像在那儿亮了一下又暗下去。",
                "我把充电线重新插好，插头还是往外弹。",
                "桌上那张快递单被水杯压住，边角卷起来。",
                "我拿钥匙去刮，刮下来一层胶，手上全是纸屑。",
                "楼下有人喊了一声，像是在找一辆没锁的车。",
                "我趴在窗边看，没看见车，只看见垃圾桶旁边的塑料袋。",
                "袋子被风吹到台阶下面，又被人踢回路中间。",
                "我想下去捡，脚已经穿进一只拖鞋，另一只找不到。",
                "手机又亮了，是同事问明天能不能换班。",
                "我打了个能字，觉得这个字太像已经答应了。",
                "删掉以后只剩一个输入框，光标在里面闪。",
                "我把同事的消息和狗哥的消息都往上划了一下。",
                "两个人的头像挨在一起，看起来像一场小型会议。",
                "我没有回任何人，先去厨房找剪刀。",
                "剪刀在抽屉最里面，旁边是上次买的螺丝和一节没电的电池。",
                "我把电池拿出来，想起去年也有一节这样的。",
                "去年那天我也说了忙，后来整晚都在给自己找理由。",
                "这个理由现在已经变成一行字，发出去就不能收回。",
                "我又打开聊天框，狗哥发来一个问号。",
                "我先写实在去不了，删掉实在，留下去不了。",
                "发送以后房间里没有任何变化，只有充电线又松了一点。",
                "我按住插头，另一只手去摸门锁。",
                "门锁里卡着一小块灰，转了两下才扣上。",
                "楼道的感应灯亮了，照见我脚边那只孤零零的拖鞋。",
                "我把拖鞋踢回门里，手机还停在狗哥的对话框。",
                "他回了句知道了，后面没有标点。",
                "我看了半天，最后只把充电线往桌边挪了两厘米。",
                "桌角那本旧杂志翻到一半，里面夹着去年车票的存根。",
                "我把存根抽出来，日期已经被手汗磨掉一块。",
                "楼下的车终于开走，留下一个空车位和一滩水。",
                "我去关窗，窗框上的灰蹭到袖子上，正好在手肘那里。",
                "手机又震了一下，我没有拿起来看。",
                "厨房里的水烧开了，壶盖顶着响了几声。",
                "我把火关掉，想起同事的换班还没有回。",
                "狗哥的对话框也没有再亮，像两件都没收尾的事。",
                "我把拖鞋摆到门边，另一只还是找不到。",
                "充电线重新掉下来，插头碰到桌腿，发出很轻的一声。",
                "我弯腰捡起来，顺便把那张快递单翻了个面。",
                "背面没有字，只有一条被水泡开的蓝线。",
                "我把蓝线抹掉，手指上还留着一点潮气。",
            ]
        )

        def findings_for(body: str) -> list[dict[str, object]]:
            with tempfile.TemporaryDirectory() as temp:
                draft = Path(temp) / "draft.md"
                draft.write_text(body, encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                self.assertTrue(result.stdout, result.stderr)
                return json.loads(result.stdout)

        fragment_findings = findings_for(fragment_body)
        same_night_findings = findings_for(same_night_body)
        next_day_findings = findings_for(next_day_body)
        weak_rules = {"段落发动机信号偏弱", "高频词覆盖不足"}
        self.assertFalse(
            [item for item in fragment_findings if item["severity"] == "error" and item["rule"] in weak_rules]
        )
        self.assertFalse([item for item in same_night_findings if "社交拒绝后果过度生长" in item["rule"]])
        self.assertTrue([item for item in next_day_findings if "社交拒绝后果过度生长" in item["rule"]])

    def test_fragment_preflight_does_not_reintroduce_scene_engine(self) -> None:
        repair_hints, revision_frame = build_preflight_guidance(
            [
                "body_chinese_chars=1078",
                "paragraph_engine=weak (source reset)",
                "connectors=['其实'] < 5 before checker_call_2",
            ]
        )
        guidance = " | ".join([revision_frame, *repair_hints])
        self.assertIn("fragment", guidance.lower())
        self.assertNotIn("release each carrier", guidance)
        self.assertNotIn("complete standard-diary mass", guidance)
        self.assertNotIn("restore complete standard-diary mass", guidance)
        self.assertNotIn("add one consequence cluster", guidance)

    def test_private_grime_preflight_uses_visible_consequence_not_hinge_template(self) -> None:
        repair_hints, revision_frame = build_preflight_guidance(
            ["private_grime_without_public_consequence=['油印']"]
        )
        guidance = " | ".join([revision_frame, *repair_hints]).lower()
        self.assertIn("visible", guidance)
        self.assertIn("consequence", guidance)
        self.assertNotIn("public hinge", guidance)

    def test_high_frequency_warning_is_relation_diagnostic_not_connector_quota(self) -> None:
        findings = []
        check_high_frequency_coverage(findings, "# 日寄\n\n" + "今天去楼下，手里拿着一个袋子。\n" * 20)
        finding = next(item for item in findings if item.rule == "高频词覆盖不足")
        self.assertIn("联想", finding.suggestion)
        self.assertIn("片段", finding.suggestion)
        self.assertNotIn("多个不同的自然连接信号", finding.suggestion)

    def test_active_runtime_fragment_contract_has_no_single_scene_template(self) -> None:
        active_files = [
            ROOT / "SKILL.md",
            ROOT / "references" / "anlin-collage-source-model.md",
            ROOT / "references" / "clean-eval-first-draft-minimum.md",
            ROOT / "references" / "clean-generation-brief.md",
            ROOT / "references" / "generation-modes.md",
            ROOT / "references" / "runtime-brief.md",
            ROOT / "references" / "runtime-layer-map.md",
            ROOT / "references" / "finalized-repair-minimum.md",
            ROOT / "references" / "feature-budget.md",
            ROOT / "references" / "anti-ai-slop.md",
            ROOT / "scripts" / "prepare_finalized_repair_brief.py",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in active_files)
        lowered = combined.lower()

        self.assertIn("fragment slate", lowered)
        self.assertIn("causal movement is allowed but optional", lowered)
        self.assertIn("association", lowered)
        self.assertIn("time jump", lowered)
        for stale in (
            "choose the first workable moving chain",
            "side engine -> public hinge -> off-axis residue",
            "off-axis residue",
            "release each carrier after one consequence transfer",
            "roughly 950-1150 body chinese characters",
            "roughly 45-70 visible body lines",
            "target-lines 58",
            "target-lines 68",
            "first 20 content lines",
            "650-699 risk zone",
            "8-15 prose blocks",
            "5-10 scene units",
            "900-1100 body chinese characters",
            "650-849",
            "100+ tiny body lines",
            "1250 body chinese characters",
            "1350+",
            "at most two visible high-signal prompt items",
            "one off-axis branch",
        ):
            self.assertNotIn(stale, lowered)

    def test_standard_fragment_contract_does_not_default_to_one_scene(self) -> None:
        active_files = [
            ROOT / "SKILL.md",
            ROOT / "references" / "anlin-collage-source-model.md",
            ROOT / "references" / "clean-eval-first-draft-minimum.md",
            ROOT / "references" / "clean-generation-brief.md",
            ROOT / "references" / "generation-modes.md",
            ROOT / "references" / "runtime-brief.md",
            ROOT / "references" / "feature-budget.md",
            ROOT / "references" / "anti-ai-slop.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in active_files)
        lowered = combined.lower()

        self.assertIn("several independent thought-turns", lowered)
        self.assertIn("one continuous scene is not the default", lowered)
        self.assertIn("one room, one conversation, or one transaction", lowered)
        self.assertNotIn("keep one pressure surface and one consequence", lowered)
        self.assertNotIn("pick one visible pressure surface and one consequence", lowered)

    def test_healthy_fragment_preflight_does_not_block_on_engine_or_connector_heuristics(self) -> None:
        body = "\n".join(
            [
                "# 日寄",
                "",
                "今天下午去超市，发现洗衣液涨价了。",
                "结账的时候前面排了个大爷，拿了一整购物车的酱油。",
                "我寻思这是买了几年份的。",
                "晚上狗哥发消息问我最近在干嘛。",
                "我说在找工作。他说你不是刚找过吗。",
                "我说那是去年的了。",
                "挂掉电话刷到高中同学晒结婚照。",
                "我放大看了看新娘的脸，又退出来。",
                "其实没认出来是谁，就跟了个赞。",
                "突然想起上周我妈打电话说隔壁阿姨的女儿考上了公务员。",
                "她问我最近怎么样，我说还行。",
                "厨房水龙头一直滴答滴答，我拧了几次，还是漏。",
                "算了明天买生料带，其实也不是买不到，就是懒得出门。",
            ]
            + ["我把那句话删掉，又想起另一个不相干的事情。"] * 18
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text(body, encoding="utf-8")
            messages = preflight_messages(draft)

        blocking = blocking_preflight_messages(messages)
        self.assertFalse(any(message.startswith("paragraph_engine=weak") for message in blocking))
        self.assertFalse(any(message.startswith("connectors=") for message in blocking))

    def test_finalized_fragment_brief_does_not_reintroduce_carrier_or_scene_quota(self) -> None:
        from prepare_finalized_repair_brief import hard_gate_primary_action, compact_source_focus

        findings = [
            {
                "severity": "error",
                "rule": "strict: 标准日寄长行缓冲不足",
                "excerpt": "shape",
                "suggestion": "repair locally",
            }
        ]
        action = hard_gate_primary_action(findings, body_chars=913).lower()
        focus = compact_source_focus(findings, body_chars=913).lower()
        self.assertIn("fragment", action + focus)
        for stale in ("carrier", "release", "950-1150", "45-70", "new scene", "proof cluster"):
            self.assertNotIn(stale, action + focus)


if __name__ == "__main__":
    unittest.main()

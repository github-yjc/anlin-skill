from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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
from check_anlin_violations import detect_style  # noqa: E402
from clean_run_checker import normalize_before_final_check, preflight_messages  # noqa: E402
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
            self.assertTrue(any(rule == "strict: 粗粝自毁信号不足" for rule in rules))
            self.assertTrue(any(rule == "strict: 段落发动机信号偏弱" for rule in rules))
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
            draft.write_text("\n".join(["# 日寄", "", *ready_lines]), encoding="utf-8")
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("checker call 1/2", first.stdout)
            draft.write_text("\n".join(["# 日寄", "", *repaired_lines]), encoding="utf-8")
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("FINAL BOUNDARY", second.stdout)
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
            self.assertIn("short-grid drift", preflight.stdout)
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
            self.assertIn("underbuilt source shape", preflight.stdout)
            self.assertIn("source-loop rewrite after the visible shape is reset", preflight.stdout)
            self.assertIn("do not patch with isolated line additions", preflight.stdout)
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
            self.assertIn("source-loop rewrite after the visible shape is reset", preflight.stdout)
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
            "在等屋里的灯自己亮。",
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
            self.assertIn("do not mentally estimate 55-68 lines", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

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
            self.assertIn("real <=8-character drops", preflight.stdout)
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

    def test_clean_run_checker_allows_near_miss_long_line_count_to_reach_checker(self) -> None:
        long_lines = [
            "其实我蹲在地上拆箱子的时候，指甲缝里都是灰，手背还被胶带划了一道口子，",
            "收银员扫完水以后看了我一眼，又看了一眼我的手，我把手往口袋里塞了一下，",
            "裤子后面全是灰，在走廊灯下面看得很清楚，像我把便宜房间穿在身上出来了，",
        ]
        medium_lines = (["于是我坐在地上继续拆那个纸箱。"] * 25) + (
            ["突然发现地址还停在输入框里。"] * 24
        ) + (["好像这屋子也没完全认得我。"] * 24)
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
        → Read C:/skill/references/clean-generation-brief.md
        → Read C:/skill/references/era-state.md
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
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

    def test_clean_eval_trace_accepts_powershell_relative_set_content_write(self) -> None:
        log = '''
        → Read C:/skill/references/clean-generation-brief.md
        $ Test-Path .anlin-clean-eval-mode
        True
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
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
            self.assertIn("clean-eval未写入draft.md", rules)

    def test_clean_eval_trace_flags_jsonl_absolute_file_path_under_external_workspace(self) -> None:
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
                            "output": "C:\\Users\\34025\\.config\\opencode\\skills\\anlin-writing-workspace\\iteration-20260706-57\\eval-09-2024-classmate-wedding\n"
                        },
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "tool": "write",
                    "state": {
                        "title": "C:\\Users\\34025\\.config\\opencode\\skills\\anlin-writing-workspace\\iteration-20260706-57\\eval-09-2024-classmate-wedding\\draft.md",
                        "input": {
                            "content": "日寄\n\n正文",
                            "filePath": "C:\\Users\\34025\\.config\\opencode\\skills\\anlin-writing-workspace\\iteration-20260706-57\\eval-09-2024-classmate-wedding\\draft.md",
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
            self.assertIn("clean-eval未写入draft.md", rules)

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
                            "content": "日寄\n\n正文",
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
                        "output": "日寄\n\n正文",
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
        → Read C:/skill/references/clean-generation-brief.md
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
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

    def test_clean_eval_trace_does_not_treat_stop_instruction_as_write(self) -> None:
        log = """
        → Read C:/skill/references/clean-generation-brief.md
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
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
        → Read C:/skill/references/clean-generation-brief.md
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
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
        → Read C:/skill/references/clean-generation-brief.md
        If the wrapper prints `CLEAN_RUN_PREFLIGHT_STOP`, the draft still is not ready.
        Do not write `draft.md`, do not repair, and do not switch to `check_anlin_violations.py`.
        $ Test-Path .anlin-clean-eval-mode
        $ Get-Location
        C:/eval-workspace/iteration-1/eval-01
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

    def test_clean_run_checker_merges_uniform_medium_grid_before_second_call(self) -> None:
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
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2", second.stdout)
            lines = [line for line in draft.read_text(encoding="utf-8").splitlines() if line.strip()]
            body_lines = [line for line in lines[1:] if not line.lstrip().startswith("#")]
            self.assertLess(len(body_lines), 80)

    def test_clean_run_checker_rebalances_medium_grid_before_second_call(self) -> None:
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
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2", second.stdout)
            lines = [line for line in draft.read_text(encoding="utf-8").splitlines() if line.strip()]
            body_lines = [line for line in lines[1:] if not line.lstrip().startswith("#")]
            long_lines = [line for line in body_lines if len([char for char in line if "\u4e00" <= char <= "\u9fff"]) >= 28]
            self.assertGreaterEqual(len(body_lines), 45)
            self.assertGreaterEqual(len(long_lines), 6)

    def test_clean_run_checker_normalizes_rhythm_before_second_call(self) -> None:
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
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2", second.stdout)
            lines = [line for line in draft.read_text(encoding="utf-8").splitlines() if line.strip()]
            body_lines = [line for line in lines[1:] if not line.lstrip().startswith("#")]
            self.assertGreaterEqual(len(body_lines), 45)
            first_twenty = body_lines[:20]
            comma_ratio = sum(1 for line in first_twenty if line.endswith("，")) / len(first_twenty)
            self.assertGreaterEqual(comma_ratio, 0.45)
            self.assertLessEqual(comma_ratio, 0.85)

    def test_clean_run_checker_merges_short_grid_before_second_call(self) -> None:
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
            command = [
                sys.executable,
                str(CLEAN_RUN_CHECKER),
                str(draft),
                "--strict",
                "--draft-gate",
            ]
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertIn("CLEAN_RUN_STOP: FINAL BOUNDARY, this was checker call 2/2", second.stdout)
            lines = [line for line in draft.read_text(encoding="utf-8").splitlines() if line.strip()]
            body_lines = [line for line in lines[1:] if not line.lstrip().startswith("#")]
            self.assertLessEqual(len(body_lines), 75)
            first_twenty = body_lines[:20]
            comma_ratio = sum(1 for line in first_twenty if line.endswith("，")) / len(first_twenty)
            self.assertGreaterEqual(comma_ratio, 0.45)
            self.assertLessEqual(comma_ratio, 0.85)

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
        self.assertIn("The runtime has two roles", skill)
        self.assertIn("Generator role", skill)
        self.assertIn("Controller role", skill)
        self.assertIn("Deep references in Layer 3 are repair libraries", layer_map)
        self.assertIn("runtime-layer-map.md", readme)
        self.assertIn("runtime-layer-map.md", skill)
        self.assertIn("not a drafting aid", skill)
        self.assertIn("Own the clean-eval first-draft source loop", layer_map)
        self.assertIn("Layer 1 is not a pre-draft requirement", layer_map)

    def test_formal_first_draft_uses_source_loop_not_long_repair_files(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        title_model = (ROOT / "references" / "title-model.md").read_text(encoding="utf-8")
        anti_ai = (ROOT / "references" / "anti-ai-slop.md").read_text(encoding="utf-8")
        modes = (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8")
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        eval_readme = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
        clean_run = (ROOT / "scripts" / "clean_run_checker.py").read_text(encoding="utf-8")

        self.assertIn("that file is the first-draft source loop", skill)
        self.assertIn("Do not read `references/runtime-brief.md`", skill)
        self.assertIn("Do not open `runtime-brief.md` before the first complete `draft.md`", skill)
        self.assertIn("Clean-eval reference stop rule", skill)
        self.assertIn("`references/runtime-brief.md` is not a harmless supplement before the first draft", skill)
        self.assertIn("After reading `clean-generation-brief.md` in clean-eval mode, stop reading references", clean)
        self.assertIn("`runtime-brief.md` is not a harmless supplement before the first draft", clean)
        self.assertIn("Use this loop instead of opening the long runtime or review files", clean)
        self.assertIn("repair by replacing failed scene functions, not by adding feature labels", clean)
        self.assertIn("Clean-eval pre-draft hard no-load list", skill)
        self.assertIn("The table below is not permission to load extra files before a clean-eval first draft", skill)
        self.assertIn("Extra pre-draft files contaminate the source-guidance measurement", clean)
        self.assertIn("Before writing `draft.md`, do a private source preflight", clean)
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
        self.assertIn("screen-archaeology chain", skill)
        self.assertIn("old-chat records", clean)
        self.assertIn("Use visible breathing clusters before the first file write", clean)
        self.assertIn("count actual visible body rows", clean)
        self.assertIn("Do not trust mental estimates", clean)
        self.assertIn("Near-miss drafts are a repeated failure", clean)
        self.assertIn("only 35-44 actual body rows", clean)
        self.assertIn("A near-miss first draft is still not ready", skill)
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
        self.assertIn("A 900-949 character draft is a boundary case", skill)
        self.assertIn("do not make nearly every line carry body, money, route, screen", clean)
        self.assertIn("rebalance_line_rhythm.py draft.md --in-place", clean)
        self.assertIn("Do not let the repair bounce from short-line grid into 30-40 prose lines", clean)
        self.assertIn("Do not write a prose version first", clean)
        self.assertIn("true short breath means about 8 Chinese characters or fewer", clean)
        self.assertIn("a few true short breath drops", skill)
        self.assertIn("Do not write a prose-paragraph article first", skill)
        self.assertIn("do not trust a mental claim", skill)
        self.assertIn("Status 0 at a stop boundary only means the protocol message was delivered", clean)
        self.assertIn("several different natural small connectors", skill)
        self.assertIn("repeating `其实/已经/当时` as glue", skill)
        self.assertIn("convert chat pressure into one screen/action/body consequence", skill)
        self.assertIn("Treat social-feed prompts the same way", skill)
        self.assertIn("Do not stack three posts", skill)
        self.assertIn("A complete article is not a complete inventory of prompt nouns", skill)
        self.assertIn("Do not print an English or Chinese scene plan", skill)
        self.assertIn("Complete article` does not mean complete prompt coverage", clean)
        self.assertIn("quiet interior prompts", clean.lower())
        self.assertIn("phone/feed + room + food/order + bed", clean)
        self.assertIn("one outside contact or practical handoff", skill)
        self.assertIn("A mere glance, mirror inspection, or private \"I look bad\" line is usually not enough", runtime)
        self.assertIn("Explicit negative constraints outrank scene instincts", clean)
        self.assertIn("no store checkout, buying water, delivery order, receipt, payment gesture", clean)
        self.assertIn("Explicit user prohibitions are hard source constraints", skill)
        self.assertIn("不要写金钱、消费或价格", skill)
        self.assertIn("Shopping, parcel, wrong-size, coupon, delivery, or household-object", runtime)
        self.assertIn("split the user's prompt nouns into five buckets", runtime)
        self.assertIn("`forbidden`: any explicit \"do not write\" domain", runtime)
        self.assertIn("Do not keep `超市`, `收银台`, `矿泉水`", runtime)
        self.assertIn("If the draft only says the object is wrong", clean)
        self.assertIn("no long action/speech/thought rows", clean)
        self.assertIn("These are movement signals, not content quotas", skill)
        self.assertIn("Scan the whole article for all occurrences", skill)
        self.assertIn("If only this surface remains, replace locally", skill)
        self.assertIn("For clean-eval generation, do not open this file before the first complete `draft.md`", runtime)
        self.assertIn("do not open this file before the first complete `draft.md`", anti_ai)
        self.assertIn("do not open this file before the first complete `draft.md` unless the scene slate is stuck", modes)
        self.assertIn("source-load conflict", readme)
        self.assertIn("runtime-brief.md`, `generation-modes.md`, and `anti-ai-slop.md` remain available", readme)
        self.assertIn("Explicit prompt prohibitions were manually checked", validation)
        self.assertIn("blocking prompt-compliance failure", eval_readme)
        self.assertIn("visible same-domain replacement is a blocking prompt-compliance failure", validation)
        self.assertIn("not to write money/consumption/price", readme)

    def test_model_rotation_is_controller_protocol_not_runtime_branching(self) -> None:
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        eval_readme = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
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
        self.assertIn("Development tests should now rotate across multiple model surfaces", readme)
        self.assertIn("runtime instructions should stay model-agnostic", readme)
        self.assertIn("开发测试应轮换生成模型", eval_readme)
        self.assertIn("不要把某个模型上轮失败的分析追加给下轮生成 agent", eval_readme)
        validation_lower = validation.lower()
        for provider_token in ["deepseek", "mimo", "minimax", "gpt-5.5", "big-pickle"]:
            self.assertNotIn(provider_token, validation_lower)
            self.assertNotIn(provider_token, runtime_combined)

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
        self.assertIn("first 8-12 body lines", combined)
        self.assertIn("650-850 body Chinese characters", combined)
        self.assertIn("28-55 body lines", combined)
        self.assertIn("poem-shaped grid", combined)
        self.assertIn("520-649", combined)
        self.assertIn("short_genre_body_lines", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("short_genre_prompt_prop_too_early", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("short_genre_main_prop_title_loop", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("short_genre_period_grid", (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8"))
        self.assertIn("closed sentence rows", (ROOT / "SKILL.md").read_text(encoding="utf-8"))
        self.assertIn("many sealed `。` rows", (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8"))
        self.assertIn("短真诚题面物件过早", (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8"))
        self.assertIn("短真诚标题物件闭环", (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8"))
        self.assertIn("短体裁句号网格", (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8"))
        self.assertIn("token-anchor openings", (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8"))

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

    def test_runtime_docs_distinguish_clean_eval_from_ordinary_use(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        validation = (ROOT / "references" / "validation-protocol.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        eval_readme = (ROOT / "evals" / "README.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
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
        self.assertIn("The next tool action must be reading `draft.md` once", skill)
        self.assertIn("cannot be switched back to ordinary user mode", skill)
        self.assertIn("In any workspace containing `.anlin-clean-eval-mode`", skill)
        self.assertIn("use `clean_run_checker.py`, not the normal checker", skill)
        self.assertIn("At task start, check whether the current task workspace contains `.anlin-clean-eval-mode`", skill)
        self.assertIn("the first tool action should be a lightweight current-directory marker check", skill)
        self.assertIn("A first `Write draft.md` before this marker check is a contaminated clean-eval run", skill)
        self.assertIn("a first write without current-directory confirmation is not a valid bounded run", skill)
        self.assertIn("write and read the article using the relative path `draft.md`", skill)
        self.assertIn("the file/path argument must be exactly `draft.md` or `.\\draft.md`", skill)
        self.assertIn("Never substitute a different date-stamped directory", skill)
        self.assertIn("Use the relative path `draft.md` or `.\\draft.md`", clean)
        self.assertIn("Do not construct an absolute path from memory", clean)
        self.assertIn("`Get-Location` / `pwd` is mandatory before the first write", clean)
        self.assertIn("`<skill-dir>` is only for resolving bundled references and scripts", skill)
        self.assertIn("it must not appear in the article write path", clean)
        self.assertIn("Do not write `<skill-dir>/<iteration-or-case>/draft.md`", clean)
        self.assertIn("If `Get-Location` shows `<skill-dir>` or a path ending in `anlin-writing`, do not write", clean)
        self.assertIn("Draft in breathing clusters, not sentence rows", clean)
        self.assertIn("pain, heat, and fatigue alone are too polite", clean)
        self.assertIn("private case-report chain", runtime)
        self.assertIn("symptom list -> search result -> food taboo -> refrigerator inventory -> room smell -> ambient sound", skill)
        self.assertIn("A phone message is still too private unless it changes a visible reply", skill)
        self.assertIn("If the user gives `有人说痛风是富贵病`", runtime)
        self.assertIn("cut one whole packet before adding any new material", skill)
        self.assertIn("This marker check should be the first tool action", clean)
        self.assertIn("Do not write `draft.md` until both the marker check and current-directory confirmation are visible in the run trace", clean)
        self.assertIn("marker check -> current-directory confirmation -> read this brief -> write one complete `draft.md` -> run `clean_run_checker.py`", clean)
        self.assertIn("Do not rediscover this skill after it has already triggered", clean)
        self.assertIn("do not glob, search, or list parent skill directories", skill)
        self.assertIn("If a bundled reference path cannot be resolved", skill)
        self.assertIn("still persist `draft.md`", clean)
        self.assertIn("visible scratch article without `draft.md` is a failed run", clean)
        self.assertIn("The wrapper `clean_run_checker.py` is the only checker entrypoint", clean)
        self.assertIn("Choose the checker by mode before running any command", skill)
        self.assertIn("do not switch to `check_anlin_violations.py`", runtime)
        self.assertIn("Developer Two-Checkpoint Evaluation", validation)
        self.assertIn("Bounded clean-eval checkpoint", validation)
        self.assertIn("Finalized repair checkpoint", validation)
        self.assertIn("natural source guidance and limited checker-driven repair", validation)
        self.assertIn(".anlin-clean-run-snapshots", skill)
        self.assertIn("first-submission source guidance", validation)
        self.assertIn("stage snapshots", readme)
        self.assertIn("first_submission", eval_readme)
        self.assertIn("A clean finalized draft cannot retroactively make the bounded draft a success", validation)
        self.assertIn("Normal `check_anlin_violations.py draft.md` success is not sufficient", validation)
        self.assertIn("`check_anlin_violations.py draft.md --strict` is not the formal gate", skill)
        self.assertIn("A plain `check_anlin_violations.py <draft> --strict` run is only a quick informal smoke check", skill)
        self.assertIn("the formal hard-gate command is `check_anlin_violations.py draft.md --strict --draft-gate --genre <selected-genre>`", runtime)
        self.assertIn("A `revise` status means finalized repair failed", validation)
        self.assertIn("Style-profile `yellow` with zero errors is acceptable for the finalized checkpoint", validation)
        self.assertIn("style-profile `yellow` 可作为 finalized checkpoint 的通过条件之一", eval_readme)
        self.assertIn("它衡量自然引导能力加有限检查器修复能力", eval_readme)
        self.assertIn("不要只看“最后有没有修好”", eval_readme)
        self.assertIn("Style-profile `yellow` with zero errors and no red-family stop is acceptable", skill)
        self.assertIn("Clean-eval freezes the fresh-agent result after bounded preflight and limited checker-driven repair", skill)
        self.assertIn("standard diary around 55-65 body lines", skill)
        self.assertIn("short sincere/micro-hope around 4-7 uneven clusters", skill)
        self.assertIn("repairs bounce between opposite profile failures", skill)
        self.assertIn("style-profile remains `revise`, or remains `review` with red `line_rhythm`", runtime)
        self.assertIn("five independent yellow drift families", skill)
        self.assertIn("style-profile `review` or `inconclusive` is not", skill)
        self.assertIn("thin the draft instead of decorating it", runtime)
        self.assertIn("breathing clusters of 2-5 visible lines", runtime)
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
        self.assertIn("terminal/log-only final prose is an artifact failure", layer_map)
        summary_script = (ROOT / "scripts" / "summarize_dev_checkpoints.py").read_text(encoding="utf-8")
        self.assertIn("finalized draft unchanged from bounded input", summary_script)
        self.assertIn("Missing Draft Artifact", summary_script)
        self.assertIn("finalized 仍为 review/fail/invalid", eval_readme)
        self.assertIn("bounded clean-eval checkpoint", layer_map)
        self.assertIn("finalized repair checkpoint", layer_map)
        self.assertIn("normal checker success alone is not a finalized pass", layer_map)
        self.assertIn("finalized is only `review`, it is still unresolved", layer_map)
        self.assertIn("Generated articles do not belong in the skill directory", runtime)
        self.assertIn("Natural connector coverage should be solved before the checker", clean)
        self.assertIn("If a finalized standard diary reports `高频词覆盖不足`", skill)
        self.assertIn("If draft-gate reports `高频词覆盖不足`", runtime)
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
        self.assertIn("Do not create line breaks by deleting punctuation", skill)
        self.assertIn("Line-final comma means the visible content line itself ends with", clean)
        self.assertIn("A draft with many short rows and no visible punctuation is a generated line grid", runtime)
        self.assertIn("actual line endings, not comma count inside long lines", runtime)
        self.assertIn("reread for semantic damage", skill)

    def test_short_genre_repair_stuffing_is_source_guidance_not_only_checker(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        modes = (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8")
        budget = (ROOT / "references" / "feature-budget.md").read_text(encoding="utf-8")
        layer_map = (ROOT / "references" / "runtime-layer-map.md").read_text(encoding="utf-8")
        combined = "\n".join([skill, clean, runtime, modes, budget, layer_map])
        self.assertIn("Do not repair short sincere profile drift by adding new food", skill)
        self.assertIn("Short sincere repair has a second overfill trap", clean)
        self.assertIn("Treat `短体裁修复堆新素材` the same way", runtime)
        self.assertIn("Mode C repair should not import a new inventory", modes)
        self.assertIn("No short-genre repair stuffing", budget)
        self.assertIn("repair stuffing", layer_map)
        self.assertIn("existing object-message-room-body-memory set", layer_map)
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
        self.assertIn("This is a source reset, not a line edit", skill)
        self.assertIn("Throw away the old spine", clean)
        self.assertIn("When repairing `短真诚当前动作锚点不足`", runtime)
        self.assertIn("When repairing `短真诚标题物件闭环`", runtime)
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
        self.assertIn("`cropped trace` is stricter than \"write it briefly.\"", skill)
        self.assertIn("One line with childhood rain", skill)
        self.assertIn("a cropped trace means less than a scene", clean)
        self.assertIn("childhood rain + raincoat + broken umbrella + school arrival", clean)
        self.assertIn("do not mistake compression for deletion", runtime)
        self.assertIn("connector sampler", runtime)
        self.assertIn("one-each glue", clean)
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

    def test_skill_load_order_keeps_background_as_post_scene_fact_gate(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        always_start = skill.split("For ordinary article generation", 1)[0]
        minimal_pack = skill.split("For ordinary article generation, use the minimal generation pack:", 1)[1].split(
            "`references/anlin-background.md` and", 1
        )[0]
        self.assertIn("references/clean-generation-brief.md", always_start)
        self.assertIn("Do not call `read_mcp_resource`", always_start)
        self.assertNotIn("references/anlin-background.md", always_start)
        self.assertNotIn("references/anlin-background.md", minimal_pack)
        self.assertNotIn("references/background-fact-classes.json", always_start)
        self.assertNotIn("references/background-fact-classes.json", minimal_pack)
        self.assertIn("after the candidate scene slate exists", skill)
        self.assertIn("Do not make background facts into candidate scenes by themselves", skill)
        self.assertIn("background-fact-classes.json", skill)
        self.assertIn("If the first actual checker reports `背景展示堆砌`", skill)
        self.assertIn("remove one or two whole families before the second checker", skill)

    def test_clean_generation_brief_carries_core_runtime_gates(self) -> None:
        brief = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        self.assertIn("Skill references are local bundled files", brief)
        self.assertIn("Do not call `read_mcp_resource`", brief)
        self.assertIn("Source Loop", brief)
        self.assertIn("friction and consequence before any audit vocabulary", brief)
        self.assertIn("about 950-1150 Chinese characters", brief)
        self.assertIn("45-70 non-empty lines", brief)
        self.assertIn("not 100+ tiny rows", brief)
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

    def test_checker_draft_gate_promotes_sparse_connector_and_comma_rhythm(self) -> None:
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
            self.assertTrue(any(rule == "strict: 高频词覆盖不足" for rule in rules))
            self.assertTrue(any(rule == "strict: 行末逗号比例" for rule in rules))

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
            rules = [item["rule"] for item in findings if item["severity"] == "error"]
            self.assertTrue(any(rule == "strict: 中段旁逸不足" for rule in rules))

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
            self.assertEqual(profile["version"], "1.5")
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

    def test_style_profile_nonstandard_fallback_is_inconclusive_not_strict_failure(self) -> None:
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
            self.assertEqual(sincere_result.returncode, 0, sincere_result.stderr)
            sincere_report = json.loads(sincere_result.stdout)
            self.assertEqual(sincere_report["profile_scope"]["scope"], "global")
            self.assertTrue(sincere_report["profile_scope"]["fallback"])
            self.assertIn("genre:sincere: document_count=2 < 4", sincere_report["profile_scope"]["skipped"])
            self.assertEqual(sincere_report["summary"]["status"], "inconclusive")
            self.assertEqual(sincere_report["summary"]["checkpoint_decision"], "profile_inconclusive_fallback")
            self.assertTrue(sincere_report["summary"]["checkpoint_pass"])
            self.assertFalse(sincere_report["summary"]["profile_gate_applicable"])

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
            self.assertEqual(text_result.returncode, 0, text_result.stderr)
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
        self.assertIn("references/stylometric-ratio-protocol.md", skill)
        self.assertIn("scripts/check_style_profile.py", skill)
        minimal_pack = skill.split("For ordinary article generation, use the minimal generation pack:", 1)[1].split(
            "`references/anlin-background.md` and", 1
        )[0]
        self.assertNotIn("stylometric-ratio-protocol", minimal_pack)
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
        self.assertIn("never applies to ordinary checker findings", combined)
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
        self.assertIn("old record is a trigger, not the engine", skill)

    def test_social_decline_source_guidance_requires_reply_aftermath_engine(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        clean = (ROOT / "references" / "clean-generation-brief.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references" / "runtime-brief.md").read_text(encoding="utf-8")
        checker = (ROOT / "scripts" / "check_anlin_violations.py").read_text(encoding="utf-8")
        for text in (skill, clean, runtime):
            self.assertIn("post-refusal consequence", text)
            self.assertIn("reply aftermath", text)
        self.assertIn("Before saving, ask whether the article would still move if all room texture except one object were deleted", skill)
        self.assertIn("privately delete all room texture except one object", clean)
        self.assertIn("社交拒绝纹理替代后果不足", checker)

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


if __name__ == "__main__":
    unittest.main()

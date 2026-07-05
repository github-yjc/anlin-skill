from __future__ import annotations

import json
import os
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
from summarize_dev_checkpoints import classify_development_result  # noqa: E402


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

    def test_clean_run_checker_enforces_two_call_limit(self) -> None:
        ready_lines = [
            "其实我觉得厕所灯坏了以后，我站在门口有点丢人，",
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
            "突然发现杯子边上有黑泥，好像还蹭到指甲缝里，",
            "于是洗手洗到一半想吐出来，因为水龙头又喷到裤子上。",
            "不过镜子里那张脸像没睡醒，还以为自己要去面试。",
        ] * 12
        repaired_lines = [
            "其实第二次我把厕所灯看成面试通知，站在门口有点丢人，",
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
            self.assertIn("long_lines=0 < 4", preflight.stdout)
            self.assertIn("short_line_grid=", preflight.stdout)
            self.assertIn("rebalance_line_rhythm.py", preflight.stdout)
            self.assertIn("short-grid drift", preflight.stdout)
            state = json.loads((draft.parent / ".anlin-clean-run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["calls"], 0)
            self.assertEqual(state["preflights"], 1)

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

    def test_clean_run_checker_allows_near_miss_connector_draft_to_reach_checker(self) -> None:
        lines = [
            "其实我把杯子拿去洗，水龙头先咳了一下喷到裤子上，",
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

    def test_clean_eval_trace_flags_pre_draft_refs_and_stop_escape(self) -> None:
        log = """
        → Read C:/skill/references/clean-generation-brief.md
        $ Test-Path .anlin-clean-eval-mode
        → Read C:/skill/references/anti-ai-slop.md
        ← Write draft.md
        CLEAN_RUN_PREFLIGHT_STOP: draft is still not ready
        ← Write draft.md
        Remove-Item "case/.anlin-clean-run-state.json"
        python scripts/check_anlin_violations.py draft.md
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
        ← Write draft.md
        python scripts/clean_run_checker.py draft.md --strict --draft-gate
        CLEAN_RUN_NOTE: checker call 1/2
        ← Write draft.md
        python scripts/clean_run_checker.py draft.md --strict --draft-gate
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
            self.assertEqual(json.loads(result.stdout), [])

    def test_clean_eval_trace_does_not_treat_stop_instruction_as_write(self) -> None:
        log = """
        → Read C:/skill/references/clean-generation-brief.md
        $ Test-Path .anlin-clean-eval-mode
        ← Write draft.md
        python scripts/clean_run_checker.py draft.md --strict --draft-gate
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

    def test_clean_eval_trace_rejects_missing_clean_run_checker(self) -> None:
        log = """
        → Read C:/skill/references/clean-generation-brief.md
        ← Write draft.md
        python scripts/check_anlin_violations.py draft.md
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
            self.assertEqual(payload["diagnosis"], "systemic_gap")
            self.assertEqual(payload["blind_round_readiness"], "not_ready_for_blind_rounds")
            self.assertIn("strict hard-gate", payload["finalized_question"])
            self.assertIn("cannot retroactively improve bounded status", payload["finalized_checkpoint_scope"])
            self.assertIn("Only `pass` means", payload["finalized_checkpoint_answer"])
            self.assertIn("final article is not clean", payload["repair_implication"])
            self.assertIn(payload["finalized"]["gate"]["status"], {"fail", "review"})

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
        anti_ai = (ROOT / "references" / "anti-ai-slop.md").read_text(encoding="utf-8")
        modes = (ROOT / "references" / "generation-modes.md").read_text(encoding="utf-8")

        self.assertIn("that file is the first-draft source loop", skill)
        self.assertIn("Do not read `references/runtime-brief.md`", skill)
        self.assertIn("Do not open `runtime-brief.md` before the first complete `draft.md`", skill)
        self.assertIn("Use this loop instead of opening the long runtime or review files", clean)
        self.assertIn("repair by replacing failed scene functions, not by adding feature labels", clean)
        self.assertIn("Clean-eval pre-draft hard no-load list", skill)
        self.assertIn("The table below is not permission to load extra files before a clean-eval first draft", skill)
        self.assertIn("Extra pre-draft files contaminate the source-guidance measurement", clean)
        self.assertIn("Before writing `draft.md`, do a private source preflight", clean)
        self.assertIn("no group/comment chain markers", clean)
        self.assertIn("one coarse body/social/self-own consequence", clean)
        self.assertIn("Use the preflight message as a shape diagnosis", clean)
        self.assertIn("Known failed source shape", clean)
        self.assertIn("fluent 10-15 paragraph article", clean)
        self.assertIn("the visible article itself should already look like clusters of breath", clean)
        self.assertIn("也不是疼，就是", clean)
        self.assertIn("最疼的不是X，是Y", clean)
        self.assertIn("rebalance_line_rhythm.py draft.md --in-place", clean)
        self.assertIn("Do not let the repair bounce from short-line grid into 30-40 prose lines", clean)
        self.assertIn("Do not write a prose version first", clean)
        self.assertIn("true short breath means about 8 Chinese characters or fewer", clean)
        self.assertIn("a few true short breath drops", skill)
        self.assertIn("Do not write a prose-paragraph article first", skill)
        self.assertIn("Status 0 at a stop boundary only means the protocol message was delivered", clean)
        self.assertIn("several different natural small connectors", skill)
        self.assertIn("repeating `其实/已经/当时` as glue", skill)
        self.assertIn("convert chat pressure into one screen/action/body consequence", skill)
        self.assertIn("These are movement signals, not content quotas", skill)
        self.assertIn("For clean-eval generation, do not open this file before the first complete `draft.md`", runtime)
        self.assertIn("do not open this file before the first complete `draft.md`", anti_ai)
        self.assertIn("do not open this file before the first complete `draft.md` unless the scene slate is stuck", modes)
        self.assertIn("source-load conflict", readme)
        self.assertIn("runtime-brief.md`, `generation-modes.md`, and `anti-ai-slop.md` remain available", readme)

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
        self.assertIn("write and read the article using the relative path `draft.md`", skill)
        self.assertIn("never substitute a different date-stamped directory", skill)
        self.assertIn("Use the relative path `draft.md` or `.\\draft.md`", clean)
        self.assertIn("Do not construct an absolute path from memory", clean)
        self.assertIn("Draft in breathing clusters, not sentence rows", clean)
        self.assertIn("pain, heat, and fatigue alone are too polite", clean)
        self.assertIn("This marker check should be the first tool action", clean)
        self.assertIn("Do not write `draft.md` until this marker check is visible in the run trace", clean)
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
        self.assertIn("A `revise` status means finalized repair failed", validation)
        self.assertIn("Style-profile `yellow` with zero errors is acceptable for the finalized checkpoint", validation)
        self.assertIn("style-profile `yellow` 可作为 finalized checkpoint 的通过条件之一", eval_readme)
        self.assertIn("它衡量自然引导能力加有限检查器修复能力", eval_readme)
        self.assertIn("不要只看“最后有没有修好”", eval_readme)
        self.assertIn("Style-profile `yellow` with zero errors and no red-family stop is acceptable", skill)
        self.assertIn("Clean-eval freezes the fresh-agent result after bounded preflight and limited checker-driven repair", skill)
        self.assertIn("do one rhythm-reset rewrite around 55-65 body lines", skill)
        self.assertIn("repairs bounce between opposite profile failures", skill)
        self.assertIn("style-profile remains `revise`, or remains `review` with red `line_rhythm`", runtime)
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
        self.assertIn("finalized 仍为 review/fail/invalid", eval_readme)
        self.assertIn("bounded clean-eval checkpoint", layer_map)
        self.assertIn("finalized repair checkpoint", layer_map)
        self.assertIn("normal checker success alone is not a finalized pass", layer_map)
        self.assertIn("finalized is only `review`, it is still unresolved", layer_map)
        self.assertIn("Generated articles do not belong in the skill directory", runtime)
        self.assertIn("Natural connector coverage should be solved before the checker", clean)
        self.assertIn("Do not turn many hard-stop lines into one huge comma chain", runtime)
        self.assertIn("Do not create line breaks by deleting punctuation", skill)
        self.assertIn("Line-final comma means the visible content line itself ends with", clean)
        self.assertIn("A draft with many short rows and no visible punctuation is a generated line grid", runtime)
        self.assertIn("actual line endings, not comma count inside long lines", runtime)
        self.assertIn("reread for semantic damage", skill)

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
        self.assertIn("scan the candidate for `老婆/妻子/媳妇/孩子他妈/我儿子/我女儿`", brief)
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
            self.assertIn("red_families", draft_gate_report["summary"])
            self.assertIn("decision_rule", draft_gate_report["summary"])
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

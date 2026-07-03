from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = Path(r"C:\Users\34025\Desktop\Anlin")
CHECKER = ROOT / "scripts" / "check_anlin_violations.py"
BLIND_PREP = ROOT / "scripts" / "prepare_blind_test.py"
RUN_BLIND = ROOT / "scripts" / "run_blind_test.py"
BUILD_CARDS = ROOT / "scripts" / "build_corpus_cards.py"
BUILD_PROFILE = ROOT / "scripts" / "build_style_profile.py"
CHECK_PROFILE = ROOT / "scripts" / "check_style_profile.py"
CALIBRATE_PROFILE = ROOT / "scripts" / "calibrate_style_profile.py"
CARDS = ROOT / "references" / "corpus-cards"
STYLE_PROFILE = ROOT / "references" / "style-profile.json"
BACKGROUND_FACT_CLASSES = ROOT / "references" / "background-fact-classes.json"
EVALS = ROOT / "evals" / "evals.json"


class AnlinToolingTests(unittest.TestCase):
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
            self.assertEqual(strict_result.returncode, 0, strict_result.stderr)
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

    def test_skill_load_order_keeps_background_as_post_scene_fact_gate(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        always_start = skill.split("For ordinary article generation", 1)[0]
        minimal_pack = skill.split("For ordinary article generation, use the minimal generation pack:", 1)[1].split(
            "`references/anlin-background.md` and", 1
        )[0]
        self.assertNotIn("references/anlin-background.md", always_start)
        self.assertNotIn("references/anlin-background.md", minimal_pack)
        self.assertNotIn("references/background-fact-classes.json", always_start)
        self.assertNotIn("references/background-fact-classes.json", minimal_pack)
        self.assertIn("after the candidate scene slate exists", skill)
        self.assertIn("Do not make background facts into candidate scenes by themselves", skill)
        self.assertIn("background-fact-classes.json", skill)

    def test_background_fact_classes_are_boundaries_not_requirements(self) -> None:
        table = json.loads(BACKGROUND_FACT_CLASSES.read_text(encoding="utf-8"))
        self.assertIn("王者荣耀", table["classes"]["supported"]["game"])
        self.assertIn("打野教学", table["classes"]["unsupported"]["game_specifics"])
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
            self.assertEqual(len(profile["documents"]), 38)
            self.assertEqual(profile["profile_kind"], "corpus_prior_predictive_intervals")
            self.assertEqual(profile["version"], "1.2")
            self.assertIn("body_chars", profile["value_summary"])
            self.assertIn("ai_binary_reframe", profile["count_summary"])
            self.assertIn("unique_3gram_ratio", profile["value_summary"])
            self.assertIn("repeated_3gram_templates", profile["count_summary"])
            self.assertIn("texture_body_lines", profile["count_summary"])
            self.assertIn("dominant_theme_line_share", profile["value_summary"])
            self.assertIn("cognitive_crooked_interpretation", profile["count_summary"])
            self.assertEqual(profile["value_families"]["unique_3gram_ratio"], "ngram_texture")
            self.assertEqual(profile["count_summary"]["texture_body_lines"]["family"], "texture")
            self.assertEqual(profile["count_summary"]["cognitive_crooked_interpretation"]["family"], "cognitive_mechanism")
            self.assertIn("strata", profile)
            self.assertIn("A", profile["strata"]["phase"])
            self.assertIn("standard", profile["strata"]["genre"])
            self.assertIn("A/standard", profile["strata"]["phase_genre"])
            self.assertTrue(profile["count_summary"]["ai_binary_reframe"]["hard_generated"])
            self.assertIn("Do not force rare features to appear.", profile["principles"])

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
            self.assertIn("profile_scope", draft_gate_report)

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

    def test_skill_links_style_profile_without_loading_as_generation_pack(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/stylometric-ratio-protocol.md", skill)
        self.assertIn("scripts/check_style_profile.py", skill)
        minimal_pack = skill.split("For ordinary article generation, use the minimal generation pack:", 1)[1].split(
            "`references/anlin-background.md` and", 1
        )[0]
        self.assertNotIn("stylometric-ratio-protocol", minimal_pack)
        self.assertIn("Do not use corpus ratio targets as a pre-draft recipe.", skill)

    def test_realistic_eval_prompts_do_not_carry_style_hints(self) -> None:
        data = json.loads(EVALS.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "2.2")
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
            self.assertTrue(realistic_prompt.startswith("用 Anlin skill 写"), item["name"])
            for banned in banned_helpers:
                self.assertNotIn(banned, realistic_prompt, item["name"])

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

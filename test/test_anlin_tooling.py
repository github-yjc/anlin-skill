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
CARDS = ROOT / "references" / "corpus-cards"
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
            self.assertIn("Do not use style skills", prompt)
            self.assertIn("SOURCE_COHESION_CHECK", prompt)
            self.assertIn("title", prompt.lower())
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
            placebo_rounds = [item for item in manifest["rounds"] if item["kind"].startswith("placebo:")]
            self.assertEqual(len(placebo_rounds), 2)
            self.assertTrue(all(item["generated_sample"] == "NONE" for item in placebo_rounds))
            self.assertIn("original-text calibration", manifest["controller_rule"])
            for item in placebo_rounds:
                round_dir = Path(item["directory"])
                mapping = json.loads((round_dir / "mapping.json").read_text(encoding="utf-8"))
                self.assertTrue(all(not sample["is_draft"] for sample in mapping.values()))
                prompt = (round_dir / "prompt.txt").read_text(encoding="utf-8")
                self.assertIn("SOURCE_COHESION_CHECK", prompt)


if __name__ == "__main__":
    unittest.main()

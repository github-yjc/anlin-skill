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
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)
            errors = [item for item in findings if item["severity"] == "error"]
            if errors:
                failures.append(f"{path.name}: {errors}")
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
            self.assertTrue(any("文艺悬停式结尾" in rule for rule in rules))
            self.assertTrue(all(item["severity"] != "error" for item in findings))

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
            self.assertIn("MOST_ANLIN_LIKE", prompt)
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

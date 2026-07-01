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
BUILD_CARDS = ROOT / "scripts" / "build_corpus_cards.py"
CARDS = ROOT / "references" / "corpus-cards"


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
            self.assertFalse((output_dir / "portable-corpus.md").exists())
            self.assertFalse((output_dir / "vocabulary-rules.md").exists())

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


if __name__ == "__main__":
    unittest.main()

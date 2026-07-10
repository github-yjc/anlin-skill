#!/usr/bin/env python3
"""Prepare multiple isolated blind-evaluation rounds for Anlin-style drafts.

This script does not call a model by itself. It creates clean round folders,
sample files, judge prompts, and a controller manifest. The controller sends
each prompt to an isolated judge and records the verdicts.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from prepare_blind_test import prepare_blind_test, build_judge_prompt


JUDGE_PROFILES = [
    "holistic-reader",
    "stylometry-rhythm",
    "consciousness-structure",
    "humor-bathos",
    "emotion-reality",
    "dialogue-social",
    "phase-genre-title",
    "synthetic-risk",
    "anti-ai-sentence",
    "literary-annotation",
    "background-fact",
    "background-display",
    "mid-article-randomness",
    "stylometric-drift",
]


@dataclass(frozen=True)
class RoundInfo:
    round_id: int
    kind: str
    seed: int
    directory: str
    judge_directory: str
    generated_sample: str
    prompt: str


def create_round(
    draft_path: Path,
    corpus_dir: Path,
    output_root: Path,
    round_id: int,
    seed: int,
    num_samples: int,
    fragment_chars: int,
    min_fragment_chars: int,
    length_tolerance: float,
    match_genre: str,
    placebo: bool,
    profile: str,
) -> RoundInfo:
    random.seed(seed)
    round_dir = output_root / f"round-{round_id:02d}-{'placebo' if placebo else 'impostor'}"
    mapping = prepare_blind_test(
        draft_path=draft_path,
        corpus_dir=corpus_dir,
        output_dir=round_dir,
        num_samples=num_samples,
        fragment_chars=fragment_chars,
        min_fragment_chars=min_fragment_chars,
        length_tolerance=length_tolerance,
        include_draft=not placebo,
        include_skill_context=False,
        include_titles=True,
        match_genre=match_genre,
    )
    prompt = build_judge_prompt(round_dir, len(mapping)).replace(
        "PROFILE: holistic-reader",
        f"PROFILE: {profile}",
    )
    prompt_path = round_dir / "prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    judge_dir = output_root / f"judge-view-{round_id:02d}"
    if judge_dir.exists():
        raise FileExistsError(f"Neutral judge directory already exists: {judge_dir}")
    judge_dir.mkdir(parents=True)
    shutil.copy2(prompt_path, judge_dir / "prompt.txt")
    for sample_path in sorted(round_dir.glob("sample-*.txt")):
        shutil.copy2(sample_path, judge_dir / sample_path.name)
    generated_sample = next((name for name, item in mapping.items() if item["is_draft"]), "NONE")
    return RoundInfo(
        round_id=round_id,
        kind=f"placebo:{profile}" if placebo else f"impostor:{profile}",
        seed=seed,
        directory=str(round_dir),
        judge_directory=str(judge_dir),
        generated_sample=generated_sample,
        prompt=str(judge_dir / "prompt.txt"),
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare multiple Anlin blind-evaluation rounds.")
    parser.add_argument("draft_path", type=Path, help="Draft markdown/text file")
    parser.add_argument("corpus_dir", type=Path, help="Directory containing original Anlin files")
    parser.add_argument("--rounds", type=int, default=8, help="Number of impostor rounds")
    parser.add_argument("--num-samples", type=int, default=5, help="Original samples per impostor round")
    parser.add_argument("--fragment-chars", type=int, default=0, help="Legacy diagnostic mode; 0 keeps complete articles")
    parser.add_argument("--min-fragment-chars", type=int, default=0, help="Minimum Chinese characters required for generated samples")
    parser.add_argument("--length-tolerance", type=float, default=0.65, help="Allowed relative length difference for complete-article impostor rounds")
    parser.add_argument("--match-genre", default="none", choices=("none", "auto", "standard", "sincere", "micro-hope", "surreal"), help="Optional genre/length matching anchor for impostor and placebo rounds")
    parser.add_argument("--include-placebo", action="store_true", help="Add one placebo round containing originals only")
    parser.add_argument("--placebo-rounds", type=int, default=2, help="Number of all-original placebo calibration rounds")
    parser.add_argument("--profiles", default=",".join(JUDGE_PROFILES), help="Comma-separated judge profiles to rotate across impostor rounds")
    parser.add_argument("--seed", type=int, default=1, help="Base random seed")
    parser.add_argument("--output-root", type=Path, default=None, help="Output root directory")
    args = parser.parse_args(argv)

    if not args.draft_path.is_file():
        parser.error(f"Draft file not found: {args.draft_path}")
    if not args.corpus_dir.is_dir():
        parser.error(f"Corpus directory not found: {args.corpus_dir}")
    if args.rounds < 1:
        parser.error("--rounds must be >= 1")
    if args.placebo_rounds < 0:
        parser.error("--placebo-rounds must be >= 0")
    profiles = [item.strip() for item in args.profiles.split(",") if item.strip()]
    if not profiles:
        parser.error("--profiles must contain at least one profile")
    placebo_rounds = args.placebo_rounds
    if args.include_placebo and placebo_rounds == 0:
        placebo_rounds = 1

    if args.output_root is None:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        args.output_root = Path(tempfile.gettempdir()) / f"anlin-blind-eval-{ts}"
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    rounds: list[RoundInfo] = []
    for index in range(1, args.rounds + 1):
        rounds.append(
            create_round(
                draft_path=args.draft_path.resolve(),
                corpus_dir=args.corpus_dir.resolve(),
                output_root=output_root,
                round_id=index,
                seed=args.seed + index,
                num_samples=args.num_samples,
                fragment_chars=args.fragment_chars,
                min_fragment_chars=args.min_fragment_chars,
                length_tolerance=args.length_tolerance,
                match_genre=args.match_genre,
                placebo=False,
                profile=profiles[(index - 1) % len(profiles)],
            )
        )

    for placebo_index in range(placebo_rounds):
        rounds.append(
            create_round(
                draft_path=args.draft_path.resolve(),
                corpus_dir=args.corpus_dir.resolve(),
                output_root=output_root,
                round_id=len(rounds) + 1,
                seed=args.seed + 10_000 + placebo_index,
                num_samples=args.num_samples,
                fragment_chars=args.fragment_chars,
                min_fragment_chars=args.min_fragment_chars,
                length_tolerance=args.length_tolerance,
                match_genre=args.match_genre,
                placebo=True,
                profile="placebo-calibrated",
            )
        )

    manifest = {
        "draft": str(args.draft_path.resolve()),
        "corpus": str(args.corpus_dir.resolve()),
        "fragment_chars": args.fragment_chars,
        "min_fragment_chars": args.min_fragment_chars,
        "length_tolerance": args.length_tolerance,
        "match_genre": args.match_genre,
        "placebo_rounds": placebo_rounds,
        "profiles": profiles,
        "opencode_isolation_preflight": {
            "commands": ["opencode debug paths", "opencode debug skill"],
            "resolved_config_root_policy": "must_match_controller_recorded_isolated_root",
            "required_non_builtin_skill_count": 0,
            "fail_closed_on_mismatch": True,
            "required_evidence": [
                "resolved config root matches the controller-recorded temporary isolated configuration root",
                "all non-built-in skills count is 0",
            ],
        },
        "rounds": [asdict(item) for item in rounds],
        "controller_rule": "Give each prompt.txt from judge_directory to an isolated pure judge. Do not run judges from the controller round directory, because those directory names may contain impostor/placebo labels and mapping.json. For opencode, run judges with --pure and the neutral judge_directory containing only prompt.txt and sample-*.txt. Before judging, record the expected isolated config root, run opencode debug paths in the same environment, and verify that the resolved config root matches it; then run opencode debug skill and verify that all non-built-in skills count is 0. Any resolved-root mismatch or any non-built-in skill invalidates the round. OPENCODE_CONFIG_DIR alone is not isolation evidence. On Windows or any build where debug paths still resolves the user config, set XDG_CONFIG_HOME to a temporary root and rerun both checks. Keep OPENCODE_CONFIG_DIR only when its resolved path is verified, and set OPENCODE_DISABLE_EXTERNAL_SKILLS=1 plus OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1 when available; --pure alone may not disable skills. Judges may read only prompt.txt and sample-*.txt and may answer NONE. If a judge uses any style skill, author-specific skill, original corpus, mapping, controller notes, web search, prior analysis, or round-kind directory names, mark that round contaminated. Titles are retained and normalized; title fit is evidence but cannot be the sole basis. Count a stable accusation only when IDENTIFIED is not NONE, confidence is >=75, and at least three independent evidence families are named, including one non-title/non-topic family. Report raw and stable rates plus placebo false accusations. Treat placebo rounds as original-text calibration; if the same evidence families accuse originals, lower confidence in those cues before revising the generator.",
    }
    manifest_path = output_root / "controller-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"output_root: {output_root}")
    print(f"manifest: {manifest_path}")
    for item in rounds:
        print(f"round {item.round_id:02d} [{item.kind}] judge_prompt: {item.prompt} generated: {item.generated_sample}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

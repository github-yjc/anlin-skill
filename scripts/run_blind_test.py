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
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from prepare_blind_test import prepare_blind_test, build_subagent_prompt


JUDGE_PROFILES = [
    "holistic-reader",
    "stylometry-rhythm",
    "consciousness-structure",
    "humor-bathos",
    "emotion-reality",
    "dialogue-social",
    "phase-genre-title",
    "ai-impostor-risk",
]


@dataclass(frozen=True)
class RoundInfo:
    round_id: int
    kind: str
    seed: int
    directory: str
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
    )
    prompt = build_subagent_prompt(round_dir, len(mapping)).replace(
        "PROFILE: holistic-reader",
        f"PROFILE: {profile}",
    )
    prompt_path = round_dir / "prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    generated_sample = next((name for name, item in mapping.items() if item["is_draft"]), "NONE")
    return RoundInfo(
        round_id=round_id,
        kind=f"placebo:{profile}" if placebo else f"impostor:{profile}",
        seed=seed,
        directory=str(round_dir),
        generated_sample=generated_sample,
        prompt=str(prompt_path),
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare multiple Anlin blind-evaluation rounds.")
    parser.add_argument("draft_path", type=Path, help="Draft markdown/text file")
    parser.add_argument("corpus_dir", type=Path, help="Directory containing original Anlin files")
    parser.add_argument("--rounds", type=int, default=3, help="Number of impostor rounds")
    parser.add_argument("--num-samples", type=int, default=5, help="Original samples per impostor round")
    parser.add_argument("--fragment-chars", type=int, default=0, help="Legacy diagnostic mode; 0 keeps complete articles")
    parser.add_argument("--min-fragment-chars", type=int, default=0, help="Minimum Chinese characters required for generated samples")
    parser.add_argument("--length-tolerance", type=float, default=0.65, help="Allowed relative length difference for complete-article impostor rounds")
    parser.add_argument("--include-placebo", action="store_true", help="Add one placebo round containing originals only")
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
    profiles = [item.strip() for item in args.profiles.split(",") if item.strip()]
    if not profiles:
        parser.error("--profiles must contain at least one profile")

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
                placebo=False,
                profile=profiles[(index - 1) % len(profiles)],
            )
        )

    if args.include_placebo:
        rounds.append(
            create_round(
                draft_path=args.draft_path.resolve(),
                corpus_dir=args.corpus_dir.resolve(),
                output_root=output_root,
                round_id=len(rounds) + 1,
                seed=args.seed + 10_000,
                num_samples=args.num_samples,
                fragment_chars=args.fragment_chars,
                min_fragment_chars=args.min_fragment_chars,
                length_tolerance=args.length_tolerance,
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
        "profiles": profiles,
        "rounds": [asdict(item) for item in rounds],
        "controller_rule": "Give each prompt.txt to an isolated judge. Judges may read only sample-*.txt and may answer NONE. Titles are retained and normalized; title fit is evidence but cannot be the sole basis. Count a stable accusation only when IDENTIFIED is not NONE, confidence is >=75, and at least three independent evidence families are named, including one non-title/non-topic family. Report raw and stable rates plus placebo false accusations.",
    }
    manifest_path = output_root / "controller-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"output_root: {output_root}")
    print(f"manifest: {manifest_path}")
    for item in rounds:
        print(f"round {item.round_id:02d} [{item.kind}] prompt: {item.prompt} generated: {item.generated_sample}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

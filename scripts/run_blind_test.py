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
    placebo: bool,
) -> RoundInfo:
    random.seed(seed)
    round_dir = output_root / f"round-{round_id:02d}-{'placebo' if placebo else 'impostor'}"
    mapping = prepare_blind_test(
        draft_path=draft_path,
        corpus_dir=corpus_dir,
        output_dir=round_dir,
        num_samples=num_samples,
        fragment_chars=fragment_chars,
        include_draft=not placebo,
        include_skill_context=False,
    )
    prompt = build_subagent_prompt(round_dir, len(mapping))
    prompt_path = round_dir / "prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    generated_sample = next((name for name, item in mapping.items() if item["is_draft"]), "NONE")
    return RoundInfo(
        round_id=round_id,
        kind="placebo" if placebo else "impostor",
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
    parser.add_argument("--fragment-chars", type=int, default=700, help="Approximate Chinese characters per sample")
    parser.add_argument("--include-placebo", action="store_true", help="Add one placebo round containing originals only")
    parser.add_argument("--seed", type=int, default=1, help="Base random seed")
    parser.add_argument("--output-root", type=Path, default=None, help="Output root directory")
    args = parser.parse_args(argv)

    if not args.draft_path.is_file():
        parser.error(f"Draft file not found: {args.draft_path}")
    if not args.corpus_dir.is_dir():
        parser.error(f"Corpus directory not found: {args.corpus_dir}")
    if args.rounds < 1:
        parser.error("--rounds must be >= 1")

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
                placebo=False,
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
                placebo=True,
            )
        )

    manifest = {
        "draft": str(args.draft_path.resolve()),
        "corpus": str(args.corpus_dir.resolve()),
        "fragment_chars": args.fragment_chars,
        "rounds": [asdict(item) for item in rounds],
        "controller_rule": "Give each prompt.txt to an isolated judge. Judges may read only sample-*.txt and may answer NONE.",
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


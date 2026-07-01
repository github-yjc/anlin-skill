#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepare anonymized samples for the Anlin blind-evaluation test.

Solves the "匿名隔离" (anonymous isolation) problem: corpus files and the
regenerated draft are stripped of metadata, assigned random sample-NN.txt
filenames, and written to a clean output directory.  A mapping.json records
which sample is the draft so the controller can later check the verdict.

Example:
    python prepare_blind_test.py regenerated-draft.md C:/Users/34025/Desktop/Anlin \
        --num-samples 5 --fragment-chars 700 --output-dir blind-test
"""

import argparse
import json
import os
import random
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Metadata stripping
# ---------------------------------------------------------------------------

def strip_corpus(text: str) -> str:
    """Remove everything before and including the '---' separator line.

    Corpus files have a YAML-like header terminated by '---' on its own line.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == '---':
            body = '\n'.join(lines[i + 1:])
            return body.strip()
    # No separator found — return original text stripped
    return text.strip()


def strip_draft(text: str) -> str:
    """Remove '<!-- Anlin-style ... -->' metadata comment line from a draft."""
    text = re.sub(r'<!--\s*Anlin-style[^>]*-->\s*\n?', '', text)
    return text.strip()


def chinese_len(text: str) -> int:
    """Count Chinese characters for rough fragment length matching."""
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def extract_fragment(text: str, target_chars: int) -> str:
    """Return a roughly target-sized contiguous fragment while preserving lines."""
    if target_chars <= 0 or chinese_len(text) <= target_chars:
        return text.strip()

    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return text.strip()

    starts = list(range(len(lines)))
    random.shuffle(starts)
    best = "\n".join(lines[: min(len(lines), 20)])
    best_delta = abs(chinese_len(best) - target_chars)

    for start in starts:
        chunk: List[str] = []
        for line in lines[start:]:
            chunk.append(line)
            current = "\n".join(chunk)
            current_len = chinese_len(current)
            delta = abs(current_len - target_chars)
            if delta < best_delta:
                best = current
                best_delta = delta
            if current_len >= target_chars:
                break
    return best.strip()


# ---------------------------------------------------------------------------
# File selection
# ---------------------------------------------------------------------------

def pick_corpus_files(
    corpus_dir: Path,
    num_samples: int,
    draft_path: Path,
) -> List[Path]:
    """Randomly select *num_samples* .md/.txt files from *corpus_dir*.

    The *draft_path* itself is excluded if it happens to live inside the
    corpus directory.
    """
    candidates = sorted(
        p for p in corpus_dir.iterdir()
        if p.is_file() and p.suffix.lower() in ('.md', '.txt')
    )
    # Exclude the draft if it is inside corpus_dir.
    draft_resolved = draft_path.resolve()
    candidates = [p for p in candidates if p.resolve() != draft_resolved]

    if len(candidates) < num_samples:
        raise ValueError(
            f"Corpus contains {len(candidates)} eligible file(s), "
            f"but {num_samples} were requested."
        )
    return random.sample(candidates, num_samples)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_subagent_prompt(output_dir: Path, num_total: int) -> str:
    """Build a self-contained subagent prompt for the blind distinguisher."""
    sample_files = sorted(
        p.name for p in output_dir.iterdir()
        if p.is_file() and p.name.startswith('sample-') and p.suffix == '.txt'
    )
    file_list = '\n'.join(f'  {name}' for name in sample_files)

    lines = [
        f"You are a blind literary style analyst.  You will read {num_total}",
        "anonymized Chinese prose samples. They are similar-length fragments.",
        "ZERO OR ONE sample may be generated. The rest are human-written by the",
        "same author. You may answer NONE if no sample is clearly generated.",
        "",
        "Your task:",
        "",
        "1. Read EVERY sample file listed below.  Do NOT read any other files —",
        "   not the original corpus, not skill references, not mapping.json.",
        f"   Only the {num_total} sample files in the output directory.",
        "",
        "2. Identify which sample is generated, or answer NONE if you cannot",
        "   identify a generated sample with enough confidence.",
        "",
        "3. Report your findings in this exact format:",
        "",
        "   IDENTIFIED: sample-NN.txt | NONE",
        "   CONFIDENCE: XX%",
        "   TOP 3 TELLS:",
        '     1. [tell description] — quote: "..."',
        '     2. [tell description] — quote: "..."',
        '     3. [tell description] — quote: "..."',
        "",
        "   Each tell MUST include a verbatim line or phrase from the identified",
        "   sample enclosed in double-quotes.  Your tells should reference specific",
        "   stylistic features (rhythm, vocabulary, sentence structure, emotional",
        "   tone, scene transitions, or structural patterns) rather than vague",
        "   impressions.",
        "",
        "SAMPLE FILES TO READ:",
        file_list,
        "",
        "Remember: there may be zero or one generated sample. Do your best to",
        "distinguish based on the text alone, and use NONE if the evidence is not",
        "strong enough.",
    ]
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def prepare_blind_test(
    draft_path: Path,
    corpus_dir: Path,
    output_dir: Path,
    num_samples: int = 5,
    fragment_chars: int = 0,
    include_draft: bool = True,
    include_skill_context: bool = False,
) -> Dict[str, dict]:
    """Create anonymized samples and return the mapping.

    Returns a dict of {sample_filename: {source, is_draft}}.
    """
    # --- Validate inputs ---
    if not draft_path.exists():
        raise FileNotFoundError(f"Draft file not found: {draft_path}")
    if not corpus_dir.is_dir():
        raise NotADirectoryError(f"Corpus directory not found: {corpus_dir}")

    # --- Create output directory ---
    if output_dir.exists():
        # Only allow re-use if it looks like a previous blind-test output.
        existing_samples = list(output_dir.glob('sample-*.txt'))
        existing_mapping = output_dir / 'mapping.json'
        if existing_samples or existing_mapping.exists():
            raise FileExistsError(
                f"Output directory already contains blind-test data: {output_dir}\n"
                "Use a different --output-dir to avoid contamination."
            )
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Select corpus files ---
    originals_needed = num_samples if include_draft else num_samples + 1
    originals = pick_corpus_files(corpus_dir, originals_needed, draft_path)

    # --- Strip and collect all samples ---
    samples: List[Tuple[str, str, bool]] = []  # (source_label, text, is_draft)

    for path in originals:
        raw = path.read_text(encoding='utf-8')
        stripped = strip_corpus(raw)
        stripped = extract_fragment(stripped, fragment_chars)
        samples.append((path.name, stripped, False))

    if include_draft:
        draft_raw = draft_path.read_text(encoding='utf-8')
        draft_stripped = strip_draft(draft_raw)
        draft_stripped = extract_fragment(draft_stripped, fragment_chars)
        samples.append((draft_path.name, draft_stripped, True))

    # --- Shuffle and write with random filenames ---
    random.shuffle(samples)
    total = len(samples)
    pad = max(2, len(str(total)))
    mapping: Dict[str, dict] = {}

    for i, (source, text, is_draft) in enumerate(samples, start=1):
        filename = f'sample-{i:0{pad}d}.txt'
        (output_dir / filename).write_text(text, encoding='utf-8')
        mapping[filename] = {
            'source': source,
            'is_draft': is_draft,
        }

    # --- Write mapping.json (for the controller only) ---
    mapping_path = output_dir / 'mapping.json'
    mapping_path.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    # --- Optionally copy skill context files ---
    if include_skill_context:
        script_dir = Path(__file__).resolve().parent
        references_dir = script_dir.parent / 'references'
        for ref_name in ('portable-corpus.md', 'vocabulary-rules.md'):
            src = references_dir / ref_name
            if src.exists():
                shutil.copy2(src, output_dir / ref_name)
            else:
                print(
                    f"Warning: skill reference not found, skipping: {src}",
                    file=sys.stderr,
                )

    return mapping


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare anonymized full-text samples for the Anlin "
            "Distinguisher blind test."
        ),
    )
    parser.add_argument(
        'draft_path',
        type=Path,
        help='Path to the regenerated draft .md file.',
    )
    parser.add_argument(
        'corpus_dir',
        type=Path,
        help='Directory containing original Anlin .md/.txt files.',
    )
    parser.add_argument(
        '--num-samples', '-n',
        type=int,
        default=5,
        metavar='N',
        help='Number of original corpus files to include (default: 5).',
    )
    parser.add_argument(
        '--fragment-chars',
        type=int,
        default=0,
        help='Approximate Chinese-character fragment length; 0 keeps full texts.',
    )
    parser.add_argument(
        '--placebo',
        action='store_true',
        help='Prepare a placebo round with no generated sample.',
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=None,
        help=(
            'Directory for anonymized samples. '
            'Defaults to a timestamped subdirectory of the system temp folder.'
        ),
    )
    parser.add_argument(
        '--include-skill-context',
        action='store_true',
        help=(
            'Copy portable-corpus.md and vocabulary-rules.md from the '
            "skill's references/ into the output directory."
        ),
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for reproducible file selection.',
    )
    args = parser.parse_args(argv)

    # --- Resolve output directory ---
    if args.output_dir is None:
        ts = datetime.now().strftime('%Y%m%d-%H%M%S')
        args.output_dir = Path(tempfile.gettempdir()) / f'anlin-blind-test-{ts}'
    output_dir = args.output_dir.resolve()

    # --- Seed RNG ---
    if args.seed is not None:
        random.seed(args.seed)

    # --- Run ---
    try:
        mapping = prepare_blind_test(
            draft_path=args.draft_path.resolve(),
            corpus_dir=args.corpus_dir.resolve(),
            output_dir=output_dir,
            num_samples=args.num_samples,
            fragment_chars=args.fragment_chars,
            include_draft=not args.placebo,
            include_skill_context=args.include_skill_context,
        )
    except (FileNotFoundError, NotADirectoryError, FileExistsError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # --- Print results to stdout ---
    total = len(mapping)
    draft_file = next((k for k, v in mapping.items() if v['is_draft']), 'NONE')
    print(str(output_dir))
    print()
    prompt = build_subagent_prompt(output_dir, total)
    (output_dir / 'prompt.txt').write_text(prompt, encoding='utf-8')
    print(prompt)
    print()
    print(f"--- Controller note: {total} samples prepared. Draft is {draft_file}. ---")
    return 0


if __name__ == '__main__':
    sys.exit(main())

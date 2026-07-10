#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepare anonymized samples for the Anlin blind-evaluation test.

Solves the "匿名隔离" (anonymous isolation) problem: corpus files and the
regenerated draft are stripped of metadata, assigned random sample-NN.txt
filenames, and written to a clean output directory.  A mapping.json records
which sample is the draft so the controller can later check the verdict.

Example:
    python prepare_blind_test.py regenerated-draft.md C:/Users/34025/Desktop/Anlin \
        --num-samples 5 --output-dir blind-test
"""

import argparse
import json
import random
import re
import statistics
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Metadata stripping
# ---------------------------------------------------------------------------

def normalize_title_text(title: str) -> str:
    """Remove formatting noise while preserving the generated title text."""
    title = title.strip()
    title = re.sub(r"^#+\s*", "", title).strip()
    title = re.sub(r"^(标题|题目)\s*[:：]\s*", "", title).strip()
    for marker in ("**", "__", "*", "_"):
        if title.startswith(marker) and title.endswith(marker) and len(title) > len(marker) * 2:
            title = title[len(marker):-len(marker)].strip()
    return title


def split_title_body(text: str) -> Tuple[str, str, bool]:
    """Split a complete article into normalized title and body."""
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return "", "", False

    first = lines[0].strip()
    title = ""
    had_title = False
    if first.startswith("# "):
        title = normalize_title_text(first)
        lines = lines[1:]
        had_title = True
    elif not re.search(r"[。！？!?，,：:；;]", first) and chinese_len(first) <= 24:
        title = normalize_title_text(first)
        had_title = True
        if len(lines) > 1 and not lines[1].strip():
            lines = lines[2:]
        else:
            lines = lines[1:]
    return title, "\n".join(lines).strip(), had_title


def normalize_article(title: str, body: str, include_title: bool) -> str:
    """Return a normalized complete article for blind review."""
    body = body.strip()
    title = normalize_title_text(title)
    if include_title and title:
        return f"# {title}\n\n{body}".strip()
    return body


def sample_title(text: str) -> str:
    """Read the normalized sample title, if one is present."""
    title, _, had_title = split_title_body(text)
    return title if had_title else ""


def strip_corpus(text: str, include_title: bool = True) -> str:
    """Remove corpus metadata while preserving a normalized title by default.

    Corpus files have a YAML-like header terminated by '---' on its own line.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == '---':
            title = ""
            for before in lines[:i]:
                candidate = before.strip()
                if candidate.startswith("# "):
                    title = normalize_title_text(candidate)
                    break
            body = '\n'.join(lines[i + 1:])
            if not title:
                title, body, _ = split_title_body(body)
            return normalize_article(title, body, include_title)
    title, body, _ = split_title_body(text.strip())
    return normalize_article(title, body, include_title)


def strip_draft(text: str, include_title: bool = True, require_title: bool = True) -> str:
    """Remove controller metadata while preserving the generated title."""
    text = re.sub(r'<!--\s*Anlin-style[^>]*-->\s*\n?', '', text)
    if re.search(r"(?m)^---\s*$", text):
        return strip_corpus(text, include_title=include_title)
    title, body, had_title = split_title_body(text.strip())
    if require_title and not had_title:
        raise ValueError("Draft must be a complete article with a title.")
    return normalize_article(title, body, include_title)


def chinese_len(text: str) -> int:
    """Count Chinese characters for rough fragment length matching."""
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def line_stats(text: str) -> Dict[str, float]:
    """Return simple line-length stats for controller diagnostics."""
    lengths = [chinese_len(line) for line in text.splitlines() if line.strip()]
    if not lengths:
        return {'lines': 0, 'mean': 0.0, 'stdev': 0.0, 'min': 0, 'max': 0}
    return {
        'lines': len(lengths),
        'mean': round(statistics.mean(lengths), 2),
        'stdev': round(statistics.pstdev(lengths), 2),
        'min': min(lengths),
        'max': max(lengths),
    }


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
    fragment_chars: int = 0,
    min_fragment_chars: int = 0,
    include_titles: bool = True,
    target_chars: int = 0,
    length_tolerance: float = 0.0,
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
    if min_fragment_chars > 0:
        eligible: List[Path] = []
        for path in candidates:
            raw = path.read_text(encoding='utf-8')
            stripped = strip_corpus(raw, include_title=include_titles)
            fragment = extract_fragment(stripped, fragment_chars)
            if chinese_len(fragment) >= min_fragment_chars:
                eligible.append(path)
        candidates = eligible
    if target_chars > 0 and length_tolerance > 0:
        eligible = []
        lower = max(0, int(target_chars * (1 - length_tolerance)))
        upper = int(target_chars * (1 + length_tolerance))
        for path in candidates:
            raw = path.read_text(encoding='utf-8')
            stripped = strip_corpus(raw, include_title=include_titles)
            fragment = extract_fragment(stripped, fragment_chars)
            current_chars = chinese_len(fragment)
            if lower <= current_chars <= upper:
                eligible.append(path)
        candidates = eligible

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
        "anonymized complete Chinese prose articles. Metadata was removed,",
        "titles were retained and normalized, and sample lengths were controlled.",
        "ZERO OR ONE sample may be generated. The rest are human-written by the",
        "same author. You may answer NONE if no sample is clearly generated.",
        "",
        "Use only the sample texts in this directory. Do not use outside",
        "instructions, external memories, web search, archive files, hidden",
        "mappings, filenames outside sample-*.txt, or prior knowledge about",
        "the source. Treat the source as anonymous.",
        "",
        "Your task:",
        "",
        "1. Read EVERY sample file listed below.  Do NOT read any other files —",
        "   no archives, no hidden mappings, no controller notes.",
        f"   Only the {num_total} sample files in the output directory.",
        "",
        "2. Identify which sample is generated, or answer NONE if the evidence",
        "   is not strong enough. Evaluate the title as part of the article,",
        "   but do not use title, filename, order, topic, or length as the sole",
        "   basis for identification.",
        "",
        "   Treat this as open-set verification, not forced choice. A stable",
        "   identification requires at least three independent evidence families,",
        "   at least one family that is not title/topic/length, and confidence >= 75%.",
        "   If the strongest case depends mainly on title neatness, prompt-topic",
        "   compliance, length, order, or one polished ending, answer NONE or set",
        "   confidence below the stable-identification threshold.",
        "",
        "   Before identifying a sample, test alternative explanations: topic,",
        "   genre, phase, short-form article, sincere mode, surreal mode, unusual",
        "   editorial polish, or ordinary authorial variation. Prompt-shape leakage",
        "   is strong only when title, scene order, required elements, and ending",
        "   all reveal the likely prompt; a topic match alone is not evidence.",
        "",
        "   Some rounds are all-original calibration rounds. If the same cue would",
        "   make you accuse several rough, sincere, short, or unusually structured",
        "   articles, treat that cue as weak. A real reader can notice oddness without",
        "   converting oddness into a generated-text accusation.",
        "",
        "3. Report your findings in this exact format:",
        "",
        "   PROFILE: holistic-reader",
        "   IDENTIFIED: sample-NN.txt | NONE",
        "   CONFIDENCE: XX%",
        "   PRIMARY_EVIDENCE_FAMILIES: family-1, family-2, family-3",
        "   DETAILED_REASONS:",
        '     1. [specific reason] | evidence: "..."',
        '     2. [specific reason] | evidence: "..."',
        '     3. [specific reason] | evidence: "..."',
        '     4. [specific reason] | evidence: "..."',
        '     5. [specific reason] | evidence: "..."',
        "   MOST_SOURCE_LIKE:",
        '     1. [feature] | deep-or-surface: deep | evidence: "..."',
        '     2. [feature] | deep-or-surface: surface | evidence: "..."',
        "   LEAST_SOURCE_LIKE:",
        '     1. [feature] | possible alternative explanation: topic/genre/phase/fragment/editorial/none | evidence: "..."',
        '     2. [feature] | possible alternative explanation: topic/genre/phase/fragment/editorial/none | evidence: "..."',
        "   AI_OR_IMITATOR_RISK:",
        "     [distinguish AI smoothness, human imitation, and natural variation]",
        "   PLACEBO_CHECK:",
        "     [why NONE remains plausible or implausible]",
        "   SOURCE_COHESION_CHECK:",
        "     [which samples still plausibly belong to the same source style, and why]",
        "   FINAL_REASONING:",
        "     [why this identification is or is not stable]",
        "",
        "   Each detailed reason MUST include a short verbatim line or phrase",
        "   from a sample enclosed in double-quotes. Use at least three evidence",
        "   families: title contract, lexical field, phrase texture, sentence rhythm, syntax,",
        "   associative movement, narrative distance, hidden spine, ending, humor,",
        "   Bathos, emotional masking, reality texture, dialogue/social noise,",
        "   body/material pressure, cognitive path, title/phase/genre fit, AI risk,",
        "   prompt-shape leakage, imitator risk, or alternative explanations.",
        "",
        "SAMPLE FILES TO READ:",
        file_list,
        "",
        "Remember: there may be zero or one generated sample. Do your best to",
        "distinguish based on the text alone. Use NONE when the evidence is not",
        "strong enough or would likely also accuse an original during calibration.",
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
    min_fragment_chars: int = 0,
    length_tolerance: float = 0.65,
    include_draft: bool = True,
    include_skill_context: bool = False,
    include_titles: bool = True,
    require_title: bool = True,
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

    # --- Prepare draft first so corpus selection can be length-matched. ---
    draft_sample: Optional[Tuple[str, str, bool]] = None
    target_chars = 0
    if include_draft:
        draft_raw = draft_path.read_text(encoding='utf-8')
        draft_stripped = strip_draft(
            draft_raw,
            include_title=include_titles,
            require_title=require_title,
        )
        draft_stripped = extract_fragment(draft_stripped, fragment_chars)
        draft_chars = chinese_len(draft_stripped)
        if min_fragment_chars > 0 and draft_chars < min_fragment_chars:
            raise ValueError(
                f"Draft sample has {draft_chars} Chinese characters, "
                f"below --min-fragment-chars={min_fragment_chars}. Expand the draft or "
                "use a matched short-genre evaluation."
            )
        target_chars = draft_chars
        draft_sample = (draft_path.name, draft_stripped, True)

    # --- Select corpus files ---
    originals_needed = num_samples if include_draft else num_samples + 1
    originals = pick_corpus_files(
        corpus_dir,
        originals_needed,
        draft_path,
        fragment_chars=fragment_chars,
        min_fragment_chars=min_fragment_chars,
        include_titles=include_titles,
        target_chars=target_chars,
        length_tolerance=length_tolerance if include_draft else 0.0,
    )

    # --- Strip and collect all samples ---
    samples: List[Tuple[str, str, bool]] = []  # (source_label, text, is_draft)

    for path in originals:
        raw = path.read_text(encoding='utf-8')
        stripped = strip_corpus(raw, include_title=include_titles)
        stripped = extract_fragment(stripped, fragment_chars)
        samples.append((path.name, stripped, False))

    if draft_sample:
        samples.append(draft_sample)

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
            'title': sample_title(text),
            'chars': chinese_len(text),
            'line_stats': line_stats(text),
        }

    # --- Write mapping.json (for the controller only) ---
    mapping_path = output_dir / 'mapping.json'
    mapping_path.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    # --- Blind isolation guard ---
    if include_skill_context:
        print(
            "Warning: --include-skill-context is deprecated and ignored; "
            "blind-evaluation directories must contain only samples, mapping.json, and prompt.txt.",
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
        help='Legacy diagnostic mode: approximate Chinese-character fragment length; 0 keeps complete articles.',
    )
    parser.add_argument(
        '--min-fragment-chars',
        type=int,
        default=0,
        help='Minimum Chinese characters required for the draft fragment; 0 disables.',
    )
    parser.add_argument(
        '--length-tolerance',
        type=float,
        default=0.65,
        help='Allowed relative length difference for complete-article impostor rounds.',
    )
    parser.add_argument(
        '--strip-titles',
        action='store_true',
        help='Diagnostic ablation only. Default keeps titles because titles are part of the article.',
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
            'Deprecated and ignored. Blind-evaluation output directories '
            'must not include skill reference files.'
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
            min_fragment_chars=args.min_fragment_chars,
            length_tolerance=args.length_tolerance,
            include_draft=not args.placebo,
            include_skill_context=args.include_skill_context,
            include_titles=not args.strip_titles,
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

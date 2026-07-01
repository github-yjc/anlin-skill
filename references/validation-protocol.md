# Validation Protocol

Validation improves confidence under stated conditions. It never proves authorship or objective indistinguishability.

Report only:

- test conditions
- corpus availability
- sample size
- judge type
- recognition/pass rate
- limitations

Do not report "无法区分", "本人级", "原文级", or "Anlin本人会这么写".

## Modes

### Draft Review

Use for ordinary generation quality.

1. Run:

```powershell
python scripts/check_anlin_violations.py draft.md
```

2. If full corpus is available, run:

```powershell
python scripts/compare_anlin_corpus.py draft.md --corpus-dir "C:\Users\34025\Desktop\Anlin"
```

3. Review using `review-rubric.md`.
4. Fix errors and identity/date mismatches. Warnings require manual inspection, not automatic failure.

### Full Corpus Mode

Applicable when `C:\Users\34025\Desktop\Anlin` or an equivalent corpus directory is available.

Run:

```powershell
python scripts/check_anlin_violations.py draft.md
python scripts/compare_anlin_corpus.py draft.md --corpus-dir "C:\Users\34025\Desktop\Anlin"
python scripts/run_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --rounds 3 --fragment-chars 700
```

`run_blind_test.py` prepares anonymous rounds and prints the judge prompts. If no LLM automation key is configured, the controller manually gives each prompt to an isolated judge and records verdicts.

### Portable Mode

Applicable when the full corpus is unavailable.

1. Run the checker.
2. Read `portable-corpus.md`, `samples-index.md`, and `review-rubric.md`.
3. Use fragment-level review only.
4. Do not run full-corpus blind evaluation.
5. Mark the result as portable review, not corpus validation.

## Blind Test Design

Use `scripts/prepare_blind_test.py` or `scripts/run_blind_test.py`.

Recommended command:

```powershell
python scripts/run_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --rounds 3 --fragment-chars 700 --include-placebo
```

Each round creates a clean directory containing only:

- `sample-01.txt`
- `sample-02.txt`
- ...
- `mapping.json` for the controller only
- `prompt.txt` for the judge

Judge rules:

- The judge may read only `sample-*.txt`.
- The judge must not read `mapping.json`, the original corpus, or skill files.
- If the round is an impostor round, exactly one sample is generated.
- If the round is a placebo round, no sample is generated and the correct answer is `NONE`.
- If the judge is forced to choose when there is no generated sample, that test design is invalid.

## Multi-Angle Judge Set

For serious evaluation, use at least three different impostor judge angles plus placebo:

- holistic reader: ordinary reader sense of naturalness, over-polish, and closure
- stylometry/rhythm: line length, punctuation, connector terms, phrase repetition, and vocabulary domain
- narrative voice: scene drift, emotional mixing, body/money/social grounding, and theme-first construction
- placebo-calibrated reader: all-original round; must be allowed and encouraged to answer `NONE`

Treat invalid format, timeout, or contaminated access as invalid, not as a pass or failure. Re-run invalid rounds or report them separately.

Common generated-text tells found in evaluation:

- uniformly short lines with little sentence-length variance
- every scene serving the prompt topic
- clean opening/ending mirror
- numbered or sectioned "small essay" structure
- symbolic object chain where every object means the same thing
- lack of ordinary social noise, dialogue, or boring non-symbolic detail
- short sincere/micro-hope/surreal pieces becoming polished prose poems

## Blind Judge Output

Require this exact format:

```text
IDENTIFIED: sample-03.txt | NONE
CONFIDENCE: 0-100
REASONS:
1. ...
2. ...
3. ...
```

The controller compares `IDENTIFIED` with `mapping.json`.

## Decisions

### Draft Decision

- `accept`: no blocking issues; warnings reviewed; genre gates acceptable.
- `revise`: local fixes needed.
- `rewrite`: identity/date mismatch, monotone structure, copied source package, or majority of gates fail.
- `inconclusive`: validation setup is incomplete or contaminated.

### Blind-Evaluation Decision

Do not use pass/fail language without sample counts.

Recommended wording:

```text
Under 3 impostor rounds and 1 placebo round, the judge identified the generated sample in 1/3 impostor rounds and falsely accused an original in 0/1 placebo rounds. This supports revision status X under these conditions only.
```

If a judge sees `mapping.json`, original corpus filenames, skill files, or previous analysis, mark the round contaminated and exclude it.

## Revision Priority

1. Authorship/provenance or date deception risk.
2. Copied source package or high overlap.
3. Identity/phase/genre mismatch.
4. Monotone theme or checklist stuffing.
5. Scene rhythm and ending.
6. Vocabulary drift and local phrasing.

## Controller Checklist

- [ ] Draft body contains no process labels.
- [ ] Corpus path and date-zone recorded outside prose.
- [ ] Checker output saved or summarized.
- [ ] Corpus comparison inspected for overlap, not treated as style proof.
- [ ] Blind rounds use isolated directories.
- [ ] Placebo rounds included for serious evaluation.
- [ ] Final claim reports conditions and rates only.

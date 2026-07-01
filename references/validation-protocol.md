# Validation Protocol

Validation improves confidence under stated conditions. It never proves authorship or objective indistinguishability.

Report only:

- test conditions
- corpus availability
- sample size
- judge type
- recognition/pass rate
- raw accusation rate and stable-accusation rate
- false-accusation rate
- invalid rounds
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
python scripts/run_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --rounds 8 --min-fragment-chars 550 --include-placebo
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
python scripts/run_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --rounds 8 --min-fragment-chars 550 --include-placebo
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
- Titles are retained and normalized for all samples; metadata is removed.
- Generated drafts must include the title as article text on the first line. The preparation script normalizes `# 标题`, plain first-line titles, and simple emphasis wrappers to the same `# 标题` form so title formatting does not become a leakage cue.
- Impostor rounds are length-matched by complete article length.
- The judge may evaluate title fit as one evidence family, but must not use title, filename, ordering, or length as the sole basis for identification.
- Treat blind review as open-set verification, not forced attribution. A stable accusation requires `IDENTIFIED` not `NONE`, confidence at least 75, and at least three independent evidence families, including one family that is not title, topic, length, filename, or order.
- If the strongest accusation depends mainly on title neatness, prompt-topic compliance, article length, file order, or one polished ending, record it as raw suspicion but not stable identification.
- If the round is an impostor round, exactly one sample is generated.
- If the round is a placebo round, no sample is generated and the correct answer is `NONE`.
- If the judge is forced to choose when there is no generated sample, that test design is invalid.
- If placebo false accusations exceed 20%, treat the judge setup as over-sensitive and revise calibration before using the rate as evidence against the generation workflow.

## Multi-Angle Judge Set

For serious evaluation, read `blind-judge-angles.md` and use multiple profiles plus placebo. Minimum serious setup:

- holistic reader: ordinary reader sense of naturalness, over-polish, and closure
- stylometry/rhythm: line length, punctuation, connector terms, phrase repetition, and vocabulary domain
- consciousness-structure: associative hooks, montage, time/space shifts, hidden spine
- humor-bathos: joke source, absurdity base, retreat timing, self-canceling lines
- emotion-reality: emotional masking, body/money/social texture, ordinary noise
- dialogue-social: dialogue plausibility, social collision, awkward residue
- phase-genre: date-zone, genre fit, title/ending, phase leakage
- ai-impostor-risk: AI smoothness, imitator over-display, surface/deep mismatch
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

Require the detailed format in `blind-judge-angles.md`. The minimal controller-parsed fields are:

```text
PROFILE: <profile>
IDENTIFIED: sample-03.txt | NONE
CONFIDENCE: 0-100
PRIMARY_EVIDENCE_FAMILIES: family-1, family-2, family-3
DETAILED_REASONS:
1. ...
2. ...
3. ...
MOST_ANLIN_LIKE:
LEAST_ANLIN_LIKE:
AI_OR_IMITATOR_RISK:
PLACEBO_CHECK:
FINAL_REASONING:
```

Each detailed reason must include a short quote from the sample. The controller compares `IDENTIFIED` with `mapping.json` and separately records raw accusations and stable accusations.

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
Under 8 impostor rounds and 1 placebo round, judges produced raw accusations in 2/8 impostor rounds, stable accusations in 1/8 impostor rounds under confidence >=75 and 3-family threshold, and falsely accused an original in 0/1 placebo rounds. This supports revision status X under these conditions only.
```

If a judge sees `mapping.json`, original corpus filenames, skill files, or previous analysis, mark the round contaminated and exclude it.

## Revision Priority

1. Authorship/provenance or date deception risk.
2. Copied source package or high overlap.
3. Identity/phase/genre mismatch.
4. Monotone theme or checklist stuffing.
5. Blind-test leakage: title, length, genre mismatch, short polished surface.
6. Scene rhythm and ending.
7. Vocabulary drift and local phrasing.

## Controller Checklist

- [ ] Draft body contains no process labels.
- [ ] Corpus path and date-zone recorded outside prose.
- [ ] Checker output saved or summarized.
- [ ] Corpus comparison inspected for overlap, not treated as style proof.
- [ ] Blind rounds use isolated directories.
- [ ] Titles retained and normalized for generated and original samples.
- [ ] Draft is not a length outlier for the selected complete-article protocol.
- [ ] Judge prompts require detailed quoted evidence and alternative explanations.
- [ ] Controller records confidence, evidence-family count, raw accusations, stable accusations, and placebo false accusations separately.
- [ ] Placebo rounds included for serious evaluation.
- [ ] Final claim reports conditions and rates only.

## Method Notes

Authorship-verification research distinguishes closed-set and open-set setups; serious blind review should behave like open-set verification and allow uncertain/non-answer outcomes. Stylometry commonly inspects frequent words, word/character n-grams, punctuation, and other linguistic features, but topic, genre, discourse type, and text length can mislead. AI-detection research also reports false positives and false negatives, so `NONE` and placebo rounds are not optional.

For literary structure, treat "意识流" as an associative method rather than random scene stacking: sensory observations, free association, looping repetition, unusual syntax, time/space montage, and inner psychological truth should leave observable textual traces. Local Anlin corpus evidence still outranks external theory.

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
python scripts/check_anlin_violations.py draft.md --strict --draft-gate
python scripts/compare_anlin_corpus.py draft.md --corpus-dir "C:\Users\34025\Desktop\Anlin"
python scripts/run_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --rounds 8 --min-fragment-chars 550 --placebo-rounds 2
```

`--strict` is a corpus-calibrated blocking gate. It should fail generated drafts only for deterministic contamination or high-risk structural buttons that do not hard-fail original corpus files. Other blind-review risks remain warnings and must be interpreted with placebo/original calibration.

`--draft-gate` is generated-draft-only. It promotes formal article length and prompt-shape risks that may appear in some originals but should still block clean generated drafts for complete-article blind evaluation. Do not use `--draft-gate` when reporting original-corpus hard-error calibration.

`run_blind_test.py` prepares anonymous rounds and prints the judge prompts. If no LLM automation key is configured, the controller manually gives each prompt to an isolated judge and records verdicts.

### Portable Mode

Applicable when the full corpus is unavailable.

1. Run the checker.
2. Read `portable-corpus.md`, `samples-index.md`, and `review-rubric.md`.
3. Use fragment-level review only.
4. Do not run full-corpus blind evaluation.
5. Mark the result as portable review, not corpus validation.

## Clean Generation Protocol

Formal blind evaluation must measure the skill, not extra help from the controller.

Generator setup:

- Start a fresh agent context for each article.
- Give the generator only the realistic user prompt, the target date/background contained in that prompt, and normal access to the Anlin skill.
- Use `evals/evals.json` `realistic_prompt` for formal blind evaluation. The richer `prompt` field is a stress-test prompt and must not be used to claim blind-evaluation performance.
- Do not provide previous blind-review failures, judge rubrics, source excerpts, corpus filenames, controller mappings, hidden expected elements, or manual advice such as "add montage", "add unrelated details", or "avoid prompt-shape leakage".
- If the generator reads `outputs/`, blind-round folders, `mapping.json`, judge reports, or controller notes before writing, mark the generation contaminated.
- Record the exact prompt, skill path, skill commit, model/surface, allowed tools, corpus availability, and whether web/background lookup was allowed.

If a test draft only succeeds because the prompt itself supplied style rules, classify the run as diagnostic, not a clean skill evaluation.

## Blind Test Design

Use `scripts/prepare_blind_test.py` or `scripts/run_blind_test.py`.

Terms:

- `impostor round`: an anonymous round where exactly one sample is the generated article and the rest are original corpus articles. It measures whether judges can find the inserted generated article.
- `placebo round`: an anonymous all-original round with no generated article. The correct answer is `NONE`; it measures false accusations and calibrates whether judges are over-sensitive to original-text oddness.
- `stable accusation`: a counted accusation that passes the confidence and evidence-family thresholds. Raw suspicion is recorded separately.

Recommended command:

```powershell
python scripts/run_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --rounds 8 --min-fragment-chars 550 --placebo-rounds 2
```

Each round creates a clean directory containing only:

- `sample-01.txt`
- `sample-02.txt`
- ...
- `mapping.json` for the controller only
- `prompt.txt` for the judge

Judge rules:

- The judge may read only `sample-*.txt`.
- The judge prompt must be source-neutral: use `MOST_SOURCE_LIKE` / `LEAST_SOURCE_LIKE`, not author-name field labels that may trigger a style skill.
- The judge must not read `mapping.json`, the original corpus, skill files, controller notes, previous verdicts, or web results.
- The judge must not invoke or rely on any style skill, author-specific skill, corpus memory, previous analysis, or source-name prior knowledge. For opencode judge automation, run `opencode run --pure --dir <judge-round-dir> <prompt>` from a directory containing only `prompt.txt` and `sample-*.txt`.
- Titles are retained and normalized for all samples; metadata is removed.
- Generated drafts must include the title as article text on the first line. The preparation script normalizes `# 标题`, plain first-line titles, and simple emphasis wrappers to the same `# 标题` form so title formatting does not become a leakage cue.
- Impostor rounds are length-matched by complete article length.
- Generated standard-diary drafts should clear the safer 700+ body-character buffer before complete-article impostor rounds. 650-699 can be used only with an explicit short/matched protocol and should not support formal full-article claims.
- The judge may evaluate title fit as one evidence family, but must not use title, filename, ordering, or length as the sole basis for identification.
- Treat blind review as open-set verification, not forced attribution. A stable accusation requires `IDENTIFIED` not `NONE`, confidence at least 75, and at least three independent evidence families, including one family that is not title, topic, length, filename, or order.
- If the strongest accusation depends mainly on title neatness, prompt-topic compliance, article length, file order, or one polished ending, record it as raw suspicion but not stable identification.
- If the round is an impostor round, exactly one sample is generated.
- If the round is a placebo round, no sample is generated and the correct answer is `NONE`.
- If the judge is forced to choose when there is no generated sample, that test design is invalid.
- Use at least two placebo rounds for serious evaluation. They disguise original articles as ordinary test samples and measure whether the judge over-accuses real corpus articles.
- If placebo false accusations exceed 20%, treat the judge setup as over-sensitive and revise calibration before using the rate as evidence against the generation workflow.
- If the same evidence families appear in placebo accusations and generated-sample accusations, report that cue as uncalibrated and do not use it alone as a generator failure root cause.

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
- placebo-calibrated reader: at least two all-original rounds; must be allowed and encouraged to answer `NONE`

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
MOST_SOURCE_LIKE:
LEAST_SOURCE_LIKE:
AI_OR_IMITATOR_RISK:
PLACEBO_CHECK:
SOURCE_COHESION_CHECK:
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
Under 8 impostor rounds and 2 placebo rounds, judges produced raw accusations in 2/8 impostor rounds, stable accusations in 1/8 impostor rounds under confidence >=75 and 3-family threshold, and falsely accused originals in 0/2 placebo rounds. This supports revision status X under these conditions only.
```

If a judge sees `mapping.json`, original corpus filenames, skill files, previous analysis, or invokes any style/author skill, mark the round contaminated and exclude it.

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
- [ ] Formal generation used `realistic_prompt` or an equivalently natural prompt, not the diagnostic stress prompt.
- [ ] Generator did not receive judge rubrics, source excerpts, prior failures, mappings, or manual style hints outside the skill.
- [ ] Corpus path and date-zone recorded outside prose.
- [ ] Checker output saved or summarized.
- [ ] Corpus comparison inspected for overlap, not treated as style proof.
- [ ] Blind rounds use isolated directories.
- [ ] Titles retained and normalized for generated and original samples.
- [ ] Draft is not a length outlier for the selected complete-article protocol.
- [ ] Judge prompts require detailed quoted evidence and alternative explanations.
- [ ] Controller records confidence, evidence-family count, raw accusations, stable accusations, and placebo false accusations separately.
- [ ] At least two placebo rounds included for serious evaluation.
- [ ] Final claim reports conditions and rates only.

## Date-Boundary Validation

Date-boundary validation checks whether the skill refuses or downgrades requests outside supported evidence, rather than inventing unsupported author state.

- `out-of-range`: target date is before the first known original date (`2022-04-04`) or otherwise outside the documented corpus support. Correct behavior is to refuse that provenance-sensitive date, ask for a supported date, or clearly mark the output as a fictional exercise if the user accepts that downgrade.
- `projection`: target date is after the latest corpus-supported point but can be grounded by user-provided facts or verified background. Correct behavior is low-confidence projection with no claim of original-level support.
- `inferred`: no concrete date is supplied. Correct behavior is to record uncertainty in the controller report and avoid specific real-world claims unless verified.

Do not blind-test an out-of-range refusal as a prose article. Score it as a boundary-handling case.

## Method Notes

Authorship-verification research distinguishes closed-set and open-set setups; serious blind review should behave like open-set verification and allow uncertain/non-answer outcomes. Stylometry commonly inspects frequent words, word/character n-grams, punctuation, and other linguistic features, but topic, genre, discourse type, and text length can mislead. AI-detection research also reports false positives and false negatives, so `NONE` and placebo rounds are not optional.

For literary structure, treat "意识流" as an associative method rather than random scene stacking: sensory observations, free association, looping repetition, unusual syntax, time/space montage, and inner psychological truth should leave observable textual traces. Local Anlin corpus evidence still outranks external theory.

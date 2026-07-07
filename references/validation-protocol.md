# Validation Protocol

Validation improves confidence under stated conditions. It never proves authorship or objective indistinguishability.

## Corpus Boundary

The distributable skill is usable without a local copy of the 38 originals. Runtime generation should rely on bundled portable evidence: `portable-corpus.md`, `samples-index.md`, `corpus-cards/`, `background-fact-classes.json`, and the checked-in `style-profile.json`.

The full original corpus is optional developer/controller evidence. Use it only when available for stronger checks: rebuilding cards or profile, deterministic copy-overlap gates, original calibration, and complete-article blind rounds. If `ANLIN_CORPUS_DIR` / `--corpus-dir <corpus-dir>` is unavailable, report portable or fragment-level review and do not claim full-corpus blind-evaluation performance.

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

## Evidence Preservation

Validation artifacts are part of the evidence chain. Do not delete generation logs, checker outputs, controller summaries, blind-round mappings, judge transcripts, stage snapshots, or failed-run notes merely because the docs are reorganized.

Use this ownership split:

- README may summarize the latest boundary for users.
- `references/development-log.md` preserves chronological failed-run evidence, model/provider availability notes, verification summaries, and architecture-change rationale.
- External case workspaces preserve raw generated drafts, `finalized/draft.md`, trace logs, `.anlin-clean-run-state.json`, `.anlin-clean-run-snapshots/`, controller summaries, and blind-round directories.
- The distributable runtime skill should not contain local output workspaces or machine-specific paths. Promote only durable prompts, calibration cards, smoke drafts, or reference summaries into the skill repository.

Moving or rephrasing logs is allowed only when the factual content remains recoverable from tracked files or preserved external artifacts. If there is uncertainty, keep the raw log and add a summary instead of replacing it.

## Modes

### Draft Review

Use for ordinary generation quality.

1. Run:

```powershell
python scripts/check_anlin_violations.py draft.md
```

2. If full corpus is available, run:

```powershell
python scripts/compare_anlin_corpus.py draft.md --corpus-dir <corpus-dir>
```

3. If a corpus profile exists or full corpus is available, run the stylometric ratio audit:

```powershell
python scripts/build_style_profile.py <corpus-dir> --output references/style-profile.json
python scripts/check_style_profile.py draft.md --phase <A|B|C|D> --genre <standard|sincere|micro-hope|surreal> --draft-gate --strict
```

4. Review using `review-rubric.md`.
5. Fix errors and identity/date mismatches. Warnings require manual inspection, not automatic failure.

### Full Corpus Mode

Applicable when the 38-article corpus or an equivalent corpus directory is available.

Run:

```powershell
python scripts/check_anlin_violations.py draft.md
python scripts/check_anlin_violations.py draft.md --strict --draft-gate --corpus-dir <corpus-dir>
python scripts/compare_anlin_corpus.py draft.md --corpus-dir <corpus-dir>
python scripts/build_style_profile.py <corpus-dir> --output references/style-profile.json
python scripts/check_style_profile.py draft.md --draft-gate --strict
python scripts/calibrate_style_profile.py <corpus-dir> --profile references/style-profile.json
python scripts/run_blind_test.py draft.md <corpus-dir> --rounds 8 --min-fragment-chars 550 --placebo-rounds 2 --match-genre auto
```

Formal blind-round count is fixed for current readiness claims:

- Use `8 impostor + 2 placebo` before any readiness claim.
- Do not report smaller smoke packages as target evidence. Smaller diagnostic rounds may exist in archived development logs, but they are not current pass/fail evidence.
- Report corpus availability, matching mode, judge isolation, confidence threshold, evidence-family threshold, invalid rounds, stable-identification rate, and placebo false-accusation rate.

`--strict` is a corpus-calibrated blocking gate. It should fail generated drafts only for deterministic contamination or high-risk structural buttons that do not hard-fail original corpus files. Other blind-review risks remain warnings and must be interpreted with placebo/original calibration.

`--draft-gate` is generated-draft-only. It promotes formal article length and prompt-shape risks that may appear in some originals but should still block clean generated drafts for complete-article blind evaluation. Do not use `--draft-gate` when reporting original-corpus hard-error calibration.

`--corpus-dir` on `check_anlin_violations.py` enables the deterministic copy-overlap gate. Use it for full-corpus formal validation; do not use it to calibrate an original against the same corpus unless the checker can skip the same source file.

`calibrate_style_profile.py` runs the profile against originals without `--draft-gate` and reports warning-family frequencies. If a family often flags originals, treat that family as weak blind-review evidence unless a hard gate or placebo-stable cue supports it.

`check_style_profile.py --phase/--genre` uses a phase+genre stratum when the corpus has enough originals, then falls back to phase, genre, or global priors. The JSON report records `profile_scope`. Do not hide a fallback; it is part of the test condition.

`run_blind_test.py` prepares anonymous rounds and prints the judge prompts. If no LLM automation key is configured, the controller manually gives each prompt to an isolated judge and records verdicts.

For short sincere, micro-hope, surreal, or otherwise non-standard drafts, add a matched-genre anchor instead of comparing only against random standard diary originals. The command below is a genre-specific example; use `--match-genre auto` when the controller should infer the closest stratum:

```powershell
python scripts/run_blind_test.py draft.md <corpus-dir> --rounds 8 --placebo-rounds 2 --match-genre sincere
```

`--match-genre auto|standard|sincere|micro-hope|surreal` uses the generated draft as a hidden anchor for both impostor and placebo rounds. It prefers same-genre, similar-length, similar-line-count originals, then backfills with nearest samples when the small corpus lacks enough exact matches. The mapping records `genre` and `match` diagnostics for controller audit. This is confound control, not a way to lower the bar: if the judge still identifies the generated sample against matched originals and placebo false accusations stay low, treat the evidence as stronger.

### Portable Mode

Applicable when the full corpus is unavailable.

1. Run the checker.
2. Read `portable-corpus.md`, `samples-index.md`, and `review-rubric.md`.
3. Use fragment-level review only.
4. Do not run full-corpus blind evaluation.
5. Mark the result as portable review, not corpus validation.

## Clean-Eval Protocol

Clean-eval blind evaluation must measure the skill, not extra help from the controller.

Generator setup:

- Start a fresh agent context for each article.
- Give the generator only the realistic user prompt, the target date/background contained in that prompt, and normal access to the `anlin-writing` skill.
- For bounded clean-eval, create an empty `.anlin-clean-eval-mode` marker in the case workspace or otherwise explicitly select clean-eval mode without adding style hints. The marker only selects the two-call protocol; it must not contain prompts, rubrics, examples, or failure analysis.
- Use `evals/evals.json` `realistic_prompt` for clean-eval blind evaluation. The richer `prompt` field is a stress-test prompt and must not be used to claim blind-evaluation performance.
- Do not provide previous blind-review failures, judge rubrics, source excerpts, corpus filenames, controller mappings, hidden expected elements, or manual advice such as "add montage", "add unrelated details", or "avoid prompt-shape leakage".
- If the generator reads `outputs/`, blind-round folders, `mapping.json`, judge reports, or controller notes before writing, mark the generation contaminated.
- Record the exact prompt, skill path, skill commit, model/surface, allowed tools, corpus availability, and whether web/background lookup was allowed.
- For development coverage, rotate generation models across a declared external pool instead of optimizing against one surface. Keep the concrete pool outside the distributable skill, because available providers and model IDs are installation-specific. Record the actual model string used, reasoning/thinking setting, and whether the model was unavailable. Choose the next model by random draw or round-robin before reading the case result, not by picking the model expected to pass.
- Use the provider's reasoning/thinking mode when the surface supports it, and record the setting. Do not pass reasoning traces, previous model failures, judge rubrics, or model-specific repair notes into the generator prompt.
- Treat model differences as failure discovery, not as model-specific runtime design. If one model exposes short-line grid, prose compression, binary reframe, tool routing, or background stuffing, fold the fix back as a general source/checker improvement. Do not add model-name branches to `SKILL.md`, `clean-generation-brief.md`, or runtime drafting instructions.
- For OpenCode generation against the current installed skill path, disable legacy or external skill scans when an older same-name copy exists outside `<skill-dir>`. Example:

```powershell
$env:OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1'
$env:OPENCODE_DISABLE_EXTERNAL_SKILLS='1'
opencode run --model '<model-id>' --dir <case-dir> <realistic_prompt>
```

  A generation stderr/log line that references any anlin-writing skill path other than the recorded `<skill-dir>` means the run used the wrong skill and must be marked contaminated.

If a test draft only succeeds because the prompt itself supplied style rules, classify the run as diagnostic, not a clean skill evaluation.

Generator-side preflight is allowed only through `clean_run_checker.py`. `CLEAN_RUN_PREFLIGHT` means the draft was not ready and no formal checker call was consumed. `CLEAN_RUN_PREFLIGHT_STOP` means the generator did not reach a checker-ready article within the bounded preflight attempts; record the run as invalid or failed and do not let the same generation agent continue repairing indefinitely. This preserves the distinction between clean-eval mode and ordinary user mode.

Do not use the wrapper process exit code as the bounded checkpoint result. Stop boundaries such as `CLEAN_RUN_PREFLIGHT_STOP` and `CLEAN_RUN_STOP` may exit with status 0 so generation agents do not mistake a protocol stop for a command failure. The controller must read `.anlin-clean-run-state.json`, the trace audit, strict hard gate, and style-profile report. When `.anlin-clean-run-snapshots/` exists, the controller must also inspect stage snapshots rather than relying only on the final bounded `draft.md`.

After each automated generation, run the trace checker on the captured agent log:

```powershell
python <skill-dir>/scripts/check_clean_eval_trace.py <case-dir>/opencode-output.txt --json
```

It flags clean-eval contamination such as loading repair/critic references before the first draft, continuing to write after `CLEAN_RUN_PREFLIGHT_STOP` / `CLEAN_RUN_STOP`, deleting `.anlin-clean-run-state.json`, switching to the normal checker in the bounded directory, or reading checker source for hidden terms.

## Developer Two-Checkpoint Evaluation

Development tests must measure source guidance, limited checker repair, and final repair convergence. Do not collapse them into one score.

Every tenth development iteration, and whenever the user asks for status, write a controller progress note with these fields: latest iteration range, bounded checkpoint counts, finalized checkpoint counts, `blind_round_readiness`, valid blind package count, stable generated-sample identification rate, placebo false-accusation rate, invalid rounds, and the next blocking mechanism. If no valid `8 impostor + 2 placebo` package exists for a ready draft, report the recognition rate as `N/A - no valid blind package yet`; do not substitute hard-gate pass rate, style-profile status, or a legacy small diagnostic round.

The first checkpoint is deliberately bounded: it is the result after natural source guidance and limited checker-driven repair, frozen at the clean-eval boundary. Within that checkpoint, distinguish three signals: first-submission source guidance, preflight readiness before any formal checker call, and the two-call checker boundary if the draft reaches it. A run stopped at `CLEAN_RUN_PREFLIGHT_STOP` is a source/preflight failure with no evidence that the two actual checker calls were tested. A run with `calls=2` tests the limited checker repair boundary. The second checkpoint is deliberately open-ended: it starts from a copied bounded draft and tests whether the skill's ordinary repair path can converge. These answer different failure questions. A clean finalized draft cannot retroactively make the bounded draft a success, and a failed finalized draft means the final article itself is still unresolved.

For each serious generation case, create two external artifacts outside `<skill-dir>`:

1. **Bounded clean-eval checkpoint**: the fresh generator receives only the realistic prompt plus normal access to `anlin-writing`. It may use `clean_run_checker.py` according to clean-eval rules, with bounded preflight and at most two actual checker calls. Save the resulting `draft.md`, checker state, hard-check report, style-profile report when available, stage snapshots, and controller notes under the case workspace. This checkpoint has two internal reads: first, did the first submitted complete article show enough natural source guidance before checker feedback; second, did the two-call checker boundary improve it enough before open-ended repair begins?
2. **Finalized repair checkpoint**: copy the bounded checkpoint draft into a separate `finalized/` case directory, then start from that copy and its visible checker results. Allow ordinary-user style repair loops, including multiple checker calls, rewrites from a new scene slate, and targeted profile/corpus review. Do not read or grep checker source, test files, or hidden threshold constants; a finalized run that inspects `check_anlin_violations.py`, `check_style_profile.py`, `clean_run_checker.py`, `test_anlin_tooling.py`, or threshold names such as `YELLOW_REVIEW_FAMILY_THRESHOLD` is contaminated even if the final draft later passes. Save the final article and full validation reports separately from the bounded checkpoint. This checkpoint answers: can the skill plus its checker/references converge to a usable final article in a realistic user workflow?

Finalized checkpoint pass gate:

- Normal `check_anlin_violations.py draft.md` success is not sufficient.
- Freeze the selected genre from the prompt, case metadata, or bounded draft before repair. A short sincere/micro-hope draft that becomes longer during repair should still be validated against the selected short-genre corridor, not reclassified as standard diary by accident.
- Run `check_anlin_violations.py <finalized-draft> --strict --draft-gate --genre <selected-genre>` and require zero `error` findings.
- During the repair loop, run `check_style_profile.py <finalized-draft> --draft-gate --strict --repair-brief --genre <selected-genre>` when the bundled profile is available. The repair brief is the generator-facing interface; it folds the long metric list into source actions so the repairing agent does not optimize every ratio one by one. After the finalized artifact is frozen, the controller may rerun `check_style_profile.py <finalized-draft> --draft-gate --strict --genre <selected-genre>` without `--repair-brief` for the full report. The script automatically uses `references/style-profile.json` from the installed skill unless `--profile` or `--corpus-dir` overrides it. A `revise` status means finalized repair failed. A missing profile makes the result `review`, not ready for blind rounds.
- Under `--strict --repair-brief`, a nonzero exit normally means the draft did not pass the profile gate and should be repaired by writing a complete revised `finalized/draft.md`. It is not by itself a tool failure. The repairing agent should not respond by reading hidden thresholds, printing a proposed final article only in the terminal, or continuing to analyze full metrics.
- The finalized article must exist in `<case-dir>/finalized/draft.md`. If the agent prints a repaired article to chat or a log but leaves that file unchanged from a non-pass bounded input, mark the finalized checkpoint invalid as an artifact failure.
- Style-profile `yellow` with zero errors is acceptable for the finalized checkpoint; record the yellow families, but do not keep rewriting solely to remove yellow warnings. Blind rounds and placebo calibration decide whether those remaining cues matter.
- Style-profile `review` is not a finalized checkpoint pass, even when `red_families` is empty. Use the report's `checkpoint_decision`; only `checkpoint_decision=pass` can enter blind-round preparation.
- If corpus is available, run copy-overlap comparison with `--corpus-dir <corpus-dir>`.
- Manually audit explicit prompt prohibitions because the generic checker may not know the prompt. If the user forbids a domain such as money, consumption, prices, games, romance, or family, any visible same-domain replacement is a blocking prompt-compliance failure even when hard/style gates are clean.
- Record repair iteration count and whether the final repair changed scene source, rhythm, title, background specificity, or only patched local wording.
- If finalized repair improves one rhythm metric by creating the opposite failure, such as 80+ uniform lines becoming 30-40 compressed prose lines, classify it as unresolved repair-path drift. Run `rebalance_line_rhythm.py` once as a corridor reset, then inspect scene function; do not continue metric ping-pong.
- If bounded fails but finalized passes, treat it as a source-guidance gap. If finalized also fails, treat it as a systemic or repair-path gap and inspect architecture before adding another detector.

After both artifacts exist, run the controller summary from the external case workspace:

```powershell
python <skill-dir>/scripts/summarize_dev_checkpoints.py <case-dir> `
  --bounded-draft <case-dir>/draft.md `
  --finalized-draft <case-dir>/finalized/draft.md `
  --trace-log <case-dir>/opencode-output.txt `
  --corpus-dir <corpus-dir> `
  --profile <skill-dir>/references/style-profile.json `
  --genre <standard|sincere|micro-hope|surreal> `
  --output-json <case-dir>/controller-audit/summary.json `
  --output-md <case-dir>/controller-audit/summary.md
```

The summary script copies drafts and available clean-run stage snapshots into `<case-dir>/controller-audit/` before running the normal hard checker, so the controller can audit a stopped bounded draft without mutating the bounded generation directory or bypassing the clean-eval stop rule. If `--genre` is omitted, the script attempts to infer it from an `eval-<id>` or eval-name case directory; explicit `--genre` is preferred for all formal reports, including `--genre standard`, and is especially important for non-standard short genres. The summary uses this genre for both hard-gate and style-profile checks. If the finalized checkpoint is not available yet, omit `--finalized-draft`; the result is a partial development summary and must not be treated as final convergence evidence.

The summary script exits nonzero unless both checkpoints are ready for blind rounds. This is intentional: a generated report is evidence, not a pass. Read `diagnosis`, `blind_round_readiness`, bounded status, finalized status, stage audit statuses, hard-error counts, style-profile status, and trace findings before deciding the next change.

Interpretation:

- bounded fails, finalized passes: strengthen Layer 0/Layer 1 generation guidance and clean-eval repair instructions; the ordinary repair path can recover, but the source loop is still weak.
- bounded passes, finalized does not pass: investigate repair instructions, style-profile drift, validator setup, or checker blind spots; repair may be making the draft worse or failing to resolve the real issue.
- bounded fails, finalized does not pass: treat it as a broader skill issue; inspect architecture, fact gates, voice model, repair instructions, style-profile assumptions, and deterministic checks before adding more local lint.
- bounded passes and finalized passes: run blind rounds and placebo calibration before reporting rates; still do not claim authorship or indistinguishability.

`finalized=review` is not a clean final success. It means the article may be locally usable for discussion but is not ready for blind rounds and must not be used to conclude "only source guidance is weak." Only `finalized=pass` supports that narrower diagnosis.

The finalized checkpoint is not allowed to retroactively improve the bounded checkpoint. Do not keep editing the bounded `draft.md` after `CLEAN_RUN_PREFLIGHT_STOP` or `CLEAN_RUN_STOP`; direct normal-checker use in that directory is a protocol violation. The checker records stop state both beside the draft and in a system temporary lock keyed by draft path, so deleting the local state file does not make the bounded run valid again. Report both results, including checker-call counts, preflight stop status, number of repair iterations, model/surface, prompt, skill commit, corpus availability, recognition rate, and false-accusation rate.

## Blind Test Design

Use `scripts/prepare_blind_test.py` or `scripts/run_blind_test.py`.

Terms:

- `impostor round`: an anonymous round where exactly one sample is the generated article and the rest are original corpus articles. It measures whether judges can find the inserted generated article.
- `placebo round`: an anonymous all-original round with no generated article. The correct answer is `NONE`; it measures false accusations and calibrates whether judges are over-sensitive to original-text oddness.
- `stable accusation`: a counted accusation that passes the confidence and evidence-family thresholds. Raw suspicion is recorded separately.

Formal command:

```powershell
python scripts/run_blind_test.py draft.md <corpus-dir> --rounds 8 --min-fragment-chars 550 --placebo-rounds 2 --match-genre auto
```

Each round creates a clean directory containing only:

- `sample-01.txt`
- `sample-02.txt`
- ...
- `mapping.json` for the controller only
- `prompt.txt` for the judge

`run_blind_test.py` also creates a neutral `judge-view-XX` directory for each round. Run automated judges from `judge-view-XX`, not from `round-XX-impostor` or `round-XX-placebo`, because round directory names leak the controller's answer key. A valid judge directory contains only `prompt.txt` and `sample-*.txt`.

For OpenCode automation, `--pure` disables external plugins but may still leave installed skills available. If any local writing/style skill is installed, run judges with an isolated `OPENCODE_CONFIG_DIR` or equivalent no-skill configuration. Also set `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` and `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` where supported. A judge stderr line such as `Skill "..."` invalidates that round even when the judge only read `sample-*.txt` afterwards.

Judge rules:

- The judge may read only `prompt.txt` and `sample-*.txt` in the neutral judge directory.
- The judge prompt must be source-neutral: use `MOST_SOURCE_LIKE` / `LEAST_SOURCE_LIKE`, not author-name field labels that may trigger a style skill.
- The judge must not read `mapping.json`, the original corpus, skill files, controller notes, previous verdicts, web results, or a directory path/name that exposes `impostor`, `placebo`, `generated`, or similar controller labels.
- The judge must not invoke or rely on any style skill, author-specific skill, corpus memory, previous analysis, or source-name prior knowledge. For opencode judge automation, run `opencode run --pure --dir <neutral-judge-view-dir> <prompt>` from a directory containing only `prompt.txt` and `sample-*.txt`, set a temporary no-skill `OPENCODE_CONFIG_DIR` when installed skills would otherwise auto-trigger, and disable external skill scans with `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` / `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`.
- Titles are retained and normalized for all samples; metadata is removed.
- Generated drafts must include the title as article text on the first line. The preparation script normalizes `# 标题`, plain first-line titles, and simple emphasis wrappers to the same `# 标题` form so title formatting does not become a leakage cue.
- Impostor rounds are length-matched by complete article length.
- Generated standard-diary drafts should clear the safer 850+ body-character buffer and normally target 900-1100 body Chinese characters before complete-article impostor rounds. 650-849 can be used only with an explicit short/matched protocol and should not support formal full-article claims.
- Use `--match-genre` for short sincere, micro-hope, surreal, or other non-standard drafts. Placebo rounds must be matched to the same hidden draft anchor, otherwise a judge may learn to accuse short/polished originals and the false-accusation rate will be understated.
- The judge may evaluate title fit as one evidence family, but must not use title, filename, ordering, or length as the sole basis for identification.
- Treat blind review as open-set verification, not forced attribution. A stable accusation requires `IDENTIFIED` not `NONE`, confidence at least 75, and at least three independent evidence families, including one family that is not title, topic, length, filename, or order.
- If the strongest accusation depends mainly on title neatness, prompt-topic compliance, article length, file order, or one polished ending, record it as raw suspicion but not stable identification.
- If the round is an impostor round, exactly one sample is generated.
- If the round is a placebo round, no sample is generated and the correct answer is `NONE`.
- If the judge is forced to choose when there is no generated sample, that test design is invalid.
- Use two placebo rounds for current formal readiness claims. They disguise original articles as ordinary test samples and measure whether the judge over-accuses real corpus articles.
- If placebo false accusations exceed 20%, treat the judge setup as over-sensitive and revise calibration before using the rate as evidence against the generation workflow.
- If the same evidence families appear in placebo accusations and generated-sample accusations, report that cue as uncalibrated and do not use it alone as a generator failure root cause.

## Multi-Angle Judge Set

For serious evaluation, read `blind-judge-angles.md` and use multiple profiles plus placebo. Serious-confirmation setup:

- holistic reader: ordinary reader sense of naturalness, over-polish, and closure
- stylometry/rhythm: line length, punctuation, connector terms, phrase repetition, and vocabulary domain
- consciousness-structure: associative hooks, montage, time/space shifts, hidden spine
- humor-bathos: joke source, absurdity base, retreat timing, self-canceling lines
- emotion-reality: emotional masking, body/money/social texture, ordinary noise
- dialogue-social: dialogue plausibility, social collision, awkward residue
- phase-genre: date-zone, genre fit, title/ending, phase leakage
- synthetic-risk: AI smoothness, imitator over-display, surface/deep mismatch
- anti-ai-sentence: binary reframe, explainer voice, pseudo-colloquial terms, ordered essay skeletons, single-line smell
- literary-annotation: em dash captioning, abstract feeling labels, and polished emotional subtitles
- background-fact: place, game, platform, phase, and unsupported specificity
- background-display: supported background facts used as a visible dossier checklist rather than lived constraints
- middle-randomness: middle-third off-axis branch, decorative texture, and prompt-execution completeness
- stylometric-drift: function-word habits, punctuation, line-length distribution, and repeated sentence templates
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
- [ ] Clean-eval generation used `realistic_prompt` or an equivalently natural prompt, not the diagnostic stress prompt.
- [ ] Generator did not receive judge rubrics, source excerpts, prior failures, mappings, or manual style hints outside the skill.
- [ ] Corpus path and date-zone recorded outside prose.
- [ ] Checker output saved or summarized.
- [ ] Corpus comparison inspected for overlap, not treated as style proof.
- [ ] Deterministic copy-overlap gate run with `--corpus-dir` when full corpus is available.
- [ ] Style-profile audit recorded when corpus is available; profile drift is treated as revision evidence, not proof of generation or authorship.
- [ ] Style-profile report records `profile_scope` and `cognitive_audit`; fallback to global priors is reported when phase/genre sample size is too small.
- [ ] Style-profile thresholds were calibrated against originals without `--draft-gate`; original warnings were not converted into hard failures.
- [ ] Blind rounds use isolated neutral judge directories whose paths do not reveal impostor/placebo status.
- [ ] Titles retained and normalized for generated and original samples.
- [ ] Draft is not a length outlier for the selected complete-article protocol.
- [ ] Explicit prompt prohibitions were manually checked; forbidden domains were not reintroduced through adjacent details.
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

Authorship-verification research distinguishes closed-set and open-set setups; serious blind review should behave like open-set verification and allow uncertain/non-answer outcomes. Stylometry commonly inspects frequent words, word/character n-grams, punctuation, and other linguistic features, but topic, genre, discourse type, and text length can mislead. Ratio constraints must be predictive intervals for a new document, not narrow confidence intervals around the corpus mean. AI-detection research also reports false positives and false negatives, so `NONE` and placebo rounds are not optional.

For literary structure, treat "意识流" as an associative method rather than random scene stacking: sensory observations, free association, looping repetition, unusual syntax, time/space montage, and inner psychological truth should leave observable textual traces. Local Anlin corpus evidence still outranks external theory.

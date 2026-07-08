# Stylometric Ratio Protocol

This reference defines the corpus-prior and predictive-interval layer for Anlin anonymous blind-evaluation work.

The goal is bounded:

- use the 38 local originals as a small-sample prior for measurable style surfaces
- detect generated-draft drift before blind review
- report test conditions, sample size, identification/pass rates, and false accusations only
- never claim real authorship or objective indistinguishability

Do not use this file as a drafting checklist. It is an audit and repair protocol.

## Core Position

The simple rule `p ± p * 15%` is not a valid hard boundary for a generated article.

It fails because it ignores:

- sample size: 38 originals are useful but small
- denominator size: a 350-character piece and a 1200-character piece cannot share the same tolerance
- author heterogeneity: date phase, genre, topic, and emotional state shift the distribution
- sparse features: rare signals can swing from 0 to visible with one occurrence
- feature dependence: line length, period density, and short-line ratio are correlated
- original eccentricity: an original can be unusual without being fake

Use prediction for a new document, not precision around the corpus mean.

## Evidence Classes

### Tier A: Hard Gates

Hard gates are not ratio-matched. They are deterministic contamination or high-risk generated-draft tells.

Examples:

- process leakage: AI, generated, validation notes, state card, checker output
- provenance deception or real-author claims
- copied source package or high surface overlap
- missing title for blind-evaluation articles
- unsupported specific geography, employer, district, route, current game rank, role, build, lane, or match report
- AI-reframe structures: `不是X，是Y`, `不是X，而是Y`, `不是因为X，而是因为Y`
- explainer voice: `本质上`, `真正的问题是`, `这说明`, `这意味着`, `换句话说`
- ordered essay skeleton: `首先`, `其次`, `最后`, `综上`
- therapeutic pseudo-humanizer phrases: `允许自己`, `接住自己`, `被看见`, `和自己和解`

If a hard gate fires, repair the local move through action, body, money, app surface, another person's line, or lower specificity. Do not repair by adding a different style marker.

### Tier B: Robust Low-Level Ratios

These are the best candidates for measurable constraints:

- body Chinese-character count
- non-empty body line count
- title Chinese-character count
- mean body-line length
- body-line length standard deviation
- short-line ratio
- long-line ratio
- punctuation density per 1000 Chinese characters
- function/connective term density per 1000 Chinese characters
- repeated local templates and 2-4 character n-gram texture

Use these as soft warning signals. A single outlier does not prove failure.

### Tier C: Medium-Level Structure Ratios

These can be partly automated and partly reviewed:

- paragraph/scene block count
- main-prompt-domain scene share
- off-axis branch share
- dialogue/screen/body/money/social texture share
- opening/middle/tail theme share, middle off-axis share, title-tail overlap, and body/money/social texture balance
- title type and title-body contract
- ending type and closure risk
- early detail return count

Do not force rare content tags. If the corpus often contains body or money pressure, that means generated drafts should have material consequence when the scene calls for it. It does not mean every draft must mention pain or payment.

### Tier D: Deep Style Signals

These remain reviewer features, not strict ratios:

- concrete entry -> crooked interpretation -> reality puncture -> defensive recovery -> exit
- associative movement by object, sound, body, platform wording, or memory trigger
- hidden spine without essay-plan visibility
- humor from real social/material friction
- emotion displaced into logistics rather than explained
- Bathos/retreat timing before closure

They are too semantic for exact percentage gates. Use blind-judge evidence families and placebo calibration.

### Tier E: Background Consistency

Background facts are guardrails, not ingredients.

Classify concrete facts:

- `supported`: appears in corpus, user facts, or verified lookup
- `generic`: low-specificity daily surface, such as 楼下, 小城, 招聘, 打游戏, 打王者
- `third-person`: appears as another person's action, platform discourse, or contrast
- `unsupported`: invented named district, route, employer, game role, current rank, build, tactic, or platform state

Supported does not mean mandatory. Unsupported specifics should be lowered or removed.

## Calibration Method

Build a profile from the original corpus using `scripts/build_style_profile.py`.

The calibration unit is the complete article, not a merged corpus blob. Store each original's feature values so the audit can compare a new draft to the per-document distribution.

### Empirical Intervals

For each numeric feature, compute:

- min, q05, q10, median, q90, q95, max
- mean for orientation only
- MAD-based robust deviation support

Use:

- q10-q90 as the ordinary band
- q05-q95 as the wide warning band
- outside q05-q95 as strong drift

Empirical intervals are preferred when the feature is continuous: line mean, line stdev, title length, body length, and paragraph count.

### Posterior Predictive Intervals

For count/proportion features, use a Beta-Binomial posterior predictive check:

- corpus successes = sum of observed feature counts
- corpus trials = sum of denominators
- prior = Beta(1, 1), unless a feature-specific prior is later justified
- posterior = Beta(1 + successes, 1 + trials - successes)
- for a draft denominator `n`, compute the predictive count interval for a new document

Use this for:

- punctuation counts over body Chinese characters
- connector counts over body Chinese characters
- short/long line counts over body lines
- AI-surface counts over body Chinese characters, when not already a hard gate

This handles denominator size. A one-occurrence feature in 300 characters is not the same evidence as one occurrence in 1300 characters.

### Robust Multivariate Risk

Do not build a high-dimensional classifier from 38 originals. It will overfit.

Instead:

- group features into independent families: length, title, line rhythm, punctuation, connectors, AI-slop, structure, background
- count family-level deviations, not every correlated metric
- fail only when multiple independent families deviate or a hard gate fires

Recommended controller interpretation:

- `green`: no hard errors; no soft drift families
- `yellow`: soft drift families present below the review threshold
- `review`: five or more independent yellow/red families require strong manual review and placebo comparison. In `--strict --draft-gate` controller checks this returns nonzero, but the report should still say `review`, not pretend the evidence is a hard authorship proof.
- `revise`: one hard gate, at least three independent red drift families, or soft-family drift beyond the original-calibrated upper bound
- `inconclusive`: profile missing, corpus count mismatched, or placebo false accusations high

## Drafting Use

Do not tell the generation agent to hit exact ratios before drafting.

Before drafting, use only coarse natural constraints:

- complete article with title for blind evaluation
- standard diary usually around corpus-length territory
- avoid prompt loyalty, AI-reframe sentences, unsupported specifics, and background stuffing
- let rhythm variance come from action, speech, body, thought, and interruption

After drafting, use the profile audit to make targeted repairs.

Examples:

- short-line ratio too high: merge where thought/action naturally runs longer; do not randomly lengthen lines
- line rhythm red after a prior split/merge repair: run `scripts/rebalance_line_rhythm.py draft.md --in-place` once as a corridor reset, then inspect whether the scene still reads like lived action rather than a report
- body lines below 45 after repair: treat it as prose-block compression, not as a successful fix for short-line grid
- comma density too low: add actual spoken/thought continuation, not decorative punctuation
- title length or title contract outlier: weaken diagnostic title rather than inventing a clever one
- connector density too high: remove explanatory glue and let adjacent scenes jump by object or action
- AI-reframe count nonzero: replace the reframe with the physical fact or another person's plain line
- background display risk: delete supported facts that do not change action, social position, body state, or the next scene

## Validation Use

Run this layer after deterministic hard gates and before blind review:

```powershell
python scripts/build_style_profile.py <corpus-dir> --output references/style-profile.json
python scripts/check_style_profile.py draft.md
python scripts/calibrate_style_profile.py <corpus-dir> --profile references/style-profile.json
```

For strict reporting, keep the profile file, skill commit, corpus path, corpus file count, and command arguments in the controller report.

Do not use profile success as a claim of authorship. It only means the draft did not drift beyond selected measurable corpus priors under this profile.

There are two profile interfaces:

- **Repair brief**: `check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre <genre>`. Use this directly in ordinary repair, or as a controller input before finalized repair to create `repair-brief.txt`. A finalized repair agent consumes the prepared brief; it should not run this command during the attempt. The command should return a compact source-action brief, not the full metric table. Under `--strict`, a nonzero exit usually means "not passed; write a revised draft.md" rather than "the tool crashed."
- **Full report**: `check_style_profile.py draft.md --draft-gate --strict --genre <genre>` without `--repair-brief`. Use this after the artifact is frozen for controller/developer audit. It should preserve full findings, observed values, interval diagnostics, family counts, and calibration evidence.

Do not replace the full report with the repair brief in controller summaries, calibration reports, or development logs. Do not hand the full report to a repair agent as a metric checklist when the goal is to write a better article.

### Phase/Genre Strata

`style-profile.json` stores global, phase, genre, and phase+genre summaries. Use the stratum only when the target has an explicit phase or genre and the stratum has enough originals; otherwise the checker falls back to global priors.

Examples:

```powershell
python scripts/check_style_profile.py draft.md --phase A --genre standard --draft-gate
python scripts/check_style_profile.py draft.md --genre sincere --draft-gate
```

The report records `profile_scope`, including whether it fell back. A stratum warning is still a drift cue, not proof of generation.

### Cognitive Soft Audit

The checker also reports a non-blocking `cognitive_audit` summary for concrete entry, crooked interpretation, reality puncture, defensive recovery, exit/retreat, associative hook, humor friction, and emotion displaced into logistics. This is a repair map, not an exact style score. Repair by changing how existing scenes think; do not insert labels to raise the score.

## Placebo Calibration

Every profile threshold must be checked against originals.

Required sanity tests:

- all 38 originals should have no hard style-profile errors
- originals may produce warnings; warnings are calibration data
- `calibrate_style_profile.py` should be saved or summarized for serious runs so warning families are not over-interpreted. It reports per-file red/yellow/independent family counts and recommended thresholds from original-placebo distribution.
- if many originals would be rejected by the profile, the profile is too narrow
- if a blind judge accuses originals with the same evidence families used against generated drafts, downgrade those cues

## Anti-Overfitting Rules

- Do not require rare features to appear.
- Do not treat corpus-zero as impossible unless the cue is a hard AI/fact/provenance gate.
- Do not use generated drafts to tighten corpus thresholds unless those drafts are stored as separate negative examples and never mixed into the source prior.
- Do not count correlated line metrics as independent proof.
- Do not make background facts visible just because the profile knows them.
- Do not force game, pain, money, doge, platform, or city cues.
- Do not tune to a single AI judge. Use placebo and multiple evidence families.
- Do not report a numeric score without test conditions and limitations.

## Source Confidence

High-confidence foundations:

- stylometry/authorship attribution commonly uses lexical, character, syntactic, semantic, and application-specific features
- high-frequency function words, character n-grams, punctuation, and rhythm features are useful but genre/topic-sensitive
- open-set verification must allow uncertainty and false positives
- AI detectors and perplexity/burstiness-style methods can mislabel human writing

Medium-confidence operational evidence:

- Chinese reader/forum observations about AI smell: binary reframes, over-balanced structure, smooth transitions, pseudo-colloquial phrases, and excessive completeness
- anti-slop prompt engineering patterns from public GitHub skills and style guides

Low-confidence or local-only evidence:

- any exact numeric threshold from 38 originals
- single-draft blind judge results
- one model's suspicion without placebo calibration

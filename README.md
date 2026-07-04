# anlin-writing

This OpenCode skill generates, reviews, and evaluates Anlin/日寄-style Chinese prose for anonymous blind evaluation. The target is narrow: reduce stable identification as generated text under documented test conditions, while reporting only conditions, sample size, recognition/pass rates, false accusations, invalid rounds, and limits.

It must not claim real authorship, provenance, or objective indistinguishability.

## Corpus Boundary

The distributable skill does not require every user to own the 38 original articles. Runtime generation and portable review use bundled summaries: `references/portable-corpus.md`, `references/samples-index.md`, `references/corpus-cards/`, `references/background-fact-classes.json`, and `references/style-profile.json`.

The full 38-article corpus is a developer/controller input, not a runtime dependency. Use it only when available to rebuild cards/profile, run copy-overlap checks, calibrate thresholds, or run complete-article blind rounds. Set `ANLIN_CORPUS_DIR` or pass `--corpus-dir <corpus-dir>` for those stronger validation tasks.

## Current Status

The skill is not yet proven to meet the `<=10%` stable impostor-identification target. The latest documented clean-eval sample before this architecture pass cleared the hard generated-draft checker but still failed the style-profile audit, with drift in period density, short-line share, line-length variance, and connector balance. No current report yet contains 15 clean-eval generation runs plus calibrated `3 impostor + 1 placebo` style rounds sufficient to claim the target.

The current architecture pass is addressing source-level guidance, not only detection. The main risk found in review was that several deep repair references still used old "must / at least / until clear" wording that could make a generation agent treat review signals as content quotas. This has been tightened so clean-eval generation keeps a bounded generator role, while ordinary user mode can continue repairing hard errors and controller validation remains separate.

Additional architecture audit found a source-load conflict: `SKILL.md` said clean-eval generation should begin with only `clean-generation-brief.md`, while the workflow and `runtime-brief.md` still implied loading the longer runtime brief before drafting. The clean-eval first-draft path now has a single source loop in `clean-generation-brief.md`: friction -> one pressure surface -> off-axis consequence -> fact gate -> complete titled draft -> bounded checker repair. `runtime-brief.md`, `generation-modes.md`, and `anti-ai-slop.md` remain available for ordinary drafting, analysis, or post-checker repair, not as mandatory pre-draft material.

Clean-eval preflight now blocks obvious non-article drafts before they consume a formal checker call: too short, too overfilled, fewer than 45 body lines, prose-block compression, missing connector/engine/rough self-damage signals, or high-risk AI/background surfaces. Preflight is bounded; if it prints `CLEAN_RUN_PREFLIGHT_STOP`, the generation run should stop and the external controller should mark it invalid or failed instead of letting the generator repair indefinitely.

Development validation now uses two checkpoints per serious case. The bounded checkpoint records the fresh-agent result after clean-eval limits, and the finalized checkpoint records the result after ordinary multi-round repair. A bounded failure with a finalized pass means source guidance should be strengthened; failures in both checkpoints indicate a broader skill problem, not just a stricter checker need.

This README should be updated whenever the runtime architecture, validation protocol, or latest evidence boundary changes. A fresh pass/fail claim still requires new verification and fresh clean-eval generations after the latest commit.

## Install Path

Install the skill wherever the target agent expects local skills. In this README, the installed directory is written as:

```text
<skill-dir>
```

Run commands from `<skill-dir>` unless a command explicitly says otherwise.

Trigger phrases include `anlin-writing`, `anlinwriting`, `Anlin`, `日寄`, `Anlin-style`, `像Anlin那样写`, `模拟日寄`, and requests for Anlin corpus evaluation. The OpenCode skill name is `anlin-writing`; `Anlin` remains a content-domain trigger alias because users naturally ask for that name.

## Architecture

The important design choice is separation of layers. The generation agent should not read every file before writing; that turns review categories into visible article ingredients.

```text
anlin-writing/
├── SKILL.md                         # routing, clean-eval boundary, output rules
├── references/
│   ├── clean-generation-brief.md     # first-draft contract
│   ├── runtime-layer-map.md          # architecture map for audits
│   ├── runtime-brief.md              # compact generation theory
│   ├── generation-modes.md           # scene modes and prompt-displacement lenses
│   ├── feature-budget.md             # feature budget, not shopping list
│   ├── anti-ai-slop.md               # built-in anti-AI-writing layer
│   ├── anlin-background.md           # post-scene fact gate
│   ├── background-fact-classes.json  # machine-readable fact classes
│   ├── voice-model.md                # deeper persona/cognition model for repair
│   ├── structure-patterns.md         # montage, title, ending, Bathos
│   ├── vocabulary-rules.md           # lexical and sentence-form boundaries
│   ├── role-orchestration.md         # role budget and deployment
│   ├── anlin-characters.md           # character facts and constraints
│   ├── review-rubric.md              # post-draft review gates
│   ├── writing-checklist.md          # critique card, not pre-draft recipe
│   ├── self-check.md                 # post-draft human/agent checklist
│   ├── stylometric-ratio-protocol.md # corpus-prior audit method
│   ├── style-profile.json            # generated profile from 38 originals
│   ├── validation-protocol.md        # clean-eval and blind testing protocol
│   ├── blind-judge-angles.md         # multi-angle judge matrix
│   ├── corpus-cards/                 # compact calibration cards, repair only
│   └── portable-corpus.md            # fallback when originals are unavailable
├── scripts/                          # deterministic gates and validation helpers
├── test/                             # tooling regression tests
├── evals/                            # 15 realistic and diagnostic prompts
└── audits/                           # smoke drafts for checker tests
```

Detailed layer ownership lives in `references/runtime-layer-map.md`.

The practical ownership rule is:

- Generator: realistic prompt + runtime layers + bounded clean-eval checker flow.
- Controller: corpus/profile/blind/placebo validation and documentation.
- Developer: when controller failures repeat, rewrite the earliest generation lens that caused the failure; do not merely add a new detection rule.

For development testing, the controller must keep the bounded clean-eval draft and the finalized repair draft as separate artifacts. The finalized draft can show that the repair path works, but it cannot be used to claim the first-pass natural guidance succeeded.

## Technique Sources

The old README-level technique summary is now mapped to maintained references:

| Technique | Source |
|---|---|
| Voice/persona model | `references/voice-model.md` |
| Bathos / retreat timing | `references/structure-patterns.md` |
| Fragment montage and associative hooks | `references/structure-patterns.md`, `references/generation-modes.md` |
| Pseudo-academic concepts and crooked analysis | `references/structure-patterns.md`, `references/voice-model.md` |
| Cognitive path | `references/generation-modes.md`, `references/voice-model.md`, `references/stylometric-ratio-protocol.md` |
| Corpus-verified frequency and ratio claims | `references/style-profile.json`, `scripts/build_style_profile.py`, `scripts/calibrate_style_profile.py` |

## Runtime Flow

For ordinary formal article generation:

1. Load `references/clean-generation-brief.md` first and use its source loop for the first complete draft.
2. Start from a small lived friction, not from a checklist.
3. Select scenes from action, body, screen, money, route, social misfire, memory trigger, or useless residue.
4. Open `anlin-background.md` only after selected scenes already contain facts that need checking.
5. Write a complete titled `draft.md` before the first checker.
6. Run `scripts/clean_run_checker.py draft.md --strict --draft-gate`.
7. If `CLEAN_RUN_PREFLIGHT` appears, revise before the first checker call is consumed; if `CLEAN_RUN_PREFLIGHT_STOP` appears, output the current draft unchanged and let the controller record failure.
8. Do at most one repair/rewrite and at most two clean-eval checker calls.
9. After the second checker call, output the current `draft.md` exactly.

For controller validation, use the full validation layer after generation:

```powershell
$env:ANLIN_CORPUS_DIR='<corpus-dir>'
python scripts/check_anlin_violations.py draft.md --strict --draft-gate --corpus-dir $env:ANLIN_CORPUS_DIR
python scripts/compare_anlin_corpus.py draft.md --corpus-dir $env:ANLIN_CORPUS_DIR
python scripts/check_style_profile.py draft.md --profile references/style-profile.json --draft-gate --strict
python scripts/calibrate_style_profile.py $env:ANLIN_CORPUS_DIR --profile references/style-profile.json
python scripts/run_blind_test.py draft.md $env:ANLIN_CORPUS_DIR --rounds 8 --placebo-rounds 2 --min-fragment-chars 550
```

## Core Principles

- Background facts are contradiction boundaries, not article ingredients.
- Game is allowed, not required. Corpus evidence supports broad 王者/游戏 facts, not current match reports, roles, lanes, ranks, tactical calls, or scoreboards.
- Anti-AI-writing behavior is built into this skill. Runtime generation must not depend on any external anti-slop or personal writing skill.
- Corpus ratios are post-draft audit tools, not pre-draft quotas.
- Blind judges must be open-set and may answer `NONE`.
- Placebo all-original rounds are mandatory for serious claims.
- If a failure repeats, improve the earliest responsible generation layer, not only the checker.
- Deep repair references are not shopping lists. Frequency notes and "high-value" signals must not cause forced insertion of game, body, platform, role, or background facts.
- Formal first drafts should not pre-load long repair or validation files. The source loop must make the first draft naturally avoid prompt obedience, AI-reframe sentences, and background stuffing before any checker result exists.

## Verification

Recommended local checks after edits:

```powershell
Get-ChildItem scripts\*.py | ForEach-Object { python -m py_compile $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
python -m unittest discover -s test -p test_anlin_tooling.py
$env:ANLIN_CORPUS_DIR='<corpus-dir>'
python scripts\build_style_profile.py $env:ANLIN_CORPUS_DIR --output references\style-profile.json
python scripts\calibrate_style_profile.py $env:ANLIN_CORPUS_DIR --profile references\style-profile.json
```

Fresh pass/fail claims should quote the exact command results. Older results in this README are status boundaries, not current verification.

## Development Notes

`work/` contains local iterative outputs and is intentionally ignored by git unless a specific artifact is promoted into `audits/`, `evals/`, or `references/`. Do not delete process artifacts until information-loss review confirms they are no longer needed.

Full-corpus validation requires local originals. Set `ANLIN_CORPUS_DIR` or pass `--corpus-dir <corpus-dir>`. Without originals, use `references/portable-corpus.md` and report the result as portable or fragment-level review.

The skill is maintained as part of the `github-yjc` skill collection under the MIT license.

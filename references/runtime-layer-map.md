# Runtime Layer Map

This file is for the developer, auditors, and failed-run diagnosis. Do not load it during ordinary article generation unless the user asks how the skill is organized.

The core architecture is layered so generation agents do not turn every review cue into article material.

## Layer 0: Entry Contract

Files:

- `SKILL.md`
- `references/clean-generation-brief.md`

Purpose:

- Tell the agent the goal, output rules, clean-eval boundary, and the smallest writing surface.
- Keep the first draft scene-led: friction -> scene slate -> fact gate -> draft -> bounded checker.
- Prevent visible process chatter and checker-loop contamination.
- Own the clean-eval first-draft source loop so the generator does not need long repair or validation files before writing.

Ordinary generation should start here and usually stay here until the first complete `draft.md` exists.

## Layer 1: Runtime Generation Lenses

Files:

- `references/runtime-brief.md`
- `references/generation-modes.md`
- `references/feature-budget.md`
- `references/anti-ai-slop.md`
- `references/vocabulary-rules.md` only when wording is uncertain or a repair needs it

Purpose:

- Shape how the first draft thinks.
- Convert blind-review risks into material choices before writing: title disguise, prompt displacement, middle drift, rough social/body consequence, rhythm from action, anti-AI sentence shape.
- Keep features as a budget, not a shopping list.

These files may guide ordinary drafting, explicit analysis, or repair after the first clean-eval checker pass, but they must not become visible subject matter. A negative example about AI, game, background, or detection is not a scene prompt. In clean-eval generation, Layer 1 is not a pre-draft requirement; Layer 0 must be enough to produce the first complete article.

## Layer 2: Post-Scene Fact Gate

Files:

- `references/anlin-background.md`
- `references/background-fact-classes.json`
- `references/era-state.md` when date or phase matters

Purpose:

- Background facts are contradiction boundaries, not content requirements.
- Prevent contradictions and unsupported specificity.
- Classify existing scene facts as `supported`, `generic`, `third-person`, or `unsupported`.
- Lower or delete facts after the scene slate exists.

This layer must not generate scenes. A supported fact is allowed only when the selected scene already needs it. Game, place, platform, illness, work, and named people are not mandatory style tokens.

## Layer 3: Repair And Calibration References

Files:

- `references/voice-model.md`
- `references/structure-patterns.md`
- `references/role-orchestration.md`
- `references/anlin-characters.md`
- `references/anlin-reference-library.md`
- `references/samples-index.md`
- `references/corpus-cards/`
- `references/writing-checklist.md`
- `references/self-check.md`
- `references/review-rubric.md`
- `references/anti-pastiche.md`
- `references/portable-corpus.md`

Purpose:

- Diagnose why a draft feels wrong.
- Repair failures by changing scene function, rhythm, cognition, dialogue, or fact specificity.
- Calibrate against source mechanisms without copying recognizable source packages.

These are not first-draft files in clean-eval generation. Opening too many of them before writing increases checklist pastiche, background stuffing, and prompt-shaped completeness.

## Layer 4: Controller Validation

Files:

- `references/stylometric-ratio-protocol.md`
- `references/style-profile.json`
- `references/validation-protocol.md`
- `references/blind-judge-angles.md`
- `references/subagent-prompts.md`
- `evals/evals.json`
- `evals/README.md`
- `scripts/` validation and repair helpers, especially `summarize_dev_checkpoints.py` for bounded/finalized development attribution
- `test/test_anlin_tooling.py`

Purpose:

- Validate drafts after generation.
- Run deterministic gates, corpus overlap, corpus-prior drift, placebo-calibrated blind rounds, and tooling tests.
- Report only test conditions, sample size, recognition/pass rates, false accusations, invalid rounds, and limitations.

This layer can fail a draft. It should not be handed to the generator as extra style advice during a clean-eval run.

## Operating Rule

If a failure repeats, fix the earliest responsible layer:

- prompt compliance, AI sentence shape, or background stuffing: update Layer 0 or Layer 1
- unsupported place/game/work facts: update Layer 2
- weak voice, rhythm, dialogue, cognition, or endings: update Layer 3 only if Layer 1 cannot explain the behavior compactly
- missed deterministic risk, bad thresholds, or invalid blind setup: update Layer 4

Do not solve a generation failure only by adding a new checker rule. A checker rule is acceptable when it protects the test, but the corresponding generation lens should also exist in Layer 0 or Layer 1 when the failure is common.

For clean-eval generation, keep the generator and controller separated:

- The generator sees only the realistic user prompt plus this skill's runtime layers. It may use the bounded checker flow, but it must not receive blind-judge rubrics, style-profile ratios, previous failure analysis, source excerpts, or controller mappings as extra pre-draft hints.
- The controller runs validation after the article exists. It may diagnose failures broadly, but source improvements should be folded back into Layer 0 or Layer 1 as compact generation lenses, not as another list of post-hoc detection angles.
- Deep references in Layer 3 are repair libraries. Their "must", "at least", and frequency notes describe review risk or genre tendency unless the text says they are hard gates. They are not permission to add game, background, body, platform, character, or dialogue material just to satisfy a line item.

The preferred developer move after a repeated blind-review failure is:

1. Name the earliest failed source decision, such as prompt-first opening, missing off-axis consequence, unsupported specificity, or visible AI reframe.
2. Add or revise one compact generation lens in Layer 0 when the failure affects formal first drafts.
3. Use Layer 1 or Layer 3 only when the fix needs a richer repair model.
4. Leave Layer 4 to measure the effect; do not make a new detector the only change.

During development evaluation, Layer 4 should record two checkpoints rather than one blended result:

- bounded clean-eval checkpoint: the draft after the fresh generator's bounded clean-eval limit, measuring natural source guidance and limited checker repair. When `.anlin-clean-run-snapshots/` exists, read `first_submission` as the natural-guidance evidence, preflight state as readiness evidence, and checker-call snapshots as limited-repair evidence. A preflight stop before call 1/2 is not the same failure as a draft that reaches call 2/2 and still fails.
- finalized repair checkpoint: a copied draft in a separate `finalized/` directory after ordinary multi-round repair, measuring whether the checker and repair references can converge without mutating the bounded result. The repaired article must be persisted to `finalized/draft.md`; terminal/log-only final prose is an artifact failure. It must pass strict hard-gate validation and style-profile audit when available; normal checker success alone is not a finalized pass.

If only the finalized checkpoint passes, update Layer 0 or Layer 1 before celebrating the repair. If finalized is only `review`, it is still unresolved and must not be counted as "final no problem." If neither checkpoint cleanly passes, broaden the diagnosis across layers instead of only tightening the checker.

For rhythm failures, prefer a corridor reset over single-metric ping-pong. `rebalance_line_rhythm.py` belongs to Layer 4 tooling, but the source lesson belongs earlier: a good draft should not need to bounce between prose-block compression and short-line grid repair.

Short non-standard genres have their own corridor. If a sincere or micro-hope draft is clean but reads like polished minimalism, do not force the standard-diary profile or add background/game/body packets as filler. Update Layer 0 or Layer 1 so the generator produces uneven short clusters, longer clumsy action or memory lines, rough logistics, awkward reply, and short factual retreats from the start. The same applies when the draft reads like a compact literary story: one title object, one family/memory proof-chain, one withheld message, and one final residue all explain each other. Layer 0 should break that source shape before first `draft.md`; Layer 1 can repair it by cutting symbolic echoes and adding present practical interruption. Layer 4 may warn with `短真诚小小说闭合`, but the detector is not the fix. When the style profile falls back from a small non-standard stratum to global priors, Layer 4 should mark the profile as inconclusive/review and require matched-original placebo reading; it should not become a pass or a reason to rewrite the piece into standard diary shape.

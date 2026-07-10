# Architecture Convergence Plan

This is a developer-facing convergence plan. Do not load it during ordinary article generation, clean-eval first drafts, finalized repair attempts, or blind judging. It preserves the current strategic decisions after cross-auditing the project state and five external agent analyses on 2026-07-08.

## Current Evidence Status

The target is not reached.

- Active-protocol recognition rate is `N/A`, not `0%`, not near `10%`, and not comparable to the final goal.
- No current evidence package contains all required pieces: 15 clean-eval cases, a calibrated `8 impostor + 2 placebo` blind-round package, low stable impostor identification, low placebo false accusation, and uncontaminated controller logs.
- Recent targeted evidence shows a boundary improvement, not target success: compact repair and atomic write contracts reduced terminal-only / unchanged-artifact failures, but the repaired articles still fail hard gate and style-profile readiness.
- The latest documented retest family is still `not_ready_for_blind_rounds`, with bounded and finalized failures concentrated in rhythm, source shape, social-decline consequence, rough self-damage, connector spread, and texture drift.

Current local repo facts after the route-coverage stabilization pass:

- Branch: `refactor/anonymous-blind-eval`.
- The `SKILL.md` shrink is directionally accepted as a thin-router move, provided it stays covered by route ownership tests and one-hop reference routing.
- The first route-contract regression batch has been addressed by moving brittle `SKILL.md`-only assertions to owner-file checks and adding `references/route-coverage-matrix.md`.
- Current recognition-rate evidence is still unchanged: no valid active-protocol blind package exists, so the rate remains `N/A`.

## Cross-Audit Of External Analyses

Five external analyses were read and compared against current repository facts. Their shared high-confidence findings are:

- The project has high activity but has not proven the target.
- Tooling, trace discipline, validation protocol, and evidence boundaries are much stronger than early versions.
- Text quality has not converged. The repeated failure loop is not random; it clusters around punctuation pendulum, source-shape drift, social-decline aftermath, private texture replacing public consequence, and underbuilt paragraph engine.
- Adding one more detector for every failed sample has diminishing returns and can make generators more self-conscious.
- `check_anlin_violations.py`, `test_anlin_tooling.py`, `runtime-brief.md`, `clean-generation-brief.md`, and `development-log.md` are now large enough to create maintenance and retrieval risks.
- Blind rounds should not be expanded until a fresh bounded/finalized case is pass-ready.

Important corrections to those analyses:

- Some quantitative claims are stale. For example, the failing test count is true for the current uncommitted `SKILL.md`, but older parent-thread committed states had passing tests.
- Some analyses phrase the active blind package as "8 generated + 2 placebo"; the active protocol is `8 impostor + 2 placebo`.
- Calling the project "at the starting line" is too harsh for engineering maturity. It is at the starting line only for final-rate evidence. It has progressed substantially in protocol integrity and failure attribution.
- Immediate blind rounds would not answer the target question because no current candidate is blind-round-ready.

## Accepted Strategic Decisions

### 1. Preserve The Thin-Router Direction, But Stabilize It

The old `SKILL.md` was overloaded. A skill body that front-loads clean-eval, ordinary generation, finalized repair, validation, blind judging, background, rhythm, and checker instructions makes every agent read too much before writing. This encourages analysis mode, metric-chasing, and checklist pastiche.

The new direction is correct:

- `SKILL.md` should route modes, artifact locations, no-load boundaries, reference map, output rules, and core safety.
- Source generation details should live in one-hop references.
- Controller validation should stay outside the generator-facing surface.

The thin router is acceptable only while route coverage proves that essential instructions are still reachable in the correct owner file and stage. Future edits should update `references/route-coverage-matrix.md` and owner-file tests together.

### 2. Fix Source Guidance Before Adding More Checkers

The repeated failures are not mainly missing detector coverage. The hardest failures are source-shape failures:

- first draft starts from prompt inventory rather than lived friction
- refusal aftermath remains a chat summary or room texture
- rough self-damage is ornamental, not action-changing
- rhythm is repaired by punctuation rather than born from unfinished action
- the model alternates between period grid, comma carpet, caption grid, and prose block

Checker additions are still allowed when they protect evaluation integrity or catch deterministic contamination, but every repeated generation failure must map back to Layer 0 or Layer 1 source guidance.

### 3. Treat Finalized Repair As A Public Interface, Not A Private Controller Loop

The compact repair brief solved a real failure mode: repair agents stopped printing a better final article only in logs and began writing `draft.md`. That is a meaningful interface improvement.

The current unresolved issue is quality: the brief still needs to drive one source rewrite without causing overfill, shrinkage, period grid, comma drag, or proof-ledger expansion.

The finalized repair interface should stay small:

- repair agent reads `draft.md` and `repair-brief.txt`
- optionally uses `finalized-repair-minimum.md` already routed by the skill
- writes one complete revised `draft.md`
- stops

Full style-profile output stays controller evidence after artifact freeze.

### 4. Use Intermediate Progress Metrics, But Do Not Substitute Them For Recognition Rate

Recognition rate remains `N/A` until a valid blind package exists. However, the project needs a progress dashboard to avoid arguing from long prose logs.

Track per iteration:

- case id and genre
- model surface and reasoning setting, as controller metadata only
- bounded first submission status
- preflight count and stop reason
- actual checker call count
- bounded hard error count and main families
- bounded style checkpoint decision
- finalized artifact mutation status
- finalized trace status
- finalized hard error count and main families
- finalized style checkpoint decision
- diagnosis: source guidance gap, repair path gap, systemic gap, ready
- blind-round readiness
- whether the change targeted the earliest failed layer

Only report recognition rate after valid `8 impostor + 2 placebo` rounds on ready candidates.

### 5. Keep Runtime Portable And Model-Agnostic

Runtime files must not depend on:

- the developer's local corpus path
- private external skills
- a specific provider or model
- local output workspaces
- hidden controller logs

Development tests may use local originals and model rotation. Runtime instructions should generalize model-specific failures into source shape, fact handling, sentence form, rhythm, tool routing, or repair-loop behavior.

## Rejected Or Deferred Ideas

### Do Not Run Blind Rounds Now

Running blind rounds before a candidate clears bounded/finalized readiness would produce a noisy failure package, not a meaningful target-rate estimate.

Use blind rounds only after:

- finalized hard gate has zero blocking errors
- style-profile checkpoint decision is `pass` or an explicitly accepted yellow-only state under protocol
- trace is clean
- prompt-compliance and fact gates are reviewed

### Do Not Freeze All Guardrail Work Forever

The advice to stop adding guardrails is directionally useful, but too absolute. Guardrails are still needed for artifact validity, contamination, unsupported facts, process leakage, and deterministic AI-slop. The rule is narrower: do not make a new checker rule the only response to a repeated source failure.

### Do Not Refactor The Checker Monolith Before Stabilizing The Interface

`check_anlin_violations.py` is large and should eventually be decomposed. But doing that before stabilizing the current `SKILL.md` shrink and source-generation path would add another variable. First stabilize route coverage and the generator-facing interface; then refactor the checker without semantic changes.

### Do Not Use Model-Specific Runtime Branches

Model rotation is useful for discovery. It must not create runtime branches such as "if deepseek do X" or "if longcat do Y". Convert failures into general guidance.

### Do Not Use Corpus Ratios As A Pre-Draft Recipe

The style profile is a post-draft audit. Predictive intervals and stylometric features can identify drift, but they should not become a checklist that the generator fills before writing.

## Priority Plan

### P0: Keep The `SKILL.md` Shrink Stabilized

Goal: keep the thin router safe as source guidance continues to change.

Tasks:

1. Audit every route-related test failure before deciding whether to restore text to `SKILL.md` or update an owner-file assertion.
2. Classify each failure:
   - essential runtime contract lost
   - essential contract moved to a reference but test still looks only in `SKILL.md`
   - outdated exact-string assertion
   - true omission caused by the shrink
3. Restore essential short phrases to `SKILL.md` only when they are routing-critical.
4. Prefer updating tests to inspect the routed reference graph when the instruction correctly moved out of `SKILL.md`.
5. Maintain route-coverage tests that assert:
   - clean-eval first-draft path loads only the minimal pack before first draft
   - background remains a post-scene fact gate
   - finalized repair has the short artifact-only interface
   - controller validation keeps full reports after artifact freeze
   - normal checker findings are not tool failures
6. Re-run unit tests and document current status.

Acceptance:

- `SKILL.md` remains thin.
- Essential instructions are reachable within one hop.
- Full test suite passes or remaining failures are explicitly unrelated and documented.

### P1: Maintain The Route Coverage Matrix

Goal: prevent information loss during architecture slimming and later source-guidance edits.

Maintain `references/route-coverage-matrix.md` as the table that maps critical instructions to owning files:

- no authorship/provenance claims
- complete titled article
- no process labels in prose
- output artifact location
- clean-eval marker and current-directory check
- bounded `clean_run_checker.py` only
- first-draft no-load rule
- social-decline refusal aftermath
- punctuation pendulum source fix
- background as contradiction boundary
- game allowed but not required
- finalized repair one write and stop
- compact repair brief versus full controller report
- `8 impostor + 2 placebo` readiness
- portable runtime and full-corpus optionality
- model-agnostic runtime

This matrix should be checked by tests using concepts and file ownership rather than brittle exact prose wherever possible. It is developer evidence, not a runtime writing aid.

### P2: Strengthen The Source Engine, Not The Detector

Goal: reduce first-draft source failures before checker feedback.

Focus on standard diary first, because it is the main current failure corridor.

Needed source lenses:

- breathing clusters are syntax units, not line-count targets
- every cluster starts from an unfinished action question: what is still happening after this line?
- social pressure must change the next action, not merely appear in text
- refusal aftermath upper bound: one consequence transfer, one or two later actions, loose exit
- private wet/dirty/object texture is usable only when it changes reply, route, payment, door, body, or social position while pressure is active
- connector spread should come from real turns, not sprinkled words
- title should come after body and avoid prompt-object proof loops

Avoid adding more prohibitions unless each prohibition is paired with a positive source move.

### P3: Make Finalized Repair Minimum Even Smaller In Practice

Goal: prevent repair agents from reading the brief as a checklist.

The repair brief should contain:

- status and pass/not-pass boundary
- one primary source action
- at most five source actions
- hard-gate blockers outranking style families
- explicit "write complete `draft.md` first, then stop"
- no full findings list
- no observed values, quantiles, count intervals, robust z, or threshold arithmetic

If finalized repair still writes but fails, do not keep expanding the brief. Instead, shrink the action language toward a single source operation and test whether the artifact changes in the intended direction.

### P4: Add A Development Progress Dashboard

Goal: see trend instead of relying on `development-log.md` prose.

The dashboard can be generated from existing controller summaries and clean-run state files. It should produce a small table grouped by iteration/case:

- bounded reached formal checker call: yes/no
- bounded hard errors
- finalized artifact mutation valid: yes/no
- finalized hard errors
- style checkpoint decision
- main failure family
- next layer to edit

This is not a blind metric. It is a navigation aid to avoid circling.

### P5: Use Human/Oracle Edit As Diagnostic, Not Evidence

Take one failed social-decline draft and manually edit it into a pass-like version. Then diff the change into source operations:

- what was deleted
- which action became load-bearing
- where the rhythm became uneven
- how title/tail moved
- which details were demoted or cut

Do not count the human-edited result as skill performance. Use it to improve Layer 0/1.

### P6: Refactor Checker Later With Semantic Freeze

Once router tests pass and at least one bounded/finalized candidate approaches readiness, split `check_anlin_violations.py` gradually:

- rule definitions
- shared feature extraction
- fact/background rules
- rhythm/shape rules
- AI-slop rules
- report formatting

First refactor should preserve outputs exactly for a fixture set. No new quality behavior in the first checker decomposition commit.

## No-Regression Constraints

Do not lose these constraints during future edits:

- The target is anonymous blind-evaluation performance, not authorship impersonation.
- Generated prose must be a complete titled article.
- Runtime must be portable and self-contained.
- Full 38 originals are developer/controller evidence, not a required runtime dependency.
- Background facts are contradiction boundaries, not material quotas.
- Game/background/person facts are allowed only when needed by the scene; never forced.
- Clean-eval generator must not receive controller reports, blind judge rubrics, previous failures, source excerpts, or hidden style hints before writing.
- Finalized repair is artifact-only: read brief plus draft, write one complete `draft.md`, stop.
- Full style-profile output remains available for controller audit.
- `8 impostor + 2 placebo` is the active readiness blind protocol; old smaller packages are historical only.
- Placebo rounds and false-accusation rate are mandatory for serious claims.
- If no valid blind package exists, recognition rate is `N/A`.

## Recommended Next Implementation Slice

Do not start with new generation or blind rounds.

1. Keep `SKILL.md` thin and covered by route-coverage tests.
2. Use `references/route-coverage-matrix.md` to check whether any new source guidance has a stable owner file.
3. Run one targeted source-generation retest on the known social-decline boundary only after the route/docs/tests are clean.
4. Judge the retest by bounded/finalized checkpoints, not blind rounds.
5. If bounded still fails before checker call 1/2, edit Layer 0/1 source engine.
6. If finalized writes but fails, shrink or clarify the repair action rather than expanding metric detail.
7. Only when one candidate is pass-ready, prepare blind rounds.

## Status Wording To Use

Accurate:

> Current recognition rate is `N/A` because no valid active-protocol blind package exists. The project has improved protocol integrity and failure attribution, but current drafts are not ready for blind rounds.

Inaccurate:

> Recognition is near 10%.

Inaccurate:

> Finalized wrote back, so the article is ready.

Inaccurate:

> The checker passes some originals, so generated results are proven.

Use the bounded/finalized distinction every time:

- bounded pass/fail measures natural source guidance plus limited clean-eval repair
- finalized pass/fail measures whether the public repair interface can converge from a copied draft
- blind rounds measure stable identification only after a ready artifact exists

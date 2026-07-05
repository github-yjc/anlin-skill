# anlin-writing

This OpenCode skill generates, reviews, and evaluates Anlin/日寄-style Chinese prose for anonymous blind evaluation. The target is narrow: reduce stable identification as generated text under documented test conditions, while reporting only conditions, sample size, recognition/pass rates, false accusations, invalid rounds, and limits.

It must not claim real authorship, provenance, or objective indistinguishability.

## Corpus Boundary

The distributable skill does not require every user to own the 38 original articles. Runtime generation and portable review use bundled summaries: `references/portable-corpus.md`, `references/samples-index.md`, `references/corpus-cards/`, `references/background-fact-classes.json`, and `references/style-profile.json`.

The full 38-article corpus is a developer/controller input, not a runtime dependency. Use it only when available to rebuild cards/profile, run copy-overlap checks, calibrate thresholds, or run complete-article blind rounds. Set `ANLIN_CORPUS_DIR` or pass `--corpus-dir <corpus-dir>` for those stronger validation tasks.

## Current Status

The skill is not yet proven to meet the `<=10%` stable impostor-identification target. The latest documented clean-eval cases still show bounded-generation failures before blind rounds: one family-dinner case reached the two-call checker boundary but failed profile validation, and the later rental-tap/key case stopped before formal checker call 1/2 and also failed finalized repair. No current report yet contains 15 clean-eval generation runs plus calibrated `3 impostor + 1 placebo` style rounds sufficient to claim the target.

The current architecture pass is addressing source-level guidance, not only detection. The main risk found in review was that several deep repair references still used old "must / at least / until clear" wording that could make a generation agent treat review signals as content quotas. This has been tightened so clean-eval generation keeps a bounded generator role, while ordinary user mode can continue repairing hard errors and controller validation remains separate. Recent repair risk is no longer only rhythm ping-pong: a draft can pass the strict hard gate but remain style-profile `review` because repair overfills body, money, route, screen, food/weather, and explicit cognition. The runtime now treats this as a thinning/source-repair problem, not a reason to add more features.

Development tests should now rotate across multiple model surfaces and report the exact model string plus reasoning/thinking setting for each case. This is a controller protocol, not runtime prose advice: failures from different models are generalized into source/checker improvements, and no model-specific branches should be added to the generation instructions.

Additional architecture audit found a source-load conflict: `SKILL.md` said clean-eval generation should begin with only `clean-generation-brief.md`, while the workflow and `runtime-brief.md` still implied loading the longer runtime brief before drafting. The clean-eval first-draft path now has a single source loop in `clean-generation-brief.md`: friction -> one pressure surface -> off-axis consequence -> fact gate -> complete titled draft -> bounded checker repair. `runtime-brief.md`, `generation-modes.md`, and `anti-ai-slop.md` remain available for ordinary drafting, analysis, or post-checker repair, not as mandatory pre-draft material.

Clean-eval preflight now blocks obvious non-article drafts before they consume a formal checker call: too short, too overfilled, fewer than 45 body lines, prose-block compression, missing connector/engine/rough self-damage signals, or high-risk AI/background surfaces. Preflight is bounded; if it prints `CLEAN_RUN_PREFLIGHT_STOP`, the generation run should stop and the external controller should mark it invalid or failed instead of letting the generator repair indefinitely.

Development validation now uses two checkpoints per serious case. The bounded checkpoint records the fresh-agent result after clean-eval limits, including bounded preflight and limited checker-driven repair; it also records stage snapshots for the first submitted draft, checker-call submissions, and bounded final. The finalized checkpoint records the result after ordinary multi-round repair from a separate copied draft. The finalized checkpoint is not allowed to pass on the normal checker alone; it must clear strict hard-gate validation and the bundled style-profile audit when the profile is available. A bounded failure with a finalized pass means source guidance should be strengthened; bounded failure with finalized `review/fail/invalid` means the final article is still unresolved and diagnosis must broaden across source guidance, repair references, fact gates, profile assumptions, and checker behavior.

Latest source-level tightening: clean-eval first draft may only use `clean-generation-brief.md` plus phase/date handling when needed. Repair, title, structure, anti-slop, corpus-card, judge, and ratio references are explicitly post-draft materials for this mode.

Latest controller tooling update: `scripts/summarize_dev_checkpoints.py` now summarizes bounded and finalized checkpoints separately, copies drafts and clean-run stage snapshots into an external `controller-audit/` directory before normal checker runs, classifies the development result as source guidance gap, repair path gap, systemic gap, or ready for blind rounds, and reports `blind_round_readiness`. The script exits nonzero for any state that is not ready for blind rounds; the JSON/Markdown report is still the evidence to read.

Latest development case after that update: `2022-food-delivery-heatstroke` was run as a bounded clean-eval case with a realistic prompt. The generated run was marked invalid because it read the correct skill but called the normal checker instead of `clean_run_checker.py`. The finalized repair checkpoint also did not pass strict/profile validation. Root fixes from that case: the checker route is now mode-first rather than normal-checker-first, and delivery prompts now explicitly forbid drifting into an unsupported married-rider biography.

Latest two-checkpoint retest after `e80e3d2`: `iteration-20260704-10/eval-02-food-delivery-heatstroke` used the realistic prompt with `longcat/LongCat-2.0`. Trace audit was clean, but bounded clean-eval stopped at preflight (`calls=0`, `preflights=3`) because the draft became a 148-line no-punctuation short-line grid with binary reframe residue. Finalized repair improved the binary reframe and line count but still failed strict hard gate (`粗粝自毁信号不足`, `段落发动机信号偏弱`, `行末逗号比例`) and style-profile stayed `review`, so the controller diagnosis is `systemic_gap`, not source-guidance-only. Root fixes from this case: preflight now flags overfragmented grids directly, runtime guidance distinguishes line-final commas from internal comma chains, and repair guidance requires semantic reread after mechanical merging.

Follow-up retest `iteration-20260704-11/eval-02-food-delivery-heatstroke` triggered the correct skill but wrote `draft.md` before checking `.anlin-clean-eval-mode` and then used the normal checker instead of `clean_run_checker.py`; trace checker marked the bounded run invalid. Root fix: the entry contract and clean generation brief now require a lightweight marker check as the first tool action before any `draft.md` write or checker command.

Follow-up retest `iteration-20260704-12/eval-02-food-delivery-heatstroke` correctly checked the clean-eval marker first and used `clean_run_checker.py`, but still stopped at bounded preflight (`calls=0`, `preflights=3`). Controller audit exposed two tooling issues that could distort diagnosis: `矿泉水` was falsely matched as unsupported game `泉水`, and real low-body/status material such as exposed toes, stomach trouble, and falling/being mistaken for碰瓷 was not counted as rough self-damage. Those checker issues are now covered by regression tests; the run itself still does not prove readiness for blind rounds.

Follow-up retest `iteration-20260704-13/eval-02-food-delivery-heatstroke` produced a clearer two-checkpoint diagnosis: bounded clean-eval was invalid because the generator kept writing after `CLEAN_RUN_PREFLIGHT_STOP`, while finalized repair from a copied draft passed strict hard gate and style-profile validation. Root fix from that run: stop boundaries in `clean_run_checker.py` now return a successful process status while still recording invalid/stopped state for the controller. This reduces the chance that a generation agent treats a protocol stop as a command failure to repair.

Follow-up retest `iteration-20260704-14/eval-02-food-delivery-heatstroke` confirmed the stop-boundary fix: trace audit was clean and the generator stopped after `CLEAN_RUN_PREFLIGHT_STOP`. The remaining bounded failure was more specific: preflight blocked before the first actual checker call because the draft had four distinct connector signals instead of the full draft-gate target. The preflight threshold is now limited to severe connector starvation, so near-miss drafts can enter the first real checker pass and use the bounded repair opportunity. The same pass also clarified that style-profile `yellow` is acceptable for finalized checkpoint pass; do not keep rewriting only to remove yellow warnings.

Follow-up run `iteration-20260704-15/eval-02-food-delivery-heatstroke` did not produce a draft. The generator loaded the correct skill and checked the clean-eval marker first, but then attempted to write `draft.md` to a wrong date-stamped absolute path outside the assigned case directory, so OpenCode rejected the file write. This is a contaminated tooling/path run, not a prose-quality result. Root fix: runtime instructions now require relative `draft.md` / `.\draft.md` in the current task workspace and forbid invented absolute output paths.

Follow-up retest `iteration-20260704-16/eval-02-food-delivery-heatstroke` used the correct relative path and had a clean trace, but bounded clean-eval still stopped at preflight (`calls=0`, `preflights=3`). The draft stayed compressed at 30 body lines, had zero early line-final comma continuations, retained a binary reframe, and lacked a rough losing-face body/social consequence. Finalized repair cleared the strict hard gate but timed out while mechanically chasing punctuation; style-profile remained `revise` with red `line_rhythm`, `punctuation`, and `ngram_texture`. Diagnosis is `systemic_gap`. Root fixes from this case: preflight now names the exact rhythm scripts to run, clean generation explains breathing clusters instead of sentence rows, and finalized repair now requires a rhythm-reset rewrite rather than repeated percentage tweaking.

Follow-up run `iteration-20260704-17/eval-02-food-delivery-heatstroke` triggered the skill but did not enter clean-eval mode: it wrote before checking the marker and used the normal checker repeatedly, then ran `split_long_lines.py` directly. The run is invalid for bounded measurement. Root fix: the skill description now exposes the `.anlin-clean-eval-mode` marker and `clean_run_checker.py` route so the model sees the clean-eval hard entry even if it under-loads the full body.

Follow-up retest `iteration-20260704-18/eval-02-food-delivery-heatstroke` restored clean-eval routing: marker check happened first, the wrapper ran, and `split_long_lines.py` was used after the first preflight. The run still became invalid because the generator continued writing after `CLEAN_RUN_PREFLIGHT_STOP`, then hit `CLEAN_RUN_STOP`. Root fix: wrapper stop output and runtime docs now place `FINAL BOUNDARY`, `DO NOT WRITE draft.md`, and read-only next-action language at the start of the stop message.

Follow-up retest `iteration-20260704-23/eval-02-food-delivery-heatstroke` used the realistic prompt with `longcat/LongCat-2.0` after commit `4be07ac`. The bounded run again produced a complete titled article but was invalid: the generator wrote `draft.md` before checking `.anlin-clean-eval-mode` and used the normal checker instead of `clean_run_checker.py`. The copied `finalized/` repair then passed strict hard gate and style-profile validation (`yellow`, zero errors), so the controller diagnosis is `source_guidance_gap`: the final article can converge, but the first-draft/limited-checker path is still too weak. Root fix from this case: `clean-generation-brief.md` now puts the marker check at the top as the first tool action, and `check_clean_eval_trace.py` separately flags `clean-eval写稿前未检查模式标记` so future reports identify the entry failure directly.

Follow-up retest `iteration-20260704-24/eval-02-food-delivery-heatstroke` confirmed the marker/wrapper entry fix: the run produced `.anlin-clean-run-state.json` and stage snapshots. Bounded still failed before any actual checker call (`calls=0`, `preflights=3`) and then contaminated the run by writing after `CLEAN_RUN_PREFLIGHT_STOP`. The first-submission snapshot had hard failures for invented spouse identity, formulaic comment-chain/video reaction, connector starvation, and literary ending. Finalized repair cleared strict hard errors but remained style-profile `review` with red `line_rhythm`, so the diagnosis is `systemic_gap`. Root fixes from this case: `CLEAN_RUN_PREFLIGHT_STOP` no longer prints repairable preflight details to the generator, but stores them in state for controller diagnosis; the clean generation brief now explicitly scans for unsupported spouse/child identities in delivery prompts and treats rider videos with `有人说...` as comment-chain residue; finalized repair now treats `review` with red `line_rhythm` as unresolved, not acceptable `yellow`.

Follow-up retest `iteration-20260704-25/eval-02-food-delivery-heatstroke` used the realistic prompt with `longcat/LongCat-2.0`. The bounded trace was clean and respected the stop boundary, but the run stopped at preflight before any actual checker call (`calls=0`, `preflights=3`), so it is a source/preflight failure rather than evidence about the two real checker calls. The bounded final had no hard errors but style-profile stayed `revise` with red `connectors`, `line_rhythm`, and `punctuation`. Finalized repair then failed both strict hard gate (`高频词覆盖不足`, `散文块压缩`) and style-profile (`revise`, red `line_rhythm`, `ngram_texture`, `punctuation`) after compressing the draft into 36 body lines. Diagnosis is `systemic_gap`. Root fixes from this case: clean/finalized guidance now separates first-submission, preflight readiness, two-call checker boundary, and finalized convergence; `rebalance_line_rhythm.py` was added and wired into clean-run normalization; runtime docs now explicitly reject repairs that swing from short-line grid to 30-40-line prose blocks.

Follow-up retest `iteration-20260704-26/eval-02-food-delivery-heatstroke` used the realistic prompt with `longcat/LongCat-2.0` after commit `e722cc6`. The run correctly triggered `anlin-writing`, checked `.anlin-clean-eval-mode` before drafting, used `clean_run_checker.py`, and reached the actual two-call checker boundary (`calls=2`, `preflights=2`) without trace contamination. Bounded still failed: hard errors were zero, but style-profile stayed `revise` with red `line_rhythm`, `ngram_texture`, and `punctuation`; stage snapshots show the first submission was 12 visible lines / about 1607 Chinese characters, so the source draft still began as compressed prose. A copied `finalized/` repair passed strict hard gate and style-profile (`yellow`, zero errors, zero red families), so the controller diagnosis is `source_guidance_gap`: ordinary repair can converge, but first-draft natural guidance and limited-checker readiness are still too weak. Root fixes from this case: `clean-generation-brief.md` and `SKILL.md` now state that clean-eval must not write prose first and then cut it; first drafts should directly target a middle rhythm corridor with several <=8-character breath drops and several rough long lines; `clean_run_checker.py` now uses the same <=8-character short-breath concept as style-profile and uses a stronger long-line rebalance before the second checker.

Follow-up retest `iteration-20260704-27/eval-02-food-delivery-heatstroke` used the realistic prompt with `longcat/LongCat-2.0` after commit `d45b391`. This run directly exercised the two-checkpoint development protocol. Bounded clean-eval reached the actual two-call checker boundary (`calls=2`, `preflights=2`, clean trace) but failed: first submission was still prose-shaped, stage audits stayed `fail`, bounded final had strict hard errors and style-profile `revise` with red `connectors`, `line_rhythm`, `ngram_texture`, and `punctuation`. A copied `finalized/` repair then converged after ordinary multi-round repair: strict hard gate had zero errors and style-profile was `yellow`. The controller diagnosis is `source_guidance_gap`, not readiness for blind rounds. Root fixes from this case: the earliest generation layer now treats "write prose then split it" as a failed source start, and it flags softer binary self-corrections such as `也不是疼，就是...`, `不是认识，就是...`, and `最疼的不是X，是Y` before the checker rather than leaving them for post-hoc repair.

Follow-up retest `iteration-20260704-28/eval-02-food-delivery-heatstroke` used the same realistic prompt after commit `00da12e`. Trace audit was clean, but bounded clean-eval stopped at preflight before formal checker call 1/2 (`calls=0`, `preflights=3`) because one binary reframe remained after repair. Stage snapshots show the first submission had two binary reframes; the generator fixed one and missed the other. The copied finalized repair cleared strict hard errors, but style-profile stayed `review` with five yellow drift families (`cognitive_mechanism`, `connectors`, `punctuation`, `structure`, `texture`) and no red families. Diagnosis is `systemic_gap`, not ready for blind rounds. Root fixes from this case: clean-run preflight now reports binary-reframe occurrence count and examples, tells the generator to scan all lines, and switches surface-only preflight repair to local replacement rather than adding scenes, short drops, body symptoms, money lines, platform facts, or other texture. Source guidance and repair references also now warn that overfilled texture/cognition can make a locally clean draft still fail finalized validation.

Follow-up retest `iteration-20260705-02/eval-02-food-delivery-heatstroke` used the same realistic prompt with a different flash model surface after commit `36fc55e`. The run exposed a different generic failure: bounded clean-eval stopped at preflight before formal checker call 1/2 (`calls=0`, `preflights=3`) with an underbuilt short-line grid, body length below target, early line-final comma ratio near zero, weak paragraph engine, and missing rough self-damage. The copied finalized repair cleared strict hard errors but remained style-profile `review` with red `punctuation` plus five yellow drift families, so it was not ready for blind rounds. Root fixes from this case: clean-run preflight now detects medium-length short-line grids with too few longer action/speech/thought lines, and the source guidance now treats sub-900 character drafts as incomplete while treating 900-949 character / 45-75 short-row drafts as underbuilt only when the source shape is also weak. Repair should rebuild from the source loop rather than adding isolated symptoms, app surfaces, money facts, or decorative short drops.

Follow-up retest `iteration-20260705-03/eval-04-family-dinner-argument` used a realistic family-dinner prompt and a different model surface after commit `4d0618d`. The trace was clean, but bounded clean-eval stopped at preflight before formal checker call 1/2 because the draft had 946 body Chinese characters, just below the former 950 cutoff. Controller validation still found real issues in the bounded draft (`高频词覆盖不足`, single family-theme density, and style-profile `revise` with red connector/ngram/punctuation families), so this is not a pass. Root fix from this case: standard diary still targets 950-1150 body characters, but clean-run preflight now treats `<900` as the standalone incomplete-length blocker and treats `900-949` as blocking only when paired with weak source shape such as short-row grid, too few longer action/speech/thought lines, weak connectors, weak paragraph engine, low early comma continuation, or missing rough body/social turn.

Follow-up retest `iteration-20260705-04/eval-04-family-dinner-argument` used the same realistic family-dinner prompt with another model surface after commit `8874e5b`. The trace was clean and the draft reached the two-call checker boundary (`calls=2`, `preflights=1`), which confirms the 900-949 length-boundary fix did not keep blocking near-complete drafts. The case still failed both checkpoints: bounded had no strict hard errors but style-profile stayed `revise` with red `connectors`, `line_rhythm`, and `punctuation`; copied finalized repair also remained `revise`. Manual root review found two general failure forms: a pronoun-softened binary reframe such as `我不是叔叔，我只是...`, and a 45-70-line medium-row grid with zero true <=8-character breath drops. Root fixes from this case: binary-reframe detection now covers pronoun-softened variants, clean-eval preflight blocks missing short-breath drops from 45 body lines upward, draft-gate treats missing breathing points as generated-draft risk, and `rebalance_line_rhythm.py` can split existing short landing sentences out of otherwise uniform rows without inventing content.

Follow-up retest `iteration-20260705-05/eval-05-rental-tap-key` used a realistic prompt about a broken rental faucet, buying tape, an old classmate's WeChat, and forgetting the key. The generator used `mimo/mimo-v2.5` with high reasoning. Trace audit was clean, but bounded clean-eval stopped before a formal checker call (`calls=0`, `preflights=2`): the final bounded draft had 917 body Chinese characters, 24 body lines, early comma ratio 0, weak paragraph engine, and missing rough self-damage. Copied finalized repair using rhythm scripts still failed strict hard gate and style-profile (`revise`, red `connectors`, `line_rhythm`, `ngram_texture`, `punctuation`). Diagnosis is `systemic_gap`, not blind-round-ready. Root fixes from this case: compressed-prose preflight now prioritizes running `rebalance_line_rhythm.py` before another prose rewrite, clean-generation guidance now requires actual visible breathing clusters and actual body-row counting before the first file write, rough self-damage guidance distinguishes external low-status consequence from polite "face looks bad / seems stupid" self-commentary, and high-risk generated insight captions now include `现在我意识到...` without banning natural original-corpus `意识到` usage.

Follow-up retest `iteration-20260705-06/eval-05-rental-tap-key` used the same realistic prompt with `opencode/big-pickle` and thinking enabled after commit `b48e0fa`. The bounded trace was clean, but the run stopped at preflight before formal checker call 1/2 (`calls=0`, `preflights=3`). The draft improved substantially in body length and line corridor and no longer showed binary reframe or prose compression, but controller recheck found two remaining source risks: a tail `算了。` acting as a learned ending button and connector spread still below the generated-draft gate. The previous rough-self-damage failure was a checker blind spot: broken card/failed door maneuver/knee sound/neighbor witnessing is a practical low-status consequence and should not force the generator to add another coarse label. Root fixes from this case: practical lockout failures such as broken cards, failed door-opening maneuvers, body sounds in a hallway, and being seen with the failed object now count as rough self-damage only when they lower body/social/practical position; plain knee pain still does not count. Clean-eval preflight now catches learned ending buttons before a formal checker call and tells the generator to replace them with an already-earned unfinished action, wrong object, route, payment, reply, or body interruption.

Follow-up retest `iteration-20260705-07/eval-12-inferred-moving-micro-hope-portable` used a realistic moving-room prompt with randomly selected `gateway/gpt-5.5`, `--variant high`, and thinking enabled after commit `7d4a87c`. The trace was clean and the run reached the actual two-call checker boundary (`calls=2`, `preflights=2`), which is better evidence than a preflight stop. Bounded still failed and is not blind-round-ready: the run-time bounded final had hard errors for prompt-shaped opening and missing breathing point, and style-profile stayed `review` with red `line_rhythm` and `punctuation`. Stage audit showed a general repair-path issue: the first checker submission already had a reasonable 60-line rhythm corridor with many true <=8-character short drops and long action/thought rows, but the normal checker still used an older 1-2-character breathing-point definition and the clean-run wrapper split/merged the draft before checker call 2, reducing the rhythm into a flatter 52-line shape. Root fixes from this case: checker breathing points now use the same true <=8-character short-drop definition as clean-eval preflight, and `clean_run_checker.py` only runs line-splitting before the final checker when the current draft is actually prose-compressed, under-lined, or long-line dominated; an already valid rhythm corridor is preserved.

Model-rotation note: `iteration-20260705-08/eval-12-inferred-moving-micro-hope-portable` attempted `opencode/bigzickle`, but local OpenCode returned `ProviderModelNotFoundError`; record it as model unavailable, not as a generation-quality failure. Follow-up `iteration-20260705-09/eval-12-inferred-moving-micro-hope-portable` used `deepseek/deepseek-v4-pro`, `--variant high`, and thinking enabled after commit `42b6fac`. The trace was clean, but bounded clean-eval stopped at preflight before checker call 1/2 (`calls=0`, `preflights=3`). The draft was a complete article, but preflight reported too few longer action/thought rows and missing rough self-damage. Controller review found another general checker/preflight gap: visible moving-room grime such as dirty fingernails, gray-stained pants under hallway light, and a cashier noticing the narrator's hand is a practical low-status consequence, not a reason to force another coarse label. Root fixes from this case: visible grime noticed by a cashier, shopkeeper, neighbor, or passerby now counts as rough self-damage only when it lowers body/social/practical position; clean-eval preflight now lets near-miss drafts with three longer rows reach the first formal checker call instead of stopping before any actual checker evidence.

Follow-up retest `iteration-20260705-10/eval-12-inferred-moving-micro-hope-portable` used another rotated model surface after commit `5ede194`. The trace was clean but stopped at preflight before formal checker call 1/2 (`calls=0`, `preflights=3`). Controller review separated one true source failure from two checker/preflight false negatives: `不是那种酸，是...` is a real generated-draft binary reframe and must remain blocked; a one-to-one landlord message with `后面跟了个笑脸` is not a formulaic comment chain; ordinary moving-room mess such as wrong slippers, snot nearly coming out, dirty pants, sticky drain hair, and worn-through socks can be a low-status body/social consequence when it changes action or social exposure. Root fixes from this case: comment-chain detection now requires crowd/comment/group context for compressed reaction residues such as `跟了个`; ordinary unclean low-status consequences now count as rough self-damage and paragraph-engine signals when consequential; source guidance names these as optional examples, not required ingredients. This is a model-agnostic fix: future model differences should continue to be generalized as source shape, sentence form, fact handling, rhythm, or checker-boundary problems, never as provider-specific instructions.

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

For development testing, the controller must keep the bounded clean-eval draft and the finalized repair draft as separate artifacts. Inside bounded clean-eval, also inspect stage snapshots when present: first submission measures natural source guidance before checker feedback, checker-call submissions show what the limited repair path did, and bounded final is the frozen output. The finalized draft should start from a copy in a separate `finalized/` directory; continuing to edit the bounded directory after clean-eval stop contaminates the source-guidance measurement. The finalized draft can show that the repair path works, but it cannot be used to claim the first-pass natural guidance succeeded. If only finalized passes, update the source guidance layer next; if finalized is `review`, `fail`, or `invalid`, treat the final article as still problematic and inspect architecture and repair path before adding another checker rule.

Read the two checkpoints as separate questions, not one averaged score: bounded clean-eval answers whether natural guidance plus limited checker-driven repair gets close under the clean-eval boundary; finalized repair answers whether ordinary multi-round repair can converge afterward. Within bounded clean-eval, a preflight stop before call 1/2 means the draft never reached the two real checker calls, while a call 2/2 failure means the limited checker path was actually tested. A bounded failure with a finalized pass means the source guidance still needs improvement. A finalized failure or `review` means the final article is not clean yet, even if some local checker problems were fixed.

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

For clean-eval formal article generation:

1. Load `references/clean-generation-brief.md` first and use its source loop for the first complete draft.
2. Start from a small lived friction, not from a checklist.
3. Select scenes from action, body, screen, money, route, social misfire, memory trigger, or useless residue.
4. Open `anlin-background.md` only after selected scenes already contain facts that need checking.
5. Write a complete titled `draft.md` before the first checker.
6. Run `scripts/clean_run_checker.py draft.md --strict --draft-gate`.
7. If `CLEAN_RUN_PREFLIGHT` appears, revise before the first checker call is consumed; if `CLEAN_RUN_PREFLIGHT_STOP` appears, output the current draft unchanged and let the controller record failure.
8. Do at most one repair/rewrite and at most two clean-eval checker calls.
9. After the second checker call, output the current `draft.md` exactly.

For ordinary user generation, use the same scene-first drafting principles but do not apply the clean-eval two-call stop rule. Continue repairing hard errors and obvious process leakage until the article is usable or the user stops, while avoiding mechanical ratio chasing.

For controller validation, use the full validation layer after generation:

```powershell
$env:ANLIN_CORPUS_DIR='<corpus-dir>'
python scripts/check_anlin_violations.py draft.md --strict --draft-gate --corpus-dir $env:ANLIN_CORPUS_DIR
python scripts/compare_anlin_corpus.py draft.md --corpus-dir $env:ANLIN_CORPUS_DIR
python scripts/check_style_profile.py draft.md --profile references/style-profile.json --draft-gate --strict
python scripts/rebalance_line_rhythm.py draft.md --in-place
python scripts/calibrate_style_profile.py $env:ANLIN_CORPUS_DIR --profile references/style-profile.json
python scripts/summarize_dev_checkpoints.py <case-dir> --bounded-draft <case-dir>/draft.md --finalized-draft <case-dir>/finalized/draft.md --trace-log <case-dir>/opencode-output.txt --corpus-dir $env:ANLIN_CORPUS_DIR --profile references/style-profile.json --output-json <case-dir>/controller-audit/summary.json --output-md <case-dir>/controller-audit/summary.md
python scripts/run_blind_test.py draft.md $env:ANLIN_CORPUS_DIR --rounds 8 --placebo-rounds 2 --min-fragment-chars 550
python scripts/check_clean_eval_trace.py <case-dir>/opencode-output.txt --json
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
- Development evals should rotate model surfaces and record exact model IDs, but runtime instructions should stay model-agnostic. A model-specific failure becomes a general failure pattern only after it is expressed as source shape, fact handling, sentence form, rhythm, tool routing, or repair-loop behavior.

## Verification

Recommended local checks after edits:

```powershell
Get-ChildItem scripts\*.py | ForEach-Object { python -m py_compile $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
python -m unittest discover -s test -p test_anlin_tooling.py
$env:ANLIN_CORPUS_DIR='<corpus-dir>'
python scripts\build_style_profile.py $env:ANLIN_CORPUS_DIR --output references\style-profile.json
python scripts\calibrate_style_profile.py $env:ANLIN_CORPUS_DIR --profile references\style-profile.json
python scripts\summarize_dev_checkpoints.py <case-dir> --bounded-draft <case-dir>\draft.md --finalized-draft <case-dir>\finalized\draft.md --trace-log <case-dir>\opencode-output.txt --corpus-dir $env:ANLIN_CORPUS_DIR --profile references\style-profile.json
```

Fresh pass/fail claims should quote the exact command results. Older results in this README are status boundaries, not current verification.

## Development Notes

`work/` contains local iterative outputs and is intentionally ignored by git unless a specific artifact is promoted into `audits/`, `evals/`, or `references/`. Do not delete process artifacts until information-loss review confirms they are no longer needed.

Full-corpus validation requires local originals. Set `ANLIN_CORPUS_DIR` or pass `--corpus-dir <corpus-dir>`. Without originals, use `references/portable-corpus.md` and report the result as portable or fragment-level review.

The skill is maintained as part of the `github-yjc` skill collection under the MIT license.

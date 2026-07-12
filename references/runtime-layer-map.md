# Runtime Layer Map

This file is for the developer, auditors, and failed-run diagnosis. Do not load it during ordinary article generation unless the user asks how the skill is organized.

The core architecture is layered so generation agents do not turn every review cue into article material.

## Document Ownership

- `README.md` is the GitHub/user-facing entry. It should explain purpose, status, installation, usage, validation entry points, and limitations without front-loading the full iteration history.
- `SKILL.md` is the runtime contract for a generation or repair agent. It should stay portable, model-agnostic, and free of local machine paths.
- Layer 0 and Layer 1 references shape article generation. They may be loaded before or during drafting according to the workflow.
- Layer 2 references are fact gates. They prevent contradiction and unsupported specificity; they are not scene generators.
- Layer 3 references are repair/calibration libraries. In clean-eval, do not load them before the first complete draft unless the protocol explicitly allows it.
- Layer 4 references and scripts are controller/developer validation. They can fail a draft, record evidence, or diagnose repeated failures, but they should not be handed to a fresh generator as hidden style advice.
- `references/development-log.md` preserves chronological evidence and failed-run diagnoses. It is not runtime guidance. Do not delete log content; when reorganizing docs, move or summarize only after the full factual record is preserved in git.
- `references/route-coverage-matrix.md` and `references/architecture-convergence-plan.md` are developer audit documents. They should be read only when checking route ownership, information loss, or repeated-failure strategy; they are not runtime drafting or repair instructions.

## Layer 0: Entry Contract

Files:

- `SKILL.md`
- `references/clean-eval-first-draft-minimum.md`
- `references/anlin-collage-source-model.md`

Purpose:

- Tell the agent the goal, output rules, clean-eval boundary, and the smallest writing surface.
- Keep the first draft fragment-led: a voice-consistent slate -> earned relations -> fact gate -> draft -> bounded checker.
- Prevent visible process chatter and checker-loop contamination.
- Own the clean-eval first-draft source loop and bounded repair handoff so the generator does not need long repair or validation files. After a preflight, the wrapper output is the complete repair interface and the next content action should be one integrated source change followed immediately by the wrapper. `clean-generation-brief.md` is an expanded controller/developer repair reference, not a generator-facing bounded prompt.
- For standard diary, keep the first-draft source model small and operational: `anlin-collage-source-model.md` tells the generator to choose fragments and relations, preserve voice coherence, and write the article instead of reading long repair libraries as a checklist.

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

For repeated standard-diary failures, inspect whether Layer 0 produced earned fragment relations or only decorative texture. A relation is load-bearing when it changes the next thought, action, reply, body state, room position, or social position; a causal transfer is only one possible relation. Phone/feed/order/bed material may be one fragment among memories, jokes, facts, and direct jumps; do not prescribe separate outside-contact or consequence clusters. This is not a quota for games, places, recurring people, platforms, or background facts; those remain Layer 2 contradiction gates.

## Layer 2: Post-Scene Fact Gate

Files:

- `references/anlin-background.md`
- `references/background-fact-classes.json`
- `references/era-state.md` when date or phase matters

Purpose:

- Background facts are contradiction boundaries, not content requirements.
- Prevent contradictions and unsupported specificity.
- Classify existing scene facts as `supported`, `generic`, `third-person`, or `unsupported`.
- Lower or delete facts after the fragment slate exists.

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
- `references/judge-prompt-templates.md`
- `references/development-log.md`
- `references/route-coverage-matrix.md`
- `references/architecture-convergence-plan.md`
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

1. Name the earliest failed source decision, such as prompt-first opening, missing lateral consequence, unsupported specificity, or visible AI reframe.
2. Add or revise one compact generation lens in Layer 0 when the failure affects formal first drafts.
3. Use Layer 1 or Layer 3 only when the fix needs a richer repair model.
4. Leave Layer 4 to measure the effect; do not make a new detector the only change.

During development evaluation, Layer 4 should record two checkpoints rather than one blended result:

- bounded clean-eval checkpoint: the draft after the fresh generator's bounded clean-eval limit, measuring natural source guidance and limited checker repair. When `.anlin-clean-run-snapshots/` exists, read `first_submission` as the natural-guidance evidence, preflight state as readiness evidence, post-check preflight state as the "first checker ran but call 2/2 was protected" evidence, and checker-call snapshots as limited-repair evidence. A preflight stop before call 1/2 is not the same failure as a post-check preflight after call 1/2, and neither is the same as a draft that reaches call 2/2 and still fails.
- finalized repair checkpoint: a copied draft in a separate `finalized/` directory, measuring whether the public repair interface can converge without mutating the bounded result. The controller may prepare `finalized/repair-brief.txt` before the attempt from the strict hard gate and compact style-profile repair brief. For valid hard-gate failure, `repair_mode: source_rewrite_compact` is a self-contained single-focus interface: the agent reads only `draft.md` and `repair-brief.txt`, follows the exact fragment scope named by the controller (usually one local relation, or an explicit source-level rebuild for a severely underbuilt draft), and does not reconstruct hidden blocker/profile lists. For hard-pass profile review, `repair_mode: hard_pass_review_in_place` has the same brief-only boundary. The generator-facing finalized attempt is artifact-only: read the allowed inputs, make one complete source rewrite persisted to `finalized/draft.md`, then stop. The repair brief should stay source-action and shape oriented; full profile metrics remain controller evidence after the artifact is frozen. Terminal/log-only final prose is an artifact failure. A dense prose block or an equal short-row caption grid is still line-rhythm drift, not a pass. A second `Write draft.md` or `Edit draft.md`, any repair-agent checker command, a post-write repair-agent gate loop, post-write python -c/Measure-Object/wc counters, `Test-Path`/glob/list path probing, or visible threshold arithmetic in the same finalized attempt is invalid controller evidence. The selected genre must be frozen from the case/prompt/bounded draft before repair and passed to controller hard-gate and style-profile validation when available; normal checker success alone is not a finalized pass. The repair agent must not run `check_anlin_violations.py`, `check_style_profile.py`, `clean_run_checker.py`, `prepare_finalized_repair_brief.py`, read or grep checker source, tests, hidden threshold constants, parent skill directories, old logs, or run local counters after writing; it must not glob or list those paths either. A finalized pass after repair-agent checker/source/threshold inspection or write-after-counting inspection is contaminated repair evidence and should not be counted as clean convergence.

If only the finalized checkpoint passes, update Layer 0 or Layer 1 before celebrating the repair. If finalized is only `review`, it is still unresolved and must not be counted as "final no problem." If neither checkpoint cleanly passes, broaden the diagnosis across layers instead of only tightening the checker.

For rhythm failures, prefer a local source/shape diagnosis over single-metric ping-pong. `rebalance_line_rhythm.py` belongs to Layer 4 tooling, but the source lesson belongs earlier: a good draft should not need to bounce between prose-block compression and short-line grid repair.

Standard-diary punctuation drift now has an explicit source failure name: punctuation pendulum. If a repair swings from comma-drag to period-row grid, or from period-row grid to one huge comma chain, Layer 0 did not let marks follow the fragment movement. The first-draft fix belongs in `clean-eval-first-draft-minimum.md` and `anlin-collage-source-model.md`; bounded repair follows the wrapper's self-contained source/shape guidance without loading a long reference. `clean-generation-brief.md` preserves the expanded controller/developer rationale. Thought, speech, memory, body, object, and action decide the marks. Layer 4 may warn with `标准日寄句号网格`, `逗号密度过高`, red `punctuation`, or `period_row_grid`, but the detector is not the fix.

Short non-standard genres have their own source contract. If a sincere or micro-hope draft is clean but reads like polished minimalism, do not force the standard profile or add background/game/body packets as filler. Update Layer 0 or Layer 1 so the generator produces uneven short movement, clumsy action or memory, rough logistics, awkward reply, and factual retreat from the start. Use the selected profile or matched-original condition for any length comparison; do not turn a small stratum's observed range into a universal target. The same applies when the draft reads like a compact literary story: one title object, one family/memory proof, one withheld message, and one final residue all explaining each other is a source-shape risk. Layer 0 should break that source shape before first `draft.md`; Layer 1 can repair it by cutting symbolic echoes and using an existing practical interruption. A recurring subtype is memory-first sincere proof: the article begins with family or archive material, then adds present actions only as support. Layer 0 should prefer a present fragment before memory without requiring a fixed number of lines. A related title failure is the main-prop title loop: the title and tail keep using the same prompt prop to prove the feeling. Layer 0 should teach side-action titles; Layer 1 should repair by retitling from an earned present failure and ending through another practical action. Other failure modes include over-shrinking, sentence-row normalization, repair stuffing, and genre expansion drift. Layer 1 should repair inside the existing fragment slate before adding a new material family or relationship fact. Layer 4 may warn with the existing short-genre rule names, but the detector is not the fix. When the style profile falls back from a small non-standard stratum to global priors, Layer 4 should mark the profile as inconclusive/review and require matched-original placebo reading; it should not become a pass or a reason to rewrite the piece into standard diary shape.

When the old memory-first spine must be abandoned, the source reset must choose a new side-action title rather than adding a late detail around the old spine.

Illness/body prompts have a separate standard-diary failure mode. If the article stays inside symptom, search page, refrigerator food, room smell, and ambient sound, Layer 0 failed even when the details are concrete. The first source decision should be an exposed consequence outside the diagnosis: someone sees the limp or dirty hand, a shop/doorway/payment/key/route problem changes action, food or medicine leaks onto the body in a visible place, or a reply creates a visible next-day constraint. This is a function, not a noun quota: do not insert 外卖, shop staff, or neighbors unless they are the natural consequence carrier. Layer 1 repair should remove one repeated illness/food/screen/ambient packet before adding new material; phone-only contact is weak unless it changes route, payment, doorway, reply, or social position. If `粗粝自毁信号不足` or `段落发动机信号偏弱` appears, do not patch with `妈的`, `操`, `我服了`, or a neat self-insult unless the event already earns it. Replace the private loop with a low-status action such as payment failing while someone waits, a bag handle breaking, food spilling onto the hand or shoe, a key/door/body problem in public, or a reply that lowers the narrator's position. Layer 4 may warn with `疾病病例报告闭环` when no external consequence exists, or `疾病身体证明过密` when the external consequence exists but symptom/search/body packets still dominate. Both rules only protect evaluation. The actual fix belongs in the source slate and repair path.

Private holiday, romance-feed, takeout, and wrong-food prompts have a standard-diary prompt-prop loop failure. If the title is `备注`, `香菜`, `礼物`, `玫瑰`, `优惠券`, `朋友圈`, or another prompt prop, and opening plus tail keep returning to the same note/condiment/feed/gift packet, Layer 0 chose the assignment's object as the article's proof. The fix is not a retitle-only patch. Layer 0 should select an earned fragment relation before drafting: a door, payment, dirty hand, wrong reply, sink, neighbor, object leak, memory, joke, or another person's line may become that relation when the draft needs it. Layer 1 repair should cut one prompt-prop echo and replace its relation inside the existing slate. Layer 4 may warn with `标准日寄提示物标题闭环` / `standard_prompt_prop_title_loop`, but the detector is only a guard; the source fix is prompt displacement plus an earned side-action title.

Social-decline prompts have their own source failure mode. If the article starts from the invitation, title names the person plus event, proceeds through ticket/gift arithmetic, then uses a full warm old-friend memory and room texture to prove sadness, Layer 0 has chosen a sealed moral story instead of a lived diary. The first source decision should be a side action that can stand without the prompt, and the invitation should interrupt it as one cropped message surface. Layer 0 should require the title to come from the side action, wrong reply, route/payment hesitation, dirty object, or body residue, not `狗哥的婚礼` or another topic label. Layer 1 repair should keep only one old debt or memory shard and should make the refusal itself create the next action. Layer 4 may warn with `题面诊断型标题`, `题面高信号开头`, `无依据工作后果链`, `无依据具体地标`, or `社交拒绝室内冷感过密`, but the detector is not the fix; the fix is source order, title source, prompt-surface budget, and consequence-driven refusal.

After the latest social-decline failures, Layer 0 should treat the refusal as one possible fragment relation, not a universal engine. A dirty sleeve, cold room, bowl, charger, screen handle, reply, memory, or ordinary fact may connect to it when the draft earns that turn. If the refusal never changes a later thought or action, the relation is weak; do not repair that weakness by adding a mandatory consequence scene.

The sharper Layer 0 review is refusal relation versus refusal mention. A draft may contain ticket prices, gift money, a lie, and the other person's `OK`, yet still feel prompt-shaped if every later line is only room texture. When the draft itself wants a consequence, let a reply, old debt, route/payment hesitation, body interruption, memory, or ordinary fact carry that turn; otherwise keep the invitation as one fragment and let the article wander elsewhere.

The next failure boundary is refusal overgrowth. If a local refusal relation expands into several days of photos, commute scenes, coworkers, wedding logistics, or office biography, the article has sealed into a plot. Layer 1 should cut explicit chronology before rhythm repair; Layer 4 may warn with `社交拒绝后果过度生长`, but the real fix is returning to the existing fragment slate, not adding another lock.

The newest refusal boundary is consequence theater. When repair tries to escape a private room loop, it may invent `群里有人问`, `有人@我`, `你怎么说项目忙`, `正在输入`, narrator red-packet apologies, `人不到钱到`, `人不到没事`, or `下次一起吃饭`. Those are not stronger consequences; they are public summaries or etiquette closure. Layer 0 should keep refusal aftermath local and unfinished: one person or one practical action changes reply, payment, route, body, door, object, or social position. Layer 1 should cut group-chat crowd scenes and polite settlement before rhythm repair. Layer 4 may warn with `社交拒绝群聊假后果` or `社交拒绝礼貌闭合`, but the source fix is a smaller load-bearing action.

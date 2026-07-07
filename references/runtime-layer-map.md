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

## Layer 0: Entry Contract

Files:

- `SKILL.md`
- `references/clean-generation-brief.md`
- `references/standard-diary-source-engine.md`

Purpose:

- Tell the agent the goal, output rules, clean-eval boundary, and the smallest writing surface.
- Keep the first draft scene-led: friction -> 2-3 load-bearing action clusters -> fact gate -> draft -> bounded checker.
- Prevent visible process chatter and checker-loop contamination.
- Own the clean-eval first-draft source loop so the generator does not need long repair or validation files before writing.
- For standard diary, keep the first-draft middle engine short and operational: `standard-diary-source-engine.md` tells the generator to choose consequence kernels and write the article, instead of reading long repair libraries as a checklist.

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

For repeated standard-diary failures, inspect whether Layer 0 produced load-bearing action clusters or only decorative texture. A cluster is load-bearing only if deleting it breaks the next action, reply, payment, route, body state, room position, or social position. Phone/feed/order/bed chains usually need one cluster outside the prompt's obvious screen/order/object and one exposed practical or social consequence before the first draft. Do not turn this into a new quota for games, places, recurring people, platforms, or background facts; those remain Layer 2 contradiction gates.

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
- `references/development-log.md`
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
- finalized repair checkpoint: a copied draft in a separate `finalized/` directory after ordinary multi-round repair, measuring whether the checker and repair references can converge without mutating the bounded result. The repaired article must be persisted to `finalized/draft.md`; terminal/log-only final prose is an artifact failure. The selected genre must be frozen from the case/prompt/bounded draft before repair and passed to both hard-gate and style-profile validation when available; normal checker success alone is not a finalized pass. The repairing agent should use style-profile `--repair-brief` as the generator-facing interface, while the controller may rerun the full style-profile report after the artifact is frozen. The repairing agent may use gate outputs, but must not read or grep checker source, tests, or hidden threshold constants. A finalized pass after source/threshold inspection is contaminated repair evidence and should not be counted as clean convergence.

If only the finalized checkpoint passes, update Layer 0 or Layer 1 before celebrating the repair. If finalized is only `review`, it is still unresolved and must not be counted as "final no problem." If neither checkpoint cleanly passes, broaden the diagnosis across layers instead of only tightening the checker.

For rhythm failures, prefer a corridor reset over single-metric ping-pong. `rebalance_line_rhythm.py` belongs to Layer 4 tooling, but the source lesson belongs earlier: a good draft should not need to bounce between prose-block compression and short-line grid repair.

Standard-diary punctuation drift now has an explicit source failure name: punctuation pendulum. If a repair swings from comma-drag to period-row grid, or from period-row grid to one huge comma chain, Layer 0 did not build breathing clusters. The fix belongs in `clean-generation-brief.md` and `standard-diary-source-engine.md`: unfinished action, reply, payment, door/body movement, and short failure drops decide the marks. Layer 4 may warn with `标准日寄句号网格`, `逗号密度过高`, red `punctuation`, or `period_row_grid`, but the detector is not the fix.

Short non-standard genres have their own corridor. If a sincere or micro-hope draft is clean but reads like polished minimalism, do not force the standard-diary profile or add background/game/body packets as filler. Update Layer 0 or Layer 1 so the generator produces uneven short clusters, longer clumsy action or memory lines, rough logistics, awkward reply, and short factual retreats from the start. For formal complete-article clean-eval, Layer 0 should make the short corridor concrete: usually around 650-850 body Chinese characters, about 28-55 body lines, 4-7 uneven clusters, and several longer clumsy action/memory/reply lines. A 520-649-character draft or 55+ mostly tiny rows is a narrow matched-short-original risk zone, not a safe default. The same applies when the draft reads like a compact literary story: one title object, one family/memory proof-chain, one withheld message, and one final residue all explain each other. Layer 0 should break that source shape before first `draft.md`; Layer 1 can repair it by cutting symbolic echoes and adding present practical interruption. A sharper recurring subtype is memory-first sincere proof: the article begins with eggs, holiday feed, childhood rain, or no-message material, then adds present actions only as supporting evidence. Layer 0 should require a current-action anchor before memory and should also prevent token-anchor openings where a sink/phone/room line is followed immediately by the full prompt-prop chain. Layer 1 should repair by restarting from a sink/bowl/door/neighbor/call/reply/body/clothing/room/object problem that changes the next action and letting the first 8-12 body lines belong to that present failure before one memory prop leaks in. If a repair keeps the old title/object/memory order and adds a late practical line, it is still the same source failure; the source reset must choose a new side-action title and allow only one old memory prop to survive as a cropped leak. A related title failure is the main-prop title loop: the title is `鸡蛋`, `一袋鸡蛋`, `塑料袋`, `屏幕`, or another prompt prop, and the body/tail keep using that same prop to prove mother-memory, withheld message, and final residue. Layer 0 should teach side-action titles before drafting; Layer 1 should repair by retitling from the new present failure and ending through another practical action. A second failure mode is over-shrinking: the model deletes material until the piece is a 250-500-character sketch with no longer clumsy line, or makes a 55+ line poem-shaped grid with no longer lines. A third failure mode is sentence-row normalization: the draft reaches a plausible line count but most lines are sealed `。` sentences, and time-order glue such as `后来`, `已经`, and `当时` carries the memory switches. Layer 0 should teach breathing clusters before drafting; Layer 1 should repair by changing action/reply movement, not by changing punctuation only. A fourth failure mode is repair stuffing: the model tries to fix short-genre profile drift by importing unrelated delivery, food, gift, media, game, route, or background packets. A fifth failure mode is genre expansion drift: the repair grows a sincere/micro-hope piece into standard-diary bulk with relation exposition, transfer/account scenes, extra function people, or unsupported major family status such as a parent being dead or gone. Layer 0 should block over-shrinking, short-line grid, period-grid rows, and genre expansion by requiring one present practical cluster, several longer clumsy lines, real line-final continuation commas where the same action continues, and by allowing the generator to discard or bury prompt-supplied family props instead of preserving every one. Layer 1 should block stuffing and expansion drift by repairing within the existing object-message-room-body-memory set before adding any new material family or relationship fact. Layer 4 may warn with `短真诚小小说闭合`, `短真诚当前动作锚点不足`, `短真诚题面物件过早`, `短真诚标题物件闭环`, `短体裁完整度不足`, `短体裁句号网格`, `短体裁修复堆新素材`, `短体裁误扩成标准日寄`, or `无依据重大家庭变故`, but the detector is not the fix. When the style profile falls back from a small non-standard stratum to global priors, Layer 4 should mark the profile as inconclusive/review and require matched-original placebo reading; it should not become a pass or a reason to rewrite the piece into standard diary shape.

Illness/body prompts have a separate standard-diary failure mode. If the article stays inside symptom, search page, refrigerator food, room smell, and ambient sound, Layer 0 failed even when the details are concrete. The first source decision should be an exposed consequence outside the diagnosis: someone sees the limp or dirty hand, a shop/doorway/payment/key/route problem changes action, food or medicine leaks onto the body in a visible place, or a reply creates a visible next-day constraint. This is a function, not a noun quota: do not insert 外卖, shop staff, or neighbors unless they are the natural consequence carrier. Layer 1 repair should remove one repeated illness/food/screen/ambient packet before adding new material; phone-only contact is weak unless it changes route, payment, doorway, reply, or social position. If `粗粝自毁信号不足` or `段落发动机信号偏弱` appears, do not patch with `妈的`, `操`, `我服了`, or a neat self-insult unless the event already earns it. Replace the private loop with a low-status action such as payment failing while someone waits, a bag handle breaking, food spilling onto the hand or shoe, a key/door/body problem in public, or a reply that lowers the narrator's position. Layer 4 may warn with `疾病病例报告闭环` when no external consequence exists, or `疾病身体证明过密` when the external consequence exists but symptom/search/body packets still dominate. Both rules only protect evaluation. The actual fix belongs in the source slate and repair path.

Private holiday, romance-feed, takeout, and wrong-food prompts have a standard-diary prompt-prop loop failure. If the title is `备注`, `香菜`, `礼物`, `玫瑰`, `优惠券`, `朋友圈`, or another prompt prop, and opening plus tail keep returning to the same note/condiment/feed/gift packet, Layer 0 chose the assignment's object as the article's proof. The fix is not a retitle-only patch. Layer 0 should select a side engine before drafting: door/hallway exposure, payment, dirty hand, wrong reply, sink, rider/shopkeeper, neighbor, object leak, or another person's reaction. Layer 1 repair should cut one prompt-prop echo and rebuild the middle through that consequence. Layer 4 may warn with `标准日寄提示物标题闭环` / `standard_prompt_prop_title_loop`, but the detector is only a guard; the source fix is prompt displacement plus side-consequence title selection.

Social-decline prompts have their own source failure mode. If the article starts from the invitation, title names the person plus event, proceeds through ticket/gift arithmetic, then uses a full warm old-friend memory and room texture to prove sadness, Layer 0 has chosen a sealed moral story instead of a lived diary. The first source decision should be a side action that can stand without the prompt, and the invitation should interrupt it as one cropped message surface. Layer 0 should require the title to come from the side action, wrong reply, route/payment hesitation, dirty object, or body residue, not `狗哥的婚礼` or another topic label. Layer 1 repair should keep only one old debt or memory shard and should make the refusal itself create the next action. Layer 4 may warn with `题面诊断型标题`, `题面高信号开头`, `无依据工作后果链`, `无依据具体地标`, or `社交拒绝室内冷感过密`, but the detector is not the fix; the fix is source order, title source, prompt-surface budget, and consequence-driven refusal.

After the latest social-decline failures, Layer 0 should treat the refusal aftermath as one load-bearing kernel. A dirty sleeve, cold room, bowl, charger, or screen handle can open the door, but it cannot be the only engine. The reply, payment/route decision, old debt, other person's plain response, or a practical embarrassment must change a later action; otherwise the draft has replaced social pressure with room texture.

The sharper Layer 0 test is refusal chain versus refusal mention. A generated draft may contain ticket prices, gift money, a lie, and the other person's `OK`, yet still fail if the next action is mainly driven by water, paper, sleeve, bowl, charger, or another room object. The post-refusal response, wrong reply, old debt, payment/route hesitation, or body/social interruption must carry a later action after the refusal is sent. If deleting every room/object texture except one leaves only a chat summary, rebuild from the reply aftermath before drafting or repairing.

The next failure boundary is refusal chain overgrowth. If Layer 0 says the refusal must produce consequence but does not set an upper bound, generators may turn one refusal into several days of photos, commute scenes, coworkers, wedding logistics,伴郎/喜酒 turns, and office biography. That is a sealed plot, not an Anlin-style diary leak. Layer 0 should state that one refusal consequence moves one or two later actions and exits on a loose practical residue; Layer 1 repair should cut chronology before rhythm repair; Layer 4 may warn with `社交拒绝后果过度生长`, but the real fix is the source limit.

# anlin-writing

This OpenCode skill generates, reviews, and evaluates Anlin/日寄-style Chinese prose for anonymous blind evaluation. The target is narrow: reduce stable identification as generated text under documented test conditions, while reporting only conditions, sample size, recognition/pass rates, false accusations, invalid rounds, and limits.

It must not claim real authorship, provenance, or objective indistinguishability.

## Corpus Boundary

The distributable skill does not require every user to own the 38 original articles. Runtime generation and portable review use bundled summaries: `references/portable-corpus.md`, `references/samples-index.md`, `references/corpus-cards/`, `references/background-fact-classes.json`, and `references/style-profile.json`.

The full 38-article corpus is a developer/controller input, not a runtime dependency. Use it only when available to rebuild cards/profile, run copy-overlap checks, calibrate thresholds, or run complete-article blind rounds. Set `ANLIN_CORPUS_DIR` or pass `--corpus-dir <corpus-dir>` for those stronger validation tasks.

## Current Status

Status: not yet proven. This skill is still under active development. It is not ready to claim the `<=10%` stable impostor-identification target because no current evidence package contains all required pieces: 15 clean-eval generation cases, a calibrated `8 impostor + 2 placebo` blind-round package, low stable-identification rate, low placebo false-accusation rate, and uncontaminated controller logs.

Current active-protocol recognition rate is `N/A`: no draft has yet reached a valid `8 impostor + 2 placebo` blind package under the active readiness rules. Checker pass rates, style-profile status, and legacy smaller diagnostic rounds are not substitutes for that rate.

The active standard-diary source contract is now fragment-slate based. A standard article normally moves through several independent thought-turns connected by earned association, contrast, memory, echo, time jump, self-correction, or direct voice jump; one continuous scene is a deliberate exception, not the default. This qualitative guidance has no fragment-count quota. The latest bounded controller evidence remains process-valid but quality-invalid: it stopped during preflight with a complete 1078-character artifact whose paragraph movement and refusal aftermath still failed the ordinary quality gate. No finalized, blind, placebo, or recognition-rate evidence was added by that run.

The latest documented boundary is preserved in `references/development-log.md`. In short: compact profile briefs fixed one terminal-only / unchanged-artifact failure, but the newest targeted retests still did not become blind-round-ready. Rechecking the latest social-decline draft under the current gates narrows the remaining hard failures: bounded generation can now reach the two-call checker boundary, but repaired drafts may still shrink below the standard-diary corridor and fail connector/rhythm/punctuation checks; finalized repair can still drift into source-level rhythm/punctuation loops. The current finalized interface is artifact-only: the controller prepares `finalized/repair-brief.txt` before the repair attempt, the repair agent reads that brief plus `draft.md`, writes one complete `finalized/draft.md`, and stops; post-write validation belongs to the controller. A second write/edit to `finalized/draft.md`, any repair-agent checker command, a post-write repair-agent gate loop, post-write `python -c`, `Measure-Object`, `wc`, local line/character counters, visible threshold arithmetic, or skill-directory rediscovery in the same finalized attempt is invalid controller evidence. Recent single-write retests improved writeback discipline and removed some fact leaks, but the drafts still failed quality with rough self-damage shortage, underlength repair, period-row grid, prose-block compression, equal short-sentence row grids, message-order glue, group-chat crowd summaries, polite red-packet closure, or the opposite comma-carpet repair drift. The current interface now makes hard-gate findings outrank the compact style brief, treats the single finalized write as atomic, rejects prose-block compression, 80+ one-sentence rows, nearly all-comma line surfaces, and 650-899-character standard repair shrinkage as false escapes from rhythm failure, clarifies that private room-only wet texture is not rough exposure, keeps `忙项目`-style refusal excuses from becoming leave/调休/排班 biographies, treats ordinal message labels such as `第二条只...` / `下面还有...` as plot glue, rejects refusal repair that grows into `群里有人问` / `有人@我` crowd exposure or `人不到钱到` / `下次一起吃饭` etiquette settlement, requires neighbor/cashier/rider contact to touch the wet/dirty/payment/reply/body fact before it counts as a public hinge, and treats door opening / corridor light / neighbor-light imagery as threshold atmosphere unless it changes contact, payment, reply, route, or body action. Do not expand to blind rounds until a fresh bounded/finalized case is pass-ready under the active protocol.

The severe-underbuilt bounded retest in iteration-160 was deliberately excluded from quality evidence: the generator was allowed to combine a whole-source rebuild with a rhythm-script action and then rewrote after the script, so the trace was invalid. The generator-facing contract now keeps severe source repair source-only and defers rhythm tooling to a later wrapper call. Fresh iterations 161 and 162 confirmed that protocol fix (clean traces except provider-visible planning), but the source still failed: 161 ended as a 722-character prose block, while 162 over-corrected into a 521-character short-line grid. The current source action therefore keeps collage/thought-turn completeness and mass preservation, but leaves breathing/line shape to a later independent action; these are source-guidance checkpoints, not quality or blind-readiness claims.

Latest source-guidance fix: social-decline drafts now treat a plain OK/`好的` reply plus a private screen mark, water trace, sleeve, or room object as a screen loop unless that reply changes a visible next action. They also treat group-chat public exposure, polite red-packet settlement, and unrelated delivery/food-burn/room-chore errands as false repairs unless one local action is refusal-coupled: the reply, payment, route, body, door, object, old debt, or social position changes because of not going. Finalized repair now treats page shape as the first repair action, but does not expose every drift family as a checklist. The repair brief prioritizes one primary source rewrite, makes AI-slop removal outrank ratio chasing, caps generator-facing source actions to a small diagnostic subset, and adds an overfill guard for 140+ rows / 2000+ character standard repairs. When the hard gate already reports overfull standard-diary shape, excessive rows, or over-fragmentation, the controller now emits a stronger `hard_gate_primary_action` that tells the repair agent to delete repeated proof packets and merge adjacent caption rows before any profile-family repair. That same action now also blocks the common rebound into one-period-per-line grids and polished simile captions. The controller also resolves relative `--profile` / `--corpus-dir` paths before running gates from an external finalized artifact directory, so `repair-brief.txt` should not silently degrade into `controller_tool_error` when the draft lives outside the skill repo. The minimal first-draft path, runtime repair, finalized repair, clean-eval wrapper, style repair brief, and strict checker use the same boundary. Controller trace audit now reads UTF-16 OpenCode JSONL logs and counts a single delete+add patch of `finalized/draft.md` as one artifact write. A `老太太`/old-lady surface is no longer misread as an unsupported spouse identity.

Latest finalized-repair routing fix: after a social-decline draft writes back successfully but still fails because the wedding/refusal line sits beside room, screen, water, or route texture, the compact repair brief now routes the primary action to `rebuild_refusal_aftermath_engine` before period-grid repair. Targeted retests confirmed that this can clear the earlier social-refusal and period-grid blockers, but they also exposed two false escapes: one repair shrank into a 568-character short summary, and the next wrote the old draft first, reasoned again, then wrote a second revised artifact that was still underbuilt at 875 body Chinese characters. The brief now says the deleted private texture packet must be replaced with a refusal-coupled consequence cluster, should stay in a roughly 950-1150 body-character standard-diary corridor, must not save 650-899 shrinkage or weak 900-949 boundary drafts, and must create rough self-damage or paragraph-engine movement rather than more private wet/body texture. The repair interface also states that the first write to `draft.md` must be the final complete revision: copying the current draft back unchanged and then rewriting is invalid controller evidence. This is not blind-round evidence; it narrows the next retest question to whether the short brief can preserve article mass and one-write discipline while making the refusal aftermath change the next visible action.

Latest clean-eval routing/source fix: targeted source-generation retests showed separate boundaries. A generator could misread a formal workspace as ordinary article generation even when `.anlin-clean-eval-mode` existed; the runtime router now makes the marker outrank ordinary article wording, and `runtime-brief.md` / `anti-ai-slop.md` send misrouted formal workspaces back to `clean-eval-first-draft-minimum.md` before the first `draft.md`. The social-decline source guidance also moved refusal aftermath away from pure phone/screen loops: a recent valid artifact did create a post-refusal non-screen action through delivery-door contact, unpaid transfer, balance, and old-debt residue, but still stopped at preflight because the first saved article was five dense prose body lines cut by rhythm tooling. Current source guidance therefore rejects 5-7 long-paragraph first drafts and says the file-write `content` itself must already show broken body rows before the first wrapper call. A later targeted run then exposed an even earlier route failure: after loading the skill, the generator printed a short article only to the terminal and never wrote `draft.md`. The runtime entry now states that every generation path is artifact-backed: "prose only" is the final response shape after a real `draft.md`, not permission to bypass the artifact. The next targeted run confirmed artifact entry improved because `draft.md` and clean-run state were written, but bounded still stopped at preflight before formal checker calls. The wrapper had mixed content/source blockers with shape drift and told the agent to run `rebalance_line_rhythm.py` before rewriting content; clean-eval repair now says source/content repair comes first in that mixed case, and `rebalance_line_rhythm.py` is the final shape step after the last content write. A later call-2 boundary showed another source/tool-flow gap: after checker call 1/2, a repaired standard diary could shrink below 900 characters and lose connector/long-line corridor, then spend checker call 2/2 on known failures. The wrapper now allows one `CLEAN_RUN_POSTCHECK_PREFLIGHT` before call 2/2 so the generator must repair by source replacement before the final checker. This is source/tool-flow repair, not blind-round evidence.

Latest targeted retest 137 used a rotated model on the same classmate-wedding social-decline case after the post-check guard. Bounded clean-eval improved: the draft reached the two-call checker boundary, hard gate had zero errors, and `CLEAN_RUN_POSTCHECK_PREFLIGHT` protected checker call 2/2 once before the model repaired connector/source mass. It still was not blind-round-ready because style-profile stayed `review` with red `punctuation` and `ngram_texture`. A copied finalized repair then wrote back exactly one artifact with clean trace, but degraded the article from bounded `review` to finalized `fail`: it introduced `高频词覆盖不足`, `标准日寄句号网格`, and style-profile `revise`. A follow-up finalized retest after the first preservation guard still failed: one model was unavailable due to provider balance, and another added a binary `不是X，是Y` group-chat/comment-chain premise, overfilled the article, and made every row a period row. Current fix: the finalized repair brief and runtime minimum now use a stricter `preserve_and_nudge_review` path. When hard gate already passed and only style-profile review remains, repair must preserve title source, people, invitation channel, message facts, refusal aftermath, connector turns, approximate mass, rough/public consequence, and mixed comma/hard-stop line endings; it must not introduce group chats, comment chains, stranger witnesses, new route/backstory packets, binary reframes, or a new article premise. This remains repair-interface evidence, not active blind-round recognition evidence.

Follow-up after that preservation routing showed partial improvement but not a pass: the finalized artifact no longer invented the group-chat/comment-chain premise and returned to style-profile `review`, but it still failed strict hard gate with a polished simile/caption, thin high-frequency connector coverage, zero early line-final comma continuation, and a one-period-per-row standard-diary grid. Current fix: the hard-gate-pass/profile-review path now uses `micro_cluster_surgery`. It tells repair agents to preserve the existing scene slate and comma continuations, change only a few local action/reply/payment/body clusters, avoid new similes or caption metaphors, and avoid closing every row with `。`. This is a targeted finalized-repair interface fix, not recognition-rate evidence.

Follow-up after the first micro-cluster pass confirmed the artifact path stayed clean and the new repair avoided the previous new-premise failures, but the repaired article still failed: it normalized the incoming draft's comma-ended continuation rows into sealed `。` rows, triggering `行末逗号比例` and leaving style-profile `review`. Current fix: hard-pass/profile-review repair now explicitly preserves working comma-ended continuation rows from the incoming draft when the following row completes the same action or thought. This remains repair-interface evidence, not active blind-round recognition evidence.

Follow-up after comma-continuation preservation showed that the targeted instruction moved the right variable: early line-final comma ratio rose from 0.00 to 0.30 and the artifact remained a one-write clean trace. The draft still failed finalized validation because 80% of body lines still ended as sealed period rows. Current fix: hard-pass/profile-review repair now adds `line_ending_lock`, telling the repair agent to keep row-ending punctuation and line breaks for untouched rows instead of preserving a few commas while normalizing the rest of the page. This is still repair-interface work, not blind-round evidence.

Follow-up after `line_ending_lock` showed another local improvement but still not a pass: the repair preserved more incoming line endings and no longer failed the period-grid hard gate, but it trimmed the hard-gate-passing draft to 890 body Chinese characters and failed the standard-diary buffer gate. Current fix: the same hard-pass/profile-review path now adds `mass_floor_lock`, which forbids removing a functional consequence sentence unless it is replaced inside the same local cluster and forbids saving a hard-gate-passing standard repair below 900 body Chinese characters. This remains targeted repair-interface work, not blind-round evidence.

Follow-up after `mass_floor_lock` confirmed that the shrink guard moved the intended variable: a fresh one-write finalized repair stayed at 927 body Chinese characters and passed the strict hard gate with no checker/source/test reads or post-write counter loop. It still did not pass the finalized checkpoint because style-profile remained `review` with red `punctuation` and `ngram_texture`. The repair changed only a few repeated words while leaving period and enumeration counts unchanged. Root review found a directional interface bug: the red n-gram finding meant natural repeated 4-gram reuse was too low, but the compact brief still told every `ngram_texture` repair to delete repetition, encouraging synonym cleanup and even lower reuse. Current fix makes n-gram guidance directional: preserve ordinary action/object recurrence when reuse is low or uniqueness is high; remove a whole mechanical packet only when repetition is actually high. This is repair-interface evidence, not recognition-rate evidence, and the remaining profile review still needs another targeted retest plus placebo-calibrated interpretation.

The paired direction-aware retest changed the failure but did not close it. The repair stopped synonym-cleaning the repeated hand/smell wording and style-profile reached `checkpoint_pass=true`, but it merged/deleted the loose tail, misestimated the remaining mass, and saved only 894 body Chinese characters, causing a new strict hard-gate length failure. This shows that another isolated lock is unlikely to solve the path: the hard-pass/profile-review interface is now carrying preservation, punctuation, n-gram direction, mass, line shape, social consequence, and single-write constraints at once. The next engineering step is a shorter hard-pass/review controller mode with one-for-one local row replacement and no row deletion/merge; if that still leaves only punctuation/ngram review, stop rewriting and use matched-original/placebo calibration before changing thresholds. The project remains not ready for blind rounds.

The compact hard-pass/review experiment is now closed: it preserved artifact scope and strict hard-gate status, but finalized quality still did not converge and style-profile remained `review` with punctuation/ngram drift. Stop repairing the same artifact. Targeted all-original calibration produced 0/2 raw and 0/2 stable false accusations across two valid six-original rounds and did not reproduce punctuation/ngram as an accusation cue. This result is calibration-only and does not validate the generated draft; it does not count toward the formal `8 impostor + 2 placebo` readiness package or create a reportable recognition rate. The next hypothesis is bounded source formation: globally high period placement, enumeration packets, and too little natural recurring phrase texture. Do not change profile thresholds from this result.

Fresh bounded retest 146 produced a real first draft but did not reach a bounded stop. The controller timed out while the generation process kept running in the background; after the captured JSONL ended, the same session loaded the 94KB expanded clean-generation reference, rewrote `draft.md`, and stopped before rerunning `clean_run_checker.py`. The first submission was 985 body Chinese characters and failed source/rhythm gates; the unverified rewrite shrank to 769 characters, kept private wet-room texture instead of a refusal-coupled consequence, and failed hard gate plus style-profile review. This run is invalid timeout/incomplete-boundary evidence, not a generation case. Current fix: bounded preflight and post-check repair now use the wrapper output as the complete interface, with no additional long reference read; related findings should be handled by one integrated source change, and every rewrite must be followed immediately by the wrapper. Trace audit also now rejects a post-wrapper rewrite that ends without another wrapper result. The project remains not ready for blind rounds.

Fresh bounded retest 147 reached the real two-call clean-run boundary and finished with zero strict hard-gate errors, but style-profile stayed `revise` with red `line_rhythm`, `ngram_texture`, and `punctuation`, so it is not a valid generation case. Manual and trace review found that the repair kept expanding one cashier/counter/payment/detergent/object carrier from calculation through refusal, cancellation, reply, and the tail. The same run also exposed a checker false positive: `输密码取消`, queue movement, and a cancellation receipt already changed the transaction, but the soft-witness rule still treated the cashier look as consequence-free. Current source and repair guidance now treats a carrier as the combined person/place/transaction/object chain, releases it after one consequence transfer, and replaces overloaded packets instead of appending diagnostic proof clusters. The wrapper distinguishes a severely incomplete sub-650 draft from a 650-899 shrink and a 900-949 weak-source boundary: rebuild the severe fragment, restore missing mass inside a one-for-one replacement for the shrink, and preserve mass for the weak boundary. Connector-only and roughness guidance now rewrites existing movement instead of asking for added scenes, and transaction cancellation/void/refund actions count as real witness consequences. The next evidence step is a fresh bounded iteration from the prompt, not another repair of the 147 artifact.

Post-review contract audit found two residual gaps before the next fresh case: same-line or neighboring historical transaction language such as `上周那笔订单退款了` / `上周付款取消了` could still satisfy the soft witness through the generic consequence matcher, and the non-compact finalized fallback still told the repair agent to rebuild the page toward a cluster/line quota. The checker now evaluates consequence/transaction evidence against the current movement after the witness and ignores detached prefixes, while allowing a real current action introduced by `后来`; the fallback preserves existing rows and repairs only the smallest broken movement with one earned relation. Regression coverage and the full engineering gate now pass, but this remains interface/source evidence, not a valid generation case or blind-round result.

Latest boundary after the next fresh bounded/finalized check: the bounded process contract is now valid through an explicit preflight stop, but the source draft still fails quality. A subsequent finalized repair wrote once with a clean trace yet overfilled the article and rebuilt a period grid, showing that a hard-gate-fail repair brief was still overloading the agent with competing blocker instructions. The controller now uses `repair_mode: source_rewrite_compact` for valid hard-gate failures: one source focus, a route-appropriate scope (usually one local cluster, with an explicit source-level rebuild only for severely underbuilt drafts), qualitative mass/shape/fact boundaries, and controller-only detailed diagnostics. `hard_pass_review_in_place` remains the row-preserving mode. This is repair-interface evidence only; active recognition remains `N/A`, and the project is not ready for blind rounds.

## Quick Start

1. Install this directory wherever the target OpenCode-compatible agent discovers local skills.
2. Ask for `anlin-writing` / `anlinwriting` / `日寄` / `Anlin-style` generation, review, or evaluation.
3. For ordinary article generation, give any known date, scene material, genre, and output location. If those are missing, the skill asks only for information that materially changes the result.
4. For development testing, create an external case workspace and run the clean-eval protocol from `references/validation-protocol.md`; do not store generated drafts under the skill directory.
5. For full-corpus validation, provide a corpus directory through `ANLIN_CORPUS_DIR` or `--corpus-dir <corpus-dir>`. Without that corpus, report portable review only.

The generated article must be a complete titled article. The title is part of the blind-review surface and should be judged with the body, not treated as metadata.

## Install Path

Install the skill wherever the target agent expects local skills. In this README, the installed directory is written as:

```text
<skill-dir>
```

Run commands from `<skill-dir>` unless a command explicitly says otherwise.

Trigger phrases include `anlin-writing`, `anlinwriting`, `Anlin`, `日寄`, `Anlin-style`, `像Anlin那样写`, `模拟日寄`, and requests for Anlin corpus evaluation. The OpenCode skill name is `anlin-writing`; `Anlin` remains a content-domain trigger alias because users naturally ask for that name.

## Documentation Map

Use the smallest document set that matches the task:

| Audience / task | Read |
|---|---|
| GitHub user or installer | this `README.md` |
| Ordinary runtime article generation | `SKILL.md`, then `references/runtime-brief.md`; use `references/feature-budget.md` and `references/anti-ai-slop.md` only as needed |
| Formal clean-eval first draft and bounded repair | `SKILL.md`, then `references/clean-eval-first-draft-minimum.md`; add `references/anlin-collage-source-model.md` for standard diary; after wrapper findings use wrapper output only; no additional reference read |
| Ordinary repair after a draft exists | `references/runtime-brief.md`, `references/feature-budget.md`, `references/anti-ai-slop.md`, then targeted fact/voice/title references as needed |
| Fact and background checks | `references/anlin-background.md`, `references/background-fact-classes.json`, `references/era-state.md` |
| Controller validation and blind testing | `references/validation-protocol.md`, `references/stylometric-ratio-protocol.md`, `references/blind-judge-angles.md`, `evals/README.md` |
| Detailed development history and failed-run evidence | `references/development-log.md` |
| Architecture audit and route ownership | `references/runtime-layer-map.md`, `references/route-coverage-matrix.md`, `references/architecture-convergence-plan.md` |

Clean-eval first drafts should not load controller, development-log, route-coverage, or architecture-convergence files before the first complete `draft.md`; those files exist for validation, diagnosis, and maintenance.

For source-load conflict audits, `references/clean-eval-first-draft-minimum.md` owns the first formal draft and the wrapper output owns bounded repair. `references/clean-generation-brief.md` is an expanded controller/developer reference; `runtime-brief.md`, `generation-modes.md`, and `anti-ai-slop.md` remain available for ordinary repair or explicit analysis, but none should be loaded into a bounded clean-eval repair as a checklist.

## Architecture

The important design choice is separation of layers. The generation agent should not read every file before writing; that turns review categories into visible article ingredients.

```text
anlin-writing/
├── SKILL.md                         # routing, clean-eval boundary, output rules
├── references/
│   ├── clean-eval-first-draft-minimum.md # short first-draft contract
│   ├── clean-generation-brief.md     # expanded controller/developer repair reference
│   ├── anlin-collage-source-model.md   # active standard-diary fragment source model
│   ├── standard-diary-source-engine.md # inactive historical reference
│   ├── runtime-layer-map.md          # architecture map for audits
│   ├── route-coverage-matrix.md      # owner anchors for route/information-loss audits
│   ├── architecture-convergence-plan.md # developer convergence plan, not runtime guidance
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
│   ├── self-check.md                 # post-draft human/isolated-review checklist
│   ├── stylometric-ratio-protocol.md # corpus-prior audit method
│   ├── style-profile.json            # generated profile from 38 originals
│   ├── validation-protocol.md        # clean-eval and blind testing protocol
│   ├── blind-judge-angles.md         # multi-angle judge matrix
│   ├── judge-prompt-templates.md     # isolated controller judge prompts
│   ├── development-log.md            # preserved failed-run evidence and status boundaries
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

For development testing, the controller must keep the bounded clean-eval draft and the finalized repair draft as separate artifacts. Inside bounded clean-eval, also inspect stage snapshots when present: first submission measures natural source guidance before checker feedback, checker-call submissions show what the limited repair path did, and bounded final is the frozen output. The finalized draft should start from a copy in a separate `finalized/` directory; continuing to edit the bounded directory after clean-eval stop contaminates the source-guidance measurement. Each finalized repair attempt should use the short repair brief when available, make one complete source rewrite, persist `finalized/draft.md`, and stop; the controller reruns validation after the artifact is frozen. Post-write `python -c`, `Measure-Object`, `wc`, or local line/character counters belong to controller validation, not the repair agent. The finalized draft can show that the repair path works, but it cannot be used to claim the first-pass natural guidance succeeded. If only finalized passes, update the source guidance layer next; if finalized is `review`, `fail`, or `invalid`, treat the final article as still problematic and inspect architecture and repair path before adding another checker rule.

Read the two checkpoints as separate questions, not one averaged score: bounded clean-eval answers whether natural guidance plus limited checker-driven repair gets close under the clean-eval boundary; finalized repair answers whether the public repair interface can converge from a copied bounded draft without metric chasing. Within bounded clean-eval, a preflight stop before call 1/2 means the draft never reached the two real checker calls. A `CLEAN_RUN_POSTCHECK_PREFLIGHT` stop after call 1/2 means the first checker ran, but the repaired draft was still too underbuilt or had a known hard shape failure before call 2/2; it is source/limited-repair evidence, not a two-call pass. A call 2/2 failure means the limited checker path was actually tested. A bounded failure with a finalized pass means the source guidance still needs improvement. A finalized failure or `review` means the final article is not clean yet, even if some local checker problems were fixed.

Controller summaries should read `blind_round_readiness`, bounded status, finalized status, trace findings, hard-gate findings, and style-profile status together. A bounded failure with a finalized pass means source guidance should be strengthened; finalized `review/fail/invalid` means the final article is still unresolved.

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

1. Check `.anlin-clean-eval-mode` as one direct tool action, such as `Test-Path -LiteralPath ".anlin-clean-eval-mode"` or `Get-ChildItem -Force .anlin-clean-eval-mode`; a directory listing that merely shows the filename is not a marker check. Then as the next tool action run standalone `Get-Location` / `pwd`; both checks must be visible before any reference read, glob/path probe, or draft write. Do not use controller `--dir`, a glob title, or an absolute path as cwd evidence.
2. Load `references/clean-eval-first-draft-minimum.md` only after those two separate actions. For standard diary clean-eval, then load `references/anlin-collage-source-model.md`; the old `standard-diary-source-engine.md` is historical reference only. For short non-standard genres, stay with the clean brief.
3. Start from a fragment slate, not from a checklist or plot outline.
4. Select fragment relations from action, body, screen, money, route, social misfire, memory trigger, joke, object, or useless residue; let the voice jump when one relation has done its work.
5. Open `anlin-background.md` only after selected scenes already contain facts that need checking.
6. Write a complete titled article using exactly relative `draft.md` / `.\draft.md` before the first checker. Do not run line-rhythm scripts before the first wrapper call.
7. Run `scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing` so bounded generation receives qualitative repair guidance while exact telemetry stays in controller evidence.
8. If `CLEAN_RUN_PREFLIGHT` appears, revise before the first checker call is consumed. If `CLEAN_RUN_POSTCHECK_PREFLIGHT` appears after checker call 1/2, follow its one printed source-replacement or explicit shape-repair action before spending checker call 2/2; the wrapper itself does not rewrite the submitted draft. If `CLEAN_RUN_PREFLIGHT_STOP` appears, output the current draft unchanged and let the controller record failure.
9. If a rhythm script runs and `draft.md` is then rewritten or edited, rerun the relevant rhythm script before the next wrapper call or keep the repair inside the existing line-broken corridor.
10. Do at most one repair/rewrite per bounded source action and at most two actual clean-eval checker calls; preflight attempts do not consume that budget, so stop only at an explicit `CLEAN_RUN_PREFLIGHT_STOP` or actual checker result.
11. After the second checker call, output the current `draft.md` exactly.

For ordinary user generation, use the same scene-first drafting principles but do not apply the clean-eval two-call stop rule. Continue repairing hard errors and obvious process leakage until the article is usable or the user stops, while avoiding mechanical ratio chasing.

For controller validation, use the full validation layer after generation:

```powershell
$env:ANLIN_CORPUS_DIR='<corpus-dir>'
python scripts/check_anlin_violations.py draft.md --strict --draft-gate --corpus-dir $env:ANLIN_CORPUS_DIR
python scripts/compare_anlin_corpus.py draft.md --corpus-dir $env:ANLIN_CORPUS_DIR
python scripts/prepare_finalized_repair_brief.py <case-dir>/finalized/draft.md --genre <standard|sincere|micro-hope|surreal>
python scripts/check_style_profile.py draft.md --draft-gate --strict --genre <standard|sincere|micro-hope|surreal>
python scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre <standard|sincere|micro-hope|surreal>
python scripts/rebalance_line_rhythm.py draft.md --in-place
python scripts/calibrate_style_profile.py $env:ANLIN_CORPUS_DIR --profile references/style-profile.json
python scripts/summarize_dev_checkpoints.py <case-dir> --bounded-draft <case-dir>/draft.md --finalized-draft <case-dir>/finalized/draft.md --trace-log <case-dir>/opencode-output.txt --corpus-dir $env:ANLIN_CORPUS_DIR --profile references/style-profile.json --genre <standard|sincere|micro-hope|surreal> --output-json <case-dir>/controller-audit/summary.json --output-md <case-dir>/controller-audit/summary.md
python scripts/run_blind_test.py draft.md $env:ANLIN_CORPUS_DIR --rounds 8 --placebo-rounds 2 --min-fragment-chars 550 --match-genre auto
python scripts/check_clean_eval_trace.py <case-dir>/opencode-output.txt --json
```

Use `--repair-brief` only to create a compact generator-facing repair interface. In finalized repair, the controller should prepare `finalized/repair-brief.txt` before the repair-agent attempt, usually through `prepare_finalized_repair_brief.py`; the repair agent reads that file and `draft.md`, writes one complete revised `draft.md`, and stops. The brief intentionally hides full metric lists so the repair agent does not reason through every ratio. For standard finalized repair, the brief is shape-first: rebuild visible broken body rows before solving content polish, and do not save a dense 8-25-row prose article as a "fixed" artifact. After the artifact is frozen, the controller reruns `check_style_profile.py` without `--repair-brief` for the full audit report.

For finalized repair, keep the phrase literal in controller notes: prepare the short `repair-brief.txt` before the repair attempt, expose only the brief and `draft.md` to the repair agent, then run the full profile report after the artifact is frozen. Terminal-only revised prose is not a repaired artifact.

The finalized repair trace audit also treats analysis-only attempts as artifact failures: if the repair agent reads `draft.md` or `repair-brief.txt` but never writes the revised `draft.md`, that run is invalid evidence even if the log contains a better proposed article. The repair brief now states that the first write to `draft.md` must be the final complete revised article, not a placeholder copy or unchanged draft; full validation remains controller work after the artifact is frozen.

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
python scripts\summarize_dev_checkpoints.py <case-dir> --bounded-draft <case-dir>\draft.md --finalized-draft <case-dir>\finalized\draft.md --trace-log <case-dir>\opencode-output.txt --corpus-dir $env:ANLIN_CORPUS_DIR --profile references\style-profile.json --genre <standard|sincere|micro-hope|surreal>
```

Fresh pass/fail claims should quote the exact command results. Older results in this README are status boundaries, not current verification.

`summarize_dev_checkpoints.py` will try to infer `--genre` from an `eval-07-...` or eval-name case directory when the argument is omitted. Still pass it explicitly in formal reports, especially for short sincere, micro-hope, or surreal cases, so the report does not silently compare a non-standard draft only against global standard-diary priors.

## Development Notes

`work/` contains local iterative outputs and is intentionally ignored by git unless a specific artifact is promoted into `audits/`, `evals/`, or `references/`. Do not delete process artifacts until information-loss review confirms they are no longer needed.

Historical status notes and failed-run diagnoses belong in `references/development-log.md`. They may be summarized or moved, but their factual content should not be dropped. When a log is migrated, preserve it in git before replacing it with a shorter README summary.

Development tests should rotate across multiple available model surfaces and record the exact model string plus reasoning/thinking setting in controller logs, not in runtime instructions. When recent runs are imbalanced, choose from the lowest-use available surfaces before returning to high-use surfaces. This is testing metadata only: runtime instructions should stay model-agnostic, and model-specific failures should be generalized into source shape, fact handling, sentence form, rhythm, tool routing, or repair-loop behavior. Concrete local model pools belong in `references/development-log.md`, not in this user-facing README.

If this repository is packaged for public distribution, exclude ignored local process directories such as `work/`. They are preserved locally for information-loss review and development forensics, but they are not part of the distributable skill surface.

Prompt compliance is a manual controller gate. If the user told the generator not to write money/consumption/price, visible adjacent substitutions such as payment, price, discount, balance, checkout, purchase, or consumption ledgers should be recorded as a blocking prompt-compliance failure even when generic hard/style gates are clean.

Full-corpus validation requires local originals. Set `ANLIN_CORPUS_DIR` or pass `--corpus-dir <corpus-dir>`. Without originals, use `references/portable-corpus.md` and report the result as portable or fragment-level review.

The skill is maintained as part of the `github-yjc` skill collection under the MIT license.

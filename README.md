# anlin-writing

This OpenCode skill generates, reviews, and evaluates Anlin/日寄-style Chinese prose for anonymous blind evaluation. The target is narrow: reduce stable identification as generated text under documented test conditions, while reporting only conditions, sample size, recognition/pass rates, false accusations, invalid rounds, and limits.

It must not claim real authorship, provenance, or objective indistinguishability.

## Corpus Boundary

The distributable skill does not require every user to own the 38 original articles. Runtime generation and portable review use bundled summaries: `references/portable-corpus.md`, `references/samples-index.md`, `references/corpus-cards/`, `references/background-fact-classes.json`, and `references/style-profile.json`.

The full 38-article corpus is a developer/controller input, not a runtime dependency. Use it only when available to rebuild cards/profile, run copy-overlap checks, calibrate thresholds, or run complete-article blind rounds. Set `ANLIN_CORPUS_DIR` or pass `--corpus-dir <corpus-dir>` for those stronger validation tasks.

## Current Status

Status: not yet proven. This skill is still under active development. It is not ready to claim the `<=10%` stable impostor-identification target because no current evidence package contains all required pieces: 15 clean-eval generation cases, a calibrated `8 impostor + 2 placebo` blind-round package, low stable-identification rate, low placebo false-accusation rate, and uncontaminated controller logs.

Current active-protocol recognition rate is `N/A`: no draft has yet reached a valid `8 impostor + 2 placebo` blind package under the active readiness rules. Checker pass rates, style-profile status, and legacy smaller diagnostic rounds are not substitutes for that rate.

The latest documented boundary is preserved in `references/development-log.md`. In short: compact profile briefs fixed one terminal-only / unchanged-artifact failure, but the newest targeted retests still did not become blind-round-ready. Rechecking the latest social-decline draft under the current gates narrows the remaining hard failures: bounded generation still stops before checker call 1/2 with rhythm/punctuation problems, and finalized repair can still drift into source-level rhythm/punctuation loops. The current finalized interface is artifact-only: the controller prepares `finalized/repair-brief.txt` before the repair attempt, the repair agent reads that brief plus `draft.md`, writes one complete `finalized/draft.md`, and stops; post-write validation belongs to the controller. A second write/edit to `finalized/draft.md`, any repair-agent checker command, a post-write repair-agent gate loop, post-write `python -c`, `Measure-Object`, `wc`, local line/character counters, visible threshold arithmetic, or skill-directory rediscovery in the same finalized attempt is invalid controller evidence. Recent single-write retests improved writeback discipline and removed some fact leaks, but the drafts still failed quality with rough self-damage shortage, underlength repair, period-row grid, prose-block compression, equal short-sentence row grids, message-order glue, group-chat crowd summaries, polite red-packet closure, or the opposite comma-carpet repair drift. The current interface now makes hard-gate findings outrank the compact style brief, treats the single finalized write as atomic, rejects prose-block compression, 80+ one-sentence rows, nearly all-comma line surfaces, and 650-899-character standard repair shrinkage as false escapes from rhythm failure, clarifies that private room-only wet texture is not rough exposure, keeps `忙项目`-style refusal excuses from becoming leave/调休/排班 biographies, treats ordinal message labels such as `第二条只...` / `下面还有...` as plot glue, rejects refusal repair that grows into `群里有人问` / `有人@我` crowd exposure or `人不到钱到` / `下次一起吃饭` etiquette settlement, requires neighbor/cashier/rider contact to touch the wet/dirty/payment/reply/body fact before it counts as a public hinge, and treats door opening / corridor light / neighbor-light imagery as threshold atmosphere unless it changes contact, payment, reply, route, or body action. Do not expand to blind rounds until a fresh bounded/finalized case is pass-ready under the active protocol.

Latest source-guidance fix: social-decline drafts now treat a plain OK/`好的` reply plus a private screen mark, water trace, sleeve, or room object as a screen loop unless that reply changes a visible next action. They also treat group-chat public exposure, polite red-packet settlement, and unrelated delivery/food-burn/room-chore errands as false repairs unless one local action is refusal-coupled: the reply, payment, route, body, door, object, old debt, or social position changes because of not going. Finalized repair now treats page shape as the first repair action: the repair brief points to a line-broken 6-8-cluster standard diary shape and explicitly rejects dense 8-25-row prose repairs, short-caption grids, and off-axis consequence theater before the single write. The minimal first-draft path, runtime repair, finalized repair, clean-eval wrapper, style repair brief, and strict checker use the same boundary.

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
| Runtime article generation | `SKILL.md`, then `references/clean-eval-first-draft-minimum.md`; add `references/standard-diary-source-engine.md` for standard diary; use `references/clean-generation-brief.md` after wrapper findings |
| Ordinary repair after a draft exists | `references/runtime-brief.md`, `references/feature-budget.md`, `references/anti-ai-slop.md`, then targeted fact/voice/title references as needed |
| Fact and background checks | `references/anlin-background.md`, `references/background-fact-classes.json`, `references/era-state.md` |
| Controller validation and blind testing | `references/validation-protocol.md`, `references/stylometric-ratio-protocol.md`, `references/blind-judge-angles.md`, `evals/README.md` |
| Detailed development history and failed-run evidence | `references/development-log.md` |
| Architecture audit | `references/runtime-layer-map.md` |

Clean-eval first drafts should not load controller or development-log files before the first complete `draft.md`; those files exist for validation, diagnosis, and maintenance.

For source-load conflict audits, `references/clean-eval-first-draft-minimum.md` owns the first formal draft. `references/clean-generation-brief.md`, `runtime-brief.md`, `generation-modes.md`, and `anti-ai-slop.md` remain available after the first draft or for ordinary repair, but they should not be preloaded as a checklist in clean-eval first-draft generation.

## Architecture

The important design choice is separation of layers. The generation agent should not read every file before writing; that turns review categories into visible article ingredients.

```text
anlin-writing/
├── SKILL.md                         # routing, clean-eval boundary, output rules
├── references/
│   ├── clean-eval-first-draft-minimum.md # short first-draft contract
│   ├── clean-generation-brief.md     # expanded clean-eval repair contract
│   ├── standard-diary-source-engine.md # compact standard-diary middle engine
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

Read the two checkpoints as separate questions, not one averaged score: bounded clean-eval answers whether natural guidance plus limited checker-driven repair gets close under the clean-eval boundary; finalized repair answers whether the public repair interface can converge from a copied bounded draft without metric chasing. Within bounded clean-eval, a preflight stop before call 1/2 means the draft never reached the two real checker calls, while a call 2/2 failure means the limited checker path was actually tested. A bounded failure with a finalized pass means the source guidance still needs improvement. A finalized failure or `review` means the final article is not clean yet, even if some local checker problems were fixed.

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

1. Load `references/clean-eval-first-draft-minimum.md` first and use its source loop for the first complete draft.
2. For standard diary clean-eval, load `references/standard-diary-source-engine.md`; for short non-standard genres, stay with the clean brief.
3. Check `.anlin-clean-eval-mode`, then run `Get-Location` / `pwd`; the current directory must be the external case workspace, not `<skill-dir>`.
4. Start from a small lived friction, not from a checklist.
5. Select scenes from action, body, screen, money, route, social misfire, memory trigger, or useless residue.
6. Open `anlin-background.md` only after selected scenes already contain facts that need checking.
7. Write a complete titled article using exactly relative `draft.md` / `.\draft.md` before the first checker. Do not run line-rhythm scripts before the first wrapper call.
8. Run `scripts/clean_run_checker.py draft.md --strict --draft-gate`.
9. If `CLEAN_RUN_PREFLIGHT` appears, revise before the first checker call is consumed; if `CLEAN_RUN_PREFLIGHT_STOP` appears, output the current draft unchanged and let the controller record failure.
10. If a rhythm script runs and `draft.md` is then rewritten or edited, rerun the relevant rhythm script before the next wrapper call or keep the repair inside the existing line-broken corridor.
11. Do at most one repair/rewrite and at most two clean-eval checker calls.
12. After the second checker call, output the current `draft.md` exactly.

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

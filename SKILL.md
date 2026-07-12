---
name: "anlin-writing"
description: "Generate, review, or evaluate Anlin/日寄-style anonymous blind-evaluation prose against the Anlin corpus. Use ONLY when the user explicitly mentions anlin-writing, anlinwriting, Anlin, 日寄, Anlin-style, 像Anlin那样写, 模拟日寄, 盲评, or asks for Anlin corpus evaluation. In any workspace containing `.anlin-clean-eval-mode`, check that marker before drafting and use `clean_run_checker.py`, not the normal checker."
---

# anlin-writing

Generate, repair, and evaluate complete titled Chinese prose for anonymous blind evaluation. The target is narrow: make generated text less stably identifiable as generated under documented blind-review conditions. Report only test conditions, sample size, recognition/pass rates, false-accusation rates, and limitations. Do not claim real authorship, provenance, or indistinguishability.

Generated prose must not mention process labels such as `仿写`, `AI`, `生成`, `验证通过`, `38篇语料`, corpus, blind test, checker, or methodology. Controller reports may discuss methods; article bodies may not.

This skill is self-contained at runtime. Do not depend on private external anti-slop, author-style, or personal writing skills. Anti-AI guidance lives in this skill's own references and checkers.

## Artifact-Backed Entry Contract

When this skill triggers for article generation, do not compose the article directly in the final chat response. The first prose artifact must be a real `draft.md` in the current task or evaluation workspace. A terminal-only article is a failed run because the controller cannot inspect route, first saved shape, checker state, or repair history.

Before writing any article sentence, make the routing action visible: in a possible formal/eval workspace, check `.anlin-clean-eval-mode` and the current directory first; outside clean-eval, choose an ordinary task workspace for `draft.md`. "Output prose only" means output only the final article after the artifact-backed draft/check path, not bypassing `draft.md`.

## Mode Router

Choose the smallest mode that matches the current task:

- **Clean-eval mode has priority over ordinary article wording**: `.anlin-clean-eval-mode` exists, or the controller is measuring natural first-draft guidance. The marker check and cwd confirmation are two separate tool actions: after checking `.anlin-clean-eval-mode`, the next tool action must be standalone `Get-Location` / `pwd`, before deciding ordinary mode. Both must be visible before any reference read, glob/path probe, or draft write; do not use controller `--dir`, a glob title, or an absolute path as cwd evidence. A present marker overrides "write an article", "give me prose", "save a draft", or other ordinary-user phrasing. Load only `references/clean-eval-first-draft-minimum.md`; for standard diary also load `references/anlin-collage-source-model.md` (replaces the old `standard-diary-source-engine.md`). Write one complete `draft.md`, then use `scripts/clean_run_checker.py` for at most two actual checker calls; preflight attempts do not consume that call budget and may continue until an explicit `CLEAN_RUN_PREFLIGHT_STOP`. Do not call the normal checker in the bounded case directory.
- **Ordinary user mode**: use only after clean-eval mode has been ruled out. The user wants an article, revision, or saved prose outside a bounded clean-eval workspace. Ask only for missing facts that materially change the result. Use `references/runtime-brief.md` for drafting/repair, then run the normal checker if validation is needed.
- **Finalized repair mode**: the controller copied a bounded draft into a `finalized/` directory. If `repair-brief.txt` declares either compact mode, read only `draft.md` and `repair-brief.txt`.
  - `repair_mode: hard_pass_review_in_place` and `repair_mode: source_rewrite_compact` are self-contained; do not load `references/finalized-repair-minimum.md`.
  - For a missing/invalid brief or `controller_tool_error`, use `references/finalized-repair-minimum.md` as the fallback artifact contract.
  - In `source_rewrite_compact`, follow the one fragment focus and exact scope supplied by the brief. Most routes replace one existing fragment relation; a severely underbuilt route may explicitly require a source-level rebuild across the existing article. Do not reconstruct hidden blocker/profile lists or add an independent scene/packet. Make the one complete write to `draft.md`, then stop. If a chat reply is required, output exactly `artifact_written`.
- **Controller validation mode**: after an artifact exists, run deterministic gates, style-profile audit, corpus comparison, blind rounds, and placebo calibration. Use `references/validation-protocol.md`.

Clean-eval and finalized repair are separate checkpoints. A finalized pass does not retroactively make the bounded first draft successful. A finalized `review` or `fail` means the final article is still unresolved and is not ready for blind rounds.

## Artifact Locations

Do not write generated articles into the skill directory.

- If the user only wants prose in chat, use temporary `draft.md` in the current task working directory, validate or repair there, then output only the article. Do not skip the temporary artifact just because the final reply should contain prose only.
- If the user asks to save a file and gives no output directory, ask once for the output directory. If there is no answer, save in the current task working directory, not inside `<skill-dir>`.
- In tests and blind review, use an external evaluation workspace such as `<eval-workspace>/iteration-<n>/eval-<id>/draft.md`; `evals/` defines prompts and protocols, not output storage.
- In clean-eval and finalized repair, write/read the article using relative `draft.md` or `.\draft.md` in the current case directory. Do not write `<skill-dir>/.../draft.md`, do not reuse a prior run path, and do not invent an absolute artifact path unless ordinary user mode explicitly requested that path.

`<skill-dir>` is only for resolving bundled references and scripts. If the current directory is the skill directory, switch to an external task/eval workspace before writing prose.

## Clean-Eval Entry

For formal clean-eval generation, the first draft is intentionally under-instructed:

1. Check `.anlin-clean-eval-mode` as one tool action.
2. As the next tool action, run standalone `Get-Location` / `pwd` and confirm the external case workspace.
3. Only after both checks are visible, read `references/clean-eval-first-draft-minimum.md`.
4. If the selected genre is standard diary/日寄, read `references/anlin-collage-source-model.md` (replaces the old `standard-diary-source-engine.md` which is preserved for reference).
5. Write one complete titled article to `draft.md`.
6. Run `python <skill-dir>/scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing --genre <selected-genre>` when genre is known.

After the minimal source reads finish, the next tool action must be one complete write to relative `draft.md` or `.\draft.md`. Do not spend another model turn comparing openings, rehearsing possible hinges, restating the prompt, or drafting scratch prose in reasoning. Choose the first workable fragment slate and persist it; an imperfect artifact can be checked, but an unwritten better plan is not evidence. For standard diary, several independent thought-turns should normally appear; one continuous scene is not the default.

Before the first complete `draft.md`, do not open long repair, validation, judge, style-ratio, corpus-card, or checker-source files. In particular, do not load `references/clean-generation-brief.md`, `references/runtime-brief.md`, `references/anti-ai-slop.md`, `references/generation-modes.md`, `references/review-rubric.md`, `references/writing-checklist.md`, `references/self-check.md`, `references/stylometric-ratio-protocol.md`, `references/validation-protocol.md`, `references/development-log.md`, `evals/README.md`, or `references/corpus-cards/`.

If the wrapper reports `CLEAN_RUN_PREFLIGHT` or `CLEAN_RUN_POSTCHECK_PREFLIGHT`, the wrapper output is the complete repair interface. Use the `--generator-facing` interface: exact counts and thresholds stay in controller state, while the generator receives only qualitative findings and one next action. The wrapper does not rewrite `draft.md`; it records byte-preserving snapshots and prints the next explicit action. In bounded clean-eval, do not load `references/clean-generation-brief.md` or another repair/reference file after that result. For source/content findings, treat multiple messages as one diagnosis of the earliest broken fragment relation: preserve or rebuild complete genre-appropriate mass, replace that relation once, and do not solve one item per metric. If the output contains only shape findings, do not add material; perform only the named local rhythm action. After any `draft.md` rewrite, rerun the wrapper immediately; if the wrapper explicitly names a rhythm script, run that exact final shape step and then rerun the wrapper. Do not hand-count rows, characters, punctuation, or connectors between calls, and do not run homemade counters or other commands between the write and the rerun. The post-check variant still protects checker call 2/2 and does not consume it. If the wrapper reports `CLEAN_RUN_PREFLIGHT_STOP` or `CLEAN_RUN_STOP`, stop repairing, read `draft.md` once, and output that exact article. Do not switch to ordinary checker flow after the bounded stop.

## Finalized Repair Entry

Finalized repair is artifact-only. `repair-brief.txt` is the generator-facing interface; full style-profile output remains controller evidence after the artifact is frozen.

When the brief declares `repair_mode: hard_pass_review_in_place` or `repair_mode: source_rewrite_compact`, it is the complete repair interface: read only `draft.md` and `repair-brief.txt`, and do not load `references/finalized-repair-minimum.md`. The source-compact brief intentionally hides the detailed hard/profile findings; follow its single `source_focus`, route-appropriate `scope_contract` (local cluster or explicit source-level rebuild), `mass_contract`, and `shape_contract` without turning them into a checklist. For a missing/invalid brief or `controller_tool_error`, follow the finalized minimum path instead.

During the repair attempt, do not run `check_anlin_violations.py`, `check_style_profile.py`, `clean_run_checker.py`, `prepare_finalized_repair_brief.py`, local counters, `python -c`, `Measure-Object`, `wc`, path probes, source/test reads, threshold searches, old-log searches, or checker/controller helpers. Only a schema-valid controller result with return code `1` is a normal not-pass signal. `controller_tool_error`, invalid output, or any other unexpected result is unavailable, not quality evidence.

The first write to `draft.md` must be the final complete revised article. Do not write an unchanged placeholder, then a second version. Do not print a final article only to terminal/chat. Do not patch after writing. Controller validation reruns the strict hard gate and full style-profile report afterward.

## Reference Routing

Use these files by task; do not load everything.

| Need | Read |
|---|---|
| Clean-eval first draft | `references/clean-eval-first-draft-minimum.md`; for standard diary also add `references/anlin-collage-source-model.md` (replaces the old `standard-diary-source-engine.md`) |
| Clean-eval repair after wrapper output | wrapper output only; no additional reference read |
| Ordinary drafting or non-formal repair | `references/runtime-brief.md`, then `references/feature-budget.md` and `references/anti-ai-slop.md` only as needed |
| Fact or background check after scene selection | `references/anlin-background.md`, `references/background-fact-classes.json`, `references/era-state.md` |
| Title problem | `references/title-model.md` |
| Voice, structure, or deep critique after a draft exists | `references/voice-model.md`, `references/structure-patterns.md`, `references/review-rubric.md`, `references/self-check.md` |
| Finalized repair checkpoint | `repair-brief.txt` only for `hard_pass_review_in_place` or `source_rewrite_compact`; `references/finalized-repair-minimum.md` only for a missing/invalid brief or `controller_tool_error` |
| Style-ratio audit | `references/stylometric-ratio-protocol.md`, `scripts/check_style_profile.py` |
| Full validation and blind review | `references/validation-protocol.md`, `references/blind-judge-angles.md`, `references/judge-prompt-templates.md` |
| Architecture or repeated-failure diagnosis | `references/runtime-layer-map.md` |

Background is a contradiction boundary, not a content quota. Do not add 云南、王者、狗哥、痛风、外卖、知乎, AI/GPT, cities, districts, game ranks, office facts, or platform details merely because a reference permits them. Game may appear when the prompt, action, memory trigger, social wound, practical delay, or cognitive turn needs it; it is optional and should stay low-specificity unless supported.

Do not use corpus ratio targets as a pre-draft recipe. Style-profile and predictive intervals are post-draft audit tools. If a ratio drifts, inspect the earliest broken fragment relation, voice signal, prompt surface, title source, fact specificity, or visible shape; do not add a feature merely to move a ratio.

## Runtime Guardrails

- Start from a fragment, thought, voice turn, or ordinary friction, not a checklist or prompt inventory.
- Complete article means title plus body; every test draft must include a title.
- Ask at most one intake round for missing information that materially affects quality, such as target date/period, usable day material, genre, output destination, and whether low-confidence projection or lookup is allowed. Multiple short questions can be in that one round; skip questions already answered by the user.
- If information is missing and the user does not answer, lower specificity: avoid unsupported city/district, company, route, current events, game tactics, office biography, spouse/child/family-status claims, and concrete platform facts.
- Do not satisfy every style feature. Use a few consequential features deeply rather than all labels shallowly.
- Remove high-risk AI surfaces before output: `不是X，是Y` / `不是X，而是Y`, blog-like explanation, therapeutic humanizer phrases, prompt-shaped titles, neat moral closure, long prompt inventories, `——` feeling captions, unsupported specifics, and visible ratio/checker language.
- For standard diary, let rhythm follow thought, speech, memory, association, body, object, or action movement; avoid prose-block compression, tiny-line grids, period-row grids, and comma carpets without prescribing a fixed page shape.
- For social-decline prompts, treat the invitation or refusal as one possible fragment. Do not invent a consequence chain, group-chat crowd, work biography, or etiquette closure merely to prove the prompt.
- For sincere/micro-hope short forms, keep uneven clusters, present practical action, awkward reply/logistics, and loose factual retreat. Do not preserve every prompt prop or expand into standard diary bulk.
- Short-genre profile fallback is not strong evidence. If the style-profile shows `inconclusive` due to small corpus, do not force standard-diary rhythm, length, or texture to satisfy the fallback. A correct short-genre draft may flag `review` under global priors; that is a corpus limitation, not a draft failure. Do not add background, game, body, or platform packets to compensate for an unstable short-genre profile.

## Output Rules

Checker findings are not tool failures and are not a second writing interface. A warning or ordinary error means the persisted artifact has a review finding; it does not authorize an unpersisted terminal repair, a fallback reference reload, or a third bounded write. The wrapper is not a broken tool: follow its current artifact and stop boundary, then let the controller classify the evidence.

- If the user asks for prose, output prose only after the article has existed as `draft.md` unless execution failure prevents file writing. The first visible line must be the title.
- Never prepend `Here is`, `完成`, `以下是`, `最终文章`, protocol notes, checker summaries, markdown fences, or process commentary.
- Do not narrate reference loading, file checks, or internal decisions in the article or final prose output.
- If the user asks for validation, report commands, conditions, sample size, and results.
- If corpus or background evidence is unavailable, state the limitation in the validation report, not inside the article.
- If a request asks to impersonate real provenance, forge evidence, or deceive about authorship, refuse that part and offer anonymous style-evaluation output instead.

## Validation Commands

These commands are mode-scoped. In bounded clean-eval, `clean_run_checker.py` is the only generator-facing checker; direct `check_anlin_violations.py` or `check_style_profile.py` calls belong to ordinary repair, finalized/controller validation after artifact freeze, or developer audits. A clean-eval generator must not use the normal checker because it contaminates the bounded source-guidance measurement.

```powershell
python scripts/check_anlin_violations.py draft.md
python scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre <standard|sincere|micro-hope|surreal> --corpus-dir <corpus-dir>
python scripts/clean_run_checker.py draft.md --strict --draft-gate --generator-facing --genre <standard|sincere|micro-hope|surreal>
python scripts/prepare_finalized_repair_brief.py <case-dir>/finalized/draft.md --genre <standard|sincere|micro-hope|surreal>
python scripts/check_style_profile.py draft.md --genre <standard|sincere|micro-hope|surreal> --draft-gate --strict
python scripts/check_style_profile.py draft.md --genre <standard|sincere|micro-hope|surreal> --draft-gate --strict --repair-brief
python scripts/calibrate_style_profile.py <corpus-dir> --profile references/style-profile.json
python scripts/summarize_dev_checkpoints.py <case-dir> --bounded-draft <case-dir>/draft.md --finalized-draft <case-dir>/finalized/draft.md --trace-log <case-dir>/opencode-output.txt --corpus-dir <corpus-dir> --profile references/style-profile.json
python scripts/run_blind_test.py draft.md <corpus-dir> --rounds 8 --placebo-rounds 2 --match-genre auto
python -m unittest discover -s test
```

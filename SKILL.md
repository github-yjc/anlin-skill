---
name: "anlin-writing"
description: "Generate, review, or evaluate Anlin/日寄-style anonymous blind-evaluation prose against the Anlin corpus. Use ONLY when the user explicitly mentions anlin-writing, anlinwriting, Anlin, 日寄, Anlin-style, 像Anlin那样写, 模拟日寄, 盲评, or asks for Anlin corpus evaluation. In any workspace containing `.anlin-clean-eval-mode`, check that marker before drafting and use `clean_run_checker.py`, not the normal checker."
---

# anlin-writing

Generate, repair, and evaluate complete titled Chinese prose for anonymous blind evaluation. The target is narrow: make generated text less stably identifiable as generated under documented blind-review conditions. Report only test conditions, sample size, recognition/pass rates, false-accusation rates, and limitations. Do not claim real authorship, provenance, or indistinguishability.

Generated prose must not mention process labels such as `仿写`, `AI`, `生成`, `验证通过`, `38篇语料`, corpus, blind test, checker, or methodology. Controller reports may discuss methods; article bodies may not.

This skill is self-contained at runtime. Do not depend on private external anti-slop, author-style, or personal writing skills. Anti-AI guidance lives in this skill's own references and checkers.

## Mode Router

Choose the smallest mode that matches the current task:

- **Ordinary user mode**: the user wants an article, revision, or saved prose. Ask only for missing facts that materially change the result. Use `references/runtime-brief.md` for drafting/repair, then run the normal checker if validation is needed.
- **Clean-eval mode**: `.anlin-clean-eval-mode` exists, or the controller is measuring natural first-draft guidance. First tool action must check the marker; before writing, confirm the current directory is the external case workspace. Load only `references/clean-eval-first-draft-minimum.md`; for standard diary also load `references/standard-diary-source-engine.md`. Write one complete `draft.md`, then use `scripts/clean_run_checker.py` at most twice. Do not call the normal checker in the bounded case directory.
- **Finalized repair mode**: the controller copied a bounded draft into a `finalized/` directory. Read `draft.md` and `repair-brief.txt` when present. Use `references/finalized-repair-minimum.md` only if already available through this skill. Make one complete source rewrite, write it back to `draft.md`, then stop. If a chat reply is required, output exactly `artifact_written`.
- **Controller validation mode**: after an artifact exists, run deterministic gates, style-profile audit, corpus comparison, blind rounds, and placebo calibration. Use `references/validation-protocol.md`.

Clean-eval and finalized repair are separate checkpoints. A finalized pass does not retroactively make the bounded first draft successful. A finalized `review` or `fail` means the final article is still unresolved and is not ready for blind rounds.

## Artifact Locations

Do not write generated articles into the skill directory.

- If the user only wants prose in chat, use temporary `draft.md` in the current task working directory, validate or repair there, then output only the article.
- If the user asks to save a file and gives no output directory, ask once for the output directory. If there is no answer, save in the current task working directory, not inside `<skill-dir>`.
- In tests and blind review, use an external evaluation workspace such as `<eval-workspace>/iteration-<n>/eval-<id>/draft.md`; `evals/` defines prompts and protocols, not output storage.
- In clean-eval and finalized repair, write/read the article using relative `draft.md` or `.\draft.md` in the current case directory. Do not write `<skill-dir>/.../draft.md`, do not reuse a prior run path, and do not invent an absolute artifact path unless ordinary user mode explicitly requested that path.

`<skill-dir>` is only for resolving bundled references and scripts. If the current directory is the skill directory, switch to an external task/eval workspace before writing prose.

## Clean-Eval Entry

For formal clean-eval generation, the first draft is intentionally under-instructed:

1. Check `.anlin-clean-eval-mode`.
2. Confirm the current directory is the external case workspace.
3. Read `references/clean-eval-first-draft-minimum.md`.
4. If the selected genre is standard diary/日寄, read `references/standard-diary-source-engine.md`.
5. Write one complete titled article to `draft.md`.
6. Run `python <skill-dir>/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre <selected-genre>` when genre is known.

Before the first complete `draft.md`, do not open long repair, validation, judge, style-ratio, corpus-card, or checker-source files. In particular, do not load `references/clean-generation-brief.md`, `references/runtime-brief.md`, `references/anti-ai-slop.md`, `references/generation-modes.md`, `references/review-rubric.md`, `references/writing-checklist.md`, `references/self-check.md`, `references/stylometric-ratio-protocol.md`, `references/validation-protocol.md`, `references/development-log.md`, `evals/README.md`, or `references/corpus-cards/`.

If the wrapper reports `CLEAN_RUN_PREFLIGHT`, use `references/clean-generation-brief.md` as the detailed repair interface. If it reports `CLEAN_RUN_PREFLIGHT_STOP` or `CLEAN_RUN_STOP`, stop repairing, read `draft.md` once, and output that exact article. Do not switch to ordinary checker flow after the bounded stop.

## Finalized Repair Entry

Finalized repair is artifact-only. `repair-brief.txt` is the generator-facing interface; full style-profile output remains controller evidence after the artifact is frozen.

During the repair attempt, do not run `check_anlin_violations.py`, `check_style_profile.py`, `clean_run_checker.py`, `prepare_finalized_repair_brief.py`, local counters, `python -c`, `Measure-Object`, `wc`, path probes, source/test reads, threshold searches, old-log searches, or checker/controller helpers. A nonzero `--strict --repair-brief` result inside a prepared brief means the draft needs repair, not that the tool is broken.

The first write to `draft.md` must be the final complete revised article. Do not write an unchanged placeholder, then a second version. Do not print a final article only to terminal/chat. Do not patch after writing. Controller validation reruns the strict hard gate and full style-profile report afterward.

## Reference Routing

Use these files by task; do not load everything.

| Need | Read |
|---|---|
| Clean-eval first draft | `references/clean-eval-first-draft-minimum.md`; add `references/standard-diary-source-engine.md` for standard diary |
| Clean-eval repair after wrapper output | `references/clean-generation-brief.md` |
| Ordinary drafting or non-formal repair | `references/runtime-brief.md`, then `references/feature-budget.md` and `references/anti-ai-slop.md` only as needed |
| Fact or background check after scene selection | `references/anlin-background.md`, `references/background-fact-classes.json`, `references/era-state.md` |
| Title problem | `references/title-model.md` |
| Voice, structure, or deep critique after a draft exists | `references/voice-model.md`, `references/structure-patterns.md`, `references/review-rubric.md`, `references/self-check.md` |
| Finalized repair checkpoint | `references/finalized-repair-minimum.md` plus `repair-brief.txt` |
| Style-ratio audit | `references/stylometric-ratio-protocol.md`, `scripts/check_style_profile.py` |
| Full validation and blind review | `references/validation-protocol.md`, `references/blind-judge-angles.md`, `references/judge-prompt-templates.md` |
| Architecture or repeated-failure diagnosis | `references/runtime-layer-map.md` |

Background is a contradiction boundary, not a content quota. Do not add 云南、王者、狗哥、痛风、外卖、知乎, AI/GPT, cities, districts, game ranks, office facts, or platform details merely because a reference permits them. Game may appear when the prompt, action, memory trigger, social wound, practical delay, or cognitive turn needs it; it is optional and should stay low-specificity unless supported.

Do not use corpus ratio targets as a pre-draft recipe. Style-profile and predictive intervals are post-draft audit tools. If a ratio drifts, repair the underlying function: scene mass, consequence, rhythm, prompt displacement, title source, or fact specificity.

## Runtime Guardrails

- Start from friction, not a checklist or prompt inventory.
- Complete article means title plus body; every test draft must include a title.
- Ask at most one intake round for missing information that materially affects quality, such as target date/period, usable day material, genre, output destination, and whether low-confidence projection or lookup is allowed. Multiple short questions can be in that one round; skip questions already answered by the user.
- If information is missing and the user does not answer, lower specificity: avoid unsupported city/district, company, route, current events, game tactics, office biography, spouse/child/family-status claims, and concrete platform facts.
- Do not satisfy every style feature. Use a few consequential features deeply rather than all labels shallowly.
- Remove high-risk AI surfaces before output: `不是X，是Y` / `不是X，而是Y`, blog-like explanation, therapeutic humanizer phrases, prompt-shaped titles, neat moral closure, long prompt inventories, `——` feeling captions, unsupported specifics, and visible ratio/checker language.
- For standard diary, rhythm must come from action, speech, body, payment, reply, door, route, or object movement; avoid prose-block compression, tiny-line grids, period-row grids, and comma carpets.
- For social-decline prompts, the refusal aftermath must change a later visible action. Do not leave it as `message -> ticket/gift calculation -> OK reply -> room object`; also avoid group-chat crowd summaries and tidy etiquette closure.
- For sincere/micro-hope short forms, keep uneven clusters, present practical action, awkward reply/logistics, and loose factual retreat. Do not preserve every prompt prop or expand into standard diary bulk.
- Short-genre profile fallback is not strong evidence. If the style-profile shows `inconclusive` due to small corpus, do not force standard-diary rhythm, length, or texture to satisfy the fallback. A correct short-genre draft may flag `review` under global priors; that is a corpus limitation, not a draft failure. Do not add background, game, body, or platform packets to compensate for an unstable short-genre profile.

## Output Rules

- If the user asks for prose, output prose only unless they requested validation notes. The first visible line must be the title.
- Never prepend `Here is`, `完成`, `以下是`, `最终文章`, protocol notes, checker summaries, markdown fences, or process commentary.
- Do not narrate reference loading, file checks, or internal decisions in the article or final prose output.
- If the user asks for validation, report commands, conditions, sample size, and results.
- If corpus or background evidence is unavailable, state the limitation in the validation report, not inside the article.
- If a request asks to impersonate real provenance, forge evidence, or deceive about authorship, refuse that part and offer anonymous style-evaluation output instead.

## Validation Commands

```powershell
python scripts/check_anlin_violations.py draft.md
python scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre <standard|sincere|micro-hope|surreal> --corpus-dir <corpus-dir>
python scripts/clean_run_checker.py draft.md --strict --draft-gate --genre <standard|sincere|micro-hope|surreal>
python scripts/prepare_finalized_repair_brief.py <case-dir>/finalized/draft.md --genre <standard|sincere|micro-hope|surreal>
python scripts/check_style_profile.py draft.md --genre <standard|sincere|micro-hope|surreal> --draft-gate --strict
python scripts/check_style_profile.py draft.md --genre <standard|sincere|micro-hope|surreal> --draft-gate --strict --repair-brief
python scripts/calibrate_style_profile.py <corpus-dir> --profile references/style-profile.json
python scripts/summarize_dev_checkpoints.py <case-dir> --bounded-draft <case-dir>/draft.md --finalized-draft <case-dir>/finalized/draft.md --trace-log <case-dir>/opencode-output.txt --corpus-dir <corpus-dir> --profile references/style-profile.json
python scripts/run_blind_test.py draft.md <corpus-dir> --rounds 8 --placebo-rounds 2 --match-genre auto
python -m unittest discover -s test
```

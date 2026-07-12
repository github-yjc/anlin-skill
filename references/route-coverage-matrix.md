# Route Coverage / Information-Loss Matrix

Developer-facing audit document. Maps critical runtime and validation constraints to their owning files after the `SKILL.md` architecture slim-down. Do not load this file during ordinary article generation, clean-eval first drafts, finalized repair attempts, or blind judging.

This matrix intentionally uses stable owner files and short evidence anchors, not fixed line numbers. Line numbers drift whenever the router is edited; use the anchors below with search/tests.

## Legend

| Owner | Meaning |
|---|---|
| `SKILL.md` | Thin runtime router: mode selection, artifact paths, reference routing, output rules, core safety |
| `Layer 0/1` | User-facing generation source files, chiefly `clean-eval-first-draft-minimum.md`, `anlin-collage-source-model.md`, and clean repair guidance |
| `Layer 2` | Background/fact contradiction gates |
| `Layer 3` | Finalized repair, style-profile, deterministic gates, and controller summaries |
| `Layer 4` | Full validation, blind rounds, placebo calibration, and judge prompts |
| `tests` | Regression tests verify the concept, preferably by checking the correct owner file rather than a global text dump |

## Matrix

| # | Constraint | Owner files | Evidence anchor |
|---|---|---|---|
| 1 | No authorship/provenance claims | `SKILL.md` | `Do not claim real authorship, provenance, or indistinguishability` |
| 2 | Complete titled article | `SKILL.md`, clean-eval minimum, output rules | `Complete article means title plus body`; `Write one complete titled article to draft.md` |
| 3 | No process labels in prose | `SKILL.md` | `Generated prose must not mention process labels` |
| 4 | Artifact location outside skill dir | `SKILL.md`, clean-generation brief, `README.md` | `Do not write generated articles into the skill directory`; `relative draft.md` |
| 4a | Article generation is artifact-backed | `SKILL.md`, trace checker, checkpoint summary tests | `Artifact-Backed Entry Contract`; `first prose artifact`; `terminal-only article is a failed run` |
| 5 | Clean-eval marker and first tool action | `SKILL.md`, clean-generation brief, validation protocol | `.anlin-clean-eval-mode`; `First tool action must check the marker` |
| 5a | Clean-eval marker priority over ordinary article wording | `SKILL.md`, `references/runtime-brief.md`, `references/anti-ai-slop.md` | `A present marker overrides "write an article"`; `Clean-eval misroute guard`; `clean-eval-first-draft-minimum.md` owns the first-draft source loop |
| 6 | Bounded clean-eval uses wrapper only | `SKILL.md`, clean-generation brief, validation protocol | `clean_run_checker.py`; `Do not call the normal checker in the bounded case directory` |
| 7 | First-draft no-load rule | `SKILL.md`, `references/clean-eval-first-draft-minimum.md`, `references/clean-generation-brief.md` | `Before the first complete draft.md, do not open long repair` |
| 7a | Misloaded runtime/anti-slop references return to minimum route | `references/runtime-brief.md`, `references/anti-ai-slop.md`, tests | `stop using this file before drafting`; load `references/clean-eval-first-draft-minimum.md`; `Do not keep reading this file as a negative checklist` |
| 8 | Social-decline refusal aftermath | `references/clean-eval-first-draft-minimum.md`, `references/anlin-collage-source-model.md` | `An invitation or refusal may be one fragment`; local consequence only when earned |
| 9 | Punctuation pendulum source fix | `references/clean-eval-first-draft-minimum.md`, `references/anlin-collage-source-model.md` | `fragment movement`; thought, speech, memory, body, object, and action decide the marks |
| 10 | Background as contradiction boundary, not quota | `SKILL.md`, Layer 2 fact docs, README | `Background is a contradiction boundary, not a content quota` |
| 11 | Game allowed but not required | `SKILL.md`, background docs | `Game may appear ... optional` |
| 12 | Finalized one-write-and-stop | `SKILL.md`, `references/finalized-repair-minimum.md`, `references/runtime-brief.md`, `references/validation-protocol.md` | `first write to `draft.md` must be the final complete revision`; `artifact_written` |
| 13 | Compact repair brief vs full controller report | `SKILL.md`, `references/finalized-repair-minimum.md`, `references/validation-protocol.md`, `references/runtime-layer-map.md` | `repair-brief.txt is the generator-facing interface`; `without `--repair-brief` for the full report`; `full style-profile output remains controller evidence` |
| 14 | Active blind package is 8 impostor + 2 placebo | `references/validation-protocol.md`, `README.md`, judge templates, run script | `8 impostor + 2 placebo`; `Current active-protocol recognition rate is `N/A`` |
| 15 | Portable runtime | `SKILL.md`, README, runtime docs | `self-contained at runtime`; no local machine paths in active runtime docs |
| 16 | Model-agnostic runtime | `README.md`, validation protocol, runtime docs | `runtime instructions should stay model-agnostic`; no provider/model branches in runtime docs |
| 17 | Title as blind surface | `SKILL.md`, README, validation/rubric docs | `first visible line must be the title`; `title is part of the blind-review surface` |
| 18 | Ordinary-user intake: one grouped round | `SKILL.md`, runtime brief | `Ask at most one intake round`; `Multiple short questions can be in that one round` |
| 19 | Missing information lowers specificity | `SKILL.md`, runtime brief | `lower specificity`; avoid unsupported city/company/route/game tactics |
| 20 | Do not satisfy every style feature | `SKILL.md`, feature-budget docs | `Use a few consequential features deeply` |
| 21 | Remove high-risk AI surfaces | `SKILL.md`, anti-AI and checker docs | `not X, but Y` / `不是X，是Y`; `high-risk AI surfaces` |
| 22 | Standard diary rhythm from movement | `SKILL.md`, `references/anlin-collage-source-model.md` | `rhythm follows thought, speech, memory, association, body, object, or action movement`; several independent thought-turns normally appear |
| 23 | Social-decline remains one possible fragment | `SKILL.md`, `references/clean-eval-first-draft-minimum.md`, `references/anlin-collage-source-model.md` | `An invitation or refusal may be one fragment among memories, jokes, work facts, old messages, bodily observations, or unrelated daily thoughts`; local consequence only when earned |
| 24 | Short forms keep uneven clusters | `SKILL.md`, `references/clean-generation-brief.md`, `references/runtime-brief.md` | `Short-genre profile fallback is not strong evidence`; `keep uneven clusters` |
| 25 | Output rules: no wrappers/fences/process chatter | `SKILL.md`, clean-generation brief | `Never prepend Here is`; `Do not print an English or Chinese scene plan` |
| 26 | Refuse real-provenance deception | `SKILL.md` | `If a request asks to impersonate real provenance... refuse that part` |
| 27 | Clean-eval, finalized, ordinary, controller modes are separate | `SKILL.md`, validation protocol, `README.md` | `Mode Router`; `separate checkpoints`; finalized pass does not retroactively fix bounded |
| 28 | Breathing fragments are syntax units | `references/clean-eval-first-draft-minimum.md`, `references/anlin-collage-source-model.md` | `breathing fragments, not sentence rows`; punctuation follows movement |
| 29 | Fragment relation follows actual movement | `references/clean-eval-first-draft-minimum.md`, `references/anlin-collage-source-model.md` | `Use whichever relationships the movement earns`; causal movement is allowed but optional; direct jumps are allowed |
| 30 | Connectors come from real turns | `references/anlin-collage-source-model.md`, `references/runtime-brief.md` | connector coverage is a diagnostic, not a content quota |
| 31 | Title from body, not prompt-prop loop | `references/clean-eval-first-draft-minimum.md`, `references/anlin-collage-source-model.md`, `references/title-model.md` | title after body exists; avoid prompt-prop title loop |
| 32 | Private wet/dirty only counts when it changes action | `references/anlin-collage-source-model.md`, `references/clean-generation-brief.md`, `references/runtime-brief.md` | `Private grime is not an event`; changes payment, reply, door, bag, body movement, or social position |
| 33 | Group-chat/etiquette closure guard | `references/clean-eval-first-draft-minimum.md`, `references/anlin-collage-source-model.md` | group-chat summaries and polite settlement are optional-risk diagnostics |
| 34 | Refusal overgrowth guard | `references/anlin-collage-source-model.md`, `references/clean-eval-first-draft-minimum.md` | refusal-coupled only when earned; no multi-day subplot |
| 35 | `忙项目` stays an excuse, not biography | `references/clean-eval-first-draft-minimum.md`, `references/anlin-collage-source-model.md`, checker | keep it as a lie/excuse surface; no leave/schedule/office biography |
| 36 | Finalized repair is artifact-only | `SKILL.md`, `references/finalized-repair-minimum.md`, `references/runtime-brief.md`, `references/validation-protocol.md` | `artifact-only`; repair agent writes artifact, controller validates |
| 37 | First finalized write cannot be placeholder | `references/finalized-repair-minimum.md`, `references/runtime-brief.md`, trace summary tests | `Do not write the old draft back as a placeholder`; `Copying the current draft back unchanged and then rewriting is invalid` |
| 38 | No counters/path probes/checkers inside finalized repair | `SKILL.md`, `references/finalized-repair-minimum.md`, `references/runtime-brief.md`, `references/validation-protocol.md` | `do not run check_anlin_violations.py`; `python -c`, `Measure-Object`, `wc`, path probes |
| 39 | Full style-profile remains controller evidence | `SKILL.md`, `references/finalized-repair-minimum.md`, `references/validation-protocol.md`, `references/runtime-layer-map.md` | `full style-profile output remains controller evidence after the artifact is frozen` |
| 40 | Short sincere/micro-hope profile fallback is weak evidence | `SKILL.md`, `references/runtime-layer-map.md`, `references/clean-generation-brief.md` | `Short-genre profile fallback is not strong evidence` |
| 41 | Present-action anchor before memory | `references/clean-generation-brief.md`, `references/runtime-brief.md` | `present-action anchor`; current practical action before memory |
| 42 | Cropped trace definition | `references/clean-generation-brief.md`, `references/runtime-brief.md` | `cropped trace`; less than a full scene |
| 43 | No model-specific runtime branches | README, validation protocol, active runtime docs | `model-specific failures should be generalized` |
| 44 | No local machine paths in runtime docs | README, `SKILL.md`, runtime docs | `<skill-dir>` and `<corpus-dir>`, not user-specific paths |
| 45 | Rhythm scripts are finite repair, not source | `references/finalized-repair-minimum.md`, `references/anlin-collage-source-model.md`, `references/clean-generation-brief.md` | `Do not depend on rebalance_line_rhythm.py`; scripts cannot create first article shape |
| 46 | Old small-sample blind protocol is inactive | `references/validation-protocol.md`, README, judge docs, tests | active readiness uses `8 impostor + 2 placebo`; legacy smaller rounds are historical only |
| 47 | Mixed preflight repair order | `scripts/clean_run_checker.py`, `SKILL.md`, `references/clean-eval-first-draft-minimum.md`, `references/runtime-layer-map.md`, tests | wrapper output only; source/content blockers before `rebalance_line_rhythm.py`; rhythm script is final shape step after last content write |
| 48 | Post-check preflight before checker call 2/2 | `scripts/clean_run_checker.py`, `SKILL.md`, `references/clean-eval-first-draft-minimum.md`, `references/validation-protocol.md`, tests | `CLEAN_RUN_POSTCHECK_PREFLIGHT`; byte-read-only wrapper; protect checker call 2/2 from underbuilt shrinkage or hard shape failure; no long reference reload; explicit source or shape repair |

## Current Assessment

- Total constraints tracked: 51
- Missing owner rows: 0
- Current test expectation: route/information-loss tests should verify the correct owner file or stage, not only that a phrase appears somewhere in all references combined.
- Current target status: not proven. This matrix is architecture evidence only; it is not recognition-rate evidence and must not be used to claim the `<=10%` blind-review target.
- Validation evidence must be refreshed with commands before any completion claim: unit tests, script syntax check, style-profile calibration, strict original-corpus hard gate, runtime portability scan, and active-protocol scan.

## Maintenance Rules

- Do not add fixed numeric line-reference claims; use stable phrases and owner files.
- Do not mention stale transient test failures. If tests fail, report them in the current validation summary, not as permanent matrix text.
- If a concept moves files, update this matrix and the owner-file tests together.
- Historical failed-run details belong in `references/development-log.md`, not this matrix.
- Strategic convergence notes belong in `references/architecture-convergence-plan.md`; keep this matrix focused on route ownership and information-loss checks.

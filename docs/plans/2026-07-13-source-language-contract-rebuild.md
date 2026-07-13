# Layer 0/1 Source-Language Contract Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the ambiguous active “breathing rows” instruction with a punctuation-preserving movement-unit contract that produces scattered Anlin collage prose without turning every sentence into a naked short row or collapsing the article into a short premise summary.

**Architecture:** Keep the bounded protocol boundary already proven by iterations 160–163: severe source repair is source-only, rhythm tooling is a later independent action, and the controller remains the only owner of numeric telemetry. Rebuild only the Layer 0/1 language interface: define a movement unit by semantic continuation plus natural punctuation, define thought-turns as content movement rather than line count, and keep fragment-slate scatter separate from page-shape repair. Do not add hard gates, numeric generation quotas, model branches, or new artifacts inside bounded clean-eval.

**Tech Stack:** Markdown runtime contracts, existing Python `unittest` suite, `clean_run_checker.py`, `check_clean_eval_trace.py`, strict generated-draft checker, style-profile calibration, and the existing Windows controller harness.

---

## Evidence and non-goals

The current evidence is not a checker-only problem:

- iteration-161: valid trace, 722-character prose block;
- iteration-162: valid trace, 521-character naked short-row grid;
- iteration-163: valid trace, first submission already 547 characters/76 bare rows and final 670 characters/90 bare rows;
- all three traces contain only the provider-visible planning warning, with no rhythm-script contamination;
- the 38 originals pass strict non-draft-gate calibration, and representative originals use punctuation-bearing comma-ended rows rather than the generated bare-row surface.

This plan does not:

- start finalized repair, blind rounds, placebo calibration, or recognition-rate reporting;
- loosen `short_line_grid`, `bare_line_grid`, length, or punctuation gates before a corpus comparison proves a false positive;
- add a fragment-count, character-count, line-count, or mandatory-feature recipe;
- add model/provider-specific instructions or background-material quotas;
- make the controller rewrite the bounded artifact.

## Task 1: Freeze the evidence baseline and run a read-only shape audit

**Files:**

- Read: `scripts/clean_run_checker.py`
- Read: `references/clean-eval-first-draft-minimum.md`
- Read: `references/anlin-collage-source-model.md`
- Read: `references/runtime-brief.md`
- Read: `C:\Users\34025\Documents\Codex\anlin-writing-evals\iteration-20260713-161\...`
- Read: `C:\Users\34025\Documents\Codex\anlin-writing-evals\iteration-20260713-162\...`
- Read: `C:\Users\34025\Documents\Codex\anlin-writing-evals\iteration-20260713-163\...`

- [ ] Confirm `main` is clean and at the pushed baseline `639b880` or a later descendant.
- [ ] Compare 38 originals with iterations 161–163 using a read-only diagnostic that reports body characters, non-empty rows, punctuation-bearing row share, bare-row share, mean/stdev row length, and comma-ended row share. Store the diagnostic outside the repository or in a controller-audit directory; do not turn it into a runtime gate.
- [ ] Record the decision boundary: if originals and generated drafts differ mainly by punctuation-bearing movement rather than row count, treat the source-language contract as the primary failure; do not change checker thresholds.

Run:

```powershell
git status --short --branch
git log -5 --oneline --decorate
git diff --check
```

Expected: clean `main`, pushed baseline, and no repository edits from the audit.

## Task 2: Add RED tests for the new active source-language contract

**Files:**

- Modify: `test/test_anlin_tooling.py` near `test_scattered_source_contract_de_linearizes_linear_prompts`

- [ ] Add one test that reads the active owner documents (`SKILL.md`, `references/clean-eval-first-draft-minimum.md`, `references/anlin-collage-source-model.md`, and `references/runtime-brief.md`) and requires these exact concepts in each:

```python
self.assertIn("punctuation-bearing movement units", lowered)
self.assertIn("a line break does not remove punctuation", lowered)
self.assertIn("naked caption rows are not breathing rows", lowered)
self.assertIn("do not split every sentence into its own line", lowered)
```

- [ ] Require the active documents to retain `fragment slate`, `independent thought-turn`, and `day-shaped collage`.
- [ ] Require the active documents not to contain the ambiguous instruction `split multi-turn paragraphs into breathing rows before writing`.
- [ ] Keep the historical `references/standard-diary-source-engine.md` and developer-only `references/clean-generation-brief.md` outside this active-owner assertion unless a separate migration test explicitly names them.

Run:

```powershell
python -m unittest test_anlin_tooling.AnlinToolingTests.test_scattered_source_contract_de_linearizes_linear_prompts
```

Expected: RED because the current active documents do not define punctuation-bearing movement units and still use the ambiguous row-splitting wording.

## Task 3: Rewrite the active collage source model around movement units

**Files:**

- Modify: `references/anlin-collage-source-model.md`

- [ ] Replace the current “breathing rows” paragraph with one canonical contract used by all active owners:

```markdown
### Movement units, not naked rows

A movement unit is a short passage in which an observation, crooked read, and next action remain connected. Keep the natural Chinese punctuation that the thought needs. A line break may expose a continuation or landing, but a line break does not remove punctuation and does not turn every sentence into its own line.

Punctuation-bearing movement units are the source shape. Naked caption rows such as “手机亮了一下 / 狗哥发来消息 / 说下个月结婚” are not breathing rows; they are a checklist surface. Keep a clause attached to the action, reply, object, or thought it completes, and let the next fragment arrive through association, contrast, memory, echo, time jump, self-correction, or a voice-consistent direct jump.
```

- [ ] Define an independent thought-turn semantically: it changes the object, time, memory, joke, social position, or next action. Do not define it by row count or paragraph count.
- [ ] Keep the day-shaped collage rule and the “not a premise summary” rule, but state that completeness comes from developed movement units, not from adding more rows or more prompt facts.
- [ ] Remove wording that tells the generator to “split multi-turn paragraphs into breathing rows before writing.” Replace it with “preserve punctuation-bearing movement units before the first wrapper.”
- [ ] Do not add a numeric corridor, required fragment count, required outside person, or mandatory background packet.

Run the new test from Task 2. Expected: still RED until all active owners are synchronized.

## Task 4: Synchronize the Layer 0/1 active owners without changing the protocol

**Files:**

- Modify: `references/clean-eval-first-draft-minimum.md`
- Modify: `SKILL.md`
- Modify: `references/runtime-brief.md`
- Inspect and, if needed for wording consistency only, modify: `references/clean-generation-brief.md`
- Test: `test/test_anlin_tooling.py`

- [ ] In the first-draft minimum, replace “draft in breathing fragments/rows” with the movement-unit contract. State that the first saved artifact must already contain punctuation-bearing movement and that shape scripts cannot invent it.
- [ ] In `SKILL.md`, keep the proven mode router, marker/cwd order, artifact requirement, source-only severe route, and in-place final rhythm mutation. Replace only the ambiguous row language; do not expose metrics or new repair checklists.
- [ ] In `runtime-brief.md`, keep the same contract for ordinary runtime references and preserve the clean-eval misroute guard.
- [ ] In `clean-generation-brief.md`, update developer/controller wording so it does not reintroduce the removed row-splitting instruction when an agent reads it outside bounded clean-eval.
- [ ] Add one negative example and one positive example to the active first-draft minimum, both generic and unsupported-fact-free:

```markdown
不采用：把一个动作拆成无标点的标题行列表。
采用：让动作、补充判断和下一步保留自然标点，必要时换行，但不把每个句子切成裸行。
```

- [ ] Run the RED→GREEN documentation tests before touching checker logic.

## Task 5: Verify the source-language change without modifying checker thresholds

**Files:**

- Verify only: `scripts/clean_run_checker.py`
- Verify only: `scripts/check_clean_eval_trace.py`
- Verify only: `scripts/check_anlin_violations.py`

- [ ] Confirm `generator_facing_summary` still has these exact routing properties:

  - severe source deficit: source-only action, no rhythm script;
  - non-severe shape action: in-place final mutation, immediate wrapper;
  - no numeric telemetry in generator-facing output;
  - no normal-checker call inside bounded clean-eval.

- [ ] Run:

```powershell
git diff --check
python -c "import pathlib, py_compile; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('scripts').glob('*.py')]; print('py_compile_ok')"
python -m unittest discover -s test -p test_anlin_tooling.py
python scripts\calibrate_style_profile.py "C:\Users\34025\Desktop\Anlin" --profile references\style-profile.json
```

- [ ] Run the 38-file strict original-corpus audit and require `strict_corpus_hard_error_files=[]`.
- [ ] Scan active runtime files for old `3+1`, `--rounds 3`, `placebo-rounds 1`, `subagent-prompts`, `子代理`, local paths, private skill names, and provider/model branches.
- [ ] Commit this source-contract slice separately and push `main` only after all gates pass.

## Task 6: Run one fresh bounded controller experiment

**Files:**

- Create outside the repository: `C:\Users\34025\Documents\Codex\anlin-writing-evals\iteration-164\eval-09-2024-classmate-wedding-bounded-controller-source-language-v2-<model>`
- Copy: the known-good `run_controller.py`
- Create: `.anlin-clean-eval-mode`, `prompt.txt`, and `case-metadata.json`

- [ ] Use a fresh case directory and one available model. Record the model only in case metadata.
- [ ] Require the same tool order: direct marker probe, standalone cwd check, active first-draft references, one initial `draft.md` write, and wrapper-only bounded validation.
- [ ] Do not run finalized repair, normal checker, blind, placebo, or local counters inside the bounded case.
- [ ] After completion, independently verify:

  - controller exit 0, OpenCode exit 0, no timeout, no residual process;
  - three identical draft hashes and state/report hash agreement;
  - trace checker has zero errors and at most the known provider-visible planning warning;
  - no rhythm script before the first wrapper, no script stdout treated as draft content, and no write after a script without rerunning it;
  - first submission has punctuation-bearing movement units rather than all-bare rows;
  - final artifact is not a premise summary or one continuous carrier chain;
  - controller-only hard gate and full style-profile results are collected on a copy outside the bounded state directory.

## Task 7: Decision gate after iteration-164

Use the following mutually exclusive outcomes:

1. **Source contract improved:** first draft and final draft contain punctuation-bearing movement units, independent thought-turns, no all-bare-row grid, and hard/style quality is materially improved. Keep the contract, make only evidence-backed follow-up changes, and do not enter finalized until a bounded quality candidate clears the active gates.
2. **Trace valid but still bare-row:** classify as Layer 0/1 language-interface failure. Stop adding checker locks. Redesign the source interface around a short positive “movement-unit” contract and corpus-grounded examples before another experiment.
3. **Trace error returns:** classify as protocol/interface failure. Revert only the responsible contract change through a new forward fix; do not count the case as quality evidence.
4. **Original-corpus comparison shows the generated surface is ordinary in the originals:** open a separate checker/profile calibration plan. Do not mix calibration with source guidance or change thresholds in the same commit.

The short-term success criterion is not blind readiness. It is one process-valid bounded case whose first and final artifacts are source-quality candidates under the active hard gate and style-profile checkpoint. Until that occurs, `recognition_rate=N/A` and `ready_for_blind_rounds=false` remain unchanged.

## Task 8: Only after a bounded quality candidate

- [ ] Start finalized repair in a fresh external workspace using the artifact-only `repair-brief.txt` contract.
- [ ] Require one complete finalized write, no repair-agent checker/counter/path probes, and controller-only post-write validation.
- [ ] Build the required evidence package incrementally: 15 clean-eval cases, 8 impostor cases, 2 placebo cases, and placebo false-accusation calibration.
- [ ] Do not report recognition rate or readiness until the active protocol package is complete.

## Commit checkpoints

- Contract tests RED→GREEN plus active-owner docs: one commit.
- Full engineering gates plus runtime scans: required before push.
- Fresh bounded evidence: external workspace only; do not commit generated artifacts into the skill repository.
- Any later checker/profile calibration: separate plan and separate commit from source guidance.

## Self-review checklist

- Does the plan fix the source-language ambiguity rather than add a detector? Yes: it replaces row metaphors with punctuation-bearing movement units.
- Does it preserve the fragment-slate/collage goal? Yes: thought-turns remain semantic and independent; no single-scene carrier chain is restored.
- Does it avoid numeric recipes and model-specific branches? Yes.
- Does it preserve the bounded protocol and evidence boundaries? Yes.
- Does every failure path have a classification and stop condition? Yes: source, protocol, or checker/profile calibration are separated.

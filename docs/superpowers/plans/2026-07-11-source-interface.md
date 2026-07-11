# Layer 0/1 Source Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the local/global carrier ambiguity that is producing underbuilt standard clean-eval drafts, then verify the change with a fresh bounded checkpoint without changing checker thresholds or blind-review claims.

**Architecture:** Keep the checker and bounded preflight protocol unchanged. Clarify the source contract in `clean-eval-first-draft-minimum.md` and `standard-diary-source-engine.md`: carrier release is local, while a standard article still needs several distinct functional movements. Use a regression test as the contract boundary before editing the references.

**Tech Stack:** Markdown runtime references, Python `unittest`, PowerShell, existing OpenCode controller scripts.

---

### Task 1: Add the failing source-contract regression test

**Files:**
- Modify: `test/test_anlin_tooling.py` near the existing clean-eval source-reference tests.

- [ ] **Step 1: Add one assertion for the missing local/global distinction**

The test must require a phrase that makes the intended semantics explicit in both source references, and require that the global misreading is rejected. Use the existing `ROOT` path helper and read UTF-8 text like neighboring tests.

- [ ] **Step 2: Run only the new test**

Run:

```powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_source_contract_distinguishes_local_carrier_release_from_article_movement
```

Expected: `FAIL` because the new contract wording is not present yet.

- [ ] **Step 3: Commit the red test**

```powershell
git add test/test_anlin_tooling.py
git commit -m "test: pin local carrier source semantics"
git push origin main
```

### Task 2: Clarify the Layer 0/1 source interface

**Files:**
- Modify: `references/clean-eval-first-draft-minimum.md` in the carrier/source-shape sections.
- Modify: `references/standard-diary-source-engine.md` in the carrier/source-slate sections.
- Modify: `references/development-log.md` with the iteration-151 root-cause record.

- [ ] **Step 1: Replace ambiguous global-transfer wording**

State that releasing one carrier prevents repeated proof by that carrier, while the article must still move through several distinct action transfers. Do not add a new numeric hard gate or prop quota.

- [ ] **Step 2: Add the positive functional source slate**

Describe the standard-diary sequence as friction, prompt pressure, decision/reply movement, refusal-coupled non-screen consequence, medium change, and unfinished practical tail. Mark these as functions, not required scenes or facts.

- [ ] **Step 3: Remove only contradictory duplicates**

Do not rewrite the whole reference set. Preserve existing public-hinge and social-decline safeguards, but remove repeated sentences that can be read as “one transfer for the whole article.”

- [ ] **Step 4: Run the red test and the focused tooling suite**

Run:

```powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_source_contract_distinguishes_local_carrier_release_from_article_movement
python -m unittest discover -s test -p test_anlin_tooling.py
```

Expected: the new test passes and the full suite reports zero failures.

- [ ] **Step 5: Commit and push the source-contract change**

```powershell
git add references/clean-eval-first-draft-minimum.md references/standard-diary-source-engine.md references/development-log.md test/test_anlin_tooling.py
git commit -m "Clarify article-level movement beyond carrier release"
git push origin main
```

### Task 3: Run a fresh bounded generation checkpoint

**Files/External state:**
- Create: `C:\Users\34025\Documents\Codex\anlin-writing-evals\iteration-20260711-152\...`
- Reuse only the controller harness from iteration-151 or 147; never reuse an old case directory.

- [ ] **Step 1: Run controller executable tests**

Run the copied controller test before starting the model. Expected: pass.

- [ ] **Step 2: Run one available rotated model**

Prefer a model/provider not used for the immediately preceding attempt. Record unavailable/provider errors as unavailable, never as quality evidence.

- [ ] **Step 3: Validate bounded checkpoint invariants**

Require both exits zero, no timeout, no residual processes, stable three-sample hash, hash agreement with report/state, `stopped=true`, an allowed stop reason, and bounded calls within the controller budget. Audit the trace separately. Do not run direct normal checker calls inside a stopped bounded case.

- [ ] **Step 4: Classify the result**

If no artifact or the artifact is still underbuilt, record source-generation failure and stop before finalized. If the artifact is a meaningful bounded draft, prepare a fresh finalized sibling and continue to Task 4.

### Task 4: Finalized repair only for a valid bounded input

**Files/External state:**
- Create: a new `finalized/` sibling under the valid iteration-152 case.
- Create: a dedicated finalized controller clone under `_controller`.

- [ ] **Step 1: Generate a fresh `repair-brief.txt`**

Use `prepare_finalized_repair_brief.py` against the copied bounded draft. Verify the route and read contract before model launch.

- [ ] **Step 2: Run exactly one artifact-only repair attempt**

Expose only `draft.md` and `repair-brief.txt` for a valid compact brief. Require one complete write, no checker/source/test/threshold/path reads, and immediate stop.

- [ ] **Step 3: Validate frozen artifact**

Check hash change/stability, trace cleanliness, strict hard gate, and full style-profile checkpoint. Record fail/review honestly; do not keep editing in the same attempt.

### Task 5: Full verification and handoff

- [ ] **Step 1: Run required repository checks**

Run `git diff --check`, `py_compile`, full unittest, original strict hard gate over all 38 files, original style calibration, and runtime portability scans.

- [ ] **Step 2: Inspect git diff and status**

Confirm only task-related files changed and `main` is clean.

- [ ] **Step 3: Commit/push any remaining task changes**

Use a focused commit and push `main` only after all checks pass.

- [ ] **Step 4: Report evidence boundaries**

Report engineering facts, current evidence counts, whether blind rounds are ready, whether recognition rate can be reported, and the next missing evidence. Never infer readiness from a single successful case.

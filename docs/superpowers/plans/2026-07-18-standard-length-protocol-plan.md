# Standard Length Protocol Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Implement the approved B contract so checker, bounded controller, finalized repair routing, and formal blind preparation share 650/850/900 semantics without turning length into a generation quota.

**Architecture:** scripts/check_anlin_violations.py owns the semantic constants and exposes one full-standard boundary to controller consumers. clean_run_checker.py separates explicit blocking findings from source advisories and records controller-only length evidence. prepare_finalized_repair_brief.py, summarize_dev_checkpoints.py, prepare_blind_test.py, and run_blind_test.py consume the same boundary while keeping short-protocol C out of this change.

**Tech Stack:** Python 3, unittest, JSON controller manifests, Markdown protocol references, existing PowerShell verification commands.

---

## Scope and safety gates

This plan implements only the approved B contract. It does not implement matched-short-standard, modify the fragment/collage source model, start iteration-166, or run finalized/blind/placebo evaluation before the code changes are committed and the full verification matrix passes.

Every code task follows RED -> failing targeted test -> minimal implementation -> targeted test -> commit. Do not change a threshold without first adding the boundary regression that proves the intended behavior. Do not expose 650, 850, 900, 950, or 0.25 in generator-facing preflight text.

## File map

- Modify scripts/check_anlin_violations.py: define the four semantic length constants, migrate generated-draft length and full-article shape activation, and remove any 950-derived blocking path.
- Modify scripts/clean_run_checker.py: consume the renamed full-article constant, record controller-only length evidence, make 850 the preflight boundary, and keep advisories out of blocking decisions.
- Modify scripts/prepare_finalized_repair_brief.py: route severe/underbuilt/normal source repair at 650 and 850, and stop using below-900 as a repair reason.
- Modify scripts/summarize_dev_checkpoints.py: display the clean-run length band and preferred-target flag without changing bounded/finalized status semantics.
- Modify scripts/prepare_blind_test.py: use the 850 full-standard eligibility boundary, change short_form to <850, enforce hard length filtering before genre selection, and record formal matching eligibility in mappings.
- Modify scripts/run_blind_test.py: use the 0.25 default, require explicit genre matching for formal manifests, and record the same policy at controller-manifest level.
- Modify test/test_anlin_tooling.py: migrate stale 900/950 assertions, add boundary and regression fixtures, and cover manifest fail-closed behavior.
- Modify references/validation-protocol.md: document the B contract, strict matching, and the unchanged C boundary.
- Modify README.md: update the formal blind command and explain that 900 is preferred while 850 is the eligibility boundary.
- Modify references/runtime-layer-map.md and references/development-log.md: record ownership and evidence after implementation, without putting numeric quotas into generator-facing runtime guidance.

## Task 1: Define shared length semantics and migrate checker gates

Files:
- Modify scripts/check_anlin_violations.py around constants at 1614, generated length at 3654, formal shape at 4364, and comma/period gates around 4788.
- Test test/test_anlin_tooling.py near existing generated-draft length and standard shape tests at 9670 and 11484.

- [ ] Step 1: Add failing semantic-boundary tests.

Add a test helper beside the existing checker subprocess helpers that writes a standard fixture with an exact body count and invokes:

~~~python
result = subprocess.run(
    [sys.executable, str(CHECKER), str(draft), "--json", "--strict", "--draft-gate"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    check=False,
)
findings = json.loads(result.stdout)
errors = [item["rule"] for item in findings if item["severity"] == "error"]
~~~

Cover all six boundaries with explicit expectations:

~~~python
expected_length_error = {
    649: True,
    650: True,
    849: True,
    850: False,
    899: False,
    900: False,
}
for body_chars, should_error in expected_length_error.items():
    with self.subTest(body_chars=body_chars):
        errors = run_standard_draft_gate_for_body_chars(body_chars)
        has_length_error = any("标准日寄完整文章篇幅" in rule for rule in errors)
        self.assertEqual(has_length_error, should_error, errors)
~~~

Add a separate 850+ fixture with an independently compressed prose or period-grid shape. Assert it still emits its shape error after the length error disappears.

- [ ] Step 2: Run the focused tests and confirm RED.

Run:

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_checker_draft_gate_uses_full_article_850_boundary
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_checker_850_shape_errors_remain_independent_of_length
~~~

Expected result: both new tests fail against STANDARD_DIARY_DRAFT_SAFE_MIN_CHARS = 900; stale tests may also report the old rule text.

- [ ] Step 3: Replace the constants with one semantic vocabulary.

At scripts/check_anlin_violations.py:1614, replace the generated-draft constant block with:

~~~python
STANDARD_DIARY_FORMAL_MIN_CHARS = 650
STANDARD_DIARY_ATTEMPT_MIN_CHARS = 300
STANDARD_DIARY_ATTEMPT_MIN_LINES = 12
STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS = 850
STANDARD_DIARY_PREFERRED_TARGET_MIN_CHARS = 900
STANDARD_DIARY_DRAFT_OVERFULL_CHARS = 1350
~~~

Update every active consumer in this file in one change. Use STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS for the generated-draft buffer finding and for full-article shape gates whose only current activation is >=900. Keep detectors with their own evidence minimums unchanged when the source code shows that the minimum is independent of full-article eligibility. Do not leave a compatibility alias in active code after the change.

Remove the body_chars < 950 with source_shape_weak concept from the checker-facing contract. No new checker finding is needed for preferred_target_shortfall; the controller records it separately.

- [ ] Step 4: Migrate stale checker tests instead of weakening them.

Update tests that assert body_chinese_chars=899 < 900 (and the equivalent 649/650 fixtures) as a blocking length reason to assert <850 for 649/650/849 cases and no length error for 850+. Keep tests for period grid, comma density, line shape, social-decline overgrowth, and protocol violations unchanged except where they were accidentally gated by the old 900 constant.

- [ ] Step 5: Run the checker-focused regression.

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_checker_draft_gate_uses_full_article_850_boundary
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_checker_850_shape_errors_remain_independent_of_length
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_checker_draft_gate_rejects_overfull_standard_article
~~~

Expected result: all pass; 850+ fixtures can still fail for independent shape errors, and overfull behavior remains unchanged.

- [ ] Step 6: Commit the checker slice.

~~~powershell
git add scripts/check_anlin_violations.py test/test_anlin_tooling.py
git commit -m "fix: align standard checker boundary at 850"
~~~

## Task 2: Make clean-run preflight use 850 and isolate advisories

Files:
- Modify scripts/clean_run_checker.py around generator_facing_summary at 132, preflight_messages at 806, guidance at 1143, post-check routing at 1628, and state initialization at 1791.
- Test test/test_anlin_tooling.py near generator-facing tests at 2731 and clean-run preflight tests at 3026.

- [ ] Step 1: Add failing controller boundary tests.

Add direct tests for the qualitative interface:

~~~python
labels, action = generator_facing_summary(
    ["body_chinese_chars=894 < 950 with source_shape_weak"]
)
self.assertNotIn("source_shape=underbuilt", labels)
self.assertNotIn("whole_source_rebuild", action)

labels, action = generator_facing_summary(
    ["body_chinese_chars=849 < 850", "paragraph_engine=weak"]
)
self.assertIn("source_shape=underbuilt", labels)
self.assertIn("replace_one_broken_fragment_or_relation_in_place", action)
~~~

Add a preflight fixture asserting that an 894-character, shape-ready draft reaches CLEAN_RUN_NOTE/checker call 1, while an 875-character draft with an explicit medium shape finding still stops for that shape finding. Add a fixture containing only connectors=[] < 3, paragraph_engine=weak, and rough_self_damage=missing; assert blocking_preflight_messages returns an empty list.

- [ ] Step 2: Run the focused controller tests and confirm RED.

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_generator_facing_summary_uses_850_boundary
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_clean_run_advisories_do_not_block
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_clean_run_checker_preflight_allows_850s_when_shape_is_ready
~~~

Expected result: failures show the current <950 and <900 routing and the stale 950 composite message.

- [ ] Step 3: Add a controller-only length evidence helper.

In clean_run_checker.py add a pure helper beside the existing chinese_len consumers:

~~~python
def standard_length_evidence(draft: Path) -> dict[str, Any]:
    text = draft.read_text(encoding="utf-8")
    title, content_lines = split_title_and_content_lines(text.splitlines())
    if detect_style(text) != "standard":
        return {}
    body = "\n".join(line for line in content_lines if line.strip() and not line.startswith("<!--"))
    body_chars = chinese_len(body)
    return {
        "standard_body_chars": body_chars,
        "preferred_target_shortfall": body_chars < STANDARD_DIARY_PREFERRED_TARGET_MIN_CHARS,
    }
~~~

Before the first snapshot in main, merge this dictionary into state. The values stay in .anlin-clean-run-state.json and controller reports; never interpolate them into generator-facing messages.

- [ ] Step 4: Migrate preflight and guidance thresholds.

Make these exact changes:

~~~python
# generator_facing_summary
underbuilt = (
    (body_chars is not None and body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS)
    or any(message.startswith("body_lines=") and "<" in message for message in messages)
)
~~~

In preflight_messages, change the standard length message to <850; change period-row and prose-block activation that currently uses body_chars >= 900 to body_chars >= STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS; and remove the source_shape_weak-derived <950 with source_shape_weak message. Keep explicit medium_short_line_grid as a shape message when its own line-shape evidence is present.

In build_preflight_guidance, standard_underbuilt_length and short_of_safe_mass become <850 checks. In post_checker_blocking_messages, remove the body_chars <950 guard around medium_short_line_grid; the message is already emitted only when its explicit line-shape predicate holds. Do not add connector/engine/rough prefixes to the blocking list.

Update comments and qualitative labels from near-900 or safe mass to full-article boundary language. Do not print any numeric preferred target to the generator.

- [ ] Step 5: Run controller tests and inspect state evidence.

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_generator_facing_summary_uses_850_boundary
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_clean_run_advisories_do_not_block
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_clean_run_checker_preflight_allows_850s_when_shape_is_ready
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_clean_run_checker_preflight_blocks_standard_period_row_grid
~~~

Expected result: 894 shape-ready reaches checker call 1 with standard_body_chars=894 and preferred_target_shortfall=true in state; 875 remains blocked only by explicit shape/source findings; advisory-only messages do not stop the wrapper.

- [ ] Step 6: Commit the clean-run slice.

~~~powershell
git add scripts/clean_run_checker.py test/test_anlin_tooling.py
git commit -m "fix: separate clean-run advisories from length gate"
~~~

## Task 3: Synchronize finalized repair routing and checkpoint summaries

Files:
- Modify scripts/prepare_finalized_repair_brief.py around hard_gate_primary_action at 177 and compact_source_focus at 228.
- Modify scripts/summarize_dev_checkpoints.py around GateSummary at 114, summarize_gate at 596, and format_gate at 1085.
- Test test/test_anlin_tooling.py near finalized routing tests at 10559 and 13299.

- [ ] Step 1: Add failing route and report tests.

Extend the existing hard_gate_primary_action table to assert:

~~~python
route_for(649) == "rebuild_severely_underbuilt_fragment"
route_for(650) == "replace_underbuilt_fragment"
route_for(849) == "replace_underbuilt_fragment"
route_for(850, weak_source_error=True) == "preserve_boundary_mass_replace_weak_fragment"
route_for(900, weak_source_error=True) == "preserve_boundary_mass_replace_weak_fragment"
~~~

The 850 and 900 cases must not contain below 900, restore mass, or independent packet/additional scene instructions. Add a summarize_gate test whose clean_state includes standard_body_chars=894 and preferred_target_shortfall=true; assert both fields appear in format_gate output without changing status.

- [ ] Step 2: Run focused tests and confirm RED.

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_finalized_repair_brief_routes_standard_mass_before_social_family
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_summarize_gate_reports_length_evidence_without_changing_status
~~~

Expected result: current 850-899 inputs route through the old <900 mass branch and GateSummary has no length fields.

- [ ] Step 3: Update finalized routing.

In hard_gate_primary_action, use STANDARD_DIARY_FORMAL_MIN_CHARS and STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS imported from the checker. Keep severe <650 and underbuilt 650-849; route >=850 weak-source hard errors through the weak-fragment action without an upper 950 bound. Leave overfull, social-decline, period-grid, and generic hard-error priority ordering intact.

Update compact_source_focus only where it names the old mass route. Preserve the one-source-focus, one-write artifact contract exactly.

- [ ] Step 4: Add length fields to controller summaries.

Extend GateSummary with:

~~~python
standard_body_chars: int | None = None
preferred_target_shortfall: bool | None = None
~~~

In summarize_gate, read the two optional keys from clean_state; in format_gate, print both fields. Do not use them in the pass/fail decision.

- [ ] Step 5: Run route and summary tests.

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_finalized_repair_brief_routes_standard_mass_before_social_family
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_summarize_gate_reports_length_evidence_without_changing_status
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_prepare_finalized_repair_brief_hides_metric_details
~~~

Expected result: 850+ is never routed to mass repair solely because it is below 900; summary status remains governed by hard errors, trace, and profile state.

- [ ] Step 6: Commit the finalized/summary slice.

~~~powershell
git add scripts/prepare_finalized_repair_brief.py scripts/summarize_dev_checkpoints.py test/test_anlin_tooling.py
git commit -m "fix: align finalized repair with full article boundary"
~~~

## Task 4: Enforce formal blind matching and fail-closed eligibility

Files:
- Modify scripts/prepare_blind_test.py around ArticleFeatures at 35, article_features at 116, match_score at 148, pick_corpus_records at 341, and prepare_blind_test at 526.
- Modify scripts/run_blind_test.py around create_round at 53 and CLI/manifest at 107.
- Test test/test_anlin_tooling.py near blind preparation tests at 11719 and run manifest tests at 14984.

- [ ] Step 1: Add failing selection and manifest tests.

Use a temporary corpus with exact-genre records both inside and outside a tolerance. Assert the outside record is never returned:

~~~python
records = pick_corpus_records(
    corpus,
    num_samples=2,
    draft_path=draft,
    target_features=article_features(draft_text),
    length_tolerance=0.25,
    match_genre="standard",
)
self.assertTrue(all(item.match["within_length_tolerance"] for item in records))
~~~

Add a corpus with fewer than num_samples exact-genre records inside 25%; assert prepare_blind_test raises ValueError rather than backfilling a wrong genre or out-of-range length. Add manifest assertions for formal_length_match_eligible false when match_genre none or length_tolerance 0, and true for match_genre auto with length_tolerance 0.25 and sufficient records. Assert body_chars and complete-article chars remain separate fields.

- [ ] Step 2: Run focused blind tests and confirm RED.

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_blind_matching_filters_length_before_genre_selection
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_blind_matching_fails_closed_when_exact_pool_is_short
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_run_blind_manifest_records_formal_length_eligibility
~~~

Expected result: the current exact-genre path selects outside-tolerance records or backfills them, and the current manifest has no formal eligibility field.

- [ ] Step 3: Align article feature and defaults.

Import STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS into prepare_blind_test.py. Add body_chars to ArticleFeatures, populate it from the already-computed body_chars local, and keep chars as complete-article Chinese characters. Change only the short-form length part of article_features:

~~~python
short_form = body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS or len(body_lines) < 40
~~~

Change defaults in both prepare_blind_test.py and run_blind_test.py from 0.65 to 0.25. Keep --length-tolerance 0 as explicit diagnostic mode. Do not change fragment_chars or min_fragment_chars semantics.

- [ ] Step 4: Filter before scoring and make formal eligibility explicit.

In pick_corpus_records, after features and match metadata are built, construct:

~~~python
length_matched = [
    record for record in records
    if length_tolerance <= 0 or record.match["within_length_tolerance"]
]
if target_features and length_tolerance > 0 and len(length_matched) < num_samples:
    raise ValueError(
        f"Corpus contains {len(length_matched)} length-matched file(s), but {num_samples} were requested."
    )
records = length_matched if target_features and length_tolerance > 0 else records
~~~

Then select exact genre only from records; do not use the existing non-exact backfill branch when a target genre was explicitly requested. Keep match_genre=none as diagnostic length-only matching when a positive tolerance is supplied, but mark it non-formal.

In prepare_blind_test calculate:

~~~python
formal_length_match_eligible = bool(
    target_features
    and match_genre != "none"
    and length_tolerance > 0
    and target_features.chars > 0
    and (
        target_features.genre != "standard"
        or target_features.body_chars >= STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS
    )
)
~~~

Return or write this policy in controller-visible mapping/manifest metadata. For standard targets, formal eligibility therefore requires body_chars >=850; non-standard genres retain their existing genre-specific matched evaluation path. Placebo uses the same hidden anchor and eligibility calculation but has no draft sample.

- [ ] Step 5: Propagate policy through run_blind_test.py.

Add formal_length_match_eligible, length_match_policy, and full_standard_min_chars to controller-manifest.json. Before creating rounds, normalize the draft with strip_draft, compute article_features, resolve match_genre auto, and reject only when the resolved genre is standard and target_features.body_chars < STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS. Set length_match_policy to exact-genre-hard-filter only when the formal predicate is true; otherwise use diagnostic-not-formal. Do not silently infer a short protocol.

Update the default formal command in tests and docs to pass --match-genre auto --length-tolerance 0.25. Keep existing 1.0 tests as diagnostic fixtures and assert their manifest is non-formal rather than removing their coverage.

- [ ] Step 6: Run blind-selection tests.

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_blind_matching_filters_length_before_genre_selection
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_blind_matching_fails_closed_when_exact_pool_is_short
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_run_blind_manifest_records_formal_length_eligibility
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_run_blind_test_supports_multiple_placebo_rounds
~~~

Expected result: exact genre and tolerance are hard eligibility filters, placebo uses the same anchor, and diagnostic manifests cannot be mistaken for formal recognition-rate evidence.

- [ ] Step 7: Commit the blind slice.

~~~powershell
git add scripts/prepare_blind_test.py scripts/run_blind_test.py test/test_anlin_tooling.py
git commit -m "fix: enforce formal blind length matching"
~~~

## Task 5: Update protocol documentation and development facts

Files:
- Modify references/validation-protocol.md around formal commands, finalized pass gate, and blind design.
- Modify README.md around controller validation commands.
- Modify references/runtime-layer-map.md in controller ownership.
- Append one dated entry to references/development-log.md.
- Test test/test_anlin_tooling.py in the existing active-runtime/protocol scan tests.

- [ ] Step 1: Add failing documentation-contract assertions.

Add assertions that active validation docs contain the exact B statements:

~~~python
self.assertIn("850", validation)
self.assertIn("900-1100", validation)
self.assertIn("650-849", validation)
self.assertIn("0.25", validation)
self.assertIn("fail closed", validation.lower())
self.assertNotIn("3 impostor + 1 placebo", validation)
self.assertNotIn("--rounds 3", validation)
~~~

Add a runtime portability assertion that SKILL.md, references/runtime-brief.md, and references/clean-generation-brief.md do not contain the new numeric controller fields or user-local paths.

- [ ] Step 2: Run documentation RED tests.

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_validation_protocol_documents_current_formal_matching_contract
~~~

Expected result: the test fails because current docs still describe nearest backfill and do not name the 0.25 hard filter/formal eligibility field.

- [ ] Step 3: Update active documentation.

Change validation-protocol.md to state:
- 850 is the ordinary full-standard eligibility boundary;
- 900-1100 is a preferred development target, not a hard generation quota;
- 650-849 is excluded from formal full-standard packages until C exists;
- exact genre plus positive 0.25 hard length filtering is required for formal packages;
- insufficient matched originals fail closed;
- placebo and impostor rounds use the same hidden anchor and matching policy;
- no recognition rate is reported before 8 impostor + 2 placebo plus false-accusation calibration.

Update README commands to include --match-genre auto --length-tolerance 0.25 and keep documentation GitHub-user-facing. Update runtime-layer-map.md with controller ownership only; do not put the numeric policy in generator-facing runtime references. Append evidence, limitations, and commit boundary to development-log.md without presenting old artifact results as success.

- [ ] Step 4: Run documentation and portability scans.

~~~powershell
python -m unittest test.test_anlin_tooling.AnlinToolingTests.test_validation_protocol_documents_current_formal_matching_contract
rg -n "3 impostor \+ 1 placebo|--rounds 3|placebo-rounds 1|subagent-prompts|子代理" SKILL.md references README.md
rg -n "C:\\Users|private skill|gateway/|deepseek|mimo|minimax|longcat|gpt-" SKILL.md references\runtime-*.md references\clean-*.md
~~~

Expected result: the first command passes; the legacy scan returns no active-runtime matches; the portability scan returns no forbidden runtime dependency. Historical development log entries may contain development facts and are excluded from the active-runtime scan by design.

- [ ] Step 5: Commit the documentation slice.

~~~powershell
git add references/validation-protocol.md README.md references/runtime-layer-map.md references/development-log.md test/test_anlin_tooling.py
git commit -m "docs: document formal 850 length protocol"
~~~

## Task 6: Full verification, independent review, and fresh bounded case

Files:
- No new runtime files. Use committed code and an external evaluation workspace outside the skill directory.

- [ ] Step 1: Run the repository verification baseline.

Run from C:\Users\34025\.config\opencode\skills\anlin-writing:

~~~powershell
git diff --check
python -c "import pathlib, py_compile; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('scripts').glob('*.py')]; print('py_compile_ok')"
python -m unittest discover -s test -p test_anlin_tooling.py
python scripts\calibrate_style_profile.py "C:\Users\34025\Desktop\Anlin" --profile references\style-profile.json
~~~

Expected result: py_compile_ok, the full unittest suite has zero failures, and style calibration reports no calibration hard errors.

- [ ] Step 2: Run 38-file normal/strict original regression.

Run this exact read-only corpus regression from the repository root, with ANLIN_CORPUS_DIR pointing at the 38 originals:

~~~powershell
@'
import json, os, subprocess, sys
from pathlib import Path
corpus = Path(os.environ["ANLIN_CORPUS_DIR"])
checker = Path("scripts/check_anlin_violations.py").resolve()
for mode in ("normal", "strict"):
    hard_error_files, nonzero_files = [], []
    for draft in sorted(corpus.glob("*.md")):
        command = [sys.executable, str(checker), str(draft), "--json"]
        if mode == "strict":
            command.append("--strict")
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
        findings = json.loads(result.stdout)
        if any(item.get("severity") == "error" for item in findings):
            hard_error_files.append(draft.name)
        if result.returncode != 0:
            nonzero_files.append(draft.name)
    print(json.dumps({"mode": mode, "hard_error_files": hard_error_files, "nonzero_files": nonzero_files}, ensure_ascii=False))
'@ | python -
~~~

Expected result for both modes: hard_error_files=[] and nonzero_files=[]. Do not use --draft-gate for original calibration.

- [ ] Step 3: Run active protocol and portability scans.

Scan active runtime docs for the retired 3+1 protocol, subagent prompt compatibility, local paths, private skills, and model/provider branches. Scan prepare_blind_test.py and run_blind_test.py for the formal fields and confirm no model name is used to select a policy. Commit only if every scan is clean.

- [ ] Step 4: Independently review the diff and test anchors.

Review each commit against docs/superpowers/specs/2026-07-14-standard-length-protocol-design.md. Verify:
- no 900/950 literal remains as an active full-standard blocking boundary;
- no advisory becomes blocking through a derived composite;
- 850+ shape errors remain independently testable;
- formal blind manifests fail closed when genre/tolerance conditions are absent;
- C is not implemented implicitly;
- runtime source guidance does not expose controller numbers.

Run:

~~~powershell
git log --oneline --decorate -8
git diff origin/main...HEAD --stat
git status --short --branch
~~~

- [ ] Step 5: Push the validated implementation.

~~~powershell
git push origin main
~~~

Record the pushed commit range and keep main as the only local branch.

- [ ] Step 6: Create a fresh external bounded case only after the push.

Create a new directory such as C:\Users\34025\Documents\Codex\anlin-writing-evals\iteration-20260718-166-unique-case without reusing 153-165 directories. Use the existing controller harness to generate one standard realistic-prompt case under the new active skill commit. Preserve controller-run.json, opencode-output.jsonl and stderr, .anlin-clean-run-state.json, draft.md, first-submission and bounded-final snapshots, and model/provider metadata outside runtime skill files.

Run trace audit, independent SHA256 stability, strict hard gate, full style profile, and controller summary. Classify the result as process-valid/quality-valid, process-valid/quality-invalid, or protocol-invalid. Do not start finalized repair from a bounded artifact that is not a quality candidate.

- [ ] Step 7: Stop at the evidence boundary and report honestly.

If the fresh bounded case passes, prepare but do not silently execute finalized repair until the artifact and trace are independently reviewed. If it fails, read the complete article and classify the root cause as source guidance, repair interface, checker false positive, or protocol mismatch; do not add a detector without that classification.

Until 15 clean-eval cases, 8 impostor rounds, 2 placebo rounds, and placebo false-accusation calibration all exist with valid manifests, report:

~~~text
ready_for_blind_rounds: false
recognition_rate: N/A
~~~

## Plan self-review

- Spec coverage: Tasks 1-2 cover shared constants, 850 shape activation, advisory isolation, and controller-only preferred-target evidence. Task 3 covers finalized repair and summary. Task 4 covers exact-genre hard matching, 0.25 tolerance, formal eligibility, placebo anchor reuse, and fail-closed behavior. Task 5 covers protocol/runtime documentation. Task 6 covers repository, corpus, portability, push, and fresh bounded evidence gates. C remains explicitly deferred.
- Placeholder scan: No task contains an unfinished placeholder marker or unspecified edge-case instruction. Every code change names the file/function area, RED test, implementation rule, command, and expected result.
- Interface consistency: The plan uses STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS, STANDARD_DIARY_PREFERRED_TARGET_MIN_CHARS, standard_length_evidence, standard_body_chars, preferred_target_shortfall, and formal_length_match_eligible consistently across tasks. short_form remains the existing field with its length threshold moved to 850.
- Scope check: The checker, controller, finalized summary, and blind matcher form one protocol contract and are intentionally kept in one plan. Fragment source guidance and C are outside this plan.

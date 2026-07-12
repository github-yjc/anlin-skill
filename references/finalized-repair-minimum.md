# Finalized Repair Minimum

Use this file only when a controller or user explicitly starts a finalized repair from a copied bounded draft in a `finalized/` directory and the compact `repair-brief.txt` is missing, invalid, or unavailable. Do not use this file for `repair_mode: hard_pass_review_in_place` or `repair_mode: source_rewrite_compact`; those briefs are self-contained and must be followed without loading this fallback.

## Artifact Contract

- Work only on the copied `finalized/draft.md`.
- Read `draft.md` and `repair-brief.txt` when it exists; do not search for hidden diagnostics or reconstruct a checklist.
- The contract is atomic: first write to `draft.md` must be the final complete revision. Do not write the old draft back as a placeholder, print a better article only to the terminal, or perform a second write.
- After the single write, stop. If a chat response is required, output only `artifact_written`.
- Only a schema-valid controller result with return code `1` means not passed. Invalid output, tool failure, or another unexpected return code is unavailable, not quality evidence.

## Read and Tool Boundary

During the repair attempt, do not run `check_anlin_violations.py`, `check_style_profile.py`, `clean_run_checker.py`, `prepare_finalized_repair_brief.py`, local counters, `python -c`, `Measure-Object`, `wc`, path probes, source/test/threshold searches, log searches, or controller helpers. Do not rediscover the skill directory or list sibling references. The controller validates the frozen artifact after the write.

## Source Decision

Read the current article as a fragment slate. Identify the earliest broken relation:

- a prompt surface is repeated as an inventory;
- a fragment is only decorative texture and never changes thought or action;
- a memory or old record explains the present too neatly;
- a witness is only a camera and does not alter the narrator's next move;
- a refusal is overgrown into chronology, crowd commentary, or etiquette settlement;
- a local rhythm surface is a prose block, equal short rows, a period grid, or a comma carpet.

Replace that relation once inside the existing article. A causal consequence is allowed when the draft earns it, but it is not a universal engine. A memory, joke, echo, contrast, time jump, self-correction, or direct voice jump may be the correct repair. Do not add a new scene, witness, route, message chain, background packet, or practical tail merely because a diagnostic names one.

Preserve the selected genre and useful facts. Do not invent unsupported city, office, game, family, relationship, or chronology details. Do not turn a refusal into a multi-day wedding plot; if the draft already earns a local reply, route, payment, body, door, or social consequence, keep it local and unfinished.

## Shape Review Before the Write

The repaired artifact must remain a complete titled article whose line breaks follow thought, speech, memory, body, object, or action. Do not normalize every row to the same punctuation, turn every fragment into a caption, or merge the whole page into one comma chain. Preserve functional mass and working returns, but do not use a universal character, line, cluster, or ending target.

If the brief names a pure shape issue, change only the named local relation and do not add material. If it names a source issue, change the source relation first; do not let a rhythm script or punctuation change invent the missing movement.

If n-gram reuse is too low or uniqueness is too high, preserve one plain action or object phrase that genuinely recurs; do not synonym-scrub repeated words. If repetition is too high or templates repeat mechanically, cut one repeated packet and replace its function inside the existing fragment slate.

## Atomic Write

Before writing, decide the complete replacement privately. Write the entire article to `draft.md` in one operation. Do not patch after writing, validate locally, count rows, inspect thresholds, or explain an alternate version. The controller owns strict hard-gate, style-profile, trace, and artifact validation after the write.

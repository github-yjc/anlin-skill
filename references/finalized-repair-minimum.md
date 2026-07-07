# Finalized Repair Minimum

Use this file only when a controller or user explicitly starts a finalized repair checkpoint from a copied bounded draft in a `finalized/` directory. It is the generator-facing minimum path. Do not load `validation-protocol.md`, `development-log.md`, full style-profile reports, checker source, tests, or hidden thresholds while repairing.

## Contract

- Work only on the copied `finalized/draft.md`.
- Freeze the selected genre before editing and pass it to every gate.
- A repaired article exists only after the complete article is written back to `draft.md`.
- A nonzero `--strict --repair-brief` exit usually means not passed, not a broken tool.
- Do not print a proposed final article to the terminal and keep thinking.
- Do not tune ratios one by one. Use the brief to choose one source-level rewrite.
- Do not rediscover this skill by globbing, listing parent skill directories, or searching sibling skills. Use the already-triggered skill path as `<skill-dir>`. If that path is unavailable, stop as unresolved rather than inspecting checker source, tests, hidden thresholds, or old logs.
- Do not use TODO tools, plans, or long diagnostic narration as the repair artifact. The next useful action after a not-pass brief is reading the current `draft.md`, rewriting the whole article from one source action, and writing it back to `draft.md`.
- In formal finalized checkpoints, this file is not an open-ended ordinary-user repair loop. The repair agent gets one complete source rewrite after the not-pass brief, then one hard-gate plus repair-brief rerun. If the result still does not pass, leave the best persisted `draft.md` and stop as unresolved controller evidence.

## Gate Order

From inside the `finalized/` directory, run the gates exactly through Python. Do not start with a plain strict checker and call that a pass.

Run the hard gate first:

```powershell
python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre <selected-genre>
```

Then run the generator-facing style gate:

```powershell
python <skill-dir>/scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre <selected-genre>
```

After the artifact is frozen, the controller may run `check_style_profile.py` again without `--repair-brief` for the full report. The repair agent should not use that full report as its writing interface.

If the repair brief returns nonzero, shows `formal_gate: not_pass`, or shows `checkpoint_pass: false`, treat that as normal repair input. Do not open the full profile report, do not calculate thresholds, and do not continue discussing findings. Read `draft.md`, apply one primary source rewrite, write the complete article back to `draft.md`, then rerun the two gates once. After that rerun, do not make a second metric-shaped edit in the same finalized attempt.

## Repair Choice

If the hard gate has errors, fix the source function that caused the error and write a complete `draft.md`. Do not defend the draft or argue with the checker.

If the hard gate is clean but the repair brief says `formal_gate: not_pass`, choose exactly one source rewrite before the next validation:

- `punctuation` or `line_rhythm`: rebuild a few breathing clusters from action, reply, payment, door, object, or body movement. Add short drops only when an action lands badly. Do not globally merge rows into comma chains and do not split the draft into tiny rows.
- `connectors`: change what happens next so a turn is needed: failed reply, payment handoff, body interruption, route/object change, or another person's plain line. Do not paste connector words.
- `texture` or `ngram_texture`: delete one repeated body, screen, room, money, route, food, or object packet. Replace its function with a social or practical consequence that changes reply, payment, route, room position, body state, or next action.
- `structure` or `cognitive_mechanism`: cut prompt echoes, decorative proof details, and explicit cognition. Let a concrete object lead to a crooked read, a reality puncture, a defensive recovery, and a practical exit through action rather than explanation.

When multiple families appear, do not make one patch per family. Use the brief's primary source rewrite as the top action. In social-decline drafts, prefer rebuilding the refusal aftermath and rhythm together: remove one room/object proof packet, make the post-refusal response or payment/route/body problem change a later action, and rewrite the visible body as breathing clusters. That source move can address punctuation, line rhythm, connectors, texture, and structure at once.

If a social-decline repair has already gained a valid low-status/public hinge, do not add more roughness just because an older run reported weak engine. Recheck the current hard gate first, then repair the remaining source failure. If the current failure is comma-drag or period-grid, rebuild only the clusters where the refusal aftermath is still active: edited reply, unfinished transfer, route hesitation, door/body interruption, ordinary response, or a dirty/wet hand changing the phone action. Do not turn this into all-comma breath or all-period captions.

## Stop Rule

Validate after writing the revised `draft.md`. If the same or opposite failures bounce again, such as period grid -> comma drag, comma drag -> period grid, too few short drops -> tiny-row grid, texture thinning -> underbuilt source, or refusal consequence -> room texture, stop and record unresolved finalized repair. The next fix belongs in the skill architecture or first-draft source guidance, not in another metric-shaped rewrite.

If the revised article is only printed in a log/chat but `draft.md` is unchanged, mark artifact failure. If `draft.md` changes but the style gate is still `review` or `revise`, mark finalized unresolved or failed according to the controller summary; do not call it ready for blind rounds.

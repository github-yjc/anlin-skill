# Finalized Repair Minimum

Use this file only when a controller or user explicitly starts a finalized repair checkpoint from a copied bounded draft in a `finalized/` directory. It is the generator-facing minimum path. Do not load `validation-protocol.md`, `development-log.md`, full style-profile reports, checker source, tests, or hidden thresholds while repairing.

## Contract

- Work only on the copied `finalized/draft.md`.
- Freeze the selected genre before editing and pass it to every gate.
- A repaired article exists only after the complete article is written back to `draft.md`.
- A nonzero `--strict --repair-brief` exit usually means not passed, not a broken tool.
- Do not print a proposed final article to the terminal and keep thinking.
- Do not tune ratios one by one. Use the brief to choose one source-level rewrite.

## Gate Order

Run the hard gate first:

```powershell
python <skill-dir>/scripts/check_anlin_violations.py draft.md --strict --draft-gate --genre <selected-genre>
```

Then run the generator-facing style gate:

```powershell
python <skill-dir>/scripts/check_style_profile.py draft.md --draft-gate --strict --repair-brief --genre <selected-genre>
```

After the artifact is frozen, the controller may run `check_style_profile.py` again without `--repair-brief` for the full report. The repair agent should not use that full report as its writing interface.

## Repair Choice

If the hard gate has errors, fix the source function that caused the error and write a complete `draft.md`. Do not defend the draft or argue with the checker.

If the hard gate is clean but the repair brief says `formal_gate: not_pass`, choose exactly one source rewrite before the next validation:

- `punctuation` or `line_rhythm`: rebuild a few breathing clusters from action, reply, payment, door, object, or body movement. Add short drops only when an action lands badly. Do not globally merge rows into comma chains and do not split the draft into tiny rows.
- `connectors`: change what happens next so a turn is needed: failed reply, payment handoff, body interruption, route/object change, or another person's plain line. Do not paste connector words.
- `texture` or `ngram_texture`: delete one repeated body, screen, room, money, route, food, or object packet. Replace its function with a social or practical consequence that changes reply, payment, route, room position, body state, or next action.
- `structure` or `cognitive_mechanism`: cut prompt echoes, decorative proof details, and explicit cognition. Let a concrete object lead to a crooked read, a reality puncture, a defensive recovery, and a practical exit through action rather than explanation.

## Stop Rule

Validate after writing the revised `draft.md`. If the same opposite failures bounce again, such as period grid -> comma drag, too few short drops -> tiny-row grid, or texture thinning -> underbuilt source, stop and record unresolved finalized repair. The next fix belongs in the skill architecture or first-draft source guidance, not in another metric-shaped rewrite.


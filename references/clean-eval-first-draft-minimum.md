# Clean-Eval First Draft Minimum

Use this file for the first complete draft in formal clean-eval mode. It is intentionally short. The goal is to write one complete titled `draft.md` from source movement before any checker or long repair file can turn the article into a metric checklist.

## Tool Order

1. Check `.anlin-clean-eval-mode`.
2. Confirm the current directory is the external case workspace.
3. Read this file.
4. If the selected genre is standard diary, read `references/standard-diary-source-engine.md`.
5. Write one complete article to relative `draft.md` or `.\draft.md`.
6. Run `python <skill-dir>/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre <selected-genre>` when the genre is known.

Do not print a plan, title list, line count, metric table, trial article, or code-fenced final version before writing `draft.md`. Do not run counting scripts, rhythm scripts, homemade regex probes, `python -c`, `Measure-Object`, or the normal checker before the first wrapper call.

## No-Load Rule

Before the first complete `draft.md`, do not open `runtime-brief.md`, `clean-generation-brief.md`, validation protocol, judge rubrics, style-profile reports, corpus cards, review checklists, anti-slop references, background fact tables, checker source, tests, or hidden thresholds.

If you feel the draft needs more rules, write the best complete titled candidate to `draft.md` first. The controller is measuring source guidance; an imperfect persisted article is better evidence than a perfect article left in the terminal.

## Source Loop

Start from friction, not from the prompt noun.

Pick one small daily snag that would exist without the assignment: a door, sleeve, sink, bowl, charger, slipper, key, bag, payment, route, room chore, body interruption, bad reply, or object in the wrong place.

Then choose three consequence kernels in your head:

- side engine: a practical snag changes hand, room, body, reply, route, payment, or next action
- public hinge: another person, app/payment step, object handoff, door movement, or visible body problem keeps pressure active long enough to force a reply, wait, point, hold, wipe, drop, hide, pay, answer, leave, or change of room/route/body
- off-axis residue: one unrelated daily branch changes a later action; it is not random decoration

The user's topic is pressure, not the route map. Let one prompt surface leak only after the first engine has already moved the body, room, hand, route, payment, or reply. A complete article does not mean complete prompt coverage.

## Standard Diary Shape

For a standard diary / `日寄` clean-eval draft, the first saved article should already look like a complete broken-line piece:

- about 950-1150 body Chinese characters as a visual corridor
- about 45-70 body lines
- several rough longer action/speech/thought lines
- a few short drops that land failure, bad reply, body lowering, social cost, or practical retreat
- some line-final commas where an action or thought truly continues
- no 8-15 paragraph prose block
- no 80-100 tiny caption grid
- no 50-70 sealed `。` sentence rows

Do not hand-count. Look at the page shape. If it is visibly a prose block, a tiny-row grid, or a neat sentence grid, rebuild the source movement before saving.

## Cluster Grammar

Write breathing clusters, not sentence rows. A cluster can be 2-5 visible lines:

- one line trails with `，` because the hand, reply, payment, body, door, or object has not finished moving
- one rougher line runs longer because speech/action/thought has to keep going
- one line lands with `。` when an action closes
- one short drop may land a failed answer, low body fact, or retreat

Punctuation follows movement. Do not fix rhythm by deleting punctuation, adding connector words, making one giant comma chain, or turning every beat into `没管。/删了。/没回。/算了。`.

## Prompt Displacement

For feed, holiday, wrong-food, invitation, old-chat, annual-summary, illness, delivery, route, shopping, or family-pressure prompts:

- keep at most one or two prompt surfaces visible before the checker
- do not open with a feed/comment/message inventory
- do not title from the diagnostic prompt noun when the same noun also opens and closes the body
- do not let one material family own title, opening, middle, sink/table/pants/phone, and tail
- do not invent a current office identity, named district, route, game rank/role/tactics, spouse, child, or major family fact unless the user supplied it
- game is allowed only when it changes action, status, social relation, or cognition; it is never a required background label

If the draft can be summarized as `phone/feed -> order food -> wrong item -> wash bowl -> bed`, or `message -> price ledger -> refusal -> old chat -> room object`, restart the middle before saving.

## Title And Ending

Choose the title after the body exists. Bare `日寄` is allowed but not mandatory. `X日寄`, `X寄`, a phrase, question, sentence title, or side-object title can work when earned by the body. Weaken any title that exposes the prompt before the article has lived movement.

End on a loose practical leftover: unfinished reply, wrong object, cold food, route, payment, body interruption, door/room problem, or chore that did not resolve. Avoid clean ambient fades and learned administrative buttons such as `今天先这样` / `就先这样`.

## Stop

After writing `draft.md`, run the wrapper. If the wrapper returns `CLEAN_RUN_PREFLIGHT`, use `references/clean-generation-brief.md` as the detailed repair interface. If it returns `CLEAN_RUN_PREFLIGHT_STOP` or `CLEAN_RUN_STOP`, stop repairing, read `draft.md` once, and output it exactly.

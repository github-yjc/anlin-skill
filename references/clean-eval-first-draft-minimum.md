# Clean-Eval First Draft Minimum

Use this file for the first complete draft in formal clean-eval mode. It is intentionally short: the controller is measuring natural source guidance, not the agent's ability to reconstruct a hidden checklist.

## Tool Order

1. Check .anlin-clean-eval-mode.
2. As the next tool action, run standalone `Get-Location` / `pwd` and confirm the external case workspace.
3. Only after those two separate tool actions are visible, read this file.
4. If the selected genre is standard diary, read references/anlin-collage-source-model.md.
5. Write one complete titled article to relative draft.md or .\draft.md.
6. Run scripts/clean_run_checker.py with --generator-facing and the selected genre when known.

The marker check and cwd confirmation are two separate tool actions. Both must occur before any reference read, glob/path probe, or draft write; do not use controller `--dir`, a glob title, or an absolute path as cwd evidence.

Do not print a plan, title list, metric table, scratch article, or code-fenced final version before writing draft.md. Do not run counters, rhythm scripts, homemade regex probes, python -c, Measure-Object, or the normal checker before the first wrapper call.

Do not load `references/clean-generation-brief.md` or another long repair reference inside bounded clean-eval. The wrapper output is the complete repair interface.

After these source reads, the next tool action is one complete write to draft.md. Do not spend another model turn comparing openings. Choose the first workable fragment slate and persist it; a persisted imperfect article is evidence; an unwritten better plan is not.

After the minimal source reads finish, the next tool action must be one complete write to relative `draft.md`; do not spend another model turn comparing openings. Choose the first workable fragment slate and persist it; an unwritten better plan is not evidence.

## No-Load Rule

Before the first complete draft.md, do not open runtime-brief.md, clean-generation-brief.md, validation protocol, judge rubrics, style-profile reports, corpus cards, review checklists, anti-slop references, background fact tables, checker source, tests, or hidden thresholds.

If the draft feels incomplete, write the best complete titled candidate first. The wrapper and controller own later diagnosis.

## Fragment Source Contract

Build a fragment slate, not a preselected plot. A fragment can be:

- a present observation or bodily fact;
- a friend sentence or remembered conversation;
- an old memory;
- a platform, school, or work fact that the thought already needs;
- a joke, pun, logic inversion, fantasy, or absurd explanation;
- a word echo, self-correction, or change of mind.

Connect fragments by association, contrast, language echo, time jump, self-correction, cognitive habit, or an abrupt but voice-consistent jump. A causal chain is allowed when it occurs naturally, but it is not required. Use whichever relationships the movement earns. Do not allocate one period to each line or cluster.

The prompt is a trigger and a fact boundary, not a material inventory. It may appear early, late, repeatedly, indirectly, or be diluted by side thoughts. Do not turn supplied background into a quota. Keep only facts needed to avoid contradiction or to make an existing fragment truthful.

Consistency comes from the narrator: first-person voice, recurring questions, self-deprecation, crooked logic, word echoes, and a shared humor or irritation. Scattered does not mean arbitrary, and coherence does not mean one scene must explain every later line.

For standard diary, several independent thought-turns should normally be visible in the saved body. Do not let one room, one conversation, one message thread, or one transaction carry the whole article by default; let a later fragment move through an earned association, memory, contrast, joke, object, or time jump. This is a qualitative source contract, not a fragment-count quota.

For invitation prompts, reject a single carrier chain such as `present desk/room -> message -> ticket/money -> old-friend inventory -> work excuse -> refusal -> friendship thesis`. If the slate follows that carrier chain, replace one middle fragment with a lateral thought that does not explain the invitation. A dense body of a few prose paragraphs is prose-block compression, not a fragment slate; split multi-turn paragraphs into breathing rows before writing.

The ending may be a joke, question, absurd explanation, word echo, offhand fact, small practical landing, or a thought that fades without explanation. No ending type is mandatory.

## Minimum Artifact Rules

Before the first wrapper call, save a real artifact that has:

- a title and a complete body;
- fragments rather than a prompt inventory;
- at least one visible relation among fragments through voice, association, contrast, echo, time, or self-correction;
- no process language about generation, models, checkers, corpus, blind evaluation, or authorship;
- no unsupported high-risk identity, place, work, game, family, or relationship facts.

There is no universal standard-diary character target, line target, cluster count, required jump count, required outside person, required payment, required refusal aftermath, or required practical ending. Do not add material only to satisfy a number.

Do not compress amounts, reply candidates, or object choices into an `A、B、C` inventory. Put one selected detail into a fragment, action, joke, memory, or wrong reply and omit the rest.

When the same real action or object genuinely returns, let one plain action/object phrase return unchanged; this is not a decorative refrain or repetition quota. Do not synonym-scrub it or plant an echo.

Broken lines are allowed when the movement earns them. Use the line break, comma, period, or blank space that the thought or action needs; do not make every row a caption, a sealed sentence, or a comma continuation. Do not depend on a later rhythm script to invent the source shape.

Draft in breathing fragments, not sentence rows. The content being written must already visibly contain the complete broken article; a script cannot invent a source relation after the write.

## Prompt and Fact Discipline

Do not write a message, feed, price list, game inventory, background biography, or wedding logistics list merely because the prompt mentions it. Put one selected detail into a thought, action, joke, memory, or wrong reply; omit the rest.

For social prompts, an invitation or refusal may be one fragment among many. Keep a local consequence only when the text naturally creates one. Do not force a same-night consequence chain, a group-chat scene, a payment scene, a stranger, or a practical tail.

For background, use facts to prevent contradiction after the fragment exists. Do not invent a current office identity, named route, spouse, child, rank, district, or major family event to make the article feel concrete.

If the prompt only says `忙项目`, keep it as an excuse surface; do not invent a client, deadline, leave, team, coworker, city, or office biography.

## Stop

After writing draft.md, run the bounded wrapper. Its generator-facing output is the complete repair interface.

The wrapper output is the complete repair interface. It does not rewrite `draft.md`; the generator performs one integrated source or shape action and reruns it immediately.

- If it reports a source finding, replace the earliest broken fragment or relation while preserving a complete article. Do not solve each message as a separate material request.
- If it reports a pure shape finding, perform only the named local rhythm action.
- If the output is shape-only, do not add material.
- After any rewrite, rerun the wrapper immediately.
- After any `draft.md` rewrite, rerun the wrapper immediately.
- Do not load a long repair reference, inspect checker source/tests/thresholds, run counters, or switch to the normal checker inside the bounded case directory.
- Stop only at an explicit CLEAN_RUN_PREFLIGHT_STOP, CLEAN_RUN_STOP, or an actual checker result allowed by the protocol. At a stop boundary, read draft.md once and output that exact article.

# Runtime Brief

This file is for ordinary non-formal drafting and explicit analysis. Clean-eval misroute guard: if `.anlin-clean-eval-mode` exists, or if you have not yet checked that marker, stop using this file before drafting. Check it with a direct command such as `Test-Path -LiteralPath ".anlin-clean-eval-mode"` or `Get-ChildItem -Force .anlin-clean-eval-mode`; a directory listing that merely shows the filename is not a marker check. The marker check and cwd confirmation are two separate tool actions: after checking the marker, the next tool action must be standalone `Get-Location` / `pwd`. Both must be visible before any reference read, glob/path probe, or draft write; do not use controller `--dir`, a glob title, or an absolute path as cwd evidence. Then load `references/clean-eval-first-draft-minimum.md` plus `references/anlin-collage-source-model.md`. `clean-eval-first-draft-minimum.md` owns the first-draft source loop; this file must not become a hidden second clean-eval checklist. Do not use this file as an extra bounded repair prompt.

## Goal and Boundary

The goal is text that is less stably identified as generated under documented blind-review conditions. Never claim real authorship, provenance, or objective indistinguishability.

The article itself must not mention AI, generation, validation, corpus, blind review, checker, model, or methodology unless the user supplied that material as the subject. These references are runtime instructions, not prose ingredients.

## Source Contract

Start with a fragment slate rather than a plot outline or prompt inventory. Fragments may be present observations, bodily facts, remembered speech, old memories, jokes, platform or work facts already needed by the thought, logical inversions, fantasies, word echoes, or self-corrections.

Let the text move by association, contrast, language echo, time jump, self-correction, cognitive habit, or a direct voice-consistent jump. Causal movement is allowed but not required. A standard diary can have a loose spine, a conversation passage, or a collage; do not force all standard drafts into one shape.

In standard diary, several independent thought-turns should normally be visible. One room, one conversation, or one transaction carrying the whole article is not the default; after a fragment has done its work, let the voice move through an earned memory, joke, object, contrast, time jump, or ordinary fact. This is a qualitative movement cue, not a fragment quota.

**A complete standard diary is a day-shaped collage, not a premise summary.** If the body only has the prompt surface, one memory, and a final reply, it is a sketch; continue through another independent thought-turn before the required residue. Deepen existing fragments rather than appending checker-shaped scenes.

A movement unit is a short passage in which an observation, crooked read, and next action remain connected. Keep the natural Chinese punctuation that the thought needs. Punctuation-bearing movement units are the source shape: a line break does not remove punctuation, and naked caption rows are not breathing rows. Do not split every sentence into its own line. Keep short clauses attached to the action, reply, object, or thought they complete. A movement unit may occupy one or several uneven rows.

A thought-turn is not a paragraph or row count. It is semantic movement: the object, time, memory, joke, social position, or next action changes. Within one movement unit, an observation, crooked read, and next move stay connected. One thought-turn may contain several movement units, and the first artifact must show that movement because a rhythm script cannot invent missing source movement.

For invitation prompts, reject a single carrier chain such as `present desk/room -> message -> ticket/money -> old-friend inventory -> work excuse -> refusal -> friendship thesis`. If the slate follows that carrier chain, replace one middle fragment with a lateral thought that does not explain the invitation. A dense body of a few prose paragraphs is prose-block compression, not a fragment slate; preserve punctuation-bearing movement units before the first wrapper.

Keep coherence through first-person voice, recurring questions, social position, word echoes, humor, irritation, and the narrator's way of explaining or correcting himself. Scattered does not mean random, and coherence does not require every detail to change the next action.

The user prompt is a trigger and fact boundary, not a list of things to include. It may appear early, late, repeatedly, indirectly, or disappear while another thought takes over. Background facts prevent contradiction; they are not content quotas.

**A prompt's sequence is a fact constraint, not the article's outline.** For a linear social/event prompt, start with a non-prompt fragment before the prompt surface, crop the supplied event to one needed surface, and after the prompt fragment, leave it for an independent thought-turn that does not explain the event. Return to any required reply only as a short residue. If every cluster answers “what happens next with the invitation?”, replace the next plot step with a thought that can stand without the event; this is source routing, not a fragment quota.

There is no universal standard-diary character target, line target, cluster count, required jump count, required outside person, required payment, required refusal aftermath, or required practical tail. If the user or controller specifies a matched length/profile, treat that as an evaluation condition after the source decision, not as a material checklist.

If the prompt only says `忙项目`, keep it as an excuse surface; do not invent a client, deadline, leave, team, coworker, city, or office biography.

The wrapper output is the complete repair interface. The wrapper does not rewrite `draft.md`; after any `draft.md` rewrite, rerun it immediately. Do not load a long repair reference or solve one checker message as a separate material request.

In ordinary mode, the checker loop may continue until hard errors are cleared; bounded clean-eval and finalized repair have separate stop rules. After a finalized artifact is frozen, the controller may run the full `check_style_profile.py draft.md --draft-gate --strict --genre <selected-genre>` report without exposing that report to the repair agent.

When a finalized brief declares `repair_mode: hard_pass_review_in_place` or `repair_mode: source_rewrite_compact`, read only `draft.md` and `repair-brief.txt`; do not load `references/finalized-repair-minimum.md`. A missing/invalid brief or `controller_tool_error` uses that minimum only as the fallback artifact contract. Only a schema-valid controller result with return code `1` is a normal not-pass signal; other tool failures are unavailable, not quality evidence.

A post-check preflight protects checker call 2/2 when a known underbuilt source or hard shape failure is already present. It is byte-read-only, does not rewrite `draft.md`, and does not turn a controller diagnosis into a material checklist.

## Artifact and Tool Boundary

For an article-generation task, write a complete titled artifact to draft.md in the current task workspace before presenting prose. In clean-eval, use relative draft.md, the marker/cwd check, and clean_run_checker.py only. Do not write into the skill directory.

For bounded clean-eval:

- the wrapper output is the complete repair interface;
- when the action says `whole_source_rebuild`, keep that turn source-only: restore a day-shaped collage with independent thought-turns while preserving existing source mass; do not shrink it to a short premise summary, then call the wrapper again without running a rhythm script; rhythm tooling is exposed only by a later shape action after the severe source deficit is gone;
- a named rhythm command is an in-place final mutation: do not read its stdout or write draft.md afterward; rerun the wrapper immediately;
- after any draft.md rewrite, rerun the wrapper immediately;
- after any `draft.md` rewrite, rerun the wrapper immediately;
- do not load clean-generation-brief.md, runtime-brief.md, or another long reference after a bounded preflight;
- do not load `references/clean-generation-brief.md`, `references/runtime-brief.md`, or another long reference after a bounded preflight;
- do not run checkers, counters, source/test/threshold searches, path probes, or model diagnostics inside the bounded case;
- stop at CLEAN_RUN_PREFLIGHT_STOP, CLEAN_RUN_STOP, or the permitted checker result and read draft.md once.

For finalized repair, repair-brief.txt is the only generator-facing input when it is valid. The agent reads draft.md and repair-brief.txt, writes one complete revised draft.md once, then stops. It must not run checkers, counters, path probes, source/test reads, or a second write. The controller owns validation.

## Fact Gate

Open anlin-background.md, background-fact-classes.json, or era-state.md only after an existing fragment needs a fact checked. Lower unsupported specificity instead of inventing a named city, route, district, company, game role, current office identity, spouse, child, or major family event.

Game, delivery work, illness, family, platform, and classmate facts are optional. Keep a fact when the current fragment needs it; delete it when it only proves that the reference library was read.

## Prompt Surface Risks

Do not convert a feed, old chat, holiday, illness page, order, invitation, or annual-summary prompt into an inventory. Use one selected detail in a thought, action, joke, memory, or wrong reply and omit the rest.

Do not let the title, opening, middle, and ending all explain the same prompt prop. A prompt-adjacent title is allowed when earned by the body; it is risky when it becomes a diagnostic label.

For social prompts, an invitation or refusal can be one fragment among memories, jokes, facts, and side observations. A reply aftermath is optional: keep a local response only when the text naturally creates it. Do not invent a work biography, group-chat crowd, etiquette settlement, or multi-day wedding plot to prove social consequence. A warning about explicit cross-day expansion is a controller diagnosis, not a required scene.

## Anti-AI Surface

Avoid binary explanation frames, blog-like insight, therapeutic closure, process language, prompt-shaped titles, neat moral balance, numbered chat logs, unsupported specifics, and polished caption metaphors. Let a physical action, ordinary sentence, memory, joke, or wrong decision carry the turn.

Use a few features naturally. Do not satisfy every style label, connector list, body signal, or vocabulary category. Repetition is allowed when the same action or word genuinely returns; do not synonym-scrub repeated words or plant echoes.

Line breaks and punctuation follow thought and action. Do not make every row a caption, every row a sealed sentence, or every row a comma continuation. Do not run a rhythm script before the first clean-eval draft exists.

Blind-judge angles are review lenses, not pre-draft content requirements. Use them to locate the earliest weak fragment after a draft exists; do not add one fragment per lens.

Treat a silent witness as decoration when the contact does not change the narrator's thought, action, object, reply, or social position. A look, glance, or room texture is not automatically an event.

A rider or cashier who only looks once and leaves is still decoration; keep the contact only when the existing handoff changes what happens next.

Private grime is not an event by itself. Oil stains, sleeve dirt, sticky fingers, burps, mirror face, hair, smell, and clothing inspection become source movement only when an existing fragment changes payment, reply, door, bag, body movement, or social position.

## Post-Draft Diagnosis

After a draft exists, diagnose the earliest broken source decision:

- prompt inventory: remove the earliest redundant prompt packet;
- single-domain dominance: replace a repeated topic fragment with an existing lateral thought, memory, joke, or ordinary fact;
- private texture loop: cut repeated object/body proof unless it changes a real thought or action;
- social sealing: remove a cameo that only delivers facts, or keep it only if its line changes the narrator's position;
- designed thesis: keep an accidental plain detail and remove the line that explains its meaning;
- prose block or caption grid: repair the local movement, not the whole article by count;
- overgrowth: cut explicit chronology, new roles, and follow-up logistics before changing punctuation.

Use the post-draft source loop as a diagnosis, not a scene quota. If a prompt prop repeats, cut the earliest redundant packet; do not let food/body texture become the new loop.

Several findings may be one source failure. Replace the earliest broken fragment or relation once; do not add one scene per warning.

Do not let food/body texture become the new loop after removing a prompt surface. A feed is not a scene slate, and a sealed story shape is still a source failure when every fragment explains the assignment. Preserve one plain action or object phrase when it genuinely recurs; do not synonym-scrub repeated words. If repetition is mechanical, cut one repeated packet and replace its function inside the existing fragment slate.

If connector spread is thin, replace one inert observation so a real thought or action earns the turn; do not append a connector scene or swap synonyms. The reverse priority also matters: do not clean the article into a new hard-gate failure while chasing a profile signal.

For rhythm review, do not turn many hard-stop lines into one huge comma chain. A draft with many short rows and no visible punctuation is a generated line grid; actual line endings, not comma count inside long lines, decide the shape.

Many sealed `。` rows are a review risk, not a command to sprinkle commas. Let punctuation follow the existing thought or action.

Pure ambient ending, learned ending button, one-screen chronology failure, and caption metaphors that explain pressure are controller diagnoses. Replace them with an already-earned thought, joke, wrong decision, unfinished action, or ordinary fact; do not append a new scene.

If n-gram reuse is too low or uniqueness is too high, preserve one plain action or object phrase that genuinely recurs; do not synonym-scrub repeated words. If repetition is too high or templates repeat mechanically, cut one repeated local packet and replace its function inside the existing fragment slate.

The old record is a trigger, not the engine. Let one present humiliation, wrong reply, object failure, or ordinary fact make the present day answer it badly; The old record should not be a museum tour.

When a witness does not change the next thought or action, the contact has failed; remove it or replace the existing fragment relation instead of adding a gaze explanation.

Private texture must be replaced with a consequence when it only repeats body or object proof. Do not swing from comma-drag to period rows or from period rows to a single comma chain; choose the relation the local movement earns, not all four as a repeated cluster template.

The phrase pure ambient ending names a review risk, not a required replacement. Do not end by fading out on light, wind, appliance noise, or screen glow unless that sound is already doing work.

For short genres, do not mistake compression for deletion or repair stuffing. Keep the selected present fragment, discard unused prompt props, and do not expand a sincere piece merely to satisfy a standard-diary comparison.

Treat `短体裁修复堆新素材` the same way: repair inside the existing fragment slate before importing a new material family.

When repairing `短真诚当前动作锚点不足` or `短真诚标题物件闭环`, reset the source relation rather than adding one current detail around the old memory spine.

## Validation Boundary

Controller validation may compute length, line, punctuation, n-gram, prompt-surface, and profile distributions. Those are evidence after the artifact exists. Weak source heuristics such as connector coverage or a named paragraph engine are warnings unless a separate protocol rule makes the artifact invalid. A controller warning must not become an instruction to add material.

A finalized review or fail remains unresolved. A hard-gate pass does not prove style-profile pass. Report conditions, sample size, pass/recognition or false-accusation rates, invalid evidence, and limitations only when the corresponding evidence exists.

Do not start with plain `--strict` and treat a clean result as a pass. The controller reruns `check_anlin_violations.py draft.md --strict --draft-gate --genre <selected-genre>` and the full style-profile report after the artifact is frozen. A finalized `review` status still means the final article has unresolved risk; thin the draft instead of decorating it, and do not repeat a four-part cluster template.

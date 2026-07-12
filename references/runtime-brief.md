# Runtime Brief

This file is for ordinary non-formal drafting and explicit analysis. If .anlin-clean-eval-mode exists, first confirm the marker and current directory, then use clean-eval-first-draft-minimum.md plus anlin-collage-source-model.md. Do not use this file as an extra bounded repair prompt.

## Goal and Boundary

The goal is text that is less stably identified as generated under documented blind-review conditions. Never claim real authorship, provenance, or objective indistinguishability.

The article itself must not mention AI, generation, validation, corpus, blind review, checker, model, or methodology unless the user supplied that material as the subject. These references are runtime instructions, not prose ingredients.

## Source Contract

Start with a fragment slate rather than a plot outline or prompt inventory. Fragments may be present observations, bodily facts, remembered speech, old memories, jokes, platform or work facts already needed by the thought, logical inversions, fantasies, word echoes, or self-corrections.

Let the text move by association, contrast, language echo, time jump, self-correction, cognitive habit, or a direct voice-consistent jump. Causal movement is allowed but not required. A standard diary can have a loose spine, a conversation passage, or a collage; do not force all standard drafts into one shape.

Keep coherence through first-person voice, recurring questions, social position, word echoes, humor, irritation, and the narrator's way of explaining or correcting himself. Scattered does not mean random, and coherence does not require every detail to change the next action.

The user prompt is a trigger and fact boundary, not a list of things to include. It may appear early, late, repeatedly, indirectly, or disappear while another thought takes over. Background facts prevent contradiction; they are not content quotas.

There is no universal standard-diary character target, line target, cluster count, required jump count, required outside person, required payment, required refusal aftermath, or required practical tail. If the user or controller specifies a matched length/profile, treat that as an evaluation condition after the source decision, not as a material checklist.

## Artifact and Tool Boundary

For an article-generation task, write a complete titled artifact to draft.md in the current task workspace before presenting prose. In clean-eval, use relative draft.md, the marker/cwd check, and clean_run_checker.py only. Do not write into the skill directory.

For bounded clean-eval:

- the wrapper output is the complete repair interface;
- after any draft.md rewrite, rerun the wrapper immediately;
- do not load clean-generation-brief.md, runtime-brief.md, or another long reference after a bounded preflight;
- do not run checkers, counters, source/test/threshold searches, path probes, or model diagnostics inside the bounded case;
- stop at CLEAN_RUN_PREFLIGHT_STOP, CLEAN_RUN_STOP, or the permitted checker result and read draft.md once.

For finalized repair, repair-brief.txt is the only generator-facing input when it is valid. The agent reads draft.md and repair-brief.txt, writes one complete revised draft.md once, then stops. It must not run checkers, counters, path probes, source/test reads, or a second write. The controller owns validation.

## Fact Gate

Open anlin-background.md, background-fact-classes.json, or era-state.md only after an existing fragment needs a fact checked. Lower unsupported specificity instead of inventing a named city, route, district, company, game role, current office identity, spouse, child, or major family event.

Game, delivery work, illness, family, platform, and classmate facts are optional. Keep a fact when the current fragment needs it; delete it when it only proves that the reference library was read.

## Prompt Surface Risks

Do not convert a feed, old chat, holiday, illness page, order, invitation, or annual-summary prompt into an inventory. Use one selected detail in a thought, action, joke, memory, or wrong reply and omit the rest.

Do not let the title, opening, middle, and ending all explain the same prompt prop. A prompt-adjacent title is allowed when earned by the body; it is risky when it becomes a diagnostic label.

For social prompts, an invitation or refusal can be one fragment among memories, jokes, facts, and side observations. Keep a local response only when the text naturally creates it. Do not invent a work biography, group-chat crowd, etiquette settlement, or multi-day wedding plot to prove social consequence. A warning about explicit cross-day expansion is a controller diagnosis, not a required scene.

## Anti-AI Surface

Avoid binary explanation frames, blog-like insight, therapeutic closure, process language, prompt-shaped titles, neat moral balance, numbered chat logs, unsupported specifics, and polished caption metaphors. Let a physical action, ordinary sentence, memory, joke, or wrong decision carry the turn.

Use a few features naturally. Do not satisfy every style label, connector list, body signal, or vocabulary category. Repetition is allowed when the same action or word genuinely returns; do not synonym-scrub or plant echoes.

Line breaks and punctuation follow thought and action. Do not make every row a caption, every row a sealed sentence, or every row a comma continuation. Do not run a rhythm script before the first clean-eval draft exists.

## Post-Draft Diagnosis

After a draft exists, diagnose the earliest broken source decision:

- prompt inventory: remove the earliest redundant prompt packet;
- single-domain dominance: replace a repeated topic fragment with an existing lateral thought, memory, joke, or ordinary fact;
- private texture loop: cut repeated object/body proof unless it changes a real thought or action;
- social sealing: remove a cameo that only delivers facts, or keep it only if its line changes the narrator's position;
- designed thesis: keep an accidental plain detail and remove the line that explains its meaning;
- prose block or caption grid: repair the local movement, not the whole article by count;
- overgrowth: cut explicit chronology, new roles, and follow-up logistics before changing punctuation.

Several findings may be one source failure. Replace the earliest broken fragment or relation once; do not add one scene per warning.

## Validation Boundary

Controller validation may compute length, line, punctuation, n-gram, prompt-surface, and profile distributions. Those are evidence after the artifact exists. Weak source heuristics such as connector coverage or a named paragraph engine are warnings unless a separate protocol rule makes the artifact invalid. A controller warning must not become an instruction to add material.

A finalized review or fail remains unresolved. A hard-gate pass does not prove style-profile pass. Report conditions, sample size, pass/recognition or false-accusation rates, invalid evidence, and limitations only when the corresponding evidence exists.

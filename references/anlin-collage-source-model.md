# Anlin Collage Source Model

This is the active standard-diary source model for clean-eval. It replaces the historical scene-engine document; the historical file remains available only for migration and failure analysis.

## Corpus Observation

The 38 supplied originals span approximately 235-1932 Chinese characters and 17-91 non-empty body lines. These are observed ranges, not generation targets. Standard is a corpus/profile label, not a command to make every article the same size or page shape.

The originals vary: some stay with a conversation for a while, some move through a loose daily montage, and many jump between present objects, memories, jokes, platform facts, social comparison, and absurd explanations. The common signal is the narrator's mind and voice, not one universal plot.

## Fragment Slate

A fragment is a thought-turn that can stand briefly on its own:

- current observation or body state;
- friend dialogue or remembered speech;
- old memory;
- school, work, or platform fact already needed by the thought;
- joke, pun, naming theory, or logic inversion;
- fantasy or absurd explanation;
- word echo, callback, or self-correction.

A slate can contain several kinds in any order. Do not assign one slot to each kind, and do not preserve every prompt detail.

For a standard diary, normally let the slate move through several independent thought-turns. One continuous scene, conversation, message thread, or transaction carrying the whole article is a deliberate exception, not the default; after a fragment has done its work, let the voice jump when an earned association, memory, contrast, joke, object, or ordinary fact appears. This is a qualitative source contract, not a fragment-count quota.

For invitation prompts, reject a single carrier chain such as `present desk/room -> message -> ticket/money -> old-friend inventory -> work excuse -> refusal -> friendship thesis`. If the slate follows that carrier chain, replace one middle fragment with a lateral thought that does not explain the invitation. A dense body of a few prose paragraphs is prose-block compression, not a fragment slate; split multi-turn paragraphs into breathing rows before writing.

## Fragment Relations

Use the relation the text earns:

- association: one object, word, smell, or question calls up another fragment;
- contrast: the next thought undercuts or reverses the previous one;
- language echo: a word returns with a changed meaning;
- time jump: now, memory, another day, and now again;
- self-correction: the narrator revises what he just said;
- cognitive habit: a price, system, joke, symptom, or social rank becomes an explanation;
- direct jump: a new fragment arrives without a bridge because the voice makes the jump believable.

causal movement is allowed but optional. Do not repair a collage into a plot merely because a checker cannot name its engine.

## Coherence Without a Single Scene

Scattered is not random. Keep one or more stable signals:

- first-person narrator and recognizable self-deprecating or ironic voice;
- recurring question, anxiety, comparison, or social position;
- repeated words or ordinary objects whose meaning shifts;
- a shared humor, irritation, or defensive logic;
- a similar way of explaining, denying, exaggerating, or correcting.

These are soft source lenses, not quotas. Do not count fragments, jumps, echoes, or jokes.

## Prompt and Background

The user prompt is a trigger, not a material checklist. It can surface early, late, repeatedly, indirectly, or disappear for a while. A wedding, illness, feed, route, game, job, family fact, or old chat can be one fragment among others.

**A prompt's sequence is a fact constraint, not the article's outline.** When a social/event prompt supplies a chain or an explicit final action, keep the facts but break the chain as prose: start with a non-prompt fragment before the prompt surface; crop the prompt to the one message, object, or sentence the thought needs; after the prompt fragment, leave it for an independent thought-turn that does not explain the event; then return to the required action as a small residue. If every cluster answers “what happens next with the invitation?”, the article has become a plot. This is a source-order guard, not a quota for fragments or topics.

Background facts are contradiction boundaries. Keep a fact only when an existing fragment needs it. Do not insert a place, game role, current job identity, relationship, platform detail, or named person just because the reference library contains it.

If the prompt only says `忙项目`, keep it as an excuse surface; do not invent a client, deadline, leave, team, coworker, city, or office biography.

## Title and Ending

Choose the title after the body exists. A title may name a side object, phrase, question, joke, or ordinary fact when the body earns it. Do not let the title and last line form a neat explanation of each other.

End where the voice naturally stops: a joke, question, absurd theory, word echo, offhand fact, practical interruption, or unfinished thought. A practical leftover is allowed, never mandatory.

## Social Prompts

An invitation or refusal may be one fragment among memories, jokes, work facts, old messages, bodily observations, or unrelated daily thoughts. Do not default to message -> ticket -> money -> refusal -> same-night consequence. Keep a local consequence only when the draft naturally makes it load-bearing, and do not grow it into a multi-day subplot.

## Minimum

The first saved article must be a complete titled artifact in draft.md. It must not contain process language, checker language, model names, corpus claims, authorship claims, or unsupported high-risk facts. There is no fixed character corridor, line corridor, cluster quota, required scene order, required outside contact, or required tail.

# Generation Modes

Use these scene modes while drafting. Do not force every scene through one path.

## Mode A: Misread Scene

Best for jokes, system absurdity, and pseudo-analysis.

Shape:

1. concrete detail
2. deliberate misread or crooked explanation
3. external puncture or reality check
4. light defense
5. land and leave

Use when the scene has a strong daily object or platform/system surface.

In standard diary, use at least one Mode A scene with a real punchline. A misread is not a metaphor; it is the narrator applying a wrong but internally coherent rule to the world. If the line could appear in a sad prose poem, it is not a misread.

## Mode B: Social Collision

Best for dialogue and embarrassment.

Shape:

1. real setup
2. someone says something plausible
3. narrator's internal reaction is sharper than external response
4. misunderstanding or status wound appears
5. conversation hangs rather than resolves

Dialogue must sound like people trying to get through a day, not performers cooperating on a punchline.

The best social collision wounds by accident. Prefer:

- someone asks a normal question at the worst possible angle
- someone over-explains a practical detail and exposes a status wound
- someone shares good news without noticing the narrator's position
- someone misunderstands the narrator in a way that is funny and embarrassing

Avoid dialogue that merely delivers the prompt topic. A line like "你那个工作找到了没" is useful only if it causes a crooked answer, a social dodge, or a misfire that could not be replaced by narration.

## Mode C: Sincere Exposure

Best for mother/family/memory pieces.

Shape:

1. concrete memory or current action
2. cost becomes visible
3. narrator says less than he knows
4. retreat by plain fact, not a joke if a joke would cheapen it

Use sparingly in standard diaries. In sincere pieces this can be the main mode.

## Mode D: Body Intrusion

Best for gout, sleep, pain, hunger, urine, stomach, heart, or fatigue.

Shape:

1. abstract or emotional pressure rises
2. body interrupts without asking permission
3. narrator tries to reason around it
4. body wins

The body is not decoration. It breaks narratives that are too clean.

Use body intrusion as an actual break, not atmosphere. It should change what the narrator can do next: stop typing, fail to answer, get up, miss a message, choose food, avoid walking, or abandon an analysis.

## Mode E: Analysis Descent

Best for later-phase pieces where the narrator still thinks deeply.

Shape:

1. ordinary entry point
2. analysis that could almost be serious
3. a crooked but coherent conclusion
4. descent into body, money, social rank, or short retreat

Avoid sounding like an essay. The analysis must remain tied to a seen object, book, phone screen, conversation, or symptom.

## Mode F: Memory Trigger

Best for time drift.

Shape:

1. current sensory detail
2. older scene appears because of that detail
3. past expectation collides with current position
4. narrator exits before explaining the lesson

Do not insert memory as decoration. It must be triggered.

## Scene Selection

After listing candidates, choose by non-redundancy:

- What does this scene add that no other scene adds?
- Which scene is too clean and should be cut?
- Which scene is only there to satisfy a label?
- Which accidental detail makes the day feel lived rather than designed?
- Which scene is only a mirror for the title, opening, or ending?
- Which scene contains a real interruption: a clumsy phrase, unfinished reply, boring chore, wrong object, or social noise?

If the piece feels like a style checklist, remove one iconic Anlin feature and add one plain daily observation.

For standard diary blind evaluation, also run a domain-count pass:

- Mark each selected scene as `main-domain`, `side-pressure`, or `off-axis`.
- `main-domain` scenes directly answer the user's prompt topic.
- `side-pressure` scenes touch the pressure through body, money, another person, or an app surface.
- `off-axis` scenes would still make sense if the prompt topic disappeared.

Keep `main-domain` below half the selected scenes. If it is too high, cut the cleanest on-topic scene first, usually the one that only restates the prompt, and replace it with an off-axis scene connected by a small hook.

For formal blind evaluation, also cap visible high-signal prompt surfaces:

- keep at most two: e.g. roommate offer, class group benefits, job app, resume, rent subsidy, family question, old classmate success
- discard or bury the rest
- if `单主题词密度偏高` appears, remove high-signal nouns first; do not merely add unrelated details around them
- a prompt item can count as "buried" only if a reader would not reconstruct the original request from it

Useful off-axis scene sources:

- an unrelated route or delivery problem
- a game/login/app reward that turns into a bad joke
- a household object being dirty, missing, broken, expired, or wrongly labeled
- a body interruption that does not care about the theme
- another person's unrelated complaint
- a remembered scene triggered by smell, heat, sound, object, or phrase

The replacement scene still needs a turn. A useless detail without a punchline is just padding.

Run an enclosure pass:

- `single-room`: most scenes happen in one room/bed/desk.
- `single-night`: most scenes unfold chronologically in one night.
- `single-app-chain`: phone notifications drive the order.
- `closed-loop`: ending returns to an early object or debt with neat emotional force.

If two or more are true, the draft is too sealed. Replace one central scene with a time/space jump: earlier that day, a previous semester, downstairs, a shop, stairwell, street, delivery route, or another person's unrelated story. Do not let the ending return to the cleanest early object.

## Prompt-Compliance Trap

Recent blind failures mostly came from drafts that answered the prompt too well. Treat the user prompt as background pressure, not as the article's visible outline.

Before drafting, mark each prompt noun as one of:

- **driver**: one item may start the piece.
- **pressure**: one or two items may appear as consequences.
- **background**: most items should be displaced into phone screens, other people's words, receipts, unfinished replies, or objects.
- **discard**: anything that would make the piece feel like a complete response to the prompt.

Do not march through all prompt items in order. If the prompt says Valentine's Day, the article may start from a wrong condiment, a delivery note, a family message, or a game loss. If the prompt says moving, the article may start from tape stuck to a slipper. If the prompt says mother, the article may start from an unanswered delivery call. If the prompt says spring recruitment, roommate offer, and class group benefits, the article should not start from the group chat; start from something like a charger, stale food, a game loss, an app badge, or a body problem, then let the job pressure arrive late and partially. The theme should become visible late and partially, not on the first page.

Opening preflight:

- First content line should survive if the prompt topic were removed.
- First scene should not expose more than one high-signal prompt noun.
- If the opening directly answers "what happened today", replace it with a small local action that merely creates room for the pressure.

In formal evaluation, assume the generator sees only the user prompt and this skill. Do not rely on extra controller hints, prior judge failures, or hidden explanations. If a draft only works because the evaluation prompt told it "use montage", "do not summarize", or "add unrelated scenes", the skill has not actually learned that behavior; revise the skill, not the test prompt.

## Bounded Delivery

The generation agent must deliver a finished article, not a validation transcript.

For formal standard diary evaluation:

- write the first complete article with title
- run the local checker
- perform one targeted repair or one full rewrite from the scene slate
- run the checker again if the tool is available
- output only the best pure article

Do not keep repairing connector coverage, comma ratio, breathing-point hints, or line-rhythm warnings until the answer disappears. Those are controller diagnostics, not permission to stall. If a blocking issue remains after one rewrite, still output the cleanest pure article and let the external validation fail it; a visible process log is worse than a weak article for clean generation.

## Title Selection

Choose the title after the body has a lived shape.

Rules:

- Standard diary defaults to `日寄`. Use a modified `X日寄` only when `X` is a shame/body/side-object handle that sounds like a first defensive move, not a prompt label.
- Sincere or micro-hope titles may be complete sentences, but the title should come from a side action or wrong object, not from the final meaning.
- Avoid titles that contain the full emotional contract: `不算坏事`, `没发出去那条消息`, `给不存在的人写信`, and similar prompt-summary phrases are high-risk.
- Avoid topic-diagnostic standard titles such as `春招日寄`, `情人节日寄`, `婚礼日寄`, `痛风日寄`, `搬家日寄`, unless the body makes the modifier feel like an ugly side handle rather than the user's assignment.
- If the body already has a strong motif, use a weaker title.
- If the title is specific, the ending must not mirror it.

Bad pattern:

```text
Title says the lesson.
Body proves the lesson.
Ending restates the lesson.
```

Better pattern:

```text
Title is a small handle.
Body wanders through pressure.
Ending leaves on an action that does not explain the handle.
```

## Anti-Detection Pass

Before finalizing, remove the most "written" surface:

- If most lines are 4-12 Chinese characters, merge several into rougher longer lines.
- If the draft has fewer than 650 Chinese characters and is headed for full blind evaluation, expand with lived material rather than adjectives: one dialogue/social residue, one body or money action, and one unrelated daily detail.
- If the ending neatly echoes the opening, break the echo with a bodily action, social interruption, or plain unfinished fact.
- If every object is symbolic, add one object that is just there.
- If there is no dialogue or quoted social texture in a standard diary, add one plausible line from a real person or app surface.
- If the piece can be summarized by one theme sentence, insert or replace a scene with unrelated daily noise.
- If every transition is legible on first read, remove one connective explanation and leave only the object, app line, sound, or body sensation that triggered the jump.
- If a sincere/micro-hope/surreal draft reads like a polished prose poem, add rough logistics and delete the line that tells the reader what the feeling means.
- If the draft uses repeated typing/deleting as the main emotional engine, replace at least one repetition with a physical delay, bad reply, family interruption, or app surface. Repeated deletion is now a high-risk generated tell.
- If the final line is `哦`, `算了`, `睡了`, `屏幕暗了`, or a neat sound effect, keep it only when the preceding scene forces it. These are not default ending buttons.
- If a detail appears because it is in the prompt, bury it: have another person mention it, make it half-visible on screen, or let it produce a practical problem rather than a theme.
- If three consecutive scenes all point to the same wound, replace the middle one with a useless scene that still belongs to the day.
- If a sentence sounds like a portable aphorism, delete it or convert it into a bad practical claim someone could argue with.
- If the first scene, title, or final image would let a reader reconstruct the user's prompt, displace one required item into an offhand line, wrong object, or practical inconvenience.
- If a scene feels like it was added because a rubric wanted "realistic texture", make it do something mundane: delay a reply, dirty an object, change a route, interrupt a body, or create a small cost.
- If the text reads like a complete realist short story, damage the composition: insert one lateral branch, one rough social misfire, and one low bodily/material consequence; delete the sentence that makes the loneliness most legible.
- If the central wound remains visible in every object, choose one object and refuse its symbolism. Let it be cheap, dirty, wrong, or practically annoying.
- If the ending is a tasteful withheld image (`没点开`, `没回`, `看着`, `放下`), make sure the surrounding sentence is not a literary fade-out. Prefer an inconvenient continuation: food going cold, stomach reacting, wrong charger, toilet, payment, next notification, or a message from the wrong person.
- If the draft has no line that is actually funny, do not submit it. Add one Mode A or Mode B scene and let the joke land cold.
- If a scene ends in "大概是因为..." or another clean emotional explanation, cut the explanation and make reality answer instead.
- If the draft is "accurate but quiet", it is probably generated. Raise the amplitude through a social cut, body collapse, or bad system analogy.
- If the whole article can be described as one closed night, break time or place. Add a memory or outside scene caused by a small object, not by "I remembered".
- If the ending repays an early object too beautifully, remove the repayment. End on a loose tail that could annoy the narrator tomorrow.

Run this pass from the judge's point of view:

- What would a judge identify in five seconds: shortness, title, symmetry, lyric lineation, or obvious motif?
- Which scene exists only because the prompt asked for the topic?
- Which ordinary detail would survive if the title were removed?
- Which turn is too well designed to feel accidental?

## Failure Repair Map

Use this map when a blind judge identifies a draft.

| judge reason | repair |
|---|---|
| title too diagnostic | weaken the title or switch to plain `日寄`; move the strong phrase into an ordinary line, if at all |
| scenes all serve one theme | add two useless-but-real residues and cut one prompt-obvious scene |
| low-temperature realism | add one crooked joke, one social interruption, or one person who misunderstands the situation |
| realist short-story smoothness | cut one elegant sadness line; insert an off-axis branch connected by a sensory/object hook |
| no real laugh | build a small crooked explanation, self-own, or status collapse; do not add a meme punchline |
| polite social dialogue | replace with a plausible misfire, over-share, misunderstanding, or sentence that wounds by accident |
| polished micro-hope | add logistics, bad timing, and an unresolved body action; remove the final hopeful sentence |
| sincere piece too clean | keep one ugly practical detail and one awkward reply; do not let memory prove love too neatly |
| surreal piece too symbolic | add a dumb object, a payment/log-in problem, or an ordinary bodily action that breaks the symbol chain |
| short-line fragment poem | merge lines into uneven spoken syntax and add a longer clumsy clause |
| ending uses a learned button | end on a consequence: unread reply, cold food, wrong object, body pain, route, payment, or interrupted chore |
| clean observational minimalism | add one ugly self-own or body/social embarrassment; remove one tasteful object scene |
| pure ambient sound ending | make the sound cause a concrete interruption, or end on the interruption rather than the sound |
| repeated material hook | keep one occurrence; make the return change consequence, not wording |
| evenly spaced prose paragraphs | break into rougher line rhythm, comma-ended run-ons, blunt drops, and one messy dialogue/action chain |
| test prompt over-compliance | remove one visible required item, weaken the title, and add one scene that could survive without the prompt |
| single-theme density remains | delete a high-signal prompt surface before adding anything; keep only two visible pressure items |
| judge could also accuse originals | preserve the rough cue but reduce polish around it; do not optimize toward a detector that fails placebo |

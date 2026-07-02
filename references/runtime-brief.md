# Runtime Brief

Use this file before drafting. It is the small operating surface for generation. The larger reference files are for calibration and critique.

## Target

The target is anonymous blind-evaluation performance: a generated text should not be stably identified as generated under documented test conditions. Never claim real authorship or objective indistinguishability.

The prose body itself should read as ordinary prose. Do not insert methodology labels such as AI, generated, imitation, validation, corpus, sample, or blind test.

## Starting Point

Do not start from a checklist. Start from friction.

Ask internally:

- What small thing is bothering the narrator today?
- What is he pretending not to care about?
- Which coordinate is active first: body, money, social rank, platform system, family, or memory?
- What did he see, hear, touch, smell, pay for, avoid, or misread?
- What unrelated detail happened to pass through the day?

If there is no friction, do not manufacture a grand theme. Use a small daily mismatch.

Do not start from the user's topic sentence. The topic is often too clean. Start from a small misfit that could have happened even if nobody had asked for the topic: a stuck app badge, a wrong condiment, a dirty charging cable, a half-finished reply, a body itch, a bad route, a household object in the wrong place, or another person's offhand line.

For standard diary mode, treat the first visible sentence as a blind-review risk surface. If it contains the user's main pressure word, date event, relationship label, or requested object, rewrite the opening. The opening should usually be a body/object/app residue that only later lets the prompt pressure leak in.

## State Card

Create this before scene generation:

```text
date:
date-zone: high | medium | low | projection | inferred | fictional
phase:
genre:
place:
body-state:
money-state:
social-friction:
screen-texture:
avoidance:
hurt:
accidental-detail:
displaced-or-ignored-prompt-item:
useless-scene:
target-length:
line-rhythm:
feature-budget:
forbidden-risks:
```

The state card is not part of the final prose.

If the user asked for an article, the final answer must contain only the article title and body. Do not print the state card, prompt buckets, scene slate, validation summary, checker output, overlap score, or any line such as `草拟`, `校验通过`, `State Card`, or `Prompt item`.

For formal standard diary blind evaluation, run the checker in strict mode before final output, but keep the loop bounded. Strict mode is corpus-calibrated: original corpus files should not fail with hard errors. If strict mode reports a blocking issue, rewrite from the scene slate or reduce prompt-surface coverage.

This applies even when the user asked only for the article. Use a temporary/local draft file for the check, keep the report internal, and output only the title and article body after the bounded gate.

Blocking issues are process leakage, missing title, copied source phrasing, high-signal opening, learned ending buttons, sealed-night/story enclosure, pure ambient endings, repeated material hooks, and obvious prompt-shape leakage. Diagnostic title, body length, single-theme density, quiet explanation, weak paragraph engine, missing coarse self-damage, connector coverage, comma ratio, breathing-point warnings, and rhythm hints are review prompts unless the current test protocol explicitly requires full-article length.

Use at most one checker-driven repair loop. If the second draft still carries only soft style warnings, output the cleanest pure article rather than process notes; the external controller will validate it.

If the file/checker tool flow itself fails, do not end the response with logs or process text. Manually apply the strict gate, rewrite once, and output the article only. The external controller will validate afterward.

## Prompt Material Handling

Before drafting, split the user's prompt nouns into four buckets:

- `driver`: at most one item may visibly push the piece.
- `pressure`: one or two items may appear later as consequences.
- `background`: most items should be half-visible through another person's line, a phone surface, a receipt, an unfinished action, or a practical problem.
- `discard`: remove anything that would make the article look like a complete answer to the prompt.

For formal standard-diary blind evaluation, use at most two high-signal prompt items visibly. Everything else must be discarded, merged into a low-signal consequence, or made invisible. More prompt coverage is worse, not better.

Example: if the request says spring recruitment failure, roommate offer, class group physical exam, rent subsidy, job app, and old classmates, choose only two visible pressure surfaces. Do not include all of roommate offer + group physical exam + rent subsidy + job app + resume + position + classmate success. A blind judge reads that as prompt execution.

Do not preserve the prompt's order. If the prompt says "spring recruitment failure, roommate offer, class group physical exam, rent subsidy", the article must not open with the group and then march through roommate, job app, family, money. Start from a dirty or boring local detail, then let one pressure item interrupt.

When `scripts/check_anlin_violations.py` reports `单主题词密度偏高`, do not fix it by adding more off-axis scenes around the same central chain. Remove or weaken high-signal prompt terms first. Usually cut the job app or the group digest; keep one pressure surface and one displaced consequence.

When a prompt item is high-signal, prefer displacement:

- title: usually weaken to `日寄`
- opening: move the item out of the first scene
- middle: let another person or an app surface mention it
- ending: end on a consequence, not the prompt's emotional thesis

## Deep Voice Gates

Recent calibrated blind reviews caught drafts that fixed titles and length but still read like complete realist short stories. Avoid that failure before drafting.

For a standard diary, the scene slate must satisfy all four gates:

1. **Main-domain cap**: fewer than half the selected scenes may belong to the user's main topic domain. If the prompt is about spring recruitment, only 2-3 selected scenes should be directly about offers, job apps, group chats, benefits, resumes, or workplace envy. The rest must come from body, food, game, family, street, odd language, app residue, old memory, or another person's unrelated problem.
2. **Crooked joke gate**: include at least one laugh that is not just "I am sad and unemployed." Use status collapse, bad logic, low bodily truth, platform absurdity, or a self-own that feels a little embarrassing to say.
3. **Social misfire gate**: include one rough social moment where somebody accidentally wounds, misunderstands, over-shares, or says the wrong thing. The line should sound possible in real life, not like a stand-up punchline.
4. **Unhelpful residue gate**: keep one detail that does not symbolize the main theme and would be boring in a plot summary: wrong packaging, stale smell, a minor route problem, a useless app badge, someone else's errand, dirty object, neighbor sound, or a half-finished chore.

If a draft can be summarized as one clean thesis, it fails. Replace one on-theme scene with a lateral branch connected by a small hook: a word, smell, body sensation, app notification, memory, bad object, or someone's unrelated line.

Do not use quiet sadness as the default emotional solvent. Standard diary needs bounce: joke -> sting -> mouthy defense -> body/social interruption -> leave. A line like "I laughed, my stomach hurt" is usually too polite unless the surrounding scene has already made the laugh sharp or ugly.

## Paragraph Engine

Standard diary is not a low-energy diary. It needs an engine every few scenes.

Before finalizing, mark each scene with one engine tag:

- `misread`: a thing is deliberately read wrong, too literally, or through a bad system analogy.
- `self-own`: the narrator damages himself harder than the reader would.
- `social-cut`: another person says a plausible line that wounds by accident.
- `bathos`: a serious thought collapses into body, money, bad food, toilet, app friction, or a stupid object.
- `off-axis`: a lateral observation with its own turn.
- `plain`: setup or connective tissue.

In standard diary, at least four selected scenes should be non-plain, and no more than two plain scenes may appear consecutively. If the draft feels "true but quiet", it is not done. Add an engine; do not add another tasteful detail.

Repairs:

- replace "this is sad" with a misread that is technically stupid but emotionally accurate
- replace "I realized" with a person/app/body interrupting the realization
- replace quiet object symbolism with a bad practical consequence
- replace polite dialogue with a possible accidental wound
- delete the prettiest explanatory sentence after a good image

## Open Montage Gate

Do not write a sealed single-night short story unless the user explicitly asks for one. Standard diary should feel like a day and a mind leaking sideways, not a closed chamber drama.

Before final output, check:

- Does the draft stay in one room, one night, one app loop, and one pressure chain?
- Do early objects return at the end in a neat emotional loop?
- Could the piece be summarized as "tonight I could not sleep because of job anxiety"?
- Are most scenes ordered by time rather than by association?

If yes, break the enclosure:

- insert one past or earlier-day fragment triggered by a concrete object or phrase
- insert one outside-place fragment: corridor, street, shop, gate, delivery route, stairwell, group chat from another time, or someone else's errand
- cut one ending callback that makes the piece feel designed
- end on a loose practical tail, not the best emotional object

For early 2022 standard diary, prefer scattered daily montage over a single polished nocturne. The final article may have a weak spine, but it should not close like a short story.

## Core Voice

Anlin's stable tension is not "sad unemployed young man." It is:

- a 211 CS graduate who understands systems but is crushed by them
- a narrator who says he does not care while every sentence proves he does
- a mind that translates daily life into systems, jokes, prices, symptoms, and social rank
- a body that interrupts every clean explanation
- a writer who retreats before closure

Use concrete behavior instead of emotional labels. Use actions, numbers, bad sleep, payment failure, body signals, ordinary conversations, and phone screens.

## Generation Discipline

- Draft from state and scenes first.
- Use rules after the draft.
- Do not satisfy every high-frequency feature.
- Do not reuse iconic original images unless the user's background naturally requires them.
- Do not smooth transitions just because the reader might need help.
- Do not explain the joke after the image already works.
- Do not create a blind-test length outlier. For serious validation, the complete article including title is compared against length-matched complete originals; otherwise the judge can identify it by length and thinness rather than style.
- Do not let every detail serve the same emotional thesis. Keep two ordinary residues that remain slightly useless: a repeated app action, bad wording, household object, irrelevant message, route detail, or physical interruption.
- Do not default to short-line lyricism. Mix short cuts with longer spoken or thought clauses, especially in standard diary mode.
- Do not let the title, first scene, and ending agree too neatly. At least one of them should be weaker, dirtier, or off-axis.
- Do not use learned Anlin-like end buttons unless the scene forces them. `哦`, `算了`, `睡了`, sound effects, and dark-screen endings are high-risk when used as decorative closure.
- Do not make every required prompt detail visible. A blind judge can identify prompt-compliant writing faster than subtle style drift.
- For standard diary blind evaluation, revise before final output if the body is under roughly 650 Chinese characters. Expand with action, dialogue, body/material pressure, and useless daily residue rather than adjectives.
- For standard diary, do not deliver a title that diagnoses the prompt. `日寄` is safer than `春招日寄`, `情人节日寄`, `婚礼日寄`, or any title built from the user's topic noun unless the corpus phase and body strongly justify it.
- Before final output, inspect the first five content lines, the title, and the last three content lines together. If a judge could reconstruct the user's prompt from those surfaces, displace one of them.
- If the last line is `哦`, `算了`, `睡了`, `关屏`, a dark-screen action, or a lone sound effect, keep it only when the preceding scene forces that exact consequence. Otherwise end on a less iconic unfinished action, reply, route, object, payment, or bodily interruption.
- If the ending is a poised refusal such as "I did not open it", check whether it behaves like a literary closing image. If yes, break it with a lower consequence: stomach, toilet, bad food, route, payment, a second notification, or a stupid practical problem.
- Do not let a standard diary become clean observational minimalism. It needs at least one coarse social/body/self-humiliation turn that would feel a little ugly to quote, not only medicine, appliances, and quiet objects.
- Do not end on pure ambient sound unless the sound is actively doing social or bodily damage. `空调外机嗡嗡嗡。`, fan noise, rain noise, light hum, or screen buzz as the final line is a high-risk literary button when it merely fades out.
- Do not repeat the same material hook almost verbatim. If medicine, a charger, a temperature, or an app badge returns, the second return must change the social/body consequence rather than echo the first sentence.
- Do not compress standard diary into evenly spaced prose paragraphs. In corpus-calibrated full articles, 550+ Chinese characters usually need many short content lines rather than 8-12 large blocks. Keep broken line rhythm, blunt single-line drops, and one messy dialogue/action chain.

## Source Of Truth

Local references are the current contract for this skill. Original corpus evidence outranks summaries. If a script or summary conflicts with the 38 originals, treat the script/summary as suspect and document the mismatch.

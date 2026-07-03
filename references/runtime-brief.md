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

## Quiet Execution

Clean generation must look quiet from the outside. Do not print planning, checker summaries, state cards, repair notes, or "now I will" lines before the article. The first visible line returned to the user must be the title. If an internal note would be useful, keep it private or in tool-local reasoning; do not write it to chat or `draft.md`.

## State Card

Form this mentally before scene generation. Do not print it:

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
background-fact-boundary:
anti-ai-slop-watch:
```

For `background-fact-boundary`, write only constraints that prevent contradiction. It can be `none beyond prompt`. Do not list background facts as required ingredients, and do not copy the boundary into prose. A good boundary looks like `small-city texture only; no named district; game only if an already selected scene needs it; GPT only in late phase`, not `must mention Yunnan, 王者, 知乎, 狗哥`.

## Background Fact Intake

Use background in this order:

1. **Scene source first**: choose material from the user's prompt, current action, body state, screen surface, memory trigger, social interruption, route, food, money, or an accidental object.
2. **Necessity test**: ask whether the fact changes action, social position, body state, money state, next scene, or the joke. If deleting it changes nothing, delete it.
3. **Background check**: only then use `anlin-background.md` to classify the fact as supported, generic, third-person, or unsupported.
4. **Lower specificity**: if unsupported, lower the noun instead of adding more facts. `打了两把排位` becomes `打了会游戏`; `字节广州签字费股票` becomes `那张表`; `黄埔区` becomes `那边`.

Do not use the background file to expand the scene slate. If a fact was not already needed before opening the background file, it should not enter the article because the file lists it.

This means game is allowed, but never compulsory and never forbidden by silence. It may appear if the day has a natural game action, a social memory involving games, a user-provided game detail, or a corpus-backed thought turn that cannot be carried by a simpler object. It should not appear just because the background file confirms that Anlin has played 王者荣耀. If game appears, keep it coarse unless user material or a selected corpus anchor supports more detail.

The state card is not part of the final prose. For formal standard diary blind evaluation, set `target-length` to roughly 950-1150 body Chinese characters and `line-rhythm` to roughly 45-70 non-empty body lines, usually averaging 14-24 Chinese characters per content line. Do not aim near 650, 700, 800, or just under 900; repairs often shorten drafts. Keep at least six naturally longer lines above about 24 Chinese characters. Do not exceed 75 body lines under 1000 characters or 90 body lines in a 900-1300 character draft; if the draft has 100+ body lines, merge short adjacent lines before the first checker call.

Do not write `draft.md` until the candidate is complete. A file that contains only a title, a 400-character sketch, or a few scene notes is a contaminated generation artifact. If interrupted before a complete article exists, leave the run invalid rather than treating the stub as the answer.

Pre-write contract for formal standard diary: before writing `draft.md`, the candidate should already be around 950-1150 body Chinese characters, 45-70 body lines, at least six lines above about 24 Chinese characters, fewer than 75 lines when under 1000 characters, and not dominated by 4-10 character rows. If the candidate has 90+ body lines or no long lines, merge adjacent short rows into rough spoken/action syntax before the first file write. Do not expect the checker repair loop to fix a line grid later.

If the user asked for an article, the final answer must contain only the article title and body. Do not print the state card, prompt buckets, scene slate, validation summary, checker output, overlap score, or any line such as `草拟`, `校验通过`, `State Card`, or `Prompt item`.
Do not explain the stopping rule in the final answer. Never print `This is the second checker call`, `per protocol`, `current draft.md`, or `Here is the article`; the first visible line must be the title.

For formal standard diary blind evaluation, run the checker with `--strict --draft-gate` before final output, but keep the loop bounded. `--strict` is corpus-calibrated; `--draft-gate` is generated-draft-only and promotes formal article length plus prompt-shape risks. Original corpus files should be calibrated with `--strict`, not `--draft-gate`.

This applies even when the user asked only for the article. Use `draft.md` in the current working directory for the check, keep the report internal, and output only the title and article body after the bounded gate. Do not use OS temp files for formal evaluation drafts because timeout recovery needs the artifact.

Blocking issues are process leakage, missing title, copied source phrasing, high-signal opening, learned ending buttons, sealed-night/story enclosure, pure ambient endings, repeated material hooks, obvious prompt-shape leakage, generated-draft AI slop, unsupported background facts, literary annotation voice, middle-third prompt looping, severe rhythm/connective outliers, and any `--draft-gate` error. Quiet explanation, weak paragraph engine, missing coarse self-damage, breathing-point warnings, and minor rhythm hints are review prompts.

Generated-draft AI slop includes explanatory `不是X，是Y` / `不是X，而是Y`, `像X，其实不是，好像就是Y`, blog-like insight translation, self-annotation such as `其实就是那种怎么说呢` / `大概就是这个意思`, unsupported specific place names, unsupported game-role filler, isolated Chinese punctuation lines such as `。`, ordinary `——` connectors, literary `——那种...` explanation, abstract emotion labels such as `放松` / `释然` / `自洽`, A/B or 甲乙 variable explanation, or any line that mainly announces a reframe rather than letting a scene create it.

Use at most one checker-driven repair loop and call the checker at most twice. Checker findings are not tool failures; a nonzero checker exit with findings is an ordinary evaluation result. A third checker call, post-second write, fallback rewrite, or unpersisted final repair invalidates the clean-generation run more severely than a weak article does. After the second checker call, stop repair work: do not edit, write, compare, explain, invoke fallback, or run another command. You may read `draft.md` once only to output it exactly. Output the current `draft.md` content exactly, even if errors remain. Do not produce an unpersisted hand-repaired final variant after the second checker. Soft style warnings are not permission to run a third repair.

If the file/checker tool flow itself fails, do not end the response with logs or process text. Manually apply the strict gate, rewrite once, and output the article only. This fallback is only for execution failure such as file creation, overwrite, missing interpreter, or checker command not running. It is never for checker findings, hard-rule errors, or a failed style grade. The external controller will validate afterward.

## Prompt Material Handling

Before drafting, split the user's prompt nouns into four buckets:

- `driver`: at most one item may visibly push the piece.
- `pressure`: one or two items may appear later as consequences.
- `background`: most items should be half-visible through another person's line, a phone surface, a receipt, an unfinished action, or a practical problem.
- `discard`: remove anything that would make the article look like a complete answer to the prompt.

For formal standard-diary blind evaluation, use at most two high-signal prompt items visibly. Everything else must be discarded, merged into a low-signal consequence, or made invisible. More prompt coverage is worse, not better.

Example: if the request says spring recruitment failure, roommate offer, class group physical exam, rent subsidy, job app, and old classmates, choose only two visible pressure surfaces. Do not include all of roommate offer + group physical exam + rent subsidy + job app + resume + position + classmate success. A blind judge reads that as prompt execution.

Do not make classmate or roommate success more specific than the prompt or corpus supports. Do not invent company names, city, title, base, signing bonus, stock, rent-subsidy amount, salary, physical-exam package, office policy, or relocation detail for another person's offer. A screen can show a cropped notification, a vague table, a file name, a red dot, a practical question, or the narrator's delayed action; it should not become an HR compensation dossier.

Do not preserve the prompt's order. If the prompt says "spring recruitment failure, roommate offer, class group physical exam, rent subsidy", the article must not open with the group and then march through roommate, job app, family, money. Start from a dirty or boring local detail, then let one pressure item interrupt.

When `scripts/check_anlin_violations.py` reports `单主题词密度偏高`, do not fix it by adding more off-axis scenes around the same central chain. Remove or weaken high-signal prompt terms first. Usually cut the job app or the group digest; keep one pressure surface and one displaced consequence.

When a prompt item is high-signal, prefer displacement:

- title: usually weaken to `日寄`
- opening: move the item out of the first scene
- middle: let another person or an app surface mention it
- ending: end on a consequence, not the prompt's emotional thesis

For group chat, forum, or comment material, do not summarize a chain of speakers. A generated line like "有人回A。有人说B。又有人开始C" reads like prompt coverage and online-content formula. In clean generation, avoid forum-reply scenes unless the user specifically supplies one; `第一条回复`, `底下有人`, `评论区`, `热评`, and `谢邀人在美国刚下飞机` are all high-risk comment-chain residue. Use one of four lower-risk entries instead:

- one concrete message or screenshot detail, followed by the narrator's action
- a visual surface such as a row of numbers, avatars, red dots, or repeated file names
- one practical consequence such as delayed reply, changed route, payment, food, body interruption, or a missed task
- a vague crowd texture without multiple quoted positions

If the checker reports `评论链公式化转述`, delete the chain. Do not repair it by adding more people or more comments.

Also delete residue versions such as `底下跟了一串回答`, `底下追了一串问号`, or `被人回了个笑哭`; they are the same formula after compression.

For formal generated drafts, group chat and forum scenes should usually contain zero `有人` actors. Do not repair `有人发/有人说/有人问/有个人问/另一个人说` into a different `有人` sentence. Also avoid compressed reaction residue such as `跟了个捂脸`, `又发了个文档`, `发截图的人`, `群里回了两个人`, or `下面跟了个表情`. If a forum or group scene remains after repair, keep only the screen/action surface: unread count, screenshot crop, a blurred title, scroll action, delayed reply, body reaction, or the narrator closing it. Do not quote replies.

For ordinary dialogue, do not let people take turns delivering prompt facts. Five or more consecutive `我说/他说/他问/我回` lines read like a script. Compress the exchange into one or two rough narrated lines and interrupt it with a body action, misheard word, practical errand, or silence. Family chat is especially high-risk: `我妈问吃了没/我回面/她说少吃` should become one rough sentence plus the action of continuing to eat, not a turn-by-turn transcript.

## Deep Voice Gates

Recent calibrated blind reviews caught drafts that fixed titles and length but still read like complete realist short stories. Avoid that failure before drafting.

Treat likely blind-judge angles as generation lenses, not only review categories. Before drafting, make the selected scenes answer these reader risks in the material itself: title contract, opening disguise, middle-third drift, associative hook, rhythm variance, dialogue plausibility, body/money consequence, background fact support without background-display stuffing, anti-AI sentence shape, prompt displacement, ending consequence, and placebo humility. If a lens is only satisfied by an instruction note, it is not satisfied.

The middle third is the main clean-generation danger zone. It cannot keep repeating the prompt pressure with new nouns. Before writing the middle, choose one off-axis branch with a physical or social consequence: water spills, a route changes, a body demand interrupts, food goes wrong, someone says a dumb thing, a household object wastes time, or a small payment/action changes the narrator's position. Decorative "random texture" without consequence still reads generated.

Rhythm must be produced by thought and action, not by a visible anti-AI pattern. Do not cut every line to the same length. Keep at least a few longer spoken/thought lines, a few blunt short drops, and some comma-led broken movement; vary because the scene changes, not because a rule demanded variation. If many adjacent lines are 4-10 characters, merge them into rough spoken syntax.

For formal standard diary, do not compress the article into 8-15 prose paragraphs, but also do not cut it into 100+ tiny lines. Draft as broken body lines where each line usually carries a full action, reply, thought turn, or object consequence. The first `draft.md` should already be around 45-70 non-empty body lines and 950-1150 body Chinese characters before the first checker call; a short first draft usually becomes shorter after repair and fails clean generation.

If the model tends to underwrite, aim the first candidate near 1000-1200 body Chinese characters and let repair remove a little. Under 900 body characters is not a concise standard diary success in formal testing; it usually becomes a length cue.

After the first checker, repair by replacement rather than subtraction. If you delete a comment chain, unsupported game detail, city, dash sentence, or prompt-shaped line, add an equally concrete action, body consequence, social misfire, route, food, household object, or app surface before the second checker. If the checker reports line-grid errors, do a rhythm rewrite: reduce toward 55-70 body lines, merge many short rows into longer action/speech/thought lines, keep at least six 24+ character lines, and remove all-current-match game details. Never call the second checker on a draft that became visibly shorter than the first candidate or still has a visible short-line grid.

For a standard diary, the scene slate must satisfy all four gates:

1. **Main-domain cap**: fewer than half the selected scenes may belong to the user's main topic domain. If the prompt is about spring recruitment, only 2-3 selected scenes should be directly about offers, job apps, group chats, benefits, resumes, or workplace envy. The rest must come from body, food, family, street, odd language, app residue, old memory, route, money, or another person's unrelated problem. Use game only when the prompt or a corpus-backed consequence genuinely needs it.
2. **Crooked joke gate**: include at least one laugh that is not just "I am sad and unemployed." Use status collapse, bad logic, low bodily truth, platform absurdity, or a self-own that feels a little embarrassing to say.
3. **Social misfire gate**: include one rough social moment where somebody accidentally wounds, misunderstands, over-shares, or says the wrong thing. The line should sound possible in real life, not like a stand-up punchline.
4. **Unhelpful residue gate**: keep one detail that does not symbolize the main theme and would be boring in a plot summary: wrong packaging, stale smell, a minor route problem, a useless app badge, someone else's errand, dirty object, neighbor sound, or a half-finished chore.

For formal generated drafts, gates 2 and 3 are not optional. If the draft stays polite, quiet, and observational, rewrite before the first checker. Add an embarrassing self-own, bodily low point, or accidental social cut that changes the next action.

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
- replace `——` plus abstract feeling with the next action: the food goes cold, a reply arrives from the wrong person, the body hurts, money is paid, a route changes, or someone says a plain ugly line

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
- Do not default to paragraph prose either. Formal standard diary needs many broken body lines; large paragraphs make the sample look like a smoothed short story or model answer.
- Do not let the title, first scene, and ending agree too neatly. At least one of them should be weaker, dirtier, or off-axis.
- Do not use learned Anlin-like end buttons unless the scene forces them. `哦`, `算了`, `睡了`, sound effects, and dark-screen endings are high-risk when used as decorative closure.
- Do not use AI-humanizer contrast frames. If a sentence negates one interpretation before revealing another, delete the negation and let the scene carry the turn.
- Do not create pseudo-colloquial slogans or four-item concept clusters. If a phrase sounds internet-native but has no real source community, replace it with a plain local action or an ugly spoken line.
- Do not use literary annotation frames. If a sentence needs `——` to explain a feeling, delete the explanation and make a concrete thing happen next. Avoid `放松`, `释然`, `自洽`, `真实感`, `完整感`, and `命运感` in generated formal drafts.
- Do not use ordinary `——` connectors in generated formal drafts. If the line is not quoted dragged speech, replace the dash with a comma, a line break, or a concrete action.
- Do not use A/B or 甲乙 variable placeholders to explain a daily failure. Keep the actual wrong food, broken object, price, app surface, or person's line.
- Do not invent a named district, city route, game role, company park, or platform fact to make the day concrete. Use `anlin-background.md`: unsupported specifics are worse than vague but truthful surfaces.
- Background is optional, not an Anlin label. Do not insert 云南、王者、痛风、狗哥、外卖、知乎, or AI/GPT simply because the reference file says they exist. Use a fact only when the prompt, phase, or scene consequence needs it.
- Game is optional, not an Anlin label. Prompt silence does not ban it, but the selected scene must have a natural game action, memory trigger, social consequence, practical delay, or thought turn. If a non-game object can carry the same function more truthfully, use body, food, app, family, route, money, or social misfire instead.
- Game is not the default off-axis patch, but it is not forbidden. It can be a valid branch when it changes action, status, social relation, or cognition. It fails when it only proves the skill knows Anlin played games.
- Do not turn a game scene into a match report. Without a corpus anchor, avoid `排位`, current-rank details such as `星耀二/星耀三`, `晋级赛`, `结算页面/结算界面`, `MVP`, `复活点`, `加血`, `加盾`, `奶不到`, `输出全靠`, `队友全死`, `退出匹配`, `撤退信号`, `二塔`, `团战`, `三换二`, `阵容`, `泉水`, `经济面板`, `输出比辅助低`, `干得漂亮`, `硬辅`, `下路`, `装备`, lane/role terms, equipment, quick-chat lines, and tactical explanations. A game detail should be coarse and should cause a status wound or practical action, not show MOBA knowledge. If using corpus-backed game facts, stay near `打王者`, `打了5000局王者荣耀`, `最高星耀五`, `ELO`, or `蔡文姬/补血心理`.
- Also avoid current-match sequencing: `第一把/第二把`, `赢了/输了`, `战绩`, `评分`, `队友`, and `英雄池` usually turn the scene into a match report. If the thought needs ELO, attach it to life or status, not to a fabricated current match.
- Do not make every required prompt detail visible. A blind judge can identify prompt-compliant writing faster than subtle style drift.
- For standard diary blind evaluation, revise before final output if the body is under roughly 900 Chinese characters. 650 is only the lower comparison boundary; 650-899 is still a generated-draft risk zone. Expand with action, dialogue, body/material pressure, and useless daily residue rather than adjectives.
- During repair, never fix a draft-gate error by shrinking below the length target. If deleting a high-risk line, replace it with a concrete action or off-axis residue before the second checker call.
- Before the first checker call, make sure `draft.md` itself is the candidate final article: line-broken, complete, titled, near 950-1150 body Chinese characters, with roughly 45-70 content lines and at least six naturally longer lines. The checker validates `draft.md`, not a later terminal-only rewrite.
- For standard diary, do not deliver a title that diagnoses the prompt. `日寄` is safer than `春招日寄`, `情人节日寄`, `婚礼日寄`, or any title built from the user's topic noun unless the corpus phase and body strongly justify it.
- Before final output, inspect the first five content lines, the title, and the last three content lines together. If a judge could reconstruct the user's prompt from those surfaces, displace one of them.
- If the last line is `哦`, `算了`, `睡了`, `关屏`, a dark-screen action, or a lone sound effect, keep it only when the preceding scene forces that exact consequence. Otherwise end on a less iconic unfinished action, reply, route, object, payment, or bodily interruption.
- If the ending is a poised refusal such as "I did not open it", check whether it behaves like a literary closing image. If yes, break it with a lower consequence: stomach, toilet, bad food, route, payment, a second notification, or a stupid practical problem.
- Do not let a standard diary become clean observational minimalism. It needs at least one coarse social/body/self-humiliation turn that would feel a little ugly to quote, not only medicine, appliances, and quiet objects.
- Do not end on pure ambient sound unless the sound is actively doing social or bodily damage. `空调外机嗡嗡嗡。`, fan noise, rain noise, light hum, or screen buzz as the final line is a high-risk literary button when it merely fades out.
- Do not repeat the same material hook almost verbatim. If medicine, a charger, a temperature, or an app badge returns, the second return must change the social/body consequence rather than echo the first sentence.
- Do not compress standard diary into evenly spaced prose paragraphs. In corpus-calibrated full articles, 550+ Chinese characters usually need many short content lines rather than 8-12 large blocks. Keep broken line rhythm, blunt single-line drops, and one messy dialogue/action chain.
- Do not end every content line with a full stop. Keep some comma-led broken lines and natural connective tissue; a formal generated draft with almost no high-frequency connectors or comma endings reads over-edited.
- Do not write ordinary chat or room dialogue as standalone quoted script lines. Prefer `我妈问晚上吃的啥，我回面。` or a single screen-surface line over `"晚上吃的啥。"` / `"面。"`

## Source Of Truth

Local references are the current contract for this skill. Original corpus evidence outranks summaries. If a script or summary conflicts with the 38 originals, treat the script/summary as suspect and document the mismatch.

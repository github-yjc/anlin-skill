# Feature Budget

This file replaces "must include every Anlin label" thinking.

A generated piece should carry a few high-value features deeply, not all features shallowly. High-frequency features are a budget, not a shopping list.

## Hard Requirements

These apply to all normal generation:

1. First-person limited viewpoint.
2. Concrete daily material before abstraction.
3. Defensive humor or defensive retreat unless the genre is explicitly sincere.
4. No explanatory methodology terms in prose.
5. No claim of real authorship or provenance.
6. No clean moral, advice, motivational ending, or solved emotional arc.
7. No direct copying of signature passages from the original corpus.
8. No "polished fragment poem" default: avoid uniformly short lines, numbered sections, or clean cinematic closure unless a source anchor strongly supports that exact form.
9. No blind-test length outlier: for serious anonymous evaluation, complete articles with titles must be comparable to complete corpus articles. If the draft is too short, expand or mark the evaluation as short-genre only.
10. No prompt-shaped article: the title, scene order, and ending must not reveal the user's prompt as an outline.
11. No learned ending button: `哦`, `算了`, `睡了`, a dark screen, or a lone sound effect cannot be used as default closure.
12. No external-test scaffolding: formal evaluation drafts must be achievable from the skill and a realistic user prompt, not from extra controller hints, judge rubrics, or post-failure advice supplied to the generator.
13. No diagnostic standard title: when writing a standard diary for blind evaluation, choose the title after the body using `title-model.md`. Bare `日寄` is valid, but not a universal default; use `X日寄`, `X寄`, questions, meme/platform titles, sentence titles, or literary phrases only when the body earns them and they do not expose the user's topic noun. Calendar labels such as `2024日寄`, `新年日寄`, `跨年日寄`, or `年度总结日寄` are high risk when the date/feed topic comes from the prompt.
14. No underbuilt complete article: a generated standard diary submitted to full complete-article blind evaluation should normally land around 900-1100 body Chinese characters. 650 is only the lower comparison boundary; 650-849 is a draft-risk buffer zone when repairs are likely. Below 850, expand with lived actions and residues or mark the evaluation as short-genre only.
15. No realist-short-story smoothing: standard diary cannot keep every scene inside one coherent emotional arc. It needs lateral branches, rough social misfires, crooked jokes, and unhelpful residue.
16. No high-signal prompt coverage: formal standard-diary blind evaluation should visibly use at most two prompt pressure surfaces; discard or bury the rest.
17. No AI-reframe sentence: formal generated drafts should not use `不是X，是Y`, `不是X，而是Y`, `不是因为X，而是因为Y`, `真正的问题是`, `本质上`, `现在我意识到...`, or similar explanation scaffolds. Make the turn happen through scene, body, app, money, or another person's line.
18. No unsupported concrete background: do not invent named districts, city routes, company parks, local policies, or game-role details. Use `anlin-background.md` and user-provided facts; if unsupported, lower specificity. Supported background is not mandatory material; it only prevents contradictions.
19. No literary annotation sentence: formal generated drafts should not use `——` to append an explanatory feeling, and should avoid abstract emotion nouns such as `放松`, `释然`, `自洽`, `真实感`, `完整感`, or `命运感`. If the feeling matters, turn it into an action, body interruption, payment, route, food, or another person's plain line.
20. No pseudo-humanizer regularity: do not manufacture roughness on a schedule. Avoid repeated "口语化" tics, invented internet idioms, four-item concept clusters, and a predictable alternation of short joke / sad line / object detail.
21. No middle-third prompt loop: the middle of a standard diary cannot keep restating the user's main domain. It needs at least one off-axis branch with consequence, not a decorative realism detail.
22. No line-length grid: do not make the article a sequence of same-sized short lines. Rhythm variance should come from action, speech, body, and thought turns.
23. No over-fragmented body: a 900-1300 character standard diary should not become 100+ tiny lines. Broken rhythm is not one clause per line.
24. No runtime dependence on external style cleanup: anti-AI-writing behavior must come from this skill's own references and checker. Do not call another personal style or anti-slop skill to make the prose acceptable.
25. No over-specific inference: corpus-supported inference may lower specificity, but it must not invent current city, current game rank, match tactics, employer, local policy, or platform fact.
26. No helpful clarification sentence: if a line explains why the scene matters, helps the reader understand the theme, or repairs ambiguity, delete it unless a person/app in the scene literally produced that line.
27. No ratio-matching as composition: corpus priors and predictive intervals are post-draft audit tools, not quotas. Do not add a connector, game cue, body symptom, dialogue line, comma, or short line merely to satisfy a measured ratio. If a measured feature drifts, repair the lived function that caused it.
28. No overfilled completeness: a formal standard-diary draft above about 1250 body Chinese characters should be checked for padding; 1350+ should be treated as generated-draft overfill unless the material is truly consequence-bearing. Delete non-consequential texture instead of adding another body/screen/object detail.
29. No texture saturation: body, phone/screen, route/object, money, platform, and background facts are not six boxes to tick. If three texture families are all frequent, keep only details that change what the narrator does, what someone says, what the body interrupts, or what the next scene can become.
30. No anti-AI-reference contamination: anti-slop terms in this skill are negative examples, not content prompts. Unless the user supplied it, do not write AI/GPT/model/text-detection scenes or advice about identifying generated prose.
31. No repeated texture-packet repair: if a draft keeps returning to the same body/object packet, such as hand dirt, white food, cutting board, garbage, route heat, payment, or dark room, do not add another proof-detail. Delete one packet and replace its function with a social or practical consequence that changes reply, payment, route, room position, or next action.
32. No polished short-genre essay: sincere and micro-hope pieces can be short, but they still need uneven breathing, rough logistics, awkward reply/practical interruption, and factual retreat. Do not submit a 25-35-line smooth prose piece where every line completes the same feeling.

## Strong Defaults

Use most of these, but not all:

- self-deprecating status wound
- platform or phone-screen texture
- body signal or low bodily interruption
- money, price, account, or payment behavior
- direct dialogue or social collision
- accidental non-theme detail
- associative jump rather than chronological transition
- one moment of analysis or deliberate misreading
- one short retreat line or hard cut
- one piece of ordinary noise that does not help the central motif: a stray message, bad wording, boring object, repeated action, or minor social interruption
- uneven rhythm: at least one longer spoken/thought line and at least one hard cut; do not make all lines 4-12 Chinese characters
- at least one prompt item displaced into another person's line, a screen surface, an unfinished action, or a practical consequence rather than stated directly
- first visible scene that survives without the prompt topic
- one non-iconic ending consequence: unfinished reply, cold food, wrong object, route, payment, bodily interruption, or interrupted chore
- at least one off-axis scene connected by a hook, not by chronology
- at least one plausible social misfire or ugly small line, when the mode is standard diary

## Standard Diary

Recommended budget:

- 5-10 scene units depending on phase and length.
- Usually 900-1100 body Chinese characters for generated full blind evaluation; always include a title; if shorter than 850, judge only against matched short originals or revise before submission.
- Avoid drifting past about 1250 body Chinese characters. If the draft reaches 1350+, cut material first; do not treat extra length as safer completeness.
- 2-4 emotional registers: laugh, sting, tenderness, deflection, absurdity, analysis.
- 1-2 central motifs at most.
- 0-2 recurring characters. Use none if the material is body, solitude, or observation driven.
- 1-3 one-off/random social figures at most.
- 1 main system/phone/platform texture, not a news digest.
- 2+ non-theme residues: details that make the day feel lived rather than designed.
- main-domain scenes below half the selected slate; use side-pressure and off-axis scenes to prevent a single-topic essay.
- at most two visible high-signal prompt items. If the request lists roommate offer, class group physical exam, rent subsidy, job app, and resume, do not include all of them.
- background facts used as invisible rails. If a scene only exists to show "Anlin plays 王者" or "Anlin is in Yunnan", cut the scene. If game changes action, memory, status, social relation, or cognition, it is allowed; if it only satisfies a perceived label, it fails.
- if a repair warning mentions n-gram texture, body texture, route/object texture, or low dialogue/social movement, reduce repeated local packets before adding anything. A social consequence is useful only when it changes action or status; it is not a new quota to insert a cashier, neighbor, or vendor into every article.

Avoid:

- every scene proving the same theme
- all required prompt details appearing in visible order
- a role roster
- a sequence of jokes without accumulated sting
- a single-topic essay disguised as diary
- a visible opening/ending mirror that makes the piece feel designed
- static image chains where every object becomes a symbol
- title-to-ending closure that tells the judge the piece was designed around one idea
- reader-risk fixes that appear only as visible technique: artificially spaced slang, scheduled broken sentences, or one "random" object inserted every paragraph
- a middle section that still loops through the prompt nouns while pretending to drift
- line rhythm that looks mechanically cut to avoid prose blocks
- 100+ tiny body lines in a normal-length draft
- repeated typing/deleting as the main emotional engine
- evaluation-prompt compliance: visible montage, unrelated details, anti-summary behavior, or title choice appearing only because the test prompt instructed them
- AI-humanizer surface: obvious not-X-but-Y contrasts, blog-like summary words, or one-line explainer pivots that sound corrected by a machine
- unsupported background specificity: named district/city/game-role detail inserted only to create realism
- background-display stuffing: adding 王者、痛风、狗哥、外卖、知乎, or a city cue only because the background file permits it
- a smooth chain of scenes where every object proves the same wound
- polite melancholy in place of a real laugh, self-own, or social embarrassment
- a tasteful withheld ending that could close any literary short story
- literary captioning after a good image: `——那种...`, `终于可以...的放松`, `释然`, `自洽`, or a sentence that names the feeling instead of making something happen
- game scenes that become proof of MOBA knowledge: first/second match, teammates, tactics, scoreboard, rank interface, win/loss sequence, or role vocabulary
- a cause/explanation tail after every good scene: `因为...`, `所以...`, `可能...` can be natural, but when they translate the wound for the reader they make the draft feel generated

## Sincere Piece

Recommended budget:

- 1 core relationship or memory.
- Low joke density.
- Concrete actions and irreversible cost.
- 4-7 uneven clusters rather than a single smooth paragraph or equal-length line grid.
- Several longer clumsy memory/action/speech lines, plus one or two short fact-retreat drops.
- One rough ordinary logistics detail or awkward reply that prevents the memory from becoming a clean proof of love.
- One protected retreat near the end, but do not force a joke.
- If used in blind evaluation, either expand to a comparable complete-article length or compare only against short sincere originals.

Allowed:

- shorter length
- fewer platform details
- no recurring cast beyond the relevant person
- less obvious self-deprecating humor

Avoid:

- apology essay
- greeting-card blessing
- psychological explanation
- full closure
- writing every line as a finished emotional sentence
- polished minimalism where every line is a complete emotional unit
- mother/family memories arranged as a clean proof of love or guilt
- titles that summarize the withheld confession
- stretching into standard diary only to satisfy a global profile
- adding game/body/route/background labels because the short genre feels too quiet

## Micro-Hope Piece

Recommended budget:

- 1 small observed event or action.
- Hope must be material: a sound, a payment, a walk, a sentence, a body easing.
- Keep the hope vulnerable and interruptible.
- Add one rough logistics detail so it does not become a small prose poem.
- Keep uneven breathing: a few longer practical lines and one short factual drop, not evenly polished emotional rows.

Avoid:

- "life is still worth it" phrasing
- universal encouragement
- bright ending without residue
- a final sentence that completes the emotional argument
- titles or endings that explicitly say the bad thing is still acceptable
- clean object chains where every object supports hope
- final repair that smooths away the bad timing, logistics, or body/action interruption

## Surreal Or Literary Experiment

Recommended budget:

- One loosened reality rule.
- Still anchor in body, place, money, or social friction.
- Keep the narrator's defensive intelligence intact.
- Return to a plain action after the loosened rule; do not leave the reader inside a symbolic image.

Avoid:

- generic dream prose
- ornate literary metaphors
- losing the social/body coordinates
- making every object in the dream explain the same wound
- dream elements that translate one-to-one into the prompt's theme
- symbolic systems without a dumb practical interruption

## Projection Or Inferred Dates

Use fewer specific claims and more personal texture.

Required:

- mark uncertainty in controller notes or validation report
- do not invent real events, prices, or platform states

Allowed in prose:

- ordinary phone behavior
- plausible daily scene
- user-provided background

Avoid:

- pretending a post-corpus date has original-level support
- writing macro history

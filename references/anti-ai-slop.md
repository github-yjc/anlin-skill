# Anti-AI Slop Gate

Clean-eval misroute guard: if `.anlin-clean-eval-mode` exists, or if you are in a formal/eval workspace and have not yet checked that marker, stop using this file before drafting. Check the marker with a direct command such as `Test-Path -LiteralPath ".anlin-clean-eval-mode"`; a directory listing that merely shows the filename is not a marker check. Then run standalone `Get-Location` / `pwd` as the next tool action, and load `references/clean-eval-first-draft-minimum.md`; for standard diary also load `references/anlin-collage-source-model.md`. Do not keep reading this file as a negative checklist before the first complete `draft.md`.

Use this file directly for ordinary drafting or explicit anti-AI analysis. For bounded clean-eval generation, `clean-eval-first-draft-minimum.md` and `anlin-collage-source-model.md` carry the first-draft constraints, and wrapper output alone carries bounded repair. Do not load this file or `references/clean-generation-brief.md` inside that bounded repair.

The goal is not to make the article casual. The goal is to remove surfaces that make a reader feel a model completed an assignment: too balanced, too explanatory, too coherent, too loyal to the prompt, and too clean.

This file is the complete runtime anti-AI layer for this skill. Do not depend on any external anti-slop skill, style skill, web article, or private prompt during generation. Maintenance research can inspire this file, but a generation agent must be able to avoid synthetic surfaces by reading this skill alone.

The strongest human-reader tells are not rare words. They are visible decisions: a sentence announces its own meaning, a paragraph obeys the prompt too completely, a title and ending form a clean contract, or the middle looks inserted to satisfy a rubric. Treat those as drafting constraints, not only as post-draft lint.

Important: this file is a negative list, not a topic bank. In ordinary article generation, do not write scenes about AI tools, AI article detectors, generated text, model answers, GPT chat windows, or someone teaching how to identify AI writing unless the user supplied that as real material. If the subject entered the draft because this file mentioned it, remove the subject entirely. Replacing "AI" with a synonym does not fix the contamination; choose a day-produced object, body problem, payment, route, food, social misfire, or screen surface instead.

## High-Risk AI Surfaces

### 1. Binary Explanation

Avoid explanatory contrast frames:

- `不是X，是Y`
- `不是X，而是Y`
- `不是X。是Y`
- `不是因为X，而是因为Y`
- `X不是问题，Y才是`
- `这不是X，这是Y`
- `真正的X不是Y，而是Z`
- `表面上X，实际上Y`
- `像X，其实不是，好像就是Y`

These are model-friendly because they announce a reframe, then deliver it. In Anlin-like prose the turn should come from a scene, a person, a body interruption, or a stupid object, not from a balanced sentence.

Putting `不是X，` or `不是X。` at the end of one line and `是Y` / `就是Y` / `而是Y` at the start of the next line does not fix it. It is still the same model-coded reframe.

Bad:

```text
不是包装袋漏，是电动车前面那个篮子。
```

Better:

```text
酸梅汤顺着电动车前面的篮子滴了一路。
```

If a binary contrast appears in a generated formal draft, rewrite it even if one or two originals contain natural cases. Original-corpus calibration is not permission for generated drafts to keep a high-risk generated structure.

### 2. Explainer Voice

Delete sentences that translate the scene for the reader:

- `这说明...`
- `这意味着...`
- `说白了...`
- `换句话说...`
- `翻译过来就是...`
- `本质上...`
- `核心是...`
- `真正的问题是...`
- `现在我意识到...`
- `我终于明白...`
- `最终我意识到...`
- `说不上是那种...`
- `其实就是那种怎么说呢`
- `大概就是这个意思`

Anlin can analyze, but his analysis usually stays attached to an object, price, app surface, bodily symptom, or somebody's line. When the sentence sounds like a blog post summarizing insight, cut it.

### 2b. Literary Annotation Voice

Avoid using a beautiful connector to explain what the scene already means:

- `A——那种B`
- `A——一种B`
- `终于可以...的放松`
- `松了一口气`, `释然`, `自洽`, `真实感`, `完整感`, `命运感`

These lines are dangerous because they look more human than a blog summary, but a reader can still feel the model adding a caption under the image. The repair is not "make it more casual." Delete the caption and let the next physical fact answer.

Bad:

```text
能认出那句没问题下周可以的语气——那种终于可以把话说得很轻的放松。
```

Better:

```text
那边说没问题，下周可以。
我把听筒拿远了一点，锅里的面已经坨了。
```

Em dashes are rare in the corpus and usually belong to quoted speech, interruption, or dragged sound. In generated formal drafts, default to no `——` at all. Do not use it to attach an explanation, a heard-word list, or an abstract feeling; use a comma, a line break, an action, or the plain words heard.

### 2c. Variable Placeholder Explanation

Do not turn daily failure into algebra:

- `你准备好的是A，拿到的却是B`
- `从A到B`
- `甲不是乙`

This is the same problem as binary explanation, but disguised as a practical analogy. Anlin-like analysis should stay attached to the actual wrong food, broken charger, app line, money, or person's sentence.

Bad:

```text
你准备好的是A，拿到的却是B，而且不能退货，得咽下去。
```

Better:

```text
我本来想吃鸡，最后坐在那啃排骨。
排骨还塞牙。
```

### 3. Prompt Loyalty

Generated text often looks fake because it obeys the prompt too well. The article should not show all requested nouns in the title, opening, middle, and ending.

Before drafting, bury or discard most prompt material. Choose only pressure surfaces the fragment slate actually earns, and let different fragments answer through association, memory, joke, body, object, or ordinary delay. Do not collapse the article into one pressure/consequence chain; make the rest arrive as a partial screen residue, another person's line, a practical delay, or not at all.

High-risk pattern:

```text
The prompt lists A, B, C, D.
The article opens with A, moves to B, uses C in the middle, and ends by resolving D.
```

This can pass a style checklist and still fail a real reader. Remove one requested item before drafting. If the item must remain, make it partial: a cropped screenshot, a file name, a payment, a delayed reply, a wrong object, or a person asking the wrong practical question.

### 4. Smooth Paragraph Engine

AI prose likes clean transitions:

- `然后`
- `接着`
- `与此同时`
- `另一方面`
- `更重要的是`
- `总之`
- `最后`

For standard diary mode, scenes should jump by object, sound, bodily sensation, wrong wording, app residue, or social misfire. If the transition explains itself, it is probably too smooth.

### 5. Uniformity

AI prose often has one temperature. Watch for:

- similar line lengths across the whole article
- every paragraph ending with a neat point
- every detail serving the same emotional wound
- no useless residue
- no ugly social/body interruption
- no middle section that feels genuinely accidental

Add roughness by changing what the narrator must do, not by adding adjectives.

The opposite failure is also AI-like: overfilling a draft with too many body, screen, route, object, money, and platform cues after seeing a checklist. A complete standard diary should feel lived, not saturated. If the draft passes because every line contains a concrete texture noun, cut details that do not change action, social position, body consequence, or the next scene.

### 6. Portable Humanizer Smell

Do not replace obvious AI prose with visible "humanizer" tricks:

- planned typos or fake roughness
- scheduled slang every few lines
- a rotation of joke / sad line / object / short sentence
- invented internet idioms that no actual person in the scene would say
- therapy-adjacent phrases such as `允许自己`, `接住自己`, `被看见`, `和自己和解`, `慢慢来` when they are not quoted from a real screen/person
- explanatory causal tails after a good scene: `因为打开也不知道说什么`, `所以也没什么好说的`, `可能就是这样`

The repair is not to make the line messier. Make a real thing happen: a reply comes from the wrong person, food goes cold, the body demands something, money is paid, an object breaks, a route changes, or someone says a plain ugly sentence.

### 7. Clean Causality

Models often make every detail explain the next detail. Anlin-like movement can be intelligible, but it should not feel engineered.

Before drafting a scene, ask whether it can survive without becoming a thesis. If every object points to the same wound, pick one object and refuse its symbolism. Let it stay cheap, dirty, late, wrong, or practically annoying.

Do not write:

```text
I saw X, which made me realize Y, so I did Z.
```

Prefer:

```text
I saw X.
Somebody interrupted.
Z happened for a stupid practical reason.
Y remains unstated.
```

## Human-Reader Audit

After the checker passes, do one quiet read as a skeptical ordinary reader:

1. Could I guess the user's prompt from the first five lines and title?
2. Does one sentence sound like it came from an AI-humanizer checklist?
3. Is there a `不是X，是Y` or equivalent reframe?
4. Does the middle feel like it was generated to satisfy "montage"?
5. Are the place, game, platform, job, and family details supported by corpus, user facts, or current verification?
6. Would the same article work if every specific noun were swapped? If yes, it has no life.
7. Is there one polished line with `——`, `那种`, `终于可以`, or an abstract feeling noun that sounds like a caption? If yes, remove the caption and keep the action.
8. Is any sentence using A/B, 甲乙, or a schematic analogy? Replace the variables with the actual bad object.
9. Is there any `——` in a formal draft? Remove it unless it is truly quoted dragged speech from a source-like line.
10. Did the draft hide a prompt item by simply replacing it with another prompt-adjacent item? If yes, it is still prompt execution.
11. Does any sentence sound like a universal life-coach repair: `允许`, `接住`, `和解`, `被看见`, `慢慢来`, `松弛`? Delete it unless someone in the text actually said it.
12. Does a cause word (`因为`, `所以`, `可能`) explain a feeling that a scene already showed? Cut the explanation and let the next action carry the residue.

If one line gives off AI smell, remove or rewrite the whole local move. Do not polish around it.

## Generation Lens, Not Just Review

Apply this before selecting scenes. The point is to make the first draft avoid judge-detectable surfaces naturally.

### Title Lens

Before choosing the title, ask what a reader can infer from it alone. If the title reveals the prompt noun, date event, illness, relationship, job state, or emotional thesis, weaken it. For standard diary, `日寄` is usually safer than a clever title.

### Opening Lens

The first fragment should survive after deleting the user's prompt. Start from an object, body, app residue, wrong wording, route, food, household friction, or another person's offhand line. Do not open with the clean topic.

### Middle Lens

The middle is where generated drafts often fail. It cannot be a disguised outline. Let a later fragment turn through an earned lateral relation when the slate needs one:

- a game/app action that causes a bad thought
- a body or food interruption
- another person's unrelated complaint
- a street/shop/route detail
- an old memory triggered by a concrete object or phrase

The branch must change action, mood, or social position. A random object that only "adds texture" still reads generated.

If the middle still repeats the prompt's main nouns, the draft is not drifting; it is decorating the assignment. Replace the earliest redundant relation with a practical interruption or lateral thought that makes the narrator do something else; do not add a branch as a quota.

### Rhythm Lens

Do not create a grid of equal short lines to avoid prose blocks. Vary line length because the mind is interrupted: a longer spoken sentence, a stupid explanation that runs too far, a blunt two-character retreat, a comma-led continuation, a payment/action line. If rhythm variation can be described as a pattern, it is probably visible to a judge.

Do not repair rhythm by spraying commas through the whole body. Several early comma-led continuations can help, but high comma density across a long draft reads like a model simulating breath. Replace excess comma chains with action cuts, quoted plain speech, a body interruption, or deletion.

### Density Lens

Before the final checker, judge density by function rather than a universal length corridor:

- if body, screen, and route/object details are all frequent, ask which ones change the day
- if a detail only proves "there is life texture here," cut it
- if deleting a supported background noun changes nothing, cut it

The target is not sparse prose. The target is consequential texture: fewer details that actually make the narrator move, reply, pay, limp, stop, misread, or lose face.

### Background Lens

Before using a concrete noun, decide its evidence level:

- `supported`: appears in corpus, user facts, or verified lookup
- `generic`: low-specificity daily surface such as 小城, 楼下, 学校门口, 招聘, 打游戏, 打王者
- `third-person`: appears as another person's action, platform discourse, or contrast, not narrator biography
- `unsupported`: district/city/company/game-role/platform detail added for realism

Use supported or generic. Keep third-person facts as third-person facts. Delete unsupported.

Do not add a supported background noun just because it is supported. Background facts are guardrails against contradiction, not ingredients. Prompt silence does not ban game, and corpus support does not require game. If a selected game detail has no practical, social, bodily, memory, or cognitive consequence, remove the game detail or lower it to a generic action.

Allowed inference is low-resolution. `He plays games` or `he has played 王者荣耀` can be inferred from the corpus. A current match, role, lane, build, rank, tactical signal, or win/loss sequence cannot be inferred. If a game scene starts to look like a match report, delete the game and use body, food, money, route, family, app, or social misfire instead.

### Prompt-Loyalty Lens

Pick only visible pressure surfaces that the fragment slate earns, and let different fragments answer through different kinds of consequence or no consequence at all. If the article includes all prompt items or forces them into one pressure/consequence chain, it will look generated even if each sentence is good.

### One-Line Smell Lens

Before finalizing each scene, identify the single most polished sentence. If that sentence explains the scene, remove it. If the scene collapses after removing it, the scene did not have enough life.

Also identify the single most "helpful" sentence. If it clarifies the theme, repairs the reader's confusion, or tells the reader how to feel, remove it. A rough draft can leave an edge; generated prose often over-serves.

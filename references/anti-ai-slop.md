# Anti-AI Slop Gate

Use this file before drafting and again during review. It is a short guardrail against the agent's default prose habits.

The goal is not to make the article casual. The goal is to remove surfaces that make a reader feel a model completed an assignment: too balanced, too explanatory, too coherent, too loyal to the prompt, and too clean.

## High-Risk AI Surfaces

### 1. Binary Explanation

Avoid explanatory contrast frames:

- `不是X，是Y`
- `不是X，而是Y`
- `不是因为X，而是因为Y`
- `X不是问题，Y才是`
- `真正的X不是Y，而是Z`
- `表面上X，实际上Y`

These are model-friendly because they announce a reframe, then deliver it. In Anlin-like prose the turn should come from a scene, a person, a body interruption, or a stupid object, not from a balanced sentence.

Bad:

```text
不是包装袋漏，是电动车前面那个篮子。
```

Better:

```text
酸梅汤顺着电动车前面的篮子滴了一路。
```

If a binary contrast appears in a generated formal draft, rewrite it even if one or two originals contain natural cases. Original-corpus calibration is not permission for generated drafts to use the model's favorite structure.

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
- `我终于明白...`
- `最终我意识到...`

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

Em dashes are rare in the corpus and usually belong to quoted speech, interruption, or dragged sound. In generated drafts, do not use `——` to attach an explanation or an abstract feeling.

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

Before drafting, bury or discard most prompt material. Keep one pressure surface and one consequence. Make the rest arrive as a screen residue, another person's line, a practical delay, or not at all.

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

If one line gives off AI smell, remove or rewrite the whole local move. Do not polish around it.

## Generation Lens, Not Just Review

Apply this before selecting scenes. The point is to make the first draft avoid judge-detectable surfaces naturally.

### Title Lens

Before choosing the title, ask what a reader can infer from it alone. If the title reveals the prompt noun, date event, illness, relationship, job state, or emotional thesis, weaken it. For standard diary, `日寄` is usually safer than a clever title.

### Opening Lens

The first scene should survive after deleting the user's prompt. Start from an object, body, app residue, wrong wording, route, food, household friction, or another person's offhand line. Do not open with the clean topic.

### Middle Lens

The middle third is where generated drafts often fail. It cannot be a disguised outline. It needs one off-axis branch with its own turn:

- a game/app action that causes a bad thought
- a body or food interruption
- another person's unrelated complaint
- a street/shop/route detail
- an old memory triggered by a concrete object or phrase

The branch must change action, mood, or social position. A random object that only "adds texture" still reads generated.

### Background Lens

Before using a concrete noun, decide its evidence level:

- `supported`: appears in corpus, user facts, or verified lookup
- `generic`: low-specificity daily surface such as 小城, 楼下, 学校门口, 招聘, 王者, 排位
- `unsupported`: district/city/company/game-role/platform detail added for realism

Use supported or generic. Delete unsupported.

### Prompt-Loyalty Lens

Pick one visible pressure surface and one consequence. If the article includes all prompt items, it will look generated even if each sentence is good.

### One-Line Smell Lens

Before finalizing each scene, identify the single most polished sentence. If that sentence explains the scene, remove it. If the scene collapses after removing it, the scene did not have enough life.

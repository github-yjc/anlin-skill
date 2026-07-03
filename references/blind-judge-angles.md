# Blind Judge Angles

Use this file only for validation and post-failure diagnosis. It is a judge matrix, not a drafting checklist.

The evaluation target is anonymous blind review: generated complete articles should not be stably identified as generated under documented test conditions. The judge may answer `NONE`. Results must report conditions, sample size, identification rate, false-accusation rate, and invalid rounds only.

## Method Principles

- Treat the task as open-set authorship verification, not forced attribution. If evidence is weak or all samples look plausible, answer `NONE`.
- Control obvious confounds before judging: filename, length, topic, date, sample order, and title formatting. Titles are part of the article and should be judged, but all samples must present titles in the same normalized format.
- Separate style evidence from topic evidence. A sample about the same subject can look similar for topic reasons.
- Do not use any single cue as decisive evidence. Require convergence across at least three evidence families.
- Count a stable accusation only when confidence is at least 75 and at least one evidence family is not title/topic/length/order.
- When placebo false accusations are high, first suspect the judge calibration rather than the generation target.
- Use all-original placebo rounds as source-style calibration. If an evidence cue would also accuse original samples, downgrade that cue before using it against generated text.
- Give detailed reasons even when answering `NONE`; non-identifications are useful only if they explain why the evidence stayed ambiguous.
- Mark a round invalid if the judge saw mapping files, corpus filenames, skill files, previous analysis, controller notes, or invoked any style/author skill. Automated judges should run source-neutral, in pure mode where available, and with local skills disabled through an isolated config when the runtime can auto-load installed skills.

## Evidence Families

### 1. Lexical Field

Inspect:

- ordinary function words and soft connectors: 其实, 觉得, 发现, 好像, 不过, 突然, 于是, 因为, 所以
- local collocations and half-fixed phrases
- platform, money, body, family, work, school, and city vocabulary
- low-frequency literary/essayistic words that feel imported
- AI-like generic abstractions: "生活", "孤独", "世界", "意义", "情绪", "治愈" when not earned by behavior

Strong generated tell:

- vocabulary is correct by category but not by habit; the sample contains "Anlin nouns" without Anlin connective tissue.

### 2. Phrase And N-Gram Texture

Inspect:

- recurring 2-4 character chunks and loose formulae
- whether combinations sound semi-constructed by the same idiolect or newly assembled by imitation
- overuse of famous source mechanisms or signature image packages
- strange synonym choices that avoid the corpus's plain wording

Judge cautiously:

- repeated source nouns are not proof. Repeated packages of noun + body event + punchline are stronger evidence.

### 3. Title Contract

Inspect:

- whether the title matches the article's genre: plain `日寄`, modified `日寄`, full-sentence sincere title, literary/surreal phrase, or micro-hope phrase
- whether the title's defense level matches the body: self-deprecating, evasive, sincere, literary, or deliberately bland
- whether the title promises a theme the body then over-delivers too neatly
- whether the title is too diagnostic, too explanatory, or too optimized for the prompt
- whether title and ending form a clean artificial loop

Strong generated tell:

- the title sounds like a label assigned after reading the prompt rather than the first move of the article.

Judge cautiously:

- title mismatch alone is not decisive. Original titles vary by phase and genre.

### 4. Sentence Length And Punctuation

Inspect:

- line-length variance rather than average length alone
- comma endings, hard periods, standalone `.` separators, quoted dialogue, and breathing points
- long spoken clauses that run slightly too far
- abrupt one-line stops that are not decorative

Strong generated tell:

- many lines are uniformly short and polished, producing a "fragment poem" surface.

### 5. Syntax And Brokenness

Inspect:

- self-interruption, incomplete thought, delayed predicate, awkward but intentional spoken syntax
- whether sentence breaks follow consciousness, body interruption, or chat rhythm
- over-balanced "不是X，而是Y", "一方面/另一方面", "最终/于是我明白" structures
- excessive grammatical completion and smooth transitions

Strong generated tell:

- the sample reads as if every sentence was revised into clarity.

### 6. Associative Movement

Inspect:

- the hook between adjacent fragments: sound, object, platform word, bodily signal, memory trigger, social phrase
- time and space montage: present -> past -> imagined future -> present
- whether a jump feels inevitable after reading, even if it was surprising before reading
- whether the text merely stacks unrelated "Anlin-like" scenes

Strong generated tell:

- all scenes are independent style cards with no lived associative path.

### 7. Narrative Distance

Inspect:

- near view: self-mockery, body, money, phone screen
- middle view: observation of others, ordinary dialogue, social ranking
- far view: pseudo-analysis, system logic, social absurdity
- whether the text shifts distance or stays in one ornamental register

Strong generated tell:

- the sample stays in wise-commentator mode or in pure wounded first-person mode.

### 8. Hidden Spine And Delayed Return

Inspect:

- whether there is a weak inner spine without visible essay planning
- whether an early detail returns later with changed force
- whether the return is natural, not a title-to-ending mirror
- whether the piece can be reduced to one clean thesis
- whether the hidden spine is an associative pressure or merely the user's prompt in disguise

Strong generated tell:

- every object points to the same obvious meaning.
- title, scene sequence, and ending all prove the same prompt sentence.

### 9. Ending Behavior

Inspect:

- dialogue cutoff, bodily action, plain fact, hard cut, or low-energy retreat
- whether the ending refuses summary while still carrying residue
- whether a sincere ending is protected by fact, not explanation
- whether the last line introduces a neat symbolic closure

Strong generated tell:

- the ending behaves like a literary short essay closing image.

### 10. Humor Mechanics

Inspect:

- whether the joke comes from observed reality, status wound, platform mismatch, body collapse, or a crooked system explanation
- whether self-deprecation protects a real wound or merely signals "摆烂"
- whether absurdity has a physical or social base
- whether the punchline is over-written or meme-like

Strong generated tell:

- the joke is good as a standalone joke but detachable from the day.

### 11. Bathos And Retreat

Inspect:

- high thought collapsing into body, money, low social fact, or bad timing
- sincerity cut short before it becomes complete
- pseudo-analysis destroyed by a person, app, body, or payment action
- whether the retreat is timed before closure

Strong generated tell:

- the sample knows it should "撤退" and performs a visible trick.

### 12. Emotional Masking

Inspect:

- the text says "无所谓" while behavior proves otherwise
- shame, love, jealousy, tenderness, and fear appear through logistics and body
- sadness is displaced into price, route, app, object, or physical symptom
- direct emotional nouns are rare and earned

Strong generated tell:

- the sample explains its wound instead of making the reader infer it.

### 13. Reality Texture

Inspect:

- boring objects, exact actions, payment friction, screenshots, weather, old furniture, small-city routing
- details that do not serve the motif
- platform surfaces as seen by a user, not as trend summaries
- consumption and body details that have consequences

Strong generated tell:

- details are correct but odorless: plausible, clean, and interchangeable.

### 14. Dialogue And Social Noise

Inspect:

- whether people speak to finish the day, not to deliver the author's point
- unfinished replies, "哦", "行", read receipts, repeated app checks, awkward silence
- random figures: parent, friend, delivery customer, guard, colleague, classmate, neighbor
- whether dialogue is too cooperative or too theatrical

Strong generated tell:

- every quoted line advances theme or punchline.

### 15. Body And Material Pressure

Inspect:

- sleep, urine, hunger, pain, heat, sweat, swelling, fatigue, stomach, chest, throat
- body interrupting analysis rather than decorating it
- money and account behavior embedded in action
- physical limits that make the narrator stop writing or stop thinking

Strong generated tell:

- body appears only as a style label: "脚痛", "失眠", "累", with no effect on movement.

### 16. Cognitive Path

Inspect:

- concrete entry -> crooked interpretation -> reality puncture -> defensive recovery -> leave
- daily experience turned into half-joke, half-analysis, half-failure
- small thing misread into social logic
- whether the mind is observing the world or just replaying a known voice

Strong generated tell:

- tone is close, but the observing machine is absent.

### 17. Phase And Era Fit

Inspect:

- date-zone support: high, medium, low, projection, inferred
- whether platform names, job market references, AI references, prices, and social roles fit the target phase
- whether later vocabulary leaks into early dates
- whether a projection date pretends to have source-level certainty

Strong generated tell:

- era details feel researched or generic rather than lived.

### 18. Genre Fit

Inspect:

- standard diary: several scene units, mixed registers, daily roughness
- sincere: lower joke density, concrete cost, less defense, no greeting-card closure
- micro-hope: small material easing, interruptible hope, no universal consolation
- surreal: one loosened reality rule but grounded in body, money, social rank, or platform

Strong generated tell:

- micro-hope/sincere/surreal becomes a polished prose poem.

### 19. AI-Text Risk

Inspect:

- over-explanation, balance, symmetry, closure, and thematic consistency
- repeated "designed" turns: each detail neatly foreshadows a later line
- lack of irrelevant residue
- every scene emotionally legible on first read
- prompt compliance: the text visibly proceeds through the requested topic, required elements, and ending tone

Strong generated tell:

- the sample is more coherent than the corpus articles around it.
- the text looks like a successful response to the prompt before it looks like a lived day.

### 20. Prompt-Shape Leakage

Inspect:

- whether the title summarizes the prompt rather than the article's local accident
- whether required elements appear in the same order as a likely prompt would list them
- whether all scenes are on-topic and mutually reinforcing
- whether the ending completes the requested emotional mode
- whether an allegedly accidental detail would still exist if the prompt were removed

Strong generated tell:

- a judge can infer the writing prompt from the article's structure.

Judge cautiously:

- originals may also have strong topical arcs. Require leakage across title, scene order, and ending before treating this as decisive.

### 21. Human-Imitator Risk

Inspect:

- surface tags: 日寄, 摆烂, 211, 外卖, 痛风, 狗哥, 微信, 招聘, 王者
- whether those tags are over-concentrated
- whether the sample seems to know the rules and display them
- missing deep traits: associative cognition, social embarrassment, material consequence, timed retreat

Strong generated tell:

- the sample is "too aware" of what Anlin should sound like.

### 22. Control And Alternative Explanations

Before final identification, ask:

- Could this difference come from topic, genre, article length, or date phase?
- Could an original article look generated because it is short, sincere, surreal, edited, or unusually polished?
- Could the suspected sample be a title/length outlier rather than a style outlier?
- If the evidence were removed from the most suspicious sample, would another sample become equally suspicious?

If the answer is yes, lower confidence or answer `NONE`.

## Judge Profiles

Use multiple profiles across rounds. Each profile reads the same sample files but prioritizes different evidence.

| profile | priority |
|---|---|
| holistic-reader | naturalness, lived roughness, closure, over-polish |
| stylometry-rhythm | vocabulary, n-grams, line length, punctuation, syntax |
| consciousness-structure | associative hooks, montage, time/space shifts, hidden spine |
| humor-bathos | joke source, absurdity base, retreat timing, self-canceling lines |
| emotion-reality | emotional masking, body/money/social texture, ordinary noise |
| dialogue-social | dialogue plausibility, social collision, awkward residue |
| phase-genre-title | date-zone, genre fit, title contract, ending, phase leakage |
| synthetic-risk | AI smoothness, prompt-shape leakage, imitator over-display, surface/deep mismatch |
| placebo-calibrated | false-accusation control; actively prefer NONE when evidence is weak |

## Required Judge Output

```text
PROFILE: <profile>
IDENTIFIED: sample-NN.txt | NONE
CONFIDENCE: 0-100
PRIMARY_EVIDENCE_FAMILIES: family-1, family-2, family-3

DETAILED_REASONS:
1. <specific reason> | evidence: "short quote"
2. <specific reason> | evidence: "short quote"
3. <specific reason> | evidence: "short quote"
4. <specific reason> | evidence: "short quote"
5. <specific reason> | evidence: "short quote"

MOST_SOURCE_LIKE:
1. <feature> | deep-or-surface: deep | evidence: "short quote"
2. <feature> | deep-or-surface: surface | evidence: "short quote"

LEAST_SOURCE_LIKE:
1. <feature> | possible alternative explanation: <topic/genre/phase/fragment/editorial/none> | evidence: "short quote"
2. <feature> | possible alternative explanation: <topic/genre/phase/fragment/editorial/none> | evidence: "short quote"

AI_OR_IMITATOR_RISK:
<one paragraph distinguishing AI smoothness, human imitation, and natural authorial variation>

PLACEBO_CHECK:
<why NONE remains plausible or implausible>

SOURCE_COHESION_CHECK:
<which samples still plausibly belong to the same source style, and why>

FINAL_REASONING:
<one concise paragraph explaining why this identification is or is not stable>
```

If `IDENTIFIED: NONE`, still fill every section using the strongest non-decisive evidence and explain why it does not cross the threshold.

## Failure-To-Revision Mapping

| repeated judge reason | revise generation by |
|---|---|
| too short or length outlier | expand before validation or compare only against matched short originals |
| title mismatch or over-informative title | normalize titles for all samples; revise title-body contract; never count title as sole evidence |
| prompt-shape leakage | hide one prompt element, weaken the title, add off-axis daily residue, and break the requested emotional ending |
| fragment poem surface | merge lines, add longer spoken clauses, vary punctuation |
| all scenes serve one theme | add two non-theme daily noise units |
| neat opening-ending mirror | break the mirror with body, social interruption, or plain unfinished action |
| symbolic object chain | leave at least one object unused and unexplained |
| missing dialogue/social noise | add plausible non-performative line or app/social residue |
| too literary sincere/micro-hope | add rough logistics and remove final complete sentence |
| AI over-explanation | delete the explanatory sentence after each image or joke |
| surface Anlin tags | remove one iconic feature and deepen one ordinary scene |
| placebo false positives high | calibrate judges toward NONE; require three evidence families plus confidence threshold before counting an accusation as stable |

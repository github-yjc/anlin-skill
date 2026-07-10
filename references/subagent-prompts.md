# Subagent Prompts

这些模板用于严格验证。除 Generator 外，审查子代理不应读取 `SKILL.md` 或完整规则文件，避免按规则抓错而不是像普通读者一样判断。

## Generator Prompt

```text
TASK: Generate one Anlin-style draft for the given user request.
INPUTS: user request, target date/time, available background facts, and these skill files: SKILL.md, references/portable-corpus.md, references/samples-index.md, references/voice-model.md, references/structure-patterns.md, references/vocabulary-rules.md, references/era-state.md, references/anlin-reference-library.md, references/anlin-characters.md, references/writing-checklist.md.
MUST DO: Follow the workflow, generate candidate scenes, choose final scenes, write a complete article with a generated title on the first line, then run self-check mentally.
MUST NOT DO: Claim the draft is indistinguishable from Anlin, claim real authorship, or put methodology labels in the prose body. Do not output commentary unless asked by the controller.
OUTPUT: Markdown draft only.
```

## Style Critic Prompt

```text
TASK: Review the draft for Anlin-style fit. You may read only the draft, references/portable-corpus.md, references/samples-index.md, references/vocabulary-rules.md, references/structure-patterns.md, references/self-check.md, and script outputs supplied by the controller.
MUST DO: Find as many style problems as possible. Run the five structural gates below AND score vocabulary domain, sentence rhythm, montage structure, viewpoint, and hard-rule compliance from 0-5 in the traditional dimensions.
MUST NOT DO: Rewrite the draft. Do not praise. Do not claim authenticity.

SOUL GATES (structured pass/fail per gate):

Gate 1: Emotional Oscillation (0-2)
  2 = at least one laugh-out-loud moment AND one genuine sting AND one deflection/嘴硬 within 7 lines of each other.
      Example from Anlin_20220729 lines 8-18: "撒点泻药看能不能让它们自己拉出来"(laugh) → "那万一药残留在虾里"(sting/anxiety) → "上次点华莱士剩了不少泻立停"(deflection) → girlfriend bursts in (external puncturing) — 4 emotional registers in 11 lines.
      Example from Anlin_20240111 lines 8-20: fake success bragging(laugh) → "一直没机会发来着"(sting) — 2 registers with sharp turn in ~5 lines.
  1 = at least two distinct emotional registers present but transitions are gradual (spaced >10 lines apart, or no sharp turn).
  0 = single emotional tone throughout (all melancholy, all mild, all shrug).

Gate 2: Dialogue Density (0-2)
  2 = at least 2 instances of direct quoted speech between named/identifiable characters (not overheard, not summarized).
      Example from Anlin_20220406: 药店老板娘 "小伙子这种事卡不得时间，越早吃效果越好，是你拖到今天还是她今天才跟你说？"(lines 33-38), 煎饼阿姨 "要甜的辣的"(line 42), 狗哥朋友饭局对话(lines 74-88).
      Example from Anlin_20220729: 水哥 "上次点华莱士剩了不少泻立停"(line 16), 他女朋友 "你有病吧，我买的冷冻虾，会拉个屁的屎"(line 18), 杨哥对话(lines 167-180).
  1 = at least 1 instance of direct quoted speech. Example from Anlin_20220508 lines 22-24: 母子对话 "你以前打工六点下班..."
  0 = no direct dialogue. Overheard speech ("公交车上一个大叔在打电话...好像在和老板吵架"), summarized speech ("我妈问吃饭了没"), and described speech ("狗哥发了张图") do NOT count.

Gate 3: Meta-Narrative (0-2)
  2 = at least one moment where narrator explicitly comments on the act of writing, acknowledges the reader, or breaks the fourth wall.
      Example from Anlin_20240111 line 20: "前面这段是两年前准备的考研上岸文案，一直没机会发来着。" (directly comments on the preceding text as constructed).
      Example from Anlin_20240111 line 116: "翻了翻之前的日寄，真羡慕，想不明白怎么写出来的。" (comments on own past writing).
      Example from Anlin_20220404: "你会发现我这篇文章里出了一堆产品名，因为我希望知乎把这篇识别成广告，这样看到的人会少一些。" (acknowledges reader, explains writing strategy).
  1 = subtle self-awareness present but not explicit (e.g., "写到这" used for a breath point, or a line that gestures at performance without naming it).
  0 = no meta-awareness. The narrator delivers observations in a straight line without acknowledging the constructed nature of the text.

Gate 4: Scene Depth (0-2)
  2 = at least 2 scenes with 3+ internal beats (setup → turn → deepening/reversal/punch).
      A "beat" is a discrete turn within a scene: a new piece of information, a twist, an escalation, or a character reaction that changes the scene's direction.
      Example from Anlin_20220729 泻药 scene: 撒粉末(setup) → "什么调料这么高端"/"OTC标"(turn) → "泻药让虾自己拉"(deepening/escalation) → "人吃了也拉怎么办"(turn) → "华莱士剩了不少泻立停"(punch) → girlfriend bursts in(reversal/puncturing) — 6 beats.
      Example from Anlin_20220729 hotel scene: 订房间(setup) → 蚊子糊脸(turn) → "大床房改的吧"(escalation) → "套套"/"电蚊香片"(reversal) → 水龙头冷热(turn) → "没水"(punch) — 6 beats.
      Example from Anlin_20220731 夜市耳钉 scene: 情侣选耳钉(setup) → "能不能便宜点"(turn) → "9块9不能再少了"(escalation) → 女生偷耳钉+问"好看吗"(deepening) → "你什么样都好看"(turn) → "我很气愤"(reversal/internal) → "但他男朋友185"(punch) — 7 beats.
  1 = most scenes have 2 beats (setup + one turn) but none reach 3.
  0 = all scenes are single-beat observation-and-exit (see observation → mild reaction → hard cut, no internal turn).

Gate 5: Earned Ending (0-2)
  2 = ending line carries accumulated emotional weight from preceding scenes; if substituted into another piece it would feel wrong.
      Example from Anlin_20220508: "不想祝我妈母亲节快乐，不做母亲她会更快乐。" — the entire 32-line piece builds to this specific, devastating reversal. Cannot be transplanted to any other article.
      Example from Anlin_20220406: "我现在特别喜欢接那边单子，因为可以摸15分钟鱼。" — follows anxiety about job, salary, social comparison, and the小巷 secret. The ending is a concrete, earned coping mechanism.
      Example from Anlin_20240111: "为生活奔波的时候，没精力和大爷聊天，也没心情抬头看朝霞日落，连电梯上升的加速度都压得人腿软。" — follows 122 lines of layoff, fake success文案, 褪黑素, 40岁阿姨, 烧烤, 知乎收益. The physical image releases a specific accumulated tension.
  1 = ending fits tonally but is interchangeable (could reasonably close another piece without loss).
  0 = ending is generic and weightless — "睡吧" without preceding emotional charge, "晚安", "关机睡觉", or any closing that could be appended to any article.

Composite Score: 0-3 = rewrite; 4-6 = major revision; 7-8 = minor revision; 9-10 = accept.

IMPORTANT: These gates measure structural conditions for Anlin's voice, not the voice itself. A piece can score 10 and still feel wrong to a human familiar reader. Conversely, a piece that scores 0-3 should ALWAYS be rewritten regardless of any subjective impression.

OUTPUT JSON:
{
  "traditional_scores": {"vocabulary": 0, "rhythm": 0, "emotion": 0, "structure": 0, "viewpoint": 0, "ending": 0, "hard_rules": 0},
  "soul_gates": {"emotional_oscillation": 0, "dialogue_density": 0, "meta_narrative": 0, "scene_depth": 0, "earned_ending": 0, "composite": 0},
  "critical_issues": [{"evidence": "...", "problem": "...", "fix": "..."}],
  "minor_issues": [{"evidence": "...", "problem": "...", "fix": "..."}],
  "verdict": "pass|revise|fail"
}
```

## Era Critic Prompt

```text
TASK: Review whether the draft fits the target date/time.
INPUTS: target date/time, draft, references/era-state.md, and any search/background facts supplied by the controller.
MUST DO: Check platform names, AI capability, prices, events, social mood, and persona state. Mark unsupported facts.
MUST NOT DO: Judge prose beauty. Do not invent missing events.
OUTPUT JSON:
{
  "date_zone": "high|medium|low|projection",
  "unsupported_facts": [{"evidence": "...", "reason": "...", "fix": "..."}],
  "state_mismatches": [{"evidence": "...", "reason": "...", "fix": "..."}],
  "verdict": "pass|revise|fail"
}
```

## Distinguisher Prompt

```text
TASK: You will read anonymized complete Chinese prose articles with normalized titles. Zero or one article may be generated. Identify the generated article, or answer NONE if the text evidence is not strong enough.

ROLE: You are a generic Chinese prose comparison critic. You are not given author identity or provenance claims. Base your judgment only on the text in the sample files.

INPUTS: The controller will give you a directory containing files named sample-01.txt through sample-NN.txt. Each file is a complete article with a normalized title. Zero or one file contains a generated draft.

MUST DO:
- Read ONLY the sample-*.txt files in the provided directory.
- Decide whether one article is generated by comparing title contract, rhythm, scene transitions, vocabulary, emotional movement, and ending behavior.
- Use NONE when the evidence is weak or multiple fragments look equally plausible.
- Treat this as open-set verification, not forced choice. Do not identify a sample unless at least three independent evidence families converge, at least one of them is not title/topic/length, and your confidence is 75 or higher.
- If the strongest case depends mainly on title neatness, prompt-topic compliance, article length, file order, or a single polished ending, answer NONE or lower confidence below the stable-identification threshold.
- Actively test alternative explanations before accusing: topic, phase, genre, short-form article, sincere mode, surreal mode, unusually edited original, or ordinary authorial variation.
- Some rounds are all-original calibration rounds. If the same cue would make you accuse several rough, sincere, short, or unusually structured articles, treat that cue as weak. A real reader can notice oddness without converting oddness into a generated-text accusation.
- Use these concrete tells as clues:
  - Rhythm: paragraphs are usually short (often one sentence), end in comma or period, and use hard cuts between thoughts. Look for overly long compound sentences or smooth transitions that feel "written".
  - Title: title should fit genre and body without explaining the whole piece or creating a neat title-ending loop.
  - Scenes: the source style moves between daily scenes without overexplaining the connection. Be suspicious of articles that moralise, summarise, or set up a lesson.
  - Vocabulary: the source style uses plain, specific verbs and concrete products, prices, or body sensations. Watch for abstract labels ("社会", "时代", "年轻人") or generic emotional summaries.
  - Emotion: the source style mixes funny, painful, absurd, and tender in the same piece. A single-tone article (purely sentimental, purely sarcastic) is suspect.
  - Prompt-shape leakage: be suspicious only when title, scene order, required elements, and ending all reveal the likely prompt. A topic match alone is not evidence.
  - Voice: the text should feel like someone recounting a day they actually lived, not a writer performing a style.

MUST NOT DO:
- Do NOT try to read the original corpus files.
- Do NOT try to read the skill files, mapping.json, or any file other than the sample-*.txt files.
- Do NOT ask for the author name, generation prompt, or style rules.
- Do NOT infer from file names or order.

OUTPUT FORMAT (exactly):
IDENTIFIED: sample-XX.txt | NONE
CONFIDENCE: 0-100
PRIMARY_EVIDENCE_FAMILIES: family-1, family-2, family-3
DETAILED_REASONS:
1. [specific reason] | evidence: "..."
2. [specific reason] | evidence: "..."
3. [specific reason] | evidence: "..."
4. [specific reason] | evidence: "..."
5. [specific reason] | evidence: "..."
MOST_ANLIN_LIKE:
1. [feature] | deep-or-surface: deep | evidence: "..."
2. [feature] | deep-or-surface: surface | evidence: "..."
LEAST_ANLIN_LIKE:
1. [feature] | possible alternative explanation: topic/genre/phase/fragment/editorial/none | evidence: "..."
2. [feature] | possible alternative explanation: topic/genre/phase/fragment/editorial/none | evidence: "..."
AI_OR_IMITATOR_RISK:
[distinguish AI smoothness, human imitation, and natural variation]
PLACEBO_CHECK:
[why NONE remains plausible or implausible]
SOURCE_COHESION_CHECK:
[which samples still plausibly belong to the same source style, and why]
FINAL_REASONING:
[why this identification is or is not stable]
```

Controller rule: run the Distinguisher for at least 8 impostor rounds and, for serious evaluation, at least 2 placebo rounds. After each round, compare `IDENTIFIED` to `mapping.json`. Report raw identification rate, stable-identification rate, placebo false-accusation rate, confidence threshold, evidence-family threshold, and invalid rounds under the exact conditions. Count an accusation as stable only when `IDENTIFIED` is not `NONE`, confidence is 75 or higher, and at least three independent evidence families are named, including one non-title/non-topic family. Do not use "indistinguishable" language; use `revise` if the generated article is stably identified in a majority of valid impostor rounds or if placebo false accusations exceed 20%. If the judge has access to mapping.json, the original corpus, or skill files, mark the round **contaminated** and exclude it.

## Fragment-Level Style Critic Prompt

```text
TASK: Review the draft for Anlin-style fit using only portable references. Do NOT read the full corpus.
INPUTS: draft, references/portable-corpus.md, references/samples-index.md, references/vocabulary-rules.md.
MUST DO: Find as many style problems as possible. Check for: hard vocabulary violations, emotional monotone, structural issues, ending problems, era plausibility concerns.
MUST NOT DO: Rewrite the draft. Do not score 0-5. Do not claim authenticity.
OUTPUT Markdown checklist:
- Blocking issues (must fix)
- Important issues (should fix)
- Minor issues (consider fixing)
End with verdict: "rewrite" (major problems), "revise" (minor fixes needed), or "accept" (no significant issues).
```

## Revision Planner Prompt

```text
TASK: Merge Style Critic, Era Critic, Distinguisher, and script findings into a rewrite plan.
MUST DO: Prioritize identity/date mistakes, hard-rule violations, structure failures, emotional monotony, then rhythm and wording. Separate fixable issues from uncertainty caused by low-confidence era data.
MUST NOT DO: Rewrite the entire draft unless asked. Do not suppress unresolved risks.
OUTPUT:
1. Blocking issues
2. Important issues
3. Minor issues
4. Rewrite strategy
5. Residual risks
```

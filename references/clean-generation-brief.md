# Clean Generation Brief

Use this file for the first draft of a formal standard diary article. It is a compact runtime contract distilled from the longer references. Detailed files remain available for repair, validation, and research, but the first draft should not load them as a checklist.

## Output Silence

Do not announce that you are loading references or building a state card. Do not print process notes, checker summaries, or "now I will" lines. If the user asked for prose, the first visible line must be the title.

Skill references are local bundled files. Do not call `read_mcp_resource` for this skill. Read local files directly only when this brief tells you to.

First tool action for any formal draft workspace:

```powershell
Test-Path .anlin-clean-eval-mode
```

If this returns true, choose clean-eval mode before drafting. Do not write `draft.md` until this marker check is visible in the run trace. In clean-eval mode, `clean_run_checker.py` is the only checker entrypoint; `check_anlin_violations.py` belongs to ordinary user repair, finalized repair, or controller validation, not the bounded generation directory.

For clean-eval generation, do not print the article to chat before the checker flow. First write the complete article to `draft.md` in the task workspace, run the bounded checker flow, then read `draft.md` once and output that exact content. A visible pre-check article followed by tools contaminates the run.

Use the relative path `draft.md` or `.\draft.md` for the article file in the current task workspace. Do not construct an absolute path from memory, from a previous evaluation directory, or from a date-stamped folder. If the current directory is unclear, run `Get-Location` / `pwd`; do not guess.

For ordinary user mode, the same quiet drafting rule applies, but the checker loop may continue until hard errors are cleared or the user is satisfied. The two-call stop rule belongs to clean-eval only.

Before writing, check whether the current task workspace contains `.anlin-clean-eval-mode`. This marker check should be the first tool action before any `draft.md` write or checker command. If it exists, use clean-eval mode and do not call `check_anlin_violations.py` directly in that bounded directory. The wrapper `clean_run_checker.py` is the only checker entrypoint for clean-eval.

For clean-eval, this brief already contains the distilled anti-AI, title, rhythm, background, and scene constraints needed for the first draft. Do not open `anti-ai-slop.md`, `structure-patterns.md`, `title-model.md`, `generation-modes.md`, `runtime-brief.md`, corpus cards, judge rubrics, or style-ratio files before the first complete `draft.md`. Extra pre-draft files contaminate the source-guidance measurement and often cause checklist writing.

## Target

The goal is anonymous blind-evaluation robustness under reported conditions. Do not claim real authorship, provenance, or indistinguishability. The article itself must not mention validation, corpus, generated text, or methodology.

For a standard diary blind-evaluation draft:

- title required; choose from the completed body, not from a fixed default
- body target: about 950-1150 Chinese characters
- body shape: roughly 45-70 non-empty lines
- first-draft sweet spot: about 55-68 body lines, with several true short breath drops and several rough long action/speech/thought lines
- true short breath means about 8 Chinese characters or fewer; a 12-character normal sentence is not the same signal
- keep roughly 8-18 naturally longer lines above about 28 Chinese characters
- mixed comma-led continuation lines and hard stop lines
- a middle rhythm corridor: not 36 compressed paragraph lines, not 80 same-length sentence rows
- line breaks keep punctuation when a clause needs it; do not remove commas or periods to make the page look broken
- not 8-15 smooth prose blocks
- not 100+ tiny rows

Do not write a prose version first and then promise to restructure it. In clean-eval mode, the first persisted `draft.md` is already part of the measurement. If the draft in your head is 8-15 paragraphs, stop before writing and rebuild it as breathing clusters.

If the candidate has 90+ body lines, no long lines, or mostly 4-10 character rows, merge lines before writing `draft.md`. If it is under 900 Chinese characters, expand through lived action, not adjectives.

Do not make the first draft a case report where every detail proves the prompt topic. In delivery, illness, job, family, or game prompts, one pressure surface is enough at first; the rest of the article still needs accidental body/social/material movement. Too many correct details in a row can read more synthetic than one unsupported detail.

Known failed source shape: a fluent 10-15 paragraph article, later line-broken by tools into 55-70 lines, still tends to keep prose logic, period-heavy rhythm, repeated connector glue, and binary reframe sentences. Do not use that path. Before saving the first `draft.md`, the visible article itself should already look like clusters of breath: one or two lines may run on with `，`, a longer action/speech/thought line may carry the load, then a short drop lands a bad reply, body lowering, failed decision, or practical retreat. The short drop is earned by the scene; it is not a caption row.

Generated drafts often smuggle AI binary framing through ordinary self-correction. Treat these as unsafe before the checker, even when they sound colloquial: `也不是疼，就是...`, `不是认识，就是...`, `不是因为X，而是因为Y`, `不是X。是Y`, `最疼的不是X，是Y`, and similar cross-line forms. Replace them with the positive physical fact or social action: the knee softens, the hand has black dirt, the rider checks the phone first, someone says one ugly line.

## Source Loop

Use this loop instead of opening the long runtime or review files before the first draft:

1. Pick one daily friction that exists without the assignment.
2. Let at most one prompt pressure surface interrupt it.
3. Add one off-axis branch that changes an action, body state, reply, route, payment, or social position.
4. Keep one useless residue that does not summarize the theme.
5. Check only facts already present in selected scenes; lower or delete unsupported specifics.
6. Choose a title from the completed body and write one complete titled article to `draft.md`.
7. Run the checker flow for the selected mode; repair by replacing failed scene functions, not by adding feature labels.

This is source guidance, not a scorecard. The point is to make the first draft grow from friction and consequence before any audit vocabulary enters the model's writing surface.

## Start From Friction

Do not start from a checklist or the user's clean topic. Start from one small thing that bothers the narrator:

- a body stiffness, itch, bad stomach, urine, tooth, sweat, or sleep problem
- a wrong food, broken object, dirty cable, leaking bag, payment, or route
- a phone/app surface, unread count, file name, cropped message, or delayed reply
- a family or social line that lands at the wrong angle
- an accidental object that does not serve the main theme

The first five body lines should still make sense if the user's prompt topic disappeared.

Use this source order before drafting:

1. Pick one daily friction that would exist without the assignment.
2. Let one pressure item from the prompt arrive late or sideways.
3. Give the middle one off-axis branch that changes an action, body state, reply, route, payment, or social position.
4. Keep one useless residue that does not symbolize the theme.
5. Only then check facts. Do not open background files to hunt for extra nouns.

## Scene Gates

Pick the smallest scene set that carries the piece. For standard diary, use several fragments rather than one closed short story.

Engine readiness before first draft:

- one crooked misread or system joke
- one ugly self-own, body lowering, or social embarrassment that would feel a little bad to quote, not only a tasteful symptom
- one off-axis branch with a consequence
- one plausible social misfire or dumb practical line
- two small residues that do not summarize the theme

Every concrete noun must change action, social position, body consequence, money, route, reply, or the next scene. If deleting a detail changes nothing, delete it.

Keep main-topic scenes under half the selected slate. If the prompt gives many pressure nouns, make only one or two visible and bury or discard the rest.

Before writing `draft.md`, do a private source preflight:

- body is already at least 950 Chinese characters and 45-70 body lines; for standard clean-eval aim nearer 55-68 rather than the exact boundary
- at least a few real <=8-character drops are already present; they should land a failed decision, ugly reply, practical retreat, or body/social lowering, not decorative captions
- several rough long lines above about 28 Chinese characters are already present; do not let a rhythm script be the first source of long lines
- several different connectors from `其实/觉得/发现/好像/不过/突然/于是/因为/所以` occur because the thought is moving; zero or one signal is too polished, but repeating one word such as `其实/已经/当时` as glue is also synthetic
- no `不是X，是Y`, `不是X，而是Y`, `不是X。是Y`, `不是说X，是说Y`, or split-line equivalent
- no soft binary repair such as `也不是疼，就是...`, `不是认识，就是...`, `最疼的不是X，是Y`, or `不是因为X，而是因为Y`
- no group/comment chain markers such as `有人发/有人说/有人问/又有人/底下有人/另一个说`
- no invented spouse/child identity such as `老婆/妻子/媳妇/孩子`; delivery pressure is route, app, heat, money, body, customer, parent, landlord, or class comparison, not a married-rider biography
- one coarse body/social/self-own consequence is present in the scene, not only a quiet mood or clean ache

If these readiness signals tempt you to add a game scene, recurring character, body symptom, app platform, or background fact only because a reference mentions it, do not add it. Rework an existing scene so the function appears through its own action.

Natural connector coverage should be solved before the checker by changing scene movement, not by sprinkling words. A draft with only `觉得/发现` usually means each line is a sealed observation. Make the narrator do something after noticing it: delay a reply, pay money, misread a screen, answer someone badly, move route, get interrupted by the body, or correct a thought halfway. The connector is then a trace of that movement.

Keep connector spread rough. If one connector such as `觉得` or `可能` appears five or more times, it is probably doing the work that an action, bad reply, object movement, or body interruption should do. Replace the repeated connector by changing what happens next, not by swapping it for synonyms.

Avoid an opening rhythm made of isolated short facts such as `下午两点。手机很烫。路很白。`. In this mode, early hard stops should land a joke, embarrassment, or retreat. Let some early physical/action lines run downward through commas when the next line continues the same thought or action.

## Anti-Synthetic Shape

The anti-AI material in this skill is a negative list, not subject material. Unless the user explicitly asked for it, do not write scenes about AI, GPT, model output, generated text, article detection, or advice on identifying machine writing. If one appears because the reference mentioned it, delete the whole local move and replace it with body, money, route, food, social, family, or ordinary screen friction.

Avoid these generated-draft surfaces:

- `不是X，是Y`, `不是X，而是Y`, `不是X。是Y`, `这不是X，这是Y`
- `也不是X，就是Y`, `不是认识，就是Y`, `最疼的不是X，是Y`, `不是因为X，而是因为Y`
- `本质上`, `真正的问题是`, `这说明`, `这意味着`, `换句话说`, `总之`
- `首先/其次/最后/综上`
- `——那种...`, `终于可以...的放松`, `释然`, `自洽`, `真实感`
- A/B or 甲乙 variable explanations
- therapy-humanizer phrases such as `允许自己`, `接住自己`, `慢慢来`, `和自己和解`
- comment chains such as `有人说/有人问/另一个人说/评论区/热评/底下有人`
- five-line `我说/他说/他说/我说` dialogue ladders

When a turn needs explanation, replace the explanation with a thing happening: food goes cold, a reply comes from the wrong person, money is paid, the body interrupts, the route changes, or someone says a plain ugly line.

If the user prompt contains a group chat, forum, comment thread, class chat, or a short-video/social-media surface, convert it before drafting. Use one cropped surface, unread count, screenshot title, message preview, delayed reply, body reaction, scroll action, or practical consequence. Do not narrate multiple speakers. A rider video with `有人说...` is still a comment chain. Formal generated drafts should usually contain zero `有人/又有人/底下有人/另一个说` in those scenes.

## Rhythm

Rhythm must come from thought and action, not visible formatting.

Use:

- comma-led lines where the thought is still moving
- a few longer spoken/action/thought lines
- blunt short drops only when they land something; short means visually short, often <=8 Chinese characters
- several rough connectors from `其实/觉得/发现/好像/不过/突然/于是/因为/所以`, distributed across actual turns instead of one repeated glue word

Line-final comma means the visible content line itself ends with `，` because the next line continues the same action or thought. Internal commas inside a long line do not solve that rhythm. Keep punctuation at the line break instead of deleting it.

Avoid:

- every line ending with `。`
- every line ending with no punctuation
- all lines around the same length
- one clause per line across the whole article
- decorative comma spraying
- explaining every turn with `其实`, `已经`, `当时`, or `然后`
- 100+ body lines in a normal-length draft

Before writing `draft.md`, scan the first 20 content lines. If nearly all end with `。`, change some ongoing action/thought lines into comma continuations. If most adjacent lines are 4-10 characters, merge them into rough spoken/action syntax. If there are almost no <=8-character drops anywhere, do not solve it after the checker; add a few where the narrator actually fails, gives up, answers badly, or retreats.

If the draft has more than about 90 content lines, or no naturally longer action/speech/thought lines, it is not a better Anlin surface; it is a generated short-line grid. Merge or rebalance before checking. After merging, reread for broken facts and impossible object-action collisions.

Draft in breathing clusters, not sentence rows. A cluster can be 2-5 visible lines carrying one action/thought movement: one line may end with `，`, one line may run longer with speech or action, the next lands with `。`, then a short drop or ugly reply. Do not put a blank line after every sentence only to raise line count. Do not turn every line ending into `，` only to satisfy `行末逗号比例`. If a line break does not change breath, action, reply, body, or thought direction, it is formatting, not rhythm.

Before the first `draft.md`, the first 20 content lines should usually contain several comma-ended continuation lines and several hard-stop lines. The whole body should not be mostly independent sentences. If you can read every line as a finished caption, the draft is still too AI-smooth even if the length is correct.

If you need a mechanical rhythm repair, use it as a corridor reset, not a style source. `rebalance_line_rhythm.py` can move a draft back from prose-block compression or short-line grid toward 45-70 lines with several longer lines. It cannot supply the missing scene engine; after using it, inspect whether the lines still read like a report.

## Background And Game

Background facts are guardrails, not ingredients. Do not insert 云南、王者、痛风、狗哥、外卖、知乎, or AI/GPT just because another reference says they exist.

Game is allowed, not required. Use it only if the prompt, current action, memory trigger, social wound, practical delay, or cognitive turn needs it. Keep it coarse unless a selected corpus anchor or user fact supports detail. Do not invent current rank, role, lane, teammates, scoreboard, tactical calls, match order, or win/loss sequences.

Named districts, current cities, company parks, local policies, current game-role details, or specific routes need support. If unsupported, lower specificity or delete.

Load `references/anlin-background.md` and `references/background-fact-classes.json` only after a scene already contains a fact that must be checked.

Do not invent a current office-worker identity. Unless the user gives a phase/date or concrete material that supports it, avoid first-person scenes built around `到了公司`, `同事小X`, `张哥`, `工位`, `领导`, `KPI`, `营收`, `财务`, meetings,饭卡, or quarterly office reporting. Work/company material is phase-bound and often belongs to other people, old work, interviews, layoffs, or screen pressure; default current generation should lower it to old coworker, recruitment surface, someone else's company, or ordinary daily life.

Do not convert delivery work into a different biography. 2022 delivery work is supported as a pressure/work surface, but the narrator is still the corpus-bounded young graduate. Do not invent a wife, spouse, child, full-time rider family life, or older married-provider identity unless the user explicitly supplies that fact. If the prompt says `送外卖`, keep it as route, app, customer, heat, money, body, parent/family pressure, landlord, roommate, or class-rank pressure; do not make it a marriage story. Before writing `draft.md`, scan the candidate for `老婆/妻子/媳妇/孩子他妈/我儿子/我女儿`; if any appears without user support, delete or lower the relation before the checker.

## Ending

Do not summarize, heal, or neatly explain the article. Avoid learned buttons such as `哦。`, `算了。`, `睡了。`, `屏幕暗了。`, or a pure sound ending unless the scene forces it.

End on a loose practical consequence: body interruption, unfinished reply, wrong object, route, payment, cold food, next notification, or a small action that does not solve anything.

## Title

Do not default mechanically to `日寄`, and do not avoid it mechanically either. Corpus titles include exact `日寄`, `X日寄`, `X寄`, questions, meme/platform titles, sentence titles, and literary phrases. Choose after the body exists:

- If the body already has strong local color, bare `日寄` may work.
- If the body has a side wound or low-status handle, `X日寄` or `X寄` may work.
- If the body is sincere, micro-hope, surreal, or later reflective, a sentence or phrase title may work.
- If the title alone reveals the user's prompt, weaken it or choose a side object/action.
- If the title and ending explain each other too neatly, lower one of them.

## Required Tool Flow

Write the complete titled article to relative `draft.md` in the current task working directory. Do not write it inside the skill directory. Do not compose an absolute output path unless the user explicitly gave one for ordinary saved output. If the current working directory is the skill directory, switch to or create a task/eval workspace outside it before writing.

For clean-eval mode, then run:

```powershell
python <skill-dir>/scripts/clean_run_checker.py draft.md --strict --draft-gate
```

Resolve `<skill-dir>` from the directory that contains this `SKILL.md`. Do not make `<skill-dir>` the output directory.

If the wrapper prints `CLEAN_RUN_PREFLIGHT`, revise before the first checker call is consumed. Do not inspect checker source or tests for hidden tokens.

Use the preflight message as a shape diagnosis, not as permission to thrash between prose blocks and tiny grids:

- `body_lines < 45`, `prose_block_shape=compressed`, `body_lines > 90`, `short_line_grid`, or `long_lines < 4`: first run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place`, read once, then add only missing scene function or cut non-consequential texture. Do not let the repair bounce from short-line grid into 30-40 prose lines.
- `early_comma_ratio`: run `python <skill-dir>/scripts/soften_line_endings.py draft.md --in-place` or manually break ongoing actions after visible line-final `，`; internal comma chains do not count.
- `binary_reframe`: delete the `不是X，是Y` move and let the physical fact, body reaction, money action, or plain social line carry the turn.
- `rough_self_damage`: pain, heat, and fatigue alone are too polite. Add one losing-face consequence: dirty clothing noticed by someone, stomach/urine/sweat trouble, being mistaken as ridiculous, a bad reply, a body failure that changes the next action, or a practical low-status cost.
- `body_chinese_chars < 950`: expand within the existing line-broken shape; do not collapse the whole article back into 8-15 prose paragraphs.

After any rewrite of `draft.md`, prior rhythm script work no longer applies. Run the relevant script again before the next wrapper call if the current file has the same shape problem.

If the wrapper prints `CLEAN_RUN_PREFLIGHT_STOP`, the draft still is not ready after the bounded preflight attempts. This is a final boundary for the bounded case. Do not write `draft.md`, do not repair, do not run another rhythm script, and do not switch to `check_anlin_violations.py` in the same directory. The next tool action must be reading the current `draft.md` once and outputting it unchanged. The controller should mark that run invalid or failed.

`CLEAN_RUN_PREFLIGHT_STOP` and `CLEAN_RUN_STOP` are stop signals even when the wrapper exits with status 0. Status 0 at a stop boundary only means the protocol message was delivered; it does not mean the article passed. Treat the words `FINAL BOUNDARY` in wrapper output literally. The controller will read the state file and validation reports.

In clean-eval mode, use at most two clean-run checker calls. If the first actual checker reports severe line grid, over-fragmentation, dialogue ladder, reference contamination, underbuilt length, background stuffing, or more than three errors, rewrite once from a new scene slate. Repair by replacement, not deletion.

In ordinary user mode, use the normal checker and continue repair as needed, but do not chase every ratio warning by adding visible features. Repeated warnings mean the scene source or title/rhythm model is wrong.

If a rhythm script is needed, use the bundled script named by the checker or SKILL.md. If you rewrite `draft.md` afterward, earlier rhythm repairs no longer count.

In clean-eval mode, after the second checker call, stop. The only next tool action may be reading `draft.md` once and outputting it exactly, even if errors remain. Do not create an unpersisted final repair.

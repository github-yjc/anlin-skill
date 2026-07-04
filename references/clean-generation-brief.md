# Clean Generation Brief

Use this file for the first draft of a formal standard diary article. It is a compact runtime contract distilled from the longer references. Detailed files remain available for repair, validation, and research, but the first draft should not load them as a checklist.

## Output Silence

Do not announce that you are loading references or building a state card. Do not print process notes, checker summaries, or "now I will" lines. If the user asked for prose, the first visible line must be the title.

Skill references are local bundled files. Do not call `read_mcp_resource` for this skill. Read local files directly only when this brief tells you to.

For clean-eval generation, do not print the article to chat before the checker flow. First write the complete article to `draft.md` in the task workspace, run the bounded checker flow, then read `draft.md` once and output that exact content. A visible pre-check article followed by tools contaminates the run.

For ordinary user mode, the same quiet drafting rule applies, but the checker loop may continue until hard errors are cleared or the user is satisfied. The two-call stop rule belongs to clean-eval only.

## Target

The goal is anonymous blind-evaluation robustness under reported conditions. Do not claim real authorship, provenance, or indistinguishability. The article itself must not mention validation, corpus, generated text, or methodology.

For a standard diary blind-evaluation draft:

- title required; choose from the completed body, not from a fixed default
- body target: about 950-1150 Chinese characters
- body shape: roughly 45-70 non-empty lines
- at least six naturally longer lines above about 24 Chinese characters
- mixed comma-led continuation lines and hard stop lines
- not 8-15 smooth prose blocks
- not 100+ tiny rows

If the candidate has 90+ body lines, no long lines, or mostly 4-10 character rows, merge lines before writing `draft.md`. If it is under 900 Chinese characters, expand through lived action, not adjectives.

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
- one ugly self-own, body lowering, or social embarrassment
- one off-axis branch with a consequence
- one plausible social misfire or dumb practical line
- two small residues that do not summarize the theme

Every concrete noun must change action, social position, body consequence, money, route, reply, or the next scene. If deleting a detail changes nothing, delete it.

Keep main-topic scenes under half the selected slate. If the prompt gives many pressure nouns, make only one or two visible and bury or discard the rest.

If these readiness signals tempt you to add a game scene, recurring character, body symptom, app platform, or background fact only because a reference mentions it, do not add it. Rework an existing scene so the function appears through its own action.

## Anti-Synthetic Shape

The anti-AI material in this skill is a negative list, not subject material. Unless the user explicitly asked for it, do not write scenes about AI, GPT, model output, generated text, article detection, or advice on identifying machine writing. If one appears because the reference mentioned it, delete the whole local move and replace it with body, money, route, food, social, family, or ordinary screen friction.

Avoid these generated-draft surfaces:

- `不是X，是Y`, `不是X，而是Y`, `这不是X，这是Y`
- `本质上`, `真正的问题是`, `这说明`, `这意味着`, `换句话说`, `总之`
- `首先/其次/最后/综上`
- `——那种...`, `终于可以...的放松`, `释然`, `自洽`, `真实感`
- A/B or 甲乙 variable explanations
- therapy-humanizer phrases such as `允许自己`, `接住自己`, `慢慢来`, `和自己和解`
- comment chains such as `有人说/有人问/另一个人说/评论区/热评/底下有人`
- five-line `我说/他说/他说/我说` dialogue ladders

When a turn needs explanation, replace the explanation with a thing happening: food goes cold, a reply comes from the wrong person, money is paid, the body interrupts, the route changes, or someone says a plain ugly line.

## Rhythm

Rhythm must come from thought and action, not visible formatting.

Use:

- comma-led lines where the thought is still moving
- a few longer spoken/action/thought lines
- blunt short drops only when they land something
- some rough connectors from `其实/觉得/发现/好像/不过/突然/于是/因为/所以`

Avoid:

- every line ending with `。`
- all lines around the same length
- one clause per line across the whole article
- decorative comma spraying
- 100+ body lines in a normal-length draft

Before writing `draft.md`, scan the first 20 content lines. If nearly all end with `。`, change some ongoing action/thought lines into comma continuations. If most adjacent lines are 4-10 characters, merge them into rough spoken/action syntax.

## Background And Game

Background facts are guardrails, not ingredients. Do not insert 云南、王者、痛风、狗哥、外卖、知乎, or AI/GPT just because another reference says they exist.

Game is allowed, not required. Use it only if the prompt, current action, memory trigger, social wound, practical delay, or cognitive turn needs it. Keep it coarse unless a selected corpus anchor or user fact supports detail. Do not invent current rank, role, lane, teammates, scoreboard, tactical calls, match order, or win/loss sequences.

Named districts, current cities, company parks, local policies, current game-role details, or specific routes need support. If unsupported, lower specificity or delete.

Load `references/anlin-background.md` and `references/background-fact-classes.json` only after a scene already contains a fact that must be checked.

Do not invent a current office-worker identity. Unless the user gives a phase/date or concrete material that supports it, avoid first-person scenes built around `到了公司`, `同事小X`, `张哥`, `工位`, `领导`, `KPI`, `营收`, `财务`, meetings,饭卡, or quarterly office reporting. Work/company material is phase-bound and often belongs to other people, old work, interviews, layoffs, or screen pressure; default current generation should lower it to old coworker, recruitment surface, someone else's company, or ordinary daily life.

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

Write the complete titled article to `draft.md` in the current task working directory. Do not write it inside the skill directory. If the current working directory is the skill directory, switch to or create a task/eval workspace outside it before writing.

For clean-eval mode, then run:

```powershell
python <skill-dir>/scripts/clean_run_checker.py draft.md --strict --draft-gate
```

Resolve `<skill-dir>` from the directory that contains this `SKILL.md`. Do not make `<skill-dir>` the output directory.

If the wrapper prints `CLEAN_RUN_PREFLIGHT`, revise before the first checker call is consumed. Do not inspect checker source or tests for hidden tokens.

If the wrapper prints `CLEAN_RUN_PREFLIGHT_STOP`, the draft still is not ready after the bounded preflight attempts. Stop repair work for this clean-eval run, read the current `draft.md` once, and output it unchanged. The controller should mark that run invalid or failed; do not keep rewriting until the preflight disappears.

In clean-eval mode, use at most two clean-run checker calls. If the first actual checker reports severe line grid, over-fragmentation, dialogue ladder, reference contamination, underbuilt length, background stuffing, or more than three errors, rewrite once from a new scene slate. Repair by replacement, not deletion.

In ordinary user mode, use the normal checker and continue repair as needed, but do not chase every ratio warning by adding visible features. Repeated warnings mean the scene source or title/rhythm model is wrong.

If a rhythm script is needed, use the bundled script named by the checker or SKILL.md. If you rewrite `draft.md` afterward, earlier rhythm repairs no longer count.

In clean-eval mode, after the second checker call, stop. The only next tool action may be reading `draft.md` once and outputting it exactly, even if errors remain. Do not create an unpersisted final repair.

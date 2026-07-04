# Clean Generation Brief

Use this file for the first draft of a formal standard diary article. It is a compact runtime contract distilled from the longer references. Detailed files remain available for repair, validation, and research, but the first draft should not load them as a checklist.

## Output Silence

Do not announce that you are loading references or building a state card. Do not print process notes, checker summaries, or "now I will" lines. If the user asked for prose, the first visible line must be the title.

Skill references are local bundled files. Do not call `read_mcp_resource` for this skill. Read local files directly only when this brief tells you to.

## Target

The goal is anonymous blind-evaluation robustness under reported conditions. Do not claim real authorship, provenance, or indistinguishability. The article itself must not mention validation, corpus, generated text, or methodology.

For a standard diary blind-evaluation draft:

- title required; default `日寄`
- body target: about 950-1150 Chinese characters
- body shape: roughly 45-70 non-empty lines
- at least six naturally longer lines above about 24 Chinese characters
- mixed comma-led continuation lines and hard stop lines
- not 8-15 smooth prose blocks
- not 100+ tiny rows

If the candidate has 90+ body lines, no long lines, or mostly 4-10 character rows, merge lines before writing `draft.md`. If it is under 900 Chinese characters, expand through lived action, not adjectives.

## Start From Friction

Do not start from a checklist or the user's clean topic. Start from one small thing that bothers the narrator:

- a body stiffness, itch, bad stomach, urine, tooth, sweat, or sleep problem
- a wrong food, broken object, dirty cable, leaking bag, payment, or route
- a phone/app surface, unread count, file name, cropped message, or delayed reply
- a family or social line that lands at the wrong angle
- an accidental object that does not serve the main theme

The first five body lines should still make sense if the user's prompt topic disappeared.

## Scene Gates

Pick the smallest scene set that carries the piece. For standard diary, use several fragments rather than one closed short story.

Required before first draft:

- one crooked misread or system joke
- one ugly self-own, body lowering, or social embarrassment
- one off-axis branch with a consequence
- one plausible social misfire or dumb practical line
- two small residues that do not summarize the theme

Every concrete noun must change action, social position, body consequence, money, route, reply, or the next scene. If deleting a detail changes nothing, delete it.

Keep main-topic scenes under half the selected slate. If the prompt gives many pressure nouns, make only one or two visible and bury or discard the rest.

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

## Ending

Do not summarize, heal, or neatly explain the article. Avoid learned buttons such as `哦。`, `算了。`, `睡了。`, `屏幕暗了。`, or a pure sound ending unless the scene forces it.

End on a loose practical consequence: body interruption, unfinished reply, wrong object, route, payment, cold food, next notification, or a small action that does not solve anything.

## Required Tool Flow

Write the complete titled article to `draft.md` in the current working directory. Then run:

```powershell
python C:\Users\34025\.config\opencode\skills\anlin-writing\scripts\clean_run_checker.py draft.md --strict --draft-gate
```

If the wrapper prints `CLEAN_RUN_PREFLIGHT`, revise before the first checker call is consumed. Do not inspect checker source or tests for hidden tokens.

Use at most two clean-run checker calls. If the first actual checker reports severe line grid, over-fragmentation, dialogue ladder, reference contamination, underbuilt length, background stuffing, or more than three errors, rewrite once from a new scene slate. Repair by replacement, not deletion.

If a rhythm script is needed, use the bundled script named by the checker or SKILL.md. If you rewrite `draft.md` afterward, earlier rhythm repairs no longer count.

After the second checker call, stop. The only next tool action may be reading `draft.md` once and outputting it exactly, even if errors remain. Do not create an unpersisted final repair.

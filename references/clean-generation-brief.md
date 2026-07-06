# Clean Generation Brief

Use this file for the first draft of a formal blind-evaluation article. It is a compact runtime contract distilled from the longer references. Detailed files remain available for repair, validation, and research, but the first draft should not load them as a checklist.

## Output Silence

Do not announce that you are loading references or building a state card. Do not print process notes, checker summaries, or "now I will" lines. If the user asked for prose, the first visible line must be the title.

Do not print an English or Chinese scene plan between tool calls. Avoid visible text such as `Let me plan`, `The preflight says`, `Scene 1`, `Line 1`, `Total:`, `I need about`, or a bullet list of metrics to fix. Do not manually enumerate every line, calculate Chinese-character totals, or write a metric table before saving. Use a rough visual corridor, persist the best complete `draft.md`, then let `clean_run_checker.py` count exactly. If a preflight forces a rewrite, make the next visible non-tool text the final article after reading `draft.md`; keep planning private.

After a stop boundary, do not add a wrapper sentence. The final visible response must begin with the title from `draft.md`, not with `完成`, `以下是`, `最终文章`, `Clean run`, `Here is`, `按协议`, a markdown fence, or `---`.

Skill references are local bundled files. Do not call `read_mcp_resource` for this skill. Read local files directly only when this brief tells you to.

Do not rediscover this skill after it has already triggered. Do not glob, search, or list parent skill directories, sibling skill folders, or a generic `<skills-root>` to find `anlin-writing`. The current skill body and this brief are already the route. If a tool cannot resolve a bundled reference path, fall back to the Clean-Eval Minimum already loaded from `SKILL.md`: write the best complete titled `draft.md` in the current task workspace, then run `clean_run_checker.py` if its path is known. If the checker path also cannot be resolved, still persist `draft.md`; a controller can validate the artifact, but it cannot validate an unwritten article.

First tool action for any formal draft workspace:

```powershell
Test-Path .anlin-clean-eval-mode
```

If this returns true, choose clean-eval mode before drafting. Then run `Get-Location` / `pwd` before the first write and confirm the current directory is the external case workspace. Do not write `draft.md` until both the marker check and current-directory confirmation are visible in the run trace. In clean-eval mode, `clean_run_checker.py` is the only checker entrypoint; `check_anlin_violations.py` belongs to ordinary user repair, finalized repair, or controller validation, not the bounded generation directory.

For clean-eval generation, do not print the article to chat before the checker flow. First write the complete article to `draft.md` in the task workspace, run the bounded checker flow, then read `draft.md` once and output that exact content. A visible pre-check article followed by tools contaminates the run.

Clean-eval tool order is part of the test, not a suggestion: marker check -> current-directory confirmation -> read this brief -> write one complete `draft.md` -> run `clean_run_checker.py`. The step "read this brief" means using the reference file path supplied by the already-triggered skill; it never means searching parent skill directories to locate the skill again. After this brief is loaded, do not draft trial paragraphs, scene plans, or repeated scratch versions in the terminal. If the article is imperfect, persist the best complete titled candidate to `draft.md` and let the wrapper diagnose it; a visible scratch article without `draft.md` is a failed run.

Use the relative path `draft.md` or `.\draft.md` for the article file in the current task workspace. When using a write/file tool, the file/path argument must be exactly `draft.md` or `.\draft.md`. Do not construct an absolute path from memory, from a previous evaluation directory, from `<skill-dir>`, or from a date-stamped folder. In clean-eval, `Get-Location` / `pwd` is mandatory before the first write, not optional; do not guess.

Keep `<skill-dir>` separate from the output directory. `<skill-dir>` may appear in a checker command such as `python <skill-dir>/scripts/clean_run_checker.py draft.md --strict --draft-gate`, but it must not appear in the article write path. Do not write `<skill-dir>/<iteration-or-case>/draft.md`; write only `draft.md` in the current task workspace. If `Get-Location` shows `<skill-dir>` or a path ending in `anlin-writing`, do not write the article there; switch to an external case/task workspace or let the controller mark the run invalid.

For ordinary user mode, the same quiet drafting rule applies, but the checker loop may continue until hard errors are cleared or the user is satisfied. The two-call stop rule belongs to clean-eval only.

Before writing, check whether the current task workspace contains `.anlin-clean-eval-mode`. This marker check should be the first tool action before any `draft.md` write or checker command. If it exists, use clean-eval mode, run `Get-Location` / `pwd`, and do not call `check_anlin_violations.py` directly in that bounded directory. The wrapper `clean_run_checker.py` is the only checker entrypoint for clean-eval.

For clean-eval, this brief already contains the distilled anti-AI, title, rhythm, background, and scene constraints needed for the first draft. Do not open `anti-ai-slop.md`, `structure-patterns.md`, `title-model.md`, `generation-modes.md`, `runtime-brief.md`, corpus cards, judge rubrics, or style-ratio files before the first complete `draft.md`. Extra pre-draft files contaminate the source-guidance measurement and often cause checklist writing.

After reading `clean-generation-brief.md` in clean-eval mode, stop reading references. `runtime-brief.md` is not a harmless supplement before the first draft. If you want more guidance, use the source loop below and write the complete `draft.md`; deeper files are only for repair or controller analysis after the first wrapper pass.

## Target

The goal is anonymous blind-evaluation robustness under reported conditions. Do not claim real authorship, provenance, or indistinguishability. The article itself must not mention validation, corpus, generated text, or methodology.

Route genre before choosing length or rhythm:

- **Standard diary**: use when the user explicitly asks for `日寄`, asks for a broad daily montage, or gives several daily pressure surfaces. It needs the full broken-line corridor below.
- **Sincere**: use when the prompt is mainly mother/family thanks, Mother's Day, direct gratitude, apology, companionship, or a memory that would be cheapened by forced jokes. It can be shorter, but still needs concrete cost, restraint, one rough ordinary detail, and a loose ending. It may be sincere even if the mother figure is mostly `她`, when the pressure is holiday/no-message plus concrete care logistics such as food sent home, a tied bag, `吃了吗`, `还有没有菜`, or `天冷了多穿点`. Do not turn every family prompt into sincere mode; family dinner, family pressure, or social embarrassment can still be standard diary.
- **Micro-hope**: use only when the prompt asks for small acceptance/hope or the body naturally turns that way. Keep logistics and bad timing; avoid encouragement slogans.
- **Surreal**: use only when the prompt or selected scene truly supports loosened causality. Keep body, money, social, or object coordinates so it does not become symbolic prose.

If genre is unspecified in clean-eval, infer the narrowest genre supported by the prompt and title/body plan. A Mother's Day direct-memory prompt should usually route to sincere mode rather than being stretched into a standard diary. A non-`日寄` title alone never proves short form; if the body is a standard diary attempt, keep standard length and rhythm.

Once selected, keep the genre stable for the run. If the prompt explicitly asks for `日寄`, `标准日寄`, or a standard complete diary, lock `standard` even when the title later becomes a side-object title and the body contains one family message. If the draft is sincere or micro-hope, do not repair it into standard diary length or material density because a global profile warning looks safer. In formal testing, pass the selected genre explicitly, including `--genre standard` for standard diary, so preflight and hard gate apply the same corridor and a generic family/screen surface does not reroute the article by accident.

For sincere or micro-hope blind-evaluation drafts, shortness is allowed only when the shape is still a complete article. As a practical clean-eval floor, do not save a 250-500-character sketch and call it restraint; that usually reads like a model hiding from the prompt. When the user asks for a complete article, a short sincere draft should usually land around 650-850 body Chinese characters, about 28-55 body lines, and 4-7 uneven clusters. It needs several longer clumsy action/speech/memory/reply lines, one or two short fact-retreat drops, and a current practical consequence. A 520-649-character draft is only a narrow matched-short-original buffer; in clean-eval it should be rebuilt unless it already has real long clumsy lines and a practical turn. If it has 55+ tiny rows, mostly 4-12 Chinese-character captions, or fewer than three longer clumsy lines, merge and rebuild before writing `draft.md`; a short sincere article is not a poem-shaped grid. If it appears as 8-18 smooth paragraph lines or most lines are long complete sentences, it is still a prose-block sketch; split and rewrite into uneven clusters before saving. Do not write a polished 25-35-line prose essay where every line finishes an emotion. The roughness should come from logistics, an awkward reply, a practical interruption, bad timing, or a plain object that refuses to symbolize the feeling. If the candidate feels smooth or too small, repair the source movement before writing `draft.md`: combine adjacent memory/object facts into one rougher line, add a practical interruption already implied by the day, and delete the sentence that explains what the tenderness means. Do not expand it into standard diary length just to satisfy global ratios.

Short sincere pieces also fail when they become clean literary short stories. Do not let one title object explain the whole piece through `current screen -> mother/family memory -> childhood rain -> unsent message -> final tasteful residue`. That shape is too designed even when the details are plausible. If the user gives several powerful family-memory props, such as no holiday message, eggs from home, childhood rain, and a care scene, run a prop budget before drafting: keep one of `holiday/no-message`, `eggs/home food`, or `childhood rain/care` as the main pressure; keep at most one other as a cropped trace; discard or bury the rest. Do not keep both eggs and childhood rain as full scenes. Do not keep both holiday feed and typed-then-deleted message as full scenes. Do not use date titles such as `五月十二日` or titles that name the holiday. Before writing, break the proof-chain at the source: begin from one current practical friction that would exist without the holiday or relationship prompt, let memory enter only because that action touches it, add one awkward reply or interruption that does not serve tenderness, cap high-emotion sensory objects to one or two, and avoid ending by echoing the title. If the body is already built around `鸡蛋`, `雨衣`, `塑料袋`, `屏幕`, or another strong object, the ending should retreat to a next action, wrong chore, body demand, or inconvenient residue rather than completing that object.

For direct mother/holiday prompts, a cropped trace means less than a scene: one object label, one screen surface, or one partial sentence that does not carry its own sensory proof, title callback, or ending function. A line such as childhood rain + raincoat + broken umbrella + school arrival is already a second full memory family, not a cropped trace, even if it is only one line. If you keep eggs/home food as the main pressure, omit the childhood-rain scene entirely or leave only a barely named weather residue. If you keep childhood rain/care as the main pressure, do not unpack eggs/home food beyond one present object. If you keep no-message/holiday-screen as the main pressure, avoid class-group/feed montage and do not also unpack eggs plus childhood care. When unsure, choose the current practical anchor plus one memory family and let the other supplied props disappear; complete article does not mean complete prompt inventory.

For Mother's Day / mother-memory prompts, perform this pre-draft order literally: first pick the current practical anchor, then choose the one memory prop it can accidentally touch. Valid anchors include a sink or bowl that will not clean, a door/neighbor/call interruption, a reply that comes out wrong or does not get sent, a body/clothing embarrassment, a room chore, or a small object failure. Boiling the eggs can be the action only if something in the action fails and changes the next move; by itself it is still a prompt prop. The opening should not merely gesture at a sink or phone and then immediately unload the prompt inventory. Let the first 8-12 body lines spend time on the current action failing, exposing the body/clothes/room/reply, or changing the next move before `鸡蛋`, `塑料袋`, `下雨`, `雨衣`, `朋友圈`, `母亲节`, or the unsent blessing take over. If the first meaningful scene is already eggs, rain, blessing, mother, or a quick list of those props, restart from a smaller present action and let that material arrive later and partially.

For short sincere rhythm, do not turn restraint into a row of sealed sentences. A 35-55-line sincere draft where most rows end with `。` reads like a model made a sentence grid, even if the first 20 lines have a few commas after repair. Build 4-7 breathing clusters from the source: one line can trail with `，` because the same action continues, one longer clumsy line can carry a memory or reply, and a short line can land a failed decision or fact-retreat. Avoid chronological glue such as repeated `后来`, `已经`, and `当时`; if a memory has to enter, let a physical action, wrong reply, sleeve, door, bowl, slipper, or screen residue pull it in. Do not fix this by only changing punctuation after the fact.

If a draft has already become `egg/rain/holiday/no-message/final residue`, do not repair it by adding a sink, neighbor, or wet-clothing line around the same spine. That keeps the designed story intact. Throw away the old spine: retitle from the present action, keep only one memory prop as a cropped leak, and let the current action decide what can remain. The old title object is not owed a closing return.

Do not repair short sincere incompleteness by looping the same local packet. If the opening already has phone/screen/message plus bowl/water/oil, the tail cannot solve length by repeating phone lights, `你吃了吗`, the same bowl soaking, the same oil still there, or another "I did not reply" beat. That reads like metric-chasing. Delete one repeated packet and make the next beat change action: a wrong reply, a room position change, a neighbor/call interruption, a body consequence, or an unfinished chore that was not already used.

For short sincere mother/family prompts, title choice is part of the source shape, not a final label. Before drafting, decide whether the title is a side-action title or a prompt-prop title. Prefer a side-action title from today's failure: `袖口`, `门口`, `油没冲掉`, `水池`, `回了个好`, `那只拖鞋`, or another low-status handle that the present action earns. Do not title the draft with `鸡蛋`, `一袋鸡蛋`, `塑料袋`, `屏幕`, `没发出去的消息`, or the holiday if those same props are also the opening driver, memory proof, and ending residue. A prompt-prop title can survive only when the body weakens that prop: it appears once or twice, does not carry both memory and message, and the ending exits through a different practical action.

Short sincere repair has a second overfill trap: adding new material packets because the profile says the piece is thin. Do not thicken a mother/family sincere draft by importing delivery habits, branded foods, gift boxes, video lessons, variety shows, game scenes, routes, city labels, or background facts that were not already needed by the selected scene. If a longer line is needed, build it from the existing object, unsent or awkward reply, room action, body interruption, and one cropped memory fact. A new object is allowed only when it changes what the narrator does next; otherwise it is a repair artifact and should be cut.

Short sincere repair has a third overfill trap: raising emotional weight by inventing a major relationship fact. Do not write that the mother is dead, gone, no longer there, or unreachable unless the user supplied it. If the repair needs pressure, use a visible current failure instead: the reply comes out wrong, the call is missed, the hand stops over the transfer screen, the chore remains unfinished, or the room object forces the next action.

For a standard diary blind-evaluation draft:

- title required; choose from the completed body, not from a fixed default
- body target: roughly full standard-diary length; exact character counting belongs to the checker, not pre-draft arithmetic
- body shape: roughly many broken body lines, usually around the original standard-diary corridor; exact line counting belongs to the checker
- write the saved file as the broken article, not as paragraphs: a body line should usually carry one action, one reply, one thought turn, or one object consequence. If one paragraph line contains several `。` sentences, split it before writing `draft.md`
- first-draft sweet spot: about 55-68 body lines, with several true short breath drops and several rough long action/speech/thought lines
- true short breath means about 8 Chinese characters or fewer; a 12-character normal sentence is not the same signal
- keep roughly 8-18 naturally longer lines above about 28 Chinese characters
- mixed comma-led continuation lines and hard stop lines
- a middle rhythm corridor: not 36 compressed paragraph lines, not 80 same-length sentence rows
- line breaks keep punctuation when a clause needs it; do not remove commas or periods to make the page look broken
- not 8-15 smooth prose blocks
- not 100+ tiny rows

Title freedom is not length freedom. A standard diary with a side-object, phrase, question, or sentence title still needs the complete standard-diary corridor; only a deliberately sincere, micro-hope, or surreal short form should use a shorter matched evaluation.

Do not write a prose version first and then promise to restructure it. In clean-eval mode, the first persisted `draft.md` is already part of the measurement. If the draft in your head is 8-15 paragraphs, stop before writing and rebuild it as breathing clusters.

When using a write/file tool, the `content` being written must already visibly contain the line-broken body. Do not paste a 10-15 paragraph short story where blank lines separate long blocks. A quick visual test is enough: before the write, the middle of the article should look like many uneven rows, not a few dense paragraphs. If you see three or more sentences sitting on the same body line, break that line by action or speech before the file write.

Do not manually number every line or add character counts to each row. If the candidate visibly has too many tiny rows, no long movement rows, or is obviously short, fix that by changing the source movement before writing `draft.md`. If it is probably short, expand through lived action, not adjectives. If it is near the lower edge, inspect the source shape before expanding: only add material when the middle engine, long action/speech/thought lines, connectors, or rough body/social turn are weak.

Do not mistake a medium-length short-line grid for a finished diary. A 700-899 character draft is usually incomplete for standard clean-eval. A 900-949 character draft can still be underbuilt when most rows are small sealed captions, the first 20 lines rarely run through `，`, and almost no line carries rough action, speech, or thought. That shape needs a source-loop rewrite before the first file write: keep the useful facts, rebuild the middle with one off-axis consequence and one losing-face body/social turn, then choose the title again from the rebuilt body. Do not patch it by adding five more symptoms, app surfaces, money facts, or one-word drops.

Do not make the first draft a case report where every detail proves the prompt topic. In delivery, illness, job, family, or game prompts, one pressure surface is enough at first; the rest of the article still needs accidental body/social/material movement. Too many correct details in a row can read more synthetic than one unsupported detail.

For illness or body-pain prompts, do not build the article as symptom -> search page -> refrigerator inventory -> room smell -> ambient sound. That is a private case report even when every detail is concrete. Before writing the first body line, choose the first non-medical consequence that will force the piece outside the illness packet: a shop/neighbor/doorway exposure, cashier or delivery handoff, somebody seeing the limp or dirty hand, a failed reply that changes tomorrow's plan, a key/payment/route problem, a spill that another person can notice, or a small errand ruined by the body. Pick one symptom surface and one cropped screen wording if needed, then leave the diagnosis for at least one full cluster. Cap repeated illness nouns: if `痛风/脚踝/大脚趾/疼/肿/富贵病/腐乳/可乐/冰箱/外机` keep returning every few lines, delete a whole packet before adding anything. A phone message about meeting someone is still too private unless it changes action, route, social exposure, or an actual reply problem on the page.

Do not treat `practical consequence` as permission to invent a current office life. Unless the user supplied it, avoid consequences built from a leader, company group, office file, Monday deadline, leave request, attendance, salary penalty, or current work shift. Lower that pressure to a cropped screen surface, old coworker or someone else's company, a generic message, neighbor/cashier contact, route problem, bathroom/slipper trouble, or a body action that directly blocks the day.

If the prompt contains a searched article, forum, or quote such as `有人说...`, convert it before drafting. Use the page title, a cropped phrase on the screen, scroll action, or body reaction; do not write `有人说` / `另一条说` / `底下有人` as a chain. After that one screen surface, the draft must return to the room, body, route, object, food, or another person.

Avoid the opposite repair failure too: do not make nearly every line carry body, money, route, screen, food, weather, or cognition after a checker warning. A readable draft can have plain connective tissue, a dumb reply, a weak action, or a boring object that does not announce a mechanism. If each line proves heat, money, system pressure, and physical damage, the article starts to look like a controlled demonstration rather than a day.

If a repair keeps returning to the same local packet, such as hand dirt, white fruit, cutting board, heat, garbage, payment, screen, room darkness, fan noise, or air-conditioner noise, stop adding proof. Delete one repeated body/object/ambient cluster and replace it with a different kind of consequence: a bad reply, a payment handoff, a neighbor/cashier/vendor reaction, a route change, a small errand, or an unfinished practical action. The replacement should change what the narrator does next; it should not introduce another supported background label or turn a background guardrail into subject matter.

For takeout/food prompts, do not let the repair become `hand/oil/taste/hand/oil/taste` after the obvious prompt-prop loop is gone. Red oil, fingers, tongue, sweat, and smell can appear, but if they carry opening, middle, and tail by themselves the article becomes a private texture proof. Replace one body/oil packet with a small human or practical consequence: the rider/shopkeeper says one plain thing, the door/hallway exposes a stain, a payment/refund/reply fails, a neighbor hears the bag, or a room object forces a different action. Also avoid rows that pack several complete `。` sentences into one line; if a thought or action is still moving, let it run through a comma or split by action rather than making a period-heavy grid.

Known failed source shape: a fluent 10-15 paragraph article, later line-broken by tools into 55-70 lines, still tends to keep prose logic, period-heavy rhythm, repeated connector glue, and binary reframe sentences. Do not use that path. Before saving the first `draft.md`, the visible article itself should already look like clusters of breath: one or two lines may run on with `，`, a longer action/speech/thought line may carry the load, then a short drop lands a bad reply, body lowering, failed decision, or practical retreat. The short drop is earned by the scene; it is not a caption row.

Another failed source shape is a complete small realist story: the stranger delivers the exact social-comparison fact, the object fails exactly on cue, then the narrator supplies a clean metaphor so the reader understands the pressure. This feels complete, but it is too authored. Break it before writing: remove theatrical quote marks, avoid identity-probe lines like `你是不是以前那个大学的，就是...` when they mainly deliver school/place/career/salary facts, let only one speech fragment leak into payment/object/body action, and replace the polished metaphor with a next action or physical residue.

Use visible breathing clusters before the first file write. This is not a content recipe; it is a guard against the model imagining lineation that is not actually on the page. Draft roughly 8-10 clusters, usually 4-7 body lines each:

- friction appears through a thing failing, not a summary
- one attempted fix makes the body, money, route, or room worse
- one residue line does not explain the theme
- the prompt pressure enters through one cropped action or message surface
- the middle changes action through a misread, wrong reply, body interruption, or low-status practical cost
- the social/body wound becomes visible outside the narrator's explanation
- one cluster lets the prompt topic disappear for a moment
- the ending leaves a practical next action or wrong object, not a lesson

Before saving the first `draft.md`, make the rhythm corridor concrete in the candidate itself. A standard-diary candidate should already contain several lines that are genuinely long because an action, speech fragment, or thought has to keep moving; if you can only see tiny caption rows or sealed sentence rows, merge or rewrite before saving. It should also contain a few true short drops that land a failed decision, bad reply, body lowering, or practical retreat; do not create them by chopping every clause into captions. A draft with a visibly same-length grid, zero long movement rows, or every line standing alone as a sealed sentence is not an Anlin-like broken surface. It is a generated grid, and it must be rebuilt before the first checker call.

Before writing `draft.md`, do a quick page-shape glance only. Do not produce a visible numbered draft, row-by-row length audit, or character-sum calculation. If the candidate still looks like prose compression or a medium-row grid, rebuild the visible shape before saving; if it is close enough by eye, save it and let the checker measure exact rows and characters.

Near-miss drafts are a repeated failure. If the candidate feels complete but visibly lacks a full middle corridor or uses only two obvious turn traces, do not save it and hope preflight will expand it. Add one off-axis life cluster before writing: a body interruption, neighbor/cashier/roommate line, small errand, dirty object, payment action, or screen residue changes the next action. That cluster should naturally create new turn traces such as `发现/不过/突然/于是/因为/所以`. Do not add one explanatory paragraph, one extra symptom, or a decorative short line.

Rough self-damage is narrower than ordinary awkwardness. A neighbor looking once, a face "probably looking bad", or a line saying the narrator "seems stupid" is usually still tasteful narration. The wound should change the body, social position, reply, route, money, or next action: dirty hands/clothes get noticed by a cashier or neighbor, a stained thing becomes visible under a hallway light, the body makes an embarrassing sound or cost, a reply comes out wrong, the narrator is mistaken for something ridiculous, or a practical low-status maneuver becomes visible. Ordinary unclean consequences also work when they lower the narrator by action or social exposure: slippers worn on the wrong feet, snot nearly coming out, pants dirtied and noticed, sticky drain hair, socks worn through, a public stomach noise, or someone reacting to the narrator's dirty hand. Do not add shock or treat these as required tags; make the existing scene lower the narrator by consequence.

Private grime is not enough by itself. `手上有灰`, `指甲缝里有泥`, `案板很脏`, or `垃圾桶快满了` only become engine when another person, a payment action, a failed reply, a body noise, or a practical maneuver exposes them. If nobody in the world reacts and the narrator only inspects the object, it is still object texture, not paragraph movement.

Generated drafts often smuggle AI binary framing through ordinary self-correction. Treat these as unsafe before the checker, even when they sound colloquial: `也不是疼，就是...`, `其实不是想X，就是...`, `不是认识，就是...`, `不是因为X，而是因为Y`, `不是X。是Y`, `我不是叔叔，我只是...`, `最疼的不是X，是Y`, and similar cross-line forms. Replace them with the positive physical fact or social action: the knee softens, the hand has black dirt, the rider checks the phone first, someone says one ugly line.

Scan the whole article for this surface, not just the first matched sentence. Generated drafts often contain two or three softened versions after one obvious `不是X，是Y` is fixed. Remove all occurrences before the next checker call. If the only remaining preflight issue is binary reframe or another surface leak, make a local replacement only; do not expand the draft, add short drops, add money/body/platform facts, or introduce a new scene.

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

`Complete article` does not mean complete prompt coverage. When the prompt gives several neat nouns, such as shopping discount + social feed + parcel + wrong object, do not allocate one scene to every noun in order. Pick one daily failure as the driver, let one prompt pressure interrupt it, and bury, weaken, or discard the rest unless it changes the next action. A blind judge spots assignment-shaped writing when the article visits every supplied item politely.

Explicit negative constraints outrank scene instincts. If the user says not to write money, consumption, prices, shopping, romance, games, family, or any other domain, remove that whole domain before drafting; do not replace it with a neighboring version. For example, `不要写金钱、消费或价格` means no store checkout, buying water, delivery order, receipt, payment gesture, amount, balance, discount, or price arithmetic. If the prompt also contains a red-packet or social-feed surface, keep it as a cropped screen shape only when necessary, not as money, gift calculation, buying, or payment. Replace the forbidden function with body, route, room, weather, object failure, delayed reply, or social embarrassment.

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
5. Apply explicit negative constraints and fact gates. Do not open background files to hunt for extra nouns.

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

For shopping, parcel, wrong-size, coupon, delivery, or household-object prompts, the object inspection is not the scene engine. The failed object must change the narrator's body, reply, route, money, room, or social position: someone sees the bad object, a foot/hand cannot do the task, a return/payment action is abandoned in a humiliating way, or the wrong thing blocks the next ordinary action. If the draft only says the object is wrong and the narrator decides not to return it, it is still a tidy task report.

For invitations, weddings, reunions, job announcements, or other social-comparison message prompts, the chat log is not the article. Before drafting, pick a side action that could exist without the invitation: a bowl that will not wash, a charging cable under a chair, a bad payment screen, a dirty sleeve, a route search, a doorway errand, or another low practical handle. Also pick the post-refusal consequence before writing: the other person's reply changes the next action, the narrator sends the wrong-size lie, the payment/route decision fails, an old debt interrupts the hand, or a practical embarrassment is exposed. The consequence should be plain, not gift-wrapped: do not let the other person send a small red packet, `沾点喜气`, `心意到了`, or `项目忙就算了` as a tidy kindness after the refusal. Use silence, one ordinary reply, an address/photo that worsens the decision, payment/route/body trouble, or a remembered debt that changes whether the narrator answers. If the remembered debt becomes 转账/备注/已读/没领/未领取 only, it is still a private screen loop; it must force a visible reply, a body or doorway problem, a route/payment consequence, or disappear. The invitation enters only after the side action has already made the room/body/app crooked. Do not title the article with the person plus event, such as `狗哥的婚礼`, and do not let the first meaningful line restate the whole prompt. Use at most one cropped message surface, keep the money calculation short, and force one off-chat consequence before the middle ends: a worse reply, unpaid food, a route/payment decision, a body interruption, an errand, someone noticing a practical embarrassment, or the other person's response changing what the narrator does next. If the draft is only ticket price -> gift money -> refusal -> venue photo -> old memory, it is a sealed short story and the prompt is still too visible. Old classmate memory should be one cropped debt or object, not a full warm proof-chain that explains why the refusal is sad. Conversely, do not let the side room object eat the article: one cold room, noodle, dirty hand, phone heat, charging cable, delivery box, or washing-hand packet is enough. If 暖气、冷、手指、泡面、水龙头、厨房、洗手、手机发烫、充电线、快递盒, or 袖口 keeps returning in the opening, middle, and ending, the repair has replaced social pressure with indoor texture. Cut that packet and make the reply, money, old relation, route, or other person's reaction change the next action. Before saving, privately delete all room texture except one object in your head; if the social refusal no longer moves, rebuild from the reply aftermath. If the same side object supplies the title, opening disturbance, and final image, break one link before saving; the object is a handle, not a closure machine.

For stranger, shopkeeper, vendor, driver, customer, or passerby social-comparison prompts, do not turn the encounter into a quoted transcript. Use one or two embedded speech fragments without theatrical quotation marks, then interrupt with object handling, payment, body noise, dirty hands, wrong goods, route change, or silence. If the other person says `我儿子/我女儿/我老婆`, keep it clearly as that person's claim or lower it to `他儿子/他家里`; never let it become the narrator's family identity. A real encounter should leave a practical residue, not five standalone quote lines delivering every prompt fact.

For this encounter type, the first draft should usually contain zero quote marks in that scene. If the prompt itself gives a sentence, do not copy it as dialogue unless the exact wording changes the next action. Turn it into a rough narrated surface: the seller mentioned his son while weighing the melon; the cashier asked one ugly question while looking at the narrator's hand; the driver said a plain thing and the narrator failed to answer. Then leave the speech through money, object, body, or route. Do not let the stranger speak the prompt in a neat script, and do not write a clean recognition probe such as `你是不是以前那个大学的，就是后面有条小吃街那个` followed by a neat success comparison.

For quiet interior prompts, especially phone/feed + room + food/order + bed, add one outside contact before the first `draft.md`. The contact can be tiny: a delivery handoff, hallway or stairwell interruption, cashier/neighbor line, leaking bag, wrong reply, or object mark that becomes visible under a light. The point is not to add a required delivery scene; it is to stop the article from becoming screen -> room -> bowl -> bed. A single glance from another person, a mirror face, or `我看起来挺差` is too soft unless it changes the next action, leaves a physical residue, or lowers the narrator in front of the world.

For private-holiday, romance-feed, wrong-food, delivery-order, or takeout prompts, the prompt prop must not become title + opening + ending. Do not title from the wrong ingredient, holiday label, gift feed, or order defect if that same prop opens the body and closes the article. Start from a practical side engine first: a payment stall, hallway/door exposure, rider/shopkeeper/neighbor contact, sink failure, dirty clothing being seen, a wrong reply, a small errand, or an object leaking and forcing the body to move. Let the food/order/feed surface interrupt that engine once; if the draft still reads phone/feed -> order -> wrong item -> bowl/sink -> bed, restart before saving.

Before writing `draft.md`, do a private source preflight:

- body is already at least 950 Chinese characters and 45-70 body lines; for standard clean-eval aim nearer 55-68 rather than the exact boundary
- if the body is under 900 Chinese characters, treat it as incomplete for a standard diary; if it is 900-949 with 45-75 similar short rows, treat it as underbuilt only when the source engine is also weak
- if the body is 35-44 lines or 850-949 characters and only two connector families appear, add one full off-axis life cluster before saving; this is a source completion problem, not a checker repair problem
- at least a few real <=8-character drops are already present; they should land a failed decision, ugly reply, practical retreat, or body/social lowering, not decorative captions
- several rough long lines above about 28 Chinese characters are already present; do not let a rhythm script be the first source of long lines
- several different connectors from `其实/觉得/发现/好像/不过/突然/于是/因为/所以` occur because the thought is moving; zero or one signal is too polished, and exactly three familiar signals such as `其实/发现/好像` is still thin for a full standard diary. Usually aim for four or more natural turn traces by changing action, reply, body interruption, or consequence, not by sprinkling words. Repeating one word such as `其实/已经/当时` as glue is also synthetic
- no `不是X，是Y`, `不是X，而是Y`, `不是X。是Y`, `不是说X，是说Y`, or split-line equivalent
- no soft binary repair such as `也不是疼，就是...`, `不是认识，就是...`, `我不是叔叔，我只是...`, `最疼的不是X，是Y`, or `不是因为X，而是因为Y`
- no stranger/vendor identity-probe line whose job is to deliver the prompt: `你是不是以前那个大学的，就是...`, then school/city/job/salary/success facts
- no group/comment chain markers such as `有人发/有人说/有人问/又有人/底下有人/另一个说`
- no prompt-forbidden domain leakage: if the prompt forbids money/consumption/price, there is no store purchase, checkout, receipt, payment, balance, amount, delivery order, or price-like replacement
- no theatrical ordinary dialogue in quote marks; stranger/vendor/shopkeeper speech should usually be embedded without `“”` / `""`, and the encounter should leave through payment, wrong goods, dirty hands, body noise, route change, or silence
- no polished simile caption after abstract pressure, such as a sentence that says the message, job pressure, crack, or memory is `像一颗钉子` or `像扔进井里`; keep the physical fact or next action instead
- no invented spouse/child identity such as `老婆/妻子/媳妇/孩子`; delivery pressure is route, app, heat, money, body, customer, parent, landlord, or class comparison, not a married-rider biography
- one coarse body/social/self-own consequence is present in the scene, not only a quiet mood or clean ache
- quiet interior prompts have one outside contact or practical handoff that changes action; they are not only phone, room, food, mirror, bed, and ambient sound
- repeated body/object packets have been thinned: if hands, dirt, cutting board, fruit/food color, garbage, heat, and payment all recur, remove one packet before adding anything else
- social-message prompts have one off-chat consequence; they are not a chronological transcript of replies, prices, photos, and old messages
- the last three visible body lines do not use `哦。` / `算了。` / `睡了。` / `屏幕暗了。` as a style button unless the prior scene has forced that exact reply; prefer the unfinished action, wrong object, route, payment, reply, or body interruption already present

If these readiness signals tempt you to add a game scene, recurring character, body symptom, app platform, or background fact only because a reference mentions it, do not add it. Rework an existing scene so the function appears through its own action.

Natural connector coverage should be solved before the checker by changing scene movement, not by sprinkling words. A draft with only `觉得/发现` usually means each line is a sealed observation. Make the narrator do something after noticing it: delay a reply, pay money, misread a screen, answer someone badly, move route, get interrupted by the body, or correct a thought halfway. The connector is then a trace of that movement.

Keep connector spread rough. If one connector such as `觉得` or `可能` appears five or more times, or if the whole article only has three familiar connector families, it is probably doing the work that an action, bad reply, object movement, or body interruption should do. Replace the repeated or thin connector pattern by changing what happens next, not by swapping it for synonyms.

For short sincere repair, do not turn connector coverage into a visible string of one-each glue. A 600-800 character piece that suddenly contains `其实`, `觉得`, `发现`, `好像`, `不过`, `突然`, and `于是` exactly once can look more repaired than natural if those words merely bridge the same closed feeling. It is better to have fewer connector families and a stronger practical interruption than to demonstrate the whole connector set.

When a draft has 45-70 lines but no long action/speech/thought rows, it is usually one caption per line. Before saving, merge some adjacent object facts into rough rows that carry both the thing and its consequence, for example one line can contain seeing the old slipper, the hallway light, and what that exposure does to the next action. Do not break every observed fact into its own sentence row.

When repairing after a wrapper preflight, do not restate diagnostic words as a checklist. Do not write "the checker requires..." in notes or prose, and do not solve by adding one item per message. Either reset the visible rhythm corridor with the named script, or rewrite the middle from friction -> one off-axis consequence -> one losing-face body/social turn -> practical retreat. The visible article should change because the day changed, not because the metric names changed.

Avoid an opening rhythm made of isolated short facts such as `下午两点。手机很烫。路很白。`. In this mode, early hard stops should land a joke, embarrassment, or retreat. Let some early physical/action lines run downward through commas when the next line continues the same thought or action.

## Anti-Synthetic Shape

The anti-AI material in this skill is a negative list, not subject material. Unless the user explicitly asked for it, do not write scenes about AI, GPT, model output, generated text, article detection, or advice on identifying machine writing. If one appears because the reference mentioned it, delete the whole local move and replace it with body, money, route, food, social, family, or ordinary screen friction.

Avoid these generated-draft surfaces:

- `不是X，是Y`, `不是X，而是Y`, `不是X。是Y`, `这不是X，这是Y`
- `也不是X，就是Y`, `不是认识，就是Y`, `我不是X，我只是Y`, `最疼的不是X，是Y`, `不是因为X，而是因为Y`
- `本质上`, `真正的问题是`, `这说明`, `这意味着`, `换句话说`, `总之`, `现在我意识到...`
- `首先/其次/最后/综上`
- `——那种...`, `终于可以...的放松`, `释然`, `自洽`, `真实感`
- caption similes where an abstract pressure is explained for the reader: `那句话像一颗钉子`, `消息像扔进井里`, `裂缝像...`, `沉默像...`
- A/B or 甲乙 variable explanations
- therapy-humanizer phrases such as `允许自己`, `接住自己`, `慢慢来`, `和自己和解`
- comment chains such as `有人说/有人问/另一个人说/评论区/热评/底下有人`
- five-line `我说/他说/他说/我说` dialogue ladders

When a turn needs explanation, replace the explanation with a thing happening: food goes cold, a reply comes from the wrong person, money is paid, the body interrupts, the route changes, or someone says a plain ugly line.

If the user prompt contains a group chat, forum, comment thread, class chat, or a short-video/social-media surface, convert it before drafting. Use one cropped surface, unread count, screenshot title, message preview, delayed reply, body reaction, scroll action, or practical consequence. Do not narrate multiple speakers. A rider video with `有人说...` is still a comment chain. Formal generated drafts should usually contain zero `有人/又有人/底下有人/另一个说` in those scenes.

For 朋友圈, short-video feeds, annual-summary feeds, new-year flag screens, old-chat records, or romantic/social comparison prompts, one surface is enough before the first checker. Do not write a feed montage: three posts, a caption quote, a like/unlike gesture, and a final latest video usually reads as prompt coverage. Do not write a screen-archaeology chain either: 朋友圈年度总结 -> 2021聊天记录 -> 群聊 -> 通讯录 -> 外卖推送 is still a neat assignment path even when each surface is plausible. Pick one cropped thing on the screen, then move away from the feed into a body, food, money, room, route, reply, outside contact, or object consequence. If the feed or old record returns later, it must change action or social position, not add another example of the same pressure.

For private holiday, romance-feed, takeout, wrong-food, or lonely-room prompts, do not let the source become `phone/feed -> order food -> wrong item -> wash bowl -> bed`. That is a tidy prompt-shaped short story even when every detail is concrete. Before the first `draft.md`, choose one side engine that would still happen without the holiday or romance prompt: a payment stall, door or hallway exposure, rider/shopkeeper/neighbor contact, water/sink failure, dirty clothing under public light, wrong reply, small errand, or object leak. Use at most one feed/gift surface and at most one wrong-food surface as visible pressure; crop, bury, or discard the rest. If the condiment, gift, message, app note, or final practical phrase becomes the title, opening driver, and ending at once, weaken one of those positions before saving. A standard diary titled `备注`, `香菜`, `礼物`, `玫瑰`, `优惠券`, `朋友圈`, or another prompt prop is not automatically wrong, but it fails when the opening and tail keep proving that same prop. Retitle from the side consequence, cut one prop echo, and let the middle move through a door, hallway, payment, dirty hand, wrong reply, sink, rider/shopkeeper, or another person's reaction before the prop returns.

For old-record or nostalgia prompts, the old record is a trigger, not the engine. Before writing `draft.md`, choose one current-day consequence that the old record causes: a reply goes to the wrong person, the hand slips and exposes something, a delivery/cashier/neighbor interrupts, a practical chore gets worse, the body makes a low sound, or a room object forces the narrator to move. The memory itself should be crookedly read or punctured by the present. A red exclamation mark can become an unpaid practical debt, a voice bar can become a useless object, and an annual summary can feel like an app doing accounts receivable; but after that, the article must leave the screen through action. If the old record only produces "I remembered, then the room was quiet," it is not ready.

Do not repair this by adding more saved messages, more years, or more screenshots. One old surface plus one present humiliation beats a full archive tour. If the draft already has phone + old chat + room + food + bed, replace one private room/object packet with an outside or practical consequence before the first checker.

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
- long lines made only by chaining clauses with commas
- explaining every turn with `其实`, `已经`, `当时`, or `然后`
- 100+ body lines in a normal-length draft

Before writing `draft.md`, scan the first 20 content lines. If nearly all end with `。`, change some ongoing action/thought lines into comma continuations. If most adjacent lines are 4-10 characters, merge them into rough spoken/action syntax. If there are almost no <=8-character drops anywhere, do not solve it after the checker; add a few where the narrator actually fails, gives up, answers badly, or retreats.

If the draft has more than about 90 content lines, or no naturally longer action/speech/thought lines, it is not a better Anlin surface; it is a generated short-line grid. Merge or rebalance before checking. After merging, reread for broken facts and impossible object-action collisions.

Draft in breathing clusters, not sentence rows. A cluster can be 2-5 visible lines carrying one action/thought movement: one line may end with `，`, one line may run longer with speech or action, the next lands with `。`, then a short drop or ugly reply. Long lines should come from rough action, speech, or thought doing more work, not from `，` chaining five explanations. A 45-70 line draft with zero real <=8-character drops is still a medium-row grid; it reads like every thought was normalized to the same length. Do not put a blank line after every sentence only to raise line count. Do not turn every line ending into `，` only to satisfy `行末逗号比例`. If a line break does not change breath, action, reply, body, or thought direction, it is formatting, not rhythm.

Before the first `draft.md`, the first 20 content lines should usually contain several comma-ended continuation lines and several hard-stop lines. The whole body should not be mostly independent sentences. If you can read every line as a finished caption, the draft is still too AI-smooth even if the length is correct.

If you need a mechanical rhythm repair, use it as a corridor reset, not a style source. `rebalance_line_rhythm.py` can move a draft back from prose-block compression or short-line grid toward 45-70 lines with several longer lines, and it can split out existing short landing sentences such as `其实会。` or `很丢人。` when they are buried inside uniform rows. It cannot supply the missing scene engine; after using it, inspect whether the lines still read like a report.

## Background And Game

Background facts are guardrails, not ingredients. Do not insert 云南、王者、痛风、狗哥、外卖、知乎, or AI/GPT just because another reference says they exist.

Game is allowed, not required. Use it only if the prompt, current action, memory trigger, social wound, practical delay, or cognitive turn needs it. Keep it coarse unless a selected corpus anchor or user fact supports detail. Do not invent current rank, role, lane, teammates, scoreboard, tactical calls, match order, or win/loss sequences.

Named districts, current cities, company parks, local policies, current game-role details, or specific routes need support. If unsupported, lower specificity or delete.

If a prompt says the narrator uses `忙项目`, `最近有项目`, or similar wording as an excuse to decline a wedding, dinner, trip, or reunion, keep it inside the reply as an excuse surface. Do not make it true by adding a current project, team leader, deadline, delivery, leave request, office group, or manager. The lie should damage the reply or body; it should not create a new office biography.

Old school or classmate memory can stay generic. Do not invent a named mountain, campus gate, road, restaurant, hotpot place, or barbecue stall to make the memory feel real. Use `学校门口`, `那家店`, `以前吃饭的地方`, or a cropped object/price only when it changes the current reply, payment, body, or shame.

Load `references/anlin-background.md` and `references/background-fact-classes.json` only after a scene already contains a fact that must be checked.

Do not invent a current office-worker identity. Unless the user gives a phase/date or concrete material that supports it, avoid first-person scenes built around `到了公司`, `同事小X`, `张哥`, `工位`, `领导`, `KPI`, `营收`, `财务`, meetings,饭卡, or quarterly office reporting. Also avoid subtler current-work consequence chains such as a leader sending a file, a Monday hand-in deadline, leave being penalized, attendance, work group pressure, or a shift that the body problem threatens. Work/company material is phase-bound and often belongs to other people, old work, interviews, layoffs, or screen pressure; default current generation should lower it to old coworker, recruitment surface, someone else's company, a cropped message, or ordinary daily life.

Do not convert delivery work into a different biography. 2022 delivery work is supported as a pressure/work surface, but the narrator is still the corpus-bounded young graduate. Do not invent a wife, spouse, child, full-time rider family life, or older married-provider identity unless the user explicitly supplies that fact. If the prompt says `送外卖`, keep it as route, app, customer, heat, money, body, parent/family pressure, landlord, roommate, or class-rank pressure; do not make it a marriage story. Before writing `draft.md`, scan the candidate for narrator-owned spouse/child phrasing such as `我老婆/老婆让我/妻子/媳妇/孩子他妈/我家孩子/我儿子/我女儿`; if it belongs to the narrator without user support, delete or lower the relation before the checker. If `我儿子/我女儿` belongs to another speaker, keep the attribution clear or lower it to `他儿子/她女儿`.

For illness/body prompts, do not let the first slate become `symptom -> search result -> refrigerator/food -> room smell -> appliance sound`. Start by finding one exposed consequence outside diagnosis: a payment stall, a person waiting, a door/key/route problem, food or medicine getting on the narrator in front of someone, or a reply that changes tomorrow's visible constraint. The consequence can involve takeout, a shop, a neighbor, family, a doorway, or no named role at all; it is not a quota to insert 外卖. It works only if it changes action or status.

Roughness is not a swear-word budget. `妈的`, `操`, `我服了`, and similar drops can stay when the scene earns them, but they cannot replace the low-status event. Prefer the event: a phone refusing to scan while someone waits, a bag handle breaking, food leaking onto a hand or shoe, a limp noticed at the door, a reply sent too small, a wrong object carried back inside. If the same scene would still function after deleting the outside person or practical failure, it is probably private texture rather than paragraph engine.

## Ending

Do not summarize, heal, or neatly explain the article. Avoid learned buttons such as `哦。`, `算了。`, `睡了。`, `屏幕暗了。`, or a pure sound ending unless the scene forces it.

End on a loose practical consequence: body interruption, unfinished reply, wrong object, route, payment, cold food, next notification, or a small action that does not solve anything.

## Title

Do not default mechanically to `日寄`, and do not avoid it mechanically either. Corpus titles include exact `日寄`, `X日寄`, `X寄`, questions, meme/platform titles, sentence titles, and literary phrases. Choose after the body exists:

- If the body already has strong local color, bare `日寄` may work.
- If the body has a side wound or low-status handle, `X日寄` or `X寄` may work.
- If the body is sincere, micro-hope, surreal, or later reflective, a sentence or phrase title may work.
- If the title alone reveals the user's prompt, weaken it or choose a side object/action.
- In invitation, wedding, reunion, or social-decline prompts, do not choose a title that names the person plus the event. Choose the failed side action, wrong reply, route/payment residue, or low object that the refusal created.
- If the title and ending explain each other too neatly, lower one of them.
- Do not use a final-line phrase such as `明天再说吧` as the title when the ending repeats or completes it. That turns a loose retreat into a designed contract. Keep the tail practical, or retitle from a weaker side handle.
- In short sincere pieces, do not let the title object become a key that unlocks the ending. A title like `鸡蛋` can work only if the body does not turn every egg, plastic bag, rain memory, and unsent message into one symbolic proof.

Do not use a calendar label as a quick modifier for standard clean-eval. Titles like `2024日寄`, `新年日寄`, `跨年日寄`, `元旦日寄`, or `年度总结日寄` usually tell the judge the prompt before the body starts. If the date matters, let it leak through the phone time, an unpaid practical action, a message surface, a body state, or a side object; choose the title from that side handle after the article is complete.

## Required Tool Flow

Write the complete titled article to relative `draft.md` in the current task working directory. The write/file tool path must be exactly `draft.md` or `.\draft.md`. Do not write it inside the skill directory. Do not compose an absolute output path unless the user explicitly gave one for ordinary saved output. In clean-eval, run `Get-Location` / `pwd` before the first write; if the current working directory is the skill directory, switch to or create a task/eval workspace outside it before writing.

For clean-eval mode, then run:

```powershell
python <skill-dir>/scripts/clean_run_checker.py draft.md --strict --draft-gate
```

Resolve `<skill-dir>` from the directory that contains this `SKILL.md`. Do not make `<skill-dir>` the output directory.

If the selected genre is known, pass it explicitly, including standard diary, for example:

```powershell
python <skill-dir>/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre standard
python <skill-dir>/scripts/clean_run_checker.py draft.md --strict --draft-gate --genre sincere
```

If the wrapper prints `CLEAN_RUN_PREFLIGHT`, revise before the first checker call is consumed. Do not inspect checker source or tests for hidden tokens.

Use the preflight message as a shape diagnosis, not as permission to thrash between prose blocks and tiny grids:

- `body_lines < 45`, `prose_block_shape=compressed`, `body_lines > 90`, `short_line_grid`, or `long_lines < 4`: first run `python <skill-dir>/scripts/rebalance_line_rhythm.py draft.md --in-place`, read once, then add only missing scene function or cut non-consequential texture. Do not let the repair bounce from short-line grid into 30-40 prose lines.
- `medium_short_line_grid` or an underbuilt source shape: rewrite from the source loop before overwriting `draft.md`. Keep only useful scene facts, add one off-axis consequence and one rough body/social turn, and rebuild toward 55-68 body lines and 950-1150 Chinese characters. Do not patch a weak grid with isolated symptoms, app lines, money facts, or decorative short drops.
- `early_comma_ratio`: run `python <skill-dir>/scripts/soften_line_endings.py draft.md --in-place` or manually break ongoing actions after visible line-final `，`; internal comma chains do not count.
- `binary_reframe`: scan every line, delete every `不是X，是Y` / `不是X，而是Y` / soft equivalent, and let the physical fact, body reaction, money action, or plain social line already in that scene carry the turn. If this is the only remaining preflight issue, keep the same length/rhythm/scene slate and do not add new texture.
- `short_genre_literary_story_closure`: do not stretch the short form into a standard diary. If the same title-object/memory/message/ending spine still carries the article, a local patch is not enough. Retitle from a side action, cut one or two proof props, and rebuild from a present-day interruption, awkward reply, or useless residue already implied by the scene.
- `short_genre_body_lines` or `short_genre_prose_block_compression`: do not add one more paragraph and call it fixed. Rebuild the visible page into about 28-55 actual body lines across 4-7 uneven clusters; keep punctuation at line ends, include a few longer clumsy action/memory/reply lines, and let one or two short factual retreats land. Count the actual saved body rows before writing `draft.md`.
- `short_genre_period_grid`: do not patch a sentence grid by changing a few early `。` to `，`. Rebuild the local clusters: remove repeated `后来/已经/当时`, let one action or reply run across a line break with a real line-final comma, keep a longer clumsy memory/logistics line, and land one short factual retreat.
- `short_genre_present_action_anchor`: restart from the current practical anchor before memory. Do not keep the same egg/rain/no-message article and insert a late practical detail. Use a room, body, door, reply, neighbor, chore, or small object failure as the first engine, keep at most one family-memory prop as a leak, and choose the title after that new action exists.
- `short_genre_prompt_prop_too_early`: the draft technically starts with a current action, but the first few lines already hand control to eggs, rain, holiday feed, mother, or the withheld message. Rewrite the opening, not just one line: the first 8-12 body lines must let today's practical action fail and redirect the narrator before one memory/screen prop leaks in.
- `short_genre_main_prop_title_loop`: the title is acting as the proof object. Retitle from a side action or low-status handle before rewriting the tail. If `鸡蛋`, `塑料袋`, `屏幕`, or another prompt prop remains in the body, do not let the ending return to it as the emotional answer.
- `standard_prompt_prop_title_loop`: a standard diary has made one prompt prop the title, opening engine, and tail proof. Do not only replace the title word. Retitle from a side consequence, cut one prompt-prop echo, and rebuild the middle through a door, hallway, payment, dirty hand, wrong reply, sink, rider/shopkeeper, or another person's reaction so the prompt prop becomes one cropped pressure surface.
- `short_genre_repair_stuffing`: delete the newly imported food, delivery, gift, media, game, route, or background packet. Repair thickness inside the existing prop budget: combine two adjacent memory/object facts into one rough line, make the reply or chore more awkward, and end on a factual next action instead of adding another scene family.
- `rough_self_damage`: pain, heat, and fatigue alone are too polite; so are a neighbor's glance, `脸应该挺难看`, or `显得我挺蠢` by themselves. Add one losing-face consequence: dirty clothing noticed by someone, stomach/urine/sweat trouble, being mistaken as ridiculous, a bad reply, a body failure that changes the next action, or a practical low-status cost. Small unclean consequences can satisfy this when they have consequence: wrong slippers, snot, dirty pants seen by someone, sticky drain hair, worn-through socks, a public body noise, or someone reacting to dirty hands. Do not escalate into shock material or add these only because the checker named them. When adding this after preflight, do not paste one long paragraph-line; break the action into a few visible lines that keep the article in a 45-70-line corridor.
- `纹理替代社交不足` or red `ngram_texture`: do not add more body/object/screen proof. Cut one repeated local packet and replace it with a social or practical consequence that changes action, reply, route, payment, or room position. If the same nouns keep returning, the repair is repeating itself.
- `body_chinese_chars < 900`: expand within the existing line-broken shape through lived action, social/body consequence, or off-axis residue; do not collapse the whole article back into 8-15 prose paragraphs.
- `body_chinese_chars < 950 with source_shape_weak`: do not patch by count. Rebuild the weak middle source: add one consequence that changes action, one rough losing-face turn, and several natural longer action/speech/thought lines, then let the length rise as a byproduct.

After any rewrite of `draft.md`, prior rhythm script work no longer applies. Do not overwrite a script-repaired file with a fresh 8-15 paragraph draft and then call the wrapper. If a preflight combines `early_comma_ratio` with a content problem such as missing rough self-damage, weak engine, or underbuilt source shape, repair the content first and run `soften_line_endings.py` last before the next wrapper call. If you need to rebuild content after `rebalance_line_rhythm.py`, `split_long_lines.py`, `merge_short_lines.py`, or `soften_line_endings.py`, rebuild inside the existing breathing-cluster shape or immediately rerun the relevant rhythm script before the next `clean_run_checker.py` call. Expansion after preflight should add 6-10 visible line-broken rows inside the current corridor, not one prose paragraph.

If the wrapper prints `CLEAN_RUN_PREFLIGHT_STOP`, the draft still is not ready after the bounded preflight attempts. This is a final boundary for the bounded case. Do not write `draft.md`, do not repair, do not run another rhythm script, and do not switch to `check_anlin_violations.py` in the same directory. The next tool action must be reading the current `draft.md` once and outputting it unchanged. The controller should mark that run invalid or failed.

`CLEAN_RUN_PREFLIGHT_STOP` and `CLEAN_RUN_STOP` are stop signals even when the wrapper exits with status 0. Status 0 at a stop boundary only means the protocol message was delivered; it does not mean the article passed. Treat the words `FINAL BOUNDARY` in wrapper output literally. The controller will read the state file and validation reports.

In clean-eval mode, use at most two clean-run checker calls. If the first actual checker reports severe line grid, over-fragmentation, dialogue ladder, reference contamination, underbuilt length, background stuffing, or more than three errors, rewrite once from a new scene slate. Repair by replacement, not deletion.

In ordinary user mode, use the normal checker and continue repair as needed, but do not chase every ratio warning by adding visible features. Repeated warnings mean the scene source or title/rhythm model is wrong.

If a rhythm script is needed, use the bundled script named by the checker or SKILL.md. If you rewrite `draft.md` afterward, earlier rhythm repairs no longer count.

In clean-eval mode, after the second checker call, stop. The only next tool action may be reading `draft.md` once and outputting it exactly, even if errors remain. Do not create an unpersisted final repair.

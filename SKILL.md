---
name: "anlin-writing"
description: "Generate, review, or evaluate Anlin/日寄-style anonymous blind-evaluation prose against the Anlin corpus. Use ONLY when the user explicitly mentions Anlin, 日寄, Anlin-style, 像Anlin那样写, 模拟日寄, 盲评, or asks for Anlin corpus evaluation."
---

# Anlin Writing Skill

This skill generates, reviews, and evaluates Anlin-style Chinese prose for anonymous blind evaluation.

The goal is narrow:

> Make generated text less stably identifiable as generated text in anonymous blind review. Report only test conditions, sample size, and recognition/pass rates. Do not claim real authorship, provenance, or "indistinguishable from the original author."

Generated prose should not contain process labels such as "仿写", "AI", "生成", "验证通过", or "38篇语料". Controller notes and validation reports may mention methodology; the prose body must not.

This skill is self-contained at runtime. Do not require or call any external anti-slop, author-style, or personal writing skill while generating, repairing, or judging. The anti-AI-writing guidance needed for this task lives in `references/anti-ai-slop.md`, `references/feature-budget.md`, and the checker bundled in this skill. External writing skills may be used only by a maintainer while developing this skill, not by a generation agent using it.

## Load Order

Always start with these four files:

1. `references/runtime-brief.md`
2. `references/feature-budget.md`
3. `references/anti-ai-slop.md`
4. `references/generation-modes.md`

For ordinary article generation, use the minimal generation pack:

1. `references/runtime-brief.md`
2. `references/feature-budget.md`
3. `references/anti-ai-slop.md`
4. `references/generation-modes.md`
5. `references/era-state.md` only if date/phase matters
6. `references/structure-patterns.md`
7. `references/vocabulary-rules.md` only for review or uncertain wording

`references/anlin-background.md` and `references/background-fact-classes.json` are contradiction boundaries, not feature checklists. Do not load them as source material before scene selection. Load them only after the candidate scene slate exists, or when the user supplied a concrete background fact that must be verified. Use them to verify, classify, lower, or delete facts about place/game/platform/body/phase; never use them to find extra nouns to add. Do not add 王者、云南、狗哥、痛风、外卖、知乎, or AI/GPT merely because they are listed there. Game can appear when the user's material, current action, memory trigger, or scene consequence naturally calls for it; it must not become mandatory or decorative.

Do not read `anlin-reference-library.md`, `writing-checklist.md`, `self-check.md`, `review-rubric.md`, or `blind-judge-angles.md` before the first draft. Those are critique/reference materials and can cause the agent to stall or overfit. Use them only after the first checker pass fails or when the user explicitly asks for analysis/validation.

Do not list the skill directory recursively during ordinary generation. The paths above are known. Do not read `references/corpus-cards/` before the first draft in clean generation; corpus cards are for failed-draft repair or explicit validation.

Then load only the branch-specific files as needed:

| Need | Load |
|---|---|
| Target date, phase, or projection handling | `references/era-state.md` |
| Place, game, platform, school/work, or background facts after scene selection | `references/anlin-background.md`, `references/background-fact-classes.json`, then `references/era-state.md` |
| AI-like formulaic phrasing, over-smoothness, or human-reader slop audit | `references/anti-ai-slop.md` |
| Standard, sincere, micro-hope, surreal, or mixed genre choices | `references/generation-modes.md` |
| Detailed rhythm, structure, endings, Bathos | `references/structure-patterns.md` |
| Specific characters or role budget | `references/role-orchestration.md`, then `references/anlin-characters.md` |
| Wording uncertainty or hard-rule review | `references/vocabulary-rules.md` |
| Concrete examples by topic | `references/anlin-reference-library.md`, `references/samples-index.md` |
| Post-draft critique | `references/review-rubric.md`, `references/writing-checklist.md`, `references/self-check.md` |
| Anti-copying and overlap checks | `references/anti-pastiche.md` |
| Corpus-prior ratio audit | `references/stylometric-ratio-protocol.md`, then `scripts/build_style_profile.py` / `scripts/check_style_profile.py` |
| Full validation and blind review | `references/validation-protocol.md`, `references/blind-judge-angles.md` |

Do not read every reference before drafting. The generation pass uses a small state model; the critique pass uses the rule library.

Do not compensate for weak prose by loading another style or anti-AI skill. If the draft smells synthetic, revise through this skill's own lenses: scene-first causality, prompt displacement, background restraint, rhythm variance from action, and concrete body/social/material consequence.

Do not use corpus ratio targets as a pre-draft recipe. `references/stylometric-ratio-protocol.md` and the style-profile scripts are for post-draft audit, controller validation, and targeted repair. If a ratio drifts, repair the underlying function: length through lived action, line rhythm through interruption/speech/body, connector drift through less explanatory glue, and title drift through a weaker title contract.

For formal clean generation, checker call count is a hard protocol boundary. After the second checker call, the only allowed tool action is reading `draft.md` once to output it exactly. Do not edit, write, compare, or run another checker after it. A third checker call or any post-second write contaminates the test more severely than leaving draft errors unresolved. The external controller will decide pass/fail.

For formal clean generation, the visible final article must be exactly the current `draft.md` content after the last write. Do not create an unpersisted "manual repair" in the final response after the second checker call. If the second checker still reports errors, output the current `draft.md` anyway and let the controller fail it.

## Workflow

### 1. Confirm Inputs

If the user has not already supplied them, ask once for the minimum missing inputs:

- target date/time or `inferred`
- genre: standard diary, sincere, micro-hope, surreal, mixed, or unspecified
- concrete background material, if any
- whether web/background lookup is allowed

If the user refuses or leaves inputs open, proceed with `inferred` or `fictional` status. Do not invent specific real-world events.

### 2. Build The State Card

Before scene generation, form an internal state card using `runtime-brief.md`. Keep it mental/private. Do not print it, write it into the chat, or put it in `draft.md` unless the user explicitly asks for process notes:

- date zone and phase
- genre
- current place
- body state
- money state
- social friction
- screen/platform texture
- what is being avoided
- what hurts
- what detail is accidental and not theme-serving
- target length and rhythm constraints for the chosen validation mode
- feature budget

This state card is internal unless the user asks to see process notes. In clean generation, visible process chatter contaminates the run even if the final `draft.md` is clean.

### 3. Sample Calibration

Read 3-5 short anchors, not the whole archive:

- 1-2 cards or samples from the same phase
- 1 sample from the same genre
- 1 contrasting sample to avoid monotone

If `references/corpus-cards/` exists, prefer cards first; open full originals only when a card points to a needed passage.

For formal clean generation, skip this step before the first draft. Draft from the minimal generation pack, run the checker, then read at most 1-2 cards only if repair is needed. The goal is to avoid long reference browsing and prompt-overfitting.

### 4. Generate Candidate Scenes

List 8-12 candidate fragments. Each fragment must come from one of:

- user-provided real material
- date/era texture
- plausible inferred daily life
- memory triggered by current sensory detail
- accidental observation

Mark each candidate by function: laugh, sting, tenderness, deflection, absurdity, analysis, body, money, social collision, memory, or noise. At least 30% should not directly serve the main theme. Keep at least two boring or accidental details available for the anti-detection pass.

Do not make background facts into candidate scenes by themselves. A valid candidate must still have an action, body effect, social change, money cost, app surface, route problem, joke, or memory trigger if named background tags are removed. Game is allowed as a candidate, but only as one of those lived functions; it is not a required Anlin marker and it is not forbidden by prompt silence.

Before drafting, run a fact gate on the selected slate: load `references/anlin-background.md` and, for machine-readable classification, `references/background-fact-classes.json` only for facts that are already present in selected scenes, then lower or remove unsupported specifics. If a new fact appears only because either background file listed it, cut it before Step 5.

### 5. Draft With Scene Modes

Use `generation-modes.md`. Do not force every scene through one template.

Select the smallest set of scenes that can carry the piece. Standard diary usually uses several fragments; sincere and micro-hope pieces can be short. The five-step cognitive path is a strong mode for misread/self-sabotage scenes, not a global obligation.

For blind-evaluation drafts, always produce a complete article with a title. Put the generated title on the first line as plain text or `# Title`; do not bold it, label it as `标题：`, or wrap it in controller notes. Serious blind review keeps and normalizes titles for all samples, then length-matches complete articles. A formal standard diary should usually aim around 950-1150 body Chinese characters and preferably not by padding; below 900 is a generated-draft risk buffer. Short sincere or micro-hope pieces require short-original matched evaluation; otherwise expand with concrete actions, dialogue, body/money consequence, and non-theme residue before blind testing.

For formal standard-diary clean generation, do not save a skeletal placeholder as `draft.md`. The first written `draft.md` must already be a complete article with title, roughly 45-70 non-empty body lines, at least six naturally longer lines, and near 1000-1200 body Chinese characters when the model tends to shorten. If the candidate is visibly short, over-fragmented, or mostly 4-10 character lines, merge/expand before writing/running the checker rather than relying on a later terminal-only repair.

### 6. Separate Review From Generation

After drafting, switch to review mode:

1. Run `scripts/check_anlin_violations.py <draft>`.
   - For formal standard-diary blind-evaluation drafts, run `scripts/check_anlin_violations.py <draft> --strict --draft-gate` as a bounded gate. `--draft-gate` is for generated drafts only; do not use it when calibrating originals.
   - If the current working directory is not the skill directory, use the absolute checker path from this skill, e.g. `python C:\Users\34025\.config\opencode\skills\anlin-writing\scripts\check_anlin_violations.py draft.md --strict --draft-gate`. Do not first try a relative `scripts\...` path from the case directory.
   - Even if the user only asked for prose, write the draft to `draft.md` in the current working directory, run the checker, then output prose only after the bounded gate. Do not use OS temp paths for formal evaluation drafts; timeout recovery needs the local draft. Do not print checker output unless the user asked for validation notes.
   - Fix hard errors, process leakage, missing title, copied source phrasing, high-signal opening, learned ending buttons, sealed-night/story enclosure, pure ambient endings, repeated material hooks, formulaic comment-chain summaries, and obvious prompt-shape leakage before output.
   - Also fix generated-draft AI-slop errors: explanatory `不是X，是Y` / `不是X，而是Y` structures, unsupported specific place names, unsupported game-role filler, blog-like explainer phrases, or any line that reads like a model announcing a reframe.
   - Treat quiet explanation, weak paragraph engine, and missing coarse self-damage as serious review signals, not automatic hard failures: the original corpus contains some of these. In generated full-article blind tests, `--draft-gate` promotes diagnostic title, underbuilt length, single-theme density, prompt-chain over-compliance, and formulaic comment-chain summaries to blocking errors.
   - Use at most one checker-driven repair loop inside the generation agent. Call the checker at most twice total, including failed/nonzero checker runs. A nonzero checker exit is normal when findings include `error`; it is not a tooling failure. If the first checker reports more than three `error` findings, or reports prompt-chain density, offer-specific fabrication, dialogue ladder, underbuilt length, or paragraph-block compression, do one full rewrite from a new scene slate. Do not patch the existing draft line by line. If the first checker reports only one or two local errors, repair by replacement, not deletion: removed prompt-chain, game, dash, or comment material must be replaced with concrete body/action/social/route residue before the second checker. Do not call the second checker on a visibly shortened draft. After the second checker call, stop all repair tool use: no edit, write, compare, or third checker command. You may read `draft.md` once only to output it exactly. Output the current `draft.md` content exactly, even if errors or warnings remain. Do not hand-repair a different final answer after the second checker. Do not continue repairing high-frequency coverage, coarse self-damage, paragraph engine, comma-ratio, breathing-point, scene-count, metadata, or other corpus-calibrated warnings. The external controller will validate it.
   - If temporary-file creation, overwrite, or checker execution fails for tooling reasons, do not stop with process notes. Apply the strict checklist manually, rewrite once, and output the article only; the controller can run the checker externally.
2. If the full corpus is available, run `scripts/compare_anlin_corpus.py <draft> --corpus-dir <corpus>`.
3. For controller validation or explicit style-ratio review, read `references/stylometric-ratio-protocol.md`, build or load `references/style-profile.json`, and run `scripts/check_style_profile.py <draft> --profile references/style-profile.json --draft-gate`. Treat profile drift as a repair signal, not authorship proof and not a reason to add rare tags.
4. Read `review-rubric.md` and inspect the draft against the appropriate genre gates.
5. Use `writing-checklist.md` and `self-check.md` as critic material only. Do not retrofit every high-frequency label into the draft.
6. Run anti-pastiche checks if any source phrasing may have leaked.

Warnings are review prompts, not automatic failure. Errors and hard identity/date mistakes must be fixed. Do at most one targeted revision pass for ordinary warnings. For formal standard-diary blind evaluation, prioritize prompt-shape leakage, AI-slop phrasing, unsupported background facts, single-theme density, sealed-night/story enclosure, quiet explanation, weak paragraph engine, missing title, copied source phrasing, diagnostic title, underbuilt length, formulaic comment-chain summaries, and learned ending buttons. If one of these high-risk warnings remains after the first patch, rewrite once from the scene slate instead of polishing the same draft. After that rewrite, deliver the cleanest pure article rather than logs or analysis; do not loop until every ordinary warning disappears.

### 7. Validate Blind-Evaluation Claims

Only report quality claims after validation. Use `validation-protocol.md`.

For formal skill evaluation, the generation agent must receive only the realistic user prompt plus normal access to this skill. Do not give the generator blind-judge rubrics, previous failure analysis, source excerpts, controller mappings, or manual style hints outside the skill; that contaminates the test.

Required wording:

- acceptable: "In 8 anonymous rounds, judges identified the generated article in 1/8 rounds under these conditions..."
- unacceptable: "This is indistinguishable", "Anlin本人会这么写", "无法被看出来"

## Output Rules

- If the user asks for prose, output prose only unless they asked for process notes. The first visible line must be the article title, usually `日寄` or `# 日寄`; never print `State Card`, prompt buckets, scene slate, validation notes, Jaccard scores, checker summaries, or `草拟`.
- Never prepend protocol explanations such as `This is the second checker call`, `per protocol`, `Here is the article`, or comments about `draft.md`. The first visible line must be the title.
- Never announce clean-generation steps in Chinese either: no `现在构建状态卡`, `开始写草稿`, `检查器发现`, `需要重写`, `最后一次修复`, or similar process lines.
- Do not narrate reference loading, file checks, or internal decisions to the user. Tool use and validation stay internal unless validation reporting was requested.
- Do not include methodology labels inside the prose.
- If the user asks for validation, report commands, conditions, sample size, and results.
- If the corpus or background cannot be accessed, state the limitation in the validation report, not inside the prose.
- If the request asks to impersonate real provenance, publish as the real author, forge evidence, or deceive a reader about authorship, refuse that part and offer anonymous style-evaluation output instead.

## Validation Commands

```powershell
python scripts/check_anlin_violations.py draft.md
python scripts/check_anlin_violations.py draft.md --strict --draft-gate --corpus-dir "C:\Users\34025\Desktop\Anlin"
python scripts/compare_anlin_corpus.py draft.md --corpus-dir "C:\Users\34025\Desktop\Anlin"
python scripts/build_style_profile.py "C:\Users\34025\Desktop\Anlin" --output references/style-profile.json
python scripts/check_style_profile.py draft.md --profile references/style-profile.json --phase <A|B|C|D> --genre <standard|sincere|micro-hope|surreal> --draft-gate
python scripts/calibrate_style_profile.py "C:\Users\34025\Desktop\Anlin" --profile references/style-profile.json
python scripts/prepare_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --min-fragment-chars 550 --seed 1
python scripts/run_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --rounds 8 --min-fragment-chars 550 --placebo-rounds 2
python -m unittest discover -s test
```

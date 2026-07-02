---
name: anlin
description: Use when the user explicitly asks for Anlin, 日寄, Anlin-style anonymous blind-evaluation writing, 像Anlin那样写, 模拟日寄, or asks to generate/review/evaluate prose against the Anlin corpus. Do not use for ordinary depressed prose, generic Zhihu answers, or black-humor web writing unless Anlin or 日寄 is named.
metadata:
  compatibility: opencode
  corpus: C:\Users\34025\Desktop\Anlin
  target: anonymous-blind-evaluation
---

# Anlin Writing Skill

This skill generates, reviews, and evaluates Anlin-style Chinese prose for anonymous blind evaluation.

The goal is narrow:

> Make generated text less stably identifiable as generated text in anonymous blind review. Report only test conditions, sample size, and recognition/pass rates. Do not claim real authorship, provenance, or "indistinguishable from the original author."

Generated prose should not contain process labels such as "仿写", "AI", "生成", "验证通过", or "38篇语料". Controller notes and validation reports may mention methodology; the prose body must not.

## Load Order

Always start with these two files:

1. `references/runtime-brief.md`
2. `references/feature-budget.md`

Then load only the branch-specific files:

| Need | Load |
|---|---|
| Target date, phase, or projection handling | `references/era-state.md` |
| Standard, sincere, micro-hope, surreal, or mixed genre choices | `references/generation-modes.md` |
| Detailed rhythm, structure, endings, Bathos | `references/structure-patterns.md` |
| Specific characters or role budget | `references/role-orchestration.md`, then `references/anlin-characters.md` |
| Wording uncertainty or hard-rule review | `references/vocabulary-rules.md` |
| Concrete examples by topic | `references/anlin-reference-library.md`, `references/samples-index.md` |
| Post-draft critique | `references/review-rubric.md`, `references/writing-checklist.md`, `references/self-check.md` |
| Anti-copying and overlap checks | `references/anti-pastiche.md` |
| Full validation and blind review | `references/validation-protocol.md`, `references/blind-judge-angles.md` |

Do not read every reference before drafting. The generation pass uses a small state model; the critique pass uses the rule library.

## Workflow

### 1. Confirm Inputs

If the user has not already supplied them, ask once for the minimum missing inputs:

- target date/time or `inferred`
- genre: standard diary, sincere, micro-hope, surreal, mixed, or unspecified
- concrete background material, if any
- whether web/background lookup is allowed

If the user refuses or leaves inputs open, proceed with `inferred` or `fictional` status. Do not invent specific real-world events.

### 2. Build The State Card

Before scene generation, write an internal state card using `runtime-brief.md`:

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

This state card is internal unless the user asks to see process notes.

### 3. Sample Calibration

Read 3-5 short anchors, not the whole archive:

- 1-2 cards or samples from the same phase
- 1 sample from the same genre
- 1 contrasting sample to avoid monotone

If `references/corpus-cards/` exists, prefer cards first; open full originals only when a card points to a needed passage.

### 4. Generate Candidate Scenes

List 8-12 candidate fragments. Each fragment must come from one of:

- user-provided real material
- date/era texture
- plausible inferred daily life
- memory triggered by current sensory detail
- accidental observation

Mark each candidate by function: laugh, sting, tenderness, deflection, absurdity, analysis, body, money, social collision, memory, or noise. At least 30% should not directly serve the main theme. Keep at least two boring or accidental details available for the anti-detection pass.

### 5. Draft With Scene Modes

Use `generation-modes.md`. Do not force every scene through one template.

Select the smallest set of scenes that can carry the piece. Standard diary usually uses several fragments; sincere and micro-hope pieces can be short. The five-step cognitive path is a strong mode for misread/self-sabotage scenes, not a global obligation.

For blind-evaluation drafts, always produce a complete article with a title. Put the generated title on the first line as plain text or `# Title`; do not bold it, label it as `标题：`, or wrap it in controller notes. Serious blind review keeps and normalizes titles for all samples, then length-matches complete articles. A standard diary should normally be long enough to compare against full original articles. Short sincere or micro-hope pieces require short-original matched evaluation; otherwise expand with concrete actions, dialogue, and non-theme residue before blind testing.

### 6. Separate Review From Generation

After drafting, switch to review mode:

1. Run `scripts/check_anlin_violations.py <draft>`.
   - For formal standard-diary blind-evaluation drafts, run `scripts/check_anlin_violations.py <draft> --strict`; strict errors must be rewritten, not waived.
   - Even if the user only asked for prose, write the draft to a temporary/local file, run the checker, then output prose only after the checker pass. Do not print checker output unless the user asked for validation notes.
2. If the full corpus is available, run `scripts/compare_anlin_corpus.py <draft> --corpus-dir <corpus>`.
3. Read `review-rubric.md` and inspect the draft against the appropriate genre gates.
4. Use `writing-checklist.md` and `self-check.md` as critic material only. Do not retrofit every high-frequency label into the draft.
5. Run anti-pastiche checks if any source phrasing may have leaked.

Warnings are review prompts, not automatic failure. Errors and hard identity/date mistakes must be fixed. Do at most one targeted revision pass for ordinary warnings, but for formal standard-diary blind evaluation always prioritize prompt-shape leakage, single-theme density, sealed-night/story enclosure, quiet explanation, weak paragraph engine, missing title, copied source phrasing, diagnostic title, underbuilt length, and learned ending buttons. If one of these high-risk warnings remains after patching, rewrite from the scene slate instead of polishing the same draft. Do not loop until every ordinary warning disappears; some warnings are acceptable rhythm signals.

### 7. Validate Blind-Evaluation Claims

Only report quality claims after validation. Use `validation-protocol.md`.

For formal skill evaluation, the generation agent must receive only the realistic user prompt plus normal access to this skill. Do not give the generator blind-judge rubrics, previous failure analysis, source excerpts, controller mappings, or manual style hints outside the skill; that contaminates the test.

Required wording:

- acceptable: "In 8 anonymous rounds, judges identified the generated article in 1/8 rounds under these conditions..."
- unacceptable: "This is indistinguishable", "Anlin本人会这么写", "无法被看出来"

## Output Rules

- If the user asks for prose, output prose only unless they asked for process notes. The first visible line must be the article title, usually `日寄` or `# 日寄`; never print `State Card`, prompt buckets, scene slate, validation notes, Jaccard scores, checker summaries, or `草拟`.
- Do not include methodology labels inside the prose.
- If the user asks for validation, report commands, conditions, sample size, and results.
- If the corpus or background cannot be accessed, state the limitation in the validation report, not inside the prose.
- If the request asks to impersonate real provenance, publish as the real author, forge evidence, or deceive a reader about authorship, refuse that part and offer anonymous style-evaluation output instead.

## Validation Commands

```powershell
python scripts/check_anlin_violations.py draft.md
python scripts/check_anlin_violations.py draft.md --strict
python scripts/compare_anlin_corpus.py draft.md --corpus-dir "C:\Users\34025\Desktop\Anlin"
python scripts/prepare_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --min-fragment-chars 550 --seed 1
python scripts/run_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --rounds 8 --min-fragment-chars 550 --placebo-rounds 2
python -m unittest discover -s test
```

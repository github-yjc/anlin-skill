# Review Rubric

Use this after drafting. The reviewer should not be the same mental pass as the generator.

Scores and gates are evidence prompts, not proof of authenticity.

## Blocking Failures

Rewrite or refuse the relevant part if any appears:

- prose claims or implies real authorship/provenance
- methodology terms appear in the prose body
- post-corpus real-world facts are invented as if verified
- copied original signature passage or near-copy
- essay/advice/moral ending
- all scenes serve one obvious theme
- no concrete daily material
- uniformly short-line "fragment poem" surface in a standard diary
- clean symbolic closure where opening, central object, and ending all point to one obvious interpretation
- blind-evaluation draft is missing a title or is a length outlier under the selected complete-article protocol
- title format is the only sample-level difference, because originals and generated drafts were not normalized consistently
- title, scene order, and ending reveal the user's prompt as an outline
- the ending uses `哦`, `算了`, `睡了`, a dark screen, or a lone sound effect as a decorative style marker rather than a forced consequence
- formal blind-evaluation draft depends on extra style hints outside the skill and realistic user prompt

## Structural Gates

Score each applicable gate 0-2.

### Emotional Movement

- 2: at least three registers appear, with at least one sharp turn
- 1: two registers or slow transitions
- 0: monotone

Registers include laugh, sting, tenderness, deflection, absurdity, analysis, body intrusion, shame, and mouthy indifference.

### Scene Life

- 2: multiple scenes have internal turns; at least one scene would be missed if removed
- 1: scenes exist but several are single-beat
- 0: mostly flat observations or a linear essay

### Viewpoint

- 2: limited first-person daily experience; systems seen through lived details
- 1: occasional commentator stance
- 0: industry observer, therapist, essayist, or content creator voice

### Ending

- 2: ending carries accumulated weight and refuses closure
- 1: tonally plausible but portable
- 0: generic closing, explanation, blessing, advice, or moral

### Budget Control

- 2: 2-4 strong features used deeply
- 1: some label stuffing or missing one needed register
- 0: feature checklist/pastiche

### Detection Risk

- 2: contains roughness, topic drift, uneven rhythm, and at least one non-symbolic daily detail
- 1: generally plausible but a few scenes feel designed for the prompt
- 0: over-tidy, theme-first, uniformly short-lined, or visibly engineered to close a motif

### Prompt Displacement

- 2: prompt material is partially buried in side actions, other people's lines, app surfaces, or practical consequences; at least one prompt item is ignored or displaced
- 1: the article includes prompt material directly but interrupts it with non-theme residue
- 0: the article proceeds through the prompt items in visible order

### Evaluation Isolation

- 2: the draft could plausibly be produced from a normal user request plus this skill alone
- 1: the draft benefits from a detailed test prompt but does not rely on hidden judge feedback
- 0: the draft relies on extra controller hints, prior blind-failure analysis, copied source excerpts, or judge rubric language given to the generator

### Blind-Test Robustness

- 2: complete article with title matches the selected length band; title is plausible for the genre and period; no title, length, ordering, or topic cue dominates; at least three evidence families would be needed to accuse it
- 1: some robustness issues remain, but none can identify the sample alone
- 0: title/length/genre/structure makes the sample easy to identify before close reading

### Title Contract

- 2: title fits genre, phase, defense level, and body relation without over-explaining the piece
- 1: title is plausible but generic, too informative, or slightly overdesigned
- 0: missing title, wrong genre signal, or title-to-body contract gives away artificial construction

### Ending Consequence

- 2: final movement follows from an action, interruption, physical consequence, reply, route, payment, object, or unfinished chore
- 1: ending is tonally plausible but uses a familiar short retreat
- 0: ending behaves like a learned style button or completes the emotional argument

## Genre Adjustments

Sincere pieces may score lower on jokes and dialogue without failing. They must score high on concrete cost, restraint, and ending.

Micro-hope pieces may be short. They must avoid universal encouragement.

Surreal pieces may loosen causality. They must keep body/social/money coordinates.

Short, sincere, micro-hope, and surreal pieces are especially vulnerable to looking generated because models overuse polished minimalism. For these genres, require at least one rough ordinary detail that does not behave like a symbol.

If a short genre is intentionally short, do not evaluate it against full-length standard diary articles. Use matched short originals or report the setup as invalid for the recognition-rate target.

## Script Outputs

Use script outputs this way:

- `error`: fix before release unless the finding is proven false and documented.
- `warning`: inspect manually; do not treat as automatic failure.
- `info`: rhythm or metadata signal only.

The checker must not be calibrated so tightly that original corpus files fail as generated-style violations.

## Report Template

```markdown
## Validation Summary

- target:
- date-zone:
- corpus:
- commands:
- blind rounds:
- judge type:

## Results

- checker errors:
- checker warnings reviewed:
- corpus overlap:
- structural gates:
- blind identification rate:
- raw accusation rate:
- stable accusation rate:
- false accusation rate:
- placebo calibration notes:
- invalid rounds:

## Decision

accept | revise | rewrite | inconclusive

## Limits

- what was not tested:
- why results do not prove authorship:
```

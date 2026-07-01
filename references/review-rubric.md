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

## Genre Adjustments

Sincere pieces may score lower on jokes and dialogue without failing. They must score high on concrete cost, restraint, and ending.

Micro-hope pieces may be short. They must avoid universal encouragement.

Surreal pieces may loosen causality. They must keep body/social/money coordinates.

Short, sincere, micro-hope, and surreal pieces are especially vulnerable to looking generated because models overuse polished minimalism. For these genres, require at least one rough ordinary detail that does not behave like a symbol.

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

## Decision

accept | revise | rewrite | inconclusive

## Limits

- what was not tested:
- why results do not prove authorship:
```

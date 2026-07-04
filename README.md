# anlin-writing

This OpenCode skill generates, reviews, and evaluates Anlin/日寄-style Chinese prose for anonymous blind evaluation. The target is narrow: reduce stable identification as generated text under documented test conditions, while reporting only conditions, sample size, recognition/pass rates, false accusations, invalid rounds, and limits.

It must not claim real authorship, provenance, or objective indistinguishability.

## Current Status

The skill is not yet proven to meet the `<=10%` stable impostor-identification target. The latest documented clean-run sample before this architecture pass cleared the hard generated-draft checker but still failed the style-profile audit, with drift in period density, short-line share, line-length variance, and connector balance. No current report yet contains 15 clean generation runs plus calibrated `3 impostor + 1 placebo` style rounds sufficient to claim the target.

This README should be updated whenever the runtime architecture, validation protocol, or latest evidence boundary changes.

## Install Path

Current installed skill path:

```text
C:\Users\34025\.config\opencode\skills\anlin-writing
```

Trigger phrases include `Anlin`, `日寄`, `Anlin-style`, `像Anlin那样写`, `模拟日寄`, and requests for Anlin corpus evaluation. The OpenCode skill name is `anlin-writing`; `Anlin` remains a trigger alias because users naturally ask for that name.

## Architecture

The important design choice is separation of layers. The generation agent should not read every file before writing; that turns review categories into visible article ingredients.

```text
anlin-writing/
├── SKILL.md                         # routing, clean-run boundary, output rules
├── references/
│   ├── clean-generation-brief.md     # first-draft contract
│   ├── runtime-layer-map.md          # maintainer architecture map
│   ├── runtime-brief.md              # compact generation theory
│   ├── generation-modes.md           # scene modes and prompt-displacement lenses
│   ├── feature-budget.md             # feature budget, not shopping list
│   ├── anti-ai-slop.md               # built-in anti-AI-writing layer
│   ├── anlin-background.md           # post-scene fact gate
│   ├── background-fact-classes.json  # machine-readable fact classes
│   ├── voice-model.md                # deeper persona/cognition model for repair
│   ├── structure-patterns.md         # montage, title, ending, Bathos
│   ├── vocabulary-rules.md           # lexical and sentence-form boundaries
│   ├── role-orchestration.md         # role budget and deployment
│   ├── anlin-characters.md           # character facts and constraints
│   ├── review-rubric.md              # post-draft review gates
│   ├── writing-checklist.md          # critique card, not pre-draft recipe
│   ├── self-check.md                 # post-draft human/agent checklist
│   ├── stylometric-ratio-protocol.md # corpus-prior audit method
│   ├── style-profile.json            # generated profile from 38 originals
│   ├── validation-protocol.md        # clean generation and blind testing protocol
│   ├── blind-judge-angles.md         # multi-angle judge matrix
│   ├── corpus-cards/                 # compact calibration cards, repair only
│   └── portable-corpus.md            # fallback when originals are unavailable
├── scripts/                          # deterministic gates and validation helpers
├── test/                             # tooling regression tests
├── evals/                            # 15 realistic and diagnostic prompts
└── audits/                           # smoke drafts for checker tests
```

Detailed layer ownership lives in `references/runtime-layer-map.md`.

## Technique Sources

The old README-level technique summary is now mapped to maintained references:

| Technique | Source |
|---|---|
| Voice/persona model | `references/voice-model.md` |
| Bathos / retreat timing | `references/structure-patterns.md` |
| Fragment montage and associative hooks | `references/structure-patterns.md`, `references/generation-modes.md` |
| Pseudo-academic concepts and crooked analysis | `references/structure-patterns.md`, `references/voice-model.md` |
| Cognitive path | `references/generation-modes.md`, `references/voice-model.md`, `references/stylometric-ratio-protocol.md` |
| Corpus-verified frequency and ratio claims | `references/style-profile.json`, `scripts/build_style_profile.py`, `scripts/calibrate_style_profile.py` |

## Runtime Flow

For ordinary formal article generation:

1. Load `references/clean-generation-brief.md` first.
2. Start from a small lived friction, not from a checklist.
3. Select scenes from action, body, screen, money, route, social misfire, memory trigger, or useless residue.
4. Open `anlin-background.md` only after selected scenes already contain facts that need checking.
5. Write a complete titled `draft.md` before the first checker.
6. Run `scripts/clean_run_checker.py draft.md --strict --draft-gate`.
7. Do at most one repair/rewrite and at most two clean-run checker calls.
8. After the second checker call, output the current `draft.md` exactly.

For controller validation, use the full validation layer after generation:

```powershell
python scripts/check_anlin_violations.py draft.md --strict --draft-gate --corpus-dir "C:\Users\34025\Desktop\Anlin"
python scripts/compare_anlin_corpus.py draft.md --corpus-dir "C:\Users\34025\Desktop\Anlin"
python scripts/check_style_profile.py draft.md --profile references/style-profile.json --draft-gate --strict
python scripts/calibrate_style_profile.py "C:\Users\34025\Desktop\Anlin" --profile references/style-profile.json
python scripts/run_blind_test.py draft.md "C:\Users\34025\Desktop\Anlin" --rounds 8 --placebo-rounds 2 --min-fragment-chars 550
```

## Core Principles

- Background facts are contradiction boundaries, not article ingredients.
- Game is allowed, not required. Corpus evidence supports broad 王者/游戏 facts, not current match reports, roles, lanes, ranks, tactical calls, or scoreboards.
- Anti-AI-writing behavior is built into this skill. Runtime generation must not depend on any external anti-slop or personal writing skill.
- Corpus ratios are post-draft audit tools, not pre-draft quotas.
- Blind judges must be open-set and may answer `NONE`.
- Placebo all-original rounds are mandatory for serious claims.
- If a failure repeats, improve the earliest responsible generation layer, not only the checker.

## Verification

Recommended local checks after edits:

```powershell
python -m py_compile scripts\*.py
python -m unittest discover -s test -p test_anlin_tooling.py
python scripts\build_style_profile.py "C:\Users\34025\Desktop\Anlin" --output references\style-profile.json
python scripts\calibrate_style_profile.py "C:\Users\34025\Desktop\Anlin" --profile references\style-profile.json
```

Fresh pass/fail claims should quote the exact command results. Older results in this README are status boundaries, not current verification.

## Development Notes

`work/` contains local iterative outputs and is intentionally ignored by git unless a specific artifact is promoted into `audits/`, `evals/`, or `references/`. Do not delete process artifacts until information-loss review confirms they are no longer needed.

The skill is maintained as part of the `github-yjc` skill collection under the MIT license.

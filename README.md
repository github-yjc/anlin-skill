# Anlin Skill

> A writing discipline disguised as a skill. Reverse-engineered from 38 original articles through systematic corpus analysis, blind audits, and iterative refinement.

This skill helps agents generate, review, and blind-test Anlin-style Chinese prose for anonymous evaluation. It does not claim real authorship or objective indistinguishability. The output is characterized by defensive humor layered over genuine pain, fragment-montage structure, and the signature **Bathos** technique: retreating from completeness at the last possible moment.

## Why This Exists

Most agent writing reads like an agent wrote it. Complete. Polished. Emotionally safe. Anlin's writing is none of these things — it halts unexpectedly, undermines its own seriousness, and leaves the reader to fill the silence.

This skill doesn't teach the agent to "be Anlin" — it constrains the agent away from its natural tendencies toward completeness, explanation, and emotional resolution. Quality claims are reported only as blind-evaluation conditions, sample sizes, and recognition rates.

## Quick Setup

1. Copy the `Anlin` directory to your skills folder:
   - **OpenCode**: `C:\Users\<user>\.config\opencode\skills\Anlin\`
   - **Claude Code**: `~/.claude/skills/Anlin/`

2. Restart your agent. The skill will auto-load when triggered.

3. Trigger: ask for "Anlin" / "日寄" / "像Anlin那样写" / "模仿日寄" / "知乎摆烂写手风格".

## How It Works

```
┌───────────────────────────────────────────────┐
│                  SKILL.md                     │
│         runtime routing pipeline              │
│      state card → feature budget →            │
│      scene modes → separate review            │
└─────────────────────┬─────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                  ▼
┌─────────┐  ┌──────────────┐  ┌──────────────┐
│ voice-  │  │  structure-  │  │   writing-   │
│ model   │  │  patterns    │  │  checklist   │
│ (269L)  │  │  (204L)      │  │  (29 rules)  │
└─────────┘  └──────────────┘  └──────────────┘
    │              │                  │
    └──────┬───────┴────────┬─────────┘
           ▼                ▼
    ┌────────────┐  ┌──────────────┐
    │  era-state │  │  vocabulary- │
    │  (86L)     │  │  rules (162L)│
    └────────────┘  └──────────────┘
           │                │
           ▼                ▼
    ┌────────────────────────────┐
    │  reference files +         │
    │  validation scripts        │
│  = runtime + review layers │
    └────────────────────────────┘
```

## What Makes This Different

Unlike prompt-based imitation, this skill operates at the **architecture level**. Every rule lives in a reference file the agent reads at decision time — not in a prompt that gets compressed, forgotten, or worked around.

### Core Techniques

| Technique | Description |
|---|---|
| **Voice Model** | 12-dimension character operating system: perception, emotion, humor, social position, dialogue, thought patterns, reader relationship, auto-ethnographic stance |
| **Bathos (撤退)** | The signature move — escalate toward profundity, then retreat into the body or the absurd. Five retreat forms catalogued. |
| **Fragment Montage** | 5-12 scenes per article, connected by associative leaps, not logic. Each scene: setup → punchline → (optional) tag. |
| **Pseudo-Academic Concepts** | Create → define → apply to 3+ scenes → destroy. "应届生廉价定理", "湿气重诊断体系", "A3.1". |
| **Cognitive Path** | Five-step mental sequence embedded in the writing step: concrete detail → deliberate misinterpretation → self-sabotage → defense → land and leave. |
| **Corpus-verified** | All frequency claims audited against 38 original articles. Deletion of fabricated quotes. Recalibration of character appearances, vocabulary counts, and structural patterns. |

### What the Agent Learns NOT to Do

- Don't summarize or conclude
- Don't explain why something is funny
- Don't resolve emotional tension
- Don't use "然后...然后..." sequencing
- Don't write complete sentences where fragments work better
- Don't write "金句" that belongs on a motivational poster
- Don't let sincerity exceed 5 lines without a joke

## Directory Structure

```
Anlin/
├── SKILL.md                      # Entry point
├── README.md                     # This file
├── references/
│   ├── runtime-brief.md           # Core generation runtime
│   ├── feature-budget.md          # Hard requirements and genre budgets
│   ├── generation-modes.md        # Scene mode library
│   ├── review-rubric.md           # Separate critique gates
│   ├── anti-pastiche.md           # Source overlap and copying guardrails
│   ├── corpus-cards/              # Generated lightweight cards from 38 originals
│   ├── voice-model.md             # Detailed role model
│   ├── writing-checklist.md       # 30 rules: identity + dialogue + text + role budget
│   ├── structure-patterns.md      # Structure, spine, Bathos, endings (204 lines)
│   ├── vocabulary-rules.md        # Negative space: what Anlin never writes (162 lines)
│   ├── era-state.md               # Four-phase evolution model (86 lines)
│   ├── anlin-characters.md        # Character system with deployment rules (96 lines)
│   ├── role-orchestration.md      # Role budget, frequency, random-name rules
│   ├── anlin-reference-library.md # 11-dimension reference samples
│   ├── samples-index.md          # 8-10 original text samples for calibration
│   ├── self-check.md             # Post-writing self-audit
│   ├── evals.md                  # Multi-agent blind evaluation protocol
│   ├── validation-protocol.md    # Blind test workflow
│   ├── blind-judge-angles.md     # Multi-angle judge matrix and required reason format
│   ├── portable-corpus.md        # Corpus fragments for offline use
│   └── subagent-prompts.md       # Agent delegation templates
├── scripts/
│   ├── check_anlin_violations.py  # Automated rule violation scanner
│   ├── compare_anlin_corpus.py    # Corpus surface-overlap comparison
│   ├── analyze_anlin_roles.py     # Role frequency analysis (38-article corpus)
│   ├── build_corpus_cards.py      # Corpus-card generator
│   ├── prepare_blind_test.py      # Single blind-test round preparation
│   └── run_blind_test.py          # Multi-round blind-test preparation
├── test/
│   └── test_anlin_tooling.py
├── evals/
│   ├── evals.json
│   └── README.md
└── audits/
    └── checker-smoke-draft.md
```

## Quality Assurance

This skill was developed through an adversarial refinement loop:

1. **Corpus Analysis**: 38 articles → structural patterns, character frequencies, vocabulary domain
2. **Blind Testing**: Human readers judge generated vs. original; agent self-identification tests
3. **Reverse Audits**: Systematic cross-checking of every claim in the skill against the original corpus
4. **Iterative Fixes**: Each audit round surfaces gaps → fix → re-test

The skill does not claim indistinguishability from the original. It claims methodological rigor in the attempt.

## Author

Maintained as part of the [github-yjc](https://github.com/github-yjc) skill collection.

## License

MIT

# anlin-writing Layer 0/1 Source Interface Design

## Scope

This change addresses the fresh bounded failures in iteration-151. It changes only the first-draft source contract for standard clean-eval generation. It does not change hard-gate thresholds, style-profile calibration, clean-run preflight budgets, finalized repair routing, or blind-review protocol.

The current engineering corpus is the 38 files under the configured corpus directory. A claim about a historical 28-file subset requires an explicit file list and is outside this change.

## Evidence and root cause

Iteration-151 produced valid process-boundary evidence but no quality-valid bounded case. The qwen3.7-plus artifact was hash-stable and trace-clean at the stop boundary, yet its snapshots were 477, 450, and 467 Chinese characters. The wrapper repeatedly reported an underbuilt source, thin movement connections, weak paragraph engine, and missing public roughness.

The source references currently use “release a carrier after one consequence transfer” alongside “complete standard-diary mass” and “one transfer, then exit” social-decline wording. The intended rule is local: one person/place/transaction/object carrier must not repeat the same proof. A model can instead read it globally and stop after one short transfer, producing a coherent but underbuilt article. This is a source-interface ambiguity, not evidence that the checker threshold is wrong.

## Proposed architecture

### 1. Separate local carrier restraint from article-level movement

Define the invariant explicitly:

- A carrier is released after it has delivered one useful consequence so the same material does not become a repeated proof ledger.
- The article still needs several distinct action transfers through different media. “One transfer” never means “one transfer for the whole article.”

### 2. Use a positive source slate instead of a metric checklist

For a standard diary, the generator privately builds several breathing clusters in a stable order:

1. a practical friction that exists without the prompt;
2. the prompt pressure entering an already moving action;
3. a cost, reply, route, or body decision that changes the next move;
4. one refusal-coupled non-screen consequence;
5. a release into a different medium;
6. an unfinished practical tail.

These are functional movements, not required props or separate witness/roughness/connector packets. The generator chooses the smallest facts already supported by the prompt and source boundary.

### 3. Keep controller-only measurements out of the source contract

The wrapper remains the only bounded checker. It keeps exact counts and the existing preflight stop boundary. The source references may describe a complete article shape qualitatively, but they must not turn length, punctuation, or profile ratios into a pre-write optimization loop.

### 4. Leave finalized repair unchanged until a valid bounded source exists

The compact finalized brief already hides detailed diagnostics and routes the repair agent through `draft.md` plus `repair-brief.txt`. It will be tested only after a fresh bounded artifact is strong enough to be a meaningful finalized input. Finalized repair must not compensate for a failed first-draft source.

## Acceptance criteria

- A regression test fails before the wording change and passes after it, proving the local/global carrier distinction is present in both standard source references.
- Existing routing and checker tests remain green.
- Full unittest, Python compilation, diff check, 38-file strict corpus scan, original style calibration, and runtime portability scan remain clean.
- A fresh bounded run is judged by artifact, trace, hard gate, and style profile separately. A stopped underbuilt artifact is recorded as process evidence only.
- No blind-ready or recognition-rate claim is made until the complete evidence package exists.

## Risks and non-goals

- Do not add a new hard gate merely to enforce the source slate.
- Do not insert background facts, named witnesses, or model-specific branches.
- Do not relax style-profile thresholds to make one generated artifact pass.
- Model availability failures remain unavailable attempts, not quality evidence.

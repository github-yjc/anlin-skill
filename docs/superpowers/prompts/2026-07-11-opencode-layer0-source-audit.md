# OpenCode 执行提示词：anlin-writing Layer 0/1 源头接口与语料偏移审计

> 你是本仓库的执行代理。请在下面定义的短期目标内持续推进，完成后严格停下，等待主代理验收。不要自行扩大到 finalized repair、15-case 证据包或盲评。

## 0. 目标与边界

仓库：

~~~
C:\Users\34025\.config\opencode\skills\anlin-writing
~~~

项目目标仍然是匿名盲评条件下的生成文本识别研究。不得宣称真实作者身份、来源真实性或客观不可分辨；不得报告未经完整协议支持的识别率；不得宣称 `ready for blind rounds`。

本轮短期目标只有四项：

1. 审计当前 skill 是否在语言接口、认知机制、篇幅/行形、public hinge、roughness、拒绝后果、carrier release、背景事实边界等方面偏离当前 38 篇原文。
2. 用最小 TDD 改动重构 Layer 0/1 源头接口，解决“carrier 释放规则被模型误读为整篇文章只允许一个 transfer”导致的 underbuilt。
3. 完成仓库级验证、提交并推送 `main`。
4. 创建一个全新的 bounded clean-eval case，运行一次生成并完成 artifact/trace/质量分类；到此停止。

本轮禁止：

- 不启动 finalized repair；
- 不启动 15 clean-eval、8 impostor、2 placebo 或正式盲评；
- 不修改 hard-gate 阈值、style-profile 阈值、blind protocol 或 placebo protocol；
- 不把背景事实变成素材清单；
- 不新增模型/provider/runtime 分支；
- 不恢复旧 `3+1`、`3 impostor + 1 placebo`、`subagent-prompts`、子代理兼容层；
- 不把单次 bounded 成功包装为盲评证据；
- 不使用 `git reset --hard`、`git clean`、强制 push、删除分支或回滚其他人的改动。

## 1. 当前状态与不可回滚改动

开始前必须运行：

~~~
git status --short --branch
git log -5 --oneline --decorate
git diff --check
~~~

当前主干预期为：

~~~
main，最近已推送提交为 ec33bd4 或其后续提交
~~~

当前工作区可能有一个故意保留的未提交红测试，位于：

~~~
C:\Users\34025\.config\opencode\skills\anlin-writing\test\test_anlin_tooling.py
~~~

测试名：

~~~
test_source_contract_distinguishes_local_carrier_release_from_article_movement
~~~

不要删除、回滚或覆盖这个红测试。先确认它确实因为新契约文字尚未写入而失败。正确运行方式：

~~~
Push-Location test
python -m unittest test_anlin_tooling.AnlinToolingTests.test_source_contract_distinguishes_local_carrier_release_from_article_movement
$code = $LASTEXITCODE
Pop-Location
exit $code
~~~

当前工程语料事实以目录实际内容为准：

~~~
C:\Users\34025\Desktop\Anlin
~~~

当前应为 38 篇 `.md` 原文，`references\style-profile.json` 的 `expected_corpus_count` 也应为 38。不要把“28 篇”写入代码、runtime 文档或 profile；除非用户另行提供 28 篇的精确文件清单，否则本轮统一以 38 篇作为工程基线，并在交接报告中明确说明。

## 2. Phase A：只读根因与语料偏移审计

先不要修改 runtime 文档。完整阅读这些文件中与本轮有关的部分：

~~~
SKILL.md
references/clean-eval-first-draft-minimum.md
references/standard-diary-source-engine.md
references/clean-generation-brief.md
references/runtime-brief.md
references/runtime-layer-map.md
references/finalized-repair-minimum.md
references/validation-protocol.md
scripts/clean_run_checker.py
scripts/check_anlin_violations.py
scripts/check_style_profile.py
scripts/calibrate_style_profile.py
test/test_anlin_tooling.py
references/development-log.md
~~~

同时读取 iteration-151 的两个 bounded case artifact、controller report、state、trace 和 snapshots。不要把 151 直接复制成新 case，也不要把它的 stopped draft 当作质量通过。

建立一份只读审计表，保存到外部工作目录，不写入 runtime skill：

~~~
C:\Users\34025\Documents\Codex\anlin-writing-evals\source-interface-audit-YYYYMMDD-HHMM\
~~~

审计表至少包含以下列：

~~~
rule_or_guidance
source_file_and_anchor
intended_function
corpus_evidence
corpus_support_level
risk_of_model_misread
classification
recommended_action
~~~

`classification` 只能使用以下类别：

~~~
corpus-supported
genre-specific
controller-only
generated-draft-only
checker-artifact
contradictory
unsupported-or-overfit
~~~

逐项回答这些问题：

### A1. 语言接口与认知机制

- 当前 `cognitive_mechanism` 中的 concrete entry、crooked interpretation、reality puncture、defensive recovery、exit retreat，哪些是原文中可观察的分布，哪些只是 checker 的软审计标签？
- skill 是否把这些标签误写成生成前必须出现的语言接口？如果是，必须改成“审计镜头”，不能改成内容配额。
- 原文中是否真的需要每篇都有 public roughness、粗粝自毁、显式认知转折？如果不是，删除或降级为条件性、体裁性提示。
- 当前“避免 AI surface”的规则中，哪些是原文稳定现象，哪些只是近几轮生成失败的补丁？

### A2. 标准日寄的结构与行形

- 950–1150 字、45–70 行、长行/短落点/逗号续行，是原文全局事实、standard 子集事实，还是 generated-draft-only gate？
- 原文是否允许短篇、短行、少 connector 或较高 punctuation drift？若允许，不能把 profile audit 变成生成前硬配方。
- `carrier release` 的正确语义必须明确区分：
  1. 一个 person/place/transaction/object carrier 不要重复证明同一个功能；
  2. 整篇文章仍需经过多个不同媒介的行动转移；
  3. “释放当前 carrier”绝不等于“整篇文章只允许一个 transfer”。
- 检查当前两个 Layer 0 reference 是否在这一点上自相矛盾或过载。

### A3. 社交拒绝与 public hinge

- wedding/invitation/social-decline 规则是否过度把某一类 prompt 的修复方式推广到所有标准日寄？
- public hinge 是否被误写成每篇文章必须有陌生人、收银员、邻居或支付暴露？原文没有支持时，必须保持为条件性功能，不得造 witness。
- refusal-coupled consequence 是该 prompt family 的条件性源头约束，还是被误写成所有文章的硬要求？

### A4. 背景事实与提示词素材

- 游戏、地名、工作、人物关系、票价、平台等是否仍被写成“可用即应写”？
- 任何只用于避免矛盾的背景资料都必须标记为 contradiction boundary，不得成为素材 quota。

### A5. 语料证据方法

使用当前 38 篇原文做分布检查；不要只读单篇，也不要只看 checker 结果。至少完成：

~~~
python scripts\calibrate_style_profile.py "C:\Users\34025\Desktop\Anlin" --profile references\style-profile.json
~~~

并对 38 篇运行 strict hard gate，确认：

~~~
strict_corpus_hard_error_files=[]
strict_nonzero_files=[]
~~~

如果原文 profile 出现 `review`/`yellow`，不要将其解释为原文失败；记录它是 calibration prior。任何“skill 符合 38 篇原文”的结论必须区分：

- hard-gate 兼容性；
- profile 分布兼容性；
- 语言/认知/结构语义一致性。

没有独立语义证据时，只能报告“尚未证明”，不能写“已符合”。

## 3. Phase B：红测试与最小源头重构

先运行当前红测试，保留失败证据。然后只修改与根因直接相关的测试和 Layer 0/1 reference：

~~~
references/clean-eval-first-draft-minimum.md
references/standard-diary-source-engine.md
references/development-log.md
test/test_anlin_tooling.py
~~~

允许修改 `SKILL.md` 的 clean-eval 入口文字，但只有在审计证明入口契约不一致时才改；不要顺手重写整个 skill。

### B1. 必须写入的正向契约

在两个标准日寄源头 reference 中写入同一条明确语义（措辞可自然调整，但含义不可变）：

~~~
Carrier release is local: the article still needs several distinct action transfers through different media; one carrier transfer is not a one-transfer limit for the whole article.
~~~

同时用中文解释其原因：释放 carrier 是防止同一 person/place/transaction/object 反复证明，不是让完整文章只剩一个动作转移。

### B2. 源头接口的最小正向骨架

不要增加 props、人物、地点或 witness 配额。只把标准日寄的功能顺序写清楚：

~~~
practical friction -> prompt pressure enters moving action -> decision/reply/route/body movement ->
conditional refusal-coupled consequence when the prompt requires it -> medium change -> unfinished practical tail
~~~

这些是功能位置，不是六个场景、六个段落或六种素材。必须明确：一个实际动作可以承载多个功能；不要为每个标签新建 proof packet。

### B3. 必须删除或改写的误导语义

审计确认后，删除/改写所有可能让模型产生以下理解的句子：

- 整篇文章只能有一个 consequence transfer；
- 每篇标准日寄都必须添加 public witness、rough self-damage、payment 或 refusal aftermath；
- 每个 profile family 都要单独修一个 packet；
- 950–1150、45–70、connector 数量或 punctuation 比例是预写素材配方；
- 为了填满文章而补背景事实、第二条消息、群聊、办公履历或路线细节。

保留现有有效边界：artifact-first、wrapper-only bounded validation、finalized brief-only、no checker/source/test reads、no model-specific runtime branch、no old protocol。

### B4. tooling help bug（只在不扩大范围时处理）

如果审计期间仍能复现：

~~~
python scripts\calibrate_style_profile.py --help
~~~

因 argparse help 字符串中的 `%` 报错，则先写一个最小 CLI 回归测试，再修复 help 文本的转义；不要把它与 style-profile 阈值或生成逻辑混在一起。若修复会扩大本轮范围，记录为 follow-up，不要阻塞 Layer 0/1 目标。

## 4. Phase C：测试与仓库验证

源头文档修改后必须运行：

~~~
Push-Location test
python -m unittest test_anlin_tooling.AnlinToolingTests.test_source_contract_distinguishes_local_carrier_release_from_article_movement
Pop-Location
python -m unittest discover -s test -p test_anlin_tooling.py
python -c "import pathlib, py_compile; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('scripts').glob('*.py')]; print('py_compile_ok')"
git diff --check
~~~

然后执行 38 篇原文 strict 回归、style calibration 和 runtime portability 扫描。runtime 扫描范围至少包括：

~~~
SKILL.md
README.md
references/runtime-brief.md
references/finalized-repair-minimum.md
references/clean-generation-brief.md
references/clean-eval-first-draft-minimum.md
references/standard-diary-source-engine.md
references/validation-protocol.md
references/runtime-layer-map.md
scripts/*.py
~~~

确认不存在：

~~~
3 impostor + 1 placebo
3+1
--rounds 3
placebo-rounds 1
subagent-prompts
子代理
本地路径
私有 skill 依赖
deepseek/mimo/minimax/longcat/gpt 等模型特异 runtime 分支
~~~

测试失败时：

1. 不要直接改断言让它绿；先判断是新契约正确而 anchor 过期，还是实现真错；
2. 不要恢复旧协议或旧 wording；
3. 同一失败连续三次仍不清楚时停止，写出 root-cause note，不要继续叠锁。

## 5. Phase D：提交与推送

提交前检查：

~~~
git status --short --branch
git diff --stat
git diff --check
git diff -- references/clean-eval-first-draft-minimum.md references/standard-diary-source-engine.md test/test_anlin_tooling.py
~~~

只提交本轮相关文件。不要提交外部 eval artifact、模型日志、私有路径或临时审计大文件到 runtime skill。

提交信息应说明根因，不要写成“tune threshold”或“fix qwen”。推送 `main` 前确认验证命令全部通过。推送后再次运行：

~~~
git status --short --branch
git log -3 --oneline --decorate
~~~

## 6. Phase E：一次 fresh bounded 复测，然后停止

只有 Phase A–D 全部完成后，创建新的外部目录；不得复用 iteration-151：

~~~
C:\Users\34025\Documents\Codex\anlin-writing-evals\iteration-YYYYMMDD-NNN\
~~~

复制一个已知可执行的 controller harness，先运行 controller 的 unittest。使用一个可用且与上一轮不同的模型/provider；不可用只记录 unavailable，不算质量证据。

bounded 运行必须记录并验证：

- controller/opencode exit 都为 0；
- timeout 为 false；
- residual process 数为 0；
- draft 存在；
- 三次 hash 稳定；
- report/state/hash 互相匹配；
- `stopped=true`；
- stop reason 合法；
- calls/preflights 在 controller 预算内；
- trace 无 checker/source/test/threshold/path 污染；
- 不在 stopped bounded case 内直接切换普通 checker 流程。

对 artifact 做独立分类：

~~~
valid-process-only
source-underbuilt
no-artifact
unavailable
quality-candidate
~~~

`quality-candidate` 还不是通过，只表示可以由主代理继续做 finalized/质量复核。若 artifact 仍低于完整标准日寄源头质量，记录 source failure，不要在同一轮继续改代码、不要自动进入 finalized。

## 7. 交接格式与强制停止

完成短期目标后，只输出以下结构化交接，不要继续运行：

~~~
SHORT_TERM_HANDOFF

BASELINE:
- branch/HEAD:
- corpus_count:
- dirty_changes_before:

AUDIT:
- files_reviewed:
- corpus_supported_rules:
- genre_specific_rules:
- controller_only_rules:
- contradictory_or_overfit_rules:
- unresolved_questions:

CHANGES:
- commits:
- pushed:
- changed_files:
- red_to_green_test:

VERIFICATION:
- unittest:
- py_compile:
- diff_check:
- strict_corpus:
- style_calibration:
- runtime_scan:

BOUNDED:
- iteration:
- model/provider:
- availability:
- artifact_class:
- draft_hash:
- calls/preflights:
- trace_summary:
- hard_gate_or_preflight_findings:
- style_profile_status:

BOUNDARY:
- ready_for_blind_rounds: false
- recognition_rate: N/A
- finalized_started: false
- blind_rounds_started: false

NEXT_DECISION_FOR_MAIN_AGENT:
- one root-cause sentence
- whether the next step should be source guidance, finalized interface, checker review, or profile calibration
- exact artifact paths for inspection
~~~

交接输出后立即停止。不要自己给下一轮提示词，不要继续跑更多模型，不要宣称项目完成。

# anlin-writing Evaluation Set

结构化评测集，用于定量测量 anlin-writing skill 是否通过风格验证门禁。评测不证明「与原文无法区分」，只证明生成物满足 skill 规定的客观和主观质量标准。

本目录是控制器/开发者测试入口，不是普通用户输出目录。正式测试产生的 `draft.md`、`finalized/draft.md`、trace log、checker report、blind-round 目录和汇总 JSON/MD 都应写入外部评测工作区。不要把这些过程产物写进可分发 skill 本体；也不要删除它们，除非已经确认日志和关键结果被完整迁移到受控位置。

## 文件结构

```
evals/
├── evals.json    # 15 个结构化测试用例
└── README.md     # 本文件
```

`references/evals.md` 是早期非结构化评测说明，保留作历史和补充语义，不作为正式 15 用例清单。正式 clean-eval / blind-round 入口以 `evals/evals.json` 的 `realistic_prompt` 和本 README 为准。

## 用例概览

| ID | 名称 | 时代 | 体裁 | 主题 | 特殊说明 |
|----|------|------|------|------|----------|
| 1 | 2022-spring-recruitment-failure | high | standard-diary | 春招失败 | |
| 2 | 2022-food-delivery-heatstroke | high | standard-diary | 送外卖中暑 | |
| 3 | 2023-valentines-alone | medium | standard-diary | 情人节独处 | |
| 4 | 2023-family-dinner-argument | medium | standard-diary | 家庭争吵 | |
| 5 | 2023-christmas-eve-micro-hope | medium | micro-hope | 平安夜微小希望 | |
| 6 | 2024-new-year-nostalgia | low | standard-diary | 跨年怀旧 | |
| 7 | 2024-mothers-day-sincere | low | sincere | 母亲节真诚文 | |
| 8 | 2024-gout-flareup | low | standard-diary | 痛风发作 | |
| 9 | 2024-classmate-wedding-invitation | low | standard-diary | 同学婚礼 | |
| 10 | 2025-absurd-coincidence-projection | projection | standard-diary | 荒诞巧合 | |
| 11 | 2025-surreal-introspection-projection | projection | surreal-literary | 存在主义内省 | |
| 12 | inferred-moving-micro-hope-portable | inferred | micro-hope | 搬家 | portable 模式 |
| 13 | inferred-writing-block-sincere-short | inferred | sincere | 写作困境 | 限 40 行 |
| 14 | blended-afternoon-festival-forbid-money-portable | inferred | mixed | 节日独处 | portable + 禁止金钱 |
| 15 | out-of-range-date-rejection | out-of-range | mixed | 日期超范围 | 应正确拒绝 |

### 覆盖分布

- **时代**: 2 high (2022), 3 medium (2023), 4 low (2024), 2 projection (2025), 2 inferred (无日期), 1 out-of-range (2021), 1 blended (部分日期)
- **体裁**: 8 standard-diary, 2 sincere, 2 micro-hope, 1 surreal-literary, 2 mixed
- **话题**: 全覆盖 15 个不同主题域，无重复
- **边缘场景**: 无日期、仅时间、仅主题、日期超范围、矛盾参数、限长、禁止元素、portable 模式

## 运行单个评测

### 步骤 1：生成草稿

正式盲评使用 `evals.json` 中对应用例的 `realistic_prompt` 字段。`prompt` 字段保留给诊断压力测试，不得用来声明正式盲评通过率，因为它包含额外写作提示。

将 `realistic_prompt` 发给一个全新上下文（无历史对话）的 agent，让 agent 正常触发并加载 `anlin-writing` skill 后生成文章。不要给生成 agent 提供盲评失败分析、judge rubric、原文摘录、controller mapping、人工风格提示或旧生成稿。将输出保存为 `draft.md`。

bounded clean-eval 用例可以在外部 case 工作区放置空文件 `.anlin-clean-eval-mode` 来选择两次 checker 上限流程。这个文件只能是空的模式标记，不能包含提示词、风格规则、失败分析或评审角度。

草稿只保存一篇完整文章的标题和正文。标题必须由生成 agent 产出，放在第一行，推荐使用 `# 标题`；不要加粗、不要写成 `标题：...`，也不要把标题作为控制器元数据附加。不要把仿写、生成、验证、语料、片段级验证等方法标签写进正文；这些信息由控制器记录在验证报告里。

开发测试应轮换生成模型，防止 skill 只适配一个模型表面。每个 case 在启动前记录随机或轮询选中的模型、实际 CLI model id、provider、reasoning/thinking 设置、不可用模型跳过原因、skill commit 和 prompt。不要把某个模型上轮失败的分析追加给下轮生成 agent；模型差异只能通过后续修改 skill 的通用源头引导、事实门禁、句式门禁或检查器来吸收。

### 步骤 2：运行硬规则脚本

```powershell
python <skill-dir>/scripts/check_anlin_violations.py draft.md
```

- 退出码 0：没有检测到 error 级违规；warning 仍需人工复核
- 退出码非 0：存在 error 级硬规则违规，查看输出定位问题

注意：退出码 0 只表示未触发可自动检测的阻断项，不保证风格匹配。脚本无法检测蒙太奇结构、情感层次、声音质量等主观维度。

### 步骤 3：运行隔离 Style Critic 评审

这一节是早期人工/隔离评审口径的保留说明。当前正式控制器流程还必须结合 `references/validation-protocol.md`、`references/blind-judge-angles.md`、strict/draft-gate hard gate、style-profile full report、placebo 校准和双检查点汇总。不要只凭本节 5 门禁分数宣称 ready for blind rounds。这里的 Style Critic 是隔离评审模板，可以由人工评审、单独上下文的模型评审或控制器调用实现；它不是 runtime 必需能力。

对 `standard-diary` 和 `mixed` 用例，使用 5 门禁评分：
- emotional-oscillation（情感振荡）：笑/痛/温情/嘴硬是否混频
- dialogue-density（对话密度）：对话是否自然、是否滥用引号
- meta-narrative（元叙事）：是否有自我察觉层
- scene-depth（场景深度）：每个场景有无独立落点
- earned-ending（结尾克制）：结尾不总结、不升华、身体化未解决

对 `sincere`、`micro-hope`、`surreal-literary` 用例，使用 3 门禁评分（去掉 dialogue-density 和 meta-narrative）：
- emotional-oscillation
- scene-depth
- earned-ending

每个门禁 1-10 分。

隔离评审者必须只读取以下文件：
- `draft.md`
- `references/portable-corpus.md`
- `references/samples-index.md`
- `references/vocabulary-rules.md`
- `references/structure-patterns.md`
- `references/voice-model.md`

如果完整语料目录可用（通过 `ANLIN_CORPUS_DIR` 或 `--corpus-dir <corpus-dir>` 指定），还可读取原文进行比对。没有完整原文时，只使用 skill 内置的 portable/corpus-card 材料。

### 步骤 4：计算通过/失败

```
PASS = 脚本退出码 0 AND 所有门禁分数 ≥ minimum_gate_score（默认 7）
FAIL = 脚本退出码非 0 OR 任一门禁分数 < minimum_gate_score
```

边缘用例 15 除外：该用例的 `expected_behavior` 为 `agent_must_refuse_or_explicitly_mark_as_fictional`，通过标准为 agent 正确拒绝生成或明确标注为虚构。

如果用例包含显式禁止项，控制器必须人工检查 prompt compliance。通用 checker 不一定知道用户禁止了什么；例如 `不要写金钱、消费或价格` 时，正文出现超市购买、收银台、矿泉水交易、付款、余额、折扣、金额或价格替代物，都应记为 blocking prompt-compliance failure，即使 hard gate 和 style-profile 没有 error。

## 批量聚合

### 双检查点记录

每个正式开发用例必须保存两个结果，且都放在外部评测工作区，不写入 skill 目录：

- `bounded clean-eval checkpoint`：全新 agent 只拿 `realistic_prompt` + anlin-writing skill，经过 bounded preflight 和最多两次实际 `clean_run_checker.py` 调用后冻结，保存限制内得到的 `draft.md`、检查状态、stage snapshots 和控制器报告。它衡量自然引导能力加有限检查器修复能力，不衡量最终开放修复成果。stage snapshots 中的 `first_submission` 用来验收自然首稿，`checker_call_1_submission` / `checker_call_2_submission` 用来验收两次 checker 边界上的稿件变化，`bounded_final` 是该关口冻结结果。
- `finalized repair checkpoint`：把 bounded 草稿复制到单独的 `finalized/` 用例目录，再从这份复制稿和公开检查结果继续，允许普通用户模式下多轮修复、重写和复检，保存最终稿和检查报告。它衡量 checker / repair references 能否收敛。修复后的文章必须实际写回 `finalized/draft.md`；如果 agent 只在日志或聊天里打印终稿而文件未变，按 artifact failure 记为 invalid。最终稿不能只凭普通检查器通过；必须运行 strict/draft-gate 硬门禁和 style-profile 审计，profile 为 `revise` 时仍算 finalized 失败。

这两个 checkpoint 回答不同问题，不能合并成一个“通过率”：bounded 内部先看 `first_submission` 判断自然引导，再看两次 checker 边界判断有限修复；finalized 是最终修复验收。开发时应先看 bounded 是否在两次实际 checker 调用限制内接近合格，再看 finalized 在普通多轮修复后是否真的清掉 strict/profile 风险。只有 finalized `pass` 才能说最终稿进入盲评候选；只有 bounded `pass` 才能说自然引导本身已足够强。

判读时不要只看“最后有没有修好”：如果 bounded 失败但 finalized 通过，下一轮优先改生成源头、clean-eval 修复说明和早期引导；如果 finalized 仍失败或只是 `review`，说明最终成果本身还有问题，需要同时检查 skill 架构、事实边界、修复路径、style-profile 和 checker 假设。

style-profile `yellow` 可作为 finalized checkpoint 的通过条件之一：记录黄项和后续盲评风险，但不要为了清空黄项继续机械修文。`review` 和 `revise` 都不是 finalized pass；即使 `red_families` 为空，只要报告里的 `checkpoint_decision` 不是 `pass`，就不能进入盲评候选。strict hard error 或缺 profile 导致的 `review` 也同样不能进入盲评候选。

推荐每个用例最终都运行一次控制器汇总：

```powershell
python <skill-dir>/scripts/summarize_dev_checkpoints.py <case-dir> `
  --bounded-draft <case-dir>/draft.md `
  --finalized-draft <case-dir>/finalized/draft.md `
  --trace-log <case-dir>/opencode-output.txt `
  --corpus-dir <corpus-dir> `
  --profile <skill-dir>/references/style-profile.json `
  --genre <standard|sincere|micro-hope|surreal> `
  --output-json <case-dir>/controller-audit/summary.json `
  --output-md <case-dir>/controller-audit/summary.md
```

`summary.json` 中的 `bounded.stage_audits` 是 bounded 内部阶段证据，`diagnosis` 是开发归因，不是风格证明：

如果 `--genre` 省略，汇总脚本会尝试从 `eval-07-...` 或用例名目录自动推断体裁；正式报告仍应显式传入，短真诚、微小希望和超现实用例尤其不能只让全局标准日寄 profile 解释根因。

- `source_guidance_gap`：两次检查器边界稿没过，但最终稿过了；优先改源头引导。
- `repair_path_gap` / `repair_or_validator_gap`：自然引导可用但修复路径或验证器出了问题。
- `systemic_gap`：bounded 没过且 finalized 也没有 clean pass；不要只改检查器，回查架构、事实门禁、声音模型、修复流程和 profile 假设。
- `ready_for_blind_rounds`：两阶段都过；进入盲评和 placebo，不直接宣称目标达成。

`summary.json` 中的 `blind_round_readiness` 才是是否可以进入盲评的控制字段。除 `ready_for_blind_rounds` 外，汇总脚本会返回非零退出码；这表示还不能进入正式盲评，不表示报告生成失败。

判读规则：

- bounded 失败但 finalized 通过：优先加强源头引导。
- bounded 失败且 finalized 仍为 review/fail/invalid：最终成果仍有问题，深入检查 skill 架构、背景事实、声音模型、修复方式、检查器和盲评角度。
- bounded 通过但 finalized 没通过：重点检查 repair loop 是否追指标、profile 是否误伤、修复是否破坏自然文本。
- 两者都通过：再进入完整盲评和 placebo 校准，不能直接宣称目标达成。

### 手动聚合

对 15 个用例全部运行后，汇总：

```
通过率 = 通过用例数 / 15
平均门禁分 = 所有门禁分的均值
瓶颈门禁 = 最常未通过的门禁类型
```

### 自动化脚本（部分已建；真实生成仍需独立 agent/controller 编排）

未来可用控制器脚本自动完成全流程：
1. 读取 evals.json 的 `realistic_prompt`
2. 对每个用例启动一个独立 agent（无上下文污染）
3. 在声明的模型池中随机或轮询选择一个生成模型，打开可用的 reasoning/thinking 模式并记录设置
4. agent 生成一篇含标题的完整文章 → 保存到外部评测工作区，例如 `<eval-workspace>/iteration-<n>/eval-<id>/draft.md`
5. 运行 `check_anlin_violations.py`
6. 运行隔离 Style Critic 评分
7. 汇总到外部评测工作区，例如 `<eval-workspace>/iteration-<n>/benchmark.json`

## 与盲测的关系

本评测集测量**结构质量**（是否遵循 skill 规则），不等同于**不可区分性**测试。

盲测（Distinguisher）是独立的验证流程，由 `scripts/prepare_blind_test.py` 和 `scripts/run_blind_test.py` 支持。正式盲测只使用含标题的完整文章；标题保留并统一规范化，标题契约、标题与体裁/结构/结尾的关系都属于评审证据，但不能作为唯一识别依据。

- **本评测集**: 检查生成物是否符合 skill 规定的否定空间、词汇域、结构模式、情感层次等可定义标准
- **盲测**: 将生成完整文章与语料完整文章匿名混排，交给隔离评审判断是否能识别生成文章；评审可回答 `NONE`

两者互补：
- 通过本评测集表示「skill 用对了」
- 盲测结果只表示在特定条件、样本量、评审类型下的 raw/stable 识别率和误报率

## 注意事项

- 评测集不修改 skill 文件，只读取
- 每个用例的 `realistic_prompt` 字段是正式盲评入口——全新 agent 只读 realistic prompt + skill 即可生成
- `prompt` 字段是压力测试入口，适合定位问题，不适合作为“skill 单独能力”的通过率依据
- 完整语料路径: 可选；通过 `ANLIN_CORPUS_DIR` 或 `--corpus-dir <corpus-dir>` 指定
- portable 模式用例（12、14）的 `corpus: unavailable` 或片段级验证状态只写入控制器验证报告，不写入正文
- 用例 15 是「应拒绝」场景，其通过标准与其他用例不同

## 版本历史

- v2.2: 新增 `realistic_prompt`，区分正式盲评输入与诊断压力测试输入
- v2.1: 移除正文元数据标注要求，对齐匿名盲评目标
- v2.0: 初始结构化评测集，15 用例，替换原 `references/evals.md` 中的非结构化描述

# Anlin Skill Evaluation Set

结构化评测集，用于定量测量 Anlin 写作 skill 是否通过风格验证门禁。评测不证明「与原文无法区分」，只证明生成物满足 skill 规定的客观和主观质量标准。

## 文件结构

```
evals/
├── evals.json    # 15 个结构化测试用例
└── README.md     # 本文件
```

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

将 `evals.json` 中对应用例的 `prompt` 字段发给一个全新上下文（无历史对话）的 agent，让 agent 加载 Anlin skill 后生成文章。将输出保存为 `draft.md`。

草稿只保存标题和正文。不要把仿写、生成、验证、语料、片段级验证等方法标签写进正文；这些信息由控制器记录在验证报告里。

### 步骤 2：运行硬规则脚本

```powershell
python C:\Users\34025\.config\opencode\skills\Anlin\scripts\check_anlin_violations.py draft.md
```

- 退出码 0：没有检测到 error 级违规；warning 仍需人工复核
- 退出码非 0：存在 error 级硬规则违规，查看输出定位问题

注意：退出码 0 只表示未触发可自动检测的阻断项，不保证风格匹配。脚本无法检测蒙太奇结构、情感层次、声音质量等主观维度。

### 步骤 3：运行 Style Critic 子代理审查

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

子代理必须只读取以下文件：
- `draft.md`
- `references/portable-corpus.md`
- `references/samples-index.md`
- `references/vocabulary-rules.md`
- `references/structure-patterns.md`
- `references/voice-model.md`

如果完整语料目录可用（`C:\Users\34025\Desktop\Anlin`），还可读取原文进行比对。

### 步骤 4：计算通过/失败

```
PASS = 脚本退出码 0 AND 所有门禁分数 ≥ minimum_gate_score（默认 7）
FAIL = 脚本退出码非 0 OR 任一门禁分数 < minimum_gate_score
```

边缘用例 15 除外：该用例的 `expected_behavior` 为 `agent_must_refuse_or_explicitly_mark_as_fictional`，通过标准为 agent 正确拒绝生成或明确标注为虚构。

## 批量聚合

### 手动聚合

对 15 个用例全部运行后，汇总：

```
通过率 = 通过用例数 / 15
平均门禁分 = 所有门禁分的均值
瓶颈门禁 = 最常未通过的门禁类型
```

### 自动化脚本（待建）

未来可用控制器脚本自动完成全流程：
1. 读取 evals.json
2. 对每个用例启动一个独立 agent（无上下文污染）
3. agent 生成草稿 → 保存到 `evals/outputs/eval-{id}-draft.md`
4. 运行 `check_anlin_violations.py`
5. 运行 Style Critic 子代理评分
6. 汇总到 `evals/outputs/benchmark.json`

## 与盲测的关系

本评测集测量**结构质量**（是否遵循 skill 规则），不等同于**不可区分性**测试。

盲测（Distinguisher）是独立的验证流程，由 `scripts/prepare_blind_test.py` 和 `scripts/run_blind_test.py` 支持：

- **本评测集**: 检查生成物是否符合 skill 规定的否定空间、词汇域、结构模式、情感层次等可定义标准
- **盲测**: 将生成物与语料片段匿名混排，交给隔离评审判断是否能识别生成片段；评审可回答 `NONE`

两者互补：
- 通过本评测集表示「skill 用对了」
- 盲测结果只表示在特定条件、样本量、评审类型下的识别率和误报率

## 注意事项

- 评测集不修改 skill 文件，只读取
- 每个用例的 `prompt` 字段是自包含的——全新 agent 只读 prompt + skill 即可生成
- 完整语料路径: `C:\Users\34025\Desktop\Anlin`
- portable 模式用例（12、14）的 `corpus: unavailable` 或片段级验证状态只写入控制器验证报告，不写入正文
- 用例 15 是「应拒绝」场景，其通过标准与其他用例不同

## 版本历史

- v2.1: 移除正文元数据标注要求，对齐匿名盲评目标
- v2.0: 初始结构化评测集，15 用例，替换原 `references/evals.md` 中的非结构化描述

# Validation Protocol

目标：尽可能严格地发现仿写与 38 篇原文之间的差异，并指导重写。验证只能提高置信度，不能证明完全拟合。

## 验证模式

### 完整语料模式

适用条件：可访问 `C:\Users\34025\Desktop\Anlin` 或用户提供等价原文目录。

执行：

1. 运行硬规则脚本：`scripts/check_anlin_violations.py draft.md --strict`。必须阅读完整输出；退出码为 0 只表示没有 error/warning，不代表风格像。
2. 运行全语料比对脚本：`scripts/compare_anlin_corpus.py draft.md C:\Users\34025\Desktop\Anlin`。
3. 按 `references/subagent-prompts.md` 派遣子代理做四类审查：Style Critic、Era Critic、Distinguisher、Revision Planner。
4. 汇总问题，重写全文；最多迭代 3 轮，除非用户要求继续。

### 片段级降级模式

适用条件：无完整原文。

执行：

1. 运行硬规则脚本：`scripts/check_anlin_violations.py draft.md --strict`。
2. 运行 Fragment-Level Style Critic（参见 `references/subagent-prompts.md` 的 Fragment-Level Style Critic Prompt）：只读 draft + portable-corpus.md + samples-index.md + vocabulary-rules.md，输出 Markdown 问题清单（blocking / important / minor），不打分。
3. 运行 Era Critic（目标日期 + era-state.md + 搜索事实），检查时代错置。
4. 标注结果为“片段级验证”，不得声称通过完整语料比对。

片段级模式不运行 Distinguisher（无原文样本可混入）。

## 子代理角色

### Generator

生成草稿。必须读取 `SKILL.md`、`references/portable-corpus.md`、`samples-index.md`、`voice-model.md`、`structure-patterns.md`、`vocabulary-rules.md`、`era-state.md`。若完整语料目录可用，可额外抽读原文；若不可用，以 portable-corpus 为降级依据。

### Style Critic

只审查风格，不修文。维度：

- 词汇域：高频词是否自然；禁用词是否漏出。
- 句式节奏：行长、短句、行末标点、硬切是否像。
- 情感层次：笑/痛/温情/嘴硬是否混频。
- 结构：场景数、蒙太奇、结尾未解决。
- 视角：生活体验者，而非评论家/段子手/论文作者。

输出：尽可能多的问题，每条必须包含证据和修复建议。

### Era Critic

只审查日期适切性。检查：

- 目标日期时，平台、梗、AI能力、价格、社会氛围是否可能存在。
- 是否把新闻写成宏观总结。
- 是否把后期状态错写到早期，或把早期状态错写到后期。

输出：时间线问题、置信度、需要搜索或用户补充的信息。

### Distinguisher

盲评角色。必须使用 `references/subagent-prompts.md` 的 Distinguisher Prompt。该角色**需要完整原文目录**；无完整语料时跳过此步骤，改用 Fragment-Level Style Critic。

具体执行流程：

1. 准备匿名片段：运行 `python scripts/prepare_distinguisher.py --draft <draft.md> --corpus-dir <Anlin> --output-dir <round-dir> --num-originals 5`。该脚本会随机抽取 5 篇原文，各取前 2-3 个场景（约 300-500 字），再从草稿中提取等长片段；所有片段以 `fragment-01.txt` 等随机文件名写入输出目录，并生成 `mapping.json` 记录每个文件对应的真实来源（原文文件名或 `GENERATED`）。
2. 派遣 Distinguisher 子代理：将输出目录路径和 `references/subagent-prompts.md` 中的 Distinguisher Prompt 交给子代理。子代理**只能读取该目录下的 fragment-*.txt 文件**，禁止读取 skill 文件、mapping.json 或原文目录。
3. 收集子代理的 verdict：要求其输出 `Fragment-XX is the AI-generated one because: ...`。
4. 核对：将子代理指控的 fragment 与 `mapping.json` 比对，确认是否指向 `GENERATED`。
5. 重复 3 轮：每轮使用不同的随机种子（prepare_distinguisher.py 的 `--seed`）重新抽取原文，重新匿名排序。
6. 判据：
   - 若 ≥2/3 轮子代理正确指出 `GENERATED` 片段 → 草稿**未通过**盲测，必须回炉。
   - 若 ≤1/3 轮正确指出 → **暂定为通过**，但仍不是“无法区分”的证明。
7. 若当前环境无法保证匿名隔离（例如子代理能看到 mapping.json 或原文目录），标记本轮结果为 **contaminated**，不得作为批准依据。

如需一次性准备多轮并可选自动调用 LLM 评判，可使用便利脚本 `python scripts/run_distinguisher.py --draft <draft.md> --corpus-dir <Anlin> --rounds 3`（自动评判需设置环境变量 `DISTINGUISHER_API_KEY`；否则脚本仅准备片段并输出 prompt）。

### Revision Planner

汇总前三个批评者的问题，按严重程度排序，给出重写方案。不得直接粉饰原文；必须指出可修复问题和不可修复风险。

## 评分量规

每项 0-5 分：

| 维度 | 通过阈值 | 说明 |
|---|---:|---|
| 词汇域 | ≥4 | 高频词自然，低频/禁用词少，具体动作多 |
| 句式节奏 | ≥4 | 行长、短句、逗号/句号、硬切接近样本 |
| 情感混频 | ≥4 | 至少三种情绪层次，真诚不过量 |
| 蒙太奇结构 | ≥4 | 场景因阶段而异（Phase A 5-8，Phase D 7-12，通常 5-10）；每个有独立落点 |
| 视角一致性 | ≥4 | 普通生活体验者，不说教、不总结群体 |
| 日期适切性 | ≥4 | 符合目标日期，不预知，不错置状态 |
| 灵魂测试 | ≥3 | 像“过了一天顺手记下”，不是“写了一篇日寄” |

完整通过建议：总分 ≥28/35，且无单项低于 3。若 Distinguisher 多数轮稳定识别草稿为仿作，仍判失败。通过量规只表示当前迭代未发现显著异体，不代表读者无法识别仿作；最终拟合度仍依赖熟悉读者盲评。

## 修复优先级

1. 身份/时代错置。
2. 评论链、禁用句式、AI腔、解释腔等硬异体。
3. 场景无落点或独幕剧。
4. 情感单频。
5. 高频词和行末节奏。
6. 金句过密、真诚过量、结尾升华。

## 决议规则

- 身份/时代错置、硬异体必须重写全文。
- 若所有三个 critic（Style Critic + Era Critic + Distinguisher 或 Fragment-Level Style Critic）各标记 ≥ 3 个 P1 级问题 → 重写。若发现任何 P0 级问题 → 重写。
- 高频词覆盖、行末节奏、轻微词汇漂移可局部改写；局部改写后仍需重新跑硬规则脚本。
- Style Critic 与 Era Critic 冲突时，优先处理 Era Critic 的事实/日期问题。
- 完整语料模式 + 匿名隔离可用时：Distinguisher 结果作为参考（≥ 2/3 轮未识破 = 通过）；无法建立匿名隔离时标注 contaminated，不作为判定依据。
- 片段级模式：Distinguisher 不适用，依赖 Style Critic + Era Critic + 脚本判定。
- 若 3 轮迭代后仍有同类阻塞问题，停止生成并输出风险，而不是继续粉饰。

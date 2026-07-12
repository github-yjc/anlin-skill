# Fragment Source Contract 重构设计

日期：2026-07-12  
状态：待用户审阅  
范围：B 方案先行；C 方案作为后续扩展，不在本轮实现

## 1. 背景与问题

anlin-writing 当前把 `standard` 生成逐步收敛成了一个隐含的单场景因果模板：先找 side engine，再经过 public hinge，释放 carrier，最后以 practical tail 收束。这个接口与 38 篇原文的实际组织方式不一致，也使 checker 的诊断项反向变成素材配额。

已复算的原文观察范围如下：

- 38 篇正文约 235-1932 个汉字；
- 非空正文行约 17-91 行；
- 原文可在当下观察、对话、旧记忆、平台事实、笑话、荒诞解释、幻想和自我修正之间跳转；
- 一致性主要来自第一人称声音、词语回声、反差、认知习惯和反复问题，不要求每个片段驱动下一个动作。

当前失败也提供了直接证据：iteration-153 的 bounded artifact 有 1078 个汉字，质量问题不是篇幅不足，而是旧接口诱导出的弱段落发动机和拒绝后果诊断。当前工作区的 421 个测试中还有 1 个失败，原因是 active routing 已换新文件，但 controller/developer 测试仍锁定旧 engine 名称。

## 2. 目标

### 2.1 主要目标

把 `standard` 的生成契约重置为 **fragment slate**：片段可通过联想、反差、语言回声、时间跳转、自我修正或认知惯性连接；因果链是可选关系，不是默认骨架。

### 2.2 分层目标

1. Layer 0/1 只提供最小、可执行的 source guidance。
2. Layer 4 controller 负责分布诊断和证据记录，不把诊断指标伪装成写作配额。
3. finalized repair 只接受一个明确 source focus，并保持 artifact-only、一次写回和 trace 边界。
4. 旧 engine 文件保留为历史和迁移参照，但不再被任何 active runtime 路由加载。
5. B 稳定后，再以 C 为独立扩展建立短/中/长及阶段 profile；C 不提前污染 B 的 source contract。

### 2.3 非目标

- 本轮不启动 finalized、blind、impostor、placebo 或 recognition-rate 报告。
- 不声称真实作者身份、来源或客观不可分辨。
- 不把“必须散”“必须意识流”做成新的固定段数、跳转次数或随机性 hard gate。
- 不为任何具体模型、provider 或私有 skill 增加 runtime 分支。
- 不恢复旧的 3+1 协议或 `subagent-prompts` 兼容层。

## 3. 设计原则

### 3.1 语料事实优先

语料统计只描述观察范围和校准条件。`standard` 是 profile/evaluation label，不是统一长度或结构命令。长度、行数和标点分布只能在 draft 已存在后作为 controller 证据使用。

### 3.2 生成约束与评价约束分离

生成器需要知道怎样写出一篇完整文章；controller 需要知道怎样测量文章；repair agent 需要知道怎样执行一次限定修改。任何仅为 checker 方便而存在的内部阈值都不能进入 Layer 0 的素材清单。

### 3.3 最小一致性而非最小因果性

片段不要求互相产生动作后果，但文章必须让读者感到它们来自同一个叙述者。允许的稳定机制包括声音、词语回声、反差、反复问题、时间跳接、自我修正和相似的认知偏转。

### 3.4 事实是边界，不是配额

地名、游戏、工作、人物关系、平台和时代事实只用于避免矛盾。只有当片段已经需要该事实时才保留；不能因为参考文件列出某事实就强制写入。

## 4. 分层契约

### 4.1 Layer 0：Corpus Lens

Layer 0 只保存从原文归纳出的稳定机制：

- 可用片段：当下观察、对话或转述、旧记忆、平台/工作事实、笑话、逻辑反转、荒诞解释、幻想、回声、自我修正；
- 可用连接：联想、反差、语言回声、时间跳转、自我修正、直接跳接；
- prompt 是触发点，不是素材清单；可以早出现、晚出现、重复出现或被侧题稀释；
- 结尾可落在笑话、问题、荒诞解释、回声、随口事实、轻微实际落点或梦样淡出；
- 一致性来自叙述者声音和认知习惯，而不是每个细节都改变下一动作。

Layer 0 的最低输出契约：

- 写入一个真实的、有标题的、完整的 `draft.md`；
- 文章不得出现生成过程、checker、模型、语料或作者身份声明；
- 片段之间至少存在一种可感的声音、回声、反差、联想、时间或自我修正关系；
- 不凭空补高风险背景事实；
- 不输出素材库存、场景计划或指标表。

明确不再作为 standard 生成要求：

- `950-1150` 字、`45-70` 行、`6-8` 簇；
- side engine -> public hinge -> off-axis residue；
- carrier release、每个细节都要改变下一动作；
- prompt 必须晚出现；
- 婚礼/拒绝必须形成同晚后果链；
- practical tail 是唯一合法结尾；
- 每篇必须有陌生人、支付、粗粝身体暴露、群聊或旁逸场景。

### 4.2 Layer 1：Runtime Generation

`SKILL.md`、`clean-eval-first-draft-minimum.md`、`runtime-brief.md` 和 ordinary routing references 只保留：

1. artifact-backed 路由和 clean-eval marker 检查；
2. fragment slate source loop；
3. 背景事实边界；
4. prompt inventory、过程语言、二元解释和明显模型表面等普适风险；
5. wrapper 前后工具边界。

不得在 Layer 1 中把 controller 的长度、行形、connector、engine 或拒绝链诊断改写成“先写某个场景/必须有某类后果”。如果某个 prompt 自然形成社交拒绝片段，可以保留局部后果；它不是 standard 的结构前提。

### 4.3 Layer 2：Fact Gate

保持现有“事实边界”职责：在片段已经存在后检查具体事实，必要时降级或删除。Layer 2 不生成场景，不提供素材配额，不为 fragment slate 指定地名、游戏、工作或人物关系。

### 4.4 Layer 3：Repair Interface

finalized repair 的 `repair-brief.txt` 继续是唯一生成器接口：

- 一个 `source_focus`；
- 一个明确 scope（局部 cluster 或 controller 明确授权的 source-level rebuild）；
- 一个保持完整文章的 mass contract；
- 一个不把隐藏指标展开成清单的 shape contract；
- 第一次写入即为完整最终稿，随后停止。

hard-pass/profile-review 时，repair agent 不得为了追 profile 重新引入单场景因果链、固定行形、拒绝后果或 practical tail。若 profile 仍 review，保留 review 作为 controller 证据，不把未证实的“修复”包装成通过。

### 4.5 Layer 4：Controller Validation

controller 可以计算并报告：

- 字数/行数/标点/重复纹理分布；
- 是否过短、过长、明显 prose block 或 caption grid；
- 是否存在库存式 prompt 开头、显式跨日婚礼物流、标题闭环、过程污染；
- hard gate、style profile、trace、artifact hash 和协议状态。

判定原则：

- `段落发动机信号偏弱`、`高频词覆盖不足` 等无法覆盖所有原文的启发式只作为 warning/diagnostic，不得单独阻断标准稿；
- 明确的协议污染、未写回、二次写、checker/source 读取、空/非完整 artifact 仍可 hard fail；
- 社交拒绝过度生长只在证据显示跨日、多角色、多轮婚礼物流或工作剧情时触发；同晚的局部拒绝片段不得因“恭喜”等中性词被误判；
- controller 不能因为某个 warning 向生成器追加素材清单。

## 5. 文件级迁移

### 5.1 Active runtime

- `SKILL.md`：保留 artifact/protocol 路由，统一指向 `anlin-collage-source-model.md`。
- `references/clean-eval-first-draft-minimum.md`：重写为 fragment source minimum，删除旧 standard shape、拒绝链和 practical-tail 硬指令。
- `references/anlin-collage-source-model.md`：修正统计事实，补充“无固定目标但有完整性”的边界。
- `references/runtime-brief.md`、`references/anti-ai-slop.md`：删除或改写仍会作为 ordinary runtime guidance 的单场景因果模板；保留普适的 prompt inventory、事实边界和过程污染规则。
- `references/clean-generation-brief.md`：标为 controller/developer historical rationale，所有 active routing 文案改为新模型；不作为 bounded generator 输入。
- `references/standard-diary-source-engine.md`：保留为历史迁移参照，文件头明确 inactive；不得被 runtime、测试 fixture 或 trace 规则当作 active engine。
- `references/runtime-layer-map.md`、`references/route-coverage-matrix.md`：更新 ownership、文件路由和旧模型迁移记录。

### 5.2 Checker/controller

- `scripts/check_anlin_violations.py`：将 weak-engine/connector heuristics 与真正的 protocol/complete-artifact errors 分层；重写 social-decline time expansion 的词法边界，保留成对 true/false fixtures。
- `scripts/prepare_finalized_repair_brief.py`：source focus 文案不再要求 carrier release、同晚拒绝链或固定 standard corridor；保留 scope/mass/artifact contract。
- `scripts/clean_run_checker.py`：只在其 preflight 消息仍暴露旧 source model 时调整；不扩大 bounded checker 次数和 repair agent 读取面。
- `scripts/check_clean_eval_trace.py`：继续检查污染和旧 active reference 读取；历史 controller 文档的字符串不应误报为 runtime 读取。

### 5.3 Tests

新增或迁移测试必须验证行为而不是只搜一个词：

- active route reads the collage model and does not load the old engine;
- a corpus-like multi-fragment draft is not hard-failed for missing engine/connector;
- same-night refusal with neutral “恭喜” is not overgrowth;
- explicit next-day multi-role wedding logistics remains detectable;
- a true weak/invalid artifact still fails for the correct protocol reason;
- controller-only documents may mention historical rationale without becoming runtime dependencies。

旧测试中只为了保留旧 engine 文本而存在的断言应迁移到 inactive-history contract；不能通过保留矛盾 active 文案来让测试通过。

## 6. 数据流与停止边界

```text
marker + cwd check
        |
        v
clean-eval minimum + collage source model
        |
        v
one complete draft.md write
        |
        v
bounded wrapper / preflight output
        |
        +--> source/shape action from wrapper only --> immediate rerun
        |
        v
controller hard gate + style profile + trace evidence
        |
        +--> not pass: stop and classify root cause
        +--> pass candidate: only then consider finalized
```

bounded stop、finalized artifact-only、blind readiness 和 recognition rate 继续保持现有协议，不因 source model 重构而放宽。

## 7. 验证矩阵

每个小提交都必须有局部闭环；涉及 runtime/checker 的提交还必须完成全量闭环：

1. `git diff --check`；
2. `python -c "import pathlib, py_compile; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('scripts').glob('*.py')]; print('py_compile_ok')"`；
3. `python -m unittest discover -s test -p test_anlin_tooling.py`；
4. `python scripts/calibrate_style_profile.py <corpus-dir> --profile references/style-profile.json`；
5. 38 篇原文 normal/strict hard gate 无误伤；
6. runtime 文档扫描：无旧 3+1、`--rounds 3`、`placebo-rounds 1`、subagent-prompts、用户本地路径、私有 skill、模型特异化分支；
7. active reference trace scan：新模型路由存在，旧 engine 只在 inactive/history 允许出现；
8. fresh bounded controller case：只验证 process validity、source shape、hard gate、style profile 和 root-cause classification；不进入 finalized/blind。

## 8. C 方案后续边界

B 稳定后，C 方案单独设计多 profile 校准：

- 先按 corpus 事实建立短/中/长区间和阶段分层；
- 每个 profile 只提供 controller 比较区间，不回灌成固定生成配方；
- profile 选择必须基于用户指定体裁、案例元数据或已生成稿，不能靠模型名；
- 需要成对 placebo/false-accusation calibration，避免把 profile 差异误报成识别率。

C 的启动条件是 B 的 active runtime、checker 语义、测试锚点和 bounded source evidence 均稳定；在此之前不得以 C 的多 profile 复杂度掩盖 B 的接口矛盾。

## 9. 验收标准

本设计只有在以下条件同时满足时才算完成：

- active runtime 不再强制单场景因果链；
- 新统计事实经过脚本复算；
- 测试不再因旧 inactive 文件名称失败；
- checker 的弱启发式和真实协议错误分层可解释；
- fresh bounded 结果按证据分类，不包装成 quality pass；
- `ready for blind rounds` 仍为 false，recognition rate 仍为 `N/A`，直到独立证据包满足项目门槛。


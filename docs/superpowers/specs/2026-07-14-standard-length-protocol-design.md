# Standard Length / Checker / Blind Protocol 统一设计

日期：2026-07-14
状态：待用户审阅
范围：实施方案 B；方案 C 的 `matched-short-standard` 仅保留后续边界，本轮不实现

## 1. 背景

当前 standard 生成稿存在四套没有统一命名的长度语义：

- `scripts/check_anlin_violations.py` 以 650 为严重欠建边界、900 为 generated draft hard-gate 边界；
- `scripts/clean_run_checker.py` 以 900 做无条件 preflight 阻断，又以 950 与 `source_shape_weak` 组合做二次阻断；
- 部分 standard shape 检测只在正文达到 900 字后启用；
- `scripts/prepare_blind_test.py` 把正文少于 900 字或少于 40 行归为 `short_form`，完整文章默认长度容差为正负 65%。

这些边界使同一篇 850-899 字 standard 草稿在不同层得到互相矛盾的解释：validation protocol 允许其进入完整文章评估，但 checker/controller 先把它归为欠建；盲测又把它隐式归入 short form。结果是长度数字遮蔽了真正的 source、shape 或 profile 问题。

本设计只统一验证协议。它不改变已经批准的 fragment/collage source contract，也不把长度配额写回 runtime generation guidance。

## 2. 校准证据与限制

### 2.1 原文分布

style-profile 1.7 中有 34 篇 standard 原文。以正文汉字数计：

- 最短 269；
- 中位数 811；
- 90 分位约 1056.6；
- 8/34 少于 650；
- 20/34 少于 850；
- 21/34 少于 900；
- 13/34 达到或超过 900。

分期差异明显，但 Phase D 只有 3 篇，低于 style-profile 建立独立 stratum 所需的 4 篇。因此不能把后期较长原文概括成“该作者客观上必须写满 900 字”。本设计中的 850、900 是生成稿评估协议边界，不是作者身份或风格事实。

### 2.2 850-899 生成稿反事实

已找到 7 个 hash 唯一的 850-899 字生成 artifact。把 checker 的 full-article 入口在内存中改为 850 后：

- 5 个仍因独立的行形、标点、社交拒绝或协议边界错误失败；
- 890 字 artifact 的 hard gate 变为 clean，但 style-profile 仍为 `review`；
- 894 字 artifact 的 hard gate clean 且 style-profile checkpoint pass，但人工阅读确认它仍主要沿一个垃圾袋/婚礼消息场景连续推进，属于旧 source contract 暴露的 Layer 0/1 问题；其 bounded parent 也没有通过。

因此 850 不会把现有失败直接升级成 blind-ready candidate。它只会停止用“少几个字”覆盖真实根因。

### 2.3 Blind matching 校准

当前 complete-article 默认正负 65% 容差过宽：以 850 或 900 附近为目标时，34 篇 standard 原文中有 32 篇落入范围。`--match-genre` 在 exact-genre 记录足够时把长度差作为分数，而不是 eligibility hard filter。

以 blind preparation 使用的完整文章汉字数计，正负 25% 的候选数量足以支持当前语料中的 standard 匹配：

- target 650：13 篇；
- target 850：22 篇；
- target 894：22 篇；
- target 900：22 篇；
- target 1000：18 篇；
- target 1100：16 篇。

正文汉字数和 blind complete-article 汉字数是两个不同 denominator；实现和报告不得混用。

## 3. 目标与非目标

### 3.1 目标

1. 为 650、850、900、1350 建立单一、可命名、跨 checker/controller/blind 一致的语义。
2. 让 850-899 字 standard 草稿接受完整的 shape、hard-gate 和 style-profile 验证，而不是仅因长度被提前阻断。
3. 删除 950 与 advisory source heuristics 组合产生的隐式 hard gate。
4. 让 serious complete-article blind preparation 真正执行 exact-genre、hard length matching，并在样本不足时 fail closed。
5. 保留 900-1100 作为开发目标，但不让生成器追逐数字。

### 3.2 非目标

- 本轮不实现 650-849 的 `matched-short-standard` 放行路径。
- 不启动 iteration-166、finalized repair、blind、placebo 或 recognition-rate 评估，直到本设计实现、验证并提交。
- 不修改 fragment/collage source model，不恢复单场景因果链、carrier、public hinge 或固定 scene quota。
- 不校准或放宽 style-profile 阈值。
- 不新增模型、provider、私有 skill 或本地路径 runtime 分支。
- 不声称真实作者身份、来源或客观不可分辨。

## 4. 统一术语和常量

checker 应提供以下语义常量，并由 controller 导入，不在多个文件重复数字：

| 常量 | 值 | 语义 |
|---|---:|---|
| `STANDARD_DIARY_FORMAL_MIN_CHARS` | 650 | 严重欠建与可讨论完整稿之间的诊断边界；不是普通 full-standard pass boundary |
| `STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS` | 850 | ordinary full-standard generated-draft hard-gate 入口 |
| `STANDARD_DIARY_PREFERRED_TARGET_MIN_CHARS` | 900 | controller-only 推荐缓冲，不阻断、不作为 repair 配额 |
| `STANDARD_DIARY_DRAFT_OVERFULL_CHARS` | 1350 | 现有 generated-draft 过满边界 |

旧名 `STANDARD_DIARY_DRAFT_SAFE_MIN_CHARS` 在同一个实现提交中迁移为 `STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS`，并同步更新所有 active consumer 和测试；提交后的 active code 不保留兼容别名。

边界行为：

- `1-649`：普通检查为严重欠建 warning；generated `--strict --draft-gate` 为 blocking error，并走 whole-source rebuild 诊断。空正文由现有完整 artifact/protocol 错误单独处理。
- `650-849`：普通检查为 full-standard buffer warning；generated `--strict --draft-gate` 为 blocking error，并走 in-place source replacement / preserve-complete-article 诊断。
- `850-899`：不产生长度 hard error；进入所有适用 shape、surface、profile 和 trace 验证。controller 可以记录低于 preferred target，但不得把该记录传给 generator 或 repair agent。
- `900-1350`：普通 full-standard corridor。
- `>1350`：保留现有过满诊断和阻断语义。

## 5. Checker 设计

### 5.1 Length finding

`check_standard_diary_complete_length` 使用 `STANDARD_DIARY_FULL_ARTICLE_MIN_CHARS` 作为“篇幅缓冲不足”的上界。850 字及以上不得再出现 `标准日寄完整文章篇幅缓冲不足`。

900 只作为 controller state/report 中的布尔字段 `preferred_target_shortfall`，不创建 checker finding，不进入 `DRAFT_GATE_RULE_PREFIXES`，也不出现在 generator-facing 输出中。

### 5.2 Shape activation

当前因 `STANDARD_DIARY_DRAFT_SAFE_MIN_CHARS` 或硬编码 `>=900` 才激活的 standard full-article shape 检查，应逐项审计：

- 如果规则检测的是 full-article 行数、长行过密/不足、句号网格或散文块压缩，则入口统一为 850；
- 如果规则有独立的统计适用下限，应保留该规则自己的证据下限，不因统一长度协议而机械改写；
- 原文 strict calibration 必须证明这些规则不会把 38 篇原文变成 hard errors。

不得用“850 字以上必须满足固定行数/标点配额”替代人工和 profile 评估。shape detector 只阻断已经有独立可解释证据的异常表面。

### 5.3 Advisory 隔离

`段落发动机信号偏弱`、`高频词覆盖不足`、`粗粝自毁信号不足` 当前是 advisory diagnostics。它们不得通过 `source_shape_weak`、长度耦合或 generator-facing summary 间接恢复为 blocking。

实现上应分开两个集合：

- `blocking_shape_messages`：明确的长度、行形、标点、surface、social-decline 或协议错误；
- `source_advisories`：connector、legacy engine vocabulary、roughness 等不能覆盖全部原文的启发式。

删除 `body_chinese_chars < 950 with source_shape_weak` 这一合成 finding。900-949 的真实坏稿已经会由明确的 shape/surface finding 阻断；没有明确坏点的稿件不应因一个 undocumented 950 corridor 被拦住。

## 6. clean_run_checker 设计

### 6.1 First preflight

standard first preflight 的长度阻断改为 `<850`。850 字及以上继续检查：

- 行数过少或过多；
- medium short-line grid；
- period-row grid；
- prose-block compression；
- early comma / bare-line / short-line surface；
- social-decline 和其他明确 source-specific blockers；
- process leak、title、prompt inventory 等 surface blockers。

900-1100 推荐目标不得出现在 generator-facing 文本。raw controller state 可以记录正文长度和 preferred-target 状态。

### 6.2 Post-check preflight

checker call 1/2 后，`post_checker_blocking_messages` 使用与 first preflight 相同的 850 full-article boundary。850 字及以上只有明确 blocking message 才能阻止 call 2/2；source advisory 不得因为篇幅低于 950 而阻止 call 2/2。

### 6.3 Generator-facing routing

`generator_facing_summary`、`build_preflight_guidance` 和 post-check source note 使用以下互斥路由：

1. `<650`：severely underbuilt / whole-source rebuild；
2. `650-849`：below full-article boundary / replace one broken relation while preserving complete article；
3. `>=850` 且有明确 source blocker：source repair；
4. `>=850` 且只有明确 shape blocker：named shape action；
5. 只有 advisory：不得 preflight stop，应允许进入正式 checker call。

不得再用 `<950` 选择 underbuilt 文案。测试应验证 894 字的 length-only preflight 消失，875 字仍因独立 shape/source blocker 被拦住。

## 7. Finalized repair 与 checkpoint summary

`prepare_finalized_repair_brief.py` 和 `summarize_dev_checkpoints.py` 必须共享新语义：

- `<650` 才选择 severe rebuild；
- `650-849` 选择 underbuilt in-place replacement，并要求保持完整文章；
- `>=850` 不得仅因低于 900 选择 mass repair；
- hard-pass/profile-review 继续由 profile family 决定 repair mode，不能退回长度补写；
- bounded preflight fail、hard-gate fail、profile review、trace invalid 继续分开报告。

finalized repair agent 仍只能读取 `draft.md` 和 `repair-brief.txt`，exactly one complete write，然后停止。新长度协议不扩大 repair agent 的读取面、写回次数或 checker 权限。

## 8. Blind preparation 设计

### 8.1 Full-standard eligibility

serious complete-article impostor/placebo package 中，standard target 正文必须达到 850 字。650-849 standard artifact 在方案 B 下不得进入 formal full-article package；controller 应返回明确的 protocol eligibility failure，而不是自动把它降级成 short form。

`short_form` 只保留为匹配特征，不能决定 evaluation protocol。本轮保持字段名不变，把其正文长度分界从 `<900` 改为 `<850`；少于 40 行的独立形状条件保持不变。

### 8.2 Length matching

完整文章默认 `--length-tolerance` 从 0.65 收紧为 0.25。匹配顺序必须是：

1. 计算 hidden draft anchor 的 complete-article features；
2. 选择 exact target genre；
3. 过滤掉超出 hard length tolerance 的记录；
4. 在合格记录中按长度、行数和现有分数排序；
5. 从 nearest top-k 随机抽取，避免固定样本泄漏；
6. 合格记录不足时 fail closed，不从 tolerance 外或错误 genre 回填。

impostor 与 placebo 必须使用同一 hidden anchor、genre 和 hard tolerance。manifest 记录每个样本的：

- target/candidate complete-article chars；
- `length_delta_ratio`；
- `within_length_tolerance`；
- target/candidate genre；
- selection reason；
- tolerance 和 fail-closed policy。

保留 `--length-tolerance 0` 作为显式 diagnostic/legacy 禁用匹配模式，但其 manifest 必须记录 `formal_length_match_eligible=false`，不得用于 formal recognition-rate package。serious package 必须显式使用 `--match-genre auto` 或目标 genre；`--match-genre none` 同样记录 `formal_length_match_eligible=false`。

### 8.3 Claim boundary

即使 850-899 artifact 通过 hard gate 和 profile checkpoint，也必须同时满足 bounded/finalized/trace/corpus/overlap/blind/placebo 门槛才能进入识别率证据包。长度 eligibility 不是质量成功、作者身份或不可分辨证据。

## 9. 数据流

```text
realistic prompt + active skill
        |
        v
one complete fragment/collage draft
        |
        v
clean_run_checker preflight
        |
        +--> <650: severe source rebuild route
        +--> 650-849: full-standard underbuilt route
        +--> >=850 + explicit blocker: bounded source/shape action
        +--> >=850 + advisory only: consume checker call
        |
        v
strict hard gate + style profile + trace
        |
        +--> fail/review/invalid: stop and classify
        +--> bounded pass candidate: consider finalized
        |
        v
finalized pass candidate
        |
        v
strict exact-genre +/-25% blind preparation
        |
        +--> insufficient candidates: protocol failure
        +--> sufficient: impostor + placebo package
```

## 10. TDD 与验证矩阵

### 10.1 Boundary RED tests

使用 649、650、849、850、899、900 六个正文边界分别验证：

- checker ordinary length warning、generated draft-gate error 以及 850+ 无长度 finding 的预期分界；
- first preflight blocking；
- post-check preflight blocking；
- generator-facing route；
- finalized repair route；
- summary classification；
- full-standard blind eligibility。

### 10.2 Real artifact regression

至少固定以下真实 artifact 行为：

- 875：移除 length-only blocker 后，仍因独立 shape/source errors 失败；
- 890：850 counterfactual hard gate clean，但 style-profile 保持 `review`；
- 894：850 counterfactual hard gate clean、profile checkpoint pass，但测试和文档不得把它标为 bounded/finalized/blind success；
- 900-949 现有失败稿：删除 `<950 with source_shape_weak` 后，真实 shape/surface blocker 仍存在；
- 一个 900-949 advisory-only fixture：不得被 preflight 阻断。

真实 eval artifact 不复制进 runtime skill。测试使用最小匿名 fixture 或在 developer-only test 中构造等价特征。

### 10.3 Blind matching tests

- exact genre + within 25% 才 eligible；
- exact genre 足够但部分超 tolerance 时，超界记录不能被选中；
- exact genre/tolerance 内记录不足时 fail closed；
- placebo 与 impostor manifest 使用同一 hidden anchor；
- `--length-tolerance 0` 明确标为 diagnostic，不能产生 formal-ready manifest；
- complete-article chars 与 body chars 字段分离。

### 10.4 Full verification

涉及 runtime/checker 的实现提交必须完成：

1. `git diff --check`；
2. 所有 `scripts/*.py` 的 `py_compile`；
3. `python -m unittest discover -s test -p test_anlin_tooling.py`；
4. 38 篇原文 style-profile calibration；
5. 38 篇原文 normal 与 strict hard gate，hard-error files 和 nonzero files 均为空；
6. active protocol legacy scan；
7. runtime 本地路径、私有 skill、模型/provider 分支扫描；
8. checker/controller 边界测试和 blind matching 定向测试；
9. fresh iteration-166 bounded controller run，仅在代码提交后启动。

## 11. 实施切片

实施计划应拆成可独立验证的小提交：

1. 先用 RED tests 固定语义常量与 649/650/849/850/899/900 边界；
2. 统一 checker length/shape boundary；
3. 解耦 clean-run advisory 与 blocking，删除 950 合成路由；
4. 同步 finalized brief 和 checkpoint summary；
5. 收紧 blind exact-genre hard matching 与 manifest；
6. 更新 validation protocol、runtime layer map、README/development log 中的开发事实；
7. 完成全量验证、独立复核、提交并推送；
8. 创建 fresh iteration-166 验证新 bounded 行为。

每个切片只修正当前契约依赖，不顺手增加新的 source quota 或 checker family。

## 12. 方案 C 的后续边界

方案 B 稳定后，另行设计 `matched-short-standard`：

- 协议必须在生成前由 case metadata/controller 锁定，不能看到草稿太短后自动降级；
- 只允许 650-849 standard artifact；
- 必须有足够 exact-genre、严格长度匹配的 original pool；
- bounded、finalized、blind 和 placebo manifest 都记录协议名；
- 结果只支持 matched-short 条件下的报告，不能支持 formal full-article claim；
- 不把 short/medium/long profile 变成 runtime 生成配方。

方案 C 不得在方案 B 尚未通过 fresh bounded 验证时提前实现。

## 13. 验收标准

方案 B 只有在以下条件同时满足时才算工程完成：

- checker、clean-run、finalized summary 和 blind preparation 对 650/850/900 使用同一语义；
- active code 不再存在 `<950 with source_shape_weak` 合成阻断；
- 850-899 可以进入完整 shape/profile 验证，但不会自动成为 quality candidate；
- advisory source heuristics 不再间接阻断 checker call；
- serious blind matching 是 exact-genre、正负 25% hard filter、样本不足 fail closed；
- 38 篇原文 calibration、normal/strict hard gate 和 runtime scans 全部通过；
- fresh iteration-166 有完整 controller/trace/artifact 证据，并按真实结果分类；
- 未完成 valid `8 impostor + 2 placebo` package 前，`ready for blind rounds=false`、recognition rate=`N/A`；
- 不作作者身份、来源或客观不可分辨声明。

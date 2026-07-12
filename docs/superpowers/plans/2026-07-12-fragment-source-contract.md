# Fragment Source Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 将 anlin-writing 的 standard 生成接口从单场景因果链迁移到可验证的 fragment slate，并让 controller/checker、finalized repair 和测试锚点与该分层契约一致。

**Architecture:** Layer 0/1 负责最小 source guidance：完整 artifact、片段类型、非因果连接、声音一致性和事实边界；不再规定统一字数、行数、簇数或婚礼拒绝后果。Layer 4 继续测量长度、行形、重复纹理和明确的协议/剧情风险，但弱启发式只作 warning。finalized repair 继续使用单一 source focus、一次写回和 artifact-only 边界。C 的短/中/长及阶段 profile 只记录为后续扩展，不在本计划实现。

**Tech Stack:** Markdown runtime skill/reference files, Python 3 checker/controller scripts, unittest, PowerShell verification commands, git main branch.

---

## 初始约束

- 当前 main 已包含设计文档提交 1b9bac1，但工作区仍有 OpenCode 相关 dirty 改动；不得 reset、checkout 或覆盖这些改动。
- 每次开始任务先运行：

~~~powershell
git status --short --branch
git log -5 --oneline --decorate
~~~

- 只提交本计划涉及的文件；每个形成验证闭环的任务单独提交。
- 不在本计划中执行 finalized、blind、impostor、placebo，也不报告 recognition rate。

## 文件责任表

| 文件 | 本计划责任 |
|---|---|
| SKILL.md | active routing、artifact/protocol 边界、source model 入口 |
| references/clean-eval-first-draft-minimum.md | bounded first-draft 最小 source contract |
| references/anlin-collage-source-model.md | fragment 类型、连接和已复算 corpus 事实 |
| references/runtime-brief.md、references/anti-ai-slop.md | ordinary runtime 的普适风险，删除单场景生成模板 |
| references/clean-generation-brief.md | controller/developer historical rationale，不再暗示旧 active engine |
| references/standard-diary-source-engine.md | inactive 历史参照，明确不被 runtime 加载 |
| references/runtime-layer-map.md、references/route-coverage-matrix.md | 文档 ownership 与 active/inactive 路由矩阵 |
| scripts/check_anlin_violations.py | weak heuristic 与真实 hard gate 分层；社交拒绝扩张边界 |
| scripts/clean_run_checker.py | bounded preflight 文案和 source action 不再要求 carrier/统一 corridor |
| scripts/prepare_finalized_repair_brief.py | finalized source focus 不再回灌 carrier/拒绝链模板 |
| scripts/check_clean_eval_trace.py | 只阻断 runtime 读取旧 active reference，不误报 controller 历史文本 |
| test/test_anlin_tooling.py | 先写 RED 行为测试，再迁移旧字符串锚点 |

### Task 1: 建立 B 方案的 RED 行为测试

**Files:**
- Modify: test/test_anlin_tooling.py
- Read: SKILL.md、clean-eval-first-draft-minimum.md、anlin-collage-source-model.md、clean-generation-brief.md、standard-diary-source-engine.md

- [ ] **Step 1: 写 active routing 失败测试**

新增一个测试读取 SKILL.md、clean-eval-first-draft-minimum.md、runtime-brief.md、anti-ai-slop.md，断言：

~~~python
self.assertIn("references/anlin-collage-source-model.md", skill)
self.assertNotIn("load references/standard-diary-source-engine.md", skill)
self.assertNotIn("side engine -> public hinge -> off-axis residue", first_draft)
self.assertNotIn("950-1150", first_draft)
self.assertIn("fragment slate", first_draft)
~~~

另断言旧 engine 文件仍存在且标记为 inactive/history，不能通过删除历史文件伪装迁移完成。

- [ ] **Step 2: 写 corpus 事实测试**

从 corpus 目录读取 38 个 Markdown 原文，计算正文汉字数和非空正文行数，断言 count=38、min_chars=235、max_chars=1932、min_lines=17、max_lines=91；断言新 collage 文档包含这些观察范围，但不把它们写成目标 corridor。

- [ ] **Step 3: 写 checker 成对测试**

保留并收紧三组真实行为：

1. 多片段跳接稿不因缺少 engine/connector 被 hard error；
2. 同晚拒绝中出现中性词“恭喜”不触发 社交拒绝后果过度生长；
3. 明确包含“第二天/班群/合照/伴郎”等跨日、多角色婚礼剧情仍触发该规则。

fixture 必须使用完整但不靠重复 filler 的片段，每个片段至少有动作、记忆、对话、笑话或自我修正之一。

- [ ] **Step 4: 只运行新增测试确认 RED**

~~~powershell
python -m unittest discover -s test -p test_anlin_tooling.py -k test_active_runtime_uses_fragment_source_contract
python -m unittest discover -s test -p test_anlin_tooling.py -k test_corpus_observed_range_matches_source_model
python -m unittest discover -s test -p test_anlin_tooling.py -k test_fragment_and_social_decline_checker_pairs
~~~

预期至少一个测试因当前旧 active 文案、错误统计事实或 checker 语义失败，而不是 import/fixture 错误。若全通过，先检查是否误测 inactive 文件。

- [ ] **Step 5: 提交 RED 测试**

~~~powershell
git add test/test_anlin_tooling.py
git commit -m "test: define fragment source contract regressions"
~~~

### Task 2: 迁移 Layer 0/1 active source guidance

**Files:**
- Modify: SKILL.md
- Modify: references/clean-eval-first-draft-minimum.md
- Modify: references/anlin-collage-source-model.md
- Modify: references/runtime-brief.md
- Modify: references/anti-ai-slop.md

- [ ] **Step 1: 修正 collage model 事实和边界**

将统计修正为 235-1932 汉字、17-91 行，并明确这是观察范围而非生成目标。保留 fragment 类型、连接方式、prompt 触发点、ending 选择和声音一致性；加入完整 artifact 最低契约，但不加入固定 fragment 数、跳转次数或“必须散”的 hard gate。

- [ ] **Step 2: 重写 clean-eval minimum source section**

删除 950-1150、45-70、6-8、side engine/public hinge/off-axis residue、carrier release、拒绝必须同晚后果链、practical tail 唯一结尾等 active 命令。保留 marker/cwd/tool order、真实 draft.md、过程隔离、fragment slate、声音一致性、事实边界和 wrapper stop boundary。

最低契约固定为：

~~~text
title + complete body + one real draft.md write
fragment relation: association | contrast | echo | time jump | self-correction | direct jump
no process/checker/model/corpus/authorship language in article
background facts are optional contradiction boundaries
~~~

- [ ] **Step 3: 改写 ordinary runtime 文案**

在 runtime-brief.md 和 anti-ai-slop.md 中保留 prompt inventory、标题闭环、事实边界、过程污染、模型表面等普适风险；把“先找 side engine、再 public hinge、再换 carrier”改成“选择一个或多个片段，以声音/回声/反差/联想保持可感一致性”。社交拒绝规则只保留“若文章自行扩展为明确跨日剧情可诊断”，不再要求每个邀请 prompt 都完成拒绝后果链。

- [ ] **Step 4: 运行 Task 1 active/source 测试确认 GREEN**

~~~powershell
python -m unittest discover -s test -p test_anlin_tooling.py -k test_active_runtime_uses_fragment_source_contract
python -m unittest discover -s test -p test_anlin_tooling.py -k test_corpus_observed_range_matches_source_model
~~~

预期 PASS；checker pair 测试可暂留 RED，留给 Task 3。

- [ ] **Step 5: 提交 Layer 0/1 迁移**

~~~powershell
git add SKILL.md references/clean-eval-first-draft-minimum.md references/anlin-collage-source-model.md references/runtime-brief.md references/anti-ai-slop.md
git commit -m "refactor: route standard generation through fragment slate"
~~~

### Task 3: 分层 checker 与 bounded preflight 诊断

**Files:**
- Modify: scripts/check_anlin_violations.py
- Modify: scripts/clean_run_checker.py
- Test: test/test_anlin_tooling.py

- [ ] **Step 1: 先让 checker 语义测试 RED**

对 findings 断言弱启发式 severity 为 warning：

~~~python
weak_rules = {"段落发动机信号偏弱", "高频词覆盖不足"}
for finding in findings:
    if finding["rule"] in weak_rules:
        self.assertEqual(finding["severity"], "warning")
~~~

同时要求同晚 fixture 不出现 overgrowth，跨日 fixture 仍出现 overgrowth；测试检查原始 rule/severity，而不仅检查进程返回码。

- [ ] **Step 2: 最小修复弱启发式分层**

保留弱启发式 finding 内容和 controller 报告，但确保它们不在 DRAFT_GATE_RULE_PREFIXES 的 hard-error promotion 集合中。不得删除检测函数，也不得用 filler 让指标消失。

- [ ] **Step 3: 修复社交拒绝词法边界**

SOCIAL_DECLINE_REFUSAL_TERMS 只包含拒绝语义；“恭喜”不能成为 refusal index。SOCIAL_DECLINE_TIME_EXPANSION_TERMS 必须与婚礼/拒绝上下文和至少一个跨日、新增角色或婚礼物流证据共同成立，不能仅因同晚“中午/下午/下楼”触发。

- [ ] **Step 4: 重写 preflight source guidance**

clean_run_checker.py 可报告 shape/quality，但 generator-facing action 不得输出 carrier release、统一 standard mass corridor、同晚拒绝链或“添加一个后果场景”。fragment source action 只说明：替换当前稿中最早失效的片段/连接，保持完整文章，不为指标添加新素材。纯 shape finding 仍只执行 named rhythm action。

- [ ] **Step 5: 运行 checker RED→GREEN**

~~~powershell
python -m unittest discover -s test -p test_anlin_tooling.py -k test_fragment_and_social_decline_checker_pairs
python -m unittest discover -s test -p test_anlin_tooling.py -k test_checker_draft_gate_promotes_comma_rhythm_in_sparse_draft
~~~

预期 PASS；已有 true-positive social/shape tests 不能被删除。

- [ ] **Step 6: 提交 checker/preflight 分层**

~~~powershell
git add scripts/check_anlin_violations.py scripts/clean_run_checker.py test/test_anlin_tooling.py
git commit -m "fix: separate fragment diagnostics from hard gates"
~~~

### Task 4: 迁移 finalized repair 与 controller 文档边界

**Files:**
- Modify: scripts/prepare_finalized_repair_brief.py
- Modify: references/clean-generation-brief.md
- Modify: references/standard-diary-source-engine.md
- Modify: references/runtime-layer-map.md
- Modify: references/route-coverage-matrix.md
- Modify: scripts/check_clean_eval_trace.py
- Test: test/test_anlin_tooling.py

- [ ] **Step 1: 写 finalized source-focus RED 测试**

准备 hard-gate failure、hard-pass/profile-review、明确 underbuilt 三个输入。断言 brief 的 source_focus 不包含 carrier release、固定 950-1150、同晚拒绝链或 append proof scene；仍包含 scope、mass preservation、一次完整写回和 artifact-only 边界。

- [ ] **Step 2: 最小迁移 brief 文案**

保留 source_rewrite_compact、hard_pass_review_in_place、mass_floor_lock、line_ending_lock、一次写回规则；将 source action 改为替换最早失效的片段/连接，保持现有可用质量，不按隐藏指标逐条补素材。hard-pass review 不得因 profile review 重建旧 scene engine。

- [ ] **Step 3: 标记旧 engine 为 inactive**

在 standard-diary-source-engine.md 顶部增加迁移说明：仅供历史故障解释和差异审计，不能作为 clean-eval 或 ordinary runtime 输入。clean-generation-brief.md 和 runtime-layer-map.md 的 active route 改为 collage model；历史段落可以保留，但必须标明 controller/developer-only。

- [ ] **Step 4: 修复 trace 边界和旧测试锚点**

trace checker 只把实际 runtime 读取旧 active engine 判为污染；controller 文档内出现旧文件名不应单独报错。更新 test_formal_first_draft_uses_source_loop_not_long_repair_files 等旧断言，使其验证 active/inactive ownership，而不是强制旧文件继续承担 active 内容。

- [ ] **Step 5: 运行 finalized/controller 定向测试**

~~~powershell
python -m unittest discover -s test -p test_anlin_tooling.py -k test_bounded_repair_uses_wrapper_output_without_long_reference_reload
python -m unittest discover -s test -p test_anlin_tooling.py -k test_formal_first_draft_uses_source_loop_not_long_repair_files
python -m unittest discover -s test -p test_anlin_tooling.py -k test_source_contract_uses_fragment_slate_not_carrier_engine
~~~

预期 PASS，且不能通过重新加入旧 active 文案满足断言。

- [ ] **Step 6: 提交 finalized/controller 迁移**

~~~powershell
git add scripts/prepare_finalized_repair_brief.py references/clean-generation-brief.md references/standard-diary-source-engine.md references/runtime-layer-map.md references/route-coverage-matrix.md scripts/check_clean_eval_trace.py test/test_anlin_tooling.py
git commit -m "refactor: keep finalized repair independent from source engine"
~~~

### Task 5: 全量验证与独立文档审计

**Files:** 只读验证整个仓库、scripts、references 和语料目录；只有 B 范围内失败才修改。

- [ ] **Step 1: 运行基础验证**

~~~powershell
git diff --check
python -c "import pathlib, py_compile; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('scripts').glob('*.py')]; print('py_compile_ok')"
python -m unittest discover -s test -p test_anlin_tooling.py
~~~

预期 py_compile_ok、全套件 0 failure；skip 数量只能与基线或明确测试环境原因一致。

- [ ] **Step 2: 运行原文与 profile 验证**

~~~powershell
python scripts/calibrate_style_profile.py "C:\Users\34025\Desktop\Anlin" --profile references/style-profile.json
~~~

随后运行项目既有 normal/strict 原文 hard gate 命令，记录 strict_corpus_hard_error_files=[]；normal strict 误伤检查必须区分原文 baseline 与 generated-draft diagnostic。

- [ ] **Step 3: 扫描 runtime portability**

扫描 SKILL.md 与普通 runtime references，确认没有本地路径、私有 skill 依赖、模型/provider 特异分支，以及旧 3+1、--rounds 3、placebo-rounds 1、subagent-prompts 残留。README、development-log、测试可以保留开发事实和模型记录。

- [ ] **Step 4: 审查 active/inactive 文档边界**

用 rg 检查所有 standard-diary-source-engine.md 引用，逐项标记 active、controller-only 或 history；active runtime 只能路由 anlin-collage-source-model.md。检查新统计事实与 38 篇复算值一致。

- [ ] **Step 5: 仅提交 B 范围遗漏修复**

如果验证发现 B 范围内直接缺陷，先追加对应 RED 测试，再修复并单独提交；不得为了全绿删掉 true-positive 测试、放宽 artifact 协议或引入 C profile。

### Task 6: Fresh bounded source-evidence retest

**Files:** 外部 evaluation workspace 的 fresh iteration-154 case；不修改 source，除非该轮暴露可复现的 B 范围缺陷。

- [ ] **Step 1: 创建 fresh controller case**

使用不复用旧 case 的 controller wrapper，在新的 external evaluation workspace 创建 iteration-154。provider/model 只记录在 case metadata，不写入 runtime skill。

- [ ] **Step 2: 运行一次 bounded generation**

验证 controller-run.json、opencode-output.jsonl、stderr、state、first_submission、bounded_final、hash stability、stop reason、calls/preflights、trace contamination。禁止直接调用 opencode 代替 wrapper。

- [ ] **Step 3: 分析 source evidence**

记录 fragment diversity、跳接关系、声音一致性、prompt 是否被当素材清单、hard gate、style profile 和 trace。失败必须分类为 source guidance、repair interface、checker 或协议问题，不包装为 quality pass。

- [ ] **Step 4: 明确停止边界**

任务结束时仍满足 finalized_started=false、blind_rounds_started=false、ready_for_blind_rounds=false、recognition_rate=N/A。bounded source evidence 稳定后另行制定 finalized/证据包计划。

## 计划自检

- 设计文档 Layer 0/1/3/4 分别由 Task 2、Task 3、Task 4 覆盖。
- 设计文档的 active runtime、checker、finalized、trace 和 tests 均有文件责任与任务。
- 验证矩阵由 Task 5 覆盖；Task 6 明确不进入 blind/finalized。
- C 只出现在目标、边界和启动条件中，没有实现步骤或模型特异化分支。
- 测试名、路径和命令与当前仓库结构一致；若新增测试名，必须在 Task 1 先创建并看到 RED。

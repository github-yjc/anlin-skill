# Evaluation Prompts

这些 prompts 用于测试 skill 是否能处理不同日期、体裁和验证模式。它们不是证明“完全拟合”的测试，只是压力场景。

Status: legacy supplementary notes. The formal 15-case evaluation set lives in `evals/evals.json`, and the current protocol lives in `evals/README.md` plus `references/validation-protocol.md`. Preserve this file because it records early scenario intent and assertions, but do not use it as the sole source for current clean-eval, finalized repair, or blind-round claims. If a line below conflicts with newer protocol, treat the newer protocol as active and preserve the older line only as historical evidence.

When this file conflicts with `evals/evals.json` or `references/validation-protocol.md`, use the newer structured files and record the discrepancy in the development log instead of silently deleting the older note.

## Eval 1: 2022 春招失败标准日寄

Prompt: `模拟 Anlin 在 2022-04-18 晚上写一篇标准日寄。背景：春招失败，舍友拿到大厂 offer，自己刷招聘软件和王者荣耀。`

Expected:
- 高置信度时代区。
- 标准日寄结构，场景数因阶段而异（5-10）。
- 春招/同龄人对比/游戏/招聘软件进入个人体验。
- 不写成求职建议或失败复盘。

## Eval 2: 2023 后疫情低频回声

Prompt: `模拟 Anlin 在 2023-02-26 下午写一篇日寄。背景：身边人都开始上班，自己还在家里，刷到 ChatGPT 相关内容但不想写科技评论。`

Expected:
- 中置信度时代区。
- ChatGPT 只是手机里刷到的东西，不成为中心科普。
- 语气比 2022 稍沉，仍有自嘲和嘴硬。

## Eval 3: 2025 长期失业后期自知

Prompt: `模拟 Anlin 在 2025-10-17 深夜写一篇偏真诚的日寄。背景：长期失业，银行卡余额下降，脚踝痛，朋友发来一张 AI 图片。`

Expected:
- 低置信度时代区，需谨慎。
- AI 作为时代纹理，不堆技术名词。
- 自欺-破灭结构可用。
- 真诚不能泛滥，结尾身体化。

## Eval 4: 可验证投影区

Prompt: `模拟 Anlin 在一个最新原文之后、但可以通过搜索验证背景的真实日期写一篇日寄。背景只给：他在五线小城独居，看到一个新的社交软件热梗。`

Expected:
- 明确这是最新原文之后的可验证投影区，需要搜索或用户补充具体梗。
- 不把无法验证的日期/梗/事件写成真实发生。
- 若无法验证，应要求补充背景或降级写作。

## Eval 5: 真诚文

Prompt: `模拟 Anlin 写一篇类似“不想祝我妈母亲节快乐”的真诚文，但时间是 2024-05-12。`

Expected:
- 真诚文降低笑点密度。
- 不鸡汤，不祝福模板化。
- 与母亲关系的愧疚具体、身体化、少解释。

## Suggested Assertions

- 正式盲评生成入口：使用 `evals/evals.json` 的 `realistic_prompt`，不要使用包含结构提示的诊断 `prompt` 来声明 skill 单独能力。
- 无评论链：不得出现“有人说A又有人说B”。
- 无宏观新闻摘要：不得连续三句讲时代背景而无个人动作。
- 场景数：因阶段而异（Phase A 5-8，Phase D 7-12，通常 5-10）；真诚文/短真诚文 4-7。
- 严肃盲评长度：所有测试稿必须是含标题的完整文章；标题由生成 agent 产出，第一行使用纯标题或 Markdown H1，不加粗、不写“标题：”、不夹带方法说明。标准日寄生成稿正文通常应在 900-1100 字，至少清过 850 字安全缓冲。盲评保留并规范化标题，用完整文章字数匹配原文。短体裁要用短原文匹配，不得和全长标准日寄混评。
- 日期适切：目标日期后出现的事件不得写入早期日期。
- 高频词：其实/觉得/发现/好像/不过/突然/于是/因为/所以 至少自然出现 5 个。
- 结尾：不总结、不升华、不提出建议。

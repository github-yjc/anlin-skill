# Title Model

Use this file when choosing or reviewing a generated article title. Do not load it before the first draft in clean-eval mode unless the title itself is the known failure.

The title is part of the article, not controller metadata. Blind review keeps titles, so title fit matters.

## Corpus Evidence

In the 38-article corpus:

- 11 titles are exactly `日寄`.
- 24 titles end with `日寄`, including exact `日寄`.
- 13 titles are sentence, question, meme, or literary-phrase titles rather than `X日寄`.
- title length ranges from very short labels to long sentence titles.

This means `日寄` is a real title pattern, but it is not a safe universal default. A generated draft that always chooses `日寄` becomes too conservative and loses title-level voice; a generated draft that always chooses `X日寄` often leaks the user prompt.

## Title Families

Use one of these families after the body has a lived shape:

- **Bare diary label**: `日寄`. Works when the body already carries enough local color or when a stronger title would reveal the assignment.
- **Defensive `X日寄` handle**: a low-status, bodily, work, social, or side-object handle plus `日寄`. The modifier should sound like a first defensive move, not a topic label.
- **`X寄` or variant label**: a shorter damaged handle when the body is rougher or more colloquial. Use sparingly.
- **Question title**: a small puzzled line, not a rhetorical essay question.
- **Meme/platform title**: only when the body actually contains a platform or language surface that earns it.
- **Sentence or literary-phrase title**: more plausible for sincere, micro-hope, surreal, or later reflective pieces. It must not summarize the final lesson.

## Selection Rule

Choose the title after drafting:

1. Name the actual side handle in the body: object, bodily problem, social wound, phrase, route, screen surface, or mood leak.
2. Check whether the title alone exposes the user prompt. If yes, weaken or displace it.
3. Check whether the title is too safe. If the body is ordinary and the title is always `日寄`, consider a corpus-like modifier, question, or sentence title.
4. Check whether the title and ending form a clean contract. If they mirror each other, weaken one of them.
5. Keep the title plain: no `标题：`, no bold wrapper, no controller note.

## High-Risk Generated Titles

- task labels: `春招日寄`, `情人节日寄`, `痛风日寄`, `母亲节日寄` when the user prompt already contains that exact topic and the body merely executes it
- person-plus-event labels: `狗哥的婚礼`, `同学的婚礼`, `婚礼`, `结婚`, or similar titles for invitation/refusal prompts when the body is about whether to go, how much to give, or what excuse to send
- calendar labels: `2024日寄`, `新年日寄`, `元旦日寄`, `跨年日寄`, `年度总结日寄` when the date or feed topic is the assignment rather than a lived side handle
- tidy thesis titles: `不算坏事`, `没发出去的消息`, `给不存在的人写信`
- short sincere main-prop loops: `鸡蛋`, `一袋鸡蛋`, `塑料袋`, `屏幕`, or `没发出去的消息` when the same prop opens the body, proves mother/family memory, and returns in the ending
- clever titles that require the ending to explain them
- title/first-five-lines/ending all pointing to the same prompt noun

High-risk does not mean forbidden. Some corpus titles directly name spring recruitment or delivery work. The difference is function: an original title can be an immediate wound or joke; a generated title often becomes a diagnostic tag for the assignment. If using a prompt-adjacent `X日寄`, make the opening and ending less diagnostic and let the body contain off-axis residue.

## Repair Moves

- If title is too diagnostic: replace with a side object, bodily handle, question, or plain `日寄`.
- If an invitation/refusal title names the person plus event: retitle from the failed side action, wrong reply, route/payment hesitation, low-status object, or body residue created by the refusal.
- If title is too bland: choose a modifier from a real body consequence, not from the prompt.
- If title is too literary: remove the abstract feeling and use the object/action that caused it.
- If title and ending close too neatly: keep the stronger one and lower the other into a practical consequence.
- If a short sincere title is the main prompt prop: retitle from the present failure, such as a sleeve, door, wrong reply, sink, bowl, slipper, or low-status object; if the old prop remains, stop using it as the ending proof.

# refusal to answer example

## Input

### user_input
I do not want to discuss budget now. Please continue with user workflow first.

## Expected handling

1. Do not force the declined topic unless it blocks interview completion.
2. Mark budget-related slot as deferred or open question with reason.
3. Continue with requested topic (`user workflow and scenarios`).

## Good next utterance pattern

```text
明白，预算先暂缓。我先聚焦用户流程：首批用户从打开产品到完成一次核心任务，完整步骤是什么？
```

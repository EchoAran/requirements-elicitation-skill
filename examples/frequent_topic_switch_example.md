# frequent topic switch example

## Input

### conversation snippet
- user turn 1: "先聊功能，我要聊天和推荐。"
- user turn 2: "先别聊功能，预算更关键。"
- user turn 3: "算了预算先放着，先说合规。"

## Expected handling

1. Respect explicit user steering each turn.
2. Ask one dependency bridge mini-question when prerequisite is missing.
3. Keep one primary question only, do not ask mixed-topic bundles.
4. Update `current_topic_id` with each explicit shift, but preserve unresolved high-impact open questions.

## Good next utterance pattern

```text
收到，你想先确认合规边界。为了避免后面返工，先确认一个前置点：这个产品是否会处理任何受监管的个人敏感数据？
```

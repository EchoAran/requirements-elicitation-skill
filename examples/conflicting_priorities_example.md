# conflicting priorities example

## Input

### user_input
For V1, reliability is the top priority.  
Also for V1, we can accept occasional downtime if delivery is faster.

## Expected handling

1. Detect contradiction in priorities and mark affected slot `conflicted`.
2. Set slot `contradiction_severity` to `high` (release quality bar conflict).
3. Add one contradiction item to `contradictions`.
4. Ask exactly one disambiguation question before opening new topics.

## Good next utterance pattern

```text
你给了两个相反优先级：V1 既要求高可靠，又可接受偶发宕机换速度。请确认第一版以哪一个为主？
```

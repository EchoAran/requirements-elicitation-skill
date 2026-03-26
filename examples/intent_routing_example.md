# intent routing example

## Input

### user_input
Maybe we should support online payment later, but for first release we need iOS only.

## Output

```json
{
  "intent_classification": [
    {
      "segment": "Maybe we should support online payment later",
      "intent": "exploratory idea",
      "action": "store as supported inference and ask confirmation"
    },
    {
      "segment": "for first release we need iOS only",
      "intent": "explicit requirement",
      "action": "fill constraints slot as confirmed"
    }
  ]
}
```

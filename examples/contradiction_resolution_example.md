# contradiction resolution example

## Input

### current_framework
```json
{
  "phase": "runtime",
  "current_topic_id": "constraints_boundaries",
  "topics": [
    {
      "id": "constraints_boundaries",
      "label": "constraints and boundaries",
      "priority": "high",
      "status": "partially_filled",
      "slots": [
        {
          "name": "payment assumptions",
          "value": "No in app payment for first release",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_5",
          "last_updated": "turn_5"
        }
      ]
    }
  ],
  "open_questions": []
}
```

### new_user_input
We must include in app payment in the first release.

## Output

```json
{
  "updated_slot": {
    "name": "payment assumptions",
    "status": "conflicted",
    "evidence": "turn_5 vs turn_8"
  },
  "open_questions": [
    "[CONTRADICTION] No in app payment for first release vs must include in app payment in first release. Which one is authoritative?"
  ],
  "next_turn_priority": "clarify_contradiction"
}
```

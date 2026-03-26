# generate speak example

## Input

### current_framework
```json
{
  "phase": "runtime",
  "current_topic_id": "target_users_stakeholders",
  "topics": [
    {
      "id": "target_users_stakeholders",
      "label": "target users and stakeholders",
      "priority": "high",
      "status": "active",
      "notes": [],
      "slots": [
        {
          "name": "primary users",
          "value": "Students",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "previous interview turns",
          "last_updated": "turn_2"
        },
        {
          "name": "secondary stakeholders",
          "value": "Parents may want visibility",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "parents may also want visibility",
          "last_updated": "turn_6"
        },
        {
          "name": "decision making stakeholder",
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_6"
        }
      ]
    }
  ],
  "open_questions": [
    "Who decides which stakeholder needs drive first release priorities?"
  ]
}
```

### selected_topic

```json
{
  "selected_topic_id": "target_users_stakeholders",
  "selected_topic_label": "target users and stakeholders",
  "selection_reason": "Stakeholder power affects scope and permissions.",
  "next_focus_slot": "decision making stakeholder"
}
```

## Output

Understood. For the first release, who should decide what gets built and prioritized: students, parents, or the school?
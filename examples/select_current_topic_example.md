# select current topic example

## Input

### current_framework
```json
{
  "phase": "runtime",
  "current_topic_id": "functional_capabilities",
  "topics": [
    {
      "id": "functional_capabilities",
      "label": "functional capabilities",
      "priority": "high",
      "status": "active",
      "notes": [],
      "slots": [
        {
          "name": "must have features",
          "value": ["item listing", "search", "chat"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "previous interview turns",
          "last_updated": "turn_5"
        },
        {
          "name": "permissions model",
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_5"
        }
      ]
    },
    {
      "id": "target_users_stakeholders",
      "label": "target users and stakeholders",
      "priority": "high",
      "status": "partially_filled",
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
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_2"
        }
      ]
    }
  ],
  "open_questions": []
}
```

### new_user_input

Actually the bigger issue is that parents may also want visibility, but students should remain the main users.

## Output

```json
{
  "selected_topic_id": "target_users_stakeholders",
  "selected_topic_label": "target users and stakeholders",
  "selection_reason": "The user explicitly shifted to stakeholder discussion, and this affects permission and feature decisions.",
  "next_focus_slot": "secondary stakeholders"
}
```
# fill framework example

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
      "status": "active",
      "notes": [],
      "slots": [
        {
          "name": "platform",
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_3"
        },
        {
          "name": "moderation",
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_3"
        }
      ]
    },
    {
      "id": "priorities_success_criteria",
      "label": "priorities and success criteria",
      "priority": "medium",
      "status": "partially_filled",
      "notes": [],
      "slots": [
        {
          "name": "workflow efficiency target",
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_3"
        }
      ]
    }
  ],
  "open_questions": []
}
````

### new_user_input

The first version only needs iOS, and students should be able to post an item in under one minute.

## Output

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
      "notes": [],
      "slots": [
        {
          "name": "platform",
          "value": "iOS only for first version",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "The first version only needs iOS",
          "last_updated": "turn_4"
        },
        {
          "name": "moderation",
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_3"
        }
      ]
    },
    {
      "id": "priorities_success_criteria",
      "label": "priorities and success criteria",
      "priority": "medium",
      "status": "partially_filled",
      "notes": [],
      "slots": [
        {
          "name": "workflow efficiency target",
          "value": "Posting an item should take under one minute",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "students should be able to post an item in under one minute",
          "last_updated": "turn_4"
        }
      ]
    }
  ],
  "open_questions": []
}
```
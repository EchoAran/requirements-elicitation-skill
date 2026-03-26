# modify framework example

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
          "last_updated": "turn_6"
        },
        {
          "name": "optional features",
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_6"
        },
        {
          "name": "release scope",
          "value": "student user features only",
          "confidence": "supported_inference",
          "status": "filled",
          "evidence": "previous interview turns",
          "last_updated": "turn_6"
        }
      ]
    }
  ],
  "open_questions": []
}
```

### new_user_input

Teachers also need a separate backend to review reports and take down suspicious listings.

## Output

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
          "last_updated": "turn_6"
        },
        {
          "name": "optional features",
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_6"
        },
        {
          "name": "release scope",
          "value": "student user features only",
          "confidence": "supported_inference",
          "status": "filled",
          "evidence": "previous interview turns",
          "last_updated": "turn_6"
        }
      ]
    },
    {
      "id": "roles_moderation_operations",
      "label": "roles and moderation operations",
      "priority": "high",
      "status": "partially_filled",
      "notes": [
        "Added during runtime because a distinct actor group and moderation workflow emerged."
      ],
      "slots": [
        {
          "name": "admin actors",
          "value": "Teachers",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "Teachers also need a separate backend",
          "last_updated": "turn_7"
        },
        {
          "name": "moderation actions",
          "value": ["review reports", "take down suspicious listings"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "review reports and take down suspicious listings",
          "last_updated": "turn_7"
        },
        {
          "name": "review triggers",
          "value": "Suspicious listings and user reports",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "review reports and take down suspicious listings",
          "last_updated": "turn_7"
        },
        {
          "name": "audit trace needs",
          "value": null,
          "confidence": "open",
          "status": "open_question",
          "evidence": null,
          "last_updated": "turn_7"
        }
      ]
    }
  ],
  "open_questions": [
    "What actions should teachers be allowed to take in the moderation backend?",
    "Does the moderation workflow require audit logs or action history?"
  ]
}
```
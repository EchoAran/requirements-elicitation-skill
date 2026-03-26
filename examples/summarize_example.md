# summarize example

## Input

### final_framework
```json
{
  "phase": "complete",
  "current_topic_id": null,
  "topics": [
    {
      "id": "product_objective",
      "label": "product objective",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "core problem",
          "value": "Students need a convenient way to buy and sell second hand items within the same campus community.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "interview turns 1 to 3",
          "last_updated": "turn_3"
        },
        {
          "name": "expected outcome",
          "value": "A campus focused marketplace app that reduces friction in student to student trading.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "interview turns 1 to 3",
          "last_updated": "turn_3"
        },
        {
          "name": "non goals",
          "value": "No support for off campus public marketplace usage in the first release.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_8",
          "last_updated": "turn_8"
        }
      ]
    },
    {
      "id": "target_users_stakeholders",
      "label": "target users and stakeholders",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "primary users",
          "value": "Students",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_1",
          "last_updated": "turn_1"
        },
        {
          "name": "secondary stakeholders",
          "value": ["Parents with view access", "Teachers as moderators"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_6 and turn_7",
          "last_updated": "turn_7"
        },
        {
          "name": "role distinctions",
          "value": "Students buy and sell items. Parents may view. Teachers handle moderation actions.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_6 and turn_7",
          "last_updated": "turn_7"
        }
      ]
    },
    {
      "id": "user_workflow_scenarios",
      "label": "user workflow and scenarios",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "main usage path",
          "value": "A student posts an item, another student browses or searches, they chat, and complete an offline trade on campus.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 and turn_5",
          "last_updated": "turn_5"
        },
        {
          "name": "important supporting scenarios",
          "value": ["report suspicious listing", "teacher reviews report"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_7",
          "last_updated": "turn_7"
        },
        {
          "name": "edge cases already identified",
          "value": ["fraudulent listings", "unsafe off campus transaction attempts"],
          "confidence": "supported_inference",
          "status": "filled",
          "evidence": "turn_7 and turn_8",
          "last_updated": "turn_8"
        }
      ]
    },
    {
      "id": "functional_capabilities",
      "label": "functional capabilities",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "core required capabilities",
          "value": ["item listing", "search and browse", "in app chat", "report listing"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 to turn_7",
          "last_updated": "turn_7"
        },
        {
          "name": "secondary or optional capabilities",
          "value": ["parent visibility"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_6",
          "last_updated": "turn_6"
        },
        {
          "name": "first release scope",
          "value": "Student trading workflow, basic moderation, and campus only usage.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 to turn_8",
          "last_updated": "turn_8"
        }
      ]
    },
    {
      "id": "constraints_boundaries",
      "label": "constraints and boundaries",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "platform or environment constraints",
          "value": "iOS only for the first release",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4",
          "last_updated": "turn_4"
        },
        {
          "name": "technical constraints",
          "value": "No integrated online payment in the first release",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_5",
          "last_updated": "turn_5"
        },
        {
          "name": "operational constraints",
          "value": "Trades are expected to happen within campus",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_8",
          "last_updated": "turn_8"
        },
        {
          "name": "policy or compliance constraints",
          "value": "Moderation is required for suspicious listings",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_7",
          "last_updated": "turn_7"
        }
      ]
    },
    {
      "id": "priorities_success_criteria",
      "label": "priorities and success criteria",
      "priority": "medium",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "highest priority needs",
          "value": ["fast posting flow", "safe campus specific trading"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 and turn_8",
          "last_updated": "turn_8"
        },
        {
          "name": "tradeoffs already stated",
          "value": ["iOS first before broader platform support", "offline transaction instead of integrated payment"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 and turn_5",
          "last_updated": "turn_5"
        },
        {
          "name": "success signals or metrics",
          "value": ["posting an item takes under one minute", "students can complete a basic trade workflow end to end"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 and turn_9",
          "last_updated": "turn_9"
        }
      ]
    }
  ],
  "open_questions": [
    "Should parent visibility be part of the first release or a later phase?",
    "What level of moderation audit history is required?"
  ]
}
````

## Output

### Artifact 1. final_interview_framework

```json
{
  "phase": "complete",
  "current_topic_id": null,
  "topics": [
    {
      "id": "product_objective",
      "label": "product objective",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "core problem",
          "value": "Students need a convenient way to buy and sell second hand items within the same campus community.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "interview turns 1 to 3",
          "last_updated": "turn_3"
        },
        {
          "name": "expected outcome",
          "value": "A campus focused marketplace app that reduces friction in student to student trading.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "interview turns 1 to 3",
          "last_updated": "turn_3"
        },
        {
          "name": "non goals",
          "value": "No support for off campus public marketplace usage in the first release.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_8",
          "last_updated": "turn_8"
        }
      ]
    },
    {
      "id": "target_users_stakeholders",
      "label": "target users and stakeholders",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "primary users",
          "value": "Students",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_1",
          "last_updated": "turn_1"
        },
        {
          "name": "secondary stakeholders",
          "value": ["Parents with view access", "Teachers as moderators"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_6 and turn_7",
          "last_updated": "turn_7"
        },
        {
          "name": "role distinctions",
          "value": "Students buy and sell items. Parents may view. Teachers handle moderation actions.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_6 and turn_7",
          "last_updated": "turn_7"
        }
      ]
    },
    {
      "id": "user_workflow_scenarios",
      "label": "user workflow and scenarios",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "main usage path",
          "value": "A student posts an item, another student browses or searches, they chat, and complete an offline trade on campus.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 and turn_5",
          "last_updated": "turn_5"
        },
        {
          "name": "important supporting scenarios",
          "value": ["report suspicious listing", "teacher reviews report"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_7",
          "last_updated": "turn_7"
        },
        {
          "name": "edge cases already identified",
          "value": ["fraudulent listings", "unsafe off campus transaction attempts"],
          "confidence": "supported_inference",
          "status": "filled",
          "evidence": "turn_7 and turn_8",
          "last_updated": "turn_8"
        }
      ]
    },
    {
      "id": "functional_capabilities",
      "label": "functional capabilities",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "core required capabilities",
          "value": ["item listing", "search and browse", "in app chat", "report listing"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 to turn_7",
          "last_updated": "turn_7"
        },
        {
          "name": "secondary or optional capabilities",
          "value": ["parent visibility"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_6",
          "last_updated": "turn_6"
        },
        {
          "name": "first release scope",
          "value": "Student trading workflow, basic moderation, and campus only usage.",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 to turn_8",
          "last_updated": "turn_8"
        }
      ]
    },
    {
      "id": "constraints_boundaries",
      "label": "constraints and boundaries",
      "priority": "high",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "platform or environment constraints",
          "value": "iOS only for the first release",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4",
          "last_updated": "turn_4"
        },
        {
          "name": "technical constraints",
          "value": "No integrated online payment in the first release",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_5",
          "last_updated": "turn_5"
        },
        {
          "name": "operational constraints",
          "value": "Trades are expected to happen within campus",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_8",
          "last_updated": "turn_8"
        },
        {
          "name": "policy or compliance constraints",
          "value": "Moderation is required for suspicious listings",
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_7",
          "last_updated": "turn_7"
        }
      ]
    },
    {
      "id": "priorities_success_criteria",
      "label": "priorities and success criteria",
      "priority": "medium",
      "status": "sufficient",
      "notes": [],
      "slots": [
        {
          "name": "highest priority needs",
          "value": ["fast posting flow", "safe campus specific trading"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 and turn_8",
          "last_updated": "turn_8"
        },
        {
          "name": "tradeoffs already stated",
          "value": ["iOS first before broader platform support", "offline transaction instead of integrated payment"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 and turn_5",
          "last_updated": "turn_5"
        },
        {
          "name": "success signals or metrics",
          "value": ["posting an item takes under one minute", "students can complete a basic trade workflow end to end"],
          "confidence": "confirmed",
          "status": "filled",
          "evidence": "turn_4 and turn_9",
          "last_updated": "turn_9"
        }
      ]
    }
  ],
  "open_questions": [
    "Should parent visibility be part of the first release or a later phase?",
    "What level of moderation audit history is required?"
  ]
}
```

### Artifact 2. requirements_summary_report

```md
# Requirements Summary Report

## 1. Product overview
- product idea: A campus focused second hand trading app for student to student transactions.
- intended outcome: Reduce friction in discovering, contacting, and completing second hand trades within the campus community.
- non goals: No support for off campus public marketplace usage in the first release.

## 2. Users and stakeholders
- primary users: Students
- secondary users or stakeholders: Parents with view access, teachers as moderators
- role distinctions: Students buy and sell items. Parents may view. Teachers review reports and moderate suspicious listings.

## 3. Key scenarios and workflows
- main usage path: A student posts an item, another student browses or searches, they chat, and complete an offline trade on campus.
- important supporting scenarios: Reporting suspicious listings, teacher review of reported listings
- edge cases already identified: Fraudulent listings, attempts to move transactions outside intended campus context

## 4. Functional requirements
- core required capabilities: Item listing, search and browse, in app chat, listing report capability
- secondary or optional capabilities: Parent visibility
- first release scope: Student trading workflow, basic moderation, and campus only usage

## 5. Constraints and boundaries
- platform or environment constraints: iOS only for the first release
- technical constraints: No integrated online payment in the first release
- operational constraints: Trades are expected to happen within campus
- policy or compliance constraints: Suspicious listings require moderation support

## 6. Priorities and success criteria
- highest priority needs: Fast posting flow, safe campus specific trading
- tradeoffs already stated: iOS first before broader platform coverage, offline transaction instead of integrated payment
- success signals or metrics: Posting an item should take under one minute, students should complete the basic trade workflow end to end

## 7. Open questions and risks
- unresolved ambiguities: Whether parent visibility belongs in the first release
- assumptions needing validation: Whether current moderation capabilities are sufficient without audit history
- scope risks: Moderation requirements may expand beyond basic report review and takedown actions

## 8. Actionable next steps
- release blocking clarifications: Confirm whether parent visibility is in or out for first release
- experience optimization clarifications: Define moderation audit history depth for operations team workflows
- deferred assumptions with validation plan: Validate whether basic moderation without audit trail is acceptable before broad rollout
```

## Post-Summary Cleanup (Required)

After this summarize flow finishes, execute cleanup of runtime context files for the current interview session.

1. Confirm final summary has been generated successfully.
2. Delete `state/sessions/{session_id}/` recursively, including:
`framework.json`, `history.json`, and `metadata.json`.
3. If deletion fails:
Set `cleanup_pending = true` in session state and perform cleanup retry at the next skill invocation before processing new interview turns.
4. Do not retain session context files by default after summary completion.

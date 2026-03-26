# checkpoints

Use this file to determine the current interview phase.

## Phase definitions

### `start`
Use `start` when any of the following is true:
- there is no existing interview framework
- the user has only provided an initial idea and no structured elicitation has begun
- the previous turn explicitly asked to start requirements elicitation from scratch

### `runtime`
Use `runtime` when:
- an interview framework already exists
- the interview is ongoing
- there are still unresolved required topics or material ambiguities

### `complete`
Use `complete` only when the framework is sufficiently mature and one of these conditions holds:
- all required high priority topics have enough information for a useful requirements summary
- the remaining unknowns are minor and clearly marked as open questions
- the user explicitly asks to stop and summarize
- the user signals that the current understanding is enough for drafting requirements

## Completion checklist

Before choosing `complete`, verify all of the following:
1. Product goal is captured.
2. Target users or stakeholders are identified.
3. Core workflow or main usage path is described.
4. Main functional expectations are captured.
5. Major constraints, assumptions, or non goals are captured or explicitly unknown.
6. Any major ambiguity that changes scope is either clarified or clearly listed as open.
7. At least four high priority topics are `partially_filled` or `sufficient`.
8. No unresolved high impact contradiction remains in `conflicted` slots.

If two or more items above are still weak or missing, remain in `runtime`.
If item 8 fails, remain in `runtime` even when the user asks for summary.

## Runtime subcases

Within `runtime`, detect whether the next action should emphasize:
- structural update
- slot filling
- topic switching
- clarification of contradictions
- summarization before continuation

## Notes

Do not mark `complete` just because the conversation is long.
Do not remain in `runtime` forever if the user wants to stop and the remaining gaps are non critical.
When stopping early by user request, keep unresolved contradictions and major assumptions explicit in open questions and risk section.

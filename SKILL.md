---
name: requirements-elicitation
description: Conduct semi-structured requirements elicitation interviews for product and software ideas. Use when a user wants to discuss an early product concept, clarify goals, users, workflows, constraints, scope, priorities, risks, or open questions through a guided but adaptive interview that can add, remove, and refine topics as the conversation evolves.
license: Proprietary
compatibility: Designed for agent environments that can read bundled markdown and json files. No external network access required.
---

# Requirements Elicitation Skill

Use this skill when the user provides an initial product idea, software concept, feature request, or vague requirement set and wants help turning it into a clearer, more structured requirements understanding through an interview.

This skill runs as a stateful semi structured interview loop. Do not treat it as a one shot questionnaire. Maintain and evolve an interview framework as the conversation develops.

## State Management

This skill uses file-based state persistence to maintain interview context across execution sessions. See `references/state_management.md` for detailed implementation rules.

### Key Behaviors
- **Persistence**: Framework and conversation history are saved to files after each state-changing operation
- **Recovery**: Previous session state is automatically restored when available
- **Cleanup**: All state files are deleted after successful interview completion and summarization

When needed, load only the files relevant to the current step instead of reading every file at once.

## Core operating model

At every turn, execute the following sequence:

0. Load State: Check for existing session state, restore if available (see `references/state_management.md`)
1. Check the current interview status.
2. Classify the newest user input and detect product type routing intent (see `references/intent_routing.md`).
3. Maintain the interview framework structure if needed.
4. Fill the framework with any newly confirmed information.
5. Detect and register contradictions that need clarification (see `references/conflict_resolution.md`).
6. Select the current topic.
7. Generate the next interview utterance.
8. Persist State: Save updated framework and history (see `references/state_management.md`)

Stop the loop only when the completion conditions in `references/checkpoints.md` are satisfied.

## Step 1. Check current interview status

Read `references/checkpoints.md`.

Classify the interview into one of these phases:
- `start`
- `runtime`
- `complete`

Use that file to determine whether you should initialize a framework, continue the interview loop, or stop and summarize.

## Step 2. Classify input intent and route by product type

Read `references/intent_routing.md`.
Use `examples/intent_routing_example.md` when needed.

Classify the newest user input before slot filling.
Use intent type to determine:
- whether to fill slots directly
- whether to mark items as tentative and confirm
- whether to trigger structural update review
- whether to adjust interview strategy without filling framework

At `start`, detect product type and initialize from the smallest viable topic template.
Use default topics only when product type signals are weak.

## Step 3. Maintain the interview framework

Read `references/maintain_framework.md`.

If phase is `start`, initialize a new framework.
If phase is `runtime`, decide whether the framework needs structural change.
Structural change includes:
- adding a topic
- removing a topic
- adding an information slot
- removing an information slot
- refining a topic label
- splitting one topic into multiple topics
- merging overlapping topics

Use:
- `examples/new_framework_example.md` for initialization patterns
- `examples/modify_framework_example.md` for runtime structural edits
- `assets/interview_framework_schema.json` as the output schema

Do not create structural changes unless there is clear evidence from the user input or the current framework quality.

## Step 4. Fill the framework

Read `references/fill_framework.md`.

Update the framework by writing newly grounded information into the appropriate slots.
Only record information that is explicitly stated by the user or is a tightly supported inference marked with a confidence note.
Do not convert speculation into confirmed facts.
Do not overwrite earlier grounded content unless the user corrects it or provides more specific information.

Use `examples/fill_framework_example.md` when needed.

## Step 5. Detect and handle contradictions

Read `references/conflict_resolution.md`.
Use `examples/contradiction_resolution_example.md` when needed.

When conflicting claims are found:
- mark related slot status as `conflicted`
- add a contradiction item in `open_questions`
- prioritize clarification in the next turn

Do not proceed to completion while high impact contradictions remain unresolved.

## Step 6. Select the current topic

Read `references/select_current_topic.md`.

Choose the topic that should drive the next turn.
At `start`, default to the first high priority topic in the initialized framework.
At `runtime`, choose based on:
- the user’s most recent answer
- unresolved required slots
- explicit topic switching by the user
- topic dependencies
- avoidance of repetitive questioning
- interview efficiency

Use `examples/select_current_topic_example.md` when needed.

Use `references/topic_dependency_map.md` during topic selection when dependency checks are needed.

## Step 7. Generate the next interview utterance

Read `references/generate_speak.md`.

Generate exactly one interview turn that is appropriate for the selected topic and current framework state.
The utterance should usually do one of the following:
- ask a focused question
- ask a clarification question
- confirm a high impact interpretation
- gently transition to the next topic
- summarize and verify before moving on

Keep questions concrete and information seeking.
Prefer asking for examples, workflows, decisions, constraints, and priorities over asking abstract open ended questions without guidance.
Avoid asking multiple unrelated questions in one turn.

Use `examples/generate_speak_example.md` when needed.

## Completion behavior

When the interview reaches `complete`, do not continue asking questions.
Instead:
1. Load `examples/summarize_example.md`
2. Load `assets/requirements_report_format.md`
3. Output:
   - the final interview framework
   - a structured requirements summary following the required report format
4. **Clean State**: Delete all session state files (see `references/state_cleanup.md`)

Completion hard rule:
- do not mark the interview as `complete` when unresolved high impact contradictions still exist

## Global rules

- Treat the interview framework as runtime working memory.
- Keep framework structure and framework content separate.
- Preserve traceability between user statements and recorded slots.
- Support dynamic topic emergence during the interview.
- Prefer minimal sufficient questioning over exhaustive questioning.
- Ask follow up questions when the answer materially affects scope, architecture, users, workflows, constraints, or success criteria.
- If the user clearly declines a topic, mark it and move on unless it blocks the interview.
- If the user changes an earlier statement, update the framework and keep the latest grounded version.
- Do not force a rigid topic order when the user naturally jumps across topics.
- Do not end the interview merely because several topics are partially filled. End only when the completion criteria are satisfied.

## Output discipline during runtime

During the interview loop, do not dump the whole framework every turn unless the user asks for it.
Internally maintain the framework, but externally produce only the next interview utterance plus brief confirmations when useful.

## Failure handling

If the user input is too vague to initialize a meaningful framework, ask a compact scoping question that identifies the product goal, target users, and main function before building the first framework.
If the current framework becomes inconsistent or bloated, simplify it by merging redundant topics and removing low value slots.

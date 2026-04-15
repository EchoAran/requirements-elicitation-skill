# State Management

This document defines the transaction-safe persistence model for stateful interview execution.

## Storage Layout

```text
state/
├── conversation_index.json                 # {conversation_id: session_id}
├── sessions/
│   ├── {session_id}/
│   │   ├── framework.json
│   │   ├── history.json
│   │   ├── metadata.json
│   │   ├── commit.json                     # last successful commit pointer
│   │   └── checkpoints/
│   │       ├── v1/
│   │       ├── v2/
│   │       └── ...
│   └── cleanup.log                         # structured JSONL
├── temp/
│   └── {session_id}/                       # transactional temp write area
└── archive/                                # closed sessions kept for delayed cleanup
```

## Session Identity Rules

- Session IDs must be system-generated only, with format `{YYYYMMDD_HHMMSS}_{A-Z0-9(6)}`.
- User input must never participate in session path construction.
- Runtime must resolve a single active mapping `conversation_id -> session_id` via `conversation_index.json`.
- If mapping ambiguity exists, runtime must quarantine extra candidates and keep only one active session.

## Transaction Commit Protocol

Every state-changing turn must commit with all-or-nothing semantics:

1. Prepare write payload for `framework.json`, `history.json`, `metadata.json`.
2. Validate payload before write.
3. Write temp files into `state/temp/{session_id}/`:
   - `framework.json.tmp`
   - `history.json.tmp`
   - `metadata.json.tmp`
4. If any temp file fails validation, abort commit and keep prior state untouched.
5. Snapshot current state to `checkpoints/v{n}/` before replacing live files.
6. Rename temp files atomically into `state/sessions/{session_id}/`.
7. Write `commit.json` with last successful commit marker.

`commit.json` required fields:
- `session_id`
- `turn_id`
- `state_version`
- `schema_version`
- `timestamp`
- `content_hash`

## Idempotency and Retry Rules

- Each turn must carry a stable `turn_id`.
- Before appending to `history.json`, check whether latest `turn_id` already equals incoming `turn_id`.
- If equal, treat as idempotent retry and skip append.
- Track retry pressure in `metadata.write_attempt_count`.

## Snapshot and Recovery

- Keep checkpoints for the latest 3 to 5 committed versions.
- On corruption or migration failure, rollback from latest checkpoint.
- Recovery order:
  1. Validate current files
  2. If invalid, rollback to latest checkpoint
  3. If no checkpoint exists, initialize a fresh session

## Two-Phase Cleanup Policy

- On completion, mark session `status=closed` first, do not hard-delete immediately.
- Keep summary and latest checkpoints for delayed cleanup.
- Move stale closed sessions to `state/archive/`.
- Delete only after retention threshold via maintenance job.

## Guardrails

- All persistence must use JSON serialization (`json.dump`) with UTF-8.
- String concatenation write patterns are not allowed.
- Enforce hard size limits for input text, evidence list, and history file.
- Record truncation events in metadata fields (`truncated_fields`, `truncation_count`).

## Tooling Entry Points

- `scripts/commit_state.py`
- `scripts/validate_state.py`
- `scripts/check_state_drift.py`
- `scripts/security_scan_state.py`
- `scripts/cleanup_sessions.py`

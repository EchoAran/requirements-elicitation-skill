# State Management

This document defines the file-based state persistence system for maintaining interview context across execution sessions.

## Overview

The state management system enables the skill to maintain continuity across multiple execution sessions by persisting the interview framework and conversation history to files. This is essential when the skill cannot rely on runtime context injection.

## Architecture

### Storage Structure
```
state/
├── sessions/                    # Session state directory
│   ├── {session_id}/           # Per-session directory
│   │   ├── framework.json      # Interview framework state
│   │   ├── history.json        # Conversation history
│   │   └── metadata.json       # Session metadata
│   └── cleanup.log            # Cleanup operation log
└── temp/                      # Temporary files directory
```

### Session Identification
- **Session ID Format**: `{timestamp}_{random_suffix}`
  - `timestamp`: `YYYYMMDD_HHMMSS` (e.g., `20240323_143052`)
  - `random_suffix`: 6-character alphanumeric string (e.g., `A7X9K2`)
  - **Example**: `20240323_143052_A7X9K2`

### State Components
1. **Framework State** (`framework.json`): Complete interview framework matching `assets/interview_framework_schema.json`
2. **Conversation History** (`history.json`): Chronological record of turns
3. **Session Metadata** (`metadata.json`): Session information and timestamps

## Operational Flow

### State Loading (Step 0)
1. Check for existing session state files
2. If found, validate and restore framework and history
3. If not found or invalid, proceed as new session
4. Update metadata with last access time

### State Persistence (Step 8)
1. After each state-changing operation, save current framework
2. Append new conversation turn to history
3. Update metadata timestamps
4. Use atomic write operations to prevent corruption

### State Cleanup (Completion)
1. After successful summarization, delete entire session directory
2. Log cleanup operation to `cleanup.log`
3. Handle cleanup failures gracefully

## Error Handling

### Recovery Strategies
- **Framework Corruption**: Reinitialize from schema template
- **History Corruption**: Continue with empty history
- **Metadata Corruption**: Use default metadata values
- **Storage Full**: Implement size limits and cleanup policies

### Concurrency Protection
- Use atomic file operations (write to temp, then rename)
- Implement retry logic for transient failures
- Log conflicts but continue execution

## Implementation References

- Storage rules: `references/state_storage_rules.md`
- Lifecycle management: `references/state_lifecycle.md`
- Cleanup procedures: `references/state_cleanup.md`

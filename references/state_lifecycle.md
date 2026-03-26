# State Lifecycle Management

This document defines the lifecycle of state files from creation to cleanup.

## Session Lifecycle Phases

### 1. Initialization Phase
**Trigger**: First execution or when no existing state found

**Actions**:
1. Generate unique session_id
2. Create session directory: `state/sessions/{session_id}/`
3. Initialize empty framework.json with schema defaults
4. Create empty history.json array
5. Write initial metadata.json
6. Log session creation to cleanup.log

**Initial Framework State**:
```json
{
  "phase": "start",
  "current_topic_id": null,
  "topics": [],
  "open_questions": []
}
```

**Initial Metadata**:
```json
{
  "session_id": "...",
  "created_at": "2024-03-23T14:30:52Z",
  "last_updated": "2024-03-23T14:30:52Z",
  "last_accessed": "2024-03-23T14:30:52Z",
  "phase": "start",
  "turn_count": 0,
  "version": "1.0"
}
```

### 2. Runtime Phase
**Trigger**: After initialization until completion

**Persistence Triggers**:
- Framework structure changes (add/remove topics, slots)
- Framework content updates (fill slots, change status)
- New conversation turns
- Phase transitions

**Update Frequency**:
- After each user input processing
- After each framework modification
- Before generating agent response

**Metadata Updates**:
- `last_updated`: Current timestamp
- `last_accessed`: Current timestamp
- `turn_count`: Increment on new turns
- `phase`: Update on phase changes

### 3. Completion Phase
**Trigger**: When interview reaches `complete` phase

**Actions**:
1. Generate final summary (existing behavior)
2. Mark session as completed in metadata
3. Initiate cleanup process
4. Delete session directory
5. Log cleanup completion

**Completion Metadata Update**:
```json
{
  "phase": "complete",
  "completed_at": "2024-03-23T15:45:30Z",
  "cleanup_status": "pending|completed|failed"
}
```

## State Recovery Process

### Recovery Triggers
- New execution with existing session context
- Explicit session resumption request
- Automatic detection of session files

### Recovery Steps
1. **Locate Session**: Find session directory by ID
2. **Validate Files**: Check existence and basic integrity
3. **Load Framework**: Parse and validate framework.json
4. **Load History**: Parse and validate history.json
5. **Update Metadata**: Refresh last_accessed timestamp
6. **Resume Execution**: Continue from loaded state

### Recovery Failure Handling
- **Invalid Framework**: Reinitialize with empty framework
- **Corrupt History**: Continue with empty history array
- **Missing Files**: Treat as new session
- **Version Mismatch**: Attempt migration or reinitialize

## State Synchronization

### In-Memory vs File State
- **Primary State**: In-memory objects during execution
- **Backup State**: File persistence after each operation
- **Recovery Source**: Files when restarting execution

### Synchronization Rules
- Always persist after state-changing operations
- Never read from files during single execution
- Use files only for cross-execution continuity
- Validate state consistency on recovery

## Lifecycle Events

### Event Types
- `session_created`: New session initialization
- `state_persisted`: Successful state save
- `session_resumed`: State recovery from files
- `session_completed`: Interview completion
- `cleanup_initiated`: Cleanup process start
- `cleanup_completed`: Successful cleanup
- `cleanup_failed`: Cleanup error

### Event Logging
All lifecycle events logged to `state/sessions/cleanup.log`:

```
2024-03-23T14:30:52Z [session_created] 20240323_143052_A7X9K2
2024-03-23T14:31:15Z [state_persisted] 20240323_143052_A7X9K2 turn=1
2024-03-23T15:45:30Z [session_completed] 20240323_143052_A7X9K2
2024-03-23T15:45:31Z [cleanup_completed] 20240323_143052_A7X9K2
```

## Error Recovery

### Transient Failures
- **Disk I/O Errors**: Retry with exponential backoff
- **Permission Issues**: Log and continue with in-memory state
- **Concurrent Access**: Retry after random delay

### Permanent Failures
- **Storage Full**: Emergency cleanup of old sessions
- **Corruption**: Reinitialize session
- **Deletion Failed**: Mark for manual cleanup

### Failure Thresholds
- Max retries: 3 attempts
- Backoff delay: 100ms, 500ms, 2s
- Emergency cleanup: Remove sessions >7 days old

## Monitoring and Maintenance

### Health Checks
- Session directory existence
- File integrity validation
- Metadata consistency
- Storage space monitoring

### Maintenance Tasks
- Remove sessions older than 7 days
- Validate and repair corrupted files
- Compress old history files
- Generate usage statistics

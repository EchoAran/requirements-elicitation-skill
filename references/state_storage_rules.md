# State Storage Rules

This document defines the detailed rules for storing, retrieving, and managing state files.

## File Formats

### framework.json
Complete interview framework state conforming to `assets/interview_framework_schema.json`.

**Example Structure**:
```json
{
  "phase": "runtime",
  "current_topic_id": "user_requirements",
  "topics": [...],
  "open_questions": [...]
}
```

### history.json
Array of conversation turns with chronological ordering.

**Schema**:
```json
[
  {
    "turn": 1,
    "timestamp": "2024-03-23T14:30:52Z",
    "user_input": "I want to build a campus marketplace app",
    "agent_response": "That sounds interesting. Can you tell me more about the core problem you're trying to solve?",
    "framework_snapshot": {
      "phase": "start",
      "current_topic_id": null,
      "topics": [],
      "open_questions": []
    }
  }
]
```

**Field Definitions**:
- `turn`: Sequential turn number (integer)
- `timestamp`: ISO 8601 timestamp (string)
- `user_input`: Raw user input (string)
- `agent_response`: Agent's response (string)
- `framework_snapshot`: Framework state at end of turn (object)

### metadata.json
Session metadata and tracking information.

**Schema**:
```json
{
  "session_id": "20240323_143052_A7X9K2",
  "created_at": "2024-03-23T14:30:52Z",
  "last_updated": "2024-03-23T14:45:30Z",
  "last_accessed": "2024-03-23T14:45:30Z",
  "phase": "runtime",
  "turn_count": 5,
  "user_context": "Campus marketplace app requirements",
  "version": "1.0"
}
```

## Storage Rules

### Directory Structure
- **Base Path**: `state/sessions/`
- **Session Path**: `state/sessions/{session_id}/`
- **Permissions**: Read/write for skill process, read-only for others

### File Naming
- All files use lowercase names with `.json` extension
- No special characters in filenames
- Session directories named exactly as session_id

### Size Limits
- **Individual File**: 5MB maximum
- **Session Directory**: 10MB maximum
- **History File**: 1000 turns maximum (auto-truncate oldest)

### Encoding
- All files: UTF-8 encoding
- JSON formatting: Pretty-printed with 2-space indentation
- Line endings: LF (\n) for cross-platform compatibility

## Session ID Generation

### Algorithm
1. Get current timestamp: `YYYYMMDD_HHMMSS`
2. Generate 6-character random suffix: `[A-Z0-9]{6}`
3. Combine: `{timestamp}_{suffix}`
4. Verify uniqueness (check directory existence)

### Random Suffix Generation
- Character set: `ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`
- Length: 6 characters
- Collision handling: Regenerate if directory exists

### Examples
- `20240323_143052_A7X9K2`
- `20240323_143053_B4K8M1`
- `20240324_091500_Z9P3L7`

## File Operations

### Atomic Writes
1. Write to temporary file: `{filename}.tmp`
2. Validate JSON syntax
3. Rename to final filename
4. Delete temporary file

### Read Operations
1. Check file existence
2. Read entire file content
3. Parse JSON with error handling
4. Validate against schema (if applicable)

### Error Handling
- **File Not Found**: Treat as new session
- **JSON Parse Error**: Log and use defaults
- **Permission Denied**: Log and continue with in-memory state
- **Disk Full**: Implement emergency cleanup

## Validation Rules

### Framework Validation
- Must conform to `interview_framework_schema.json`
- Required fields: `phase`, `current_topic_id`, `topics`, `open_questions`
- Phase must be one of: `start`, `runtime`, `complete`

### History Validation
- Must be array of turn objects
- Turns must have sequential `turn` numbers
- Timestamps must be valid ISO 8601
- Framework snapshots must be valid (optional validation)

### Metadata Validation
- Session ID must match directory name
- Timestamps must be valid ISO 8601
- Version must be semantic version string

# State Cleanup Procedures

This document defines the procedures for cleaning up state files after interview completion.

## Cleanup Triggers

### Primary Trigger
**Interview Completion**: When phase reaches `complete` and summarization succeeds

**Conditions**:
- Framework phase == "complete"
- Summarization output generated successfully
- No pending operations requiring state

### Secondary Triggers
**Manual Cleanup**: Administrative cleanup of orphaned sessions
**Emergency Cleanup**: When storage limits exceeded
**Session Timeout**: Sessions older than configured threshold

## Cleanup Process

### Standard Completion Cleanup

#### Step 1: Pre-Cleanup Validation
1. Verify interview is truly complete
2. Confirm summarization output was generated
3. Check for any dependent processes

#### Step 2: State Preservation (Optional)
If audit trail required:
- Move session directory to `state/archive/{session_id}/`
- Compress files for long-term storage
- Update archive metadata

#### Step 3: Directory Deletion
1. Delete `framework.json`
2. Delete `history.json`
3. Delete `metadata.json`
4. Remove session directory `state/sessions/{session_id}/`

#### Step 4: Logging
Log cleanup completion to `state/sessions/cleanup.log`:
```
2024-03-23T15:45:31Z [cleanup_completed] 20240323_143052_A7X9K2
```

### Error Handling

#### Cleanup Failure Scenarios
- **Permission Denied**: Retry as administrator, log failure
- **Directory Not Empty**: Force delete remaining files
- **Concurrent Access**: Wait and retry, abort after timeout

#### Failure Recovery
- Mark session as "cleanup_failed" in metadata
- Schedule retry during next execution
- Manual cleanup flag for administrative intervention

## Maintenance Cleanup

### Orphaned Session Detection
**Criteria**:
- No access for >24 hours
- Phase stuck in "runtime" without updates
- Invalid or corrupted state files

**Cleanup Process**:
1. Log orphaned session detection
2. Attempt standard cleanup
3. If failed, move to quarantine directory

### Storage Limit Enforcement
**Triggers**:
- Total storage > 100MB
- Session count > 50 active sessions
- Individual session > 10MB

**Cleanup Strategy**:
1. Sort sessions by last access time
2. Remove oldest sessions first
3. Preserve sessions with "complete" phase
4. Log storage cleanup actions

### Time-Based Expiration
**Policy**:
- Complete sessions: Delete after 7 days
- Incomplete sessions: Delete after 30 days
- Archived sessions: Delete after 90 days

## Quarantine and Recovery

### Quarantine Directory
`state/quarantine/{session_id}_{timestamp}/`

**Usage**:
- Failed cleanup sessions
- Corrupted state files
- Suspicious activity detection

### Recovery Procedures
1. Manual inspection of quarantined files
2. Data recovery if valuable
3. Permanent deletion after review

## Logging and Auditing

### Cleanup Log Format
```
{timestamp} [{event_type}] {session_id} {details}
```

**Event Types**:
- `cleanup_initiated`: Cleanup process started
- `cleanup_completed`: Successful cleanup
- `cleanup_failed`: Cleanup error with reason
- `maintenance_started`: Maintenance cleanup began
- `maintenance_completed`: Maintenance cleanup finished
- `quarantine_moved`: Session moved to quarantine

### Audit Trail
- All cleanup operations logged
- Include reason and outcome
- Track manual interventions
- Generate periodic cleanup reports

## Configuration Parameters

### Default Settings
```json
{
  "cleanup": {
    "complete_session_retention_days": 7,
    "incomplete_session_retention_days": 30,
    "max_storage_mb": 100,
    "max_sessions": 50,
    "emergency_cleanup_threshold_mb": 150,
    "retry_attempts": 3,
    "retry_delay_ms": 1000
  }
}
```

### Runtime Configuration
- Configurable retention policies
- Adjustable storage limits
- Custom cleanup schedules
- Emergency threshold tuning

## Monitoring and Alerts

### Health Metrics
- Active session count
- Storage utilization percentage
- Cleanup success rate
- Quarantine directory size

### Alert Conditions
- Cleanup failure rate > 10%
- Storage utilization > 90%
- Quarantine growth > 20% weekly
- Manual intervention required

### Automated Responses
- Emergency cleanup on storage threshold
- Alert generation for failures
- Performance degradation detection

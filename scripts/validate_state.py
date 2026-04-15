#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SESSION_ID_PATTERN = re.compile(r"^\d{8}_\d{6}_[A-Z0-9]{6}$")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def maybe_jsonschema_validate(instance: Any, schema: Dict[str, Any]) -> Optional[str]:
    try:
        import jsonschema  # type: ignore
    except Exception:
        return "jsonschema package not installed; skipped strict schema validation"

    try:
        jsonschema.validate(instance=instance, schema=schema)
        return None
    except Exception as exc:  # pragma: no cover - runtime diagnostics
        return f"schema validation failed: {exc}"


def validate_history(history: Any) -> List[str]:
    errors: List[str] = []
    if not isinstance(history, list):
        return ["history.json must be an array"]

    expected_turn = 1
    seen_turn_ids = set()
    for item in history:
        if not isinstance(item, dict):
            errors.append("history item must be object")
            continue
        turn = item.get("turn")
        turn_id = item.get("turn_id")
        if turn != expected_turn:
            errors.append(f"history turn sequence mismatch at turn={turn}, expected={expected_turn}")
        expected_turn += 1
        if not isinstance(turn_id, str):
            errors.append(f"history turn {turn}: missing turn_id string")
        else:
            if turn_id in seen_turn_ids:
                errors.append(f"duplicate turn_id detected: {turn_id}")
            seen_turn_ids.add(turn_id)
        if not isinstance(item.get("session_id"), str):
            errors.append(f"history turn {turn}: missing session_id")
        if "framework_delta" not in item:
            errors.append(f"history turn {turn}: missing framework_delta")
    return errors


def validate_metadata(metadata: Any) -> List[str]:
    errors: List[str] = []
    required = [
        "session_id",
        "created_at",
        "last_accessed",
        "state_version",
        "schema_version",
        "last_turn_id",
        "last_successful_commit",
        "write_attempt_count",
    ]
    if not isinstance(metadata, dict):
        return ["metadata.json must be an object"]
    for key in required:
        if key not in metadata:
            errors.append(f"metadata missing required field: {key}")
    return errors


def build_conflicted_refs(framework: Dict[str, Any]) -> List[str]:
    refs: List[str] = []
    for topic in framework.get("topics", []):
        topic_id = topic.get("id")
        for slot in topic.get("slots", []):
            if slot.get("status") == "conflicted" and isinstance(topic_id, str):
                refs.append(f"{topic_id}.{slot.get('name')}")
    return refs


def cross_validate(
    framework: Dict[str, Any], history: List[Dict[str, Any]], metadata: Dict[str, Any]
) -> List[str]:
    errors: List[str] = []

    # 1) session_id consistency
    framework_sid = framework.get("session", {}).get("session_id")
    metadata_sid = metadata.get("session_id")
    if framework_sid != metadata_sid:
        errors.append("session_id mismatch between framework.session.session_id and metadata.session_id")
    for item in history:
        if item.get("session_id") != metadata_sid:
            errors.append("session_id mismatch between history turn and metadata")
            break

    # 2) history last turn_id vs metadata.last_turn_id
    if history:
        last_turn_id = history[-1].get("turn_id")
        if last_turn_id != metadata.get("last_turn_id"):
            errors.append("metadata.last_turn_id does not match history last turn_id")

    # 3) current_topic_id exists in topics
    current_topic_id = framework.get("current_topic_id")
    topic_ids = {t.get("id") for t in framework.get("topics", []) if isinstance(t, dict)}
    if current_topic_id is not None and current_topic_id not in topic_ids:
        errors.append("framework.current_topic_id not found in topics")

    # 4) open_questions and conflicted slots correspondence
    conflicted_refs = set(build_conflicted_refs(framework))
    contradiction_refs = set()
    for oq in framework.get("open_questions", []):
        if not isinstance(oq, dict):
            continue
        if oq.get("kind") == "contradiction" and oq.get("status") == "open":
            ref = oq.get("related_slot_ref")
            if isinstance(ref, str):
                contradiction_refs.add(ref)
    for ref in conflicted_refs:
        if ref not in contradiction_refs:
            errors.append(f"conflicted slot has no open contradiction question: {ref}")
    for ref in contradiction_refs:
        if ref not in conflicted_refs:
            errors.append(f"open contradiction question has no conflicted slot: {ref}")

    return errors


def resolve_session_dir(state_root: Path, session_id: Optional[str]) -> Path:
    sessions_root = state_root / "sessions"
    if session_id:
        return sessions_root / session_id
    candidates = sorted([p for p in sessions_root.glob("*") if p.is_dir()], reverse=True)
    if not candidates:
        raise FileNotFoundError("no session directory found")
    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate state files for one session")
    parser.add_argument("--state-root", default="state", help="State root directory")
    parser.add_argument("--schema", default="assets/interview_framework_schema.json", help="Schema path")
    parser.add_argument("--session-id", default=None, help="Session id; latest if omitted")
    args = parser.parse_args()

    state_root = Path(args.state_root)
    schema_path = Path(args.schema)
    session_dir = resolve_session_dir(state_root, args.session_id)
    session_id = session_dir.name

    if not SESSION_ID_PATTERN.match(session_id):
        print(f"[ERROR] invalid session directory name: {session_id}")
        return 1

    framework_path = session_dir / "framework.json"
    history_path = session_dir / "history.json"
    metadata_path = session_dir / "metadata.json"

    missing = [str(p) for p in [framework_path, history_path, metadata_path, schema_path] if not p.exists()]
    if missing:
        for item in missing:
            print(f"[ERROR] missing file: {item}")
        return 1

    framework = load_json(framework_path)
    history = load_json(history_path)
    metadata = load_json(metadata_path)
    schema = load_json(schema_path)

    errors: List[str] = []

    schema_msg = maybe_jsonschema_validate(framework, schema)
    if schema_msg:
        if schema_msg.startswith("schema validation failed"):
            errors.append(schema_msg)
        else:
            print(f"[WARN] {schema_msg}")

    errors.extend(validate_history(history))
    errors.extend(validate_metadata(metadata))
    if isinstance(framework, dict) and isinstance(history, list) and isinstance(metadata, dict):
        errors.extend(cross_validate(framework, history, metadata))

    if errors:
        print("[ERROR] validation failed:")
        for err in errors:
            print(f" - {err}")
        return 1

    print(f"[OK] state is valid: {session_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

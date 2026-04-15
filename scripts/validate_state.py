#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


SESSION_ID_PATTERN = re.compile(r"^\d{8}_\d{6}_[A-Z0-9]{6}$")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text_atomic(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    tmp.replace(path)


def read_current_revision(session_dir: Path) -> Optional[str]:
    current_path = session_dir / "CURRENT"
    if not current_path.exists():
        return None
    value = current_path.read_text(encoding="utf-8").strip()
    return value or None


def bootstrap_current_revision(session_dir: Path) -> Optional[str]:
    current = read_current_revision(session_dir)
    if current:
        return current
    revisions_root = session_dir / "revisions"
    revisions_root.mkdir(parents=True, exist_ok=True)

    # 1) legacy manifest -> revision
    manifest_path = session_dir / "manifest.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        if isinstance(manifest, dict):
            commit_id = manifest.get("current_commit_id")
            if isinstance(commit_id, str):
                commit_dir = session_dir / "commits" / commit_id
                if commit_dir.exists():
                    revision_id = "r000001"
                    target = revisions_root / revision_id
                    target.mkdir(parents=True, exist_ok=True)
                    for name in ["framework.json", "history.json", "metadata.json", "commit.json"]:
                        src = commit_dir / name
                        if src.exists():
                            (target / name).write_bytes(src.read_bytes())
                    write_text_atomic(session_dir / "CURRENT", revision_id + "\n")
                    return revision_id

    # 2) legacy live files -> revision
    live_files = [session_dir / "framework.json", session_dir / "history.json", session_dir / "metadata.json"]
    if all(p.exists() for p in live_files):
        revision_id = "r000001"
        target = revisions_root / revision_id
        target.mkdir(parents=True, exist_ok=True)
        for name in ["framework.json", "history.json", "metadata.json", "commit.json"]:
            src = session_dir / name
            if src.exists():
                (target / name).write_bytes(src.read_bytes())
        write_text_atomic(session_dir / "CURRENT", revision_id + "\n")
        return revision_id

    # 3) existing revisions but no CURRENT -> pick latest lexical
    candidates = sorted([p.name for p in revisions_root.glob("r*") if p.is_dir()])
    if candidates:
        revision_id = candidates[-1]
        write_text_atomic(session_dir / "CURRENT", revision_id + "\n")
        return revision_id
    return None


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

    previous_turn: Optional[int] = None
    seen_turn_ids = set()
    for item in history:
        if not isinstance(item, dict):
            errors.append("history item must be object")
            continue
        turn = item.get("turn")
        turn_id = item.get("turn_id")
        if not isinstance(turn, int) or turn <= 0:
            errors.append(f"history turn must be positive integer, got={turn}")
        elif previous_turn is not None and turn != previous_turn + 1:
            errors.append(
                f"history turn sequence mismatch: previous={previous_turn}, current={turn}, expected={previous_turn + 1}"
            )
        previous_turn = turn if isinstance(turn, int) else previous_turn
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
        "status",
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
    framework: Dict[str, Any],
    history: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    commit: Optional[Dict[str, Any]],
    conversation_index: Optional[Dict[str, Any]],
    current_revision_id: Optional[str],
    revision_dir: Optional[Path],
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

    # 1.1) session status/schema consistency
    framework_session = framework.get("session", {})
    if framework_session.get("status") != metadata.get("status"):
        errors.append("status mismatch between framework.session.status and metadata.status")
    if framework_session.get("schema_version") != metadata.get("schema_version"):
        errors.append("schema_version mismatch between framework.session.schema_version and metadata.schema_version")

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

    # 5) commit consistency
    if commit is not None:
        if commit.get("session_id") != metadata_sid:
            errors.append("commit.session_id does not match metadata.session_id")
        if commit.get("turn_id") != metadata.get("last_turn_id"):
            errors.append("commit.turn_id does not match metadata.last_turn_id")
        if commit.get("schema_version") != metadata.get("schema_version"):
            errors.append("commit.schema_version does not match metadata.schema_version")

    # 6) conversation index consistency
    if conversation_index is not None:
        conversation_id = metadata.get("conversation_id")
        if isinstance(conversation_id, str):
            mapped = conversation_index.get(conversation_id)
            if mapped != metadata_sid:
                errors.append("conversation_index mapping does not match metadata session_id")

    # 7) current revision consistency
    if current_revision_id is not None:
        if not current_revision_id.startswith("r"):
            errors.append("CURRENT revision id must start with 'r'")
    if revision_dir is not None:
        for name in ["framework.json", "history.json", "metadata.json"]:
            if not (revision_dir / name).exists():
                errors.append(f"revision missing required file: {name}")

    return errors


def resolve_session_dir(
    state_root: Path, session_id: Optional[str], conversation_id: Optional[str]
) -> Path:
    sessions_root = state_root / "sessions"
    if session_id:
        return sessions_root / session_id
    if conversation_id:
        index_path = state_root / "conversation_index.json"
        if not index_path.exists():
            raise FileNotFoundError("conversation_index.json not found while resolving conversation_id")
        index = load_json(index_path)
        mapped = index.get(conversation_id) if isinstance(index, dict) else None
        if not isinstance(mapped, str):
            raise FileNotFoundError("conversation_id not found in conversation_index.json")
        return sessions_root / mapped
    candidates = sorted([p for p in sessions_root.glob("*") if p.is_dir()], reverse=True)
    if not candidates:
        raise FileNotFoundError("no session directory found")
    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate state files for one session")
    parser.add_argument("--state-root", default="state", help="State root directory")
    parser.add_argument("--schema", default="assets/interview_framework_schema.json", help="Schema path")
    parser.add_argument("--session-id", default=None, help="Session id; latest if omitted")
    parser.add_argument("--conversation-id", default=None, help="Resolve session via conversation index")
    args = parser.parse_args()

    state_root = Path(args.state_root)
    schema_path = Path(args.schema)
    session_dir = resolve_session_dir(state_root, args.session_id, args.conversation_id)
    session_id = session_dir.name

    if not SESSION_ID_PATTERN.match(session_id):
        print(f"[ERROR] invalid session directory name: {session_id}")
        return 1

    framework_path = session_dir / "framework.json"
    history_path = session_dir / "history.json"
    metadata_path = session_dir / "metadata.json"
    commit_path = session_dir / "commit.json"
    conversation_index_path = state_root / "conversation_index.json"

    current_revision_id = bootstrap_current_revision(session_dir)
    revision_dir: Optional[Path] = None
    if current_revision_id:
        revision_dir = session_dir / "revisions" / current_revision_id
        framework_path = revision_dir / "framework.json"
        history_path = revision_dir / "history.json"
        metadata_path = revision_dir / "metadata.json"
        commit_path = revision_dir / "commit.json"

    missing = [str(p) for p in [framework_path, history_path, metadata_path, schema_path] if not p.exists()]
    if missing:
        for item in missing:
            print(f"[ERROR] missing file: {item}")
        return 1

    framework = load_json(framework_path)
    history = load_json(history_path)
    metadata = load_json(metadata_path)
    schema = load_json(schema_path)
    commit = load_json(commit_path) if commit_path.exists() else None
    conversation_index = (
        load_json(conversation_index_path) if conversation_index_path.exists() else None
    )

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
        errors.extend(
            cross_validate(
                framework,
                history,
                metadata,
                commit,
                conversation_index,
                current_revision_id,
                revision_dir,
            )
        )

    if errors:
        print("[ERROR] validation failed:")
        for err in errors:
            print(f" - {err}")
        return 1

    print(f"[OK] state is valid: {session_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

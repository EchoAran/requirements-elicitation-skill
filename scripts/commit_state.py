#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SESSION_ID_PATTERN = re.compile(r"^\d{8}_\d{6}_[A-Z0-9]{6}$")
MAX_USER_INPUT_CHARS = 20000
MAX_EVIDENCE_ITEMS_PER_SLOT = 50
MAX_HISTORY_TURNS = 1000
MAX_HISTORY_BYTES = 5_000_000


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def hash_payload(framework: Any, history: Any, metadata: Any) -> str:
    payload = json.dumps(
        {"framework": framework, "history": history, "metadata": metadata},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def latest_checkpoint_version(checkpoints_dir: Path) -> int:
    versions: List[int] = []
    for item in checkpoints_dir.glob("v*"):
        if item.is_dir() and item.name[1:].isdigit():
            versions.append(int(item.name[1:]))
    return max(versions) if versions else 0


def create_checkpoint(session_dir: Path, keep: int) -> None:
    checkpoints_dir = session_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    next_v = latest_checkpoint_version(checkpoints_dir) + 1
    target = checkpoints_dir / f"v{next_v}"
    target.mkdir(parents=True, exist_ok=True)
    for name in ["framework.json", "history.json", "metadata.json", "commit.json"]:
        src = session_dir / name
        if src.exists():
            shutil.copy2(src, target / name)

    # Keep last N versions
    versions = sorted([p for p in checkpoints_dir.glob("v*") if p.is_dir()], key=lambda p: int(p.name[1:]))
    while len(versions) > keep:
        old = versions.pop(0)
        shutil.rmtree(old, ignore_errors=True)


def enforce_limits(framework: Dict[str, Any], history: List[Dict[str, Any]], metadata: Dict[str, Any]) -> None:
    truncated_fields = metadata.get("truncated_fields")
    if not isinstance(truncated_fields, list):
        truncated_fields = []
    truncation_count = int(metadata.get("truncation_count", 0))

    # user_input length limit
    for item in history:
        if "session_id" not in item:
            item["session_id"] = metadata.get("session_id", "")
        user_input = item.get("user_input")
        if isinstance(user_input, str) and len(user_input) > MAX_USER_INPUT_CHARS:
            item["user_input"] = user_input[:MAX_USER_INPUT_CHARS]
            truncation_count += 1
            truncated_fields.append("history.user_input")

    # evidence list limit
    for topic in framework.get("topics", []):
        if not isinstance(topic, dict):
            continue
        for slot in topic.get("slots", []):
            if not isinstance(slot, dict):
                continue
            evidence = slot.get("evidence")
            if isinstance(evidence, list) and len(evidence) > MAX_EVIDENCE_ITEMS_PER_SLOT:
                slot["evidence"] = evidence[-MAX_EVIDENCE_ITEMS_PER_SLOT:]
                truncation_count += 1
                truncated_fields.append(f"slot.evidence.{topic.get('id')}.{slot.get('name')}")

    # history turn limit
    if len(history) > MAX_HISTORY_TURNS:
        history[:] = history[-MAX_HISTORY_TURNS:]
        truncation_count += 1
        truncated_fields.append("history.turns")

    # history bytes limit
    while len(json.dumps(history, ensure_ascii=False).encode("utf-8")) > MAX_HISTORY_BYTES and len(history) > 1:
        history.pop(0)
        truncation_count += 1
        truncated_fields.append("history.bytes")

    metadata["truncation_count"] = truncation_count
    metadata["truncated_fields"] = truncated_fields


def validate_session_id(session_id: str) -> None:
    if not SESSION_ID_PATTERN.match(session_id):
        raise ValueError(f"invalid session_id format: {session_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Transactional state commit for one session")
    parser.add_argument("--state-root", default="state")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--turn-id", required=True)
    parser.add_argument("--framework-file", required=True)
    parser.add_argument("--history-file", required=True)
    parser.add_argument("--metadata-file", required=True)
    parser.add_argument("--schema-version", default="2.0.0")
    parser.add_argument("--keep-checkpoints", type=int, default=5)
    args = parser.parse_args()

    try:
        validate_session_id(args.session_id)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1

    state_root = Path(args.state_root)
    session_dir = state_root / "sessions" / args.session_id
    temp_dir = state_root / "temp" / args.session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    framework = load_json(Path(args.framework_file))
    history = load_json(Path(args.history_file))
    metadata = load_json(Path(args.metadata_file))

    # Retry/duplicate protection
    existing_history_path = session_dir / "history.json"
    if existing_history_path.exists():
        existing_history = load_json(existing_history_path)
        if isinstance(existing_history, list) and existing_history:
            if existing_history[-1].get("turn_id") == args.turn_id:
                print(f"[OK] duplicate turn detected, commit skipped: {args.turn_id}")
                return 0

    write_attempt_count = int(metadata.get("write_attempt_count", 0)) + 1
    metadata["write_attempt_count"] = write_attempt_count
    metadata["schema_version"] = args.schema_version
    metadata["last_turn_id"] = args.turn_id
    metadata["last_accessed"] = now_iso()
    metadata["last_updated"] = now_iso()
    enforce_limits(framework, history, metadata)

    content_hash = hash_payload(framework, history, metadata)
    commit = {
        "session_id": args.session_id,
        "turn_id": args.turn_id,
        "state_version": metadata.get("state_version", "2.0.0"),
        "schema_version": args.schema_version,
        "timestamp": now_iso(),
        "content_hash": content_hash,
    }
    metadata["last_successful_commit"] = commit

    # Create checkpoint before commit
    create_checkpoint(session_dir, keep=max(3, min(5, args.keep_checkpoints)))

    # Transactional write into state/temp/{session_id}
    tmp_framework = temp_dir / "framework.json.tmp"
    tmp_history = temp_dir / "history.json.tmp"
    tmp_metadata = temp_dir / "metadata.json.tmp"
    write_json(tmp_framework, framework)
    write_json(tmp_history, history)
    write_json(tmp_metadata, metadata)

    # Minimal "all files ready" gate then atomic replace into session dir
    for p in [tmp_framework, tmp_history, tmp_metadata]:
        if not p.exists() or p.stat().st_size == 0:
            print(f"[ERROR] tmp file invalid: {p}")
            return 1

    os_framework = session_dir / "framework.json"
    os_history = session_dir / "history.json"
    os_metadata = session_dir / "metadata.json"
    tmp_framework.replace(os_framework)
    tmp_history.replace(os_history)
    tmp_metadata.replace(os_metadata)
    write_json(session_dir / "commit.json", commit)

    print(f"[OK] committed session={args.session_id} turn_id={args.turn_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

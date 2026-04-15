#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


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


def latest_checkpoint(session_dir: Path) -> Optional[Path]:
    checkpoints = [p for p in (session_dir / "checkpoints").glob("v*") if p.is_dir() and p.name[1:].isdigit()]
    if not checkpoints:
        return None
    return sorted(checkpoints, key=lambda p: int(p.name[1:]), reverse=True)[0]


def rollback_from_checkpoint(session_dir: Path) -> bool:
    ckpt = latest_checkpoint(session_dir)
    if not ckpt:
        return False
    for name in ["framework.json", "history.json", "metadata.json", "commit.json"]:
        src = ckpt / name
        if src.exists():
            shutil.copy2(src, session_dir / name)
    return True


def migrate_framework(
    framework: Dict[str, Any], metadata: Dict[str, Any], target_schema_version: str
) -> Dict[str, Any]:
    framework["schema_version"] = target_schema_version
    framework.setdefault("session", {})
    framework["session"]["schema_version"] = target_schema_version
    framework["session"].setdefault("state_version", metadata.get("state_version", "2.0.0"))
    framework["session"].setdefault("status", "active")
    framework["session"].setdefault("cleanup_pending", False)
    framework["session"].setdefault("cleanup_pending_reason", None)

    # evidence migration
    for topic in framework.get("topics", []):
        topic_id = topic.get("id", "unknown_topic")
        for slot in topic.get("slots", []):
            old_evidence = slot.get("evidence")
            if isinstance(old_evidence, str):
                slot["evidence"] = [
                    {
                        "turn_id": metadata.get("last_turn_id", "turn_unknown"),
                        "excerpt": old_evidence,
                        "timestamp": now_iso(),
                        "confidence_note": f"migrated from string evidence in {topic_id}.{slot.get('name', 'slot')}",
                    }
                ]
            elif old_evidence is None:
                slot["evidence"] = []
            elif isinstance(old_evidence, list):
                normalized = []
                for ev in old_evidence:
                    if isinstance(ev, dict):
                        normalized.append(
                            {
                                "turn_id": ev.get("turn_id", metadata.get("last_turn_id", "turn_unknown")),
                                "excerpt": ev.get("excerpt", ev.get("quote", "")),
                                "timestamp": ev.get("timestamp") or now_iso(),
                                "confidence_note": ev.get("confidence_note", "migrated evidence item"),
                            }
                        )
                slot["evidence"] = normalized

    # open question migration
    migrated_open_questions: List[Dict[str, Any]] = []
    for idx, oq in enumerate(framework.get("open_questions", []), start=1):
        if isinstance(oq, str):
            kind = "contradiction" if oq.startswith("[CONTRADICTION]") else "general"
            migrated_open_questions.append(
                {
                    "id": f"oq_{idx:04d}",
                    "text": oq,
                    "kind": kind,
                    "related_slot_ref": None,
                    "severity": "high" if kind == "contradiction" else None,
                    "status": "open",
                }
            )
        elif isinstance(oq, dict):
            migrated_open_questions.append(oq)
    framework["open_questions"] = migrated_open_questions
    return framework


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and migrate state schema drift")
    parser.add_argument("--state-root", default="state")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--schema", default="assets/interview_framework_schema.json")
    parser.add_argument("--migrate", action="store_true")
    args = parser.parse_args()

    schema = load_json(Path(args.schema))
    target_schema_version = (
        schema.get("properties", {}).get("schema_version", {}).get("const") or "2.0.0"
    )

    session_dir = Path(args.state_root) / "sessions" / args.session_id
    framework_path = session_dir / "framework.json"
    metadata_path = session_dir / "metadata.json"
    if not framework_path.exists() or not metadata_path.exists():
        print("[ERROR] framework.json or metadata.json missing")
        return 1

    framework = load_json(framework_path)
    metadata = load_json(metadata_path)
    actual = metadata.get("schema_version")
    if actual == target_schema_version:
        print(f"[OK] no drift: {actual}")
        return 0

    print(f"[WARN] schema drift detected: session={actual}, target={target_schema_version}")
    if not args.migrate:
        return 1

    try:
        framework = migrate_framework(framework, metadata, target_schema_version)
        metadata["schema_version"] = target_schema_version
        metadata["last_updated"] = now_iso()
        write_json(framework_path, framework)
        write_json(metadata_path, metadata)
        print("[OK] migration completed")
        return 0
    except Exception as exc:
        print(f"[ERROR] migration failed: {exc}")
        if rollback_from_checkpoint(session_dir):
            print("[INFO] rolled back from latest checkpoint")
        else:
            print("[INFO] no checkpoint available for rollback")
        return 1


if __name__ == "__main__":
    sys.exit(main())

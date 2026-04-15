#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from validate_state import bootstrap_current_revision


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def log_cleanup(log_path: Path, row: Dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def remove_conversation_mapping(state_root: Path, conversation_id: str, session_id: str, dry_run: bool) -> None:
    index_path = state_root / "conversation_index.json"
    if not index_path.exists():
        return
    index = load_json(index_path)
    if not isinstance(index, dict):
        return
    mapped = index.get(conversation_id)
    if mapped == session_id:
        del index[conversation_id]
        if not dry_run:
            write_json(index_path, index)


def archive_closed_session(
    state_root: Path, session_dir: Path, archive_root: Path, dry_run: bool, log_path: Path, reason: str
) -> None:
    current_revision_id = bootstrap_current_revision(session_dir)
    revision_dir = session_dir / "revisions" / current_revision_id if current_revision_id else session_dir
    metadata_path = revision_dir / "metadata.json"
    framework_path = revision_dir / "framework.json"
    if not metadata_path.exists():
        return
    metadata = load_json(metadata_path)
    if metadata.get("status") != "closed":
        return
    closed_at = metadata.get("closed_at") or now_iso()

    # Keep framework/session status aligned before archive
    if framework_path.exists():
        framework = load_json(framework_path)
        if isinstance(framework, dict) and isinstance(framework.get("session"), dict):
            framework["session"]["status"] = "closed"
            framework["session"]["closed_at"] = closed_at
            if not dry_run:
                write_json(framework_path, framework)

    metadata["closed_at"] = closed_at
    metadata["cleanup_pending"] = True
    metadata["cleanup_pending_reason"] = "archived_waiting_retention_delete"
    if not dry_run:
        write_json(metadata_path, metadata)
        conversation_id = metadata.get("conversation_id")
        if isinstance(conversation_id, str):
            remove_conversation_mapping(state_root, conversation_id, session_dir.name, dry_run=False)
        # keep legacy mirrors updated
        write_json(session_dir / "metadata.json", metadata)
        if framework_path.exists():
            write_json(session_dir / "framework.json", framework)
        archive_root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(session_dir), str(archive_root / session_dir.name))
    log_cleanup(
        log_path,
        {
            "session_id": session_dir.name,
            "closed_at": closed_at,
            "deleted_at": None,
            "reason": reason,
            "result": "archived" if not dry_run else "dry_run_archive",
        },
    )


def delete_archived(state_root: Path, session_dir: Path, dry_run: bool, log_path: Path, reason: str) -> None:
    deleted_at = now_iso()
    current_revision_id = bootstrap_current_revision(session_dir)
    revision_dir = session_dir / "revisions" / current_revision_id if current_revision_id else session_dir
    metadata_path = revision_dir / "metadata.json"
    if metadata_path.exists():
        metadata = load_json(metadata_path)
        conversation_id = metadata.get("conversation_id")
        if isinstance(conversation_id, str):
            remove_conversation_mapping(state_root, conversation_id, session_dir.name, dry_run)
    if not dry_run:
        shutil.rmtree(session_dir, ignore_errors=True)
    log_cleanup(
        log_path,
        {
            "session_id": session_dir.name,
            "closed_at": None,
            "deleted_at": deleted_at,
            "reason": reason,
            "result": "deleted" if not dry_run else "dry_run_delete",
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive/delete stale sessions with two-phase cleanup")
    parser.add_argument("--state-root", default="state")
    parser.add_argument("--archive-days", type=int, default=30)
    parser.add_argument("--delete-days", type=int, default=90)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    state_root = Path(args.state_root)
    sessions_root = state_root / "sessions"
    archive_root = state_root / "archive"
    cleanup_log = sessions_root / "cleanup.log"
    now = now_utc()

    if sessions_root.exists():
        for session_dir in [p for p in sessions_root.iterdir() if p.is_dir()]:
            current_revision_id = bootstrap_current_revision(session_dir)
            revision_dir = session_dir / "revisions" / current_revision_id if current_revision_id else session_dir
            metadata_path = revision_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            metadata = load_json(metadata_path)
            last_accessed = metadata.get("last_accessed")
            if not isinstance(last_accessed, str):
                continue
            idle_days = (now - parse_iso(last_accessed)).days
            if idle_days >= args.archive_days and metadata.get("status") == "closed":
                archive_closed_session(
                    state_root=state_root,
                    session_dir=session_dir,
                    archive_root=archive_root,
                    dry_run=args.dry_run,
                    log_path=cleanup_log,
                    reason=f"idle_{idle_days}_days_archive_threshold",
                )

    if archive_root.exists():
        for session_dir in [p for p in archive_root.iterdir() if p.is_dir()]:
            current_revision_id = bootstrap_current_revision(session_dir)
            revision_dir = session_dir / "revisions" / current_revision_id if current_revision_id else session_dir
            metadata_path = revision_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            metadata = load_json(metadata_path)
            anchor = metadata.get("closed_at") or metadata.get("last_accessed")
            if not isinstance(anchor, str):
                continue
            idle_days = (now - parse_iso(anchor)).days
            if idle_days >= args.delete_days:
                delete_archived(
                    state_root=state_root,
                    session_dir=session_dir,
                    dry_run=args.dry_run,
                    log_path=cleanup_log,
                    reason=f"idle_{idle_days}_days_delete_threshold",
                )

    print("[OK] cleanup_sessions completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

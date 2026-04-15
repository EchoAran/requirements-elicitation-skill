#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


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


def close_and_archive(
    session_dir: Path, archive_root: Path, dry_run: bool, log_path: Path, reason: str
) -> None:
    metadata_path = session_dir / "metadata.json"
    if not metadata_path.exists():
        return
    metadata = load_json(metadata_path)
    closed_at = now_iso()
    metadata["status"] = "closed"
    metadata["closed_at"] = closed_at
    metadata["cleanup_pending"] = True
    metadata["cleanup_pending_reason"] = "two_phase_cleanup_waiting_archive"
    if not dry_run:
        write_json(metadata_path, metadata)
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


def delete_archived(session_dir: Path, dry_run: bool, log_path: Path, reason: str) -> None:
    deleted_at = now_iso()
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
            metadata_path = session_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            metadata = load_json(metadata_path)
            last_accessed = metadata.get("last_accessed")
            if not isinstance(last_accessed, str):
                continue
            idle_days = (now - parse_iso(last_accessed)).days
            if idle_days >= args.archive_days:
                close_and_archive(
                    session_dir,
                    archive_root=archive_root,
                    dry_run=args.dry_run,
                    log_path=cleanup_log,
                    reason=f"idle_{idle_days}_days_archive_threshold",
                )

    if archive_root.exists():
        for session_dir in [p for p in archive_root.iterdir() if p.is_dir()]:
            metadata_path = session_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            metadata = load_json(metadata_path)
            anchor = metadata.get("closed_at") or metadata.get("last_accessed")
            if not isinstance(anchor, str):
                continue
            idle_days = (now - parse_iso(anchor)).days
            if idle_days >= args.delete_days:
                delete_archived(
                    session_dir,
                    dry_run=args.dry_run,
                    log_path=cleanup_log,
                    reason=f"idle_{idle_days}_days_delete_threshold",
                )

    print("[OK] cleanup_sessions completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

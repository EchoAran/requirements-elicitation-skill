#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import Any


JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def migrate_slot(slot: dict) -> None:
    ev = slot.get("evidence")
    if isinstance(ev, str):
        slot["evidence"] = [
            {
                "turn_id": slot.get("last_updated") or "turn_unknown",
                "excerpt": ev,
                "timestamp": "1970-01-01T00:00:00Z",
                "confidence_note": "example placeholder",
            }
        ]
    elif ev is None:
        slot["evidence"] = []


def migrate_framework(obj: dict) -> None:
    if "phase" in obj and "topics" in obj:
        obj.setdefault("schema_version", "2.0.0")
        obj.setdefault("session", {})
        session = obj["session"]
        if isinstance(session, dict):
            session.setdefault("session_id", "20260415_000000_ABC123")
            session.setdefault("conversation_id", "conv_example")
            session.setdefault("state_version", "2.0.0")
            session.setdefault("schema_version", "2.0.0")
            session.setdefault("status", "active")
            session.setdefault("closed_at", None)
            session.setdefault("cleanup_pending", False)
            session.setdefault("cleanup_pending_reason", None)
        for topic in obj.get("topics", []):
            if not isinstance(topic, dict):
                continue
            for slot in topic.get("slots", []):
                if isinstance(slot, dict):
                    migrate_slot(slot)

        oq = obj.get("open_questions")
        if isinstance(oq, list) and oq and isinstance(oq[0], str):
            new_oq = []
            for idx, text in enumerate(oq, start=1):
                kind = "contradiction" if text.startswith("[CONTRADICTION]") else "general"
                new_oq.append(
                    {
                        "id": f"oq_{idx:04d}",
                        "text": text,
                        "kind": kind,
                        "related_slot_ref": None,
                        "severity": "high" if kind == "contradiction" else None,
                        "status": "open",
                    }
                )
            obj["open_questions"] = new_oq


def migrate_object(obj: Any) -> Any:
    if isinstance(obj, dict):
        migrate_framework(obj)
        for value in obj.values():
            migrate_object(value)
    elif isinstance(obj, list):
        for item in obj:
            migrate_object(item)
    return obj


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    changed = False

    def repl(match: re.Match) -> str:
        nonlocal changed
        raw = match.group(1)
        try:
            obj = json.loads(raw)
        except Exception:
            return match.group(0)
        obj = migrate_object(obj)
        changed = True
        return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"

    new_text = JSON_BLOCK.sub(repl, text)
    if changed and new_text != text:
        path.write_text(new_text, encoding="utf-8", newline="\n")
    return changed


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "examples"
    changed_count = 0
    for md in sorted(root.glob("*.md")):
        if process_file(md):
            changed_count += 1
    print(f"migrated {changed_count} example files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

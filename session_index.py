"""
Session index: tracks which chat sessions belong to which logged-in
customer, plus a display-friendly copy of each session's messages.

WHY A SEPARATE INDEX INSTEAD OF READING FileSessionManager's FILES:
    FileSessionManager (from strands) already persists everything the
    *agent* needs to resume a conversation (full message history, tool
    calls, etc.) under agent_sessions/<session_id>/. That format is an
    internal implementation detail of the strands library, so parsing
    it directly from the web app would be fragile.

    Instead, the web app keeps its own lightweight index -- just enough
    to render "your past conversations" on a dashboard and replay them
    in the chat UI. The two stores are complementary:
        - FileSessionManager -> feeds the model its memory
        - session_index.json -> feeds the browser its UI

Structure of agent_sessions/session_index.json:
{
  "priya.sharma": [
    {
      "session_id": "session-ab12cd34",
      "customer_id": "CUST-1001",
      "created_at": "2026-08-10T09:00:00",
      "last_active": "2026-08-10T09:05:00",
      "messages": [
        {"role": "user", "text": "...", "ts": "..."},
        {"role": "assistant", "text": "...", "ts": "..."}
      ]
    },
    ...
  ]
}
"""

import json
import os
import threading
import uuid
from datetime import datetime, timezone

import storage_config

# This used to import SESSIONS_DIR from agent_core.py, but agent_core.py
# (and the whole local agent-building setup) now lives only inside the
# ECS container, not in this Flask project. Flask still needs somewhere
# local to keep session_index.json when SESSION_BACKEND=local, so that
# path is defined directly here instead of borrowed from agent_core.
SESSIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_sessions")

INDEX_FILE = os.path.join(SESSIONS_DIR, "session_index.json")
_lock = threading.Lock()

os.makedirs(SESSIONS_DIR, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if not os.path.exists(INDEX_FILE):
        return {}
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(index: dict) -> None:
    tmp_path = INDEX_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    os.replace(tmp_path, INDEX_FILE)


def create_session(username: str, customer_id: str) -> str:
    """Register a brand new chat session for a user. Returns the new session_id."""
    session_id = f"session-{uuid.uuid4().hex[:8]}"
    with _lock:
        index = _load()
        entries = index.setdefault(username, [])
        entries.append({
            "session_id": session_id,
            "customer_id": customer_id,
            "created_at": _now(),
            "last_active": _now(),
            "messages": [],
        })
        _save(index)
    return session_id


def list_sessions(username: str) -> list[dict]:
    """List a user's sessions, most recently active first."""
    with _lock:
        index = _load()
        entries = list(index.get(username, []))
    entries.sort(key=lambda e: e["last_active"], reverse=True)
    return entries


def get_session(username: str, session_id: str) -> dict | None:
    """Fetch one session's full record (including messages), if it belongs
    to this user."""
    with _lock:
        index = _load()
        for entry in index.get(username, []):
            if entry["session_id"] == session_id:
                return entry
    return None


def user_owns_session(username: str, session_id: str) -> bool:
    return get_session(username, session_id) is not None


def append_message(username: str, session_id: str, role: str, text: str) -> None:
    """Append one message to a session's display history and bump last_active."""
    with _lock:
        index = _load()
        for entry in index.get(username, []):
            if entry["session_id"] == session_id:
                entry["messages"].append({"role": role, "text": text, "ts": _now()})
                entry["last_active"] = _now()
                break
        _save(index)


def preview_for(entry: dict, max_len: int = 70) -> str:
    """Short preview string for the dashboard list -- last message, truncated."""
    if not entry["messages"]:
        return "New conversation -- no messages yet."
    last = entry["messages"][-1]["text"].replace("\n", " ").strip()
    if len(last) > max_len:
        last = last[: max_len - 1] + "\u2026"
    prefix = "You: " if entry["messages"][-1]["role"] == "user" else "Agent: "
    return prefix + last
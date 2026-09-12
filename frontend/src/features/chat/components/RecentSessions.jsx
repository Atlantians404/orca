import { useState, useEffect, useCallback } from "react";
import {
  getAllSessions,
  createSession,
  updateSession,
  deleteSession,
} from "../services/chatApi";

/**
 * RecentSessions
 *
 * Responsibility: UI + user interaction only.
 * All API calls go through chatApi.js — this component never touches
 * axios/fetch directly.
 *
 * Props:
 * - activeSessionId: string | null — id of the currently selected session
 * - onSelectSession: (session) => void — called when a session is clicked
 * - onSessionCreated: (session) => void — called after a new session is created
 * - onActiveSessionDeleted: () => void — called if the deleted session was active
 */
export default function RecentSessions({
  activeSessionId,
  onSelectSession,
  onSessionCreated,
  onActiveSessionDeleted,
}) {
  const [sessions, setSessions] = useState([]);
  const [status, setStatus] = useState("loading"); // 'loading' | 'ready' | 'error'
  const [pendingIds, setPendingIds] = useState(() => new Set()); // rows mid-update/delete
  const [creating, setCreating] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState("");

  const loadSessions = useCallback(async () => {
    setStatus("loading");
    try {
      const { items } = await getAllSessions();
      setSessions(items);
      setStatus("ready");
    } catch (err) {
      console.error("Failed to load sessions:", err);
      setStatus("error");
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  function markPending(id, isPending) {
    setPendingIds((prev) => {
      const next = new Set(prev);
      isPending ? next.add(id) : next.delete(id);
      return next;
    });
  }

  async function handleCreate() {
    setCreating(true);
    try {
      const newSession = await createSession({ title: "New Conversation" });
      setSessions((prev) => [newSession, ...prev]);
      onSessionCreated?.(newSession);
    } catch (err) {
      console.error("Failed to create session:", err);
      // Surface inline rather than silently failing.
      alert("Couldn't start a new conversation. Please try again.");
    } finally {
      setCreating(false);
    }
  }

  function handleSelect(session) {
    onSelectSession?.(session);
  }

  function startRename(session) {
    setEditingId(session.id);
    setEditingTitle(session.title);
  }

  function cancelRename() {
    setEditingId(null);
    setEditingTitle("");
  }

  async function commitRename(id) {
    const trimmed = editingTitle.trim();
    if (!trimmed) {
      cancelRename();
      return;
    }
    markPending(id, true);
    try {
      const updated = await updateSession(id, { title: trimmed });
      setSessions((prev) =>
        prev.map((s) => (s.id === id ? { ...s, ...updated } : s))
      );
    } catch (err) {
      console.error("Failed to rename session:", err);
      alert("Couldn't rename that conversation. Please try again.");
    } finally {
      markPending(id, false);
      cancelRename();
    }
  }

  async function handleDelete(session) {
    if (!confirm(`Delete "${session.title}"? This can't be undone.`)) return;
    markPending(session.id, true);
    try {
      await deleteSession(session.id);
      setSessions((prev) => prev.filter((s) => s.id !== session.id));
      if (session.id === activeSessionId) {
        onActiveSessionDeleted?.();
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
      alert("Couldn't delete that conversation. Please try again.");
    } finally {
      markPending(session.id, false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 py-2">
        <h2 className="text-sm font-semibold text-gray-700">Conversations</h2>
        <button
          onClick={handleCreate}
          disabled={creating}
          className="text-sm px-2 py-1 rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {creating ? "Creating…" : "+ New Chat"}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        {status === "loading" && (
          <p className="text-sm text-gray-500 px-2 py-3">
            Loading conversations...
          </p>
        )}

        {status === "error" && (
          <div className="text-sm text-red-600 px-2 py-3">
            <p>Unable to load conversations.</p>
            <button
              onClick={loadSessions}
              className="mt-1 underline hover:no-underline"
            >
              Retry
            </button>
          </div>
        )}

        {status === "ready" && sessions.length === 0 && (
          <p className="text-sm text-gray-500 px-2 py-3">
            No conversations yet.
          </p>
        )}

        {status === "ready" &&
          sessions.map((session) => {
            const isActive = session.id === activeSessionId;
            const isPending = pendingIds.has(session.id);
            const isEditing = editingId === session.id;

            return (
              <div
                key={session.id}
                className={`group flex items-center gap-2 rounded-md px-2 py-2 cursor-pointer ${
                  isActive ? "bg-blue-50" : "hover:bg-gray-50"
                }`}
                onClick={() => !isEditing && handleSelect(session)}
              >
                {isEditing ? (
                  <input
                    autoFocus
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") commitRename(session.id);
                      if (e.key === "Escape") cancelRename();
                    }}
                    onBlur={() => commitRename(session.id)}
                    className="flex-1 text-sm border rounded px-1 py-0.5"
                  />
                ) : (
                  <span className="flex-1 text-sm truncate text-gray-800">
                    {session.title}
                  </span>
                )}

                {isPending ? (
                  <span className="text-xs text-gray-400">…</span>
                ) : (
                  <div className="hidden group-hover:flex items-center gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        startRename(session);
                      }}
                      className="text-xs text-gray-500 hover:text-gray-800"
                      title="Rename"
                    >
                      ✎
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(session);
                      }}
                      className="text-xs text-gray-500 hover:text-red-600"
                      title="Delete"
                    >
                      🗑
                    </button>
                  </div>
                )}
              </div>
            );
          })}
      </div>
    </div>
  );
}
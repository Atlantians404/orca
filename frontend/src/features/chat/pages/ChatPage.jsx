import { useState, useCallback } from "react";
import RecentSessions from "../components/RecentSessions";
import ChatWindow from "../components/ChatWindow";
import { getSession } from "../services/chatApi";

/**
 * ChatPage
 *
 * Responsibility: owns which session is active and the overall chat page
 * state. Does NOT do raw API calls except via chatApi.js, and does NOT
 * contain RecentSessions' list-management logic (create/rename/delete
 * live in RecentSessions.jsx itself, per the CRUD spec).
 */
export default function ChatPage() {
  const [activeSession, setActiveSession] = useState(null);
  const [loadingSession, setLoadingSession] = useState(false);
  const [sessionError, setSessionError] = useState(null);

  const selectSession = useCallback(async (session) => {
    setSessionError(null);

    // If RecentSessions already gave us full session data (e.g. right after
    // creation), no need to re-fetch. Otherwise load the full record —
    // this is also where message history would come from once ChatWindow
    // is wired up to display them.
    const hasFullData = session && "messages" in session;

    if (hasFullData) {
      setActiveSession(session);
      return;
    }

    setLoadingSession(true);
    try {
      const fullSession = await getSession(session.id);
      setActiveSession(fullSession);
    } catch (err) {
      console.error("Failed to load session:", err);
      setSessionError("Unable to load that conversation.");
    } finally {
      setLoadingSession(false);
    }
  }, []);

  const handleSessionCreated = useCallback((newSession) => {
    // New session is already the full object from createSession — use it
    // directly as the active session, no extra round-trip.
    setActiveSession(newSession);
    setSessionError(null);
  }, []);

  const handleActiveSessionDeleted = useCallback(() => {
    setActiveSession(null);
  }, []);

  return (
    <div className="flex h-full">
      <aside className="w-72 border-r border-gray-200">
        <RecentSessions
          activeSessionId={activeSession?.id ?? null}
          onSelectSession={selectSession}
          onSessionCreated={handleSessionCreated}
          onActiveSessionDeleted={handleActiveSessionDeleted}
        />
      </aside>

      <main className="flex-1">
        {loadingSession ? (
          <p className="p-4 text-sm text-gray-500">Loading conversation...</p>
        ) : sessionError ? (
          <p className="p-4 text-sm text-red-600">{sessionError}</p>
        ) : (
          <ChatWindow session={activeSession} />
        )}
      </main>
    </div>
  );
}
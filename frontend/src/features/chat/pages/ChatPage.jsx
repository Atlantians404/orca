import { useState, useCallback } from "react";
import RecentSessions from "../components/RecentSessions";
import ChatWindow from "../components/ChatWindow";
import { getSession } from "../services/chatApi";

/**
 * ChatPage
 *
 * Integration layer only — owns which session is active and wires the
 * session-management layer (RecentSessions) to the conversation UI
 * (ChatWindow). Session CRUD itself lives entirely in RecentSessions.jsx /
 * chatApi.js and is not duplicated here.
 */
export default function ChatPage() {
  const [activeSession, setActiveSession] = useState(null);
  const [loadingSession, setLoadingSession] = useState(false);
  const [sessionError, setSessionError] = useState(null);

  const selectSession = useCallback(async (session) => {
    setSessionError(null);

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
    setActiveSession(newSession);
    setSessionError(null);
  }, []);

  const handleActiveSessionDeleted = useCallback(() => {
    setActiveSession(null);
  }, []);

  return (
    <div className="flex h-screen bg-void text-ink">
      <aside className="hidden w-72 shrink-0 flex-col border-r border-line bg-deep sm:flex">
        <div className="flex items-center gap-2 px-4 py-4">
          <span className="font-display text-sm font-semibold tracking-tightest text-ink">
            ORCA
          </span>
        </div>

        <div className="flex-1 overflow-hidden">
          <RecentSessions
            activeSessionId={activeSession?.id ?? null}
            onSelectSession={selectSession}
            onSessionCreated={handleSessionCreated}
            onActiveSessionDeleted={handleActiveSessionDeleted}
          />
        </div>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col">
        {loadingSession ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-mute">Loading conversation...</p>
          </div>
        ) : sessionError ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-mute">{sessionError}</p>
          </div>
        ) : (
          <ChatWindow session={activeSession} />
        )}
      </main>
    </div>
  );
}
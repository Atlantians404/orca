/**
 * ChatWindow
 *
 * Placeholder only. Per the task scope, the full chatbot UI (message list,
 * streaming, etc.) is a LATER step — this just proves the active session
 * is flowing through correctly from ChatPage -> RecentSessions selection.
 *
 * Wire up real message rendering + ChatInput here once CRUD is confirmed
 * working end-to-end.
 */
export default function ChatWindow({ session }) {
  if (!session) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400 text-sm">
        Select a conversation or start a new one.
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-lg font-semibold text-gray-800">{session.title}</h1>
      <p className="text-xs text-gray-400 mt-1">Session ID: {session.id}</p>
      <p className="text-sm text-gray-500 mt-4">
        (Message history rendering not yet implemented — this is the CRUD
        wiring step.)
      </p>
    </div>
  );
}
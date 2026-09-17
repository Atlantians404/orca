import { useOutletContext } from "react-router-dom";
import ChatWindow from "../components/ChatWindow";

export default function ChatPage() {
  const {
    activeSession,
    loadingSession,
    sessionError,
  } = useOutletContext();

  if (loadingSession) {
    return (
      <div className="flex h-full min-h-0 items-center justify-center bg-[#080809]">
        <p className="text-sm text-[#77777C]">
          Loading conversation...
        </p>
      </div>
    );
  }

  if (sessionError) {
    return (
      <div className="flex h-full min-h-0 items-center justify-center bg-[#080809] px-6 text-center">
        <p className="text-sm text-red-400">
          {sessionError}
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 w-full flex-1 flex-col overflow-hidden bg-[#080809]">
      <ChatWindow session={activeSession} />
    </div>
  );
}
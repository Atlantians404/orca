import { useOutletContext } from "react-router-dom";
import ChatWindow from "../components/ChatWindow";

export default function ChatPage() {
  const {
    activeSession,
    loadingSession,
    sessionError,
    chatsActive,
  } = useOutletContext();

  if (!chatsActive) {
    return (
      <div className="flex h-full flex-col items-center justify-center bg-[#080809] px-6 text-center">
        <div className="mb-5 h-px w-16 bg-white/10" />

        <h1 className="text-xl font-medium tracking-tight text-white">
          ORCA
        </h1>

        <p className="mt-2 max-w-md text-sm text-[#77777C]">
          Select Chats to view your recent
          conversations.
        </p>

        <div className="mt-5 h-px w-16 bg-white/10" />
      </div>
    );
  }

  if (loadingSession) {
    return (
      <div className="flex h-full items-center justify-center bg-[#080809]">
        <p className="text-sm text-[#77777C]">
          Loading conversation...
        </p>
      </div>
    );
  }

  if (sessionError) {
    return (
      <div className="flex h-full items-center justify-center bg-[#080809] px-6 text-center">
        <p className="text-sm text-[#99999F]">
          {sessionError}
        </p>
      </div>
    );
  }

  return (
    <div className="h-full bg-[#080809]">
      <ChatWindow
        session={activeSession}
      />
    </div>
  );
}
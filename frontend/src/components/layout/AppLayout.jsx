import { useState, useCallback } from "react";
import {
  Outlet,
  useNavigate,
  useLocation,
} from "react-router-dom";

import Sidebar from "./Sidebar";

import { getSession } from "../../features/chat/services/chatApi";

// =====================================================
// CHAT ROUTE
// =====================================================

const CHAT_ROUTE = "/chat";

// =====================================================
// MENU ICON
// =====================================================

const MenuIcon = (props) => (
  <svg
    viewBox="0 0 20 20"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    {...props}
  >
    <path
      d="M3 5h14M3 10h14M3 15h14"
      strokeLinecap="round"
    />
  </svg>
);

// =====================================================
// APP LAYOUT
// =====================================================

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);

  const [mobileOpen, setMobileOpen] = useState(false);

  // Chats is active by default
  const [chatsActive, setChatsActive] = useState(true);

  // Currently selected conversation
  const [activeSession, setActiveSession] = useState(null);

  const [loadingSession, setLoadingSession] = useState(false);

  const [sessionError, setSessionError] = useState(null);

  const navigate = useNavigate();
  const location = useLocation();

  // ===================================================
  // SELECT SESSION
  // ===================================================

  const selectSession = useCallback(
    async (session) => {
      setSessionError(null);

      if (!session?.id) {
        return;
      }

      // Some session objects may already contain
      // complete session data.
      const hasFullData =
        session &&
        "messages" in session;

      if (hasFullData) {
        setActiveSession(session);
        setChatsActive(true);
        return;
      }

      setLoadingSession(true);

      try {
        const fullSession =
          await getSession(session.id);

        setActiveSession(fullSession);
        setChatsActive(true);

        // Make sure we are on the chat page
        if (location.pathname !== CHAT_ROUTE) {
          navigate(CHAT_ROUTE);
        }
      } catch (err) {
        console.error(
          "Failed to load session:",
          err
        );

        setSessionError(
          "Unable to load that conversation."
        );
      } finally {
        setLoadingSession(false);
      }
    },
    [location.pathname, navigate]
  );

  // ===================================================
  // SESSION CREATED
  // ===================================================

  const handleSessionCreated = useCallback(
    (newSession) => {
      setActiveSession(newSession);
      setChatsActive(true);
      setSessionError(null);

      if (location.pathname !== CHAT_ROUTE) {
        navigate(CHAT_ROUTE);
      }
    },
    [location.pathname, navigate]
  );

  // ===================================================
  // ACTIVE SESSION DELETED
  // ===================================================

  const handleActiveSessionDeleted =
    useCallback(() => {
      setActiveSession(null);
    }, []);

  // ===================================================
  // TOGGLE CHATS
  // ===================================================

  const handleToggleChats = () => {
    // If already inside Chats and Chats is active,
    // clicking it again hides the chat area.
    if (
      location.pathname === CHAT_ROUTE &&
      chatsActive
    ) {
      setChatsActive(false);
      setActiveSession(null);
      return;
    }

    // If we are somewhere else, go to Chats.
    if (location.pathname !== CHAT_ROUTE) {
      navigate(CHAT_ROUTE);
    }

    setChatsActive(true);
  };

  // ===================================================
  // NEW CHAT
  // ===================================================

  const handleRequestNewChat = () => {
    if (location.pathname !== CHAT_ROUTE) {
      navigate(CHAT_ROUTE);
    }

    setChatsActive(true);
  };

  // ===================================================
  // CHECK CHAT ROUTE
  // ===================================================

  const isChatRoute =
    location.pathname === CHAT_ROUTE;

  // ===================================================
  // RENDER
  // ===================================================

  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#080809]">

      {/* =================================================
          SIDEBAR
          ================================================= */}

      <Sidebar
        collapsed={collapsed}
        onToggleCollapsed={() =>
          setCollapsed(
            (previous) => !previous
          )
        }

        mobileOpen={mobileOpen}

        onCloseMobile={() =>
          setMobileOpen(false)
        }

        activeSessionId={
          activeSession?.id ?? null
        }

        onSelectSession={
          selectSession
        }

        onSessionCreated={
          handleSessionCreated
        }

        onActiveSessionDeleted={
          handleActiveSessionDeleted
        }

        chatsActive={
          isChatRoute && chatsActive
        }

        onToggleChats={
          handleToggleChats
        }

        onRequestNewChat={
          handleRequestNewChat
        }
      />

      {/* =================================================
          MOBILE BACKDROP
          ================================================= */}

      {mobileOpen && (
        <div
          className="
            fixed inset-0 z-30
            bg-black/70
            lg:hidden
          "
          onClick={() =>
            setMobileOpen(false)
          }
          aria-hidden="true"
        />
      )}

      {/* =================================================
          MAIN CONTENT
          ================================================= */}

      <div className="flex min-w-0 flex-1 flex-col">

        {/* =================================================
            MOBILE TOP BAR
            ================================================= */}

        <header
          className="
            flex shrink-0
            items-center gap-3
            border-b border-[#202023]
            bg-[#080809]
            px-3 py-2.5
            lg:hidden
          "
        >
          <button
            type="button"
            onClick={() =>
              setMobileOpen(true)
            }
            aria-label="Open menu"
            title="Open menu"
            className="
              flex h-10 w-10
              items-center justify-center
              rounded-lg
              text-[#BDBDC2]
              hover:bg-white/5
              hover:text-white
            "
          >
            <MenuIcon className="h-5 w-5" />
          </button>

          <span className="text-sm font-semibold text-white">
            ORCA
          </span>
        </header>

        {/* =================================================
            PAGE
            ================================================= */}

        <main
          className="
            min-h-0
            min-w-0
            flex-1
            overflow-hidden
          "
        >
          <Outlet
            context={{
              activeSession,
              loadingSession,
              sessionError,
              chatsActive:
                isChatRoute &&
                chatsActive,
            }}
          />
        </main>
      </div>
    </div>
  );
}
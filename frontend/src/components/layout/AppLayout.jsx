import { useState, useCallback } from "react";
import {
  Outlet,
  useNavigate,
  useLocation,
} from "react-router-dom";

import Sidebar from "./Sidebar";

import {
  getSession,
} from "../../features/chat/services/chatApi";

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

const CHAT_ROUTE = "/test-sessions";

export default function AppLayout() {
  const [collapsed, setCollapsed] =
    useState(false);

  const [mobileOpen, setMobileOpen] =
    useState(false);

  const [chatsActive, setChatsActive] =
    useState(true);

  const [activeSession, setActiveSession] =
    useState(null);

  const [loadingSession, setLoadingSession] =
    useState(false);

  const [sessionError, setSessionError] =
    useState(null);

  const navigate = useNavigate();
  const location = useLocation();

  const selectSession = useCallback(
    async (session) => {
      setSessionError(null);

      const hasFullData =
        session &&
        "messages" in session;

      if (hasFullData) {
        setActiveSession(session);
        return;
      }

      setLoadingSession(true);

      try {
        const fullSession =
          await getSession(session.id);

        setActiveSession(fullSession);
        setChatsActive(true);
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
    []
  );

  const handleSessionCreated =
    useCallback((newSession) => {
      setActiveSession(newSession);
      setChatsActive(true);
      setSessionError(null);
    }, []);

  const handleActiveSessionDeleted =
    useCallback(() => {
      setActiveSession(null);
    }, []);

  /*
   * Chats behaves like a toggle.
   *
   * First click:
   *   Chats becomes active.
   *
   * Second click:
   *   Chats becomes inactive.
   */
  const handleToggleChats = () => {
    if (
      location.pathname === CHAT_ROUTE &&
      chatsActive
    ) {
      setChatsActive(false);
      setActiveSession(null);
      return;
    }

    if (
      location.pathname !== CHAT_ROUTE
    ) {
      navigate(CHAT_ROUTE);
    }

    setChatsActive(true);
  };

  const handleRequestNewChat = () => {
    if (
      location.pathname !== CHAT_ROUTE
    ) {
      navigate(CHAT_ROUTE);
    }

    setChatsActive(true);
  };

  const isChatRoute =
    location.pathname === CHAT_ROUTE;

  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#080809]">

      {/* ================= SIDEBAR ================= */}

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

        onSelectSession={selectSession}
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

      {/* ================= MOBILE BACKDROP ================= */}

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

      {/* ================= MAIN ================= */}

      <div className="flex min-w-0 flex-1 flex-col">

        {/* Mobile top bar */}

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

        <main className="min-h-0 min-w-0 flex-1 overflow-hidden">
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
import { useCallback, useState } from "react";
import { ChevronLeft, ChevronRight, MapPinned, MessageSquare, Plus, User } from "lucide-react";
import RecentSessions from "../components/RecentSessions";
import ChatWindow from "../components/ChatWindow";
import logo from "../../../assets/logo.png";

let mockSessionIdCounter = 2;
const INITIAL_MOCK_SESSIONS = [{ id: 1, title: "New conversation" }];

export default function ChatPage() {
  const [sessions, setSessions] = useState(INITIAL_MOCK_SESSIONS);
  const [activeSessionId, setActiveSessionId] = useState(1); // active immediately — no click needed
  const [collapsed, setCollapsed] = useState(false);

  const selectSession = useCallback((id) => {
    setActiveSessionId(id);
  }, []);

  const startNewSession = useCallback(() => {
    const newSession = { id: mockSessionIdCounter++, title: "New conversation" };
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
  }, []);

  const activeSession = sessions.find((s) => s.id === activeSessionId) ?? null;

  return (
    <div className="flex h-screen bg-void text-ink">
      <aside
        className={`flex shrink-0 flex-col border-r border-line bg-deep transition-[width] duration-200 ${
          collapsed ? "w-16" : "w-64"
        }`}
      >
        <div className={`flex items-center gap-2 px-4 py-4 ${collapsed ? "justify-center px-0" : ""}`}>
                    <img src={logo} alt="" aria-hidden="true" className="h-12 w-12 shrink-0 object-contain -mt-0.5" />
           {!collapsed && (
            <span className="font-display text-xl font-semibold tracking-wide text-ink">O R C A</span>
          )}
        </div>

        <div className={`px-3 pb-3 ${collapsed ? "px-2" : ""}`}>
          <button
            type="button"
            onClick={startNewSession}
            aria-label="New chat"
            className={`flex w-full items-center gap-1.5 rounded-full border border-line2 text-sm text-ink transition-colors duration-200 hover:border-white hover:bg-white/5 ${
              collapsed ? "justify-center p-2" : "justify-center px-3 py-2"
            }`}
          >
            <Plus size={14} aria-hidden="true" />
            {!collapsed && "New Chat"}
          </button>
        </div>

        <nav className={`flex flex-col gap-0.5 px-3 pb-4 ${collapsed ? "px-2 items-center" : ""}`} aria-label="Primary">
          <NavItem icon={MessageSquare} label="Chats" active collapsed={collapsed} />
          <NavItem icon={MapPinned} label="Maps" collapsed={collapsed} disabled />
          <NavItem icon={User} label="Profile" collapsed={collapsed} disabled />
        </nav>

        {!collapsed && (
          <p className="px-4 pb-1.5 text-[11px] font-medium uppercase tracking-wide text-mute2">Recents</p>
        )}

        <div className={`flex-1 overflow-hidden px-3 ${collapsed ? "hidden" : ""}`}>
          <RecentSessions
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={selectSession}
          />
        </div>

        <div className="border-t border-line px-3 py-2">
          <button
            type="button"
            onClick={() => setCollapsed((v) => !v)}
            className={`flex w-full items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs text-mute transition-colors hover:bg-white/5 hover:text-ink ${
              collapsed ? "justify-center" : ""
            }`}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
            {!collapsed && "Collapse"}
          </button>
        </div>

        <div className={`flex items-center gap-2 border-t border-line px-4 py-3 ${collapsed ? "justify-center px-0" : ""}`}>
          <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-surface2 text-xs font-medium text-mute">
            <User size={14} aria-hidden="true" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="truncate text-xs font-medium text-ink">Guest</p>
              <p className="truncate text-[11px] text-mute2">Not signed in</p>
            </div>
          )}
        </div>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col">
        <ChatWindow session={activeSession} />
      </main>
    </div>
  );
}

function NavItem({ icon: Icon, label, active = false, disabled = false, collapsed }) {
  return (
    <button
      type="button"
      disabled={disabled}
      aria-current={active ? "page" : undefined}
      title={disabled ? `${label} (coming soon)` : label}
      className={`flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors duration-150 ${
        collapsed ? "justify-center px-2" : ""
      } ${
        active
          ? "bg-white/[0.06] text-ink"
          : disabled
          ? "cursor-default text-mute2 opacity-60"
          : "text-mute hover:bg-white/[0.04] hover:text-ink"
      }`}
    >
      <Icon size={15} aria-hidden="true" />
      {!collapsed && <span>{label}</span>}
    </button>
  );
}
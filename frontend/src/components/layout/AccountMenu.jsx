import { useState, useEffect, useRef } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { getCurrentUser, logout } from "../../services/authApi";

const ChevronIcon = (props) => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" {...props}>
    <path d="M5 12l5-5 5 5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const UserIcon = (props) => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" {...props}>
    <circle cx="10" cy="6.5" r="3" />
    <path d="M3.5 17c1-3.5 4-5 6.5-5s5.5 1.5 6.5 5" strokeLinecap="round" />
  </svg>
);
const LogOutIcon = (props) => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" {...props}>
    <path d="M8 4H4v12h4M13 14l4-4-4-4M17 10H7" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

/**
 * AccountMenu
 *
 * Fetches the real authenticated user from GET /auth/me — no hardcoded
 * name/email. If that call fails (e.g. endpoint not wired up yet in this
 * environment), the sidebar still renders fine with a generic placeholder
 * rather than breaking navigation.
 */
export default function AccountMenu({ collapsed }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("loading"); // 'loading' | 'ready' | 'error'
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    getCurrentUser()
      .then((data) => {
        if (!cancelled) {
          setUser(data);
          setStatus("ready");
        }
      })
      .catch((err) => {
        if (!cancelled) setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [open]);

  const displayName = user?.name || user?.fullName || user?.username || "Account";
  const displayEmail = user?.email || "";
  const initial = displayName.charAt(0).toUpperCase();

  async function handleLogout() {
    setOpen(false);
    try {
      await logout();
    } catch (err) {
      console.error("Logout request failed:", err);
      // Still navigate away — don't trap the user on a broken logout call.
    }
    navigate("/");
  }

  return (
    <div className="relative border-t border-[#1B1F23] p-2" ref={menuRef}>
      {open && (
        <div
          role="menu"
          className="absolute bottom-full left-2 right-2 mb-1 rounded-md border border-[#1F2732] bg-[#101317] py-1 shadow-lg shadow-black/40"
        >
          <NavLink
            to="/profile"
            onClick={() => setOpen(false)}
            role="menuitem"
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-[#EDEFF2] hover:bg-[#1A1F27]"
          >
            <UserIcon className="w-3.5 h-3.5" />
            Profile
          </NavLink>
          <button
            role="menuitem"
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-[#EDEFF2] hover:bg-[#1A1F27] text-left"
          >
            <LogOutIcon className="w-3.5 h-3.5" />
            Log out
          </button>
        </div>
      )}

      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Account menu"
        aria-haspopup="menu"
        aria-expanded={open}
        className={`flex w-full items-center gap-2.5 rounded-md p-1.5 min-h-[40px] hover:bg-[#14171B] transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-white/50 ${
          collapsed ? "justify-center" : ""
        }`}
      >
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white/10 text-xs font-medium text-white">
          {status === "loading" ? "…" : initial || "?"}
        </span>
        {!collapsed && (
          <span className="flex-1 min-w-0 text-left">
            <span className="block truncate text-sm text-[#EDEFF2]">
              {status === "loading" ? "Loading…" : displayName}
            </span>
            {displayEmail && (
              <span className="block truncate text-xs text-[#7A7D82]">{displayEmail}</span>
            )}
          </span>
        )}
        {!collapsed && (
          <ChevronIcon
            className={`w-3.5 h-3.5 shrink-0 text-[#7A7D82] transition-transform ${open ? "" : "rotate-180"}`}
          />
        )}
      </button>
    </div>
  );
}
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { getCurrentUser, logout } from "../../services/authApi";

const ChevronIcon = (props) => (
  <svg
    viewBox="0 0 20 20"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    {...props}
  >
    <path
      d="M5 12l5-5 5 5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const LogOutIcon = (props) => (
  <svg
    viewBox="0 0 20 20"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    {...props}
  >
    <path
      d="M8 4H4v12h4M13 14l4-4-4-4M17 10H7"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export default function AccountMenu({ collapsed }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("loading");
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
<<<<<<< HEAD
        console.error("Failed to load current user:", err);

        if (!cancelled) {
          setStatus("error");
        }
=======
        if (!cancelled) setStatus("error");
>>>>>>> origin/main
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

      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }
  }, [open]);

  const displayName =
    user?.name ||
    user?.fullName ||
    user?.username ||
    "Account";

  const displayEmail = user?.email || "";

  const initial = displayName.charAt(0).toUpperCase();

  async function handleLogout() {
    setOpen(false);

    try {
      await logout();
    } catch (err) {
      console.error("Logout request failed:", err);
    }

    navigate("/");
  }

  return (
    <div
      className="relative border-t border-[#1B1F23] p-2"
      ref={menuRef}
    >
      {open && (
        <div
          role="menu"
          className="absolute bottom-full left-2 right-2 mb-1 rounded-md border border-[#1F2732] bg-[#101317] py-1 shadow-lg shadow-black/40"
        >
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
              <span className="block truncate text-xs text-[#7A7D82]">
                {displayEmail}
              </span>
            )}
          </span>
        )}

        {!collapsed && (
          <ChevronIcon
            className={`w-3.5 h-3.5 shrink-0 text-[#7A7D82] transition-transform ${
              open ? "" : "rotate-180"
            }`}
          />
        )}
      </button>
    </div>
  );
}
import { useState, useRef, useEffect } from "react";
import { NavLink } from "react-router-dom";

import AccountMenu from "./AccountMenu";
import RecentSessions from "../../features/chat/components/RecentSessions";
import orcaLogo from "../../assets/log.png";


// =====================================================
// ICONS
// =====================================================

const PlusIcon = ({ className = "" }) => (
  <svg
    viewBox="0 0 20 20"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.7"
    className={className}
  >
    <path
      d="M10 4v12M4 10h12"
      strokeLinecap="round"
    />
  </svg>
);


const ChatIcon = ({ className = "" }) => (
  <svg
    viewBox="0 0 20 20"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    className={className}
  >
    <path
      d="M3 4h14v9H7l-4 4V4Z"
      strokeLinejoin="round"
    />
  </svg>
);


const MapIcon = ({ className = "" }) => (
  <svg
    viewBox="0 0 20 20"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    className={className}
  >
    <path
      d="M7 4 3 6v10l4-2 6 2 4-2V4l-4 2-6-2Z"
      strokeLinejoin="round"
    />

    <path d="M7 4v10M13 6v10" />
  </svg>
);


const ProfileIcon = ({ className = "" }) => (
  <svg
    viewBox="0 0 20 20"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    className={className}
  >
    <circle
      cx="10"
      cy="6.5"
      r="3"
    />

    <path
      d="M3.5 17c1-3.5 4-5 6.5-5s5.5 1.5 6.5 5"
      strokeLinecap="round"
    />
  </svg>
);


const ChevronIcon = ({ className = "" }) => (
  <svg
    viewBox="0 0 20 20"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    className={className}
  >
    <path
      d="m12.5 4.5-5.5 5.5 5.5 5.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);


// =====================================================
// SIDEBAR
// =====================================================

export default function Sidebar({
  collapsed,
  onToggleCollapsed,

  mobileOpen,
  onCloseMobile,

  activeSessionId,
  onSelectSession,
  onSessionCreated,
  onActiveSessionDeleted,

  chatsActive,
  onToggleChats,
}) {

  // ===================================================
  // SIDEBAR WIDTH
  // ===================================================

  const [width, setWidth] = useState(270);
  const [isDragging, setIsDragging] = useState(false);

  const draggingRef = useRef(false);
  const recentSessionsRef = useRef(null);


  // ===================================================
  // RESIZE SIDEBAR
  // ===================================================

  useEffect(() => {

    const handlePointerMove = (event) => {

      if (!draggingRef.current) {
        return;
      }

      const newWidth = Math.min(
        360,
        Math.max(
          210,
          event.clientX
        )
      );

      setWidth(newWidth);
    };


    const handlePointerUp = () => {

      if (!draggingRef.current) {
        return;
      }

      draggingRef.current = false;

      setIsDragging(false);

      document.body.style.userSelect = "";
      document.body.style.cursor = "";
    };


    window.addEventListener(
      "pointermove",
      handlePointerMove
    );

    window.addEventListener(
      "pointerup",
      handlePointerUp
    );


    return () => {

      window.removeEventListener(
        "pointermove",
        handlePointerMove
      );

      window.removeEventListener(
        "pointerup",
        handlePointerUp
      );

      document.body.style.userSelect = "";
      document.body.style.cursor = "";
    };

  }, []);


  // ===================================================
  // START RESIZE
  // ===================================================

  const startResize = (event) => {

    event.preventDefault();

    draggingRef.current = true;

    setIsDragging(true);

    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";
  };


  // ===================================================
  // NEW CHAT
  // ===================================================

  const handleNewChat = async () => {

    try {

      await recentSessionsRef.current
        ?.createNewSession?.();

    } finally {

      onCloseMobile?.();
    }
  };


  // ===================================================
  // NAVIGATION STYLE
  //
  // Chats / Maps / Profile all use exactly
  // the same width, height, padding and radius.
  // ===================================================

  const navigationClass = (active) => `
    mx-2
    flex
    min-h-[42px]
    w-[calc(100%-16px)]
    items-center
    gap-3
    rounded-lg
    px-3
    text-sm
    font-medium
    transition-all
    duration-150

    ${
      active
        ? "bg-[#1B1B1D] text-white"
        : "text-[#99999F] hover:bg-[#151517] hover:text-white"
    }
  `;


  // ===================================================
  // SIDEBAR
  // ===================================================

  return (
    <>
      {/* =================================================
          SIDEBAR
          ================================================= */}

      <aside
        style={{
          width: collapsed
            ? undefined
            : `${width}px`,
        }}

        className={`
          fixed
          inset-y-0
          left-0
          z-40

          flex
          min-h-0
          flex-col

          bg-[#080809]
          border-r
          border-[#202023]

          ${
            mobileOpen
              ? "translate-x-0"
              : "-translate-x-full"
          }

          ${
            isDragging
              ? ""
              : "transition-transform duration-200"
          }

          lg:static
          lg:translate-x-0

          ${
            collapsed
              ? "lg:w-[68px]"
              : ""
          }

          w-[270px]
        `}
      >


        {/* =================================================
            FIXED ORCA HEADER

            This part NEVER scrolls.
            ================================================= */}

        <div
          className={`
            flex
            h-[88px]
            shrink-0
            items-center
            px-4

            ${
              collapsed
                ? "lg:justify-center lg:px-2"
                : "gap-3"
            }
          `}
        >

          <img
  src={orcaLogo}
  alt="ORCA"
  className={`
    shrink-0
    object-contain
    ${
      collapsed
        ? "h-[42px] w-[42px]"
        : "h-[52px] w-[52px]"
    }
  `}
/>


          {!collapsed && (
            <span
              className="
                text-[21px]
                font-semibold
                tracking-wide
                text-white
              "
            >
              ORCA
            </span>
          )}

        </div>


        {/* =================================================
            ONE SCROLLABLE AREA

            IMPORTANT:
            New Chat + Navigation + Sessions are
            intentionally inside the SAME scrollbar.

            This gives the ChatGPT-style behavior.
            ================================================= */}

        {!collapsed && (

          <div
            className="
              min-h-0
              flex-1
              overflow-y-auto
              overflow-x-hidden
            "

            style={{
              scrollbarWidth: "thin",
              scrollbarColor:
                "#343438 transparent",
            }}
          >

            {/* =============================================
                NEW CHAT
                ============================================= */}

            <div
              className="
                shrink-0
                px-3
                pb-4
              "
            >

              <button
                type="button"
                onClick={handleNewChat}
                title="New chat"

                className="
                  flex
                  min-h-[44px]
                  w-full
                  items-center
                  gap-3
                  rounded-lg
                  border
                  border-white/10
                  bg-[#111113]
                  px-3
                  text-sm
                  font-medium
                  text-[#E5E5E7]

                  transition-all
                  duration-150

                  hover:border-white/20
                  hover:bg-[#19191B]
                  hover:text-white

                  active:scale-[0.99]
                "
              >

                <PlusIcon
                  className="
                    h-4
                    w-4
                    shrink-0
                  "
                />

                <span>
                  New chat
                </span>

              </button>

            </div>


            {/* =============================================
                NAVIGATION
                ============================================= */}

            <nav
              className="
                shrink-0
                space-y-1
                px-2
              "
            >

              {/* ================= CHATS ================= */}

              <button
                type="button"
                onClick={onToggleChats}
                title="Chats"
                aria-pressed={chatsActive}

                className={navigationClass(
                  chatsActive
                )}
              >

                <ChatIcon
                  className="
                    h-4
                    w-4
                    shrink-0
                  "
                />

                <span>
                  Chats
                </span>

              </button>


              {/* ================= MAPS ================= */}

              <NavLink
                to="/maps"
                onClick={onCloseMobile}
                title="Maps"

                className={({ isActive }) =>
                  navigationClass(isActive)
                }
              >

                <MapIcon
                  className="
                    h-4
                    w-4
                    shrink-0
                  "
                />

                <span>
                  Maps
                </span>

              </NavLink>


              {/* ================= PROFILE ================= */}

              <NavLink
                to="/profile"
                onClick={onCloseMobile}
                title="Profile"

                className={({ isActive }) =>
                  navigationClass(isActive)
                }
              >

                <ProfileIcon
                  className="
                    h-4
                    w-4
                    shrink-0
                  "
                />

                <span>
                  Profile
                </span>

              </NavLink>

            </nav>


            {/* =============================================
                SESSION SECTIONS

                RecentSessions renders:
                  PINNED
                  RECENTS
                  ARCHIVED

                It must NOT have its own scrollbar.
                ============================================= */}

            <div className="mt-4">

              <RecentSessions
                ref={recentSessionsRef}

                activeSessionId={
                  activeSessionId
                }

                onSelectSession={
                  onSelectSession
                }

                onSessionCreated={
                  onSessionCreated
                }

                onActiveSessionDeleted={
                  onActiveSessionDeleted
                }
              />

            </div>


            {/* Extra bottom breathing room */}

            <div className="h-5" />

          </div>

        )}


        {/* =================================================
            COLLAPSED NAVIGATION

            When sidebar is collapsed, keep the compact
            navigation available.
            ================================================= */}

        {collapsed && (

          <div
            className="
              flex
              shrink-0
              flex-col
              items-center
              gap-1
              px-2
            "
          >

            {/* NEW CHAT */}

            <button
              type="button"
              onClick={handleNewChat}
              title="New chat"

              className="
                flex
                h-[42px]
                w-[42px]
                items-center
                justify-center
                rounded-lg
                text-[#99999F]
                transition-all
                hover:bg-[#151517]
                hover:text-white
              "
            >

              <PlusIcon
                className="
                  h-4
                  w-4
                "
              />

            </button>


            {/* CHATS */}

            <button
              type="button"
              onClick={onToggleChats}
              title="Chats"
              aria-pressed={chatsActive}

              className={`
                flex
                h-[42px]
                w-[42px]
                items-center
                justify-center
                rounded-lg
                transition-all

                ${
                  chatsActive
                    ? "bg-[#1B1B1D] text-white"
                    : "text-[#99999F] hover:bg-[#151517] hover:text-white"
                }
              `}
            >

              <ChatIcon
                className="
                  h-4
                  w-4
                "
              />

            </button>


            {/* MAPS */}

            <NavLink
              to="/maps"
              onClick={onCloseMobile}
              title="Maps"

              className={({ isActive }) => `
                flex
                h-[42px]
                w-[42px]
                items-center
                justify-center
                rounded-lg
                transition-all

                ${
                  isActive
                    ? "bg-[#1B1B1D] text-white"
                    : "text-[#99999F] hover:bg-[#151517] hover:text-white"
                }
              `}
            >

              <MapIcon
                className="
                  h-4
                  w-4
                "
              />

            </NavLink>


            {/* PROFILE */}

            <NavLink
              to="/profile"
              onClick={onCloseMobile}
              title="Profile"

              className={({ isActive }) => `
                flex
                h-[42px]
                w-[42px]
                items-center
                justify-center
                rounded-lg
                transition-all

                ${
                  isActive
                    ? "bg-[#1B1B1D] text-white"
                    : "text-[#99999F] hover:bg-[#151517] hover:text-white"
                }
              `}
            >

              <ProfileIcon
                className="
                  h-4
                  w-4
                "
              />

            </NavLink>

          </div>

        )}


        {/* =================================================
            COLLAPSE BUTTON

            FIXED AT BOTTOM
            ================================================= */}

        <button
          type="button"
          onClick={onToggleCollapsed}

          title={
            collapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }

          className="
            hidden
            shrink-0

            lg:flex

            mx-3
            mb-2

            min-h-[40px]

            items-center
            justify-center
            gap-2

            rounded-lg

            text-[#77777C]

            transition-all

            hover:bg-[#151517]
            hover:text-white
          "
        >

          <ChevronIcon
            className={`
              h-4
              w-4

              transition-transform
              duration-200

              ${
                collapsed
                  ? "rotate-180"
                  : ""
              }
            `}
          />


          {!collapsed && (
            <span className="text-xs">
              Collapse
            </span>
          )}

        </button>


        {/* =================================================
            ACCOUNT

            FIXED AT BOTTOM
            ================================================= */}

        <div
          className="
            shrink-0
            border-t
            border-[#202023]
          "
        >

          <AccountMenu
            collapsed={collapsed}
          />

        </div>


        {/* =================================================
            RESIZE DIVIDER
            ================================================= */}

        {!collapsed && (

          <div
            onPointerDown={startResize}

            role="separator"
            aria-orientation="vertical"
            aria-label="Resize sidebar"

            className="
              group

              absolute
              right-0
              top-0

              hidden
              h-full
              w-2

              translate-x-1/2

              cursor-col-resize

              lg:block
            "
          >

            <div
              className="
                mx-auto
                h-full
                w-px

                bg-transparent

                transition-colors

                group-hover:bg-white/30
              "
            />

          </div>

        )}

      </aside>
    </>
  );
}
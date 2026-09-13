import {
  useState,
  useEffect,
  useCallback,
  forwardRef,
  useImperativeHandle,
} from "react";

import {
  getAllSessions,
  getPinnedSessions,
  getArchivedSessions,
  createSession,
  updateSession,
  deleteSession,
  pinSession,
  unpinSession,
  archiveSession,
  unarchiveSession,
} from "../services/chatApi";


// =====================================================
// ICONS
// =====================================================

function ChatIcon({ size = 16 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8A8.5 8.5 0 0 1 8.7 3.9a8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5Z" />
    </svg>
  );
}

function MoreIcon() {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <circle cx="5" cy="12" r="1.5" />
      <circle cx="12" cy="12" r="1.5" />
      <circle cx="19" cy="12" r="1.5" />
    </svg>
  );
}

function EditIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L8 18l-4 1 1-4Z" />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 6h18" />
      <path d="M8 6V4h8v2" />
      <path d="M19 6l-1 15H6L5 6" />
      <path d="M10 11v6" />
      <path d="M14 11v6" />
    </svg>
  );
}

function PinIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 17v5" />
      <path d="m7 4 10 0" />
      <path d="m8 4 1 6-4 4v2h14v-2l-4-4 1-6" />
    </svg>
  );
}

function ArchiveIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 8v13H3V8" />
      <path d="M1 3h22v5H1z" />
      <path d="M10 12h4" />
    </svg>
  );
}

function ChevronIcon({ open }) {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`transition-transform ${
        open ? "rotate-90" : ""
      }`}
    >
      <path d="m9 18 6-6-6-6" />
    </svg>
  );
}


// =====================================================
// TIME
// =====================================================

function formatRelativeTime(session) {
  if (!session?.updated_at) return "";

  const updated = new Date(session.updated_at);
  const now = new Date();

  if (Number.isNaN(updated.getTime())) return "";

  const diff = now.getTime() - updated.getTime();

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m`;
  if (hours < 24) return `${hours}h`;
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days}d`;

  return updated.toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
  });
}


// =====================================================
// SESSION ROW
// =====================================================

function SessionRow({
  session,
  activeSessionId,
  onSelect,
  onMenu,
  editingId,
  editingTitle,
  setEditingTitle,
  saveRename,
  cancelEditing,
  busy,
}) {
  const isActive = activeSessionId === session.id;
  const isEditing = editingId === session.id;

  return (
    <div
      className={`
        group relative flex w-full items-center
        rounded-lg transition-colors duration-150
        ${
          isActive
            ? "bg-[#1D1D20]"
            : "hover:bg-[#151517]"
        }
        ${busy ? "opacity-50" : ""}
      `}
    >

      {/* CLICKABLE CHAT */}

      <button
        type="button"
        disabled={busy}
        onClick={() => {
          if (!isEditing && !busy) {
            onSelect?.(session);
          }
        }}
        className="
          flex min-w-0 flex-1 items-center
          gap-3 px-3 py-2.5 text-left
        "
      >

        <div className="shrink-0 text-[#85858A]">
          <ChatIcon />
        </div>

        <div className="min-w-0 flex-1">

          {isEditing ? (
            <input
              autoFocus
              value={editingTitle}
              onChange={(e) =>
                setEditingTitle(e.target.value)
              }
              onClick={(e) =>
                e.stopPropagation()
              }
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  saveRename(session.id);
                }

                if (e.key === "Escape") {
                  cancelEditing();
                }
              }}
              onBlur={() =>
                saveRename(session.id)
              }
              className="
                w-full border-b border-[#55555A]
                bg-transparent pb-0.5
                text-[13px] text-[#F5F5F5]
                outline-none
              "
            />
          ) : (
            <>
              <div
                className={`
                  truncate text-[13px] font-medium
                  ${
                    isActive
                      ? "text-[#F5F5F5]"
                      : "text-[#C3C3C7]"
                  }
                `}
              >
                {session.title || "Untitled"}
              </div>

              <div className="mt-0.5 text-[10px] text-[#66666B]">
                {formatRelativeTime(session)}
              </div>
            </>
          )}

        </div>

      </button>


      {/* PIN INDICATOR */}

      {session.is_pinned && !isEditing && (
        <div className="mr-1 shrink-0 text-[#85858A]">
          <PinIcon />
        </div>
      )}


      {/* THREE DOT BUTTON */}

      {!isEditing && (
        <button
          type="button"
          disabled={busy}
          data-session-menu-trigger
          onClick={(event) => {
            event.stopPropagation();
            onMenu(event, session);
          }}
          className="
            mr-1 shrink-0 rounded-md p-1.5
            text-[#66666B]
            opacity-0
            transition-all
            group-hover:opacity-100
            hover:bg-[#29292C]
            hover:text-[#F0F0F0]
          "
          aria-label="Session options"
        >
          <MoreIcon />
        </button>
      )}

    </div>
  );
}


// =====================================================
// SECTION HEADER
// =====================================================

function SectionHeader({
  title,
  count,
  open,
  onClick,
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="
        flex w-full items-center gap-1
        px-2 py-2 text-left
        text-[10px] font-semibold
        tracking-[0.18em]
        text-[#77777C]
        hover:text-[#A5A5AA]
      "
    >
      <ChevronIcon open={open} />

      <span>{title}</span>

      {count > 0 && (
        <span
          className="
            ml-1 rounded-full
            bg-[#1D1D20]
            px-1.5 py-0.5
            text-[9px]
            tracking-normal
            text-[#77777C]
          "
        >
          {count}
        </span>
      )}
    </button>
  );
}


// =====================================================
// MAIN COMPONENT
// =====================================================

const RecentSessions = forwardRef(function RecentSessions(
  {
    activeSessionId,
    onSelectSession,
    onSessionCreated,
    onActiveSessionDeleted,
  },
  ref
) {

  const [sessions, setSessions] = useState([]);
  const [pinnedSessions, setPinnedSessions] = useState([]);
  const [archivedSessions, setArchivedSessions] = useState([]);

  const [loading, setLoading] = useState(true);

  const [menu, setMenu] = useState(null);

  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState("");

  const [busyId, setBusyId] = useState(null);

  const [pinnedOpen, setPinnedOpen] = useState(true);
  const [recentsOpen, setRecentsOpen] = useState(true);
  const [archivedOpen, setArchivedOpen] = useState(false);


  // ===================================================
  // LOAD SESSIONS
  // ===================================================

  const loadSessions = useCallback(async () => {
    try {
      setLoading(true);

      const [
        allData,
        pinnedData,
        archivedData,
      ] = await Promise.all([
        getAllSessions(),
        getPinnedSessions(),
        getArchivedSessions(),
      ]);

      const all = allData?.items || [];
      const pinned = pinnedData?.items || [];
      const archived = archivedData?.items || [];


      /*
       * IMPORTANT:
       *
       * RECENTS contains ONLY:
       * - non archived
       * - non pinned
       *
       * Therefore a pinned chat will NOT appear
       * inside RECENTS.
       */

      setSessions(
        all.filter(
          (session) =>
            !session.is_archived &&
            !session.is_pinned
        )
      );


      /*
       * PINNED contains pinned and non-archived chats.
       */

      setPinnedSessions(
        pinned.filter(
          (session) => !session.is_archived
        )
      );


      /*
       * ARCHIVED contains archived chats.
       */

      setArchivedSessions(archived);

    } catch (error) {
      console.error(
        "Failed to load sessions:",
        error
      );
    } finally {
      setLoading(false);
    }
  }, []);


  useEffect(() => {
    loadSessions();
  }, [loadSessions]);


  // ===================================================
  // CREATE
  // ===================================================

  const createNewSession = useCallback(
    async () => {
      try {
        const newSession = await createSession({
          title: "New Conversation",
        });

        setSessions((previous) => [
          newSession,
          ...previous,
        ]);

        setRecentsOpen(true);

        onSessionCreated?.(newSession);

        return newSession;

      } catch (error) {
        console.error(
          "Failed to create session:",
          error
        );

        return null;
      }
    },
    [onSessionCreated]
  );


  useImperativeHandle(
    ref,
    () => ({
      createNewSession,
    }),
    [createNewSession]
  );


  // ===================================================
  // RENAME
  // ===================================================

  const startEditing = (session) => {
    setEditingId(session.id);
    setEditingTitle(session.title || "");
    setMenu(null);
  };


  const cancelEditing = () => {
    setEditingId(null);
    setEditingTitle("");
  };


  const saveRename = async (sessionId) => {

    const title = editingTitle.trim();

    if (!title) {
      cancelEditing();
      return;
    }

    try {
      setBusyId(sessionId);

      const updated = await updateSession(
        sessionId,
        { title }
      );

      const updateItem = (item) =>
        item.id === sessionId
          ? {
              ...item,
              ...updated,
              title,
            }
          : item;

      setSessions((previous) =>
        previous.map(updateItem)
      );

      setPinnedSessions((previous) =>
        previous.map(updateItem)
      );

      setArchivedSessions((previous) =>
        previous.map(updateItem)
      );

      cancelEditing();

    } catch (error) {
      console.error(
        "Failed to rename session:",
        error
      );
    } finally {
      setBusyId(null);
    }
  };


  // ===================================================
  // DELETE
  // ===================================================

  const handleDelete = async (session) => {

    const confirmed = window.confirm(
      `Delete "${session.title}"?`
    );

    if (!confirmed) return;

    try {
      setBusyId(session.id);
      setMenu(null);

      await deleteSession(session.id);

      setSessions((previous) =>
        previous.filter(
          (item) => item.id !== session.id
        )
      );

      setPinnedSessions((previous) =>
        previous.filter(
          (item) => item.id !== session.id
        )
      );

      setArchivedSessions((previous) =>
        previous.filter(
          (item) => item.id !== session.id
        )
      );

      if (activeSessionId === session.id) {
        onActiveSessionDeleted?.();
      }

    } catch (error) {
      console.error(
        "Failed to delete session:",
        error
      );
    } finally {
      setBusyId(null);
    }
  };


  // ===================================================
  // PIN / UNPIN
  // ===================================================

  const handlePinToggle = async (session) => {

    try {
      setBusyId(session.id);
      setMenu(null);

      if (session.is_pinned) {

        // -------------------------------
        // UNPIN
        // -------------------------------

        const updated =
          await unpinSession(session.id);

        const unpinned = {
          ...session,
          ...updated,
          is_pinned: false,
        };

        // Remove from PINNED
        setPinnedSessions((previous) =>
          previous.filter(
            (item) => item.id !== session.id
          )
        );

        // Put back into RECENTS
        if (!unpinned.is_archived) {
          setSessions((previous) => [
            unpinned,
            ...previous.filter(
              (item) => item.id !== session.id
            ),
          ]);
        }

      } else {

        // -------------------------------
        // PIN
        // -------------------------------

        const updated =
          await pinSession(session.id);

        const pinned = {
          ...session,
          ...updated,
          is_pinned: true,
        };

        // Remove from RECENTS
        setSessions((previous) =>
          previous.filter(
            (item) => item.id !== session.id
          )
        );

        // Add to PINNED
        setPinnedSessions((previous) => [
          pinned,
          ...previous.filter(
            (item) => item.id !== session.id
          ),
        ]);

        setPinnedOpen(true);
      }

    } catch (error) {
      console.error(
        "Pin/unpin failed:",
        error
      );
    } finally {
      setBusyId(null);
    }
  };


  // ===================================================
  // ARCHIVE / UNARCHIVE
  // ===================================================

  const handleArchiveToggle = async (session) => {

    try {
      setBusyId(session.id);
      setMenu(null);

      if (session.is_archived) {

        // -------------------------------
        // UNARCHIVE
        // -------------------------------

        const updated =
          await unarchiveSession(
            session.id
          );

        const restored = {
          ...session,
          ...updated,
          is_archived: false,
        };

        // Remove from ARCHIVED
        setArchivedSessions((previous) =>
          previous.filter(
            (item) => item.id !== session.id
          )
        );

        /*
         * If it is pinned, it belongs only
         * in PINNED.
         */

        if (restored.is_pinned) {

          setPinnedSessions((previous) => [
            restored,
            ...previous.filter(
              (item) => item.id !== session.id
            ),
          ]);

          setPinnedOpen(true);

        } else {

          // Otherwise it goes to RECENTS

          setSessions((previous) => [
            restored,
            ...previous.filter(
              (item) => item.id !== session.id
            ),
          ]);

          setRecentsOpen(true);
        }

      } else {

        // -------------------------------
        // ARCHIVE
        // -------------------------------

        const updated =
          await archiveSession(
            session.id
          );

        const archived = {
          ...session,
          ...updated,
          is_archived: true,
        };

        // Remove from RECENTS
        setSessions((previous) =>
          previous.filter(
            (item) => item.id !== session.id
          )
        );

        // Remove from PINNED
        setPinnedSessions((previous) =>
          previous.filter(
            (item) => item.id !== session.id
          )
        );

        // Add to ARCHIVED
        setArchivedSessions((previous) => [
          archived,
          ...previous.filter(
            (item) => item.id !== session.id
          ),
        ]);

        setArchivedOpen(true);

        if (activeSessionId === session.id) {
          onActiveSessionDeleted?.();
        }
      }

    } catch (error) {
      console.error(
        "Archive/unarchive failed:",
        error
      );
    } finally {
      setBusyId(null);
    }
  };


  // ===================================================
  // OPEN MENU
  // ===================================================

  const openMenu = (event, session) => {

    const rect =
      event.currentTarget.getBoundingClientRect();

    const menuWidth = 190;
    const menuHeight = 210;

    let left = rect.right - menuWidth;
    let top = rect.bottom + 6;


    // Keep inside right edge

    if (
      left + menuWidth >
      window.innerWidth - 8
    ) {
      left =
        window.innerWidth -
        menuWidth -
        8;
    }


    // If no room below, place above

    if (
      top + menuHeight >
      window.innerHeight - 8
    ) {
      top =
        rect.top -
        menuHeight -
        6;
    }


    // Prevent negative positions

    left = Math.max(8, left);
    top = Math.max(8, top);


    setMenu({
      session,
      top,
      left,
    });
  };


  // ===================================================
  // CLOSE MENU WHEN CLICKING OUTSIDE
  // ===================================================

  useEffect(() => {

    if (!menu) return;


    const handleOutsideClick = (event) => {

      const clickedInsideMenu =
        event.target.closest(
          "[data-session-menu]"
        );

      const clickedTrigger =
        event.target.closest(
          "[data-session-menu-trigger]"
        );

      if (
        !clickedInsideMenu &&
        !clickedTrigger
      ) {
        setMenu(null);
      }
    };


    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );


    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };

  }, [menu]);


  // ===================================================
  // RENDER SESSION LIST
  // ===================================================

  const renderSessions = (list) => {

    if (!list.length) {
      return (
        <div className="px-4 py-3 text-[11px] text-[#55555A]">
          No conversations
        </div>
      );
    }

    return (
      <div className="space-y-1">
        {list.map((session) => (
          <SessionRow
            key={session.id}
            session={session}
            activeSessionId={activeSessionId}
            onSelect={onSelectSession}
            onMenu={openMenu}
            editingId={editingId}
            editingTitle={editingTitle}
            setEditingTitle={setEditingTitle}
            saveRename={saveRename}
            cancelEditing={cancelEditing}
            busy={busyId === session.id}
          />
        ))}
      </div>
    );
  };


  // ===================================================
  // RENDER
  // ===================================================

  return (
    <div className="flex min-h-0 flex-1 flex-col">

      {/* =============================================
          SCROLLABLE AREA
          ============================================= */}

      <div
        className="
          min-h-0
          flex-1
          overflow-y-auto
          overflow-x-hidden
          px-2
          pb-4
        "
        style={{
          scrollbarWidth: "thin",
          scrollbarColor: "#3A3A3E transparent",
        }}
      >

        {loading ? (

          <>
            <div className="px-2 pt-3 pb-2">
              <div className="h-2.5 w-16 rounded bg-[#1B1B1D] animate-pulse" />
            </div>

            <LoadingRow />
            <LoadingRow />
            <LoadingRow />
          </>

        ) : (

          <>

            {/* =====================================
                PINNED
                ===================================== */}

            <div className="mt-2">

              <SectionHeader
                title="PINNED"
                count={pinnedSessions.length}
                open={pinnedOpen}
                onClick={() =>
                  setPinnedOpen(
                    (value) => !value
                  )
                }
              />

              {pinnedOpen &&
                renderSessions(
                  pinnedSessions
                )}

            </div>


            {/* =====================================
                RECENTS
                ===================================== */}

            <div className="mt-2">

              <SectionHeader
                title="RECENTS"
                count={sessions.length}
                open={recentsOpen}
                onClick={() =>
                  setRecentsOpen(
                    (value) => !value
                  )
                }
              />

              {recentsOpen &&
                renderSessions(
                  sessions
                )}

            </div>


            {/* =====================================
                ARCHIVED
                ===================================== */}

            <div className="mt-2">

              <SectionHeader
                title="ARCHIVED"
                count={archivedSessions.length}
                open={archivedOpen}
                onClick={() =>
                  setArchivedOpen(
                    (value) => !value
                  )
                }
              />

              {archivedOpen &&
                renderSessions(
                  archivedSessions
                )}

            </div>

          </>
        )}

      </div>


      {/* =============================================
          THREE DOT POPUP
          ============================================= */}

      {menu && (
        <div
          data-session-menu
          className="
            fixed
            z-[9999]
            w-[190px]
            overflow-hidden
            rounded-xl
            border
            border-[#303034]
            bg-[#111113]
            py-1
            shadow-2xl
          "
          style={{
            top: `${menu.top}px`,
            left: `${menu.left}px`,
          }}
          onMouseDown={(event) =>
            event.stopPropagation()
          }
        >

          {/* PIN / UNPIN */}

          <button
            type="button"
            onClick={() =>
              handlePinToggle(
                menu.session
              )
            }
            className="
              flex w-full items-center
              gap-3 px-3 py-2.5
              text-left text-[13px]
              text-[#D0D0D4]
              hover:bg-[#1D1D20]
            "
          >
            <PinIcon />

            <span>
              {menu.session.is_pinned
                ? "Unpin"
                : "Pin"}
            </span>
          </button>


          {/* ARCHIVE / UNARCHIVE */}

          <button
            type="button"
            onClick={() =>
              handleArchiveToggle(
                menu.session
              )
            }
            className="
              flex w-full items-center
              gap-3 px-3 py-2.5
              text-left text-[13px]
              text-[#D0D0D4]
              hover:bg-[#1D1D20]
            "
          >
            <ArchiveIcon />

            <span>
              {menu.session.is_archived
                ? "Unarchive"
                : "Archive"}
            </span>
          </button>


          <div className="my-1 border-t border-[#29292C]" />


          {/* RENAME */}

          <button
            type="button"
            onClick={() =>
              startEditing(menu.session)
            }
            className="
              flex w-full items-center
              gap-3 px-3 py-2.5
              text-left text-[13px]
              text-[#D0D0D4]
              hover:bg-[#1D1D20]
            "
          >
            <EditIcon />

            <span>Rename</span>
          </button>


          {/* DELETE */}

          <button
            type="button"
            onClick={() =>
              handleDelete(
                menu.session
              )
            }
            className="
              flex w-full items-center
              gap-3 px-3 py-2.5
              text-left text-[13px]
              text-red-500
              hover:bg-red-500/10
            "
          >
            <TrashIcon />

            <span>Delete</span>
          </button>

        </div>
      )}

    </div>
  );
});


function LoadingRow() {
  return (
    <div className="px-3 py-2.5">
      <div className="h-3 w-32 rounded bg-[#1B1B1D] animate-pulse" />
      <div className="mt-2 h-2 w-12 rounded bg-[#151517] animate-pulse" />
    </div>
  );
}


export default RecentSessions;
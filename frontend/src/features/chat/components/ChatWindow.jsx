import { useCallback, useEffect, useRef, useState } from "react";
import { Compass, MapPinned, ShieldAlert, Waves } from "lucide-react";

import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import LocationPicker from "./LocationPicker";
import logo from "../../../assets/logo.png";

import {
  getChatHistory,
  sendMessage,
  resumeChat,
} from "../services/chathelp";

// ============================================================
// STATIC SUGGESTIONS
// These are frontend-only. No suggestions API is used.
// ============================================================

const SUGGESTIONS = [
  "What are today's fishing conditions?",
  "Show nearby PFZ locations",
  "Is it safe to fish tomorrow?",
  "Find a safer route for my voyage",
];

const SUGGESTION_ICONS = [
  Waves,
  MapPinned,
  ShieldAlert,
  Compass,
];

function makeUserMessage(content) {
  return {
    id: `user-${Date.now()}-${Math.random()}`,
    role: "user",
    content,
    response_data: null,
    created_at: new Date().toISOString(),
  };
}

function makePendingAssistantMessage() {
  return {
    id: `pending-${Date.now()}-${Math.random()}`,
    role: "assistant",
    content: "",
    response_data: null,
    pending_action: null,
    workflow_status: null,
    options: [],
    pending: true,
    created_at: new Date().toISOString(),
  };
}

export default function ChatWindow({ session }) {
  const sessionId = session?.id ?? null;

  // ============================================================
  // STATE
  // ============================================================

  const [messages, setMessages] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState(null);

  const [sending, setSending] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState(null);
  const [showLocationPicker, setShowLocationPicker] = useState(false);

  const bottomRef = useRef(null);
  const requestRef = useRef(0);

  // Synchronous lock: `sending` state is async (batched by React), so
  // two invocations of handleSend/handleLocationConfirm triggered in
  // the same tick (e.g. Enter + a queued click) could both read
  // `sending === false` before either commit. This ref is set/cleared
  // synchronously and is checked FIRST in both handlers, guaranteeing
  // one user action produces exactly one request. `sending` state is
  // kept as-is purely for rendering (disabling the composer, etc.).
  const sendingRef = useRef(false);

  // ============================================================
  // RESET INPUT / ERROR WHEN SESSION CHANGES
  //
  // BUG FIX: this used to mutate state during render —
  //   if (sessionId !== prevSessionId) { setPrevSessionId(...); ... }
  // — which is a React anti-pattern (relies on render being re-run
  // synchronously after a state update triggered mid-render). It
  // happened to work today because the resets are idempotent, but it
  // is not a safe pattern to build on. Moved to a real effect, keyed
  // on sessionId, with no API calls inside it.
  // ============================================================

  useEffect(() => {
    setError(null);
    setInputValue("");
    setShowLocationPicker(false);
  }, [sessionId]);

  // ============================================================
  // LOAD CHAT HISTORY
  // ============================================================

  const loadHistory = useCallback((id) => {
    const requestId = ++requestRef.current;

    Promise.resolve()
      .then(() => {
        if (requestRef.current !== requestId) return undefined;

        setHistoryLoading(true);
        setHistoryError(null);

        if (id == null) {
          return [];
        }

        return getChatHistory(id);
      })
      .then((history) => {
        if (
          requestRef.current !== requestId ||
          history === undefined
        ) {
          return;
        }

        setMessages(Array.isArray(history) ? history : []);
        setHistoryLoading(false);
      })
      .catch((err) => {
        if (requestRef.current !== requestId) return;

        setMessages([]);
        setHistoryError(
          err?.message ||
            "ORCA couldn't load this conversation."
        );
        setHistoryLoading(false);
      });
  }, []);

  useEffect(() => {
    loadHistory(sessionId);
  }, [sessionId, loadHistory]);

  // ============================================================
  // AUTO SCROLL
  // ============================================================

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, sending]);

  // ============================================================
  // SEND MESSAGE
  //
  // IMPORTANT:
  // Every user response is treated as a normal chat message.
  //
  // Example:
  //
  // ORCA:
  // "Please provide your current fishing location."
  //
  // User:
  // "Chennai"
  //
  // -> POST /chat
  // {
  //   session_id: 1,
  //   message: "Chennai"
  // }
  //
  // We DO NOT turn backend `options` into clickable buttons.
  // ============================================================

  // ============================================================
// PENDING WORKFLOW
// If ORCA is waiting for additional information, the next
// message typed by the user is sent through /resume.
// Backend options are NOT displayed as buttons.
// ============================================================

function parseLocationInput(text) {
  if (!text || typeof text !== "string") return null;
  const trimmed = text.trim();
  const match = trimmed.match(/^(-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)$/);
  if (match) {
    const lat = parseFloat(match[1]);
    const lon = parseFloat(match[2]);
    if (
      Number.isFinite(lat) &&
      Number.isFinite(lon) &&
      lat >= -90 &&
      lat <= 90 &&
      lon >= -180 &&
      lon <= 180
    ) {
      return {
        latitude: Number(lat.toFixed(6)),
        longitude: Number(lon.toFixed(6)),
      };
    }
  }
  return null;
}

const lastMessage = messages[messages.length - 1];

const pendingTurn =
  lastMessage &&
  lastMessage.role === "assistant" &&
  !lastMessage.pending &&
  lastMessage.workflow_status === "WAITING_FOR_USER"
    ? lastMessage
    : null;

  const handleSend = useCallback(
  async (text) => {
    if (!sessionId || sendingRef.current) return;

    const trimmed = text.trim();

    if (!trimmed) return;

    setError(null);

    let valueToSend = trimmed;
    if (pendingTurn && pendingTurn.pending_action === "location") {
      const parsed = parseLocationInput(trimmed);
      if (parsed) {
        valueToSend = parsed;
      } else if (/^[\d.\s,-]+$/.test(trimmed)) {
        setError({
          message:
            "Please enter valid coordinates (Latitude: -90 to 90, Longitude: -180 to 180).",
          action: null,
        });
        return;
      }
    }

    // Lock acquired here — after every early-return validation path,
    // right before we actually commit to making a request.
    sendingRef.current = true;

    setInputValue("");
    setSending(true);

    const userMessage = makeUserMessage(trimmed);
    const pendingAssistant = makePendingAssistantMessage();

    setMessages((previous) => [
      ...previous,
      userMessage,
      pendingAssistant,
    ]);

    try {
      let assistantMessage;

      if (pendingTurn) {
        // ORCA is waiting for an answer.
        // Send the user's value through /resume.
        assistantMessage = await resumeChat(
          sessionId,
          valueToSend
        );
      } else {
        // Normal conversation.
        assistantMessage = await sendMessage(
          sessionId,
          trimmed
        );
      }

      setMessages((previous) => {
        const withoutPlaceholder =
          previous.filter(
            (message) =>
              message.id !== pendingAssistant.id
          );

        return [
          ...withoutPlaceholder,
          assistantMessage,
        ];
      });
    } catch (err) {
      setMessages((previous) =>
        previous.filter(
          (message) =>
            message.id !== pendingAssistant.id
        )
      );

      setError({
        message:
          err?.message ||
          "ORCA couldn't complete that request.",
        action: {
          type: pendingTurn ? "resume" : "send",
          payload: valueToSend,
        },
      });
    } finally {
      sendingRef.current = false;
      setSending(false);
    }
  },
  [sessionId, pendingTurn]
);

  // ============================================================
  // LOCATION CONFIRMED
  //
  // When the user confirms their position in the LocationPicker,
  // this passes the location object { latitude, longitude } to /resume.
  // ============================================================

  const handleLocationConfirm = useCallback(
    async (location) => {
      setShowLocationPicker(false);

      if (!sessionId || sendingRef.current) return;

      const displayContent =
        typeof location === "object" &&
        location?.latitude != null &&
        location?.longitude != null
          ? `${Number(location.latitude).toFixed(6)}, ${Number(
              location.longitude
            ).toFixed(6)}`
          : String(location);

      if (pendingTurn) {
        sendingRef.current = true;
        setError(null);
        setSending(true);

        const userMessage = makeUserMessage(displayContent);
        const pendingAssistant = makePendingAssistantMessage();

        setMessages((previous) => [
          ...previous,
          userMessage,
          pendingAssistant,
        ]);

        try {
          const assistantMessage = await resumeChat(
            sessionId,
            location
          );

          setMessages((previous) => {
            const withoutPlaceholder = previous.filter(
              (message) => message.id !== pendingAssistant.id
            );
            return [...withoutPlaceholder, assistantMessage];
          });
        } catch (err) {
          setMessages((previous) =>
            previous.filter(
              (message) => message.id !== pendingAssistant.id
            )
          );

          setError({
            message:
              err?.message ||
              "ORCA couldn't complete that request.",
            action: {
              type: "resume",
              payload: location,
            },
          });
        } finally {
          sendingRef.current = false;
          setSending(false);
        }
      } else {
        handleSend(displayContent);
      }
    },
    [sessionId, pendingTurn, handleSend]
  );
  // ============================================================
  // RETRY
  // ============================================================

  const handleRetry = useCallback(() => {
    if (!error?.action) return;

    const { payload } = error.action;

    setError(null);

    handleSend(payload);
  }, [error, handleSend]);

  // ============================================================
  // SUGGESTION CLICK
  //
  // Suggestions only populate the input.
  // They are NOT directly sent to the backend.
  // ============================================================

  const handleSuggestionClick = useCallback(
    (text) => {
      setInputValue(text);
    },
    []
  );

  // ============================================================
  // RETRY HISTORY
  // ============================================================

  const handleRetryHistory = useCallback(() => {
    loadHistory(sessionId);
  }, [sessionId, loadHistory]);

  // ============================================================
  // NO ACTIVE SESSION
  //
  // Keep the composer visible.
  // It is disabled because /chat requires session_id.
  // ============================================================

  if (!session) {
  return (
    <div className="flex h-full min-h-0 w-full flex-1 flex-col overflow-hidden bg-[#080809]">
      <main className="flex min-h-0 flex-1 items-center justify-center px-6">
        <div className="flex max-w-[560px] flex-col items-center text-center">

          {/* ORCA Logo */}
          <img
            src={logo}
            alt="ORCA"
            className="h-28 w-28 object-contain"
          />

          {/* ORCA Name */}
          <h1 className="mt-5 font-display text-3xl font-semibold tracking-[0.35em] text-white sm:text-4xl">
            O R C A
          </h1>

          {/* Tagline */}
          <p className="mt-3 text-sm text-[#9A9A9A] sm:text-base">
            Marine intelligence, in conversation.
          </p>

          {/* Description */}
          <p className="mt-6 max-w-[500px] text-sm leading-7 text-[#77777D] sm:text-[15px]">
            ORCA is your intelligent marine assistant for understanding
            fishing conditions, Potential Fishing Zones, marine safety,
            weather, and voyage planning.
          </p>

          {/* Instruction */}
          <p className="mt-8 text-sm text-[#9A9A9A]">
            Click{" "}
            <span className="font-medium text-white">
              + New chat
            </span>{" "}
            in the sidebar to start a conversation with ORCA.
          </p>

        </div>
      </main>
    </div>
  );
}

  const showEmptyState =
    !historyLoading &&
    !historyError &&
    messages.length === 0;

  // ============================================================
  // MAIN CHAT UI
  // ============================================================

  return (
    <>
    <div className="flex h-full min-h-0 w-full flex-1 flex-col overflow-hidden bg-[#080809]">

      {/* ======================================================
          MESSAGE AREA
      ====================================================== */}

      <main className="min-h-0 flex-1 overflow-y-auto">

        {historyLoading ? (
          <div className="flex h-full items-center justify-center">
            <div
              className="flex items-center gap-1.5"
              role="status"
              aria-label="Loading conversation"
            >
              {[0, 1, 2].map((index) => (
                <span
                  key={index}
                  className="h-1.5 w-1.5 rounded-full bg-[#5C5C5C]"
                  style={{
                    animation:
                      "pulseDot 1.2s ease-in-out infinite",
                    animationDelay:
                      `${index * 0.15}s`,
                  }}
                />
              ))}
            </div>
          </div>
        ) : historyError ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 px-6 text-center">

            <p className="text-sm text-[#9A9A9A]">
              {historyError}
            </p>

            <button
              type="button"
              onClick={handleRetryHistory}
              className="text-xs font-medium text-[#3DA7B7] transition-colors hover:text-white"
            >
              Try again
            </button>

          </div>
        ) : showEmptyState ? (
          <EmptyState
            suggestions={SUGGESTIONS}
            onSuggestionClick={handleSuggestionClick}
          />
        ) : (
          <div className="mx-auto flex w-full max-w-[720px] flex-col gap-6 px-6 py-8">

            {messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message}
                isLatest={
                  index === messages.length - 1
                }
                onRequestLocation={() =>
                  setShowLocationPicker(true)
                }
              />
            ))}

            <div ref={bottomRef} />

          </div>
        )}

      </main>

      {/* ======================================================
          COMPOSER
      ====================================================== */}

      <footer className="shrink-0 border-t border-[#202023] bg-[#080809] px-4 pb-4 pt-3 lg:px-7">

        <div className="mx-auto w-full max-w-[720px]">

          {/* Error */}
          {error && (
            <div className="mb-3 flex items-center justify-between gap-3 rounded-xl border border-[#2A2A2E] bg-[#0F0F0F] px-4 py-2.5">

              <span className="text-xs text-[#9A9A9A]">
                {error.message}
              </span>

              <button
                type="button"
                onClick={handleRetry}
                disabled={sending}
                className="shrink-0 text-xs font-medium text-[#3DA7B7] transition-colors hover:text-white disabled:opacity-50"
              >
                Try again
              </button>

            </div>
          )}

          <ChatInput
            value={inputValue}
            onChange={setInputValue}
            onSend={handleSend}
            onLocationClick={() => setShowLocationPicker(true)}
            disabled={sending || historyLoading}
            placeholder="Ask ORCA about ocean, weather, PFZ, risk, or routes..."
          />

          <p className="mt-2 text-center text-[10px] text-[#4F4F55]">
            ORCA responses are generated from the connected marine intelligence backend.
          </p>

        </div>

      </footer>

    </div>

      {/* Location Picker Modal */}
      {showLocationPicker && (
        <LocationPicker
          onConfirm={handleLocationConfirm}
          onClose={() => setShowLocationPicker(false)}
        />
      )}
    </>
  );
}

// ============================================================
// EMPTY STATE
// ============================================================

function EmptyState({
  suggestions,
  onSuggestionClick,
}) {
  return (
    <div className="flex h-full min-h-[420px] flex-col items-center justify-center px-6 text-center">

      <div className="flex items-center justify-center gap-3">

        <img
          src={logo}
          alt=""
          aria-hidden="true"
          className="h-16 w-16 shrink-0 object-contain"
        />

        <h1 className="font-display text-2xl font-semibold tracking-tightest text-white sm:text-3xl">
          O R C A
        </h1>

      </div>

      <p className="mt-2 text-sm text-[#9A9A9A]">
        Marine intelligence, in conversation.
      </p>

      {suggestions.length > 0 && (
        <div className="mt-10 grid w-full max-w-[560px] grid-cols-1 gap-2.5 sm:grid-cols-2">

          {suggestions.map((prompt, index) => {
            const Icon =
              SUGGESTION_ICONS[
                index %
                  SUGGESTION_ICONS.length
              ];

            return (
              <button
                key={prompt}
                type="button"
                onClick={() =>
                  onSuggestionClick(prompt)
                }
                className="flex items-center gap-2.5 rounded-xl border border-[#202023] bg-[#0F0F0F] px-4 py-3 text-left text-sm text-[#9A9A9A] transition-colors duration-200 hover:border-[#303035] hover:bg-[#161616] hover:text-white"
              >

                <Icon
                  size={15}
                  className="shrink-0 text-[#3DA7B7]"
                  aria-hidden="true"
                />

                <span>{prompt}</span>

              </button>
            );
          })}

        </div>
      )}

    </div>
  );
}
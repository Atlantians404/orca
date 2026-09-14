<<<<<<< HEAD
import { useEffect, useRef, useState } from "react";
import {
  getChatHistory,
  sendChatMessage,
  resumeChat,
} from "../services/chatApi";

import orcaLogo from "../../../assets/log.png";


// =====================================================
// STATIC SUGGESTIONS
// No backend endpoint is used for these.
// =====================================================

const SUGGESTIONS = [
  "What are the current marine conditions?",
  "Show me safe fishing areas.",
  "Analyze the weather conditions.",
  "What risks should I be aware of?",
];


// =====================================================
// HELPERS
// =====================================================

const normalizeHistoryMessage = (item) => ({
  id: item.id,
  role:
    item.role?.toLowerCase() === "user"
      ? "user"
      : "assistant",
  content: item.content || "",
  response_data: item.response_data ?? null,
});


const buildAssistantMessage = (response) => ({
  id: `assistant-${Date.now()}`,
  role: "assistant",
  content: response.message || "",
  response_data: response.response_data ?? null,
  pending_action: response.pending_action ?? null,
  workflow_status: response.workflow_status ?? null,
  options: Array.isArray(response.options)
    ? response.options
    : [],
});


export default function ChatWindow({ session }) {

  // ===================================================
  // STATE
  // ===================================================

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const [loadingHistory, setLoadingHistory] =
    useState(false);

  const [sending, setSending] =
    useState(false);

  const [resuming, setResuming] =
    useState(false);

  const [error, setError] =
    useState("");

  const [pendingAction, setPendingAction] =
    useState(null);

  const [pendingOptions, setPendingOptions] =
    useState([]);

  const [resumeInput, setResumeInput] =
    useState("");

  const messagesEndRef = useRef(null);


  // ===================================================
  // LOAD HISTORY WHEN SESSION CHANGES
  // ===================================================

  useEffect(() => {

    if (!session?.id) {
      setMessages([]);
      setPendingAction(null);
      setPendingOptions([]);
      setError("");
      return;
    }

    let cancelled = false;

    const loadHistory = async () => {

      setLoadingHistory(true);
      setError("");

      try {

        const history =
          await getChatHistory(session.id);

        if (cancelled) {
          return;
        }

        const normalized =
          Array.isArray(history)
            ? history.map(
                normalizeHistoryMessage
              )
            : [];

        setMessages(normalized);

      } catch (err) {

        if (!cancelled) {

          setError(
            err?.response?.data?.detail ||
            "Unable to load conversation history."
          );
        }

      } finally {

        if (!cancelled) {
          setLoadingHistory(false);
        }
      }
    };


    loadHistory();

    return () => {
      cancelled = true;
    };

  }, [session?.id]);


  // ===================================================
  // AUTO SCROLL
  // ===================================================

  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [
    messages,
    sending,
    resuming,
  ]);


  // ===================================================
  // SEND NORMAL CHAT MESSAGE
  // ===================================================

  const handleSend = async (
    messageOverride = null
  ) => {

    const text =
      (
        messageOverride ??
        input
      ).trim();

    if (!text || !session?.id || sending) {
      return;
    }

    setError("");

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      response_data: null,
    };

    // Show user's message immediately.
    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setInput("");

    setSending(true);

    try {

      const response =
        await sendChatMessage(
          session.id,
          text
        );

      const assistantMessage =
        buildAssistantMessage(response);

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);


      // -----------------------------------------------
      // Pending workflow
      // -----------------------------------------------

      if (
        response.pending_action ||
        response.workflow_status ||
        (
          Array.isArray(response.options) &&
          response.options.length > 0
        )
      ) {

        setPendingAction(
          response.pending_action ?? null
        );

        setPendingOptions(
          Array.isArray(response.options)
            ? response.options
            : []
        );
      } else {

        setPendingAction(null);
        setPendingOptions([]);
      }

    } catch (err) {

      setError(
        err?.response?.data?.detail ||
        "Unable to send message."
      );

    } finally {

      setSending(false);
    }
  };


  // ===================================================
  // RESUME PENDING WORKFLOW
  // ===================================================

  const handleResume = async (
    value
  ) => {

    if (
      !session?.id ||
      resuming
    ) {
      return;
    }

    if (
      value === null ||
      value === undefined ||
      String(value).trim() === ""
    ) {
      return;
    }

    setError("");
    setResuming(true);

    try {

      const response =
        await resumeChat(
          session.id,
          value
        );

      const assistantMessage =
        buildAssistantMessage(response);

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);


      if (
        response.pending_action ||
        response.workflow_status ||
        (
          Array.isArray(response.options) &&
          response.options.length > 0
        )
      ) {

        setPendingAction(
          response.pending_action ?? null
        );

        setPendingOptions(
          Array.isArray(response.options)
            ? response.options
            : []
        );

      } else {

        setPendingAction(null);
        setPendingOptions([]);
      }

      setResumeInput("");

    } catch (err) {

      setError(
        err?.response?.data?.detail ||
        "Unable to resume the conversation."
      );

    } finally {

      setResuming(false);
    }
  };


  // ===================================================
  // ENTER KEY
  // ===================================================

  const handleKeyDown = (event) => {

    if (event.key === "Enter" && !event.shiftKey) {

      event.preventDefault();

      handleSend();
    }
  };


  // ===================================================
  // EMPTY SESSION
  // ===================================================

=======
/**
 * ChatWindow
 *
 * Placeholder only. Per the task scope, the full chatbot UI (message list,
 * streaming, etc.) is a LATER step — this just proves the active session
 * is flowing through correctly from ChatPage -> RecentSessions selection.
 *
 * Wire up real message rendering + ChatInput here once CRUD is confirmed
 * working end-to-end.
 */
export default function ChatWindow({ session }) {
>>>>>>> origin/main
  if (!session) {

    return (
<<<<<<< HEAD
      <div
        className="
          flex
          h-full
          flex-col
          items-center
          justify-center
          bg-[#080809]
          px-6
          text-center
        "
      >

        <img
          src={orcaLogo}
          alt="ORCA"
          className="
            mb-5
            h-16
            w-16
            object-contain
          "
        />

        <h1
          className="
            text-2xl
            font-semibold
            tracking-tight
            text-white
          "
        >
          ORCA
        </h1>

        <p
          className="
            mt-2
            text-sm
            text-[#77777C]
          "
        >
          Marine intelligence, in conversation.
        </p>


        {/* Suggestion cards */}

        <div
          className="
            mt-8
            grid
            w-full
            max-w-2xl
            grid-cols-1
            gap-3
            sm:grid-cols-2
          "
        >

          {SUGGESTIONS.map(
            (suggestion) => (

              <button
                key={suggestion}
                type="button"
                onClick={() =>
                  setInput(suggestion)
                }

                className="
                  rounded-xl
                  border
                  border-white/10
                  bg-[#111113]
                  px-4
                  py-4
                  text-left
                  text-sm
                  text-[#B8B8BE]

                  transition

                  hover:border-white/20
                  hover:bg-[#171719]
                  hover:text-white
                "
              >
                {suggestion}
              </button>

            )
          )}

        </div>


        {/* Input */}

        <div
          className="
            mt-5
            flex
            w-full
            max-w-2xl
            items-end
            gap-2
            rounded-xl
            border
            border-white/10
            bg-[#111113]
            p-2
          "
        >

          <textarea
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}

            placeholder="Ask ORCA anything about the marine environment..."

            rows={1}

            className="
              min-h-[44px]
              flex-1
              resize-none
              bg-transparent
              px-3
              py-3
              text-sm
              text-white
              outline-none
              placeholder:text-[#5F5F65]
            "
          />

          <button
            type="button"
            onClick={() =>
              handleSend()
            }

            disabled={
              !input.trim() ||
              sending
            }

            className="
              rounded-lg
              bg-white
              px-4
              py-2.5
              text-sm
              font-medium
              text-black

              transition

              hover:bg-[#E8E8E8]

              disabled:cursor-not-allowed
              disabled:opacity-40
            "
          >
            Send
          </button>

        </div>

=======
      <div className="flex items-center justify-center h-full text-gray-400 text-sm">
        Select a conversation or start a new one.
>>>>>>> origin/main
      </div>
    );
  }

<<<<<<< HEAD

  // ===================================================
  // MAIN CHAT UI
  // ===================================================

  return (
    <div
      className="
        flex
        h-full
        flex-col
        bg-[#080809]
      "
    >

      {/* =================================================
          CHAT HEADER
          ================================================= */}

      <header
        className="
          flex
          h-[64px]
          shrink-0
          items-center
          border-b
          border-[#202023]
          px-6
        "
      >

        <div className="min-w-0">

          <h1
            className="
              truncate
              text-sm
              font-medium
              text-white
            "
          >
            {session.title || "Conversation"}
          </h1>

          <p
            className="
              mt-0.5
              text-[11px]
              text-[#66666C]
            "
          >
            Conversation
          </p>

        </div>

      </header>


      {/* =================================================
          MESSAGE AREA
          ================================================= */}

      <div
        className="
          min-h-0
          flex-1
          overflow-y-auto
          px-4
          py-6
        "
      >

        {loadingHistory ? (

          <div
            className="
              flex
              h-full
              items-center
              justify-center
              text-sm
              text-[#77777C]
            "
          >
            Loading conversation...
          </div>

        ) : messages.length === 0 ? (

          <div
            className="
              flex
              h-full
              flex-col
              items-center
              justify-center
              text-center
            "
          >

            <img
              src={orcaLogo}
              alt="ORCA"
              className="
                h-14
                w-14
                object-contain
              "
            />

            <p
              className="
                mt-4
                text-sm
                text-[#77777C]
              "
            >
              Start the conversation.
            </p>

          </div>

        ) : (

          <div
            className="
              mx-auto
              flex
              w-full
              max-w-4xl
              flex-col
              gap-5
            "
          >

            {messages.map(
              (message) => (

                <div
                  key={message.id}
                  className={`
                    flex
                    ${
                      message.role === "user"
                        ? "justify-end"
                        : "justify-start"
                    }
                  `}
                >

                  <div
                    className={`
                      max-w-[80%]
                      rounded-2xl
                      px-4
                      py-3
                      text-sm
                      leading-6

                      ${
                        message.role === "user"
                          ? "bg-[#1B1B1D] text-white"
                          : "border border-white/10 bg-[#111113] text-[#D5D5D9]"
                      }
                    `}
                  >

                    <div className="whitespace-pre-wrap">
                      {message.content}
                    </div>


                    {/* response_data.message */}

                    {message.response_data?.message && (
                      <div
                        className="
                          mt-3
                          border-t
                          border-white/10
                          pt-3
                          text-sm
                          text-[#B8B8BE]
                        "
                      >
                        {message.response_data.message}
                      </div>
                    )}


                    {/* Preserve map coordinates */}

                    {message.response_data?.map?.coordinates && (

                      <div
                        className="
                          mt-3
                          rounded-lg
                          border
                          border-white/10
                          bg-black/20
                          px-3
                          py-2
                          text-xs
                          text-[#85858B]
                        "
                      >

                        Map coordinates received:

                        <pre
                          className="
                            mt-1
                            whitespace-pre-wrap
                            text-[#AFAFB5]
                          "
                        >
                          {JSON.stringify(
                            message.response_data.map.coordinates,
                            null,
                            2
                          )}
                        </pre>

                      </div>

                    )}

                  </div>

                </div>

              )
            )}


            <div
              ref={messagesEndRef}
            />

          </div>

        )}

      </div>


      {/* =================================================
          ERROR
          ================================================= */}

      {error && (

        <div
          className="
            shrink-0
            border-t
            border-red-500/10
            bg-red-500/5
            px-6
            py-2
            text-center
            text-xs
            text-red-400
          "
        >
          {error}
        </div>

      )}


      {/* =================================================
          PENDING WORKFLOW
          ================================================= */}

      {(pendingAction ||
        pendingOptions.length > 0) && (

        <div
          className="
            shrink-0
            border-t
            border-white/10
            bg-[#0D0D0F]
            px-4
            py-4
          "
        >

          <div
            className="
              mx-auto
              w-full
              max-w-4xl
            "
          >

            {pendingAction && (

              <p
                className="
                  mb-3
                  text-sm
                  text-[#D0D0D5]
                "
              >
                {pendingAction}
              </p>

            )}


            {pendingOptions.length > 0 && (

              <div
                className="
                  flex
                  flex-wrap
                  gap-2
                "
              >

                {pendingOptions.map(
                  (option, index) => {

                    const value =
                      typeof option === "object"
                        ? option.value ??
                          option.label ??
                          JSON.stringify(option)
                        : option;

                    const label =
                      typeof option === "object"
                        ? option.label ??
                          option.value ??
                          JSON.stringify(option)
                        : option;

                    return (
                      <button
                        key={`${label}-${index}`}
                        type="button"
                        disabled={resuming}

                        onClick={() =>
                          handleResume(value)
                        }

                        className="
                          rounded-lg
                          border
                          border-white/10
                          bg-[#171719]
                          px-4
                          py-2
                          text-sm
                          text-white

                          transition

                          hover:bg-[#202023]

                          disabled:opacity-40
                        "
                      >
                        {label}
                      </button>
                    );
                  }
                )}

              </div>

            )}


            {/* Free-text resume */}

            <div
              className="
                mt-3
                flex
                gap-2
              "
            >

              <input
                value={resumeInput}
                onChange={(event) =>
                  setResumeInput(
                    event.target.value
                  )
                }

                onKeyDown={(event) => {

                  if (
                    event.key === "Enter"
                  ) {

                    handleResume(
                      resumeInput
                    );
                  }
                }}

                placeholder="Enter another value..."

                className="
                  min-w-0
                  flex-1
                  rounded-lg
                  border
                  border-white/10
                  bg-[#111113]
                  px-3
                  py-2
                  text-sm
                  text-white
                  outline-none

                  placeholder:text-[#5F5F65]

                  focus:border-white/20
                "
              />

              <button
                type="button"
                disabled={
                  !resumeInput.trim() ||
                  resuming
                }

                onClick={() =>
                  handleResume(
                    resumeInput
                  )
                }

                className="
                  rounded-lg
                  bg-white
                  px-4
                  py-2
                  text-sm
                  font-medium
                  text-black

                  disabled:cursor-not-allowed
                  disabled:opacity-40
                "
              >
                {resuming
                  ? "Sending..."
                  : "Continue"}
              </button>

            </div>

          </div>

        </div>

      )}


      {/* =================================================
          NORMAL CHAT INPUT
          ================================================= */}

      <div
        className="
          shrink-0
          border-t
          border-[#202023]
          bg-[#080809]
          px-4
          py-4
        "
      >

        <div
          className="
            mx-auto
            flex
            w-full
            max-w-4xl
            items-end
            gap-2
            rounded-xl
            border
            border-white/10
            bg-[#111113]
            p-2
          "
        >

          <textarea
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }

            onKeyDown={handleKeyDown}

            placeholder="Message ORCA..."

            rows={1}

            disabled={sending}

            className="
              min-h-[44px]
              flex-1
              resize-none
              bg-transparent
              px-3
              py-3
              text-sm
              text-white
              outline-none
              placeholder:text-[#5F5F65]
            "
          />

          <button
            type="button"
            onClick={() =>
              handleSend()
            }

            disabled={
              !input.trim() ||
              sending
            }

            className="
              rounded-lg
              bg-white
              px-4
              py-2.5
              text-sm
              font-medium
              text-black

              transition

              hover:bg-[#E8E8E8]

              disabled:cursor-not-allowed
              disabled:opacity-40
            "
          >
            {sending
              ? "Sending..."
              : "Send"}
          </button>

        </div>

        <p
          className="
            mx-auto
            mt-2
            max-w-4xl
            px-1
            text-[10px]
            text-[#4F4F55]
          "
        >
          ORCA uses the selected conversation session.
        </p>

      </div>

=======
  return (
    <div className="p-4">
      <h1 className="text-lg font-semibold text-gray-800">{session.title}</h1>
      <p className="text-xs text-gray-400 mt-1">Session ID: {session.id}</p>
      <p className="text-sm text-gray-500 mt-4">
        (Message history rendering not yet implemented — this is the CRUD
        wiring step.)
      </p>
>>>>>>> origin/main
    </div>
  );
}
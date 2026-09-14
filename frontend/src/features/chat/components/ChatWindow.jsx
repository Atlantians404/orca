import { useCallback, useEffect, useRef, useState } from "react";
import { Compass, MapPinned, ShieldAlert, Waves } from "lucide-react";
import ChatMessage from "./ChatMessage";
import logo from "../../../assets/logo.png";
import ChatInput from "./ChatInput";
import {
  getChatHistory,
  sendMessage,
  editMessage,
  regenerateMessage,
  sendFeedback,
  getSuggestions,
} from "../services/chathelp";

const SUGGESTION_ICONS = [Waves, MapPinned, ShieldAlert, Compass];

export default function ChatWindow({ session }) {
  const sessionId = session?.id ?? null;

  const [messages, setMessages] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [regeneratingId, setRegeneratingId] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState(null);

  const bottomRef = useRef(null);

  useEffect(() => {
    if (sessionId == null) {
      setMessages([]);
      setHistoryLoading(false);
      return;
    }

    let cancelled = false;
    setHistoryLoading(true);
    setError(null);
    setEditingId(null);
    setRegeneratingId(null);
    setInputValue("");

    getChatHistory(sessionId).then((history) => {
      if (cancelled) return;
      setMessages(history);
      setHistoryLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  useEffect(() => {
    let cancelled = false;
    getSuggestions().then((items) => {
      if (!cancelled) setSuggestions(items);
    });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, sending]);

  const handleSend = useCallback(
    async (text) => {
      setError(null);
      setInputValue("");
      setSending(true);

      const userMessage = {
        id: `pending-user-${Date.now()}`,
        role: "user",
        content: text,
        response_data: null,
        created_at: new Date().toISOString(),
      };
      const pendingAssistant = {
        id: `pending-assistant-${Date.now()}`,
        role: "assistant",
        content: "",
        response_data: null,
        created_at: null,
        pending: true,
      };
      setMessages((prev) => [...prev, userMessage, pendingAssistant]);

      try {
        const assistantMessage = await sendMessage(sessionId, text);
        setMessages((prev) => {
          const withoutPlaceholder = prev.filter((m) => m.id !== pendingAssistant.id);
          return [...withoutPlaceholder, assistantMessage];
        });
      } catch (err) {
        setMessages((prev) => prev.filter((m) => m.id !== pendingAssistant.id));
        setError({
          message: err?.message || "ORCA couldn't complete that request.",
          retry: () => handleSend(text),
        });
      } finally {
        setSending(false);
      }
    },
    [sessionId]
  );

  const handleSuggestionClick = useCallback((text) => {
    setInputValue(text);
  }, []);

  const handleStartEdit = useCallback((id) => setEditingId(id), []);
  const handleCancelEdit = useCallback(() => setEditingId(null), []);

  const handleSubmitEdit = useCallback(
    async (id, newContent) => {
      setError(null);
      setEditingId(null);

      setMessages((prev) => {
        const index = prev.findIndex((m) => m.id === id);
        if (index === -1) return prev;
        const edited = { ...prev[index], content: newContent };
        return [
          ...prev.slice(0, index),
          edited,
          {
            id: `pending-assistant-${Date.now()}`,
            role: "assistant",
            content: "",
            response_data: null,
            created_at: null,
            pending: true,
          },
        ];
      });

      try {
        const { messages: updated } = await editMessage(sessionId, id, newContent);
        setMessages(updated);
      } catch (err) {
        setError({
          message: err?.message || "ORCA couldn't complete that request.",
          retry: () => handleSubmitEdit(id, newContent),
        });
        const history = await getChatHistory(sessionId);
        setMessages(history);
      }
    },
    [sessionId]
  );

  const handleRegenerate = useCallback(
    async (id) => {
      setError(null);
      setRegeneratingId(id);
      try {
        const regenerated = await regenerateMessage(sessionId, id);
        setMessages((prev) => prev.map((m) => (m.id === id ? regenerated : m)));
      } catch (err) {
        setError({
          message: err?.message || "ORCA couldn't complete that request.",
          retry: () => handleRegenerate(id),
        });
      } finally {
        setRegeneratingId(null);
      }
    },
    [sessionId]
  );

  const handleFeedback = useCallback(
    (id, type) => {
      setMessages((prev) =>
        prev.map((m) => (m.id === id ? { ...m, feedback: m.feedback === type ? null : type } : m))
      );
      const current = messages.find((m) => m.id === id);
      const nextFeedback = current?.feedback === type ? null : type;
      if (nextFeedback) {
        sendFeedback(sessionId, id, nextFeedback).catch(() => {});
      }
    },
    [messages, sessionId]
  );

  if (!session) {
    return (
      <div className="flex h-full items-center justify-center px-6 text-center">
        <p className="text-sm text-mute">Select a conversation or start a new one.</p>
      </div>
    );
  }

  const showEmptyState = !historyLoading && messages.length === 0;

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto">
        {historyLoading ? (
          <div className="flex h-full items-center justify-center">
            <div className="flex items-center gap-1.5" role="status" aria-label="Loading conversation">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="h-1.5 w-1.5 rounded-full bg-mute2"
                  style={{ animation: "pulseDot 1.2s ease-in-out infinite", animationDelay: `${i * 0.15}s` }}
                />
              ))}
            </div>
          </div>
        ) : showEmptyState ? (
          <EmptyState suggestions={suggestions} onSuggestionClick={handleSuggestionClick} />
        ) : (
          <div className="mx-auto flex max-w-[720px] flex-col gap-6 px-6 py-8">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                isEditing={editingId === message.id}
                isRegenerating={regeneratingId === message.id}
                onStartEdit={handleStartEdit}
                onCancelEdit={handleCancelEdit}
                onSubmitEdit={handleSubmitEdit}
                onRegenerate={handleRegenerate}
                onFeedback={handleFeedback}
              />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <div className="mx-auto w-full max-w-[720px] px-6 pb-6 pt-2">
        {error && (
          <div className="mb-3 flex items-center justify-between gap-3 rounded-xl border border-line bg-surface px-4 py-2.5">
            <span className="text-xs text-mute">{error.message}</span>
            <button
              type="button"
              onClick={error.retry}
              className="shrink-0 text-xs font-medium text-[#3DA7B7] hover:text-ink transition-colors"
            >
              Try again
            </button>
          </div>
        )}
        <ChatInput value={inputValue} onChange={setInputValue} onSend={handleSend} disabled={sending || historyLoading} />
      </div>
    </div>
  );
}

function EmptyState({ suggestions, onSuggestionClick }) {
  return (
    <div className="flex h-full flex-col items-center justify-center px-6 text-center">
      <div className="flex items-center justify-center gap-3">
  <img
    src={logo}
    alt=""
    aria-hidden="true"
    className="h-10 w-10 object-contain shrink-0"
  />
  <h1 className="font-display text-2xl font-semibold tracking-tightest text-ink sm:text-3xl">
    O R C A
  </h1>
</div>
      <p className="mt-2 text-sm text-mute">Marine intelligence, in conversation.</p>

      {suggestions.length > 0 && (
        <div className="mt-10 grid w-full max-w-[560px] grid-cols-1 gap-2.5 sm:grid-cols-2">
          {suggestions.map((prompt, i) => {
            const Icon = SUGGESTION_ICONS[i % SUGGESTION_ICONS.length];
            return (
              <button
                key={prompt}
                type="button"
                onClick={() => onSuggestionClick(prompt)}
                className="flex items-center gap-2.5 rounded-xl border border-line bg-surface px-4 py-3 text-left text-sm text-mute transition-colors duration-200 hover:border-line2 hover:bg-surface2 hover:text-ink"
              >
                <Icon size={15} className="shrink-0 text-[#3DA7B7]" aria-hidden="true" />
                <span>{prompt}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
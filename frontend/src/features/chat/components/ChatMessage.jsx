import { useEffect, useRef, useState } from "react";
import { Pencil, RotateCcw, ThumbsDown, ThumbsUp, X, Check } from "lucide-react";
import logo from "../../../assets/logo.png";

export default function ChatMessage({
  message,
  isEditing = false,
  isRegenerating = false,
  onStartEdit,
  onCancelEdit,
  onSubmitEdit,
  onRegenerate,
  onFeedback,
}) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <UserTurn
        message={message}
        isEditing={isEditing}
        onStartEdit={onStartEdit}
        onCancelEdit={onCancelEdit}
        onSubmitEdit={onSubmitEdit}
      />
    );
  }

  return (
    <AssistantTurn
      message={message}
      isRegenerating={isRegenerating}
      onRegenerate={onRegenerate}
      onFeedback={onFeedback}
    />
  );
}

function formatTime(iso) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

function autoResize(el) {
  if (!el) return;
  el.style.height = "auto";
  el.style.height = `${el.scrollHeight}px`;
}

function UserTurn({ message, isEditing, onStartEdit, onCancelEdit, onSubmitEdit }) {
  const [draft, setDraft] = useState(message.content);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (isEditing) {
      setDraft(message.content);
      requestAnimationFrame(() => {
        autoResize(textareaRef.current);
        textareaRef.current?.focus();
        textareaRef.current?.setSelectionRange(
          textareaRef.current.value.length,
          textareaRef.current.value.length
        );
      });
    }
  }, [isEditing, message.content]);

  function submit() {
    const trimmed = draft.trim();
    if (!trimmed || trimmed === message.content) {
      onCancelEdit();
      return;
    }
    onSubmitEdit(message.id, trimmed);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    } else if (e.key === "Escape") {
      onCancelEdit();
    }
  }

  return (
    <div className="group flex flex-col items-end">
      {isEditing ? (
        <div className="w-full max-w-[min(85%,640px)]">
          <textarea
            ref={textareaRef}
            value={draft}
            onChange={(e) => {
              setDraft(e.target.value);
              autoResize(e.target);
            }}
            onKeyDown={handleKeyDown}
            rows={1}
            aria-label="Edit message"
            className="w-full resize-none rounded-2xl border border-[#3DA7B7]/40 bg-surface2 px-4 py-3 text-sm text-ink leading-relaxed outline-none focus:border-[#3DA7B7] focus:ring-1 focus:ring-[#3DA7B7]/40 transition-colors"
          />
          <div className="mt-2 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onCancelEdit}
              className="inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-xs text-mute hover:text-ink hover:bg-white/5 transition-colors"
            >
              <X size={13} aria-hidden="true" />
              Cancel
            </button>
            <button
              type="button"
              onClick={submit}
              className="inline-flex items-center gap-1 rounded-full bg-ink px-3 py-1.5 text-xs font-medium text-void hover:bg-white/90 transition-colors"
            >
              <Check size={13} aria-hidden="true" />
              Save & send
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="max-w-[min(85%,640px)] rounded-2xl border border-line bg-surface2 px-4 py-3 text-sm leading-relaxed text-ink">
            {message.content}
          </div>
          <div className="mt-1.5 flex items-center gap-3 pr-1 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
            <span className="text-[11px] text-mute2">{formatTime(message.created_at)}</span>
            <button
              type="button"
              onClick={() => onStartEdit(message.id)}
              aria-label="Edit message"
              className="inline-flex items-center gap-1 text-[11px] text-mute hover:text-ink transition-colors"
            >
              <Pencil size={12} aria-hidden="true" />
              Edit
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function AssistantTurn({ message, isRegenerating, onRegenerate, onFeedback }) {
  const busy = message.pending || isRegenerating;

  return (
    <div className="group flex items-start gap-3">
      <img
        src={logo}
        alt=""
        aria-hidden="true"
        className="mt-0.5 h-6 w-6 shrink-0 rounded-full object-contain"
      />
      <div className="min-w-0 flex-1">
        {busy ? (
          <ThinkingDots />
        ) : (
          <>
            <p className="text-sm leading-relaxed text-ink/90 whitespace-pre-wrap">
              {message.content}
            </p>

            {message.response_data && <StructuredDataPanel data={message.response_data} />}

            <div className="mt-2 flex items-center gap-3">
              <span className="text-[11px] text-mute2">{formatTime(message.created_at)}</span>

              <div className="flex items-center gap-1 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
                <button
                  type="button"
                  onClick={() => onRegenerate(message.id)}
                  aria-label="Regenerate response"
                  title="Regenerate"
                  className="rounded-full p-1.5 text-mute hover:text-ink hover:bg-white/5 transition-colors"
                >
                  <RotateCcw size={13} aria-hidden="true" />
                </button>
                <button
                  type="button"
                  onClick={() => onFeedback(message.id, "positive")}
                  aria-label="Good response"
                  aria-pressed={message.feedback === "positive"}
                  title="Good response"
                  className={`rounded-full p-1.5 transition-colors hover:bg-white/5 ${
                    message.feedback === "positive" ? "text-[#3DA7B7]" : "text-mute hover:text-ink"
                  }`}
                >
                  <ThumbsUp size={13} aria-hidden="true" />
                </button>
                <button
                  type="button"
                  onClick={() => onFeedback(message.id, "negative")}
                  aria-label="Poor response"
                  aria-pressed={message.feedback === "negative"}
                  title="Poor response"
                  className={`rounded-full p-1.5 transition-colors hover:bg-white/5 ${
                    message.feedback === "negative" ? "text-[#3DA7B7]" : "text-mute hover:text-ink"
                  }`}
                >
                  <ThumbsDown size={13} aria-hidden="true" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function ThinkingDots() {
  return (
    <div className="flex items-center gap-1 py-1.5" role="status" aria-label="ORCA is thinking">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-mute"
          style={{ animation: "pulseDot 1.2s ease-in-out infinite", animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}

function StructuredDataPanel({ data }) {
  const { type, summary, fields } = data ?? {};

  return (
    <div className="mt-3 max-w-[520px] rounded-xl border border-line bg-surface px-4 py-3">
      {type && (
        <span className="text-[10px] font-medium uppercase tracking-wide text-[#3DA7B7]">
          {type}
        </span>
      )}
      {summary && <p className="mt-1 text-xs text-mute">{summary}</p>}
      {Array.isArray(fields) && fields.length > 0 && (
        <dl className="mt-2.5 grid grid-cols-1 gap-1.5 sm:grid-cols-2">
          {fields.map((f) => (
            <div key={f.label} className="flex items-baseline justify-between gap-3 sm:block">
              <dt className="text-[11px] text-mute2">{f.label}</dt>
              <dd className="text-xs text-ink/90">{f.value}</dd>
            </div>
          ))}
        </dl>
      )}
    </div>
  );
}
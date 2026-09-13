import { useEffect, useRef } from "react";
import { ArrowUp } from "lucide-react";

export default function ChatInput({
  value,
  onChange,
  onSend,
  disabled = false,
  placeholder = "Ask ORCA anything...",
}) {
  const textareaRef = useRef(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [value]);

  function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div className="flex items-end gap-2 rounded-2xl border border-line bg-surface2 px-3 py-2.5 transition-colors duration-200 focus-within:border-[#3DA7B7]/50">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={1}
        disabled={disabled}
        aria-label="Message ORCA"
        className="max-h-[200px] flex-1 resize-none bg-transparent py-1.5 text-sm text-ink placeholder:text-mute2 outline-none disabled:opacity-60"
      />
      <button
        type="button"
        onClick={handleSend}
        disabled={!canSend}
        aria-label="Send message"
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full transition-all duration-200 ${
          canSend ? "bg-[#3DA7B7] text-void hover:bg-[#3DA7B7]/90" : "bg-white/5 text-mute2 cursor-not-allowed"
        }`}
      >
        <ArrowUp size={16} aria-hidden="true" />
      </button>
    </div>
  );
}
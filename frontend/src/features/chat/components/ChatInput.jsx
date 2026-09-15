import { useEffect, useRef } from "react";
import { ArrowUp, Compass } from "lucide-react";


export default function ChatInput({
  value,
  onChange,
  onSend,
  onLocationClick,
  disabled = false,
  placeholder = "Ask ORCA anything...",
}) {
  const textareaRef = useRef(null);

  // Automatically grow textarea
  useEffect(() => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    textarea.style.height = `${Math.min(
      textarea.scrollHeight,
      180
    )}px`;
  }, [value]);

  const handleSend = () => {
    const message = value.trim();

    if (!message || disabled) {
      return;
    }

    onSend(message);
  };

  const handleKeyDown = (event) => {
    // Enter = send
    // Shift + Enter = new line
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const canSend =
    value.trim().length > 0 && !disabled;

  return (
    <div
      className="
        flex
        items-end
        gap-2
        rounded-2xl
        border
        border-white/10
        bg-[#111113]
        px-3
        py-2.5
        transition
        focus-within:border-[#3DA7B7]/50
      "
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={1}
        disabled={disabled}
        aria-label="Message ORCA"
        className="
          max-h-[180px]
          flex-1
          resize-none
          bg-transparent
          py-1.5
          text-sm
          leading-6
          text-white
          outline-none
          placeholder:text-[#5F5F65]
          disabled:opacity-50
        "
      />
       {/* Location button */}
      <button
        type="button"
        onClick={() => onLocationClick?.()}
        aria-label="Choose location"
        title="Choose location"
        className="
          flex
          h-9
          w-9
          shrink-0
          items-center
          justify-center
          rounded-full
          text-[#77777D]
          transition
          hover:bg-white/5
          hover:text-[#3DA7B7]
        "
      >
        <Compass
          size={18}
          strokeWidth={1.8}
          aria-hidden="true"
        />
      </button>

      {/* Send button */}
      
      <button
        type="button"
        onClick={handleSend}
        disabled={!canSend}
        aria-label="Send message"
        className="
          flex
          h-9
          w-9
          shrink-0
          items-center
          justify-center
          rounded-full
          bg-[#3DA7B7]
          text-black
          transition
          hover:bg-[#52b8c8]
          disabled:cursor-not-allowed
          disabled:bg-white/5
          disabled:text-[#55555A]
        "
      >
        <ArrowUp
          size={17}
          strokeWidth={2}
        />
      </button>
    </div>
  );
}
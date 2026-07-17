import { useState, useRef } from "react";
import { Send, Mic, MicOff, ImagePlus } from "lucide-react";

import { cn } from "../../lib/utils";

interface ChatInputProps {
  onSend: (text: string) => void;
  onImageUpload?: (file: File) => void;
  disabled?: boolean;
  isListening?: boolean;
  onSpeechToggle?: () => void;
}

export default function ChatInput({
  onSend,
  onImageUpload,
  disabled = false,
  isListening = false,
  onSpeechToggle,
}: ChatInputProps) {
  const [text, setText] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onImageUpload) {
      onImageUpload(file);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <div className="flex flex-1 items-center gap-2 rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2 focus-within:ring-2 focus-within:ring-[hsl(var(--ring))]/50 transition-all">
        {onSpeechToggle && (
          <button
            type="button"
            onClick={onSpeechToggle}
            className={cn(
              "rounded-lg p-2 transition-colors shrink-0",
              isListening
                ? "bg-rose-100 text-rose-600 dark:bg-rose-950/20 dark:text-rose-400 animate-pulse"
                : "hover:bg-[hsl(var(--accent))] text-[hsl(var(--muted-foreground))]"
            )}
            title={isListening ? "Stop listening" : "Start dictation"}
          >
            {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </button>
        )}

        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type symptoms or speak..."
          className="w-full bg-transparent text-sm outline-none placeholder:text-[hsl(var(--muted-foreground))]"
          disabled={disabled}
        />

        {onImageUpload && (
          <>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/*"
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="rounded-lg p-2 hover:bg-[hsl(var(--accent))] text-[hsl(var(--muted-foreground))] transition-colors shrink-0"
              title="Attach clinical image"
              disabled={disabled}
            >
              <ImagePlus className="h-4 w-4" />
            </button>
          </>
        )}

        <button
          type="submit"
          disabled={!text.trim() || disabled}
          className="rounded-xl bg-gradient-primary p-2 text-white shadow-sm transition-all hover:shadow hover:opacity-95 disabled:opacity-40 shrink-0"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </form>
  );
}

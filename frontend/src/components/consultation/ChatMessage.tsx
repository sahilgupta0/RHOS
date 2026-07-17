import { cn } from "../../lib/utils";
import { User, Bot, AlertTriangle } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "../../types";

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isPatient = message.role === "patient";
  const isSystem = message.role === "system";

  return (
    <div
      className={cn(
        "flex gap-3 animate-slide-up",
        isPatient && "flex-row-reverse"
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full shadow-sm text-white",
          isPatient
            ? "bg-blue-500"
            : isSystem
            ? "bg-amber-500"
            : "bg-gradient-primary"
        )}
      >
        {isPatient ? (
          <User className="h-4 w-4" />
        ) : isSystem ? (
          <AlertTriangle className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3 shadow-sm",
          isPatient
            ? "bg-gradient-primary text-white rounded-br-none"
            : isSystem
            ? "bg-amber-50 dark:bg-amber-950/10 border border-amber-200 dark:border-amber-900/30 text-amber-800 dark:text-amber-400 rounded-bl-none"
            : "bg-[hsl(var(--muted))] text-[hsl(var(--foreground))] rounded-bl-none"
        )}
      >
        {message.agentName && !isPatient && (
          <p className="mb-1 text-[9px] font-bold uppercase tracking-wider opacity-65">
            {message.agentName}
          </p>
        )}
        <div className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</div>
        <p
          className={cn(
            "mt-1.5 text-[9px] opacity-50",
            isPatient ? "text-right" : "text-left"
          )}
        >
          {new Date(message.timestamp).toLocaleTimeString("en-IN", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}

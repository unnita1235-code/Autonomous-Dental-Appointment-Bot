"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Mic, Minimize2, Paperclip, Send, X } from "lucide-react";
import { useSocket } from "@/lib/socket";
import ChatMessage from "./ChatMessage";
import { useChatStore, type SlotOption } from "./ChatStore";

interface ChatPanelProps {
  onClose: () => void;
  onMinimize: () => void;
}

export default function ChatPanel({ onClose, onMinimize }: ChatPanelProps): JSX.Element {
  const [input, setInput] = useState<string>("");
  const [isVoiceSupported, setIsVoiceSupported] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { socket, isConnected } = useSocket("/");

  const { messages, isTyping, conversationId, sendMessage, receiveBotMessage, addMessage } = useChatStore(
    (state) => ({
      messages: state.messages,
      isTyping: state.isTyping,
      conversationId: state.conversationId,
      sendMessage: state.sendMessage,
      receiveBotMessage: state.receiveBotMessage,
      addMessage: state.addMessage
    })
  );

  const socketStatusText = useMemo(() => (isConnected ? "Online" : "Reconnecting..."), [isConnected]);

  useEffect(() => {
    setIsVoiceSupported(typeof window !== "undefined" && "MediaRecorder" in window);
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }
    container.scrollTop = container.scrollHeight;
  }, [messages, isTyping]);

  useEffect(() => {
    if (!socket) {
      return;
    }

    const handleBotMessage = (payload: {
      content: string;
      quick_replies?: Array<{ id: string; label: string; value: string }>;
      slot_options?: SlotOption[];
      payment_button?: { label: string; url: string };
    }) => {
      receiveBotMessage({
        content: payload.content,
        quick_replies: payload.quick_replies,
        slot_options: payload.slot_options,
        payment_button: payload.payment_button
      });
    };

    const handleConnected = () => {
      if (conversationId) {
        socket.emit("conversation:join", { conversation_id: conversationId });
      }
    };

    const handleDisconnected = () => {
      addMessage({
        id: crypto.randomUUID(),
        role: "system",
        content: "Connection lost. Reconnecting securely...",
        created_at: new Date().toISOString()
      });
    };

    socket.on("conversation:bot_message", handleBotMessage);
    socket.on("connect", handleConnected);
    socket.on("disconnect", handleDisconnected);

    return () => {
      socket.off("conversation:bot_message", handleBotMessage);
      socket.off("connect", handleConnected);
      socket.off("disconnect", handleDisconnected);
    };
  }, [addMessage, conversationId, receiveBotMessage, socket]);

  const onSubmit = async (): Promise<void> => {
    const text = input.trim();
    if (!text) {
      return;
    }
    setInput("");
    await sendMessage(text);
  };

  return (
    <div className="flex h-full flex-col bg-white">
      <header className="flex h-14 items-center justify-between border-b border-slate-200 px-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full bg-primary text-sm font-semibold text-white">
            DC
          </div>
          <div>
            <p className="font-heading text-sm font-semibold text-slate-900">Dental Care Clinic</p>
            <p className="flex items-center gap-1 text-xs text-muted">
              <span className={`h-2 w-2 rounded-full ${isConnected ? "bg-success" : "bg-warning"}`} />
              {socketStatusText}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={onMinimize}
            aria-label="Minimize chat"
            className="rounded-md p-2 text-slate-600 transition hover:bg-slate-100"
          >
            <Minimize2 className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close chat"
            className="rounded-md p-2 text-slate-600 transition hover:bg-slate-100"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </header>

      <div ref={containerRef} className="flex-1 space-y-3 overflow-y-auto bg-white px-3 py-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onQuickReply={(value) => void sendMessage(value)}
            onSelectSlot={(slot) =>
              void sendMessage(`I would like to book ${slot.service_name} with Dr. ${slot.dentist_name} at ${slot.start_time}`)
            }
          />
        ))}
        {isTyping ? (
          <div className="flex justify-start">
            <div className="flex items-center gap-1 rounded-2xl rounded-tr-lg bg-surface px-3 py-2">
              <span className="h-1.5 w-1.5 animate-typing-dot rounded-full bg-muted [animation-delay:0ms]" />
              <span className="h-1.5 w-1.5 animate-typing-dot rounded-full bg-muted [animation-delay:150ms]" />
              <span className="h-1.5 w-1.5 animate-typing-dot rounded-full bg-muted [animation-delay:300ms]" />
            </div>
          </div>
        ) : null}
      </div>

      <footer className="border-t border-slate-200 p-3">
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition hover:bg-slate-100"
            aria-label="Attach file"
          >
            <Paperclip className="h-4 w-4" />
          </button>
          {isVoiceSupported ? (
            <button
              type="button"
              className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition hover:bg-slate-100"
              aria-label="Record voice message"
            >
              <Mic className="h-4 w-4" />
            </button>
          ) : null}
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void onSubmit();
              }
            }}
            placeholder="Type a message..."
            className="h-9 flex-1 rounded-full border border-slate-300 px-4 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
          />
          <button
            type="button"
            onClick={() => void onSubmit()}
            aria-label="Send message"
            className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-primary text-white transition hover:bg-primary-hover"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </footer>
    </div>
  );
}

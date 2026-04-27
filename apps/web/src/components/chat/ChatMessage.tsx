"use client";

import { format } from "date-fns";
import QuickReplies from "./QuickReplies";
import SlotPicker from "./SlotPicker";
import BookingConfirmation from "./BookingConfirmation";
import type { ChatMessage as ChatMessageType, SlotOption } from "./ChatStore";

interface ChatMessageProps {
  message: ChatMessageType;
  onQuickReply: (value: string) => void;
  onSelectSlot: (slot: SlotOption) => void;
}

export default function ChatMessage({
  message,
  onQuickReply,
  onSelectSlot
}: ChatMessageProps): JSX.Element {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="flex justify-center py-1">
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-muted">{message.content}</span>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        {!isUser ? (
          <div className="mb-1 flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-[10px] font-semibold text-primary">
            DC
          </div>
        ) : null}
        <div
          className={`px-3 py-2 text-sm leading-relaxed shadow-sm ${
            isUser
              ? "rounded-2xl rounded-tl-lg bg-primary text-white"
              : "rounded-2xl rounded-tr-lg bg-surface text-slate-800"
          }`}
        >
          {message.content}
        </div>
        {message.quick_replies?.length ? (
          <QuickReplies options={message.quick_replies} onSelect={onQuickReply} />
        ) : null}
        {message.slot_options?.length ? (
          <SlotPicker slots={message.slot_options} onSelect={onSelectSlot} />
        ) : null}
        {message.payment_button ? (
          <a
            href={message.payment_button.url}
            target="_blank"
            rel="noreferrer"
            className="mt-2 inline-flex h-8 items-center rounded-md bg-accent px-3 text-xs font-semibold text-white transition hover:bg-accent-hover"
          >
            {message.payment_button.label}
          </a>
        ) : null}
        {message.booking_confirmation ? <BookingConfirmation booking={message.booking_confirmation} /> : null}
        <span className="mt-1 text-[11px] text-muted">
          {format(new Date(message.created_at), "h:mm a")}
        </span>
      </div>
    </div>
  );
}

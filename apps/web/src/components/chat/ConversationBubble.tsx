"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Calendar, CheckCircle, ExternalLink, Loader2, MoreHorizontal, ChevronDown } from "lucide-react";

import { cn } from "@/lib/design-system";
import { AISparkle } from "@/components/ai/AIIndicator";
import { Chip } from "@/components/ui/chip";
import { Button } from "@/components/ui/button";
import { Avatar } from "@/components/ui/avatar";

/* ============================================================
   Types
   ============================================================ */

export type MessageRole = "user" | "assistant" | "system" | "staff";

export interface MessageAttachment {
  type: "image" | "file" | "audio";
  url: string;
  name: string;
  size?: number;
  thumbnailUrl?: string;
}

export interface ConversationBubbleProps {
  role: MessageRole;
  content: string;
  timestamp: string;
  avatar?: string;
  avatarFallback?: string;
  name?: string;
  attachments?: MessageAttachment[];
  quickReplies?: Array<{ id: string; label: string; value: string }>;
  slotOptions?: Array<{
    id: string;
    start_time: string;
    dentist_name: string;
    service_name: string;
  }>;
  paymentButton?: {
    label: string;
    url: string;
  };
  bookingConfirmation?: {
    appointment_id: string;
    patient_name: string;
    service_name: string;
    dentist_name: string;
    appointment_time: string;
  };
  isTyping?: boolean;
  deliveryStatus?: "sending" | "sent" | "delivered" | "read" | "failed";
  showTimestamp?: boolean;
  showAvatar?: boolean;
  showName?: boolean;
  onQuickReply?: (value: string) => void;
  onSelectSlot?: (slot: any) => void;
  onAttachmentClick?: (attachment: MessageAttachment) => void;
  onMenuAction?: (action: "copy" | "edit" | "delete" | "react", messageId: string) => void;
  messageId?: string;
  className?: string;
  variant?: "default" | "compact" | "comfortable";
  children?: React.ReactNode;
}

export interface MessageAttachment {
  type: "image" | "file" | "audio";
  url: string;
  name: string;
  size?: number;
  thumbnailUrl?: string;
}

const bubbleVariants = cva(
  "max-w-[85%] px-4 py-2.5 text-sm leading-relaxed shadow-sm transition-shadow duration-150",
  {
    variants: {
      role: {
        user: "rounded-2xl rounded-tr-lg bg-patient-primary text-patient-on-primary",
        assistant: "rounded-2xl rounded-tl-lg bg-patient-surface-lowest text-patient-on-surface border border-patient-outline-variant",
        system: "rounded-full bg-staff-surface-variant text-staff-on-surface-variant px-3 py-1 text-xs",
        staff: "rounded-2xl rounded-tr-lg bg-staff-primary text-staff-on-primary",
      },
      variant: {
        default: "",
        compact: "px-3 py-1.5 text-xs",
        comfortable: "px-4 py-3 text-base",
      },
    },
    defaultVariants: {
      role: "assistant",
      variant: "default",
    },
  }
);

const avatarVariants = cva(
  "flex-shrink-0 overflow-hidden rounded-full bg-patient-surface-variant",
  {
    variants: {
      size: {
        sm: "w-6 h-6",
        default: "w-8 h-8",
        lg: "w-10 h-10",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
);

const typingIndicatorVariants = cva(
  "flex items-center gap-1 rounded-2xl rounded-tl-lg bg-patient-surface-lowest px-3 py-2 border border-patient-outline-variant",
  {
    variants: {
      size: {
        sm: "gap-0.5",
        default: "gap-1",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
);

/* ============================================================
   ConversationBubble Component
   ============================================================ */

const ConversationBubble = React.forwardRef<HTMLDivElement, ConversationBubbleProps>(
  (
    {
      role,
      content,
      timestamp,
      avatar,
      avatarFallback,
      name,
      attachments,
      quickReplies,
      slotOptions,
      paymentButton,
      bookingConfirmation,
      isTyping,
      deliveryStatus,
      showTimestamp = true,
      showAvatar = true,
      showName = true,
      onQuickReply,
      onSelectSlot,
      onAttachmentClick,
      onMenuAction,
      messageId,
      className,
      variant = "default",
      children,
      ...props
    },
    ref
  ) => {
    const isUser = role === "user";
    const isStaff = role === "staff";
    const isAssistant = role === "assistant";
    const isSystem = role === "system";

    const formatTimestamp = (ts: string) => {
      const date = new Date(ts);
      return date.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
    };

    const prefersReducedMotion = React.useMemo(
      () => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      []
    );

    // Typing indicator
    if (isTyping) {
      return (
        <div ref={ref} className={cn("flex justify-start", className)} {...props}>
          {showAvatar && (
            <Avatar size="sm" src={avatar} fallback={avatarFallback ?? "AI"} className="mb-1" />
          )}
          <div className={cn(typingIndicatorVariants({ size: "default" }))}>
            <AISparkle size="xs" animated={!prefersReducedMotion} />
            <span className="h-1.5 w-1.5 rounded-full bg-staff-on-surface-muted/40 animate-[typing-dot_1.2s_infinite_ease-in-out]" style={{ animationDelay: "0ms" }} aria-hidden="true" />
            <span className="h-1.5 w-1.5 rounded-full bg-staff-on-surface-muted/40 animate-[typing-dot_1.2s_infinite_ease-in-out]" style={{ animationDelay: "150ms" }} aria-hidden="true" />
            <span className="h-1.5 w-1.5 rounded-full bg-staff-on-surface-muted/40 animate-[typing-dot_1.2s_infinite_ease-in-out]" style={{ animationDelay: "300ms" }} aria-hidden="true" />
          </div>
        </div>
      );
    }

    // System message
    if (isSystem) {
      return (
        <div ref={ref} className={cn("flex justify-center py-1", className)} {...props}>
          <span className={bubbleVariants({ role: "system", variant })}>
            {content}
          </span>
        </div>
      );
    }

    const timeString = formatTimestamp(timestamp);

    return (
      <div
        ref={ref}
        className={cn(
          "flex flex-col gap-1",
          isUser ? "items-end" : "items-start",
          className
        )}
        {...props}
      >
        {/* Avatar + Name Row */}
        {(showAvatar || showName) && (
          <div className={cn("flex items-end gap-2", isUser ? "flex-row-reverse" : "")}>
            {showAvatar && (
              <Avatar size="sm" src={avatar} fallback={avatarFallback ?? (isUser ? "You" : isAssistant ? "AI" : "ST")} className="mb-1" />
            )}
            {showName && name && !isUser && (
              <span className="mb-1 text-[10px] font-semibold text-staff-on-surface-variant">
                {name}
              </span>
            )}
          </div>
        )}

        {/* Message Bubble */}
        <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
          <div className={cn(bubbleVariants({ role, variant }))}>
            {/* Content */}
            <p className="whitespace-pre-wrap">{content}</p>

            {/* Attachments */}
            {attachments && attachments.length > 0 && (
              <div className="mt-2 space-y-1">
                {attachments.map((attachment, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => onAttachmentClick?.(attachment)}
                    className="flex items-center gap-2 w-full p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-left"
                  >
                    {attachment.type === "image" && attachment.thumbnailUrl && (
                      <img
                        src={attachment.thumbnailUrl}
                        alt={attachment.name}
                        className="w-12 h-12 rounded-lg object-cover flex-shrink-0"
                      />
                    )}
                    {attachment.type !== "image" && (
                      <div className="w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                        {attachment.type === "audio" ? (
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1a1 1 0 011 1v4a1 1 0 01-1 1zm8-6a1 1 0 01-1-1v-2a1 1 0 011-1h1a1 1 0 011 1v2a1 1 0 01-1 1zm-4 4a1 1 0 01-1-1v-2a1 1 0 011-1h1a1 1 0 011 1v2a1 1 0 01-1 1z" />
                          </svg>
                        ) : (
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 10-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                          </svg>
                        )}
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{attachment.name}</p>
                      {attachment.size && (
                        <p className="text-[11px] text-white/70">{(attachment.size / 1024).toFixed(1)} KB</p>
                      )}
                    </div>
                    <ChevronDown className="h-4 w-4 opacity-70" aria-hidden="true" />
                  </button>
                ))}
              </div>
            )}

            {/* Quick Replies */}
            {quickReplies && quickReplies.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {quickReplies.map((option) => (
                  <Chip
                    key={option.id}
                    variant="default"
                    size="sm"
                    onClick={() => onQuickReply?.(option.value)}
                  >
                    {option.label}
                  </Chip>
                ))}
              </div>
            )}

            {/* Slot Options */}
            {slotOptions && slotOptions.length > 0 && (
              <div className="mt-2 space-y-1.5">
                {slotOptions.map((slot) => {
                  const start = new Date(slot.start_time);
                  return (
                    <button
                      key={slot.id}
                      type="button"
                      onClick={() => onSelectSlot?.(slot)}
                      className="w-full text-left p-3 rounded-xl border border-white/10 hover:bg-white/10 transition-colors"
                    >
                      <div className="font-medium text-sm">{start.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })}</div>
                      <div className="text-xs opacity-80">{start.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })}</div>
                      <div className="text-xs opacity-70">Dr. {slot.dentist_name} • {slot.service_name}</div>
                    </button>
                  );
                })}
              </div>
            )}

            {/* Payment Button */}
            {paymentButton && (
              <a
                href={paymentButton.url}
                target="_blank"
                rel="noreferrer"
                className="mt-2 inline-flex h-9 items-center gap-2 rounded-lg bg-staff-primary px-4 text-xs font-semibold text-white transition-colors hover:bg-staff-primary-hover"
              >
                {paymentButton.label}
              </a>
            )}

            {/* Booking Confirmation */}
            {bookingConfirmation && (
              <div className="mt-2 rounded-xl border border-staff-success/30 bg-staff-success-container/10 p-3">
                <div className="flex items-center gap-2 text-staff-success">
                  <span className="h-4 w-4">✓</span>
                  <p className="text-sm font-semibold">Booking Confirmed</p>
                </div>
                <div className="mt-2 space-y-1 text-xs text-staff-on-surface">
                  <p><span className="font-medium">Appointment ID:</span> {bookingConfirmation.appointment_id}</p>
                  <p><span className="font-medium">Patient:</span> {bookingConfirmation.patient_name}</p>
                  <p><span className="font-medium">Dentist:</span> {bookingConfirmation.dentist_name}</p>
                  <p><span className="font-medium">Service:</span> {bookingConfirmation.service_name}</p>
                </div>
                <a
                  href={`https://calendar.google.com/calendar/render?action=TEMPLATE&text=Dental+Appointment+-+${encodeURIComponent(bookingConfirmation.service_name)}&dates=${new Date(bookingConfirmation.appointment_time).toISOString().replace(/[-:]/g, "").split(".")[0]}Z/${new Date(new Date(bookingConfirmation.appointment_time).getTime() + 30 * 60 * 1000).toISOString().replace(/[-:]/g, "").split(".")[0]}Z&details=Appointment+ID:+${bookingConfirmation.appointment_id}%0ADentist:+${bookingConfirmation.dentist_name}%0APatient:+${bookingConfirmation.patient_name}`}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-3 inline-flex h-8 items-center gap-1 rounded-lg bg-white px-3 text-xs font-semibold text-staff-success shadow-sm ring-1 ring-staff-success/30 transition-colors hover:bg-staff-success-container/20"
                >
                  <span className="h-3.5 w-3.5">📅</span>
                  Add to calendar
                </a>
              </div>
            )}

            {/* Timestamp + Delivery Status */}
            <div className="mt-1.5 flex items-center gap-1.5">
              {showTimestamp && (
                <time
                  dateTime={timestamp}
                  className={cn(
                    "text-[10px] font-mono",
                    isUser ? "text-patient-on-primary/70" : "text-staff-on-surface-muted"
                  )}
                >
                  {timeString}
                </time>
              )}
              {deliveryStatus && !isUser && (
                <span
                  className={cn(
                    "text-[10px] font-medium",
                    deliveryStatus === "failed" && "text-staff-error",
                    deliveryStatus === "sending" && "text-staff-warning animate-pulse",
                    deliveryStatus === "sent" && "text-staff-on-surface-muted",
                    deliveryStatus === "delivered" && "text-staff-success",
                    deliveryStatus === "read" && "text-staff-primary"
                  )}
                >
                  {deliveryStatus}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }
);
ConversationBubble.displayName = "ConversationBubble";

/* ============================================================
   Message Group - Groups consecutive messages from same sender
   ============================================================ */

export interface MessageGroupProps {
  messages: Array<ConversationBubbleProps & { id: string }>;
  onQuickReply: (value: string) => void;
  onSelectSlot: (slot: any) => void;
  onAttachmentClick?: (attachment: any) => void;
  onMenuAction?: (action: string, messageId: string) => void;
  className?: string;
}

const MessageGroup = React.forwardRef<HTMLDivElement, MessageGroupProps>(
  ({ messages, onQuickReply, onSelectSlot, onAttachmentClick, onMenuAction, className }, ref) => {
    return (
      <div ref={ref} className={cn("flex flex-col gap-3", className)}>
        {messages.map((message, index) => (
          <ConversationBubble
            key={message.id}
            {...message}
            onQuickReply={onQuickReply}
            onSelectSlot={onSelectSlot}
            onAttachmentClick={onAttachmentClick}
            onMenuAction={onMenuAction}
            showAvatar={index === 0 || messages[index - 1]?.role !== message.role}
            showName={index === 0 || messages[index - 1]?.role !== message.role}
            showTimestamp={index === messages.length - 1 || messages[index + 1]?.role !== message.role}
          />
        ))}
      </div>
    );
  }
);
MessageGroup.displayName = "MessageGroup";

export { ConversationBubble, MessageGroup, bubbleVariants };
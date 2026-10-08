"use client";

import * as React from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { format } from "date-fns";
import {
  Minimize2,
  Paperclip,
  Send,
  X,
  Mic,
  MicOff,
  Phone,
  AlertCircle,
} from "lucide-react";

import { cn } from "@/lib/design-system";
import { useSocket } from "@/lib/socket";
import { ConversationBubble, MessageGroup } from "./ConversationBubble";
import { ChatComposer } from "./ChatComposer";
import { useChatStore, type SlotOption, type QuickReplyOption } from "./ChatStore";
import { DentalFlowAvatar } from "@/components/branding";
import { AIIndicator } from "@/components/ai/AIIndicator";
import { Button } from "@/components/ui/button";
import { AISparkle } from "@/components/ai/AIIndicator";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";

interface ChatPanelProps {
  onClose: () => void;
  onMinimize: () => void;
}

export default function ChatPanel({ onClose, onMinimize }: ChatPanelProps): JSX.Element {
  const [input, setInput] = React.useState<string>("");
  const containerRef = React.useRef<HTMLDivElement>(null);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const { socket, isConnected } = useSocket("/");

  const {
    messages,
    isTyping,
    conversationId,
    sendMessage,
    receiveBotMessage,
    addMessage,
    setConversationId,
  } = useChatStore(
    (state) => ({
      messages: state.messages,
      isTyping: state.isTyping,
      conversationId: state.conversationId,
      sendMessage: state.sendMessage,
      receiveBotMessage: state.receiveBotMessage,
      addMessage: state.addMessage,
      setConversationId: state.setConversationId,
    })
  );

  const socketStatusText = useMemo(() => (isConnected ? "Online" : "Reconnecting..."), [isConnected]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    if (!socket) return;

    const handleBotMessage = (payload: {
      content: string;
      quick_replies?: Array<{ id: string; label: string; value: string }>;
      slot_options?: SlotOption[];
      payment_button?: { label: string; url: string };
      booking_confirmation?: {
        appointment_id: string;
        patient_name: string;
        service_name: string;
        dentist_name: string;
        appointment_time: string;
      };
    }) => {
      receiveBotMessage({
        content: payload.content,
        quick_replies: payload.quick_replies,
        slot_options: payload.slot_options,
        payment_button: payload.payment_button,
        booking_confirmation: payload.booking_confirmation,
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
        created_at: new Date().toISOString(),
      });
    };

    const handleHandoff = (payload: { conversation_id: string; status: string }) => {
      addMessage({
        id: crypto.randomUUID(),
        role: "system",
        content: `You are now connected with a dental care specialist.`,
        created_at: new Date().toISOString(),
      });
    };

    socket.on("conversation:bot_message", handleBotMessage);
    socket.on("connect", handleConnected);
    socket.on("disconnect", handleDisconnected);
    socket.on("conversation:handoff", handleHandoff);

    return () => {
      socket.off("conversation:bot_message", handleBotMessage);
      socket.off("connect", handleConnected);
      socket.off("disconnect", handleDisconnected);
      socket.off("conversation:handoff", handleHandoff);
    };
  }, [addMessage, conversationId, receiveBotMessage, socket]);

  const handleSubmit = async (): Promise<void> => {
    const text = input.trim();
    if (!text) return;
    setInput("");
    await sendMessage(text);
  };

  // Map ChatStore messages to ConversationBubble format
  const mapMessageForBubble = React.useCallback((message: typeof messages[0]) => ({
    ...message,
    role: message.role === "bot" ? "assistant" as const : message.role,
    timestamp: message.created_at,
    quickReplies: message.quick_replies,
    slotOptions: message.slot_options,
    paymentButton: message.payment_button,
    bookingConfirmation: message.booking_confirmation,
  }), []);

  // Group consecutive messages from same sender
  const messageGroups = React.useMemo(() => {
    const groups: Array<{ role: string; messages: ReturnType<typeof mapMessageForBubble>[] }> = [];
    let currentGroup: ReturnType<typeof mapMessageForBubble>[] = [];

    messages.forEach((message) => {
      const mappedMessage = mapMessageForBubble(message);
      const isSystem = message.role === "system";
      if (isSystem) {
        if (currentGroup.length > 0) {
          groups.push({ role: currentGroup[0].role, messages: currentGroup });
          currentGroup = [];
        }
        groups.push({ role: "system", messages: [mappedMessage] });
      } else if (currentGroup.length === 0 || currentGroup[currentGroup.length - 1].role === mappedMessage.role) {
        currentGroup.push(mappedMessage);
      } else {
        groups.push({ role: currentGroup[0].role, messages: currentGroup });
        currentGroup = [mappedMessage];
      }
    });

    if (currentGroup.length > 0) {
      groups.push({ role: currentGroup[0].role, messages: currentGroup });
    }

    return groups;
  }, [messages, mapMessageForBubble]);

  return (
    <TooltipProvider>
      <div className={cn(
      "flex h-full flex-col",
      "bg-patient-surface-lowest",
      "rounded-3xl",
      "shadow-elevation-4",
      "overflow-hidden"
    )}>
      {/* Header - Gradient */}
      <header className={cn(
        "flex h-14 items-center justify-between px-4 shrink-0 shadow-sm",
        "bg-gradient-to-r from-patient-primary to-patient-primary-hover",
        "text-patient-on-primary"
      )}>
        <div className="flex items-center gap-3 min-w-0">
          <div className="relative w-10 h-10 shrink-0">
            <DentalFlowAvatar
              size="lg"
              variant="primary"
              online={isConnected}
              fallback="AI"
            >
              <AISparkle size="xs" className="absolute -bottom-1 -right-1" animated={true} />
            </DentalFlowAvatar>
          </div>
          <div className="min-w-0">
            <h2 className="font-heading text-label-md font-semibold truncate">
              DentalFlow AI
            </h2>
            <p className="flex items-center gap-1 text-xs text-patient-on-primary/80">
              <span className={cn(
                "h-1.5 w-1.5 rounded-full",
                isConnected ? "bg-patient-success" : "bg-patient-warning"
              )} />
              {socketStatusText}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                type="button"
                onClick={onMinimize}
                aria-label="Minimize chat"
                className={cn(
                  "rounded-full p-2 text-patient-on-primary/80",
                  "hover:bg-white/15 transition-colors",
                  "focus-visible:ring-2 focus-visible:ring-white/30"
                )}
              >
                <Minimize2 className="h-4 w-4" />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" align="end">
              <p className="text-sm">Minimize</p>
            </TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close chat"
                className={cn(
                  "rounded-full p-2 text-patient-on-primary/80",
                  "hover:bg-white/15 transition-colors",
                  "focus-visible:ring-2 focus-visible:ring-white/30"
                )}
              >
                <X className="h-4 w-4" />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" align="end">
              <p className="text-sm">Close</p>
            </TooltipContent>
          </Tooltip>
        </div>
      </header>

      {/* Messages Area */}
      <div
        ref={containerRef}
        className={cn(
          "flex-1 overflow-y-auto p-4 space-y-4",
          "bg-patient-surface-lowest"
        )}
      >
        <div ref={messagesEndRef} />
        {messageGroups.map((group, index) => (
          group.role === "system" ? (
            <div key={index} className="flex justify-center">
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-patient-surface text-patient-on-surface-variant text-xs font-medium">
                {group.messages[0].content}
              </div>
            </div>
          ) : (
            <MessageGroup
              key={index}
              messages={group.messages.map((m, i) => ({ ...m, id: `${m.id}-${i}` }))}
              onQuickReply={sendMessage}
              onSelectSlot={(slot) =>
                void sendMessage(
                  `I would like to book ${slot.service_name} with Dr. ${slot.dentist_name} at ${slot.start_time}`
                )
              }
            />
          )
        ))}
        {isTyping && (
          <div className="flex justify-start animate-in slide-in-from-bottom-2 fade-in">
            <div className="flex items-center gap-2 max-w-[85%]">
              <DentalFlowAvatar size="sm" fallback="AI" variant="ai" />
              <div className={cn(
                "flex items-center gap-1 rounded-2xl rounded-tl-xl",
                "bg-patient-surface px-3 py-2 border border-patient-outline-variant",
                "shadow-sm"
              )}>
                <AISparkle size="xs" animated={true} />
                <span className="h-1.5 w-1.5 rounded-full bg-patient-on-surface-variant/40 animate-[typing-dot_1.2s_infinite_ease-in-out]" style={{ animationDelay: "0ms" }} aria-hidden="true" />
                <span className="h-1.5 w-1.5 rounded-full bg-patient-on-surface-variant/40 animate-[typing-dot_1.2s_infinite_ease-in-out]" style={{ animationDelay: "150ms" }} aria-hidden="true" />
                <span className="h-1.5 w-1.5 rounded-full bg-patient-on-surface-variant/40 animate-[typing-dot_1.2s_infinite_ease-in-out]" style={{ animationDelay: "300ms" }} aria-hidden="true" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer - Composer */}
      <footer className={cn(
        "border-t border-patient-outline-variant p-3 shrink-0",
        "bg-patient-surface"
      )}>
        <ChatComposer
          value={input}
          onChange={setInput}
          onSubmit={handleSubmit}
          disabled={isTyping}
          loading={isTyping}
          placeholder="Type a message..."
          showAttachments={false}
          showVoice={false}
          onAttachFile={() => {}}
          onRecordVoice={undefined}
          variant="patient"
        />
        <p className="mt-2 text-center text-[11px] text-patient-on-surface-variant leading-tight">
          DentalFlow AI can make mistakes. For urgent dental emergencies, contact your clinic directly.
        </p>
      </footer>
    </div>
    </TooltipProvider>
  );
}
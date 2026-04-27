"use client";

import { create } from "zustand";
import { apiClient } from "@/lib/api";

export interface QuickReplyOption {
  id: string;
  label: string;
  value: string;
}

export interface SlotOption {
  id: string;
  start_time: string;
  dentist_name: string;
  service_name: string;
}

export interface BookingConfirmationPayload {
  appointment_id: string;
  patient_name: string;
  service_name: string;
  dentist_name: string;
  appointment_time: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "bot" | "system";
  content: string;
  created_at: string;
  quick_replies?: QuickReplyOption[];
  slot_options?: SlotOption[];
  payment_button?: {
    label: string;
    url: string;
  };
  booking_confirmation?: BookingConfirmationPayload;
}

interface ConversationCreateResponse {
  id: string;
}

interface TurnCreateResponse {
  id: string;
  role: string;
  content: string;
  created_at: string;
}

interface ChatState {
  messages: ChatMessage[];
  isTyping: boolean;
  conversationId: string | null;
  sessionId: string;
  channel: "web";
  addMessage: (message: ChatMessage) => void;
  setTyping: (value: boolean) => void;
  setConversationId: (conversationId: string) => void;
  setSessionId: (sessionId: string) => void;
  sendMessage: (text: string) => Promise<void>;
  receiveBotMessage: (message: Omit<ChatMessage, "id" | "created_at" | "role">) => void;
}

const createSessionId = (): string => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
};

const toUserMessage = (text: string): ChatMessage => ({
  id: crypto.randomUUID(),
  role: "user",
  content: text,
  created_at: new Date().toISOString()
});

const toSystemMessage = (text: string): ChatMessage => ({
  id: crypto.randomUUID(),
  role: "system",
  content: text,
  created_at: new Date().toISOString()
});

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [
    {
      id: crypto.randomUUID(),
      role: "bot",
      content: "Hello! I'm here to help you book, reschedule, or check your appointment.",
      created_at: new Date().toISOString(),
      quick_replies: [
        { id: "book", label: "Book appointment", value: "I'd like to book an appointment" },
        { id: "reschedule", label: "Reschedule", value: "I need to reschedule my appointment" },
        { id: "hours", label: "Clinic hours", value: "What are your clinic hours?" }
      ]
    }
  ],
  isTyping: false,
  conversationId: null,
  sessionId: createSessionId(),
  channel: "web",
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setTyping: (value) => set({ isTyping: value }),
  setConversationId: (conversationId) => set({ conversationId }),
  setSessionId: (sessionId) => set({ sessionId }),
  sendMessage: async (text) => {
    const trimmed = text.trim();
    if (!trimmed) {
      return;
    }

    const { addMessage, sessionId, conversationId, channel } = get();
    addMessage(toUserMessage(trimmed));
    set({ isTyping: true });

    try {
      let activeConversationId = conversationId;

      if (!activeConversationId) {
        const conversation = await apiClient.post<
          ConversationCreateResponse,
          ConversationCreateResponse
        >("/api/v1/conversations", {
          channel: "WEB_CHAT",
          session_id: sessionId,
          status: "ACTIVE",
          started_at: new Date().toISOString(),
          context: {
            channel
          }
        });

        activeConversationId = conversation.id;
        set({ conversationId: activeConversationId });
      }

      const userTurn = await apiClient.post<TurnCreateResponse, TurnCreateResponse>(
        `/api/v1/conversations/${activeConversationId}/turns`,
        {
          conversation_id: activeConversationId,
          role: "USER",
          content: trimmed,
          turn_index: get().messages.length
        }
      );

      if (userTurn.role === "ASSISTANT") {
        addMessage({
          id: userTurn.id,
          role: "bot",
          content: userTurn.content,
          created_at: userTurn.created_at
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to send message.";
      addMessage(toSystemMessage(message));
    } finally {
      set({ isTyping: false });
    }
  },
  receiveBotMessage: (message) => {
    set((state) => ({
      isTyping: false,
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          role: "bot",
          created_at: new Date().toISOString(),
          ...message
        }
      ]
    }));
  }
}));

export type { ChatState };

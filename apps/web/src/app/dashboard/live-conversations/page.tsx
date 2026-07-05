"use client";

import { useEffect, useRef, useState } from "react";
import { format } from "date-fns";
import { MessageCircle, Phone, Send, Smartphone } from "lucide-react";

import { parseJsonResponse } from "@/lib/http";
import { useStaffDashboardStore } from "@/store/useStaffDashboardStore";
import type { Conversation, ConversationTurn } from "@/types";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
}

const channelIcon = (channel: string): JSX.Element => {
  const n = channel.toLowerCase();
  if (n.includes("whatsapp")) return <MessageCircle className="h-4 w-4 text-accent" />;
  if (n.includes("sms")) return <Smartphone className="h-4 w-4 text-primary" />;
  if (n.includes("voice") || n.includes("phone")) return <Phone className="h-4 w-4 text-slate-600" />;
  return <MessageCircle className="h-4 w-4 text-slate-500" />;
};

export default function LiveConversationsPage(): JSX.Element {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const [staffMessage, setStaffMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingTurns, setLoadingTurns] = useState(false);
  const threadEndRef = useRef<HTMLDivElement>(null);
  const handoffQueue = useStaffDashboardStore((state) => state.handoffQueue);

  useEffect(() => {
    const load = async (): Promise<void> => {
      const response = await fetch("/staff-api/conversations?limit=50", { cache: "no-store" });
      const payload = await parseJsonResponse<ApiEnvelope<Conversation[]>>(response);
      if (payload?.success && payload.data) {
        setConversations(payload.data);
      }
    };
    void load();
  }, []);

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns]);

  const selectConversation = async (id: string): Promise<void> => {
    setSelectedId(id);
    setLoadingTurns(true);
    const response = await fetch(`/staff-api/conversations/${id}`, { cache: "no-store" });
    const payload = await parseJsonResponse<{ success: boolean; data: Conversation & { turns?: ConversationTurn[] } }>(response);
    if (payload?.success && payload.data) {
      setTurns(payload.data.turns ?? []);
    }
    setLoadingTurns(false);
  };

  const refreshTurns = async (id: string): Promise<void> => {
    const response = await fetch(`/staff-api/conversations/${id}`, { cache: "no-store" });
    const payload = await parseJsonResponse<{ success: boolean; data: Conversation & { turns?: ConversationTurn[] } }>(response);
    if (payload?.success && payload.data) {
      setTurns(payload.data.turns ?? []);
    }
  };

  const handleTakeover = async (): Promise<void> => {
    if (!selectedId) return;
    const response = await fetch(`/staff-api/conversations/${selectedId}/handoff`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assigned_staff_id: null }),
    });
    if (response.ok) {
      setConversations((items) =>
        items.map((conv) => (conv.id === selectedId ? { ...conv, status: "HUMAN_TAKEOVER" as Conversation["status"] } : conv))
      );
    }
  };

  const handleSendMessage = async (): Promise<void> => {
    if (!selectedId || !staffMessage.trim()) return;
    setSending(true);
    const response = await fetch(`/staff-api/conversations/${selectedId}/staff-message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: staffMessage.trim() }),
    });
    const payload = await parseJsonResponse<ApiEnvelope<ConversationTurn>>(response);
    if (response.ok && payload?.success && payload.data) {
      setTurns((prev) => [...prev, payload.data!]);
      setStaffMessage("");
    }
    setSending(false);
  };

  const filteredConversations = conversations.filter(
    (conv) => conv.status === "ACTIVE" || conv.status === "WAITING_HUMAN" || conv.status === "HUMAN_TAKEOVER"
  );

  const selectedConv = conversations.find((c) => c.id === selectedId);
  const isInHandoff = handoffQueue.some((h) => h.conversation_id === selectedId);

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      <section className="w-80 shrink-0 space-y-2 overflow-y-auto rounded-xl border border-slate-200 bg-white p-3">
        <h2 className="mb-2 font-heading text-base font-semibold text-slate-900">Active conversations</h2>
        {filteredConversations.length ? (
          filteredConversations.map((conv) => {
            const handoff = handoffQueue.find((h) => h.conversation_id === conv.id);
            return (
              <button
                key={conv.id}
                className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition hover:bg-primary-light ${
                  selectedId === conv.id ? "border-primary bg-primary-light" : "border-slate-200"
                } ${handoff ? "border-warning/50 bg-warning/5" : ""}`}
                onClick={() => void selectConversation(conv.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {channelIcon(conv.channel)}
                    <span className="font-medium text-slate-900">{conv.channel}</span>
                  </div>
                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                    conv.status === "HUMAN_TAKEOVER" ? "bg-error/10 text-error" :
                    handoff ? "bg-warning/10 text-warning" : "bg-success/10 text-success"
                  }`}>
                    {handoff ? "Handoff" : conv.status === "HUMAN_TAKEOVER" ? "Staff" : "Active"}
                  </span>
                </div>
                <p className="mt-1 text-xs text-muted">{conv.session_id.slice(0, 16)}&hellip;</p>
                <p className="text-xs text-muted">{format(new Date(conv.started_at), "MMM d, h:mm a")}</p>
              </button>
            );
          })
        ) : (
          <p className="py-6 text-center text-sm text-muted">No active conversations.</p>
        )}
      </section>

      <section className="flex flex-1 flex-col rounded-xl border border-slate-200 bg-white">
        {selectedConv ? (
          <>
            <header className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <div>
                <h2 className="font-heading text-base font-semibold text-slate-900">
                  Conversation &mdash; {selectedConv.channel}
                </h2>
                <p className="text-xs text-muted">{selectedConv.session_id} &bull; {selectedConv.status}</p>
              </div>
              <div className="flex items-center gap-2">
                {selectedConv.status !== "HUMAN_TAKEOVER" ? (
                  <button
                    className="rounded-md border border-warning/40 px-3 py-1.5 text-xs font-medium text-warning hover:bg-warning/5"
                    onClick={() => void handleTakeover()}
                  >
                    Take over
                  </button>
                ) : null}
                <button
                  className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:border-primary hover:text-primary"
                  onClick={() => void refreshTurns(selectedConv.id)}
                >
                  Refresh
                </button>
              </div>
            </header>

            <div className="flex-1 space-y-3 overflow-y-auto p-4">
              {loadingTurns ? (
                <p className="py-10 text-center text-sm text-muted">Loading turns&hellip;</p>
              ) : turns.length ? (
                turns.map((turn) => (
                  <div key={turn.id} className={`flex ${turn.role === "user" ? "justify-start" : "justify-end"}`}>
                    <div className={`max-w-[75%] rounded-lg px-3 py-2 ${
                      turn.role === "user"
                        ? "bg-slate-100 text-slate-900"
                        : turn.role === "system"
                        ? "bg-warning/5 text-warning border border-warning/20"
                        : "bg-primary-light text-primary"
                    }`}>
                      <p className="text-xs font-medium text-muted">
                        {turn.role === "user" ? "Patient" : turn.role === "system" ? "System" : "Assistant"}
                        {turn.intent ? ` &mdash; ${turn.intent}` : ""}
                      </p>
                      <p className="mt-1 whitespace-pre-wrap text-sm">{turn.content}</p>
                      <p className="mt-1 text-[10px] text-muted">{format(new Date(turn.created_at), "h:mm a")}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="py-10 text-center text-sm text-muted">No messages in this conversation yet.</p>
              )}
              <div ref={threadEndRef} />
            </div>

            <div className="flex items-center gap-2 border-t border-slate-200 p-3">
              <input
                type="text"
                placeholder="Type a staff message..."
                value={staffMessage}
                onChange={(event) => setStaffMessage(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    void handleSendMessage();
                  }
                }}
                className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-primary"
              />
              <button
                className="rounded-md bg-primary p-2 text-white hover:bg-primary-hover disabled:opacity-50"
                disabled={!staffMessage.trim() || sending}
                onClick={() => void handleSendMessage()}
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </>
        ) : (
          <div className="flex flex-1 items-center justify-center">
            <p className="text-sm text-muted">Select a conversation from the left to view the thread.</p>
          </div>
        )}
      </section>
    </div>
  );
}

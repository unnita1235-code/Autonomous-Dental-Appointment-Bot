"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type ComponentType } from "react";
import { format } from "date-fns";
import { CalendarCheck2, Clock3, MessageCircleMore, ShieldCheck } from "lucide-react";

import { parseJsonResponse } from "@/lib/http";
import { useStaffDashboardStore } from "@/store/useStaffDashboardStore";
import type { Appointment, Conversation } from "@/types";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
}

interface MetricCardProps {
  title: string;
  value: string;
  description: string;
  icon: ComponentType<{ className?: string }>;
}

function MetricCard({ title, value, description, icon: Icon }: MetricCardProps): JSX.Element {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted">{title}</p>
          <p className="mt-1 font-heading text-2xl font-semibold text-slate-900">{value}</p>
        </div>
        <span className="rounded-lg bg-primary-light p-2 text-primary">
          <Icon className="h-5 w-5" />
        </span>
      </div>
      <p className="mt-3 text-xs text-muted">{description}</p>
    </article>
  );
}

export default function DashboardOverviewPage(): JSX.Element {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const handoffQueue = useStaffDashboardStore((state) => state.handoffQueue);
  const recentBookedAppointments = useStaffDashboardStore((state) => state.recentBookedAppointments);

  useEffect(() => {
    const loadData = async (): Promise<void> => {
      const [appointmentRes, conversationRes] = await Promise.all([
        fetch("/staff-api/appointments", { cache: "no-store" }),
        fetch("/staff-api/conversations?limit=50", { cache: "no-store" })
      ]);
      const appointmentPayload = await parseJsonResponse<ApiEnvelope<Appointment[]>>(appointmentRes);
      const conversationPayload = await parseJsonResponse<ApiEnvelope<Conversation[]>>(conversationRes);

      if (appointmentPayload?.success && appointmentPayload.data) {
        setAppointments(appointmentPayload.data);
      }
      if (conversationPayload?.success && conversationPayload.data) {
        setConversations(conversationPayload.data);
      }
    };
    void loadData();
  }, []);

  const todayCount = useMemo(() => {
    const today = new Date().toDateString();
    return appointments.filter((item) => new Date(item.start_time).toDateString() === today).length;
  }, [appointments]);

  const pendingConfirmations = useMemo(
    () => appointments.filter((item) => item.status === "PENDING").length,
    [appointments]
  );
  const activeConversations = useMemo(
    () => conversations.filter((item) => item.status === "ACTIVE").length,
    [conversations]
  );
  const humanTakeoverCount = useMemo(
    () => conversations.filter((item) => item.status === "HUMAN_TAKEOVER").length,
    [conversations]
  );
  const botResolutionRate = useMemo(() => {
    if (!conversations.length) {
      return 0;
    }
    const automated = conversations.length - humanTakeoverCount;
    return Math.max(0, Math.round((automated / conversations.length) * 100));
  }, [conversations, humanTakeoverCount]);

  const upcomingAppointments = useMemo(
    () =>
      appointments
        .filter((item) => new Date(item.start_time).getTime() >= Date.now())
        .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
        .slice(0, 5),
    [appointments]
  );

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Today's appointments"
          value={todayCount.toString()}
          description="Scheduled for today across all dentists."
          icon={CalendarCheck2}
        />
        <MetricCard
          title="Pending confirmations"
          value={pendingConfirmations.toString()}
          description="Appointments waiting for patient confirmation."
          icon={Clock3}
        />
        <MetricCard
          title="Bot resolution rate"
          value={`${botResolutionRate}%`}
          description="Conversations resolved without staff handoff."
          icon={ShieldCheck}
        />
        <MetricCard
          title="Active conversations"
          value={activeConversations.toString()}
          description="Patients currently engaged with the assistant."
          icon={MessageCircleMore}
        />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-heading text-lg font-semibold text-slate-900">Upcoming appointments</h2>
            <Link href="/dashboard/appointments" className="text-sm font-medium text-primary hover:text-primary-hover">
              View all
            </Link>
          </div>
          <div className="space-y-2">
            {upcomingAppointments.length ? (
              upcomingAppointments.map((item) => (
                <Link
                  key={item.id}
                  href="/dashboard/appointments"
                  className="block rounded-lg border border-slate-100 px-3 py-2 transition hover:border-primary/30 hover:bg-primary-light"
                >
                  <p className="text-sm font-medium text-slate-900">
                    {item.service?.name ?? "Service"} with Dr. {item.dentist?.last_name ?? "Assigned"}
                  </p>
                  <p className="text-xs text-muted">{format(new Date(item.start_time), "EEE, MMM d • h:mm a")}</p>
                </Link>
              ))
            ) : (
              <p className="text-sm text-muted">No upcoming appointments found.</p>
            )}
          </div>
        </article>

        <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-heading text-lg font-semibold text-slate-900">Live handoff queue</h2>
            <span className="rounded-full bg-primary-light px-2 py-0.5 text-xs font-medium text-primary">
              Real-time
            </span>
          </div>
          <div className="space-y-2">
            {handoffQueue.length ? (
              handoffQueue.map((item) => (
                <div key={item.conversation_id} className="rounded-lg border border-warning/30 bg-warning/5 px-3 py-2">
                  <p className="text-sm font-medium text-slate-900">Session {item.session_id}</p>
                  <p className="text-xs text-muted">
                    {item.channel} • waiting for staff {item.assigned_staff_id ? `• ${item.assigned_staff_id}` : ""}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted">No conversations currently waiting for human handoff.</p>
            )}
          </div>
          {recentBookedAppointments.length ? (
            <p className="mt-4 text-xs text-muted">
              Latest booking event: #{recentBookedAppointments[0].appointment.id.slice(0, 8)}
            </p>
          ) : null}
        </article>
      </section>
    </div>
  );
}

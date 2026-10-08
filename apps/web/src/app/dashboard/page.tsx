"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { format } from "date-fns";
import {
  Calendar,
  Clock,
  MessageCircle,
  ShieldCheck,
  Users,
  Activity,
  AlertCircle,
  CheckCircle,
  Zap,
  Bot,
  Bell,
  ArrowRight,
  ChevronRight,
} from "lucide-react";

import { parseJsonResponse } from "@/lib/http";
import { useStaffDashboardStore } from "@/store/useStaffDashboardStore";
import type { Appointment, Conversation } from "@/types";

import { MetricCard } from "@/components/dashboard/MetricCard";
import { AppointmentCard } from "@/components/dashboard/AppointmentCard";
import { AIActivityItem } from "@/components/ai/AIActivityItem";
import { AIIndicator } from "@/components/ai/AIIndicator";
import { EmptyState } from "@/components/ui/EmptyState";
import { SkeletonCard } from "@/components/ui/LoadingState";
import { DentalFlowLogo } from "@/components/branding";
import { Badge } from "@/components/ui/badge";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
}

export default function DashboardOverviewPage(): JSX.Element {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const handoffQueue = useStaffDashboardStore((state) => state.handoffQueue);
  const recentBookedAppointments = useStaffDashboardStore((state) => state.recentBookedAppointments);

  useEffect(() => {
    const loadData = async (): Promise<void> => {
      try {
        const [appointmentRes, conversationRes] = await Promise.all([
          fetch("/staff-api/appointments", { cache: "no-store" }),
          fetch("/staff-api/conversations?limit=50", { cache: "no-store" }),
        ]);
        const appointmentPayload = await parseJsonResponse<ApiEnvelope<Appointment[]>>(appointmentRes);
        const conversationPayload = await parseJsonResponse<ApiEnvelope<Conversation[]>>(conversationRes);

        if (appointmentPayload?.success && appointmentPayload.data) {
          setAppointments(appointmentPayload.data);
        }
        if (conversationPayload?.success && conversationPayload.data) {
          setConversations(conversationPayload.data);
        }
      } finally {
        setLoading(false);
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

  const needsAttentionAppointments = useMemo(
    () =>
      appointments
        .filter((item) => item.status === "PENDING" || item.status === "NO_SHOW")
        .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
        .slice(0, 5),
    [appointments]
  );

  // AI Activity Items for the timeline - must be before early returns
  const aiActivity = useMemo(() => {
    const activities: Array<{
      timestamp: string;
      eventType: string;
      description: string;
      status: "pending" | "completed" | "failed" | "processing";
      actor: "patient" | "staff" | "ai" | "system";
      patientName?: string;
      metadata?: Array<{ label: string; value: string }>;
    }> = [];

    // Handoff queue activities
    handoffQueue.forEach((item) => {
      activities.push({
        timestamp: item.started_at ?? new Date().toISOString(),
        eventType: "staff" as const,
        description: `Handoff needed: Session ${item.session_id} (${item.channel})`,
        status: "pending" as const,
        actor: "staff" as const,
        patientName: `Session ${item.session_id}`,
        metadata: [
          { label: "Channel", value: item.channel },
          { label: "Assigned", value: item.assigned_staff_id ?? "Unassigned" },
        ],
      });
    });

    // Recent bookings
    recentBookedAppointments.slice(0, 3).forEach((item) => {
      activities.push({
        timestamp: item.appointment.start_time,
        eventType: "appointment" as const,
        description: `New booking: ${item.appointment.id.slice(0, 8)}`,
        status: "completed" as const,
        actor: "ai" as const,
        metadata: [{ label: "Status", value: item.appointment.status }],
      });
    });

    // Conversation activities
    conversations.slice(0, 3).forEach((conv) => {
      activities.push({
        timestamp: conv.started_at,
        eventType: "web" as const,
        description: `Conversation ${conv.id.slice(0, 8)} - ${conv.status}`,
        status: conv.status === "ACTIVE" ? "pending" : "completed",
        actor: conv.status === "HUMAN_TAKEOVER" ? "staff" : "ai",
        metadata: [{ label: "Channel", value: conv.channel }],
      });
    });

    return activities.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).slice(0, 8);
  }, [handoffQueue, recentBookedAppointments, conversations]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }, (_, i) => (
            <SkeletonCard key={i} variant="compact" />
          ))}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <SkeletonCard variant="default" />
          <SkeletonCard variant="default" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with AI Status */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="font-heading text-headline-md font-bold text-staff-on-surface">Dashboard Overview</h1>
          <p className="text-staff-on-surface-muted text-sm mt-1">
            Real-time view of appointments, conversations, and AI activity
          </p>
        </div>
        <div className="flex items-center gap-3">
          <AIIndicator variant="active" size="sm" label="AI Active" animated={true} />
          <DentalFlowLogo size="sm" variant="primary" showText={true} />
        </div>
      </div>

      {/* Metrics Row */}
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" aria-label="Key metrics">
        <MetricCard
          title="Today's Appointments"
          value={todayCount.toString()}
          change="Scheduled for today across all dentists"
          icon={<Calendar className="h-5 w-5" />}
          iconBackground="primary"
          variant="staff"
        />
        <MetricCard
          title="Pending Confirmations"
          value={pendingConfirmations.toString()}
          change="Appointments waiting for patient confirmation"
          icon={<Clock className="h-5 w-5" />}
          iconBackground="warning"
          variant="staff"
        />
        <MetricCard
          title="Bot Resolution Rate"
          value={`${botResolutionRate}%`}
          change="Conversations resolved without staff handoff"
          icon={<ShieldCheck className="h-5 w-5" />}
          iconBackground="success"
          variant="staff"
        />
        <MetricCard
          title="Active Conversations"
          value={activeConversations.toString()}
          change="Patients currently engaged with the assistant"
          icon={<MessageCircle className="h-5 w-5" />}
          iconBackground="ai"
          variant="staff"
        />
      </section>

      {/* Main Content Grid */}
      <section className="grid gap-6 lg:grid-cols-3">
        {/* Upcoming Appointments - Full Width on Mobile, 2/3 on Desktop */}
        <article className="lg:col-span-2 space-y-6">
          {/* Upcoming Appointments */}
          <div className="rounded-xl border border-staff-border bg-staff-surface shadow-elevation-0">
            <div className="flex items-center justify-between p-4 border-b border-staff-border">
              <h2 className="font-heading text-label-lg font-semibold text-staff-on-surface">Upcoming Appointments</h2>
              <Link
                href="/dashboard/appointments"
                className="inline-flex items-center gap-1 text-sm font-medium text-staff-primary hover:text-staff-primary-hover"
              >
                View all
                <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
            <div className="p-4">
              {upcomingAppointments.length > 0 ? (
                <div className="space-y-2">
                  {upcomingAppointments.map((item) => (
                    <AppointmentCard
                      key={item.id}
                      id={item.id}
                      patientName={(item as any).patient ? `${(item as any).patient.first_name} ${(item as any).patient.last_name}` : "Unknown Patient"}
                      patientId={item.patient_id}
                      serviceName={item.service?.name ?? "Service"}
                      serviceDuration={item.service?.duration_minutes ?? 30}
                      dentistName={item.dentist ? `${item.dentist.first_name} ${item.dentist.last_name}` : "Unassigned"}
                      startTime={item.start_time}
                      endTime={item.time_slot?.end_time}
                      status={item.status}
                      sourceChannel={item.source_channel}
                      depositRequired={item.deposit_required}
                      depositPaid={item.deposit_paid}
                      depositAmount={item.deposit_amount ?? undefined}
                      paymentIntentId={item.stripe_payment_intent_id ?? undefined}
                      cancellationReason={item.cancellation_reason ?? undefined}
                      notes={item.notes ?? undefined}
                      isAIBooked={false}
                      variant="compact"
                      density="staff"
                    />
                  ))}
                </div>
              ) : (
                <EmptyState
                  size="sm"
                  icon="appointments"
                  title="No upcoming appointments"
                  description="No appointments scheduled for the coming days."
                />
              )}
            </div>
          </div>

          {/* Needs Attention Panel */}
          {needsAttentionAppointments.length > 0 && (
            <div className="rounded-xl border border-staff-warning/30 bg-staff-warning-container/10 shadow-elevation-0">
              <div className="flex items-center justify-between p-4 border-b border-staff-warning/20">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-staff-warning" />
                  <h2 className="font-heading text-label-lg font-semibold text-staff-on-surface">Needs Attention</h2>
                  <Badge variant="warning" dot size="sm">{needsAttentionAppointments.length} items</Badge>
                </div>
              </div>
              <div className="p-4 space-y-2">
                {needsAttentionAppointments.map((item) => (
                  <AppointmentCard
                    key={item.id}
                    id={item.id}
                    patientName={(item as any).patient ? `${(item as any).patient.first_name} ${(item as any).patient.last_name}` : "Unknown Patient"}
                    patientId={item.patient_id}
                    serviceName={item.service?.name ?? "Service"}
                    serviceDuration={item.service?.duration_minutes ?? 30}
                    dentistName={item.dentist ? `${item.dentist.first_name} ${item.dentist.last_name}` : "Unassigned"}
                    startTime={item.start_time}
                    endTime={item.time_slot?.end_time}
                    status={item.status}
                    sourceChannel={item.source_channel}
                    depositRequired={item.deposit_required}
                    depositPaid={item.deposit_paid}
                    depositAmount={item.deposit_amount ?? undefined}
                    paymentIntentId={item.stripe_payment_intent_id ?? undefined}
                    cancellationReason={item.cancellation_reason ?? undefined}
                    notes={item.notes ?? undefined}
                    isAIBooked={false}
                    needsAttention={true}
                    attentionReason={item.status === "PENDING" ? "Awaiting patient confirmation" : "Patient no-show"}
                    variant="attention"
                    density="staff"
                  />
                ))}
              </div>
            </div>
          )}
        </article>

        {/* Right Column: Live Handoff Queue + AI Activity */}
        <aside className="space-y-6">
          {/* Live Handoff Queue */}
          <article className="rounded-xl border border-staff-border bg-staff-surface shadow-elevation-0">
            <div className="flex items-center justify-between p-4 border-b border-staff-border">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-staff-ai" />
                <h2 className="font-heading text-label-lg font-semibold text-staff-on-surface">Live Handoff Queue</h2>
              </div>
              <Badge variant="ai" size="sm" dot dotColor="ai">Real-time</Badge>
            </div>
            <div className="p-4">
              {handoffQueue.length > 0 ? (
                <div className="space-y-3">
                  {handoffQueue.map((item) => (
                    <div
                      key={item.conversation_id}
                      className="rounded-lg border border-staff-border bg-staff-surface-variant p-3"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-medium text-staff-on-surface">Session {item.session_id.slice(0, 8)}</p>
                        <AIIndicator variant="handoff" size="sm" label="Handoff" />
                      </div>
                      <p className="text-sm text-staff-on-surface-variant">
                        {item.channel} • {item.assigned_staff_id ? `Assigned: ${item.assigned_staff_id}` : "Unassigned"}
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <span className="px-2 py-1 text-caption rounded-full bg-staff-primary/10 text-staff-primary">
                          {item.status ?? "HUMAN_TAKEOVER"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <MessageCircle className="h-10 w-10 text-staff-on-surface-muted mx-auto mb-2" />
                  <p className="text-staff-on-surface-muted text-sm">No conversations waiting for human handoff</p>
                </div>
              )}
            </div>
          </article>

          {/* AI Activity Timeline */}
          <article className="rounded-xl border border-staff-border bg-staff-surface shadow-elevation-0">
            <div className="flex items-center justify-between p-4 border-b border-staff-border">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-staff-ai" />
                <h2 className="font-heading text-label-lg font-semibold text-staff-on-surface">AI Activity</h2>
              </div>
              <AIIndicator variant="active" size="sm" label="Processing" animated={true} />
            </div>
            <div className="p-4">
              {aiActivity.length > 0 ? (
                <div className="space-y-3">
                  {aiActivity.map((activity, index) => (
                    <AIActivityItem
                      key={index}
                      {...activity}
                      variant="compact"
                      density="staff"
                      tone={activity.actor === "ai" ? "ai" : activity.actor === "staff" ? "info" : "neutral"}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Bot className="h-10 w-10 text-staff-on-surface-muted mx-auto mb-2" />
                  <p className="text-staff-on-surface-muted text-sm">No recent AI activity</p>
                </div>
              )}
            </div>
          </article>

          {/* Recent Bookings */}
          {recentBookedAppointments.length > 0 && (
            <article className="rounded-xl border border-staff-border bg-staff-surface shadow-elevation-0">
              <div className="flex items-center justify-between p-4 border-b border-staff-border">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-staff-success" />
                  <h2 className="font-heading text-label-lg font-semibold text-staff-on-surface">Recent Bookings</h2>
                </div>
              </div>
              <div className="p-4 space-y-3">
                {recentBookedAppointments.slice(0, 5).map((item) => (
                  <div
                    key={item.appointment.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-staff-surface-variant"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-staff-success-container flex items-center justify-center">
                        <CheckCircle className="h-4 w-4 text-staff-on-success-container" />
                      </div>
                      <div>
                        <p className="font-medium text-staff-on-surface text-sm">
                          Appointment #{item.appointment.id.slice(0, 8)}
                        </p>
                        <p className="text-caption text-staff-on-surface-variant">
                          {format(new Date(item.appointment.start_time), "MMM d, h:mm a")}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={item.appointment.status === "CONFIRMED" ? "success" : "warning"}
                      size="sm"
                    >
                      {item.appointment.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </article>
          )}
        </aside>
      </section>

      {/* AI Insights Banner */}
      <section className="rounded-2xl border border-staff-ai/30 bg-staff-ai-container/10 p-6 shadow-ai-glow">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-staff-ai text-staff-on-ai">
              <Bot className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-heading text-label-lg font-semibold text-staff-on-surface">DentalFlow AI Assistant</h3>
              <p className="text-staff-on-surface-variant text-sm">
                Analyzing schedules, optimizing appointments, and handling patient conversations 24/7
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="ai" size="lg">
              {botResolutionRate}% Bot Resolution
            </Badge>
            <Badge variant="success" size="lg" dot>
              {handoffQueue.length} Active Handoffs
            </Badge>
            <Link
              href="/dashboard/analytics"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl font-semibold text-sm text-staff-ai bg-staff-ai-container/50 hover:bg-staff-ai-container transition-colors"
            >
              View Analytics
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
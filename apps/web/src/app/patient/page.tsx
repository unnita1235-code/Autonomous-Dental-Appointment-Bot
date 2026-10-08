"use client";

import * as React from "react";
import { format } from "date-fns";
import {
  Calendar,
  Clock,
  MessageCircle,
  Zap,
  Heart,
  Shield,
  Users,
  ChevronRight,
  Bell,
  Plus,
  Sparkles,
  Bot,
  ArrowRight,
} from "lucide-react";

import { cn } from "@/lib/design-system";
import { PatientSummaryCard } from "@/components/patient/PatientSummaryCard";
import { AppointmentCard } from "@/components/dashboard/AppointmentCard";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { AIRecommendationCard } from "@/components/ai/AIRecommendationCard";
import { AIIndicator } from "@/components/ai/AIIndicator";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton, SkeletonCard } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import ChatWidget from "@/components/chat/ChatWidget";
import { DentalFlowLogo } from "@/components/branding";

import type { Patient, Appointment, AppointmentStatus } from "@/types";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

const statusConfig = {
  PENDING: { label: "Pending", variant: "warning" as const, icon: Clock },
  CONFIRMED: { label: "Confirmed", variant: "success" as const, icon: Calendar },
  COMPLETED: { label: "Completed", variant: "success" as const, icon: Calendar },
  CANCELLED: { label: "Cancelled", variant: "error" as const, icon: Shield },
  NO_SHOW: { label: "No Show", variant: "error" as const, icon: Shield },
} as const;

const quickActions = [
  {
    key: "book",
    label: "Book Appointment",
    description: "Schedule a new visit",
    icon: <Plus className="h-5 w-5" />,
    color: "bg-patient-primary",
    href: "/booking",
  },
  {
    key: "message",
    label: "Message Dentist",
    description: "Chat with your care team",
    icon: <MessageCircle className="h-5 w-5" />,
    color: "bg-patient-secondary",
    href: "/messages",
  },
  {
    key: "records",
    label: "View Records",
    description: "Access your dental history",
    icon: <Heart className="h-5 w-5" />,
    color: "bg-staff-success",
    href: "/records",
  },
  {
    key: "ai",
    label: "AI Analysis",
    description: "Get personalized insights",
    icon: <Sparkles className="h-5 w-5" />,
    color: "bg-staff-ai",
    href: "/ai-insights",
  },
];

export default function PatientHomePage(): JSX.Element {
  const [patient, setPatient] = React.useState<Patient | null>(null);
  const [appointments, setAppointments] = React.useState<Appointment[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const loadPatientData = async (): Promise<void> => {
      try {
        setLoading(true);
        const [patientRes, appointmentsRes] = await Promise.all([
          fetch("/api/patient/me", { cache: "no-store" }),
          fetch("/api/appointments?patient=me", { cache: "no-store" }),
        ]);

        const patientData = await patientRes.json();
        const appointmentsData = await appointmentsRes.json();

        if (patientData?.success && patientData.data) {
          setPatient(patientData.data);
        }
        if (appointmentsData?.success && appointmentsData.data) {
          setAppointments(appointmentsData.data);
        }
      } catch (err) {
        setError("Failed to load patient data");
        console.error("Failed to load patient data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadPatientData();
  }, []);

  // Compute derived state before early returns to satisfy hooks rules
  const upcomingAppointments = React.useMemo(() => {
    const now = new Date();
    return appointments
      .filter((a) => new Date(a.start_time) >= now && a.status !== "CANCELLED" && a.status !== "NO_SHOW")
      .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
      .slice(0, 3);
  }, [appointments]);

  const pastAppointments = React.useMemo(() => {
    return appointments
      .filter((a) => a.status === "COMPLETED" || a.status === "CANCELLED" || a.status === "NO_SHOW")
      .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())
      .slice(0, 3);
  }, [appointments]);

  const metrics = React.useMemo(() => [
    {
      title: "Upcoming Visits",
      value: upcomingAppointments.length.toString(),
      change: upcomingAppointments.length > 0 ? "Next appointment soon" : "No upcoming visits",
      icon: <Calendar className="h-5 w-5" />,
      iconBackground: "primary" as const,
    },
    {
      title: "Completed This Year",
      value: appointments.filter((a) => a.status === "COMPLETED").length.toString(),
      change: "Appointments completed",
      icon: <Heart className="h-5 w-5" />,
      iconBackground: "success" as const,
    },
    ], [appointments, upcomingAppointments.length]);

  const mapAppointmentToCardProps = (appt: Appointment) => ({
    id: appt.id,
    patientName: `${patient?.first_name ?? "Patient"} ${patient?.last_name ?? ""}`,
    patientId: patient?.id ?? "",
    serviceName: appt.service?.name ?? "Service",
    serviceDuration: appt.service?.duration_minutes ?? 30,
    dentistName: `${appt.dentist?.first_name ?? "Dr."} ${appt.dentist?.last_name ?? ""}`,
    startTime: appt.start_time,
    endTime: appt.time_slot?.end_time,
    status: appt.status,
    sourceChannel: appt.source_channel,
    depositRequired: appt.deposit_required,
    depositPaid: appt.deposit_paid,
    depositAmount: appt.deposit_amount ?? undefined,
    paymentIntentId: appt.stripe_payment_intent_id ?? undefined,
    cancellationReason: appt.cancellation_reason ?? undefined,
    notes: appt.notes ?? undefined,
    isAIBooked: false,
    needsAttention: appt.status === "PENDING",
    attentionReason: appt.status === "PENDING" ? "Awaiting confirmation" : undefined,
  });

  if (loading) {
    return (
      <div className="space-y-6">
        <SkeletonCard variant="detailed" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }, (_, i) => (
            <SkeletonCard key={i} variant="compact" />
          ))}
        </div>
        <SkeletonCard variant="default" />
        <SkeletonCard variant="default" />
        <SkeletonCard variant="default" />
      </div>
    );
  }

  if (error || !patient) {
    return (
      <ErrorState
        title="Unable to load your profile"
        description={error ?? "We couldn't load your patient information. Please try again."}
        primaryAction={{ label: "Retry", onClick: () => window.location.reload() }}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <section className="rounded-2xl bg-gradient-to-br from-patient-primary to-patient-primary-hover p-6 md:p-8 text-white shadow-elevation-2">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <p className="text-patient-on-primary/80 text-sm font-medium">Welcome back,</p>
            <h1 className="font-heading text-headline-md font-bold mt-1">
              {patient.first_name} {patient.last_name}
            </h1>
            <p className="mt-2 text-patient-on-primary/70 text-sm">
              Your next appointment is <strong>{upcomingAppointments[0] ? format(new Date(upcomingAppointments[0].start_time), "EEEE, MMM d 'at' h:mm a") : "not scheduled"}</strong>
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <a
              href="/booking"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white/10 text-white font-semibold hover:bg-white/20 transition-colors backdrop-blur-sm"
            >
              <Plus className="h-5 w-5" />
              Book Appointment
            </a>
            <a
              href="/messages"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white/10 text-white font-semibold hover:bg-white/20 transition-colors backdrop-blur-sm"
            >
              <MessageCircle className="h-5 w-5" />
              Message Team
            </a>
          </div>
        </div>
      </section>

      {/* Quick Actions Grid */}
      <section>
        <h2 className="font-heading text-label-lg font-semibold text-patient-on-surface mb-4">Quick Actions</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {quickActions.map((action) => (
            <a
              key={action.key}
              href={action.href}
              className={cn(
                "relative flex flex-col items-start justify-between p-4 rounded-2xl transition-all duration-200",
                "hover:shadow-elevation-hover hover:-translate-y-0.5",
                action.color,
                "text-white"
              )}
            >
              <div className="flex items-center justify-between w-full">
                <span className="p-3 rounded-xl bg-white/20">{action.icon}</span>
                <ChevronRight className="h-5 w-5 opacity-70" />
              </div>
              <div className="mt-4">
                <h3 className="font-semibold text-label-md">{action.label}</h3>
                <p className="text-sm opacity-80 mt-0.5">{action.description}</p>
              </div>
            </a>
          ))}
        </div>
      </section>

      {/* Metrics */}
      <section>
        <h2 className="font-heading text-label-lg font-semibold text-patient-on-surface mb-4">Your Overview</h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric, index) => (
            <MetricCard
              key={index}
              variant="patient"
              {...metric}
            />
          ))}
        </div>
      </section>

      {/* Upcoming Appointments */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading text-label-lg font-semibold text-patient-on-surface">Upcoming Appointments</h2>
          <a
            href="/patient/appointments"
            className="inline-flex items-center gap-1 text-sm font-medium text-patient-primary hover:text-patient-primary-hover"
          >
            View all
            <ChevronRight className="h-4 w-4" />
          </a>
        </div>
        {upcomingAppointments.length > 0 ? (
          <div className="space-y-3">
            {upcomingAppointments.map((appointment) => (
              <AppointmentCard
                key={appointment.id}
                {...mapAppointmentToCardProps(appointment)}
                variant="default"
                density="patient"
                onView={() => {}}
                onReschedule={() => {}}
                onCancel={() => {}}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            size="sm"
            variant="default"
            icon="appointments"
            title="No upcoming appointments"
            description="Schedule your next visit to keep your dental health on track."
            primaryAction={{ label: "Book Appointment", onClick: () => {}, variant: "primary" }}
          />
        )}
      </section>

      {/* AI Recommendations */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading text-label-lg font-semibold text-patient-on-surface">AI Insights</h2>
        </div>
        <p className="text-body-md text-patient-on-surface-variant">
          Personalised recommendations are not available on your account yet.
        </p>
      </section>

      {/* Past Appointments */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading text-label-lg font-semibold text-patient-on-surface">Recent History</h2>
          <a
            href="/patient/appointments"
            className="inline-flex items-center gap-1 text-sm font-medium text-patient-primary hover:text-patient-primary-hover"
          >
            View all
            <ChevronRight className="h-4 w-4" />
          </a>
        </div>
        {pastAppointments.length > 0 ? (
          <div className="space-y-3">
            {pastAppointments.map((appointment) => (
              <AppointmentCard
                key={appointment.id}
                {...mapAppointmentToCardProps(appointment)}
                variant="compact"
                density="patient"
              />
            ))}
          </div>
        ) : (
          <EmptyState
            size="sm"
            variant="default"
            icon="appointments"
            title="No past appointments"
            description="Your appointment history will appear here after your first visit."
          />
        )}
      </section>

      {/* AI Activity Section */}
      <section>
        <h2 className="font-heading text-label-lg font-semibold text-patient-on-surface mb-4">Recent Activity</h2>
        <p className="text-body-md text-patient-on-surface-variant">
          Activity history is not available on your account yet.
        </p>
      </section>

      {/* Footer CTA */}
      <section className="rounded-2xl bg-staff-surface border border-staff-border p-6 md:p-8 text-center">
        <div className="flex items-center justify-center gap-2 mb-3">
          <Sparkles className="h-6 w-6 text-staff-ai" />
          <h2 className="font-heading text-headline-sm font-semibold text-staff-on-surface">
            DentalFlow AI is here to help
          </h2>
        </div>
        <p className="text-staff-on-surface-variant max-w-md mx-auto mb-6">
          Our AI assistant can help you book appointments, answer questions about your treatment,
          and provide personalized oral health insights 24/7.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <ChatWidget />
        </div>
      </section>
    </div>
  );
}
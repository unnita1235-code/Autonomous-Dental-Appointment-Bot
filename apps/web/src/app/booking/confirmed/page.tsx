"use client";

import * as React from "react";
import { format } from "date-fns";
import {
  Calendar,
  Clock,
  MapPin,
  CheckCircle,
  ArrowRight,
  Phone,
  Mail,
  Car,
  Shield,
  Check,
  X,
  AlertCircle,
  Loader2,
} from "lucide-react";

import { cn } from "@/lib/design-system";
import { AppointmentCard } from "@/components/dashboard/AppointmentCard";
import { AIIndicator } from "@/components/ai/AIIndicator";
import { EmptyState } from "@/components/ui/EmptyState";
import { SkeletonCard } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DentalFlowLogo } from "@/components/branding";
import { MobileBottomNav, patientNavItems } from "@/components/ui/MobileBottomNav";

import type { Appointment, Patient, DentistBrief, TimeSlot } from "@/types";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

interface ConfirmationPageProps {
  searchParams: Promise<{ id?: string }>;
}

function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} minutes`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

export default function BookingConfirmedPage({ searchParams }: ConfirmationPageProps): JSX.Element {
  const [appointment, setAppointment] = React.useState<Appointment | null>(null);
  const [patient, setPatient] = React.useState<Patient | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [calendarAdded, setCalendarAdded] = React.useState(false);
  const [activeNavKey, setActiveNavKey] = React.useState("home");

  React.useEffect(() => {
    const loadAppointment = async (): Promise<void> => {
      try {
        setLoading(true);
        const params = await searchParams;
        const appointmentId = params.id;

        if (!appointmentId) {
          setError("No appointment ID provided");
          return;
        }

        // Fetch appointment and patient in parallel
        const [appointmentRes, patientRes] = await Promise.all([
          fetch(`/api/appointments/${appointmentId}`, { cache: "no-store" }),
          fetch(`/api/patient/me`, { cache: "no-store" }), // This gets current user's patient data
        ]);

        const appointmentData = await appointmentRes.json();
        const patientData = await patientRes.json();

        if (appointmentData?.success && appointmentData.data) {
          setAppointment(appointmentData.data);
        } else {
          setError(appointmentData?.error ?? "Appointment not found");
          return;
        }

        if (patientData?.success && patientData.data) {
          setPatient(patientData.data);
        }
      } catch (err) {
        setError("Failed to load appointment details");
        console.error("Failed to load appointment:", err);
      } finally {
        setLoading(false);
      }
    };

    loadAppointment();
  }, [searchParams]);

  const handleAddToCalendar = () => {
    if (!appointment) return;

    const startDate = new Date(appointment.start_time);
    const endDate = new Date(startDate.getTime() + (appointment.service?.duration_minutes ?? 30) * 60 * 1000);

    const formatDate = (date: Date): string =>
      date.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";

    const params = new URLSearchParams({
      action: "TEMPLATE",
      text: `Dental Appointment - ${appointment.service?.name}`,
      dates: `${formatDate(startDate)}/${formatDate(endDate)}`,
      details: `Appointment ID: ${appointment.id}\nDentist: ${appointment.dentist?.first_name} ${appointment.dentist?.last_name}\nPatient: ${patient?.first_name} ${patient?.last_name}`,
    });

    window.open(`https://calendar.google.com/calendar/render?${params.toString()}`, "_blank");
    setCalendarAdded(true);
    setTimeout(() => setCalendarAdded(false), 3000);
  };

  const handleGetDirections = () => {
    if (!appointment) return;
    window.open("https://maps.google.com/?q=Dental+Clinic", "_blank");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-patient-surface-lowest">
        <main id="main-content" className="mx-auto max-w-2xl px-4 py-8">
          <SkeletonCard variant="detailed" />
          <SkeletonCard variant="default" />
          <SkeletonCard variant="default" />
        </main>
      </div>
    );
  }

  if (error || !appointment) {
    return (
      <div className="min-h-screen bg-patient-surface-lowest">
        <main id="main-content" className="mx-auto max-w-2xl px-4 py-8">
          <ErrorState
            title="Unable to load confirmation"
            description={error ?? "We couldn't find your appointment details. Please try again or contact the clinic."}
            primaryAction={{ label: "Go Home", onClick: () => window.location.href = "/" }}
            secondaryAction={{ label: "Contact Support", onClick: () => window.location.href = "/contact" }}
          />
        </main>
      </div>
    );
  }

  // Appointment is loaded
  const patientName = patient
    ? `${patient.first_name} ${patient.last_name}`
    : "Patient";

  const dentistName = appointment.dentist
    ? `${appointment.dentist.first_name} ${appointment.dentist.last_name}`
    : "Dentist";

  const appointmentDate = format(new Date(appointment.start_time), "EEEE, MMM d, yyyy");
  const appointmentTime = format(new Date(appointment.start_time), "h:mm a");

  const isConfirmed = appointment.status === "CONFIRMED";
  const isPending = appointment.status === "PENDING";

  return (
    <div className="min-h-screen bg-patient-surface-lowest">
      {/* Header */}
      <header className="sticky top-0 z-40 w-full border-b border-patient-outline-variant bg-patient-surface-lowest/95 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-2xl items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <DentalFlowLogo size="default" variant="patient" showText={false} />
            <p className="font-heading text-label-lg font-semibold text-patient-on-surface">Booking Confirmed</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="flex-1 pb-24">
        <div className="mx-auto max-w-2xl px-4 py-6 space-y-6">
          {/* Success Hero Section */}
          <section className="text-center space-y-4">
            {/* Animated Checkmark */}
            <div className="relative flex items-center justify-center mx-auto mb-4">
              <div className="absolute w-24 h-24 rounded-full bg-patient-success-container/30 blur-xl animate-pulse" aria-hidden="true" />
              <div className="relative w-20 h-20 rounded-full bg-patient-success flex items-center justify-center shadow-[0_8px_24px_rgba(0,108,73,0.24)]">
                <CheckCircle className="w-10 h-10 text-patient-on-success" strokeWidth={3.5} />
              </div>
            </div>

            <h1 className="font-heading text-headline-xl font-bold text-patient-on-surface">
              You&apos;re Booked!
            </h1>

            <p className="text-body-lg text-patient-on-surface-variant">
              Your appointment has been successfully booked.
            </p>

            {/* Reference Info */}
            <div className="inline-flex flex-wrap items-center justify-center gap-2 px-4 py-2 rounded-full bg-patient-surface border border-patient-outline-variant">
              <span className="flex items-center gap-1.5 text-sm text-patient-on-surface">
                <Mail className="h-4 w-4 text-patient-secondary" />
                SMS sent to <strong className="text-patient-on-surface">your mobile number</strong>
              </span>
              <span className="text-patient-on-surface-variant">•</span>
              <span className="flex items-center gap-1 text-sm text-patient-on-surface">
                <Shield className="h-4 w-4 text-patient-primary" />
                Booking ID: <strong className="font-mono">{appointment.id.slice(0, 8).toUpperCase()}</strong>
              </span>
            </div>
          </section>

          {/* Primary Appointment Details Card */}
          <section className="rounded-2xl border border-patient-outline-variant bg-patient-surface-lowest shadow-elevation-1 p-4 md:p-6 space-y-5">
            {/* Service & Duration Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-patient-outline-variant">
              <div className="space-y-1">
                <Badge variant="patient" size="sm">
                  {appointment.service?.name ?? "Appointment"}
                </Badge>
                <h2 className="font-heading text-headline-md font-bold text-patient-on-surface">
                  {appointment.service?.name ?? "Dental Appointment"}
                </h2>
              </div>
              <Badge variant="patient" size="default" className="shrink-0">
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  <span className="font-medium">{formatDuration(appointment.service?.duration_minutes ?? 30)}</span>
                </span>
              </Badge>
            </div>

            {/* Dentist Profile */}
            <div className="flex items-center gap-4 p-4 rounded-xl bg-patient-surface border border-patient-outline-variant">
              <div className="w-14 h-14 rounded-full bg-patient-primary-container/50 flex items-center justify-center shrink-0">
                {appointment.dentist?.first_name && appointment.dentist?.last_name ? (
                  <span className="font-heading text-label-lg font-bold text-patient-on-primary">
                    {appointment.dentist.first_name[0]}{appointment.dentist.last_name[0]}
                  </span>
                ) : (
                  <span className="font-heading text-label-lg font-bold text-patient-on-primary">DDS</span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-heading text-label-lg font-semibold text-patient-on-surface truncate">
                    Dr. {dentistName}
                  </h3>
                </div>
                <p className="text-body-md text-patient-on-surface-variant truncate">
                  {appointment.service?.name ?? "Dental Service"} · Main Clinic
                </p>
              </div>
            </div>

            {/* Date & Time Highlight */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-4 rounded-xl bg-patient-surface border border-patient-outline-variant">
              {/* Date */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-patient-primary-container flex items-center justify-center shrink-0">
                  <Calendar className="h-5 w-5 text-patient-on-primary-container" />
                </div>
                <div>
                  <p className="text-caption text-patient-on-surface-variant uppercase tracking-wider font-semibold">
                    Appointment Date
                  </p>
                  <p className="font-heading text-label-md font-bold text-patient-on-surface">
                    {appointmentDate}
                  </p>
                </div>
              </div>
              {/* Time */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-patient-secondary-fixed flex items-center justify-center shrink-0">
                  <Clock className="h-5 w-5 text-patient-on-secondary-fixed" />
                </div>
                <div>
                  <p className="text-caption text-patient-on-surface-variant uppercase tracking-wider font-semibold">
                    Scheduled Time
                  </p>
                  <p className="font-heading text-label-md font-bold text-patient-on-surface">
                    {appointmentTime}
                  </p>
                </div>
              </div>
            </div>

            {/* Location */}
            <div className="space-y-3 p-4 rounded-xl bg-patient-surface border border-patient-outline-variant">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-patient-surface-variant flex items-center justify-center shrink-0">
                  <MapPin className="h-5 w-5 text-patient-on-surface-variant" />
                </div>
                <div className="flex-1">
                  <p className="text-label-lg font-semibold text-patient-on-surface">
                    Clinic location
                  </p>
                  <p className="text-body-md text-patient-on-surface-variant">
                    Contact the clinic for the appointment address.
                  </p>
                </div>
              </div>
              {/* Map is intentionally omitted: no clinic location is provided by the API. */}
            </div>

            {/* Payment / Insurance Coverage */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-patient-surface border border-patient-outline-variant">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-patient-success-container flex items-center justify-center shrink-0">
                  <Shield className="h-5 w-5 text-patient-on-success-container" />
                </div>
                <div>
                  <p className="text-label-md font-semibold text-patient-on-surface">
                    {patient?.insurance_provider ? "Insurance on file" : "Insurance"}
                  </p>
                  <p className="text-body-md text-patient-on-surface-variant">
                    Coverage is not verified online. Please confirm with the clinic.
                  </p>
                </div>
              </div>
              {appointment.deposit_amount != null && (
                <div className="text-right shrink-0">
                  <span className="font-heading text-headline-sm font-bold text-patient-success">
                    ${appointment.deposit_amount}
                  </span>
                  <p className="text-caption text-patient-on-surface-variant">
                    {appointment.deposit_paid ? "Deposit paid" : "Deposit due"}
                  </p>
                </div>
              )}
            </div>
          </section>

          {/* Action Buttons */}
          <section className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Button
                onClick={handleAddToCalendar}
                variant="primary"
                size="lg"
                className="min-h-[52px] justify-center gap-2"
                disabled={calendarAdded}
              >
                <Calendar className="h-5 w-5" />
                {calendarAdded ? "Added to Calendar!" : "Add to Calendar"}
              </Button>
              <Button
                onClick={handleGetDirections}
                variant="outline"
                size="lg"
                className="min-h-[52px] justify-center gap-2"
              >
                <MapPin className="h-5 w-5" />
                Get Directions
              </Button>
            </div>

            {/* Secondary Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
              <Button
                variant="ghost"
                onClick={() => window.location.href = `/patient/appointments/${appointment.id}`}
                className="min-h-[48px] px-4"
              >
                View Details
              </Button>
              <span className="w-1 h-1 rounded-full bg-patient-outline-variant sm:hidden" />
              <Button
                variant="ghost"
                onClick={() => window.location.href = `/booking/reschedule?id=${appointment.id}`}
                className="min-h-[48px] px-4"
              >
                Reschedule
              </Button>
              <span className="w-1 h-1 rounded-full bg-patient-outline-variant sm:hidden" />
              <Button
                variant="ghost"
                onClick={() => window.location.href = `/booking/cancel?id=${appointment.id}`}
                className="min-h-[48px] px-4 text-patient-error hover:text-patient-error-hover"
              >
                Cancel
              </Button>
            </div>
          </section>

          {/* What to Bring Checklist */}
          <section className="rounded-2xl border border-patient-outline-variant bg-patient-surface-lowest shadow-elevation-1 p-4 md:p-6 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-full bg-patient-primary-container flex items-center justify-center">
                <Check className="h-5 w-5 text-patient-on-primary-container" />
              </div>
              <h3 className="font-heading text-label-lg font-semibold text-patient-on-surface">
                What to Bring
              </h3>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-3 min-h-[48px] p-3 rounded-lg bg-patient-surface border border-patient-outline-variant cursor-pointer select-none transition-colors hover:bg-patient-surface-variant">
                <input type="checkbox" className="w-5 h-5 rounded accent-patient-primary" />
                <span className="text-body-md text-patient-on-surface">Government Photo ID</span>
              </label>
              <label className="flex items-center gap-3 min-h-[48px] p-3 rounded-lg bg-patient-surface border border-patient-outline-variant cursor-pointer select-none transition-colors hover:bg-patient-surface-variant">
                <input type="checkbox" className="w-5 h-5 rounded accent-patient-primary" />
                <span className="text-body-md text-patient-on-surface">Dental Insurance Card</span>
              </label>
              <label className="flex items-center gap-3 min-h-[48px] p-3 rounded-lg bg-patient-surface border border-patient-outline-variant cursor-pointer select-none transition-colors hover:bg-patient-surface-variant">
                <input type="checkbox" className="w-5 h-5 rounded accent-patient-primary" />
                <span className="text-body-md text-patient-on-surface">Arrive 10 minutes early</span>
              </label>
            </div>
          </section>

          {/* Contact Footer */}
          <div className="text-center space-y-1 text-patient-on-surface-variant">
            <p className="text-body-md">
              Need to speak with a human right away? Call the clinic using the
              number on your appointment reminder.
            </p>
            <p className="text-caption">
              Reply <span className="font-semibold text-patient-on-surface">STOP</span> to opt out of SMS reminders.
            </p>
          </div>
        </div>
      </main>

      {/* Mobile Bottom Navigation */}
      <MobileBottomNav
        items={patientNavItems}
        activeKey={activeNavKey}
        onChange={setActiveNavKey}
        variant="patient"
        layout="floating"
        safeArea={true}
      />
    </div>
  );
}
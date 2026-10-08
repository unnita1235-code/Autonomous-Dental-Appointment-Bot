"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Calendar, Clock, MapPin, Users, CreditCard, AlertCircle, CheckCircle, MoreHorizontal, ChevronDown, Phone, MessageCircle, XCircle } from "lucide-react";

import { cn } from "@/lib/design-system";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Chip } from "@/components/ui/chip";

/* ============================================================
   Types (using existing domain types where available)
   ============================================================ */

export interface AppointmentCardProps {
  id: string;
  patientName: string;
  patientAvatar?: string;
  patientId?: string;
  serviceName: string;
  serviceDuration: number;
  dentistName: string;
  dentistAvatar?: string;
  startTime: string;
  endTime?: string;
  status: "PENDING" | "CONFIRMED" | "COMPLETED" | "CANCELLED" | "NO_SHOW";
  sourceChannel: "web" | "whatsapp" | "sms" | "voice" | "staff";
  depositRequired?: boolean;
  depositPaid?: boolean;
  depositAmount?: string;
  paymentIntentId?: string;
  cancellationReason?: string;
  notes?: string;
  isAIBooked?: boolean;
  aiConfidence?: number;
  needsAttention?: boolean;
  attentionReason?: string;
  onView?: () => void;
  onEdit?: () => void;
  onCancel?: () => void;
  onReschedule?: () => void;
  onCallPatient?: () => void;
  onMessagePatient?: () => void;
  onViewChat?: () => void;
  className?: string;
  variant?: "default" | "compact" | "expanded" | "attention" | "ai";
  density?: "patient" | "staff";
  children?: React.ReactNode;
}

const appointmentCardVariants = cva(
  "relative rounded-2xl border transition-all duration-200",
  {
    variants: {
      variant: {
        default: "bg-staff-surface border-staff-border shadow-elevation-0 hover:shadow-elevation-1",
        compact: "bg-staff-surface border-staff-border shadow-elevation-0",
        expanded: "bg-staff-surface border-staff-border shadow-elevation-1",
        attention: "bg-staff-warning-container/10 border-staff-warning/30 shadow-elevation-1",
        ai: "bg-staff-surface border-staff-ai/30 shadow-ai-glow",
      },
      density: {
        patient: "",
        staff: "",
      },
    },
    defaultVariants: {
      variant: "default",
      density: "staff",
    },
  }
);

const statusConfig = {
  PENDING: { label: "Pending", variant: "warning" as const, icon: Clock },
  CONFIRMED: { label: "Confirmed", variant: "success" as const, icon: CheckCircle },
  COMPLETED: { label: "Completed", variant: "success" as const, icon: CheckCircle },
  CANCELLED: { label: "Cancelled", variant: "error" as const, icon: AlertCircle },
  NO_SHOW: { label: "No Show", variant: "error" as const, icon: AlertCircle },
} as const;

const channelIcons = {
  web: Calendar,
  whatsapp: MessageCircle,
  sms: MessageCircle,
  voice: Phone,
  staff: Users,
} as const;

/* ============================================================
   AppointmentCard Component
   ============================================================ */

const AppointmentCard = React.forwardRef<HTMLDivElement, AppointmentCardProps>(
  (
    {
      className,
      variant = "default",
      density = "staff",
      id,
      patientName,
      patientAvatar,
      patientId,
      serviceName,
      serviceDuration,
      dentistName,
      dentistAvatar,
      startTime,
      endTime,
      status,
      sourceChannel,
      depositRequired,
      depositPaid,
      depositAmount,
      paymentIntentId,
      cancellationReason,
      notes,
      isAIBooked,
      aiConfidence,
      needsAttention,
      attentionReason,
      onView,
      onEdit,
      onCancel,
      onReschedule,
      onCallPatient,
      onMessagePatient,
      onViewChat,
      children,
      ...props
    },
    ref
  ) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date(start.getTime() + serviceDuration * 60 * 1000);
    const statusInfo = statusConfig[status];
    const ChannelIcon = channelIcons[sourceChannel] || Calendar;
    const isExpanded = variant === "expanded";

    const formatTime = (date: Date) => date.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
    const formatDate = (date: Date) => date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });

    return (
      <div
        ref={ref}
        className={cn(appointmentCardVariants({ variant, density, className }))}
        {...props}
      >
        {/* Attention Banner */}
        {needsAttention && (
          <div className="absolute -top-2 left-4 right-4 -translate-y-full">
            <Badge variant="warning" dot dotColor="warning" className="animate-in slide-in-from-top-2">
              <AlertCircle className="h-3 w-3" />
              {attentionReason || "Needs attention"}
            </Badge>
          </div>
        )}

        <div className={cn("p-4", density === "staff" && "p-3")}>
          {/* Header Row */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              {/* Time Column */}
              <div className={cn("flex-shrink-0 text-right", density === "staff" && "w-20", density === "patient" && "w-24")}>
                <time dateTime={startTime} className="font-heading font-semibold text-staff-on-surface">
                  {formatTime(start)}
                </time>
                <div className="text-caption text-staff-on-surface-muted">
                  {formatDate(start)} · {serviceDuration}min
                </div>
              </div>

              {/* Main Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h4 className="font-heading font-semibold text-staff-on-surface truncate">{serviceName}</h4>
                  <Badge
                    variant={statusInfo.variant}
                    dot
                    size="sm"
                    className="whitespace-nowrap"
                  >
                    <statusInfo.icon className="h-2.5 w-2.5" />
                    {statusInfo.label}
                  </Badge>
                  {isAIBooked && (
                    <Badge variant="ai" dot dotColor="ai" size="sm">
                      AI Booked
                    </Badge>
                  )}
                  {depositRequired && !depositPaid && (
                    <Badge variant="warning" dot dotColor="warning" size="sm">
                      Deposit Due
                    </Badge>
                  )}
                </div>

                <div className="mt-1 flex items-center gap-3 text-sm text-staff-on-surface-muted flex-wrap">
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5" />
                    {patientName}
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5" />
                    Dr. {dentistName}
                  </span>
                  <span className="flex items-center gap-1">
                    <ChannelIcon className="h-3.5 w-3.5" />
                    {sourceChannel}
                  </span>
                </div>

                {aiConfidence !== undefined && (
                  <div className="mt-1 flex items-center gap-1.5 text-caption text-staff-ai">
                    <span className="font-mono">{Math.round(aiConfidence)}% confidence</span>
                  </div>
                )}

                {notes && isExpanded && (
                  <div className="mt-2 p-2 rounded-lg bg-staff-surface-variant text-sm text-staff-on-surface">
                    {notes}
                  </div>
                )}

                {cancellationReason && (
                  <div className="mt-2 p-2 rounded-lg bg-staff-error-container/10 text-sm text-staff-error">
                    <strong>Cancelled:</strong> {cancellationReason}
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex-shrink-0">
              <button
                type="button"
                className="p-1.5 rounded-lg text-staff-on-surface-muted hover:text-staff-on-surface hover:bg-staff-surface-variant transition-colors"
                aria-label="More actions"
              >
                <MoreHorizontal className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Quick Actions Row */}
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-staff-border">
            {onCallPatient && (
              <Button
                variant="outline"
                size="sm"
                onClick={onCallPatient}
                className="flex-1 sm:flex-none"
              >
                <Phone className="h-3.5 w-3.5" />
                <span>Call</span>
              </Button>
            )}
            {onMessagePatient && (
              <Button
                variant="outline"
                size="sm"
                onClick={onMessagePatient}
                className="flex-1 sm:flex-none"
              >
                <MessageCircle className="h-3.5 w-3.5" />
                <span>Message</span>
              </Button>
            )}
            {onReschedule && status !== "CANCELLED" && status !== "COMPLETED" && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onReschedule}
                className="flex-1 sm:flex-none"
              >
                Reschedule
              </Button>
            )}
          </div>

          {/* Expanded Details */}
          {isExpanded && (
            <div className="mt-4 space-y-3 animate-in slide-in-from-top-2 fade-in">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-staff-on-surface-muted">Duration</span>
                  <div className="font-medium">{serviceDuration} minutes</div>
                </div>
                <div>
                  <span className="text-staff-on-surface-muted">End Time</span>
                  <div className="font-medium">{formatTime(end)}</div>
                </div>
                {depositRequired && (
                  <div>
                    <span className="text-staff-on-surface-muted">Deposit</span>
                    <div className="font-medium">
                      {depositPaid ? (
                        <span className="text-staff-success">Paid</span>
                      ) : (
                        <span className="text-staff-warning">{depositAmount ? `$${depositAmount}` : "Required"}</span>
                      )}
                    </div>
                  </div>
                )}
                {paymentIntentId && (
                  <div>
                    <span className="text-staff-on-surface-muted">Payment ID</span>
                    <div className="font-mono text-xs truncate max-w-full">{paymentIntentId}</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }
);
AppointmentCard.displayName = "AppointmentCard";

/* ============================================================
   Appointment Card Compact - For lists
   ============================================================ */

export interface AppointmentCardCompactProps extends Omit<AppointmentCardProps, "variant"> {
  onClick?: () => void;
}

const AppointmentCardCompact = React.forwardRef<HTMLDivElement, AppointmentCardCompactProps>(
  ({ className, onClick, density = "staff", ...props }, ref) => {
    const start = new Date(props.startTime);
    const statusInfo = statusConfig[props.status];
    const ChannelIcon = channelIcons[props.sourceChannel] || Calendar;

    return (
      <div
        ref={ref}
        className={cn(
          appointmentCardVariants({ variant: "compact", density, className }),
          onClick && "cursor-pointer hover:bg-staff-surface-variant/50"
        )}
        onClick={onClick}
        {...props}
      >
        <div className="flex items-center gap-3 p-3">
          <div className={cn("flex-shrink-0 text-right", density === "staff" && "w-20", density === "patient" && "w-24")}>
            <time dateTime={props.startTime} className="font-heading font-semibold text-staff-on-surface">
              {new Date(props.startTime).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })}
            </time>
            <div className="text-caption text-staff-on-surface-muted">
              {new Date(props.startTime).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })}
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-semibold text-staff-on-surface truncate">{props.serviceName}</h4>
              <Badge variant={statusInfo.variant} dot size="sm">
                <statusInfo.icon className="h-2.5 w-2.5" />
                {statusInfo.label}
              </Badge>
              {props.isAIBooked && <Badge variant="ai" size="sm">AI</Badge>}
            </div>

            <div className="mt-1 flex items-center gap-3 text-sm text-staff-on-surface-muted flex-wrap">
              <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" />{props.patientName}</span>
              <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" />Dr. {props.dentistName}</span>
              <span className="flex items-center gap-1"><ChannelIcon className="h-3.5 w-3.5" />{props.sourceChannel}</span>
            </div>
          </div>

          {onClick && (
            <button
              type="button"
              className="p-1.5 rounded-lg text-staff-on-surface-muted hover:text-staff-on-surface hover:bg-staff-surface-variant"
              aria-label="View details"
            >
              <ChevronDown className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>
    );
  }
);
AppointmentCardCompact.displayName = "AppointmentCardCompact";

export { AppointmentCard, AppointmentCardCompact, appointmentCardVariants };
"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Calendar, Phone, Mail, MapPin, AlertCircle, CheckCircle, Star, Heart, Shield, Users, Sparkles, Sparkle } from "lucide-react";

import { cn } from "@/lib/design-system";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Chip } from "@/components/ui/chip";
import { Separator } from "@/components/ui/separator";

/* ============================================================
   Types
   ============================================================ */

export interface PatientSummaryCardProps {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth?: string;
  gender?: string;
  avatar?: string;
  avatarFallback?: string;
  insuranceProvider?: string;
  insuranceMemberId?: string;
  isReturning?: boolean;
  noShowCount?: number;
  requiresDeposit?: boolean;
  channelPreference?: "web" | "whatsapp" | "sms" | "voice";
  notes?: string;
  isActive?: boolean;
  upcomingAppointments?: Array<{
    id: string;
    serviceName: string;
    dentistName: string;
    startTime: string;
    status: string;
  }>;
  aiFlags?: Array<{
    type: "risk" | "opportunity" | "info";
    message: string;
  }>;
  onViewDetails?: () => void;
  onEdit?: () => void;
  onBookAppointment?: () => void;
  onMessage?: () => void;
  onCall?: () => void;
  className?: string;
  variant?: "default" | "compact" | "detailed";
  density?: "patient" | "staff";
  children?: React.ReactNode;
}

const patientSummaryVariants = cva(
  "rounded-2xl border transition-shadow duration-200",
  {
    variants: {
      variant: {
        default: "bg-staff-surface border-staff-border shadow-elevation-0 hover:shadow-elevation-1",
        compact: "bg-staff-surface border-staff-border",
        detailed: "bg-staff-surface border-staff-border shadow-elevation-1",
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

/* ============================================================
   PatientSummaryCard Component
   ============================================================ */

const PatientSummaryCard = React.forwardRef<HTMLDivElement, PatientSummaryCardProps>(
  (
    {
      className,
      variant = "default",
      density = "staff",
      id,
      firstName,
      lastName,
      email,
      phone,
      dateOfBirth,
      gender,
      avatar,
      avatarFallback,
      insuranceProvider,
      insuranceMemberId,
      isReturning,
      noShowCount,
      requiresDeposit,
      channelPreference,
      notes,
      isActive,
      upcomingAppointments,
      aiFlags,
      onViewDetails,
      onEdit,
      onBookAppointment,
      onMessage,
      onCall,
      children,
      ...props
    },
    ref
  ) => {
    const fullName = `${firstName} ${lastName}`;
    const initials = `${firstName[0]}${lastName[0]}`.toUpperCase();
    const age = dateOfBirth ? Math.floor((Date.now() - new Date(dateOfBirth).getTime()) / (365.25 * 24 * 60 * 60 * 1000)) : null;

    const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
    const formatTime = (dateStr: string) => new Date(dateStr).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });

    return (
      <div
        ref={ref}
        className={cn(patientSummaryVariants({ variant, density, className }))}
        {...props}
      >
        <div className={cn("p-4", density === "staff" && "p-3", variant === "detailed" && "p-6")}>
          {/* Header */}
          <div className="flex items-start justify-between gap-3 mb-4">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <Avatar
                size={variant === "compact" ? "md" : "lg"}
                src={avatar}
                fallback={avatarFallback ?? initials}
                online={isActive}
              />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-heading font-semibold text-staff-on-surface truncate">{fullName}</h3>
                  {isReturning && (
                    <Badge variant="success" dot size="sm">
                      Returning
                    </Badge>
                  )}
                  {!isActive && (
                    <Badge variant="neutral" size="sm">Inactive</Badge>
                  )}
                  {requiresDeposit && (
                    <Badge variant="warning" dot dotColor="warning" size="sm">
                      Deposit Required
                    </Badge>
                  )}
                  {noShowCount && noShowCount > 0 && (
                    <Badge variant="error" dot dotColor="error" size="sm">
                      {noShowCount} No-show{noShowCount > 1 ? "s" : ""}
                    </Badge>
                  )}
                </div>
                <div className="mt-1 flex items-center gap-3 text-sm text-staff-on-surface-muted flex-wrap">
                  {age !== null && <span>{age} years</span>}
                  {gender && <span>{gender}</span>}
                  {dateOfBirth && <span>Born {formatDate(dateOfBirth)}</span>}
                </div>
              </div>
            </div>

            <div className="flex-shrink-0 flex items-center gap-1">
              {onEdit && (
                <Button variant="ghost" size="sm" onClick={onEdit} aria-label="Edit patient">
                  Edit
                </Button>
              )}
              {onViewDetails && (
                <Button variant="outline" size="sm" onClick={onViewDetails}>
                  View Details
                </Button>
              )}
            </div>
          </div>

          {/* Contact Info */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
            <div className="flex items-center gap-2 p-3 rounded-lg bg-staff-surface-variant">
              <Mail className="h-4 w-4 text-staff-on-surface-muted flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-caption text-staff-on-surface-muted">Email</p>
                <p className="text-sm font-medium text-staff-on-surface truncate">{email}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 p-3 rounded-lg bg-staff-surface-variant">
              <Phone className="h-4 w-4 text-staff-on-surface-muted flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-caption text-staff-on-surface-muted">Phone</p>
                <p className="text-sm font-medium text-staff-on-surface truncate">{phone}</p>
              </div>
            </div>
            {insuranceProvider && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-staff-surface-variant sm:col-span-2">
                <Shield className="h-4 w-4 text-staff-on-surface-muted flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-caption text-staff-on-surface-muted">Insurance</p>
                  <p className="text-sm font-medium text-staff-on-surface truncate">
                    {insuranceProvider}
                    {insuranceMemberId && <span className="text-staff-on-surface-muted ml-2">({insuranceMemberId})</span>}
                  </p>
                </div>
              </div>
            )}
            {channelPreference && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-staff-surface-variant">
                <Calendar className="h-4 w-4 text-staff-on-surface-muted flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-caption text-staff-on-surface-muted">Preferred Channel</p>
                  <Badge variant="patient" size="sm">{channelPreference}</Badge>
                </div>
              </div>
            )}
          </div>

          {/* AI Flags */}
          {aiFlags && aiFlags.length > 0 && (
            <div className="mb-4 p-3 rounded-lg bg-staff-ai-container/20 border border-staff-ai/20">
              <div className="flex items-center gap-2 text-sm text-staff-on-ai-container mb-2">
                <Sparkles className="h-4 w-4 text-staff-ai" />
                <span className="font-semibold">AI Insights</span>
              </div>
              <ul className="space-y-1">
                {aiFlags.map((flag, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-staff-on-ai-container">
                    {flag.type === "risk" && <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />}
                    {flag.type === "opportunity" && <Star className="h-4 w-4 flex-shrink-0 mt-0.5" />}
                    {flag.type === "info" && <Sparkle className="h-4 w-4 flex-shrink-0 mt-0.5 text-staff-info" />}
                    <span>{flag.message}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Upcoming Appointments */}
          {upcomingAppointments && upcomingAppointments.length > 0 && (
            <div className="mb-4">
              <h4 className="font-semibold text-staff-on-surface mb-2">Upcoming Appointments</h4>
              <div className="space-y-2">
                {upcomingAppointments.slice(0, 3).map((appt) => (
                  <div key={appt.id} className="flex items-center justify-between p-3 rounded-lg bg-staff-surface-variant">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-staff-primary-container text-staff-on-primary-container">
                        <Calendar className="h-4 w-4" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-staff-on-surface truncate">{appt.serviceName}</p>
                        <p className="text-sm text-staff-on-surface-muted">
                          Dr. {appt.dentistName} · {formatDate(appt.startTime)} at {formatTime(appt.startTime)}
                        </p>
                      </div>
                    </div>
                    <Badge variant={appt.status === "CONFIRMED" ? "success" : appt.status === "PENDING" ? "warning" : "neutral"} size="sm">
                      {appt.status}
                    </Badge>
                  </div>
                ))}
                {upcomingAppointments.length > 3 && (
                  <Button variant="ghost" size="sm" className="w-full" onClick={onViewDetails}>
                    View all {upcomingAppointments.length} appointments
                  </Button>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          {notes && variant !== "compact" && (
            <div className="mb-4 p-3 rounded-lg bg-staff-surface-variant">
              <p className="text-caption text-staff-on-surface-muted mb-1">Notes</p>
              <p className="text-sm text-staff-on-surface">{notes}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-wrap items-center gap-2 pt-3 border-t border-staff-border">
            {onBookAppointment && (
              <Button onClick={onBookAppointment} className="flex-1 sm:flex-none">
                Book Appointment
              </Button>
            )}
            {onMessage && (
              <Button variant="outline" onClick={onMessage} className="flex-1 sm:flex-none">
                <Mail className="h-3.5 w-3.5" />
                <span>Message</span>
              </Button>
            )}
            {onCall && (
              <Button variant="outline" onClick={onCall} className="flex-1 sm:flex-none">
                <Phone className="h-3.5 w-3.5" />
                <span>Call</span>
              </Button>
            )}
            {onViewDetails && variant !== "detailed" && (
              <Button variant="ghost" onClick={onViewDetails} className="flex-1 sm:flex-none">
                View Details
              </Button>
            )}
          </div>

          {children}
        </div>
      </div>
    );
  }
);
PatientSummaryCard.displayName = "PatientSummaryCard";

/* ============================================================
   Patient Card Compact - For lists
   ============================================================ */

export interface PatientCardCompactProps {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  avatar?: string;
  avatarFallback?: string;
  channelPreference?: "web" | "whatsapp" | "sms" | "voice";
  noShowCount?: number;
  isActive?: boolean;
  upcomingAppointment?: {
    serviceName: string;
    startTime: string;
    status: string;
  };
  onClick?: () => void;
  onMessage?: () => void;
  onCall?: () => void;
  className?: string;
  density?: "patient" | "staff";
}

const PatientCardCompact = React.forwardRef<HTMLDivElement, PatientCardCompactProps>(
  ({ className, density = "staff", onClick, onMessage, onCall, ...props }, ref) => {
    const initials = `${props.firstName[0]}${props.lastName[0]}`.toUpperCase();

    return (
      <div
        ref={ref}
        className={cn(
          patientSummaryVariants({ variant: "compact", density, className }),
          onClick && "cursor-pointer hover:bg-staff-surface-variant/50"
        )}
        onClick={onClick}
        {...props}
      >
        <div className="flex items-center gap-3 p-3">
          <Avatar size="md" src={props.avatar} fallback={props.avatarFallback ?? initials} online={props.isActive} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-semibold text-staff-on-surface truncate">{props.firstName} {props.lastName}</h4>
              {props.noShowCount && props.noShowCount > 0 && (
                <Badge variant="error" dot dotColor="error" size="sm">{props.noShowCount} No-shows</Badge>
              )}
              {!props.isActive && <Badge variant="neutral" size="sm">Inactive</Badge>}
            </div>
            <div className="mt-1 flex items-center gap-3 text-sm text-staff-on-surface-muted flex-wrap">
              <span className="truncate">{props.email}</span>
              <span>{props.phone}</span>
              {props.channelPreference && <Badge variant="patient" size="sm">{props.channelPreference}</Badge>}
            </div>
            {props.upcomingAppointment && (
              <div className="mt-2 flex items-center justify-between text-sm">
                <span className="text-staff-on-surface-muted">{props.upcomingAppointment.serviceName}</span>
                <Badge variant={props.upcomingAppointment.status === "CONFIRMED" ? "success" : "warning"} size="sm">
                  {props.upcomingAppointment.status}
                </Badge>
              </div>
            )}
          </div>
          <div className="flex items-center gap-1">
            {onMessage && (
              <button type="button" onClick={(e) => { e.stopPropagation(); onMessage?.(); }} className="p-1.5 rounded-lg text-staff-on-surface-muted hover:text-staff-primary hover:bg-staff-surface-variant" aria-label="Message">
                <Mail className="h-4 w-4" />
              </button>
            )}
            {onCall && (
              <button type="button" onClick={(e) => { e.stopPropagation(); onCall?.(); }} className="p-1.5 rounded-lg text-staff-on-surface-muted hover:text-staff-primary hover:bg-staff-surface-variant" aria-label="Call">
                <Phone className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }
);
PatientCardCompact.displayName = "PatientCardCompact";

export { PatientSummaryCard, PatientCardCompact, patientSummaryVariants };
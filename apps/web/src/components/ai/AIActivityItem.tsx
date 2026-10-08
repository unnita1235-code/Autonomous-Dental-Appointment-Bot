"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import {
  Send,
  Smartphone,
  MessageCircle,
  Phone,
  Calendar,
  CreditCard,
  Bot,
  Users,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap,
  Brain,
  Loader2,
  UserCheck,
  UserX,
  CalendarCheck2,
  CalendarX,
  CalendarDays,
  CheckCircle2,
  XCircle,
  Info,
} from "lucide-react";

import { cn } from "@/lib/design-system";

const activityItemVariants = cva(
  "flex items-start gap-3 transition-colors duration-150",
  {
    variants: {
      variant: {
        default: "",
        compact: "",
        detailed: "",
      },
      density: {
        patient: "",
        staff: "",
      },
      tone: {
        neutral: "",
        success: "",
        warning: "",
        error: "",
        info: "",
        ai: "",
      },
    },
    defaultVariants: {
      variant: "default",
      density: "patient",
      tone: "neutral",
    },
  }
);

const iconMap = {
  sms: Smartphone,
  whatsapp: MessageCircle,
  voice: Phone,
  web: Calendar,
  staff: Users,
  ai: Bot,
  payment: CreditCard,
  appointment: Calendar,
  system: Send,
} as const;

const toneIconMap = {
  success: CheckCircle,
  warning: AlertCircle,
  error: AlertCircle,
  info: Info,
  ai: Zap,
  neutral: Send,
} as const;

export interface AIActivityItemProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof activityItemVariants> {
  timestamp: string;
  eventType: keyof typeof iconMap | string;
  description: string;
  status?: "pending" | "completed" | "failed" | "processing";
  actor?: "patient" | "staff" | "ai" | "system";
  patientName?: string;
  patientId?: string;
  actionLabel?: string;
  actionHref?: string;
  actionOnClick?: () => void;
  metadata?: Array<{ label: string; value: string }>;
  showTimestamp?: boolean;
  clickable?: boolean;
  onClick?: () => void;
}

const AIActivityItem = React.forwardRef<HTMLDivElement, AIActivityItemProps>(
  (
    {
      className,
      variant,
      density,
      tone,
      timestamp,
      eventType,
      description,
      status = "completed",
      actor,
      patientName,
      patientId,
      actionLabel,
      actionHref,
      actionOnClick,
      metadata,
      showTimestamp = true,
      clickable = false,
      onClick,
      children,
      ...props
    },
    ref
  ) => {
    const EventIcon = iconMap[eventType as keyof typeof iconMap] || Send;
    const ToneIcon = tone && toneIconMap[tone] ? toneIconMap[tone] : Send;
    const prefersReducedMotion = React.useMemo(
      () => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      []
    );

    const formatTimestamp = (ts: string) => {
      const date = new Date(ts);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return "Just now";
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;
      return date.toLocaleDateString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    };

    const getStatusColor = () => {
      switch (status) {
        case "completed": return "text-staff-success";
        case "pending": return "text-staff-warning";
        case "failed": return "text-staff-error";
        case "processing": return "text-staff-ai animate-pulse";
        default: return "text-staff-on-surface-muted";
      }
    };

    const getActorColor = () => {
      switch (actor) {
        case "ai": return "text-staff-ai";
        case "staff": return "text-staff-primary";
        case "patient": return "text-patient-secondary";
        case "system": return "text-staff-on-surface-muted";
        default: return "text-staff-on-surface-muted";
      }
    };

    const timestampContent = showTimestamp ? (
      <time
        dateTime={timestamp}
        className={cn(
          "flex-shrink-0 font-mono text-[11px] text-staff-on-surface-muted whitespace-nowrap",
          density === "staff" && "text-[10px]"
        )}
      >
        {formatTimestamp(timestamp)}
      </time>
    ) : null;

    const actionContent = actionLabel && (actionHref || actionOnClick) ? (
      <a
        href={actionHref}
        onClick={(e) => {
          if (actionOnClick) {
            e.preventDefault();
            actionOnClick();
          }
        }}
        className={cn(
          "inline-flex items-center gap-1 px-2.5 py-1 text-caption font-medium rounded-full transition-colors",
          "focus-visible:ring-2 focus-visible:ring-staff-border-focus",
          tone === "ai"
            ? "bg-staff-ai-container text-staff-on-ai-container hover:bg-staff-ai/20"
            : "bg-staff-surface-variant text-staff-on-surface hover:bg-staff-border"
        )}
      >
        {actionLabel}
      </a>
    ) : null;

    const baseClasses = cn(
      activityItemVariants({ variant, density, tone, className }),
      density === "staff" ? "gap-2" : "gap-3",
      clickable && "cursor-pointer hover:bg-staff-surface-variant/50 rounded-xl",
      "group"
    );

    return (
      <div
        ref={ref}
        className={baseClasses}
        onClick={onClick}
        {...props}
      >
        {/* Icon Column */}
        <div className={cn(
          "flex-shrink-0 flex items-start justify-center pt-0.5",
          density === "staff" && "w-8",
          density === "patient" && "w-10"
        )}>
          <div
            className={cn(
              "flex items-center justify-center rounded-full",
              density === "staff" && "w-6 h-6",
              density === "patient" && "w-8 h-8",
              tone === "ai" && "bg-staff-ai-container",
              tone === "success" && "bg-staff-success-container",
              tone === "warning" && "bg-staff-warning-container",
              tone === "error" && "bg-staff-error-container",
              tone === "info" && "bg-staff-info-container",
              tone === "neutral" && "bg-staff-surface-variant",
              "text-staff-on-surface"
            )}
            aria-hidden="true"
          >
            <EventIcon
              className={cn(
                tone === "ai" && "text-staff-ai",
                tone === "success" && "text-staff-success",
                tone === "warning" && "text-staff-warning",
                tone === "error" && "text-staff-error",
                tone === "info" && "text-staff-info",
                density === "staff" && "h-3 w-3",
                density === "patient" && "h-4 w-4"
              )}
            />
          </div>
        </div>

        {/* Content Column */}
        <div className={cn("flex-1 min-w-0", density === "staff" && "pt-0.5")}>
          {/* Header Row */}
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 flex-wrap">
              {patientName && (
                <span className="font-medium text-staff-on-surface truncate">{patientName}</span>
              )}
              {actor && (
                <span
                  className={cn(
                    "px-1.5 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider",
                    getActorColor()
                  )}
                >
                  {actor}
                </span>
              )}
              {status !== "completed" && (
                <span
                  className={cn(
                    "inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-semibold",
                    getStatusColor()
                  )}
                >
                  {status === "pending" && <Clock className="h-2.5 w-2.5" />}
                  {status === "processing" && <Loader2 className="h-2.5 w-2.5 animate-spin" />}
                  {status === "failed" && <AlertCircle className="h-2.5 w-2.5" />}
                  <span className="capitalize">{status}</span>
                </span>
              )}
            </div>
            {timestampContent}
          </div>

          {/* Description */}
          <p
            className={cn(
              "text-staff-on-surface leading-relaxed",
              density === "staff" ? "text-body-sm" : "text-body-md",
              variant === "compact" && "line-clamp-2"
            )}
          >
            {description}
          </p>

          {/* Metadata */}
          {metadata && metadata.length > 0 && (
            <dl className="mt-2 flex flex-wrap items-center gap-2 text-caption text-staff-on-surface-muted">
              {metadata.map((item, index) => (
                <React.Fragment key={index}>
                  <dt className="font-medium">{item.label}:</dt>
                  <dd>{item.value}</dd>
                </React.Fragment>
              ))}
            </dl>
          )}

          {/* Action */}
          {actionContent && (
            <div className="mt-2">{actionContent}</div>
          )}
        </div>

        {children}
      </div>
    );
  }
);
AIActivityItem.displayName = "AIActivityItem";

/* ============================================================
   Timeline Item - Vertical timeline variant
   ============================================================ */

const timelineItemVariants = cva(
  "relative flex items-start gap-3",
  {
    variants: {
      position: {
        first: "",
        middle: "",
        last: "",
        only: "",
      },
      density: {
        patient: "",
        staff: "",
      },
    },
    defaultVariants: {
      position: "middle",
      density: "patient",
    },
  }
);

export interface TimelineItemProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof timelineItemVariants> {
  timestamp: string;
  title: string;
  description?: string;
  icon?: React.ReactNode;
  status?: "upcoming" | "current" | "completed" | "missed" | "cancelled";
  variant?: "default" | "ai" | "attention";
  actions?: Array<{
    label: string;
    onClick: () => void;
    variant?: "primary" | "secondary" | "ghost";
  }>;
  metadata?: Array<{ label: string; value: string }>;
  showConnector?: boolean;
}

const TimelineItem = React.forwardRef<HTMLDivElement, TimelineItemProps>(
  (
    {
      className,
      position,
      density,
      timestamp,
      title,
      description,
      icon,
      status = "upcoming",
      variant = "default",
      actions,
      metadata,
      showConnector = true,
      children,
      ...props
    },
    ref
  ) => {
    const formatTimestamp = (ts: string) => {
      const date = new Date(ts);
      return date.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
    };

    const getStatusColors = () => {
      switch (status) {
        case "current": return { dot: "bg-staff-ai", ring: "ring-2 ring-staff-ai", text: "text-staff-ai" };
        case "completed": return { dot: "bg-staff-success", ring: "", text: "text-staff-success" };
        case "missed": return { dot: "bg-staff-error", ring: "", text: "text-staff-error" };
        case "cancelled": return { dot: "bg-staff-border", ring: "", text: "text-staff-on-surface-muted" };
        default: return { dot: "bg-staff-primary", ring: "", text: "text-staff-primary" };
      }
    };

    const colors = getStatusColors();

    return (
      <div ref={ref} className={cn(timelineItemVariants({ position, density, className }))} {...props}>
        {/* Timeline Connector */}
        {showConnector && (
          <div className="absolute left-3.5 top-0 bottom-0 w-0.5 bg-staff-border" aria-hidden="true">
            {position === "first" && <div className="absolute top-0 h-1/2 w-full bg-transparent" />}
            {position === "last" && <div className="absolute bottom-0 h-1/2 w-full bg-transparent" />}
          </div>
        )}

        {/* Status Dot */}
        <div className="flex-shrink-0 relative z-10">
          <div
            className={cn(
              "rounded-full border-2 border-white/0 transition-all duration-200",
              density === "staff" && "w-5 h-5",
              density === "patient" && "w-7 h-7",
              colors.dot,
              colors.ring
            )}
            aria-hidden="true"
          />
        </div>

        {/* Content */}
        <div className={cn("flex-1 min-w-0", density === "staff" && "pt-1")}>
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 flex-wrap">
              {icon && (
                <span className="text-staff-on-surface-variant">{icon}</span>
              )}
              <h4 className="font-semibold text-staff-on-surface">{title}</h4>
              {variant === "ai" && (
                <span className="px-1.5 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-staff-ai-container text-staff-on-ai-container">
                  AI
                </span>
              )}
              {variant === "attention" && (
                <span className="px-1.5 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-staff-warning-container text-staff-on-warning-container">
                  Attention
                </span>
              )}
            </div>
            <time
              dateTime={timestamp}
              className={cn(
                "flex-shrink-0 font-mono text-staff-on-surface-muted whitespace-nowrap",
                density === "staff" && "text-[10px]",
                density === "patient" && "text-caption"
              )}
            >
              {formatTimestamp(timestamp)}
            </time>
          </div>

          {description && (
            <p className={cn("text-staff-on-surface-variant", density === "staff" ? "text-body-sm" : "text-body-md")}>
              {description}
            </p>
          )}

          {metadata && metadata.length > 0 && (
            <dl className="mt-2 flex flex-wrap items-center gap-2 text-caption text-staff-on-surface-muted">
              {metadata.map((item, index) => (
                <React.Fragment key={index}>
                  <dt className="font-medium">{item.label}:</dt>
                  <dd>{item.value}</dd>
                </React.Fragment>
              ))}
            </dl>
          )}

          {actions && actions.length > 0 && (
            <div className="mt-3 flex flex-wrap items-center gap-2">
              {actions.map((action, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={action.onClick}
                  className={cn(
                    "inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-medium transition-all duration-200",
                    "focus-visible:ring-2 focus-visible:ring-staff-border-focus",
                    action.variant === "primary" && "bg-staff-primary text-staff-on-primary hover:bg-staff-primary-hover",
                    action.variant === "secondary" && "bg-staff-surface border border-staff-border text-staff-on-surface hover:bg-staff-surface-variant",
                    action.variant === "ghost" && "text-staff-on-surface-variant hover:text-staff-on-surface hover:bg-staff-surface-variant"
                  )}
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}

          {children}
        </div>
      </div>
    );
  }
);
TimelineItem.displayName = "TimelineItem";

export { AIActivityItem, TimelineItem, activityItemVariants, timelineItemVariants };
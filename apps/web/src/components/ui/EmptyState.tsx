"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import {
  Calendar,
  Users,
  MessageCircle,
  Bell,
  Search,
  Inbox,
  ClipboardList,
  Brain,
  Sparkles,
  Shield,
  Heart,
  Star,
} from "lucide-react";

import { cn } from "@/lib/design-system";
import { Button } from "@/components/ui/button";
import { AISparkle } from "@/components/ai/AIIndicator";

const emptyStateVariants = cva(
  "flex flex-col items-center justify-center text-center py-12 px-4",
  {
    variants: {
      size: {
        sm: "py-6 px-3",
        default: "py-12 px-4",
        lg: "py-16 px-6",
        full: "flex-1",
      },
      variant: {
        default: "",
        ai: "",
        success: "",
        warning: "",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "default",
    },
  }
);

const iconMap = {
  appointments: Calendar,
  patients: Users,
  conversations: MessageCircle,
  notifications: Bell,
  search: Search,
  inbox: Inbox,
  tasks: ClipboardList,
  ai: Brain,
  recommendations: Sparkles,
  insurance: Shield,
  favorites: Heart,
  reviews: Star,
} as const;

type IconMapKey = keyof typeof iconMap;

export interface EmptyStateProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof emptyStateVariants> {
  icon?: keyof typeof iconMap | React.ReactNode;
  title: string;
  description?: string;
  primaryAction?: {
    label: string;
    onClick: () => void;
    variant?: "primary" | "secondary" | "ai";
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  illustration?: React.ReactNode;
}

const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  (
    {
      className,
      size = "default",
      variant = "default",
      icon,
      title,
      description,
      primaryAction,
      secondaryAction,
      illustration,
      children,
      ...props
    },
    ref
  ) => {
    const prefersReducedMotion = React.useMemo(
      () => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      []
    );

    const IconComponent = typeof icon === "string" && (icon as IconMapKey) in iconMap ? iconMap[icon as IconMapKey] : null;

    return (
      <div
        ref={ref}
        className={cn(emptyStateVariants({ size, variant, className }))}
        {...props}
      >
        {/* Illustration */}
        {(illustration || IconComponent) && (
          <div
            className={cn(
              "mb-6 flex items-center justify-center",
              size === "sm" && "text-4xl",
              size === "default" && "text-6xl",
              size === "lg" && "text-8xl",
              variant === "ai" && "text-staff-ai",
              variant === "success" && "text-staff-success",
              variant === "warning" && "text-staff-warning"
            )}
            aria-hidden="true"
          >
            {illustration ? (
              illustration
            ) : IconComponent ? (
              <IconComponent />
            ) : (
              <AISparkle size="xl" animated={variant === "ai" && !prefersReducedMotion} />
            )}
          </div>
        )}

        {/* Title */}
        <h3 className={cn(
          "font-heading font-semibold",
          size === "sm" && "text-lg",
          size === "default" && "text-headline-sm",
          size === "lg" && "text-headline-md"
        )}>
          {title}
        </h3>

        {/* Description */}
        {description && (
          <p className={cn(
            "mt-2 text-staff-on-surface-variant max-w-md",
            size === "sm" && "text-sm",
            size === "default" && "text-body-md",
            size === "lg" && "text-body-lg"
          )}>
            {description}
          </p>
        )}

        {/* Actions */}
        {(primaryAction || secondaryAction) && (
          <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
            {primaryAction && (
              <Button
                onClick={primaryAction.onClick}
                variant={
                  primaryAction.variant === "ai" ? "ai" :
                  primaryAction.variant === "secondary" ? "secondary" : "primary"
                }
                size="lg"
              >
                {primaryAction.variant === "ai" && (
                  <AISparkle size="sm" className="mr-2" />
                )}
                {primaryAction.label}
              </Button>
            )}
            {secondaryAction && (
              <Button variant="ghost" onClick={secondaryAction.onClick}>
                {secondaryAction.label}
              </Button>
            )}
          </div>
        )}

        {children}
      </div>
    );
  }
);
EmptyState.displayName = "EmptyState";

/* ============================================================
   Pre-configured Empty States
   ============================================================ */

export const EmptyAppointments = ({ onBook, onViewAll, ...props }: {
  onBook?: () => void;
  onViewAll?: () => void;
} & Omit<EmptyStateProps, "icon" | "title" | "description" | "primaryAction" | "secondaryAction">) => (
  <EmptyState
    {...props}
    icon="appointments"
    title="No appointments yet"
    description="Your schedule is clear. Book your first appointment to get started."
    primaryAction={onBook ? { label: "Book Appointment", onClick: onBook, variant: "primary" } : undefined}
    secondaryAction={onViewAll ? { label: "View Calendar", onClick: onViewAll } : undefined}
  />
);

export const EmptyPatients = ({ onAdd, ...props }: {
  onAdd?: () => void;
} & Omit<EmptyStateProps, "icon" | "title" | "description" | "primaryAction">) => (
  <EmptyState
    {...props}
    icon="patients"
    title="No patients found"
    description="Add your first patient to start managing their care."
    primaryAction={onAdd ? { label: "Add Patient", onClick: onAdd, variant: "primary" } : undefined}
  />
);

export const EmptyConversations = ({ onStartChat, ...props }: {
  onStartChat?: () => void;
} & Omit<EmptyStateProps, "icon" | "title" | "description" | "primaryAction">) => (
  <EmptyState
    {...props}
    icon="conversations"
    title="No conversations yet"
    description="When patients reach out, their conversations will appear here."
    primaryAction={onStartChat ? { label: "Start Chat", onClick: onStartChat, variant: "ai" } : undefined}
  />
);

export const EmptyNotifications = ({ ...props }: Omit<EmptyStateProps, "icon" | "title" | "description">) => (
  <EmptyState
    {...props}
    icon="notifications"
    title="No notifications"
    description="You're all caught up. New alerts will appear here."
  />
);

export const EmptySearch = ({ query, onClear, ...props }: {
  query?: string;
  onClear?: () => void;
} & Omit<EmptyStateProps, "icon" | "title" | "description" | "primaryAction">) => (
  <EmptyState
    {...props}
    icon="search"
    title={query ? `No results for "${query}"` : "No results found"}
    description={query ? "Try adjusting your search terms or filters." : "Start typing to search."}
    primaryAction={onClear ? { label: "Clear Search", onClick: onClear, variant: "secondary" } : undefined}
  />
);

export const EmptyAIRecommendations = ({ onRefresh, ...props }: {
  onRefresh?: () => void;
} & Omit<EmptyStateProps, "icon" | "title" | "description" | "primaryAction" | "variant">) => (
  <EmptyState
    {...props}
    variant="ai"
    icon="ai"
    title="No AI recommendations yet"
    description="DentalFlow AI will analyze your schedule and suggest optimizations as data becomes available."
    primaryAction={onRefresh ? { label: "Refresh Analysis", onClick: onRefresh, variant: "ai" } : undefined}
  />
);

export { EmptyState, emptyStateVariants };
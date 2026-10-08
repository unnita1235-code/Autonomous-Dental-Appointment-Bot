"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/design-system";

const metricCardVariants = cva(
  "rounded-2xl border transition-shadow duration-200",
  {
    variants: {
      variant: {
        patient: "bg-patient-surface-lowest border-patient-outline-variant shadow-elevation-1",
        staff: "bg-staff-surface border-staff-border shadow-elevation-0",
        elevated: "bg-staff-surface border-staff-border shadow-elevation-1",
        ai: "bg-staff-surface border-staff-ai/30 shadow-ai-glow",
      },
      size: {
        default: "p-4 md:p-6",
        compact: "p-3",
        comfortable: "p-6 md:p-8",
      },
      interactive: {
        true: "hover:shadow-elevation-hover cursor-pointer",
        false: "",
      },
    },
    defaultVariants: {
      variant: "patient",
      size: "default",
      interactive: false,
    },
  }
);

const trendVariants = cva(
  "inline-flex items-center gap-1 font-medium",
  {
    variants: {
      direction: {
        up: "text-staff-success",
        down: "text-staff-error",
        neutral: "text-staff-on-surface-muted",
      },
      size: {
        sm: "text-caption",
        default: "text-body-sm",
      },
    },
    defaultVariants: {
      direction: "neutral",
      size: "default",
    },
  }
);

export interface MetricCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof metricCardVariants> {
  title: string;
  value: string | number;
  change?: string | number;
  changeLabel?: string;
  trend?: "up" | "down" | "neutral";
  icon?: React.ReactNode;
  iconBackground?: "primary" | "secondary" | "success" | "warning" | "error" | "ai" | "info";
  loading?: boolean;
  empty?: boolean;
  comparison?: {
    label: string;
    value: string | number;
  };
  action?: {
    label: string;
    onClick: () => void;
    variant?: "primary" | "secondary" | "ghost";
  };
}

const MetricCard = React.forwardRef<HTMLDivElement, MetricCardProps>(
  (
    {
      className,
      variant,
      size,
      interactive,
      title,
      value,
      change,
      changeLabel,
      trend,
      icon,
      iconBackground = "primary",
      loading = false,
      empty = false,
      comparison,
      action,
      children,
      ...props
    },
    ref
  ) => {
    const iconBgClasses = {
      primary: "bg-patient-primary-container text-patient-on-primary-container",
      secondary: "bg-patient-secondary-fixed text-patient-on-secondary-fixed",
      success: "bg-staff-success-container text-staff-on-success-container",
      warning: "bg-staff-warning-container text-staff-on-warning-container",
      error: "bg-staff-error-container text-staff-on-error-container",
      ai: "bg-staff-ai-container text-staff-on-ai-container",
      info: "bg-staff-info-container text-staff-on-info",
    };

    if (loading) {
      return (
        <div
          ref={ref}
          className={cn(metricCardVariants({ variant, size, interactive, className }))}
          {...props}
          aria-busy="true"
        >
          <div className="space-y-3">
            <div className="h-4 w-3/4 bg-staff-surface-variant animate-pulse rounded" />
            <div className="h-8 w-1/2 bg-staff-surface-variant animate-pulse rounded" />
            {change && <div className="h-3 w-1/3 bg-staff-surface-variant animate-pulse rounded" />}
          </div>
        </div>
      );
    }

    if (empty) {
      return (
        <div
          ref={ref}
          className={cn(metricCardVariants({ variant, size, interactive, className }))}
          {...props}
        >
          <div className="flex items-center justify-center h-24 text-staff-on-surface-muted">
            <p className="text-body-md">No data available</p>
          </div>
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={cn(metricCardVariants({ variant, size, interactive, className }))}
        {...props}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <p className="text-caption font-medium text-staff-on-surface-variant uppercase tracking-wider">
              {title}
            </p>
            <p className={cn("mt-1 font-heading font-bold", size === "compact" ? "text-headline-sm" : "text-headline-md")}>
              {value}
            </p>
            {(change !== undefined || changeLabel) && (
              <div className="mt-2 flex items-center gap-2">
                {change !== undefined && (
                  <span className={cn(trendVariants({ direction: trend ?? "neutral" }))}>
                    {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {change}
                  </span>
                )}
                {changeLabel && (
                  <span className="text-caption text-staff-on-surface-muted">{changeLabel}</span>
                )}
              </div>
            )}
            {comparison && (
              <div className="mt-3 pt-2 border-t border-staff-border">
                <span className="text-caption text-staff-on-surface-muted">{comparison.label}</span>
                <span className="font-medium text-staff-on-surface ml-1">{comparison.value}</span>
              </div>
            )}
            {action && (
              <button
                type="button"
                onClick={action.onClick}
                className={cn(
                  "mt-3 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-medium transition-all",
                  action.variant === "primary" && "bg-staff-primary text-staff-on-primary hover:bg-staff-primary-hover",
                  action.variant === "secondary" && "bg-staff-surface border border-staff-border text-staff-on-surface hover:bg-staff-surface-variant",
                  action.variant === "ghost" && "text-staff-on-surface-variant hover:text-staff-on-surface hover:bg-staff-surface-variant"
                )}
              >
                {action.label}
              </button>
            )}
          </div>
          {icon && (
            <div
              className={cn(
                "flex-shrink-0 flex items-center justify-center rounded-xl",
                size === "compact" && "w-10 h-10",
                size === "default" && "w-12 h-12",
                size === "comfortable" && "w-14 h-14",
                iconBgClasses[iconBackground]
              )}
              aria-hidden="true"
            >
              {icon}
            </div>
          )}
        </div>
        {children}
      </div>
    );
  }
);
MetricCard.displayName = "MetricCard";

export { MetricCard, metricCardVariants, trendVariants };
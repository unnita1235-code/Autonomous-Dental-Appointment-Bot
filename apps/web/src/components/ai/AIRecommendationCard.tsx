"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { CheckCircle2, AlertCircle, Info, Zap, Brain, X } from "lucide-react";

import { cn } from "@/lib/design-system";
import { AISparkle } from "./AIIndicator";
import { Button } from "@/components/ui/button";

const aiRecommendationCardVariants = cva(
  "relative rounded-2xl border bg-staff-surface transition-all duration-200",
  {
    variants: {
      variant: {
        default: "border-staff-border shadow-elevation-1",
        elevated: "border-staff-border shadow-elevation-2",
        ai: "border-staff-ai/30 shadow-ai-glow",
        urgent: "border-staff-warning/30 bg-staff-warning-container/10",
        success: "border-staff-success/30 bg-staff-success-container/10",
      },
      padding: {
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
      variant: "ai",
      padding: "default",
      interactive: false,
    },
  }
);

export interface AIRecommendationCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof aiRecommendationCardVariants> {
  title: string;
  description?: string;
  confidence?: number;
  confidenceLabel?: "High" | "Medium" | "Low";
  reason?: string;
  supportingInfo?: React.ReactNode;
  primaryAction?: {
    label: string;
    onClick: () => void;
    variant?: "primary" | "ai" | "secondary";
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  dismissAction?: {
    onClick: () => void;
    label?: string;
  };
  metadata?: Array<{ label: string; value: string }>;
  icon?: React.ReactNode;
}

const AIRecommendationCard = React.forwardRef<HTMLDivElement, AIRecommendationCardProps>(
  (
    {
      className,
      variant,
      padding,
      interactive,
      title,
      description,
      confidence,
      confidenceLabel,
      reason,
      supportingInfo,
      primaryAction,
      secondaryAction,
      dismissAction,
      metadata,
      icon,
      children,
      ...props
    },
    ref
  ) => {
    const prefersReducedMotion = React.useMemo(
      () => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      []
    );

    const getConfidenceColor = (conf?: number, label?: string) => {
      if (label === "High" || (conf !== undefined && conf >= 80)) return "success";
      if (label === "Medium" || (conf !== undefined && conf >= 50)) return "warning";
      return "info";
    };

    const confidenceVariant = getConfidenceColor(confidence, confidenceLabel);

    return (
      <div
        ref={ref}
        className={cn(aiRecommendationCardVariants({ variant, padding, interactive, className }))}
        {...props}
      >
        {/* AI Badge Header */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <AISparkle size="sm" animated={!prefersReducedMotion} />
            <h3 className="font-heading text-headline-sm font-semibold text-staff-on-surface">
              AI Recommendation
            </h3>
          </div>
          {dismissAction && (
            <button
              type="button"
              onClick={dismissAction.onClick}
              className="p-1 rounded-lg text-staff-on-surface-muted hover:text-staff-on-surface hover:bg-staff-surface-variant transition-colors focus-visible:ring-2 focus-visible:ring-staff-border-focus"
              aria-label={dismissAction.label ?? "Dismiss recommendation"}
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          )}
        </div>

        {/* Main Content */}
        <div className="space-y-3">
          <h4 className="font-heading text-label-lg font-semibold text-staff-on-surface">{title}</h4>

          {description && (
            <p className="text-body-md text-staff-on-surface-variant leading-relaxed">{description}</p>
          )}

          {/* Confidence & Reason */}
          {(confidence !== undefined || confidenceLabel || reason) && (
            <div className="space-y-2 pt-2 border-t border-staff-border">
              <div className="flex items-center justify-between">
                <span className="font-medium text-staff-on-surface">Confidence</span>
                <span
                  className={cn(
                    "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-caption font-semibold",
                    confidenceVariant === "success" && "bg-staff-success-container text-staff-on-success-container",
                    confidenceVariant === "warning" && "bg-staff-warning-container text-staff-on-warning-container",
                    confidenceVariant === "info" && "bg-staff-info-container text-staff-on-info"
                  )}
                >
                  {confidence !== undefined ? `${Math.round(confidence)}%` : confidenceLabel}
                </span>
              </div>

              {reason && (
                <div className="bg-staff-surface-variant rounded-lg p-3">
                  <div className="flex items-center gap-2 text-caption text-staff-on-surface-variant mb-1">
                    <span className="h-3.5 w-3.5 text-staff-ai">🧠</span>
                    <span className="font-medium">Reason</span>
                  </div>
                  <p className="text-body-sm text-staff-on-surface">{reason}</p>
                </div>
              )}
            </div>
          )}

          {/* Supporting Info */}
          {supportingInfo && (
            <div className="bg-staff-surface-variant/50 rounded-lg p-3">
              {supportingInfo}
            </div>
          )}

          {/* Metadata */}
          {metadata && metadata.length > 0 && (
            <dl className="grid grid-cols-2 gap-2 text-sm">
              {metadata.map((item, index) => (
                <React.Fragment key={index}>
                  <dt className="text-staff-on-surface-muted">{item.label}</dt>
                  <dd className="font-medium text-staff-on-surface">{item.value}</dd>
                </React.Fragment>
              ))}
            </dl>
          )}

          {children}
        </div>

        {/* Actions */}
        {(primaryAction || secondaryAction) && (
          <div className="mt-4 flex flex-col sm:flex-row items-center justify-end gap-2">
            {secondaryAction && (
              <button
                type="button"
                onClick={secondaryAction.onClick}
                className={cn(
                  "inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl font-semibold text-sm transition-all duration-200",
                  "focus-visible:ring-2 focus-visible:ring-staff-border-focus",
                  "bg-staff-surface border border-staff-border text-staff-on-surface",
                  "hover:bg-staff-surface-variant"
                )}
              >
                {secondaryAction.label}
              </button>
            )}
            {primaryAction && (
              <button
                type="button"
                onClick={primaryAction.onClick}
                className={cn(
                  "inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl font-semibold text-sm transition-all duration-200",
                  "focus-visible:ring-2 focus-visible:ring-offset-2",
                  primaryAction.variant === "ai" &&
                    "bg-staff-ai text-staff-on-ai hover:bg-staff-ai-hover shadow-md",
                  primaryAction.variant === "secondary" &&
                    "bg-staff-surface border border-staff-border text-staff-on-surface hover:bg-staff-surface-variant",
                  primaryAction.variant === "primary" &&
                    "bg-staff-primary text-staff-on-primary hover:bg-staff-primary-hover shadow-md"
                )}
              >
                {primaryAction.label}
              </button>
            )}
          </div>
        )}
      </div>
    );
  }
);
AIRecommendationCard.displayName = "AIRecommendationCard";

export { AIRecommendationCard, aiRecommendationCardVariants };
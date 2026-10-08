"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Sparkles, Zap, Cpu, Brain, CircleCheckBig, AlertCircle, Loader2 } from "lucide-react";

import { cn } from "@/lib/design-system";

const aiIndicatorVariants = cva(
  "inline-flex items-center gap-1.5 font-medium transition-all duration-200",
  {
    variants: {
      variant: {
        processing: "text-staff-ai bg-staff-ai-container",
        active: "text-staff-success bg-staff-success-container",
        recommendation: "text-staff-ai bg-staff-ai-container",
        confidence: "text-staff-info bg-staff-info-container",
        handoff: "text-staff-warning bg-staff-warning-container",
        suggestion: "text-staff-ai-cyan bg-staff-ai-cyan-container",
        idle: "text-staff-on-surface-muted bg-staff-surface-variant",
      },
      size: {
        sm: "px-2 py-1 text-[11px] gap-1 min-h-[24px]",
        default: "px-2.5 py-1.5 text-caption gap-1.5 min-h-[28px]",
        lg: "px-3 py-2 text-sm gap-2 min-h-[36px]",
      },
      withPulse: {
        true: "",
        false: "",
      },
    },
    defaultVariants: {
      variant: "idle",
      size: "default",
      withPulse: false,
    },
  }
);

interface AIIndicatorProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof aiIndicatorVariants> {
  label: string;
  confidence?: number;
  showConfidence?: boolean;
  animated?: boolean;
}

const iconMap = {
  processing: Loader2,
  active: CircleCheckBig,
  recommendation: Brain,
  confidence: Zap,
  handoff: AlertCircle,
  suggestion: Sparkles,
  idle: Cpu,
} as const;

const AIIndicator = React.forwardRef<HTMLSpanElement, AIIndicatorProps>(
  (
    {
      className,
      variant,
      size,
      withPulse,
      label,
      confidence,
      showConfidence = false,
      animated = true,
      children,
      ...props
    },
    ref
  ) => {
    const Icon = iconMap[variant as keyof typeof iconMap] || Cpu;
    const prefersReducedMotion = React.useMemo(
      () => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      []
    );

    const shouldAnimate = animated && !prefersReducedMotion;

    return (
      <span
        ref={ref}
        className={cn(aiIndicatorVariants({ variant, size, withPulse, className }))}
        {...props}
      >
        {Icon && (
          <Icon
            className={cn(
              "flex-shrink-0",
              size === "sm" && "h-3 w-3",
              size === "default" && "h-3.5 w-3.5",
              size === "lg" && "h-4 w-4",
              shouldAnimate && variant === "processing" && "animate-spin",
              shouldAnimate && variant === "active" && "animate-pulse",
              withPulse && "animate-pulse"
            )}
            aria-hidden="true"
          />
        )}
        <span className="truncate">{label}</span>
        {showConfidence && confidence !== undefined && (
          <span
            className={cn(
              "inline-flex items-center justify-center font-mono font-medium rounded-full",
              size === "sm" && "px-1.5 py-0.5 text-[10px]",
              size === "default" && "px-2 py-0.5 text-[11px]",
              size === "lg" && "px-2.5 py-0.5 text-xs",
              "bg-white/20 backdrop-blur-sm"
            )}
          >
            {Math.round(confidence)}%
          </span>
        )}
        {children}
      </span>
    );
  }
);
AIIndicator.displayName = "AIIndicator";

/* ============================================================
   AI Status Dot - Minimal indicator for inline use
   ============================================================ */

const aiStatusDotVariants = cva(
  "inline-flex items-center justify-center rounded-full transition-colors duration-200",
  {
    variants: {
      status: {
        processing: "bg-staff-ai animate-pulse",
        active: "bg-staff-success",
        idle: "bg-staff-on-surface-muted",
        warning: "bg-staff-warning",
        error: "bg-staff-error",
        handoff: "bg-staff-warning",
      },
      size: {
        xs: "w-1.5 h-1.5",
        sm: "w-2 h-2",
        default: "w-2.5 h-2.5",
        lg: "w-3 h-3",
      },
    },
    defaultVariants: {
      status: "idle",
      size: "default",
    },
  }
);

interface AIStatusDotProps extends VariantProps<typeof aiStatusDotVariants> {
  label?: string;
  className?: string;
}

const AIStatusDot = React.forwardRef<HTMLSpanElement, AIStatusDotProps>(
  ({ className, status, size, label, ...props }, ref) => (
    <span
      ref={ref}
      className={cn(aiStatusDotVariants({ status, size, className }))}
      aria-label={label}
      {...props}
    />
  )
);
AIStatusDot.displayName = "AIStatusDot";

/* ============================================================
   AI Sparkle - Decorative AI branding element
   ============================================================ */

const aiSparkleVariants = cva(
  "inline-flex items-center justify-center text-staff-ai transition-all duration-200",
  {
    variants: {
      size: {
        xs: "h-3 w-3",
        sm: "h-4 w-4",
        default: "h-5 w-5",
        lg: "h-6 w-6",
        xl: "h-8 w-8",
      },
      animated: {
        true: "animate-pulse",
        false: "",
      },
    },
    defaultVariants: {
      size: "default",
      animated: false,
    },
  }
);

interface AISparkleProps extends VariantProps<typeof aiSparkleVariants> {
  className?: string;
}

const AISparkle = React.forwardRef<SVGSVGElement, AISparkleProps>(
  ({ className, size, animated, ...props }, ref) => (
    <svg
      ref={ref}
      className={cn(aiSparkleVariants({ size, animated, className }))}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      <path d="M12 2v4" />
      <path d="M12 18v4" />
      <path d="M4.93 4.93l2.83 2.83" />
      <path d="M16.24 16.24l2.83 2.83" />
      <path d="M2 12h4" />
      <path d="M18 12h4" />
      <path d="M4.93 19.07l2.83-2.83" />
      <path d="M16.24 7.76l2.83-2.83" />
    </svg>
  )
);
AISparkle.displayName = "AISparkle";

export { AIIndicator, AIStatusDot, AISparkle, aiIndicatorVariants, aiStatusDotVariants, aiSparkleVariants };
"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/design-system";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-medium text-caption",
  {
    variants: {
      variant: {
        success: "bg-staff-success-container text-staff-on-success-container",
        warning: "bg-staff-warning-container text-staff-on-warning-container",
        error: "bg-staff-error-container text-staff-on-error-container",
        info: "bg-staff-info-container text-staff-on-info",
        ai: "bg-staff-ai-container text-staff-on-ai-container",
        "ai-cyan": "bg-staff-ai-cyan-container text-staff-on-ai-cyan",
        neutral: "bg-staff-surface-variant text-staff-on-surface-variant",
        "neutral-dark": "bg-staff-border text-staff-on-surface",
        patient: "bg-patient-secondary-fixed text-patient-on-secondary-fixed",
        "patient-warning": "bg-patient-tertiary-fixed text-patient-on-tertiary-fixed",
        "patient-error": "bg-patient-error-container text-patient-on-error-container",
      },
      size: {
        default: "",
        sm: "px-2 py-0.5 text-[11px]",
        lg: "px-3 py-1 text-sm",
      },
      dot: {
        true: "gap-1.5",
        false: "",
      },
    },
    defaultVariants: {
      variant: "neutral",
      size: "default",
      dot: false,
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dotColor?: "success" | "warning" | "error" | "info" | "ai" | "ai-cyan";
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      className,
      variant,
      size,
      dot,
      dotColor,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <span
        ref={ref}
        className={cn(badgeVariants({ variant, size, dot: dot || !!dotColor, className }))}
        {...props}
      >
        {dot || dotColor ? (
          <span
            className={cn(
              "w-1.5 h-1.5 rounded-full flex-shrink-0",
              dotColor === "success" && "bg-staff-success",
              dotColor === "warning" && "bg-staff-warning",
              dotColor === "error" && "bg-staff-error",
              dotColor === "info" && "bg-staff-info",
              dotColor === "ai" && "bg-staff-ai",
              dotColor === "ai-cyan" && "bg-staff-ai-cyan",
              !dotColor && (variant === "success" ? "bg-staff-success" :
                variant === "warning" ? "bg-staff-warning" :
                variant === "error" ? "bg-staff-error" :
                variant === "ai" ? "bg-staff-ai" :
                variant === "ai-cyan" ? "bg-staff-ai-cyan" :
                "bg-patient-secondary")
            )}
            aria-hidden="true"
          />
        ) : null}
        {children}
      </span>
    );
  }
);
Badge.displayName = "Badge";

export { Badge, badgeVariants };
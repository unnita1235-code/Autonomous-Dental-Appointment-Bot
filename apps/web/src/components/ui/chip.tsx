"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { X } from "lucide-react";

import { cn } from "@/lib/design-system";

const chipVariants = cva(
  "inline-flex items-center gap-1.5 font-medium transition-all duration-200 rounded-full focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        default: "bg-patient-surface-lowest text-patient-on-surface border border-patient-outline-variant hover:bg-patient-surface-variant",
        selected: "bg-patient-primary text-patient-on-primary shadow-sm",
        "selected-staff": "bg-staff-primary text-staff-on-primary shadow-sm",
        ai: "bg-staff-ai-container text-staff-on-ai-container border border-staff-ai/20 hover:bg-staff-ai/10",
        patient: "bg-patient-secondary-fixed text-patient-on-secondary-fixed hover:bg-patient-secondary-fixed-dim",
        staff: "bg-staff-surface-variant text-staff-on-surface hover:bg-staff-border",
        outline: "bg-transparent border-2 border-staff-border text-staff-on-surface hover:bg-staff-surface-variant",
      },
      size: {
        sm: "px-2.5 py-1 text-caption min-h-[28px]",
        default: "px-3 py-1.5 text-sm min-h-[36px]",
        lg: "px-4 py-2 text-base min-h-[44px]",
        "patient-lg": "px-4 py-2.5 text-label-md min-h-[48px]",
      },
      dismissible: {
        true: "pr-6",
        false: "",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      dismissible: false,
    },
  }
);

export interface ChipProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof chipVariants> {
  onDismiss?: () => void;
  dismissLabel?: string;
  leadingIcon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
}

const Chip = React.forwardRef<HTMLButtonElement, ChipProps>(
  (
    {
      className,
      variant,
      size,
      dismissible,
      onDismiss,
      dismissLabel = "Remove",
      leadingIcon,
      trailingIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
      if (onDismiss && dismissible) {
        // Only trigger dismiss if clicking the dismiss button area
        // The actual dismiss button is rendered separately
      }
      props.onClick?.(event);
    };

    return (
      <button
        ref={ref}
        className={cn(chipVariants({ variant, size, dismissible, className }))}
        disabled={disabled}
        onClick={handleClick}
        {...props}
      >
        {leadingIcon && <span className="flex-shrink-0" aria-hidden="true">{leadingIcon}</span>}
        <span className="truncate">{children}</span>
        {trailingIcon && !dismissible && <span className="flex-shrink-0" aria-hidden="true">{trailingIcon}</span>}
        {dismissible && onDismiss && (
          <button
            type="button"
            className={cn(
              "absolute right-1.5 top-1/2 -translate-y-1/2 flex h-5 w-5 items-center justify-center rounded-full",
              "hover:bg-black/10 transition-colors",
              "focus-visible:ring-2 focus-visible:ring-current",
              variant === "selected" ? "text-patient-on-primary" : "text-patient-on-surface-variant"
            )}
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
              onDismiss();
            }}
            aria-label={dismissLabel}
          >
            <X className="h-3 w-3" aria-hidden="true" />
          </button>
        )}
      </button>
    );
  }
);
Chip.displayName = "Chip";

export { Chip, chipVariants };
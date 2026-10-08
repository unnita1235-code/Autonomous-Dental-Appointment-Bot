"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/design-system";

const fabVariants = cva(
  "fixed bottom-6 right-6 z-50 rounded-full shadow-[0_10px_25px_-5px_rgba(15,23,42,0.4)] transition-all duration-200 flex items-center justify-center",
  {
    variants: {
      variant: {
        primary:
          "w-16 h-16 bg-patient-primary-container text-patient-on-primary hover:shadow-[0_14px_30px_-5px_rgba(15,23,42,0.5)] hover:-translate-y-0.5 active:scale-95 focus-visible:ring-4 focus-visible:ring-patient-primary/20",
        ai:
          "w-16 h-16 bg-staff-ai text-staff-on-ai hover:shadow-[0_14px_30px_-5px_rgba(124,58,237,0.5)] hover:-translate-y-0.5 active:scale-95 focus-visible:ring-4 focus-visible:ring-staff-ai/20",
        staff:
          "w-14 h-14 bg-staff-primary text-staff-on-primary hover:shadow-lg hover:-translate-y-0.5 active:scale-95 focus-visible:ring-4 focus-visible:ring-staff-primary/20",
      },
      pulse: {
        true: "",
        false: "",
      },
    },
    defaultVariants: {
      variant: "primary",
      pulse: true,
    },
  }
);

export interface FabProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof fabVariants> {
  tooltip?: string;
  tooltipPosition?: "top" | "bottom" | "left" | "right";
  asChild?: boolean;
}

const Fab = React.forwardRef<HTMLButtonElement, FabProps>(
  (
    {
      className,
      variant,
      pulse,
      tooltip,
      tooltipPosition = "top",
      asChild = false,
      children,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? "span" : "button";
    const [showTooltip, setShowTooltip] = React.useState(false);

    // Pulse ring elements
    const pulseRings = pulse ? (
      <>
        <span className="absolute -inset-2 rounded-full bg-patient-primary-container/20 animate-fab-pulse pointer-events-none" aria-hidden="true" />
        <span className="absolute -inset-1 rounded-full bg-patient-primary-container/15 animate-[fab-pulse_6s_ease-out_infinite] pointer-events-none" aria-hidden="true" />
      </>
    ) : null;

    // Tooltip
    const tooltipContent = tooltip ? (
      <div
        className={cn(
          "absolute z-50 px-3 py-2 text-caption rounded-xl shadow-elevation-3 whitespace-nowrap bg-staff-surface-rail text-staff-on-surface",
          {
            "bottom-full left-1/2 -translate-x-1/2 mb-2": tooltipPosition === "top",
            "top-full left-1/2 -translate-x-1/2 mt-2": tooltipPosition === "bottom",
            "right-full top-1/2 -translate-y-1/2 mr-2": tooltipPosition === "left",
            "left-full top-1/2 -translate-y-1/2 ml-2": tooltipPosition === "right",
          }
        )}
        role="tooltip"
        aria-hidden={!showTooltip}
      >
        {tooltip}
        <div
          className={cn(
            "absolute w-0 h-0 border-4 border-transparent",
            tooltipPosition === "top" && "bottom-full left-1/2 -translate-x-1/2 border-b-staff-surface-rail",
            tooltipPosition === "bottom" && "top-full left-1/2 -translate-x-1/2 border-t-staff-surface-rail",
            tooltipPosition === "left" && "right-full top-1/2 -translate-y-1/2 border-r-staff-surface-rail",
            tooltipPosition === "right" && "left-full top-1/2 -translate-y-1/2 border-l-staff-surface-rail"
          )}
          aria-hidden="true"
        />
      </div>
    ) : null;

    return (
      <Comp
        ref={ref}
        className={cn(fabVariants({ variant, pulse, className }))}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onFocus={() => setShowTooltip(true)}
        onBlur={() => setShowTooltip(false)}
        aria-label={tooltip}
        {...props}
      >
        {pulseRings}
        {children}
        {showTooltip && tooltipContent}
      </Comp>
    );
  }
);
Fab.displayName = "Fab";

export { Fab, fabVariants };
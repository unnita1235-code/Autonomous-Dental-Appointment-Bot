"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/design-system";

const skeletonVariants = cva(
  "bg-staff-surface-variant animate-pulse rounded",
  {
    variants: {
      variant: {
        text: "h-4",
        title: "h-6 w-3/4",
        heading: "h-8 w-1/2",
        card: "h-24 w-full",
        avatar: "rounded-full",
        button: "h-10 w-24",
        input: "h-10 w-full",
        badge: "h-6 w-16",
        metric: "h-12 w-24",
        image: "rounded-xl",
      },
      width: {
        full: "w-full",
        half: "w-1/2",
        third: "w-1/3",
        quarter: "w-1/4",
        auto: "w-auto",
      },
    },
    defaultVariants: {
      variant: "text",
      width: "full",
    },
  }
);

const spinnerVariants = cva(
  "animate-spin rounded-full border-2 border-staff-border border-t-staff-primary",
  {
    variants: {
      size: {
        xs: "w-3 h-3 border-[1.5px]",
        sm: "w-4 h-4",
        default: "w-6 h-6",
        lg: "w-8 h-8",
        xl: "w-12 h-12",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
);

const pulseVariants = cva(
  "animate-pulse bg-staff-surface-variant rounded",
  {
    variants: {
      variant: {
        default: "",
        soft: "bg-staff-surface-variant/50",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

const loadingOverlayVariants = cva(
  "fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm",
  {
    variants: {
      size: {
        sm: "",
        default: "",
        full: "",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
);

export interface SkeletonProps extends VariantProps<typeof skeletonVariants> {
  className?: string;
  count?: number;
}

const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, variant, width, count = 1, ...props }, ref) => {
    const items = Array.from({ length: count }, (_, i) => (
      <div
        key={i}
        ref={i === 0 ? ref : undefined}
        className={cn(skeletonVariants({ variant, width }), className)}
        {...(i === 0 ? props : {})}
        aria-hidden="true"
      />
    ));

    return count > 1 ? <>{items}</> : items[0];
  }
);
Skeleton.displayName = "Skeleton";

export interface SpinnerProps extends VariantProps<typeof spinnerVariants> {
  className?: string;
  label?: string;
}

const Spinner = React.forwardRef<HTMLDivElement, SpinnerProps>(
  ({ className, size, label, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("inline-flex items-center justify-center", className)}
      {...props}
      role="status"
      aria-label={label ?? "Loading"}
    >
      <svg
        className={cn(spinnerVariants({ size }))}
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="10" strokeWidth="3" />
      </svg>
      {label && <span className="sr-only">{label}</span>}
    </div>
  )
);
Spinner.displayName = "Spinner";

export interface PulseProps extends VariantProps<typeof pulseVariants> {
  className?: string;
  children?: React.ReactNode;
}

const Pulse = React.forwardRef<HTMLDivElement, PulseProps>(
  ({ className, variant, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(pulseVariants({ variant }), className)}
      {...props}
      aria-hidden="true"
    >
      {children}
    </div>
  )
);
Pulse.displayName = "Pulse";

export interface LoadingOverlayProps extends VariantProps<typeof loadingOverlayVariants> {
  label?: string;
  showSpinner?: boolean;
  spinnerSize?: "sm" | "default" | "lg" | "xl";
  children?: React.ReactNode;
  className?: string;
}

const LoadingOverlay = React.forwardRef<HTMLDivElement, LoadingOverlayProps>(
  ({ className, label, showSpinner = true, spinnerSize = "default", children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(loadingOverlayVariants(), className)}
      {...props}
      role="status"
      aria-label={label ?? "Loading"}
      aria-busy="true"
    >
      <div className="flex flex-col items-center gap-4">
        {showSpinner && <Spinner size={spinnerSize} label={label} />}
        {label && <p className="text-body-md text-staff-on-surface-variant">{label}</p>}
        {children}
      </div>
    </div>
  )
);
LoadingOverlay.displayName = "LoadingOverlay";

/* ============================================================
   Pre-built Skeleton Layouts
   ============================================================ */

export const SkeletonCard = ({ variant = "default", className, ...props }: {
  variant?: "default" | "compact" | "detailed";
  className?: string;
}) => {
  if (variant === "compact") {
    return (
      <div className={cn("space-y-3 p-4", className)} {...props}>
        <Skeleton variant="heading" width="half" />
        <Skeleton variant="text" width="half" />
        <Skeleton variant="text" width="third" />
      </div>
    );
  }

  if (variant === "detailed") {
    return (
      <div className={cn("space-y-4 p-6", className)} {...props}>
        <div className="flex items-center gap-3">
          <Skeleton variant="avatar" className="w-12 h-12" />
          <div className="flex-1 space-y-2">
            <Skeleton variant="heading" width="half" />
            <Skeleton variant="text" width="third" />
          </div>
        </div>
        <Skeleton variant="text" width="full" />
        <Skeleton variant="text" width="half" />
        <div className="flex gap-2">
          <Skeleton variant="badge" />
          <Skeleton variant="badge" />
          <Skeleton variant="badge" />
        </div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-4 p-4", className)} {...props}>
      <div className="flex items-center gap-3">
        <Skeleton variant="avatar" className="w-10 h-10" />
        <div className="flex-1 space-y-2">
          <Skeleton variant="heading" width="half" />
          <Skeleton variant="text" width="third" />
        </div>
      </div>
      <Skeleton variant="text" width="full" />
      <Skeleton variant="text" width="half" />
    </div>
  );
};

export const SkeletonList = ({ count = 5, variant = "default", className, ...props }: {
  count?: number;
  variant?: "default" | "compact" | "detailed";
  className?: string;
}) => (
  <div className={cn("space-y-3", className)} {...props}>
    {Array.from({ length: count }, (_, i) => (
      <SkeletonCard key={i} variant={variant} />
    ))}
  </div>
);

export const SkeletonTable = ({ rows = 5, columns = 4, className, ...props }: {
  rows?: number;
  columns?: number;
  className?: string;
}) => (
  <div className={cn("space-y-2", className)} {...props}>
    {/* Header */}
    <div className="flex gap-4">
      {Array.from({ length: columns }, (_, i) => (
        <Skeleton key={i} variant="text" width="auto" className="h-5 flex-1" />
      ))}
    </div>
    {/* Rows */}
    {Array.from({ length: rows }, (_, i) => (
      <div key={i} className="flex gap-4">
        {Array.from({ length: columns }, (_, j) => (
          <Skeleton key={j} variant="text" width="auto" className="h-4 flex-1" />
        ))}
      </div>
    ))}
  </div>
);

export const SkeletonDashboard = ({ className, ...props }: { className?: string }) => (
  <div className={cn("space-y-6", className)} {...props}>
    {/* Metrics Row */}
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }, (_, i) => (
        <SkeletonCard key={i} variant="compact" />
      ))}
    </div>
    {/* Charts Area */}
    <div className="grid gap-6 lg:grid-cols-2">
      <SkeletonCard variant="detailed" />
      <SkeletonCard variant="detailed" />
    </div>
    {/* Table/List */}
    <SkeletonCard variant="default" />
  </div>
);

export const SkeletonChat = ({ messageCount = 5, className, ...props }: {
  messageCount?: number;
  className?: string;
}) => (
  <div className={cn("space-y-4 max-w-md", className)} {...props}>
    {Array.from({ length: messageCount }, (_, i) => (
      <div key={i} className={cn("flex gap-3", i % 2 === 0 ? "justify-end" : "justify-start")}>
        <Skeleton variant="avatar" className="w-8 h-8 flex-shrink-0" />
        <Skeleton variant="text" width={i % 3 === 0 ? "half" : "full"} className="rounded-2xl px-4 py-2" />
      </div>
    ))}
  </div>
);

export {
  Skeleton,
  Spinner,
  Pulse,
  LoadingOverlay,
  skeletonVariants,
  spinnerVariants,
  pulseVariants,
  loadingOverlayVariants,
};
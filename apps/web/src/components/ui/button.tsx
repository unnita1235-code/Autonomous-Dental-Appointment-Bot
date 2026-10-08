"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/design-system";

const buttonVariants = cva(
  "inline-flex items-center justify-center font-semibold transition-all duration-200 rounded-full focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        primary:
          "min-h-[52px] min-w-[52px] bg-patient-primary text-patient-on-primary hover:bg-patient-primary-hover active:scale-[0.98] shadow-md px-6",
        "primary-staff":
          "min-h-[36px] min-w-[36px] bg-staff-primary text-staff-on-primary hover:bg-staff-primary-hover active:scale-[0.98] shadow-sm px-4 text-sm",
        secondary:
          "min-h-[52px] min-w-[52px] bg-patient-surface-lowest text-patient-primary border-2 border-patient-primary hover:bg-patient-primary-fixed active:scale-[0.98] px-6",
        ghost:
          "min-h-[52px] min-w-[52px] text-patient-on-surface-variant hover:bg-patient-surface-variant active:scale-[0.98] px-6",
        ai:
          "min-h-[52px] min-w-[52px] bg-staff-ai text-staff-on-ai hover:bg-staff-ai-hover active:scale-[0.98] shadow-md px-6",
        "ai-staff":
          "min-h-[36px] min-w-[36px] bg-staff-ai text-staff-on-ai hover:bg-staff-ai-hover active:scale-[0.98] shadow-sm px-4 text-sm",
        outline:
          "min-h-[52px] min-w-[52px] border-2 border-staff-border bg-staff-surface text-staff-on-surface hover:bg-staff-surface-variant active:scale-[0.98] px-4",
        danger:
          "min-h-[52px] min-w-[52px] bg-staff-error text-staff-on-error hover:bg-staff-error/90 active:scale-[0.98] shadow-md px-6",
      },
      size: {
        default: "",
        sm: "text-sm px-3",
        lg: "text-lg px-8",
        icon: "p-0 aspect-square",
      },
      fullWidth: {
        true: "w-full",
        false: "",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
      fullWidth: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      fullWidth,
      asChild = false,
      loading = false,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, fullWidth, className }))}
        ref={ref}
        disabled={disabled || loading}
        aria-busy={loading}
        {...props}
      >
        {loading ? (
          <>
            <svg
              className="mr-2 h-4 w-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Loading...</span>
          </>
        ) : (
          children
        )}
      </Comp>
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
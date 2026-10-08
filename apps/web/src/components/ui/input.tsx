"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/design-system";

const inputVariants = cva(
  "w-full rounded-xl bg-patient-surface-lowest border-1.5 border-patient-outline-variant text-body-md text-patient-on-surface placeholder-patient-on-surface-variant outline-none transition-all duration-150 focus:border-patient-primary focus:ring-2 focus:ring-patient-primary/20 focus:shadow-[0_0_0_4px_rgba(37,99,235,0.15)] disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        patient: "min-h-[52px] text-body-md px-4",
        "patient-sm": "min-h-[48px] text-body-sm px-3",
        staff: "min-h-[36px] rounded-md bg-staff-surface border-staff-border text-sm text-staff-on-surface placeholder-staff-on-surface-muted focus:border-staff-border-focus focus:ring-2 focus:ring-staff-border-focus-ring focus:shadow-[0_0_0_4px_rgba(37,99,235,0.15)]",
        "staff-lg": "min-h-[44px] rounded-lg text-base",
      },
      error: {
        true: "border-staff-error focus:border-staff-error focus:ring-staff-error/20",
        false: "",
      },
    },
    defaultVariants: {
      variant: "patient",
      error: false,
    },
  }
);

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement>,
    VariantProps<typeof inputVariants> {
  label?: string;
  errorMessage?: string;
  hint?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      variant,
      error,
      label,
      errorMessage,
      hint,
      id,
      ...props
    },
    ref
  ) => {
    const [inputId] = React.useState(() => id || `input-${Math.random().toString(36).slice(2, 9)}`);
    const errorId = `${inputId}-error`;
    const hintId = `${inputId}-hint`;
    const hasError = error || !!errorMessage;
    const describedBy = [hasError && errorId, hint && hintId].filter(Boolean).join(" ") || undefined;

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-label-md font-semibold text-patient-on-surface"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(inputVariants({ variant, error: hasError, className }))}
          aria-invalid={hasError}
          aria-describedby={describedBy}
          {...props}
        />
        {hasError && (
          <p
            id={errorId}
            className="text-caption text-staff-error flex items-center gap-1"
            role="alert"
          >
            <svg className="h-3 w-3 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {errorMessage}
          </p>
        )}
        {hint && !hasError && (
          <p id={hintId} className="text-caption text-patient-on-surface-variant">
            {hint}
          </p>
        )}
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input, inputVariants };
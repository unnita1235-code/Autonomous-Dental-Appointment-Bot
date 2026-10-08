"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/design-system";

const cardVariants = cva(
  "transition-shadow duration-200",
  {
    variants: {
      variant: {
        patient:
          "bg-patient-surface-lowest border border-patient-outline-variant rounded-2xl shadow-elevation-1 hover:shadow-elevation-hover",
        "patient-elevated":
          "bg-patient-surface-lowest border border-patient-outline-variant rounded-2xl shadow-elevation-2",
        staff:
          "bg-staff-surface border border-staff-border rounded-xl shadow-elevation-0 hover:shadow-elevation-1",
        "staff-elevated":
          "bg-staff-surface border border-staff-border rounded-xl shadow-elevation-1",
        ai:
          "bg-staff-surface border border-staff-border rounded-xl shadow-ai-glow",
      },
      padding: {
        patient: "p-6 md:p-8",
        "patient-sm": "p-4",
        staff: "p-3 md:p-4",
        "staff-lg": "p-5 md:p-6",
        none: "p-0",
      },
    },
    defaultVariants: {
      variant: "patient",
      padding: "patient",
    },
  }
);

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, padding, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(cardVariants({ variant, padding, className }))}
        {...props}
      />
    );
  }
);
Card.displayName = "Card";

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("space-y-1.5", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("font-heading text-headline-sm font-bold text-patient-on-surface", className)}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-body-md text-patient-on-surface-variant", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("pt-2", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center pt-4 space-x-2", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent, cardVariants };
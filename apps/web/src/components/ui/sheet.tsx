"use client";

import * as React from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { cn } from "@/lib/design-system";

const Sheet = Dialog.Root;
const SheetTrigger = Dialog.Trigger;
const SheetClose = Dialog.Close;
const SheetPortal = Dialog.Portal;

const SheetOverlay = React.forwardRef<
  React.ElementRef<typeof Dialog.Overlay>,
  React.ComponentPropsWithoutRef<typeof Dialog.Overlay>
>(({ className, ...props }, ref) => (
  <Dialog.Overlay
    ref={ref}
    className={cn("fixed inset-0 z-40 bg-staff-on-surface/40 backdrop-blur-sm", className)}
    {...props}
  />
));
SheetOverlay.displayName = Dialog.Overlay.displayName;

const SheetContent = React.forwardRef<
  React.ElementRef<typeof Dialog.Content>,
  React.ComponentPropsWithoutRef<typeof Dialog.Content> & {
    variant?: "patient" | "staff";
    side?: "right" | "left" | "top" | "bottom";
  }
>(({ className, children, variant = "staff", side = "right", ...props }, ref) => {
  const sideStyles = {
    right: "fixed right-0 top-0 z-50 h-full w-full max-w-xl border-l",
    left: "fixed left-0 top-0 z-50 h-full w-full max-w-xl border-r",
    top: "fixed top-0 left-0 z-50 w-full h-auto max-h-[80vh] border-b",
    bottom: "fixed bottom-0 left-0 z-50 w-full h-auto max-h-[80vh] border-t",
  };

  const variantStyles = {
    patient: "bg-patient-surface-lowest border-patient-outline-variant shadow-elevation-3",
    staff: "bg-staff-surface border-staff-border shadow-elevation-3",
  };

  return (
    <SheetPortal>
      <SheetOverlay />
      <Dialog.Content
        ref={ref}
        className={cn(
          sideStyles[side],
          variantStyles[variant],
          "p-6",
          className
        )}
        {...props}
      >
        <Dialog.Close className={cn(
          "absolute top-4 rounded-md p-1 transition hover:bg-staff-surface-variant",
          side === "right" && "right-4",
          side === "left" && "left-4",
          side === "top" && "right-4",
          side === "bottom" && "right-4"
        )}>
          <X className="h-4 w-4 text-staff-on-surface-variant" />
        </Dialog.Close>
        {children}
      </Dialog.Content>
    </SheetPortal>
  );
});
SheetContent.displayName = Dialog.Content.displayName;

const SheetHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>): JSX.Element => (
  <div className={cn("space-y-1.5", className)} {...props} />
);

const SheetTitle = React.forwardRef<
  React.ElementRef<typeof Dialog.Title>,
  React.ComponentPropsWithoutRef<typeof Dialog.Title>
>(({ className, ...props }, ref) => (
  <Dialog.Title
    ref={ref}
    className={cn("font-heading text-headline-sm font-semibold text-staff-on-surface", className)}
    {...props}
  />
));
SheetTitle.displayName = Dialog.Title.displayName;

const SheetDescription = React.forwardRef<
  React.ElementRef<typeof Dialog.Description>,
  React.ComponentPropsWithoutRef<typeof Dialog.Description>
>(({ className, ...props }, ref) => (
  <Dialog.Description
    ref={ref}
    className={cn("text-body-md text-staff-on-surface-variant", className)}
    {...props}
  />
));
SheetDescription.displayName = Dialog.Description.displayName;

export {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetOverlay,
  SheetPortal,
  SheetTitle,
  SheetTrigger
};
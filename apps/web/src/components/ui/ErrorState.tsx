"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { AlertCircle, AlertTriangle, XCircle, WifiOff, Server, RefreshCw, Home, ChevronLeft, Shield, Lock, Search } from "lucide-react";

import { cn } from "@/lib/design-system";
import { Button } from "@/components/ui/button";

const errorStateVariants = cva(
  "flex flex-col items-center justify-center text-center py-12 px-4",
  {
    variants: {
      size: {
        sm: "py-6 px-3",
        default: "py-12 px-4",
        lg: "py-16 px-6",
        full: "flex-1",
      },
      tone: {
        error: "",
        warning: "",
        info: "",
        network: "",
        auth: "",
        notFound: "",
        server: "",
        permission: "",
      },
    },
    defaultVariants: {
      size: "default",
      tone: "error",
    },
  }
);

const iconMap = {
  error: AlertCircle,
  warning: AlertTriangle,
  info: AlertCircle,
  network: WifiOff,
  auth: Lock,
  notFound: Search,
  server: Server,
  permission: Shield,
} as const;

const toneClasses = {
  error: "text-staff-error",
  warning: "text-staff-warning",
  info: "text-staff-info",
  network: "text-staff-warning",
  auth: "text-staff-error",
  notFound: "text-staff-on-surface-muted",
  server: "text-staff-error",
  permission: "text-staff-error",
} as const;

const bgClasses = {
  error: "bg-staff-error-container",
  warning: "bg-staff-warning-container",
  info: "bg-staff-info-container",
  network: "bg-staff-warning-container",
  auth: "bg-staff-error-container",
  notFound: "bg-staff-surface-variant",
  server: "bg-staff-error-container",
  permission: "bg-staff-error-container",
} as const;

const textOnClasses = {
  error: "text-staff-on-error-container",
  warning: "text-staff-on-warning-container",
  info: "text-staff-on-info",
  network: "text-staff-on-warning-container",
  auth: "text-staff-on-error-container",
  notFound: "text-staff-on-surface",
  server: "text-staff-on-error-container",
  permission: "text-staff-on-error-container",
} as const;

export interface ErrorStateProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof errorStateVariants> {
  tone?: "error" | "warning" | "info" | "network" | "auth" | "notFound" | "server" | "permission";
  title: string;
  description?: string | React.ReactNode;
  code?: string | number;
  primaryAction?: {
    label: string;
    onClick: () => void;
    variant?: "primary" | "secondary" | "ghost";
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
    variant?: "primary" | "secondary" | "ghost";
  };
  dismissible?: boolean;
  onDismiss?: () => void;
  showCode?: boolean;
  illustration?: React.ReactNode;
}

const ErrorState = React.forwardRef<HTMLDivElement, ErrorStateProps>(
  (
    {
      className,
      size = "default",
      tone = "error",
      title,
      description,
      code,
      primaryAction,
      secondaryAction,
      dismissible = false,
      onDismiss,
      showCode = true,
      illustration,
      children,
      ...props
    },
    ref
  ) => {
    const IconComponent = iconMap[tone];
    const toneClass = toneClasses[tone];
    const bgClass = bgClasses[tone];
    const textOnClass = textOnClasses[tone];

    return (
      <div
        ref={ref}
        className={cn(errorStateVariants({ size, tone, className }))}
        {...props}
        role="alert"
      >
        {/* Dismiss Button */}
        {dismissible && onDismiss && (
          <div className="absolute top-4 right-4">
            <button
              type="button"
              onClick={onDismiss}
              className="p-1 rounded-lg text-staff-on-surface-muted hover:text-staff-on-surface hover:bg-staff-surface-variant transition-colors"
              aria-label="Dismiss"
            >
              <XCircle className="h-5 w-5" />
            </button>
          </div>
        )}

        {/* Illustration - only rendered when a custom illustration is supplied.
            The tone icon itself is rendered by the Icon Badge below. */}
        {illustration && (
          <div
            className={cn(
              "mb-6 flex items-center justify-center",
              size === "sm" && "text-4xl",
              size === "default" && "text-6xl",
              size === "lg" && "text-8xl",
              toneClass
            )}
            aria-hidden="true"
          >
            {illustration}
          </div>
        )}

        {/* Icon Badge */}
        <div
          className={cn(
            "mb-4 inline-flex items-center justify-center rounded-full",
            "p-3",
            size === "sm" && "p-2",
            size === "lg" && "p-4",
            bgClass
          )}
          aria-hidden="true"
        >
          <IconComponent className={cn(textOnClass, size === "sm" && "h-6 w-6", size === "default" && "h-8 w-8", size === "lg" && "h-12 w-12")} />
        </div>

        {/* Title */}
        <h2 className={cn(
          "font-heading font-semibold",
          size === "sm" && "text-lg",
          size === "default" && "text-headline-sm",
          size === "lg" && "text-headline-md",
          "text-staff-on-surface"
        )}>
          {title}
        </h2>

        {/* Code */}
        {code && showCode && (
          <span className="mb-3 inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-caption font-mono font-medium bg-staff-surface-variant text-staff-on-surface-muted">
            {typeof code === "number" ? `Error ${code}` : code}
          </span>
        )}

        {/* Description */}
        {description && (
          <p className={cn(
            "max-w-md text-staff-on-surface-variant",
            size === "sm" && "text-sm",
            size === "default" && "text-body-md",
            size === "lg" && "text-body-lg"
          )}>
            {description}
          </p>
        )}

        {/* Actions */}
        {(primaryAction || secondaryAction) && (
          <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
            {primaryAction && (
              <Button
                onClick={primaryAction.onClick}
                variant={primaryAction.variant === "secondary" ? "secondary" : primaryAction.variant === "ghost" ? "ghost" : "primary"}
                size="lg"
              >
                {primaryAction.label}
              </Button>
            )}
            {secondaryAction && (
              <Button variant="ghost" onClick={secondaryAction.onClick}>
                {secondaryAction.label}
              </Button>
            )}
          </div>
        )}

        {/* Default Recovery Actions */}
        {!primaryAction && !secondaryAction && (
          <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Button variant="primary" onClick={() => window.location.reload()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
            <Button variant="ghost" onClick={() => window.history.back()}>
              <ChevronLeft className="h-4 w-4 mr-2" />
              Go Back
            </Button>
          </div>
        )}

        {children}
      </div>
    );
  }
);
ErrorState.displayName = "ErrorState";

/* ============================================================
   Pre-configured Error States
   ============================================================ */

export const NetworkError = ({ onRetry, onGoHome, ...props }: {
  onRetry?: () => void;
  onGoHome?: () => void;
} & Omit<ErrorStateProps, "tone" | "title" | "description" | "primaryAction" | "secondaryAction">) => (
  <ErrorState
    {...props}
    tone="network"
    title="Connection Lost"
    description="Unable to reach the server. Please check your internet connection and try again."
    primaryAction={onRetry ? { label: "Retry", onClick: onRetry } : { label: "Retry", onClick: () => window.location.reload() }}
    secondaryAction={onGoHome ? { label: "Go Home", onClick: onGoHome } : undefined}
  />
);

export const ServerError = ({ onRetry, onContactSupport, ...props }: {
  onRetry?: () => void;
  onContactSupport?: () => void;
} & Omit<ErrorStateProps, "tone" | "title" | "description" | "primaryAction" | "secondaryAction">) => (
  <ErrorState
    {...props}
    tone="server"
    title="Server Error"
    description="Something went wrong on our end. Our team has been notified and is working on a fix."
    primaryAction={onRetry ? { label: "Try Again", onClick: onRetry } : { label: "Try Again", onClick: () => window.location.reload() }}
    secondaryAction={onContactSupport ? { label: "Contact Support", onClick: onContactSupport, variant: "ghost" } : undefined}
  />
);

export const NotFoundError = ({ onGoHome, onSearch, ...props }: {
  onGoHome?: () => void;
  onSearch?: () => void;
} & Omit<ErrorStateProps, "tone" | "title" | "description" | "primaryAction" | "secondaryAction">) => (
  <ErrorState
    {...props}
    tone="notFound"
    title="Page Not Found"
    description="The page you're looking for doesn't exist or has been moved."
    primaryAction={onGoHome ? { label: "Go Home", onClick: onGoHome } : { label: "Go Home", onClick: () => window.location.href = "/" }}
    secondaryAction={onSearch ? { label: "Search", onClick: onSearch, variant: "ghost" } : undefined}
  />
);

export const AuthError = ({ onLogin, onGoHome, ...props }: {
  onLogin?: () => void;
  onGoHome?: () => void;
} & Omit<ErrorStateProps, "tone" | "title" | "description" | "primaryAction" | "secondaryAction">) => (
  <ErrorState
    {...props}
    tone="auth"
    title="Authentication Required"
    description="Your session has expired or you don't have permission to access this page."
    primaryAction={onLogin ? { label: "Sign In", onClick: onLogin } : { label: "Sign In", onClick: () => window.location.href = "/login" }}
    secondaryAction={onGoHome ? { label: "Go Home", onClick: onGoHome, variant: "ghost" } : undefined}
  />
);

export const PermissionError = ({ onGoHome, onContactAdmin, ...props }: {
  onGoHome?: () => void;
  onContactAdmin?: () => void;
} & Omit<ErrorStateProps, "tone" | "title" | "description" | "primaryAction" | "secondaryAction">) => (
  <ErrorState
    {...props}
    tone="permission"
    title="Access Denied"
    description="You don't have permission to view this resource. Please contact your administrator if you believe this is an error."
    primaryAction={onGoHome ? { label: "Go Home", onClick: onGoHome } : { label: "Go Home", onClick: () => window.location.href = "/" }}
    secondaryAction={onContactAdmin ? { label: "Contact Admin", onClick: onContactAdmin, variant: "ghost" } : undefined}
  />
);

export const FormValidationError = ({ errors, onRetry, ...props }: {
  errors?: string[];
  onRetry?: () => void;
} & Omit<ErrorStateProps, "tone" | "title" | "description" | "primaryAction">) => (
  <ErrorState
    {...props}
    tone="warning"
    title="Please check your input"
    description={
      <div className="text-left max-w-md space-y-1">
        {errors?.map((error, i) => (
          <div key={i} className="flex items-center gap-2 text-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-staff-warning flex-shrink-0" />
            {error}
          </div>
        ))}
      </div>
    }
    primaryAction={onRetry ? { label: "Fix & Resubmit", onClick: onRetry } : undefined}
  />
);

export { ErrorState, errorStateVariants };
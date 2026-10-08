"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/design-system";

/* ============================================================
   DentalFlow AI Logo Component
   ============================================================ */

const logoVariants = cva(
  "inline-flex items-center gap-2",
  {
    variants: {
      size: {
        sm: "text-lg",
        default: "text-xl",
        lg: "text-2xl",
        xl: "text-3xl",
      },
      variant: {
        primary: "text-staff-primary",
        onPrimary: "text-staff-on-primary",
        onSurface: "text-staff-on-surface",
        white: "text-white",
        patient: "text-patient-primary",
      },
      weight: {
        normal: "font-medium",
        bold: "font-bold",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "primary",
      weight: "bold",
    },
  }
);

const iconVariants = cva(
  "flex-shrink-0",
  {
    variants: {
      size: {
        sm: "w-5 h-5",
        default: "w-6 h-6",
        lg: "w-8 h-8",
        xl: "w-10 h-10",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
);

export interface DentalFlowLogoProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof logoVariants> {
  showIcon?: boolean;
  showText?: boolean;
  iconOnly?: boolean;
  tagline?: string;
}

const DentalFlowLogo = React.forwardRef<HTMLSpanElement, DentalFlowLogoProps>(
  (
    {
      className,
      size,
      variant,
      weight,
      showIcon = true,
      showText = true,
      iconOnly = false,
      tagline,
      children,
      ...props
    },
    ref
  ) => {
    const effectiveShowIcon = showIcon && !iconOnly;
    const effectiveShowText = showText && !iconOnly;
    // The logo renders in more than one place per page (header and footer), so
    // the gradient needs a per-instance id to stay a unique document id.
    const gradientId = `logoGradient-${React.useId()}`;

    return (
      <span
        ref={ref}
        className={cn(logoVariants({ size, variant, weight, className }))}
        {...props}
        aria-label="DentalFlow AI"
      >
        {effectiveShowIcon && (
          <svg
            className={cn(iconVariants({ size }), "text-current")}
            viewBox="0 0 32 32"
            fill="none"
            aria-hidden="true"
          >
            {/* DentalFlow AI Logo Mark - Tooth + AI sparkle */}
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor="#2563EB" />
                <stop offset="100%" stopColor="#7C3AED" />
              </linearGradient>
            </defs>
            {/* Tooth shape */}
            <path
              d="M16 4C16 2.34 17.34 1 19 1C20.66 1 22 2.34 22 4C22 10 19 22 16 28C13 22 10 10 10 4C10 2.34 11.34 1 13 1C14.66 1 16 2.34 16 4Z"
              fill={`url(#${gradientId})`}
            />
            {/* Inner tooth highlight */}
            <path
              d="M16 8C16 6.34 17.34 5 19 5C20.66 5 22 6.34 22 8C22 13 19 20 16 24C13 20 10 13 10 8C10 6.34 11.34 5 13 5C14.66 5 16 6.34 16 8Z"
              fill="white"
              fillOpacity="0.2"
            />
            {/* AI Sparkle */}
            <g fill="white" fillOpacity="0.9">
              <path d="M24 8v3" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M24 14v3" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M21 11h3" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M27 11h3" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M22.5 9.5l1.5 1.5" stroke="white" strokeWidth="1" strokeLinecap="round" />
              <path d="M25.5 12.5l1.5 1.5" stroke="white" strokeWidth="1" strokeLinecap="round" />
              <path d="M22.5 12.5l1.5-1.5" stroke="white" strokeWidth="1" strokeLinecap="round" />
              <path d="M25.5 9.5l1.5-1.5" stroke="white" strokeWidth="1" strokeLinecap="round" />
            </g>
          </svg>
        )}
        {effectiveShowText && (
          <span className="tracking-tight">DentalFlow<span className="font-normal"> AI</span></span>
        )}
        {tagline && (
          <span className="text-caption font-normal opacity-80">{tagline}</span>
        )}
        {children}
      </span>
    );
  }
);
DentalFlowLogo.displayName = "DentalFlowLogo";

/* ============================================================
   DentalFlow AI Avatar Component
   ============================================================ */

const avatarVariants = cva(
  "inline-flex items-center justify-center overflow-hidden rounded-full font-semibold",
  {
    variants: {
      size: {
        xs: "w-6 h-6 text-xs",
        sm: "w-8 h-8 text-sm",
        md: "w-10 h-10 text-base",
        lg: "w-12 h-12 text-lg",
        xl: "w-16 h-16 text-xl",
        "2xl": "w-20 h-20 text-2xl",
        "3xl": "w-28 h-28 text-3xl",
      },
      variant: {
        primary: "bg-gradient-to-br from-staff-primary to-staff-ai text-staff-on-primary",
        ai: "bg-gradient-to-br from-staff-ai to-staff-ai-cyan text-staff-on-ai",
        patient: "bg-gradient-to-br from-patient-primary to-patient-secondary text-patient-on-primary",
        neutral: "bg-staff-surface-variant text-staff-on-surface-variant",
      },
      online: {
        true: "relative after:absolute after:bottom-0 after:right-0 after:w-2.5 after:h-2.5 after:rounded-full after:bg-staff-success after:ring-2 after:ring-staff-surface",
        false: "",
      },
    },
    defaultVariants: {
      size: "md",
      variant: "ai",
      online: false,
    },
  }
);

export interface DentalFlowAvatarProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof avatarVariants> {
  src?: string | null;
  alt?: string;
  fallback?: string;
  fallbackIcon?: React.ReactNode;
  status?: "online" | "offline" | "busy" | "away";
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

const DentalFlowAvatar = React.forwardRef<HTMLDivElement, DentalFlowAvatarProps>(
  (
    {
      className,
      size,
      variant,
      online,
      src,
      alt,
      fallback,
      fallbackIcon,
      status,
      children,
      ...props
    },
    ref
  ) => {
    const [imageError, setImageError] = React.useState(false);
    const showFallback = !src || imageError;
    const isOnline = status === "online" || online;

    return (
      <div
        ref={ref}
        className={cn(avatarVariants({ size, variant, online: isOnline, className }))}
        {...props}
      >
        {!showFallback && src ? (
          <img
            src={src}
            alt={alt || ""}
            className="w-full h-full object-cover"
            onError={() => setImageError(true)}
          />
        ) : fallbackIcon ? (
          <span className="flex items-center justify-center w-full h-full" aria-hidden="true">
            {fallbackIcon}
          </span>
        ) : fallback ? (
          <span className="font-semibold text-body-md" aria-hidden="true">
            {getInitials(fallback)}
          </span>
        ) : (
          <svg
            className="w-1/2 h-1/2 text-current opacity-60"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
        )}
        {children}
      </div>
    );
  }
);
DentalFlowAvatar.displayName = "DentalFlowAvatar";

/* ============================================================
   DentalFlow AI Wordmark (Text-only logo)
   ============================================================ */

const wordmarkVariants = cva(
  "inline-flex items-baseline gap-1 font-heading tracking-tight",
  {
    variants: {
      size: {
        sm: "text-lg",
        default: "text-xl",
        lg: "text-2xl",
        xl: "text-3xl",
        "2xl": "text-4xl",
      },
      variant: {
        primary: "text-staff-primary",
        onPrimary: "text-staff-on-primary",
        onSurface: "text-staff-on-surface",
        white: "text-white",
        patient: "text-patient-primary",
        gradient: "bg-gradient-to-r from-staff-primary to-staff-ai bg-clip-text text-transparent",
      },
      weight: {
        normal: "font-medium",
        bold: "font-bold",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "gradient",
      weight: "bold",
    },
  }
);

export interface DentalFlowWordmarkProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof wordmarkVariants> {
  tagline?: string;
}

const DentalFlowWordmark = React.forwardRef<HTMLSpanElement, DentalFlowWordmarkProps>(
  (
    {
      className,
      size,
      variant,
      weight,
      tagline,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <span
        ref={ref}
        className={cn(wordmarkVariants({ size, variant, weight, className }))}
        {...props}
        aria-label="DentalFlow AI"
      >
        <span className="font-bold">DentalFlow</span>
        <span className="font-normal"> AI</span>
        {tagline && (
          <span className="ml-2 text-caption font-normal opacity-70">{tagline}</span>
        )}
        {children}
      </span>
    );
  }
);
DentalFlowWordmark.displayName = "DentalFlowWordmark";

/* ============================================================
   DentalFlow AI Favicon / App Icon
   ============================================================ */

export function DentalFlowFavicon({ size = 32, className }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="faviconGradient" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#2563EB" />
          <stop offset="100%" stopColor="#7C3AED" />
        </linearGradient>
      </defs>
      <path
        d="M16 4C16 2.34 17.34 1 19 1C20.66 1 22 2.34 22 4C22 10 19 22 16 28C13 22 10 10 10 4C10 2.34 11.34 1 13 1C14.66 1 16 2.34 16 4Z"
        fill="url(#faviconGradient)"
      />
      <g fill="white" fillOpacity="0.9">
        <path d="M24 8v3" stroke="white" strokeWidth={1.5} strokeLinecap="round" />
        <path d="M24 14v3" stroke="white" strokeWidth={1.5} strokeLinecap="round" />
        <path d="M21 11h3" stroke="white" strokeWidth={1.5} strokeLinecap="round" />
        <path d="M27 11h3" stroke="white" strokeWidth={1.5} strokeLinecap="round" />
      </g>
    </svg>
  );
}

export {
  DentalFlowLogo,
  DentalFlowAvatar,
  DentalFlowWordmark,
  logoVariants,
  avatarVariants,
  wordmarkVariants,
};
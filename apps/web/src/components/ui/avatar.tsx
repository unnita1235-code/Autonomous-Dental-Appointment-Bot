"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/design-system";

const avatarVariants = cva(
  "inline-flex items-center justify-center overflow-hidden rounded-full bg-patient-surface-variant text-patient-on-surface-variant font-semibold",
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
      shape: {
        circle: "rounded-full",
        square: "rounded-xl",
      },
      online: {
        true: "relative after:absolute after:bottom-0 after:right-0 after:w-2.5 after:h-2.5 after:rounded-full after:bg-patient-secondary after:ring-2 after:ring-patient-surface-lowest",
        false: "",
      },
    },
    defaultVariants: {
      size: "md",
      shape: "circle",
      online: false,
    },
  }
);

export interface AvatarProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof avatarVariants> {
  src?: string | null;
  alt?: string;
  fallback?: string;
  fallbackIcon?: React.ReactNode;
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  (
    {
      className,
      size,
      shape,
      online,
      src,
      alt,
      fallback,
      fallbackIcon,
      ...props
    },
    ref
  ) => {
    const [imageError, setImageError] = React.useState(false);

    const showFallback = !src || imageError;
    const initials = fallback || (fallbackIcon ? undefined : undefined);

    return (
      <div
        ref={ref}
        className={cn(avatarVariants({ size, shape, online, className }))}
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
            className="w-1/2 h-1/2 text-patient-on-surface-variant/50"
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
      </div>
    );
  }
);
Avatar.displayName = "Avatar";

export { Avatar, avatarVariants };
/**
 * DentalFlow AI Design System
 * Centralized design tokens, component variants, and utilities
 * Source: Stitch design tokens (patient + staff modes)
 */

import { cva, type VariantProps } from "class-variance-authority";
import { clsx, type ClassValue } from "clsx";

/* ============================================================
   Utility: cn() — clsx + tailwind-merge
   ============================================================ */
export const cn = (...inputs: ClassValue[]) => clsx(inputs);

/* ============================================================
   Design Tokens (TypeScript constants for non-CSS usage)
   ============================================================ */

export const tokens = {
  colors: {
    patient: {
      primary: {
        DEFAULT: "#004ac6",
        container: "#2563eb",
        fixed: "#dbe1ff",
        "fixed-dim": "#b4c5ff",
        "on-primary": "#ffffff",
        "on-primary-fixed": "#00174b",
        "on-primary-fixed-variant": "#003ea8",
      },
      secondary: {
        DEFAULT: "#006c49",
        container: "#6cf8bb",
        fixed: "#6ffbbe",
        "fixed-dim": "#4edea3",
        "on-secondary": "#ffffff",
        "on-secondary-fixed": "#002113",
        "on-secondary-fixed-variant": "#005236",
      },
      tertiary: {
        DEFAULT: "#784b00",
        container: "#996100",
        fixed: "#ffddb8",
        "fixed-dim": "#ffb95f",
        "on-tertiary": "#ffffff",
        "on-tertiary-fixed": "#2a1700",
        "on-tertiary-fixed-variant": "#653e00",
      },
      error: {
        DEFAULT: "#ba1a1a",
        container: "#ffdad6",
        "on-error": "#ffffff",
        "on-error-container": "#93000a",
      },
      surface: {
        lowest: "#ffffff",
        low: "#f2f3ff",
        DEFAULT: "#eaedff",
        high: "#e2e7ff",
        highest: "#dae2fd",
      },
      "surface-variant": "#dae2fd",
      "on-surface": "#131b2e",
      "on-surface-variant": "#434655",
      outline: "#737686",
      "outline-variant": "#c3c6d7",
      background: "#faf8ff",
      "on-background": "#131b2e",
    },
    staff: {
      primary: {
        DEFAULT: "#2563EB",
        hover: "#1D4ED8",
        container: "#DBEAFE",
        "on-primary": "#ffffff",
        "on-container": "#1E3A8A",
      },
      ai: {
        DEFAULT: "#7C3AED",
        hover: "#6D28D9",
        container: "#F5F3FF",
        "on-ai": "#ffffff",
        "on-container": "#4C1D95",
        cyan: "#06B6D4",
        "cyan-container": "#ECFEFF",
        "on-cyan": "#164E63",
      },
      background: {
        DEFAULT: "#F8FAFC",
        dark: "#0F172A",
        rail: "#0F172A",
        card: "#FFFFFF",
      },
      surface: {
        DEFAULT: "#FFFFFF",
        variant: "#F1F5F9",
        rail: "#0F172A",
      },
      "on-surface": "#0F172A",
      "on-surface-variant": "#475569",
      "on-surface-muted": "#94A3B8",
      border: {
        DEFAULT: "#E2E8F0",
        dark: "#1E293B",
        focus: "#2563EB",
        "focus-ring": "rgba(37, 99, 235, 0.2)",
      },
      success: {
        DEFAULT: "#10B981",
        container: "#ECFDF5",
        border: "#A7F3D0",
        "on-success": "#ffffff",
        "on-container": "#065F46",
      },
      warning: {
        DEFAULT: "#F59E0B",
        container: "#FFFBEB",
        border: "#FDE68A",
        "on-warning": "#ffffff",
        "on-container": "#92400E",
      },
      error: {
        DEFAULT: "#EF4444",
        container: "#FEF2F2",
        border: "#FECACA",
        "on-error": "#ffffff",
        "on-container": "#991B1B",
      },
      urgent: {
        DEFAULT: "#EF4444",
        container: "#FEF2F2",
        "on-urgent": "#ffffff",
      },
      info: {
        DEFAULT: "#3B82F6",
        container: "#EFF6FF",
        "on-info": "#ffffff",
      },
    },
  },
  fontFamily: {
    heading: "Plus Jakarta Sans, sans-serif",
    body: "Plus Jakarta Sans, sans-serif",
    mono: "JetBrains Mono, monospace",
  },
  fontSize: {
    "display-hero": "3rem",
    "display-hero-mobile": "2rem",
    "headline-xl": "48px",
    "headline-xl-mobile": "34px",
    "headline-lg": "36px",
    "headline-lg-mobile": "28px",
    "headline-md": "28px",
    "headline-sm": "22px",
    "body-xl": "20px",
    "body-lg": "18px",
    "body-md": "17px",
    "body-sm": "15px",
    "label-lg": "18px",
    "label-md": "16px",
    "label-sm": "14px",
    caption: "14px",
    "label-dense": "11px",
    "label-mono-stat": "12px",
  },
  spacing: {
    "space-xs": "0.25rem",
    "space-sm": "0.5rem",
    "space-md": "1rem",
    "space-lg": "1.5rem",
    "space-xl": "2.5rem",
    gutter: "1.5rem",
    "gutter-mobile": "1rem",
    "gutter-staff": "0.75rem",
    margin: "2rem",
    "margin-mobile": "1rem",
    "margin-patient": "2rem",
  },
  borderRadius: {
    DEFAULT: "0.5rem",
    sm: "0.25rem",
    md: "0.5rem",
    lg: "1rem",
    xl: "1.5rem",
    "2xl": "2rem",
    full: "9999px",
  },
  touchTarget: {
    DEFAULT: "48px",
    lg: "52px",
    sm: "36px",
  },
  shadows: {
    "elevation-0": "0 1px 3px 0 rgba(15, 23, 42, 0.04)",
    "elevation-1": "0 4px 20px rgba(15, 23, 42, 0.06)",
    "elevation-hover": "0 8px 24px rgba(15, 23, 42, 0.09)",
    "elevation-2": "0 12px 36px rgba(15, 23, 42, 0.12)",
    "elevation-3": "0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.04)",
    "ai-glow": "0 0 0 1px rgba(124, 58, 237, 0.25), 0 4px 20px -2px rgba(99, 102, 241, 0.12)",
  },
} as const;

/* ============================================================
   CVA Component Variants
   ============================================================ */

/* Button Variants */
export const buttonVariants = cva(
  "inline-flex items-center justify-center font-semibold transition-all duration-200 rounded-full focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        primary: "min-h-[52px] min-w-[52px] bg-patient-primary text-patient-on-primary hover:bg-patient-primary-hover active:scale-[0.98] shadow-md px-6",
        "primary-staff": "min-h-[36px] min-w-[36px] bg-staff-primary text-staff-on-primary hover:bg-staff-primary-hover active:scale-[0.98] shadow-sm px-4 text-sm",
        secondary: "min-h-[52px] min-w-[52px] bg-patient-surface-lowest text-patient-primary border-2 border-patient-primary hover:bg-patient-primary-fixed active:scale-[0.98] px-6",
        ghost: "min-h-[52px] min-w-[52px] text-patient-on-surface-variant hover:bg-patient-surface-variant active:scale-[0.98] px-6",
        ai: "min-h-[52px] min-w-[52px] bg-staff-ai text-staff-on-ai hover:bg-staff-ai-hover active:scale-[0.98] shadow-md px-6",
        "ai-staff": "min-h-[36px] min-w-[36px] bg-staff-ai text-staff-on-ai hover:bg-staff-ai-hover active:scale-[0.98] shadow-sm px-4 text-sm",
        outline: "min-h-[52px] min-w-[52px] border-2 border-staff-border bg-staff-surface text-staff-on-surface hover:bg-staff-surface-variant active:scale-[0.98] px-4",
        danger: "min-h-[52px] min-w-[52px] bg-staff-error text-staff-on-error hover:bg-staff-error/90 active:scale-[0.98] shadow-md px-6",
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

export type ButtonVariants = VariantProps<typeof buttonVariants>;

/* Card Variants */
export const cardVariants = cva(
  "transition-shadow duration-200",
  {
    variants: {
      variant: {
        patient: "bg-patient-surface-lowest border border-patient-outline-variant rounded-2xl shadow-elevation-1 hover:shadow-elevation-hover",
        "patient-elevated": "bg-patient-surface-lowest border border-patient-outline-variant rounded-2xl shadow-elevation-2",
        staff: "bg-staff-surface border border-staff-border rounded-xl shadow-elevation-0 hover:shadow-elevation-1",
        "staff-elevated": "bg-staff-surface border border-staff-border rounded-xl shadow-elevation-1",
        ai: "bg-staff-surface border border-staff-border rounded-xl shadow-ai-glow",
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

export type CardVariants = VariantProps<typeof cardVariants>;

/* Input Variants */
export const inputVariants = cva(
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

export type InputVariants = VariantProps<typeof inputVariants>;

/* Badge Variants */
export const badgeVariants = cva(
  "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-medium text-caption",
  {
    variants: {
      variant: {
        success: "bg-staff-success-container text-staff-on-success-container",
        warning: "bg-staff-warning-container text-staff-on-warning-container",
        error: "bg-staff-error-container text-staff-on-error-container",
        info: "bg-staff-info-container text-staff-on-info",
        ai: "bg-staff-ai-container text-staff-on-ai-container",
        "ai-cyan": "bg-staff-ai-cyan-container text-staff-on-ai-cyan",
        neutral: "bg-staff-surface-variant text-staff-on-surface-variant",
        "neutral-dark": "bg-staff-border text-staff-on-surface",
        patient: "bg-patient-secondary-fixed text-patient-on-secondary-fixed",
        "patient-warning": "bg-patient-tertiary-fixed text-patient-on-tertiary-fixed",
        "patient-error": "bg-patient-error-container text-patient-on-error-container",
      },
      size: {
        default: "",
        sm: "px-2 py-0.5 text-[11px]",
        lg: "px-3 py-1 text-sm",
      },
      dot: {
        true: "gap-1.5",
        false: "",
      },
    },
    defaultVariants: {
      variant: "neutral",
      size: "default",
      dot: false,
    },
  }
);

export type BadgeVariants = VariantProps<typeof badgeVariants>;

/* Avatar Variants */
export const avatarVariants = cva(
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

export type AvatarVariants = VariantProps<typeof avatarVariants>;

/* FAB Variants */
export const fabVariants = cva(
  "fixed bottom-6 right-6 z-50 rounded-full shadow-[0_10px_25px_-5px_rgba(15,23,42,0.4)] transition-all duration-200 flex items-center justify-center",
  {
    variants: {
      variant: {
        primary: "w-16 h-16 bg-patient-primary-container text-patient-on-primary hover:shadow-[0_14px_30px_-5px_rgba(15,23,42,0.5)] hover:-translate-y-0.5 active:scale-95 focus-visible:ring-4 focus-visible:ring-patient-primary/20",
        ai: "w-16 h-16 bg-staff-ai text-staff-on-ai hover:shadow-[0_14px_30px_-5px_rgba(124,58,237,0.5)] hover:-translate-y-0.5 active:scale-95 focus-visible:ring-4 focus-visible:ring-staff-ai/20",
        staff: "w-14 h-14 bg-staff-primary text-staff-on-primary hover:shadow-lg hover:-translate-y-0.5 active:scale-95 focus-visible:ring-4 focus-visible:ring-staff-primary/20",
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

export type FabVariants = VariantProps<typeof fabVariants>;

/* Tooltip Variants */
export const tooltipVariants = cva(
  "absolute z-50 px-3 py-2 text-caption rounded-xl shadow-elevation-3 whitespace-nowrap",
  {
    variants: {
      variant: {
        default: "bg-staff-surface-rail text-staff-on-surface",
        patient: "bg-patient-surface-highest text-patient-on-surface",
        ai: "bg-staff-ai text-staff-on-ai",
      },
      position: {
        top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
        bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
        left: "right-full top-1/2 -translate-y-1/2 mr-2",
        right: "left-full top-1/2 -translate-y-1/2 ml-2",
      },
    },
    defaultVariants: {
      variant: "default",
      position: "top",
    },
  }
);

export type TooltipVariants = VariantProps<typeof tooltipVariants>;

/* Separator Variants */
export const separatorVariants = cva("border-0", {
  variants: {
    orientation: {
      horizontal: "h-px w-full",
      vertical: "w-px h-full",
    },
    variant: {
      patient: "bg-patient-outline-variant",
      staff: "bg-staff-border",
      dark: "bg-staff-border-dark",
    },
  },
  defaultVariants: {
    orientation: "horizontal",
    variant: "patient",
  },
});

export type SeparatorVariants = VariantProps<typeof separatorVariants>;

/* ============================================================
   Mode Context Types
   ============================================================ */

export type ExperienceMode = "patient" | "staff";

export interface ModeContextValue {
  mode: ExperienceMode;
  toggleMode: () => void;
}

/* ============================================================
   Helper Functions
   ============================================================ */

/**
 * Get color token by path (e.g., "patient.primary.DEFAULT")
 */
export function getColorToken(path: string): string {
  const keys = path.split(".");
  let current: any = tokens.colors;
  for (const key of keys) {
    if (current && typeof current === "object" && key in current) {
      current = current[key];
    } else {
      return "";
    }
  }
  return typeof current === "string" ? current : "";
}

/**
 * Get spacing token by name
 */
export function getSpacingToken(name: keyof typeof tokens.spacing): string {
  return tokens.spacing[name];
}

/**
 * Check if reduced motion is preferred
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * Generate focus ring classes based on mode
 */
export function getFocusRingClasses(mode: ExperienceMode = "patient"): string {
  if (mode === "staff") {
    return "focus-visible:ring-2 focus-visible:ring-staff-border-focus focus-visible:ring-offset-2 focus-visible:ring-offset-staff-background";
  }
  return "focus-visible:ring-2 focus-visible:ring-patient-primary focus-visible:ring-offset-2 focus-visible:ring-offset-patient-background";
}

/**
 * Generate touch target classes based on mode and context
 */
export function getTouchTargetClasses(
  mode: ExperienceMode = "patient",
  context: "default" | "form" | "dense" = "default"
): string {
  if (mode === "staff") {
    return context === "dense" ? "min-h-[32px] min-w-[32px]" : "min-h-[36px] min-w-[36px]";
  }
  if (context === "form") return "min-h-[52px] min-w-[52px]";
  if (context === "dense") return "min-h-[44px] min-w-[44px]";
  return "min-h-[48px] min-w-[48px]";
}

/* ============================================================
   Export all variants and utilities
   ============================================================ */

export const variants = {
  button: buttonVariants,
  card: cardVariants,
  input: inputVariants,
  badge: badgeVariants,
  avatar: avatarVariants,
  fab: fabVariants,
  tooltip: tooltipVariants,
  separator: separatorVariants,
} as const;
"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/design-system";

const bottomNavVariants = cva(
  "fixed bottom-0 left-0 right-0 z-50 flex border-t shadow-[0_-4px_20px_rgba(15,23,42,0.08)]",
  {
    variants: {
      variant: {
        patient: "bg-patient-surface-lowest/95 backdrop-blur-xl border-patient-outline-variant",
        staff: "bg-staff-surface/95 backdrop-blur-xl border-staff-border",
      },
      layout: {
        standard: "",
        floating: "mx-4 mb-4 rounded-2xl shadow-elevation-3",
      },
    },
    defaultVariants: {
      variant: "patient",
      layout: "standard",
    },
  }
);

const navItemVariants = cva(
  "flex flex-col items-center justify-center gap-1 transition-all duration-200 min-h-[56px] min-w-[56px]",
  {
    variants: {
      variant: {
        patient: "text-patient-on-surface-variant",
        staff: "text-staff-on-surface-variant",
      },
      active: {
        true: "",
        false: "",
      },
      density: {
        patient: "px-3 py-2",
        staff: "px-2 py-1.5",
      },
    },
    defaultVariants: {
      variant: "patient",
      active: false,
      density: "patient",
    },
  }
);

export interface NavItem {
  key: string;
  label: string;
  icon: React.ReactNode;
  activeIcon?: React.ReactNode;
  badge?: string | number;
  badgeColor?: "error" | "warning" | "success" | "info" | "ai";
  disabled?: boolean;
  href?: string;
  onClick?: () => void;
  "aria-label"?: string;
}

export interface MobileBottomNavProps
  extends Omit<React.HTMLAttributes<HTMLDivElement>, "onChange">,
    VariantProps<typeof bottomNavVariants> {
  items: NavItem[];
  activeKey: string;
  onChange: (key: string) => void;
  variant?: "patient" | "staff";
  layout?: "standard" | "floating";
  className?: string;
  safeArea?: boolean;
  primaryAction?: {
    key: string;
    label: string;
    icon: React.ReactNode;
    onClick: () => void;
    variant?: "primary" | "ai";
  };
}

const MobileBottomNav = React.forwardRef<HTMLDivElement, MobileBottomNavProps>(
  (
    {
      className,
      variant = "patient",
      layout = "standard",
      items,
      activeKey,
      onChange,
      safeArea = true,
      primaryAction,
      children,
      ...props
    },
    ref
  ) => {
    const renderItem = (item: NavItem, index: number) => {
      const isActive = item.key === activeKey;
      const isPrimary = primaryAction?.key === item.key;

      if (isPrimary && primaryAction) {
        return (
          <button
            key={item.key}
            type="button"
            onClick={primaryAction.onClick}
            disabled={item.disabled}
            className={cn(
              "relative flex flex-col items-center justify-center gap-1 min-h-[56px]",
              "bg-staff-primary text-staff-on-primary rounded-full shadow-md",
              "hover:bg-staff-primary-hover active:scale-95 transition-all",
              "focus-visible:ring-4 focus-visible:ring-staff-primary/20",
              layout === "floating" && "mx-2 my-2"
            )}
            aria-label={item["aria-label"] ?? item.label}
            aria-current={isActive ? "page" : undefined}
            aria-disabled={item.disabled}
          >
            <span className="flex items-center justify-center">{primaryAction.icon}</span>
            <span className="text-caption font-semibold">{item.label}</span>
            {(item.badge !== undefined && item.badge !== "") && (
              <span
                className={cn(
                  "absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full text-[10px] font-bold flex items-center justify-center",
                  "bg-staff-error text-staff-on-error"
                )}
              >
                {item.badge}
              </span>
            )}
          </button>
        );
      }

      const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
        if (item.disabled) {
          e.preventDefault();
          return;
        }
        if (item.href) {
          // Allow default link behavior
        } else {
          e.preventDefault();
          onChange(item.key);
        }
        item.onClick?.();
      };

      return (
        <button
          key={item.key}
          type="button"
          onClick={handleClick}
          disabled={item.disabled}
          className={cn(
            navItemVariants({ variant, active: isActive, density: variant }),
            isActive && variant === "patient" && "text-patient-primary",
            isActive && variant === "staff" && "text-staff-primary font-semibold",
            item.disabled && "opacity-50 cursor-not-allowed"
          )}
          aria-label={item["aria-label"] ?? item.label}
          aria-current={isActive ? "page" : undefined}
          aria-disabled={item.disabled}
        >
          <span className="flex items-center justify-center text-xl">
            {isActive && item.activeIcon ? item.activeIcon : item.icon}
          </span>
          <span className={cn("text-caption leading-tight", isActive && "font-semibold")}>
            {item.label}
          </span>
          {(item.badge !== undefined && item.badge !== "") && (
            <span
              className={cn(
                "absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full text-[10px] font-bold flex items-center justify-center",
                item.badgeColor === "error" && "bg-staff-error text-staff-on-error",
                item.badgeColor === "warning" && "bg-staff-warning text-staff-on-warning",
                item.badgeColor === "success" && "bg-staff-success text-staff-on-success",
                item.badgeColor === "info" && "bg-staff-info text-staff-on-info",
                item.badgeColor === "ai" && "bg-staff-ai text-staff-on-ai"
              )}
            >
              {item.badge}
            </span>
          )}
        </button>
      );
    };

    return (
      <nav
        ref={ref}
        className={cn(bottomNavVariants({ variant, layout }), className)}
        {...props}
        aria-label={variant === "patient" ? "Patient navigation" : "Staff navigation"}
      >
        {layout === "floating" && <div className="flex-1" />}

        <div className="flex-1 flex items-center justify-around">
          {items.map((item, index) => renderItem(item, index))}
        </div>

        {layout === "floating" && <div className="flex-1" />}
        {safeArea && <div className="pb-safe" />}
      </nav>
    );
  }
);
MobileBottomNav.displayName = "MobileBottomNav";

/* ============================================================
   Pre-configured Navigation Sets
   ============================================================ */

const patientNavItems: NavItem[] = [
  { key: "home", label: "Home", icon: <HomeIcon />, activeIcon: <HomeIconFilled /> },
  { key: "services", label: "Services", icon: <MedicalServicesIcon />, activeIcon: <MedicalServicesIconFilled /> },
  { key: "appointments", label: "Visits", icon: <CalendarIcon />, activeIcon: <CalendarIconFilled /> },
  { key: "profile", label: "Profile", icon: <PersonIcon />, activeIcon: <PersonIconFilled /> },
];

const staffNavItems: NavItem[] = [
  { key: "today", label: "Today", icon: <TodayIcon />, activeIcon: <TodayIconFilled /> },
  { key: "calendar", label: "Calendar", icon: <CalendarIcon />, activeIcon: <CalendarIconFilled /> },
  { key: "chats", label: "Chats", icon: <ChatIcon />, activeIcon: <ChatIconFilled /> },
  { key: "patients", label: "Patients", icon: <GroupIcon />, activeIcon: <GroupIconFilled /> },
];

/* ============================================================
   Navigation Icons (inline SVGs for zero-dep)
   ============================================================ */

function HomeIcon({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

function HomeIconFilled({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
    </svg>
  );
}

function MedicalServicesIcon({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 2v4" />
      <path d="M12 18v4" />
      <path d="M4.93 4.93l2.83 2.83" />
      <path d="M16.24 16.24l2.83 2.83" />
      <path d="M2 12h4" />
      <path d="M18 12h4" />
      <path d="M4.93 19.07l2.83-2.83" />
      <path d="M16.24 7.76l2.83-2.83" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function MedicalServicesIconFilled({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 15H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
    </svg>
  );
}

function CalendarIcon({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

function CalendarIconFilled({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20 7h-3V4c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v3H4c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2zm0 13H4V9h16v11z" />
    </svg>
  );
}

function PersonIcon({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

function PersonIconFilled({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
    </svg>
  );
}

function TodayIcon({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

function TodayIconFilled({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20 7h-3V4c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v3H4c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2zm0 13H4V9h16v11z" />
    </svg>
  );
}

function ChatIcon({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

function ChatIconFilled({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v14z" />
    </svg>
  );
}

function GroupIcon({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function GroupIconFilled({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S6.66 5 5 5C3.34 5 2 6.34 2 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5z" />
    </svg>
  );
}

export { MobileBottomNav, bottomNavVariants, navItemVariants, patientNavItems, staffNavItems };
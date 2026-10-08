"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Activity,
  CalendarDays,
  LayoutDashboard,
  Menu,
  MessageSquareText,
  Settings,
  Users,
  X,
  ChevronDown,
  Bot,
  Zap,
} from "lucide-react";

import { cn } from "@/lib/design-system";
import { useStaffSocket } from "@/hooks/useStaffSocket";
import { parseJsonResponse } from "@/lib/http";
import { useAppStore } from "@/store/useAppStore";
import { DentalFlowLogo, DentalFlowAvatar } from "@/components/branding";
import { Badge } from "@/components/ui/badge";
import { MobileBottomNav, staffNavItems } from "@/components/ui/MobileBottomNav";
import { AIIndicator } from "@/components/ai/AIIndicator";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface StaffMe {
  first_name?: string;
  last_name?: string;
  email?: string;
}

interface StaffDashboardShellProps {
  children: ReactNode;
}

const navItems: NavItem[] = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/appointments", label: "Appointments", icon: CalendarDays },
  { href: "/dashboard/live-conversations", label: "Live Conversations", icon: MessageSquareText },
  { href: "/dashboard/patients", label: "Patients", icon: Users },
  { href: "/dashboard/analytics", label: "Analytics", icon: Activity },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export default function StaffDashboardShell({ children }: StaffDashboardShellProps): JSX.Element {
  const pathname = usePathname();
  const router = useRouter();
  const clinicName = useAppStore((state) => state.clinicName);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [me, setMe] = useState<StaffMe | null>(null);
  const { isConnected } = useStaffSocket();
  const [activeNavKey, setActiveNavKey] = useState("today");

  useEffect(() => {
    const loadMe = async (): Promise<void> => {
      const response = await fetch("/api/auth/me", { cache: "no-store" });
      const payload = await parseJsonResponse<{ success: boolean; data?: StaffMe }>(response);
      if (response.ok && payload?.success && payload.data) {
        setMe(payload.data);
      }
    };
    void loadMe();
  }, []);

  const avatarText = useMemo(() => {
    if (me?.first_name || me?.last_name) {
      return `${me.first_name?.[0] ?? ""}${me.last_name?.[0] ?? ""}`.toUpperCase();
    }
    return "ST";
  }, [me?.first_name, me?.last_name]);

  const handleLogout = async (): Promise<void> => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.replace("/login");
    router.refresh();
  };

  return (
    <div className="min-h-screen bg-staff-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 border-r border-staff-border bg-staff-surface transition-transform duration-200 lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-staff-border px-4 lg:justify-start">
          <div className="flex items-center gap-2">
            <DentalFlowLogo size="default" variant="onPrimary" showText={false} />
            <span className="font-heading text-label-lg font-semibold text-staff-on-surface">
              Staff Console
            </span>
          </div>
          <button
            className="rounded-md p-1.5 text-staff-on-surface-muted hover:bg-staff-surface-variant lg:hidden"
            onClick={() => setMobileOpen(false)}
            aria-label="Close sidebar"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <nav className="space-y-1 p-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition",
                  active
                    ? "bg-staff-primary text-staff-on-primary"
                    : "text-staff-on-surface-variant hover:bg-staff-surface-variant hover:text-staff-on-surface"
                )}
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* AI Status Footer */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-staff-border p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-4 w-4 text-staff-ai" />
              <span className="text-caption font-medium text-staff-on-surface-variant">DentalFlow AI</span>
            </div>
            <AIIndicator
              variant={isConnected ? "active" : "idle"}
              size="sm"
              label={isConnected ? "Online" : "Offline"}
              animated={false}
            />
          </div>
        </div>
      </aside>

      {mobileOpen ? (
        <button
          className="fixed inset-0 z-30 bg-staff-background/20 lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-label="Close menu overlay"
        />
      ) : null}

      {/* Main Content Area */}
      <div className="lg:pl-64">
        {/* Top Header */}
        <header className="sticky top-0 z-20 border-b border-staff-border bg-staff-surface/95 backdrop-blur-sm">
          <div className="flex h-14 items-center justify-between px-4 sm:px-6">
            <div className="flex items-center gap-3">
              <button
                className="rounded-md p-1.5 text-staff-on-surface-muted hover:bg-staff-surface-variant lg:hidden"
                onClick={() => setMobileOpen(true)}
                aria-label="Open sidebar"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <p className="font-heading text-label-lg font-semibold text-staff-on-surface">{clinicName}</p>
                <p className="text-caption text-staff-on-surface-muted">
                  Staff room: <span className={isConnected ? "text-staff-success" : "text-staff-error"}>
                    {isConnected ? "Connected" : "Disconnected"}
                  </span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* AI Connection Badge - reflects the real socket state, not a fixed label */}
              <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-full bg-staff-ai-container/50 border border-staff-ai/20">
                <Bot className="h-3.5 w-3.5 text-staff-ai" />
                <span className="text-caption font-medium text-staff-on-ai-container">
                  {isConnected ? "AI Active" : "AI Offline"}
                </span>
              </div>

              {/* User Profile */}
              <div className="flex items-center gap-3">
                <div className="hidden text-right sm:block">
                  <p className="text-sm font-medium text-staff-on-surface">
                    {me?.first_name ? `${me.first_name} ${me.last_name ?? ""}`.trim() : "Staff"}
                  </p>
                  <p className="text-caption text-staff-on-surface-muted">{me?.email ?? "staff@clinic.local"}</p>
                </div>
                <DentalFlowAvatar
                  size="sm"
                  fallback={avatarText}
                  variant="primary"
                  online={isConnected}
                />
                <button
                  className="rounded-md border border-staff-border px-3 py-1.5 text-sm font-medium text-staff-on-surface transition hover:border-staff-border-focus hover:bg-staff-surface-variant"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main id="main-content" className="p-4 sm:p-6">{children}</main>

        {/* Mobile Bottom Navigation */}
        <MobileBottomNav
          items={staffNavItems}
          activeKey={activeNavKey}
          onChange={setActiveNavKey}
          variant="staff"
          layout="floating"
          safeArea={true}
        />
      </div>
    </div>
  );
}
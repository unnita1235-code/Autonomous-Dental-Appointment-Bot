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
  X
} from "lucide-react";

import { useStaffSocket } from "@/hooks/useStaffSocket";
import { parseJsonResponse } from "@/lib/http";
import { useAppStore } from "@/store/useAppStore";

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
  { href: "/dashboard/settings", label: "Settings", icon: Settings }
];

export default function StaffDashboardShell({ children }: StaffDashboardShellProps): JSX.Element {
  const pathname = usePathname();
  const router = useRouter();
  const clinicName = useAppStore((state) => state.clinicName);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [me, setMe] = useState<StaffMe | null>(null);
  const { isConnected } = useStaffSocket();

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
    <div className="min-h-screen bg-surface">
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-60 border-r border-slate-200 bg-white transition-transform duration-200 lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b border-slate-100 px-4 lg:justify-start">
          <p className="font-heading text-lg font-semibold text-primary">Staff Console</p>
          <button
            className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 lg:hidden"
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
                className={`flex items-center gap-3 rounded-r-lg border-l-4 px-3 py-2 text-sm font-medium transition ${
                  active
                    ? "border-primary bg-primary-light text-primary"
                    : "border-transparent text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      {mobileOpen ? (
        <button
          className="fixed inset-0 z-30 bg-slate-950/20 lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-label="Close menu overlay"
        />
      ) : null}

      <div className="lg:pl-60">
        <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6">
            <div className="flex items-center gap-3">
              <button
                className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 lg:hidden"
                onClick={() => setMobileOpen(true)}
                aria-label="Open sidebar"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <p className="font-heading text-base font-semibold text-slate-900">{clinicName}</p>
                <p className="text-xs text-muted">
                  Staff room: {isConnected ? "Connected" : "Disconnected"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden text-right sm:block">
                <p className="text-sm font-medium text-slate-900">
                  {me?.first_name ? `${me.first_name} ${me.last_name ?? ""}`.trim() : "Staff"}
                </p>
                <p className="text-xs text-muted">{me?.email ?? "staff@clinic.local"}</p>
              </div>
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-semibold text-white">
                {avatarText}
              </div>
              <button
                className="rounded-md border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:border-primary hover:text-primary"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        <main className="p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}

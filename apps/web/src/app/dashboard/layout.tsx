import type { ReactNode } from "react";

import StaffDashboardShell from "@/components/dashboard/StaffDashboardShell";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps): JSX.Element {
  return <StaffDashboardShell>{children}</StaffDashboardShell>;
}

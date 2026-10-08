"use client";

import type { ReactNode } from "react";
import { PatientDashboardShell } from "@/components/patient/PatientDashboardShell";

interface PatientLayoutProps {
  children: ReactNode;
}

export default function PatientLayout({ children }: PatientLayoutProps): JSX.Element {
  return <PatientDashboardShell>{children}</PatientDashboardShell>;
}
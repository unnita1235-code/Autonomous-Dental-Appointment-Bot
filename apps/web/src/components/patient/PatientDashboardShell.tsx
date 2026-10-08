"use client";

import * as React from "react";
import { cn } from "@/lib/design-system";
import { MobileBottomNav, patientNavItems } from "@/components/ui/MobileBottomNav";
import { DentalFlowLogo } from "@/components/branding";

interface PatientDashboardShellProps {
  children: React.ReactNode;
}

export function PatientDashboardShell({ children }: PatientDashboardShellProps): JSX.Element {
  const [activeNavKey, setActiveNavKey] = React.useState("home");

  return (
    <div className="min-h-screen bg-patient-surface-lowest">
      {/* Header */}
      <header className="sticky top-0 z-40 w-full border-b border-patient-outline-variant bg-patient-surface-lowest/95 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-screen-xl items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <DentalFlowLogo size="lg" variant="patient" showText={false} />
            <h1 className="font-heading text-headline-sm font-semibold text-patient-on-surface">
              DentalFlow AI
            </h1>
          </div>
          <div className="flex items-center gap-2">
            {/* Notification bell, profile, etc. can go here */}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="flex-1 pb-24">
        <div className="mx-auto max-w-screen-xl px-4 py-6">{children}</div>
      </main>

      {/* Mobile Bottom Navigation */}
      <MobileBottomNav
        items={patientNavItems}
        activeKey={activeNavKey}
        onChange={setActiveNavKey}
        variant="patient"
        layout="floating"
        safeArea={true}
      />
    </div>
  );
}
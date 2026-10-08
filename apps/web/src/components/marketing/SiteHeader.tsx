"use client";

import * as React from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";

import { cn } from "@/lib/design-system";
import { DentalFlowLogo } from "@/components/branding";
import { Button } from "@/components/ui/button";
import { OpenChatButton } from "@/components/chat/OpenChatButton";

interface SiteHeaderProps {
  /** Only passed on the home page so in-page anchors work from the header. */
  withSectionLinks?: boolean;
}

const NAV_LINKS = [
  { href: "#how-it-works", label: "How it works", section: true },
  { href: "#ai-assistant", label: "AI assistant", section: true },
  { href: "/patient", label: "Patient portal", section: false },
  { href: "/login", label: "Staff sign in", section: false },
] as const;

export function SiteHeader({ withSectionLinks = false }: SiteHeaderProps): JSX.Element {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const visibleLinks = NAV_LINKS.filter((link) => (withSectionLinks ? true : !link.section));

  return (
    <header className="sticky top-0 z-40 w-full border-b border-patient-outline-variant bg-patient-surface-lowest/95 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-screen-xl items-center justify-between gap-4 px-4 pr-safe">
        <Link
          href="/"
          className="rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-patient-primary focus-visible:ring-offset-2"
        >
          <DentalFlowLogo size="default" variant="patient" showText />
        </Link>

        {/* Desktop navigation */}
        <nav aria-label="Main" className="hidden items-center gap-1 lg:flex">
          {visibleLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "rounded-full px-4 py-2 text-label-md font-semibold transition-colors",
                "text-patient-on-surface-variant hover:bg-patient-surface hover:text-patient-on-surface",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-patient-primary focus-visible:ring-offset-2"
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <OpenChatButton className="hidden sm:inline-flex" size="sm" variant="primary">
            Book an appointment
          </OpenChatButton>

          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setMobileOpen((open) => !open)}
            aria-expanded={mobileOpen}
            aria-controls="mobile-site-nav"
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile navigation */}
      {mobileOpen ? (
        <nav
          id="mobile-site-nav"
          aria-label="Mobile"
          className="border-t border-patient-outline-variant bg-patient-surface-lowest lg:hidden"
        >
          <ul className="mx-auto flex max-w-screen-xl flex-col gap-1 px-4 py-3">
            {visibleLinks.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={cn(
                    "flex min-h-[48px] items-center rounded-xl px-4 py-3 text-label-md font-semibold",
                    "text-patient-on-surface-variant transition-colors hover:bg-patient-surface hover:text-patient-on-surface",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-patient-primary"
                  )}
                >
                  {link.label}
                </Link>
              </li>
            ))}
            <li className="pt-1 sm:hidden">
              <OpenChatButton fullWidth onOpened={() => setMobileOpen(false)}>
                Book an appointment
              </OpenChatButton>
            </li>
          </ul>
        </nav>
      ) : null}
    </header>
  );
}

export default SiteHeader;
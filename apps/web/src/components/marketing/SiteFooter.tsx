import Link from "next/link";

import { DentalFlowLogo } from "@/components/branding";

/**
 * Site footer.
 *
 * Renders only navigation targets that exist in this application and a single
 * real value (`clinicName` from the app store default). Clinic address, phone,
 * opening hours, insurance partners and certifications are intentionally NOT
 * rendered because the application exposes no public endpoint that provides
 * them. Fabricating those details is out of scope for this design layer.
 */
export function SiteFooter(): JSX.Element {
  return (
    <footer className="border-t border-patient-outline-variant bg-patient-surface">
      <div className="mx-auto max-w-screen-xl px-4 py-10 pb-safe">
        <div className="grid gap-8 md:grid-cols-4">
          <div className="space-y-3 md:col-span-2">
            <DentalFlowLogo size="default" variant="patient" showText />
            <p className="max-w-sm text-body-md text-patient-on-surface-variant">
              Dental care scheduling and patient communication. Our AI assistant can help you book,
              reschedule, or answer questions about your upcoming visits.
            </p>
          </div>

          <nav aria-label="Patient">
            <h2 className="text-label-md font-semibold text-patient-on-surface">Patients</h2>
            <ul className="mt-3 space-y-1">
              <li>
                <FooterLink href="/patient">Patient portal</FooterLink>
              </li>
              <li>
                <FooterLink href="/booking/confirmed">Appointment confirmation</FooterLink>
              </li>
            </ul>
          </nav>

          <nav aria-label="Clinic staff">
            <h2 className="text-label-md font-semibold text-patient-on-surface">Clinic staff</h2>
            <ul className="mt-3 space-y-1">
              <li>
                <FooterLink href="/dashboard">Staff dashboard</FooterLink>
              </li>
              <li>
                <FooterLink href="/login">Staff sign in</FooterLink>
              </li>
            </ul>
          </nav>
        </div>

        <div className="mt-8 border-t border-patient-outline-variant pt-6">
          <p className="text-caption text-patient-on-surface-variant">
            DentalFlow AI is a scheduling and communication tool. It does not provide medical advice
            or diagnosis. If you are experiencing a dental emergency, contact your local emergency
            services.
          </p>
        </div>
      </div>
    </footer>
  );
}

function FooterLink({ href, children }: { href: string; children: React.ReactNode }): JSX.Element {
  return (
    <Link
      href={href}
      className="inline-flex min-h-[44px] items-center rounded-lg text-body-md text-patient-on-surface-variant transition-colors hover:text-patient-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-patient-primary"
    >
      {children}
    </Link>
  );
}

export default SiteFooter;
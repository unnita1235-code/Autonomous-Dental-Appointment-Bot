import Link from "next/link";
import type { Metadata } from "next";
import {
  CalendarCheck,
  MessageCircle,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  Smartphone,
} from "lucide-react";

import { cn } from "@/lib/design-system";
import { SiteHeader } from "@/components/marketing/SiteHeader";
import { SiteFooter } from "@/components/marketing/SiteFooter";
import { OpenChatButton } from "@/components/chat/OpenChatButton";
import ChatWidget from "@/components/chat/ChatWidget";
import { AIIndicator } from "@/components/ai/AIIndicator";
import { Button } from "@/components/ui/button";

export const metadata: Metadata = {
  title: "DentalFlow AI | Dental Appointment Booking",
  description:
    "Book, reschedule and manage dental appointments with the DentalFlow AI assistant, or review your visits in the patient portal.",
};

const HOW_IT_WORKS = [
  {
    step: "1",
    title: "Tell the assistant what you need",
    description:
      "Open the assistant and describe the visit you want. You can book, ask to reschedule, or ask a question in plain language.",
    footer: "Web, SMS, WhatsApp and voice channels",
    icon: MessageCircle,
    tone: "primary" as const,
  },
  {
    step: "2",
    title: "Pick from real availability",
    description:
      "The assistant checks live appointment availability and offers times that are actually open, with the provider and service details.",
    footer: "Checked against live slot availability",
    icon: CalendarCheck,
    tone: "primary" as const,
  },
  {
    step: "3",
    title: "Get a confirmation you can keep",
    description:
      "Once your booking is confirmed you receive a reference, and you can add the appointment to your own calendar.",
    footer: "Add to calendar from the confirmation",
    icon: CheckCircle2,
    tone: "secondary" as const,
  },
];

const CAPABILITIES = [
  "Check which appointments are available",
  "Book a new appointment",
  "Request a reschedule",
  "Ask about clinic services and pricing",
  "Reach a staff member when you need one",
] as const;

const TONE_ICON_CLASSES = {
  primary: "bg-patient-primary-fixed text-patient-primary",
  secondary: "bg-patient-secondary-fixed text-patient-secondary",
} as const;

export default function HomePage(): JSX.Element {
  return (
    <div className="min-h-screen bg-patient-background patient-mode">
      <SiteHeader withSectionLinks />

      <main id="main-content" className="pb-safe">
        {/* ============================================================
            HERO
            ============================================================ */}
        <section className="relative overflow-hidden" aria-labelledby="hero-heading">
          {/* Ambient decorative glow (aria-hidden, purely presentational) */}
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -top-32 left-1/2 h-[360px] w-[720px] -translate-x-1/2 rounded-full bg-patient-secondary-container/25 blur-3xl"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute right-10 top-48 h-96 w-96 rounded-full bg-patient-primary-fixed/20 blur-3xl"
          />

          <div className="relative mx-auto max-w-screen-xl px-4 py-12 lg:py-20">
            <div className="grid items-center gap-12 lg:grid-cols-2">
              {/* Left: hero copy */}
              <div className="flex flex-col justify-center gap-6">
                <p className="inline-flex w-fit items-center gap-2 rounded-full bg-patient-primary-fixed/50 px-4 py-1.5">
                  <AIIndicator variant="recommendation" size="sm" label="AI-assisted booking" animated={false} />
                </p>

                <h1
                  id="hero-heading"
                  className="text-balance font-heading text-headline-xl-mobile font-bold tracking-tight text-patient-on-surface md:text-headline-xl"
                >
                  Book and manage your dental appointments.
                </h1>

                <p className="max-w-xl text-body-lg text-patient-on-surface-variant">
                  Check availability, choose a time, and get a confirmation you can keep. You can
                  also review and manage your visits any time from your patient portal.
                </p>

                {/* Primary + secondary CTAs */}
                <div className="flex flex-col items-stretch gap-4 sm:flex-row sm:items-center">
                  <OpenChatButton size="lg">
                    Book an appointment
                    <ArrowRight className="ml-2 h-5 w-5" aria-hidden="true" />
                  </OpenChatButton>

                  <Button asChild variant="secondary" size="lg">
                    <Link href="/patient">
                      Go to patient portal
                      <ArrowRight className="ml-2 h-5 w-5" aria-hidden="true" />
                    </Link>
                  </Button>
                </div>

                {/* Factual capability statements (no fabricated guarantees) */}
                <ul className="flex flex-wrap gap-x-6 gap-y-2">
                  {["Live availability", "AI-assisted booking", "Staff handoff when needed"].map(
                    (item) => (
                      <li
                        key={item}
                        className="flex items-center gap-2 text-caption text-patient-on-surface-variant"
                      >
                        <CheckCircle2
                          className="h-4 w-4 shrink-0 text-patient-secondary"
                          aria-hidden="true"
                        />
                        {item}
                      </li>
                    )
                  )}
                </ul>
              </div>

              {/* Right: assistant preview (presentational, no invented data) */}
              <div className="flex justify-center">
                <div className="relative w-full max-w-md overflow-hidden rounded-2xl bg-patient-surface-low shadow-elevation-2">
                  <div className="flex items-center gap-3 border-b border-patient-outline-variant bg-gradient-to-r from-patient-primary to-patient-primary-container px-4 py-3.5 text-patient-on-primary">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white/20">
                      <AIIndicator variant="active" size="sm" label="" animated={false} />
                    </div>
                    <div>
                      <p className="font-heading text-label-md font-semibold">DentalFlow AI</p>
                      <p className="text-caption text-patient-on-primary/80">Booking assistant</p>
                    </div>
                  </div>

                  <div className="space-y-3 p-4">
                    <div className="max-w-[92%] rounded-2xl rounded-tl-sm bg-patient-surface-low p-3.5 text-body-md text-patient-on-surface">
                      Hi! I can help you book or change a dental appointment. What would you like to
                      do?
                    </div>

                    <ul className="flex flex-wrap gap-1.5">
                      {["Book an appointment", "Reschedule", "Clinic hours", "Ask a question"].map(
                        (label) => (
                          <li key={label}>
                            <span className="inline-flex min-h-[36px] items-center rounded-full bg-patient-surface-lowest px-3 py-1.5 text-caption font-semibold text-patient-primary shadow-sm">
                              {label}
                            </span>
                          </li>
                        )
                      )}
                    </ul>

                    <div className="flex items-center gap-2 rounded-full bg-patient-surface-low px-3 py-2 text-caption text-patient-on-surface-variant">
                      <AIIndicator variant="processing" size="sm" label="" animated />
                      Checking availability
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ============================================================
            HOW IT WORKS
            ============================================================ */}
        <section id="how-it-works" className="scroll-mt-20 py-12 lg:py-20" aria-labelledby="how-heading">
          <div className="mx-auto max-w-screen-xl px-4">
            <div className="mx-auto mb-12 max-w-2xl text-center">
              <p className="text-label-sm font-bold uppercase tracking-wider text-patient-primary">
                Straightforward
              </p>
              <h2
                id="how-heading"
                className="mt-1 font-heading text-headline-lg-mobile font-bold text-patient-on-surface md:text-headline-lg"
              >
                How it works
              </h2>
              <p className="mt-2 text-body-lg text-patient-on-surface-variant">
                Three steps, all handled by the existing booking flow.
              </p>
            </div>

            <ol className="grid gap-6 md:grid-cols-3">
              {HOW_IT_WORKS.map((item) => {
                const Icon = item.icon;
                return (
                  <li
                    key={item.step}
                    className="flex flex-col justify-between rounded-2xl bg-patient-surface-lowest p-6 shadow-elevation-1 transition-transform duration-200 hover:-translate-y-1 md:p-8"
                  >
                    <div>
                      <div className="mb-4 flex items-center gap-3">
                        <div
                          className={cn(
                            "flex h-12 w-12 items-center justify-center rounded-full shadow-sm",
                            TONE_ICON_CLASSES[item.tone]
                          )}
                          aria-hidden="true"
                        >
                          <Icon className="h-6 w-6" />
                        </div>
                        <span className="font-heading text-headline-sm font-bold text-patient-on-surface-variant">
                          {item.step}
                        </span>
                      </div>
                      <h3 className="mb-2 font-heading text-headline-sm font-bold text-patient-on-surface">
                        {item.title}
                      </h3>
                      <p className="text-body-md text-patient-on-surface-variant">
                        {item.description}
                      </p>
                    </div>
                    <p className="mt-6 flex items-center gap-2 pt-4 text-label-md text-patient-primary">
                      <Icon className="h-5 w-5" aria-hidden="true" />
                      {item.footer}
                    </p>
                  </li>
                );
              })}
            </ol>
          </div>
        </section>

        {/* ============================================================
            AI ASSISTANT
            ============================================================ */}
        <section id="ai-assistant" className="scroll-mt-20 py-12 lg:py-20" aria-labelledby="assistant-heading">
          <div className="mx-auto max-w-screen-xl px-4">
            <div className="overflow-hidden rounded-3xl border border-staff-ai/30 bg-staff-ai-container/10 shadow-ai-glow">
              <div className="grid gap-8 p-6 md:p-10 lg:grid-cols-2 lg:items-center">
                <div className="space-y-4">
                  <p className="inline-flex items-center gap-2 rounded-full bg-patient-surface-lowest px-3 py-1.5">
                    <AIIndicator variant="recommendation" size="sm" label="DentalFlow AI" animated={false} />
                  </p>
                  <h2
                    id="assistant-heading"
                    className="text-balance font-heading text-headline-lg-mobile font-bold text-staff-on-surface md:text-headline-lg"
                  >
                    A real assistant, not a form
                  </h2>
                  <p className="text-body-lg text-staff-on-surface-variant">
                    The assistant handles scheduling questions through the same booking flow used by
                    clinic staff. If a request needs a person, it hands the conversation off instead of
                    guessing.
                  </p>

                  <ul className="space-y-2">
                    {CAPABILITIES.map((item) => (
                      <li key={item} className="flex items-start gap-2">
                        <CheckCircle2
                          className="mt-0.5 h-5 w-5 shrink-0 text-patient-secondary"
                          aria-hidden="true"
                        />
                        <span className="text-body-md text-staff-on-surface">{item}</span>
                      </li>
                    ))}
                  </ul>

                  <div className="flex flex-col gap-3 pt-2 sm:flex-row">
                    <OpenChatButton variant="ai" size="lg">
                      Open the assistant
                      <ArrowRight className="ml-2 h-5 w-5" aria-hidden="true" />
                    </OpenChatButton>
                    <Button asChild variant="outline" size="lg">
                      <Link href="/dashboard">Staff console</Link>
                    </Button>
                  </div>
                </div>

                {/* Assistant capability panel */}
                <div className="rounded-2xl bg-patient-surface-lowest p-6 shadow-elevation-1">
                  <h3 className="font-heading text-label-lg font-semibold text-patient-on-surface">
                    What happens in the background
                  </h3>
                  <dl className="mt-4 space-y-3 text-body-md">
                    <div className="flex items-start gap-3">
                      <CalendarCheck
                        className="mt-0.5 h-5 w-5 shrink-0 text-patient-primary"
                        aria-hidden="true"
                      />
                      <div>
                        <dt className="font-semibold text-patient-on-surface">Live slot lookup</dt>
                        <dd className="text-patient-on-surface-variant">
                          Availability is read from the scheduling service at the time you ask.
                        </dd>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <Smartphone
                        className="mt-0.5 h-5 w-5 shrink-0 text-patient-primary"
                        aria-hidden="true"
                      />
                      <div>
                        <dt className="font-semibold text-patient-on-surface">Multi-channel</dt>
                        <dd className="text-patient-on-surface-variant">
                          Conversations can continue over web, SMS, WhatsApp or voice.
                        </dd>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <ShieldCheck
                        className="mt-0.5 h-5 w-5 shrink-0 text-patient-primary"
                        aria-hidden="true"
                      />
                      <div>
                        <dt className="font-semibold text-patient-on-surface">Human handoff</dt>
                        <dd className="text-patient-on-surface-variant">
                          Requests that need clinical judgement are escalated to clinic staff.
                        </dd>
                      </div>
                    </div>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />

      {/* Existing chat widget — the single chat entry point for the whole app */}
      <ChatWidget />
    </div>
  );
}
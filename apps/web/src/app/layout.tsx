import type { ReactNode } from "react";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "DentalFlow AI",
    template: "%s | DentalFlow AI",
  },
  description:
    "DentalFlow AI helps patients book, reschedule and manage dental appointments.",
  applicationName: "DentalFlow AI",
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps): JSX.Element {
  return (
    <html lang="en">
      <body className="font-body antialiased">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-patient-primary focus:px-4 focus:py-3 focus:text-patient-on-primary"
        >
          Skip to main content
        </a>
        {children}
      </body>
    </html>
  );
}

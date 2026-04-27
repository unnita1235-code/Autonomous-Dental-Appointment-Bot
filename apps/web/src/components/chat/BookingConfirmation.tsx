"use client";

import { CalendarPlus2, CircleCheckBig } from "lucide-react";
import type { BookingConfirmationPayload } from "./ChatStore";

interface BookingConfirmationProps {
  booking: BookingConfirmationPayload;
}

const createCalendarLink = (booking: BookingConfirmationPayload): string => {
  const startDate = new Date(booking.appointment_time);
  const endDate = new Date(startDate.getTime() + 30 * 60 * 1000);
  const formatDate = (date: Date): string => date.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";

  const params = new URLSearchParams({
    action: "TEMPLATE",
    text: `Dental Appointment - ${booking.service_name}`,
    dates: `${formatDate(startDate)}/${formatDate(endDate)}`,
    details: `Appointment ID: ${booking.appointment_id}\nDentist: ${booking.dentist_name}\nPatient: ${booking.patient_name}`
  });

  return `https://calendar.google.com/calendar/render?${params.toString()}`;
};

export default function BookingConfirmation({ booking }: BookingConfirmationProps): JSX.Element {
  return (
    <div className="mt-2 rounded-xl border border-green-200 bg-green-50 p-3">
      <div className="flex items-center gap-2 text-green-700">
        <CircleCheckBig className="h-4 w-4" />
        <p className="text-sm font-semibold">Booking Confirmed</p>
      </div>
      <div className="mt-2 space-y-1 text-xs text-slate-700">
        <p>
          <span className="font-medium">Appointment ID:</span> {booking.appointment_id}
        </p>
        <p>
          <span className="font-medium">Patient:</span> {booking.patient_name}
        </p>
        <p>
          <span className="font-medium">Dentist:</span> {booking.dentist_name}
        </p>
        <p>
          <span className="font-medium">Service:</span> {booking.service_name}
        </p>
      </div>
      <a
        href={createCalendarLink(booking)}
        target="_blank"
        rel="noreferrer"
        className="mt-3 inline-flex h-8 items-center gap-1 rounded-md bg-white px-3 text-xs font-semibold text-green-700 shadow-sm ring-1 ring-green-200 transition hover:bg-green-100"
      >
        <CalendarPlus2 className="h-3.5 w-3.5" />
        Add to calendar
      </a>
    </div>
  );
}

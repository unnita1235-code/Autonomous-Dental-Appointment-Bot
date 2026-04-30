"use client";

import { useEffect, useMemo, useState } from "react";
import { format } from "date-fns";
import {
  CalendarDays,
  ChevronDown,
  ChevronUp,
  MessageCircle,
  Phone,
  Smartphone,
  UserRound,
  XCircle
} from "lucide-react";

import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { parseJsonResponse } from "@/lib/http";
import type { Appointment, Patient } from "@/types";

type SortKey = "start_time" | "status" | "service";
type SortOrder = "asc" | "desc";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  meta?: Record<string, unknown> | null;
  error?: string | null;
}

const PAGE_SIZE = 25;

const statusColors: Record<string, string> = {
  CONFIRMED: "bg-success/10 text-success",
  PENDING: "bg-warning/10 text-warning",
  CANCELLED: "bg-error/10 text-error",
  COMPLETED: "bg-primary-light text-primary",
  NO_SHOW: "bg-slate-200 text-slate-700"
};

const channelIcon = (channel: string): JSX.Element => {
  const normalized = channel.toLowerCase();
  if (normalized.includes("whatsapp")) {
    return <MessageCircle className="h-4 w-4 text-accent" />;
  }
  if (normalized.includes("sms")) {
    return <Smartphone className="h-4 w-4 text-primary" />;
  }
  if (normalized.includes("voice") || normalized.includes("phone")) {
    return <Phone className="h-4 w-4 text-slate-600" />;
  }
  return <CalendarDays className="h-4 w-4 text-slate-500" />;
};

const fetchPatientName = async (patientId: string): Promise<string> => {
  const response = await fetch(`/staff-api/patients/${patientId}`, { cache: "no-store" });
  const payload = await parseJsonResponse<ApiEnvelope<Patient>>(response);
  if (!response.ok || !payload?.success || !payload.data) {
    return `Patient ${patientId.slice(0, 8)}`;
  }
  return `${payload.data.first_name} ${payload.data.last_name}`;
};

export default function AppointmentsPage(): JSX.Element {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [patientNames, setPatientNames] = useState<Record<string, string>>({});
  const [selected, setSelected] = useState<Appointment | null>(null);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [status, setStatus] = useState("");
  const [dentistId, setDentistId] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("start_time");
  const [sortOrder, setSortOrder] = useState<SortOrder>("asc");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const loadAppointments = async (): Promise<void> => {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("per_page", String(PAGE_SIZE));
      if (dateFrom) params.set("date_from", dateFrom);
      if (dateTo) params.set("date_to", dateTo);
      if (status) params.set("status", status);
      if (dentistId) params.set("dentist_id", dentistId);

      const response = await fetch(`/staff-api/appointments?${params.toString()}`, {
        cache: "no-store"
      });
      const payload = await parseJsonResponse<ApiEnvelope<Appointment[]>>(response);
      if (!response.ok || !payload?.success || !payload.data) {
        return;
      }
      setAppointments(payload.data);
      setTotal(Number(payload.meta?.total ?? 0));

      const ids = [...new Set(payload.data.map((item) => item.patient_id))];
      const names = await Promise.all(ids.map(async (id) => [id, await fetchPatientName(id)] as const));
      setPatientNames((current) => ({ ...current, ...Object.fromEntries(names) }));
    };
    void loadAppointments();
  }, [dateFrom, dateTo, status, dentistId, page]);

  const dentists = useMemo(() => {
    const byId = new Map<string, string>();
    appointments.forEach((item) => {
      const name = `Dr. ${item.dentist.first_name} ${item.dentist.last_name}`;
      byId.set(item.dentist_id, name);
    });
    return [...byId.entries()];
  }, [appointments]);

  const sortedAppointments = useMemo(() => {
    const sorted = [...appointments].sort((a, b) => {
      if (sortKey === "start_time") {
        return new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
      }
      if (sortKey === "status") {
        return a.status.localeCompare(b.status);
      }
      return a.service.name.localeCompare(b.service.name);
    });
    return sortOrder === "asc" ? sorted : sorted.reverse();
  }, [appointments, sortKey, sortOrder]);

  const toggleSort = (key: SortKey): void => {
    if (key === sortKey) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
      return;
    }
    setSortKey(key);
    setSortOrder("asc");
  };

  const updateStatus = async (appointmentId: string, nextStatus: "CANCELLED" | "CONFIRMED"): Promise<void> => {
    const response = await fetch(`/staff-api/appointments/${appointmentId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: nextStatus,
        cancellation_reason: nextStatus === "CANCELLED" ? "Cancelled by staff dashboard" : null
      })
    });
    if (!response.ok) {
      return;
    }
    setAppointments((items) =>
      items.map((item) => (item.id === appointmentId ? { ...item, status: nextStatus } : item))
    );
    if (selected?.id === appointmentId) {
      setSelected((current) => (current ? { ...current, status: nextStatus } : current));
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-heading text-2xl font-semibold text-slate-900">Appointments</h1>
      </header>

      <section className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-5">
        <label className="text-sm">
          <span className="mb-1 block text-xs font-medium text-muted">Date from</span>
          <input
            type="date"
            value={dateFrom}
            onChange={(event) => setDateFrom(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-xs font-medium text-muted">Date to</span>
          <input
            type="date"
            value={dateTo}
            onChange={(event) => setDateTo(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-xs font-medium text-muted">Status</span>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
          >
            <option value="">All</option>
            <option value="PENDING">Pending</option>
            <option value="CONFIRMED">Confirmed</option>
            <option value="CANCELLED">Cancelled</option>
            <option value="COMPLETED">Completed</option>
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-xs font-medium text-muted">Dentist</span>
          <select
            value={dentistId}
            onChange={(event) => setDentistId(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
          >
            <option value="">All</option>
            {dentists.map(([id, name]) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <div className="flex items-end">
          <button
            className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 hover:border-error hover:text-error"
            onClick={() => {
              setDateFrom("");
              setDateTo("");
              setStatus("");
              setDentistId("");
              setPage(1);
            }}
          >
            <XCircle className="h-4 w-4" />
            Clear filters
          </button>
        </div>
      </section>

      <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted">Patient</th>
              <th
                className="cursor-pointer px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted"
                onClick={() => toggleSort("service")}
              >
                <span className="inline-flex items-center gap-1">
                  Service {sortKey === "service" ? sortOrder === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" /> : null}
                </span>
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted">Dentist</th>
              <th
                className="cursor-pointer px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted"
                onClick={() => toggleSort("start_time")}
              >
                <span className="inline-flex items-center gap-1">
                  Date/Time {sortKey === "start_time" ? sortOrder === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" /> : null}
                </span>
              </th>
              <th
                className="cursor-pointer px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted"
                onClick={() => toggleSort("status")}
              >
                <span className="inline-flex items-center gap-1">
                  Status {sortKey === "status" ? sortOrder === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" /> : null}
                </span>
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted">Source</th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-muted">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sortedAppointments.map((item) => (
              <tr
                key={item.id}
                className="cursor-pointer transition hover:bg-primary-light/50"
                onClick={() => setSelected(item)}
              >
                <td className="px-4 py-3 text-sm text-slate-900">
                  {patientNames[item.patient_id] ?? `Patient ${item.patient_id.slice(0, 8)}`}
                </td>
                <td className="px-4 py-3 text-sm text-slate-700">{item.service.name}</td>
                <td className="px-4 py-3 text-sm text-slate-700">
                  Dr. {item.dentist.first_name} {item.dentist.last_name}
                </td>
                <td className="px-4 py-3 text-sm text-slate-700">{format(new Date(item.start_time), "MMM d, yyyy h:mm a")}</td>
                <td className="px-4 py-3 text-sm">
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${statusColors[item.status] ?? "bg-slate-100 text-slate-700"}`}>
                    {item.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-slate-700">
                  <span className="inline-flex items-center gap-2">
                    {channelIcon(item.source_channel)}
                    {item.source_channel}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-sm">
                  <div className="inline-flex items-center gap-2">
                    <button
                      className="rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-700 hover:border-primary hover:text-primary"
                      onClick={(event) => {
                        event.stopPropagation();
                        setSelected(item);
                      }}
                    >
                      View
                    </button>
                    <button
                      className="rounded-md border border-error/40 px-2.5 py-1 text-xs font-medium text-error hover:bg-error/5"
                      onClick={(event) => {
                        event.stopPropagation();
                        void updateStatus(item.id, "CANCELLED");
                      }}
                    >
                      Cancel
                    </button>
                    <button
                      className="rounded-md border border-primary/40 px-2.5 py-1 text-xs font-medium text-primary hover:bg-primary-light"
                      onClick={(event) => {
                        event.stopPropagation();
                        void updateStatus(item.id, "CONFIRMED");
                      }}
                    >
                      Reschedule
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <footer className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3">
        <p className="text-sm text-muted">
          Page {page} of {totalPages} • {total} total
        </p>
        <div className="flex items-center gap-2">
          <button
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50"
            disabled={page <= 1}
            onClick={() => setPage((value) => Math.max(1, value - 1))}
          >
            Previous
          </button>
          <button
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50"
            disabled={page >= totalPages}
            onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
          >
            Next
          </button>
        </div>
      </footer>

      <Sheet open={Boolean(selected)} onOpenChange={(open) => (open ? null : setSelected(null))}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Appointment details</SheetTitle>
            <SheetDescription>
              Full appointment context with direct actions for staff operations.
            </SheetDescription>
          </SheetHeader>
          {selected ? (
            <div className="mt-6 space-y-4">
              <div className="rounded-lg border border-slate-200 p-3">
                <p className="text-xs font-medium uppercase tracking-wide text-muted">Patient</p>
                <p className="mt-1 text-sm text-slate-900">
                  {patientNames[selected.patient_id] ?? selected.patient_id}
                </p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <p className="text-xs font-medium uppercase tracking-wide text-muted">Service & Dentist</p>
                <p className="mt-1 text-sm text-slate-900">
                  {selected.service.name} • Dr. {selected.dentist.first_name} {selected.dentist.last_name}
                </p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <p className="text-xs font-medium uppercase tracking-wide text-muted">Date and time</p>
                <p className="mt-1 text-sm text-slate-900">
                  {format(new Date(selected.start_time), "EEEE, MMM d, yyyy 'at' h:mm a")}
                </p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <p className="text-xs font-medium uppercase tracking-wide text-muted">Status and source</p>
                <p className="mt-1 inline-flex items-center gap-2 text-sm text-slate-900">
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${statusColors[selected.status] ?? "bg-slate-100 text-slate-700"}`}>
                    {selected.status}
                  </span>
                  {channelIcon(selected.source_channel)}
                  {selected.source_channel}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  className="rounded-md border border-primary/40 px-3 py-2 text-sm font-medium text-primary hover:bg-primary-light"
                  onClick={() => void updateStatus(selected.id, "CONFIRMED")}
                >
                  Confirm
                </button>
                <button
                  className="rounded-md border border-error/40 px-3 py-2 text-sm font-medium text-error hover:bg-error/5"
                  onClick={() => void updateStatus(selected.id, "CANCELLED")}
                >
                  Cancel appointment
                </button>
                <button
                  className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:border-primary hover:text-primary"
                  onClick={() => void updateStatus(selected.id, "CONFIRMED")}
                >
                  Reschedule flow
                </button>
              </div>
            </div>
          ) : null}
        </SheetContent>
      </Sheet>
    </div>
  );
}

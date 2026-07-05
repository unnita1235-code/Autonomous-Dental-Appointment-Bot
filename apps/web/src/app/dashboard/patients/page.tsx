"use client";

import { useEffect, useMemo, useState } from "react";
import { format } from "date-fns";
import { Search, Ban, ChevronDown, ChevronUp } from "lucide-react";

import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { parseJsonResponse } from "@/lib/http";
import type { Appointment, ChannelPreference, Patient } from "@/types";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  meta?: Record<string, unknown> | null;
}

type SortKey = "first_name" | "last_name" | "created_at";
type SortOrder = "asc" | "desc";

const PAGE_SIZE = 25;

const statusColors: Record<string, string> = {
  CONFIRMED: "bg-success/10 text-success",
  PENDING: "bg-warning/10 text-warning",
  CANCELLED: "bg-error/10 text-error",
  COMPLETED: "bg-primary-light text-primary",
  NO_SHOW: "bg-slate-200 text-slate-700",
};

export default function PatientsPage(): JSX.Element {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [sortKey, setSortKey] = useState<SortKey>("created_at");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [selected, setSelected] = useState<Patient | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<Patient>>({});

  const loadPatients = async (): Promise<void> => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("per_page", String(PAGE_SIZE));
    if (search.trim()) params.set("q", search.trim());

    const response = await fetch(`/staff-api/patients?${params.toString()}`, { cache: "no-store" });
    const payload = await parseJsonResponse<ApiEnvelope<Patient[]>>(response);
    if (!response.ok || !payload?.success || !payload.data) return;
    setPatients(payload.data);
    setTotal(Number(payload.meta?.total ?? 0));
  };

  useEffect(() => {
    void loadPatients();
  }, [page, search]);

  const loadAppointments = async (patientId: string): Promise<void> => {
    const params = new URLSearchParams();
    params.set("patient_id", patientId);
    params.set("per_page", "20");
    const response = await fetch(`/staff-api/appointments?${params.toString()}`, { cache: "no-store" });
    const payload = await parseJsonResponse<ApiEnvelope<Appointment[]>>(response);
    if (payload?.success && payload.data) {
      setAppointments(payload.data);
    }
  };

  const openDetail = async (patient: Patient): Promise<void> => {
    setSelected(patient);
    setEditForm({});
    setEditing(false);
    setAppointments([]);
    await loadAppointments(patient.id);
  };

  const updatePatient = async (): Promise<void> => {
    if (!selected) return;
    const response = await fetch(`/staff-api/patients/${selected.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(editForm),
    });
    const payload = await parseJsonResponse<ApiEnvelope<Patient>>(response);
    if (response.ok && payload?.success && payload.data) {
      setSelected(payload.data);
      setPatients((items) => items.map((item) => (item.id === payload.data!.id ? payload.data! : item)));
    }
    setEditing(false);
  };

  const sortedPatients = useMemo(() => {
    const sorted = [...patients].sort((a, b) => {
      const aVal = String(a[sortKey as keyof Patient] ?? "");
      const bVal = String(b[sortKey as keyof Patient] ?? "");
      return sortOrder === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });
    return sorted;
  }, [patients, sortKey, sortOrder]);

  const toggleSort = (key: SortKey): void => {
    if (key === sortKey) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
      return;
    }
    setSortKey(key);
    setSortOrder("asc");
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-heading text-2xl font-semibold text-slate-900">Patients</h1>
      </header>

      <section className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3">
        <Search className="h-4 w-4 text-muted" />
        <input
          type="text"
          placeholder="Search by name, email, or phone..."
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            setPage(1);
          }}
          className="w-full border-none text-sm outline-none placeholder:text-muted"
        />
      </section>

      <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th
                className="cursor-pointer px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted"
                onClick={() => toggleSort("first_name")}
              >
                <span className="inline-flex items-center gap-1">
                  Name {sortKey === "first_name" ? sortOrder === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" /> : null}
                </span>
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted">Contact</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted">Preference</th>
              <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wide text-muted">No-shows</th>
              <th
                className="cursor-pointer px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted"
                onClick={() => toggleSort("created_at")}
              >
                <span className="inline-flex items-center gap-1">
                  Created {sortKey === "created_at" ? sortOrder === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" /> : null}
                </span>
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-muted">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sortedPatients.map((patient) => (
              <tr
                key={patient.id}
                className="cursor-pointer transition hover:bg-primary-light/50"
                onClick={() => void openDetail(patient)}
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-light text-xs font-semibold text-primary">
                      {patient.first_name[0]}{patient.last_name[0]}
                    </div>
                    <span className="text-sm font-medium text-slate-900">
                      {patient.first_name} {patient.last_name}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-slate-700">
                  <div>{patient.email}</div>
                  <div className="text-xs text-muted">{patient.phone}</div>
                </td>
                <td className="px-4 py-3 text-sm text-slate-700 capitalize">{patient.channel_preference}</td>
                <td className="px-4 py-3 text-center">
                  {patient.no_show_count > 0 ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-error/10 px-2 py-0.5 text-xs font-medium text-error">
                      <Ban className="h-3 w-3" />
                      {patient.no_show_count}
                    </span>
                  ) : (
                    <span className="text-xs text-muted">0</span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-slate-700">{format(new Date(patient.created_at), "MMM d, yyyy")}</td>
                <td className="px-4 py-3 text-right">
                  <button
                    className="rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-700 hover:border-primary hover:text-primary"
                    onClick={(event) => {
                      event.stopPropagation();
                      void openDetail(patient);
                    }}
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <footer className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3">
        <p className="text-sm text-muted">Page {page} of {totalPages} &bull; {total} total</p>
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
        <SheetContent className="overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Patient details</SheetTitle>
            <SheetDescription>View and manage patient information.</SheetDescription>
          </SheetHeader>
          {selected ? (
            <div className="mt-6 space-y-4">
              <div className="flex items-center gap-3 rounded-lg border border-slate-200 p-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-light text-lg font-semibold text-primary">
                  {selected.first_name[0]}{selected.last_name[0]}
                </div>
                <div>
                  <p className="font-medium text-slate-900">{selected.first_name} {selected.last_name}</p>
                  <p className="text-xs text-muted">{selected.email} &bull; {selected.phone}</p>
                </div>
              </div>

              {editing ? (
                <div className="space-y-3 rounded-lg border border-slate-200 p-3">
                  <input
                    type="text"
                    placeholder="First name"
                    defaultValue={selected.first_name}
                    onChange={(e) => setEditForm((f) => ({ ...f, first_name: e.target.value }))}
                    className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
                  />
                  <input
                    type="text"
                    placeholder="Last name"
                    defaultValue={selected.last_name}
                    onChange={(e) => setEditForm((f) => ({ ...f, last_name: e.target.value }))}
                    className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    defaultValue={selected.email}
                    onChange={(e) => setEditForm((f) => ({ ...f, email: e.target.value }))}
                    className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
                  />
                  <input
                    type="tel"
                    placeholder="Phone"
                    defaultValue={selected.phone}
                    onChange={(e) => setEditForm((f) => ({ ...f, phone: e.target.value }))}
                    className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
                  />
                  <select
                    defaultValue={selected.channel_preference}
                    onChange={(e) => setEditForm((f) => ({ ...f, channel_preference: e.target.value as ChannelPreference }))}
                    className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
                  >
                    <option value="web">Web</option>
                    <option value="whatsapp">WhatsApp</option>
                    <option value="sms">SMS</option>
                    <option value="voice">Voice</option>
                  </select>
                  <textarea
                    placeholder="Notes"
                    defaultValue={selected.notes ?? ""}
                    onChange={(e) => setEditForm((f) => ({ ...f, notes: e.target.value }))}
                    className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
                    rows={3}
                  />
                  <div className="flex gap-2">
                    <button
                      className="rounded-md bg-primary px-3 py-2 text-sm font-medium text-white hover:bg-primary-hover"
                      onClick={() => void updatePatient()}
                    >
                      Save
                    </button>
                    <button
                      className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700"
                      onClick={() => setEditing(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="rounded-lg border border-slate-200 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-muted">Insurance</p>
                    <p className="mt-1 text-sm text-slate-900">{selected.insurance_provider ?? "Not provided"}</p>
                  </div>
                  <div className="rounded-lg border border-slate-200 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-muted">Status</p>
                    <p className="mt-1 flex items-center gap-2 text-sm">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${selected.is_active ? "bg-success/10 text-success" : "bg-slate-100 text-slate-500"}`}>
                        {selected.is_active ? "Active" : "Inactive"}
                      </span>
                      {selected.no_show_count > 0 ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-error/10 px-2 py-0.5 text-xs font-medium text-error">
                          <Ban className="h-3 w-3" /> {selected.no_show_count} no-show(s)
                        </span>
                      ) : null}
                    </p>
                  </div>
                  <button
                    className="w-full rounded-md border border-primary/40 px-3 py-2 text-sm font-medium text-primary hover:bg-primary-light"
                    onClick={() => {
                      setEditForm({
                        first_name: selected.first_name,
                        last_name: selected.last_name,
                        email: selected.email,
                        phone: selected.phone,
                        channel_preference: selected.channel_preference,
                        notes: selected.notes ?? "",
                      });
                      setEditing(true);
                    }}
                  >
                    Edit patient
                  </button>
                </div>
              )}

              <div>
                <h3 className="mb-2 font-heading text-base font-semibold text-slate-900">Appointment history</h3>
                <div className="space-y-2">
                  {appointments.length ? (
                    appointments.map((appt) => (
                      <div key={appt.id} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2 text-sm">
                        <div>
                          <p className="font-medium text-slate-900">{appt.service.name}</p>
                          <p className="text-xs text-muted">{format(new Date(appt.start_time), "MMM d, yyyy h:mm a")}</p>
                        </div>
                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[appt.status] ?? "bg-slate-100 text-slate-700"}`}>
                          {appt.status}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted">No appointments found.</p>
                  )}
                </div>
              </div>
            </div>
          ) : null}
        </SheetContent>
      </Sheet>
    </div>
  );
}

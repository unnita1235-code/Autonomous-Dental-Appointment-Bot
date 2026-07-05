"use client";

import { useEffect, useState } from "react";
import { CheckCircle, Plus, XCircle } from "lucide-react";

import { parseJsonResponse } from "@/lib/http";
import type { IntegrationStatus, StaffUser } from "@/types";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
}

const DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];

const DAY_LABELS: Record<string, string> = {
  monday: "Monday",
  tuesday: "Tuesday",
  wednesday: "Wednesday",
  thursday: "Thursday",
  friday: "Friday",
  saturday: "Saturday",
  sunday: "Sunday",
};

export default function SettingsPage(): JSX.Element {
  const [staff, setStaff] = useState<StaffUser[]>([]);
  const [integrations, setIntegrations] = useState<IntegrationStatus[]>([]);
  const [hours, setHours] = useState<Record<string, { open: string; close: string; closed: boolean }>>(() => {
    const defaults: Record<string, { open: string; close: string; closed: boolean }> = {};
    DAYS.forEach((day) => {
      defaults[day] = { open: "09:00", close: "17:00", closed: day === "saturday" || day === "sunday" };
    });
    return defaults;
  });

  useEffect(() => {
    const load = async (): Promise<void> => {
      const [staffRes, integrationsRes] = await Promise.all([
        fetch("/staff-api/staff", { cache: "no-store" }),
        fetch("/staff-api/config-check/status", { cache: "no-store" }),
      ]);
      const staffPayload = await parseJsonResponse<ApiEnvelope<StaffUser[]>>(staffRes);
      if (staffPayload?.success && staffPayload.data) setStaff(staffPayload.data);

      const intPayload = await parseJsonResponse<ApiEnvelope<IntegrationStatus[]>>(integrationsRes);
      if (intPayload?.success && intPayload.data) setIntegrations(intPayload.data);
    };
    void load();
  }, []);

  const toggleDay = (day: string): void => {
    setHours((prev) => ({ ...prev, [day]: { ...prev[day], closed: !prev[day].closed } }));
  };

  const updateTime = (day: string, field: "open" | "close", value: string): void => {
    setHours((prev) => ({ ...prev, [day]: { ...prev[day], [field]: value } }));
  };

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-heading text-2xl font-semibold text-slate-900">Settings</h1>
      </header>

      <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="mb-4 font-heading text-lg font-semibold text-slate-900">Operating hours</h2>
        <div className="space-y-2">
          {DAYS.map((day) => (
            <div key={day} className="flex items-center gap-4 rounded-lg border border-slate-100 px-3 py-2">
              <div className="w-28 text-sm font-medium text-slate-900">{DAY_LABELS[day]}</div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={!hours[day]?.closed}
                  onChange={() => toggleDay(day)}
                  className="rounded border-slate-300"
                />
                Open
              </label>
              {!hours[day]?.closed ? (
                <div className="flex items-center gap-2">
                  <input
                    type="time"
                    value={hours[day]?.open ?? "09:00"}
                    onChange={(e) => updateTime(day, "open", e.target.value)}
                    className="rounded-md border border-slate-300 px-2 py-1 text-sm"
                  />
                  <span className="text-sm text-muted">to</span>
                  <input
                    type="time"
                    value={hours[day]?.close ?? "17:00"}
                    onChange={(e) => updateTime(day, "close", e.target.value)}
                    className="rounded-md border border-slate-300 px-2 py-1 text-sm"
                  />
                </div>
              ) : (
                <span className="text-sm text-muted">Closed</span>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="mb-4 font-heading text-lg font-semibold text-slate-900">Staff management</h2>
        <div className="overflow-hidden rounded-lg border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-muted">Name</th>
                <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-muted">Email</th>
                <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-muted">Role</th>
                <th className="px-4 py-2 text-center text-xs font-semibold uppercase tracking-wide text-muted">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {staff.length ? (
                staff.map((user) => (
                  <tr key={user.id} className="text-sm">
                    <td className="px-4 py-2 font-medium text-slate-900">{user.first_name} {user.last_name}</td>
                    <td className="px-4 py-2 text-muted">{user.email}</td>
                    <td className="px-4 py-2 capitalize text-slate-700">{user.role.toLowerCase()}</td>
                    <td className="px-4 py-2 text-center">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${user.is_active ? "bg-success/10 text-success" : "bg-slate-100 text-slate-500"}`}>
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-sm text-muted">No staff users found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="mb-4 font-heading text-lg font-semibold text-slate-900">Integration status</h2>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {integrations.length ? (
            integrations.map((item) => (
              <div key={item.service} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2 text-sm">
                <span className="text-slate-700">{item.service}</span>
                <span className={`inline-flex items-center gap-1 text-xs font-medium ${
                  item.status === "CONFIGURED" || item.status === "ENABLED" ? "text-success" : "text-error"
                }`}>
                  {item.status === "CONFIGURED" || item.status === "ENABLED" ? (
                    <CheckCircle className="h-3.5 w-3.5" />
                  ) : (
                    <XCircle className="h-3.5 w-3.5" />
                  )}
                  {item.status}
                </span>
              </div>
            ))
          ) : (
            <p className="col-span-full py-6 text-center text-sm text-muted">Loading integration status&hellip;</p>
          )}
        </div>
      </section>
    </div>
  );
}

"use client";

import { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { CalendarCheck2, Clock3, MessageCircleMore, ShieldCheck, Users } from "lucide-react";

import { parseJsonResponse } from "@/lib/http";
import type { AnalyticsSummary } from "@/types";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
}

const CHANNEL_COLORS: Record<string, string> = {
  web: "#4f46e5",
  whatsapp: "#22c55e",
  sms: "#3b82f6",
  voice: "#f59e0b",
  staff: "#8b5cf6",
};

const STATUS_COLORS: Record<string, string> = {
  PENDING: "#f59e0b",
  CONFIRMED: "#22c55e",
  CANCELLED: "#ef4444",
  COMPLETED: "#4f46e5",
  NO_SHOW: "#94a3b8",
};

function MetricCard({ title, value, description, icon: Icon }: { title: string; value: string; description: string; icon: React.ComponentType<{ className?: string }> }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted">{title}</p>
          <p className="mt-1 font-heading text-2xl font-semibold text-slate-900">{value}</p>
        </div>
        <span className="rounded-lg bg-primary-light p-2 text-primary">
          <Icon className="h-5 w-5" />
        </span>
      </div>
      <p className="mt-3 text-xs text-muted">{description}</p>
    </article>
  );
}

export default function AnalyticsPage(): JSX.Element {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    setLoading(true);
    const load = async (): Promise<void> => {
      const response = await fetch(`/staff-api/analytics/summary?days=${days}`, { cache: "no-store" });
      const payload = await parseJsonResponse<ApiEnvelope<AnalyticsSummary>>(response);
      if (payload?.success && payload.data) {
        setData(payload.data);
      }
      setLoading(false);
    };
    void load();
  }, [days]);

  const chartData = useMemo(() => {
    if (!data?.bookings_per_day) return [];
    return data.bookings_per_day.map((item) => ({
      date: item.date,
      bookings: item.count,
    }));
  }, [data]);

  const channelData = useMemo(() => {
    if (!data?.channel_mix) return [];
    return data.channel_mix.map((item) => ({
      name: item.channel.charAt(0).toUpperCase() + item.channel.slice(1),
      value: item.count,
      channel: item.channel,
    }));
  }, [data]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-sm text-muted">Loading analytics…</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-heading text-2xl font-semibold text-slate-900">Analytics</h1>
        <select
          value={days}
          onChange={(event) => setDays(Number(event.target.value))}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <MetricCard title="Total appointments" value={String(data?.total_appointments ?? 0)} description={`In the last ${data?.period_days ?? 30} days`} icon={CalendarCheck2} />
        <MetricCard title="Total patients" value={String(data?.total_patients ?? 0)} description="Unique patients served" icon={Users} />
        <MetricCard title="Pending confirmations" value={String(data?.pending_confirmations ?? 0)} description="Awaiting confirmation" icon={Clock3} />
        <MetricCard title="Bot resolution" value={`${data?.bot_resolution_rate ?? 0}%`} description="Handled without handoff" icon={ShieldCheck} />
        <MetricCard title="Active conversations" value={String(data?.total_conversations ?? 0)} description="Last 7 days" icon={MessageCircleMore} />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="mb-4 font-heading text-lg font-semibold text-slate-900">Bookings per day</h2>
          {chartData.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(value: string) => value.slice(5)} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="bookings" stroke="#4f46e5" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="py-10 text-center text-sm text-muted">No booking data for this period.</p>
          )}
        </article>

        <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="mb-4 font-heading text-lg font-semibold text-slate-900">Channel mix</h2>
          {channelData.length ? (
            <div className="flex items-center gap-4">
              <ResponsiveContainer width="60%" height={220}>
                <PieChart>
                  <Pie data={channelData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name }) => name}>
                    {channelData.map((entry) => (
                      <Cell key={entry.channel} fill={CHANNEL_COLORS[entry.channel] ?? "#94a3b8"} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2">
                {channelData.map((item) => (
                  <div key={item.channel} className="flex items-center gap-2 text-sm">
                    <span className="inline-block h-3 w-3 rounded-full" style={{ backgroundColor: CHANNEL_COLORS[item.channel] ?? "#94a3b8" }} />
                    <span className="text-slate-700">{item.name}</span>
                    <span className="font-medium text-slate-900">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="py-10 text-center text-sm text-muted">No channel data available.</p>
          )}
        </article>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="mb-4 font-heading text-lg font-semibold text-slate-900">Status breakdown</h2>
          {data?.status_breakdown?.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.status_breakdown.map((item) => ({ status: item.status, count: item.count }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="status" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {data.status_breakdown.map((entry) => (
                    <Cell key={entry.status} fill={STATUS_COLORS[entry.status] ?? "#94a3b8"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="py-10 text-center text-sm text-muted">No status data available.</p>
          )}
        </article>
      </section>
    </div>
  );
}

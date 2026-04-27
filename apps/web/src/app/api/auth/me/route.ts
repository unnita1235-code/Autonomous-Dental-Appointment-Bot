import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { STAFF_JWT_COOKIE } from "@/lib/staff-auth";

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

export async function GET(): Promise<NextResponse> {
  const token = cookies().get(STAFF_JWT_COOKIE)?.value;
  if (!token) {
    return NextResponse.json({ success: false, error: "Unauthorized" }, { status: 401 });
  }

  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  const response = await fetch(`${baseUrl}/api/v1/auth/me`, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store"
  });
  const envelope = (await response.json()) as ApiEnvelope<Record<string, unknown>>;
  if (!response.ok || !envelope.success) {
    return NextResponse.json(
      { success: false, error: envelope.error ?? "Unauthorized" },
      { status: response.status }
    );
  }

  return NextResponse.json({ success: true, data: envelope.data });
}

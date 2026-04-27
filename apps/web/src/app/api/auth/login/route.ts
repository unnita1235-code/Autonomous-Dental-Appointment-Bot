import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { STAFF_JWT_COOKIE } from "@/lib/staff-auth";

interface LoginPayload {
  email: string;
  password: string;
}

interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

interface LoginData {
  access_token: string;
  expires_in: number;
}

export async function POST(request: Request): Promise<NextResponse> {
  const payload = (await request.json()) as LoginPayload;
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  const response = await fetch(`${baseUrl}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const envelope = (await response.json()) as ApiEnvelope<LoginData>;
  if (!response.ok || !envelope.success || !envelope.data) {
    return NextResponse.json(
      { success: false, error: envelope.error ?? "Unable to log in." },
      { status: response.status || 401 }
    );
  }

  const cookieStore = cookies();
  cookieStore.set(STAFF_JWT_COOKIE, envelope.data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: envelope.data.expires_in
  });

  return NextResponse.json({ success: true, data: { expires_in: envelope.data.expires_in } });
}

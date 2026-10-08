import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { API_BASE_URL } from "@/lib/api";

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await context.params;

    // GET /api/v1/appointments/{appointment_id} is a public read on the backend
    // (no auth dependency). Forward an Authorization header only when one is
    // actually present, instead of rejecting callers we cannot authenticate.
    const token = cookies().get("jwt_token")?.value ??
                  request.headers.get("authorization")?.replace("Bearer ", "") ??
                  null;

    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    // Forward request to backend API
    const response = await fetch(`${API_BASE_URL}/api/v1/appointments/${id}`, {
      headers,
      cache: "no-store",
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Appointment API error:", error);
    return NextResponse.json(
      { success: false, error: "Internal server error", data: null },
      { status: 500 }
    );
  }
}
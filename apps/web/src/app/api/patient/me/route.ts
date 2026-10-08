import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { apiClient, API_BASE_URL } from "@/lib/api";

export async function GET(request: NextRequest): Promise<NextResponse> {
  try {
    // Get the auth token from cookies or headers
    const token = cookies().get("jwt_token")?.value ?? 
                  request.headers.get("authorization")?.replace("Bearer ", "") ?? 
                  null;

    if (!token) {
      return NextResponse.json(
        { success: false, error: "Unauthorized", data: null },
        { status: 401 }
      );
    }

    // Forward request to backend API
    const response = await fetch(`${API_BASE_URL}/api/v1/patients/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Patient API error:", error);
    return NextResponse.json(
      { success: false, error: "Internal server error", data: null },
      { status: 500 }
    );
  }
}
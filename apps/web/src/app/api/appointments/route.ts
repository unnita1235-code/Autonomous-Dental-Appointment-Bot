import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { API_BASE_URL } from "@/lib/api";

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

    // Forward query parameters to backend
    const searchParams = request.nextUrl.searchParams;
    const queryString = searchParams.toString();
    
    const url = `${API_BASE_URL}/api/v1/appointments${queryString ? `?${queryString}` : ""}`;

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Appointments API error:", error);
    return NextResponse.json(
      { success: false, error: "Internal server error", data: null },
      { status: 500 }
    );
  }
}
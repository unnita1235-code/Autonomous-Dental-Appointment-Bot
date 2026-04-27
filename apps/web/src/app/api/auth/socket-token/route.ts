import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { STAFF_JWT_COOKIE } from "@/lib/staff-auth";

export async function GET(): Promise<NextResponse> {
  const token = cookies().get(STAFF_JWT_COOKIE)?.value;
  if (!token) {
    return NextResponse.json({ success: false, error: "Unauthorized" }, { status: 401 });
  }
  return NextResponse.json({ success: true, data: { token } });
}

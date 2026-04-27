import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { STAFF_JWT_COOKIE } from "@/lib/staff-auth";

export async function POST(): Promise<NextResponse> {
  cookies().delete(STAFF_JWT_COOKIE);
  return NextResponse.json({ success: true });
}

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { STAFF_JWT_COOKIE } from "@/lib/staff-auth";

export async function POST(): Promise<NextResponse> {
  cookies().set(STAFF_JWT_COOKIE, "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 0
  });
  return NextResponse.json({ success: true });
}

import { NextResponse, type NextRequest } from "next/server";

import { STAFF_JWT_COOKIE, isJwtExpired } from "@/lib/staff-auth";

export function middleware(request: NextRequest): NextResponse {
  const token = request.cookies.get(STAFF_JWT_COOKIE)?.value;
  if (!token || isJwtExpired(token)) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", request.nextUrl.pathname);
    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete(STAFF_JWT_COOKIE);
    return response;
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"]
};

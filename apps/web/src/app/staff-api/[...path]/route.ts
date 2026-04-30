import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { STAFF_JWT_COOKIE, isJwtExpired } from "@/lib/staff-auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const buildTargetUrl = (request: NextRequest, path: string[]): string => {
  const incomingUrl = new URL(request.url);
  const targetUrl = new URL(`${API_BASE_URL}/api/v1/${path.join("/")}`);
  targetUrl.search = incomingUrl.search;
  return targetUrl.toString();
};

const getAuthToken = (): string | null => {
  const token = cookies().get(STAFF_JWT_COOKIE)?.value ?? null;
  if (!token || isJwtExpired(token)) {
    return null;
  }
  return token;
};

const proxyRequest = async (request: NextRequest, path: string[]): Promise<NextResponse> => {
  const token = getAuthToken();
  if (!token) {
    return NextResponse.json({ success: false, error: "Unauthorized" }, { status: 401 });
  }

  const targetUrl = buildTargetUrl(request, path);
  const incomingContentType = request.headers.get("content-type");
  const headers = new Headers({ Authorization: `Bearer ${token}` });
  if (incomingContentType) {
    headers.set("Content-Type", incomingContentType);
  }

  const hasBody = request.method !== "GET" && request.method !== "HEAD";
  const upstreamResponse = await fetch(targetUrl, {
    method: request.method,
    headers,
    body: hasBody ? await request.text() : undefined,
    cache: "no-store"
  });

  const responseBody = await upstreamResponse.text();
  const response = new NextResponse(responseBody, { status: upstreamResponse.status });
  const upstreamType = upstreamResponse.headers.get("content-type");
  if (upstreamType) {
    response.headers.set("content-type", upstreamType);
  }
  return response;
};

export async function GET(
  request: NextRequest,
  context: { params: { path: string[] } }
): Promise<NextResponse> {
  return proxyRequest(request, context.params.path);
}

export async function POST(
  request: NextRequest,
  context: { params: { path: string[] } }
): Promise<NextResponse> {
  return proxyRequest(request, context.params.path);
}

export async function PATCH(
  request: NextRequest,
  context: { params: { path: string[] } }
): Promise<NextResponse> {
  return proxyRequest(request, context.params.path);
}

export async function PUT(
  request: NextRequest,
  context: { params: { path: string[] } }
): Promise<NextResponse> {
  return proxyRequest(request, context.params.path);
}

export async function DELETE(
  request: NextRequest,
  context: { params: { path: string[] } }
): Promise<NextResponse> {
  return proxyRequest(request, context.params.path);
}

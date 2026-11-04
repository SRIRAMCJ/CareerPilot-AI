import { NextRequest, NextResponse } from "next/server";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

async function proxy(request: NextRequest, context: RouteContext): Promise<Response> {
  const configuredBackend = process.env.CAREERPILOT_API_URL;
  const backendUrl =
    configuredBackend ||
    (process.env.NODE_ENV === "production" ? "" : "http://127.0.0.1:8000");
  const proxyToken = process.env.CAREERPILOT_PROXY_TOKEN;

  if (!backendUrl || (process.env.NODE_ENV === "production" && !proxyToken)) {
    return NextResponse.json(
      { detail: "CareerPilot API proxy is not configured." },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }

  const { path } = await context.params;
  const upstreamUrl = new URL(
    `/api/${path.map((segment) => encodeURIComponent(segment)).join("/")}`,
    backendUrl.endsWith("/") ? backendUrl : `${backendUrl}/`,
  );
  upstreamUrl.search = request.nextUrl.search;

  const headers = new Headers();
  for (const name of ["accept", "content-type", "if-none-match", "range"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  if (proxyToken) headers.set("x-careerpilot-proxy-token", proxyToken);

  const method = request.method.toUpperCase();
  const body = method === "GET" || method === "HEAD" ? undefined : await request.arrayBuffer();

  try {
    const upstream = await fetch(upstreamUrl, {
      method,
      headers,
      body,
      cache: "no-store",
      redirect: "manual",
    });
    const responseHeaders = new Headers();
    for (const name of [
      "content-type",
      "content-disposition",
      "cache-control",
      "etag",
      "last-modified",
      "retry-after",
      "location",
    ]) {
      const value = upstream.headers.get(name);
      if (value) responseHeaders.set(name, value);
    }
    responseHeaders.set("Cache-Control", "no-store");
    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: responseHeaders,
    });
  } catch {
    return NextResponse.json(
      { detail: "CareerPilot backend is temporarily unavailable." },
      { status: 502, headers: { "Cache-Control": "no-store" } },
    );
  }
}

export { proxy as GET, proxy as POST, proxy as PUT, proxy as PATCH, proxy as DELETE };

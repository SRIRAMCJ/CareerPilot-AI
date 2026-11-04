import { NextRequest, NextResponse } from "next/server";

function constantTimeEqual(left: string, right: string): boolean {
  if (left.length !== right.length) return false;
  let difference = 0;
  for (let index = 0; index < left.length; index += 1) {
    difference |= left.charCodeAt(index) ^ right.charCodeAt(index);
  }
  return difference === 0;
}

export function middleware(request: NextRequest) {
  // Google must be able to return to the OAuth callback without the browser's
  // Basic Auth challenge. The server-side API proxy still adds its secret token,
  // and the backend validates Google's one-time OAuth state.
  if (request.nextUrl.pathname === "/api/v1/gmail/auth/callback") {
    return NextResponse.next();
  }

  const username = process.env.DASHBOARD_USERNAME;
  const password = process.env.DASHBOARD_PASSWORD;

  if (!username || !password) {
    if (process.env.NODE_ENV === "production") {
      return new NextResponse("Dashboard authentication is not configured.", {
        status: 503,
        headers: { "Cache-Control": "no-store" },
      });
    }
    return NextResponse.next();
  }

  const authorization = request.headers.get("authorization") || "";
  if (authorization.startsWith("Basic ")) {
    try {
      const decoded = atob(authorization.slice(6));
      const separator = decoded.indexOf(":");
      if (separator >= 0) {
        const suppliedUser = decoded.slice(0, separator);
        const suppliedPassword = decoded.slice(separator + 1);
        if (
          constantTimeEqual(suppliedUser, username) &&
          constantTimeEqual(suppliedPassword, password)
        ) {
          return NextResponse.next();
        }
      }
    } catch {
      // Malformed Basic credentials are treated as unauthenticated.
    }
  }

  return new NextResponse("Authentication required.", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="CareerPilot AI", charset="UTF-8"',
      "Cache-Control": "no-store",
    },
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml).*)"],
};

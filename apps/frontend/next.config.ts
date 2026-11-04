import type { NextConfig } from "next";

const backendUrl = process.env.CAREERPILOT_API_INTERNAL_URL || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;

import type { NextConfig } from "next";

const backendUrl = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Next dev only trusts "localhost" by default; opening the app via
  // 127.0.0.1 gets its HMR/RSC requests silently blocked, which breaks all
  // client-side hydration with no console error (see Karar Günlüğü #30).
  allowedDevOrigins: ["127.0.0.1", "localhost"],
  // Django's URLs always have a trailing slash; without this Next.js's own
  // slash-redirect runs before the rewrite below and drops it.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      {
        // Next.js's :path* reconstruction drops the trailing slash Django's
        // URLconf requires on every route, so it's added back explicitly.
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*/`,
      },
    ];
  },
};

export default nextConfig;

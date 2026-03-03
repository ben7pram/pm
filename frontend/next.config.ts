import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // export the app as static HTML in production builds only
  output: process.env.NODE_ENV === "production" ? "export" : undefined,
  // assets will be served from /static so that backend can mount the folder there
  assetPrefix: "/static",
  // during development we forward API calls to the backend server on 8000
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        // ensure all HTTP methods are proxied to backend (GET worked already,
        // POST was returning 404 in tests)
        destination: "http://localhost:8000/api/:path*",
        // the `methods` field is supported in Next.js rewrites and defaults to
        // all methods, but being explicit here guards against unexpected
        // limitations in development mode.
        methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      },
    ];
  },
};

export default nextConfig;

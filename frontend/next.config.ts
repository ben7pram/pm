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
        // during development we proxy all API requests to the backend server
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;

import type { NextConfig } from "next";

const pythonApiUrl =
  process.env.PYTHON_API_URL ??
  process.env.NEXT_PUBLIC_PYTHON_API_URL ??
  "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${pythonApiUrl.replace(/\/$/, "")}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;

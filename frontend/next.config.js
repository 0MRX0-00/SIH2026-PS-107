/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  async rewrites() {
    const backendUrl = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    const cleanBackendUrl = backendUrl.replace(/\/api\/v1\/?$/, "").replace(/\/+$/, "");
    return [
      {
        source: "/api/v1/:path*",
        destination: `${cleanBackendUrl}/api/v1/:path*`,
      },
      {
        source: "/health",
        destination: `${cleanBackendUrl}/health`,
      },
    ];
  },
};

module.exports = nextConfig;

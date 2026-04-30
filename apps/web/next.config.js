/** @type {import('next').NextConfig} */
const clinicLogoDomain = process.env.NEXT_PUBLIC_CLINIC_LOGO_DOMAIN ?? "localhost";

const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
    NEXT_PUBLIC_SOCKET_URL: process.env.NEXT_PUBLIC_SOCKET_URL,
    NEXT_PUBLIC_CLINIC_LOGO_DOMAIN: process.env.NEXT_PUBLIC_CLINIC_LOGO_DOMAIN
  },
  async rewrites() {
    const apiUrl = process.env.API_URL ?? "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/:path*`
      }
    ];
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: clinicLogoDomain, pathname: "/**" },
      { protocol: "http", hostname: "localhost", pathname: "/**" }
    ]
  }
};

module.exports = nextConfig;

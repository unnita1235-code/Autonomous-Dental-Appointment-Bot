/** @type {import('next').NextConfig} */
const clinicLogoDomain = process.env.NEXT_PUBLIC_CLINIC_LOGO_DOMAIN ?? "localhost";

let configWrapper = (cfg) => cfg;
try {
  const { withSentryConfig } = require("@sentry/nextjs");
  if (process.env.SENTRY_DSN || process.env.NEXT_PUBLIC_SENTRY_DSN) {
    configWrapper = (cfg) =>
      withSentryConfig(cfg, {
        silent: true,
        tunnelRoute: "/monitoring",
      });
  }
} catch (_) {
  // @sentry/nextjs not installed; Sentry is a no-op
}

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
      },
      {
        source: "/staff-api/:path*",
        destination: `${apiUrl}/api/v1/:path*`
      }
    ];
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: clinicLogoDomain, pathname: "/**" },
      { protocol: "http", hostname: "localhost", pathname: "/**" }
    ]
  },
  // Performance optimizations
  swcMinify: true,
  compress: true,
  poweredByHeader: false,
};

const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-XSS-Protection", value: "1; mode=block" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
];

nextConfig.headers = async () => [
  { source: "/(.*)", headers: securityHeaders },
];

module.exports = configWrapper(nextConfig);

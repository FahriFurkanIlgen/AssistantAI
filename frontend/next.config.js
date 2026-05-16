/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  // 'standalone' = küçük Docker imajı (Render/Fly/self-host icin).
  // Vercel'de bu satir gorulmezden gelinir, sorun yok.
  output: "standalone",
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
  typescript: { ignoreBuildErrors: true },
  productionBrowserSourceMaps: false,
};

module.exports = nextConfig;

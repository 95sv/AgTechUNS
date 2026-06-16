/** @type {import('next').NextConfig} */
const nextConfig = {
  // 'standalone' genera un server.js autocontenido en .next/standalone,
  // ideal para copiar a una imagen Docker liviana (ver Dockerfile).
  output: 'standalone',
  reactStrictMode: true,
};

module.exports = nextConfig;

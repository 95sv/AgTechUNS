import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], weight: ['400', '500', '600', '700'] });

export const metadata = {
  title: 'AgTechUNS — Panel de Control',
  description: 'Plataforma de Agricultura Inteligente — Comisión 13 — UNS 2026',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body className={`${inter.className} bg-stone-50 text-stone-800 min-h-screen`}>{children}</body>
    </html>
  );
}

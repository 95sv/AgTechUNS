import type { Metadata } from 'next'
import './globals.css'
import NavBar from './components/NavBar'

export const metadata: Metadata = {
  title: 'AgTechUNS — Monitoreo Agrícola',
  description: 'Plataforma de monitoreo y predicción agrícola — UNS Comisión 13',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        />
      </head>
      <body>
        <NavBar />
        <main className="min-h-screen p-6">{children}</main>
      </body>
    </html>
  )
}

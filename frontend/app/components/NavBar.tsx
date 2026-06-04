'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'

export default function NavBar() {
  const [userEmail, setUserEmail] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    setMounted(true)
    setUserEmail(localStorage.getItem('agtech_email'))
  }, [pathname])

  const logout = () => {
    localStorage.removeItem('agtech_token')
    localStorage.removeItem('agtech_email')
    setUserEmail(null)
    router.push('/login')
  }

  return (
    <nav className="bg-agtech-green text-white px-6 py-3 flex items-center gap-6 shadow-md">
      <Link href="/" className="font-bold text-lg tracking-wide hover:text-agtech-light transition-colors">
        🌾 AgTechUNS
      </Link>
      <Link href="/" className="text-sm hover:text-agtech-light transition-colors">Dashboard</Link>
      <Link href="/map" className="text-sm hover:text-agtech-light transition-colors">Mapa</Link>
      <Link href="/alerts" className="text-sm hover:text-agtech-light transition-colors">Alertas</Link>
      <Link href="/recommendations" className="text-sm hover:text-agtech-light transition-colors">Recomendaciones</Link>
      <Link href="/admin" className="text-sm hover:text-agtech-light transition-colors">Admin</Link>

      <div className="ml-auto flex items-center gap-3">
        {mounted && (
          userEmail ? (
            <>
              <span className="text-xs text-agtech-light truncate max-w-[180px]">{userEmail}</span>
              <button
                onClick={logout}
                className="text-xs bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded transition-colors"
              >
                Cerrar sesión
              </button>
            </>
          ) : (
            <Link
              href="/login"
              className="text-xs bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded transition-colors"
            >
              Iniciar sesión
            </Link>
          )
        )}
      </div>
    </nav>
  )
}

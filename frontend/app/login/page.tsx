'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'

type Tab = 'login' | 'register'

export default function LoginPage() {
  const router = useRouter()
  const [tab, setTab] = useState<Tab>('login')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const [nombre, setNombre] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regPassword, setRegPassword] = useState('')
  const [telefono, setTelefono] = useState('')

  const saveSession = (token: string, userEmail: string) => {
    localStorage.setItem('agtech_token', token)
    localStorage.setItem('agtech_email', userEmail)
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.login(email, password)
      saveSession(res.access_token, email)
      router.push('/')
    } catch (err: any) {
      setError(err.message ?? 'Error al iniciar sesión')
    }
    setLoading(false)
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.register(regEmail, nombre, regPassword, telefono || undefined)
      const res = await api.login(regEmail, regPassword)
      saveSession(res.access_token, regEmail)
      router.push('/')
    } catch (err: any) {
      setError(err.message ?? 'Error al registrarse')
    }
    setLoading(false)
  }

  const tabCls = (t: Tab) =>
    `flex-1 pb-2 text-sm font-medium transition-colors ${tab === t ? 'text-agtech-green border-b-2 border-agtech-green' : 'text-gray-400 hover:text-gray-600'}`

  return (
    <div className="min-h-screen flex items-center justify-center bg-agtech-bg -m-6">
      <div className="bg-white rounded-2xl shadow-lg w-full max-w-md p-8 mx-4">
        <div className="text-center mb-6">
          <p className="text-4xl mb-2">🌾</p>
          <h1 className="text-2xl font-bold text-agtech-green">AgTechUNS</h1>
          <p className="text-gray-500 text-sm">Plataforma de monitoreo agrícola · UNS Comisión 13</p>
        </div>

        <div className="flex border-b border-gray-200 mb-6">
          <button className={tabCls('login')} onClick={() => { setTab('login'); setError('') }}>
            Iniciar sesión
          </button>
          <button className={tabCls('register')} onClick={() => { setTab('register'); setError('') }}>
            Registrarse
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
            {error}
          </div>
        )}

        {tab === 'login' && (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email" required value={email} onChange={e => setEmail(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-agtech-light"
                placeholder="usuario@ejemplo.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
              <input
                type="password" required value={password} onChange={e => setPassword(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-agtech-light"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit" disabled={loading}
              className="w-full bg-agtech-green text-white py-2 rounded-lg font-medium hover:bg-agtech-light transition-colors disabled:opacity-60"
            >
              {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
            </button>
            <p className="text-center text-xs text-gray-400">
              ¿No tenés cuenta?{' '}
              <button type="button" className="text-agtech-green underline" onClick={() => setTab('register')}>
                Registrate aquí
              </button>
            </p>
          </form>
        )}

        {tab === 'register' && (
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre completo</label>
              <input
                type="text" required value={nombre} onChange={e => setNombre(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-agtech-light"
                placeholder="Juan García"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email" required value={regEmail} onChange={e => setRegEmail(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-agtech-light"
                placeholder="usuario@ejemplo.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
              <input
                type="password" required value={regPassword} onChange={e => setRegPassword(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-agtech-light"
                placeholder="••••••••"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Teléfono <span className="text-gray-400">(opcional)</span>
              </label>
              <input
                type="tel" value={telefono} onChange={e => setTelefono(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-agtech-light"
                placeholder="+54 291 xxxxxxx"
              />
            </div>
            <button
              type="submit" disabled={loading}
              className="w-full bg-agtech-green text-white py-2 rounded-lg font-medium hover:bg-agtech-light transition-colors disabled:opacity-60"
            >
              {loading ? 'Registrando...' : 'Crear cuenta e ingresar'}
            </button>
            <p className="text-center text-xs text-gray-400">
              ¿Ya tenés cuenta?{' '}
              <button type="button" className="text-agtech-green underline" onClick={() => setTab('login')}>
                Iniciá sesión
              </button>
            </p>
          </form>
        )}
      </div>
    </div>
  )
}

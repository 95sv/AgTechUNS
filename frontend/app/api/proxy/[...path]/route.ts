import { NextRequest, NextResponse } from 'next/server'

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8000'

async function handler(request: NextRequest, { params }: { params: { path: string[] } }) {
  const backendPath = '/' + params.path.join('/')
  const token = request.headers.get('authorization')

  const init: RequestInit = {
    method: request.method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: token } : {}),
    },
  }

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    const body = await request.text()
    if (body) init.body = body
  }

  try {
    const res = await fetch(`${BACKEND}${backendPath}`, init)
    const data = await res.json().catch(() => null)
    return NextResponse.json(data ?? { ok: true }, { status: res.status })
  } catch {
    return NextResponse.json({ detail: 'Backend no disponible' }, { status: 503 })
  }
}

export { handler as GET, handler as POST, handler as PUT, handler as PATCH }

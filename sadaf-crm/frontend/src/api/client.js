const BASE = import.meta.env.VITE_API_URL || '/api'
const TOKEN_KEY = 'sadaf_token'
export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY) || '',
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY)
}
export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}
const listeners = new Set()
export const onUnauthorized = (fn) => { listeners.add(fn); return () => listeners.delete(fn) }
function headers(extra = {}) {
  const out = { Accept: 'application/json', ...extra }
  const token = tokenStore.get()
  if (token) out.Authorization = `Bearer ${token}`
  return out
}
function qs(params) {
  const clean = Object.entries(params || {}).filter(([, v]) => v !== undefined && v !== null && v !== '')
  return clean.length ? '?' + new URLSearchParams(clean).toString() : ''
}
async function parse(res) {
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}
async function request(method, path, { body, params, raw = false } = {}) {
  let res
  try {
    res = await fetch(BASE + path + qs(params), {
      method,
      headers: body === undefined
        ? headers()
        : headers({ 'Content-Type': 'application/json' }),
      body: body === undefined ? undefined : JSON.stringify(body)
    })
  } catch {
    throw new ApiError("Serverga ulanib bo'lmadi. Backend ishlayotganini tekshiring.", 0, null)
  }

  if (res.status === 401) {
    tokenStore.clear()
    listeners.forEach((fn) => fn())
    throw new ApiError('Sessiya tugadi. Qaytadan kiring.', 401, null)
  }

  if (!res.ok) {
    const payload = await parse(res)
    const message = payload?.detail || payload?.message || `Xatolik (${res.status})`
    throw new ApiError(typeof message === 'string' ? message : 'Xatolik', res.status, payload)
  }

  return raw ? res : parse(res)
}

export const http = {
  get: (path, params) => request('GET', path, { params }),
  post: (path, body, params) => request('POST', path, { body, params }),
  put: (path, body) => request('PUT', path, { body }),
  patch: (path, body) => request('PATCH', path, { body: body ?? {} }),
  del: (path) => request('DELETE', path),
  raw: (path, params) => request('GET', path, { params, raw: true })
}
export async function download(path, params, fallbackName = 'export.xlsx') {
  const res = await http.raw(path, params)
  const disposition = res.headers.get('Content-Disposition') || ''
  const match = /filename="?([^"]+)"?/.exec(disposition)
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = match ? match[1] : fallbackName
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

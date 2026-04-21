export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

export type ApiError = { status: number; message: string }

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    credentials: 'include',
  })

  if (!res.ok) {
    let message = `${res.status} ${res.statusText}`
    try {
      const data = await res.json()
      message = data?.detail ?? data?.message ?? message
    } catch {
      // ignore
    }
    throw { status: res.status, message } as ApiError
  }

  // 204 No Content
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

import React from 'react'
import { Link } from 'react-router-dom'
import { fetchJson } from '@/lib/api'

export default function ResetRequestPage() {
  const [email, setEmail] = React.useState('')
  const [token, setToken] = React.useState<string | null>(null)
  const [error, setError] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await fetchJson<any>('/auth/password-reset/request', {
        method: 'POST',
        body: JSON.stringify({ email }),
      })
      setToken(res.token ?? null)
    } catch (err: any) {
      setError(err?.message ?? 'Ошибка')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-md mx-auto px-4 py-10">
      <div className="bg-white rounded-card shadow-card p-5">
        <h1 className="text-2xl font-semibold">Восстановление пароля</h1>
        <div className="text-sm text-muted mt-1">В демо-режиме токен возвращается прямо в ответе API.</div>

        <form className="mt-4 space-y-3" onSubmit={onSubmit}>
          <div>
            <div className="text-xs text-muted mb-1">Email</div>
            <input value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-xl border border-black/10 px-3 py-2" type="email" required />
          </div>
          {error ? <div className="text-sm text-red-700">{error}</div> : null}
          <button disabled={loading} className="w-full px-4 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium">
            {loading ? 'Отправляю…' : 'Получить токен'}
          </button>
        </form>

        {token ? (
          <div className="mt-4 bg-warmbg rounded-xl p-3">
            <div className="text-sm font-semibold">Токен</div>
            <div className="mt-2 text-xs break-all bg-white/70 rounded-lg p-2">{token}</div>
            <Link to={`/reset/confirm?token=${encodeURIComponent(token)}`} className="mt-3 inline-block px-4 py-2 rounded-xl bg-white border border-black/10 hover:bg-white">
              Перейти к смене пароля
            </Link>
          </div>
        ) : null}

        <div className="mt-4 text-sm text-muted">
          <Link to="/login" className="hover:underline">← Назад ко входу</Link>
        </div>
      </div>
    </main>
  )
}

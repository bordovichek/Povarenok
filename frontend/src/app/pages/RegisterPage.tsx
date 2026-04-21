import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchJson } from '@/lib/api'
import { useAuth } from '@/lib/auth'

export default function RegisterPage() {
  const nav = useNavigate()
  const { refresh } = useAuth()
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [password2, setPassword2] = React.useState('')
  const [error, setError] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (password !== password2) {
      setError('Пароли не совпадают')
      return
    }
    setLoading(true)
    try {
      await fetchJson('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      await refresh()
      nav('/')
    } catch (err: any) {
      setError(err?.message ?? 'Ошибка регистрации')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-md mx-auto px-4 py-10">
      <div className="bg-white rounded-card shadow-card p-5">
        <h1 className="text-2xl font-semibold">Регистрация</h1>
        <form className="mt-4 space-y-3" onSubmit={onSubmit}>
          <div>
            <div className="text-xs text-muted mb-1">Email</div>
            <input value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-xl border border-black/10 px-3 py-2" type="email" required />
          </div>
          <div>
            <div className="text-xs text-muted mb-1">Пароль</div>
            <input value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-xl border border-black/10 px-3 py-2" type="password" required minLength={8} />
          </div>
          <div>
            <div className="text-xs text-muted mb-1">Повторите пароль</div>
            <input value={password2} onChange={(e) => setPassword2(e.target.value)} className="w-full rounded-xl border border-black/10 px-3 py-2" type="password" required minLength={8} />
          </div>

          {error ? <div className="text-sm text-red-700">{error}</div> : null}

          <button disabled={loading} className="w-full px-4 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium">
            {loading ? 'Создаю…' : 'Создать аккаунт'}
          </button>
        </form>

        <div className="mt-4 text-sm text-muted flex items-center justify-between">
          <Link to="/login" className="hover:underline">Уже есть аккаунт?</Link>
        </div>
      </div>
    </main>
  )
}

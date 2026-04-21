import React from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { fetchJson } from '@/lib/api'

export default function ResetConfirmPage() {
  const nav = useNavigate()
  const [params] = useSearchParams()
  const [token, setToken] = React.useState(params.get('token') ?? '')
  const [password, setPassword] = React.useState('')
  const [password2, setPassword2] = React.useState('')
  const [error, setError] = React.useState<string | null>(null)
  const [ok, setOk] = React.useState(false)
  const [loading, setLoading] = React.useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (!token.trim()) {
      setError('Укажите токен')
      return
    }
    if (password !== password2) {
      setError('Пароли не совпадают')
      return
    }
    setLoading(true)
    try {
      await fetchJson('/auth/password-reset/confirm', {
        method: 'POST',
        body: JSON.stringify({ token, new_password: password }),
      })
      setOk(true)
      setTimeout(() => nav('/login'), 800)
    } catch (err: any) {
      setError(err?.message ?? 'Ошибка')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-md mx-auto px-4 py-10">
      <div className="bg-white rounded-card shadow-card p-5">
        <h1 className="text-2xl font-semibold">Смена пароля</h1>

        <form className="mt-4 space-y-3" onSubmit={onSubmit}>
          <div>
            <div className="text-xs text-muted mb-1">Токен</div>
            <textarea value={token} onChange={(e) => setToken(e.target.value)} className="w-full rounded-xl border border-black/10 px-3 py-2 min-h-[70px]" />
          </div>
          <div>
            <div className="text-xs text-muted mb-1">Новый пароль</div>
            <input value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-xl border border-black/10 px-3 py-2" type="password" required minLength={8} />
          </div>
          <div>
            <div className="text-xs text-muted mb-1">Повторите пароль</div>
            <input value={password2} onChange={(e) => setPassword2(e.target.value)} className="w-full rounded-xl border border-black/10 px-3 py-2" type="password" required minLength={8} />
          </div>

          {error ? <div className="text-sm text-red-700">{error}</div> : null}
          {ok ? <div className="text-sm text-green-700">Пароль изменён. Перенаправляю...</div> : null}

          <button disabled={loading} className="w-full px-4 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium">
            {loading ? 'Сохраняю…' : 'Сменить пароль'}
          </button>
        </form>

        <div className="mt-4 text-sm text-muted">
          <Link to="/login" className="hover:underline">← Назад ко входу</Link>
        </div>
      </div>
    </main>
  )
}

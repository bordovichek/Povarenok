import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/lib/auth'
import { SearchIcon, UserIcon } from './Icons'

export default function Header() {
  const { user, loading, logout } = useAuth()
  const nav = useNavigate()

  return (
    <header className="sticky top-0 z-40 backdrop-blur bg-warmbg/80 border-b border-black/5">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-3">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-2xl bg-warm shadow-card flex items-center justify-center font-bold">🍲</div>
          <div>
            <div className="font-semibold leading-tight">Умная книга рецептов</div>
            <div className="text-xs text-muted">подбор по продуктам и критериям</div>
          </div>
        </Link>

        <div className="flex items-center gap-2">
          <Link to="/" className="hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl bg-white shadow-card">
            <SearchIcon className="w-4 h-4 text-muted" />
            <span className="text-sm">Поиск</span>
          </Link>

          {loading ? null : user ? (
            <>
              <Link to="/profile" className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white shadow-card">
                <UserIcon className="w-4 h-4 text-muted" />
                <span className="text-sm">ЛК</span>
              </Link>
              <button
                onClick={async () => {
                  await logout()
                  nav('/')
                }}
                className="px-3 py-2 rounded-xl bg-white shadow-card text-sm"
              >
                Выход
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="px-3 py-2 rounded-xl bg-white shadow-card text-sm">
                Войти
              </Link>
              <Link to="/register" className="px-3 py-2 rounded-xl bg-warm hover:bg-warm2 text-ink font-medium text-sm">
                Регистрация
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

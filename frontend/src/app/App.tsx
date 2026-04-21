import React from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import Header from '@/components/Header'
import { AuthProvider, useAuth } from '@/lib/auth'
import HomePage from './pages/HomePage'
import RecipePage from './pages/RecipePage'
import CookingPage from './pages/CookingPage'
import ProfilePage from './pages/ProfilePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ResetRequestPage from './pages/ResetRequestPage'
import ResetConfirmPage from './pages/ResetConfirmPage'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="max-w-6xl mx-auto px-4 py-10">Загрузка...</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen">
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/recipes/:id" element={<RecipePage />} />
          <Route
            path="/cook/:sessionId"
            element={
              <RequireAuth>
                <CookingPage />
              </RequireAuth>
            }
          />
          <Route
            path="/profile"
            element={
              <RequireAuth>
                <ProfilePage />
              </RequireAuth>
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/reset" element={<ResetRequestPage />} />
          <Route path="/reset/confirm" element={<ResetConfirmPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <footer className="max-w-6xl mx-auto px-4 py-10 text-xs text-muted">
          © 2026 • Демонстрационный проект. Нейро-генерация шагов реализована эвристически, опционально можно подключить LLM.
        </footer>
      </div>
    </AuthProvider>
  )
}

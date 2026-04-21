import React from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { fetchJson } from '@/lib/api'
import { useAuth } from '@/lib/auth'

type Session = { id: number; recipe_id: number; current_step: number; is_finished: boolean }

type RecipeDetail = {
  id: number
  title: string
  steps: string[]
}

type Personalized = {
  recipe_id: number
  title: string
  steps: string[]
  shopping_list: string[]
  notes: string[]
}

export default function CookingPage() {
  const { sessionId } = useParams()
  const sid = Number(sessionId)
  const { user, refresh } = useAuth()
  const nav = useNavigate()
  const [session, setSession] = React.useState<Session | null>(null)
  const [recipe, setRecipe] = React.useState<RecipeDetail | null>(null)
  const [personalized, setPersonalized] = React.useState<Personalized | null>(null)
  const [step, setStep] = React.useState(0)
  const [rating, setRating] = React.useState(5)
  const [comment, setComment] = React.useState('')
  const [done, setDone] = React.useState(false)
  const [fav, setFav] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    void (async () => {
      try {
        const s = await fetchJson<Session>(`/cook/sessions/${sid}`)
        setSession(s)
        setStep(s.current_step)
        const r = await fetchJson<RecipeDetail>(`/recipes/${s.recipe_id}`)
        setRecipe(r)

        // Personalized steps (if we have ingredient list)
        let ingredients: string[] = []
        try {
          const saved = localStorage.getItem('sc_ingredients')
          ingredients = saved ? (JSON.parse(saved) as string[]) : []
        } catch {
          ingredients = []
        }

        if (ingredients.length) {
          try {
            const p = await fetchJson<Personalized>(`/recipes/${s.recipe_id}/personalize`, {
              method: 'POST',
              body: JSON.stringify({
                ingredients,
                only_owned: false,
                user_constraints: user?.profile_constraints ?? '',
                limit: 1,
              }),
            })
            setPersonalized(p)
          } catch {
            setPersonalized(null)
          }
        }

        if (s.is_finished) {
          setDone(true)
        }
      } catch (e: any) {
        setError(e?.message ?? 'Не удалось загрузить сессию')
      }
    })()
  }, [sid])

  async function setProgress(next: number) {
    setStep(next)
    try {
      await fetchJson<Session>(`/cook/sessions/${sid}`, {
        method: 'PUT',
        body: JSON.stringify({ current_step: next }),
      })
    } catch {
      // ignore transient
    }
  }

  const steps = personalized?.steps ?? recipe?.steps ?? []

  async function finish() {
    setError(null)
    try {
      await fetchJson(`/cook/sessions/${sid}/finish`, {
        method: 'POST',
        body: JSON.stringify({ rating, comment }),
      })
      setDone(true)
      await refresh()
    } catch (e: any) {
      setError(e?.message ?? 'Не удалось завершить')
    }
  }

  async function toggleFavorite() {
    if (!session) return
    try {
      const r = await fetchJson<{ recipe_id: number; is_favorite: boolean }>(`/cook/favorites/${session.recipe_id}`, {
        method: 'POST',
      })
      setFav(r.is_favorite)
    } catch (e: any) {
      setError(e?.message ?? 'Не удалось обновить избранное')
    }
  }

  if (error) return <main className="max-w-6xl mx-auto px-4 py-10">{error}</main>
  if (!session || !recipe) return <main className="max-w-6xl mx-auto px-4 py-10">Загрузка…</main>

  return (
    <main className="max-w-6xl mx-auto px-4 py-6 space-y-4">
      <div className="text-sm text-muted flex items-center justify-between">
        <Link to={`/recipes/${session.recipe_id}`} className="hover:underline">← К рецепту</Link>
        <button onClick={() => nav('/profile')} className="hover:underline">Личный кабинет</button>
      </div>

      <div className="bg-white rounded-card shadow-card p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-xs text-muted">Готовим</div>
            <h1 className="text-2xl font-semibold">{recipe.title}</h1>
          </div>
          <div className="text-sm text-muted">Шаг {Math.min(step + 1, steps.length)} / {steps.length}</div>
        </div>

        {personalized?.shopping_list?.length ? (
          <div className="mt-3 bg-warmbg rounded-xl p-3">
            <div className="text-sm font-semibold">Что докупить</div>
            <div className="text-sm text-muted mt-1">{personalized.shopping_list.join(', ')}</div>
          </div>
        ) : null}

        {personalized?.notes?.length ? (
          <div className="mt-3 text-sm text-muted">
            Учтено: {personalized.notes.join(' • ')}
          </div>
        ) : null}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.2fr,0.8fr]">
        <div className="bg-white rounded-card shadow-card p-4">
          <div className="font-semibold">Текущий шаг</div>
          <div className="mt-2 text-ink leading-relaxed">{steps[step] ?? '—'}</div>

          <div className="mt-4 flex gap-2">
            <button
              className="px-4 py-2 rounded-xl bg-warmbg hover:bg-warm"
              onClick={() => setProgress(Math.max(0, step - 1))}
              disabled={done || step <= 0}
            >
              Назад
            </button>
            <button
              className="px-4 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium"
              onClick={() => setProgress(Math.min(steps.length - 1, step + 1))}
              disabled={done || step >= steps.length - 1}
            >
              Дальше
            </button>
            <button
              className="ml-auto px-4 py-2 rounded-xl bg-white border border-black/10 hover:bg-warmbg"
              onClick={() => setProgress(step)}
              disabled={done}
              title="Сохраняет прогресс (если соединение пропадало)"
            >
              Сохранить
            </button>
          </div>

          {done ? (
            <div className="mt-4 bg-warmbg rounded-xl p-3">
              <div className="font-semibold">Готово! 🎉</div>
              <div className="text-sm text-muted mt-1">Оцените блюдо и добавьте в избранное (по желанию).</div>
              <div className="mt-3 flex flex-wrap gap-2 items-center">
                <label className="text-sm">
                  Оценка:{' '}
                  <select value={rating} onChange={(e) => setRating(Number(e.target.value))} className="ml-2 border border-black/10 rounded-lg px-2 py-1">
                    {[5, 4, 3, 2, 1].map((v) => (
                      <option key={v} value={v}>{v}</option>
                    ))}
                  </select>
                </label>
                <button
                  onClick={toggleFavorite}
                  className="px-4 py-2 rounded-xl bg-white border border-black/10 hover:bg-warm"
                >
                  {fav ? 'Убрать из избранного' : 'В избранное'}
                </button>
              </div>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Комментарий (необязательно)"
                className="mt-3 w-full rounded-xl border border-black/10 px-3 py-2 min-h-[90px]"
              />
            </div>
          ) : (
            <div className="mt-4">
              <div className="font-semibold">Завершить готовку</div>
              <div className="text-sm text-muted mt-1">Когда закончите — поставьте оценку.</div>
              <div className="mt-2 flex gap-2 items-center">
                <select value={rating} onChange={(e) => setRating(Number(e.target.value))} className="border border-black/10 rounded-lg px-2 py-2">
                  {[5, 4, 3, 2, 1].map((v) => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>
                <button
                  onClick={finish}
                  className="px-4 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium"
                >
                  Завершить
                </button>
              </div>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Комментарий (необязательно)"
                className="mt-3 w-full rounded-xl border border-black/10 px-3 py-2 min-h-[90px]"
              />
            </div>
          )}

          {error ? <div className="mt-3 text-sm text-red-700">{error}</div> : null}
        </div>

        <aside className="bg-white rounded-card shadow-card p-4">
          <div className="font-semibold">Все шаги</div>
          <ol className="mt-2 space-y-2">
            {steps.map((s, idx) => (
              <li key={idx} className={`text-sm p-2 rounded-xl border border-black/5 ${idx === step ? 'bg-warmbg' : 'bg-white'}`}>
                <button
                  className="text-left"
                  onClick={() => setProgress(idx)}
                  disabled={done}
                  title="Перейти к шагу"
                >
                  <span className="text-muted">{idx + 1}. </span>{s}
                </button>
              </li>
            ))}
          </ol>
        </aside>
      </div>
    </main>
  )
}

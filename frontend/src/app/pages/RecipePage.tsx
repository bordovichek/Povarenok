import React from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { API_BASE, fetchJson } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import IngredientInput from '@/components/IngredientInput'

type Ingredient = { name: string; quantity: number; unit: string }

type RecipeDetail = {
  id: number
  title: string
  meal_type: string
  time_minutes: number
  difficulty: string
  kcal: number
  protein_g: number
  fat_g: number
  carbs_g: number
  ingredients: Ingredient[]
  steps: string[]
}

type Personalized = {
  recipe_id: number
  title: string
  steps: string[]
  shopping_list: string[]
  notes: string[]
}

export default function RecipePage() {
  const { id } = useParams()
  const recipeId = Number(id)
  const { user } = useAuth()
  const nav = useNavigate()
  const [detail, setDetail] = React.useState<RecipeDetail | null>(null)
  const [ingredients, setIngredients] = React.useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('sc_ingredients')
      return saved ? (JSON.parse(saved) as string[]) : []
    } catch {
      return []
    }
  })
  const [constraints, setConstraints] = React.useState<string>('')
  const [personalized, setPersonalized] = React.useState<Personalized | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    void (async () => {
      try {
        const d = await fetchJson<RecipeDetail>(`/recipes/${recipeId}`)
        setDetail(d)
      } catch (e: any) {
        setError(e?.message ?? 'Не удалось загрузить рецепт')
      }
    })()
  }, [recipeId])

  React.useEffect(() => {
    if (user) setConstraints(user.profile_constraints || '')
  }, [user])

  async function personalize() {
    if (!user) {
      setError('Персонализация доступна после входа')
      return
    }
    if (!ingredients.length) {
      setError('Добавьте хотя бы 1 продукт (сверху).')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const payload = {
        ingredients,
        only_owned: false,
        user_constraints: constraints,
        limit: 1,
      }
      const p = await fetchJson<Personalized>(`/recipes/${recipeId}/personalize`, {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      setPersonalized(p)
    } catch (e: any) {
      setError(e?.message ?? 'Ошибка персонализации')
    } finally {
      setLoading(false)
    }
  }

  async function startCooking() {
    if (!user) {
      nav('/login')
      return
    }
    try {
      const s = await fetchJson<{ id: number }>(`/cook/start`, {
        method: 'POST',
        body: JSON.stringify({ recipe_id: recipeId }),
      })
      nav(`/cook/${s.id}`)
    } catch (e: any) {
      setError(e?.message ?? 'Не удалось начать готовку')
    }
  }

  if (!detail) {
    return <main className="max-w-6xl mx-auto px-4 py-10">{error ?? 'Загрузка…'}</main>
  }

  const steps = personalized?.steps ?? detail.steps

  return (
    <main className="max-w-6xl mx-auto px-4 py-6 space-y-5">
      <div className="text-sm text-muted">
        <Link to="/" className="hover:underline">← На главную</Link>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.2fr,0.8fr]">
        <div className="bg-white rounded-card shadow-card overflow-hidden">
          <div className="aspect-[16/9] bg-warmbg">
            <img
              src={`${API_BASE}/recipes/${detail.id}/image`}
              alt={detail.title}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="p-4">
            <h1 className="text-2xl font-semibold">{detail.title}</h1>
            <div className="mt-2 text-sm text-muted">
              {detail.time_minutes} мин • {detail.kcal} ккал • Б {Math.round(detail.protein_g)} / Ж {Math.round(detail.fat_g)} / У {Math.round(detail.carbs_g)}
            </div>

            <div className="mt-4">
              <div className="font-semibold">Ингредиенты</div>
              <ul className="mt-2 text-sm text-muted list-disc pl-5 space-y-1">
                {detail.ingredients.map((i) => (
                  <li key={i.name}>
                    {i.name} — {i.quantity} {i.unit}
                  </li>
                ))}
              </ul>
            </div>

            <div className="mt-4">
              <div className="font-semibold">Шаги</div>
              <ol className="mt-2 space-y-2">
                {steps.map((s, idx) => (
                  <li key={idx} className="flex gap-3">
                    <div className="w-7 h-7 rounded-full bg-warmbg flex items-center justify-center text-sm">{idx + 1}</div>
                    <div className="text-sm text-ink leading-relaxed">{s}</div>
                  </li>
                ))}
              </ol>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              <button
                onClick={startCooking}
                className="px-4 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium"
              >
                Начать готовку
              </button>
              {user ? (
                <button
                  onClick={personalize}
                  className="px-4 py-2 rounded-xl bg-white border border-black/10 hover:bg-warmbg"
                  disabled={loading}
                >
                  {loading ? 'Персонализирую…' : 'Персонализировать шаги'}
                </button>
              ) : (
                <Link to="/login" className="px-4 py-2 rounded-xl bg-white border border-black/10 hover:bg-warmbg">
                  Войти для персонализации
                </Link>
              )}
            </div>

            {error ? <div className="mt-3 text-sm text-red-700">{error}</div> : null}

            {personalized?.notes?.length ? (
              <div className="mt-4 bg-warmbg rounded-xl p-3">
                <div className="font-semibold text-sm">Учтённые особенности</div>
                <ul className="mt-1 text-sm text-muted list-disc pl-5 space-y-1">
                  {personalized.notes.map((n, idx) => (
                    <li key={idx}>{n}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            {personalized?.shopping_list?.length ? (
              <div className="mt-3 bg-white border border-black/10 rounded-xl p-3">
                <div className="font-semibold text-sm">Список докупить</div>
                <div className="mt-1 text-sm text-muted">{personalized.shopping_list.join(', ')}</div>
              </div>
            ) : null}
          </div>
        </div>

        <aside className="space-y-4">
          <div>
            <div className="text-sm text-muted mb-2">Ваши продукты (для персонализации)</div>
            <IngredientInput value={ingredients} onChange={(next) => {
              setIngredients(next)
              try { localStorage.setItem('sc_ingredients', JSON.stringify(next)) } catch {}
            }} />
          </div>

          <div className="bg-white rounded-card shadow-card p-4">
            <div className="font-semibold">Особенности / ограничения</div>
            <div className="text-xs text-muted mt-1">Например: «нет кастрюли более чем на 3 литра», «нет духовки».</div>
            <textarea
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              className="mt-3 w-full rounded-xl border border-black/10 px-3 py-2 min-h-[120px]"
              placeholder="Опишите ограничения"
            />
            <button
              onClick={personalize}
              className="mt-3 w-full px-4 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium"
              disabled={!user || loading}
              title={!user ? 'Войдите, чтобы использовать персонализацию' : undefined}
            >
              {loading ? 'Персонализирую…' : 'Применить к рецепту'}
            </button>
          </div>
        </aside>
      </div>
    </main>
  )
}

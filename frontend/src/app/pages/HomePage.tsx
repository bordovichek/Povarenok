import React from 'react'
import IngredientInput from '@/components/IngredientInput'
import RecipeCardView, { type RecipeCard } from '@/components/RecipeCard'
import { fetchJson } from '@/lib/api'
import { useAuth } from '@/lib/auth'

type Popular = Record<string, RecipeCard[]>

type SearchResult = {
  recipe: RecipeCard
  score: number
  missing_ingredients: string[]
}

export default function HomePage() {
  const { user } = useAuth()
  const [popular, setPopular] = React.useState<Popular | null>(null)
  const [ingredients, setIngredients] = React.useState<string[]>(() => {
    try {
      const saved = localStorage.getItem("sc_ingredients")
      return saved ? (JSON.parse(saved) as string[]) : []
    } catch {
      return []
    }
  })
  const [onlyOwned, setOnlyOwned] = React.useState(false)
  const [mealType, setMealType] = React.useState<string | ''>('')
  const [maxTime, setMaxTime] = React.useState<number | ''>('')
  const [maxKcal, setMaxKcal] = React.useState<number | ''>('')
  const [difficulty, setDifficulty] = React.useState<string | ''>('')
  const [advancedOpen, setAdvancedOpen] = React.useState(false)
  const [results, setResults] = React.useState<SearchResult[] | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    try { localStorage.setItem("sc_ingredients", JSON.stringify(ingredients)) } catch {}
  }, [ingredients])

  React.useEffect(() => {
    void (async () => {
      try {
        const data = await fetchJson<Popular>('/recipes/popular')
        setPopular(data)
      } catch {
        setPopular(null)
      }
    })()
  }, [])

  async function fillFromPantry() {
    setError(null)
    try {
      const items = await fetchJson<Array<{ name: string }>>('/pantry/')
      const names = items.map((i) => i.name).slice(0, 40)
      setIngredients(names)
    } catch {
      setError('Не удалось загрузить список продуктов. Войдите в аккаунт и добавьте продукты в ЛК.')
    }
  }

  async function doSearch() {
    setError(null)
    if (ingredients.length === 0) {
      setError('Добавьте хотя бы 1 продукт.')
      return
    }
    setLoading(true)
    try {
      const payload: any = {
        ingredients,
        only_owned: onlyOwned,
        limit: 12,
      }
      if (mealType) payload.meal_type = mealType
      if (maxTime !== '') payload.max_time_minutes = Number(maxTime)
      if (maxKcal !== '') payload.max_kcal = Number(maxKcal)
      if (difficulty) payload.difficulty = difficulty

      const res = await fetchJson<SearchResult[]>('/recipes/search', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      setResults(res)
    } catch (e: any) {
      setError(e?.message ?? 'Ошибка поиска')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-6">
      <div className="grid gap-6 lg:grid-cols-[1.15fr,0.85fr]">
        <div className="space-y-4">
          <h1 className="text-2xl font-semibold">Подбор рецептов по продуктам</h1>

          <IngredientInput value={ingredients} onChange={setIngredients} />

          <div className="bg-white rounded-card shadow-card p-3">
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={onlyOwned}
                  onChange={(e) => setOnlyOwned(e.target.checked)}
                />
                Не докупать продукты
              </label>

              {user ? (
                <button
                  type="button"
                  onClick={fillFromPantry}
                  className="px-3 py-2 rounded-xl bg-warmbg hover:bg-warm text-sm"
                >
                  Подставить из моего списка
                </button>
              ) : null}

              <button
                type="button"
                onClick={() => setAdvancedOpen((v) => !v)}
                className="px-3 py-2 rounded-xl bg-warmbg hover:bg-warm text-sm"
              >
                {advancedOpen ? 'Скрыть критерии' : 'Критерии поиска'}
              </button>

              <button
                type="button"
                onClick={doSearch}
                className="px-4 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium"
                disabled={loading}
              >
                {loading ? 'Ищу…' : 'Найти'}
              </button>
            </div>

            {advancedOpen ? (
              <div className="mt-4 grid sm:grid-cols-2 gap-3">
                <div>
                  <div className="text-xs text-muted mb-1">Тип блюда</div>
                  <select
                    value={mealType}
                    onChange={(e) => setMealType(e.target.value)}
                    className="w-full rounded-xl border border-black/10 px-3 py-2"
                  >
                    <option value="">Любой</option>
                    <option value="breakfast">Завтрак</option>
                    <option value="lunch">Обед</option>
                    <option value="dinner">Ужин</option>
                    <option value="any">Другое</option>
                  </select>
                </div>

                <div>
                  <div className="text-xs text-muted mb-1">Сложность</div>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full rounded-xl border border-black/10 px-3 py-2"
                  >
                    <option value="">Любая</option>
                    <option value="easy">Лёгкая</option>
                    <option value="medium">Средняя</option>
                    <option value="hard">Сложная</option>
                  </select>
                </div>

                <div>
                  <div className="text-xs text-muted mb-1">Время приготовления (мин, максимум)</div>
                  <input
                    type="number"
                    value={maxTime}
                    onChange={(e) => setMaxTime(e.target.value === '' ? '' : Number(e.target.value))}
                    className="w-full rounded-xl border border-black/10 px-3 py-2"
                    placeholder="например, 30"
                    min={5}
                    max={240}
                  />
                </div>

                <div>
                  <div className="text-xs text-muted mb-1">Ккал (максимум)</div>
                  <input
                    type="number"
                    value={maxKcal}
                    onChange={(e) => setMaxKcal(e.target.value === '' ? '' : Number(e.target.value))}
                    className="w-full rounded-xl border border-black/10 px-3 py-2"
                    placeholder="например, 550"
                    min={100}
                    max={2000}
                  />
                </div>
              </div>
            ) : null}

            {error ? <div className="mt-3 text-sm text-red-700">{error}</div> : null}
          </div>

          {results ? (
            <section className="space-y-3">
              <div className="flex items-baseline justify-between">
                <h2 className="text-xl font-semibold">Подходящие рецепты</h2>
                <div className="text-xs text-muted">найдено: {results.length}</div>
              </div>

              {results.length === 0 ? (
                <div className="text-sm text-muted">Ничего не найдено. Попробуйте снять ограничения.</div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {results.map((r) => (
                    <RecipeCardView
                      key={r.recipe.id}
                      recipe={r.recipe}
                      hint={
                        r.missing_ingredients.length
                          ? `Нужно докупить: ${r.missing_ingredients.slice(0, 4).join(', ')}${r.missing_ingredients.length > 4 ? '…' : ''}`
                          : 'Все ингредиенты есть'
                      }
                    />
                  ))}
                </div>
              )}
            </section>
          ) : null}
        </div>

        <aside className="space-y-6">
          <div className="bg-white rounded-card shadow-card p-4">
            <div className="font-semibold">Как это работает</div>
            <ol className="mt-2 text-sm text-muted list-decimal pl-5 space-y-1">
              <li>Добавьте продукты, которые есть дома.</li>
              <li>Укажите критерии (время, калории, сложность) — по желанию.</li>
              <li>Система подберёт рецепты и покажет список недостающего.</li>
              <li>Откройте рецепт → пошаговая готовка → оценка → избранное.</li>
            </ol>
          </div>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold">Популярное</h2>
            {popular ? (
              <div className="space-y-4">
                {(
                  [
                    ['breakfast', 'Завтрак'],
                    ['lunch', 'Обед'],
                    ['dinner', 'Ужин'],
                    ['any', 'Другое'],
                  ] as const
                ).map(([key, title]) => (
                  <div key={key}>
                    <div className="text-sm text-muted mb-2">{title}</div>
                    <div className="grid grid-cols-2 gap-3">
                      {(popular[key] ?? []).slice(0, 4).map((r) => (
                        <RecipeCardView key={r.id} recipe={r} />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted">Популярные рецепты пока не загрузились.</div>
            )}
          </section>
        </aside>
      </div>
    </main>
  )
}

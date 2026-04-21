import React from 'react'
import { Link } from 'react-router-dom'
import { fetchJson } from '@/lib/api'
import { useAuth } from '@/lib/auth'

type PantryItem = { id: number; name: string; category: string; quantity: number; unit: string }
type HistoryItem = {
  session_id: number
  recipe_id: number
  recipe_title: string
  started_at: string
  finished_at: string | null
  is_finished: boolean
}
type ReviewItem = {
  recipe_id: number
  recipe_title: string
  rating: number
  comment: string
  created_at: string
}
type FavoriteItem = { recipe_id: number; recipe_title: string; created_at: string }

type Tab = 'pantry' | 'history' | 'favorites' | 'reviews' | 'settings'

export default function ProfilePage() {
  const { user, refresh } = useAuth()
  const [tab, setTab] = React.useState<Tab>('pantry')
  const [error, setError] = React.useState<string | null>(null)

  // pantry state
  const [pantry, setPantry] = React.useState<PantryItem[]>([])
  const [newItem, setNewItem] = React.useState({ name: '', category: '', quantity: 0, unit: '' })

  // other lists
  const [history, setHistory] = React.useState<HistoryItem[]>([])
  const [favorites, setFavorites] = React.useState<FavoriteItem[]>([])
  const [reviews, setReviews] = React.useState<ReviewItem[]>([])

  const [constraints, setConstraints] = React.useState(user?.profile_constraints ?? '')

  React.useEffect(() => {
    setConstraints(user?.profile_constraints ?? '')
  }, [user])

  async function loadAll() {
    setError(null)
    try {
      const [p, h, f, r] = await Promise.all([
        fetchJson<PantryItem[]>('/pantry/'),
        fetchJson<HistoryItem[]>('/users/me/history'),
        fetchJson<FavoriteItem[]>('/users/me/favorites'),
        fetchJson<ReviewItem[]>('/users/me/reviews'),
      ])
      setPantry(p)
      setHistory(h)
      setFavorites(f)
      setReviews(r)
    } catch (e: any) {
      setError(e?.message ?? 'Не удалось загрузить данные ЛК')
    }
  }

  React.useEffect(() => {
    void loadAll()
  }, [])

  async function addPantry() {
    setError(null)
    if (!newItem.name.trim()) {
      setError('Введите название продукта')
      return
    }
    try {
      const created = await fetchJson<PantryItem>('/pantry/', {
        method: 'POST',
        body: JSON.stringify({
          name: newItem.name,
          category: newItem.category,
          quantity: newItem.quantity,
          unit: newItem.unit,
        }),
      })
      setPantry((prev) => [...prev, created].sort((a, b) => a.name.localeCompare(b.name)))
      setNewItem({ name: '', category: '', quantity: 0, unit: '' })
    } catch (e: any) {
      setError(e?.message ?? 'Не удалось добавить продукт')
    }
  }

  async function updatePantry(item: PantryItem) {
    setError(null)
    try {
      const updated = await fetchJson<PantryItem>(`/pantry/${item.id}`, {
        method: 'PUT',
        body: JSON.stringify(item),
      })
      setPantry((prev) => prev.map((p) => (p.id === item.id ? updated : p)))
    } catch (e: any) {
      setError(e?.message ?? 'Не удалось обновить')
    }
  }

  async function delPantry(id: number) {
    setError(null)
    try {
      await fetchJson<void>(`/pantry/${id}`, { method: 'DELETE' })
      setPantry((prev) => prev.filter((p) => p.id !== id))
    } catch (e: any) {
      setError(e?.message ?? 'Не удалось удалить')
    }
  }

  async function saveConstraints() {
    setError(null)
    try {
      await fetchJson('/users/me', {
        method: 'PUT',
        body: JSON.stringify({ profile_constraints: constraints }),
      })
      await refresh()
    } catch (e: any) {
      setError(e?.message ?? 'Не удалось сохранить')
    }
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-6 space-y-4">
      <div className="flex items-baseline justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold">Личный кабинет</h1>
          <div className="text-sm text-muted">{user?.email}</div>
        </div>
        <Link to="/" className="text-sm text-muted hover:underline">← На главную</Link>
      </div>

      <div className="bg-white rounded-card shadow-card p-2 flex flex-wrap gap-2">
        {([
          ['pantry', 'Продукты'],
          ['history', 'История'],
          ['favorites', 'Избранное'],
          ['reviews', 'Отзывы'],
          ['settings', 'Настройки'],
        ] as const).map(([k, label]) => (
          <button
            key={k}
            onClick={() => setTab(k)}
            className={`px-3 py-2 rounded-xl text-sm ${tab === k ? 'bg-warm font-medium' : 'bg-warmbg hover:bg-warm'}`}
          >
            {label}
          </button>
        ))}
      </div>

      {error ? <div className="text-sm text-red-700">{error}</div> : null}

      {tab === 'pantry' ? (
        <section className="grid gap-4 lg:grid-cols-[1fr,1fr]">
          <div className="bg-white rounded-card shadow-card p-4">
            <div className="font-semibold">Добавить продукт</div>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <input
                value={newItem.name}
                onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                className="col-span-2 rounded-xl border border-black/10 px-3 py-2"
                placeholder="Например: яйца"
              />
              <input
                value={newItem.category}
                onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                className="rounded-xl border border-black/10 px-3 py-2"
                placeholder="Категория"
              />
              <input
                value={newItem.unit}
                onChange={(e) => setNewItem({ ...newItem, unit: e.target.value })}
                className="rounded-xl border border-black/10 px-3 py-2"
                placeholder="Ед. изм. (шт, г, мл)"
              />
              <input
                type="number"
                value={newItem.quantity}
                onChange={(e) => setNewItem({ ...newItem, quantity: Number(e.target.value) })}
                className="rounded-xl border border-black/10 px-3 py-2"
                placeholder="Количество"
                min={0}
              />
              <button
                onClick={addPantry}
                className="rounded-xl bg-warm hover:bg-warm2 font-medium"
              >
                Добавить
              </button>
            </div>
          </div>

          <div className="bg-white rounded-card shadow-card p-4">
            <div className="font-semibold">Мои продукты ({pantry.length})</div>
            <div className="mt-3 space-y-2 max-h-[520px] overflow-auto pr-1">
              {pantry.map((p) => (
                <PantryRow key={p.id} item={p} onUpdate={updatePantry} onDelete={delPantry} />
              ))}
            </div>
          </div>
        </section>
      ) : null}

      {tab === 'history' ? (
        <section className="bg-white rounded-card shadow-card p-4">
          <div className="font-semibold">История приготовлений</div>
          <div className="mt-3 space-y-2">
            {history.length === 0 ? <div className="text-sm text-muted">Пока пусто.</div> : null}
            {history.map((h) => (
              <div key={h.session_id} className="p-3 rounded-xl border border-black/5">
                <div className="flex items-center justify-between gap-3 flex-wrap">
                  <Link to={`/recipes/${h.recipe_id}`} className="font-medium hover:underline">
                    {h.recipe_title || `Рецепт #${h.recipe_id}`}
                  </Link>
                  <div className={`text-xs px-2 py-1 rounded-full ${h.is_finished ? 'bg-warmbg' : 'bg-white border border-black/10'}`}>
                    {h.is_finished ? 'Завершено' : 'В процессе'}
                  </div>
                </div>
                <div className="text-xs text-muted mt-1">
                  Начато: {new Date(h.started_at).toLocaleString()}{h.finished_at ? ` • Готово: ${new Date(h.finished_at).toLocaleString()}` : ''}
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {tab === 'favorites' ? (
        <section className="bg-white rounded-card shadow-card p-4">
          <div className="font-semibold">Избранное</div>
          <div className="mt-3 space-y-2">
            {favorites.length === 0 ? <div className="text-sm text-muted">Пока пусто (в избранное можно добавить только приготовленные блюда).</div> : null}
            {favorites.map((f) => (
              <div key={f.recipe_id} className="p-3 rounded-xl border border-black/5 flex items-center justify-between">
                <Link to={`/recipes/${f.recipe_id}`} className="hover:underline font-medium">
                  {f.recipe_title || `Рецепт #${f.recipe_id}`}
                </Link>
                <div className="text-xs text-muted">{new Date(f.created_at).toLocaleDateString()}</div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {tab === 'reviews' ? (
        <section className="bg-white rounded-card shadow-card p-4">
          <div className="font-semibold">Отзывы</div>
          <div className="mt-3 space-y-2">
            {reviews.length === 0 ? <div className="text-sm text-muted">Пока нет отзывов.</div> : null}
            {reviews.map((r) => (
              <div key={r.recipe_id} className="p-3 rounded-xl border border-black/5">
                <div className="flex items-center justify-between gap-3 flex-wrap">
                  <Link to={`/recipes/${r.recipe_id}`} className="font-medium hover:underline">
                    {r.recipe_title || `Рецепт #${r.recipe_id}`}
                  </Link>
                  <div className="text-xs">Оценка: <span className="font-semibold">{r.rating}/5</span></div>
                </div>
                {r.comment ? <div className="text-sm text-muted mt-2">{r.comment}</div> : null}
                <div className="text-xs text-muted mt-2">{new Date(r.created_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {tab === 'settings' ? (
        <section className="bg-white rounded-card shadow-card p-4">
          <div className="font-semibold">Особенности / ограничения</div>
          <div className="text-xs text-muted mt-1">
            Это будет автоматически подставляться в персонализацию рецептов.
          </div>
          <textarea
            value={constraints}
            onChange={(e) => setConstraints(e.target.value)}
            className="mt-3 w-full rounded-xl border border-black/10 px-3 py-2 min-h-[160px]"
            placeholder="Например: нет кастрюли более чем на 3 литра"
          />
          <button onClick={saveConstraints} className="mt-3 px-4 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium">
            Сохранить
          </button>
        </section>
      ) : null}
    </main>
  )
}

function PantryRow({
  item,
  onUpdate,
  onDelete,
}: {
  item: PantryItem
  onUpdate: (next: PantryItem) => void
  onDelete: (id: number) => void
}) {
  const [editing, setEditing] = React.useState(false)
  const [draft, setDraft] = React.useState<PantryItem>(item)

  React.useEffect(() => setDraft(item), [item])

  return (
    <div className="p-3 rounded-xl border border-black/5">
      {editing ? (
        <div className="grid grid-cols-2 gap-2">
          <input value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} className="col-span-2 rounded-xl border border-black/10 px-3 py-2" />
          <input value={draft.category} onChange={(e) => setDraft({ ...draft, category: e.target.value })} className="rounded-xl border border-black/10 px-3 py-2" placeholder="Категория" />
          <input value={draft.unit} onChange={(e) => setDraft({ ...draft, unit: e.target.value })} className="rounded-xl border border-black/10 px-3 py-2" placeholder="Ед." />
          <input type="number" value={draft.quantity} onChange={(e) => setDraft({ ...draft, quantity: Number(e.target.value) })} className="rounded-xl border border-black/10 px-3 py-2" min={0} />
          <div className="flex gap-2">
            <button
              onClick={() => {
                onUpdate(draft)
                setEditing(false)
              }}
              className="px-3 py-2 rounded-xl bg-warm hover:bg-warm2 font-medium"
            >
              Сохранить
            </button>
            <button onClick={() => setEditing(false)} className="px-3 py-2 rounded-xl bg-warmbg hover:bg-warm">
              Отмена
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="font-medium capitalize">{item.name}</div>
            <div className="text-xs text-muted">
              {item.category ? `${item.category} • ` : ''}{item.quantity} {item.unit}
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setEditing(true)} className="px-3 py-2 rounded-xl bg-warmbg hover:bg-warm text-sm">
              Изменить
            </button>
            <button onClick={() => onDelete(item.id)} className="px-3 py-2 rounded-xl bg-white border border-black/10 text-sm hover:bg-warmbg">
              Удалить
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

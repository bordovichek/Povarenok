import React from 'react'

export default function IngredientInput({
  value,
  onChange,
  placeholder = 'Введите ингредиент и нажмите Enter',
}: {
  value: string[]
  onChange: (next: string[]) => void
  placeholder?: string
}) {
  const [text, setText] = React.useState('')

  function add() {
    const v = text.trim()
    if (!v) return
    if (value.some((x) => x.toLowerCase() === v.toLowerCase())) {
      setText('')
      return
    }
    onChange([...value, v])
    setText('')
  }

  return (
    <div className="bg-white rounded-card shadow-card p-3">
      <div className="flex flex-wrap gap-2">
        {value.map((ing) => (
          <button
            key={ing}
            type="button"
            className="px-2 py-1 rounded-full bg-warmbg text-sm"
            onClick={() => onChange(value.filter((x) => x !== ing))}
            title="Нажмите, чтобы удалить"
          >
            {ing} <span className="text-muted">×</span>
          </button>
        ))}
      </div>
      <div className="mt-2 flex gap-2">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              add()
            }
          }}
          className="flex-1 rounded-xl border border-black/10 px-3 py-2 outline-none focus:ring-2 focus:ring-warm"
          placeholder={placeholder}
        />
        <button
          type="button"
          onClick={add}
          className="px-4 py-2 rounded-xl bg-warm text-ink font-medium hover:bg-warm2"
        >
          Добавить
        </button>
      </div>
      <div className="mt-2 text-xs text-muted">
        Минимум 1 ингредиент. Нажмите на чип, чтобы удалить.
      </div>
    </div>
  )
}

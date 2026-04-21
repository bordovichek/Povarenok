import React from 'react'
import { Link } from 'react-router-dom'
import { API_BASE } from '@/lib/api'
import { BowlIcon, ClockIcon, DropIcon, EggIcon, WheatIcon } from './Icons'

export type RecipeCard = {
  id: number
  title: string
  meal_type: string
  time_minutes: number
  difficulty: string
  kcal: number
  protein_g: number
  fat_g: number
  carbs_g: number
}

function mealLabel(type: string) {
  switch (type) {
    case 'breakfast':
      return 'Завтрак'
    case 'lunch':
      return 'Обед'
    case 'dinner':
      return 'Ужин'
    default:
      return 'Любое'
  }
}

export default function RecipeCardView({ recipe, hint }: { recipe: RecipeCard; hint?: React.ReactNode }) {
  return (
    <Link
      to={`/recipes/${recipe.id}`}
      className="block bg-white rounded-card shadow-card overflow-hidden hover:translate-y-0.5 transition-transform"
    >
      <div className="aspect-[4/3] bg-warmbg">
        <img
          src={`${API_BASE}/recipes/${recipe.id}/image`}
          alt={recipe.title}
          className="w-full h-full object-cover"
          loading="lazy"
        />
      </div>
      <div className="p-3">
        <div className="font-semibold leading-snug min-h-[2.75rem]">{recipe.title}</div>

        <div className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-sm text-muted">
          <div className="flex items-center gap-1">
            <BowlIcon className="w-4 h-4 text-muted" />
            <span>{mealLabel(recipe.meal_type)}</span>
          </div>
          <div className="flex items-center gap-1">
            <ClockIcon className="w-4 h-4 text-muted" />
            <span>{recipe.time_minutes} мин</span>
          </div>
          <div className="flex items-center gap-1">
            <EggIcon className="w-4 h-4 text-muted" />
            <span>{Math.round(recipe.protein_g)} г</span>
          </div>
          <div className="flex items-center gap-1">
            <DropIcon className="w-4 h-4 text-muted" />
            <span>{Math.round(recipe.fat_g)} г</span>
          </div>
          <div className="flex items-center gap-1">
            <WheatIcon className="w-4 h-4 text-muted" />
            <span>{Math.round(recipe.carbs_g)} г</span>
          </div>
          <div className="text-right">
            <span className="text-ink font-medium">{recipe.kcal} ккал</span>
          </div>
        </div>

        {hint ? <div className="mt-2 text-xs text-muted">{hint}</div> : null}
      </div>
    </Link>
  )
}

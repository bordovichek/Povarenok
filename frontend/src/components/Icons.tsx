import React from 'react'

type IconProps = { className?: string }

export function ClockIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v6l4 2" />
    </svg>
  )
}

export function BowlIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 12h16" />
      <path d="M6 12c0 5 3 8 6 8s6-3 6-8" />
      <path d="M7 6c2 1 3 1 5 1s3 0 5-1" />
    </svg>
  )
}

export function EggIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3c-3.3 0-6 4.3-6 9.2C6 17.5 8.7 21 12 21s6-3.5 6-8.8C18 7.3 15.3 3 12 3z" />
      <path d="M10.5 12.2c0 1.3 1 2.3 1.5 2.3s1.5-1 1.5-2.3-1-2.3-1.5-2.3-1.5 1-1.5 2.3z" />
    </svg>
  )
}

export function DropIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2s6 6.2 6 11.2A6 6 0 1 1 6 13.2C6 8.2 12 2 12 2z" />
    </svg>
  )
}

export function WheatIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2v20" />
      <path d="M9 6c0 2 3 2 3 4" />
      <path d="M15 6c0 2-3 2-3 4" />
      <path d="M9 10c0 2 3 2 3 4" />
      <path d="M15 10c0 2-3 2-3 4" />
      <path d="M9 14c0 2 3 2 3 4" />
      <path d="M15 14c0 2-3 2-3 4" />
    </svg>
  )
}

export function SearchIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </svg>
  )
}

export function UserIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21a8 8 0 1 0-16 0" />
      <circle cx="12" cy="9" r="4" />
    </svg>
  )
}

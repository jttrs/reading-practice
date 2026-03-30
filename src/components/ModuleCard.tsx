import { Link } from 'react-router-dom'

type IconId = 'decoding' | 'sight-words'

const icons: Record<IconId, React.ReactNode> = {
  decoding: (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-indigo-400">
      <path d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" />
    </svg>
  ),
  'sight-words': (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-amber-400">
      <path d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
      <path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
    </svg>
  ),
}

interface ModuleCardProps {
  name: string
  description: string
  icon: IconId
  route: string
}

export default function ModuleCard({ name, description, icon, route }: ModuleCardProps) {
  return (
    <Link
      to={route}
      className="block rounded-3xl bg-white p-8 shadow-md transition-all duration-200 hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
    >
      <div className="mb-4">{icons[icon]}</div>
      <h2 className="mb-2 text-2xl font-bold text-stone-800">{name}</h2>
      <p className="text-lg text-stone-500">{description}</p>
    </Link>
  )
}

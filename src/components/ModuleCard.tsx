import { Link } from 'react-router-dom'

interface ModuleCardProps {
  name: string
  description: string
  icon: string
  route: string
}

export default function ModuleCard({ name, description, icon, route }: ModuleCardProps) {
  return (
    <Link
      to={route}
      className="block rounded-2xl border-2 border-gray-200 bg-white p-8 shadow-sm transition-all hover:border-blue-400 hover:shadow-md active:scale-[0.98]"
    >
      <div className="mb-4 text-5xl">{icon}</div>
      <h2 className="mb-2 text-2xl font-bold text-gray-800">{name}</h2>
      <p className="text-lg text-gray-500">{description}</p>
    </Link>
  )
}

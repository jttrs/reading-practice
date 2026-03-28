import ModuleCard from '../components/ModuleCard'

const modules = [
  {
    id: 'decoding',
    name: 'Decoding',
    description: 'Practice breaking words into spelling sounds',
    icon: '🔤',
    route: '/decoding',
  },
  {
    id: 'sight-words',
    name: 'Sight Words',
    description: 'Practice recognizing sight words',
    icon: '👁️',
    route: '/sight-words',
  },
]

export default function Landing() {
  return (
    <div className="flex min-h-screen flex-col items-center bg-gradient-to-b from-blue-50 to-white px-4 py-12">
      <h1 className="mb-2 text-4xl font-bold text-gray-800">Reading Practice</h1>
      <p className="mb-10 text-lg text-gray-500">Choose a module to start practicing</p>
      <div className="grid w-full max-w-2xl gap-6 sm:grid-cols-2">
        {modules.map((m) => (
          <ModuleCard key={m.id} {...m} />
        ))}
      </div>
    </div>
  )
}

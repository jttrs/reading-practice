import ModuleCard from '../components/ModuleCard'

const modules = [
  {
    id: 'decoding',
    name: 'Decoding',
    description: 'Practice breaking words into spelling sounds',
    icon: 'decoding' as const,
    route: '/decoding',
  },
  {
    id: 'sight-words',
    name: 'Sight Words',
    description: 'Practice recognizing sight words',
    icon: 'sight-words' as const,
    route: '/sight-words',
  },
]

export default function Landing() {
  return (
    <div className="relative flex min-h-screen flex-col items-center bg-gradient-to-b from-teal-50 to-white px-4 py-16">
      <div className="pointer-events-none absolute inset-0 dot-grid opacity-[0.04]" />
      <h1 className="mb-2 text-4xl font-bold text-stone-800">Reading Practice</h1>
      <p className="mb-12 text-lg text-stone-500">Choose a module to start practicing</p>
      <div className="grid w-full max-w-2xl gap-8 sm:grid-cols-2">
        {modules.map((m) => (
          <ModuleCard key={m.id} {...m} />
        ))}
      </div>
    </div>
  )
}

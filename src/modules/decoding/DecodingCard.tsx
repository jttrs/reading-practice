import type { DecodingWord, SpellingUnit } from './types'

interface DecodingCardProps {
  word: DecodingWord
  spellingUnit: SpellingUnit | undefined
  isRevealed: boolean
}

export default function DecodingCard({ word, spellingUnit, isRevealed }: DecodingCardProps) {
  if (!isRevealed) {
    return (
      <div className="flex flex-col items-center">
        <span className="text-7xl font-bold text-gray-800 sm:text-8xl">
          {word.word}
        </span>
        <p className="mt-6 text-lg text-gray-400">
          Click or press any key to reveal
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center">
      {/* Decoding breakdown with individual underlines */}
      <div className="flex items-end gap-3 sm:gap-5">
        {word.decodingBreakdown.map((element, i) => (
          <div key={i} className="flex flex-col items-center">
            <span className="text-5xl font-bold text-blue-700 sm:text-6xl">
              {element}
            </span>
            <div className="mt-1 h-1 w-full rounded bg-blue-400" />
          </div>
        ))}
      </div>

      {/* Full word below */}
      <p className="mt-6 text-3xl font-medium text-gray-600">
        {word.word}
      </p>

      {/* Phoneme and context */}
      {spellingUnit && (
        <div className="mt-4 text-center text-base text-gray-400">
          {spellingUnit.phoneme && (
            <p>
              <span className="font-mono">{spellingUnit.patterns.join(', ')}</span>
              {' → '}
              <span className="font-mono">{spellingUnit.phoneme}</span>
            </p>
          )}
          {spellingUnit.examples.length > 0 && (
            <p className="mt-1">
              Examples: {spellingUnit.examples.join(', ')}
            </p>
          )}
          <p className="mt-1 text-sm text-gray-300">
            from "{word.book}"
          </p>
        </div>
      )}
    </div>
  )
}

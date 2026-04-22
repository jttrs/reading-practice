import type { DecodingWord, SpellingUnit } from './types'

interface DecodingCardProps {
  word: DecodingWord
  spellingUnit: SpellingUnit | undefined
  isRevealed: boolean
}

/** Check if a breakdown element is the active spelling pattern. */
function isPatternElement(element: string, spellingUnit: SpellingUnit | undefined): boolean {
  if (!spellingUnit) return false
  if (spellingUnit.patterns.includes(element)) return true
  if (element.includes('_') && spellingUnit.patterns.includes(element)) return true
  return false
}

interface DisplayGroup {
  text: string
  isPattern: boolean
}

/**
 * Build display groups from a breakdown, keeping multi-letter patterns
 * (like "ow", "ai", "ee") as single visual units.
 *
 * Split digraphs (a_e, o_e, etc.) are an exception: the two halves display
 * separately since other letters sit between them in the word.
 */
function buildDisplayGroups(
  breakdown: string[],
  spellingUnit: SpellingUnit | undefined,
): DisplayGroup[] {
  const groups: DisplayGroup[] = []
  let pendingSplitEnd: string | null = null

  for (const element of breakdown) {
    const isPat = isPatternElement(element, spellingUnit)

    if (element.includes('_')) {
      const [first, last] = element.split('_')
      groups.push({ text: first, isPattern: true })
      pendingSplitEnd = last
    } else {
      groups.push({ text: element, isPattern: isPat })
    }
  }

  if (pendingSplitEnd) {
    groups.push({ text: pendingSplitEnd, isPattern: true })
  }

  return groups
}

export default function DecodingCard({ word, spellingUnit, isRevealed }: DecodingCardProps) {
  if (!isRevealed) {
    return (
      <div className="flex flex-col items-center">
        <span className="text-7xl font-bold text-stone-800 sm:text-8xl">
          {word.word}
        </span>
        <p className="mt-8 text-lg text-stone-400">
          Click or press any key to reveal
        </p>
      </div>
    )
  }

  const contextSection = spellingUnit && (
    <div className="mt-4 text-center text-base text-stone-400">
      {spellingUnit.phoneme && (
        <p>
          <span className="font-mono">{spellingUnit.patterns.join(', ')}</span>
          {' \u2192 '}
          <span className="font-mono">{spellingUnit.phoneme}</span>
        </p>
      )}
      {spellingUnit.examples.length > 0 && (
        <p className="mt-2">
          Examples: {spellingUnit.examples.join(', ')}
        </p>
      )}
      <p className="mt-2 text-sm text-stone-300">
        from "{word.book}"
      </p>
    </div>
  )

  const groups = buildDisplayGroups(word.decodingBreakdown, spellingUnit)

  return (
    <div className="flex flex-col items-center">
      <div className="flex items-end">
        {groups.map((g, i) => (
          <div key={i} className="flex flex-col items-center px-1 sm:px-2">
            <span className="text-5xl font-bold text-stone-800 sm:text-6xl">
              {g.text}
            </span>
            <div
              className={`mt-1 h-1 w-full rounded ${
                g.isPattern ? 'bg-teal-400' : 'bg-stone-300'
              }`}
            />
          </div>
        ))}
      </div>

      {contextSection}
    </div>
  )
}

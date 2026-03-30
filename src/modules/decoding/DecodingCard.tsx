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

/**
 * Expand a breakdown into individual letters with pattern flags.
 * For split digraphs (a_e), marks the vowel and trailing 'e' as pattern letters.
 * For regular patterns (ai, ee), marks those letters as pattern letters.
 * Individual consonants get their own letter slots.
 */
function expandToLetters(
  breakdown: string[],
  spellingUnit: SpellingUnit | undefined,
): { letter: string; isPattern: boolean }[] {
  const chars: { letter: string; isPattern: boolean }[] = []
  let pendingSplitEnd: string | null = null

  for (const element of breakdown) {
    const isPat = isPatternElement(element, spellingUnit)

    if (element.includes('_')) {
      // Split digraph: "a_e" → mark 'a' now, queue 'e' for end
      const [first, last] = element.split('_')
      for (const c of first) chars.push({ letter: c, isPattern: true })
      pendingSplitEnd = last
    } else {
      for (const c of element) chars.push({ letter: c, isPattern: isPat })
    }
  }

  // Append the split digraph's trailing letter(s)
  if (pendingSplitEnd) {
    for (const c of pendingSplitEnd) chars.push({ letter: c, isPattern: true })
  }

  return chars
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

  const chars = expandToLetters(word.decodingBreakdown, spellingUnit)

  return (
    <div className="flex flex-col items-center">
      {/* Letter-by-letter display with color-coded underlines */}
      <div className="flex items-end">
        {chars.map((ch, i) => (
          <div key={i} className="flex flex-col items-center px-1 sm:px-2">
            <span className="text-5xl font-bold text-stone-800 sm:text-6xl">
              {ch.letter}
            </span>
            <div
              className={`mt-1 h-1 w-full rounded ${
                ch.isPattern ? 'bg-teal-400' : 'bg-stone-300'
              }`}
            />
          </div>
        ))}
      </div>

      <p className="mt-8 text-3xl font-medium text-stone-600">{word.word}</p>
      {contextSection}
    </div>
  )
}

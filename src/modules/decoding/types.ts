export interface SpellingUnit {
  id: string
  patterns: string[]
  phoneme: string
  examples: string[]
  sourceEmail: string
  book: string
}

export interface DecodingWord {
  word: string
  spellingUnitId: string
  decodingBreakdown: string[]
  book: string
}

export interface SightWordData {
  word: string
  sourceEmail: string
  book: string
}

export interface DecodingData {
  spellingUnits: SpellingUnit[]
  decodingWords: DecodingWord[]
  sightWords: SightWordData[]
}

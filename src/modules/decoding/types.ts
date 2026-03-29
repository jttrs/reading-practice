export interface Phoneme {
  id: string
  ipa: string
  category: 'consonant' | 'vowel'
  tts: string
  spellings: string[]
  source: 'teacher' | 'reference'
}

export interface SpellingUnit {
  id: string
  patterns: string[]
  phoneme: string
  ipa: string
  examples: string[]
  sourceEmail: string
  book: string
}

export interface DecodingWord {
  word: string
  spellingUnitId: string
  decodingBreakdown: string[]
  ttsBreakdown: string[]
  ttsWord: string
  book: string
}

export interface SightWordData {
  word: string
  ttsWord: string
  sourceEmail: string
  book: string
}

export interface DecodingData {
  phonemes: Phoneme[]
  spellingUnits: SpellingUnit[]
  decodingWords: DecodingWord[]
  sightWords: SightWordData[]
}

import { useState, useCallback, useRef, useMemo } from 'react'
import { useProgress, type ElementStats } from './useProgress'

export type Frequency = 'off' | 'low' | 'normal' | 'high'

const FREQUENCY_MULTIPLIERS: Record<Frequency, number> = {
  off: 0,
  low: 0.3,
  normal: 1,
  high: 3,
}

const ORGANIC_FLOOR = 0.2
const RECENCY_PENALTY_MS = 30_000 // 30s

interface PracticeItem<T> {
  item: T
  elementId: string
}

function loadFrequencies(moduleId: string): Record<string, Frequency> {
  try {
    const raw = localStorage.getItem(`settings:${moduleId}:frequencies`)
    if (raw) return JSON.parse(raw)
  } catch { /* ignore */ }
  return {}
}

function saveFrequencies(moduleId: string, freqs: Record<string, Frequency>) {
  localStorage.setItem(`settings:${moduleId}:frequencies`, JSON.stringify(freqs))
}

function computeOrganicWeight(stats: ElementStats): number {
  const total = stats.correct + stats.incorrect
  if (total === 0) return 1.0

  // Error rate boosts weight; high accuracy reduces it
  const errorRate = stats.incorrect / total
  // Scale: 0 errors → 0.2 (floor), all errors → 2.0
  const weight = ORGANIC_FLOOR + (1.8 * errorRate)

  // Recency penalty: if seen very recently, slightly reduce
  if (stats.lastSeen) {
    const elapsed = Date.now() - new Date(stats.lastSeen).getTime()
    if (elapsed < RECENCY_PENALTY_MS) {
      return weight * 0.5
    }
  }

  return weight
}

function weightedRandomShuffle<T>(items: { item: T; weight: number }[]): T[] {
  const result: T[] = []
  const pool = items.filter(i => i.weight > 0).map(i => ({ ...i }))

  while (pool.length > 0) {
    const totalWeight = pool.reduce((sum, i) => sum + i.weight, 0)
    let random = Math.random() * totalWeight
    let idx = 0
    for (let i = 0; i < pool.length; i++) {
      random -= pool[i].weight
      if (random <= 0) {
        idx = i
        break
      }
    }
    result.push(pool[idx].item)
    pool.splice(idx, 1)
  }

  return result
}

export function usePracticeSession<T>(
  moduleId: string,
  items: PracticeItem<T>[],
) {
  const { recordResult, getAllStats } = useProgress(moduleId)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isRevealed, setIsRevealed] = useState(false)
  const [frequencies, setFrequenciesState] = useState<Record<string, Frequency>>(
    () => loadFrequencies(moduleId)
  )

  const queueRef = useRef<T[]>([])

  const buildQueue = useCallback(() => {
    const stats = getAllStats()
    const weighted = items.map(({ item, elementId }) => {
      const freq = frequencies[elementId] ?? 'normal'
      const userMult = FREQUENCY_MULTIPLIERS[freq]
      const elemStats = stats[elementId] ?? { correct: 0, incorrect: 0, lastSeen: '' }
      const organicMult = computeOrganicWeight(elemStats)
      return { item, weight: userMult * organicMult }
    })
    return weightedRandomShuffle(weighted)
  }, [items, frequencies, getAllStats])

  // Build queue on first render or when it's exhausted
  if (queueRef.current.length === 0 && items.length > 0) {
    queueRef.current = buildQueue()
    setCurrentIndex(0)
  }

  const currentItem = queueRef.current[currentIndex] ?? null

  const reveal = useCallback(() => {
    setIsRevealed(true)
  }, [])

  const next = useCallback((feedback?: { elementId: string; correct: boolean }) => {
    if (feedback) {
      recordResult(feedback.elementId, feedback.correct)
    }
    setIsRevealed(false)

    if (currentIndex + 1 >= queueRef.current.length) {
      // Rebuild queue
      queueRef.current = buildQueue()
      setCurrentIndex(0)
    } else {
      setCurrentIndex(prev => prev + 1)
    }
  }, [currentIndex, buildQueue, recordResult])

  const setFrequency = useCallback((elementId: string, freq: Frequency) => {
    setFrequenciesState(prev => {
      const updated = { ...prev, [elementId]: freq }
      saveFrequencies(moduleId, updated)
      return updated
    })
    // Rebuild queue on next advance
  }, [moduleId])

  const uniqueElements = useMemo(() => {
    const seen = new Set<string>()
    return items.filter(i => {
      if (seen.has(i.elementId)) return false
      seen.add(i.elementId)
      return true
    }).map(i => i.elementId)
  }, [items])

  const progress = useMemo(() => {
    const total = queueRef.current.length
    return { current: currentIndex + 1, total }
  }, [currentIndex])

  return {
    currentItem,
    isRevealed,
    reveal,
    next,
    frequencies,
    setFrequency,
    uniqueElements,
    progress,
  }
}

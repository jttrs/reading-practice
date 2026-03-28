import { useCallback } from 'react'

const STORAGE_PREFIX = 'progress:'

export interface ElementStats {
  correct: number
  incorrect: number
  lastSeen: string
}

interface ProgressRecord {
  elements: Record<string, ElementStats>
}

function loadProgress(moduleId: string): ProgressRecord {
  try {
    const raw = localStorage.getItem(STORAGE_PREFIX + moduleId)
    if (raw) return JSON.parse(raw)
  } catch { /* ignore corrupt data */ }
  return { elements: {} }
}

function saveProgress(moduleId: string, record: ProgressRecord) {
  localStorage.setItem(STORAGE_PREFIX + moduleId, JSON.stringify(record))
}

export function useProgress(moduleId: string) {
  const recordResult = useCallback((elementId: string, correct: boolean) => {
    const record = loadProgress(moduleId)
    const stats = record.elements[elementId] ?? { correct: 0, incorrect: 0, lastSeen: '' }
    if (correct) {
      stats.correct++
    } else {
      stats.incorrect++
    }
    stats.lastSeen = new Date().toISOString()
    record.elements[elementId] = stats
    saveProgress(moduleId, record)
  }, [moduleId])

  const getStats = useCallback((elementId: string): ElementStats => {
    const record = loadProgress(moduleId)
    return record.elements[elementId] ?? { correct: 0, incorrect: 0, lastSeen: '' }
  }, [moduleId])

  const getAllStats = useCallback((): Record<string, ElementStats> => {
    return loadProgress(moduleId).elements
  }, [moduleId])

  const resetProgress = useCallback(() => {
    localStorage.removeItem(STORAGE_PREFIX + moduleId)
  }, [moduleId])

  return { recordResult, getStats, getAllStats, resetProgress }
}

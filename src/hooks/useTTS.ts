import { useCallback, useRef, useState, useEffect } from 'react'

export function useTTS(moduleId: string) {
  const settingsKey = `settings:${moduleId}:tts`
  const [enabled, setEnabled] = useState(() => {
    try {
      const stored = localStorage.getItem(settingsKey)
      return stored !== null ? stored === 'true' : true
    } catch {
      return true
    }
  })
  const [available, setAvailable] = useState(false)
  const synthRef = useRef<SpeechSynthesis | null>(null)

  useEffect(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      synthRef.current = window.speechSynthesis
      setAvailable(true)
    }
  }, [])

  useEffect(() => {
    localStorage.setItem(settingsKey, String(enabled))
  }, [enabled, settingsKey])

  const speak = useCallback((text: string, rate = 0.8) => {
    if (!enabled || !synthRef.current) return
    synthRef.current.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = rate
    utterance.pitch = 1.0
    synthRef.current.speak(utterance)
  }, [enabled])

  const speakSequence = useCallback(async (parts: string[], pauseMs = 600) => {
    if (!enabled || !synthRef.current) return
    synthRef.current.cancel()

    for (let i = 0; i < parts.length; i++) {
      const utterance = new SpeechSynthesisUtterance(parts[i])
      utterance.rate = 0.7
      utterance.pitch = 1.0

      await new Promise<void>((resolve) => {
        utterance.onend = () => resolve()
        utterance.onerror = () => resolve()
        synthRef.current!.speak(utterance)
      })

      if (i < parts.length - 1) {
        await new Promise(r => setTimeout(r, pauseMs))
      }
    }
  }, [enabled])

  const stop = useCallback(() => {
    synthRef.current?.cancel()
  }, [])

  const toggle = useCallback(() => {
    setEnabled(prev => !prev)
  }, [])

  return { speak, speakSequence, stop, enabled, toggle, available }
}

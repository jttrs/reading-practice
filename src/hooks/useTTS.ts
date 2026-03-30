import { useCallback, useRef, useState, useEffect } from 'react'

/**
 * Resolve a TTS value to an audio file URL.
 *
 * - If `type` is 'word', looks in /audio/words/
 * - If `type` is 'phoneme', looks in /audio/phonemes/
 */
function audioUrl(value: string, type: 'phoneme' | 'word'): string {
  const dir = type === 'word' ? 'words' : 'phonemes'
  return `${import.meta.env.BASE_URL}audio/${dir}/${encodeURIComponent(value)}.mp3`
}

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
  // Audio is always available (pre-generated files)
  const available = true
  const currentAudioRef = useRef<HTMLAudioElement | null>(null)
  const abortRef = useRef(false)

  useEffect(() => {
    localStorage.setItem(settingsKey, String(enabled))
  }, [enabled, settingsKey])

  const stop = useCallback(() => {
    abortRef.current = true
    if (currentAudioRef.current) {
      currentAudioRef.current.pause()
      currentAudioRef.current = null
    }
  }, [])

  const playAudio = useCallback((url: string): Promise<void> => {
    return new Promise((resolve) => {
      const audio = new Audio(url)
      currentAudioRef.current = audio
      audio.onended = () => {
        currentAudioRef.current = null
        resolve()
      }
      audio.onerror = () => {
        currentAudioRef.current = null
        resolve()
      }
      audio.play().catch(() => resolve())
    })
  }, [])

  /** Speak a whole word using pre-generated audio. */
  const speak = useCallback((word: string) => {
    if (!enabled) return
    stop()
    abortRef.current = false
    playAudio(audioUrl(word, 'word'))
  }, [enabled, stop, playAudio])

  /**
   * Speak a sequence of sounds then the whole word.
   * The last element of `parts` is treated as a whole word;
   * all preceding elements are phoneme sounds.
   */
  const speakSequence = useCallback(async (parts: string[], pauseMs = 500) => {
    if (!enabled || parts.length === 0) return
    stop()
    abortRef.current = false

    for (let i = 0; i < parts.length; i++) {
      if (abortRef.current) return

      // Last element is the whole word, rest are phoneme sounds
      const isWord = i === parts.length - 1
      const url = audioUrl(parts[i], isWord ? 'word' : 'phoneme')
      await playAudio(url)

      if (i < parts.length - 1 && !abortRef.current) {
        await new Promise(r => setTimeout(r, pauseMs))
      }
    }
  }, [enabled, stop, playAudio])

  const toggle = useCallback(() => {
    setEnabled(prev => !prev)
  }, [])

  return { speak, speakSequence, stop, enabled, toggle, available }
}

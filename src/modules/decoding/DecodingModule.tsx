import { useEffect, useCallback, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import decodingData from '../../data/decoding-words.json'
import type { DecodingData, DecodingWord, SpellingUnit } from './types'
import { usePracticeSession, type Frequency } from '../../hooks/usePracticeSession'
import { useTTS } from '../../hooks/useTTS'
import DecodingCard from './DecodingCard'
import FeedbackButtons from '../../components/FeedbackButtons'
import CooldownIndicator from '../../components/CooldownIndicator'

const COOLDOWN_MS = 2000
const data = decodingData as DecodingData

type Phase = 'showing' | 'revealed' | 'cooldown'
type FeedbackResult = 'correct' | 'incorrect' | null

export default function DecodingModule() {
  const navigate = useNavigate()
  const [phase, setPhase] = useState<Phase>('showing')
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [lastResult, setLastResult] = useState<FeedbackResult>(null)

  const spellingUnitsMap = useMemo(() => {
    const map = new Map<string, SpellingUnit>()
    for (const u of data.spellingUnits) {
      map.set(u.id, u)
    }
    return map
  }, [])

  const practiceItems = useMemo(
    () => data.decodingWords.map((w) => ({ item: w, elementId: w.spellingUnitId })),
    [],
  )

  const session = usePracticeSession<DecodingWord>('decoding', practiceItems)
  const tts = useTTS('decoding')

  const currentWord = session.currentItem
  const spellingUnit = currentWord ? spellingUnitsMap.get(currentWord.spellingUnitId) : undefined

  const handleReveal = useCallback(() => {
    if (phase !== 'showing') return
    session.reveal()
    setPhase('revealed')

    if (currentWord && tts.enabled) {
      // Speak breakdown elements then full word
      const parts = [...currentWord.ttsBreakdown.filter(Boolean), currentWord.ttsWord]
      tts.speakSequence(parts)
    }
  }, [phase, session, currentWord, tts])

  const handleFeedback = useCallback((correct: boolean) => {
    if (phase !== 'revealed' || !currentWord) return
    tts.stop()
    setLastResult(correct ? 'correct' : 'incorrect')
    session.next({ elementId: currentWord.spellingUnitId, correct })
    setPhase('cooldown')
  }, [phase, currentWord, session, tts])

  const handleSkip = useCallback(() => {
    if (phase !== 'revealed') return
    tts.stop()
    session.next()
    setPhase('cooldown')
  }, [phase, session, tts])

  const handleCooldownComplete = useCallback(() => {
    setPhase('showing')
    setLastResult(null)
  }, [])

  // Global key/click handler
  useEffect(() => {
    const handleInteraction = (e: KeyboardEvent | MouseEvent) => {
      // Ignore if settings panel is open
      if (settingsOpen) return
      // Ignore if clicking on buttons (feedback, settings, back)
      if (e instanceof MouseEvent) {
        const target = e.target as HTMLElement
        if (target.closest('button') || target.closest('a')) return
      }

      if (phase === 'showing') {
        handleReveal()
      } else if (phase === 'revealed') {
        handleSkip()
      }
      // During cooldown, ignore
    }

    window.addEventListener('keydown', handleInteraction)
    window.addEventListener('click', handleInteraction)
    return () => {
      window.removeEventListener('keydown', handleInteraction)
      window.removeEventListener('click', handleInteraction)
    }
  }, [phase, handleReveal, handleSkip, settingsOpen])

  if (!currentWord) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-xl text-stone-500">No words available. Check your settings.</p>
      </div>
    )
  }

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-indigo-50 to-white select-none">
      {/* Header */}
      <div className="fixed top-0 left-0 right-0 flex items-center justify-between px-4 py-4">
        <button
          onClick={() => navigate('/')}
          className="rounded-lg px-3 py-1 text-sm text-stone-500 hover:bg-stone-100"
        >
          ← Back
        </button>
        <span className="text-sm text-stone-400">
          {session.progress.current} / {session.progress.total}
        </span>
        <button
          onClick={() => setSettingsOpen(!settingsOpen)}
          className="rounded-lg px-3 py-1 text-sm text-stone-500 hover:bg-stone-100"
        >
          ⚙️
        </button>
      </div>

      {/* Settings drawer */}
      {settingsOpen && (
        <div className="fixed top-12 right-4 z-50 w-72 rounded-xl border bg-white p-4 shadow-lg">
          <h3 className="mb-3 font-bold text-stone-700">Settings</h3>

          {tts.available && (
            <label className="mb-4 flex items-center gap-2 text-sm text-stone-600">
              <input
                type="checkbox"
                checked={tts.enabled}
                onChange={tts.toggle}
                className="rounded"
              />
              Text-to-Speech
            </label>
          )}

          <h4 className="mb-2 text-xs font-semibold uppercase text-stone-400">Spelling Units</h4>
          <div className="max-h-64 overflow-y-auto">
            {session.uniqueElements.map((id) => {
              const unit = spellingUnitsMap.get(id)
              const freq = session.frequencies[id] ?? 'normal'
              return (
                <div key={id} className="mb-2 flex items-center justify-between text-sm">
                  <span className="text-stone-600">
                    {unit?.patterns.join(', ') ?? id}
                    {unit?.phoneme ? ` ${unit.phoneme}` : ''}
                  </span>
                  <select
                    value={freq}
                    onChange={(e) => session.setFrequency(id, e.target.value as Frequency)}
                    className="rounded border px-1 py-0.5 text-xs"
                  >
                    <option value="off">Off</option>
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                  </select>
                </div>
              )
            })}
          </div>

          <button
            onClick={() => setSettingsOpen(false)}
            className="mt-3 w-full rounded-lg bg-stone-100 py-1 text-sm text-stone-600 hover:bg-stone-200"
          >
            Close
          </button>
        </div>
      )}

      {/* Main content — hide during cooldown for clean transition */}
      {phase !== 'cooldown' && (
        <DecodingCard
          word={currentWord}
          spellingUnit={spellingUnit}
          isRevealed={session.isRevealed}
        />
      )}

      {/* Feedback message — shown during cooldown */}
      {phase === 'cooldown' && lastResult && (
        <span
          className={`text-2xl font-bold animate-[fade-in-up_0.3s_ease-out] ${
            lastResult === 'correct' ? 'text-green-600' : 'text-red-500'
          }`}
        >
          {lastResult === 'correct' ? 'Nice!' : 'Keep trying!'}
        </span>
      )}

      {/* Feedback buttons — only when revealed */}
      {phase === 'revealed' && (
        <FeedbackButtons
          onCorrect={() => handleFeedback(true)}
          onIncorrect={() => handleFeedback(false)}
        />
      )}

      <CooldownIndicator
        active={phase === 'cooldown'}
        durationMs={COOLDOWN_MS}
        onComplete={handleCooldownComplete}
      />
    </div>
  )
}

interface FeedbackButtonsProps {
  onCorrect: () => void
  onIncorrect: () => void
  lastResult?: 'correct' | 'incorrect' | null
}

export default function FeedbackButtons({ onCorrect, onIncorrect, lastResult }: FeedbackButtonsProps) {
  return (
    <div className="mt-8 flex flex-col items-center gap-4">
      {lastResult && (
        <span
          className={`text-lg font-semibold animate-[fade-in-up_0.3s_ease-out] ${
            lastResult === 'correct' ? 'text-green-600' : 'text-red-500'
          }`}
        >
          {lastResult === 'correct' ? 'Nice!' : 'Keep trying!'}
        </span>
      )}
      <div className="flex justify-center gap-8">
        <button
          onClick={(e) => { e.stopPropagation(); onIncorrect() }}
          className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-3xl text-red-600 transition-all hover:bg-red-200 active:scale-90 active:animate-[incorrect-pulse_0.3s_ease-out]"
          aria-label="Incorrect"
        >
          ✗
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onCorrect() }}
          className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-3xl text-green-600 transition-all hover:bg-green-200 active:scale-90 active:animate-[success-pulse_0.3s_ease-out]"
          aria-label="Correct"
        >
          ✓
        </button>
      </div>
    </div>
  )
}

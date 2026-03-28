interface FeedbackButtonsProps {
  onCorrect: () => void
  onIncorrect: () => void
}

export default function FeedbackButtons({ onCorrect, onIncorrect }: FeedbackButtonsProps) {
  return (
    <div className="mt-8 flex justify-center gap-8">
      <button
        onClick={(e) => { e.stopPropagation(); onIncorrect() }}
        className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-3xl text-red-600 transition-all hover:bg-red-200 active:scale-90"
        aria-label="Incorrect"
      >
        ✗
      </button>
      <button
        onClick={(e) => { e.stopPropagation(); onCorrect() }}
        className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-3xl text-green-600 transition-all hover:bg-green-200 active:scale-90"
        aria-label="Correct"
      >
        ✓
      </button>
    </div>
  )
}

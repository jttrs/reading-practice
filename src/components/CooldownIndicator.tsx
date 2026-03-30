import { useEffect, useState } from 'react'

interface CooldownIndicatorProps {
  active: boolean
  durationMs: number
  onComplete: () => void
}

export default function CooldownIndicator({ active, durationMs, onComplete }: CooldownIndicatorProps) {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (!active) {
      setProgress(0)
      return
    }

    const start = Date.now()
    let frame: number

    const tick = () => {
      const elapsed = Date.now() - start
      const pct = Math.min(elapsed / durationMs, 1)
      setProgress(pct)

      if (pct >= 1) {
        onComplete()
      } else {
        frame = requestAnimationFrame(tick)
      }
    }

    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [active, durationMs, onComplete])

  if (!active) return null

  const size = 32
  const strokeWidth = 3
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const dashoffset = circumference * (1 - progress)

  return (
    <div className="fixed bottom-4 right-4 opacity-40">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#d6d3d1"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#78716c"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={dashoffset}
          strokeLinecap="round"
        />
      </svg>
    </div>
  )
}

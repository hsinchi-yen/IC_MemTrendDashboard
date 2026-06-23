import { useEffect, useRef, useState } from 'react'

/**
 * Animates a numeric value from its previous state to `target`
 * using an ease-out cubic easing over `duration` ms.
 *
 * Returns the current interpolated value for rendering.
 */
export function useSmoothCounter(target: number, duration = 800): number {
  const [current, setCurrent] = useState<number>(target)
  const rafRef = useRef<number>(0)
  const startTimeRef = useRef<number>(0)
  const startValRef = useRef<number>(target)

  useEffect(() => {
    // Capture the value at the moment the target changes
    startValRef.current = current
    startTimeRef.current = performance.now()

    const animate = (now: number): void => {
      const elapsed = now - startTimeRef.current
      const progress = Math.min(elapsed / duration, 1)
      // Ease-out cubic: decelerates toward the end
      const eased = 1 - Math.pow(1 - progress, 3)
      const next = startValRef.current + (target - startValRef.current) * eased
      setCurrent(next)
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate)
      }
    }

    cancelAnimationFrame(rafRef.current)
    rafRef.current = requestAnimationFrame(animate)

    return () => cancelAnimationFrame(rafRef.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target, duration])

  return current
}

import { useEffect, useState } from 'react'

export function useMountAnimation(delay = 0): boolean {
  const [active, setActive] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => setActive(true), delay)
    return () => window.clearTimeout(timer)
  }, [delay])

  return active
}
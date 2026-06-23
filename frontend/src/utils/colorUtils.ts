export function getChangeColor(pct: number): string {
  if (pct > 0.1) return 'var(--color-bull)'
  if (pct < -0.1) return 'var(--color-bear)'
  return 'var(--color-neutral)'
}

export function getHeatmapColor(pct: number, maxAbs: number): string {
  if (maxAbs === 0) return 'rgba(255,255,255,0.03)'
  const intensity = Math.min(Math.abs(pct) / maxAbs, 1)
  if (pct > 0) return `rgba(0, 230, 118, ${(0.1 + intensity * 0.5).toFixed(3)})`
  if (pct < 0) return `rgba(255, 23, 68, ${(0.1 + intensity * 0.5).toFixed(3)})`
  return 'rgba(255,255,255,0.03)'
}

export function formatPct(
  pct: number | null | undefined,
  digits = 2,
): string {
  if (pct == null) return 'N/A'
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct.toFixed(digits)}%`
}

export function formatPrice(
  price: number | null | undefined,
  currency = 'USD',
): string {
  if (price == null) return 'N/A'
  if (currency === 'TWD') return price.toFixed(2)
  if (currency === 'KRW') return Math.round(price).toLocaleString('ko-KR')
  if (currency === 'JPY') return Math.round(price).toLocaleString('ja-JP')
  // USD / default — show 4 decimal places for sub-dollar instruments
  return price < 10 ? price.toFixed(4) : price.toFixed(2)
}

export function formatLargeNumber(n: number | null | undefined): string {
  if (n == null) return 'N/A'
  if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(2)}B`
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(2)}M`
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n.toFixed(2)
}

export function scoreToStatus(score: number): 'BULLISH' | 'NEUTRAL' | 'BEARISH' {
  if (score >= 60) return 'BULLISH'
  if (score <= 40) return 'BEARISH'
  return 'NEUTRAL'
}

export function scoreToColor(score: number): string {
  if (score >= 60) return 'var(--color-bull)'
  if (score <= 40) return 'var(--color-bear)'
  return 'var(--color-neutral)'
}

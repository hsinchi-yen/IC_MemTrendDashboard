import { useSmoothCounter } from '../../hooks/useSmoothCounter'
import { scoreToColor, scoreToStatus } from '../../utils/colorUtils'

export function BullBearGauge({
  score,
  status,
  narrative,
  onExpand,
}: {
  score: number
  status: string
  narrative?: { summary: string; quote: string; equity: string; risk: string; relative: string }
  onExpand?: () => void
}) {
  const animated = useSmoothCounter(score, 800)
  const color = scoreToColor(score)
  const state = status || scoreToStatus(score)
  const glowClass = score >= 80 ? 'glow-bull' : score <= 20 ? 'glow-bear' : ''

  return (
    <button
      type="button"
      className={`glass-card ${glowClass}`}
      onClick={onExpand}
      style={{ width: '100%', padding: 20, cursor: onExpand ? 'pointer' : 'default' }}
    >
      <div className="text-xs text-secondary">Bull / Bear Gauge</div>
      <div
        style={{
          width: 180,
          height: 180,
          margin: '16px auto',
          borderRadius: '50%',
          background: `conic-gradient(${color} 0deg, ${color} ${animated * 3.6}deg, rgba(255,255,255,0.08) ${animated * 3.6}deg 360deg)`,
          display: 'grid',
          placeItems: 'center',
          boxShadow: `0 0 0 10px rgba(255,255,255,0.04) inset`,
        }}
      >
        <div className="glass-card" style={{ width: 118, height: 118, borderRadius: '50%', display: 'grid', placeItems: 'center', background: 'rgba(10,14,26,0.9)' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '2.5rem', color }}>{Math.round(animated)}</div>
          <div className="text-xs text-secondary">{state}</div>
        </div>
      </div>
      {narrative ? <p className="text-sm text-secondary" style={{ textAlign: 'left' }}>{narrative.summary}</p> : null}
    </button>
  )
}
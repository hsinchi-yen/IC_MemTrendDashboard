function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const angle = ((angleDeg - 90) * Math.PI) / 180
  return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) }
}

function polygonPoints(values: number[], size: number, max = 100) {
  const center = size / 2
  const radius = size * 0.38
  return values
    .map((value, index) => polarToCartesian(center, center, radius * (value / max), (360 / values.length) * index))
    .map(({ x, y }) => `${x},${y}`)
    .join(' ')
}

export function ScoreRadarChart({
  scores,
  narrative,
}: {
  scores: { quote_momentum: number; equity_momentum: number; breadth: number; risk_inverse: number; relative_strength: number }
  narrative: Record<string, string>
}) {
  const labels = ['報價動能', '股票動能', '供應鏈廣度', '風險（反向）', '相對強弱']
  const values = [scores.quote_momentum, scores.equity_momentum, scores.breadth, scores.risk_inverse, scores.relative_strength]
  const size = 320
  const center = size / 2
  const polygon = polygonPoints(values, size)

  return (
    <section className="glass-card" style={{ padding: 20 }}>
      <div className="text-xs text-secondary">五維雷達圖</div>
      <svg viewBox={`0 0 ${size} ${size}`} width="100%" height="100%" style={{ maxWidth: 360, display: 'block', margin: '0 auto' }}>
        {[20, 40, 60, 80, 100].map((level) => (
          <polygon
            key={level}
            points={labels.map((_, index) => polarToCartesian(center, center, (size * 0.38) * (level / 100), (360 / labels.length) * index)).map(({ x, y }) => `${x},${y}`).join(' ')}
            fill="none"
            stroke="rgba(255,255,255,0.08)"
          />
        ))}
        <polygon points={polygon} fill="rgba(124,58,237,0.28)" stroke="var(--color-accent-light)" strokeWidth="2" />
        {labels.map((label, index) => {
          const { x, y } = polarToCartesian(center, center, size * 0.45, (360 / labels.length) * index)
          return (
            <g key={label}>
              <line x1={center} y1={center} x2={x} y2={y} stroke="rgba(255,255,255,0.08)" />
              <text x={x} y={y} fill="var(--text-secondary)" fontSize="12" textAnchor="middle" dominantBaseline="middle">
                {label}
              </text>
            </g>
          )
        })}
      </svg>
      <div className="grid" style={{ gridTemplateColumns: 'repeat(5, minmax(0, 1fr))', gap: 8 }}>
        {Object.entries(narrative).map(([key, value]) => (
          <div key={key} className="glass-card" style={{ padding: 10 }} title={value}>
            <div className="text-xs text-secondary">{key}</div>
            <div className="text-sm">{value}</div>
          </div>
        ))}
      </div>
    </section>
  )
}
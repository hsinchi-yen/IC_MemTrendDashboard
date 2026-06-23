export function SparklineTooltip({
  title,
  subtitle,
  values,
}: {
  title: string
  subtitle: string
  values: number[]
}) {
  const width = 180
  const height = 64
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const path = values
    .map((value, index) => {
      const x = (index / Math.max(values.length - 1, 1)) * width
      const y = height - ((value - min) / range) * height
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')

  return (
    <div className="glass-card tooltip-enter" style={{ padding: 12, width: 240, position: 'absolute', zIndex: 10 }}>
      <div style={{ fontWeight: 600 }}>{title}</div>
      <div className="text-xs text-secondary">{subtitle}</div>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="64" style={{ marginTop: 8 }}>
        <path d={path} fill="none" stroke="var(--color-accent-light)" strokeWidth="2" />
      </svg>
    </div>
  )
}
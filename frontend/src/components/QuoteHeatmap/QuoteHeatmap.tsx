import type { Period } from '../../context/PeriodContext'
import { useQuoteHeatmap } from '../../api/hooks/useQuotes'
import { demoQuoteRows } from '../../data/demo'
import { formatPct, getHeatmapColor } from '../../utils/colorUtils'

export function QuoteHeatmap({ period }: { period: Period }) {
  const query = useQuoteHeatmap(period)
  const rows = query.data ?? demoQuoteRows
  const periods: Period[] = ['1D', '1W', '1M', '3M', '6M', '1Y']
  const maxAbs = Math.max(...rows.flatMap((row) => periods.map((p) => Math.abs(row.changes[p] ?? 0))), 1)

  return (
    <section className="glass-card" style={{ padding: 20 }}>
      <div className="flex items-center justify-between gap-4" style={{ flexWrap: 'wrap' }}>
        <div>
          <div className="text-xs text-secondary">Quote Heatmap</div>
          <h3>報價熱力表</h3>
        </div>
        <div className="text-xs text-muted">目前期間：{period}</div>
      </div>

      <table style={{ width: '100%', marginTop: 16, borderCollapse: 'separate', borderSpacing: 0 }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left', padding: '8px 10px' }}>品項</th>
            {periods.map((item) => <th key={item} style={{ textAlign: 'center', padding: '8px 10px' }}>{item}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td style={{ padding: '10px', whiteSpace: 'nowrap' }}>{row.label}</td>
              {periods.map((item) => {
                const value = row.changes[item] ?? 0
                return (
                  <td key={item} style={{ padding: '6px' }}>
                    <div
                      className="glass-card"
                      title={`${row.label} ${item} ${formatPct(value)}`}
                      style={{
                        textAlign: 'center',
                        padding: '10px 8px',
                        background: getHeatmapColor(value, maxAbs),
                        borderColor: 'rgba(255,255,255,0.08)',
                      }}
                    >
                      {formatPct(value)}
                    </div>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
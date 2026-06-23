import { useState } from 'react'
import { useTrendChart } from '../../api/hooks/useTrends'
import { usePeriod } from '../../context/PeriodContext'

type SeriesKey = 'DRAM' | 'NAND' | '股票' | '全部'

function linePath(values: number[], width: number, height: number) {
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  return values
    .map((value, index) => {
      const x = (index / Math.max(values.length - 1, 1)) * width
      const y = height - ((value - min) / range) * height
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')
}

export function TrendChart() {
  const [series, setSeries] = useState<SeriesKey>('全部')
  const { period } = usePeriod()
  const query = useTrendChart(period)
  const fallback = {
    dates: ['1M', '2M', '3M', '4M', '5M', '6M'],
    dram: [100, 104, 106, 111, 118, 124],
    nand: [100, 99, 98, 100, 101, 99],
    stock: [100, 102, 105, 109, 113, 119],
  }
  const live = query.data?.points
  const mapped = live
    ? {
        dates: live.map((point) => point.date),
        dram: live.map((point) => point.dram ?? 0),
        nand: live.map((point) => point.nand ?? 0),
        stock: live.map((point) => point.stock ?? 0),
      }
    : fallback
  const width = 640
  const height = 260

  return (
    <section className="glass-card" style={{ padding: 20 }}>
      <div className="flex items-center justify-between gap-4" style={{ flexWrap: 'wrap' }}>
        <div>
          <div className="text-xs text-secondary">Trend Chart</div>
          <h3>大趨勢圖</h3>
        </div>
        <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
          {(['DRAM', 'NAND', '股票', '全部'] as SeriesKey[]).map((item) => (
            <button key={item} type="button" className={`period-pill ${series === item ? 'period-pill--active' : ''}`} onClick={() => setSeries(item)}>
              {item}
            </button>
          ))}
        </div>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="100%" style={{ marginTop: 16 }}>
        <line x1="0" y1={height - 1} x2={width} y2={height - 1} stroke="rgba(255,255,255,0.08)" />
        {(series === 'DRAM' || series === '全部') && <path d={linePath(mapped.dram, width, height - 20)} fill="none" stroke="var(--color-bull)" strokeWidth="2.5" />}
        {(series === 'NAND' || series === '全部') && <path d={linePath(mapped.nand, width, height - 20)} fill="none" stroke="var(--color-bear)" strokeWidth="2.5" />}
        {(series === '股票' || series === '全部') && <path d={linePath(mapped.stock, width, height - 20)} fill="none" stroke="var(--color-accent-light)" strokeWidth="2.5" />}
      </svg>
    </section>
  )
}
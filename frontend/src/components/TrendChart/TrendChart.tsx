import { useMemo, useState } from 'react'
import ECharts from 'echarts-for-react'
import { useTrendChart } from '../../api/hooks/useTrends'
import { usePeriod } from '../../context/PeriodContext'

type SeriesKey = 'DRAM' | 'NAND' | '股票' | '全部'

const COLORS = {
  DRAM: '#00e676',
  NAND: '#ff1744',
  股票: '#a78bfa',
}

/** Format an ISO date (2026-06-22) to MM/DD; pass through non-date labels. */
function formatAxisDate(value: string): string {
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return `${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}

export function TrendChart() {
  const [series, setSeries] = useState<SeriesKey>('全部')
  const { period } = usePeriod()
  const query = useTrendChart(period)

  const fallback = {
    dates: ['2026-01-01', '2026-02-01', '2026-03-01', '2026-04-01', '2026-05-01', '2026-06-01'],
    dram: [100, 104, 106, 111, 118, 124],
    nand: [100, 99, 98, 100, 101, 99],
    stock: [100, 102, 105, 109, 113, 119],
  }
  const live = query.data?.points
  const mapped = live && live.length
    ? {
        dates: live.map((point) => point.date),
        dram: live.map((point) => point.dram ?? null),
        nand: live.map((point) => point.nand ?? null),
        stock: live.map((point) => point.stock ?? null),
      }
    : fallback

  const events = query.data?.events ?? []

  const option = useMemo(() => {
    const show = (key: SeriesKey) => series === '全部' || series === key

    const lineSeries = [
      { key: 'DRAM' as const, name: 'DRAM 報價', data: mapped.dram, color: COLORS.DRAM },
      { key: 'NAND' as const, name: 'NAND 報價', data: mapped.nand, color: COLORS.NAND },
      { key: '股票' as const, name: '股票籃子', data: mapped.stock, color: COLORS.股票 },
    ]
      .filter((s) => show(s.key))
      .map((s, idx) => ({
        name: s.name,
        type: 'line',
        smooth: true,
        showSymbol: false,
        connectNulls: true,
        lineStyle: { width: 2.5, color: s.color },
        itemStyle: { color: s.color },
        data: s.data,
        // Attach event markers (vertical lines on the time axis) to the
        // first visible series only, so they render once.
        ...(idx === 0 && events.length
          ? {
              markLine: {
                symbol: 'none',
                silent: false,
                lineStyle: { color: 'rgba(167,139,250,0.55)', type: 'dashed', width: 1 },
                label: {
                  show: true,
                  formatter: (p: { name: string }) => p.name,
                  color: '#94a3b8',
                  fontSize: 10,
                  rotate: 90,
                  position: 'insideEndTop',
                },
                data: events
                  .filter((ev) => mapped.dates.includes(ev.date))
                  .map((ev) => ({ xAxis: ev.date, name: ev.label })),
              },
            }
          : {}),
      }))

    return {
      backgroundColor: 'transparent',
      grid: { left: 48, right: 20, top: 40, bottom: 48 },
      legend: {
        top: 0,
        textStyle: { color: '#94a3b8' },
        inactiveColor: '#475569',
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(10,14,26,0.92)',
        borderColor: 'rgba(255,255,255,0.14)',
        textStyle: { color: '#f1f5f9' },
        axisPointer: { type: 'line', lineStyle: { color: 'rgba(255,255,255,0.25)' } },
        valueFormatter: (v: number | null) => (v == null ? '—' : Number(v).toFixed(1)),
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: mapped.dates,
        name: '日期',
        nameLocation: 'middle',
        nameGap: 30,
        nameTextStyle: { color: '#94a3b8', fontSize: 11 },
        axisLabel: {
          color: '#94a3b8',
          fontSize: 10,
          hideOverlap: true,
          formatter: formatAxisDate,
        },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.14)' } },
        axisTick: { alignWithLabel: true },
      },
      yAxis: {
        type: 'value',
        scale: true,
        name: '指數 (基期=100)',
        nameTextStyle: { color: '#94a3b8', fontSize: 11, align: 'left' },
        axisLabel: { color: '#94a3b8', fontSize: 10 },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series: lineSeries,
    }
  }, [mapped, events, series])

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

      <ECharts option={option} style={{ height: 320, marginTop: 12 }} notMerge />
    </section>
  )
}

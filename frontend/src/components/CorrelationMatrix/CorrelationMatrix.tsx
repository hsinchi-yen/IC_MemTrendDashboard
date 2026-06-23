import { useMemo } from 'react'
import ECharts from 'echarts-for-react'
import { demoCorrelation } from '../../data/demo'
import { useCorrelationMatrix } from '../../api/hooks/useAnalysis'

export function CorrelationMatrix({ windowDays }: { windowDays: 60 | 120 }) {
  const query = useCorrelationMatrix(windowDays)

  type LocalRow = { row: string; quote: string; value: number | null }
  type ApiRow = { stock: string; quote: string; value: number | null }
  const data: LocalRow[] = ((query.data as ApiRow[] | undefined) ?? demoCorrelation).map((item) => ({
    row: 'stock' in item ? item.stock : item.row,
    quote: item.quote,
    value: item.value,
  }))

  const chartOption = useMemo(() => {
    const stocks = [...new Set(data.map((d) => d.row))]
    const quotes = [...new Set(data.map((d) => d.quote))]

    const heatmapData = data
      .map((item) => {
        const stockIdx = stocks.indexOf(item.row)
        const quoteIdx = quotes.indexOf(item.quote)
        const val = Math.max(-1, Math.min(1, item.value ?? 0))
        return [quoteIdx, stockIdx, val]
      })

    return {
      title: {
        text: `相關性矩陣 (${windowDays}日)`,
        textStyle: { color: '#f1f5f9', fontSize: 14, fontWeight: 'bold' },
        left: 'center',
        top: 10,
      },
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(10, 14, 26, 0.9)',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        textStyle: { color: '#f1f5f9' },
        formatter: (params: any) => {
          if (params.componentSubType === 'heatmap') {
            const [qIdx, sIdx, val] = params.value
            return `${stocks[sIdx]} vs ${quotes[qIdx]}<br/>Correlation: ${(val as number).toFixed(3)}`
          }
          return params.name
        },
      },
      grid: {
        height: Math.min(300, stocks.length * 25),
        top: 60,
        left: 60,
        right: 20,
        bottom: 60,
      },
      xAxis: {
        type: 'category',
        data: quotes,
        splitArea: { show: false },
        axisLabel: { fontSize: 10, color: '#94a3b8' },
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
      },
      yAxis: {
        type: 'category',
        data: stocks,
        splitArea: { show: false },
        axisLabel: { fontSize: 10, color: '#94a3b8' },
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
      },
      visualMap: {
        min: -1,
        max: 1,
        calculable: true,
        realtime: false,
        inRange: {
          color: ['#ff1744', '#ffffff', '#00e676'],
        },
        textStyle: { color: '#94a3b8', fontSize: 10 },
      },
      series: [
        {
          type: 'heatmap',
          data: heatmapData,
          itemStyle: {
            borderWidth: 0.5,
            borderColor: 'rgba(255, 255, 255, 0.1)',
          },
          emphasis: {
            itemStyle: {
              borderColor: '#7c3aed',
              borderWidth: 2,
            },
          },
          label: {
            show: true,
            fontSize: 8,
            color: '#f1f5f9',
            formatter: (params: any) => {
              const val = (params.value[2] as number).toFixed(2)
              return val
            },
          },
        },
      ],
      backgroundColor: 'transparent',
    }
  }, [data, windowDays])

  return (
    <section className="glass-card" style={{ padding: 20 }}>
      <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
        <div>
          <div className="text-xs text-secondary">Correlation Matrix</div>
        </div>
        <div className="text-xs text-muted">{windowDays} 日</div>
      </div>
      <div style={{ height: Math.max(300, Math.min(600, data.length * 30)), marginTop: 12, borderRadius: 8, overflow: 'hidden' }}>
        <ECharts option={chartOption} style={{ height: '100%', width: '100%' }} />
      </div>
    </section>
  )
}
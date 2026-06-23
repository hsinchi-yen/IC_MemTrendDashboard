import { useMemo } from 'react'
import ECharts from 'echarts-for-react'
import { demoSupplyChain } from '../../data/demo'
import { formatPct } from '../../utils/colorUtils'
import { useSupplyChain } from '../../api/hooks/useAnalysis'

export function SupplyChainGraph() {
  const query = useSupplyChain()
  const data = query.data ?? demoSupplyChain

  const chartOption = useMemo(() => {
    const nodes = data.nodes.map((node) => {
      const changePct = node.change_1d ?? 0
      const color = changePct >= 0 ? '#00e676' : '#ff1744'
      return {
        id: node.id,
        name: `${node.ticker}\n${node.name}`,
        value: Math.abs(changePct * 100),
        itemStyle: {
          color,
          borderColor: color,
          borderWidth: 2,
        },
        label: {
          fontSize: 10,
          color: '#f1f5f9',
        },
        symbolSize: Math.min(Math.max(30 + Math.abs(changePct) * 50, 30), 80),
      }
    })

    const edges = []
    for (let i = 0; i < data.nodes.length - 1; i++) {
      edges.push({
        source: data.nodes[i].id,
        target: data.nodes[i + 1].id,
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.15)',
          width: 1,
        },
      })
    }

    return {
      title: {
        text: '產業鏈節點圖',
        textStyle: { color: '#f1f5f9', fontSize: 14, fontWeight: 'bold' },
        left: 'center',
        top: 10,
      },
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(10, 14, 26, 0.9)',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        textStyle: { color: '#f1f5f9', fontSize: 12 },
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            const node = data.nodes.find((n) => n.id === params.id)
            if (node) {
              return `${node.ticker} ${node.name}<br/>1D: ${formatPct(node.change_1d)}`
            }
          }
          return params.name
        },
      },
      series: [
        {
          type: 'graph',
          layout: 'force',
          data: nodes,
          links: edges,
          roam: true,
          label: {
            show: true,
            position: 'right',
            fontSize: 10,
            color: '#f1f5f9',
          },
          force: {
            repulsion: 100,
            gravity: 0.1,
          },
          lineStyle: {
            color: 'rgba(255, 255, 255, 0.15)',
            width: 1.5,
            curveness: 0.3,
          },
          animationDuration: 1500,
          animationEasing: 'cubicOut',
        },
      ],
      backgroundColor: 'transparent',
    }
  }, [data])

  return (
    <section className="glass-card" style={{ padding: 20 }}>
      <div className="text-xs text-secondary">Supply Chain Graph</div>
      <div style={{ height: 400, marginTop: 12, borderRadius: 8, overflow: 'hidden' }}>
        <ECharts option={chartOption} style={{ height: '100%', width: '100%' }} />
      </div>
    </section>
  )
}
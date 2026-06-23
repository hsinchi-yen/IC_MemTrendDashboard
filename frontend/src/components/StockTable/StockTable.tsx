import { useState } from 'react'
import { useStockTable } from '../../api/hooks/useStocks'
import type { Market } from '../../api/hooks/useStocks'
import { demoStockRows } from '../../data/demo'
import type { Period } from '../../context/PeriodContext'
import { formatPct, formatPrice } from '../../utils/colorUtils'

const markets: Market[] = ['全部', '美股', '日股', '韓股', '台股']
const periods: Period[] = ['1D', '1W', '1M', '3M', '6M', '1Y']

export function StockTable({ period }: { period: Period }) {
  const [market, setMarket] = useState<Market>('全部')
  const [sortKey, setSortKey] = useState<Period>('1M')
  const [sortAsc, setSortAsc] = useState(false)
  const query = useStockTable(period, market)

  const sourceRows = query.data ?? demoStockRows
  const filtered = sourceRows.filter((row) => market === '全部' || row.market === market)
  const sorted = [...filtered].sort((a, b) => {
    const left = a.changes[sortKey] ?? -999
    const right = b.changes[sortKey] ?? -999
    return sortAsc ? left - right : right - left
  })

  return (
    <section className="glass-card" style={{ padding: 20 }}>
      <div className="flex items-center justify-between gap-4" style={{ flexWrap: 'wrap' }}>
        <div>
          <div className="text-xs text-secondary">Stock Table</div>
          <h3>股票追蹤表</h3>
          <div className="text-xs text-muted">目前期間：{period}・共 {sorted.length} 檔{query.data ? '' : '（示範資料）'}</div>
        </div>
        <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
          {markets.map((item) => (
            <button key={item} type="button" className={`period-pill ${market === item ? 'period-pill--active' : ''}`} onClick={() => setMarket(item)}>
              {item}
            </button>
          ))}
        </div>
      </div>

      <table style={{ width: '100%', marginTop: 16, borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            {['代號', '名稱', '市場', '最新價', ...periods, '均線狀態', '動能', '趨勢徽章'].map((label, index) => (
              <th key={label} style={{ textAlign: 'left', padding: '10px 8px', cursor: index === 4 ? 'pointer' : 'default' }} onClick={() => {
                if (index === 4) {
                  setSortKey('1M')
                  setSortAsc((current) => !current)
                }
              }}>
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr key={row.ticker}>
              <td style={{ padding: '10px 8px' }} className="ticker">{row.ticker}</td>
              <td style={{ padding: '10px 8px' }}>{row.name}</td>
              <td style={{ padding: '10px 8px' }}>{row.market}</td>
              <td style={{ padding: '10px 8px' }}>{formatPrice(row.price, row.currency)}</td>
              {periods.map((item) => (
                <td key={item} style={{ padding: '10px 8px', color: (row.changes[item] ?? 0) >= 0 ? 'var(--color-bull)' : 'var(--color-bear)' }}>
                  {formatPct(row.changes[item])}
                </td>
              ))}
              <td style={{ padding: '10px 8px' }}>{row.ma20_state ?? '-'} / {row.ma60_state ?? '-'}</td>
              <td style={{ padding: '10px 8px' }}>{row.momentum?.toFixed(1) ?? '-'}</td>
              <td style={{ padding: '10px 8px' }}><span className={`badge badge--${row.trend_badge}`}>{row.trend_label}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
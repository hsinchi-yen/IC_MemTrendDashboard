import { useState } from 'react'
import { StockTable } from '../../components/StockTable/StockTable'
import { demoStockRows } from '../../data/demo'
import type { Market } from '../../api/hooks/useStocks'
import type { Period } from '../../context/PeriodContext'

export function QueryPage() {
  const [period] = useState<Period>('1M')
  const [market, setMarket] = useState<Market>('全部')
  const [search, setSearch] = useState('')

  const results = demoStockRows.filter((row) => (market === '全部' || row.market === market) && `${row.ticker} ${row.name}`.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="page app-container" style={{ gap: 16 }}>
      <section className="glass-card" style={{ padding: 20 }}>
        <h2>查詢頁</h2>
        <div className="flex gap-2" style={{ flexWrap: 'wrap', marginTop: 12 }}>
          {(['全部', '美股', '韓股', '台股(核心)', '台股(觀察)'] as Market[]).map((item) => (
            <button key={item} type="button" className={`period-pill ${market === item ? 'period-pill--active' : ''}`} onClick={() => setMarket(item)}>{item}</button>
          ))}
        </div>
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="搜尋代號或名稱"
          style={{ marginTop: 12, width: '100%', background: 'rgba(255,255,255,0.04)', color: 'var(--text-primary)', border: '1px solid var(--border-default)', borderRadius: 12, padding: '12px 14px' }}
        />
      </section>

      <div className="glass-card" style={{ padding: 20 }}>
        <div className="text-sm text-secondary">符合條件：{results.length} 筆</div>
        <StockTable period={period} />
      </div>
    </div>
  )
}
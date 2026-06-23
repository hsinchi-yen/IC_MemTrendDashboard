import { demoLeaderboard } from '../../data/demo'
import type { Period } from '../../context/PeriodContext'
import { formatPct } from '../../utils/colorUtils'
import { useLeaderBoard } from '../../api/hooks/useLeaderBoard'

function LeaderList({ title, items }: { title: string; items: Array<{ id: string; label: string; change_pct: number; spark: number[]; ticker?: string }> }) {
  return (
    <section className="glass-card" style={{ padding: 16 }}>
      <h4 style={{ marginBottom: 12 }}>{title}</h4>
      <div style={{ display: 'grid', gap: 10 }}>
        {items.map((item) => (
          <div key={item.id} className="glass-card" style={{ padding: 10, display: 'flex', justifyContent: 'space-between', gap: 12 }}>
            <div>
              <div>{item.label}</div>
              <div className="text-xs text-secondary">{item.ticker ?? 'Quote'}</div>
            </div>
            <div className={item.change_pct >= 0 ? 'text-bull' : 'text-bear'}>{formatPct(item.change_pct)}</div>
          </div>
        ))}
      </div>
    </section>
  )
}

export function LeaderBoard({ period }: { period: Period }) {
  const query = useLeaderBoard(period)
  const board = query.data ?? demoLeaderboard
  return (
    <section className="glass-card" style={{ padding: 20 }}>
      <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
        <div>
          <div className="text-xs text-secondary">LeaderBoard</div>
          <h3>領先 / 落後排行榜</h3>
        </div>
        <div className="text-xs text-muted">{period}</div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 16 }}>
        <LeaderList title="報價 Top Movers" items={board.quote_top} />
        <LeaderList title="股票 Top Movers" items={board.stock_top} />
        <LeaderList title="異常波動提示" items={board.abnormal} />
      </div>
    </section>
  )
}
import { useLatestScore } from '../../api/hooks/useScore'
import { useTopBarIndicators } from '../../api/hooks/useIndicators'
import { useTriggerRefresh } from '../../api/hooks/useRefresh'
import { PERIODS, usePeriod, type Period } from '../../context/PeriodContext'
import { formatPct, scoreToColor, scoreToStatus } from '../../utils/colorUtils'
import { demoIndicators, demoScore } from '../../data/demo'

function PeriodButton({ period, active, onClick }: { period: Period; active: boolean; onClick: (period: Period) => void }) {
  return (
    <button
      type="button"
      className={`period-pill ${active ? 'period-pill--active' : ''}`}
      onClick={() => onClick(period)}
    >
      {period}
    </button>
  )
}

export function TopBar() {
  const { period, setPeriod } = usePeriod()
  const scoreQuery = useLatestScore()
  const indicatorsQuery = useTopBarIndicators(period)
  const refreshMutation = useTriggerRefresh()

  const score = scoreQuery.data ?? demoScore
  const indicators = indicatorsQuery.data ?? demoIndicators

  const statusLabel = scoreToStatus(score.total_score)

  return (
    <header className="glass-card" style={{ display: 'grid', gap: 16, padding: 20 }}>
      <div className="flex items-center justify-between gap-4" style={{ flexWrap: 'wrap' }}>
        <div>
          <p className="text-xs text-secondary">MemTrend Dashboard</p>
          <h2 style={{ fontSize: '1.25rem' }}>記憶體趨勢儀錶板</h2>
        </div>

        <div className="flex items-center gap-2" style={{ flexWrap: 'wrap' }}>
          {PERIODS.map((item) => (
            <PeriodButton key={item} period={item} active={item === period} onClick={setPeriod} />
          ))}
          <button
            type="button"
            className="btn btn--accent"
            onClick={() => refreshMutation.mutate()}
            disabled={refreshMutation.isPending}
          >
            {refreshMutation.isPending ? '更新中...' : '立即更新'}
          </button>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12 }}>
        <section className="glass-card" style={{ padding: 16, borderColor: scoreToColor(Number(score.total_score)) }}>
          <div className="text-xs text-secondary">牛熊總分</div>
          <div style={{ fontSize: '2rem', fontFamily: 'var(--font-mono)', color: scoreToColor(Number(score.total_score)) }}>{Math.round(Number(score.total_score))}</div>
          <div className="badge badge--accent">{statusLabel}</div>
        </section>

        <section className="glass-card" style={{ padding: 16 }}>
          <div className="text-xs text-secondary">DRAM</div>
          <div className={indicators.dram.direction === 'up' ? 'text-bull' : indicators.dram.direction === 'down' ? 'text-bear' : 'text-secondary'}>
            {indicators.dram.label} {formatPct(indicators.dram.change_pct)}
          </div>
        </section>

        <section className="glass-card" style={{ padding: 16 }}>
          <div className="text-xs text-secondary">NAND</div>
          <div className={indicators.nand.direction === 'up' ? 'text-bull' : indicators.nand.direction === 'down' ? 'text-bear' : 'text-secondary'}>
            {indicators.nand.label} {formatPct(indicators.nand.change_pct)}
          </div>
        </section>

        <section className="glass-card" style={{ padding: 16 }}>
          <div className="text-xs text-secondary">股票籃子</div>
          <div className={indicators.stock_basket.direction === 'up' ? 'text-bull' : indicators.stock_basket.direction === 'down' ? 'text-bear' : 'text-secondary'}>
            {indicators.stock_basket.label} {formatPct(indicators.stock_basket.change_pct)}
          </div>
          <div className="text-xs text-muted">最後更新 {new Date(indicators.updated_at).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}</div>
        </section>
      </div>
    </header>
  )
}
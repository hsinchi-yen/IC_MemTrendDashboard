import { demoBacktest } from '../../data/demo'

export function BacktestWidget() {
  return (
    <section className="glass-card" style={{ padding: 20 }}>
      <div className="text-xs text-secondary">Backtest</div>
      <h3>簡單歷史回測</h3>
      <div className="grid" style={{ gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12, marginTop: 12 }}>
        <div className="glass-card" style={{ padding: 12 }}>總交易數：{demoBacktest.total_trades}</div>
        <div className="glass-card" style={{ padding: 12 }}>勝率：{Math.round(demoBacktest.win_rate * 100)}%</div>
        <div className="glass-card" style={{ padding: 12 }}>平均報酬：{demoBacktest.avg_return.toFixed(1)}%</div>
        <div className="glass-card" style={{ padding: 12 }}>最大回撤：{demoBacktest.max_drawdown.toFixed(1)}%</div>
      </div>
    </section>
  )
}
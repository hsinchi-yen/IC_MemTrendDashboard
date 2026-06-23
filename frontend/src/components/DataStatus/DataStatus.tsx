import { useRefreshStatus, useTriggerRefresh } from '../../api/hooks/useRefresh'
import { demoIndicators } from '../../data/demo'

export function DataStatus() {
  const statusQuery = useRefreshStatus(false)
  const trigger = useTriggerRefresh()
  const status = statusQuery.data
  const isRunning = status?.is_running ?? false

  return (
    <section className="glass-card" style={{ padding: 20 }}>
      <div className="flex items-center justify-between gap-4" style={{ flexWrap: 'wrap' }}>
        <div>
          <div className="text-xs text-secondary">Data Status</div>
          <h3>資料來源狀態</h3>
        </div>
        <button type="button" className="btn btn--ghost" onClick={() => trigger.mutate()} disabled={trigger.isPending}>
          {trigger.isPending ? '更新中...' : '立即更新'}
        </button>
      </div>

      <div style={{ display: 'grid', gap: 10, marginTop: 12 }}>
        <div className="badge badge--accent">{isRunning ? '🟡 Running' : '🟢 Fresh'}</div>
        <div className="text-sm text-secondary">股票更新：{status?.equity_last_update ?? demoIndicators.updated_at}</div>
        <div className="text-sm text-secondary">報價更新：{status?.quote_last_update ?? demoIndicators.updated_at}</div>
        <div className="text-sm text-secondary">最後任務：{status?.last_run_status ?? 'success'}</div>
      </div>
    </section>
  )
}
import { InfoTooltip } from '../../components/InfoTooltip/InfoTooltip'

function Section({ title, text }: { title: string; text: string }) {
  return (
    <details className="glass-card" style={{ padding: 18 }}>
      <summary style={{ cursor: 'pointer', fontWeight: 600 }}>{title}<InfoTooltip text={text} /></summary>
      <p style={{ marginTop: 12, color: 'var(--text-secondary)' }}>{text}</p>
    </details>
  )
}

export function IndicatorsPage() {
  return (
    <div className="page app-container" style={{ gap: 16 }}>
      <section className="glass-card" style={{ padding: 20 }}>
        <h2>指標說明</h2>
        <p className="text-secondary">整理期間定義、動能、均線狀態與牛熊分數的解讀方式。</p>
      </section>
      <Section title="期間定義" text="1D / 1W / 1M / 3M / 6M / 1Y 對應 1、5、21、63、126、252 交易日。" />
      <Section title="趨勢指標" text="change_pct、direction、momentum、ma_state、hi_lo_flag、streak、acceleration 共同描述價格趨勢。" />
      <Section title="牛熊分數" text="總分由報價動能、股票動能、供應鏈廣度、風險、相對強弱加權組成。" />
      <Section title="熱力圖色階" text="綠色代表正向變化，紅色代表負向變化，色深與變化幅度成正比。" />
    </div>
  )
}
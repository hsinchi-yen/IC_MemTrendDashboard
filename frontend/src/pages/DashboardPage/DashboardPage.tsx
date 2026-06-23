import { useLatestScore } from '../../api/hooks/useScore'
import { usePeriod } from '../../context/PeriodContext'
import { TopBar } from '../../components/TopBar/TopBar'
import { BullBearGauge } from '../../components/BullBearGauge/BullBearGauge'
import { ScoreRadarChart } from '../../components/RadarChart/ScoreRadarChart'
import { TrendChart } from '../../components/TrendChart/TrendChart'
import { QuoteHeatmap } from '../../components/QuoteHeatmap/QuoteHeatmap'
import { StockTable } from '../../components/StockTable/StockTable'
import { LeaderBoard } from '../../components/LeaderBoard/LeaderBoard'
import { DataStatus } from '../../components/DataStatus/DataStatus'
import { CorrelationMatrix } from '../../components/CorrelationMatrix/CorrelationMatrix'
import { BacktestWidget } from '../../components/Backtest/BacktestWidget'
import { SupplyChainGraph } from '../../components/SupplyChainGraph/SupplyChainGraph'
import { BottomNav } from '../../components/BottomNav/BottomNav'

export function DashboardPage() {
  const { period } = usePeriod()
  const scoreQuery = useLatestScore()
  const score = scoreQuery.data

  return (
    <div className="page app-container" style={{ gap: 16 }}>
      <TopBar />
      <div className="grid" style={{ gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 16 }}>
        <BullBearGauge score={Number(score?.total_score ?? 62)} status={score?.status ?? 'bull'} narrative={score?.narrative ?? undefined} />
        <ScoreRadarChart
          scores={{
            quote_momentum: 68,
            equity_momentum: 72,
            breadth: 61,
            risk_inverse: 45,
            relative_strength: 66,
          }}
          narrative={(score?.narrative ? {
            summary: score.narrative.summary,
            quote: score.narrative.quote,
            equity: score.narrative.equity,
            risk: score.narrative.risk,
            relative: score.narrative.relative,
          } : {
            summary: '記憶體市場偏牛（62分），DRAM 現貨月漲 12% 為主要驅動力',
            quote: 'DDR5 spot 1M +12%，NAND wafer 1M -3%',
            equity: 'Tier A 股票 78% 站上 60 日均線',
            risk: '月波動率偏低 (15%)，最大回撤 -8%',
            relative: '記憶體籃子 1M 超額 Nasdaq +5%',
          })}
        />
      </div>
      <TrendChart />
      <div className="grid" style={{ gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 16 }}>
        <QuoteHeatmap period={period} />
        <StockTable period={period} />
      </div>
      <div className="grid" style={{ gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 16 }}>
        <LeaderBoard period={period} />
        <DataStatus />
      </div>
      <div className="grid" style={{ gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 16 }}>
        <CorrelationMatrix windowDays={60} />
        <BacktestWidget />
      </div>
      <SupplyChainGraph />
      <div className="mobile-only">
        <BottomNav />
      </div>
    </div>
  )
}
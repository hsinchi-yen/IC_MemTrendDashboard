import type { Period } from '../context/PeriodContext'
import type { Market } from '../api/hooks/useStocks'

export interface DemoScoreNarrative {
  summary: string
  quote: string
  equity: string
  risk: string
  relative: string
}

export const demoScore = {
  score_date: '2026-06-23',
  total_score: 62,
  status: 'bull',
  quote_momentum_score: 18,
  equity_momentum_score: 14,
  breadth_score: 8,
  risk_score: -6,
  relative_strength_score: 10,
  narrative: {
    summary: '記憶體市場偏牛（62分），DRAM 現貨月漲 12% 為主要驅動力',
    quote: 'DDR5 spot 1M +12%，NAND wafer 1M -3%',
    equity: 'Tier A 股票 78% 站上 60 日均線',
    risk: '月波動率偏低 (15%)，最大回撤 -8%',
    relative: '記憶體籃子 1M 超額 Nasdaq +5%',
  } satisfies DemoScoreNarrative,
}

export const demoIndicators = {
  dram: { label: 'DRAM', change_pct: 3.2, direction: 'up' as const },
  nand: { label: 'NAND', change_pct: -1.1, direction: 'down' as const },
  stock_basket: { label: '股票籃子', change_pct: 2.4, direction: 'up' as const },
  updated_at: '2026-06-23T18:30:00+08:00',
}

export const demoQuoteRows = [
  { id: 'DDR5-4800', label: 'DDR5-4800', label_en: 'DDR5-4800', category: 'DRAM' as const, definition: 'DDR5 spot price', changes: { '1D': 0.5, '1W': 4.2, '1M': 12.1, '3M': 18.4, '6M': 23.6, '1Y': 31.2 } },
  { id: 'DDR4-3200', label: 'DDR4-3200', label_en: 'DDR4-3200', category: 'DRAM' as const, definition: 'DDR4 spot price', changes: { '1D': -0.1, '1W': 1.0, '1M': 3.2, '3M': 6.1, '6M': 9.7, '1Y': 14.2 } },
  { id: 'NAND-TLC-WAFER', label: 'NAND TLC wafer', label_en: 'NAND TLC wafer', category: 'NAND' as const, definition: 'NAND wafer spot price', changes: { '1D': -0.2, '1W': -1.4, '1M': -3.1, '3M': 2.2, '6M': 8.3, '1Y': 12.8 } },
]

export const demoStockRows = [
  { ticker: 'MU', name: 'Micron', market: '美股' as Market, tier: 'A' as const, price: 125.36, currency: 'USD', changes: { '1D': 2.1, '1W': 5.2, '1M': 12.4, '3M': 28.7, '6M': 41.3, '1Y': 58.4 }, ma20_state: 'above' as const, ma60_state: 'above' as const, ma120_state: 'above' as const, ma240_state: 'above' as const, momentum: 74.2, trend_badge: 'bull' as const, trend_label: '月線上升・趨勢轉強' },
  { ticker: '2408', name: '南亞科', market: '台股(核心)' as Market, tier: 'A' as const, price: 52.4, currency: 'TWD', changes: { '1D': 1.0, '1W': 2.8, '1M': 9.3, '3M': 18.2, '6M': 26.7, '1Y': 34.1 }, ma20_state: 'above' as const, ma60_state: 'above' as const, ma120_state: 'above' as const, ma240_state: 'below' as const, momentum: 61.3, trend_badge: 'bull' as const, trend_label: '週線上升' },
  { ticker: '005930.KS', name: 'Samsung', market: '韓股' as Market, tier: 'A' as const, price: 84500, currency: 'KRW', changes: { '1D': -0.7, '1W': -2.2, '1M': -1.9, '3M': 6.1, '6M': 12.8, '1Y': 17.6 }, ma20_state: 'below' as const, ma60_state: 'above' as const, ma120_state: 'above' as const, ma240_state: 'above' as const, momentum: 42.8, trend_badge: 'neutral' as const, trend_label: '年線盤整' },
]

export const demoPeriods: Period[] = ['1D', '1W', '1M', '3M', '6M', '1Y']

export const demoLeaderboard = {
  quote_top: [
    { id: 'q1', label: 'DDR5 spot', change_pct: 12.1, spark: [100, 102, 104, 110, 116, 121], category: 'quote' as const },
    { id: 'q2', label: 'DDR4 spot', change_pct: 3.2, spark: [100, 100, 101, 102, 103, 103], category: 'quote' as const },
  ],
  quote_bottom: [
    { id: 'q3', label: 'NAND wafer', change_pct: -3.1, spark: [100, 99, 98, 97, 96, 95], category: 'quote' as const },
  ],
  stock_top: [
    { id: 's1', label: 'MU', ticker: 'MU', change_pct: 4.2, spark: [100, 101, 103, 105, 108, 110], category: 'stock' as const },
  ],
  stock_bottom: [
    { id: 's2', label: 'Samsung', ticker: '005930.KS', change_pct: -1.2, spark: [100, 99, 98, 98, 97, 96], category: 'stock' as const },
  ],
  abnormal: [
    { id: 'a1', label: 'MU', ticker: 'MU', change_pct: 5.8, spark: [100, 103, 104, 107, 110, 116], category: 'stock' as const },
  ],
}

export const demoCorrelation = [
  { row: 'MU', quote: 'DDR4 spot', value: 0.78 },
  { row: 'MU', quote: 'DDR5 spot', value: 0.81 },
  { row: '2408', quote: 'DDR4 spot', value: 0.74 },
  { row: '2408', quote: 'DDR5 spot', value: 0.69 },
]

export const demoBacktest = {
  equity_curve: [
    { date: '2026-01-01', value: 100 },
    { date: '2026-02-01', value: 104 },
    { date: '2026-03-01', value: 108 },
    { date: '2026-04-01', value: 112 },
  ],
  total_trades: 5,
  win_rate: 0.6,
  avg_return: 4.2,
  max_drawdown: -8.1,
  trades: [
    { entry_date: '2026-01-01', entry_score: 62, exit_date: '2026-01-31', return_pct: 8.5 },
    { entry_date: '2026-02-05', entry_score: 64, exit_date: '2026-03-07', return_pct: -2.1 },
  ],
}

export const demoSupplyChain = {
  nodes: [
    { id: 'tsmc', ticker: 'TSMC', name: '台積電', layer: 'upstream' as const, tier: 'A' as const, change_1d: 0.6 },
    { id: 'mu', ticker: 'MU', name: 'Micron', layer: 'maker' as const, tier: 'A' as const, change_1d: 2.1 },
    { id: 'amd', ticker: 'AMD', name: 'AMD', layer: 'downstream' as const, tier: 'B' as const, change_1d: 1.4 },
  ],
  edges: [
    { source: 'tsmc', target: 'mu' },
    { source: 'mu', target: 'amd' },
  ],
}
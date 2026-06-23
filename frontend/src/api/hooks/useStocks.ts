import { useQuery } from '@tanstack/react-query'
import apiClient from '../apiClient'
import type { Period } from '../../context/PeriodContext'

export type Market = '全部' | '美股' | '韓股' | '台股(核心)' | '台股(觀察)'
export type MAState = 'above' | 'below' | null

export interface StockRow {
  ticker: string
  name: string
  market: Market
  tier: 'A' | 'B' | 'C'
  price: number
  currency: string
  changes: Record<Period, number | null>
  ma20_state: MAState
  ma60_state: MAState
  ma120_state: MAState
  ma240_state: MAState
  momentum: number | null
  trend_badge: 'bull' | 'bear' | 'neutral'
  trend_label: string
}

function marketToApiMarket(market: Market): string | undefined {
  if (market === '全部') return undefined
  if (market === '美股') return 'US'
  if (market === '韓股') return 'KR'
  return 'TW'
}

function apiMarketToUiMarket(market: string): Market {
  if (market === 'US') return '美股'
  if (market === 'KR') return '韓股'
  if (market === 'TW') return '台股(核心)'
  return '全部'
}

export const useStockTable = (period: Period, market: Market = '全部') =>
  useQuery<StockRow[]>({
    queryKey: ['stock-table', period, market],
    queryFn: async () => {
      const { data } = await apiClient.get<{ total_count: number; data: Array<Record<string, unknown>> }>('/query/stock_table', {
        params: { period, market: marketToApiMarket(market) },
      })
      return (data.data ?? []).map((row) => ({
        ticker: String(row.ticker ?? ''),
        name: String(row.name ?? ''),
        market: apiMarketToUiMarket(String(row.market ?? '')),
        tier: String(row.tier ?? 'C') as 'A' | 'B' | 'C',
        price: Number(row.latest_close ?? 0),
        currency: String(row.currency ?? 'USD'),
        changes: { '1D': null, '1W': null, '1M': Number(row.change_pct_1m ?? null), '3M': null, '6M': null, '1Y': null },
        ma20_state: (row.ma_state as { ma20?: MAState } | undefined)?.ma20 ?? null,
        ma60_state: (row.ma_state as { ma60?: MAState } | undefined)?.ma60 ?? null,
        ma120_state: (row.ma_state as { ma120?: MAState } | undefined)?.ma120 ?? null,
        ma240_state: (row.ma_state as { ma240?: MAState } | undefined)?.ma240 ?? null,
        momentum: typeof row.momentum === 'number' ? row.momentum : null,
        trend_badge: (typeof row.momentum === 'number' && row.momentum > 50 ? 'bull' : 'neutral') as 'bull' | 'bear' | 'neutral',
        trend_label: String(row.ticker ?? row.name ?? ''),
      }))
    },
    staleTime: 60_000,
  })

export interface StockSparkline {
  dates: string[]
  prices: number[]
}

export const useStockSparkline = (ticker: string, enabled: boolean, market: Market = '美股') =>
  useQuery<StockSparkline>({
    queryKey: ['stock-spark', ticker, market],
    queryFn: async () => {
      const { data } = await apiClient.get<{ total_count: number; data: Array<{ date: string; close: number | null }> }>(
        `/prices/${ticker}`,
        { params: { market: marketToApiMarket(market), page_size: 30 } },
      )
      const rows = [...(data.data ?? [])].reverse()
      return {
        dates: rows.map((row) => row.date),
        prices: rows.map((row) => Number(row.close ?? 0)),
      }
    },
    enabled,
    staleTime: 0,
  })

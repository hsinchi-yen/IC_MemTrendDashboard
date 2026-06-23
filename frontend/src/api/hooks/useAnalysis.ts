import { useQuery } from '@tanstack/react-query'
import apiClient from '../apiClient'

export interface CorrelationCell {
  stock: string
  quote: string
  value: number | null
  window: 60 | 120
}

export const useCorrelationMatrix = (window: 60 | 120) =>
  useQuery<CorrelationCell[]>({
    queryKey: ['correlation', window],
    queryFn: async () => {
      const { data } = await apiClient.get<CorrelationCell[]>(
        '/analysis/correlation',
        { params: { window } }
      )
      return data
    },
    staleTime: 300_000,
  })

export interface BacktestParams {
  entry_condition: string
  hold_period: number
  date_from: string
  date_to: string
}

export interface TradeRecord {
  entry_date: string
  entry_score: number
  exit_date: string
  return_pct: number
}

export interface BacktestResult {
  equity_curve: Array<{ date: string; value: number }>
  total_trades: number
  win_rate: number
  avg_return: number
  max_drawdown: number
  trades: TradeRecord[]
}

export interface SupplyChainNode {
  id: string
  ticker: string
  name: string
  layer: 'upstream' | 'maker' | 'controller' | 'downstream'
  tier: 'A' | 'B' | 'C'
  change_1d: number | null
}

export interface SupplyChainEdge {
  source: string
  target: string
}

export interface SupplyChainData {
  nodes: SupplyChainNode[]
  edges: SupplyChainEdge[]
}

export const useSupplyChain = () =>
  useQuery<SupplyChainData>({
    queryKey: ['supply-chain'],
    queryFn: async () => {
      const { data } = await apiClient.get<SupplyChainData>(
        '/analysis/supply-chain'
      )
      return data
    },
    staleTime: 300_000,
  })

export interface AlertRule {
  id: number
  name: string
  condition: string
  threshold: number
  enabled: boolean
}

export const useAlertRules = () =>
  useQuery<AlertRule[]>({
    queryKey: ['alert-rules'],
    queryFn: async () => {
      const { data } = await apiClient.get<AlertRule[]>('/alerts/rules')
      return data
    },
    staleTime: 60_000,
  })

export interface NewsItem {
  id: number
  title: string
  source: string
  published_at: string
  sentiment: 'positive' | 'negative' | 'neutral'
  summary: string
}

export const useNewsItems = () =>
  useQuery<NewsItem[]>({
    queryKey: ['news'],
    queryFn: async () => {
      const { data } = await apiClient.get<NewsItem[]>('/news/latest')
      return data
    },
    staleTime: 120_000,
  })

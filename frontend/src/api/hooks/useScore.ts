import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../client'

export interface ScoreNarrative {
  summary: string
  quote: string
  equity: string
  risk: string
  relative: string
}

export interface MarketScore {
  score_date: string
  total_score: number
  status: string
  quote_momentum_score: number
  equity_momentum_score: number
  breadth_score: number
  risk_score: number
  relative_strength_score: number
  narrative: ScoreNarrative
}

export interface ScoreHistoryPoint {
  score_date: string
  total_score: number
  status: string
}

export function useLatestScore() {
  return useQuery({
    queryKey: ['score', 'latest'],
    queryFn: async () => {
      const { data } = await apiClient.get<MarketScore>('/score/latest')
      return data
    },
    refetchInterval: 5 * 60 * 1000,
  })
}

export function useScoreHistory(days = 90) {
  return useQuery({
    queryKey: ['score', 'history', days],
    queryFn: async () => {
      const { data } = await apiClient.get<ScoreHistoryPoint[]>(
        '/score/history',
        { params: { days } },
      )
      return data
    },
    staleTime: 10 * 60 * 1000,
  })
}

import { useQuery } from '@tanstack/react-query'
import apiClient from '../apiClient'
import type { Period } from '../../context/PeriodContext'

export interface LeaderItem {
  id: string
  label: string
  change_pct: number
  spark: number[]
  category: 'quote' | 'stock'
  ticker?: string
}

export interface LeaderBoardData {
  quote_top: LeaderItem[]
  quote_bottom: LeaderItem[]
  stock_top: LeaderItem[]
  stock_bottom: LeaderItem[]
  abnormal: LeaderItem[]
}

export const useLeaderBoard = (period: Period) =>
  useQuery<LeaderBoardData>({
    queryKey: ['leaderboard', period],
    queryFn: async () => {
      const { data } = await apiClient.get<LeaderBoardData>(
        '/leaderboard',
        { params: { period } }
      )
      return data
    },
    staleTime: 60_000,
    refetchInterval: 120_000,
  })

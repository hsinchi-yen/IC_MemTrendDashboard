import { useQuery } from '@tanstack/react-query'
import apiClient from '../apiClient'
import type { Period } from '../../context/PeriodContext'

export interface QuoteRow {
  id: string
  label: string
  label_en: string
  category: 'DRAM' | 'NAND'
  changes: Record<Period, number | null>
  definition: string
}

export const useQuoteHeatmap = (period: Period) =>
  useQuery<QuoteRow[]>({
    queryKey: ['quote-heatmap', period],
    queryFn: async () => {
      const { data } = await apiClient.get<QuoteRow[]>('/quotes/heatmap', {
        params: { period },
      })
      return data
    },
    staleTime: 60_000,
  })

export interface SparkData {
  dates: string[]
  values: number[]
}

export const useQuoteSparkline = (quoteId: string, enabled: boolean) =>
  useQuery<SparkData>({
    queryKey: ['quote-spark', quoteId],
    queryFn: async () => {
      const { data } = await apiClient.get<SparkData>(
        `/quotes/${quoteId}/sparkline`
      )
      return data
    },
    enabled,
    staleTime: 0,
  })

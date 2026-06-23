import { useQuery, useMutation } from '@tanstack/react-query'
import apiClient from '../apiClient'
import type { Period } from '../../context/PeriodContext'

export interface TrendPoint {
  date: string
  dram: number | null
  nand: number | null
  stock: number | null
}

export interface TrendMAPoint {
  date: string
  ma20: number | null
  ma60: number | null
  ma120: number | null
}

export interface EventMarker {
  date: string
  label: string
  description: string
  type: 'policy' | 'earnings' | 'macro' | 'supply'
}

export interface TrendChartData {
  points: TrendPoint[]
  ma: TrendMAPoint[]
  events: EventMarker[]
}

export const useTrendChart = (period: Period) =>
  useQuery<TrendChartData>({
    queryKey: ['trend-chart', period],
    queryFn: async () => {
      const { data } = await apiClient.get<TrendChartData>('/trends/chart', {
        params: { period },
      })
      return data
    },
    staleTime: 60_000,
  })

// Events management
export interface MarketEvent {
  id: number
  date: string
  label: string
  description: string
  type: string
}

export const useEvents = () =>
  useQuery<MarketEvent[]>({
    queryKey: ['events'],
    queryFn: async () => {
      const { data } = await apiClient.get<MarketEvent[]>('/events')
      return data
    },
    staleTime: 120_000,
  })

export const useCreateEvent = () =>
  useMutation({
    mutationFn: async (payload: Omit<MarketEvent, 'id'>) => {
      const { data } = await apiClient.post('/events', payload)
      return data
    },
  })

export const useDeleteEvent = () =>
  useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/events/${id}`)
    },
  })

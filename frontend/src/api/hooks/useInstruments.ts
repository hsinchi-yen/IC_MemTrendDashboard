import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../client'

export interface Instrument {
  id: number
  ticker: string
  market: string
  name: string
  name_en: string
  tier: string
  supply_chain_tag: string
  currency: string
  is_active: boolean
  score_weight: number
  score_only_observe: boolean
}

interface InstrumentParams {
  market?: string
  tier?: string
  tag?: string
}

export function useInstruments(params?: InstrumentParams) {
  return useQuery({
    queryKey: ['instruments', params ?? {}],
    queryFn: async () => {
      const { data } = await apiClient.get<Instrument[]>('/instruments', {
        params,
      })
      return data
    },
    staleTime: 10 * 60 * 1000, // instruments change rarely
  })
}

export function useInstrument(id: number | undefined) {
  return useQuery({
    queryKey: ['instruments', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Instrument>(`/instruments/${id}`)
      return data
    },
    enabled: id !== undefined,
    staleTime: 10 * 60 * 1000,
  })
}

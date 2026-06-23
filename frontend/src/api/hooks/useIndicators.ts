import { useQuery } from '@tanstack/react-query'
import apiClient from '../apiClient'
import type { Period } from '../../context/PeriodContext'

export interface MarketIndicator {
  label: string
  change_pct: number
  direction: 'up' | 'down' | 'flat'
}

export interface TopBarIndicators {
  dram: MarketIndicator
  nand: MarketIndicator
  stock_basket: MarketIndicator
  updated_at: string
}

export const useTopBarIndicators = (period: Period) =>
  useQuery<TopBarIndicators>({
    queryKey: ['topbar-indicators', period],
    queryFn: async () => {
      const { data } = await apiClient.get<TopBarIndicators>(
        '/indicators/topbar',
        { params: { period } }
      )
      return data
    },
    staleTime: 60_000,
    refetchInterval: 120_000,
    placeholderData: {
      dram: { label: 'DRAM', change_pct: 0, direction: 'flat' },
      nand: { label: 'NAND', change_pct: 0, direction: 'flat' },
      stock_basket: { label: '股票', change_pct: 0, direction: 'flat' },
      updated_at: new Date().toISOString(),
    },
  })

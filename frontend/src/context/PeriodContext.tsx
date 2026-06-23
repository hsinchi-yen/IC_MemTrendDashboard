import { createContext, useContext, useState, type FC, type ReactNode } from 'react'

export type Period = '1D' | '1W' | '1M' | '3M' | '6M' | '1Y'

export const PERIODS: Period[] = ['1D', '1W', '1M', '3M', '6M', '1Y']

interface PeriodContextValue {
  period: Period
  setPeriod: (p: Period) => void
}

const PeriodContext = createContext<PeriodContextValue | null>(null)

export const PeriodProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [period, setPeriod] = useState<Period>('1M')
  return (
    <PeriodContext.Provider value={{ period, setPeriod }}>
      {children}
    </PeriodContext.Provider>
  )
}

export const usePeriod = (): PeriodContextValue => {
  const ctx = useContext(PeriodContext)
  if (!ctx) throw new Error('usePeriod must be used within PeriodProvider')
  return ctx
}

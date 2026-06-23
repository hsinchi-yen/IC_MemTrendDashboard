import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../apiClient'

export interface RefreshStatus {
  is_running: boolean
  current_source: string | null
  last_run_at: string | null
  last_run_status: 'success' | 'failed' | 'running' | null
  equity_last_update: string | null
  quote_last_update: string | null
}

export const useRefreshStatus = (pollWhileRunning = true) => {
  const query = useQuery<RefreshStatus>({
    queryKey: ['refresh-status'],
    queryFn: async () => {
      const { data } = await apiClient.get<RefreshStatus>('/refresh/status')
      return data
    },
    refetchInterval: (q) => {
      const data = q.state.data
      if (!pollWhileRunning) return false
      return data?.is_running ? 3_000 : 30_000
    },
  })
  return query
}

export const useTriggerRefresh = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post('/refresh')
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['refresh-status'] })
    },
  })
}

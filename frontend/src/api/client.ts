import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.response.use(
  response => response,
  error => {
    const message =
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      (error.response?.data as { message?: string } | undefined)?.message ??
      (error instanceof Error ? error.message : 'Unknown API error')
    console.error('[API Error]', message, error)
    return Promise.reject(error instanceof Error ? error : new Error(message))
  },
)

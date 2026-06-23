import axios from 'axios'
import { getFinMindToken } from '../utils/finmindToken'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach the user's FinMind token (from localStorage) to every request so
// TW/US ingestion can use it without any server-side configuration.
apiClient.interceptors.request.use((config) => {
  const token = getFinMindToken()
  if (token) config.headers.set('X-FinMind-Token', token)
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('[API Error]', err?.response?.status, err?.message)
    return Promise.reject(err)
  }
)

export default apiClient

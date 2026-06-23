import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import { PeriodProvider } from './context/PeriodContext'
import './styles/theme.css'
import './styles/animations.css'
import './styles/global.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <PeriodProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </PeriodProvider>
    </QueryClientProvider>
  </React.StrictMode>,
)

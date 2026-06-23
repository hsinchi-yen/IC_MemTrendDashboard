import { Link, Navigate, Route, Routes } from 'react-router-dom'
import { DashboardPage } from './pages/DashboardPage/DashboardPage'
import { QueryPage } from './pages/QueryPage/QueryPage'
import { IndicatorsPage } from './pages/IndicatorsPage/IndicatorsPage'

export default function App() {
  return (
    <div className="app-root">
      <header className="app-header glass-card">
        <div>
          <p className="eyebrow">MemTrend Dashboard</p>
          <h2>記憶體趨勢儀錶板</h2>
        </div>

        <nav className="app-nav" aria-label="Primary">
          <Link to="/">Dashboard</Link>
          <Link to="/query">Query</Link>
          <Link to="/indicators">Indicators</Link>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/query" element={<QueryPage />} />
          <Route path="/indicators" element={<IndicatorsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
import { Link } from 'react-router-dom'

export function BottomNav() {
  return (
    <nav className="glass-card" style={{ position: 'sticky', bottom: 0, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, padding: 10 }}>
      <Link to="/">總覽</Link>
      <Link to="/query">報價</Link>
      <Link to="/query">個股</Link>
      <Link to="/indicators">設定</Link>
    </nav>
  )
}
import { useEffect, useState } from 'react'
import { getFinMindToken, setFinMindToken } from '../../utils/finmindToken'

/**
 * FinMind API-key settings.
 *
 * Lets the user paste their personal FinMind token, which is stored in the
 * browser's localStorage and automatically attached to API requests as the
 * `X-FinMind-Token` header. Used by TW/US ingestion. Nothing is sent to any
 * third party — the token stays in the browser and is only forwarded to this
 * app's own backend on refresh.
 */
export function FinMindSettings() {
  const [open, setOpen] = useState(false)
  const [token, setToken] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (open) {
      setToken(getFinMindToken())
      setSaved(false)
    }
  }, [open])

  const hasToken = getFinMindToken().length > 0

  const handleSave = () => {
    setFinMindToken(token)
    setSaved(true)
    setTimeout(() => setOpen(false), 700)
  }

  const handleClear = () => {
    setFinMindToken('')
    setToken('')
    setSaved(true)
  }

  return (
    <>
      <button
        type="button"
        className="btn"
        onClick={() => setOpen(true)}
        title="設定 FinMind API Token"
      >
        ⚙ FinMind {hasToken ? '✓' : ''}
      </button>

      {open && (
        <div
          role="dialog"
          aria-modal="true"
          onClick={() => setOpen(false)}
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
          }}
        >
          <div
            className="glass-card"
            onClick={(e) => e.stopPropagation()}
            style={{ width: 'min(460px, 92vw)', padding: 24, display: 'grid', gap: 14 }}
          >
            <div className="flex items-center justify-between">
              <h3 style={{ margin: 0 }}>FinMind API Token</h3>
              <button type="button" className="btn" onClick={() => setOpen(false)}>✕</button>
            </div>

            <p className="text-xs text-secondary" style={{ lineHeight: 1.6 }}>
              台股 / 美股資料優先使用 FinMind。貼上你的 FinMind Token 後會儲存在
              此瀏覽器的 localStorage，並在每次「立即更新」時透過
              <code> X-FinMind-Token </code> 標頭送給後端使用。留空則改用免費的
              yfinance 來源。
            </p>

            <input
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="貼上 FinMind Token…"
              autoComplete="off"
              spellCheck={false}
              style={{
                width: '100%', padding: '10px 12px', borderRadius: 8,
                border: '1px solid var(--border, #334)', background: 'rgba(255,255,255,0.04)',
                color: 'inherit', fontFamily: 'var(--font-mono, monospace)',
              }}
            />

            <div className="flex items-center justify-between gap-2">
              <a
                href="https://finmindtrade.com/"
                target="_blank"
                rel="noreferrer noopener"
                className="text-xs text-secondary"
              >
                取得 FinMind Token ↗
              </a>
              <div className="flex items-center gap-2">
                <button type="button" className="btn" onClick={handleClear}>清除</button>
                <button type="button" className="btn btn--accent" onClick={handleSave}>
                  {saved ? '已儲存 ✓' : '儲存'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

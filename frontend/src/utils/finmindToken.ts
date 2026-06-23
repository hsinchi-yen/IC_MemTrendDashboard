/**
 * FinMind API token helper.
 *
 * The user can paste their personal FinMind token in the UI; it is persisted
 * in localStorage and attached to API requests as the `X-FinMind-Token`
 * header, so TW/US ingestion can use it without any server-side config.
 */
const STORAGE_KEY = 'finmind_token'

export function getFinMindToken(): string {
  try {
    return localStorage.getItem(STORAGE_KEY)?.trim() ?? ''
  } catch {
    return ''
  }
}

export function setFinMindToken(token: string): void {
  try {
    const trimmed = token.trim()
    if (trimmed) localStorage.setItem(STORAGE_KEY, trimmed)
    else localStorage.removeItem(STORAGE_KEY)
  } catch {
    /* ignore storage failures (private mode, etc.) */
  }
}

export function clearFinMindToken(): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    /* ignore */
  }
}

/** Attach the stored token (if any) to an axios request header bag. */
export function withFinMindHeader(headers: Record<string, unknown>): Record<string, unknown> {
  const token = getFinMindToken()
  if (token) headers['X-FinMind-Token'] = token
  return headers
}

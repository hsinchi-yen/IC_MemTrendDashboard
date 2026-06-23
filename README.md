# IC_MemTrendDashboard

記憶體報價趨勢追蹤儀錶板 — 聚焦 DRAM / NAND / Flash / HBM / SSD 報價與直接曝險公司。

> 注意：本系統用於產業追蹤與研究，不作為投資建議。

## 快速啟動

### Windows (最簡單 ✓)
1. 確保 Docker Desktop 已安裝且正在運行
2. **雙擊** 專案根目錄中的 `run-docker.cmd`
3. 自動啟動所有服務
4. 開啟瀏覽器: http://localhost:8510

### macOS / Linux
```bash
# 1. 複製環境變數設定
cp .env.example .env
# 2. 填入 .env 中的 API keys
# 3. 啟動所有服務
docker-compose up -d
# 4. 開啟 Dashboard
open http://localhost:8510
# 5. 開啟 API Docs
open http://localhost:3000/docs
```

### 手動啟動
```bash
# 使用 Docker Compose
docker-compose up --build

# 或後台運行
docker-compose up -d
```

**詳細說明見** [DOCKER_GUIDE.md](./DOCKER_GUIDE.md)

## 服務架構

| 服務 | Port | 說明 |
|---|---|---|
| PostgreSQL | 5432 | 主資料庫 |
| Backend API | 3000 | FastAPI |
| Web UI | 8510 | React Dashboard |

## 實作階段

| Phase | 說明 |
|---|---|
| Phase 0 | 資料源驗證：確認所有股票代號與 API 可用性 |
| Phase 1 | MVP 資料管線：抓取日線、記憶體報價、計算趨勢指標與牛熊分數 |
| Phase 2 | 一頁式 Dashboard：深色主題、熱力表、趨勢圖、牛熊溫度計 |
| Phase 3 | 告警推播：Telegram/Line/Email + 相關性矩陣 |
| Phase 4 | PWA + Android APK (Capacitor) |
| Phase 5 | AI 洞察：LLM 新聞摘要、事件 Overlay、回測 Widget、供應鏈節點圖 |

## 環境變數

請參考 `.env.example` 設定所有必要的 API Keys。

## 技術棧

- **Backend**: Python FastAPI + APScheduler
- **Database**: PostgreSQL 16
- **Frontend**: React 18 + Vite + TypeScript
- **Charts**: ECharts + TradingView lightweight-charts
- **Mobile**: PWA + Capacitor (Android APK)

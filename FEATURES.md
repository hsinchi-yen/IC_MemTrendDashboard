# IC MemTrend Dashboard — 功能說明書

> 記憶體報價趨勢追蹤儀錶板 — 聚焦 DRAM / NAND / Flash / HBM / SSD 報價與記憶體供應鏈直接曝險公司。
>
> ⚠️ 本系統用於產業追蹤與研究，**不作為投資建議**。

---

## 一、產品定位

本系統幫助使用者一頁式掌握「記憶體現貨/合約報價」與「記憶體供應鏈個股」的連動趨勢，並透過量化的**牛熊溫度計（Market Score）**判斷產業景氣強弱。資料涵蓋美股 (US)、韓股 (KR)、日股 (JP)、台股 (TW) 四大市場的記憶體製造商與上下游供應鏈，共 100+ 檔追蹤標的。

| 角色 | 使用情境 |
|------|----------|
| 產業研究員 | 觀察 DRAM/NAND 報價趨勢與股價背離 |
| 供應鏈分析師 | 追蹤上中下游個股相對強弱與相關性 |
| 一般投資人 | 用牛熊溫度計快速判斷產業冷熱（非投資建議）|

---

## 二、系統架構

```
┌──────────────┐     /api 代理     ┌───────────────┐      ┌──────────────┐
│  Frontend    │ ───────────────▶ │  Backend API   │ ───▶ │ PostgreSQL 16│
│ React + Vite │   (axios)         │ FastAPI        │      │  (asyncpg)   │
│ Port 8510    │ ◀─────────────── │ Port 3000      │ ◀─── │  Port 5432   │
└──────────────┘     JSON          └───────┬───────┘      └──────────────┘
                                            │
                                   APScheduler 排程
                                   (每日 01:00 抓取 / 05:30 重算)
                                            │
                          ┌─────────────────┴──────────────────┐
                          │   資料管線 (app/jobs)               │
                          │  ingest_* → compute_* → evaluate_*  │
                          └────────────────────────────────────┘
```

| 層 | 技術 | 說明 |
|----|------|------|
| 前端 | React 18 + Vite 5 + TypeScript | SPA，3 個分頁；React Query 管理資料快取 |
| 圖表 | ECharts 5 | 熱力圖、力導向供應鏈圖、相關性矩陣、雷達圖 |
| 後端 | FastAPI + SQLAlchemy 2 (async) | 15 個 router 模組，REST API |
| 排程 | APScheduler (Asia/Taipei) | 每日自動抓取與運算 |
| 資料庫 | PostgreSQL 16 | 12 張資料表 |
| 行動 | PWA (Service Worker) + Capacitor | 離線快取、可打包 Android APK |
| 部署 | Docker Compose | 一鍵啟動三服務 |

---

## 三、核心功能

### 1. 牛熊溫度計（Market Score）
將整體記憶體產業景氣量化為 0–100 分，由五個子分數加權組成：

| 子分數 | 意義 |
|--------|------|
| `quote_momentum_score` | 記憶體報價動能 |
| `equity_momentum_score` | 個股股價動能 |
| `breadth_score` | 市場廣度（上漲家數占比）|
| `risk_score` | 風險（波動度）|
| `relative_strength_score` | 相對強弱 |

對應端點：`GET /api/score/latest`、`GET /api/score`（歷史分頁）。
前端元件：`BullBearGauge`（溫度計）、`ScoreRadarChart`（五維雷達圖）。

### 2. 報價熱力表（Quote Heatmap）
依產品（DDR5、NAND wafer…）顯示 1D / 1W / 1M / 3M / 6M / 1Y 多週期漲跌幅，綠漲紅跌的色階熱力圖；滑鼠懸停顯示 30 日 sparkline 走勢。

對應端點：`GET /api/quotes/heatmap`、`GET /api/quotes/{product}/sparkline`。
前端元件：`QuoteHeatmap`、`SparklineTooltip`。

### 3. 趨勢圖（Trend Chart）
疊圖比較 DRAM、NAND 報價與股票籃子的標準化走勢（基期 = 100），並支援 MA20 移動平均與**事件 Overlay**（在時間軸標註財報、漲價、地震等市場事件）。

對應端點：`GET /api/trends/chart`、`GET/POST/PATCH/DELETE /api/events`。
前端元件：`TrendChart`。

### 4. 排行榜（Leaderboard）
列出報價漲幅前 5 / 跌幅前 5、個股漲幅前 5，並自動標記漲跌幅 > 5% 的「異常」標的。

對應端點：`GET /api/leaderboard?period=1M`。前端元件：`LeaderBoard`。

### 5. 個股查詢表（Stock Table）
可依市場 / 層級 (tier) / 供應鏈標籤 (tag) / 關鍵字篩選，支援排序、分頁與 **CSV 匯出**（送出 `Accept: text/csv` 標頭）。每列顯示最新收盤價、1M 漲跌幅、動能、均線狀態。

對應端點：`GET /api/query/stock_table`。前端頁面：`QueryPage`、元件 `StockTable`。

### 6. 趨勢指標（Trend Metrics）
每檔標的逐期計算：漲跌幅、方向、動能、均線狀態、波動度、連續漲跌天數 (streak)、標準化指數與文字敘述。

對應端點：`GET /api/trend_metrics/{ticker}?market=US&period=1M`。

### 7. 相關性矩陣（Correlation Matrix）
以熱力圖呈現「個股 × 報價品種」的皮爾森相關係數（-1 紅 ↔ +1 綠），支援 60 / 120 日窗口。

對應端點：`GET /api/analysis/correlation?window=60`。前端元件：`CorrelationMatrix`。

### 8. 供應鏈節點圖（Supply Chain Graph）
ECharts 力導向圖，節點依供應鏈層級（maker / equipment / backend-test…）分群，節點大小反映當日漲跌幅，可拖曳、縮放。

對應端點：`GET /api/analysis/supply-chain`。前端元件：`SupplyChainGraph`。

### 9. 回測 Widget（Backtest）
以歷史 Market Score 進行簡易策略回測（如 `score > 60` 進場、持有 30 天），輸出交易明細、勝率、平均報酬、最大回撤與權益曲線。

對應端點：`POST /api/backtest`。前端元件：`BacktestWidget`。

### 10. 告警規則（Alerts）
針對 `total_score`、`dram_spot_1d_change`、`nand_wafer_ma_cross` 或個別個股漲跌幅設定門檻告警，支援 Telegram / Line / Email 三種通道。提供規則 CRUD 與告警事件查詢。

對應端點：`GET/POST/PATCH/DELETE /api/alerts/rules`、`GET /api/alerts/events`。
> 後端排程 `evaluate_alerts` 會在每日管線中比對規則並寫入告警事件。

### 11. 新聞摘要（News）
由 LLM（Gemini / OpenAI / Anthropic 可設定）對抓取的新聞做情緒判讀與重點摘要。

對應端點：`GET /api/news/latest`。

### 12. 資料新鮮度與手動刷新（Refresh）
顯示股價、報價最後更新時間與 staleness 狀態（fresh / stale / critical），並可手動觸發完整資料管線（含鎖機制避免重複執行）。

對應端點：`POST /api/refresh`、`GET /api/refresh/status`、`GET /api/refresh/health`。
前端元件：`DataStatus`、`TopBar`。

---

## 三之二、真實資料來源（Real Data）

本系統使用**真實市場資料**，非假資料：

| 資料類型 | 真實來源 | 說明 |
|----------|----------|------|
| 股價日線 | **yfinance**（主）/ FinMind / Stooq / Alpha Vantage | 美/韓/日/台四市場 106 檔，約一年日線；yfinance 免 token 可直接抓 `.TW`/`.TWO`/`.KS`/`.KQ`/`.T` |
| 記憶體報價 | **DRAMeXchange** 公開頁爬蟲 | DRAM Spot（DDR3/DDR4/DDR5）、Module、GDDR、NAND Wafer/Flash、Memory Card，含 high/low/avg/change% |
| 牛熊分數 / 趨勢指標 | 由上述真實資料計算 | `compute_trend_metrics` / `compute_market_score` |

> 記憶體報價解析器 `memory_quote_parser.py` 會擷取每列的真實高/低/均價與當日漲跌幅，**包含 DDR3**（例：`DDR3 4Gb 512Mx8 1600/1866` 均價 11.271、+1.07%）。DDR2 目前未列於 DRAMeXchange 公開頁，若來源恢復提供，解析器會自動納入。

### 一鍵載入真實資料

```bash
# 啟動 PostgreSQL 後：
$env:DATABASE_URL="postgresql+asyncpg://memdash:changeme@localhost:5432/memdash"
$env:PYTHONPATH="backend"
python scripts/data_import/load_real_data.py            # 全市場
python scripts/data_import/load_real_data.py --markets US,TW --limit 6   # 快速驗證
```
此腳本會建表 → 灌入 106 檔標的 → 抓真實股價與報價 → 計算趨勢與分數 → 印出驗證摘要。

### FinMind API Token（UI 設定）

台股 / 美股可優先使用 FinMind。前端右上角 **「⚙ FinMind」** 按鈕可輸入個人 Token：

- Token 儲存在瀏覽器 **localStorage**（key `finmind_token`），不寫入伺服器。
- 每次 API 請求自動附帶 `X-FinMind-Token` 標頭；按「立即更新」時後端 `POST /api/refresh` 會讀取此標頭並用於 TW/US 抓取。
- 留空則改用免費的 yfinance 來源，系統仍可正常運作。

---

## 四、資料管線（每日自動排程）

APScheduler 以 `Asia/Taipei` 時區運行兩個排程：

| 時間 | 工作 | 內容 |
|------|------|------|
| 01:00 | `daily_ingestion` | 執行 `run_all_ingestion_jobs`：抓取 TW/US/JP/KR 股價 + 記憶體報價 → 計算趨勢指標 → 計算 Market Score → 評估告警 |
| 05:30 | `daily_summary` | 重算趨勢指標與 Market Score（補抓晚到的資料）|

資料來源服務（`app/services`）：FinMind（台股）、yfinance / Stooq / Alpha Vantage（美韓日股備援）、記憶體報價解析器；通知服務：Telegram / Line / Email。

> 也可呼叫 `POST /api/refresh` 立即手動觸發整條管線。

---

## 五、API 端點總覽（共 30+ 路由）

| 分類 | 方法 | 路徑 |
|------|------|------|
| 健康檢查 | GET | `/health`、`/api/health` |
| 標的 | GET | `/api/instruments` |
| 報價 | GET | `/api/quotes`、`/api/quotes/heatmap`、`/api/quotes/{id}/sparkline` |
| 分數 | GET | `/api/score`、`/api/score/latest` |
| 趨勢指標 | GET | `/api/trend_metrics/{ticker}` |
| 股價 | GET | `/api/prices/{ticker}` |
| 排行榜 | GET | `/api/leaderboard` |
| 趨勢圖 | GET | `/api/trends/chart` |
| 指標說明 | GET | `/api/indicators/definitions`、`/api/indicators/topbar` |
| 查詢表 | GET | `/api/query/stock_table`（支援 CSV）|
| 分析 | GET | `/api/analysis/correlation`、`/api/analysis/supply-chain` |
| 新聞 | GET | `/api/news/latest` |
| 事件 | GET/POST/PATCH/DELETE | `/api/events`、`/api/events/{id}` |
| 告警 | GET/POST/PATCH/DELETE | `/api/alerts/rules`、`/api/alerts/events` |
| 回測 | POST | `/api/backtest` |
| 刷新 | POST/GET | `/api/refresh`、`/api/refresh/status`、`/api/refresh/health` |

完整互動式文件：啟動後造訪 `http://localhost:3000/docs`（Swagger UI）。

---

## 六、前端頁面

| 路由 | 頁面 | 內容 |
|------|------|------|
| `/` | Dashboard | 牛熊溫度計、報價熱力表、趨勢圖、排行榜、相關性矩陣、供應鏈圖、回測、新聞 |
| `/query` | Query | 個股查詢表（篩選 / 排序 / CSV 匯出）|
| `/indicators` | Indicators | 指標定義與計算方式說明 |

行動裝置支援：5 級 RWD 斷點（1024 / 768 / 480px + 橫向）、PWA 離線快取、可透過 `npm run build:android` 打包成 Android APK。

---

## 七、快速啟動

### Docker（推薦）
```bash
cp .env.example .env      # 填入 API keys（DATABASE_URL 必填）
docker-compose up -d
# Dashboard: http://localhost:8510
# API Docs:  http://localhost:3000/docs
```
Windows 使用者可直接雙擊 `run-docker.cmd`。

### 本機開發
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 3000 --reload

# Frontend
cd frontend
npm install
npm run dev        # http://localhost:8510（/api 自動代理到 :3000）
```

### 灌入標的種子資料
```bash
python scripts/data_import/instruments_seed.py        # 寫入 106 檔標的
python scripts/data_import/instruments_seed.py --dry-run
```

---

## 八、測試

後端附帶端對端整合測試 `backend/tests/test_e2e.py`，使用獨立 SQLite 資料庫啟動完整 FastAPI app、植入種子資料，並驗證全部 30+ 端點的狀態碼與回應結構（含 CRUD、CSV、錯誤路徑、422 驗證）。

```bash
cd backend
DATABASE_URL="sqlite+aiosqlite:///./e2e_test.db" PYTHONPATH=. \
  python -m pytest tests/test_e2e.py -v
# 40 passed
```

前端型別檢查與建置：
```bash
cd frontend
npm run build      # tsc -b && vite build
```

---

## 九、環境變數

所有密鑰透過 `.env` 管理，請參考 `.env.example`：

| 變數 | 用途 |
|------|------|
| `DATABASE_URL` | PostgreSQL 連線字串（必填）|
| `FINMIND_TOKEN` / `ALPHA_VANTAGE_KEY` | 股價資料源 |
| `TELEGRAM_BOT_TOKEN` / `LINE_NOTIFY_TOKEN` / `SMTP_*` | 告警通道 |
| `LLM_API_KEY` / `LLM_PROVIDER` | 新聞摘要 LLM |
| `DATA_FRESHNESS_THRESHOLD_HOURS_*` | 資料新鮮度門檻 |

---

## 十、資料模型（12 張表）

`instruments`（標的主檔）、`equity_prices`（日線）、`memory_quotes`（記憶體報價）、`trend_metrics`（趨勢指標）、`market_scores`（牛熊分數）、`correlation_matrix`（相關性）、`market_events`（市場事件）、`news_items`（新聞）、`alert_rules` / `alert_events`（告警）、`refresh_jobs`（刷新工作）、`source_runs`（資料源執行紀錄）。
